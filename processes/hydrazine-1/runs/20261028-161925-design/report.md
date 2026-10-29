I've built the hydrazine-1 case from design basis to a balanced BFD/PFD and a preliminary gate-to-gate LCI. Everything is committed on `case/hydrazine-1` in 5 commits (scaffold through `672abc6`), with a clean working tree and nothing pushed.

## Files produced
- **Basis and chemistry:** `process.yaml` (`publication.status: internal`, maturity concept, unreviewed, with references), `process/design-basis.yaml`, `materials.yaml` (13 components), `reactions.yaml` (azine formation, 2-butanol side reaction, H2O2 decomposition, amidation, hydrolysis, pyrazoline formation).
- **Flowsheet:** `process/flowsheet.yaml` with 4 blocks, 11 steps and 41 streams. Recycles: MEK, working solution, NH3 and hydrolysis water. The generated `BFD.xml` and `PFD.xml` are rebuilt from it.
- **Balance script:** `scripts/balance.py` works out every assumed stream and duty.
- **LCI:** `lca/lca.yaml` and `lca/mappings.yaml` (steam counted in kWh only), plus the generated inventory, gaps, results, dataset and manifest files.
- **Records:** `DESIGN.md` (route and boundary memo, 9 sources, decisions D-001 to D-014, open items I-01 to I-10), `PROGRESS.md`, and an equipment list with one tag per PFD step. There are no P&IDs or layout.

## Results
- **Balances:** `cheme validate` gives 0 errors and 0 warnings. `cheme process streams` shows all 4 blocks and 11 steps closing.
- **Boundary (kg/h):** 6 888.4 in = 6 888.4 out. In: 70 % H2O2 2 294.8, NH3 1 444.0, MEK 149.2, acetic acid 96.4, Na2HPO4 4.8, water 2 899.2. Out: hydrazine hydrate 2 000, 2-butanol bleed 123.6, pyrazoline purge 56.3, working-solution purge 199.2, waste water 4 399.7, off-gas 109.6.
- **Consumption per kg N2H4:** H2O2 (as 100 %) 1.255 kg (stoichiometric 1.061), NH3 1.128 kg, MEK 0.117 kg.
- **LCI per kg hydrazine hydrate (64 wt% N2H4):** inputs 3.444 kg = outputs 3.444 kg. MP steam 6.21 kWh, LP steam 1.99 kWh, cooling water 9.45 kWh, power 0.05 kWh. `--coverage` reports mass, element and carbon balances closed. There are 14 background gaps plus NH3 and MEK, which have no GWP100 factor, so there is no impact result.
- **Library checks:** `scripts/build_lci.py --strict` only reports the expected hydrazine gaps. The full library test suite (412 tests) passes when run the way CI does, including core.
- **`cheme check`:** concept gates pass except `layout-plot-plan`, which is out of scope. `cheme maturity` reaches no level, because feed flows come from an assumed capacity and the specifications are assumed.

## Sources
- **Patents:** US 6,562,311 (azine conditions, Examples 4–5 at 81–82 % azine yield, 2-butanol formation, hydrolysis); US 6,605,265 Example 1 (working solution, make-up, regeneration steam of 10.5 t per t H2O2 at 18 bar); US 12,134,558 (hydrolysis column, pyrazolines); US 4,725,421 (about 88 % MEK overhead, lower-water hydrolysis option); US 4,724,133.
- **Data:** NIST WebBook formation enthalpies; PubChem for the azine's CAS number.
- **Secondary:** Wikipedia (scale check against the 17 kt/a Lannemezan plant). Ullmann's was not read; it is a licensed source and stays a lead only.

## Key ASSUMED values
- Capacity 2 000 kg/h hydrazine hydrate (16 kt/a), 8 000 h/a.
- Azine yield 0.85 per H2O2, inside the patent range of 81 to about 90 %.
- Inlet ratios MEK/H2O2 2.2 and NH3/H2O2 2.5.
- Hydrolysis bottoms 30 wt% hydrazine hydrate, 0.5 % of the azine lost to pyrazolines.
- All split compositions and the off-gas and waste-water trace levels.
- Duties: only the regeneration steam is a patent figure, and it is 55 % of all steam. It is the largest uncertainty in the LCI. The other duties are hand estimates, and the reactor cooling and hydrolysis steam are lower bounds.

## Missing registry entries (`chemicals/chemicals.yaml`)
- hydrazine (with a 64 % hydrate grade), hydrogen-peroxide, ammonia, methyl-ethyl-ketone, acetic-acid, 2-butanol, sodium-phosphate, acetamide.
- LCI vocabulary: H2O2, MEK, acetic acid, sodium phosphate, and incineration of spent solvent and hazardous waste.

## Open inputs and gated steps
- **Energy balance and simulation:** blocked. `cheme process props --coverage` shows no property package that covers water, hydrazine, MEK, the azine or the salts in the working solution. This is where the issue points to core #315 and #364, but I couldn't read either issue from here.
- **Core bug in cheme 0.8.0 (I-08):** in `domains/process/model.py`, every reactor after the first one that uses `selectivity:` is rejected because a variable is overwritten. I worked around it with per-reaction conversions on the hydrolysis reactor; it needs fixing in core.
- **Still open:** continuous-plant yields (Hayashi 1976), how the activator is lost, off-gas and vent emissions, heat integration, and choosing the background datasets (including linking the hydrogen-peroxide-1 and ammonia-1 datasets).

## Recommended next stage
1. An independent review of this concept PFD and LCI.
2. Once property support exists, simulate the four columns to replace the hand-estimated duties, and compare the lower-water hydrolysis option.
3. Choose the LCI backgrounds.

The branch has not been reviewed or merged, and no stage is signed off; a merge by a human reviewer is pending.

STATUS: DONE