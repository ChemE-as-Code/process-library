The concept run for hda-1 is complete and committed on `case/hda-1` (5 commits, not pushed). `cheme validate` reports 0 errors and 0 warnings, every mass, component and element balance closes, and the preliminary LCI is written. `cheme maturity` reports level **none**: the feeds are assumed and the separators and columns rest on unqualified values. methanol-1 got the same result for the same reasons.

## Files produced
- **Design basis** (`process/design-basis.yaml`):
  - 100 kt/a benzene (12.5 t/h, 8000 h/a).
  - Feeds: pure toluene, and make-up hydrogen at 95 mol% H2 / 5 mol% CH4, 3.7 MPa.
  - Product target: 99.9 mol% benzene.
- **Chemistry and flowsheet** (`process/materials.yaml`, `reactions.yaml`, `flowsheet.yaml`, generated `BFD.xml` and `PFD.xml`, `simulation.yaml`):
  - Two reactions: toluene to benzene plus methane, and benzene to biphenyl plus hydrogen.
  - Flowsheet: 2 blocks, 15 steps, 24 material and 10 energy streams.
  - Units: toluene drum and pump, mixer, feed/effluent exchanger, fired heater, adiabatic reactor, quench, trim cooler, HP separator, purge, recycle compressor, stabiliser, benzene column, vacuum toluene column.
  - `simulation.yaml` only declares the reactor adiabatic. I rendered the PFD and checked it.
- **Balance script** (`scripts/hda_balance.py`): my own Peng-Robinson solution of the loop and the columns, independent of cheme.
- **Lists:** 18 equipment items and 24 lines, with first-pass line sizes; design conditions marked ASSUMED.
- **LCI** (`lca/lca.yaml` plus the generated `inventory.csv`, `gaps.csv`, `dataset.yaml`, `manifest.json`, `results.*`).
- **Documentation:** `DESIGN.md` (decisions D-001 to D-013, evidence table, source register, method/dependency table, open inputs I-01 to I-11), `PROGRESS.md`, and `process.yaml` (internal, concept, unreviewed). The manifest passes the library catalog build.

## Results
| Check | Result |
|---|---|
| Recycle loop | converged (residual 3.5e-10); purge is 11.1 % of separator gas, recycle gas 2353 kmol/h |
| Overall mass | 16 334 kg/h in and out |
| Reactor | cheme computes the same reaction amounts as the script (167.865 and 2.569 kmol/h). Its ideal-gas duty of −45 kW (against about 7 MW of reaction heat) confirms the adiabatic outlet of 937 K, below the hydrocracking limit |
| Energy closure (script) | 7978 kW in, 7958 kW out (0.25 %) |
| Feed/effluent exchanger | minimum internal approach 53 K |
| Utilities | power 266 kW, fired heat 2957 kW, steam MP 1431 / LP 2300 / HP 650 kW, cooling water 9207 kW |
| Yield and losses | 0.949 mol benzene per mol fresh toluene; 258 kg/h of aromatics lost to fuel gas |
| Concept gates | 6 ok; only the plot plan fails (layout is out of scope) |

Before the final duties I found and fixed an error in my script: the benzene and toluene column feeds were evaluated at the wrong temperature, which left the energy balance about 1.2 MW open. After the fix the two reboiler duties dropped to 2300 and 650 kW.

**LCI per kg benzene:**

| Exchange | Amount |
|---|---|
| Toluene | 1.24146 kg |
| Make-up hydrogen gas | 0.06526 kg |
| Power | 0.0213 kWh |
| Fired heat | 0.2365 kWh |
| MP / LP / HP steam | 0.1145 / 0.1840 / 0.0520 kWh |
| Heat to cooling water | 0.7366 kWh |
| Biphenyl (co-product) | 0.03208 kg |
| Fuel gas (co-product) | 0.27464 kg |

- **Balance:** `cheme assess lca --balance` closes mass, carbon and hydrogen; by hand it is 1.30672 kg in and out per kg benzene.
- **Backgrounds:** all 10 are left as described gaps, so the coverage result has no total and no impact figure is claimed.
- **Co-products:** I proposed system expansion (substitution) for biphenyl and fuel gas. Energy and mass allocation would give benzene 71.5 % and 76.5 % of the burdens. Both the allocation method and the backgrounds are for an LCA practitioner to decide.

## Sources
- **Douglas (1988), HDA case study:** reactor temperature window, about 3.45 MPa, hydrogen-to-aromatics ratio of at least 5, and the selectivity correlation S = 1 − 0.0036/(1−X)^1.544. I used these from memory without reading the book in this run, so the exact location still needs checking (I-06).
- **Speight (2011), via the library's aromatics skill:** gives 500–600 °C, which conflicts with Douglas's range. The conflict is recorded but not resolved.
- **Component data:** `chemicals`/`thermo` (ATcT, CRC, HEOS, ChemSep interaction parameters).
- **LHVs for the allocation comparison:** CODATA values for CO2 and water.
- **IDAES:** cited as context only; none of its data is used, and no third-party content was copied.

## Key ASSUMED values
- Capacity and hours.
- Feed purities.
- Conversion of 0.75 per pass.
- Reactor inlet 895 K at 3450 kPa(a), quench to 893 K.
- Hydrogen-to-aromatics ratio 5 and 40 mol% H2 in the purge.
- Column pressures, recoveries and reflux at 1.3 × minimum (at least 0.5).
- Utility levels.
- Machine efficiencies (compressor 0.75, pump 0.65).

## Missing registry entries (`chemicals.yaml`)
- toluene
- benzene, with a product grade
- biphenyl
- natural gas, or fired heat from natural gas
- fuel gas
- steam grades at 4.5, 15 and 42 bar(a)

## Open inputs and gated steps
- **Gated by core #315:** no property package covers aromatics with hydrogen, so `props --fill`, core's energy closure and `process simulate` can't be used. Flashes, columns and duties therefore stay as ASSUMED values from my script.
- **New core bug:** `cheme process build` crashes with a `TypeError` on the `Pumping` and `HeatingInFurnace` step classes. I worked around it by using `GeneratingFlow` and `ExchangingThermalEnergy` (explained in D-011 and in comments in the flowsheet). It should be reported to core.
- **Process inputs still missing:**
  - Sourced feeds and capacity.
  - Verifying the Douglas values.
  - Possible hydrogen recovery from the purge, and a benzene absorber on it.
  - The vacuum system for the toluene column.
  - Materials for hot hydrogen service.
  - A fugitive emission estimate (needs P&IDs).
  - Every LCA background.
  - The biphenyl reaction ends slightly past equilibrium at the reactor outlet; this is flagged in D-005.

## Recommended next stage
1. Have the branch independently reviewed.
2. Check Douglas at its exact location and get a sourced toluene and hydrogen specification. That should lift maturity to "sourced".
3. Choose open background datasets for the LCI and decide the allocation.
4. Once core #315 provides a package for aromatics with hydrogen, rerun props and simulation to replace the script's values.

**Merge pending:** the branch needs a review before it can go to `main`. Nothing was signed off or pushed.
