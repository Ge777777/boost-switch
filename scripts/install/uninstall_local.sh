#!/usr/bin/env bash
set -euo pipefail

PREFIX=/usr/lib/boost-switch
DRY_RUN=0
EXTENSION_UUID=boost-switch@ge777777.github.io
DBUS_POLICY_DST=/usr/share/dbus-1/system.d/io.github.ge777777.BoostSwitch1.conf
BOOSTCTL_WRAPPER_DST=/usr/local/bin/boostctl
DIAG_WRAPPER_DST=/usr/local/bin/boost-switch-diag

log() {
    printf '%s\n' "$*"
}

run_cmd() {
    log "+ $*"
    if [[ "$DRY_RUN" -eq 0 ]]; then
        "$@"
    fi
}

reload_dbus_config() {
    run_cmd busctl call org.freedesktop.DBus /org/freedesktop/DBus org.freedesktop.DBus ReloadConfig
}

current_user_home() {
    if [[ -n "${SUDO_USER:-}" ]]; then
        getent passwd "$SUDO_USER" | cut -d: -f6
    else
        printf '%s\n' "$HOME"
    fi
}

while [[ $# -gt 0 ]]; do
    case "$1" in
        --prefix) PREFIX="$2"; shift 2 ;;
        --dry-run) DRY_RUN=1; shift ;;
        *) echo "Unknown arg: $1" >&2; exit 1 ;;
    esac
done

printf 'Removing local install from %s\n' "$PREFIX"
printf 'Would remove %s\n' /usr/share/polkit-1/actions/io.github.ge777777.boostswitch.policy
printf 'Would remove %s\n' /etc/polkit-1/rules.d/50-boost-switch-local.rules
printf 'Would remove %s\n' /etc/systemd/system/boost-switchd.service
printf 'Would remove %s\n' /usr/share/dbus-1/system-services/io.github.ge777777.BoostSwitch1.service
printf 'Would remove %s\n' "$DBUS_POLICY_DST"
printf 'Would remove %s\n' "$BOOSTCTL_WRAPPER_DST"
printf 'Would remove %s\n' "$DIAG_WRAPPER_DST"

run_cmd systemctl disable --now boost-switchd.service || true
run_cmd rm -f /etc/systemd/system/boost-switchd.service
run_cmd rm -f /usr/share/dbus-1/system-services/io.github.ge777777.BoostSwitch1.service
run_cmd rm -f /usr/share/polkit-1/actions/io.github.ge777777.boostswitch.policy
run_cmd rm -f /etc/polkit-1/rules.d/50-boost-switch-local.rules
run_cmd rm -f "$DBUS_POLICY_DST"
run_cmd rm -f "$BOOSTCTL_WRAPPER_DST"
run_cmd rm -f "$DIAG_WRAPPER_DST"
run_cmd rm -rf "$PREFIX"

extension_home=$(current_user_home)
run_cmd rm -rf "${extension_home}/.local/share/gnome-shell/extensions/${EXTENSION_UUID}"
run_cmd systemctl daemon-reload
reload_dbus_config
