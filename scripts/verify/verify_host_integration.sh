#!/usr/bin/env bash
set -euo pipefail

ALLOW_REAL_TOGGLE=0
ENABLE_EXTENSION=0
VERIFY_LOCAL_RULE=0
EXTENSION_UUID="${EXTENSION_UUID:-boost-switch@ge777777.github.io}"
LOCAL_RULE_PATH="${LOCAL_RULE_PATH:-/etc/polkit-1/rules.d/50-boost-switch-local.rules}"

while [[ $# -gt 0 ]]; do
    case "$1" in
        --allow-real-toggle) ALLOW_REAL_TOGGLE=1; shift ;;
        --enable-extension) ENABLE_EXTENSION=1; shift ;;
        --verify-local-rule) VERIFY_LOCAL_RULE=1; shift ;;
        *) echo "Unknown arg: $1" >&2; exit 1 ;;
    esac
done

warn_extension_not_visible() {
    echo "The running GNOME Shell session has not picked up $EXTENSION_UUID yet." >&2
    echo "If this was the first install or you just updated the extension directory, re-login to the GNOME session and retry." >&2
}

warn_manual_frontend_recheck() {
    echo "Manual GNOME Quick Settings check still required."
    echo "boostctl set off/on only verifies the backend and authorization path."
    echo "In the active GNOME session, manually click the Quick Settings toggle and confirm whether an extra polkit prompt appears."
}

verify_local_rule() {
    local rule_dir
    local sudo_check_output
    local sudo_check_rc

    if [[ -f "$LOCAL_RULE_PATH" ]]; then
        echo "Found local polkit rule: $LOCAL_RULE_PATH"
        return 0
    fi

    rule_dir=$(dirname "$LOCAL_RULE_PATH")
    if [[ -d "$rule_dir" && ! -x "$rule_dir" ]]; then
        set +e
        sudo_check_output=$(sudo -n test -f "$LOCAL_RULE_PATH" 2>&1)
        sudo_check_rc=$?
        set -e
        if [[ "$sudo_check_rc" -eq 0 ]]; then
            echo "Found local polkit rule via privileged check: $LOCAL_RULE_PATH"
            return 0
        fi
        if [[ "$sudo_check_rc" -eq 1 && -z "$sudo_check_output" ]]; then
            echo "Missing local polkit rule: $LOCAL_RULE_PATH" >&2
            return 1
        fi
        echo "Unable to verify local polkit rule non-interactively: $LOCAL_RULE_PATH" >&2
        echo "Review it manually with: sudo ls -l $LOCAL_RULE_PATH" >&2
        echo "Re-run --verify-local-rule once that command can confirm the file exists." >&2
        return 1
    fi

    echo "Missing local polkit rule: $LOCAL_RULE_PATH" >&2
    return 1
}

systemctl status boost-switchd.service --no-pager
busctl --system tree io.github.ge777777.BoostSwitch1
boostctl status --json

if ! gnome-extensions info "$EXTENSION_UUID"; then
    warn_extension_not_visible
    if [[ "$ENABLE_EXTENSION" -eq 1 ]]; then
        exit 1
    fi
fi

if [[ "$ENABLE_EXTENSION" -eq 1 ]]; then
    gnome-extensions enable "$EXTENSION_UUID"
fi

if [[ "$VERIFY_LOCAL_RULE" -eq 1 ]]; then
    if ! verify_local_rule; then
        exit 1
    fi
    echo "Local rule path confirmed. Front-end Quick Settings behavior still needs a manual check in the active GNOME session."
fi

if [[ "$ALLOW_REAL_TOGGLE" -eq 1 ]]; then
    boostctl set off
    boostctl set on
else
    echo "Skipping real host toggle. Re-run with --allow-real-toggle for explicit integration verification."
fi

if [[ "$ENABLE_EXTENSION" -eq 1 || "$VERIFY_LOCAL_RULE" -eq 1 ]]; then
    warn_manual_frontend_recheck
fi
