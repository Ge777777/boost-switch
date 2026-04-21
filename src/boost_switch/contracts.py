from dbus_next import Variant

BUS_NAME = "io.github.ge777777.BoostSwitch1"
OBJECT_PATH = "/io/github/ge777777/BoostSwitch1"
INTERFACE_NAME = "io.github.ge777777.BoostSwitch1.Control"
ACTION_SET_BOOST = "io.github.ge777777.boostswitch.set"
AUTHORIZED_GROUP = "boost-switch"
SYSFS_BOOST_PATH = "/sys/devices/system/cpu/cpufreq/boost"
BACKEND_NAME = "polkit-dbus"

STATUS_KEYS = (
    "supported",
    "available",
    "enabled",
    "can_toggle",
    "backend",
    "reason",
    "message",
    "last_source",
    "last_changed_usec",
)

STATUS_SIGNATURES = {
    "supported": "b",
    "available": "b",
    "enabled": "b",
    "can_toggle": "b",
    "backend": "s",
    "reason": "s",
    "message": "s",
    "last_source": "s",
    "last_changed_usec": "t",
}

DIAGNOSTICS_SIGNATURES = {
    **STATUS_SIGNATURES,
    "user_name": "s",
    "uid": "u",
    "in_authorized_group": "b",
    "session_active": "b",
    "session_remote": "b",
}


def make_status_payload(
    *,
    supported: bool,
    available: bool,
    enabled: bool,
    can_toggle: bool,
    reason: str,
    message: str,
    last_source: str,
    last_changed_usec: int,
) -> dict[str, object]:
    return {
        "supported": supported,
        "available": available,
        "enabled": enabled,
        "can_toggle": can_toggle,
        "backend": BACKEND_NAME,
        "reason": reason,
        "message": message,
        "last_source": last_source,
        "last_changed_usec": last_changed_usec,
    }


def make_diagnostics_payload(
    *,
    supported: bool,
    available: bool,
    enabled: bool,
    can_toggle: bool,
    reason: str,
    message: str,
    user_name: str,
    uid: int,
    in_authorized_group: bool,
    session_active: bool,
    session_remote: bool,
) -> dict[str, object]:
    payload = make_status_payload(
        supported=supported,
        available=available,
        enabled=enabled,
        can_toggle=can_toggle,
        reason=reason,
        message=message,
        last_source="diagnostics",
        last_changed_usec=0,
    )
    payload.update(
        {
            "user_name": user_name,
            "uid": uid,
            "in_authorized_group": in_authorized_group,
            "session_active": session_active,
            "session_remote": session_remote,
        }
    )
    return payload


def to_variant_dict(payload: dict[str, object]) -> dict[str, Variant]:
    signatures = DIAGNOSTICS_SIGNATURES if "uid" in payload else STATUS_SIGNATURES
    return {key: Variant(signatures[key], value) for key, value in payload.items()}


def from_variant_dict(payload: dict[str, object]) -> dict[str, object]:
    normalized: dict[str, object] = {}
    for key, value in payload.items():
        normalized[key] = value.value if hasattr(value, "value") else value
    return normalized
