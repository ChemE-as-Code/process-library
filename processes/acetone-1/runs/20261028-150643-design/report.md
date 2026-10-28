I've finished the run: design basis, a balanced BFD/PFD and a preliminary gate-to-gate LCI per kg of acetone, all committed in 4 commits on `case/acetone-1` with a clean worktree and nothing pushed. Two caveats up front: `cheme maturity` reaches no level, and the library's strict LCI build (`build_lci.py --strict`) exits 1 for this process because of a bug in that script (details below).

**Files produced** (all in `processes/acetone-1/`)
- `process/design-basis.yaml`, `materials.yaml` (16 components), `reactions.yaml` (8 reactions), `flowsheet.yaml` (5 blocks, 15 steps, 30 material and 18 energy streams), with `BFD.xml` and `PFD.xml` generated from them.
- `scripts/balance.py`: the script that produced the assumed stream values. It is a record of where they came from and is not rerun over the flowsheet.
- `equipment/equipment-list.yaml` with 14 tags, one per PFD step. There is no line list because there are no P&IDs.
- `process.yaml` (status internal, maturity concept, unreviewed, with references), `DESIGN.md` (route and boundary memo, source register, decisions D-001 to D-015, open items I-01 to I-10), `PROGRESS.md`.
- `lca/lca.yaml` and `lca/mappings.yaml`, plus the generated `inventory.csv`, `gaps.csv`, `results.*`, `dataset.yaml` and `manifest.json`.

**Balances and checks**
- `cheme validate`: 0 errors, 0 warnings. All 5 blocks and 15 steps close within 1 kg/h, element balances included.
- cheme itself calculates the outlets of the oxidiser, cleavage reactor, neutraliser and hydrogenation reactor from the reactions. Every separator outlet is a specified (assumed) value.
- Per tonne of phenol:
  - Fresh cumene is 1.330 t; the EU reference document (the LVOC BREF, 2017, chapter 8) gives 1.31–1.38 t.
  - Acetone is 0.629 t, against 0.616 t in Speight. The model has no acetone condensation losses, which explains the difference.
  - Tar is 47 kg; the BREF range is 20–200 kg.
  - Spent air is 1,240 Nm³; the BREF range is 1,000–1,500 Nm³.
- Energy: cooling water takes 61.9 MW against 63.6 MW going in (steam, power, reaction heats), a 2.7 % gap in my own check. cheme cannot run an enthalpy balance yet, because no property package covers this mixture of polar components (core#315).
- `cheme check --stage concept`: 6 gates ok. Only the layout plot plan fails, and layout is out of scope.
- `cheme maturity`: no level reached, because feeds, selectivities and separator splits are assumed rather than sourced. I kept the claim at "concept" (the lowest option) and say so in `process.yaml`.

**LCI** (per kg acetone, mass allocation with phenol; acetone's share is 0.386)
- Inputs total 2.0264 kg: cumene 0.8163, air 1.1785, hydrogen 0.00059, sulfuric acid 0.0025, caustic 0.0040, water 0.0246.
- Outputs total 2.0264 kg: acetone 1, tar 0.0286, effluent 0.0394, vent 0.9584. This closes against the flowsheet.
- Energy: power 0.117 kWh, LP steam 0.234 kWh, MP steam 0.620 kWh, cooling water 1.520 kWh.
- `--coverage` reports mass, element and carbon balances closed and 13 gaps, so the result is classed "partial screening" and no impact is claimed. Each gap carries a description of the background activity it should later connect to.
- `lca/mappings.yaml` has only two kinds of override: the steam is counted in kWh (otherwise the build reports a unit error), and the hydrogen is kept from being linked automatically to the chlor-alkali-1 hydrogen.
- **Strict LCI build:** 5 gaps for acetone-1 as intended, but it exits 1 on two warnings:
  - The script compares the allocation method as "None" because cheme leaves the default `method: mass` out of the generated `dataset.yaml`. This is a library bug (around line 863 of the script; recorded as I-10). acetone-1 is the first process using mass allocation, so it is the first to hit it.
  - The other warning appears for every process in an environment without core installed.
  - The strict catalog build passes, apart from the usual "no preview rendered" warnings.

**Sources**
- EU LVOC BREF (JRC109279), chapter 8, pp. 395–411, the full chapter read. It gave the conditions, CHP concentrations, cumene consumption, steam and power (Table 8.5), vents, effluent and tar.
- US 8,975,444: typical oxidation selectivity of 92–94 % and 22–32 % hydroperoxide at the oxidiser outlet.
- US 5,245,090: cleavage and acid loading (abstract only).
- Speight (2002), via the skill's table.
- Formation enthalpies from `cheme chemistry thermo`.

**Key assumed values (ASSUMED)**
- 200 kt/a phenol at 8,000 h/a.
- Oxidation selectivity per kmol cumene converted: 0.94 hydroperoxide (top of the sourced range), 0.05 dimethylbenzyl alcohol, 0.01 acetophenone; 21.7 % conversion per pass.
- In cleavage, 75 % of the dimethylbenzyl alcohol goes to alpha-methylstyrene (AMS) and 25 % to heavy ends.
- Spent air at 5 mol % O₂.
- 0.2 wt% acid, 1,000 kg/h wash water.
- Product purities and loss fractions.
- Utilities are the BREF's plant data applied to this design, not calculated. How they are split between units is assumed.

**Missing registry entries** (for the consolidated library PR)
- `chemicals.yaml`: cumene, acetone, phenol, sulfuric-acid, sodium-hydroxide, alpha-methylstyrene, acetophenone, cumene-hydroperoxide, sodium-sulfate, methanol, and a tar/heavy-residue entry.
- LCI vocabulary: `cumene`, `sodium-hydroxide-50`, heavy-residue thermal treatment.

**Open inputs and gated steps**
- An energy balance and simulation of the concentration step and the columns need the polar property package (core#315).
- Measured selectivity data for the oxidation and cleavage.
- Not yet modelled: vacuum and fractionation vents, a thermal oxidiser, methane in the off-gas, fugitive emissions, catalyst and activated carbon consumption, and heat integration.
- Choosing the backgrounds and confirming the allocation with an LCA practitioner.

**Recommended next stage:** a review of this branch, then property-method qualification for the polar system once core#315 lands. After that, simulate the concentration step and the four columns, replace the literature utilities with calculated duties, and map the LCI backgrounds.

Merge pending: the branch needs a review and a human merge; no stage is signed off.

STATUS: DONE