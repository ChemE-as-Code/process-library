I fixed all five findings from review round 1 of the S6 HAZOP. The changes are in commit `9c6aaa9`, and a second commit adds the response entries to `PROGRESS.md`.

**#1 (high), tube rupture.** The study now has a tube-rupture scenario for each exchanger the review named, covering the case where the high-pressure side ruptures into the low-pressure side:

| Scenario | Exchanger | What leaks into what |
|---|---|---|
| S65 | E-202 | process gas at about 3200 kPa(a) into the solvent side and C-302 at 150 kPa(a) |
| S66 | E-203 | process gas into cooling water |
| S67 | E-402 | process gas into cooling water |
| S68 | E-502 | loop gas at about 15,100 kPa(a) into the 4600 kPa(a) MP steam system |
| S69 | E-503 | loop gas into cooling water |
| S70 | E-701 | ammonia into cooling water |

- Each scenario is rated. Each has an action (A42 to A47) that hands a relief case or a design-pressure decision to S8 (the relief study).
- I corrected the DESIGN.md D-031 sentence that called E-504 "the one exchanger" with a large pressure step.
- No cooling water pressure is stated anywhere in the project. I did not assume one, so the pressure ratio for the four coolers is marked TBD for S8.

**#2 (medium), residual credit.** The study's assessment basis now states one rule: a trip that is credited lowers the likelihood by one code, never more, until action A2 sets the trip integrity levels.
- S22, S25, S29 and S41 now follow that rule, and S22, S29 and S41 go back to high.
- S1's basis no longer calls the reduction "the team's judgement", and S22 no longer contradicts its own rating.

**#3 to #5 (low).**
- S12, S13 and D-031 now say that both I-101 and I-103 close XV-1204.
- The N3-RF note now points to S12 instead of S13.
- S18 now cites stream S87 (150 kPa(a), assumed) instead of an inferred pressure.

After re-rating, the study has 72 scenarios and 46 actions. The governing bands are 41 high, 23 medium and 8 low, and every high scenario has an action. Everything is still `status: proposed`.

**Checks**
- **HAZOP check:** 0 errors and 0 warnings. It still lists finding #1 as blocking, because only a new review record can close it.
- **`cheme validate`:** 0 errors and 239 warnings, the same as before.
- **`cheme check`:** the same basic and detail gates fail as before this fix, among them design-review, layout and the datasheets. This branch does not touch their inputs.
- **`cheme maturity`:** unchanged; the design maturity claimed in `process.yaml` is still above what the evidence supports.

The bands are still provisional, because they come from the example risk matrix and no HAZOP team has met. The two earlier control-lists findings carried forward by the review are outside S6 and still open.

The PR comment is in `build/pr-comment.md`. I have not pushed. A merge is pending: the branch needs a new review, and the review record notes it has no PR of its own yet (#38 is an older, merged ASU-1 PR).

STATUS: DONE