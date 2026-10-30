I fixed the high finding s10#1 and the low findings s10#3 and s10#4 by design. The medium finding s10#2 is only partly done: one of the four low-point drains is drawn; the other three and the CO2-1142 drain pot are recorded in the line list but not drawn. The work is committed in 6124898 and 8e9cfd5. The previous session's uncommitted edits were correct, so I kept them and committed them with mine. No finding was accepted and no gate was relaxed.

- **s10#1 (high), PC-1083 through V-401's ladder:** the route now runs along y 128 and jogs to y 127 only at x 249. That keeps it 1.0 m clear of the platform-1 ladder and its step-off, and north of the LD-202 laydown area. I added one low support under the short run leaving V-401's bottom nozzle. The ladder warning is gone (ladder-clearance warnings 9 → 8), no finding names PC-1083, and there are 0 clashes.
- **s10#2 (medium), low-point drains:**
  - DW-1073's drain is drawn on P-106: a tee, a DN 25 ball valve and a branch segment. The routing pin is split at the tee to match.
  - The PC-1083 and PC-1084 drains (P-107) and the CO2-1142 drain pot (P-113) are in the line-list notes as ASSUMED, to be drawn. There is no `cheme pid` command in this cheme 1.1.0, and each hand-drawn tee splits a segment and its pinned route; three more did not fit the budget.
  - D-047 now says where the CO2-1142 pot drains: through a valve and a float drain trap to U-801's closed condensate collection. The dip slopes towards it, and the pot, trap and drain line are heat-traced and insulated. All of this is ASSUMED.
- **s10#3 (low), K-501 motor tray:** moving the cable entry from 4.25 to 4.5 m takes the tray out of the lane from crane pad CP-501. The lift height is back to 9.636 m; the lane is still blocked by three pipes, as at basic sign-off.
- **s10#4 (low), crossings and sleepers:**
  - The 26 sleepers are now steel posts in the model and the take-off: 0.574 t of HEB100 and 4.68 m³ of footings, with section and spacing ASSUMED.
  - The model only generates step-overs where a declared walkway crosses a low pipe, and none is declared here. D-047 therefore lists three crossings, each a grating step-over (ASSUMED), as an allowance outside the take-off.
  - The estimate goes from 103,268 to 103,354, which is +3.95 % against main.
- **s10#5:** left alone, as instructed. PROGRESS.md says `design-review` stays stale until the next design review.

**Checks:**
- `cheme validate`: 0 errors, 234 warnings. The ladder warning is gone; a new `hazop-input-changed` warning for P-106 comes from the drain. I did not re-stamp the HAZOP study, because that would claim a reassessment nobody has done; the team has to reassess that node.
- The layout model, lifting study, take-off and estimate are all current.
- `cheme check`: `design-review` and `layout-review` fail because their records are now stale. `electrical` and `datasheets` fail, as they do on main. All other gates pass.
- `cheme maturity`: unchanged.

**Still open:**
- The three undrawn drains and the drain pot are not on the P&IDs yet.
- The dip's slope is not in the model, because its routes are level.

`build/pr-comment.md` is written. A merge is pending: an independent reviewer has to review this round.

STATUS: DONE