I fixed the six S4b findings and drew the fermenter overview as three sheets; both commits pass `cheme validate` with 0 errors (54 warnings, down from 67). P-205 and P-204 are not drawn: the S3#1 to #5 fixes on train A, which have to come before P-205, didn't fit in the budget.

**Commit 1: S4b findings (decision D-034)**
- **#2 vacuum:** R-201A to P are now designed for 2.5 barg and full vacuum. I-204 now protects the sterile filters and seals rather than the vessel. The 100 t vessel weight is kept as ASSUMED until a vendor confirms it.
- **S3#3, closed along the way:** the train B/C seed vessels now have train A's equipment class, and R-213B/C are rated 6.0 barg like R-213A.
- **#6 set points:** the N2 make-up regulator PCV-2042A is set at 0.25 barg and the vent controller PIC-2041A at 0.30 barg. N2 only enters below 0.25 and only vents above 0.30, so nothing purges continuously.
- **#3 LP header relief:** the basis is now stated. The LP header has its own relief valve at 3.5 barg (ASSUMED, site utility side). Even a failed letdown then gives about 2.7 kg/s into R-201A, against 6.7 kg/s that the DN 150 rupture disc passes.
- **#4, #5 legibility:** the six small P-202 texts are now 2.5 mm, and the 100-CS-2016A label sits next to its own line.
- **#1 valve tags:** I accepted the 8 valve-tag warnings and the PSE-2045A note in `checks.yaml`, with the reason. Validate only reads instrument tags from bubbles, not from valve labels.

**Commit 2: P-203 drawn as three sheets (decision D-035)**
- **Why three sheets:** 15 fermenters on one A3 sheet would leave about 26 mm per fermenter, which is unreadable at slide size. So:
  - **P-203:** R-201B to I.
  - **P-206 (new):** R-201J to P.
  - **P-207 (new):** harvest pumps P-202A/B, the broth hold tank T-201 and the centrifuge feed pumps P-203A/B.
- **How they're drawn:** one generator script, `scripts/draft_P-203.py`, loops over the fermenters. Each is a typical of R-201A on the common headers (inoculum, sterile medium, CIP supply, SIP steam, N2, harvest, CIP return, lime ring main). Each branch valve stands for R-201A's steam block, as a note on the sheet says. I rendered each sheet and looked at it; all three have 0 drawing findings.
- **T-201:** it gets a new agitator tag, A-202. Its power is not sized (125 to 250 kW ASSUMED, left to the vendor). It is held at or above 323 K by an LP-steam coil on TIC-2052, with level LIC-2051 and harvest flow FI-2053.
- **Lists:** 195 branch lines plus the two T-201 steam-coil lines added; the J to P and harvest items moved to their new sheets; A-202 placed in the layout.
- **Accepted findings, for the reviewer to judge:**
  - The branch-over-header crossings on P-203 and P-206 are accepted by an id pattern that only matches a branch crossing a header. These crossings can't be avoided when every fermenter connects to every header.
  - Nine older connector texts on P-103, P-201 and P-202 are accepted by explicit id. They name a header and its sheet, which by nature doesn't carry the branch's own line number.

**Other things to know**
- DEXPI's DIN 2448 list has no DN 250, so the harvest header's diameter is printed and listed but left out of the model.
- TV-2052 is a printed valve tag only, not in the instrument list.
- The design-review gate now fails only because files changed since the last review; the next independent review clears it. The layout gates (3D model, lifting study, take-off, layout review) were already failing.

**Left for the next stage:**
- S3#1, #2, #4 and #5 on P-201, then P-205 (trains B and C).
- P-204 (CIP station and SIP steam).
- The S2, S3 and S4 low findings and the layout gates.

Nothing is pushed. A merge is pending: the branch needs the independent review, then a human merge.
