---
topic: design
reviewed_commit: 1d5bfda8352b1b3ec4dcf66cbfc8b804c83d2662
scope: [DESIGN.md, process.yaml, process/design-basis.yaml, process/materials.yaml, process/reactions.yaml, process/flowsheet.yaml, lca/lca.yaml, lca/mappings.yaml, lca/factors.yaml, lca/inventory.csv, lca/gaps.csv, runs/20261028-150643-design/report.md]
reviewer: review-agent
reviewer_kind: agent
branch: case/acetone-1
merge: pending
---

# Independent review: acetone-1 concept PFD and preliminary LCI (issue #132)

Reviewer: an independent agent that did not write the design. Branch `case/acetone-1`,
5 commits over `origin/main` (ea301c6..1d5bfda). I did not change any design file.

## What was re-run (not taken from the run report)

| command | result |
|---|---|
| `git diff --name-only origin/main..HEAD` | every changed file is under `processes/acetone-1/` |
| `cheme validate` | 16 files, 0 errors, 0 warnings. Info only: the template comment in `checks/checks.yaml:76` cites D-023, plus the usual port/connection cycles |
| `cheme check` | concept gates pass except `layout-plot-plan`, which is out of scope. The basic and detail gates fail as you would expect with no P&IDs and no layout. `design-review` fails until this record is committed |
| `cheme maturity` | calculation maturity: none. Warning `cheme.maturity-claim-exceeds` on `process.yaml:40` (R-02) |
| `cheme process streams` | 5 blocks and 15 steps close within 1 kg/h. The reaction extents agree between block and step |
| `cheme process propagate --check` | no output: nothing is stale and nothing would change |
| `cheme assess lca --coverage` | mass, element and carbon-origin balances closed, 13 gaps, all with a description. Classed "partial screening carbon footprint" |

## Checks against the scope

- **Route and boundary**: this is the cumene hydroperoxide (Hock) route, with cumene, H2, acid
  and caustic as boundary feeds, as issue #132 asks. The rejected routes (IPA dehydrogenation
  as its own case, phenol routes without acetone) are given with reasons. OK.
- **Balances, recomputed by hand**:
  - Air: 1 663 kmol/h. Spent air: 1 314 kmol N2 and 69 kmol O2, which is 5.0 mol% O2 dry and
    1 240 Nm3/t. OK.
  - Fresh cumene: 1.329 t/t phenol. Theoretical: 1.277 t/t.
  - Compressor: isothermal power nRT ln(600/101.3) / 0.75 = 2 716 kW. OK.
  - VOC at 35 mg C/Nm3: 1.21 kg/h of cumene. OK.
  - H2 vent: 1 Nm3/t, i.e. 2.25 kg/h. OK.
  - Brine: Na2SO4 144.8 kg/h. OK.
  - Phenol: produced 266.5 kmol/h net of cumylphenol, minus the tar and brine losses, gives
    25 000 kg/h. OK.
  - Steam: 1.9 t/t × 1 912 kJ/kg gives 25 228 kW, and 0.65 t/t × 2 108 kJ/kg gives
    9 515 kW. OK.
- **LCI**: per 1 kg acetone (S20), mass allocation with a share of 0.386 = 15 717.5 /
  40 717.5. Each exchange equals the plant flow × 0.386 / 15 717.5 (checked: cumene, air,
  power, steam). Inputs and outputs are both 2.0264 kg.
  - No zero-filled and no licensed values. `lca/factors.yaml` has only the packaged open
    profile and no own factors.
  - Every background is `missing:` with a description of the activity it should connect to.
  - The folder overrides are in `lca/mappings.yaml`: `steam-heat` exists in the shared
    `lci/mappings.yaml`, and H2 is set to `atlas: false` with its reason.
- **Copying**: I found no third-party tables, figures or passages. The ASCII block diagram is
  the author's own. Values from S1/S6 are used as facts with section locators. I did not
  fetch the BREF PDF again, so I did not re-verify the S1 numbers (Table 8.5, 8.3.x) against
  the original.
- **process.yaml**: `status: internal`, `validation: unreviewed`. The notes say plainly that
  `cheme maturity` reaches no level, that the utilities are literature data and that there
  is no impact result. Honest, apart from R-02.

## Findings
| id | sheet | item | finding | severity | status | proposed action |
|---|---|---|---|---|---|---|
| 2026-10-28-pfd-lci-review#1 | process/flowsheet.yaml (S16, S21, S30); lca/inventory.csv `product:WW` | aqueous effluent | The model's aqueous effluent is 64 kg per t phenol (1 603 kg/h; 0.039 kg per kg acetone in the LCI), and process water in is 40 kg/t. The source register (DESIGN.md S1, "8.3.5 water 1-4 t/t") cites a water figure 15-60 times larger, and DESIGN.md does not reconcile the two. The missing contributors are listed only one by one across D-005 (cleavage dilution water and acetone recycle), D-006 (vacuum system), D-007 (cumene caustic wash) and I-05 (phenol recovery). A reader of the LCI sees an effluent quantity that is probably far too low. It has no impact today because the WW background is a gap, but it will understate waste water treatment once a background is mapped | medium | open | Check what S1 8.3.5 quantifies (water use or waste water volume). Then either add an assumed effluent allowance with its source, or add a D-entry that states the gap to the BREF range and names the missing streams. Flag it on `product:WW` in lca/lca.yaml (source text) |
| 2026-10-28-pfd-lci-review#2 | process.yaml:40 | maturity | `maturity: concept` raises `cheme.maturity-claim-exceeds`: the evidence supports no design maturity. `concept` is the lowest value the schema allows, and the notes explain this, so a reader is not misled. But two of the sourced-level failures can be fixed with data already in hand. The feed compositions (pure cumene, dry air, 98 % acid, 50 % caustic) are specification values. The R101 selectivity is partly sourced from S6 | low | open | Give the specification compositions provenance `given` with a source where one exists, and re-run `cheme maturity`. If the level is still none, keep the note as it is |
| 2026-10-28-pfd-lci-review#3 | process/reactions.yaml (OX_CHP, OX_DMBA, OX_ACP); DESIGN.md D-011; flowsheet Q09, Q10 | heat duties and the "independent closure" | (a) The oxidiser cooling uses the ideal-gas heat of CHP formation (-82.4 kJ/mol). Liquid-phase values in the literature are of the order of -115 to -120 kJ/mol, and OX_DMBA and OX_ACP carry no heat at all, so Q09 is probably understated by about 30 %. (b) Q10 (spent-air condensers, 330 kW) is below a hand estimate of about 1 MW: cooling 39 t/h of gas from 383 to 308 K plus condensing 3.4 t/h of cumene. (c) `heat_of_reaction` is labelled `provenance: given`, but it is calculated from formation enthalpies. (d) The "independent closure within 2.7 %" (D-011, run report) is mostly true by construction, because each condenser is set equal to its own steam duty | low | open | Give a sourced liquid-phase heat of oxidation, or state the gas-basis bias in D-011. Add the side-reaction heats or say they are omitted. Re-estimate Q10. Mark the heats as calculated. Reword "independent closure" |
| 2026-10-28-pfd-lci-review#4 | process/flowsheet.yaml S20; DESIGN.md D-009 | acetone yield | Acetone is 0.627 t pure acetone per t phenol, above the stoichiometric 0.617 t/t. Phenol carries losses (cumylphenol, tar, brine), while acetone loses only 15 kg/h. Real plants lose acetone to mesityl oxide, diacetone alcohol and hydroxyacetone, to the brine and to vents. D-009 notes the difference from S2 (0.616), but it does not say that the ratio exceeds stoichiometry. Since the functional unit is 1 kg acetone, this lowers the per-kg burdens slightly (about 1-2 %) | low | open | Add an assumed acetone loss (for example to heavies or vents) so the ratio stays at or below 0.617, or state in D-009 that the model's acetone yield exceeds the stoichiometric ratio and why |
| 2026-10-28-pfd-lci-review#5 | DESIGN.md source register S2, S3; process.yaml references | source depth | D-007 uses S3 (US 5,245,090) for an acid loading of "0.01-5 wt%, preferably 0.1-2 %", but the register says only the abstract or a snippet was read and the full text was not audited. S2 (Speight) is cited second-hand through a skill summary. process.yaml lists two Ullmann's articles that were not read (they are labelled as such) | low | open | Read the S3 full text and give a locator (column/line or claim), or mark the acid loading ASSUMED and support it with S1 8.2.2.3 only. Keep the Ullmann's entries labelled, or move them out of `references:` until they are read |
| 2026-10-28-pfd-lci-review#6 | lca/lca.yaml emission_exclusions; dataset | cut-offs and dataset metadata | The `vacuum-vents` and `fugitive-leaks` exclusions have no amount, so the 1 % rule cannot be checked (`cheme.lca-cutoff-unchecked`). Yet S1 gives ranges that would bound them: off-gas methane of 100-400 mg/Nm3 on about 31 000 Nm3/h is 3-12 kg/h CH4, and fugitives are 0.02-0.06 kg/t. The dataset also lacks `classification.cpc`, and `emission:N2`/`emission:O2` have no compartment (info `cheme.lca-dataset-undocumented`, `cheme.lca-flow-identity`) | low | open | Give each exclusion an upper-bound amount in kg per year from the cited ranges, so the cut-off can be checked. Add the CPC code and the compartments |

No critical or high findings. The balances close, the LCI is per functional unit and
consistent with the flowsheet, no background is zero-filled or licensed, every gap has a
description, and the assumptions are marked ASSUMED.

## Previous findings
None (first review of acetone-1).
