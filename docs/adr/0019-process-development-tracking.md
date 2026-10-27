# 0019. Track process development with issues and separate workflow from evidence

- **Status:** Proposed, 2026-10-27
- **Scope:** issue forms and docs/process-development.md; tracker #114

## Context
coverage.yaml already implements the coverage roadmap (#47). Parallel process development needs
owners, references, scoped milestones and a kanban without confusing workflow with scientific maturity.

## Decision
Use one canonical process issue initially, route children when independently developed, and a
tracker for coordination. Add process/tracker forms and type:process, type:tracker and type:research
labels. Reuse the engineering issue vocabulary. Keep coverage.yaml as the ranking plan.
A GitHub Project separates Status, next milestone, target deliverable, development priority,
calculation maturity, tier, review and evidence. The main board progresses through references,
brief, BFD, PFD/balances and scoped engineering; sourced inventories have a separate branch.
Each process can stop at its agreed target after verification; detail/3D is optional. Board movement
or closure never raises maturity or approves publication. Committed evidence remains authoritative.
Text-to-flowsheet provides process suggestions only; CRYSTAL provides hub prioritization leads only.

## Consequences
Sources can accumulate per process; parallel work stays visible. Project fields require maintenance
and evidence links and can become stale. Candidate issues and absent data cannot establish maturity.
No scientific schemas or publication gates change.

## Evidence
Tracker #114, literature #115/#116 and first-batch issues #117–#124; existing #86/#42.
See [tracking guide](../process-development.md) and the new issue forms in .github/ISSUE_TEMPLATE/.
