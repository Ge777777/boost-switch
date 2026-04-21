from boost_switch.contracts import (
    ACTION_SET_BOOST,
    BUS_NAME,
    INTERFACE_NAME,
    OBJECT_PATH,
    make_diagnostics_payload,
    make_status_payload,
)


def test_status_payload_contains_required_keys():
    payload = make_status_payload(
        supported=True,
        available=True,
        enabled=False,
        can_toggle=False,
        reason="inactive_session",
        message="当前会话未激活",
        last_source="test",
        last_changed_usec=0,
    )

    assert BUS_NAME == "io.github.ge777777.BoostSwitch1"
    assert OBJECT_PATH == "/io/github/ge777777/BoostSwitch1"
    assert INTERFACE_NAME == "io.github.ge777777.BoostSwitch1.Control"
    assert ACTION_SET_BOOST == "io.github.ge777777.boostswitch.set"
    assert payload["backend"] == "polkit-dbus"
    assert payload["reason"] == "inactive_session"


def test_diagnostics_payload_contains_authorization_flags():
    payload = make_diagnostics_payload(
        supported=True,
        available=True,
        enabled=True,
        can_toggle=False,
        reason="permission_denied",
        message="当前用户不在授权组中",
        user_name="tester",
        uid=1000,
        in_authorized_group=False,
        session_active=True,
        session_remote=False,
    )

    assert payload["user_name"] == "tester"
    assert payload["uid"] == 1000
    assert payload["in_authorized_group"] is False
    assert payload["session_active"] is True
