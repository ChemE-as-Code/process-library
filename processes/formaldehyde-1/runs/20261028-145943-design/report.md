I finished design basis, balanced BFD/PFD and preliminary gate-to-gate LCI for formaldehyde-1 (Formox type, iron molybdate catalyst), committed in 4 commits on `case/formaldehyde-1`; the tree is clean. `cheme validate` reports 0 errors. The energy balance is not checked by cheme: core can't evaluate it (gated by core #315). No stage was signed off and nothing was pushed.

**Design:** 20 t/h of 50 wt% formalin (10 t/h formaldehyde, 80 000 t/a at 8000 h/a). Air and recycled absorber off-gas go through one blower. Liquid methanol is vaporised against the hot reaction gas. The reactor shell holds boiling hot oil that raises steam. The off-gas is absorbed in water, 71.2 % of it is recycled, and the rest goes to a catalytic oxidiser (ECS) that also raises steam. Methanol is a boundary feed; `processes/methanol-1` makes it but has no LCI dataset yet.

**Files produced**
- `process.yaml`: status internal, maturity concept, review status unreviewed, references.
- `process/`: `design-basis.yaml`, `materials.yaml`, `reactions.yaml`, `catalysts.yaml`, `flowsheet.yaml`, and the generated `BFD.xml` / `PFD.xml` (4 blocks, 9 steps, 20 streams).
- `scripts/formox_balance.py`: my own balance script. It is the source of the absorber outlets, the recycle split and all duties.
- `equipment/equipment-list.yaml` (10 items), `piping/line-list.yaml` (14 lines).
- `lca/`: `lca.yaml`, `mappings.yaml`, and the written `inventory.csv`, `dataset.yaml`, `gaps.csv`, `manifest.json`, results and uncertainty files.
- `DESIGN.md` (source register, decisions D-001 to D-011, LCI table, open items) and `PROGRESS.md`.

**Balances and checks**
- **Mass and elements:** all 4 blocks and 9 steps close. cheme solves the reactor and ECS outlets and their element balances. cheme's reactor duties match my script: reactor 10,143.8 kW, ECS 1,081.8 kW.
- **Energy:** not checked by cheme. No property package covers the oxygen/water/organics gas or aqueous formaldehyde. The duties rest on ideal-gas enthalpies plus an assumed heat of solution.
- **Cross-checks against the EU BREF (2017), per t of 100 % formaldehyde:**

| Quantity | This design | BREF |
|---|---|---|
| Methanol | 1147 kg | 1135–1151 kg |
| Electricity | 169 kWh | 80–190 kWh |
| Vent gas | 2414 Nm³ | 2300–2400 Nm³ |
| Steam export | about 1.7 t | about 2.0 t |

- **Stack emissions after the ECS:** formaldehyde 1.5 mg/Nm³ and total organic carbon about 13 mg C/Nm³, both inside the BREF's best-available-technique emission levels.
- **One warning:** the reactor feed enters at 399 K, below the catalyst window. It is heated to reaction temperature on the hot oil in the inert section at the tube inlet; I documented this rather than silencing it.
- **Gates:** every process gate at concept and basic stage passes. The failures are out of scope: P&IDs, layout, datasheets and a design review.
- **Calculation maturity: none**, the same as methanol-1, because the feeds are assumed and the absorber values are specified rather than modelled.

**LCI per kg formalin 50 wt%**
- **In:** methanol 0.5737 kg, process water 0.1856 kg, electricity 0.0845 kWh, air 1.750 kg (counted as free).
- **Out:**
  - exported steam 0.561 kWh, a co-product;
  - heat to cooling water 0.655 kWh;
  - fossil CO₂ 0.0512 kg at the stack, plus small amounts of CO, dimethyl ether, methanol, formaldehyde and an estimated NOx 1.2e-5 kg.
- **Consumables:** catalysts, oil and filters, at the BREF waste rates.
- **Balance:** mass closes against the flowsheet (2.50883 kg in, 2.50884 kg out). Carbon closes: 4,301 kg C/h in = 4,021 in the product + 280 at the stack.
- **Coverage:** partial screening with 14 gaps; every background is left unmapped, each with a note on the activity it should link to. The 0.051 kg CO₂-eq that cheme prints is only the direct stack CO₂; I don't claim it as a footprint.
- **Library build:** `build_lci.py --strict` lists 8 gaps for this process and no errors. It still exits 1 on a cut-off warning that every process gets in this environment, not one specific to formaldehyde-1.
- **One mapping override** in `lca/mappings.yaml`: the exported steam is counted in kWh using the library's existing steam entry, as the other cases do. Without it the build stopped on a unit mismatch.

**Sources:** EU JRC BREF on large volume organic chemicals (2017), chapter 6 and BAT 45; US EPA report EPA-450/4-91-012 (1991); NIST WebBook; the `chemicals` package for thermodynamic data. Ullmann's formaldehyde chapter is listed as a lead only; I didn't read it.

**Key assumed values:** capacity; 50 wt% product; 93 % yield (chosen within the BREF's 91–94 %); 99.3 % methanol conversion; dimethyl ether 1 kmol/h; 8.5 mol% methanol at the reactor inlet; 6 mol% oxygen in the off-gas; 1 mol% water in the air; the temperatures and pressures; blower efficiency 0.75; 80 kW for pumps; ECS conversions; steam at 1500 kPa(a); NOx at 10 mg/Nm³. The heat of solution of formaldehyde (−62 kJ/mol) is the largest term in the cooling duty. A web search found the same value attributed to Ullmann, but I couldn't check it there, so it stays assumed.

**Missing from the shared files (for the consolidated PR):**
- `chemicals/chemicals.yaml` needs formaldehyde (with a 50 wt% formalin grade), methanol, carbon monoxide and dimethyl ether.
- `lci/mappings.yaml` needs:
  - entries for methanol (linking methanol-1), formaldehyde/formalin, the two catalysts and heat-transfer oil;
  - emission identities for methanol, formaldehyde and dimethyl ether to air.

**Open inputs and gated steps**
- Energy closure in core, gated by core #315.
- A primary source for the heat of solution.
- A plant-specific yield and by-product split. The BREF's own text gives 88–91 %, which would raise methanol use by 2–6 %.
- How to allocate or credit the exported steam, which is the LCA practitioner's decision.
- Reactor kinetics and sizing, likely two reactors at this capacity.
- Fugitive emissions, which need P&IDs.

Two info findings cite decisions D-012 and D-023 that don't exist; they come from the template's `checks.yaml` and `cause-effect.yaml`, which I didn't touch.

**Recommended next stage:** have someone review this branch with `cheme diff main --list`. Then land the registry and mapping PR, source the heat of solution and the yield split, and once core #315 is resolved simulate the gas loop and absorber before moving to basic engineering. A merge is pending: the branch needs that review and must be merged by someone other than its author.

STATUS: DONE