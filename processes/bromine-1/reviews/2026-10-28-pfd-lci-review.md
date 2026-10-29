---
topic: design
reviewed_commit: 84c088c4dedd94889bfe5da77b2b54ec3b43d07b
scope: [DESIGN.md, process/design-basis.yaml, process/materials.yaml, process/reactions.yaml, process/flowsheet.yaml, process/simulation.yaml, process/BFD.xml, process/PFD.xml, scripts/balance.py, equipment/equipment-list.yaml, lca/lca.yaml, lca/mappings.yaml, lca/inventory.csv, lca/gaps.csv, lca/dataset.yaml, process.yaml]
reviewer: review-agent
reviewer_kind: agent
branch: case/bromine-1
merge: pending
---
# Review: design (concept PFD and preliminary LCI of bromine-1, issue #136)

Independent review of the bromine-1 case study on `case/bromine-1` (6 commits on top of
`cc5624f`, the merge base with `origin/main`). Every command below was re-run by the reviewer at
`84c088c`; the design agent's report was not taken on trust. Finding labels R-01 ... are given
with each id.

## Findings
| id | sheet | item | finding | severity | status | proposed action |
|---|---|---|---|---|---|---|
| 2026-10-28-pfd-lci-review#1 | - | process/flowsheet.yaml:224-226 (S15, S17), T107 | (R-01) The tail brine drops from 382.59 K (S15) to 375 K (S17) across T-107 with no duty, no vent and no source for the 375 K (`source: D-009`, and D-009 does not give it). Neutralising HCl with lime releases heat, so on its own the brine should warm slightly. If the 7.6 K drop is meant as an atmospheric flash (the brine is at about its 105 kPa boiling point), it means roughly 9 t/h of water vapour (933 t/h x 2.9 kJ/kg K x 7.6 K / about 2 250 kJ/kg), plus any H2S or halogen traces, leaves T-107. That vapour is missing from the mass balance and from the LCI (emissions and tail-brine mass). Energy closure is not evaluated in core, so no check catches it. | medium | open | Either set S17 to the energy-consistent temperature (S15 plus the neutralisation heat, minus a stated loss) in scripts/balance.py, or model the flash as a vent stream with its fate. Record the choice in D-009. |
| 2026-10-28-pfd-lci-review#2 | - | process/flowsheet.yaml:226,233 (S17, Q6); DESIGN.md D-011 (l.191) | (R-02) S17 leaves at 300 kPa(a) from T-107, an agitated tank with a design pressure of 0.5 barg, fed at 130 kPa(a). Lifting 933 t/h by about 170-200 kPa needs a transfer pump of about 50-60 kW (0.216 m3/s x 170-200 kPa / 0.7). It is neither in the equipment list nor in the power: Q6 is a 15 kW lump for "bromine, acid and lime pumps, agitator". D-001 puts only the injection pumps outside the boundary. The plant's electricity (0.0322 kWh/kg) is therefore about 40 % low. | medium | open | Add the tail-brine transfer pump (equipment list, PFD step, power) and recompute Q6/LCI power, or set S17 to the T-107 pressure and say in D-001/D-011 that the transfer pump belongs to the reinjection system outside the boundary. |
| 2026-10-28-pfd-lci-review#3 | - | process.yaml:36-39 (maturity, validation.notes) | (R-03) `cheme maturity` reports `warning cheme.maturity-claim-exceeds`: calculation maturity none, design maturity claimed concept. `concept` is the lowest value of the manifest enum, so the claim itself cannot be lowered. The honest statement is only in a YAML comment (line 33-35), which the Atlas does not publish. The published `validation.notes` never says that the evidence supports no design maturity, and DESIGN.md section 5 claims that it does. | medium | open | Add one sentence to `validation.notes`: "cheme maturity: calculation maturity none (every stream value assumed from scripts/balance.py, reactors and separators specified); the concept claim exceeds the evidence (cheme.maturity-claim-exceeds)". Raise the missing lower enum level with the library. |
| 2026-10-28-pfd-lci-review#4 | - | DESIGN.md:65 (SRC-7), :107 (Sander); process/reactions.yaml | (R-04) The heats of reaction that enter the tower energy balance (1.16 MW, about 8 % of the steam) rest on formation enthalpies the agent recalled rather than re-read, and their locator is "whole table" level (no table or page). The reviewer's own recollection of Wagman et al. 1982 agrees with every value (Cl-(aq) -167.16, Br-(aq) -121.55, Br2(aq) -2.59, Br2(g) 30.91, H2S(aq) -39.7 kJ/mol), and the arithmetic of BR_OX (-93.8) and H2S_OX (-294.6 kJ/mol) is correct. The provenance is still not to the standard the library asks for. SRC-8 ("values as commonly tabulated") has the same weakness. | low | open | Re-read the values (close O-5) and give a locator (table and species entry) for SRC-7 and SRC-8, or cite an open compilation (NIST WebBook / CODATA key values) with its page. |
| 2026-10-28-pfd-lci-review#5 | - | DESIGN.md:135-145 (D-004); process/flowsheet.yaml:210 (S1) | (R-05) Sodium by charge balance comes to about 87 g/kg (21.75 wt-% NaCl beside 8.31 wt-% CaCl2): about 5.4 mol NaCl and 1.1 mol CaCl2 per kg water. That is close to halite saturation in a Na-Ca-Cl brine, and the calcium that sets it is ASSUMED. Halite saturation is listed as unchecked (O-2), but the derived Na and how near the feed sits to saturation are not stated. The steam result also depends linearly on the ASSUMED cp 2.9 kJ/kg K. Both are disclosed, but a reader cannot see how close to the edge the basis is. | low | open | State the derived Na content in D-004 and add a note that the basis brine may be near halite saturation (to be checked with O-1/O-2). Give the steam sensitivity to cp (as already done for the feed temperature). |
| 2026-10-28-pfd-lci-review#6 | - | lca/lca.yaml:27 (feed:BRINE), :46-52 (emission_exclusions) | (R-06) The resource "bromine, in ground brine" is named only inside the `missing:` text of feed:BRINE, so the exported dataset carries no resource exchange for the bromine extracted (about 1.05 kg Br per kg product, 0.047 kg of which is reinjected). The six emission exclusions carry no amount (`cheme.lca-cutoff-unchecked`), so the 1 % cut-off rule cannot be checked. The process vents are filed under `equipment-leaks` for lack of a schema method (O-9, disclosed). | low | open | When the brine-extraction background is added, model the bromine resource as an elementary exchange (net of the reinjected bromide). Give each exclusion an order-of-magnitude amount or state why none can be given. Keep O-9 as the core item. |

No critical or high finding: the balances close, the LCI is consistent with the flowsheet, and
nothing in the record would mislead a reader about what the numbers are.

## Previous findings
| id | finding | severity | status | evidence |
|---|---|---|---|---|

None: this is the first review record of bromine-1 (`reviews/` held only README.md at
`84c088c`, so `grep '| open |' reviews/*.md` finds nothing).

## Drawing
No P&ID exists yet (`cheme validate` loaded no `pid/` sheet, so it printed no `drawing` line).
The BFD and PFD are generated by `cheme process build` and are current: gates
`process-balances` and `process-basic` are ok. The rendered `build/PFD.png` was read as a whole.
Topology matches flowsheet.yaml: the S7 bromine-water and S9 C-104 vapour recycles go to C101,
Q1-Q6 go to the utility terminals and S15 to T107. The figure has long recycle runs across the
sheet but is readable. Not read in tiles (generated sheet, no drawing findings to judge).

## Re-run results (reviewer, at 84c088c)
- `cheme validate`: 17 files, 0 errors, 0 warnings. It compared 2 sheets (BFD, PFD) and 12 lists
  and skipped the list-vs-P&ID cross-checks (no P&ID). The info `cheme.decision-unknown [D-023]`
  comes from a commented example in the scaffolded `checks/checks.yaml`, not from this case.
- `cheme check`: concept gates design-basis, concept-lists, process-concept, process-balances,
  process-links-concept and assumptions-marked are ok. `layout-plot-plan` fails (layout outside
  the issue's scope). The basic and detail gates for P&IDs, layout, datasheets and design-review
  fail as expected at concept.
- `cheme maturity`: calculation maturity none. The model basis is specified, unsourced
  conversions and stream values. Warning `cheme.maturity-claim-exceeds` (R-03).
- `cheme process streams`: every block (LIB, REC, PUR, TBT) and step balances. Extents: BR_OX
  23.4556, H2S_OX 6.69539, NEUT 6.6961 kmol/h.
- `cheme process propagate --check`: exit 0, nothing reported.
- `cheme assess lca --coverage`: partial screening carbon footprint with 10 gaps, each with a
  description. Mass, element and carbon-origin balances closed. Publishable.
- `cheme run scripts/balance.py` reproduces every stream value in flowsheet.yaml: Cl2 0.5705
  kg/kg, steam 5.815 kg/kg, overall 937 243 kg/h in = out.

## Checked and fine
- **Scope and boundary**: the route matches issue #136. It is chlorine oxidation of bromide brine
  in a steaming-out tower, followed by condensation, gravity separation, chlorine stripping,
  sulfuric-acid drying and lime neutralisation with reinjection. The boundary (D-001) is stated,
  as are what crosses it and the rejected alternatives (air blowing-out, vacuum variant, Dead Sea
  end brine).
- **Nothing outside `processes/bromine-1/` changed**: `git diff --name-only origin/main...HEAD`
  lists only this folder. The `thf-1` paths in a two-dot diff are main's later commits, not
  this branch's.
- **Hand checks of the balance**:
  - Bromide demand: 243.41 kg brine x 4 300 mg/kg x 0.955 = 1.000 kg Br2.
  - Chlorine: Cl2 stoichiometry is 0.4437 kg/kg. Plus 250 mg/kg H2S (0.1266 kg Cl2/kg) plus the
    product's Cl2 gives 0.5705 kg/kg.
  - Lime and HCl: 6.70 kmol/h x 74.09 = 496 kg/h lime, and HCl 488 kg/h.
  - Brine composition: the charge balance of D-004 reproduces NaBr 0.554, CaCl2 8.31, NaCl 21.75,
    H2O 69.37 wt-%.
  - C101 water balance: 655 533 in, 655 537 out (rounding).
  - Brine heat-up: 253.6 kg/s x 2.9 x 18.9 K = 13.9 MW.
  - Steam: about 2 272 kJ/kg delivered x 6.06 kg/s = 13.8 MW, which is the demand plus a 3 % loss.
  - Overhead water: 57.85 kPa partial pressure at aw 0.75 and T_top = 365.7 K gives about
    550 kg/h, consistent with S5.
  - E-102: about 620 kW (water about 390 kW plus bromine about 230 kW).
  - P-101: 0.211 m3/s x 350 kPa / 0.7 = 105.6 kW.
  - Drying acid: 7.84 kg/h 98 % to 9.6 kg/h 80 %, absorbing the 1.76 kg/h water removed.
  - Product: 400 ppm Cl2 + 30 ppm water = 99.957 wt-%.
- **Plausibility against the cited source**: the reviewer re-read US 4 719 096 itself. These
  figures match the patent text:
  - 3 000-5 000 ppm bromide (as NaBr); 200 000-250 000 ppm chloride; NH3 150-200; H2S 100-300 ppm;
  - 0.55-0.60 lb Cl2/lb Br2, against 0.42-0.44 stoichiometric;
  - 5.2-5.7 lb net steam/lb Br2;
  - tail brine 50-200 ppm bromide; recovery 95-96 %;
  - 14.7-15.0 psia and 228-230 degF;
  - excess chlorine about 40 % (Background) against about 25 % (Detailed Description), which the
    patent itself does not reconcile;
  - tail-brine neutralisation with lime.

  On those figures the model's chlorine (0.571), tail brine bromide (189 mg/kg) and recovery
  per barrel (1.73 lb/bbl) are inside the ranges. The steam is 2 % above the range, and that is
  disclosed. The steam, about 5.8 kg/kg Br2 and dominated by heating the brine to its boiling
  point, is the right order for an atmospheric hot-brine tower.
- **Key values sourced or ASSUMED**: every stream value is `assumed` with a source string. The
  design basis marks each engineering choice ASSUMED, and DESIGN.md lists open inputs O-1..O-9.
  The H2S side reaction is presented honestly as a calibrated chlorine sink, not a mechanism
  (D-005), and NH3, sulfate and free halogen in the tail brine are open (O-3, O-4).
- **No third-party content copied**: the source register paraphrases facts with locators. No
  tables, figures or passages are reproduced. Ullmann's (licensed) is used for route identity
  only, and the CC BY-SA Wikipedia pages for facts only. The BFD and PFD are generated from our
  own YAML.
- **LCI**:
  - Per functional unit: 1 kg S12.
  - Consistent with the flowsheet: every inventory row equals the stream divided by 3 750 kg/h.
  - Mass in = out: 249.932 kg/kg.
  - No zero-filled and no licensed background values: all 10 backgrounds are `missing:` gaps,
    each with a description of the activity to link.
  - `lca/mappings.yaml` exists with no active overrides; the candidates are listed in comments.
  - Emission exclusions carry reasons.
  - Every fact carries a locator: source strings name the stream and the decision.
- **process.yaml**: unreviewed, internal, concept. Its notes give the check results honestly,
  apart from R-03.

## Not checked
- The patent US 4 725 425, the AGS page and the Wikipedia pages were not re-read by the reviewer
  (only US 4 719 096 was).
- Halite saturation, brine cp and water activity: no property route, core#364. Bromine/chlorine
  speciation and stripping performance: no model.
- A full brine analysis (O-1). The real chlorine sinks (O-3). Free halogen in the tail brine and
  the vent (O-4).
- Equipment materials beyond the placeholder statement (D-012).
- P&IDs, layout, datasheets, HAZOP: none exist at this stage.
- Background datasets and characterisation: none linked; screening result only.

Merge pending: no critical or high finding is open. The medium findings R-01 to R-03 should
be fixed in their own commits before or soon after the merge, at the maintainer's choice.
