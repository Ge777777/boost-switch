# Contributing

Thanks for helping improve `boost-switch`.

## Scope And Expectations

- The repository is currently an alpha / mainline implementation, not a polished packaged release.
- Please keep changes scoped. If you touch install assets, verification scripts, or shared contracts, update the matching docs in the same change.
- Automated tests must not write to the real `/sys/devices/system/cpu/cpufreq/boost` path by default.

## Local Setup

On Ubuntu 24 hosts, install the baseline tools first:

```bash
sudo apt-get update
sudo apt-get install -y python3 python3-venv gjs libglib2.0-bin
```

If `uv` is not installed yet, use Astral's official installation guide or the official Linux/macOS installer first:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Official docs: <https://docs.astral.sh/uv/getting-started/installation/>

Then bootstrap the repo-local environment:

```bash
uv sync --extra dev
```

If you do not want to install `uv` yet, use this manual fallback instead of `uv sync` plus `verify_simulated.sh`:

```bash
python3 -m venv .venv-manual
. .venv-manual/bin/activate
python -m pip install --upgrade pip
python -m pip install -e '.[dev]'
python -m pytest
glib-compile-schemas gnome-extension/schemas
gjs -m gnome-extension/tests/test-state.js
gjs -m gnome-extension/tests/test-errors.js
gjs -m gnome-extension/tests/test-presenter.js
```

## Standard Verification

Run the repository-standard simulated verification before opening a PR:

```bash
bash scripts/verify/verify_simulated.sh
```

This covers Python tests, schema compilation, and the committed GJS test suite.

## Host Integration Boundary

Real host validation is still important, but it is not part of CI.

- Use `bash scripts/verify/verify_host_integration.sh` for explicit host checks.
- Only use `--allow-real-toggle` when you intentionally want to touch the real host boost switch.
- Quick Settings click-path behavior still requires a manual check in an active GNOME session.

## Public vs Private Workflow Notes

- Public repository docs live under `docs/`.
- Local design docs and implementation plans belong under `.internal/`.
- `.internal/` is a private, gitignored workspace path and should not be committed or included in public releases.

## Commit And Review Notes

- Unless the maintainer says otherwise, keep commit messages in Chinese to match the repository workflow.
- Prefer targeted tests and doc updates over broad rewrites.
- When changing files under `system/`, `scripts/install/`, `scripts/verify/`, `shared/contracts/`, `shared/examples/`, or `shared/schemas/`, keep their matching docs in sync.
