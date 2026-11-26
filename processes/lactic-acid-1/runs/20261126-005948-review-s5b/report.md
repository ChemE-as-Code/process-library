I've written the S5b review and committed it alone (19cc0ae6). There is one **high** finding, so the stage is **not acceptable for merge yet**. The merge is pending, and a human must do it. Nothing was pushed or signed off.

**Checks**
- `cheme validate`: 0 errors, 163 warnings.
  - Expected: 146 of them are line crossings and off-page connectors not on the sheet edge on the seed sheets, P-202, P-103 and P-204. The drawing gate accepts them; validate still warns.
  - Not yet accepted: 9 unknown-tag warnings for the seed rupture discs PSE-21x5x and 8 off-page text mismatches on the P-201 and P-202 connectors to P-204 (finding #7).
  - Other real ones: 3 label overlaps, 1 DN mismatch on P-204, 2 line-endpoint mismatches and 1 rack-route warning (findings #5, #6, #8, #9).
  - Items on P-301 and P-401 to P-403 are skipped because those sheets are only planned, which is expected.
- `cheme fmt --check` is clean.
- `cheme check --stage basic --only-stage`: 5 gates ok, including the drawing gate, which now passes after the final P-204 redraw. 5 fail:
  - the design-review gate, which this record should satisfy;
  - the four layout gates (3D model, lifting study, material take-off, layout review), which belong to the later layout stage.
- I skipped `cheme diff c49d86cd --list` to save budget. I reviewed the stage from the four commits and from D-036/D-037.
- I rendered P-204 (full sheet and two crops) and a P-201 crop, and looked at them.

**Findings**
1. **High:** the SIP steam header is held at 3 barg (PIC-2205).
   - The production fermenters are designed for 2.5 barg, and their rupture disc PSE-2045A bursts at 2.5 barg. Seed vessels R-211 and R-212 are designed for 3.0 barg with discs at 3.0 barg.
   - The vessels are meant to be steamed at 121 °C, about 1.05 barg, but no pressure control between the header and each vessel is drawn or described.
   - So a normal SIP step could burst a disc and break the sterile boundary. The relief capacity itself was checked in D-033/D-034, so the vessels are protected.
2. **Medium:** on the CIP return, the conductivity (AIT-2203) and temperature (TT-2204) transmitters act on nothing. There are no automated divert valves to the caustic, acid or rinse tanks or the drain, and no sequence.
3. **Medium:** on P-204, the tanks have no level instruments, the pumps have no low-level protection or isolation valves, and the caustic fills have no high level. The CIP/SIP permissives are not in the cause-and-effect matrix.
4. **Medium:** D-036 calls the three seed sheets hand-maintained, but also says changes go through the script and a redraw of all three. These conflict: either declare them generated in `plant.yaml` or drop the redraw statement.
5. **Low (findings #5 to #10):** a DN100-to-DN80 mismatch on P-204, two line-list endpoints, the unaccepted warnings above, the F-241x label overlapping the F-242x filter, the 37 m caustic line 15-NA-2152 with no rack, and about 3.4 t/h of E-221 condensate going to drain.

**Previous findings**
- **Closed in this stage:** S3#1, #2, #4, #5, #7 and #8 (commit 4d6b171e), and S1#9 and #10 (commit d42332d2).
- **Still open:** all eight S5 findings, S4#9, S1#8, S2#1, #2, #3, #6, #7 and #8, and S3#9 and #10.

**Scores:** process 3, safety 3, drawing 3, consistency 3.

The carry-over list, most important first, starts with closing #1, then #2 and #3, then S5#1 and S5#2.

Files are in `processes/lactic-acid-1`:
- reviews/2026-11-26-S5b-review.md
- build/agent-run/S5b/review.json (not committed)
