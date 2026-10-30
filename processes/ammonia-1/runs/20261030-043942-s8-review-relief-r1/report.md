I approved PR #262 (S8 relief) and merged it into `main` as `6c1e19f`. All CI checks passed first. S8 is not a stage sign-off section, so no sign-off is pending.

**What I re-ran myself:**
- `cheme validate`: 0 errors and 252 warnings. The only warning not on `main` is the disclosed `cheme.hazop-input-changed` on H-01.
- `cheme check`: `relief-on-pid` passes. The gates that fail also fail on `main` and are outside S8.
- `cheme maturity` and `cheme layout build --check` are the same as on `main`.
- `cheme run scripts/relief_loads.py` gives every rate in the study, in `special-items.yaml` and in D-033.

**Engineering check:**
- I recalculated four values by hand and they match:
  - the V-201 and V-701 fire loads;
  - the E-502 tube rupture, 17,725 kg/h;
  - the LV-1405 and LV-1903 blow-by rates.
- An API 520 orifice estimate for PSV-1212 supports finding R-5, which says the relief lines are too small.
- The set pressures equal the design pressures in the equipment list.
- I checked the cited equation values (API 521 fire equation, IEC 60534 choked gas flow, 10 % / 21 % accumulation) against the standard published figures, not against the documents themselves.
- Provenance is honest:
  - assumed values are marked ASSUMED and no trip is credited;
  - for the three devices with no established capacity (PSV-1513, PSV-1912, PSV-1911), the study says what is missing;
  - nothing third-party was copied, no gate was relaxed and no P&ID was changed.

**New findings** (record `reviews/2026-10-30-relief.md`, commit `0ab732c`, summary posted as a PR comment):
- **Medium #1:** the study misses three tube-rupture cases. Boiler water at about 45 barg in E-105 and E-201 can leak into the section PSV-1310 protects, and that is not among PSV-1310's cases. E-302 is missing from the table of cases with no relief device drawn.
- **Low #2:** the power-failure flare load of 139 t/h includes the K-101 air, although the same paragraph says K-101 stops in a power failure.
- **Low #3:** the indicative blow-by rates assume a linear valve characteristic. With the equal-percentage trim usual on level valves, they could be 2–3 times too low.

I carried forward four open findings from earlier records that touch relief: 2026-10-29-pids-loop#2 and #4, 2026-10-29-control-lists#2, and 2026-10-30-hazop-r2#1.

The study's own findings R-1 to R-5 are real design gaps. The worst are the V-401 train being unprotected when K-501 stops, the E-502 tube rupture into the steam side, and the relief lines and flare header being too small. Each is tied to an open HAZOP action, so I did not count them against this section.

FINDINGS: critical=0 high=0 medium=1 low=2
VERDICT: approve
STATUS: DONE