# Progress

Newest first. One line per change: date, sheet or file, what, why.

| date | where | what | why |
|---|---|---|---|
| 2026-10-28 | DESIGN.md, lca/, process/flowsheet.yaml, process.yaml, BFD, PFD | responses to review 2026-10-28-pfd-lci-review, see "Responses" below (commit 462152f) | close the review's medium and low findings |
| 2026-10-28 | PR #237 CI | no failed check found: `gh pr checks 237` showed every finished check passing (incl. `validate (processes/sodium-cyanide-1)`), the rest queued or running; no `--log-failed` to read, nothing changed | task asked to fix CI failures |
| 2026-10-28 | DESIGN.md, process.yaml, PROGRESS.md | source register, decisions D-001..D-012 with gated steps; Atlas manifest (internal, concept, unreviewed) | record the route, basis, model basis and open inputs (issue #150) |
| 2026-10-28 | lca/ | preliminary gate-to-gate LCI per kg solid NaCN: every foreground exchange from the flowsheet, backgrounds unmapped (`missing:`), stack CO2 elementary, emission gaps declared; inventory, gaps, dataset, manifest written by `cheme assess lca --write`; process-local `lca/mappings.yaml` | D-012 |
| 2026-10-28 | process/design-basis.yaml, process/simulation.yaml | design basis (6.25 t/h, feeds, products, utilities, assumptions); R-101 declared adiabatic | D-002..D-010; boundary check of the LCI |
| 2026-10-28 | process/*.yaml, BFD, PFD, equipment and line lists, scripts/nacn_balance.py | balanced concept flowsheet: Andrussow converter, waste heat boiler, ammonia recovery and recycle, HCN absorption and refining, neutralisation, crystallisation, drying, tail gas boiler; 5 blocks, 15 steps, 43 streams; lists for the PFD items | D-001..D-011 |
| 2026-10-28 | (all) | scaffold from `cheme init` and the process.yaml template | start of the case |

## Responses

Review 2026-10-28-pfd-lci-review (reviewed 0000a06; no critical or high findings). All in
commit 462152f.

| finding | response | status |
|---|---|---|
| #1 (medium) steam export shown as a design value | Kept the adiabatic 1429 K converter and stated the export as an UPPER BOUND (no converter, E-101 or B-301 loss; probably 15-20 % lower) in D-010, D-009 (B-301 efficiency 89 % of LHV ASSUMED, stack loss only), the Q8/Q9 provenance, the lca.yaml allocation source and the process.yaml steam note; correction required before any energy or exergy allocation | closed (documented; numbers unchanged) |
| #2 (medium) inputs with no LCI exchange | lca/lca.yaml consumables with `missing:`: `bfw-export` (water of the exported steam, 27.2 t/h, leaves with it), `bfw-makeup` (blowdown and condensate losses, 3.4 t/h, to drains), `phosphate-makeup` (20 t/a, placeholder), `hcn-stabiliser` (27 t/a as H2SO4, placeholder), all ASSUMED; steam convention named in D-012; mass closes (15.65 kg per kg), gaps 12 -> 18 | closed |
| #3 (low) R-401 product above the liquor solubility | Recorded in D-008 as a known inconsistency with the likely reason (free NaOH in the liquor) and a basic-engineering measure (keep R-401 and its line hot, or dilute caustic); not shown, because no NaCN solubility against T and NaOH is sourced | open (needs a solubility source) |
| #4 (low) chiller power outside the 1.03 MW | Stated in D-010 and in the process.yaml power and chilled-water notes (about 0.8-1.2 MW at COP 4-6, carried by product:CHW) | closed |
| #5 (low) gauze charge counted as consumed | lca.yaml consumable source and D-012: when mapped, model the net Pt/Rh loss (or the charge with the refined metal returned); stays a gap | closed (for this stage) |
| #6 (low) warning called "accepted" | D-004 reworded to a known warning: no gate covers `cheme.process-catalyst`, so no gate acceptance exists to record | closed |
| #7 (low) energy closure not reported | D-012 states 75.6 % and that the ledger counts only electricity, heat rejected and steam exported, not the feeds' chemical energy, the reaction heat or the tail gas LHV | closed |
