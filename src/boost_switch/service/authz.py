from __future__ import annotations

from dataclasses import dataclass
from grp import getgrall
import re
from pwd import getpwuid
from subprocess import CompletedProcess, run

from boost_switch.contracts import ACTION_SET_BOOST, AUTHORIZED_GROUP
from boost_switch.errors import PermissionDeniedError


@dataclass(slots=True)
class CallerIdentity:
    sender: str
    uid: int
    pid: int
    user_name: str
    in_authorized_group: bool


@dataclass(slots=True)
class AuthorizationContext(CallerIdentity):
    session_active: bool
    session_remote: bool


@dataclass(slots=True)
class AuthorizationDecision:
    allowed: bool
    reason: str
    message: str


class SubjectEvaluator:
    def __init__(self, group_evaluator: "GroupEvaluator" | None = None) -> None:
        self._group_evaluator = group_evaluator or GroupEvaluator()

    def evaluate(self, context: AuthorizationContext) -> AuthorizationDecision:
        if context.session_remote:
            return AuthorizationDecision(False, "permission_denied", "当前会话不是本地 seat")
        if not context.session_active:
            return AuthorizationDecision(False, "inactive_session", "当前会话未激活")
        return self._group_evaluator.evaluate(context)


class GroupEvaluator:
    def evaluate(self, identity: CallerIdentity) -> AuthorizationDecision:
        if not identity.in_authorized_group:
            return AuthorizationDecision(False, "permission_denied", "当前用户不在授权组中")
        return AuthorizationDecision(True, "ok", "调用方满足基础条件")


def user_in_group(uid: int, group_name: str = AUTHORIZED_GROUP) -> bool:
    user_name = getpwuid(uid).pw_name
    for group in getgrall():
        if group.gr_name == group_name and user_name in group.gr_mem:
            return True
    return False


class CommandRunner:
    def __call__(self, args: list[str]) -> CompletedProcess[str]:
        return run(args, check=False, text=True, capture_output=True)


def _parse_busctl_scalar(output: str) -> str:
    parts = output.strip().split(maxsplit=1)
    if len(parts) != 2:
        raise RuntimeError(f"unexpected busctl output: {output!r}")
    return parts[1].strip().strip('"')


def _parse_busctl_object_paths(output: str) -> list[str]:
    return [path.strip('"') for path in re.findall(r'"/[^"]*"', output)]


class SenderContextResolver:
    def __init__(self, runner: CommandRunner | None = None) -> None:
        self._runner = runner or CommandRunner()

    def _busctl(self, args: list[str]) -> str:
        completed = self._runner(["busctl", *args])
        if completed.returncode != 0:
            raise RuntimeError(completed.stderr.strip() or completed.stdout.strip() or "busctl failed")
        return completed.stdout

    def _dbus_get_unix_user(self, sender: str) -> int:
        output = self._busctl(
            [
                "--system",
                "call",
                "org.freedesktop.DBus",
                "/org/freedesktop/DBus",
                "org.freedesktop.DBus",
                "GetConnectionUnixUser",
                "s",
                sender,
            ]
        )
        return int(_parse_busctl_scalar(output))

    def _dbus_get_unix_pid(self, sender: str) -> int:
        output = self._busctl(
            [
                "--system",
                "call",
                "org.freedesktop.DBus",
                "/org/freedesktop/DBus",
                "org.freedesktop.DBus",
                "GetConnectionUnixProcessID",
                "s",
                sender,
            ]
        )
        return int(_parse_busctl_scalar(output))

    def _login1_session_path(self, pid: int) -> str:
        output = self._busctl(
            [
                "--system",
                "call",
                "org.freedesktop.login1",
                "/org/freedesktop/login1",
                "org.freedesktop.login1.Manager",
                "GetSessionByPID",
                "u",
                str(pid),
            ]
        )
        return _parse_busctl_scalar(output)

    def _login1_user_path(self, pid: int) -> str:
        output = self._busctl(
            [
                "--system",
                "call",
                "org.freedesktop.login1",
                "/org/freedesktop/login1",
                "org.freedesktop.login1.Manager",
                "GetUserByPID",
                "u",
                str(pid),
            ]
        )
        return _parse_busctl_scalar(output)

    def _login1_bool(self, session_path: str, prop: str) -> bool:
        output = self._busctl(
            [
                "--system",
                "get-property",
                "org.freedesktop.login1",
                session_path,
                "org.freedesktop.login1.Session",
                prop,
            ]
        )
        return _parse_busctl_scalar(output).lower() == "true"

    def _login1_user_display_session_path(self, user_path: str) -> str | None:
        output = self._busctl(
            [
                "--system",
                "get-property",
                "org.freedesktop.login1",
                user_path,
                "org.freedesktop.login1.User",
                "Display",
            ]
        )
        paths = _parse_busctl_object_paths(output)
        if not paths or paths[-1] == "/":
            return None
        return paths[-1]

    def _login1_user_session_paths(self, user_path: str) -> list[str]:
        output = self._busctl(
            [
                "--system",
                "get-property",
                "org.freedesktop.login1",
                user_path,
                "org.freedesktop.login1.User",
                "Sessions",
            ]
        )
        return [path for path in _parse_busctl_object_paths(output) if path != "/"]

    def _resolve_session_path(self, pid: int) -> str:
        try:
            return self._login1_session_path(pid)
        except RuntimeError as session_error:
            user_path = self._login1_user_path(pid)
            display_path = self._login1_user_display_session_path(user_path)
            if display_path:
                return display_path
            session_paths = self._login1_user_session_paths(user_path)
            if session_paths:
                return session_paths[0]
            raise session_error

    def resolve_identity(self, sender: str) -> CallerIdentity:
        uid = self._dbus_get_unix_user(sender)
        pid = self._dbus_get_unix_pid(sender)
        return CallerIdentity(
            sender=sender,
            uid=uid,
            pid=pid,
            user_name=getpwuid(uid).pw_name,
            in_authorized_group=user_in_group(uid),
        )

    def resolve(self, sender: str) -> AuthorizationContext:
        identity = self.resolve_identity(sender)
        session_path = self._resolve_session_path(identity.pid)
        return AuthorizationContext(
            sender=identity.sender,
            uid=identity.uid,
            pid=identity.pid,
            user_name=identity.user_name,
            in_authorized_group=identity.in_authorized_group,
            session_active=self._login1_bool(session_path, "Active"),
            session_remote=self._login1_bool(session_path, "Remote"),
        )


class PkcheckAuthorizer:
    def __init__(self, runner: CommandRunner | None = None) -> None:
        self._runner = runner or CommandRunner()

    def authorize(self, sender: str) -> None:
        completed = self._runner(
            [
                "pkcheck",
                "--action-id",
                ACTION_SET_BOOST,
                "--system-bus-name",
                sender,
                "--allow-user-interaction",
            ]
        )
        if completed.returncode != 0:
            message = completed.stderr.strip() or completed.stdout.strip() or "pkcheck authorization failed"
            raise PermissionDeniedError(message)
