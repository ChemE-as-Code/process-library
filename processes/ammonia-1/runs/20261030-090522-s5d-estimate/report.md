The capital estimate is now AACE 18R-97 class 4 (decision D-045, commit `62ba9eb`). The bulk unit rates are still not sourced, and four inputs still limit the accuracy (listed below). `cheme validate` shows 0 errors (258 warnings, as before). The `tea` and `mto` gates pass.

**What changed**
- **Equipment costed:** 41 of 52 items now have a cost from a published correlation, against 15 before. The total is 362.0 MUSD in 2023 dollars.
  - **Cr-Mo factors:** from Seider et al., read through the open IDAES and BioSTEAM code that cites the book. Vessels take 1.2; heat exchangers take about 3.05.
  - **Loop exchangers (161–170 barg):** Turton's pressure factor only goes up to 140 barg, so I extended it to the design pressure. That is marked ASSUMED.
  - **Reformer furnace:** priced with Turton's reformer furnace correlation, 30.6 MUSD. The catalyst tubes are included in it.
  - **Refractory-lined secondary reformer:** no open method exists. I priced the shell as carbon steel and put the lining into the allowance.
  - **Allowance:** 10 items no correlation can price (mainly the purge gas recovery, steam system and dryer packages) sit in a 10 % allowance. That figure is my judgement, with no source.
- **Cost index:** the 2023 value (797.9) stays, because the 2024 and 2025 annual values are behind the publisher's login. The TEA brings costs to 2025 with a Eurostat producer price index (×1.052) and converts at the 2023 Eurostat rate (1.0813 USD per EUR).
- **Bulk materials:** no open unit rates exist, so `estimate/rates.yaml` stays marked as an example.
  - Turton's bare module factors already include each item's piping, instruments, electrical, civil, steel, insulation, paint, erection and indirect costs. That is the factor method you asked for, applied per item in `estimate/cost-basis.yaml`.
  - The rates file can't hold it: its factors only multiply the take-off's own material cost.

**TEA results**

| | Before (IEAGHG reference) | Now (equipment estimate) |
|---|---:|---:|
| Fixed capital | 736.5 MEUR | 551.7 MEUR |
| Levelised cost | 748.2 EUR/t | 688.1 EUR/t |
| NPV | −1,049.4 MEUR | −845.3 MEUR |

The decision does not change: the levelised cost is still above the 439 EUR/t import price.

**Why it is class 4, and how accurate**
- AACE 18R-97 (rev. 2011, Table 1) defines class 4 as an equipment-factored estimate. The design is beyond the class 4 definition minimum: PFDs, P&IDs, a 3D layout and datasheets.
- Expected accuracy is −15 to −30 % and +20 to +50 %, which is 386–469 to 662–828 MEUR of fixed capital. The old IEAGHG figure falls inside the high band, which is a useful cross-check.
- **Accuracy drivers:**
  - Two loop exchangers make up 27 % of the equipment cost. Their sizes rest on assumed heat-transfer coefficients and they are priced as many split units.
  - The Cr-Mo factors come from a different textbook, and the high-pressure factor is extended past its range.
  - The 10 % package allowance has no source.
  - The location factor is 1.0, because I found no open US Gulf Coast to Netherlands factor.
  - The cost index is the 2023 value.
- **To firm it up:** vendor prices for the packages, the converter and the loop exchangers; a location factor; the current cost index.

**Things to know**
- The textbook factors were read through open code and documentation that cite the books, not the printed tables. They should be checked against the books.
- A new warning says class 4 is finer than the concept stage supports. It appears because `plant.yaml` stays at stage concept until the basic sign-off. I left it in place rather than suppress it.
- The gates that failed before still fail: the design and layout reviews (they need a new independent review), the lifting study (separate job), and two detail-stage gates.
- Calculation maturity is unchanged at balanced.

The PR description is in `build/pr-body.md` and the short PR comment in `build/pr-comment.md`. Everything is committed; a merge by the reviewer is pending.

STATUS: DONE