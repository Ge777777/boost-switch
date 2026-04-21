from dataclasses import dataclass
from time import time_ns

from boost_switch.contracts import make_diagnostics_payload, make_status_payload
from boost_switch.errors import SysfsMissingError
from boost_switch.sysfs import SysfsBoostRepository


@dataclass(slots=True)
class SubjectState:
    user_name: str = "unknown"
    uid: int = 0
    in_authorized_group: bool = False
    session_active: bool = False
    session_remote: bool = False


class BoostController:
    def __init__(self, repository: SysfsBoostRepository) -> None:
        self._repository = repository

    def get_status(self, *, source: str, can_toggle: bool = False) -> dict[str, object]:
        try:
            enabled = self._repository.read_enabled()
            return make_status_payload(
                supported=True,
                available=True,
                enabled=enabled,
                can_toggle=can_toggle,
                reason="ok",
                message="CPU Boost 可用",
                last_source=source,
                last_changed_usec=time_ns() // 1000,
            )
        except SysfsMissingError as exc:
            return make_status_payload(
                supported=False,
                available=False,
                enabled=False,
                can_toggle=False,
                reason=exc.code,
                message=exc.message,
                last_source=source,
                last_changed_usec=0,
            )

    def set_enabled(self, enabled: bool, *, source: str, can_toggle: bool) -> dict[str, object]:
        self._repository.write_enabled(enabled)
        return self.get_status(source=source, can_toggle=can_toggle)

    def get_diagnostics(self, subject: SubjectState) -> dict[str, object]:
        status = self.get_status(source="diagnostics", can_toggle=subject.in_authorized_group)
        return make_diagnostics_payload(
            supported=bool(status["supported"]),
            available=bool(status["available"]),
            enabled=bool(status["enabled"]),
            can_toggle=bool(status["can_toggle"]),
            reason=str(status["reason"]),
            message=str(status["message"]),
            user_name=subject.user_name,
            uid=subject.uid,
            in_authorized_group=subject.in_authorized_group,
            session_active=subject.session_active,
            session_remote=subject.session_remote,
        )
