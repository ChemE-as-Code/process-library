# Progress

Newest first. One line per change: date, sheet or file, what, why.

| date | where | what | why |
|---|---|---|---|
| 2026-10-28 | process/, scripts/, lca/, process.yaml, DESIGN.md | responses to reviews/2026-10-28-pfd-lci-review.md (below) | close the review findings |
| 2026-10-28 | DESIGN.md, lca/README.md | route memo, source register, decisions D-001 to D-011, method/dependency table, open inputs | record the concept basis and its gaps |
| 2026-10-28 | lca/, process.yaml | preliminary gate-to-gate LCI per kg KMnO4 (backgrounds missing), inventory/coverage written; Atlas manifest (internal, concept, unreviewed) | scope step 4 of issue #146 |
| 2026-10-28 | process/, scripts/kmno4_balance.py, equipment/, piping/, plant.yaml | design basis, materials, reactions, cells; balanced BFD/PFD (5 blocks, 10 steps, 23 material + 11 energy streams); equipment and line lists | concept flowsheet of the roasting-electrolysis route |
| 2026-10-28 | all | scaffold from `cheme init` and the process template | start of the case |

## Responses to reviews/2026-10-28-pfd-lci-review.md

The review has no critical or high finding. CI of PR #236 had no failed job (all completed
checks passed, the rest queued), so nothing was fixed for CI.

- Response #2 (medium): D-006 now says the 1000 A/m2 is the cathode current density (SRC-1),
  that the anode area and current density are open and must be lower, that CE falls with the
  per-pass conversion, and gives a CE sensitivity 0.60-0.90 of the electricity per kg
  (0.924-0.666 kWh/kg). Closed in e5d0fa3.
- Response #4 (low): D-007 records the in-cell KMnO4 crystallisation and that the Q5/Q6 split
  is open until solubility data are cited. Closed in e5d0fa3.
- Response #5 (low): D-005 describes the condensate "wash" as mostly leach dilution water and
  plans a realistic wash ratio for basic engineering. Closed in e5d0fa3.
- Response #6 (low): D-008 lists permanganate reduction and fouling in E-601 as a
  basic-engineering item. Closed in e5d0fa3.
- Response #7 (low): process.yaml validation notes say that `cheme maturity` gives none and the
  concept claim exceeds the evidence because the schema has no lower level. Closed in 0e1f04b.
- Response #9 (low): the schema's `elementary.origin` has no non-carbon origin; the "air,
  fossil" label of H2 is explained in lca/README.md and next to the flow in lca.yaml. Closed in
  0a86141.
- Response #10 (low): WATER_SPLIT heat of reaction set to `provenance: assumed` until the
  CODATA table is re-read (the review's second option); SRC-8 row updated. Closed in e5d0fa3.
- Response #11 (low): flowsheet step D501 renamed DR501 (ports, LPS port, Q10), BFD/PFD
  rebuilt, provenance script labels updated. Closed in 19e6063.
- Response #12 (low): DESIGN.md basis table (value, sourced/assumed/missing, source). Closed in
  e5d0fa3.
- Response #13 (low): concept gate `layout-plot-plan` deferred to basic engineering under "Open
  inputs and gated steps" in DESIGN.md. Closed in e5d0fa3.
- Open #1 (medium): the KOH heat of solution needs a sourced integral heat at 50 wt% and 13
  wt%, not read in this run; recorded as a known inconsistency in D-009 (e5d0fa3), Q1/Q8 and
  the LCI unchanged.
- Open #3 (medium): column:line locators need the patent PDFs, not read in this run.
- Open #8 (low): registry entries live in `chemicals/` outside this folder (consolidated PR).
