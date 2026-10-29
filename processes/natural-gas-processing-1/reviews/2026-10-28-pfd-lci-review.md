---
topic: design
reviewed_commit: a96e4fb6b4919830545c47aae99c05eca309a98f
scope: [DESIGN.md, process.yaml, process/design-basis.yaml, process/flowsheet.yaml, process/materials.yaml, process/reactions.yaml, scripts/balance.py, equipment/equipment-list.yaml, lca/lca.yaml, lca/mappings.yaml]
reviewer: review-agent
reviewer_kind: agent
branch: case/natural-gas-processing-1
merge: pending
---

# Design review: natural-gas-processing-1, concept PFD and preliminary LCI (issue #181)

Independent review of the design agent's session `runs/20261028-154743-design` (commits
9ed425e..a96e4fb). I did not write the design and changed no design file. Concept stage: BFD/PFD
from `process/*.yaml`, equipment list, gate-to-gate LCI. P&IDs, layout, HAZOP and datasheets are
out of scope and were not reviewed.

## What was re-run (not taken from the run report)

| command | result |
|---|---|
| `git diff --name-status origin/main...HEAD` (merge base cc25cf3) | every change is inside `processes/natural-gas-processing-1/`. The two-dot diff against `origin/main` also lists the deletion of `aniline-1`, `dmf-1` and `ethanol-1`, but only because main moved on after the branch point. The branch does not delete them |
| `cheme validate` | 16 files, 0 errors, 0 warnings (infos: loader reference cycles; `checks/checks.yaml:76` D-023 comes from a commented template example) |
| `cheme check` | every concept and basic process gate passes (design-basis, concept-lists, process-concept, process-balances, process-links, process-basic, assumptions-marked). These fail and are out of scope: pids-exist, design-review (this record), layout-*, lifting, mto, electrical, hvac, datasheets |
| `cheme maturity` | calculation maturity **none**. Warning `cheme.maturity-claim-exceeds` on `process.yaml:37`. The `sourced-boundary` requirement fails (see R-02) |
| `cheme process streams` | 6 blocks and 19 steps ok. H601 reactive balance with extents CH4 4.945, C2H6 0.296, C3H8 0.114 kmol/h |
| `cheme process propagate --check` | exit 0, no findings |
| `cheme assess lca --coverage` | partial screening carbon footprint, 18 gaps, each with a description of the missing background. Mass balance closed. Element balance not assessable (consumables have no composition). Energy closure 0 %. Publishable |

## Plausibility checks (my own hand calculations)

- Feed: 100 MMscf/d at 379.49 scf/lbmol is 4980 kmol/h. M = 19.42 kg/kmol gives 96.7 t/h. Bukacek
  at 104 degF and 870 psia gives 58.4 + 16.7 = 75 lb/MMscf = 142 kg/h. Free water 1 bbl/MMscf =
  662 kg/h. All agree with the design.
- Sales gas: about 4 170 kmol/h, which is 83.7 MMscf/d and 68.7 t/h. HHV about 1 005 Btu/scf, within
  1035 +-5 %. NGL: 529 kmol/h C2 plus 255 kmol/h C3 is 27.1 t/h, plus C1 and CO2. Agrees.
- Amine: 14.9 kmol/h CO2 at a net loading of 0.245 needs 61 kmol/h MDEA, i.e. about 16 t/h of 45 wt-%
  solution (about 4 100 gal/h). At 1 lb steam per gal that is about 1.1 MW, and 6.2 GJ/t CO2. Agrees
  with the 1.08 MW claimed and the "circulation-limited" explanation.
- TEG and mole sieve: 13 kg/h of water at 7 lb/MMscf. Regeneration with 8 % of the gas from 313 to
  561 K over half the cycle is about 0.6 MW. Fired 1.03 MW absorbed at 80 % LHV is 115 kg/h of fuel.
  All agree.
- K-501: ratio 2.1, ideal gas, eta 0.80 gives about 3-3.5 MW shaft (GPSA-type rule about 45 bhp per
  MMscf/d gives 2.8 MW). Electricity 3 986 kW = K-501 + NGL pump (about 115 kW) + amine pump (about
  40 kW) + 150 kW auxiliaries. Agrees.
- LCI: allocation share 68 709.5 x 48.43 / (68 709.5 x 48.43 + 27 258.5 x 47.03) = 72.2 %. Raw gas
  97 518.9 / 68 709.5 x 0.722 = 1.0245 kg. CO2 (627 + 278) / 68 709.5 x 0.722 = 9.51 g. AP-42
  conversion 100 lb/10^6 scf at 1020 Btu/scf = 42.15 g/GJ. Consumables: 1 lb/MMscf gives 15 t/a MDEA,
  0.1 gal/MMscf gives 14 t/a TEG. All agree.
- Route and boundary match the issue's scope: inlet separation, amine AGR, TEG, turbo-expander NGL,
  sales compression. Sulfur recovery is correctly left out for the sourced H2S-free feed. The added
  mole sieve is justified ahead of a cryogenic section.
- Sources and licences: no third-party table, figure or passage copied. Only facts are used, with
  locators. AP-42 and EPA Natural Gas STAR are US government works. Wikipedia is used as a discovery
  source only and labelled as such. Ullmann's is marked as not read. The licensed background is
  untouched, nothing is zero-filled, and `lca/mappings.yaml` holds no overrides, as D-014 explains.
- `process.yaml` is honest about the limits: concept (lowest enum value), `validation: unreviewed`,
  and it states the specified-split basis, ideal-gas duties and excluded fugitives.

## Findings

| id | sheet | item | finding | severity | status | proposed action |
|---|---|---|---|---|---|---|
| 2026-10-28-pfd-lci-review#1 | DESIGN.md:154-164, scripts/balance.py | E-401 / V-401 / K-401 (cold section) | **R-01.** The design states "no external refrigeration" (ASSUMED), but the cold-box energy balance is not calculated (Q13) and the ideal-gas model carries no latent heat. Condensing about 27 t/h of C2/C3 and cooling it from 318 to 283 K needs roughly 3 MW. The available refrigeration is about 1.8 MW of ideal-gas expander work plus Joule-Thomson effects and the residue approach. For a rich gas (about 4.6 GPM C2+) at 90 % ethane recovery, a propane chiller of the order of 1-3 MW electric is likely. That would raise electricity, the LCI's largest stated gap driver, by perhaps 25-75 %. D-009 and the open inputs disclose this, but `process.yaml` and `lca/results.md` present 3.99 MW / 0.0419 kWh per kg without that caveat | medium | open | Add an order-of-magnitude cold-box enthalpy check (latent heat of the NGL against expander work) to `scripts/balance.py` or DESIGN.md D-009. Either add a propane-refrigeration scenario (power ASSUMED with basis) or state the possible under-estimate of electricity in `process.yaml` `validation.notes` and in the LCI sensitivity text of DESIGN.md section 5 |
| 2026-10-28-pfd-lci-review#2 | process/flowsheet.yaml:342 (also S8 :349, S33 :374) | S1 raw gas | **R-02.** The feed composition is sourced (Bullin and Krouskop 2009, Table 1, well 2, plus the Bukacek water calculation), but S1 carries `provenance: assumed, source: "scripts/balance.py"`. As a result `cheme maturity` fails `sourced-boundary` and the calculation maturity is "none", which makes the concept claim raise `maturity-claim-exceeds`. The sourced part of the basis is hidden behind the script | medium | open | Give the S1 composition (and the flow, whose basis is the design-basis capacity) as `given` with the source and locator, and say that water is calculated by Bukacek. Do the same for S8/S33, or record why they stay assumed. Re-run `cheme maturity`: the claim then rests on "sourced" |
| 2026-10-28-pfd-lci-review#3 | lca/lca.yaml:108 | emission-excluded:leaks, non-routine | **R-03.** Fugitive and non-routine methane are excluded without an amount, so the 1 % cut-off rule cannot be checked (`cheme.lca-cutoff-unchecked`). For gas processing these are typically the dominant direct methane source. A throughput-based screening factor of order 0.05-0.1 % of the gas processed would be tens of kg/h CH4, against the 3.05 kg/h in the inventory, and could double or triple the headline 0.0105 kg CO2-eq/kg. The exclusion is disclosed (D-014, results limitations), so the LCI is not wrong, but its direct-GHG number is easily misread as complete | medium | open | Give the exclusion an order-of-magnitude amount from an open, cited screening factor (e.g. an EPA GHG inventory processing-segment intensity or Subpart W population factors), marked ASSUMED, so the cut-off can be checked. Or add it as an emission estimate scenario |
| 2026-10-28-pfd-lci-review#4 | DESIGN.md:62 | S-9 Bukacek | **R-04.** The 47484 coefficient of the water-content correlation is "quoted from memory, to verify", and the other constants rest on a secondary student-thesis web page. My recalculation (75 lb/MMscf) is consistent with the usual charts, so the number is probably right. The source is still weak for a value that sets the water flows | low | open | Verify against an open primary or a recognised handbook reference and update the S-9 entry |
| 2026-10-28-pfd-lci-review#5 | lca/lca.yaml:21 | location | **R-05.** `location: GLO`, but the design is explicitly a US (Barnett-type, Texas) plant, and the dataset geography and the backgrounds named in `missing:` (ERCOT grid) are US | low | open | Set `location: US` (or US-TX) and regenerate the LCI outputs |
| 2026-10-28-pfd-lci-review#6 | process/design-basis.yaml (products), DESIGN.md S-6 | sales gas specification | **R-06.** The sales-gas specification (7 lb/MMscf, CO2 2-3 %, heating value band) rests only on Wikipedia, which is labelled as a discovery source. The 1003 Btu/scf product is near the lower edge of the quoted band (983 Btu/scf) | low | open | Replace with an open pipeline tariff or another citable specification when available. Already listed as an open input |

No critical or high findings: the balances close, the LCI is per functional unit and consistent
with the flowsheet, every background gap is described, and the main limitations are disclosed.

## Previous findings

None: this is the first review of this process.

## Merge

Merge pending. No critical or high finding is open, so the branch may be merged by a human. R-01
to R-03 should be closed or explicitly accepted before the next stage.
