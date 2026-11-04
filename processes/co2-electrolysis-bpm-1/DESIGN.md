# Design decisions

One entry per decision: what was decided, why, what was rejected, and what it assumes.

## D-001 Scope of the concept stage: the measured bench cell first (2026-11-04)
Decision: The folder starts as the measured reference cell of Prats Vergel et al. (2025):
- its configuration (process/design-basis.yaml, capacity.reference_cell);
- the WDE series in 1 M KOH (data/measured/wde-1m-koh.yaml);
- a cross-section (figures/cell-cross-section.svg).

The pilot-skid duty, the two skid designs and the LCA come later (#330, #331, tracker core#136).

Reason: issue #329 asks for the measured case before the model is generalised. The later steps
take their cell performance from these data.

Rejected:
- Fixing a pilot-skid duty now. It would be a number without a basis before the dynamic and
  sizing tools exist (core#138, core#139).

Assumptions: none beyond the paper's stated configuration.

## D-002 WDE from the raw titration sheets with the paper's equations (2026-11-04)
Decision: scripts/adapt_4tu.py evaluates every 1 M KOH sheet of the current-density study.
- Raw data: the 4TU raw-data zip, pinned by sha256.
- Equations: Methods eq. 3 to 10. K+ lost = (V0 − V2)·c_HCl·V_tank/V_titrate; carbon gained =
  (V2 − V1)·c_HCl·V_tank/V_titrate; WDE = 1 − F·(n_K + n_C)/(j·A·t_CP).
- Constants: c_HCl = 0.1 M, V_tank = 90 mL, t_CP = 3600 s, A = 5 cm2.
- Pairing: every "before" titration (V0) is paired with every "after" pair (V1, V2) of a sheet,
  as the authors' sheets do.
- Aggregation: pooled over the three runs at each current density.
  - The replicates are the three runs (dates).
  - The pairs of one run share their V0 and V1/V2 readings, so `n_pairs` is not a count of
    independent replicates. The pooled sd (over pairs) is not a run-to-run sd.
  - The per-run means are listed in the data file. A use that needs run-to-run scatter takes it
    from those three means (clarified 2026-11-04, review of PR #343).

Two sheets deviate in their headers, and the nominal values are used. 20241007 j100 states 10 mL
of electrolyte, and 20241007 j50 leaves the field blank; 90 mL and 1 mL are used, and the data
file notes both.

Reason: the raw sheets are the measured data. The published figure values are a result and
belong to the held-out reproduction.

Rejected:
- Taking the published Fig. 3a values as design data. They are results to be reproduced, not
  inputs (ADR 0032).
- Applying the 1.2 % factor the authors' own sheet calculation implies. The paper does not
  state it, and the reproduction reports it.

Assumptions:
- Nominal titrant strength, tank volume and run time. The paper states them; there are no
  per-run measurements of them.

## D-003 Stability criterion: anolyte pH 12 as a stated threshold (2026-11-04)
Decision: The anolyte is "stable" while its pH stays above 12, the authors' criterion. It is
reported as time to that threshold, never as a predicted corrosion onset of the Ni anode.

Reason: The paper defines stability by that pH and links it to Ni corrosion. The dataset holds
no corrosion measurement.

Rejected:
- Calling the threshold time a corrosion lifetime.

Assumptions:
- pH 12 is adequate for a Ni anode (ASSUMED, after the authors). #330 states the threshold
  used for the skid.

## D-004 No process/cells.yaml until the cell balance has measured inputs (2026-11-04)
Decision: The cell balance (`cheme process cell`, schema cheme/electrochemical-cells/v1) is not
written yet.
- It needs a Faradaic efficiency and a cell voltage.
- Those come from the GC, mass-flow and chronopotentiometry raw data, whose processing is
  core#137.

Reason: the v1 contract refuses a cell without them. Writing round values from the paper's text
would present unprocessed estimates as design data.

Rejected:
- A cells.yaml with ASSUMED FE and voltage now. It would be replaced as soon as #137 lands and
  would invite use in between.

Assumptions: none.
