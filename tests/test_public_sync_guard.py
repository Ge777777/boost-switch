import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "dev" / "scan_public_sync_guard.py"


def run_guard(target: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), str(target)],
        capture_output=True,
        text=True,
    )


def test_guard_fails_on_forbidden_content(tmp_path: Path):
    legacy_uuid = "boost-switch@" + "t" + "q77.local"
    (tmp_path / "README.md").write_text(f"legacy {legacy_uuid}\n", encoding="utf-8")

    result = run_guard(tmp_path)

    assert result.returncode == 1
    assert legacy_uuid in result.stdout


def test_guard_fails_on_disallowed_path(tmp_path: Path):
    internal = tmp_path / ".internal"
    internal.mkdir()
    (internal / "plan.md").write_text("private\n", encoding="utf-8")

    result = run_guard(tmp_path)

    assert result.returncode == 1
    assert ".internal/plan.md" in result.stdout


def test_guard_passes_on_clean_tree(tmp_path: Path):
    (tmp_path / "README.md").write_text("public ready\n", encoding="utf-8")

    result = run_guard(tmp_path)

    assert result.returncode == 0
    assert "No forbidden public-sync matches found." in result.stdout
