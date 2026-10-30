I've worked through all 13 findings from the two round-1 reviews, but the one high finding (design#1) is only partly closed, so the section still can't be signed off. Gates `lifting-study` and `maturity-balanced` still fail. `cheme validate` shows 0 errors, and no gate was relaxed and no finding or lifting lane accepted.

**Closed:**
- **design#1 (a), TEA prices (dffba82):** demineralised water at 2.0 EUR/t, cooling water at −2.85 EUR/MWh (pump, fan and make-up cost of the cooling tower, worked out in the price's source), blowdown listed `free` with a reason. All are ASSUMED; no supplier price could be found. Gate `tea` now passes; the levelised cost goes from 738.6 to 748.2 EUR/t.
- **design#4, weights (b88272e):** `scripts/estimate_weights.py` now takes each item's pressure from its linked flowsheet streams. E-501 goes from 13.0 t to 167.5 t; 16 weights changed in total.
- **layout#1 (b88272e):** added crane pad CP-204 so E-401 is within reach of a crane.
- **layout#4 (b88272e):** added hazardous-area sources at the synthesis loop, X-601, V-701 and E-701. The rebuild reports no zone finding.
- **layout#2 (7a9cc1e):** added an east rack connector, PR-11. The liquid ammonia line AL-1128 drops from 432 m to 77 m, and total pipe from 10,875 m to 10,687 m. The reroute created three pipe clashes; I rerouted and pinned two lines to clear them, so there are 0 clashes.
- **design#2, #3, #5 (cfec6d0):** the missing converter, K-502/K-701 and gas blow-by trips are now listed in D-030's open items for the HAZOP. This is one of the two actions the reviewer offered.
- **layout#3, partly (7a9cc1e):** DESIGN.md now states what the material take-off leaves out.

**Still open:**
- **design#1 (b), lifting study:** 26 crane lanes are still blocked (V-701's became blocked after the reroute). Most are blocked by the item's own pipes or by erection order (H-101 under R-101). Only a lifting plan or a human acceptance can resolve them.
- **design#1 (c), class 4 estimate:** there are no sourced unit rates or CEPCI value, and equipment sizes come in S7. This needs sourced rates or a plan change from the orchestrator.
- **design#1 (d), `maturity-balanced`:** needs sourced reactor conversions and feed data, which is outside S5.
- **layout#3, pipe classes and insulation:** the line list doesn't carry class or insulation yet, so the pipe-specs file the reviewer asked for has nothing to key on.
- **layout#5 and #8:** the ladder, walkway and pinned-route fixes weren't quick; left for the next layout iteration.
- **layout#6 and #7:** these need GitHub issues, which this job can't open. The proposed issue text is in `build/pr-comment.md`.

Each finding has a Response entry in `PROGRESS.md`, and the PR comment is in `build/pr-comment.md`. The two review gates now show as out of date because the files they reviewed changed, so a round-2 review is needed. Merge pending: not pushed, not merged.

STATUS: BLOCKED: high finding 2026-10-29-design#1 is only partly closed. The 26 blocked crane lanes need a lifting plan or a human acceptance, the class 4 estimate needs sourced rates or a plan intervention by the orchestrator, and `maturity-balanced` needs sourced reactor conversions (outside S5).