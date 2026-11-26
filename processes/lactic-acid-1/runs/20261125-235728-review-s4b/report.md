I reviewed stage S4b and committed the review record alone as `8155c0ac`. **P-202 is acceptable to show:** no critical or high finding is open. **A merge is pending**; I did not push, merge or sign anything off.

**Checks**
- **`cheme validate`:** 0 errors, 67 warnings.
  - All 12 P-202 drawing warnings are accepted one by one in `checks/checks.yaml`, with a reason each.
  - 10 cross-check warnings on P-202 are not accepted (finding #1): 8 `instrument-not-on-pid` and 2 for PSE-2045A.
  - The rest are expected: the warnings from the earlier P-201 and P-103 stages, the malformed row in the S1 review record, and info items for the sheets not drawn yet.
- **`cheme fmt --check`:** clean.
- **`cheme check --stage basic`:** only five gates fail:
  - `design-review`, until this review record is on the branch;
  - `layout-3d`, `lifting-study`, `mto` and `layout-review`, because the layout stage (S8) has not run yet.
- **Renders:** I looked at the full sheet and two crops at scale 4 (`build/P-202_crop-0-20-250-220.png` and `build/P-202_crop-180-15-420-230.png`). Every actuated valve tag is now printed. The top-entry motor, gearbox, shaft and seal are drawn, and the half-pipe coil outline sits outside the shell. The TIC-2011A split-range outputs are labelled, PCV-2042A has its impulse line, and the burst indicator XA-2045A is shown.
- **Arithmetic:** I re-did the relief load: about 2.4 kg/s of SIP steam in, against about 6.0–6.4 kg/s the DN 150 disc can pass, so DN 150 holds. The recipe adds up to 12.0 h, which gives a harvest every 9.88 h with 16 fermenters.

**Earlier findings:** S4 review items 1–8 and the P-201 wildcard item (S3#6) are closed by `199c74d0`. S4#9 (vent filter heating) and the S1–S3 leftovers are still open.

**New findings (0 high)**
1. **Medium (#2):** R-201A is rated 2.5 barg with no vacuum rating. Collapsing steam after SIP would need about 24 000 m3/h of make-up gas, against 1300 m3/h for the vacuum relief. So the vessel depends on a trip with no SIL and on sequence steps not written yet. Fix: rate it for full vacuum (marked ASSUMED, as is usual practice), or state the rating and carry I-204 to a LOPA.
2. **Low (#1):** The valve tags are printed only as labels on the valves, so `validate` cannot match 8 instruments and PSE-2045A to the lists. They need representing the way `cheme` expects, or accepting one by one with a reason.
3. **Low (#3):** The relief basis assumes the LP steam header never exceeds 4.5 bar(a). A failed pressure letdown into that header, and the header's own relief, are not addressed.
4. **Low (#4):** The notes the audience will look for (drive and seal, "self-acting", "vacuum relief", PSE-2045A, coils) are about half the height of the line labels and can't be read at slide size.
5. **Low (#5):** The accepted 100-CS-2016A label reads as belonging to the drain line next to it; it should be moved instead.
6. **Low (#6):** No set points are given for the N2 regulator PCV-2042A and the vent pressure controller PIC-2041A, so the overlay could vent continuously or starve.

**Scores:** process 4, safety 3, drawing 4, consistency 3.

The next stage should first decide the vacuum rating, then enlarge the small notes and move the 100-CS-2016A label, then deal with the cross-check warnings.

Files are in `processes/lactic-acid-1/`:
- `reviews/2026-11-26-S4b-review.md`
- `build/agent-run/S4b/review.json` (not committed)
