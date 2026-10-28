I've built the acetaldehyde-1 concept case (one-stage Wacker, 100 kt/a, 99.9 wt% product) as far as the brief asked: design basis, a balanced BFD/PFD and a preliminary gate-to-gate LCI. Mass, component and element balances close in cheme for every block and step; energy closure can't be checked in core. Everything is committed in three commits on `case/acetaldehyde-1`; nothing was pushed or merged.

**Files produced**
- `process.yaml`: internal publication status, maturity claimed as concept, unreviewed.
- `process/`: `design-basis.yaml`, `materials.yaml` (13 components), `reactions.yaml` (R1–R7), `flowsheet.yaml` (3 blocks, 16 steps, 33 material and 11 energy streams), and the generated `BFD.xml` and `PFD.xml`.
- `scripts/acet_balance.py`: my own balance script for the cycle-gas loop, separator outlets and duties. Its values go into the flowsheet marked ASSUMED.
- `lca/`: `lca.yaml`, `mappings.yaml` and the written inventory and coverage outputs.
- `DESIGN.md` (source register, decisions D-001 to D-012, open items), `PROGRESS.md`, equipment list (17 items) and line list (26 lines).

**Check results**
- **Balances:** cheme's reactor extents match the script (main reaction 287.7 kmol/h). Overall in = out = 122.4 t/h.
- **Validate:** 0 errors, 0 warnings. One info finding comes from the template's `checks.yaml`, which cites a decision D-023 that doesn't exist; I left it alone.
- **`cheme check`:** all concept gates pass except the plot plan (layout is out of scope). Basic and detail gates fail where they need P&IDs, layout, datasheets or a review.
- **`cheme maturity`:** calculation maturity is "none". The feed flows come from my script rather than a cited source, and the reactor and separators are specified values rather than models. So the "concept" claim is flagged as exceeding the evidence, as it is for the hydrogen-peroxide sibling case.
- **Library build:** the catalog build passes. The strict LCI build lists our 6 Atlas gaps, exits with code 1 and prints no other errors, the same pattern as hydrogen-peroxide-1 and phosgene-1.

**LCI per kg acetaldehyde**

| Exchange | Amount |
|---|---|
| Ethylene | 0.6765 kg |
| Oxygen | 0.4096 kg |
| Hydrochloric acid, 30 % | 0.0542 kg |
| Demineralised water | 1.269 kg |
| Process water | 5.962 kg |
| LP steam (live) | 1.308 kg |
| MP steam (live) | 0.115 kg |
| Electricity | 0.0428 kWh |
| Heat to cooling water | 2.59 kWh |
| Purge gas | 0.0198 kg |
| Light ends | 0.0164 kg |
| Heavy side draw | 0.0713 kg |
| Waste water | 8.687 kg |

- Inputs and outputs both total 9.7941 kg/kg; cheme reports the mass, element and carbon balances closed.
- All 13 backgrounds are left unmapped, each with a description of the activity it should link to.
- I kept oxygen and both steams out of the Atlas build until a supplier is chosen. Water, electricity, waste water and cooling water may still be linked by the shared library mappings.

**Sources used**
- US 4,237,073 (Hoechst, 1980): its 13 t/h example gives the water, steam and waste-water figures I scaled. Against it, the design gives ethylene 677 vs 692 kg/t, oxygen 410 vs 408 kg/t, and waste water 8.69 vs 8.65 m³/t.
- Wikipedia "Wacker process" (citing Ullmann's): reactor conditions and the ethylene fate per 100 mol fed.
- US 7,339,084 and US 5,557,014: reaction temperature range, by-products and corrosion.
- NIST WebBook: gas solubilities in water.
- `cheme chemistry thermo`: heats of formation for the heats of reaction.
- Ullmann's itself was not read.

**Key ASSUMED values**
- Capacity 100 kt/a over 8000 h/a.
- Ethylene conversion per pass 35 %, and 8 mol% oxygen in the cycle gas. Neither has a source.
- How the minor by-products are split.
- Scrubber and condenser splits, and the side-draw composition.
- Feed purities, steam levels, compressor and pump efficiencies.

**Missing registry entries** (for the consolidated `chemicals.yaml` PR): acetaldehyde, ethylene, hydrochloric acid / hydrogen chloride, acetic acid, crotonaldehyde, chloroacetaldehyde, chloroethane, chloromethane, ethane.

**Open inputs and gated steps**
- No property package covers aqueous acetaldehyde, so energy closure and predictive scrubber/column models are blocked (pre-release issue 315); the catalyst solution is an electrolyte (issue 364). I couldn't open either issue from this session, so their current state is unchecked.
- Ullmann's sections 4.3.1 and 5 still need auditing.
- Per-pass conversion and the cycle-gas composition: the model gives about 40 % ethylene and 35 % CO2 in the cycle gas, a result of the assumptions rather than plant data.
- The waste water's acid load is about 2.4 times lower than the patent's, so its COD is understated.
- Palladium and copper catalyst losses are unquantified: an open item, not set to zero.

**Recommended next stage:** an independent review of the PFD and LCI (as the sibling cases had), the Ullmann's audit, and a sourced per-pass conversion. After that, a DWSIM simulation once core supports the property package, then link the backgrounds.

The branch still needs review, and a merge by someone other than me is pending.

STATUS: DONE