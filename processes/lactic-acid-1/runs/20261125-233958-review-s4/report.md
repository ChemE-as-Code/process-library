I've reviewed stage S4 and I don't think it can merge yet: R-201A is well engineered, but P-202 isn't ready to show. One high finding is open. No valve tag is printed on the sheet, so the valves the trips and control loops act on can't be found on the drawing.

**Review record:** `reviews/2026-11-26-S4-review.md` is committed alone as 22b609c4. It records 9 findings: 1 high, 4 medium, 4 low.

**Checks**
- `cheme validate`: 0 errors and 67 warnings. P-202 has 11 of them, all accepted one by one in `checks/checks.yaml`. One more, PSE-2045A not on any P&ID, comes from the rupture-disc symbol, which can't carry a tag.
- Every other warning is expected: P-201 and P-103 warnings accepted in earlier stages, a bad finding id in the S1 review record, and info items for sheets not drawn yet.
- `cheme fmt --check` is clean.
- `cheme check --stage basic` passes except design-review (it should pass now that this record is committed) and the layout, lifting and MTO gates, which wait for stage S8.
- I re-did D-031's arithmetic and it all checks: vessel volume, trip level, relief velocity, vacuum demand, cooling-water flow, the 12.5 h turnaround (harvest every 9.91 h) and the SIP steam. Assumed values are marked.

**What I saw in the renders (full sheet and three crops)**
- The sterile boundary is sound and reads like an industrial fermenter: steam blocks on medium, inoculum, lime, CIP supply and return, and harvest; a steamed sampling valve; filtered N2; the vent filter with its CIP bypass; the not-aerated and sterile-boundary notes.
- **#1 (high):** no valve tags anywhere on the sheet, including XV-2034A, TV-2011A/B, PV-2041A and PCV-2042A. The N2 regulator PCV-2042A also looks like two plain valves, with no sensing line.
- **#2 (medium):** the agitator is a zig-zag in the middle of the vessel, with no top-entry shaft, motor or seal.
- **#3 (medium):** no jacket or half-pipe coil is drawn. The tempered-water lines end on the shell, so the sheet reads as loop water going into the broth.

**Safety and process (medium)**
- **#4:** the vacuum trip I-204 doesn't stop the loop pump P-201A or close the CIP supply. Roughly 10 m3 of cooler loop water through the coils could condense about 1.5 t of steam, about 2,600 m3 of gas demand. That is far more than the 1,300 m3/h vacuum relief.
- **#5:** the rupture disc is sized on the normal SIP steam rate of 3 t/h. The real case is the steam valves wide open from the 3.5 barg LP header into a vessel designed for 2.5 barg, and nobody has calculated that flow. The disc also has no burst indication.

**Low:** TIC-2011A sits on the steam/water riser and its split range isn't readable; the vacuum relief is drawn as an untagged check valve; `process/recipe.yaml` still adds up to 12 h; the vent filter has no heating.

**Previous findings:** S1#3, S1#4, S1#7 and S2#9 are closed by 5ddd3363. Everything else stays open, with the S3 seed-train items left to S9 as the stage task asked.

**Scorecard:** `build/agent-run/S4/review.json` (not committed) scores process 4, safety 3, drawing 2 and consistency 4, with `acceptable: false`. Its carry-over list starts with #1, then #2 and #3, then #4 and #5. Findings #1 to #3 are a few hours of drawing work.

**Merge is pending.** It shouldn't merge until #1 is closed. Nothing was pushed, merged or signed off.
