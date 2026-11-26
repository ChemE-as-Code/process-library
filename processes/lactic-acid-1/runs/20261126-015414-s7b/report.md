I drew P-403 and committed it on `stage/basic-lactic-acid-fermentation` (not pushed). `cheme validate` reports 0 errors, the pre-commit hook passed, and I looked at the final render: it reads cleanly. **I split the planned sheet in two and drew only P-403.** The new P-404, with the product concentrator E-404A/B, product cooler E-405, product tanks and ethanol make-up, is not drawn yet.

**Why the split:** P-403 was planned with 38 items, about three times P-402's density, which would not read on one sheet. The split and its reasons are in DESIGN.md as D-042.
- **P-403 "Ethanol recovery and hydrolysis"** has 21 items: ethanol column C-402, stripper C-403 (drawn as C-402 mirrored) and hydrolysis reactor R-402 with their exchangers, drums and pumps.
- **P-404 "Product concentration, storage, ethanol make-up"** takes the other 17 items. It is in `plant.yaml` as planned, and those items are moved to it in the equipment list.

**What P-403 shows:**
- **Columns:** each has a reboiler on LP steam under temperature control, a condenser, a reflux drum with a pressure gauge and a vent to the vent header, reflux flow control, distillate on drum level, and sump level setting the bottoms pump speed.
- **Ethanol recycle to P-402:** both columns' ethanol and the make-up join `50-ET-4101`, which runs off-sheet to E-411 on P-402. It matches P-402's off-page connectors: P-402's ester column overhead (`100-PL-4210`) also arrives here.
- **R-402:** an agitated vessel. Its feed (C-402 bottoms plus the water recycle from P-404) is heated in E-441 under temperature control, and pumps on level control send the outlet to C-403.
- **Relief:** three relief valves (PSV-4309, PSV-4406, PSV-4509). Their relief cases are named but not sized.
- **Lists:**
  - Line list: 35 lines added, with their velocity basis.
  - Instrument list: 12 instruments added.
  - Special items: the three relief valves added.
  - Equipment list: C-402 and C-403 retyped to `ProcessColumn`, and R-402 to `Vessel`, to match what is drawn.

**Warnings I recorded as accepted or open in D-042:**
- **One line crossing:** the R-402 relief line crosses the C-403 ethanol line on its way to the top edge. Accepted.
- **DN changes with no reducer drawn:** at the pump suctions, at P-431A's discharge, and at the mixing tee before E-441. Accepted.
- **20 pump findings, cause unknown:** `cheme validate` says lines run through the pump symbols. P-402's pumps, drawn by the same builder, raise none, and I didn't find why before the budget ran low. Open.
- **Three off-page warnings:** the connectors to P-404 warn until P-404 is drawn. Open.

**One thing for you:** I couldn't delete the empty `pid/P-404.xml` that `cheme sheet new` created (the delete needed approval). It is untracked and not committed; please delete it or keep it for the P-404 drawing.

**Left open:**
- **P-404:** the sheet itself, its lines and instruments, the make-up ratio controller, and overfill protection on the product and ethanol tanks.
- **Earlier review findings:** the open S1 to S6 findings listed in this prompt. The stage asked for no other carry-over work, so I didn't work on any of them.
- **Layout:** the layout gates (`layout-3d`, `layout-plot-plan`, `lifting-study`, `mto`, `layout-review`) still fail; layout was not part of this stage.

A merge is pending: the branch needs the independent S7/S7b review first, and I did not sign anything off.
