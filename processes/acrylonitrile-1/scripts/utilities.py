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
- A101's chiller: the lean water S20 chilled from the lowest temperature the cooling water
  reaches (its return temperature, 308.15 K: 25/35 C water with a 10 K approach) to S20's
  278.15 K, liquid water heat capacity (thermo 0.6.1, see the source register), electric COP
  4.0 (ASSUMED);
- the LP steam and cooling-water lumps from the base case of Li, Dimian and Kiss (2025)
  (SRC-2): its hot utility less the fired preheat of the reactor feeds, and its cold utility less
  its refrigeration plus this plant's chiller condenser, both scaled to 15 000 kg/h;
- cross-checks (printed only): the in-bed heating of the feed S5 to the reactor temperature, the
  reaction heat with the feed at the reactor temperature per kmol of acrylonitrile against
  SRC-2, the adiabatic mixing temperature of the feeds against S5's typed 373.15 K, the
  sensible heat of the quench inlet S7 to 358.15 K, and the feed vaporisers' heat.

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
COP = 4.0  # ASSUMED electric COP of the absorber-water chiller (D-009)
# liquid water, mean heat capacity 278.15-308.15 K, kJ/(kg K): thermo 0.6.1 HeatCapacityLiquid
# (method HEOS_FIT) integrated over the range and divided by 30 K and 18.01528 kg/kmol (SRC-5)
CP_WATER = 4.18666
# SRC-2 (Li, Dimian and Kiss 2025), kW, and its capacity: 120 kt/a from 272.34 kmol/h of
# acrylonitrile at 99.9 % recovery (section 3.1)
SRC2_HOT = 48420.0  # base-case hot utility after HX1 (section 4.1)
SRC2_FEED_PREHEAT = 5280.0 + 9710.0 + 1400.0  # C1, C2, C11 to 420 C, then to 440 C (section 4.2.3)
SRC2_COLD = 43150.0  # base-case cold utility (section 4.1)
SRC2_REFRIGERATION = 3390.0  # of which refrigeration of ABS-H2O, 25 to 5 C (section 4.1)
SRC2_RATE = 272.34 * 53.0634 * 0.999  # kg/h acrylonitrile product
# heats of vaporisation at 298.15 K, kJ/kmol: thermo 0.6.1 EnthalpyVaporization (HEOS_FIT), SRC-5
HVAP_298 = {"NH3": 19854.5, "C3H6": 14092.1}


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


def sensible(state, comps, t1, t2):
    """kW to take a gas stream from t1 to t2 (ideal gas)."""
    n = moles(state, comps)
    return sum(v * h_sensible(comps[k], t1, t2) for k, v in n.items() if v > 0) / 3600.0


def mix_temperature(parts, comps):
    """Adiabatic mixing temperature of ideal-gas streams [(state, T)], by bisection."""
    def excess(t):
        return sum(sensible(s, comps, t0, t) for s, t0 in parts)
    lo, hi = min(t for _, t in parts), max(t for _, t in parts)
    for _ in range(60):
        mid = 0.5 * (lo + hi)
        lo, hi = (mid, hi) if excess(mid) < 0 else (lo, mid)
    return 0.5 * (lo + hi)


def chiller(streams, cw_floor=308.15):
    s20 = streams["S20"]
    q = s20["flow"]["value"] * CP_WATER * (cw_floor - s20["temperature"]["value"]) / 3600.0
    return q, q / COP


def main():
    streams, comps = load()
    q5, n6 = e101(streams, comps)
    power, shaft, t2s, t2 = k101(streams, comps)
    print(f"E101 duty (S6 -> S7, ideal gas): {q5:.1f} kW")
    print(f"K101: isentropic outlet {t2s:.1f} K, actual outlet {t2:.1f} K, shaft {shaft:.1f} kW, electric {power:.1f} kW")
    q_ref, w_ref = chiller(streams)
    print(f"A101 chiller: S20 308.15 -> {streams['S20']['temperature']['value']} K, {q_ref:.1f} kW refrigeration, "
          f"{w_ref:.1f} kW electric (COP {COP})")
    scale = 15000.0 / SRC2_RATE
    q7 = (SRC2_HOT - SRC2_FEED_PREHEAT) * scale
    q8 = (SRC2_COLD - SRC2_REFRIGERATION) * scale + q_ref + w_ref
    print(f"Scale to 15 000 kg/h: {scale:.5f}; LP steam Q7 ({SRC2_HOT:.0f} - {SRC2_FEED_PREHEAT:.0f}) kW x scale = {q7:.1f} kW")
    print(f"Cooling water Q8 = {(SRC2_COLD - SRC2_REFRIGERATION) * scale:.1f} kW (SRC-2 scaled) + chiller condenser "
          f"{q_ref + w_ref:.1f} kW = {q8:.1f} kW")
    # cross-checks
    s5 = streams["S5"]
    t_bed = streams["S6"]["temperature"]["value"]
    q_feed = sensible(s5, comps, s5["temperature"]["value"], t_bed)
    acn = n6.get("ACN", 0.0)
    q4 = next((s for s in yaml.safe_load((ROOT / "process/flowsheet.yaml").read_text(encoding="utf-8"))["streams"]
               if s["id"] == "Q4"))["state"]["design"]["duty"]["value"]
    print(f"Reactor: {acn:.2f} kmol/h ACN formed; in-bed heating of S5 {s5['temperature']['value']} -> {t_bed} K: {q_feed:.1f} kW")
    print(f"Reaction heat with the feed at {t_bed} K: Q4 {q4:.1f} + {q_feed:.1f} = {q4 + q_feed:.1f} kW = "
          f"{(q4 + q_feed) * 3.6 / acn:.0f} MJ/kmol ACN")
    print("SRC-2 (section 4.2): 59.74 MW at 272.34 kmol/h ACN = "
          f"{59740 * 3.6 / 272.34:.0f} MJ/kmol; with the 1.40 MW to the inlet {61140 * 3.6 / 272.34:.0f} MJ/kmol")
    t_mix = mix_temperature([(streams["S1"], streams["S1"]["temperature"]["value"]),
                             (streams["S2"], streams["S2"]["temperature"]["value"]), (streams["S4"], t2)], comps)
    print(f"Adiabatic mix of S1, S2 and S4 (at {t2:.1f} K): {t_mix:.1f} K (S5 typed {s5['temperature']['value']} K)")
    print(f"Quench inlet S7 sensible heat to 358.15 K: {sensible(streams['S7'], comps, 358.15, streams['S7']['temperature']['value']):.1f} kW")
    vap = {k: streams[s]["flow"]["value"] / comps[k]["molar_mass"] * HVAP_298[k] / 3600.0 for k, s in (("NH3", "S2"), ("C3H6", "S1"))}
    print(f"Feed vaporisers at 298.15 K: NH3 {vap['NH3']:.1f} kW, propylene {vap['C3H6']:.1f} kW")
    cases = {"design": {"Q1": {"duty": round(power, 1)}, "Q2": {"duty": round(w_ref, 1)},
                        "Q5": {"duty": round(q5, 1)}, "Q7": {"duty": round(q7, 1)},
                        "Q8": {"duty": round(q8, 1)}, "S4": {"temperature": round(t2, 1)}}}
    target = os.environ.get("BALANCE_OUTPUT")
    if target:
        doc = {"contract": "balance-output/1", "script": f"scripts/{Path(__file__).name}", "cases": cases}
        Path(target).write_text(json.dumps(doc, indent=1, default=float), encoding="utf-8")


if __name__ == "__main__":
    main()
