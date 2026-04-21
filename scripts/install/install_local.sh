#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)
PREFIX=/usr/lib/boost-switch
ENABLE_LOCAL_RULE=0
ADD_CURRENT_USER=0
DRY_RUN=0
TOOL_UV_ROOT="$ROOT_DIR/.tools/uv"
TOOL_UV_BIN="$TOOL_UV_ROOT/bin/uv"
TOOL_PYTHON_BIN="$TOOL_UV_ROOT/bin/python"

POLICY_DST=/usr/share/polkit-1/actions/io.github.ge777777.boostswitch.policy
RULE_DST=/etc/polkit-1/rules.d/50-boost-switch-local.rules
DBUS_POLICY_DST=/usr/share/dbus-1/system.d/io.github.ge777777.BoostSwitch1.conf
SYSTEMD_DST=/etc/systemd/system/boost-switchd.service
DBUS_SERVICE_DST=/usr/share/dbus-1/system-services/io.github.ge777777.BoostSwitch1.service
BOOSTCTL_WRAPPER_DST=/usr/local/bin/boostctl
DIAG_WRAPPER_DST=/usr/local/bin/boost-switch-diag
EXTENSION_UUID=boost-switch@ge777777.github.io

log() {
    printf '%s\n' "$*"
}

fail() {
    printf '%s\n' "$*" >&2
    exit 1
}

run_cmd() {
    log "+ $*"
    if [[ "$DRY_RUN" -eq 0 ]]; then
        "$@"
    fi
}

render_unit() {
    sed "s#@PREFIX@#${PREFIX}#g" "$ROOT_DIR/system/systemd/boost-switchd.service"
}

install_rendered_unit() {
    log "+ install rendered unit $SYSTEMD_DST"
    if [[ "$DRY_RUN" -eq 0 ]]; then
        render_unit | install -D -m 0644 /dev/stdin "$SYSTEMD_DST"
    fi
}

install_wrapper() {
    local dst="$1"
    local target="$2"

    log "+ install wrapper $dst -> $target"
    if [[ "$DRY_RUN" -eq 0 ]]; then
        install -D -m 0755 /dev/stdin "$dst" <<EOF
#!/usr/bin/env bash
exec "$target" "\$@"
EOF
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

ensure_tool_uv_owner() {
    if [[ "$DRY_RUN" -eq 1 ]]; then
        log "+ chown -R ${target_user}:${target_group} $TOOL_UV_ROOT"
        return 0
    fi

    if [[ "$EUID" -eq 0 ]]; then
        run_cmd chown -R "${target_user}:${target_group}" "$TOOL_UV_ROOT"
    fi
}

ensure_repo_local_uv() {
    log "+ ensure repo-local uv at $TOOL_UV_ROOT"

    if [[ "$DRY_RUN" -eq 1 ]]; then
        log "+ /usr/bin/python3 -m venv $TOOL_UV_ROOT"
        log "+ $TOOL_PYTHON_BIN -m ensurepip --upgrade"
        log "+ $TOOL_PYTHON_BIN -m pip install --upgrade pip uv"
        log "+ use repo-local uv $TOOL_UV_BIN"
        ensure_tool_uv_owner
        return 0
    fi

    if [[ -x "$TOOL_UV_BIN" ]]; then
        log "Using repo-local uv at $TOOL_UV_BIN"
        ensure_tool_uv_owner
        return 0
    fi

    [[ -x /usr/bin/python3 ]] || fail "Missing required interpreter: /usr/bin/python3"

    run_cmd install -d "$(dirname "$TOOL_UV_ROOT")"

    log "+ /usr/bin/python3 -m venv $TOOL_UV_ROOT"
    if ! /usr/bin/python3 -m venv "$TOOL_UV_ROOT"; then
        fail "Python venv module is unavailable. Install python3-venv first."
    fi

    log "+ $TOOL_PYTHON_BIN -m ensurepip --upgrade"
    if ! "$TOOL_PYTHON_BIN" -m ensurepip --upgrade; then
        fail "Failed to bootstrap repo-local pip at $TOOL_UV_ROOT"
    fi

    log "+ $TOOL_PYTHON_BIN -m pip install --upgrade pip uv"
    if ! "$TOOL_PYTHON_BIN" -m pip install --upgrade pip uv; then
        fail "Failed to bootstrap repo-local uv at $TOOL_UV_ROOT"
    fi

    [[ -x "$TOOL_UV_BIN" ]] || fail "Failed to bootstrap repo-local uv at $TOOL_UV_ROOT"
    ensure_tool_uv_owner
}

while [[ $# -gt 0 ]]; do
    case "$1" in
        --prefix) PREFIX="$2"; shift 2 ;;
        --enable-local-rule) ENABLE_LOCAL_RULE=1; shift ;;
        --add-current-user) ADD_CURRENT_USER=1; shift ;;
        --dry-run) DRY_RUN=1; shift ;;
        *) echo "Unknown arg: $1" >&2; exit 1 ;;
    esac
done

log "Installing boost-switch into ${PREFIX}"
log "Using policy file system/polkit/io.github.ge777777.boostswitch.policy"
log "Using D-Bus policy file system/dbus/io.github.ge777777.BoostSwitch1.conf"
log "Using unit file system/systemd/boost-switchd.service"
log "Using D-Bus service file system/systemd/io.github.ge777777.BoostSwitch1.service"
log "Will install CLI wrappers ${BOOSTCTL_WRAPPER_DST} and ${DIAG_WRAPPER_DST}"

if [[ "$ENABLE_LOCAL_RULE" -eq 1 ]]; then
    log "Enabling local no-prompt rule for group boost-switch"
fi

if [[ "$ADD_CURRENT_USER" -eq 1 ]]; then
    log "Adding current user to group boost-switch"
fi

target_user="${SUDO_USER:-$USER}"
target_group=$(id -gn "$target_user")

run_cmd install -d "$PREFIX"
ensure_repo_local_uv
run_cmd "$TOOL_UV_BIN" venv --python /usr/bin/python3 --clear "$PREFIX/venv"
run_cmd "$TOOL_UV_BIN" pip install --python "$PREFIX/venv/bin/python" "$ROOT_DIR"

run_cmd install -D -m 0644 "$ROOT_DIR/system/polkit/io.github.ge777777.boostswitch.policy" "$POLICY_DST"
run_cmd install -D -m 0644 "$ROOT_DIR/system/dbus/io.github.ge777777.BoostSwitch1.conf" "$DBUS_POLICY_DST"
install_rendered_unit
run_cmd install -D -m 0644 "$ROOT_DIR/system/systemd/io.github.ge777777.BoostSwitch1.service" "$DBUS_SERVICE_DST"
install_wrapper "$BOOSTCTL_WRAPPER_DST" "$PREFIX/venv/bin/boostctl"
install_wrapper "$DIAG_WRAPPER_DST" "$PREFIX/venv/bin/boost-switch-diag"

if ! getent group boost-switch >/dev/null; then
    run_cmd groupadd --system boost-switch
fi

if [[ "$ADD_CURRENT_USER" -eq 1 ]]; then
    run_cmd usermod -aG boost-switch "$target_user"
fi

if [[ "$ENABLE_LOCAL_RULE" -eq 1 ]]; then
    run_cmd install -D -m 0644 "$ROOT_DIR/system/polkit/50-boost-switch-local.rules.template" "$RULE_DST"
fi

extension_home=$(current_user_home)
extension_dir="${extension_home}/.local/share/gnome-shell/extensions/${EXTENSION_UUID}"
run_cmd install -d "$extension_dir"
run_cmd cp -r "$ROOT_DIR/gnome-extension/." "$extension_dir/"
run_cmd glib-compile-schemas "$extension_dir/schemas"
run_cmd chown -R "${target_user}:${target_group}" "$extension_dir"

run_cmd systemctl daemon-reload
reload_dbus_config
run_cmd systemctl enable boost-switchd.service
run_cmd systemctl restart boost-switchd.service

log "Install complete. Re-login to GNOME if group membership changed."
