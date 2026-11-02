# 0025. Keep the agent skills out of git

- **Status:** Proposed, 2026-11-01
- **Deciders:** the owner (Artur Schweidtmann)
- **Scope:** library structure, every process folder with `.claude/skills/`

## Context

Each of 44 process folders held a copy of the skills bundled with core: 5,680 of the 9,592 tracked
files, and the longest paths of the repository. A clone into a normal folder already worked, so
this was not a failure to fix. The copies are duplicates of what core already ships, and the depth
of their paths leaves less room for a very long folder path.

## Decision

- `processes/*/.claude/skills/` is ignored by git (`.gitignore`). `.claude/settings.json` stays.
- A person runs `cheme skills update` once in a process folder after cloning, as the root README
  and each process README say.

## Consequences

- Fewer files and shorter paths, so very long folder paths are safer.
- A process folder has no skills until that command has run, so an agent started there, or a stage
  of `scripts/agent-run/`, works without them until then.
- The skills in a folder are those of the installed core, not a version pinned by the process. A
  skill changed in a folder stays on that machine; a change meant for others goes to core.
- The licences of [0024](0024-agpl-for-code-skills-and-scripts.md) are unchanged.

## Evidence

- `.gitignore`, the process `README.md` files, `AGENTS.md`, `LICENSE-DATA`, `NOTICE`.
- Nothing in `scripts/`, `tests/` or `.github/workflows/` reads the copies; `scripts/publication.py`
  already excludes `.claude/**` from snapshots.
