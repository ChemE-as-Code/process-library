"""Energy balance of caprolactam-1's non-reacting steps (DESIGN.md D-009, D-010, D-013).

Core writes the duties of the three conversion steps R101, R201 and R301 (ADR 0059) and checks
no energy balance elsewhere. This script closes every other step on the same basis core uses
for the reactors: the constant liquid heat capacities of process/materials.yaml, sensible
enthalpy relative to 298.15 K, and the stream flows, compositions and temperatures of
process/flowsheet.yaml (as `cheme process propagate --fill` wrote them). Electric power drawn
by a step is counted as heat into it.

What it sets (cited in process/flowsheet.yaml as "scripts/energy_balance.py: ..."):
- the temperatures of the adiabatic steps: C401's outlets S16 and S17 (the crude lactam, the
  benzene and the column's 150 kW of power, no cooler) and M601's outlet S28 (a tank cannot
  cool);
- the coolers the stream temperatures imply: Q10 D101 (the oxime melt from 363 to 358 K), Q11
  D301 (the crude lactam from 353 to 323 K) and Q12 C402 (the extract and the benzene to 313 K);
- the evaporators' and the column's duties: the latent heat of the water evaporated per effect
  (Q5, Q8) or of the lactam distilled (Q6), and the steam or cooling that closes each step's
  balance with its sensible heat and power (Q4, Q7, Q9);
- the salt dryer's air heater Q13 (LP steam) and the heat its exhaust takes to the ambient
  air Q14 (ASSUMED moisture and efficiency).

Run: `cheme run scripts/energy_balance.py` in the process folder. With BALANCE_OUTPUT set it
writes the values above as the library's balance-output contract (library ADR 0027).
"""

from __future__ import annotations

import json
import os
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent.parent
T_REF = 298.15  # K, the reference of core's conversion-step duties (ADR 0059)

# Water's latent heat at 373.15 K, kJ/kg: thermo 0.6.1 EnthalpyVaporization, method HEOS_FIT
# (polynomial fit to the IAPWS-95 Helmholtz equation as packaged), queried 2026-11-19
# (DESIGN.md SRC-10): 40.649 kJ/mol / 18.015 = 2256.4 kJ/kg.
H_VAP_WATER = 2256.4
# Caprolactam's enthalpy of vaporisation, kJ/mol: NIST WebBook (Steele et al. 2002) at 440 K
# (DESIGN.md SRC-11).
H_VAP_CPL = 62.3
EFFECTS = 3  # ASSUMED, both evaporators (D-009, D-010)
REFLUX = 1.0  # ASSUMED, C501 (D-009)
CAKE_MOISTURE = 0.03  # ASSUMED, kg water per kg wet centrifuge cake (D-010)
DRYER_EFFICIENCY = 0.60  # ASSUMED, the latent heat of the moisture per heat into the air (D-010)

mat = yaml.safe_load((HERE / "process" / "materials.yaml").read_text(encoding="utf-8"))
COMP = {c["id"]: c for c in mat["components"]}
fs = yaml.safe_load((HERE / "process" / "flowsheet.yaml").read_text(encoding="utf-8"))
STREAMS = {s["id"]: s["state"]["design"] for s in fs["streams"]}


def duty(sid: str) -> float:
    return float(STREAMS[sid]["duty"]["value"])


def kmol(sid: str) -> dict[str, float]:
    """Component flows of a material stream, kmol/h."""
    st = STREAMS[sid]
    flow = float(st["flow"]["value"])
    comp = st["composition"]
    x = {k: float(v) for k, v in comp["values"].items()}
    if comp["basis"] == "mass_fraction":
        return {k: flow * v / COMP[k]["molar_mass"] for k, v in x.items()}
    mw = sum(v * COMP[k]["molar_mass"] for k, v in x.items())
    return {k: flow / mw * v for k, v in x.items()}


def cp(sid: str) -> float:
    """Heat capacity flow of a stream, kW/K."""
    return sum(n * COMP[k]["liquid_heat_capacity"] for k, n in kmol(sid).items()) / 3600.0


def temp(sid: str, override: dict[str, float]) -> float:
    return override.get(sid, float(STREAMS[sid]["temperature"]["value"]))


def h(sid: str, override: dict[str, float]) -> float:
    """Sensible enthalpy flow relative to 298.15 K, kW."""
    return cp(sid) * (temp(sid, override) - T_REF)


def net(ins: list[str], outs: list[str], override: dict[str, float]) -> float:
    """Sensible heat in less out, kW: the heat a step must reject (+) or receive (-)."""
    return sum(h(s, override) for s in ins) - sum(h(s, override) for s in outs)


T: dict[str, float] = {}
# C401 adiabatic: both outlets at one temperature, the power P4 into the liquid.
h_in = h("S11", T) + h("S15", T) + duty("P4")
t_c401 = T_REF + h_in / (cp("S16") + cp("S17"))
T["S16"] = T["S17"] = round(t_c401, 2)
# M601 adiabatic mixing.
t_m601 = T_REF + (h("S12", T) + h("S17", T)) / cp("S28")
T["S28"] = round(t_m601, 2)

Q: dict[str, float] = {}
Q["Q10"] = net(["S04"], ["S05", "S06"], T)                       # D101 melt cooler to CW
Q["Q11"] = net(["S10"], ["S11", "S12"], T)                       # D301 crude lactam cooler to CW
Q["Q12"] = net(["S16", "S20"], ["S21", "S14"], T)                # C402 cooler to CW
# E501: the last effect's vapour, the water of S19 at 1/EFFECTS, is condensed (Q5); the steam
# (Q4) supplies it and the sensible heat the products take out.
Q["Q5"] = float(STREAMS["S19"]["flow"]["value"]) * H_VAP_WATER / EFFECTS / 3600.0
Q["Q4"] = Q["Q5"] - net(["S21"], ["S19", "S22", "S23"], T)
# C501: reboiler (reflux + 1) x the lactam distilled, plus the water of the feed; the
# condenser and the product cooler take the reboiler's heat, the power and the sensible heat.
n_cpl = kmol("S24").get("CPL", 0.0) + kmol("S25").get("CPL", 0.0)
w_feed = kmol("S23").get("H2O", 0.0) * COMP["H2O"]["molar_mass"]
Q["Q6"] = (REFLUX + 1.0) * n_cpl * H_VAP_CPL / 3.6 + w_feed * H_VAP_WATER / 3600.0
Q["Q7"] = Q["Q6"] + duty("P5") + net(["S23"], ["S24", "S25", "S26"], T)
# EV601: the condensate S31 evaporated at 1/EFFECTS (Q8); the last condenser takes the steam,
# the power and the sensible heat the feed brings above the crystals, purge and condensate.
Q["Q8"] = float(STREAMS["S31"]["flow"]["value"]) * H_VAP_WATER / EFFECTS / 3600.0
Q["Q9"] = Q["Q8"] + duty("P6") + net(["S28"], ["S29", "S30", "S31"], T)
# The dryer: the centrifuge cake's moisture dried with hot air (heated by LP steam), the heat
# leaving with the exhaust air. Conservative: the model also counts this moisture in S31 and Q8.
moisture = float(STREAMS["S29"]["flow"]["value"]) * CAKE_MOISTURE / (1.0 - CAKE_MOISTURE)
Q["Q13"] = moisture * H_VAP_WATER / DRYER_EFFICIENCY / 3600.0
Q["Q14"] = Q["Q13"]

print(f"C401 adiabatic outlet temperature {t_c401:.2f} K; M601 adiabatic mix {t_m601:.2f} K")
for k in ("Q4", "Q5", "Q6", "Q7", "Q8", "Q9", "Q10", "Q11", "Q12", "Q13", "Q14"):
    print(f"{k}: {Q[k]:.1f} kW")
print(f"dryer moisture {moisture:.1f} kg/h")

target = os.environ.get("BALANCE_OUTPUT")
if target:
    shown: dict[str, dict[str, float]] = {s: {"temperature": t} for s, t in T.items()}
    shown.update({k: {"duty": round(v, 1)} for k, v in Q.items()})
    doc = {"contract": "balance-output/1", "script": "scripts/energy_balance.py",
           "cases": {"design": shown}}
    Path(target).write_text(json.dumps(doc, indent=1), encoding="utf-8")
