I finished the concept-stage scope for issue #135: a balanced BFD/PFD, the design basis and a preliminary gate-to-gate LCI, all committed in 4 commits on `case/phosphorus-oxychloride-1`. The pre-commit hook passed every time and the working tree is clean. Nothing is pushed, and no stage sign-off was written.

## Route and boundary
The PCl3 is made inside the plant boundary. Molten white phosphorus is chlorinated in a boiling PCl3 still (R-101). The PCl3 is then oxidised in the liquid phase with 5 % excess oxygen in a cooled loop reactor (R-201), and unconverted PCl3 is recycled from a light-ends column (C-301). A product column (C-302) takes the POCl3 overhead and purges a 0.5 % residue. The vents from both reactors go to a caustic scrubber (T-401).

I put the PCl3 step inside the boundary for two reasons. First, chlor-alkali-1's chlorine can be used as delivered: its 0.8 wt% O₂ just turns a little PCl3 into POCl3, which is product anyway. Second, this way the 0.70 kg/kg chlorine demand shows up in the inventory instead of being hidden in a purchased PCl3 feed. Chlorine and caustic come from chlor-alkali-1, oxygen from asu-1; white phosphorus has no library process yet.

## Results
- **Mass balance:** `cheme validate` reports 0 errors and 0 warnings. All 4 blocks and 10 steps close in `cheme process streams`, with consistent reaction extents. The script's overall balance closes to 0.0065 kg/h on 4088 kg/h, and phosphorus atoms close exactly. 99.44 % of the phosphorus reaches the product.
- **Product:** 4000 kg/h at 99.998 wt% POCl3 with 21 ppm(wt) PCl3.
- **Energy balance:** cheme calculates both reactors as conversion models. Its ideal-gas duty for R-201 (−1861.6 kW) is 2.7 % below my liquid-phase value of 1912.3 kW. That fits, since the ideal-gas basis leaves out heats of vaporisation. The 277 kJ/mol I used also lies inside the 255–320 kJ/mol range implied by US4183905. Core cannot evaluate the energy balance itself (see gated steps).
- **Gates:**
  - Concept: 6 ok, 1 fail. The failure is the plot plan, which was out of scope.
  - Maturity: `cheme maturity` reaches no level, because feeds and conversions are ASSUMED. The `concept` claim stays (it is the lowest level the manifest allows), as in phosgene-1.
  - Validate info: one note flags D-023 cited in the template's `checks/checks.yaml`, a scaffold leftover I left alone.
- **LCI per kg POCl3:**

| Exchange | Amount |
|---|---|
| White phosphorus | 0.2031 kg |
| Chlorine feed | 0.7036 kg |
| Oxygen feed | 0.1046 kg |
| Caustic soda 50 wt% | 3.87 g |
| Process water | 6.88 g |
| Electricity | 12.9 Wh |
| LP steam | 90.7 Wh |
| Heat to cooling water | 1.170 kWh |
| Heat to chilled water | 0.09 Wh |
| Residue to incineration | 5.03 g |
| Spent scrubber liquor | 11.5 g |
| Cl2 / PCl3 / POCl3 to air | 3.5e-8 / 7.7e-9 / 5.0e-8 kg |

  - Inventory mass in (1.022096 kg) and out (1.022094 kg) match the flowsheet to 1.6e-6 kg/kg.
  - Coverage is "partial": 11 backgrounds are left unmapped as gaps (none set to zero), and the three chloride emissions have no GWP100 factor.

## Files produced
- `process/` (design basis, materials, reactions, flowsheet, BFD/PFD)
- `scripts/balance.py` (the independent balance)
- `lca/` (`lca.yaml`, an empty `mappings.yaml` on purpose, and the generated outputs)
- `process.yaml` (status internal, concept, unreviewed)
- `plant.yaml`, `DESIGN.md` (source register, decisions D-001 to D-013), `PROGRESS.md`, equipment list (19 items), line list (empty until there are P&IDs)

## Sources
- US4183905: oxidation conditions, oxygen excess, heat removal, the explosion hazard of PCl3 vapour with oxygen.
- US5183649: loop reactor, temperature range, distillation.
- CN115259114B: molten phosphorus handling, P:Cl2 ratio, condensing the PCl3 tail gas.
- `cheme chemistry thermo` data (CRC and others) for formation enthalpies, vapour pressures and heats of vaporisation.
- chlor-alkali-1 stream S42 and asu-1 streams S7/S8 for the feeds.
- Ullmann's was not read (licensed).

## Key ASSUMED values
- Capacity 4000 kg/h at 8000 h/a.
- R-101: phosphorus fully converted, 0.05 % chlorine excess.
- R-201: 99.5 % PCl3 conversion per pass, 5 % oxygen excess, 20 K rise across the loop cooler.
- Vent condensers at 283 K, because POCl3 freezes at 274 K.
- C-301: reflux ratio 3, 99.5 % PCl3 recovery. C-302: reflux ratio 0.5, 0.5 % residue.
- Scrubber: 99.99 % destruction, 1.5 × stoichiometric NaOH.
- Pumps 300 kPa at 0.55 efficiency, agitator 11 kW.
- Liquid heat capacity 0.9 kJ/(kg K): thermo's PCl3/POCl3 values looked implausibly low, so I didn't use them.

## Missing shared registry entries (for the consolidated PR)
- `chemicals/chemicals.yaml` needs: phosphorus (white P4), chlorine, sodium-hydroxide, phosphorus-trichloride, phosphorus-oxychloride.
- `lci/mappings.yaml` needs entries for: white phosphorus, chlorine, sodium hydroxide, chilled water, incineration of chlorinated liquid waste, and phosphorus oxychloride.
- No biosphere identities exist yet for Cl2, PCl3 or POCl3 to air.
- There is no phosphorus-chemicals family in the taxonomy; I used `inorganic-chemicals`.
- I left the CAS number of disodium phosphite blank because I couldn't verify it.

## Open inputs and gated steps
- **Core #315 (properties):** no property package covers PCl3, POCl3, P4 or chlorine mixed with them. So the vent condensers, columns and energy balance come from `scripts/balance.py`, and column stages and sizes are not calculated.
- **Core #364 (electrolytes):** the caustic liquor is not covered.
- I couldn't open either core issue with `gh`. The gate is real anyway: `props --coverage` lists every stream as unsupported.
- **Open inputs:** phosphorus impurities, water and mud; the commercial POCl3 specification; the residue amount; R-201 kinetics and oxygen mass transfer; recovering R-101's heat as steam; all LCI backgrounds.

**Recommended next stage:** have someone independently review the concept PFD and the LCI. Once core supports these species, simulate the condensers and columns and close the energy balance. Then map the backgrounds, linking to chlor-alkali-1, asu-1 and the utility processes.

There is no merge pending a decision: the branch has not been reviewed or merged.

STATUS: DONE