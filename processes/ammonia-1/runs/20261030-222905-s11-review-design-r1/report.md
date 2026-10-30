I approve PR #281 (S10/D-047 and S11/D-048). No critical or high finding is open. I did not merge it: the layout review runs next and merges if it also approves.

The record is `reviews/2026-10-30-design-s11.md`. It reviews HEAD e2b849b and was committed as 4e388ce and pushed. The verdict is also posted as a comment on the PR.

**Checks re-run on core v1.2.1:**
- `cheme validate`: 0 errors, 228 warnings. No headroom, buried-cover, tray-fill or clash finding is left.
- `cheme check`: gate `design-review` now passes with this record. `layout-review` still fails until the layout review is written. `datasheets` fails, but it is outside this section.
- Everything else in `cheme check` passes, including electrical, layout-3d, layout-detail, lifting-study, mto and tea.
- The layout model, cable schedule, MTO, estimate and LCA outputs are all current.
- `cheme maturity` is unchanged: balanced.

**What I verified:**
- **Removed acceptances:** removing the four headroom acceptances was correct. Their findings no longer exist anywhere in the model, and the headers have 3.09 m of cover under roads R-5 and R-6, more than the 1.2 m needed. No acceptance was added or widened, and no route skip was added.
- **Cover and depth numbers in D-048:** the arithmetic is right. No buried cooling-water run is shallower than 1.0 m. The only parts above that are the risers and valve legs at the users.
- **Spot checks:** the tray split matches the electrical list (nine 10 kV and two 400 V feeders, 3,339 m of power cable). The 1.2 m road cover is the package default, as cited.
- **Estimate:** the +14.25 movement says nothing about cost, because the example rates price every pipe size at the same rate per metre. D-048 already says excavation and backfill are missing.
- **Provenance:** every new value is marked ASSUMED or named as a package default, and no third-party content was added.

**New findings:**
- **Medium, s11#1:** S11 lowered the cooling-water headers to 3.8 m, in trenches about 4.6 m deep between the pipe-rack columns. That depth comes from the routing tool's 1 m hop, not from a civil check. Nothing records how the trenches interact with the rack column footings, groundwater or shoring, and the earthworks are not tracked as an open item.
- **Low, s11#2:** because the branch tees follow the P&ID order rather than the plot, the K-501 branches carry about 120 m of extra DN 450 pipe. The fix (reorder the tees on P-114) appears only as a rejected option, not as a tracked action.
- **Low, s11#3:** the core v1.2.0 rebuild also moved two other lines, PG-1088 and PG-1089, by 0.5 m, and lowered the X-601 lift height by 0.225 m. D-048 and the PR don't mention it.

**Earlier findings:** closed s10-r2#1 (outputs rebuilt), s10-r2#3 (blind flange on the drain) and detail-gates#2 (all cooling-water branches now buried). All other open findings are carried; detail-gates#3 is still true for K-101, K-501 and K-701 (supply and return share one nozzle point).

FINDINGS: critical=0 high=0 medium=1 low=2
VERDICT: approve
STATUS: DONE