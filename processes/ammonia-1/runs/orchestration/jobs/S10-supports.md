# Your job: S10 pipe supports of ammonia-1 (branch stage/detail-supports; owner decision I-009)
Branch: stage/detail-supports (checked out), from main (basic signed off, tag nh3-run-final).
cheme is core v1.1.0.

Problem: `cheme layout build` generates **420 single full-height support posts** (`t_post`,
HEB200 from grade to the pipe) for 83 lines, wherever an off-rack run spans more than the
ASSUMED maximum unsupported length and no steel is near: median 7.9 m, 166 above 8 m, max
15.3 m; PG-1126 (DN 40 inert vent, ~100 m) alone has 54, then PG-1109 and CO2-1142 (27 each),
AL-1124 (24), DW-1073 (22). All are `review_needed`. They are unrealistic and inflate the MTO
steel and the estimate. The core-side fix is core#90 (not yours; do not work around core).

Do, by design (skills `pipe-routing`, `layout-yaml`, `structures-access`, `mto-estimate`):
1. Set a sourced `max_unsupported_length` (site plan) per DN if you can find an open, citable
   span table (cite it, our own words; else keep core's ASSUMED table and say so).
2. Route long small-bore and utility lines (vents, drains, chemicals, water, inert gas) along the
   racks or existing structures with routing intents (`rack`, `tier`, `via`, `elevation`), group
   parallel runs, bring lines low (sleeper elevation) where they run at grade, and shorten
   off-rack legs; use existing steel (rack, structures, platforms) where the build lets you.
3. Rebuild (`cheme layout build`), then report the post count, heights and the lines that still
   need posts and why; keep 0 clashes and every basic gate passing (`cheme check`), and do not
   reopen the lifting lanes (check `cheme layout lifting`).
4. Rebuild MTO and estimate (`cheme assess mto --write`, `cheme assess estimate --write`), update
   the TEA if it moves; report the steel tonnage before/after.
5. DESIGN.md decision (next free D-number), PROGRESS.md; `cheme validate` 0 errors; commit in
   logical steps; `build/pr-body.md`.
Never accept a finding. Final line: STATUS: DONE or STATUS: BLOCKED: <reason>.
