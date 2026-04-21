import asyncio
import json

from dbus_next.aio import MessageBus
from dbus_next.constants import BusType

from boost_switch.contracts import BUS_NAME, INTERFACE_NAME, OBJECT_PATH, from_variant_dict


def call_diagnostics() -> dict[str, object]:
    async def _inner():
        bus = await MessageBus(bus_type=BusType.SYSTEM).connect()
        introspection = await bus.introspect(BUS_NAME, OBJECT_PATH)
        obj = bus.get_proxy_object(BUS_NAME, OBJECT_PATH, introspection)
        iface = obj.get_interface(INTERFACE_NAME)
        try:
            payload = await iface.call_get_diagnostics()
            return from_variant_dict(payload)
        finally:
            bus.disconnect()

    return asyncio.run(_inner())


def main() -> int:
    print(json.dumps(call_diagnostics(), ensure_ascii=False))
    return 0
