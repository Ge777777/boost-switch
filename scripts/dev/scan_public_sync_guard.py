#!/usr/bin/env python3
from __future__ import annotations

import argparse
import subprocess
from pathlib import Path


DISALLOWED_PREFIXES = (
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
DISALLOWED_EXACT_PATHS = {
    "gnome-extension/schemas/gschemas.compiled",
}
FORBIDDEN_PATTERNS = (
    "t" + "q77",
    "getianqi" + "@",
    "@stu." + "scu.edu.cn",
    "/home/" + "t" + "q77",
    "boost-switch@" + "t" + "q77.local",
    "io.github." + "t" + "q77.",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Scan a candidate public repo tree for forbidden private paths and legacy identifiers."
    )
    parser.add_argument(
        "target",
        nargs="?",
        default=".",
        help="Target directory to scan.",
    )
    return parser.parse_args()


def is_binary(path: Path) -> bool:
    try:
        return b"\x00" in path.read_bytes()
    except OSError:
        return True


def iter_repo_files(root: Path):
    tracked = subprocess.run(
        ["git", "-C", str(root), "ls-files", "-z"],
        check=False,
        capture_output=True,
    )
    if tracked.returncode == 0:
        for raw in tracked.stdout.split(b"\x00"):
            if not raw:
                continue
            path = root / raw.decode("utf-8")
            if path.is_file():
                yield path
        return

    for path in sorted(root.rglob("*")):
        if path.is_dir():
            continue
        if ".git" in path.parts:
            continue
        yield path


def find_path_offenders(root: Path) -> list[str]:
    offenders = []
    for path in iter_repo_files(root):
        rel = path.relative_to(root).as_posix()
        if rel in DISALLOWED_EXACT_PATHS or any(
            rel.startswith(prefix) for prefix in DISALLOWED_PREFIXES
        ):
            offenders.append(rel)
    return offenders


def find_content_offenders(root: Path, patterns: list[str]) -> list[str]:
    folded_patterns = [(pattern, pattern.casefold()) for pattern in patterns]
    offenders = []

    for path in iter_repo_files(root):
        rel = path.relative_to(root).as_posix()
        if is_binary(path):
            continue

        text = path.read_text(encoding="utf-8", errors="replace")
        for lineno, line in enumerate(text.splitlines(), start=1):
            folded_line = line.casefold()
            for raw_pattern, folded_pattern in folded_patterns:
                if folded_pattern in folded_line:
                    offenders.append(f"{rel}:{lineno}: {raw_pattern}")

    return offenders


def main() -> int:
    args = parse_args()
    root = Path(args.target).resolve()
    path_offenders = find_path_offenders(root)
    content_offenders = find_content_offenders(root, list(FORBIDDEN_PATTERNS))

    if path_offenders or content_offenders:
        if path_offenders:
            print("Path offenders:")
            for offender in path_offenders:
                print(f"  - {offender}")
        if content_offenders:
            print("Content offenders:")
            for offender in content_offenders:
                print(f"  - {offender}")
        return 1

    print("No forbidden public-sync matches found.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
