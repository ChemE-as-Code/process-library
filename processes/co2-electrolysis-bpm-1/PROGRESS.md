# Progress

Newest first. One line per change: date, sheet or file, what, why.

| date | where | what | why |
|---|---|---|---|
| 2026-11-04 | experiments/electrochemistry/rbpm-1m-koh.yaml, scripts/adapt_4tu.py, scripts/rawsheets.py, figures/*.svg, process/materials.yaml, process/reactions.yaml, process/cells.yaml, DESIGN.md D-004 to D-006, README.md, NOTICE.md, process.yaml | measured series of the 18 runs (cell voltage, CO and H2 FE, WDE per run; CP, MFM, GC and titration files paired by date and current density; the GC sheets' FE column found to use a fixed 0.25 A and 47.5 sccm and not used); components, CO2R and WS with CODATA heats of reaction; bench-cell at 200 mA/cm2, `performance: measured`: `cheme process cell` 5.37 V, FE CO 0.383, FE H2 0.560, WDE 0.967, 5.37 W, 3.98 W heat, no findings; core pin ab9d91e | #330 groundwork: core#137 landed (D-004 superseded) |
| 2026-11-04 | process.yaml, process/design-basis.yaml, README.md, DESIGN.md D-002, scripts/adapt_4tu.py | publication status internal (public is the maintainers' own change); carbon basis left unclassified until #330; validation note cites the reproduction's existence, not its agreement; Fig. 3c record is 5 h (failure within 4 h); README licence section states the library's licences; D-002 says the runs are the replicates; adapt_4tu downloads to a `.part` file renamed after the sha256 check (output unchanged) | review of PR #343 |
| 2026-11-04 | whole folder | created with `cheme init` (core 1.4.1); measured reference cell in the design basis, WDE series from the 4TU raw data, cell cross-section, D-001 to D-004 | #329: start the CO2 electrolysis case from the measured cell (tracker core#136) |
