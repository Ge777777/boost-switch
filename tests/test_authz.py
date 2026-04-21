from types import SimpleNamespace

import pytest

from boost_switch.service import authz
from boost_switch.service.authz import (
    AuthorizationContext,
    AuthorizationDecision,
    CallerIdentity,
    GroupEvaluator,
    SenderContextResolver,
    SubjectEvaluator,
)


class FakeRunner:
    def __init__(self, responses):
        self._responses = responses
        self.calls = []

    def __call__(self, args):
        key = tuple(args)
        self.calls.append(key)
        response = self._responses[key]
        return SimpleNamespace(
            returncode=response.get("returncode", 0),
            stdout=response.get("stdout", ""),
            stderr=response.get("stderr", ""),
        )


def test_subject_evaluator_rejects_inactive_session():
    context = AuthorizationContext(
        sender=":1.51",
        uid=1000,
        pid=4242,
        user_name="tester",
        in_authorized_group=True,
        session_active=False,
        session_remote=False,
    )

    decision = SubjectEvaluator().evaluate(context)
    assert decision.allowed is False
    assert decision.reason == "inactive_session"


def test_subject_evaluator_accepts_local_active_authorized_user():
    context = AuthorizationContext(
        sender=":1.88",
        uid=1000,
        pid=9999,
        user_name="tester",
        in_authorized_group=True,
        session_active=True,
        session_remote=False,
    )

    decision = SubjectEvaluator().evaluate(context)
    assert decision.allowed is True
    assert decision.reason == "ok"


def test_group_evaluator_rejects_user_outside_authorized_group():
    identity = CallerIdentity(
        sender=":1.15",
        uid=1000,
        pid=4321,
        user_name="tester",
        in_authorized_group=False,
    )

    decision = GroupEvaluator().evaluate(identity)

    assert decision == AuthorizationDecision(
        allowed=False,
        reason="permission_denied",
        message="当前用户不在授权组中",
    )


def test_sender_context_resolver_falls_back_to_user_display_session(monkeypatch):
    monkeypatch.setattr(authz, "getpwuid", lambda uid: SimpleNamespace(pw_name="tester"))
    monkeypatch.setattr(authz, "user_in_group", lambda uid: True)
    runner = FakeRunner(
        {
            (
                "busctl",
                "--system",
                "call",
                "org.freedesktop.DBus",
                "/org/freedesktop/DBus",
                "org.freedesktop.DBus",
                "GetConnectionUnixUser",
                "s",
                ":1.51",
            ): {"stdout": "u 1000\n"},
            (
                "busctl",
                "--system",
                "call",
                "org.freedesktop.DBus",
                "/org/freedesktop/DBus",
                "org.freedesktop.DBus",
                "GetConnectionUnixProcessID",
                "s",
                ":1.51",
            ): {"stdout": "u 53016\n"},
            (
                "busctl",
                "--system",
                "call",
                "org.freedesktop.login1",
                "/org/freedesktop/login1",
                "org.freedesktop.login1.Manager",
                "GetSessionByPID",
                "u",
                "53016",
            ): {
                "returncode": 1,
                "stderr": "Call failed: PID 53016 does not belong to any known session.\n",
            },
            (
                "busctl",
                "--system",
                "call",
                "org.freedesktop.login1",
                "/org/freedesktop/login1",
                "org.freedesktop.login1.Manager",
                "GetUserByPID",
                "u",
                "53016",
            ): {"stdout": 'o "/org/freedesktop/login1/user/_1000"\n'},
            (
                "busctl",
                "--system",
                "get-property",
                "org.freedesktop.login1",
                "/org/freedesktop/login1/user/_1000",
                "org.freedesktop.login1.User",
                "Display",
            ): {"stdout": '(so) "5" "/org/freedesktop/login1/session/_35"\n'},
            (
                "busctl",
                "--system",
                "get-property",
                "org.freedesktop.login1",
                "/org/freedesktop/login1/session/_35",
                "org.freedesktop.login1.Session",
                "Active",
            ): {"stdout": "b true\n"},
            (
                "busctl",
                "--system",
                "get-property",
                "org.freedesktop.login1",
                "/org/freedesktop/login1/session/_35",
                "org.freedesktop.login1.Session",
                "Remote",
            ): {"stdout": "b false\n"},
        }
    )

    context = SenderContextResolver(runner=runner).resolve(":1.51")

    assert context.user_name == "tester"
    assert context.pid == 53016
    assert context.in_authorized_group is True
    assert context.session_active is True
    assert context.session_remote is False


def test_sender_context_resolver_falls_back_to_user_sessions_when_display_missing(monkeypatch):
    monkeypatch.setattr(authz, "getpwuid", lambda uid: SimpleNamespace(pw_name="tester"))
    monkeypatch.setattr(authz, "user_in_group", lambda uid: True)
    runner = FakeRunner(
        {
            (
                "busctl",
                "--system",
                "call",
                "org.freedesktop.DBus",
                "/org/freedesktop/DBus",
                "org.freedesktop.DBus",
                "GetConnectionUnixUser",
                "s",
                ":1.61",
            ): {"stdout": "u 1000\n"},
            (
                "busctl",
                "--system",
                "call",
                "org.freedesktop.DBus",
                "/org/freedesktop/DBus",
                "org.freedesktop.DBus",
                "GetConnectionUnixProcessID",
                "s",
                ":1.61",
            ): {"stdout": "u 54000\n"},
            (
                "busctl",
                "--system",
                "call",
                "org.freedesktop.login1",
                "/org/freedesktop/login1",
                "org.freedesktop.login1.Manager",
                "GetSessionByPID",
                "u",
                "54000",
            ): {
                "returncode": 1,
                "stderr": "Call failed: PID 54000 does not belong to any known session.\n",
            },
            (
                "busctl",
                "--system",
                "call",
                "org.freedesktop.login1",
                "/org/freedesktop/login1",
                "org.freedesktop.login1.Manager",
                "GetUserByPID",
                "u",
                "54000",
            ): {"stdout": 'o "/org/freedesktop/login1/user/_1000"\n'},
            (
                "busctl",
                "--system",
                "get-property",
                "org.freedesktop.login1",
                "/org/freedesktop/login1/user/_1000",
                "org.freedesktop.login1.User",
                "Display",
            ): {"stdout": '(so) "" "/"\n'},
            (
                "busctl",
                "--system",
                "get-property",
                "org.freedesktop.login1",
                "/org/freedesktop/login1/user/_1000",
                "org.freedesktop.login1.User",
                "Sessions",
            ): {"stdout": 'a(so) 1 "5" "/org/freedesktop/login1/session/_35"\n'},
            (
                "busctl",
                "--system",
                "get-property",
                "org.freedesktop.login1",
                "/org/freedesktop/login1/session/_35",
                "org.freedesktop.login1.Session",
                "Active",
            ): {"stdout": "b true\n"},
            (
                "busctl",
                "--system",
                "get-property",
                "org.freedesktop.login1",
                "/org/freedesktop/login1/session/_35",
                "org.freedesktop.login1.Session",
                "Remote",
            ): {"stdout": "b false\n"},
        }
    )

    context = SenderContextResolver(runner=runner).resolve(":1.61")

    assert context.session_active is True
    assert context.session_remote is False
