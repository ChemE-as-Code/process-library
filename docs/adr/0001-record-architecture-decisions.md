# 0001. Record architecture decisions

- **Status:** Accepted, 2026-10-25
- **Scope:** the library as a whole

## Context

The process library grew within a week from one engineering project (the ASU) into a library
with a manifest schema, a chemicals registry, a taxonomy, two build pipelines (the Atlas
catalog and the Brightway LCI database), publication rules, benchmarks and release governance.
The reasons for these choices are scattered over commit messages, pull request descriptions,
`docs/*.md` and comments in `lci/mappings.yaml` and the scripts. A contributor who wants to
change the structure, a schema or the LCI pipeline cannot easily see what was decided, why,
and what the change would break.

Each process already records its engineering decisions in its own `DESIGN.md` (D-NNN). Those
are decisions about one plant; nothing records decisions about the library itself. The owner
asked for Architecture Decision Records in every ChemE-as-Code repository (core keeps its own
in core's `docs/adr`).

## Decision

- Decisions about the library's structure, file formats and schemas, build pipelines,
  publication rules and governance are recorded as Architecture Decision Records in
  `docs/adr/`, one Markdown file per decision, numbered `NNNN-kebab-title.md`, following
  [the template](template.md) (Nygard / MADR-lite: Status, Context, Decision, Consequences,
  Evidence).
- Engineering decisions of a process stay in that process's `DESIGN.md` (D-NNN). An ADR may cite
  them, but does not repeat them.
- ADRs 0002 and later were written retroactively on 2026-10-25 from the repository's history.
  Their Status date is the date the decision entered `main` (the merge of its pull request),
  and their Evidence section cites the commits and pull requests.
- A decision that is still a draft for the owner's or an expert's decision has Status
  **Proposed**, even when the build already applies it.
- A change to the library structure, a schema, the LCI pipeline or the publication rules comes
  with a new or updated ADR in the same pull request. An ADR is not edited to reverse its
  decision: a new ADR supersedes it, and the old one's Status names its successor.

## Consequences

- The reasons for the library's shape are in one place and reviewed with the change that makes
  them.
- Retroactive ADRs reconstruct reasons from the record. Where the record gives no reason, the
  ADR says so rather than inventing one.
- One more file per structural change; small fixes that do not change a decision need none.

## Evidence

- Request of the owner for ADRs in all ChemE-as-Code repositories (2026-10-25).
- The per-process decision log: `processes/asu-1/DESIGN.md` (D-001 onward).
