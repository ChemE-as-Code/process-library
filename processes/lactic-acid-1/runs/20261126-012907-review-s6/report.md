I've reviewed S6 and would not merge it yet: it adds a new high-severity finding and leaves the `drawing-clean` gate failing. The review record is committed on its own as `reviews/2026-11-26-S6-review.md`, and `build/agent-run/S6/review.json` is written (not committed).

**Checks**
- `cheme validate` gives 0 errors and 180 warnings. `cheme fmt --check` is clean.
- The 52 items listed for P-402 and P-403 are expected warnings, because those sheets aren't drawn yet.
- Five warnings on P-401 are new and not accepted, so the `drawing-clean` gate went from ok at S5b to fail.
- The layout gates still fail because there is no plant model yet, which is expected before S8. `design-review` fails until this review counts.
- I rendered both sheets and read the PNGs, including crops of P-301 and of the P-401 effects. The numbers in D-038 and D-039 check out by hand: steam about 13 MW against 13.7 MW, condenser 14.5 MW, vapour velocities 33 to 45 m/s, and 172 m3/h of cooling water for the 2.0 MW cooler.
- **The previous high finding (S5b#1) is closed by `d0e8fffa`.** The SIP header now runs at 1.5 barg, below every vessel's bursting disc and design pressure, which still gives about 127 C steam for the 121 C sterilisation.

**New findings (1 high, 5 medium, 4 low)**
1. **High:** the 93 wt% sulfuric acid tank T-301 is filled from road tankers but has no level measurement, no high-level trip and no overfill protection. Its dosing pumps have no low-level protection either.
2. **Medium:** nothing stops the acid dosing if the R-301 agitator stops, the pH goes very low, or R-301 is too full.
3. **Medium:** the three centrifuges run two at a time at 55 m3/h each, so 110 m3/h. That is against feed pumps rated 125 m3/h and an average harvest of 105 m3/h, leaving about 5 % margin.
4. **Medium:** nothing controls the liquid level in the last evaporator effect, E-401D. Its outlet is controlled on density and the feed follows the filtrate receiver's level.
5. **Medium:** the first effect's steam side has no relief valve and no design pressure stated against the steam header. The effects have no vents for non-condensable gases, and there is only one pressure gauge.
6. **Medium:** the 5 unaccepted P-401 drawing warnings. The effect tags sit on their symbols, and on the render they are crossed by the symbols' tube lines. One measuring line runs through a valve actuator.
7. **Low (four):**
   - The belt filter's cloth-wash supply isn't drawn, and the vacuum line has no pressure gauge.
   - R-301 vents straight to atmosphere.
   - Two centrifuge tags touch the cake chutes.
   - The new items, including R-301's agitator A-301, aren't placed in the layout.

The other 28 earlier findings stay open; most were deferred to the close-out stage S9 by the stage task. The JSON scores are process 3, safety 2, drawing 3 and consistency 4, with `acceptable: false`.

A merge is pending, and a human should merge only after the T-301 finding is closed.
