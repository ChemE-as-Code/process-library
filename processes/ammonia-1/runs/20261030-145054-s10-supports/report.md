I cut the proposed support posts from 420 to 252 by changing the design, with 0 clashes. Two basic gates, `design-review` and `layout-review`, now fail: their review records no longer match the changed layout model, take-off and estimate, so the independent reviewer has to write new ones. `cheme validate` shows 0 errors. Everything is committed in three commits (`fd07cdc` layout, `13c485f` take-off and estimate, `0c285a8` decision D-047 and PROGRESS); the PR description is in `build/pr-body.md`.

**Span table:** I kept core's ASSUMED table. Core v1.1.0 reads spans per DN only from its own packaged file, and a plant can't override it. The site plan's `max_unsupported_length` is a single number (the 30 m rack reach), not a span per DN. So I didn't look for an open span table; this is a gap for core, next to core#90.

**What changed:**
- **Rack steel:** 173 of the original posts stood on racks, under small lines on 8–10 m bent spacing. I added intermediate steel (IPE240, ASSUMED) on the small-line tiers of PR-1, PR-2, PR-4, PR-7 and PR-8. I tried PR-10, PR-5, PR-6, PR-11 and PR-4's lower tier too and took the steel off each again, because it blocked E-105's crane lane, caused clashes, moved SM-1101 onto another rack, or stood in road R-6.
- **CO2-1142** (was 27 posts, now 0): runs along PR-4, then north at grade on sleepers in the gap between X-401 and CP-203, under X-401's crane lane, then crosses north of X-401 at 8 m.
- **PC-1083, PC-1084 and the DW-1073 grade leg** now run on sleepers.
- **Pinned to their signed-off routes:** SM-1040 and SM-1101, because the new steel had moved them (one clash, and the K-502 motor tray ending up in K-502's crane lane).
- **Moved clear of the new beams:** the drops of SL-1135 and PC-1136.

**Posts before and after:**

| | Before | After |
|---|---|---|
| T-posts | 420 | 252 (+3 short stubs on steel) |
| Median height | 7.9 m | 8.7 m (the short posts on the racks are gone) |
| Above 8 m | 166 | 144 |
| Maximum height | 15.3 m | 15.3 m |
| Free-span warnings | 73 | 41 |

Biggest drops: PG-1126 54→7, PG-1109 27→11, AL-1124 24→3, DW-1073 22→6.

**Why the rest still need posts:**
- **Relief lines** PG-1119, PG-1120 and AG-1134 (29 posts): they run at 9.6 m on purpose; sending them round by the racks would add back pressure.
- **Local runs:** process air (PA-1022), the large process lines between items, and the legs from a rack to a nozzle.
- **High runs on the U-801 package**, whose own steel isn't modelled.
- **The DW-1073/CO2-1142 crossing** over the access from road R-2, which needs a small pipe bridge.
- **About 62 posts within rack footprints.** Some of these come from a core bug: when a line is split at an off-page connector or tee, the router can lose the record that it runs on a rack. I recorded it as a core issue and did not work around it.

**Lifting:** the same 8 lifting findings as at basic sign-off, so no lane was reopened. K-501's lane, already blocked by three process lines, now also lists its motor tray, whose drop the PR-7 steel moved.

**Steel and cost:**
- **Steel take-off:** 555.1 → 672.2 t (+117.1 t of rack steel). The proposed posts were never in the take-off, because core counts them only once pinned; had they all been pinned they would have been about 208 t, and the remaining ones would be about 128 t.
- **Bulk estimate:** +3.9 %, on the example placeholder rates.
- **TEA:** unchanged; it rests on the equipment estimate and its gate is current.

**Other checks:** `cheme maturity` is unchanged (balanced, screening). The detail gates `electrical` and `datasheets` fail exactly as before and are outside this section. No finding was accepted and no gate relaxed.

**New ASSUMED values:** IPE240 for the rack steel, its spacing (2.0 m and 4.0 m), sleeper height (pipe centreline 0.35 m), and drains at the new low points, including a drain pot on the wet CO2 vent. The drains still need drawing on P-106, P-107 and P-113.

Merge pending: the independent reviewer reviews and merges.

STATUS: DONE