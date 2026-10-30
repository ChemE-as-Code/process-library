S5c is finished, but the section's target is not met: the `lifting-study` gate still fails. The crane lanes of K-101, K-102, K-103 and K-701 are blocked by their motor cable trays, and core v1.0.0 cannot route those trays out of the way (core#73). Every other basic gate passes except the two review gates. Everything is committed in five commits, `cheme validate` shows 0 errors and 258 warnings, and the PR description is in `build/pr-body.md`.

**Gates now**
- **Basic:** 10 pass; 3 fail: `design-review`, `layout-review` and `lifting-study`. `maturity-balanced` and `layout-3d` now pass; `mto` and `tea` are rebuilt and current.
- **Detail:** `layout-detail`, `hvac` and `control-complete` pass. `electrical` still fails (8 tray-fill findings, unchanged from S9). `datasheets` still fails on weights and nozzle locations.
- **`cheme maturity`:** calculation maturity is now **balanced** (it was none).

**What was done on each owner item (I-006)**
- **Feeds (D-040):** S1, S12, S61, S26 and S70 are now `given`, each source note naming the owner's approval:
  - Natural gas: Enbridge Gas typical analysis (94.7 % CH4 after lumping trace C4+ into propane).
  - Air: NASA dry air.
  - Water: demineralised water to the IAPWS make-up limits.

  Flows come from the 1500 t/d capacity. I re-ran the balance and the simulation and retuned the process air to 68,660 kg/h. That gives H2/N2 2.994, and the loop is very sensitive to it.
- **S5b boiler duty jump explained:** E-107's duty is a fixed value taken from the concept balance, so any change of gas lands on it (0.59 → 2.72 MW with this gas). With this gas the boiler duty only moves from 130.0 to 132.8 MW. The S5b run wasn't kept, so its exact 197.5 MW can't be reproduced.
- **Furnace H-101:** the H2 and NH3 burnout values are now `given`, sourced to a published furnace combustion paper (Schmitt, AFRC) and US EPA Method 19.
- **Lifting and headroom (D-041):** the owner's acceptances are recorded in `checks/checks.yaml` for the 8 lanes and the 4 buried road crossings. The tray lanes of K-101, K-102, K-103 and K-701 can't be cleared by design. The lane always covers the whole machine footprint, and the motor tray's last horizontal run always ends over the motor. No pad position, lane direction or tray elevation changes that, and there is no field for a motor cable entry point. Per your instruction I stopped there.
- **Risk matrix (D-042):** the example is replaced by an ASSUMED 5x5 project matrix accepted by the owner. The HAZOP was re-rated (12 low, 41 medium, 48 high, 16 very high); every entry stays `status: proposed`.
- **Estimate (D-044):** it is still **class 5**, not class 4. Most equipment is Cr-Mo, refractory-lined or above 140 barg, which the cost correlations have no factors for. No openly published bulk unit rates were found, so `estimate/rates.yaml` stays the example. Seven oversized items are now priced as several smaller units (87.7 MUSD, an upper estimate). The TEA uses the new gas's calorific value; NPV barely moves (−1,049.4 MEUR).
- **Datasheets (D-043):** main dimensions are filled on 51 sheets:
  - 11 exchangers sized from their area; E-501 alone needs 11 shells.
  - 15 vessels and columns got heads, supports and column sections.
  - Everything else (machines, convection coils, R-101 tubes, packages) has a `supplier` or `not_applicable` marker with a reason.

**Open items to flag**
- **Owner to confirm (review):** since the proposal, three accepted lanes also picked up blockers added in S9: K-501 (its motor tray), E-504 (an instrument tray) and E-505 (cooling-water lines of E-503). Each acceptance reason names them.
- **Datasheets:**
  - 12 are slightly stale (about 2 %) because their areas and duties were filled before the feed change.
  - 13 computed shell diameters don't match the one-shell size in the equipment list and layout.
  - Weights and nozzle locations are still open.
- **HAZOP:** two changed inputs (loop setpoints, and a relief-items change from S8) are left for the team; I did not re-stamp them.
- **Ledger:** I-006 is not yet recorded in `runs/interventions.md` on this branch.

Merge is pending: the basic reviews (design, layout) and sign-off come next, and the branch must not be merged by its author.

STATUS: BLOCKED: gate lifting-study fails on the lanes of K-101, K-102, K-103 and K-701, blocked by their motor trays; core v1.0.0 has no motor cable entry point to route them clear (core#73), and the owner did not accept these lanes.