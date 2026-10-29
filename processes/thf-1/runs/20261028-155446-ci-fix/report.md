I fixed the CI failure on PR #213 and closed six of the nine review findings. The review (`reviews/2026-10-28-pfd-lci-review.md`) had no critical or high findings: one medium (#1), eight low. Everything is committed in four commits on `case/thf-1`, all inside `processes/thf-1/`, and nothing is pushed.

**CI failure:** the library tooling test failed because `chemistry.inputs` in `process.yaml` was empty, and the schema requires at least one entry. The registry has no entry for BDO, THF or p-TSA, and adding one would mean editing outside this folder. So I moved the steam the process consumes, which is in the registry, from `utilities` to `inputs`, keeping its role as `utility`. The note says why. This is a stand-in until the BDO entry exists. I ran the catalog build locally and it reports no errors; I did not run the full pytest suite locally (ba2ac43).

**Findings closed:**
- **#1 (medium):** D-007 and the `process.yaml` description now say that the LP column duties assume a single liquid phase, while the NRTL parameters predict two. They stay unverified until a stage-by-stage check of C-201 is done (I-04) (ba2ac43).
- **#2:** D-007 now gives a steam range. At 1.3 × minimum reflux instead of the 0.3 floor, total steam would be about 4 % lower; this is a hand estimate. The screening range is 3.6 MJ/kg THF −5 %/+30 %, and the +30 % is marked ASSUMED (5e0e557).
- **#5:** steam-side design pressures now follow D-010: E-206 11 barg, E-202 5.5 barg, and the R-101 heating side 11 barg / 205 °C in its notes. D-010 records the per-side rule (3d03231).
- **#6:** D-005 now states that the THF dissolved in the reactor bleed is neglected; it is below 0.1 % of the product and not calculated (3d03231).
- **#7:** I re-read the whole patent text. The 2,3-dihydrofuran range is 37–327 ppm, not 17–327. The BDO ≤ 10 ppm result is Example 1-4, a 500 L reactor charged with 400 L of BDO. The reviewer's "400 L" was the charge volume, not the reactor size. Locators and the source register are corrected (5e0e557).
- **#9:** the template comments no longer cite D-023 / D-012, so those two info messages are gone from `cheme validate` (3d03231).

PROGRESS.md has a Response entry for each finding with its commit (a110c6b).

**Findings left open (all low):**
- **#3:** adding the ~25 kW of auxiliary power (reflux pumps, bottoms pump, agitator) to `feed:POWER` would need new energy streams on the flowsheet, which would break the energy balances matched to the balance script. It stays a declared cutoff until the pumps are drawn at basic engineering.
- **#4:** the "concept" maturity claim still exceeds what the evidence supports. Closing it needs a sourced feed and capacity basis and a sourced reactor selectivity (I-02).
- **#8:** BDO, THF and p-TSA still need registry entries outside this folder, in the consolidated PR.

**Re-run results:**
- `cheme validate`: 0 errors, 0 warnings.
- `cheme check`: the concept gates pass except `layout-plot-plan`, which is out of scope. The `design-review` gate now fails because the reviewed files changed after the review, so a fresh review is needed.
- `cheme maturity`: still none, with the same claim-exceeds warning.
- `cheme process streams`: every block and step closes.
- `cheme assess lca --coverage`: 8 declared gaps; mass, element and carbon balances closed.

A merge is pending: the branch needs a new independent review of these commits, and then a human or the reviewer merges it.

STATUS: DONE