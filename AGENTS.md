# AGENTS.md

This file defines the default change workflow for this repository.

## Scope

- These rules apply by default to all code, configuration, scripts, and documentation changes in this repository.
- Pure read-only exploration may happen in the current workspace.
- After the initial bootstrap commit, any planning, editing, testing, committing, branching, or merging work must move into an isolated `git worktree`.

## Required Workflow

- If the current agent supports Superpowers skills, it must start with `using-superpowers` before continuing with exploration, planning, implementation, or verification.
- Non-read-only work must be done in an isolated `git worktree`, not directly in the main workspace.
- The default project-local worktree directory is `.worktrees/`.
- The implementation branch must be created from the latest `main` before editing begins.
- Every substantive change must produce a Chinese implementation plan before implementation starts.
- A Chinese design doc is not required by default.
- A Chinese design doc is required before implementation when the change spans multiple modules or workflows with non-trivial boundary decisions, changes externally visible behavior or repository workflow with non-obvious consequences, changes the privilege model or install layout, records a choice among multiple reasonable approaches, or the user explicitly asks for one.
- The default local-only workflow-doc directory is `.internal/`; it is meant for private design and planning notes and must not be published with the repository.
- The default design doc path, when required, is `.internal/specs/YYYY-MM-DD-<topic>-design.md`.
- The default plan path is `.internal/plans/YYYY-MM-DD-<topic>.md`.
- Implementation must follow the written plan.
- All git commit messages must be written in Chinese by default, including merge commit messages.
- Matching verification must run before integration.
- After verification passes, the default integration path is to merge the work back into `main` locally.
- After the local merge completes, clean up the `git worktree` created for the current task by default.

## Environment

- The default development environment is the host Ubuntu shell plus a repository-local `uv` environment when Python components are present:

```bash
uv python install 3.12
uv sync
```

- During scaffold-only work, host tools such as `bash`, `git`, `python3`, `gjs`, `gnome-extensions`, and `gnome-shell` are sufficient unless the task explicitly needs more.
- For future Python-based components, prefer `uv run ...` over activating ad-hoc shared environments.
- GNOME Shell extension validation should use host GNOME tools rather than containerized or remote-only workflows unless the task explicitly says otherwise.

## Planning And Execution

- No substantive implementation begins without a written Chinese plan.
- A written Chinese design doc is optional by default and required only for the high-risk cases described above or when the user explicitly asks for one.
- If a design doc is produced, implementation and the written plan must follow it.
- When a written plan includes commit commands or commit message examples, those messages must also be written in Chinese.
- No change is complete without targeted verification.
- No verified change should remain only on an isolated branch by default; the normal finish state is a local merge back to `main` followed by cleanup of the `worktree` created for the current task.
- Changes under `system/`, `scripts/install/`, or `scripts/verify/` must update the matching docs in `docs/operations/`.
- Changes under `shared/contracts/`, `shared/examples/`, or `shared/schemas/` must keep interface examples and documentation in sync.
- Automated tests must not write to the real `/sys/devices/system/cpu/cpufreq/boost` path by default. Any real host boost toggle must be treated as an explicit integration verification step.

## Bootstrap Exception

- The first repository bootstrap that creates the project skeleton, workflow assets, and initial documentation may happen directly on `main` in the repository root, because no repository-local worktree convention exists before those files are created.
- After that bootstrap commit, the normal isolated-worktree workflow becomes mandatory for further non-read-only work.

## Exceptions

- Read-only exploration may remain outside an isolated `worktree`.
- A non-Chinese git commit message is allowed only when the user explicitly requests it for the current task.
- If `main` is not in a usable state, a requested worktree conflicts with the requested change, the local merge back to `main` cannot be completed safely, or the user explicitly says not to merge back locally or not to remove the task worktree, stop and surface the blocker instead of silently bypassing the workflow.
- Direct user instructions for the current task override these defaults.
