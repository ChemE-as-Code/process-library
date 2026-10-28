I've built the bromine-1 concept case: a balanced flowsheet with BFD and PFD, and a preliminary gate-to-gate inventory (LCI) per kg of bromine. Everything is committed on `case/bromine-1` (6 commits, clean tree, nothing pushed). Mass, component and element balances close in cheme, but every stream value comes from my own balance script and is entered as `assumed`, so `cheme maturity` rates the evidence as **none**.

**Files produced** (all in `processes/bromine-1/`)
- **Process files:** `process/design-basis.yaml`, `materials.yaml`, `reactions.yaml`, `flowsheet.yaml`, `simulation.yaml` (it only declares C-101 and T-107 as having no utility heat port; the tower is heated by injected steam), and the generated `BFD.xml` and `PFD.xml`.
- **Balance script:** `scripts/balance.py`, independent of cheme.
- **Lists:** `equipment/equipment-list.yaml` with 8 items. The line list stays empty until there are P&IDs, as in hydrogen-chloride-1.
- **Inventory:** `lca/lca.yaml`, `lca/mappings.yaml` (no overrides yet, candidates listed), and the written `inventory.csv`, `gaps.csv`, `dataset.yaml`, `manifest.json`.
- **Records:** `process.yaml` (internal, concept, unreviewed), `DESIGN.md` (decisions D-001 to D-013, source register, checks, gated steps, open inputs), `PROGRESS.md`, `plant.yaml`.

**Route:** chlorine oxidises the bromide of a hot Smackover-type brine in a steaming-out tower with live steam. The overhead is condensed and decanted; the bromine water and the chlorine stripped from the crude bromine both go back to the tower. The bromine is dried with 98 % sulfuric acid, and the spent brine ("tail brine") is neutralised with lime and reinjected. Capacity is 3 750 kg/h Br2 (30 kt/a), which I chose.

**Balance and checks**
- `cheme validate`: 0 errors, 0 warnings. `cheme process streams`: all 4 blocks and 8 steps balance.
- Concept gates: 6 ok. The plot plan fails because layout was out of scope.
- Comparison with the sources:

| quantity | model | source | result |
|---|---|---|---|
| chlorine | 0.571 kg/kg Br2 | 0.55–0.60 (patent US 4 719 096) | inside |
| bromide left in tail brine | 189 mg/kg | 50–200 ppm (same patent) | inside |
| bromine recovered per barrel of brine | 1.73 lb | 1.5–1.8 (Arkansas Geological Survey) | inside |
| live steam, from my own energy balance | 5.82 kg/kg Br2 | 5.2–5.7 (same patent) | 2 % above the range |

**Inventory per kg of bromine:**

| exchange | amount |
|---|---|
| brine | 243.41 kg |
| chlorine | 0.5705 kg |
| live steam | 5.815 kg |
| reboiler steam | 0.0162 kWh |
| sulfuric acid | 0.00209 kg |
| hydrated lime | 0.1323 kg |
| electricity | 0.0322 kWh |
| cooling water | 0.179 kWh |
| tail brine (out) | 248.93 kg |
| spent acid (out) | 0.00256 kg |

- Mass in = mass out = 249.932 kg, and the element balance closes.
- All 10 background links are reported as gaps with a description of the activity each should connect to; none is set to 0.
- The balance has no emissions to air or water. The vent, possible H2S/ammonia releases, leaks and upsets are declared as exclusions with reasons.

**Sources:**
- US 4 719 096 (Detailed Description and Background): brine constituents, temperatures, chlorine and steam use, recovery. US 4 725 425 corroborates the brine range.
- Arkansas Geological Survey "Bromine (Brine)": bromide content and pounds recovered per barrel.
- Wikipedia "Bromine" and "Bromine production in the United States": route steps and scale context.
- Boldyryev and Varbanov 2014 was read but gave no usable numbers.
- The heats of reaction come from the NBS 1982 tables as I recalled them; I did not re-read them (open item O-5).

**Key assumed values:** brine calcium (30 000 mg/kg) and density (1.2 kg/L); brine water activity (0.75) and heat capacity (2.9 kJ/kg K); 250 ppm H2S as the only side reaction using up the excess chlorine; crude bromine and bromine water compositions; product specification; spent acid at 80 %; pump and drive power. Chlorine is taken as inert-free liquefied chlorine rather than chlor-alkali-1's gas as delivered, which carries oxygen.

**Missing registry entries:** `bromine`, `chlorine`, a bromide brine, `sulfuric-acid`, `calcium-hydroxide`, plus shared mappings for brine extraction, brine reinjection and spent acid treatment. Because of this, `process.yaml` has to list `water` as a placeholder input, with a note saying so.

**Open inputs and gated steps:** no installed cheme route covers this calcium/sodium chloride brine with bromine (it supports only NaCl-water). That blocks enthalpies, energy closure in core, a check that salt doesn't crystallise out, and a DWSIM run. I couldn't read core issues #364 and #369 from this account; #369 (liquid-liquid extraction) doesn't apply to this route. Other open items are a full brine analysis, the real side reactions, the vent and its scrubber, and free halogen left in the tail brine. One note left in `checks/checks.yaml` (unchanged from the scaffold) cites a decision D-023 that DESIGN.md doesn't have.

**Recommended next stage:** model the tower properly once a property method covers the brine, close the brine analysis and side-reaction items, and evaluate preheating the feed with the hot tail brine and the vacuum variant. Heating the brine (13.9 MW) exceeds the tower's whole net demand, so this is the main energy lever. P&IDs come after that. No stage was signed off; review and merge of `case/bromine-1` are pending.

STATUS: DONE