import asyncio
from dataclasses import dataclass

from dbus_next import DBusError
from dbus_next.aio import MessageBus
from dbus_next.constants import BusType, ErrorType, MessageType
from dbus_next.service import ServiceInterface, method, signal

from boost_switch.contracts import BUS_NAME, INTERFACE_NAME, OBJECT_PATH, to_variant_dict
from boost_switch.errors import BoostSwitchError
from boost_switch.service.authz import (
    GroupEvaluator,
    PkcheckAuthorizer,
    SenderContextResolver,
    SubjectEvaluator,
)
from boost_switch.service.controller import BoostController
from boost_switch.sysfs import SysfsBoostRepository


@dataclass(slots=True)
class CallerCapture:
    sender: str | None = None

    def capture(self, msg) -> bool:
        if (
            msg.message_type == MessageType.METHOD_CALL
            and msg.path == OBJECT_PATH
            and msg.interface == INTERFACE_NAME
        ):
            self.sender = msg.sender
        return False


class BoostSwitchInterface(ServiceInterface):
    def __init__(
        self,
        controller: BoostController,
        caller_capture: CallerCapture,
        subject_resolver: SenderContextResolver,
        evaluator: SubjectEvaluator,
        write_evaluator: GroupEvaluator,
        authorizer: PkcheckAuthorizer,
    ) -> None:
        super().__init__(INTERFACE_NAME)
        self._controller = controller
        self._caller_capture = caller_capture
        self._subject_resolver = subject_resolver
        self._evaluator = evaluator
        self._write_evaluator = write_evaluator
        self._authorizer = authorizer

    def _current_sender(self) -> str:
        if not self._caller_capture.sender:
            raise DBusError(ErrorType.ACCESS_DENIED, "无法识别当前调用方")
        return self._caller_capture.sender

    def _authorized_subject(self):
        sender = self._current_sender()
        identity = self._subject_resolver.resolve_identity(sender)
        decision = self._write_evaluator.evaluate(identity)
        if not decision.allowed:
            raise DBusError(ErrorType.ACCESS_DENIED, decision.message)
        return sender, identity

    @method()
    def GetStatus(self) -> "a{sv}":
        sender = self._current_sender()
        context = self._subject_resolver.resolve(sender)
        decision = self._evaluator.evaluate(context)
        payload = self._controller.get_status(
            source="dbus",
            can_toggle=decision.allowed,
        )
        return to_variant_dict(payload)

    @method()
    def GetDiagnostics(self) -> "a{sv}":
        sender = self._current_sender()
        context = self._subject_resolver.resolve(sender)
        payload = self._controller.get_diagnostics(context)
        return to_variant_dict(payload)

    @method()
    def SetBoost(self, enabled: "b") -> "a{sv}":
        sender, _context = self._authorized_subject()
        try:
            self._authorizer.authorize(sender)
            payload = self._controller.set_enabled(enabled, source="dbus", can_toggle=True)
        except BoostSwitchError as exc:
            raise DBusError(ErrorType.FAILED, exc.message) from exc
        self.StatusChanged(to_variant_dict(payload))
        return to_variant_dict(payload)

    @signal()
    def StatusChanged(self, status: "a{sv}") -> "a{sv}":
        return status


async def main_async() -> None:
    bus = await MessageBus(bus_type=BusType.SYSTEM).connect()
    caller_capture = CallerCapture()
    bus.add_message_handler(caller_capture.capture)
    interface = BoostSwitchInterface(
        controller=BoostController(SysfsBoostRepository()),
        caller_capture=caller_capture,
        subject_resolver=SenderContextResolver(),
        evaluator=SubjectEvaluator(),
        write_evaluator=GroupEvaluator(),
        authorizer=PkcheckAuthorizer(),
    )
    bus.export(OBJECT_PATH, interface)
    await bus.request_name(BUS_NAME)
    await asyncio.get_running_loop().create_future()


def main() -> None:
    asyncio.run(main_async())


if __name__ == "__main__":
    main()
