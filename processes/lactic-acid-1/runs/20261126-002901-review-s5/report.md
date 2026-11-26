I've written and committed the S5 review on its own as `ee4499a9`; it is `reviews/2026-11-26-S5-review.md`. Stage S5 is acceptable: no critical or high finding is open, and S4b#2 to #6 and S3#3 are now closed. Only P-203, P-206 and P-207 were drawn this stage. P-205 and P-204 are still to do, and so are the S3#1 to #5 fixes on P-201 that P-205 depends on.

**Checks**
- **`cheme validate`:** 0 errors and 54 warnings, all expected. They are the drawing warnings already accepted on P-201, P-202 and P-103, the PSE-2045A item (S4b#1), and the `-` row in the S1 record. The new sheets have no drawing findings left: P-203 and P-206 have their header crossings accepted, and P-207 has none.
- **`cheme fmt --check`:** clean.
- **`cheme check --stage basic`:** two groups of gates fail:
  - `design-review`, until this record is counted;
  - the four layout gates, because there is no 3D model or layout review yet (stage S8).
- **Renders I looked at:**
  - P-203, P-206 and P-207, full sheet;
  - a crop of one typical fermenter on P-203;
  - a crop of P-202, to confirm the S4b fixes.
- **Arithmetic I re-did, all consistent:** T-201 at 2293 of 2500 m³, harvest flow about 260 against 280 m³/h, feed to the centrifuges 104.6 against 125 m³/h, line velocities, and A-202 at 125 to 250 kW.

**Findings: 2 medium, 6 low**
1. **Medium, the 15 typical fermenters (B to P) are only on the sheets.** Their instruments, rupture discs PSE-2045x, vacuum reliefs PSV-2046x and trips are in none of the lists (instrument list, `special-items.yaml`, `cause-effect.yaml`). The sheet note doesn't name the relief devices, and the vents are drawn going straight to atmosphere.
2. **Medium, the broth hold tank T-201 has no protection drawn.** There is no vent or overflow, no high-level trip on the harvest pumps (280 m³/h into a 0.05 barg tank) and no CIP connection.
3. **Low:**
   - Pumps on P-207 have no isolation valves, and the variable-speed feed pump has no minimum-flow protection.
   - On P-203 and P-206 each steam block is drawn as one valve, so the sterile boundary shows only in a footnote.
   - On P-206 the sterile headers end in a single valve to drain, with no steam trap.
   - T-201's coil condensate goes to drain, and its temperature control valve TV-2052 is not in the instrument list.
   - The P-206 title runs up to the edge of its title cell.
   - Pump tags P-201 to P-203 share numbers with drawings P-201 to P-203, which makes notes ambiguous.

The scores file `build/agent-run/S5/review.json` (not committed) rates process 4, safety 3, drawing 4 and consistency 3. Its carry-over list starts with the S3#1 to #5 fixes, then P-205.

**Other notes**
- Running `cheme validate` on the review file alone compared 0 files, so I couldn't use it to check the record's format. The pre-commit hook accepted the commit.
- Git warned that the committer name and email were set automatically from your username and hostname.

Nothing was pushed or signed off. A merge is pending: a human merges the branch after reading the review.
