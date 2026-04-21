import argparse
import asyncio
import json

from dbus_next.aio import MessageBus
from dbus_next.constants import BusType

from boost_switch.contracts import BUS_NAME, INTERFACE_NAME, OBJECT_PATH, from_variant_dict


async def _get_interface():
    bus = await MessageBus(bus_type=BusType.SYSTEM).connect()
    introspection = await bus.introspect(BUS_NAME, OBJECT_PATH)
    obj = bus.get_proxy_object(BUS_NAME, OBJECT_PATH, introspection)
    return bus, obj.get_interface(INTERFACE_NAME)


def call_status() -> dict[str, object]:
    async def _inner():
        bus, iface = await _get_interface()
        try:
            payload = await iface.call_get_status()
            return from_variant_dict(payload)
        finally:
            bus.disconnect()

    return asyncio.run(_inner())


def call_set(enabled: bool) -> dict[str, object]:
    async def _inner():
        bus, iface = await _get_interface()
        try:
            payload = await iface.call_set_boost(enabled)
            return from_variant_dict(payload)
        finally:
            bus.disconnect()

    return asyncio.run(_inner())


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="boostctl")
    sub = parser.add_subparsers(dest="command", required=True)

    status = sub.add_parser("status")
    status.add_argument("--json", action="store_true")

    set_parser = sub.add_parser("set")
    set_parser.add_argument("value", choices=["on", "off"])

    watch = sub.add_parser("watch")
    watch.add_argument("--interval", type=float, default=2.0)

    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "status":
        payload = call_status()
        print(json.dumps(payload, ensure_ascii=False))
        return 0
    if args.command == "set":
        payload = call_set(args.value == "on")
        print(json.dumps(payload, ensure_ascii=False))
        return 0 if payload.get("reason") == "ok" else 1
    if args.command == "watch":
        try:
            while True:
                print(json.dumps(call_status(), ensure_ascii=False))
                asyncio.run(asyncio.sleep(args.interval))
        except KeyboardInterrupt:
            return 0
    return 2
