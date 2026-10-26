# 0003. Turn example-asu into the library by moving the ASU to processes/asu-1 with its history

- **Status:** Accepted, 2026-10-23
- **Scope:** repository structure and history

## Context

This repository began on 2026-10-18 as `ChemE-as-Code/example-asu` (first commit `55be1e3`,
"plantcode init"): a single cryogenic air separation unit at the repository root, with five days
of engineering history (P&IDs, reviews, layout, LCA, decisions D-001 to D-057). When the
library was created ([0002](0002-one-folder-per-process-single-source.md)), the options were a new
repository that imports the ASU as a snapshot, or this repository renamed with the ASU moved
into a process folder. A snapshot would have cut the ASU's design history off from its files,
and that history is the design audit trail its reviews and `DESIGN.md` refer to.

## Decision

- This repository becomes `ChemE-as-Code/process-library`. The ASU moves to
  `processes/asu-1/` in a commit that **only moves files** (no content change), so
  `git log --follow processes/asu-1/<path>` keeps every file's history.
- Root-anchored settings (CI paths, `.gitattributes`, the pre-commit hook's location) are fixed
  in the following commit, which also adds the library's root files.

## Consequences

- The ASU's history, review records and decision log stay traceable to the files.
- The repository's early history is the history of one plant, not of the library; the library's
  own decisions start at `986803b`.
- Both commits were made with `--no-verify`, because the installed pre-commit hook ran
  `cheme validate` at the repository top, which no longer holds a plant. Each process folder
  now runs `cheme git-setup` once per clone.

## Evidence

- `d6f7e5f` "Move ASU-1 into processes/asu-1/ (pure move)" and `986803b`, both in
  [#15](https://github.com/ChemE-as-Code/process-library/pull/15) ("Process library: ASU-1 moves to
  processes/asu-1/").
- README.md note "Formerly `ChemE-as-Code/example-asu`".
