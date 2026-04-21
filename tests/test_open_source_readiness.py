import subprocess
import sys
from pathlib import Path


REQUIRED_PUBLIC_IGNORE_RULES = {
    ".worktrees/",
    ".internal/",
    ".venv/",
    ".tools/uv/",
    "__pycache__/",
    ".pytest_cache/",
    ".mypy_cache/",
    "node_modules/",
    "dist/",
    "build/",
    "*.pyc",
    "gnome-extension/schemas/gschemas.compiled",
    ".codex",
}

PUBLIC_REPO_DISALLOWED_PREFIXES = (
    ".worktrees/",
    ".internal/",
    ".venv/",
    ".tools/uv/",
    "__pycache__/",
    ".pytest_cache/",
    ".mypy_cache/",
    "node_modules/",
    "dist/",
    "build/",
    ".codex/",
)

PUBLIC_REPO_DISALLOWED_EXACT_PATHS = {
    "gnome-extension/schemas/gschemas.compiled",
}


def read_text(path: str) -> str:
    return Path(path).read_text(encoding="utf-8")


def read_gitignore_entries() -> set[str]:
    return {
        line.strip()
        for line in read_text(".gitignore").splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    }


def list_tracked_repo_paths() -> list[str]:
    result = subprocess.run(
        ["git", "ls-files"],
        check=True,
        capture_output=True,
        text=True,
    )
    return [line.strip() for line in result.stdout.splitlines() if line.strip()]


def find_disallowed_public_repo_paths(paths: list[str]) -> list[str]:
    offenders = set()

    for raw_path in paths:
        path = raw_path[2:] if raw_path.startswith("./") else raw_path
        if path in PUBLIC_REPO_DISALLOWED_EXACT_PATHS:
            offenders.add(path)
            continue
        if path.endswith(".pyc"):
            offenders.add(path)
            continue
        if any(path.startswith(prefix) for prefix in PUBLIC_REPO_DISALLOWED_PREFIXES):
            offenders.add(path)

    return sorted(offenders)


def test_open_source_files_exist():
    for rel in [
        "LICENSE",
        "CONTRIBUTING.md",
        "CODE_OF_CONDUCT.md",
        "SECURITY.md",
        ".github/workflows/ci.yml",
    ]:
        assert Path(rel).exists(), rel


def test_public_repo_does_not_keep_internal_superpowers_docs():
    assert not Path("docs/superpowers").exists()


def test_open_source_guardrail_keeps_private_and_generated_ignore_rules():
    assert REQUIRED_PUBLIC_IGNORE_RULES <= read_gitignore_entries()


def test_open_source_guardrail_rejects_sample_private_and_generated_paths():
    assert find_disallowed_public_repo_paths(
        [
            "README.md",
            ".internal/plans/private.md",
            ".codex/config.toml",
            "build/output.log",
            "module.pyc",
            "gnome-extension/schemas/gschemas.compiled",
        ]
    ) == [
        ".codex/config.toml",
        ".internal/plans/private.md",
        "build/output.log",
        "gnome-extension/schemas/gschemas.compiled",
        "module.pyc",
    ]


def test_public_repo_does_not_track_private_or_generated_artifacts():
    assert find_disallowed_public_repo_paths(list_tracked_repo_paths()) == []


def test_public_repo_has_no_legacy_private_markers():
    completed = subprocess.run(
        [sys.executable, "scripts/dev/scan_public_sync_guard.py", "."],
        check=False,
        capture_output=True,
        text=True,
    )

    assert completed.returncode == 0, completed.stdout + completed.stderr


def test_agents_points_internal_workflow_docs_to_private_directory():
    text = read_text("AGENTS.md")

    assert ".internal/specs/YYYY-MM-DD-<topic>-design.md" in text
    assert ".internal/plans/YYYY-MM-DD-<topic>.md" in text
    assert "docs/superpowers/" not in text


def test_bilingual_readmes_expose_public_collaboration_entrypoints():
    readme_en = read_text("README.md")
    readme_zh = read_text("README.zh-CN.md")

    for text in [readme_en, readme_zh]:
        assert "CONTRIBUTING.md" in text
        assert "SECURITY.md" in text
        assert "LICENSE" in text
        assert "verify_simulated.sh" in text


def test_ci_runs_repository_standard_simulated_verification():
    text = read_text(".github/workflows/ci.yml")

    assert "bash scripts/verify/verify_simulated.sh" in text
    assert "gjs" in text
    assert "glib-compile-schemas" in text


def test_public_docs_do_not_reference_internal_workflow_paths():
    for rel in [
        "README.md",
        "README.zh-CN.md",
        "docs/architecture/overview.md",
        "docs/architecture/solution-options-analysis.md",
        "CONTRIBUTING.md",
    ]:
        text = read_text(rel)
        assert "docs/superpowers" not in text


def test_contributing_local_setup_documents_uv_install_and_manual_fallback():
    text = read_text("CONTRIBUTING.md")

    assert "https://docs.astral.sh/uv/getting-started/installation/" in text
    assert "curl -LsSf https://astral.sh/uv/install.sh | sh" in text
    assert "python3 -m venv .venv-manual" in text
    assert "python -m pip install -e '.[dev]'" in text
    assert "python -m pytest" in text


def test_module_readmes_match_current_repository_artifacts():
    extension_readme = read_text("gnome-extension/README.md")
    contracts_readme = read_text("shared/contracts/README.md")
    examples_readme = read_text("shared/examples/README.md")
    schemas_readme = read_text("shared/schemas/README.md")

    assert "metadata.json" in extension_readme
    assert "src/" in extension_readme
    assert "tests/" in extension_readme
    assert "预留给未来的 GNOME Shell 扩展" not in extension_readme

    assert "io.github.ge777777.BoostSwitch1.xml" in contracts_readme
    assert "当前阶段不提供真实契约文件" not in contracts_readme

    assert "status-enabled.json" in examples_readme
    assert "status-disabled.json" in examples_readme
    assert "diagnostics-group-missing.json" in examples_readme
    assert "当前阶段不提供真实示例文件" not in examples_readme

    assert "status.schema.json" in schemas_readme
    assert "diagnostics.schema.json" in schemas_readme
    assert "当前阶段不提供真实 schema 文件" not in schemas_readme
