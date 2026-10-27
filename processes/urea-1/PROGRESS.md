# Progress

Newest first. One line per change: date, sheet or file, what, why.

| date | where | what | why |
|---|---|---|---|
| 2026-10-27 | DESIGN.md, lca/, process.yaml, design-basis.yaml, reactions.yaml | responses to review 2026-10-27-pfd-lci-review (below) | independent review, medium and low findings |
| 2026-10-27 | .gitignore, lca/dataset.yaml (untracked), DESIGN.md D-013 | LCI dataset no longer committed until lci/mappings.yaml maps its exchanges | PR #193 CI: `build_lci.py --strict` and two library tests refused 5 unmapped exchanges (8d94172) |
| 2026-10-27 | DESIGN.md, process.yaml, design-basis.yaml, equipment list | route/boundary memo, source register, basis table, decisions D-001..D-012, manifest (internal, concept, unreviewed), 18 PFD items | issue #120 concept scope |
| 2026-10-27 | lca/ | preliminary gate-to-gate LCI per kg prilled urea; every background declared missing with its target activity; balance closed | issue #120 LCI scope (D-011) |
| 2026-10-27 | process/, BFD, PFD | materials, reactions (conversion model), balanced flowsheet (5 blocks, 22 steps, 50 streams) from scripts/urea_balance.py and propagate; BFD/PFD built | issue #120 balanced PFD (D-005, D-006) |
| 2026-10-27 | all | scaffold from cheme init and the process manifest template | start of urea-1 |

## Responses to review 2026-10-27-pfd-lci-review

The review had no critical or high findings. All in commit 8d94172.

- **#1 (R-01, medium): closed.** D-010 no longer claims that the dehydration takes up E-102's
  surplus heat. It now gives the 24.2 MW left after the dehydration and the feed-preheat terms
  the script does not count (about 10 + 4 MW, ASSUMED). The remaining 10-24 MW is an open
  energy item under O-4, with its possible LCI effect. The script is unchanged.
- **#2 (R-02, medium): closed.** In `lca/lca.yaml`, the sources of feed:POWER and product:CW
  now say they are known underestimates (13 % and 25 % against BREF Tables 8.6/8.4) and what
  is missing. The CW source also names the R101/C401 heat not assigned. `inventory.csv` and
  `gaps.csv` were regenerated.
- **#3 (R-03, medium): closed.** D-004 and `design-basis.yaml` name the H2/O2 vent-gas
  hazard. New open input O-8 (H2 content, H2 removal, vent safeguards) for basic engineering
  and the HAZOP. O-1 points to it.
- **#4 (R-04, low): closed.** The fugitive NH3 cut-off now cites 0.27 g/kg NH3 and states its
  amount (about 2e-5 kg/kg, 0.002 % of the reference flow). The info
  `lca-cutoff-unchecked` remains: an emission exclusion has no amount field in the schema.
- **#5 (R-05, low): partly closed.** D-007 now says 1.6-1.8 times the BREF exhaust flow
  (6650 Nm3/t) and that the BREF capacity basis has not been checked. Still open under O-5:
  the S54 temperature against the assumed scrubber evaporation share needs the balance
  script to be re-run.
- **#6 (R-06, low): closed.** feed:CO2 is described as feed gas (98.5 mol%), and its
  `missing:` text explains the 0.86 % mass difference to the contained CO2.
- **#7 (R-07, low): closed.** Ullmann removed from the `sources` of UREA_SYN, with a comment
  saying it is added back after the O-3 audit.
- **#8 (R-08, low): closed.** `validation.notes` says that `cheme maturity` reaches no level,
  so `concept` is the schema's lowest value. It also mentions D-013 and the agent-only review.
