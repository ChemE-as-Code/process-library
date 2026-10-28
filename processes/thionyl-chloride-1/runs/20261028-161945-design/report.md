I've taken thionyl-chloride-1 through the concept stage: design basis, a balanced BFD/PFD and a preliminary gate-to-gate LCI, in four commits on `case/thionyl-chloride-1`. `cheme validate` reports 0 errors and 0 warnings. Every stream value and duty comes from my own balance script, not from cheme's property models, because none of them covers the sulfur chlorides or thionyl chloride. Nothing is pushed or merged, and no stage is signed off.

**Files produced**
- `process/`: design basis, components, reactions and flowsheet (5 blocks, 20 steps, 50 streams), plus the generated `BFD.xml` and `PFD.xml`.
- `scripts/balance.py`: the independent heat and material balance.
- `process.yaml`: publication internal, maturity concept, unreviewed.
- `lca/`: `lca.yaml`, `mappings.yaml` (empty on purpose), and `inventory.csv`, `gaps.csv`, `dataset.yaml`, `manifest.json`, results written by cheme.
- Equipment list with 15 items; the line list stays empty with a note, since line numbers come with the P&IDs.
- `DESIGN.md` (source register, decisions D-001 to D-013, method and dependency table, open inputs) and `PROGRESS.md`.

**Route**
- Molten sulfur and chlorine make S2Cl2 and then SCl2 inside the boundary.
- SCl2 reacts with SO2 and Cl2 over activated carbon (inlet 398 K, outlet 473 K).
- The gas is condensed with cooling water and brine to 263 K and degassed. The SO2/Cl2 gas is recompressed and recycled; 1 % is purged to a caustic scrubber to carry out the oxygen that comes in with the chlorine.
- The crude is distilled with sulfur added, which turns the remaining SCl2 into S2Cl2 so it leaves in the bottoms; the bottoms go back to the chlorination.

**Balance, check and LCI results**
- **Balances:** all 5 blocks and 20 steps close on mass, components and elements within tolerance, and `cheme process propagate --check` agrees.
- **Reactor duty:** cheme reproduces the script's value (−386.56 kW).
- **Plant mass balance:** 3805.00 kg/h in against 3804.99 kg/h out (product plus purge).
- **Crude and yields:** the degassed crude is 84 wt% SOCl2 and 16 wt% SCl2. Yield is 98.1 % on SO2 and 99.0 % on sulfur atoms.
- **LCI per kg of product:**

| Exchange | Amount |
|---|---|
| Sulfur | 0.1357 kg |
| Chlorine | 0.5980 kg |
| SO2 | 0.2738 kg |
| Caustic soda, 50 wt% | 0.0211 kg |
| Process water | 0.0844 kg |
| LP steam (500 kPa(a)) | 0.422 kWh (1.52 MJ) |
| Electricity | 0.0047 kWh |
| Cooling water | 0.501 kWh |
| Brine | 0.119 kWh |
| Spent scrubber liquor | 0.1127 kg |
| Vent (mostly O2; 5.3 mg SO2, 1.7 mg Cl2) | 0.28 g |

- **LCI checks:** inputs and outputs are both 1.11300 kg/kg; `--coverage` reports mass, element and carbon-origin balances closed.
- **Gaps:** 15, by design. Every background is unmapped with a description of the activity it should connect to, so there is no impact result.
- **Gates:** concept gates are 6 ok and 1 fail; the failure is the plot plan, which was out of scope.
- **Maturity:** `cheme maturity` reaches no level, because the feeds and conversions are assumed. This is the same result phosgene-1 had.

**Sources** (facts restated in my own words, with locators in `DESIGN.md`)
- **US2431823A:** temperature window, preferred excesses (about 100 % SO2, 0–10 % Cl2), recycle of the off-gas and the still bottoms.
- **DE2430631A1:** 70–75 % conversion per pass (50–80 % stated), 160–240 °C, treating the crude with sulfur.
- **US4759826A:** crude composition range, distilling with sulfur, finished-product purities.
- **EP0042530B1:** sulfur dose of 1–15 wt%. I only saw this at abstract level.
- **Property data:** the `thermo` package for vapour pressures and heats of vaporization; cheme's thermochemistry lookup for ideal-gas data.
- **Not used:** Ullmann's *Sulfur Halides* chapter is licensed, so I did not read it. I did not search for published benchmark answers.

**Key ASSUMED values**
- 3750 kg/h (30 kt/a at 8000 h).
- Product 99.7 wt% SOCl2, 0.1 wt% SCl2, 0.2 wt% S2Cl2.
- Chlorine with 0.1 mol% O2.
- SCl2 chlorinator converts 90 % of the S2Cl2; the reactor converts 95 % of the S2Cl2 entering it.
- Reactor outlet 473 K.
- Separator 263 K; the degasser removes SO2 and Cl2 completely.
- Purge 1 % of the recycle gas.
- Sulfur dose 1.10 × stoichiometric; 20 wt% SOCl2 left in the bottoms; reflux ratio 2.
- Scrubber removes 99.9 %, with NaOH at 1.2 × consumption.
- Machine efficiencies and pressure profile.

**Open points and gated steps**
- **Equilibrium conflict:** on ideal-gas data the equilibrium would allow almost complete conversion (ln(Q/K) = −8.6), while DE2430631A1 says the 50–80 % is set by equilibrium. I kept the patent figure as a sourced empirical conversion and left the conflict open.
- **Energy balances gated:** vapour–liquid equilibrium and liquid energy balances (condensers, degasser, column, chlorinators) are gated on core issue 315; the scrubber liquor on core issue 364. I couldn't open either issue from this session.
- **Not in the inventory:** activated-carbon make-up and the iron catalyst (amounts unknown, recorded as cut-off), plus fugitive, storage and start-up emissions (recorded as exclusions).
- **Open inputs:** capacity and site, feed impurities, a kinetics or bed-sizing basis for the reactor, an SO2Cl2 specification, column design, emission limits for the vent, and using the reactor heat to raise LP steam.

**Missing shared-registry entries** (for the consolidated PR)
- `chemicals.yaml` has no entries for thionyl-chloride, sulfur, sulfur-dioxide (liquid), chlorine, sodium-hydroxide (50 wt%), or brine refrigeration at 253 K.
- `lci/mappings.yaml` and the cheme crosswalk have no biosphere identity for Cl2, SOCl2, SCl2 or S2Cl2 to air.

**Recommended next stage:** have the PFD and its assumptions reviewed. Then move the balance onto a qualified property method once issue 315 allows, map the backgrounds once the registry entries exist, settle the carbon life and the vent limits, and start basic engineering (P&IDs, HAZOP).

A merge is pending: the branch is ready for review and must be merged by a human or reviewer, not by me.

STATUS: DONE