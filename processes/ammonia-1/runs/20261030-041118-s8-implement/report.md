S8 is finished on `stage/detail-relief` in two commits. The section's gate `relief-on-pid` passes. All eight relief valves have a named governing case, but only five have a required capacity; the other three are open because a needed input or method is missing. No P&ID was changed.

| valve | set (barg, ASSUMED) | governing case | required capacity (kg/h) |
|---|---|---|---|
| PSV-1212 | 38.5 | K-101 discharge blocked | 67,184 |
| PSV-1310 | 33 | front end blocked at XV-1604 or by a K-501 stop, still being fed | 139,409 |
| PSV-1513 | 2.5 | gas from C-301 through a fully open LV-1405 | not established: 355 per unit Kv, rough estimate about 127,000; at least 74,528 |
| PSV-1704 | 159.5 | synthesis loop blocked with full make-up gas | 65,958 |
| PSV-1911 | 161 | fire on V-501 | not established |
| PSV-1912 | 26.5 | gas from V-501 through a fully open LV-1903 | not established: 1,566 per unit Kv, rough estimate about 16,000 |
| PSV-2010 | 26.5 | fire on V-701 | 10,014 |
| PSV-2210 | 49.5 | process steam valve FV-1006 closed at full steam raising | 92,834 |

- **Set pressures** are the design pressures of the protected equipment. The real limits (MAWP) come with the vessel design.
- **PSV-1513 and PSV-1912:** the level valves LV-1405 and LV-1903 are not sized yet, so the rate is given per unit of valve capacity (Kv) plus a rough estimate.
- **PSV-1911:** at its relieving pressure V-501's contents are above ammonia's critical pressure. That case needs a time-dependent calculation that core v1.0.0 doesn't have.
- **What core can't do:** it has no relief sizing, no back-pressure calculation and no flare-network calculation. So no orifice, inlet line, outlet line or flare header was sized.
- **How the loads were calculated:** `scripts/relief_loads.py` uses standard published equations. I did not read the API 521, API 520 or IEC 60534 texts themselves; the equations come from secondary sources found by web search, listed below.

**Findings for the team:**
1. **(high) Methanation train unprotected:** if K-501 stops with XV-1604 open, R-401, E-402, V-401 and X-401 (rated 31–32 barg) are pushed above their design pressure. PSV-1310 doesn't protect them.
2. **(high) Hydrogen to atmosphere:** PSV-1513's worst cases vent hydrogen-rich gas through the CO2 vent.
3. **(medium) K-701 suction:** gas through LV-1907 reaches the K-701 suction, which is rated 18 barg.
4. **(high) E-502 tube rupture:** a tube rupture sends 17,725 kg/h of loop gas into the steam side. The only steam relief, PSV-2210, vents to atmosphere.
5. **(high) Relief lines too small:** every relief line and the DN 300 flare header are far too small for these loads. The worst combined flare load is a plant power failure, about 139 t/h through PSV-1310.

The HAZOP actions these cases answer stay open. The HAZOP now shows one new warning because a list it analysed (`piping/special-items.yaml`) changed. I left it visible for the team to reassess.

**Checks:**
- `cheme validate`: 0 errors, 252 warnings (251 on main).
- `cheme check`: `relief-on-pid` ok; every other gate's result is the same as on main.
- `cheme maturity`: unchanged (none).

The study is in `safety/relief/relief-study.md` and the decision is DESIGN.md D-033. The PR description is in `build/pr-body.md`. Nothing is pushed or merged; the push and the independent review and merge are still pending.

Sources for the fire equation:
- [open-exam-prep PE study guide 17.2](https://open-exam-prep.com/study-guides/pe-chemical/process-safety-relief/relief-valves-rupture-disks)
- [ioMosaic DIERS fire-case report](https://www.iomosaic.com/diersweb/docs/DIERS%20Technology%20Project%20Fire%20Case-Low%20Volatility%20Fluid%20Rev%209.pdf)
- Also searched but not used: [neqsim FireHeatLoadCalculator](https://equinor.github.io/neqsimhome/javadoc/site/apidocs/neqsim/process/util/fire/FireHeatLoadCalculator.html) and the Scribd copies of the equations.

STATUS: DONE