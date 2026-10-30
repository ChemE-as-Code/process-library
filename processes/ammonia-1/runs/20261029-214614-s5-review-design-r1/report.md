I reviewed PR #257 (S5 of ammonia-1) as the design review, and the verdict is **fix**: the section's own gates do not pass. I wrote the record `reviews/2026-10-29-design.md` (reviewed commit 546e240), committed it as 73f5263, pushed the branch and posted the verdict on the PR. With the record in place, the `design-review` gate now passes. I did not merge, because this section ends with a stage sign-off.

**Checks I re-ran myself:**
- `cheme validate`: 0 errors.
- `cheme process simulate --check`: converged and every reactor energy balance closes. It exits with code 1 because of deviation warnings, not errors.
- `cheme layout build --check`: the 3D model is up to date.
- `cheme diff origin/main --list`: no P&ID changed in S5.
- Basic gates still failing: `lifting-study`, `tea`, `maturity-balanced`, and `layout-3d` / `layout-review`. The last two wait for the separate layout review.
- **Engineering numbers:** the mass, carbon and steam balances close. Steam-to-carbon ratio, methane slip after the reformers, CO after the shifts, converter conversion and machine powers are all in the normal range for this kind of plant.
- **Cited values:** the Eurostat electricity price (0.1062 and 0.0951 EUR/kWh for 2025) matches the source, and the 3.03 GJ/t steam value agrees with steam-table values.

**New findings:**
- **High (design#1):** S5's targets are not met, so the basic sign-off cannot go ahead.
  - The `tea` gate fails: demineralised water, blowdown and cooling water have no price.
  - The `lifting-study` gate fails on 26 blocked crane lanes.
  - The class 4 estimate was not produced.
  - `maturity-balanced` (simulation#1) still fails. It is a basic gate, so it also blocks the sign-off.
- **Medium (design#2):** the converter high-temperature trip and the K-502 and K-701 trips were deferred to S4 in D-029. S4 neither added them nor listed them as open, so they have dropped out of the design record.
- **Medium (design#3):** nothing protects against gas blowing through from V-502 (2500 kPa(a)) into V-701 (110 kPa(a)) if V-502 loses its level. The same case one step upstream, V-501 into V-502, has the low-low level trip I-107.
- **Medium (design#4):** the screening weights of the high-pressure exchangers are about ten times too low. The weight script assumes 1000 kPa(a) wherever an item's notes give no pressure, so E-501 is listed at 13 t, while the script's own formula at its real 15,500 kPa(a) gives about 167 t. The lifting study is planned on these weights.

**Carried findings:**
- I split pids-front#3, whose status "partly closed" is not allowed. Its still-open half, missing protection against gas blowing through from V-201, is now design#5.
- pids-mid#1–6 had been left out of the previous review record. They are listed again now.
- All other open findings are carried unchanged.

FINDINGS: critical=0 high=1 medium=3 low=0
VERDICT: fix
STATUS: DONE