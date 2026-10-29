---
topic: simulation
reviewed_commit: 5173dd165b302d314d4eb45dde8fcb62b54a24b2
scope: [process/simulation.yaml, process/simulation-run.json, process/flowsheet.yaml, process/materials.yaml, process/BFD.xml, process/PFD.xml, checks/checks.yaml, scripts/packages_on_simulated_duties.py, DESIGN.md, PROGRESS.md, lca/, estimate/tea.md, estimate/tea-cashflow.csv, estimate/tea-sensitivity.csv]
reviewer: review-agent
reviewer_kind: agent
branch: stage/basic-simulation
merge: pending
---
# Review: S2 process simulation of ammonia-1 (PR #244, issue #86), round 1

An independent agent reviewed the seven commits on `stage/basic-simulation` (be8a34c..5173dd1)
against the S2 target in `runs/plan.md`. Earlier sections are on `main`. I re-ran every check
myself and did not rely on the PR body.

## What changed (`cheme diff origin/main --list`, 321 lines; excerpt)

```
process/BFD.xml:
removed EnergyFlow Q14 [Q14]: 0 added, 7 removed, 0 modified
added EnergyFlow Q32 [Q32]: 7 added, 0 removed, 0 modified
added EnergyFlow Q33 [Q33]: 7 added, 0 removed, 0 modified
added EnergyFlow Q35 [Q35]: 7 added, 0 removed, 0 modified
added Stream S20 [S20]: 9 added, 0 removed, 0 modified
added Stream S75 [S75]: 9 added, 0 removed, 0 modified
added Stream S87 [S87]: 9 added, 0 removed, 0 modified
changed Absorbing CO2R: 2 added, 0 removed, 10 modified
changed ReactingChemicals MET: 4 added, 2 removed, 10 modified
changed SeparatingByPhysicalProcess PGR: 2 added, 0 removed, 11 modified
...
process/PFD.xml:
changed ReactingChemicals SHF: 10 added, 8 removed, 91 modified
changed ProcessStep STM: 7 added, 0 removed, 50 modified
changed ReactingChemicals SYN: 119 added, 6 removed, 233 modified
(plus one modified Stream / MaterialState line for nearly every stream S1-S99)
```

The YAML side: `process/simulation.yaml` is now a full spec (PR, specs per step, 7 tears).
`process/flowsheet.yaml` has 268 values written as `calculated` by simulate, propagate and
props, and new SYN/PGR steps (LV501, K702, V702, E702, V703, X601/E601/X602/K601). The
template gate `maturity-balanced` is uncommented unchanged in `checks/checks.yaml`. LCA and TEA
outputs are regenerated, `scripts/packages_on_simulated_duties.py` is new, and the run records
are present. The equipment, line and instrument lists are unchanged.

## Checks re-run (at 5173dd1)

- `cheme validate`: 23 files, 0 errors, 1 warning (`process-energy-balance` K601, -2.17 kW: the
  thermo-PR stream enthalpies from `props` against DWSIM's power, as D-026 says).
- `cheme check`: every concept gate passes, as do `process-basic`, `process-links`,
  `pids-valid` and `drawing-clean`. `maturity-balanced` FAILs, on `sourced.boundary` and
  `balanced.model-basis`. The other basic failures belong to later sections: pids-exist,
  design-review (stale by design until S5r), layout-3d, lifting-study, mto and layout-review.
- `cheme process simulate --check`: case design converged with 7 tears (S4, S9, S27, S44, S46,
  S48, S88) and no error. It exits 1 on the deviation warnings S66, S28, S35, S56, S60, S36,
  S59 and Q18, which are all documented in D-024/D-026 and none of which was edited away.
- `cheme process energy`: every simulated unit closes (largest residual E501 -0.16 kW; the
  reactors close on the formation basis). C301, X401, X601 and X602 are unsupported (core#60,
  open, checked with `gh issue view 60 -R ChemE-as-Code/core`). No temperature cross, and the
  CW approaches are 15 K.
- `cheme maturity`: calculation maturity none. FAIL `sourced.boundary`,
  `balanced.model-basis`, `balanced.energy-closure` (not required, K601), `predictive.coverage`,
  `predictive.model-basis` and `predictive.property-regime` (266 cases, the core#315 cap).
  `predictive.energy-closure` is n/s (core#60). This matches DESIGN.md D-026, except for
  `balanced.energy-closure` (finding #2).
- `cheme assess lca --check` and `cheme assess tea --check`: outputs current.
  `cheme process props --check`: no stale values; H2O streams are outside the package (core#315).
- `cheme impact`: the two earlier records are stale, as expected for a new section.
- `cheme run scripts/packages_on_simulated_duties.py` reproduces the values in the flowsheet:
  Q27 10075.8 kW, Q28 34958.0 kW, Q29 386.8 kW, Q31 341.4 kW, S68 60.1 t/h, S70 105.1 t/h.

## Engineering assessment

- **Provenance.** No `given` value was removed or overwritten. The removed `assumed` values
  are all the concept balance script's outputs (`source: scripts/plant_balance.py ...`), which
  the S2 brief explicitly lets the simulation replace. Two design choices were retuned and stay
  ASSUMED with the reason in D-026: process air S12 and the E-502 outlet. Script-evaluated
  package values stay `assumed` with the script as source. This is honest.
- **Plausibility** (my own order-of-magnitude checks):
  - Product: 62.47 t/h = 1,499 t/d.
  - Converter: adiabatic rise 494 -> 703 K for 3.34 -> 18.44 mol% NH3, about 14 K per % NH3,
    as expected. 18.4 % is the equilibrium at about 150 bar, 703 K and 12 % inerts (the
    reactor is an equilibrium limit with no approach, stated as a limitation).
  - K-501: an ideal two-stage estimate for about 8,000 kmol/h from 28 to 155 bar gives
    roughly 15 MW at 75 %, against 12.72 MW. Plausible.
  - Product flash: about 9 % of the liquid flashing from 266 K to 1.1 bar matches the
    7.27 t/h of flash gas. 16 mol% NH3 in the 258 K / 17 bar vent agrees with the NH3 vapour
    pressure (2.4 bar).
  - CO2 to air: 1.564 kg/kg against 1.562 kg/kg from the carbon content of the D-004 gas, so
    carbon closes.
  - Refrigeration: COP 2.58 at 258/313 K, 0.55 of Carnot as D-017 says.
  - H2/N2 sensitivity to the process air (about 0.008 per kg/h): consistent with the
    accumulation of excess N2 through a purge of about 170 kmol/h.
- **Spot-check of two cited values.** NH3 dHf_298 -45558 kJ/kmol and CH4 -74534 kJ/kmol in
  `process/materials.yaml` ("chemicals: dHf_298 ATCT_G") match `chemicals.Hfg(cas,
  method="ATCT_G")` exactly. I ran `cheme run build/check_hf.py`, and H2O -241822 matches too.
  core#60 and core#57 exist with the titles and states the PR cites. core#315 is the
  core-archive umbrella issue that the plan names.
- **Property package (D-025, left for the reviewer).** Peng-Robinson with DWSIM's kij is an
  acceptable basic-stage substitute for PSRK/MHV in the syngas train and the loop. Cubic EOS
  are the usual choice there. The weak spot is the one D-025 names: NH3 condensation with
  dissolved inerts on unsourced kij, which remains an open input. My view as reviewer: accept
  it for the basic stage. Team acceptance is a human decision.
- **aMDEA.** It is correctly kept as a specified split (electrolytes are refused by core and
  ENRTL is unsupported), and this is stated.
- **Scope and gates.** No gate was relaxed: `maturity-balanced` is uncommented exactly as
  templated. No third-party content was copied. The scope is the S2 section.
- **Steam system "recycle".** It is not simulated. U801, K701 and H101 are energy-only
  packages because core has no adjust/design-spec. I confirmed this: `cheme schema
  process-simulation` has no adjust or target. This is a documented core limit (finding #4).

## Findings

| id | sheet | item | finding | severity | status | proposed action |
|---|---|---|---|---|---|---|
| 2026-10-29-simulation#1 | process | `process/flowsheet.yaml:203` (R100, R102A, R401, H101); `checks/checks.yaml` maturity-balanced | The gate `maturity-balanced`, now enabled at the basic stage, fails on `balanced.model-basis`. The assumed complete conversions it names are standard and can be sourced from open literature: C2+ fully cracked in a prereformer, free O2 consumed in the secondary reformer's combustion zone, CO/CO2 methanated to ppm, complete combustion in the furnace. Unlike R-03 (no public gas composition), this is not blocked. S2 only had to evaluate the gate, but as it stands it blocks the basic sign-off (S5r). | medium | open | Add sourced observations for these conversions in `process/reaction-evidence.yaml` (or give the conversions with provenance `given` and an open source) before S5r. Re-run `cheme maturity`. |
| 2026-10-29-simulation#2 | DESIGN.md | D-026 "Maturity", PR body "Maturity" | The list of failing requirements, presented as "exactly", leaves out `balanced.energy-closure`. `cheme maturity` prints `FAIL balanced.energy-closure ... (not required)` on K601, the same 2.2 kW mismatch D-026 reports as a validate warning. The statement "neither is a core limit" is also too strong for S12, S61, S26 and S70: their flows are balance results or retuned design choices (S12), which cannot honestly be "given with a source". | low | open | Add `balanced.energy-closure` (not required, K601) to the D-026 list. Say that for the non-gas feeds `sourced.boundary` asks for a provenance the design cannot honestly give, so the orchestrator can decide whether this is a core question. |
| 2026-10-29-simulation#3 | process | `process/simulation.yaml:116-161` R102B, R201, R202 | The beds run at fixed outlet temperatures and their duty is called "about 0, the check". The run record shows heat inputs of 466 kW (R102B, 1.3 % of the reaction heat), 237 kW (R201, 2.6 %) and 170 kW (R202, 5.1 %), on no utility (`boundary-utility-unassigned` in lca/tea). R501 was retuned to 31 kW (0.1 %). These beds were not retuned, so about 0.9 MW enters the plant from nowhere. | low | open | Retune the outlet temperatures (R202 about 2 K lower) to bring each duty to about 0.1 %, as was done for R501, or state the three residuals in D-024/D-026. |
| 2026-10-29-simulation#4 | process | U801, K701, H101; `scripts/packages_on_simulated_duties.py`; S66 | The steam system, the refrigeration circuit and the furnace stay script packages because core has no adjust (flow from a duty). This is a real core limit (confirmed in the schema), but unlike core#57, core#59 and core#60 no core issue is cited. The furnace balance (S66 stack 396 K against 423 K, E-107 held at 589.5 kW) is left "until H101 can be simulated", with no owner. | low | open | Orchestrator: file one core issue for adjust/design-spec support (plan rule: one issue per platform problem) and cite it in D-026. Until then, re-evaluate E-107/S66 in the packages script so that the convection balance is consistent. |

## Previous findings

Carried from `reviews/2026-10-29-concept.md`. None was addressed in this section, which is
consistent with its scope.

| id | finding | severity | status | evidence |
|---|---|---|---|---|
| 2026-10-29-concept#1 | X-601 32 m from A-900 without a separation criterion | medium | open | layout files unchanged on this branch |
| 2026-10-29-concept#2 | TEA: DMW, BD, CW free without `free:` | low | open | `cheme assess tea --check` still warns `tea-price-missing` |
| 2026-10-29-concept#3 | steam credit omits the avoided carbon cost | low | open | estimate/tea.yaml unchanged |
| 2026-10-29-concept#4 | ETS price cited from a secondary source | low | open | estimate/tea.yaml unchanged |
| 2026-10-27-pfd-lci-review#3 | R-03: natural-gas composition and supply pressure not sourced | medium | open | S2 kept it ASSUMED with the reason (DESIGN.md section 6, I-01: no public composition per connection). `sourced.boundary` still fails on S1. |
| 2026-10-27-pfd-lci-review#5 | R-05: block reaction extents not unique | low | open | unchanged; core issue is the orchestrator's |

## Verdict

The S2 target is met as `runs/plan.md` states it:
- the design case (the only case, D-003) is simulated and converged, with every simulated
  recycle torn and converged;
- the steam system is a documented core limit (no adjust);
- `process-balances` is ok on the simulated values;
- the per-unit energy audit closes, and the plant closure is unsupported by core#60;
- `maturity-balanced` is enabled and evaluated;
- `cheme maturity` is reported, with the core#315 requirement (`predictive.property-regime`)
  named.

No critical or high finding is open. **Approve**; merge to `main`. Finding #1 must be closed
before the basic sign-off (S5r).
