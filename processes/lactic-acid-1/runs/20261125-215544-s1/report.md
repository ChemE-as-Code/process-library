The basic-engineering basis for stage S1 is in place, in four commits on `stage/basic-lactic-acid-fermentation`. `cheme validate` shows 0 errors and 0 warnings, and the `layout-plot-plan` gate now passes. The concept's numbers are unchanged: the flowsheet values, recipe and duties are the same, and only the equipment links in the flowsheet point at the split tags, with BFD/PFD rebuilt.

**Decisions (DESIGN.md D-013 to D-027)**
- **Seed train (D-013):** five stages at 1:10, with stages 1–2 in the lab off-plot and stages 3–5 as plant fermenters of 1, 10 and about 107 m3. SRC-1 sizes each seed stage at about 154 h, which no 9.88 h inoculation schedule can follow. I chose 8 h of growth per stage (ASSUMED), so a stage holds its vessel 9.88 h, plus SRC-1's 12 h turnaround. That gives a 21.88 h cycle per vessel, so three trains are needed; SRC-1's two would be too tight. There is no seed hold tank: the seed moves by nitrogen pressure. Stage 5 doses milk of lime for pH; stages 3–4 use NaOH.
- **Medium and steriliser (D-014, D-015):** the flow mismatch is solved by blending the medium and sterilising it in 4 h campaigns at the fill rate (200 t/h) rather than adding a sterile buffer tank. E-101 is split into its parts: regenerative exchanger, steam heater E-102, holding tube X-101 (413 K for 120 s, ASSUMED), trim cooler E-103, back-pressure valve, and a divert valve back to V-101. The year-average steam stays at the concept's Q17 of 1.48 MW.
- **Fermenters (D-016 to D-020):** R-201A to P, each with:
  - a 160 kW agitator (127 kW absorbed) with a sterile-barrier seal;
  - half-pipe coils on its own tempered-water loop, with the temperature and lost-cooling agitator trip from D-012;
  - two pH probes dosing from a DN 100 milk-of-lime ring main;
  - no aeration (from SRC-1), a nitrogen overlay at 0.3 barg, DN 150 sterile vent and inlet filters;
  - a rupture disc sized on the SIP steam case, and a vacuum relief;
  - steam blocks on every sterile entry, which mark the sterile boundary.
- **Other decisions:** D-021 CIP and SIP, D-022 lime, D-023 sheet split and tag/line/instrument numbering, D-024 harvest and broth hold, D-025 downstream items, D-026 plot plan (fermenters outdoors in two rows of eight; a fermentation hall was rejected).
- **D-027:** the CSL protein lump has no formula, so its five component balances cannot be evaluated. Inventing a formula would be invented data, so I accepted these findings in `checks/checks.yaml` with that reason. This is my proposal; the reviewer should confirm or reject it.
- **Source register:** the SRC-1 seed-train facts from the specification are added to its row.

**Files**
- **Equipment list:** about 270 items, each with type, service, sheet, design pressure and temperature, material and dimensions, ASSUMED where not sourced.
- **`plant.yaml`:** stage set to basic, with the ten P&IDs (P-101 to P-403) declared as planned.
- **Line list:** 36 fermentation-area lines, each DN with its velocity basis.
- **Instrument list:** the instruments decided so far for P-101 to P-204, with R-201A as the typical and seed train A.
- **Layout:** `site-plan.yaml` (areas, roads, racks PR-1 to PR-6, separations around the ethanol area), `building.yaml` (B-201 for media, seed and CIP; control room; substation), and every listed item placed with no clashes.

**Gates still failing, each for a stated reason**
- `pids-exist`: no P&IDs are drawn yet; that is the next stage.
- `layout-3d`, `lifting-study`, `mto`: these need the 3D model, zones and structures, including the access structure on the fermenter tops where the filters are placed now but not yet mounted.
- `design-review`, `layout-review`: these need an independent reviewer.

**Not done yet:** the P&IDs, `control/loops.yaml` and `control/cause-effect.yaml` (they follow once P-101 and P-202 are drawn), the relief items in `piping/special-items.yaml`, R-201B to P's own lines and instruments, the tank bunds, and the HAZOP draft.

The commits carry an automatically set git identity (machine username and hostname); `git config` should be set before more commits. Nothing is pushed or signed off, and a merge is pending a human review of the branch.
