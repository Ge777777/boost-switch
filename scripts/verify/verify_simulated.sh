#!/usr/bin/env bash
set -euo pipefail

uv sync --extra dev
uv run pytest
glib-compile-schemas gnome-extension/schemas
gjs -m gnome-extension/tests/test-state.js
gjs -m gnome-extension/tests/test-errors.js
gjs -m gnome-extension/tests/test-presenter.js
