The 3D layout is now clash-free, but S5 is not complete: two of its gates fail and the class 4 estimate was not produced. Everything is committed on `stage/basic-layout` in six commits (`0a07751`…`82710fe`). The PR description is in `build/pr-body.md`, the decisions are in DESIGN.md D-031, and the change is logged in PROGRESS.md. `cheme validate` shows 0 errors and 183 warnings; calculation maturity is still none, as before.

**Gate results**

| Gate | Result | Why |
|---|---|---|
| layout-3d | Fails only on the missing layout review record, which is the S5r job | Every DN25+ process line is routed or skipped with a reason; 0 pipe, steel, equipment or headroom clashes (98 at the start); zones declared |
| lifting-study | Fails | Every heavy item has a crane pad and a laydown, but 26 lift lanes are blocked by piping over the item, often its own connections. H-101 is blocked by the R-101 headers on its roof; that is really a question of erection order, which the check can't express. None accepted |
| mto | Passes | Take-off: 10,875 m of pipe, 539 t of steel, 514 m³ of concrete |
| tea (now switched on) | Fails | Demineralised water, blowdown and cooling water still have no sourced price |

**Main layout changes**
- **New pipe racks:** the single concept rack left most equipment more than 30 m from a rack, so I added eight area racks branching off it (PR-2 to PR-8 and PR-10). To make room, K-101, E-301 and V-502 moved by 3–9 m. Rack positions, widths and tier heights are my assumptions.
- **Flare header:** its line-list start, "relief valves", gave the router no starting point, so FLR-1146 now starts at V-201, its first tie-in.
- **Furnace ducts:** the combustion-air and flue-gas ducts (DN 1800–4000) are skipped as part of the furnace package.
- **Hand-corrected routes:** I fixed four routes by hand where they met another line at a rack junction (NG-1001, BD-1141, SL-1135, PC-1136). The comments in `piping/routing.yaml` say where.
- **Tall items next to racks:** I kept the concept's toppling-distance rule (taller items kept at least their height from the rack) for the main rack PR-1 only. The new area racks stand closer than that: C-301 is 7.5 m from PR-4, R-501 15.2 m and X-601 2.0 m from PR-7. Someone needs to judge this against a risk study or the owner's spacing standard.

**Hazard zones and lifting inputs**
- **Hazard zones:** zone 2 around the synthesis-gas and ammonia compressor seals (K-501, K-502, K-701) and the natural-gas flanges, and an oxygen-deficient zone around the CO2 vent. They are screening values from cheme's built-in table of indicative radii (all marked ASSUMED), not an area classification.
- **Lifting inputs:** 13 crane pads, 12 laydown areas, and an estimated empty weight for every item from `scripts/estimate_weights.py`. All of these are assumed.

**Not done**
- **Class 4 estimate:** the bulk unit rates file is still the template example, so nothing can be priced from the take-off. The equipment cost correlations cover only 13 of 52 items, because exchanger areas, compressor powers and materials come with the datasheets in S7. I also found no cost index value with an exact source. The economics therefore still use the concept's class 5 capital (739 EUR/t, unchanged).
- **Lifting-study and tea gates:** the lifting gate needs a lifting plan or rerouting. The tea gate needs sourced prices for the three utilities above.

**Housekeeping**
- I drafted datasheets to get sizes, found they didn't provide them, and moved them out to `build/datasheets-draft-s5/` because they belong to S7. Nothing from them is committed.
- I listed the vented CO2 and the flue gas as free in the economics file, because their CO2 is already charged under the carbon price.

No merge has happened: the orchestrator pushes the branch, then S5r reviews and merges it.

STATUS: BLOCKED: lifting-study gate fails (26 blocked lanes, not accepted); tea gate fails (no sourced prices for demineralised water, blowdown and cooling water); class 4 estimate not produced (no sourced bulk rates, equipment sizes come with S7 datasheets, no sourced cost index); layout-3d waits only for the S5r layout review.