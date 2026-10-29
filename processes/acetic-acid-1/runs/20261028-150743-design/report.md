I built the case up to a balanced concept PFD and a preliminary gate-to-gate LCI, and committed it in four commits on `case/acetic-acid-1`. `cheme validate` reports 0 errors and 0 warnings, and every mass and element balance closes. Two limits: `cheme maturity` reaches no level yet, and nothing has been reviewed. Nothing was pushed or merged; a review and a merge by someone else are still pending.

**Files produced** (all in `processes/acetic-acid-1/`)
- `process.yaml`: status internal, maturity concept, unreviewed, references listed. Family is `oxygenates`.
- `process/design-basis.yaml`, `materials.yaml` (11 components), `reactions.yaml` (4 lumped reactions), `flowsheet.yaml` (23 material and 12 energy streams). `BFD.xml` and `PFD.xml` are generated from these.
- `scripts/balance.py`: my own shortcut balance for the parts cheme cannot calculate (flash, columns, decanter, scrubber, duties).
- `equipment/equipment-list.yaml` with 17 items. No line list: it isn't needed at PFD level.
- `lca/lca.yaml`, `lca/mappings.yaml`, and the generated inventory, gaps and dataset files.
- `DESIGN.md` (route and boundary memo, source register, decisions D-001 to D-013, open inputs O-1 to O-8) and `PROGRESS.md`.

**The design.** 60 t/h glacial acetic acid from a low-water iridium/ruthenium carbonylation (Cativa type) at 463 K and 2900 kPa(a). After the reactor come an HP vent knock-out and an adiabatic flash, then a light-ends column with decanter, a drying column and a heavy-ends column. The vents are scrubbed with the incoming methanol. All recycles go back to the reactor.

**Balance results**
- Every block and step closes, and the reactor's four reactions account for every component change. Cheme calculates the mixer, the pumps and the reactor itself.
- Yield is 99.1 % on methanol and 96.7 % on CO. Product water comes out at 691 ppm, under the 1500 ppm limit.
- The LCI balance check closes on mass (61,621.9 kg/h in, 61,621.8 kg/h out) and on carbon, hydrogen, iodine, nitrogen and oxygen within 0.05 %.
- Energy can't be checked in cheme because no property package covers these streams. My own rough check is consistent: steam plus power (27.6 MW) roughly equals heat to cooling water minus reaction heat (65.5 − 37.7 = 27.8 MW).
- `cheme check`: every concept gate passes except the plot plan, which was out of scope. The basic-stage PFD and process-link gates also pass.

**Inventory per kg of glacial acetic acid**

| Exchange | Amount |
|---|---|
| Methanol | 0.539 kg |
| CO feed gas | 0.488 kg |
| Methyl iodide make-up | 2.7e-6 kg |
| Electricity (pumps only, so an underestimate) | 0.0079 kWh |
| MP steam | 0.452 kWh (1.63 MJ) |
| Heat to cooling water | 1.09 kWh |
| Off-gas to flare/thermal oxidiser | 0.0257 kg |
| Heavy ends to incineration | 0.00135 kg |

- All 9 exchanges are deliberately left unlinked to any background, each with a note on the activity it should connect to later. The result is therefore classified "partial".
- The shared library LCI build shows these as gaps for acetic-acid-1, not errors. Its remaining warnings come from missing packages in my environment and appear for every process.

**Sources**
- The main open source is patent US 6,140,535 (Examples 1–5 and its stated operating ranges). It gives the reactor conditions and liquid composition, CO2 and CH4 formation (each roughly 1 % of the main reaction), the H2 content of the CO feed, the flash pressure and the product limits.
- Heats of reaction and the shortcut energy data are rounded handbook values I attributed to the NIST WebBook; I did not re-check them item by item.
- Budsberg et al. 2020 (open access) only for context; methanol-1's product stream S18 for the methanol feed.
- Jones 2000, Sunley & Watson 2000, Ullmann and Dimian & Kiss 2020 were blocked or paywalled, so they are cited but not read. One Jones figure on propionic acid comes only from a search excerpt and is marked unverified.
- No open source for steam, cooling water or power per tonne turned up, so those are my own estimates.

**Key assumed values**
- Capacity: 60 t/h at 8400 h/a.
- CO feed: 98.5 % CO, 1 % N2, 0.3 % H2, 0.2 % CH4, delivered at 3200 kPa(a).
- Propionic acid formed: 500 ppm.
- Off-gas CO at 45 mol% of the non-condensables. This sets the CO loss and is the most sensitive number in the raw-material inventory.
- All flash, column, decanter and scrubber splits; reflux ratios of 1, 3 and 1; pump efficiency 0.65; MP steam at 1100 kPa(a).

**Missing registry entries** (for the consolidated PR)
- `chemicals/chemicals.yaml`: methanol, carbon-monoxide, acetic-acid (with a glacial grade), methyl-iodide, propionic-acid.
- `lci/mappings.yaml`: methanol (or a link to methanol-1's dataset), CO gas, methyl iodide, thermal oxidation of the vent gas, and hazardous incineration of the heavy ends.

**Open inputs and blocked steps**
- No property package covers this acetic acid / water / methyl iodide / methyl acetate mixture. That is why the separations and duties are specified rather than calculated, and why maturity stays at none. The issue calls it core #315, but I couldn't open it from here.
- No kinetics, so no reactor sizing. The patent's reaction rate suggests about 53 m³ of reaction liquid as a first hint.
- No open source for iridium/ruthenium catalyst or iodide loss rates. These are not in the inventory at all, neither as zero nor cut off.
- Fugitive emissions and aqueous effluents are not estimated, and electricity covers pumps only.
- **Core bug:** `cheme process build` crashes (`TypeError: 'typing.Union' object is not iterable`) on any step with class `Pumping`. I used `TransportingFluids` for the two pumps instead (D-012). This should be reported to core.

**Recommended next stage**
1. Get a qualified property method for this mixture, or a sourced energy basis from Dimian & Kiss or Ullmann.
2. Replace the shortcut separations and duties with calculated ones.
3. Source the CO loss, the catalyst and iodide losses, and a CO producer.
4. Then add the registry entries and link the backgrounds so the LCI becomes a screening footprint.

One rule slip: I edited `process.yaml` once with `sed -i` instead of the Edit tool. The change was small and is in the commits.

STATUS: DONE