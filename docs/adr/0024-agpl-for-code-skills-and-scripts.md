# 0024. AGPL for code, skills and scripts; MIT for the LCI data installer; CC BY 4.0 for data and designs

- **Status:** Accepted, 2026-11-01; the MIT licence of `python/` awaits the owner's confirmation
- **Deciders:** the owner (Artur Schweidtmann)
- **Scope:** `LICENSE`, `LICENSE-DATA`, `python/LICENSE`, `NOTICE`, every process folder. Supersedes the code licence of [0013](0013-licences-and-no-third-party-content.md)

## Context

[0013](0013-licences-and-no-third-party-content.md) put the code under MIT and everything in
`processes/` under CC BY 4.0. That did not fit what the repository holds. The skills in
`processes/*/.claude/skills/` are copies of the ones in core, which is under AGPL-3.0-or-later,
and the scripts in a process folder were caught by the CC BY 4.0 of `processes/`, a licence not
meant for code. Before going public the owner decided: "processes are CC BY but skills and scripts
should still be AGPL".

## Decision

- Code is under **AGPL-3.0-or-later** (`LICENSE`): `scripts/`, `schemas/`, `tests/`, `docs/hooks/`,
  and inside process folders the agent skills (`.claude/skills/`) and the scripts (`scripts/` and
  any other executable script).
- The LCI data installer in `python/` is under **MIT** (`python/LICENSE`), so that people who
  download the database can use it in any workflow. The owner has yet to confirm this one.
- Data and designs stay under **CC BY 4.0** (`LICENSE-DATA`): `processes/`, `chemicals/` and `lci/`,
  except those skills and scripts. Files a script generates, such as drawings, stay under CC BY 4.0.
- Third-party excerpts keep their own licence, in a `NOTICE.md` next to them (the DEXPI snippets of
  the `dexpi-xml` skill are CC BY 4.0). The rule of 0013 never to copy third-party content is
  unchanged.

## Consequences

- Skills and scripts have the same licence here as in core, so they can move between the two.
- A process folder now mixes two licences, so reusing one whole means following both.
- `publication.license` in `process.yaml` names the licence of a process's data and designs, not of
  its skills and scripts.
- Copies of the repository from before this decision remain under the licences they came with.

## Evidence

- `LICENSE`, `LICENSE-DATA`, `python/LICENSE`, `NOTICE`, CLAUDE.md "Sources and licences",
  CONTRIBUTING.md, `README.md` "License".
