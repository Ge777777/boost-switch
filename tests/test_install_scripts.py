from pathlib import Path
from subprocess import run


def test_install_script_dry_run_mentions_policy_and_unit_files():
    completed = run(
        ["bash", "scripts/install/install_local.sh", "--dry-run", "--prefix", "/tmp/boost-switch"],
        check=False,
        capture_output=True,
        text=True,
    )
    assert completed.returncode == 0
    assert "io.github.ge777777.boostswitch.policy" in completed.stdout
    assert "boost-switchd.service" in completed.stdout
    assert "io.github.ge777777.BoostSwitch1.conf" in completed.stdout
    assert "/usr/local/bin/boostctl" in completed.stdout
    assert "/usr/local/bin/boost-switch-diag" in completed.stdout
    assert "glib-compile-schemas" in completed.stdout
    assert "chown -R" in completed.stdout
    assert "systemctl restart boost-switchd.service" in completed.stdout


def test_install_script_mentions_repo_local_uv_bootstrap():
    text = Path("scripts/install/install_local.sh").read_text(encoding="utf-8")

    assert ".tools/uv" in text
    assert "TOOL_UV_BIN" in text
    assert '/usr/bin/python3 -m venv "$TOOL_UV_ROOT"' in text
    assert '-m ensurepip --upgrade' in text
    assert '-m pip install --upgrade pip uv' in text
    assert 'chown -R "${target_user}:${target_group}" "$TOOL_UV_ROOT"' in text


def test_install_script_dry_run_mentions_repo_local_uv_bootstrap():
    completed = run(
        ["bash", "scripts/install/install_local.sh", "--dry-run", "--prefix", "/tmp/boost-switch"],
        check=False,
        capture_output=True,
        text=True,
    )

    assert completed.returncode == 0
    assert ".tools/uv/bin/uv" in completed.stdout
    assert "ensure repo-local uv" in completed.stdout
    assert ".tools/uv" in completed.stdout


def test_uninstall_script_dry_run_mentions_cleanup_targets():
    completed = run(
        ["bash", "scripts/install/uninstall_local.sh", "--dry-run", "--prefix", "/tmp/boost-switch"],
        check=False,
        capture_output=True,
        text=True,
    )
    assert completed.returncode == 0
    assert "Removing local install from /tmp/boost-switch" in completed.stdout
    assert "/usr/share/dbus-1/system.d/io.github.ge777777.BoostSwitch1.conf" in completed.stdout
    assert "/usr/local/bin/boostctl" in completed.stdout
    assert "/usr/local/bin/boost-switch-diag" in completed.stdout


def test_verify_host_script_mentions_extension_and_local_rule_checks():
    text = Path("scripts/verify/verify_host_integration.sh").read_text(encoding="utf-8")

    assert 'EXTENSION_UUID="${EXTENSION_UUID:-boost-switch@ge777777.github.io}"' in text
    assert 'gnome-extensions info "$EXTENSION_UUID"' in text
    assert 'gnome-extensions enable "$EXTENSION_UUID"' in text
    assert "50-boost-switch-local.rules" in text
    assert "--verify-local-rule" in text


def test_verify_host_script_mentions_local_rule_visibility_handling():
    text = Path("scripts/verify/verify_host_integration.sh").read_text(encoding="utf-8")

    assert 'LOCAL_RULE_PATH="${LOCAL_RULE_PATH:-/etc/polkit-1/rules.d/50-boost-switch-local.rules}"' in text
    assert "Unable to verify local polkit rule non-interactively" in text
    assert 'Review it manually with: sudo ls -l $LOCAL_RULE_PATH' in text
    assert "Continuing with runtime verification because the rule directory is not traversable to unprivileged users." not in text
    assert 'sudo -n test -f "$LOCAL_RULE_PATH"' in text


def test_verify_host_script_describes_manual_frontend_recheck():
    text = Path("scripts/verify/verify_host_integration.sh").read_text(encoding="utf-8")

    assert "Manual GNOME Quick Settings check still required" in text
    assert "boostctl set off/on only verifies the backend and authorization path" in text
