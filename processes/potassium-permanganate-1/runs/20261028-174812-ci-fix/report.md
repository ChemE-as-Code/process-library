The review has no critical or high findings, so I closed 10 of the 13 medium and low ones. Everything is committed on `case/potassium-permanganate-1` in 5 commits (19e6063 to edb0c6b) and not pushed.

**CI:** nothing to fix. `gh pr checks 236` showed no failed job: every completed check had passed and the rest were still queued (that's why it exited with code 8). The potassium-permanganate-1 validate job had passed in one run and was queued in the other. So I made no change for CI.

**Findings closed (review ids #n = R-nn):**
- **#2** (medium): `DESIGN.md` D-006 now says the 1000 A/m2 is the cathode current density, and that the anode area is open and must run at a lower current density. It also says the current efficiency falls as conversion per pass rises. A new table shows how electricity per kg changes with current efficiency from 0.6 to 0.9: 0.924 to 0.666 kWh/kg, against 0.696 in the base case.
- **#4, #5, #6** (low): notes added to D-007, D-005 and D-008: KMnO4 crystallising inside the cell, the condensate "wash" being mostly leach dilution water, and permanganate reduction and fouling in the evaporator E-601.
- **#7** (low): the validation notes in `process.yaml` now say that `cheme maturity` rates the evidence at none and that "concept" is kept only because the schema has no lower level.
- **#9** (low): the schema only allows fossil, biogenic or land-use-change as an emission origin, so the vented hydrogen keeps the "fossil" label. `lca/README.md` and a comment in `lca.yaml` explain that it comes from water.
- **#10** (low): the WATER_SPLIT heat of reaction is now marked `assumed` until the reference table is re-read, and the source register says so.
- **#11** (low): the dryer step is renamed D501 → DR501 (ports, steam port, energy stream Q10), the BFD/PFD are rebuilt and the balance script's labels updated.
- **#12** (low): `DESIGN.md` has a basis table marking each design value as sourced, assumed or missing.
- **#13** (low): the concept plot-plan gate is deferred to basic engineering, written down under the open inputs in `DESIGN.md`.

Each closed finding has a Response entry with its commit in `PROGRESS.md`.

**Findings left open:**
- **#1** (medium): fixing the missing KOH heat of solution needs a sourced value at 50 wt% and 13 wt%, which I couldn't read in this session. I recorded it in D-009 as a known gap; the review estimates the roaster's fired heat is understated by about 25-30 %. The duties and the LCI are unchanged.
- **#3** (medium): column:line locators for the patents need the patent PDFs, which I didn't read.
- **#8** (low): the registry entries belong in `chemicals/`, outside this folder.

**Re-runs:**
- `cheme validate`: 0 errors, 0 warnings.
- `cheme check`: same result as at review time. The concept gates pass except the plot-plan gate (now deferred), and the basic and detail gates still fail for missing P&IDs, layout and datasheets. The design-review gate now fails because the reviewed files changed after the review, so a fresh review is needed.
- `cheme maturity`: calculation maturity still none, with the over-claim warning, as now documented.
- `cheme process streams`: all 5 blocks and 10 steps balance (DR501 included).
- `cheme assess lca --coverage`: mass, element and carbon-origin balances closed; still a partial screening result, DQR 2.33.

The branch has not been merged; a fresh review is needed before it can be.

STATUS: DONE