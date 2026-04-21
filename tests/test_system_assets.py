from pathlib import Path


def test_boost_switchd_unit_uses_simple_service_lifecycle():
    text = Path("system/systemd/boost-switchd.service").read_text(encoding="utf-8")
    assert "Type=simple" in text
    assert "BusName=" not in text
    assert "ExecStart=@PREFIX@/venv/bin/python -m boost_switch.service.main" in text


def test_service_main_module_has_python_module_entrypoint():
    text = Path("src/boost_switch/service/main.py").read_text(encoding="utf-8")
    assert 'if __name__ == "__main__":' in text
    assert "main()" in text


def test_gnome_extension_has_top_level_entrypoints():
    extension_entry = Path("gnome-extension/extension.js").read_text(encoding="utf-8")
    prefs_entry = Path("gnome-extension/prefs.js").read_text(encoding="utf-8")

    assert "export {default}" in extension_entry
    assert "./src/extension.js" in extension_entry
    assert "export {default}" in prefs_entry
    assert "./src/prefs.js" in prefs_entry


def test_gnome_extension_uses_computer_chip_icon_for_boost_entrypoints():
    extension_source = Path("gnome-extension/src/extension.js").read_text(encoding="utf-8")

    assert extension_source.count("computer-chip-symbolic") == 2
    assert "playback-speed-symbolic" not in extension_source
    assert "power-profile-performance-symbolic" not in extension_source
