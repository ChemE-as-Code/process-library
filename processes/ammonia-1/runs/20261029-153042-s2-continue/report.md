S2 is finished on core v1.0.1: the whole process side, including the synthesis loop and the purge recovery, now converges in one DWSIM solve for the design case (the design basis has only that one case). The only section gate that fails is `maturity-balanced`, and it fails for lack of sources, not because of a core limit.

**Simulation**
- **Convergence:** 7 tears, including the loop, the purge-recovery return and the product flash gas; 121 passes. `simulate --check` exits 1, but only because of the deviation warnings below; there are no errors and nothing is stale.
- **Values written:** 105 streams are now `calculated`. The concept loop values from the first session are gone, and the obsolete script that produced them is removed. Given and assumed values were never overwritten.
- **Loop model:** built as DESIGN.md D-024 described, with changes the runs forced (recorded in the new decision D-026):
  - **Let-downs as valves:** a DWSIM vessel given only a pressure keeps its inlet temperature, so the first run sent the product flash to 313 K and the flash-gas loop ran away. The let-downs are now valves.
  - **Product flash:** an adiabatic let-down to 110 kPa(a) fails DWSIM's flash for this mixture, so V-701 runs at its adiabatic temperature, 238.7 K. Its duty, −32 kW, is the check.
  - **Converter:** DWSIM's adiabatic equilibrium reactor still fails, so R501 runs at its 703.15 K outlet temperature. Its duty, 31 kW, is 0.1 % of the reaction heat.
- **P301** is now a `Pumping` step (the core#59 fix works).
- **Left out:** the furnace radiant section, the steam system and the chiller refrigeration circuit. The last two need flows set from duties, which core cannot do; a new script re-evaluates them on the simulated duties, and those values stay ASSUMED.

**Retunes** (design choices recorded in D-026; no simulated value was edited)
- **Process air:** 67,184.1 kg/h, giving H2/N2 = 3.007 at the converter inlet (the first session had 2.85). The ratio moves about 0.008 per kg/h of air, so the plant will need an H2/N2 analyser trimming the air flow.
- **E-502 outlet:** 532.6 K, so the converter runs adiabatic. At the concept's 547 K it needed −3.3 MW.

**Results**
- Product: 62,470.7 kg/h (1,499.3 t/d), 99.981 mol% NH3.
- Loop: converter feed 294 t/h, NH3 3.3 → 18.4 mol%.
- Utilities: hot 69.5 MW, cold 254.8 MW, power 24.7 MW.
- LCA and TEA regenerated: 1.475 kg CO2 per kg NH3 (direct emissions only), cost 738.6 EUR/t (was 739; the decision is unchanged).

**Findings kept as deviations**
- The product leaves at 238.7 K, not the design basis's 240.15 K. This needs an owner decision.
- The tail gas S59 and the hydrogen return S36 come out at different states than the purge-recovery assumptions.
- From the first session, still open: stack 396.7 K (assumed 423 K), the S28/S35 pressures, and Q18 not written.
- `cheme validate` reports 0 errors and 1 warning: on K601, two Peng-Robinson implementations disagree by 2.2 kW.

**Energy audit:** every simulated unit closes (largest residual 0.17 kW) and no exchanger has a temperature cross. Core cannot evaluate the whole-plant closure while component separators are in the flowsheet (core#60).

**`cheme maturity`:** calculation maturity is none. The failing requirements:
- `sourced.boundary`: no sourced composition or pressure for the natural gas (R-03/I-01); the air and water feeds are unsourced too.
- `balanced.model-basis`: the complete conversions in four reactors are assumed.
- `predictive.coverage`: three parts are excluded.
- `predictive.model-basis`: conversions and splits are specified, not predicted.
- `predictive.property-regime` (core#315): core's benchmarked range for DWSIM Peng-Robinson covers only N2, O2 and Ar, which puts 266 stream cases outside it.
- `predictive.energy-closure`: not supported (core#60).

Commits `a1ba516`, `fb0e691` and `9c3663c` are on `stage/basic-simulation`, and the working tree is clean. The PR description for both sessions is in `build/pr-body.md`; it also lists four new core findings for the orchestrator. The merge is pending the independent review.

STATUS: DONE