---
topic: design
reviewed_commit: 4a44d70f7f5d01092dde53ef97afbc2925357910
scope: [DESIGN.md, process/design-basis.yaml, process/materials.yaml, process/reactions.yaml, process/flowsheet.yaml, process/BFD.xml, process/PFD.xml, equipment/equipment-list.yaml, lca/, process.yaml, scripts/thf_balance.py]
reviewer: review-agent
reviewer_kind: agent
branch: case/thf-1
merge: pending
---

# THF-1 concept design and preliminary LCI: independent review

Branch `case/thf-1` (issue #126), 5 commits on `origin/main` (b0b61ef..4a44d70). I am an
independent agent and did not write this design. I reviewed the design files and the LCI; I did
not change any of them. The design is at concept stage, so P&IDs, layout, datasheets, HAZOP and
TEA are out of scope (run task.md).

## What was re-run (not taken from the run report)

| command | result |
|---|---|
| `git diff --name-only origin/main..HEAD` | every changed path is under `processes/thf-1/` |
| `cheme validate` | 16 files, 0 errors, 0 warnings; infos only (see #8) |
| `cheme check` | every concept gate passes except `layout-plot-plan` (out of scope); the basic-stage gates fail on missing P&IDs, layout and this review, as expected |
| `cheme maturity` | calculation maturity none; `cheme.maturity-claim-exceeds` warning on `maturity: concept` (see #4) |
| `cheme process streams` | every block (RXN, SEP) and step closes; reactor extents CYCLO 86.64, ETHER 0.218 kmol/h |
| `cheme process propagate --check` | exit 0, nothing stale |
| `cheme assess lca --coverage` | 8 gaps, each `missing:` with a description; mass, element and carbon-origin balances closed; DQR 2.33; no impact total |
| `cheme impact` | nothing to review |

## Hand checks of the numbers

- **Stoichiometry and yield.** BDO 7921.18 kg/h = 87.90 kmol/h. THF 6250 x 0.9995 / 72.11 =
  86.63 kmol/h, so the yield is 0.9856 mol/mol, as stated. Water of reaction is (86.64 + 0.218)
  x 18.015 = 1564.7 kg/h. The water leaving is 1555.6 (process water) + 3.1 (product) + 5.9
  (bleed) = 1564.6 kg/h. The bleed carries 74.2 kg/h BDO (0.823 kmol/h), which gives a
  conversion of 0.9906; its 35.3 kg/h DHBE is 0.2177 kmol/h, equal to the ETHER extent; its acid
  is 2.354 kg/h, equal to the make-up. Specific BDO use is 1.2674 kg/kg against a stoichiometric
  1.2492 at 99.95 wt%. All consistent.
- **Condensate.** 80.0 wt% THF is the stoichiometric THF/water ratio (72/90). The patent's
  examples report 78-80 wt%, which agrees.
- **Pressure-swing balance.** THF into C-202 is 14474 x 0.9403 = 13609 kg/h. THF out is
  6247 + 8224 x 0.8953 = 13610 kg/h. Closed.
- **Azeotropes.** NRTL gives 95.3 wt% THF at 1 atm and 88.2 wt% at 8 bar. Both are in the range
  usually quoted for THF/water (about 94-96 wt% at 1 atm, about 88 wt% near 8 bar).
- **Duties, order of magnitude.**
  - R-101: vaporising 86.6 kmol/h THF and 86.5 kmol/h water at reflux 0.5 is about 2.6 MW.
    Heating the feed from 303 to 418 K adds about 0.65 MW, for about 3.2 MW in total. The design
    gives 3.05 MW.
  - E-205: 18.8 t/h of vapour at about 530 kJ/kg is about 2.8 MW. The design gives 2.82 MW.
  - P-201: 17.2 m3/h at 720 kPa and an efficiency of 0.6 is 5.7 kW. The design gives 5.73 kW.
  - Temperature levels: E-201 condenses at 410 K against a 375 K reboiler; MP steam at 453 K
    against 421 K (C-202) and 418 K (R-101); LP steam at 421 K against 375 K. All feasible.
- **Utilities per kg THF.** Steam 3.6 MJ/kg (MP 3.07, LP 0.53) and cooling 3.5 MJ/kg are
  plausible for acid-catalysed reactive distillation followed by heat-integrated pressure-swing
  distillation. The reactor section takes about half of the steam.
- **LCI per functional unit.**
  - In: 1.26739 + 0.00038 = 1.26777 kg. Out: 1 + 0.24893 + 0.01883 = 1.26776 kg. Closed.
  - The amounts equal the flowsheet streams divided by 6250 kg/h.
  - No exchange is zero-filled, and no licensed background value is used.
  - `lca/mappings.yaml` is in the folder and has no overrides, on purpose (D-011). The shared
    `lci/mappings.yaml` is untouched.
- **Sources.** I spot-checked US 9284289 B2 on Google Patents. It agrees with D-004 and D-005 on:
  - liquid temperature 80-250 C (preferred 120-180 C);
  - pressure 10-1000 kPa;
  - acid 0.01-20 wt% (more preferred 0.2-5 wt%), and 0.2-0.4 wt% p-TSA in the examples;
  - water 1.4-10 wt% (preferred 2-8 wt%);
  - condensate 78-80 wt% THF, and BDO at or below 10 ppm;
  - essentially no THF formed at 110 C.
- **Copied content.** No third-party table, figure or passage was copied. DESIGN.md states the
  facts in its own words, with locators. The NRTL parameters come from MIT-licensed software and
  are cited.
- **Honesty.**
  - process.yaml declares `validation: unreviewed`, `lca.source: none` and `publication: internal`.
  - Its notes say plainly that no calculation maturity level is reached and why.
  - The values in the flowsheet are labelled `assumed`, with the script as their source. They are
    not presented as given data.

The route and the boundary match the issue's scope: purchased BDO as a boundary feed,
acid-catalysed cyclodehydration, and pressure-swing distillation of the azeotrope.

## Findings
| id | sheet | item | finding | severity | status | proposed action |
|---|---|---|---|---|---|---|
| 2026-10-28-pfd-lci-review#1 | DESIGN.md:101-125, 127 | C-201 | R-01. The NRTL parameters used predict two liquid phases for THF/water (x_THF about 0.15 at 342-360 K). The LP column's stripping section runs through that composition and temperature range. Yet the minimum reflux, the LP reboiler duty and the condenser duties come from a binary McCabe-Thiele calculation that assumes a single liquid phase. The PSD steam (about 0.5 MW of LP steam plus E-201) and its LCI exchanges therefore rest on an assumption that the design's own model contradicts. This is disclosed as I-04, but neither D-007 nor process.yaml `description` mentions it. | medium | open | Run a stage-by-stage VLLE check of C-201 at 110 kPa(a), or qualify NRTL against measured LLE/VLE first (I-04). Until then, add one sentence to D-007 and to process.yaml `description` saying that the LP column duties assume a homogeneous liquid. |
| 2026-10-28-pfd-lci-review#2 | DESIGN.md:127; scripts/thf_balance.py:36-37 | C-201, C-202 | R-02. Both columns sit at the arbitrary 0.3 reflux floor (1.3 x Rmin would give 0.18 and 0.22). So the separation steam, about 60 % of the steam in the LCI, is set by an ASSUMED floor, not by a calculation. Stages are not computed (I-11), and "accuracy not stated" leaves a reader with no range for the 3.6 MJ/kg. | low | open | Give a stated uncertainty range for the steam per kg THF in DESIGN.md (D-006/D-007), or replace the floor with a rigorous stage-by-stage reflux once stages are set. |
| 2026-10-28-pfd-lci-review#3 | lca/lca.yaml:35, 52 | feed:POWER | R-03. The cut-off power (reflux pumps, bottoms pump and agitator, about 25 kW, ASSUMED) is four times the electricity actually inventoried (6.1 kW, 0.98 Wh/kg). The cut-off passes the 1 % rule against total energy input. But the electricity exchange is understated by about 80 %, and electricity carries a much higher burden per kWh than delivered steam heat. | low | open | Add the 25 kW ASSUMED estimate to feed:POWER, about 4 Wh/kg THF in total (as a POWER port or a note in the flowsheet), instead of cutting it off. |
| 2026-10-28-pfd-lci-review#4 | process.yaml:38 | maturity | R-04. `cheme maturity` warns `cheme.maturity-claim-exceeds`: `concept` is claimed, but the evidence supports none. `concept` is the lowest value the schema allows, and the comment and `validation.notes` explain the gap honestly. So nothing misleads, but the warning stays. | low | open | Keep the notes. Close the gap by giving the feed and capacity a source (an owner-given basis) and the reactor selectivity a sourced value (I-02), or accept the warning in the review of the next stage. |
| 2026-10-28-pfd-lci-review#5 | equipment/equipment-list.yaml:28, 40 | E-202, E-206 | R-05. The steam-side design pressures break the project's own D-010 rule (operating + 10 %, at least + 2 bar). E-206 condenses MP steam at 1000 kPa(a) (9 barg) and is given 9 barg; E-202 condenses LP steam at 3.5 barg and is given 4 barg. R-101 is heated by MP steam, but its heating-side design pressure is not stated. | low | open | Give each exchanger and the R-101 jacket/coil a design pressure per side (steam side at least 11 barg for MP and 5.5 barg for LP, per D-010). |
| 2026-10-28-pfd-lci-review#6 | process/flowsheet.yaml:268 | S7 | R-06. The bleed leaves the reactor liquid at 418 K and 130 kPa(a) with 5 wt% water but no THF. At these conditions the liquid holds some dissolved THF (likely a few kg/h). So the loss of THF to incineration is missing, and the yield is very slightly overstated (below 0.1 %). | low | open | Estimate the THF in the reactor liquid with the same NRTL basis and include it in S7, or state in D-005 that it is neglected. |
| 2026-10-28-pfd-lci-review#7 | DESIGN.md:54, 207 | US 9284289 B2 locators | R-07. My spot-check of the patent text found the BDO-below-10-ppm result in a 400 L run and 2,3-dihydrofuran values starting at 37 ppm. DESIGN.md cites "the 500 L example" and "17-327 ppm". The check covered the first 100 000 characters only, so either reading may be incomplete. | low | open | Re-read the examples and correct the locator and the range, or confirm them with the example numbers. |
| 2026-10-28-pfd-lci-review#8 | process.yaml:57 | chemistry | R-08. `chemistry.inputs` is empty, and the product THF is missing from `outputs`, because the registry has no 1,4-butanediol, tetrahydrofuran or p-toluenesulfonic acid entry. The catalog will list the process without its main feed and product. This is disclosed in `validation.notes`, and DESIGN.md lists the missing registry entries. | low | open | Add the three registry entries in the consolidated PR, then fill `chemistry.inputs`/`outputs`. |
| 2026-10-28-pfd-lci-review#9 | checks/checks.yaml:76; control/cause-effect.yaml:13 | template comments | R-09. Commented template examples cite D-023 and D-012, so `cheme validate` reports `cheme.decision-unknown` (info). This is harmless, but it is noise in every validation run. | low | open | Reword or drop the example decision ids in the template comments. |

No critical or high findings: the balances close, the LCI matches the flowsheet per functional
unit, every gap is reported with a description, and no assumed value is presented as data.

## Previous findings
None: this is the first review of thf-1 (`reviews/` held only README.md).
