import pytest
from dbus_next import DBusError

from boost_switch.service.authz import AuthorizationDecision, CallerIdentity
from boost_switch.service.main import BoostSwitchInterface, CallerCapture
from boost_switch.service.controller import BoostController
from boost_switch.sysfs import SysfsBoostRepository


def test_controller_builds_status_from_repository(tmp_path):
    boost_path = tmp_path / "devices/system/cpu/cpufreq/boost"
    boost_path.parent.mkdir(parents=True)
    boost_path.write_text("0\n", encoding="utf-8")

    controller = BoostController(SysfsBoostRepository(sysfs_root=tmp_path))
    payload = controller.get_status(source="test")

    assert payload["available"] is True
    assert payload["enabled"] is False
    assert payload["reason"] == "ok"


class FakeResolver:
    def __init__(self, *, identity):
        self.identity = identity
        self.resolve_identity_calls = []

    def resolve(self, sender: str):
        raise AssertionError("SetBoost should not require full session resolution")

    def resolve_identity(self, sender: str):
        self.resolve_identity_calls.append(sender)
        return self.identity


class FakeWriteEvaluator:
    def __init__(self, decision):
        self.decision = decision
        self.calls = []

    def evaluate(self, identity):
        self.calls.append(identity)
        return self.decision


class FakeStatusEvaluator:
    def evaluate(self, context):
        return AuthorizationDecision(True, "ok", "调用方满足基础条件")


class FakeAuthorizer:
    def __init__(self):
        self.calls = []

    def authorize(self, sender: str) -> None:
        self.calls.append(sender)


class FakeController:
    def get_status(self, *, source: str, can_toggle: bool = False):
        return {
            "supported": True,
            "available": True,
            "enabled": False,
            "can_toggle": can_toggle,
            "backend": "polkit-dbus",
            "reason": "ok",
            "message": "CPU Boost 可用",
            "last_source": source,
            "last_changed_usec": 0,
        }

    def get_diagnostics(self, subject):
        raise AssertionError("unexpected diagnostics call")

    def set_enabled(self, enabled: bool, *, source: str, can_toggle: bool):
        return {
            "supported": True,
            "available": True,
            "enabled": enabled,
            "can_toggle": can_toggle,
            "backend": "polkit-dbus",
            "reason": "ok",
            "message": "CPU Boost 可用",
            "last_source": source,
            "last_changed_usec": 0,
        }


def test_set_boost_uses_identity_resolution_before_pkcheck():
    identity = CallerIdentity(
        sender=":1.77",
        uid=1000,
        pid=53016,
        user_name="tester",
        in_authorized_group=True,
    )
    resolver = FakeResolver(identity=identity)
    write_evaluator = FakeWriteEvaluator(
        AuthorizationDecision(True, "ok", "调用方满足基础条件")
    )
    authorizer = FakeAuthorizer()
    caller_capture = CallerCapture(sender=":1.77")
    interface = BoostSwitchInterface(
        controller=FakeController(),
        caller_capture=caller_capture,
        subject_resolver=resolver,
        evaluator=FakeStatusEvaluator(),
        write_evaluator=write_evaluator,
        authorizer=authorizer,
    )

    payload = BoostSwitchInterface.SetBoost.__wrapped__(interface, True)

    assert resolver.resolve_identity_calls == [":1.77"]
    assert write_evaluator.calls == [identity]
    assert authorizer.calls == [":1.77"]
    assert payload["enabled"].value is True


def test_set_boost_rejects_user_outside_authorized_group():
    identity = CallerIdentity(
        sender=":1.88",
        uid=1000,
        pid=54000,
        user_name="tester",
        in_authorized_group=False,
    )
    resolver = FakeResolver(identity=identity)
    write_evaluator = FakeWriteEvaluator(
        AuthorizationDecision(False, "permission_denied", "当前用户不在授权组中")
    )
    authorizer = FakeAuthorizer()
    caller_capture = CallerCapture(sender=":1.88")
    interface = BoostSwitchInterface(
        controller=FakeController(),
        caller_capture=caller_capture,
        subject_resolver=resolver,
        evaluator=FakeStatusEvaluator(),
        write_evaluator=write_evaluator,
        authorizer=authorizer,
    )

    with pytest.raises(DBusError, match="当前用户不在授权组中"):
        BoostSwitchInterface.SetBoost.__wrapped__(interface, True)

    assert authorizer.calls == []
