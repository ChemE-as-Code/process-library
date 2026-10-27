# urea-1 run report: design basis → balanced BFD/PFD → preliminary gate-to-gate LCI

The flowsheet balances in every block and step. The LCI is written and closes against the flowsheet. Nothing is reviewed yet, and `cheme maturity` reaches no level (same as methanol-1). All work is committed on `case/urea-1` in 4 commits (f9e0d2a scaffold → fd2c6b6 flowsheet → bc7d9dd LCI → e671bd1 basis/docs), and the working tree is clean. Nothing was pushed, and no stage was signed off.

## Files produced
- **Design basis and manifest:** `process/design-basis.yaml` and `process.yaml` (`publication.status: internal`, maturity concept, unreviewed, with honest validation notes).
- **Chemistry:** `process/materials.yaml` (7 components) and `process/reactions.yaml` (urea synthesis, biuret, hydrolysis).
- **Flowsheet:** `process/flowsheet.yaml` (5 blocks, 22 steps, 50 streams, 13 energy streams), with the generated `process/BFD.xml` and `PFD.xml`.
- **Balance script:** `scripts/urea_balance.py` records where the separator values and duties come from.
- **LCI:** `lca/lca.yaml` plus the written `inventory.csv`, `dataset.yaml`, `gaps.csv`, `results.*` and `manifest.json`.
- **Lists and docs:** an 18-item equipment list, `DESIGN.md` (decisions D-001 to D-012, source register, basis table, reaction/model evidence, open inputs) and `PROGRESS.md`.
- **No P&IDs:** there was no DEXPI reference sheet in `pid/` to remove, and none was drawn.

## Route
- **Synthesis:** CO2 stripping at 140 bar and 180 °C, NH3/CO2 ratio 2.8, with total recycle.
- **Recirculation:** low-pressure section at 3 bar.
- **Evaporation:** two vacuum stages to melt.
- **Finishing:** I chose prilling with a wet scrubber on the exhaust. It needs no additive; granulation is noted as the next alternative.
- **Condensate:** desorbed and hydrolysed, then re-used as boiler feed water.

## Results
- **Balances:** all 5 blocks and 22 steps close. The reactor and hydrolyser outlets are calculated by `cheme process propagate`. The high-pressure loop closes to within 0.01 kg/h.
- **Independent check:** fresh feeds are 565.3 kg NH3 and 731.8 kg CO2 per t of urea. The BREF reports 567 and 733 kg/t for CO2 stripping (Table 8.3).
- **Checks:** `cheme validate` gives 0 errors and 1 warning (a core rounding issue, below). Of the concept gates, 6 pass and 1 fails (`layout-plot-plan`, out of scope).
- **LCI per kg of urea:**

| exchange | amount per kg urea |
|---|---|
| NH3 | 0.565 kg |
| CO2 feed gas | 0.738 kg |
| electricity | 0.096 kWh |
| MP steam (24 bar) | 0.408 kWh (0.8 t steam per t urea) |
| heat to cooling water | 0.524 kWh |
| NH3 to air | 0.27 g |
| urea dust to air | 0.23 g |
| CO2 to air | 0.09 g |
| treated condensate | 0.225 kg |

- **LCI balance:** material in is 816,309.6 kg/h and out is 816,308.1 kg/h (+0.0002 %). C, H, N, O and carbon by origin all close in `--balance`.
- **Backgrounds:** all 5 backgrounds (NH3, CO2, power, steam, cooling water) are left unmapped as gaps, each with a description of the activity to link later. No factor values were used. The "result" is an empty partial carbon footprint, not an impact figure.

## Sources
- **EU LVIC-AAF BREF (2007), chapter 8:** used for facts only, cited by table and printed page (Tables 8.2–8.11, 8.14, 8.20 and §8.5). I extracted its text into `build/`, which is git-ignored, and copied nothing into the repository.
- **Ullmann's and Meessen (2014):** the identities are recorded, but the content was not audited.

## Key ASSUMED values
- Capacity 2000 t/d and 8000 h/year.
- Product grade: 98.9 % urea, 0.8 % biuret, 0.3 % water.
- CO2 conversion per pass 0.58, inside the BREF's 50–80 % range.
- Water/CO2 ratio at the reactor inlet 0.45.
- Stripper retains 0.15 of the NH3, 0.12 of the CO2 and 0.85 of the water in the liquid.
- Process condensate 6 % NH3, 4 % CO2, 1 % urea.
- Prilling exhaust after scrubbing: dust 35 and NH3 30 mg/Nm³, inside the BAT ranges.
- Feed conditions for both NH3 and CO2.
- How the steam is split between users, and the hand-estimated duties.

My power estimate is 96 kWh/t against the BREF's 110, and cooling water is 45 m³/t against 60. Both are incomplete, and the LCI inherits this.

## Missing registry entries (for the consolidated PR)
`urea` (with a grade for prilled 46 % N fertiliser), `ammonia` (liquid anhydrous), and optionally `biuret`. The CPC classification of the dataset is not given because I could not verify it.

## Gated steps and open inputs
- **Predictive high-pressure loop:** carbamate speciation and vapour–liquid equilibrium need an NH3-CO2-H2O-urea electrolyte model. Core #364 is closed, but its merged scope excludes NH3/NH4+ speciation, and cheme 0.8.0 still reports electrolytes as unsupported. The follow-up sits under #81/#137.
- **Energy closure:** blocked by core #315 (open).
- **Maturity:** no level, because the feeds are assumed and the separators are specified values.
- **Open inputs:** the ammonia-plant interface (#86), the site, a numerical audit of Ullmann's, a complete energy basis, and the scrubber water balance.

## Core bugs found
- `cheme process build` crashes on the `Pumping` step class. I used `GeneratingFlow`, its parent class, for both pumps as a workaround.
- Propagate writes compositions to 6 digits, so stream S11's fractions sum to 0.999999. That is the one validate warning, and I did not hand-edit the calculated values.
- Also, the template's `checks/checks.yaml` cites a decision D-023 that doesn't exist (an info finding, not from this run).

## Not done
I did not write a run record: it needs runner data (cost, tokens) I can't see.

## Recommended next stage
1. Independent review of the basis, flowsheet and LCI.
2. Then source the conversion and stripper efficiency, link the ammonia-plant interface and the backgrounds, and complete the energy basis.
3. After that, a granulation alternative.

**Merge pending:** `case/urea-1` (4 commits) needs review and a merge by a human or the reviewer.
