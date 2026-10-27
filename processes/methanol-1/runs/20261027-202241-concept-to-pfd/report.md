The design basis through a balanced PFD is done and committed on `case/methanol-1` (3 commits, not pushed). `cheme validate` reports 0 errors and 0 warnings, and every block and step balance closes. `cheme maturity` reports **level none**, for the two reasons below.

## What was produced
- **Design basis** (`process/design-basis.yaml`): 2500 t/d of Grade AA methanol, 8400 h/a.
  - The make-up gas is ASSUMED: dry, 68 % H2, 21.5 % CO, 7.5 % CO2, 2.5 % CH4, 0.5 % N2 (stoichiometric number 2.09), at 26 bar(a) and 40 °C.
  - Loop conditions are ASSUMED: about 80 bar, a steam-raising converter with feed at 225 °C and outlet at 255 °C.
- **Chemistry** (`process/materials.yaml`, `process/reactions.yaml`, `process/catalysts.yaml`): taken from the cheme reaction library (CO and CO2 hydrogenation, water-gas shift, Cu/ZnO catalyst), plus CH4 and N2 as inerts.
- **Flowsheet** (`process/flowsheet.yaml`): 3 blocks, 12 steps, 19 material streams and 9 energy streams. Generated `process/BFD.xml` and `process/PFD.xml`; I rendered the PFD and checked it.
  - Units: make-up compressor, recycle circulator, feed/effluent exchanger, equilibrium converter, loop cooler, HP separator, purge, LP flash, topping column and refining column.
- **Balance script** (`scripts/loop_balance.py`): my own solution of the recycle loop and purification, independent of cheme.
- **Lists:** 14 equipment items and 19 lines, with first-pass line sizes and design conditions marked ASSUMED.
- **Manifest** (`process.yaml`): `publication.status: internal`, maturity concept, unreviewed. It passes the library catalog build.
- **Documentation:** `DESIGN.md` has the route/boundary memo, decisions D-001 to D-012, the reaction/model evidence table, the source register, the method/dependency table and open inputs I-01 to I-08. `PROGRESS.md` is updated, and `checks.yaml` now includes the BFD and the maturity gate.

## Balance and check results
- **Converter cross-check:** cheme computes the converter outlet itself, and it matches my script's reaction amounts to within 0.001 % (MEOH_CO 3267.5 kmol/h, WGS −783.4 kmol/h). Both reactions sit at equilibrium at the outlet.
- **Converter duty:** cheme gives 63.9 MW on an ideal-gas basis; the script gives 65.7 MW with real-gas corrections.
- **Loop figures:**

  | Figure | Value |
  |---|---|
  | Recycle ratio | 4 |
  | Purge | 2.18 % of separator gas |
  | CO conversion per pass | 63 % |
  | Make-up carbon reaching the product | 95.7 % |

- **Sensitivity:** varying the assumed 10 K approach to equilibrium between 0 and 20 K changes per-pass conversion from 71 % to 54 %. Carbon to product only moves from 96.6 % to 94.5 %, and duties change by less than 1 %.
- **Utilities:** compressors take 18.8 MW of power, the reboilers 106 MW of LP steam, and the converter raises 66 MW of MP steam. Without reformer waste heat the purification needs more steam than the converter raises.
- **Inerts:** CH4 builds up to about 21 % at the converter inlet. That is high, and the purge trade-off is listed as I-08.
- **Gates:** concept gates are 6 ok; only the plot plan fails, and layout is out of scope. The new basic-stage `maturity-balanced` gate fails, as intended.

## Why maturity is "none"
- **Make-up gas not sourced:** its composition is ASSUMED. It needs a source with a page/section reference, or an owner decision.
- **Separator and column values come from my script:** HP/LP separators, columns and all duties are ASSUMED values from it. Its Peng-Robinson method is not qualified for this mixture.

## Sources
- Ott et al. 2012, Ullmann's "Methanol" (not read in this run; subscription).
- Cheme library methanol entry.
- `chemicals`/`thermo` data: ATcT formation enthalpies, Poling heat capacities, ChemSep binary parameters.
- Vanden Bussche & Froment 1996 and Slotboom et al. 2020: not used; listed as guardrails.
- The Grade AA limits (O-M-232) and Graaf et al. 1986 are cited but not read; they are listed to verify.
- No third-party tables or figures were copied.

## Open inputs and gated steps
- **Gated by core #315 (still open):**
  - `props --fill` refuses streams S3–S19, because the syngas property package excludes methanol and water.
  - So the energy closure can't be evaluated, `process simulate` isn't qualified, and column stages and reflux can't be calculated.
- **Process inputs still missing (not core gaps):**
  - A sourced make-up gas and owner-confirmed capacity.
  - Catalyst vendor data.
  - By-product selectivities: needed to check the full Grade AA spec and to add a fusel-oil draw.
  - An audited rate law: needed to size the converter.
- **Registry gap:** `chemicals.yaml` has no `methanol` or `carbon-monoxide` entry. So `process.yaml` can't list the main product. Adding them is a library change I left out of scope.

## Recommended next stage
1. Review this branch, then source the make-up gas and confirm the capacity. That should lift maturity to sourced.
2. Once core #315 provides a methanol-water-syngas package, rerun `props`/`simulate` to replace the script's values and close the energy balance.
3. Then choose kinetics and size the converter, and run a shortcut column design.

Merge pending: the branch needs an independent review before it can go to `main`. Nothing was signed off or pushed.
