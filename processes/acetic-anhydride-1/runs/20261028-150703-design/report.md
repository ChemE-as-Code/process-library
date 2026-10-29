I built the concept case for acetic anhydride by the ketene route: design basis, a mass-balanced BFD/PFD and a preliminary gate-to-gate LCI with every background left as a gap. It's in 4 commits on `case/acetic-anhydride-1` and the tree is clean. Nothing is pushed or merged and no stage is signed off. The branch still needs review and a merge by a human.

**Results**
- **Validation:** `cheme validate` gives 0 errors and 0 warnings. One info is a citation of D-023 in the template's `checks/checks.yaml`, which isn't mine.
- **Mass balance:** all 4 blocks and 16 steps close. The whole plant is 14 892 kg/h in and 14 892 kg/h out. Every element closes within 0.03 %; for carbon, 275.2 kmol/h goes in and comes out.
- **Energy balance:** core can't evaluate it. No property package covers acetic acid, ketene, anhydride and water (core #315). Energy closure exists only in my independent script.
- **Reactors:** cheme calculates the cracking coil, absorber and furnace firebox outlets itself. They agree with the script; for example, the flue gas is 0.105929 CO₂ by mole in both.
- **Concept gate:** 6 checks pass. The 1 failure is the plot plan, which was out of scope.
- **Maturity:** `cheme maturity` reports level "none". That's honest: the separators and absorber are assumed values, not sourced ones. `process.yaml` claims "concept", the lowest level allowed, as methanol-1 does.
- **LCI per kg of anhydride:**

| Exchange | Amount |
|---|---|
| Acetic acid | 1.2458 kg |
| Triethyl phosphate (catalyst) | 0.00156 kg |
| Ammonia | 0.00029 kg |
| Natural gas | 0.0401 kg |
| Air | 1.095 kg |
| Electricity | 0.0104 kWh |
| LP steam | 0.274 kWh |
| MP steam | 0.329 kWh |
| Cooling water | 1.093 kWh |
| Brine | 0.049 kWh |
| Residue | 0.0083 kg |
| Wastewater | 0.191 kg |
| Direct fossil CO₂ | 0.195 kg |

  - The inventory closes: 2.38274 kg in and out.
  - All 11 backgrounds are declared missing, each with a description of the activity it should link to.
  - The library's strict LCI build shows no errors for this case and 10 gaps. It still exits non-zero here because of environment warnings that hit every process.
  - Two changes were needed to get there: steam has no inventory key, and the zero CO, ethylene and ketene emissions are elementary flows rather than free.
  - The generated total is only the direct CO₂, so `process.yaml` sets the LCA source to none to keep it from being shown as a footprint.

**Files:** `process.yaml`, `process/design-basis.yaml`, `materials.yaml`, `reactions.yaml`, `flowsheet.yaml`, the generated BFD and PFD, `scripts/ac2o_balance.py`, the equipment list (11 items), the line list (23 lines), `lca/lca.yaml`, `lca/mappings.yaml` (no overrides, with candidates listed) plus the generated inventory files, `DESIGN.md` (decisions D-001 to D-014 and a source register) and `PROGRESS.md`.

**Sources**
- **US 4,455,439, Example:** 700 °C, 358 mbar, 84 % conversion, 92 % ketene selectivity, 38 wt % dilute acid, condensing to −5 °C on −10 °C brine.
- **US 8,653,303 B2:** catalyst at 0.1–0.5 wt %, absorber at 35–55 °C, crude anhydride at least 85 wt %, about 100:1 liquid circulation, vent gas burned as fuel.
- **Padmanabhan et al. (1968), I&EC Process Design and Development 7(4) 511–516:** abstract only.
- **Ullmann:** a lead only; I didn't read it.

**Key assumed values**
- **Capacity:** 50 kt/a at 8000 h/a, 99.5 wt % product.
- **Cracking losses:** split equally between acid and ketene decomposition.
- **Absorption:** 99 % of the ketene absorbed, 99 % of that forms anhydride.
- **Distillation:** crude 88 wt % anhydride, reflux ratios 3 and 1, residue 50 wt % anhydride.
- **Acid recovery:** 99 % recovery, 3.0 MJ of steam per kg of water. This is the largest unsourced energy number.
- **Furnace:** 15 % excess air, stack at 443 K, natural gas taken as methane.

**Open inputs and gated steps**
- I-01: product specification and capacity.
- I-02: design of the dilute-acid recovery.
- I-03: acid vapour in the absorber vent.
- I-04: heat of absorption. Formation enthalpies give −92 kJ/mol; the patent states −63.
- I-05: furnace NOx/CO factors and efficiency. The calculated efficiency is 0.915, which is high for a fired heater.
- I-06: fugitive emissions, which need P&IDs.
- I-07: there is no reaction-evidence file yet.
- Energy closure, property fill and simulation are gated on core #315.
- **Core bug:** `cheme validate` 0.8.0 drops the reactions of every reactor step after the first one that uses a selectivity spec. I worked around it with per-reaction conversions on the absorber. It should be reported to core.

**Missing registry entries** (for the consolidated PR)
- `chemicals.yaml`: acetic-acid, acetic-anhydride, ammonia, triethyl-phosphate, carbon-monoxide, ethylene, ketene.
- `lci/mappings.yaml`: acetic acid, triethyl phosphate, −10 °C refrigeration, hazardous liquid waste incineration.
- An `oxygenates` benchmark entry.

**Recommended next stage:** write the reaction-evidence file, source the dilute-acid recovery and absorber data, then link the backgrounds. After that, a predictive simulation once core #315 covers these mixtures.

Merge pending (needs human review).

STATUS: DONE