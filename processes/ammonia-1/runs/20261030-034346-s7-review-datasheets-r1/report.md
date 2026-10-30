I approved and merged PR #260 (S7 datasheets). The merge commit on main is `58c873f`; CI was all green first. The review record is `reviews/2026-10-30-datasheets.md` (commit `b82806c`). I also posted the verdict as a PR comment.

**Checks I re-ran myself:**
- **`cheme validate`:** 0 errors, 251 warnings. Of those, 12 are datasheet warnings, all on the convection coils' length and width.
- **`cheme check`:** the `datasheets` gate passes. The gate definition in `checks/checks.yaml` is unchanged on the branch, so nothing was relaxed. The other gates that fail (layout, electrical, maturity) were failing before this branch.
- **`cheme maturity`:** "none", the same as on main.
- **`cheme datasheets fill --dry-run`:** leaves every sheet as it is, because none is a draft any more.
- **Cited values:** I re-ran the ammonia vapour pressure at 313.15 K (1554.5 kPa(a)) and the steam saturation temperature at 4600 kPa(a) (531.93 K); both match the sheets.
- **Sizes recalculated by hand:** E-501, E-502, P-801, K-101, V-701 and P-301 all match the sheets.
- **Provenance and licences:** every value I opened says where it came from, and every open field names what is still awaited. Nothing third-party was copied.

**New findings:**
- **Medium #1: high-pressure gas exchanger areas.** They use near-atmospheric typical-U rows, so E-501 (44,544 m²) and E-502 (21,610 m²) are about ten times what such exchangers usually need. The sheets call them upper bounds, but an estimate would read them.
- **Medium #2: E-502 cold-end approach of 0.67 K.** That is not a feasible boiler design point. It comes from the simulation section's retune and nothing tracks it except a sentence in `DESIGN.md`.
- **Medium #3: sheets made final without an engineer's check.** The skill says a filled sheet stays a draft until an engineer checks it. A human should check them before the detail sign-off. Final sheets are also no longer refreshed by `cheme datasheets fill`; only rerunning `scripts/complete_datasheets.py` updates them.
- **Low #4 to #8:**
  - E-502's datasheet notes contradict the simulated values on the same sheet.
  - Adiabatic-bed residuals are written as `duty_kw`, so R-501's 454 kW could be read as a cooling duty.
  - The branch adds 12 coil length/width warnings that no open record carries.
  - The new design values in the equipment list are marked ASSUMED only in the file header.
  - Writing the datasheets with a script instead of Edit/Write is not recorded in `DESIGN.md`.

I carried the 23 open findings from earlier reviews unchanged. One of them gained a concrete number from the new sheets: E-105's design pressure is 49.5 barg on the steam side against 36.5 barg on the process side. That ratio of 1.36 is above the usual 10/13 rule, so a tube rupture is a credible relief case for S8.

No merge is pending.

FINDINGS: critical=0 high=0 medium=3 low=5
VERDICT: approve
STATUS: DONE