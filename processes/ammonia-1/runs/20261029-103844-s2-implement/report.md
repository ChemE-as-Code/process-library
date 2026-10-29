S2 is only partly done: the front end is simulated and filled, but the synthesis loop and purge recovery can't be converged through core v1.0.0, so the section's gates don't pass. Everything is committed on `stage/basic-simulation` (`be8a34c`, `af54ba0`, `4daf68d`) and the PR description is in `build/pr-body.md`.

**What runs**
- **DWSIM:** it starts. Reforming without the furnace radiant section, shift, CO2 removal and methanation/drying converge for the design case, the only case in the design basis. 58 streams are now `calculated`; no given or assumed value was overwritten.
- **Recycles:** the three recycles in that part converge (S4 and S9 at the convection coils, S27 at the methanator feed heater).
- **Property package:** Peng-Robinson. For this polar mixture at 155 bar the model-selection skill recommends equations of state with polar mixing rules (PSRK, PR-MHV2) that DWSIM doesn't run, and Peng-Robinson is their listed substitute. I recorded it as a substitution, justified by the brief's "cubic EOS"; the reviewer needs to accept or reject it.
- **CO2 removal (aMDEA):** it needs an electrolyte model with rate-based absorption, which core refuses, so it stays a specified split.
- **Gates:** `cheme validate` shows 0 errors and 0 warnings, and `process-balances` and `process-basic` are OK.
- **Energy audit:** every simulated reactor closes; no exchanger has a temperature cross. Core doesn't evaluate the whole-plant closure while the CO2 removal and dryer separators are in the flowsheet, and block balances need stream enthalpies that core#315 can't supply (no property package covers H2O, O2 or C2H6).

**What blocks the section**
- **Synthesis loop and purge recovery:** I modelled them in DWSIM, but they don't pass core's recycle test. In every run the first loop recycle settles exactly, while the second recycle's copy never moves off its guess (S39-R stays at 240,150.9 kg/h against 240,077.3 computed). DWSIM then reports "maximum iterations" and core writes nothing. Core's recycle settings can't be changed from the project, and I didn't work around them.
- **Interim loop values:** until that's fixed, the loop and purge recovery keep the concept balance's loop model, re-solved on the simulated make-up gas (`scripts/loop_on_simulated_makeup.py`, values ASSUMED). The evidence and a loop model ready to run are in DESIGN.md D-024.
- **Steam system:** not simulable in core, which has no way to set a flow from a duty and can't share one energy stream between two units.
- **Maturity:** I enabled `maturity-balanced` as the template documents it; it fails, and `cheme maturity` reports "none". The causes are the unsourced natural-gas feed (R-03/I-01, open since S1), unsourced conversions, and the missing enthalpies (core#315).

**Findings (recorded as deviations, not edited away)**
- **Stack temperature:** the flue gas leaves at 395.9 K instead of 423 K, because the convection coils take 1.75 MW more with the concept fuel flow. The furnace balance needs redoing once the radiant section can be simulated.
- **H2/N2 at the converter inlet:** 2.85 instead of the design 3.0 in the re-solved concept loop. The process air needs retuning once the loop runs. Product is 1,498.5 t/d (−0.1 %).
- **E-203 duty:** 34.7 MW, against 31.2 MW in the concept balance.

**Core problems to file**
1. The loop recycle behaviour above (this is the blocker).
2. DWSIM's equilibrium reactor fails in adiabatic mode. I ran those beds at their concept outlet temperatures and used the duty as the check (0.4–2.6 % of the reaction heat). A side effect is that the LCA boundary check now flags R102B, R201 and R202.
3. `cheme process build` crashes on the DEXPI class `Pumping`, so the new make-up water pump is a generic step with `unit: pump`.
4. Whole-plant energy closure is unsupported whenever a component separator is in the flowsheet.

**Changes to earlier work (BFD/PFD regenerated)**
- **Convection section:** the coils are now exchangers on the flue gas (S80–S84).
- **Methanator feed:** E-401 is now heated by the high-temperature shift effluent.
- **CO2 removal feed:** a make-up water pump P301 and mixer M301 sit ahead of it.
- **Air compressor:** K-101's fourth stage is its own uncooled step, K101D.
- **Steam system:** a vent S87 takes out the CO2 the simulation finds dissolved in the condensates.
- **LCA:** outputs regenerated.

The branch is not merged; it needs review, and the loop needs a core fix or your decision.

STATUS: BLOCKED: the synthesis-loop and purge-recovery recycles fail DWSIM's recycle test through core v1.0.0 (first recycle converges, the second never updates); needs a core fix