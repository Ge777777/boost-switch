import json

from boost_switch.cli import boostctl


def test_boostctl_status_json(monkeypatch, capsys):
    monkeypatch.setattr(
        boostctl,
        "call_status",
        lambda: {"enabled": True, "reason": "ok", "backend": "polkit-dbus"},
    )

    assert boostctl.main(["status", "--json"]) == 0
    out = capsys.readouterr().out
    assert json.loads(out)["enabled"] is True


def test_boostctl_set_on(monkeypatch):
    calls = []

    def fake_set(value: bool):
        calls.append(value)
        return {"enabled": value, "reason": "ok", "backend": "polkit-dbus"}

    monkeypatch.setattr(boostctl, "call_set", fake_set)
    assert boostctl.main(["set", "on"]) == 0
    assert calls == [True]
