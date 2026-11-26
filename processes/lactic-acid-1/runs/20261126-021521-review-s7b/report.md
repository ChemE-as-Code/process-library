I've finished the S7/S7b review. The record is committed on its own as `34fd38e2` (`reviews/2026-11-26-S7b-review.md`), and `build/agent-run/S7b/review.json` is written but not committed.

**Verdict:** acceptable, with no critical or high finding open. Scores are process 3, safety 2, drawing 3, consistency 4. A merge is pending: `drawing-clean` and the layout gates still fail.

**Checks**
- **`cheme validate`:** 0 errors and 209 warnings.
  - On P-403: 20 warnings for lines through the pump symbols, 4 for DN changes and 1 crossing that is not accepted.
  - Expected until P-404 is drawn: the off-page connectors to P-404 and the P-404 items not yet on a sheet.
  - The other sheets' warnings are earlier ones already recorded as open (S5b#7).
- **`cheme fmt --check`:** clean.
- **`cheme check --stage basic`:**
  - `design-review` is now ok.
  - `drawing-clean` fails again. D-042 calls the crossing of the R-402 relief line over the C-403 ethanol line accepted, but that acceptance was never added to `checks.yaml`.
  - The layout gates fail, which is expected before the layout stage.
- **Renders:** I looked at the full P-402 and P-403 sheets and a crop of the top of P-403. I did not re-render P-301 or P-401. I checked their fixes through the cause-and-effect file, the lists and the gate.

**Earlier findings**
- **Closed by `4197176d`:** S6#1 (the high one: acid tank level and overfill trips), S6#2 (acid dosing trips), S6#4 (E-401D level) and S6#6 (P-401 drawing warnings).
- **Still open:** every other earlier finding.

**New findings**
1. **Relief valves (medium).** The five relief valves on P-402 and P-403 are drawn as small check-valve triangles with no tag. Their vent-header off-pages carry no text. The DN80 relief lines are far too small for the cases they name: C-402 losing cooling water with 5.1 MW of reboil gives about 6 kg/s of ethanol vapour, roughly 180 m/s in DN80. No reboiler steam trip on high column pressure is considered.
2. **R-402 (medium).** It runs at 300 kPa(a) and 363 K with about 7 mol% ethanol. The sheet shows no pressure instrument or control, no vent or blanket, and no temperature measurement in the vessel. D-042 does not state the operating pressure.
3. **`drawing-clean` fails again (medium).** The cause of the 20 pump warnings is still unknown, although the pumps look normal at sheet scale.
4. **R-401 conversion (medium).** R-401 is drawn with no reboiler, condenser or reflux and only 214 kW of heat. As drawn it is an equilibrium-limited fixed bed, so it cannot reach the stated 98 % conversion (an assumed value).
5. **Low findings:**
   - The line from the mixing tee to E-441 carries 60 m3/h but is still DN80 on the sheet and in the line list.
   - A few small label points on P-402 and P-403.
   - The ethanol make-up ratio control and the tank overfill trips wait for P-404.

The process numbers I checked hold up: the E-441 duty (1.4 to 1.6 MW against 1.39 MW), the 91 wt% ethanol overheads and the 80 % ester conversion in R-402.

S7 and S7b did not touch the fermentation area. Its open findings are unchanged: the typicals' instruments, relief and trips; T-201 protection; the CIP divert and permissives; the single seat at the sterile boundary; and the slaker interlock.

The `carry_over` list in the JSON puts the `drawing-clean` fix first, then drawing P-404, then the relief valves.
