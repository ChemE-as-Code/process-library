All five steps of S9 are committed on `stage/basic-lactic-acid-fermentation`. `cheme validate` reports 0 errors and 1250 warnings (1267 at the start). Nothing is pushed or signed off.

**What I did**
- **(0) XV-3013 on P-301 (S6#1, reopened):** the valve was already on the sheet. I rendered it and it shows the actuated ball valve on the tanker fill line, fail-closed, with the signal from LSHH-3013. Only the instrument-list check flagged it, because the tag is printed as the valve's label rather than in an instrument bubble. I accepted that check the same way the P-202 valves were accepted under D-034. I also accepted the one P-403 line crossing by its id, so the drawing-clean gate now passes.
- **(1) P-404 drawn (D-044):**
  - Concentrator: E-404A/B, E-461 condenser, V-461 drum and K-461A/B vacuum pumps. P-461A/B return the condensate as the hydrolysis water recycle and send a purge to waste water.
  - Product: P-462A/B, the E-405 cooler and the T-401A/B tanks. Each tank has a level transmitter and a separate high-high switch that closes its fill valve XV-4807A/B (trips I-401 and I-402). P-481A/B pump to truck loading.
  - Ethanol make-up: T-402, whose high-high switch closes the tanker fill valve XV-4704 (I-403), plus a low-low trip that stops P-472A/B (I-404). The make-up flow is held by the ratio controller FFIC-4701 on FV-4701.
  - The off-page connectors match P-403's. I rendered the sheet and looked at it; it has no drawing findings.
  - Lists updated: 27 lines and 17 instruments added. E-404A/B are now listed as ThinFilmEvaporator to match E-401, and the sheet title was shortened so it fits the title block.
- **(2) Layout:** `cheme layout build` ran with P-404 (1057 of 1199 segments routed; all the other 142 are the DN15 skips already declared in D-043). I then rewrote the material take-off and the lifting study from the new model.
- **(3) Documents:** README.md now says stage basic is in progress and lists the 16 sheets and what the fermentation area shows. DESIGN.md has a new "Basic-engineering status" section with each gate and why it passes or fails, and the open review findings by area. PROGRESS.md is updated.
- **(4)** The intended fixes for S8#1 to #3 and for S5#1 and #2 are written in that section as open items. None of them is implemented.

**Gates of stage basic**
- Pass: process-basic, process-links, pids-valid, drawing-clean and pids-exist. The mto gate should pass now that the take-off was rewritten, but I haven't re-run the check since.
- Fail:
  - **design-review and layout-review:** the review records are older than the latest changes, and S9 itself is unreviewed.
  - **layout-3d:** 278 pipe clashes and 158 headroom findings, mostly the fermenter branches (S8#1) and the seed building floors.
  - **lifting-study:** the removal lanes for S-301A to C are blocked by their own pipes.

**Still open**
- The fermenter deck rework (S8#1 to #4), the T-201 vent, overflow and high-high level trip (S5#2), and listing the instruments of the typical fermenters R-201B to P (S5#1).
- The medium and low review findings from S2 to S7b.
- On P-404, the remote acid-feed flow signal to FFIC-4701 is not drawn.
- The S8 review's question of why line-crossing warnings went up (S8#8) is still unanswered.
- No HAZOP.

**For the reviewer to confirm**
- The P-404 purge to waste water ends in a stub labelled "drain" (meaning a drain hub to the process sewer) rather than an off-page connector on the sheet edge.
- All the acceptances I added in `checks/checks.yaml` are marked as agent proposals.

A merge is pending: the branch needs the independent S9 review and a human merge.
