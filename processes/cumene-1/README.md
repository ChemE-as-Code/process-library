# Cumene by zeolite alkylation of benzene with propylene

> **AI-generated research output, not engineering advice.** This design was produced by AI coding
> agents (Claude Code) under human direction and is checked by automated tools; it has had
> no independent human review. It is not approved for construction, operation, procurement or
> safety decisions and comes with no warranty. Check the design maturity and review status in
> `process.yaml` before relying on any number.

A concept-stage plant, 272 kt/a cumene: liquid-phase alkylation of benzene with chemical-grade
propylene on a beta-type zeolite, transalkylation of the diisopropylbenzenes, a depropaniser on
a benzene slipstream, benzene, cumene and vacuum DIPB columns, LP steam raised by the alkylator.
Until 2026-11-03 this was a manifest-only pilot with a hand-written Tier 0 dataset; its sourced
facts are now the cross-check of the flowsheet (`DESIGN.md` D-012).

## How it is built

| Step | Where | Standing |
|---|---|---|
| Reaction evidence and route | `process/reaction-evidence.yaml`, `process/reactions.yaml` (D-005) | patent examples (US4891458A, US6888037B2) and a licensor brochure; the cumene/DIPB split at the design ratio is ASSUMED |
| Independent balance | `scripts/cumene_balance.py` (D-007) | thermo Peng-Robinson; gives the feeds, splits and drum outflow |
| PFD | `process/flowsheet.yaml` -> `process/BFD.xml`, `process/PFD.xml` (`cheme process build`) | balances closed (`cheme validate`) |
| Simulation | `process/simulation.yaml`, `process/simulation-run.json` (D-011) | DWSIM 9.0.5, Peng-Robinson, converged; **not qualified** by core for this mixture: an unqualified cross-check of the script, within about 1 % on product, recycles and column duties |
| Lists | `equipment/equipment-list.yaml`, `piping/line-list.yaml` (D-014) | concept values, ASSUMED |
| LCI | `lca/lca.yaml` -> `lca/dataset.yaml` (`cheme assess lca --write`, D-013) | foreground only, exergy allocation over cumene, LPG, heavy ends and exported LP steam; every background a gap |

Per t of cumene the flowsheet needs 0.652 t benzene and 0.352 t propylene (the licensor's
0.651 and 0.352), 2.95 GJ of steam heat (1.58 t, of which 0.30 t is exported back as LP steam)
and about 10 kWh of pump power. The net steam is about six times the licensor's 0.2 t: this
concept has no heat integration (I-08).

## What is weak

- The selectivity split at benzene/propylene 4 and the transalkylation conversion are ASSUMED
  from patent examples at other conditions (D-005, I-05, I-09).
- The property method is not qualified; DWSIM lacks TIPB, which is simulated with a property
  surrogate (D-011).
- No heat integration, no stage design, no P&IDs, plot plan, estimate or HAZOP (concept only).
- Air emissions, oily water, vacuum vents and catalyst regeneration are declared exclusions, not
  estimated (lca/lca.yaml).

## Linking

The product `product:CUMENE` has the registry slug `cumene`. acetone-1 buys cumene: its
`feed:CUM` is pinned to this dataset (acetone-1 `lca/mappings.yaml`). Benzene and propylene stay
reported gaps until their suppliers are chosen (`lca/mappings.yaml`).

## Working here

| path | what |
|---|---|
| `plant.yaml` | name, stage, sheets |
| `process/design-basis.yaml` | capacity, feeds, products, utilities, site |
| `process/materials.yaml`, `process/flowsheet.yaml` | components, blocks, steps and streams: the source of the generated BFD and PFD |
| `process/simulation.yaml` | the DWSIM model (specs, tears, surrogates) |
| `equipment/`, `piping/`, `control/` | lists |
| `lca/` | goal and scope (`lca.yaml`), generated dataset and results |
| `DESIGN.md`, `PROGRESS.md`, `STAGES.md` | decisions, change log, stage definitions |
| `scripts/` | the balance script, the exergy of the co-products, line sizes |
| `.claude/skills/` | how an agent works here (not in git: run `cheme skills update` once after cloning) |

```sh
cheme validate                  # after every change
cheme process streams           # stream table with provenance, block balances
cheme process simulate --check  # re-run DWSIM (Docker image cheme-dwsim:9.0.5)
cheme run scripts/cumene_balance.py
cheme assess lca --coverage
```
