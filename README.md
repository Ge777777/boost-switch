# boost-switch

English | [简体中文](README.zh-CN.md)

`boost-switch` is a local-first Ubuntu 24 project for toggling CPU Boost through a GNOME Shell Quick Settings entry, with a system-bus privileged service as the only writer to `/sys`.

## Current Status

This repository already includes a local install path, CLI checks, and host-integration verification for the current mainline workflow. It is still an evolving mainline implementation rather than a stable packaged release.

- GNOME Shell Quick Settings extension as the primary desktop entry
- privileged `system bus + polkit + systemd` backend for writes
- `boostctl` and diagnostics CLI for verification and troubleshooting
- repo-local `.tools/uv/` bootstrap for install-time tooling, while runtime code stays in `/usr/lib/boost-switch/venv`

## Supported Scope

- Ubuntu 24 hosts with GNOME Shell
- machines that expose `/sys/devices/system/cpu/cpufreq/boost`

Currently out of scope:

- non-GNOME desktop environments
- hosts that do not expose `/sys/devices/system/cpu/cpufreq/boost`
- migration by copying an existing runtime tree without re-running the install script

## Quick Start

Make sure the host provides `/usr/bin/python3`, `python3-venv`, `gjs`, `glib-compile-schemas`, `systemctl`, and `polkit`. The install flow bootstraps repo-local `.tools/uv/` automatically, so it does not require a preinstalled user-level `uv`.

Install with the mainline default:

```bash
sudo bash scripts/install/install_local.sh --prefix /usr/lib/boost-switch
```

Common local options:

```bash
sudo bash scripts/install/install_local.sh --prefix /usr/lib/boost-switch --enable-local-rule
sudo bash scripts/install/install_local.sh --prefix /usr/lib/boost-switch --enable-local-rule --add-current-user
```

`--enable-local-rule` is an explicit local convenience mode, not the default security baseline. It installs a local polkit rule that directly allows boost toggles for local active users in the `boost-switch` group, so only use it on trusted single-machine setups where fewer prompts are worth a broader authorization boundary.

If this is the first install, if the extension directory was updated, or if group membership changed during install, re-login to the GNOME session before frontend checks.

For the full install flow and the detailed `.tools/uv/` bootstrap behavior, see [docs/operations/ubuntu-24-install.md](docs/operations/ubuntu-24-install.md).

## Verify the Installation

Check the backend and CLI path first:

```bash
boostctl status --json
bash scripts/verify/verify_simulated.sh
bash scripts/verify/verify_host_integration.sh
```

Continuous integration only covers the simulated verification path above. It does not replace host-side GNOME session checks.

## Manual GNOME Check

Backend verification does not fully cover the Quick Settings click path. Before concluding the frontend path is good, confirm the extension is visible to GNOME Shell and then manually click the Quick Settings toggle in the active GNOME session.

```bash
gnome-extensions info boost-switch@ge777777.github.io
```

## Further Reading

This English README provides the public project overview and key entrypoints. Detailed operations docs and some current GNOME UI strings are still Chinese-first for now.

- [Ubuntu 24 install guide](docs/operations/ubuntu-24-install.md)
- [Uninstall guide](docs/operations/uninstall.md)
- [Troubleshooting](docs/operations/troubleshooting.md)
- [Same-config migration plan](docs/operations/same-config-migration.md)

## Community

- [Contributing guide](CONTRIBUTING.md)
- [Code of Conduct](CODE_OF_CONDUCT.md)
- [Security policy](SECURITY.md)

## Architecture Summary

The mainline architecture is GNOME Shell Quick Settings as the user-facing entry, a system-bus privileged service for writes, and `polkit + systemd` as the install/runtime layer. `sudoers` remains only as a fallback direction, not the primary path.

## Repository Layout

- `docs/`: public architecture and operations docs
- `scripts/`: install, verification, and development helpers
- `system/`: D-Bus, polkit, systemd, and other privilege-integration assets
- `shared/`: shared contracts, schemas, and example payloads
- `src/`: Python service and CLI implementation
- `gnome-extension/`: GNOME Shell extension source and schemas
- `tools/`: tool-specific documentation for CLI and diagnostics entrypoints

## License

This project is released under the [MIT License](LICENSE).
