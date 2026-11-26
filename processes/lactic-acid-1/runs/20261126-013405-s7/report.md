I fixed the most important review findings on P-301 and P-401 and drew P-402, but P-403 is not drawn: about $2 of the $9 budget was left after P-402, too little for its 38 items. Both are committed on `stage/basic-lactic-acid-fermentation` with 0 validate errors at each commit; nothing is pushed, merged or signed off.

**Commit 1: review fixes on P-301 and P-401 (decision D-040)**
- **S6#1 (high, acid tank T-301):**
  - Added a level transmitter LIT-3012 with high, low and low-low alarms; low-low stops the acid pumps P-304A/B (trip I-302).
  - Added a separate high-high level switch LSHH-3013, which closes the tanker fill valve (trip I-301). That valve was a hand valve and is now the actuated, fail-closed XV-3013.
  - The set points (90 % of tank height, 0.3 m above the outlet) are ASSUMED.
- **S6#2 (acid dosing trips):** dosing stops on agitator A-301 not running (I-303), pH low-low (I-304), R-301 level high-high (I-305) and broth flow low-low (I-306), all added to `control/cause-effect.yaml`. I-305 uses the control transmitter, so it is not independent; I-304 catches overdosing if the flow meter reads wrong.
- **S6#4 (E-401D level):** the last effect's level is now held by LIC-4011D on the product draw valve (the former DV-4002, now LV-4011D). DIC-4002 measures density on the pump suction and sets the steam flow controller FIC-4001. That link is in `control/loops.yaml` and is shown on the sheet as a note, not a signal line.
- **S6#6 (drawing):** the E-401A to D tags and the measuring line through the valve actuator are fixed. The `drawing-clean` gate passes again.

**Commit 2: P-402 drawn (decision D-041)**
- **Equipment drawn:** feed heater E-411, the reactive distillation column R-401 with pumps P-411A/B, and the ester column C-401 at 20 kPa(a). C-401 has its reboiler E-421 on MP steam, condenser E-422, reflux drum V-421, vacuum pumps K-421A/B, and reflux, overhead and residue pumps.
- **Relief:** two relief valves, PSV-4105 and PSV-4206, at the 3.5 barg design pressure. Their cases are named but not sized. They are drawn as check valves with PSV tags because the drawing tool has no safety-valve class; the plant already does this on P-202.
- **Lists:** 25 lines, 9 instruments and the relief items are added. R-401 and C-401 are now listed as ProcessColumn, the class actually drawn.
- **No residue cooler (deviates from the stage request):**
  - The residue leaves hot (about 423 K) in a traced line to digestion off-plot.
  - The reason is an ASSUMED steep viscosity rise on cooling.
  - If the receiver needs it colder, a cooler can be added at S9; this is flagged for the review.
- **Accepted:** three crossings where signal lines cross pipes, each with a reason in `checks/checks.yaml`.

**Left open**
- **P-403** is not drawn: ethanol column C-402, hydrolysis R-402, stripper C-403, concentrator E-404, cooler E-405, product and ethanol tanks, and the ethanol make-up. P-402 already expects its ethanol line from P-403 and sends its overhead to C-402 there.
- **Review findings deferred to S9:**
  - S6#3: centrifuge margin.
  - S6#5: evaporator steam-chest design pressure and relief, vents for non-condensables, effect pressure and temperature indications, vacuum pressure control.
  - S6#7 to S6#10, and the older medium carry-overs.
- **Basic-stage gates still failing:** design-review (the changes since the last review need an independent review), and layout-3d, lifting-study, mto and layout-review (no 3D layout model yet).

**Merge pending:** yes. The branch needs the independent review of S7 before a human merges it.
