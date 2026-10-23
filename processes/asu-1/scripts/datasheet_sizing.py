"""Hand sizing of the datasheet values `cheme datasheets fill` cannot reach (DESIGN.md D-053,
D-060, D-063).

Provenance only: it prints each value with its basis; the values are written into
equipment/datasheets/<TAG>.yaml by hand, with the source "scripts/datasheet_sizing.py section n
(DESIGN.md D-063 (m))": n is this script's section number printed in each "== section n" header,
m the numbered item of DESIGN.md D-063 that records it (they differ, D-065 (1)).
It uses only cheme-as-code's own methods (the property adapter, the sizing and line-loss functions,
the public pump sizing `chemeascode.domains.equipment.pumps` along the routed pipes of the layout
model), IAPWS-95 for water and the Yoon-Thodos gas viscosity (chemicals, the props extra), so the
numbers are reproducible:

    cheme run scripts/datasheet_sizing.py

Every input that is an assumption is named here and in D-053 / D-060 / D-063. Since D-063 the
machines' Cp/Cv is the property adapter's at each stage's suction (temperature and pressure), not
one value at 298.15 K, and the stream states are read from process/flowsheet.yaml (the DWSIM
results of D-058, D-059 and D-061 included), not typed in.
"""

from __future__ import annotations

import math
from pathlib import Path

import numpy as np
import yaml
from chemicals import critical, iapws
from chemicals.viscosity import Yoon_Thodos, mu_IAPWS
from scipy.optimize import brentq
from chemeascode.domains.equipment import pumps, sizing
from chemeascode.domains.process.model import load
from chemeascode.domains.process.props import Adapter, Inputs
from chemeascode.domains.process.separations import shortcut

ROOT = Path.cwd()
R = sizing.R  # kJ/(kmol K)
CW_IN, CW_OUT = 298.15, 308.15  # process/design-basis.yaml cooling water 25 -> 35 C
U = sizing.typical_u("cooler/gases-water")  # D-053: the gas coolers' U row, ASSUMED
M_H2O = 18.015
DRY = ("N2", "O2", "AR")  # the components the property method supports

process, _ = load(ROOT)
adapter = Adapter(process)
network = pumps.network(ROOT)
streams = {s.id: s for s in process.flowsheet.streams}
SIM = yaml.safe_load((ROOT / "process/simulation.yaml").read_text(encoding="utf-8"))["specs"]


def sheet(tag: str) -> dict:
    return yaml.safe_load((ROOT / f"equipment/datasheets/{tag}.yaml").read_text(encoding="utf-8"))


def state(stream_id: str):
    return streams[stream_id].state["design"]


def fractions(stream_id: str) -> dict[str, float]:
    return dict(state(stream_id).composition.values)


def kelvin(stream_id: str) -> float:
    return state(stream_id).temperature.value + 273.15


def kpa(stream_id: str) -> float:
    return state(stream_id).pressure.value * 100.0


def flow(stream_id: str) -> float:
    return state(stream_id).flow.value


def molar_mass(x: dict[str, float]) -> float:
    comps = process.components()
    return sum(v * comps[k].molar_mass for k, v in x.items())


def dry(x: dict[str, float]) -> dict[str, float]:
    total = sum(x.get(k, 0.0) for k in DRY)
    return {k: x.get(k, 0.0) / total for k in DRY}


def h(stream_id: str, t: float | None = None, p: float | None = None) -> float:
    """Molar enthalpy kJ/kmol of a stream (or its composition at t K, p kPa(a))."""
    t = t if t is not None else kelvin(stream_id)
    p = p if p is not None else kpa(stream_id)
    return adapter.flash(Inputs(t, p, fractions(stream_id))).enthalpy


def water_cp_molar(t: float, p_partial_kpa: float) -> float:
    """Ideal-gas-like molar Cp of water vapour, kJ/(kmol K), IAPWS-95 at its partial pressure."""
    return iapws.iapws95_properties(t, max(p_partial_kpa, 0.05) * 1000.0)[5] / 1000.0 * M_H2O


def latent_heat(t: float) -> float:
    """Latent heat of water kJ/kg at t K, IAPWS-95 (just below / above saturation)."""
    psat = iapws.iapws95_Psat(t)
    return (iapws.iapws95_properties(t, psat * 0.999)[3]
            - iapws.iapws95_properties(t, psat * 1.001)[3]) / 1000.0


def cw_flow(duty_kw: float) -> float:
    water = iapws.iapws95_properties(303.15, 4.5e5)  # CW at its mean 30 C, ~4.5 bara
    return duty_kw / (water[5] / 1000.0 * (CW_OUT - CW_IN)) / water[0] * 3600.0


def cooler(name: str, duty: float, hot_in: float, hot_out: float) -> float:
    """Area of one gas cooler against cooling water, 1-2 shell and tube (D-053)."""
    dt = sizing.lmtd(hot_in, hot_out, CW_IN, CW_OUT, "1-2")
    f = sizing.correction_factor(hot_in, hot_out, CW_IN, CW_OUT, "1-2")
    area = sizing.exchanger_area(duty, U.value, f, dt)
    print(
        f"  {name}: Q {duty:.4g} kW, hot {hot_in:.5g} -> {hot_out:.5g} K, CW 298.15 -> 308.15 K, "
        f"1-2 LMTD {dt:.4g} K, F {f:.4g}, U {U.value:g} W/(m2 K) (middle of {U.low:g}-{U.high:g}, "
        f"{U.source}), A = Q / (U F LMTD) = {area:.4g} m2; CW {cw_flow(duty):.4g} m3/h (IAPWS-95 water "
        f"at 30 C, 10 K)"
    )
    return area


def k_at(t: float, p: float, x: dict[str, float]) -> tuple[float, float]:
    """Cp/Cv and molar Cp kJ/(kmol K) at a stage suction: the property adapter for N2/O2/Ar,
    water vapour mixed in on the molar Cp (IAPWS-95 at its partial pressure); CO2 counted with
    the dry gas."""
    k_dry = adapter.heat_capacity_ratio(Inputs(t, p, dry(x)))
    cp_dry = R * k_dry / (k_dry - 1.0)
    xw = x.get("H2O", 0.0)
    cp = (1.0 - xw) * cp_dry + xw * water_cp_molar(t, xw * p)
    return cp / (cp - R), cp


def machine(tag: str, stream_id: str, p_out: float, n: int, eta: float, cooled: float | None,
            dp_cooler: float = 0.0, condense: bool = False):
    """Ideal-gas stages with Cp/Cv at each stage suction (D-063); equal stage ratios split the
    pressure after the coolers' drops; water above saturation condenses at `cooled` (IAPWS-95)."""
    x = fractions(stream_id)
    n_mol = flow(stream_id) / molar_mass(x)  # kmol/h
    t, p_in = kelvin(stream_id), kpa(stream_id)

    def outlet(r: float) -> float:  # last stage discharge (before its aftercooler)
        p = p_in
        for i in range(n):
            p = p * r - (dp_cooler if i < n - 1 else 0.0)
        return p

    ratio = brentq(lambda r: outlet(r) - p_out, 1.0001, 10.0)
    stages, p = [], p_in
    for i in range(n):
        k, cp = k_at(t, p, x)
        mw = molar_mass(x)
        st = sizing.ideal_gas_stage(t, ratio, k, mw, eta, "isentropic")
        m = n_mol * mw / 3600.0  # kg/s
        p_dis = p * ratio
        row = {"stage": i + 1, "t_in": t, "p_in": p, "k": k, "cp": cp, "mw": mw, "m_kg_h": m * 3600.0,
               "t_out": st.outlet_temperature, "p_out": p_dis, "power": m * st.work,
               "sensible": 0.0, "condensed": 0.0, "latent": 0.0}
        if cooled:
            row["sensible"] = n_mol / 3600.0 * cp * (st.outlet_temperature - cooled)
            p_c = p_dis - dp_cooler
            if condense and x.get("H2O", 0.0) > 0.0:
                y_sat = iapws.iapws95_Psat(cooled) / 1000.0 / p_c
                n_w = n_mol * x["H2O"]
                n_other = n_mol - n_w
                n_left = min(n_w, n_other * y_sat / (1.0 - y_sat))
                cond = n_w - n_left
                row["condensed"] = cond * M_H2O
                row["latent"] = cond * M_H2O / 3600.0 * latent_heat(cooled)
                n_mol = n_other + n_left
                x = {k_: (v * (n_mol + cond) - (cond if k_ == "H2O" else 0.0)) / n_mol
                     for k_, v in x.items()}
            t, p = cooled, p_c
        else:
            t, p = st.outlet_temperature, p_dis
        stages.append(row)
    power = sum(r["power"] for r in stages)
    print(f"{tag}: {flow(stream_id):.6g} kg/h ({stream_id}), {p_in:.4g} -> {p_out:.4g} kPa(a), {n} x "
          f"ratio {ratio:.4g}, eta_s {eta:g}, cooler drop {dp_cooler:g} kPa; gas power {power:.5g} kW")
    for r in stages:
        print(
            f"  stage {r['stage']}: suction {r['t_in']:.5g} K {r['p_in']:.5g} kPa(a), Cp/Cv "
            f"{r['k']:.4f} (property adapter at the suction, water by IAPWS-95 molar Cp), M "
            f"{r['mw']:.4g}, {r['m_kg_h']:.6g} kg/h, discharge {r['t_out']:.5g} K "
            f"({r['t_out'] - 273.15:.4g} C) {r['p_out']:.5g} kPa(a), {r['power']:.5g} kW; cooler: "
            f"sensible {r['sensible']:.5g} kW, condensed {r['condensed']:.5g} kg/h, latent "
            f"{r['latent']:.4g} kW"
        )
    return stages, ratio, power


def spec(step: str, key: str) -> float:
    v = SIM[step][key]
    return float(v["value"]) if isinstance(v, dict) else float(v)


print("== section 1 (DESIGN.md D-063 (2)) MAC K-1101 and coolers E-1101 / E-1102 / E-1103 (wet air, S1 80 % RH, D-058)")
mac, _, mac_power = machine("K-1101", "S1", kpa("S2") + spec("K1101", "pressure_drop") * 100.0,
                            3, spec("K1101", "efficiency"), 313.15,
                            dp_cooler=spec("K1101", "pressure_drop") * 100.0, condense=True)
# the aftercooler's drop is counted inside `outlet`: S2 is the pressure after E-1103
q_mac = 0.0
for name, r in zip(("E-1101", "E-1102", "E-1103"), mac):
    q = r["sensible"] + r["latent"]
    q_mac += q
    cooler(f"{name} (sensible {r['sensible']:.4g} + latent {r['latent']:.4g} kW, "
           f"{r['condensed']:.4g} kg/h condensate)", q, r["t_out"], 313.15)
print(f"  coolers in all {q_mac:.5g} kW, condensate {sum(r['condensed'] for r in mac):.5g} kg/h; DWSIM "
      f"(D-058): Q1 6,686 kW, S1C {flow('S1C'):.6g} kg/h, compressor 5,968 kW")

print("== section 2 (DESIGN.md D-063 (5)) GOX compressor K-4101 and coolers E-4101 (4 intercoolers) / E-4102")
gox5, r5, p5 = machine("K-4101 (5 stages, datasheet)", "S7", kpa("S8"), 5,
                       spec("K4101", "efficiency"), 313.15)
ic = [cooler(f"E-4101 intercooler {r['stage']}", r["sensible"], r["t_out"], 313.15)
      for r in gox5[:-1]]
print(f"  E-4101 total: Q {sum(r['sensible'] for r in gox5[:-1]):.5g} kW, A {sum(ic):.5g} m2")
cooler("E-4102", gox5[-1]["sensible"], gox5[-1]["t_out"], 313.15)
gox4, _, p4 = machine("K-4101 (4 stages, process/simulation.yaml)", "S7", kpa("S8"), 4,
                      spec("K4101", "efficiency"), 313.15)
n7 = flow("S7") / molar_mass(fractions("S7")) / 3600.0
w_iso = n7 * R * kelvin("S7") * math.log(kpa("S8") / kpa("S7"))
print(f"  isothermal n R T ln(p2/p1) at the {kelvin('S7'):.5g} K suction: {w_iso:.5g} kW; isothermal "
      f"efficiency on DWSIM's 2,184 kW {w_iso / 2183.78:.3g}")
print(f"  cooling, 5 stages {sum(r['sensible'] for r in gox5):.5g} kW, 4 stages "
      f"{sum(r['sensible'] for r in gox4):.5g} kW; DWSIM (D-061): 4 stages, compressor 2,184 kW, "
      f"cooling 2,086 kW")

print("== section 3 (DESIGN.md D-063 (5)) GAN compressor K-4102 and aftercooler E-4103")
gan, _, _ = machine("K-4102", "S9", kpa("S9B"), 1, spec("K4102", "efficiency"), 313.15)
cooler("E-4103", gan[0]["sensible"], gan[0]["t_out"], 313.15)
print("  DWSIM (D-061): compressor 218.6 kW, cooling 123.4 kW")

print("== section 4 (DESIGN.md D-063 (4)) Booster K-3101, aftercooler E-3104, expander KT-3101 (compander, D-061)")
bst, _, w_b = machine("K-3101", "S4B", kpa("S4C"), 1, spec("K3101", "efficiency"), None)
q3104 = 83.95  # DWSIM, D-061: E3104 -83.9536 kW (`cheme process simulate`)
cooler(f"E-3104 (DWSIM duty, S4C {kelvin('S4C'):.5g} K -> S4D 313.15 K)", q3104, kelvin("S4C"), 313.15)
cooler("E-3104 (this script's booster discharge)", flow("S4B") / bst[0]["mw"] / 3600.0 * bst[0]["cp"]
       * (bst[0]["t_out"] - 313.15), bst[0]["t_out"], 313.15)
air = fractions("S5B")
mw_air = molar_mass(air)
m_air = flow("S5B") / 3600.0
ETA_M = 0.97  # D-053, ASSUMED, each machine's bearings
ETA_E = 0.85  # D-003, ASSUMED


def temperature_at(pressure: float, enthalpy: float, x: dict[str, float], lo: float, hi: float):
    """The temperature K of a single-phase state of molar *enthalpy* at *pressure* kPa(a)."""
    return brentq(lambda t: adapter.flash(Inputs(t, pressure, x)).enthalpy - enthalpy, lo, hi,
                  xtol=1e-6)


h_in = adapter.flash(Inputs(kelvin("S5B"), kpa("S5B"), air)).enthalpy
h_is = adapter.flash_ps(kpa("S6"), adapter.entropy(Inputs(kelvin("S5B"), kpa("S5B"), air)), air).enthalpy
h_ex = h_in - ETA_E * (h_in - h_is)
w_e = m_air / mw_air * (h_in - h_ex)
t_ex = temperature_at(kpa("S6"), h_ex, air, 90.0, 314.0)
print(
    f"  KT-3101: S5B {kelvin('S5B'):.5g} K {kpa('S5B'):.4g} kPa(a) -> {kpa('S6'):.4g} kPa(a), eta_s "
    f"{ETA_E}, real gas (property adapter): gas power {w_e:.5g} kW, exhaust {t_ex:.5g} K "
    f"({t_ex - 273.15:.4g} C, S6 {state('S6').temperature.value} C), shaft {w_e * ETA_M:.5g} kW"
)
print(
    f"  K-3101 DWSIM 185.9 kW gas (D-061), shaft {185.877 / ETA_M:.5g} kW; this script {w_b:.5g} kW "
    f"gas; shaft balance (DWSIM booster) {w_e * ETA_M - 185.877 / ETA_M:.3g} kW"
)


print("== section 5 (DESIGN.md D-063 (6)) Main heat exchanger E-3101 and subcooler E-3102: composite curves")


def _side(x: dict[str, float], n_kmol_s: float, t_in: float, t_out: float, p_in: float, p_out: float):
    def heat(t: float) -> float:
        f = (t - t_in) / (t_out - t_in)
        return n_kmol_s * adapter.flash(Inputs(t, p_in + (p_out - p_in) * f, x)).enthalpy

    return {"heat": heat, "lo": min(t_in, t_out), "hi": max(t_in, t_out), "t_in": t_in,
            "t_out": t_out}


def side(sid_in: str, sid_out: str, t_in: float | None = None, t_out: float | None = None,
         p_out: float | None = None):
    x = fractions(sid_in)
    n = flow(sid_in) / molar_mass(x) / 3600.0
    return _side(x, n, t_in if t_in is not None else kelvin(sid_in),
                 t_out if t_out is not None else kelvin(sid_out), kpa(sid_in),
                 p_out if p_out is not None else kpa(sid_out))


def total(sides) -> float:
    return sum(abs(s["heat"](s["t_out"]) - s["heat"](s["t_in"])) for s in sides)


def composite(sides, n: int = 250):
    lo, hi = min(s["lo"] for s in sides), max(s["hi"] for s in sides)
    ts = np.linspace(lo, hi, n)
    q = np.array([sum(abs(s["heat"](min(max(t, s["lo"]), s["hi"])) - s["heat"](s["lo"]))
                      for s in sides) for t in ts])
    return ts, q


def approach(warm, cold):
    tw, qw = composite(warm)
    tc, qc = composite(cold)
    q = np.linspace(0.0, min(qw[-1], qc[-1]), 600)  # from the warm end
    d = np.interp(qw[-1] - q, qw, tw) - np.interp(qc[-1] - q, qc, tc)
    ua = 0.0
    for k in range(len(q) - 1):
        if d[k] <= 0 or d[k + 1] <= 0:
            ua = float("nan")
            break
        lm = (d[k] - d[k + 1]) / math.log(d[k] / d[k + 1]) if abs(d[k] - d[k + 1]) > 1e-6 else d[k]
        ua += (q[k + 1] - q[k]) / lm
    i = int(np.argmin(d))
    return float(d.min()), float(q[i]), float(d[0]), float(d[-1]), ua


warm = [side("S4A", "S5"), side("S4D", "S5B")]
q_warm = total(warm)
for (a, b), s in zip((("S4A", "S5"), ("S4D", "S5B")), warm):
    print(f"  warm {a} -> {b}: {flow(a):g} kg/h, {s['t_in']:.5g} K {kpa(a):.4g} kPa(a) -> "
          f"{s['t_out']:.5g} K {kpa(b):.4g} kPa(a): {total([s]):.5g} kW")
print(f"  warm side {q_warm:.5g} kW")
# S14 and S15 enter as saturated vapour at their simulated pressures (D-061: the stored states flash
# as liquid within 0.1 K of the dew point); the waste N2 S16 is warmed first in E-3102.
dew14 = adapter.saturation_temperature(kpa("S14"), fractions("S14"), 1.0)
dew15 = adapter.saturation_temperature(kpa("S15"), fractions("S15"), 1.0)
cold_fixed = [side("S14", "S9", t_in=dew14 + 0.01), side("S15", "S7", t_in=dew15 + 0.01)]
for (a, b), s in zip((("S14", "S9"), ("S15", "S7")), cold_fixed):
    print(f"  cold {a} -> {b}: {flow(a):g} kg/h, saturated vapour at {kpa(a):.4g} kPa(a) (dew "
          f"{s['t_in']:.5g} K, property adapter) -> {s['t_out']:.5g} K {kpa(b):.4g} kPa(a): "
          f"{total([s]):.5g} kW")
q_fixed = total(cold_fixed)
t16 = kelvin("S16")
waste_full = side("S16", "S17")
print(f"  cold S16 -> S17 from the LP column top {t16:.5g} K: {total([waste_full]):.5g} kW; cold side "
      f"{q_fixed + total([waste_full]):.5g} kW, surplus over the warm side "
      f"{q_fixed + total([waste_full]) - q_warm:.4g} kW (heat leak neglected)")
t_x = brentq(lambda t: q_fixed + total([side("S16", "S17", t_in=t)]) - q_warm, t16 + 0.1, 140.0)
cold = cold_fixed + [side("S16", "S17", t_in=t_x)]
dmin, qat, dwarm, dcold, ua = approach(warm, cold)
q_3102 = total([_side(fractions("S16"), flow("S16") / molar_mass(fractions("S16")) / 3600.0, t16,
                      t_x, kpa("S16"), kpa("S16"))])
print(
    f"  balance closed by warming S16 in E-3102 to {t_x:.5g} K (no pressure drop, heat leak neglected; "
    f"ASSUMED): E-3102 waste N2 duty {q_3102:.5g} kW; E-3101 duty {total(cold):.5g} kW, minimum "
    f"approach {dmin:.3g} K at {qat:.4g} kW from the warm end, warm end {dwarm:.3g} K (booster air "
    f"{kelvin('S4D'):.5g} K against the {kelvin('S7'):.5g} K outlets: "
    f"{kelvin('S4D') - kelvin('S7'):.3g} K), cold end {dcold:.3g} K, UA = sum dQ / LMTD over 600 "
    f"intervals {ua:.4g} kW/K"
)
# E-3102: LN reflux S18 and crude S13 subcooled to a common outlet temperature (ASSUMED: one core,
# common cold-end header) against the waste N2 duty above
liquids = (("S18", "S18"), ("S13", "S13"))


def hot_sides(t_c: float):
    return [side(a, b, t_out=t_c, p_out=kpa(a)) for a, b in liquids]


t_c = brentq(lambda t: total(hot_sides(t)) - q_3102, t16 + 0.5, kelvin("S18") - 0.01)
hs = hot_sides(t_c)
for (a, _), s in zip(liquids, hs):
    print(f"  E-3102 hot {a}: {flow(a):g} kg/h liquid, {s['t_in']:.5g} -> {t_c:.5g} K at {kpa(a):.4g} "
          f"kPa(a): {total([s]):.5g} kW (subcooled {s['t_in'] - t_c:.3g} K)")
dmin2, qat2, dwarm2, dcold2, ua2 = approach(hs, [_side(fractions("S16"), flow("S16") / molar_mass(
    fractions("S16")) / 3600.0, t16, t_x, kpa("S16"), kpa("S16"))])
print(
    f"  E-3102 cold S16 {t16:.5g} -> {t_x:.5g} K: {q_3102:.5g} kW; minimum approach {dmin2:.3g} K at "
    f"{qat2:.4g} kW from the warm end, warm end {dwarm2:.3g} K, cold end {dcold2:.3g} K, UA "
    f"{ua2:.4g} kW/K"
)

print("== section 6 (DESIGN.md D-063 (7)) HP column C-3101 Fenske / Underwood (N2 / O2 keys, Ar a non-key; DWSIM states)")
z = dry(fractions("S5"))
xd, xb = fractions("S14"), fractions("S13")
t_top, k_top = adapter.k_values(kpa("S14"), xd, 1.0)
t_bot, k_bot = adapter.k_values(kpa("S13"), xb, 0.0)
alphas = {c: math.sqrt((k_top[c] / k_top["O2"]) * (k_bot[c] / k_bot["O2"])) for c in z}
res = shortcut.fug(alphas, z, xd, xb, 0.0, "N2", "O2")
print(
    f"  feed S5 {z}, q 0 (saturated vapour, ASSUMED); distillate S14 {xd} at {kpa('S14'):.4g} kPa(a) "
    f"(dew {t_top:.4g} K); bottoms S13 {xb} at {kpa('S13'):.4g} kPa(a) (bubble {t_bot:.4g} K); alpha "
    f"N2/O2 {alphas['N2']:.4g}, Ar/O2 {alphas['AR']:.4g} (geometric mean top/bottom, property "
    f"adapter); Nmin {res.min_stages:.4g}, theta {res.theta:.5g}, Rmin {res.min_reflux:.4g}; DWSIM "
    f"reflux ratio 1.338 = {1.33766 / res.min_reflux:.3g} x Rmin; {shortcut.SOURCES}"
)

print("== section 7 (DESIGN.md D-063 (7)) LP column C-3102 Fenske (minimum stages for the specification)")
top, bot = fractions("S16"), fractions("S15")
t_top, k_top = adapter.k_values(kpa("S16"), top, 1.0)
t_bot, k_bot = adapter.k_values(kpa("S15"), bot, 0.0)
for lk in ("N2", "AR"):
    a = math.sqrt((k_top[lk] / k_top["O2"]) * (k_bot[lk] / k_bot["O2"]))
    nmin = shortcut.fenske(top[lk], top["O2"], bot[lk], bot["O2"], a)
    print(
        f"  keys {lk}/O2: waste S16 {top} at {kpa('S16'):.4g} kPa(a) (dew {t_top:.4g} K), GOX S15 "
        f"{bot} (specification) at {kpa('S15'):.4g} kPa(a) (bubble {t_bot:.4g} K); alpha {a:.4g}; "
        f"Nmin {nmin:.4g}"
    )

print("== section 8 (DESIGN.md D-063 (3)) TSA V-2101A/B: water and CO2 load (S3 saturated at 12 C, IAPWS-95, D-058)")
x3 = fractions("S3")
n3 = flow("S3") / molar_mass(x3)
y_sat = iapws.iapws95_Psat(kelvin("S3")) / 1000.0 / kpa("S3")
n_other = n3 * (1.0 - x3["H2O"])
w_iapws = n_other * y_sat / (1.0 - y_sat) * M_H2O
w_pr = n3 * x3["H2O"] * M_H2O
co2 = n3 * x3["CO2"] * 44.0095
CYCLE_H = 4.0  # equipment list: about 4 h adsorption, ASSUMED
print(
    f"  S3 {flow('S3'):g} kg/h at {kelvin('S3'):.5g} K, {kpa('S3'):.4g} kPa(a): saturation y_H2O "
    f"{y_sat:.5f} (IAPWS-95) -> water {w_iapws:.4g} kg/h (flowsheet x_H2O {x3['H2O']:.5f}, PR: "
    f"{w_pr:.4g} kg/h); CO2 {co2:.4g} kg/h (x_CO2 {x3['CO2']:.3g}); per {CYCLE_H:g} h adsorption step: "
    f"water {w_iapws * CYCLE_H:.4g} kg, CO2 {co2 * CYCLE_H:.4g} kg"
)


def show_pump(duty: pumps.PumpDuty) -> None:
    print(f"  suction: {duty.suction.basis}\n  discharge: {duty.discharge.basis}")
    for key, text in duty.basis.items():
        if key != "differential_head_m":
            print(f"  {key}: {text}")
    print(
        f"  H {duty.differential_head_m:.4g} m (suction loss {duty.suction.head_loss_m:.4g} m, "
        f"discharge loss {duty.discharge.head_loss_m:.4g} m, end points {duty.suction.end} z "
        f"{duty.suction.elevation_end_m:.3f} / {duty.discharge.end} z "
        f"{duty.discharge.elevation_end_m:.3f}, pump nozzles z {duty.suction.elevation_pump_m:.3f}"
        f" / {duty.discharge.elevation_pump_m:.3f} m)"
    )


print("== D-053 (8), D-060 (5) LOX / LIN backup pumps: head to the GOX / GAN header through the")
print("   vaporizer and the backup control valve, NPSH available (chemeascode pumps.size_pump)")
# D-060 (5), ASSUMED until the vaporizer and valve suppliers' figures: the vaporizer outlet at the
# minimum ambient -5 C (process/design-basis.yaml site) less a 10 K approach; the vaporizer's
# pressure drop 50 kPa and the backup pressure control valve PV-4111 / PV-4112 100 kPa at rated
# flow; the header pressure at the tie-in is the product delivery pressure (S8 31 bara, S9B
# 9 bara, given).
T_VAP_OUT = 268.15 - 10.0
DP_VAPORIZER, DP_VALVE = 50.0, 100.0
PUMP_ETA = 0.5  # D-042, ASSUMED
vaporizer_duties: dict[str, tuple[float, str]] = {}
for tag, sid, mflow, rho, tank, vap, tie_in, header, cas, mw_gas in (
    ("P-4101A", "S10", 5200.0, 1141.0, "T-4101", "E-4105A", "P-04/Line_GOX4004_S4", 3100.0,
     "7782-44-7", 31.9988),
    ("P-4101B", "S10", 5200.0, 1141.0, "T-4101", "E-4105B", "P-04/Line_GOX4004_S4", 3100.0,
     "7782-44-7", 31.9988),
    ("P-4102A", "S11", 6300.0, 806.0, "T-4102", "E-4106A", "P-04/Line_GAN4003_S4", 900.0,
     "7727-37-9", 28.0134),
    ("P-4102B", "S11", 6300.0, 806.0, "T-4102", "E-4106B", "P-04/Line_GAN4003_S4", 900.0,
     "7727-37-9", 28.0134),
):
    x = fractions(sid)
    m = mflow / 3600.0
    t_sat = adapter.saturation_temperature(150.0, x, 0.0)
    mu, basis = adapter.liquid_viscosity(t_sat, x)
    gas = adapter.flash(Inputs(T_VAP_OUT, header + DP_VALVE, x))
    mu_gas = Yoon_Thodos(T_VAP_OUT, critical.Tc(cas), critical.Pc(cas), mw_gas)
    line = pumps.route_line(network, vap, f"pipe:{tie_in}:end", nozzle="N2", mass_flow_kg_s=m,
                            density_kg_m3=gas.density, viscosity_pa_s=mu_gas, what="discharge")
    p_vap_in = header + line.pressure_drop_kpa + DP_VALVE + DP_VAPORIZER
    print(f"{tag}: {mflow:g} kg/h, rho {rho:g} (D-042, NIST), saturated at 150 kPa(a) {t_sat:.4g} K, "
          f"mu {mu * 1000:.4g} mPa s ASSUMED ({basis})")
    print(
        f"  gas line {vap}/N2 -> {tie_in} end (the header tee): {gas.density:.4g} kg/m3 at "
        f"{T_VAP_OUT:.2f} K, {header + DP_VALVE:g} kPa(a) (property adapter), mu {mu_gas * 1e3:.4g}"
        f" mPa s (Yoon and Thodos, AIChE J. 16 (1970) 300, chemicals; Tc, Pc chemicals.critical),"
        f" loss {line.pressure_drop_kpa:.4g} kPa; {line.basis}"
    )
    print(
        f"  pressure at the {vap} inlet = header {header:g} + gas line {line.pressure_drop_kpa:.3g}"
        f" + control valve {DP_VALVE:g} + vaporizer {DP_VAPORIZER:g} kPa = {p_vap_in:.5g} kPa(a)"
    )
    duty = pumps.size_pump(
        network, tag, suction_from=tank, discharge_to=vap, mass_flow_kg_s=m, density_kg_m3=rho,
        viscosity_pa_s=mu, suction_pressure_kpa=150.0, discharge_pressure_kpa=p_vap_in,
        vapour_pressure_kpa=150.0, efficiency=PUMP_ETA, schedule="10S",
    )
    show_pump(duty)
    p_discharge = 150.0 + rho * 9.80665 * duty.differential_head_m / 1000.0
    print(f"  rated discharge pressure at the pump = 150 kPa(a) + rho g H = {p_discharge:.5g} kPa(a)"
          f" ({p_discharge / 100:.4g} bara)")
    # vaporizer duty: liquid at the tank (bubble point at 150 kPa(a)) plus the pump's shaft work
    # (an adiabatic pump puts all of it into the liquid) to gas at the outlet: every state is
    # single-phase and inside the property method's claimed range
    n = m / molar_mass(x)
    h_liq = adapter.flash(Inputs(t_sat - 0.01, 150.0, x)).enthalpy
    q = n * (gas.enthalpy - h_liq) - duty.shaft_power_kw
    vaporizer_duties[vap] = (q, f"{n * (gas.enthalpy - h_liq):.4g} - {duty.shaft_power_kw:.3g}")
    print(
        f"  {vap} duty = n (h_gas - h_liq) - pump shaft power = {m * 3600:g} kg/h / "
        f"{molar_mass(x):.4g} kg/kmol x ({gas.enthalpy:.6g} - ({h_liq:.6g})) kJ/kmol - "
        f"{duty.shaft_power_kw:.3g} kW = {q:.4g} kW (gas {T_VAP_OUT:.2f} K at "
        f"{header + DP_VALVE:g} kPa(a), liquid saturated at 150 kPa(a); property adapter)"
    )

print("== D-053 (9) DCAC cooling water pumps P-1101A/B and chilled water pumps P-1102A/B")
allowance = 100.0  # kPa, D-053: control valve + liquid distributor + strainer, ASSUMED
eta = 0.75  # D-053, ASSUMED
for tag, t, vflow, p_src, p_dst, src, dst in (
    ("P-1101A", 298.15, 250.0, 501.3, 580.0, "pipe:P-01/Line_CW1001_S1:start", "C-1101"),
    ("P-1101B", 298.15, 250.0, 501.3, 580.0, "pipe:P-01/Line_CW1001_S1:start", "C-1101"),
    ("P-1102A", 283.15, 100.0, 105.0, 570.0, "C-1102", "C-1101"),
    ("P-1102B", 283.15, 100.0, 105.0, 570.0, "C-1102", "C-1101"),
):
    rho = iapws.iapws95_rho(t, p_src * 1000.0)
    pv = iapws.iapws95_Psat(t) / 1000.0
    mu = mu_IAPWS(t, rho)
    m = vflow * rho / 3600.0
    print(f"{tag}: {vflow:g} m3/h water at {t - 273.15:g} C: rho {rho:.5g} kg/m3, p_vap {pv:.4g} "
          f"kPa(a), mu {mu * 1000:.4g} mPa s (IAPWS-95 / IAPWS 2008 viscosity, chemicals)")
    duty = pumps.size_pump(
        network, tag, suction_from=src, discharge_to=dst, mass_flow_kg_s=m, density_kg_m3=rho,
        viscosity_pa_s=mu, suction_pressure_kpa=p_src, discharge_pressure_kpa=p_dst,
        vapour_pressure_kpa=pv, efficiency=eta, allowance_kpa=allowance,
    )
    show_pump(duty)

print("== section 9 (DESIGN.md D-063 (3)) DCAC C-1101 and evaporative cooler C-1102: duty and hydraulic loads")
s2 = fractions("S2")
n_tot = flow("S2") / molar_mass(s2)
d2 = dry(s2)
n_dry = n_tot * (1.0 - s2["H2O"])
q_dry = n_dry * (adapter.flash(Inputs(kelvin("S2"), kpa("S2"), d2)).enthalpy
                 - adapter.flash(Inputs(kelvin("S3"), kpa("S3"), d2)).enthalpy) / 3600.0
y_out = iapws.iapws95_Psat(kelvin("S3")) / 1000.0 / kpa("S3")
n_w_in = n_tot * s2["H2O"]
n_w_out = n_dry * y_out / (1.0 - y_out)
cond = max(0.0, n_w_in - n_w_out)
q_vap = n_w_in * water_cp_molar(0.5 * (kelvin("S2") + kelvin("S3")), n_w_in / n_tot * kpa("S2")) \
    * (kelvin("S2") - kelvin("S3")) / 3600.0
q_cond = cond * M_H2O * latent_heat(kelvin("S3")) / 3600.0
print(
    f"  C-1101 duty: dry gas {n_dry:.6g} kmol/h {kelvin('S2'):.5g} K {kpa('S2'):.4g} kPa(a) -> "
    f"{kelvin('S3'):.5g} K {kpa('S3'):.4g} kPa(a) {q_dry:.4g} kW (property adapter); water vapour "
    f"{n_w_in:.4g} kmol/h (S2 x_H2O {s2['H2O']:.5f}, DWSIM) sensible {q_vap:.3g} kW; saturation at the "
    f"outlet y {y_out:.5f} (IAPWS-95): {cond * M_H2O:.4g} kg/h condense, {q_cond:.4g} kW (latent "
    f"{latent_heat(kelvin('S3')):.4g} kJ/kg at the outlet); total {q_dry + q_vap + q_cond:.5g} kW "
    f"(CO2 with the dry gas); DWSIM (D-058): Q2 1,201 kW, S3C {flow('S3C'):.4g} kg/h"
)
for tag, gflow, t, p, d, liquids_, xg in (
    ("C-1101 bottom", flow("S2"), kelvin("S2"), kpa("S2"), 4.0,
     (("lower section CW", 250.0), ("upper section chilled water", 100.0)), d2),
    ("C-1102", flow("S12B"), kelvin("S12B"), kpa("S12B"), 4.5, (("water", 100.0),),
     fractions("S12B")),
):
    rho_g = adapter.flash(Inputs(t, p, xg)).density
    area = math.pi / 4.0 * d * d
    u = gflow / 3600.0 / rho_g / area
    loads = ", ".join(f"{name} {q:g} m3/h: {q / area:.3g} m3/(m2 h)" for name, q in liquids_)
    print(
        f"  {tag}: gas {gflow:g} kg/h at {t:.2f} K, {p:g} kPa(a): rho {rho_g:.4g} kg/m3 (property "
        f"adapter, dry gas), D {d:g} m (equipment list), area {area:.4g} m2, u {u:.3g} m/s, "
        f"F = u rho^0.5 {u * rho_g ** 0.5:.3g} Pa^0.5; liquid loads {loads}"
    )
# lowest water temperature the dry waste N2 can reach: its adiabatic saturation temperature
# (energy balance, liquid fed at that temperature), the bound of an evaporative cooler
xn = fractions("S12B")
n_n2 = flow("S12B") / molar_mass(xn)
p12 = kpa("S12B")
h_n2_in = adapter.flash(Inputs(kelvin("S12B"), p12, xn)).enthalpy


def _as(t: float) -> float:
    psat = iapws.iapws95_Psat(t) / 1000.0
    y = psat / p12
    w = n_n2 * y / (1.0 - y) * M_H2O  # kg/h water taken up
    return n_n2 * (h_n2_in - adapter.flash(Inputs(t, p12, xn)).enthalpy) - w * latent_heat(t)


t_as = brentq(_as, 260.0, kelvin("S12B") - 0.01)
print(
    f"  C-1102: adiabatic saturation temperature of S12B (dry, {kelvin('S12B') - 273.15:.3g} C, "
    f"{p12:g} kPa(a)) {t_as - 273.15:.3g} C (energy balance N2 enthalpy, property adapter / water "
    f"IAPWS-95; Perry's 8th ed. Section 12, psychrometry): the 10 C chilled water lies "
    f"{283.15 - t_as:.3g} K above it"
)

print("== section 10 (DESIGN.md D-063 (8)) Cooling water and line velocities")
cw = {"MAC Q1 (DWSIM)": 6686.41, "DCAC Q2 (DWSIM)": 1201.42, "GOX compressor Q3 (DWSIM)": 2085.58,
      "GAN compressor Q4 (DWSIM)": 123.36, "E-3104 (DWSIM)": 83.95}
for name, q in cw.items():
    print(f"  {name}: {q:.6g} kW, {cw_flow(q):.4g} m3/h at 10 K")
print(f"  total {sum(cw.values()):.6g} kW, {cw_flow(sum(cw.values())):.4g} m3/h at 10 K")
for line, sid, dn in (("WN-1001", "S12B", 0.7), ("WN-3002", "S17", 0.9), ("GOX-4001", "S7", 0.5),
                      ("AIR-3002", "S4D", 0.2), ("AIR-3003", "S5B", 0.15)):
    rho = adapter.flash(Inputs(kelvin(sid), kpa(sid), fractions(sid))).density
    q = flow(sid) / rho / 3600.0
    print(f"  {line} ({sid} {kelvin(sid) - 273.15:.4g} C, {kpa(sid) / 100:.4g} bara): rho {rho:.4g} "
          f"kg/m3 (property adapter), {q:.4g} m3/s, {q / (math.pi / 4 * dn * dn):.3g} m/s in "
          f"{dn * 1000:g} mm (DN as the diameter, D-016)")
for key, (q, text) in vaporizer_duties.items():
    print(f"  (summary) {key} duty {q:.4g} kW ({text})")
