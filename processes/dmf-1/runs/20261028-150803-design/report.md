I've built the dmf-1 case up to a balanced PFD and a preliminary per-kg LCI, in three commits on `case/dmf-1` (scaffold `d698c25`, design `a8f0133`, LCI `82b3933`). `cheme validate` reports 0 errors. The calculation maturity `cheme maturity` reports is "none", against the claimed "concept". Energy closes only for the CO compressor; the other units are gated on core #315.

**Files produced**
- **Process:** `process/design-basis.yaml`, `materials.yaml` (9 components), `reactions.yaml`, `flowsheet.yaml`, and the generated `BFD.xml` and `PFD.xml`. The PFD has 3 blocks, 9 steps, 17 material and 11 energy streams.
- **Balance:** `scripts/dmf_balance.py`, a short-cut balance run with `cheme run`. It supplies the separator and column splits and all duties.
- **Lists and records:** `equipment/equipment-list.yaml` (16 items, all PFD links resolve), `DESIGN.md` (decisions D-001 to D-012, source register, dependency table), `PROGRESS.md`, and a filled `process.yaml` (`internal`, `concept`, `unreviewed`, references).
- **LCI:** `lca/lca.yaml` and `lca/mappings.yaml`, plus the written outputs (`inventory.csv`, `gaps.csv`, `dataset.yaml`, `manifest.json`, results). The template's P&ID folder is untouched.

**Route and balance (design case)**
- **Route:** dimethylamine + CO, sodium methoxide in methanol, loop reactor at 90 °C and 22 bar. The catalyst is turned into sodium formate and dimethyl ether under CO; the salt is filtered off, methanol and DMA are recovered and recycled with a 2.6 % purge, and DMF is distilled under vacuum.
- **Rates:** 3902 kg/h DMA, 2546 kg/h CO and 99 kg/h catalyst solution give 6250 kg/h of DMF.
- **Balance:** total in 6547.30 kg/h, out 6547.29 kg/h. Every block and step closes, and both reactions balance by element.
- **Duties:** reactor cooler 2429 kW, CO compressor 207 kW, recovery column reboiler 1299 kW (MP steam), DMF column reboiler 1393 kW (LP steam).

**LCI per kg DMF** (all exchanges taken from flowsheet streams)

| Exchange | Amount |
|---|---|
| DMA | 0.624 kg |
| CO | 0.407 kg |
| Catalyst solution | 0.0158 kg |
| Electricity | 0.043 kWh |
| MP steam (as heat) | 0.208 kWh |
| LP steam (as heat) | 0.223 kWh |
| Heat to cooling water | 0.881 kWh |
| Vent gas | 0.0221 kg |
| Salt cake | 0.0079 kg |
| Methanol purge | 0.0074 kg |
| Heavy residue | 0.0102 kg |

- **Gaps:** cheme classes the result as partial screening with 11 declared gaps, each naming the background it should connect to. No impact number is claimed.
- **Balance check:** mass, C, H, N, Na and O all close within 0.01 %.
- **Atlas build:** the library's `build_lci.py --strict` builds dmf-1 with 7 reported gaps and no errors. Its exit code is still 1, but only because of warnings on other processes (core's units and cut-off modules aren't importable in that environment).
- **Utilities in the Atlas:** electricity, steam and cooling water link through the library's shared utility entries, not as gaps; in cheme's own LCA they stay gaps. The only overrides in `lca/mappings.yaml` are the standard `steam-heat` unit fix for MP and LP steam.
- **Methanol purge:** I counted it as waste to incineration, a gap. Treated as recyclable it would have left burden-free, and no recovery is arranged.

**Sources:** patents US 4,098,820 (reactor conditions, conversion and yields, catalyst rate), US 4,354,041 (catalyst deactivation and filtration), US 4,302,598 (the catalyst-recycle alternative I rejected) and US 4,251,460 (residue size and steam use, as a plausibility check). Also the NIST WebBook (heats of formation; the heat of reaction comes out at −109.9 kJ/mol against the patent's ~113) and Eastman's DMF sales specification. The Ullmann chapters were not read (licensed).

**Key ASSUMED values**
- 50 kt/a at 8000 h/a; no published plant basis was found.
- CO at 99.5 % with N2/H2 impurities; catalyst bought as a 30 wt% solution, fully deactivated.
- Vent organics; 99 % salt capture with a cake holding 25 % liquor.
- Sharp column splits with reflux ratios 1.0 and 0.5; 1 % of the DMF lost to the residue.
- Product methanol 30 ppm (spec is 50 ppm); utility levels, efficiencies and pump power.
- The heat of the deactivation reaction is neglected.

**Missing registry entries (for the shared PR):** chemicals DMF, dimethylamine, carbon monoxide, methanol, sodium methoxide, sodium formate and dimethyl ether. Shared LCI entries for DMA, CO and the catalyst solution, hazardous solid and liquid waste incineration, spent-solvent treatment and vent-gas thermal oxidation. The CPC code of DMF, left out because I couldn't check it.

**Open inputs and gated steps**
- **Energy:** all units except the CO compressor are gated on core #315; no property package covers DMF, methanol, DMA and the salts.
- **Core issues found:**
  - A `Pumping` step crashes `cheme process build`, so P-101 is declared as its parent class.
  - `propagate` rounds the filter-cake fractions so they sum to 1.0000011, which leaves 2 warnings in `cheme validate`.
  - There is no flowsheet category for liquid waste.
- **Not in the inventory:**
  - CO2 and NOx from oxidising the vent (about 0.03 kg CO2 per kg DMF).
  - Leak and storage emissions.
  - Construction.
- **Not done:** comparison with the methyl formate route; kinetics.
- **Gate failures:** at concept, only the plot plan; at basic, P&IDs, reviews, layout and MTO, which are out of scope here.

**Recommended next stage:** have the gaps and assumptions reviewed, then map the backgrounds once methylamines-1 and a CO supply exist. The predictive step needs sourced NRTL parameters for DMF–methanol–DMA and the core #315 qualification before a DWSIM run.

No stage was signed off; this branch is not pushed and is waiting for review and merge by a person.

STATUS: DONE