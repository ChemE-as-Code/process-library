"""Duties core does not calculate for acrylonitrile-1 (DESIGN.md D-009).

Run with `cheme run scripts/utilities.py` from the process folder. Reads the stream values that
`cheme process propagate --fill` wrote into process/flowsheet.yaml and the components' ideal-gas
data of process/materials.yaml (chemicals 1.5.2 values, see the source register), and prints:

- E101, the reactor effluent cooler (waste-heat boiler): the sensible heat of S6 from its
  temperature to that of S7, ideal gas (no condensation: the water dew point of the effluent is
  far below 493 K at 195 kPa(a));
- K101, the process air compressor: ideal-gas isentropic compression of S3 to the pressure of
  S4 with the mean heat capacity ratio over the compression, isentropic efficiency 0.80 and motor
  efficiency 0.96 (both ASSUMED), and its outlet temperature;
- cross-checks (printed only): the reactor duty per kmol of acrylonitrile against the open
  design of Li, Dimian and Kiss (2025).

With BALANCE_OUTPUT set, writes the duties the flowsheet cites from this script (balance-output
contract, library ADR 0027).
"""

from __future__ import annotations

import json
import math
import os
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
R = 8.314462618  # kJ/(kmol K)
ETA_IS = 0.80  # ASSUMED isentropic efficiency of K-101 (D-009)
ETA_MOTOR = 0.96  # ASSUMED motor efficiency (D-009)


def load():
    fs = yaml.safe_load((ROOT / "process/flowsheet.yaml").read_text(encoding="utf-8"))
    mat = yaml.safe_load((ROOT / "process/materials.yaml").read_text(encoding="utf-8"))
    comps = {c["id"]: c for c in mat["components"]}
    streams = {s["id"]: s["state"]["design"] for s in fs["streams"] if "state" in s}
    return streams, comps


def moles(state, comps):
    """kmol/h per component of a stream given in kg/h with mole fractions."""
    x = state["composition"]["values"]
    mm = sum(v * comps[k]["molar_mass"] for k, v in x.items())
    n = state["flow"]["value"] / mm
    return {k: n * v for k, v in x.items()}


def cp_r(comp, t):
    a = comp["ideal_gas"]["cp_R"]
    return sum(c * t**i for i, c in enumerate(a))


def h_sensible(comp, t1, t2, steps=200):
    """kJ/kmol from t1 to t2 (trapezoid on the Cp/R polynomial)."""
    dt = (t2 - t1) / steps
    total = 0.0
    for i in range(steps):
        ta, tb = t1 + i * dt, t1 + (i + 1) * dt
        total += 0.5 * (cp_r(comp, ta) + cp_r(comp, tb)) * dt
    return R * total


def e101(streams, comps):
    s6, s7 = streams["S6"], streams["S7"]
    n = moles(s6, comps)
    t1, t2 = s6["temperature"]["value"], s7["temperature"]["value"]
    q = sum(v * h_sensible(comps[k], t2, t1) for k, v in n.items() if v > 0) / 3600.0
    return q, n


def k101(streams, comps):
    s3, s4 = streams["S3"], streams["S4"]
    n = moles(s3, comps)
    total = sum(n.values())
    t1, p1, p2 = s3["temperature"]["value"], s3["pressure"]["value"], s4["pressure"]["value"]

    def cp_mix(t):
        return sum(v * cp_r(comps[k], t) for k, v in n.items()) / total

    t2s = t1
    for _ in range(50):  # isentropic outlet: integral of Cp/R dT/T = ln(p2/p1)
        steps = 100
        dt = (t2s - t1) / steps if t2s > t1 else 0.0
        s = sum(cp_mix(t1 + (i + 0.5) * dt) / (t1 + (i + 0.5) * dt) * dt for i in range(steps))
        resid = s - math.log(p2 / p1)
        t2s -= resid / (cp_mix(t2s) / t2s) if t2s > t1 else -10.0
    h_is = sum(v * h_sensible(comps[k], t1, t2s) for k, v in n.items())  # kJ/h
    w_shaft = h_is / ETA_IS / 3600.0
    # actual outlet: h(t2) - h(t1) = h_is / eta
    t2 = t2s
    for _ in range(50):
        h = sum(v * h_sensible(comps[k], t1, t2) for k, v in n.items())
        t2 -= (h - h_is / ETA_IS) / (total * R * cp_mix(t2))
    return w_shaft / ETA_MOTOR, w_shaft, t2s, t2


def main():
    streams, comps = load()
    q5, n6 = e101(streams, comps)
    power, shaft, t2s, t2 = k101(streams, comps)
    print(f"E101 duty (S6 -> S7, ideal gas): {q5:.1f} kW")
    print(f"K101: isentropic outlet {t2s:.1f} K, actual outlet {t2:.1f} K, shaft {shaft:.1f} kW, electric {power:.1f} kW")
    s5 = moles(streams["S5"], comps)
    acn = n6.get("ACN", 0.0)
    q4 = streams.get("Q4")
    print(f"Reactor: {acn:.2f} kmol/h ACN formed; feed C3H6 {s5['C3H6']:.2f} kmol/h")
    print("Cross-check (Li et al. 2025, section 4.2): 59.74 MW at 272.34 kmol/h ACN = "
          f"{59740 * 3600 / 272.34 / 1000:.0f} MJ/kmol ACN")
    cases = {"design": {"Q1": {"duty": round(power, 1)}, "Q5": {"duty": round(q5, 1)},
                        "S4": {"temperature": round(t2, 1)}}}
    target = os.environ.get("BALANCE_OUTPUT")
    if target:
        doc = {"contract": "balance-output/1", "script": f"scripts/{Path(__file__).name}", "cases": cases}
        Path(target).write_text(json.dumps(doc, indent=1, default=float), encoding="utf-8")
    return q4


if __name__ == "__main__":
    main()
