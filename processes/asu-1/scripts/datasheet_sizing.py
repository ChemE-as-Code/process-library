"""Hand sizing of the datasheet values `cheme datasheets fill` cannot reach (DESIGN.md D-053,
D-060, D-063).

Provenance only: it prints each value with its basis; the values are written into
equipment/datasheets/<TAG>.yaml by hand, with the source "scripts/datasheet_sizing.py section n
(DESIGN.md D-063 (m))": n is this script's section number printed in each "== section n" header,
m the numbered item of DESIGN.md D-063 that records it (they differ, D-065 (1)). Since D-068 the
sections rerun on the D-066 / D-067 states cite the item of D-068 that records them instead.
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

import hashlib
import json
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
# D-080 (2): the simulated unit results (powers, duties, reflux) are read from the run record that
# `cheme process simulate` writes, not typed in; the record must belong to the current process files
RUN = json.loads((ROOT / "process/simulation-run.json").read_text(encoding="utf-8"))["cases"]["design"]
_stale = [f for f, fp in RUN["inputs"]["fingerprints"].items()
          if fp != "sha256:" + hashlib.sha256((ROOT / f).read_bytes()).hexdigest()]
print(f"simulation run record: {RUN['simulator']['name']} {RUN['simulator']['version']}, {RUN['property_package']}, "
      f"run {RUN['run_at']} at {RUN['inputs']['commit'][:7]}; "
      + (f"STALE against {', '.join(_stale)}" if _stale else "current with process/*.yaml"))


def sim(unit: str, key: str) -> float:
    """A unit result of the simulation run record (process/simulation-run.json, case design)."""
    return float(next(u for u in RUN["units"] if u["id"] == unit)["results"][key])


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
    """Ideal-gas-like molar Cp of water vapour, kJ/(kmol K), IAPWS-95 at its partial pressure,
    held just below saturation (D-068 (1): a saturated suction rounded above Psat returned the
    liquid's Cp)."""
    p = min(max(p_partial_kpa, 0.05) * 1000.0, 0.999 * iapws.iapws95_Psat(t))
    return iapws.iapws95_properties(t, p)[5] / 1000.0 * M_H2O


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


def zoned_cooler(name: str, r: dict, t_out: float = 313.15, n: int = 400) -> dict:
    """Area of a condensing gas cooler by zones (D-065 (2)): desuperheating from the inlet to the
    dew point of the water at the cooler pressure, then condensing below it along the
    equilibrium cooling curve (the gas kept saturated, IAPWS-95 vapour pressure, as in the
    Silver / Bell-Ghaly approach), against counter-current cooling water 25 -> 35 C taking the
    same duty. Zone 1 by its LMTD and 1-2 F; zone 2 by the integrated mean temperature
    difference (sum dQ / dT over n intervals) and the 1-2 F of its terminal temperatures. The
    gas-cooler U of D-053 in both zones (ASSUMED; condensation raises the film coefficient, so
    this errs on the large side). The duty equals sensible + latent of `machine` (same Cp, latent
    heat at the outlet)."""
    n_mol, xw, p, cp, t_in = r["n_kmol_h"], r["x_w"], r["p_cool"], r["cp"], r["t_out"]
    n_w = n_mol * xw
    n_other = n_mol - n_w
    lam = latent_heat(t_out)

    def vapour(t: float) -> float:  # kmol/h of water left as vapour at t, saturated gas
        y = iapws.iapws95_Psat(t) / 1000.0 / p
        return min(n_w, n_other * y / (1.0 - y))

    def q_hot(t: float) -> float:  # kW given up by the air between t_in and t
        return n_mol / 3600.0 * cp * (t_in - t) + (n_w - vapour(t)) * M_H2O / 3600.0 * lam

    q_tot = q_hot(t_out)
    t_dew = brentq(lambda t: iapws.iapws95_Psat(t) / 1000.0 - xw * p, 274.0, 450.0)

    def t_cw(t: float) -> float:  # CW temperature opposite the air at t (CW out at the air inlet)
        return CW_OUT - (CW_OUT - CW_IN) * q_hot(t) / q_tot

    q1, t_mid = q_hot(t_dew), t_cw(t_dew)
    d1 = sizing.lmtd(t_in, t_dew, t_mid, CW_OUT, "1-2")
    f1 = sizing.correction_factor(t_in, t_dew, t_mid, CW_OUT, "1-2")
    a1 = sizing.exchanger_area(q1, U.value, f1, d1)
    ts = np.linspace(t_dew, t_out, n + 1)
    ua = 0.0
    for ta, tb in zip(ts[:-1], ts[1:]):
        dq = q_hot(tb) - q_hot(ta)
        dt = 0.5 * ((ta - t_cw(ta)) + (tb - t_cw(tb)))
        ua += dq / dt
    q2 = q_tot - q1
    d2 = q2 / ua
    f2 = sizing.correction_factor(t_dew, t_out, CW_IN, t_mid, "1-2")
    a2 = sizing.exchanger_area(q2, U.value, f2, d2)
    lat2 = (n_w - vapour(t_out)) * M_H2O / 3600.0 * lam
    area = a1 + a2
    print(
        f"  {name} by zones (D-065 (2)): water {xw:.4g} mol fraction at {p:.4g} kPa(a), dew point "
        f"{t_dew:.5g} K ({t_dew - 273.15:.4g} C, IAPWS-95)\n"
        f"    zone 1 desuperheating {t_in:.5g} -> {t_dew:.5g} K: Q {q1:.5g} kW, CW {t_mid:.5g} -> "
        f"{CW_OUT:.5g} K, LMTD {d1:.4g} K, F {f1:.4g}, A {a1:.4g} m2\n"
        f"    zone 2 condensing {t_dew:.5g} -> {t_out:.5g} K: Q {q2:.5g} kW (latent {lat2:.4g} kW, "
        f"{(n_w - vapour(t_out)) * M_H2O:.4g} kg/h), CW {CW_IN:.5g} -> {t_mid:.5g} K, integrated "
        f"mean dT {d2:.4g} K ({n} intervals), F {f2:.4g}, A {a2:.4g} m2\n"
        f"    total Q {q_tot:.5g} kW, A {area:.4g} m2 (U {U.value:g} W/(m2 K) in both zones), "
        f"effective mean dT Q / (U A) = {q_tot * 1000.0 / (U.value * area):.4g} K"
    )
    return {"t_dew": t_dew, "q1": q1, "q2": q2, "a1": a1, "a2": a2, "area": area, "d1": d1,
            "d2": d2, "f1": f1, "f2": f2, "t_mid": t_mid}


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
            # the cooler's wet-air state, for its zone sizing (D-065 (2))
            row.update(n_kmol_h=n_mol, x_w=x.get("H2O", 0.0), p_cool=p_c)
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


print("== section 1 (DESIGN.md D-068 (2)) MAC K-1101 and coolers E-1101 / E-1102 / E-1103 (wet air, S1 80 % RH, D-058, D-066)")
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
    if r["condensed"] > 0.0:  # the single-LMTD area above is not conservative here (review10#1)
        zoned_cooler(name, r)
print(f"  coolers in all {q_mac:.5g} kW, condensate {sum(r['condensed'] for r in mac):.5g} kg/h, gas power "
      f"{mac_power:.5g} kW; DWSIM (run record): Q1 {sim('K1101', 'cooling_kW'):.6g} kW, S1C {flow('S1C'):.6g} "
      f"kg/h, shaft {sim('K1101', 'shaft_kW'):.6g} kW, electric {sim('K1101', 'duty_kW'):.6g} kW")
# D-066: the motor. Electric power at the design point and at the ~90,000 Nm3/h rating (flow
# scaled, same pressure ratio), API 617 110 % of the rated power against the motor rating
n_dry_s1 = flow("S1") / molar_mass(fractions("S1")) * (1.0 - fractions("S1")["H2O"])
nm3_dry = n_dry_s1 * 22.414  # Nm3/h of dry air incl. CO2 at 0 C, 1.01325 bar
E1 = sim("K1101", "duty_kW")  # E1 = K1101 electric, the run record (D-079: S2 5.98 bara)
rated = E1 * 90000.0 / nm3_dry
print(f"  K-1101 rating: S1 dry air {nm3_dry:.6g} Nm3/h (22.414 Nm3/kmol); electric {E1:.6g} kW at the "
      f"design point, {rated:.5g} kW pro rata at 90,000 Nm3/h; motor output = electric x motor efficiency "
      f"0.97 (D-057): {rated * 0.97:.5g} kW; 110 % (API 617 driver margin) {rated * 0.97 * 1.1:.5g} kW "
      f"against the 9,000 kW motor (D-066): {9000.0 / (rated * 0.97 * 1.1) - 1.0:+.1%}")

print("== section 2 (DESIGN.md D-068 (3)) GOX compressor K-4101 and coolers E-4101 (4 intercoolers) / E-4102")
gox5, r5, p5 = machine("K-4101 (5 stages, datasheet)", "S7", kpa("S8"), 5,
                       spec("K4101", "efficiency"), 313.15)
ic = [cooler(f"E-4101 intercooler {r['stage']}", r["sensible"], r["t_out"], 313.15)
      for r in gox5[:-1]]
print(f"  E-4101 total: Q {sum(r['sensible'] for r in gox5[:-1]):.5g} kW, A {sum(ic):.5g} m2")
cooler("E-4102", gox5[-1]["sensible"], gox5[-1]["t_out"], 313.15)
n7 = flow("S7") / molar_mass(fractions("S7")) / 3600.0
w_iso = n7 * R * kelvin("S7") * math.log(kpa("S8") / kpa("S7"))
print(f"  isothermal n R T ln(p2/p1) at the {kelvin('S7'):.5g} K suction: {w_iso:.5g} kW; isothermal "
      f"efficiency on DWSIM's {sim('K4101', 'shaft_kW'):.5g} kW shaft {w_iso / sim('K4101', 'shaft_kW'):.3g}")
print(f"  cooling, 5 stages {sum(r['sensible'] for r in gox5):.5g} kW; DWSIM (run record, process/simulation.yaml "
      f"5 stages): shaft {sim('K4101', 'shaft_kW'):.5g} kW, electric {sim('K4101', 'duty_kW'):.5g} kW (E4), "
      f"cooling {sim('K4101', 'cooling_kW'):.5g} kW (Q3)")

print("== section 3 (DESIGN.md D-063 (5)) GAN compressor K-4102 and aftercooler E-4103")
gan, _, _ = machine("K-4102", "S9", kpa("S9B"), 1, spec("K4102", "efficiency"), 313.15)
cooler("E-4103", gan[0]["sensible"], gan[0]["t_out"], 313.15)
print(f"  DWSIM (run record): shaft {sim('K4102', 'shaft_kW'):.4g} kW, electric {sim('K4102', 'duty_kW'):.4g} kW, "
      f"cooling {sim('K4102', 'cooling_kW'):.4g} kW")


def counter_cooler(name: str, duty: float, hot_in: float, hot_out: float, c_in: float, c_out: float,
                   water: str) -> float:
    """Area of one counter-current gas cooler (D-067: the 1-2 shell crosses), U of D-053."""
    dt = sizing.lmtd(hot_in, hot_out, c_in, c_out, "counter-current")
    area = sizing.exchanger_area(duty, U.value, 1.0, dt)
    w = iapws.iapws95_properties(0.5 * (c_in + c_out), 4.5e5)
    m3h = duty / (w[5] / 1000.0 * (c_out - c_in)) / w[0] * 3600.0
    print(
        f"  {name}: Q {duty:.5g} kW, hot {hot_in:.5g} -> {hot_out:.5g} K, {water} {c_in:.5g} -> "
        f"{c_out:.5g} K counter-current, LMTD {dt:.4g} K, U {U.value:g} W/(m2 K) (middle of "
        f"{U.low:g}-{U.high:g}, {U.source}), A = Q / (U LMTD) = {area:.4g} m2; {water} {m3h:.4g} m3/h "
        f"(IAPWS-95 at the mean water temperature)"
    )
    return area


print("== section 4 (DESIGN.md D-068 (4)) Booster K-3101, aftercoolers E-3104 / E-3105, expander KT-3101 (compander, D-061, D-067)")
bst, _, w_b = machine("K-3101", "S4B", kpa("S4C"), 1, spec("K3101", "efficiency"), None)
q3104 = -sim("E3104", "duty_kW")  # DWSIM run record: E3104 (Q5, `cheme process simulate`)
q3105 = -sim("E3105", "duty_kW")  # DWSIM run record: E3105
counter_cooler(f"E-3104 (DWSIM duty Q5, S4C {kelvin('S4C'):.5g} K -> S4D {kelvin('S4D'):.5g} K)", q3104,
               kelvin("S4C"), kelvin("S4D"), CW_IN, CW_OUT, "CW")
CHW_IN, CHW_OUT_3105 = 283.15, 293.15  # D-067: chilled water 10 -> 20 C (ASSUMED)
counter_cooler(f"E-3105 (DWSIM duty, S4D {kelvin('S4D'):.5g} K -> S4E {kelvin('S4E'):.5g} K)", q3105,
               kelvin("S4D"), kelvin("S4E"), CHW_IN, CHW_OUT_3105, "chilled water")
h_d = h("S4D")
for t_trim in (291.65,):  # D-067: minimum acceptable trim outlet 18.5 C
    q_min = flow("S4D") / molar_mass(fractions("S4D")) / 3600.0 * (h_d - h("S4D", t=t_trim))
    print(f"  E-3105 at the 18.5 C alarm (D-067): Q {q_min:.4g} kW (property adapter)")
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
    f"  K-3101 DWSIM {sim('K3101', 'duty_kW'):.4g} kW gas (run record), shaft {sim('K3101', 'duty_kW') / ETA_M:.5g} "
    f"kW; this script {w_b:.5g} kW gas; shaft balance (DWSIM booster) "
    f"{w_e * ETA_M - sim('K3101', 'duty_kW') / ETA_M:.3g} kW"
)


print("== section 5 (DESIGN.md D-068 (5)) Main heat exchanger E-3101 and subcooler E-3102: composite curves")


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


warm = [side("S4A", "S5"), side("S4E", "S5B")]
q_warm = total(warm)
for (a, b), s in zip((("S4A", "S5"), ("S4E", "S5B")), warm):
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
# D-066: E-3102 is simulated: the waste N2 enters E-3101 as S16B (no longer closed here)
waste = side("S16B", "S17")
q_cold = q_fixed + total([waste])
print(f"  cold S16B -> S17 from the E-3102 outlet {kelvin('S16B'):.5g} K (DWSIM, D-066): "
      f"{total([waste]):.5g} kW; cold side {q_cold:.5g} kW, warm side {q_warm:.5g} kW: the cold side "
      f"can take {q_cold - q_warm:.4g} kW more (the margin for the heat leak into E-3101 and the warm-end "
      f"approach; D-067 closes the whole cold box at a 75.2 kW leak)")
dmin, qat, dwarm, dcold, ua = approach(warm, cold_fixed + [waste])
print(
    f"  E-3101 duty {q_warm:.5g} kW (warm side), minimum approach {dmin:.3g} K at {qat:.4g} kW from "
    f"the warm end, warm end {dwarm:.3g} K (booster air S4E {kelvin('S4E'):.5g} K / main air "
    f"{kelvin('S4A'):.5g} K against the {kelvin('S7'):.5g} K outlets), cold end {dcold:.3g} K, UA = "
    f"sum dQ / LMTD over 600 intervals (curves paired from the warm end) {ua:.4g} kW/K"
)
# E-3102 on the simulated states (D-066): LN S18 -> S18B, crude S13 -> S13B against S16 -> S16B
hs = [side("S18", "S18B"), side("S13", "S13B")]
for (a, b), s in zip((("S18", "S18B"), ("S13", "S13B")), hs):
    print(f"  E-3102 hot {a} -> {b}: {flow(a):g} kg/h liquid, {s['t_in']:.5g} -> {s['t_out']:.5g} K at "
          f"{kpa(a):.4g} kPa(a): {total([s]):.5g} kW (subcooled {s['t_in'] - s['t_out']:.3g} K)")
c3102 = side("S16", "S16B")
dmin2, qat2, dwarm2, dcold2, ua2 = approach(hs, [c3102])
print(
    f"  E-3102 cold S16 {t16:.5g} -> S16B {kelvin('S16B'):.5g} K: {total([c3102]):.5g} kW (DWSIM "
    f"{sim('E3102', 'duty_kW'):.5g} kW); hot side {total(hs):.5g} kW; minimum approach {dmin2:.3g} K at {qat2:.4g} kW from the warm "
    f"end, warm end {dwarm2:.3g} K, cold end {dcold2:.3g} K, UA {ua2:.4g} kW/K"
)

print("== section 6 (DESIGN.md D-068 (6)) HP column C-3101 Fenske / Underwood (N2 / O2 keys, Ar a non-key; DWSIM states)")
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
    f"reflux ratio {sim('C3101', 'reflux_ratio'):.4g} (run record) = "
    f"{sim('C3101', 'reflux_ratio') / res.min_reflux:.3g} x Rmin; {shortcut.SOURCES}"
)

print("== section 7 (DESIGN.md D-068 (6)) LP column C-3102 Fenske (minimum stages for the specification)")
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

print("== section 8 (DESIGN.md D-068 (7)) TSA V-2101A/B: water and CO2 load (S3 saturated at 12 C, IAPWS-95, D-058), E-2101, F-1101")
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
# D-066: regeneration gas S12A 18,486 kg/h heated from the warm-end 13 C (S17) to 200 C (S12H)
x12 = fractions("S12A")
n12 = flow("S12A") / molar_mass(x12) / 3600.0
# 200 C is above the property adapter's claimed range: ideal-gas Cp of thermo (the props extra)
from thermo import HeatCapacityGas  # noqa: E402

CAS = {"N2": "7727-37-9", "O2": "7782-44-7", "AR": "7440-37-1"}
q_heat = n12 * sum(v * HeatCapacityGas(CASRN=CAS[k]).T_dependent_property_integral(
    kelvin("S17"), 473.15) for k, v in x12.items())  # kmol/s x J/mol = kW
print(f"  E-2101: S12A {flow('S12A'):g} kg/h {kelvin('S17') - 273.15:.3g} -> 200 C: gas duty {q_heat:.5g} "
      f"kW (ideal-gas Cp, thermo HeatCapacityGas, mole-fraction mixing; the property adapter claims "
      f"77-315 K only); D-066 gives 1.13 MW peak; cycle average E3 377 kW (flowsheet, ASSUMED)")
# F-1101: intake air at 30 C, 1.01 bara (S1 wet), actual volume
rho1 = adapter.flash(Inputs(kelvin("S1"), kpa("S1"), dry(fractions("S1")))).density
print(f"  F-1101 / AIR-1001: S1 {flow('S1'):g} kg/h at {kelvin('S1') - 273.15:.3g} C, {kpa('S1'):g} kPa(a) "
      f"(dry-air density {rho1:.4g} kg/m3, property adapter): {flow('S1') / rho1:.6g} m3/h actual, "
      f"{flow('S1') / rho1 / 3600 / (math.pi / 4 * 1.4 ** 2):.3g} m/s in DN1400")


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

print("== section 12 (DESIGN.md D-068 (8)) Chilled-water loop of C-1102 (D-067): flows, return, evaporation")
CHW_SUPPLY = 283.15  # D-005 / D-067: chilled water 10 C, ASSUMED
T_RET_DCAC = 299.15  # D-067: the DCAC upper section returns its water at about 26 C, ASSUMED
Q_DCAC_U = -sim("C1101U", "duty_kW")  # DWSIM run record: C1101U (upper section)
w_mid = iapws.iapws95_properties(0.5 * (CHW_SUPPLY + T_RET_DCAC), 5.0e5)
m_dcac = Q_DCAC_U / (w_mid[5] / 1000.0 * (T_RET_DCAC - CHW_SUPPLY))  # kg/s
w_3105 = iapws.iapws95_properties(0.5 * (CHW_SUPPLY + CHW_OUT_3105), 5.0e5)
m_3105 = q3105 / (w_3105[5] / 1000.0 * (CHW_OUT_3105 - CHW_SUPPLY))
rho10 = iapws.iapws95_rho(CHW_SUPPLY, 5.0e5)
v_dcac, v_3105 = m_dcac * 3600 / rho10, m_3105 * 3600 / rho10
cond_u = flow("S3CU")  # kg/h condensed in the upper section into the chilled water (DWSIM)
t_mix = (m_dcac * T_RET_DCAC + m_3105 * CHW_OUT_3105) / (m_dcac + m_3105)
q_chw = Q_DCAC_U + q3105
print(
    f"  DCAC upper section {Q_DCAC_U:.5g} kW, chilled water {CHW_SUPPLY - 273.15:g} -> "
    f"{T_RET_DCAC - 273.15:g} C: {m_dcac:.4g} kg/s = {v_dcac:.4g} m3/h (+ its condensate S3CU {cond_u:.4g} "
    f"kg/h); E-3105 {q3105:.4g} kW, 10 -> 20 C: {v_3105:.4g} m3/h; loop {v_dcac + v_3105:.4g} m3/h, "
    f"{q_chw:.5g} kW; mixed return to C-1102 {t_mix - 273.15:.3g} C (IAPWS-95 cp at the mean "
    f"temperatures)"
)
xn = fractions("S12B")
n_n2 = flow("S12B") / molar_mass(xn)
p12 = kpa("S12B")
h_n2_in = adapter.flash(Inputs(kelvin("S12B"), p12, xn)).enthalpy


def water_taken(t: float) -> float:
    """kg/h of water the dry waste N2 holds when it leaves saturated at t K (IAPWS-95)."""
    y = iapws.iapws95_Psat(t) / 1000.0 / p12
    return n_n2 * y / (1.0 - y) * M_H2O


def gas_duty(t: float) -> float:
    """kW the waste N2 takes up leaving saturated at t K: sensible (property adapter) + latent."""
    return (n_n2 * (adapter.flash(Inputs(t, p12, xn)).enthalpy - h_n2_in) / 3600.0
            + water_taken(t) / 3600.0 * latent_heat(t))


for q_case, label in ((q_chw, "the design demand"), (1000.0, "D-067's ~1,000 kW capability")):
    t_g = brentq(lambda t: gas_duty(t) - q_case, kelvin("S12B") + 0.01, 314.0)
    w = water_taken(t_g)
    if q_case == q_chw:
        W_EVAP = w  # the design-duty evaporation, into the WN-1002 vent (section 11)
    print(
        f"  C-1102 at {label} {q_case:.5g} kW: S12B {flow('S12B'):g} kg/h dry at "
        f"{kelvin('S12B') - 273.15:.3g} C leaves saturated at {t_g - 273.15:.3g} C (energy balance: "
        f"N2 sensible, property adapter, + latent, IAPWS-95); water evaporated {w:.5g} kg/h; make-up "
        f"= evaporation - upper-section condensate {cond_u:.4g} kg/h = {w - cond_u:.5g} kg/h (blowdown "
        f"not included)"
    )

print("== D-053 (9), D-068 (8) DCAC cooling water pumps P-1101A/B and chilled water pumps P-1102A/B")
allowance = 100.0  # kPa, D-053: control valve + liquid distributor + strainer, ASSUMED
eta = 0.75  # D-053, ASSUMED
V_P1102 = 44.0  # the selected rating (D-068 (8), D-069): 110 % of the D-067 loop, kept (D-080 (2))
print(f"  P-1102A/B rated flow {V_P1102:g} m3/h (selected, D-069) = {V_P1102 / (v_dcac + v_3105):.1%} of the "
      f"{v_dcac + v_3105:.4g} m3/h loop (110 % ASSUMED margin as the minimum)")
# D-080 (2): the pumps discharge into the DCAC at the column's gas pressure: the lower section at S2,
# the upper section at S3 (D-079: 5.98 / 5.88 bara; was 5.8 / 5.7)
for tag, t, vflow, p_src, p_dst, src, dst in (
    ("P-1101A", 298.15, 250.0, 501.3, kpa("S2"), "pipe:P-01/Line_CW1001_S1:start", "C-1101"),
    ("P-1101B", 298.15, 250.0, 501.3, kpa("S2"), "pipe:P-01/Line_CW1001_S1:start", "C-1101"),
    ("P-1102A", 283.15, V_P1102, 105.0, kpa("S3"), "C-1102", "C-1101"),
    ("P-1102B", 283.15, V_P1102, 105.0, kpa("S3"), "C-1102", "C-1101"),
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

# D-076 (review11#4 (a)): air blow-by through the chimney-tray draw-off when the seal is lost, the bound
# of the C-1102 relief case: choked ideal-gas flow of S3 air (dry, 12 C, 5.88 bara since D-079) through the full DN150
# bore (ID 154.1 mm, schedule 40, ASSUMED; discharge coefficient 1, an upper bound)
k_air = 1.4
m_air = molar_mass(dry(fractions("S3")))
g_choked = kpa("S3") * 1000.0 * math.sqrt(k_air * m_air / 1000.0 / (8.314 * kelvin("S3"))) * (
    2.0 / (k_air + 1.0)) ** ((k_air + 1.0) / (2.0 * (k_air - 1.0)))
a150 = math.pi / 4 * 0.1541 ** 2
print(f"  CHWR-1001 blow-by bound (D-076): choked air {g_choked:.4g} kg/(m2 s) x {a150:.4g} m2 = "
      f"{g_choked * a150 * 3.6:.3g} t/h (Cd 1), against the {flow('S12B') / 1000:.3g} t/h design gas of C-1102")
# D-088 (4) (layout-review13#4): the I-03 SIF (LSLL-1115 -> XV-1115) timing. Chimney tray geometry of the
# C-1101 datasheet (D-086, ASSUMED): floor 13.0 m, chimney tops 13.8 m, N7 (DN150) draws off at the floor.
# ASSUMED for the SRS, all for HAZOP / LOPA / SRS confirmation and the packing and valve suppliers:
# N7 bore bottom flush with the floor, its top at 13.0 + 0.1541 m; seal loss (gas drawn into N7) taken
# at the bore top + 0.05 m vortex allowance with a vortex breaker in N7; LSLL-1115 trip at 13.35 m;
# LIC-1114 set point 13.50 m; chimney risers 25 % of the tray area; LV-1114 failed fully open passes at
# most twice the normal draw-off (a rating requirement on its trim); the inflow stays at normal
TRAY_FLOOR, Z_TRIP, Z_SP = 13.0, 13.35, 13.50
z_seal = TRAY_FLOOR + 0.1541 + 0.05
a_liq = math.pi / 4.0 * 4.0 ** 2 * (1.0 - 0.25)  # C-1101 D 4.0 m (equipment list)
rho26 = iapws.iapws95_rho(T_RET_DCAC, kpa("S3") * 1000.0)
q_in = (m_dcac * 3600.0 + cond_u) / rho26  # m3/h onto the tray: chilled water + upper-section condensate
q_open = 2.0 * q_in
pst = (Z_TRIP - z_seal) * a_liq / (q_open - q_in) * 3600.0
t_to_trip = (Z_SP - Z_TRIP) * a_liq / (q_open - q_in) * 3600.0
print(f"  I-03 SIF timing (D-088 (4)): tray liquid area {a_liq:.4g} m2, inflow {q_in:.4g} m3/h (IAPWS-95 at "
      f"{T_RET_DCAC - 273.15:g} C), LV-1114 full open {q_open:.4g} m3/h: net {q_open - q_in:.4g} m3/h; set point "
      f"{Z_SP:g} m -> trip {Z_TRIP:g} m: {(Z_SP - Z_TRIP) * a_liq:.3g} m3, {t_to_trip:.0f} s; trip -> seal loss "
      f"{z_seal:.3g} m: {(Z_TRIP - z_seal) * a_liq:.3g} m3, process safety time {pst:.0f} s; with the inflow "
      f"also lost (2 x net) {pst / 2:.0f} s")

print("== section 9 (DESIGN.md D-068 (8)) DCAC C-1101 (two sections, D-067) and evaporative cooler C-1102: duty and hydraulic loads")
s2 = fractions("S2")
d2 = dry(s2)


def dcac_section(name: str, sin: str, sout: str, dwsim_kw: float, dwsim_cond: float) -> None:
    x = fractions(sin)
    n_tot = flow(sin) / molar_mass(x)
    n_dry = n_tot * (1.0 - x["H2O"])
    q_dry = n_dry * (adapter.flash(Inputs(kelvin(sin), kpa(sin), dry(x))).enthalpy
                     - adapter.flash(Inputs(kelvin(sout), kpa(sout), dry(x))).enthalpy) / 3600.0
    y_out = iapws.iapws95_Psat(kelvin(sout)) / 1000.0 / kpa(sout)
    n_w_in = n_tot * x["H2O"]
    n_w_out = n_dry * y_out / (1.0 - y_out)
    cond = max(0.0, n_w_in - n_w_out)
    q_vap = n_w_in * water_cp_molar(0.5 * (kelvin(sin) + kelvin(sout)), n_w_in / n_tot * kpa(sin)) \
        * (kelvin(sin) - kelvin(sout)) / 3600.0
    q_cond = cond * M_H2O * latent_heat(kelvin(sout)) / 3600.0
    print(
        f"  {name} {sin} -> {sout}: dry gas {n_dry:.6g} kmol/h {kelvin(sin):.5g} K {kpa(sin):.4g} kPa(a) "
        f"-> {kelvin(sout):.5g} K {kpa(sout):.4g} kPa(a) {q_dry:.4g} kW (property adapter); water vapour "
        f"sensible {q_vap:.3g} kW; outlet saturated y {y_out:.5f} (IAPWS-95): {cond * M_H2O:.4g} kg/h "
        f"condense, {q_cond:.4g} kW; total {q_dry + q_vap + q_cond:.5g} kW; DWSIM (run record) "
        f"{dwsim_kw:.5g} kW, condensate {dwsim_cond:.4g} kg/h"
    )


dcac_section("C-1101 lower (cooling water)", "S2", "S3L", -sim("C1101", "duty_kW"), flow("S3C"))
dcac_section("C-1101 upper (chilled water)", "S3L", "S3", -sim("C1101U", "duty_kW"), flow("S3CU"))
for tag, gflow, t, p, d, liquids_, xg in (
    ("C-1101 bottom", flow("S2"), kelvin("S2"), kpa("S2"), 4.0,
     (("lower section CW", 250.0), ("upper section chilled water", round(v_dcac, 1))), d2),
    ("C-1102", flow("S12B"), kelvin("S12B"), kpa("S12B"), 4.5,
     (("water", round(v_dcac + v_3105, 1)),), fractions("S12B")),
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

print("== section 11 (DESIGN.md D-071 (2), D-072) Waste-N2 and regeneration-gas path hydraulics along the routed lines (LP top pressure check)")
import re as _re  # noqa: E402

from chemeascode.domains.process import hydraulics as hy  # noqa: E402

xw = fractions("S17")
# Yoon-Thodos for the waste N2 (93.6 % N2) taken as nitrogen: the O2 / Ar fractions change it < 2 %
MU_WN = Yoon_Thodos(286.15, critical.Tc("7727-37-9"), critical.Pc("7727-37-9"), 28.0134)
ROUGH = 4.6e-5  # commercial steel, Moody (1944), as the routed-line method (ASSUMED)


def rho_wn(p_kpa: float) -> float:
    return adapter.flash(Inputs(286.15, p_kpa, xw)).density


# cheme's wall table ends at DN 600: the large waste-N2 lines take the ASME B36.10M outside
# diameter of their NPS and the standard wall 9.53 mm (ASSUMED, outside cheme's table)
OD_LARGE = {600: 0.6096, 700: 0.7112, 800: 0.8128, 900: 0.9144, 1000: 1.016}
K_ELBOW = hy.fitting_k("elbow_90").value
MODEL = yaml.safe_load((ROOT / "layout/plant-model.yaml").read_text(encoding="utf-8"))
PIPES = {p["id"]: p for p in MODEL.get("pipes", []) if isinstance(p, dict) and "id" in p}


def route_of(pipe_ids, jog: float = 0.3, joins: bool = False):
    """Length m and 90 deg bends of the routed pipes (layout/plant-model.yaml). By default jogs
    under 0.3 m are not counted as bends (ASSUMED) nor the turns where one pipe of the path meets
    the next; jog=0, joins=True counts every change of direction (D-080 (1), the bound)."""
    length, bends, prev = 0.0, 0, None
    for pid in pipe_ids:
        pts = np.array(PIPES[pid]["points"], dtype=float)
        seg = np.diff(pts, axis=0)
        lens = np.linalg.norm(seg, axis=1)
        keep = seg[lens > max(jog, 1e-6)]
        length += float(lens.sum())
        if joins and prev is not None and len(keep) and abs(float(np.dot(prev, keep[0]))) < 1e-9:
            bends += 1
        bends += sum(1 for a, b in zip(keep[:-1], keep[1:]) if abs(float(np.dot(a, b))) < 1e-9)
        prev = keep[-1] if len(keep) else prev
    return length, bends


def darcy(m_kg_h: float, p_kpa: float, dn: int, length: float, k: float) -> tuple[float, float]:
    """kPa and m/s: Darcy-Weisbach, Colebrook friction factor (cheme hydraulics), ID = OD - 2 x
    9.53 mm, commercial steel roughness."""
    d = OD_LARGE[dn] - 2 * 0.00953
    seg = hy.Segment(length, d, ROUGH, {"fittings": k})
    loss = hy.line_loss(m_kg_h / 3600.0, rho_wn(p_kpa), MU_WN, [seg])
    return loss.pressure_drop, loss.segments[0].velocity


m17, m12b = flow("S17"), flow("S12B")
print(f"  waste N2 at 13 C: rho {rho_wn(112.0):.4g} kg/m3 at 112 kPa(a) (property adapter), mu "
      f"{MU_WN * 1e6:.4g} uPa s (Yoon-Thodos, nitrogen); elbows K {K_ELBOW} each, tee K 0.4 run / 1.0 "
      f"branch (Perry's Table 6-4); control valves PV-3110A/B and the C-1102 internals not in the "
      f"line loss")
L3002, B3002 = route_of(["P-03/Line_WN3002_S1", "P-03/Line_WN3002_S2"])
dp3002, v3002 = darcy(m17, 112.0, 900, L3002, B3002 * K_ELBOW + 0.4)
print(f"  WN-3002 DN900 E-3101/N3 -> WN-1001 tee: {L3002:.4g} m, {B3002} bends, {m17:g} kg/h: "
      f"{dp3002:.3g} kPa ({v3002:.3g} m/s)")
L1001, B1001 = route_of(["P-03/Line_WN1001_S1", "P-01/Line_WN1001_S1"])
for dn in (700, 900, 1000):
    dp, v = darcy(m12b, 107.0, dn, L1001, B1001 * K_ELBOW + 1.0 + 1.0)  # tee branch + entry
    print(f"  WN-1001 DN{dn} tee -> C-1102/N1: {L1001:.4g} m, {B1001} bends, {m12b:g} kg/h: {dp:.3g} "
          f"kPa ({v:.3g} m/s; K: bends + tee branch 1.0 + nozzle entry 1.0)")
L1002, B1002 = route_of(["P-01/Line_WN1002_S1"])
for dn in (700, 900):
    dp1002, v1002 = darcy(m12b + W_EVAP, 102.0, dn, L1002, B1002 * K_ELBOW + 0.5 + 1.0)
    print(f"  WN-1002 DN{dn} C-1102 top vent: {L1002:.4g} m, {m12b + W_EVAP:.6g} kg/h wet (dry-gas "
          f"density, ASSUMED): {dp1002:.3g} kPa ({v1002:.3g} m/s; K: entry 0.5 + exit 1.0)")
# the cold waste N2 inside the cold box (WN-3001, DN800): density at the mean of S16 / S16B
L3001, B3001 = route_of(["P-03/Line_WN3001_S1", "P-03/Line_WN3001_S2"])
t_cold = 0.5 * (kelvin("S16") + kelvin("S16B"))
rho_c = adapter.flash(Inputs(t_cold + 2.0, 130.0, fractions("S16"))).density
mu_c = Yoon_Thodos(t_cold, critical.Tc("7727-37-9"), critical.Pc("7727-37-9"), 28.0134)
seg_c = hy.Segment(L3001, OD_LARGE[800] - 2 * 0.00953, ROUGH, {"fittings": B3001 * K_ELBOW})
lc = hy.line_loss(flow("S16") / 3600.0, rho_c, mu_c, [seg_c])
print(f"  WN-3001 DN800 (cold, both segments, about {t_cold:.4g} K, rho {rho_c:.4g} kg/m3): {L3001:.4g} m, "
      f"{B3001} bends, {flow('S16'):g} kg/h: {lc.pressure_drop:.3g} kPa ({lc.segments[0].velocity:.3g} m/s)")
L3003, B3003 = route_of(["P-03/Line_WN3003_S1"])
for dn in (600, 800, 900):
    dp, v = darcy(m12b, 108.0, dn, L3003, B3003 * K_ELBOW + 0.4 + 1.0)
    print(f"  bypass WN-3003 DN{dn} to S-3101: {L3003:.4g} m, {B3003} bends, {m12b:g} kg/h (all of "
          f"S12B, D-067): {dp:.3g} kPa ({v:.3g} m/s); silencer S-3101 and PV-3110B extra")
dp3002b, _ = darcy(m17, 112.0, 900, L3002, B3002 * K_ELBOW + 0.4)
print(f"  (in bypass WN-3002 still carries {m17:g} kg/h: {dp3002b:.3g} kPa)")
# D-083: the C-1102 relief case. The CHWR-1001 blow-by bound (choked S3 air through the full DN150 bore,
# Cd 1, above) enters the C-1102 top with the design gas and its evaporated water; all of it leaves by
# the open vent WN-1002 (DN900, no valve). Line loss as WN-1002 above (entry K 0.5, exit 1.0), the gas
# taken as the waste-N2 density at 13 C (lower than air's: more loss, conservative). The column's own
# internals are screened by its 3.3 kPa allowable at the design gas (datasheet, D-071) scaled with the
# square of the total flow, as if all of it crossed the packing (it does not: the blow-by enters at the
# distributor above the packing; ASSUMED bound)
m_blow = g_choked * a150 * 3600.0
m_relief = m12b + W_EVAP + m_blow
dp_vent, v_vent = darcy(m_relief, 102.0, 900, L1002, B1002 * K_ELBOW + 0.5 + 1.0)
dp_int = 3.3 * (m_relief / (m12b + W_EVAP)) ** 2
print(f"  C-1102 blow-by relief (D-083): {m12b:g} + {W_EVAP:.4g} + {m_blow:.6g} = {m_relief:.6g} kg/h out of WN-1002 "
      f"DN900: {dp_vent:.3g} kPa ({v_vent:.3g} m/s) + internals bound {dp_int:.3g} kPa = {dp_vent + dp_int:.3g} kPa(g) "
      f"at the C-1102 top against its 1 barg design (equipment list): {100.0 / (dp_vent + dp_int):.2g} x margin")

# D-072 (review11#1): the regeneration gas S12A takes the other branch of the WN-3002 tee and goes
# to the atmosphere through RG-2001 (FV-2105), E-2101, RG-2002, the bed in regeneration with its
# switching valves XV-2103A/B and XV-2104A/B, RG-2003 and S-2101. Its line losses come out of the
# same 115 kPa(a) at the E-3101 warm end (S17, ASSUMED) as the C-1102 path.
OD_LARGE[500] = 0.508  # ASME B36.10M NPS 20


def gas_line(m_kg_h: float, rho: float, mu: float, dn: int, length: float, k: float) -> tuple[float, float]:
    """kPa and m/s for a gas of given density and viscosity (as darcy())."""
    seg = hy.Segment(length, OD_LARGE[dn] - 2 * 0.00953, ROUGH, {"fittings": k})
    loss = hy.line_loss(m_kg_h / 3600.0, rho, mu, [seg])
    return loss.pressure_drop, loss.segments[0].velocity


def ideal_rho(t: float, p_kpa: float, x: dict[str, float]) -> float:
    """Ideal-gas density kg/m3: 200 C lies above the property adapter's range (D-068 (7))."""
    return p_kpa * molar_mass(x) / (R * t)


T_HOT = 473.15  # S12H 200 C (flowsheet, ASSUMED); the bed outlet is taken at 200 C too, its value at
# the end of the heating step, the largest volume flow (ASSUMED bound: it starts near 13 C)
m12a, m12d = flow("S12A"), flow("S12D")
x12d = fractions("S12D")
mu_n2 = lambda t: Yoon_Thodos(t, critical.Tc("7727-37-9"), critical.Pc("7727-37-9"), 28.0134)  # noqa: E731
p_tee = kpa("S17") - dp3002
print(f"  regeneration path (D-072): S12A {m12a:g} kg/h, S12D {m12d:g} kg/h out of the bed (water and CO2 "
      f"desorbed); WN-3002 tee at {kpa('S17'):g} - {dp3002:.3g} = {p_tee:.4g} kPa(a); hot gas ideal-gas "
      f"density (M {molar_mass(xw):.4g} / {molar_mass(x12d):.4g}), Yoon-Thodos viscosity (nitrogen)")
rg_paths = {
    "bed A": (["P-03/Line_RG2001_S1", "P-02/Line_RG2001_S1", "P-02/Line_RG2001_S2"],
              ["P-02/Line_RG2002_S1", "P-02/Line_RG2002_S2", "P-02/Line_RG2002_S3"],
              ["P-02/Line_RG2003_S1", "P-02/Line_RG2003_S2", "P-02/Line_RG2003_S3", "P-02/Line_RG2003_S9"],
              # tees: RG-2002 J run + RG-2002 branch; RG-2003 A1 run + A2 run + RG-2003 run
              1.0 + 0.4, 0.4 + 1.0, 0.4 + 0.4 + 0.4),
    "bed B": (["P-03/Line_RG2001_S1", "P-02/Line_RG2001_S1", "P-02/Line_RG2001_S2"],
              ["P-02/Line_RG2002_S1", "P-02/Line_RG2002_S2", "P-02/Line_RG2002_S4"],
              ["P-02/Line_RG2003_S5", "P-02/Line_RG2003_S6", "P-02/Line_RG2003_S7", "P-02/Line_RG2003_S9"],
              1.0 + 0.4, 0.4 + 1.0, 0.4 + 0.4 + 1.0),
}
rg_lines = {}
for bed, (cold, hot_in, hot_out, k1, k2, k3) in rg_paths.items():
    (l1, b1), (l2, b2), (l3, b3) = route_of(cold), route_of(hot_in), route_of(hot_out)
    rows = []
    for name, dns, length, bends, k, m, rho, mu in (
            ("RG-2001 (13 C, FV-2105)", (500, 600), l1, b1, k1, m12a, rho_wn(110.0), MU_WN),
            ("RG-2002 (200 C)", (600, 700), l2, b2, k2, m12a, ideal_rho(T_HOT, 107.0, xw), mu_n2(T_HOT)),
            ("RG-2003 (200 C bound, S-2101)", (600, 700), l3, b3, k3, m12d, ideal_rho(T_HOT, 104.0, x12d),
             mu_n2(T_HOT))):
        res = {dn: gas_line(m, rho, mu, dn, length, bends * K_ELBOW + k) for dn in dns}
        rows.append((name, length, bends, res))
        print(f"  {bed} {name}: {length:.4g} m, {bends} bends, tees K {k:g}, rho {rho:.4g} kg/m3: "
              + "; ".join(f"DN{dn} {dp:.3g} kPa ({v:.3g} m/s)" for dn, (dp, v) in res.items()))
    rg_lines[bed] = rows
for bed, rows in rg_lines.items():
    for label, pick in (("before D-072 (DN500 / DN600 / DN600)", (500, 600, 600)),
                        ("D-072 (DN600 / DN700 / DN700)", (600, 700, 700))):
        lines_dp = sum(r[3][dn][0] for r, dn in zip(rows, pick))
        print(f"  {bed} lines {label}: {lines_dp:.3g} kPa; left for FV-2105, E-2101, the bed with its "
              f"switching valves and S-2101 down to 101.325 kPa(a): {p_tee - 101.325 - lines_dp:.3g} kPa")
# the allowables written into the datasheets and special-items (D-072, ASSUMED allocation)
ALLOW = {"FV-2105 at normal flow": 1.5, "E-2101 gas side": 1.0,
         "V-2101A/B in regeneration (distributor, bed, support, XV-2103 / XV-2104)": 1.5,
         "S-2101 with the exit": 1.0}
worst = max(sum(r[3][dn][0] for r, dn in zip(rows, (600, 700, 700))) for rows in rg_lines.values())
print(f"  allowables (D-072): " + ", ".join(f"{k} {v:g} kPa" for k, v in ALLOW.items())
      + f"; sum {sum(ALLOW.values()):g} kPa + worst lines {worst:.3g} kPa = {sum(ALLOW.values()) + worst:.3g} kPa "
      f"against {p_tee - 101.325:.3g} kPa: margin {p_tee - 101.325 - worst - sum(ALLOW.values()):.3g} kPa")
# screening of the bed allowable: Ergun (Perry's 8th ed. Section 6, packed beds) for the hot gas through
# a horizontal bed, ASSUMED: plan area 0.85 D x (L - D) of the 4.5 m x 18 m vessel, 1.5 m of alumina +
# 13X beads 3 mm, voidage 0.37 (the adsorbent supplier sets the bed)
a_bed = 0.85 * 4.5 * (18.0 - 4.5)
rho_h, mu_h = ideal_rho(T_HOT, 105.0, xw), mu_n2(T_HOT)
u_bed = m12a / 3600.0 / rho_h / a_bed
eps, dp_p, depth = 0.37, 0.003, 1.5
ergun = depth * (150 * mu_h * (1 - eps) ** 2 * u_bed / (eps ** 3 * dp_p ** 2)
                 + 1.75 * rho_h * (1 - eps) * u_bed ** 2 / (eps ** 3 * dp_p)) / 1000.0
print(f"  bed screening (Ergun, ASSUMED geometry): plan area {a_bed:.3g} m2, superficial {u_bed:.3g} m/s at 200 C: "
      f"{ergun:.3g} kPa for 1.5 m of 3 mm beads, inside the 1.5 kPa allowable with the distributor and valves")

print("== section 10 (DESIGN.md D-068 (9), D-073) Cooling water and line velocities")
cw = {"MAC Q1 (DWSIM)": sim("K1101", "cooling_kW"), "DCAC lower Q2 (DWSIM)": -sim("C1101", "duty_kW"),
      "GOX compressor Q3 (DWSIM)": sim("K4101", "cooling_kW"), "GAN compressor Q4 (DWSIM)": sim("K4102", "cooling_kW"),
      "E-3104 Q5 (DWSIM)": -sim("E3104", "duty_kW")}
for name, q in cw.items():
    print(f"  {name}: {q:.6g} kW, {cw_flow(q):.4g} m3/h at 10 K")
print(f"  total {sum(cw.values()):.6g} kW, {cw_flow(sum(cw.values())):.4g} m3/h at 10 K (the DCAC lower "
      f"section's 250 m3/h of P-1101A/B is its own circulation, D-053)")
for line, sid, dn, mflow in (
        ("WN-1001", "S12B", 0.7, None), ("WN-1001", "S12B", 0.9, None), ("WN-1001", "S12B", 1.0, None),
        ("WN-3002", "S17", 0.9, None), ("WN-3003 (bypass, all of S12B)", "S12C", 0.6, flow("S12B")),
        ("WN-3003 (bypass, all of S12B)", "S12C", 0.9, flow("S12B")), ("GOX-4001", "S7", 0.5, None),
        ("AIR-3002 (to E-3105)", "S4D", 0.2, None), ("AIR-3002 (after E-3105)", "S4E", 0.2, None),
        ("AIR-3003", "S5B", 0.15, None)):
    rho = adapter.flash(Inputs(kelvin(sid), kpa(sid), fractions(sid))).density
    q = (mflow if mflow is not None else flow(sid)) / rho / 3600.0
    print(f"  {line} ({sid} {kelvin(sid) - 273.15:.4g} C, {kpa(sid) / 100:.4g} bara): rho {rho:.4g} "
          f"kg/m3 (property adapter), {q:.4g} m3/s, {q / (math.pi / 4 * dn * dn):.3g} m/s in "
          f"{dn * 1000:g} mm (DN as the diameter, D-016)")
# D-073 (review11#2), D-080 (1): the main air lines C-1101 -> E-3101 at the D-066 flow, velocity and
# Darcy drop along the routed lines (the section 11 method: Colebrook, elbows K 0.75, tees K 0.4 run /
# 1.0 branch, the V-2101 nozzle entry 1.0; the ball valves XV-2101 / XV-2102 not counted). Density by
# the property adapter at each line's own pressure on the D-079 profile: AIR-1004 at S3 (dry air of
# S3, 12 C, 5.88 bara at the C-1101 outlet); AIR-2001 after AIR-1004 and the bed's ~8 kPa, AIR-2002
# after F-2101's 3 kPa (dry air of S4 at 15 C, D-079, ASSUMED allowables). The D-073 basis (all three
# lines at S4, 5.6 bara: the lowest density, a bound) is printed beside it. Air viscosity Yoon-Thodos as
# nitrogen (ASSUMED < 2 % off).
BED_DP, F2101_DP = 8.0, 3.0  # kPa, D-079 (ASSUMED, the suppliers' allowables; F-2101 clean, D-080 (1))
x3, x4 = dry(fractions("S3")), fractions("S4")
mu3 = Yoon_Thodos(kelvin("S3"), critical.Tc("7727-37-9"), critical.Pc("7727-37-9"), 28.0134)
mu4 = Yoon_Thodos(kelvin("S4"), critical.Tc("7727-37-9"), critical.Pc("7727-37-9"), 28.0134)
rho3 = adapter.flash(Inputs(kelvin("S3"), kpa("S3"), x3)).density
rho4 = adapter.flash(Inputs(kelvin("S4"), kpa("S4"), x4)).density


def rho_dry(p_kpa: float) -> float:
    return adapter.flash(Inputs(kelvin("S4"), p_kpa, x4)).density


AIR_PATHS = {
    "A": (["P-01/Line_AIR1004_S1", "P-02/Line_AIR1004_S1", "P-02/Line_AIR1004_S2", "P-02/Line_AIR1004_S3",
           "P-02/Line_AIR1004_S4"], 0.4 + 0.4 + 0.4 + 1.0, ["P-02/Line_AIR2001_S1", "P-02/Line_AIR2001_S3"], 0.4),
    "B": (["P-01/Line_AIR1004_S1", "P-02/Line_AIR1004_S1", "P-02/Line_AIR1004_S6", "P-02/Line_AIR1004_S7",
           "P-02/Line_AIR1004_S8"], 1.0 + 0.4 + 0.4 + 1.0, ["P-02/Line_AIR2001_S2", "P-02/Line_AIR2001_S3"], 1.0),
}
L2002a, B2002a = route_of(["P-02/Line_AIR2002_S1", "P-03/Line_AIR2002_S1"])
L2002b, B2002b = route_of(["P-03/Line_AIR2002_S2"])
print(f"  main air lines: S3 {flow('S3'):g} kg/h at {kpa('S3'):g} kPa(a) (dry-air density {rho3:.4g} kg/m3), S4 "
      f"{flow('S4'):g} kg/h, S4A {flow('S4A'):g} kg/h at {kpa('S4'):g} kPa(a) ({rho4:.4g} kg/m3); bed {BED_DP:g} kPa, "
      f"F-2101 {F2101_DP:g} kPa clean (ASSUMED, D-079 / D-080)")
for dn in (600, 700):
    area = math.pi / 4 * (dn / 1000) ** 2
    print(f"  DN{dn} (DN as the diameter, D-016): AIR-1004 {flow('S3') / rho3 / 3600 / area:.3g} m/s, AIR-2001 / "
          f"AIR-2002 {flow('S4') / rho4 / 3600 / area:.3g} m/s, after the AIR-3005 tee {flow('S4A') / rho4 / 3600 / area:.3g} m/s")
air_path = {}
for bed, (p1004, k1004, p2001, k2001) in AIR_PATHS.items():
    (l1, b1), (l2, b2) = route_of(p1004), route_of(p2001)
    for dn in (600, 700):
        for basis in ("local", "S4"):
            r1 = rho3 if basis == "local" else rho4
            dp1, v1 = gas_line(flow("S3"), r1, mu3, dn, l1, b1 * K_ELBOW + k1004)
            p2 = kpa("S3") - dp1 - BED_DP
            r2 = rho_dry(p2) if basis == "local" else rho4
            dp2, v2 = gas_line(flow("S4"), r2, mu4, dn, l2, b2 * K_ELBOW + k2001)
            p3 = p2 - dp2 - F2101_DP
            r3 = rho_dry(p3) if basis == "local" else rho4
            dp3a, v3 = gas_line(flow("S4"), r3, mu4, dn, L2002a, B2002a * K_ELBOW)
            dp3b, _ = gas_line(flow("S4A"), r3, mu4, dn, L2002b, B2002b * K_ELBOW + 0.4)
            lines = dp1 + dp2 + dp3a + dp3b
            air_path[(bed, dn, basis)] = lines
            if basis == "local":
                print(f"  bed {bed} DN{dn}: AIR-1004 {l1:.4g} m, {b1} bends, tees + entry K {k1004:g}: {dp1:.3g} kPa "
                      f"({v1:.3g} m/s in the ID); AIR-2001 {l2:.4g} m, {b2} bends, tee K {k2001:g}, at {p2:.4g} kPa(a): "
                      f"{dp2:.3g} kPa ({v2:.3g} m/s); AIR-2002 {L2002a:.4g} + {L2002b:.4g} m, {B2002a} + {B2002b} bends, at "
                      f"{p3:.4g} kPa(a): {dp3a:.3g} + {dp3b:.3g} kPa ({v3:.3g} m/s); lines {lines:.3g} kPa")
            else:
                print(f"  bed {bed} DN{dn} on the D-073 basis (every line at S4 {rho4:.4g} kg/m3): lines {lines:.3g} kPa")
# the bound (D-080 (1)): every change of direction a bend (jogs under 0.3 m and the turns where the
# path passes from one pipe to the next included), the vessel nozzles in the lines as well: V-2101
# outlet 0.5 (pipe entrance from a vessel), F-2101 in 1.0 / out 0.5, E-3101 in 1.0 (ASSUMED: these
# are normally inside the vessels' own allowables), at S4 density
for bed, (p1004, k1004, p2001, k2001) in AIR_PATHS.items():
    (l1, b1), (l2, b2) = route_of(p1004, 0.0, True), route_of(p2001, 0.0, True)
    (la, ba) = route_of(["P-02/Line_AIR2002_S1", "P-03/Line_AIR2002_S1"], 0.0, True)
    (lb, bb) = route_of(["P-03/Line_AIR2002_S2"], 0.0, True)
    dp1, _ = gas_line(flow("S3"), rho4, mu3, 700, l1, b1 * K_ELBOW + k1004)
    dp2, _ = gas_line(flow("S4"), rho4, mu4, 700, l2, b2 * K_ELBOW + k2001 + 0.5 + 1.0)
    dp3a, _ = gas_line(flow("S4"), rho4, mu4, 700, la, (ba + 1) * K_ELBOW + 0.5)
    dp3b, _ = gas_line(flow("S4A"), rho4, mu4, 700, lb, bb * K_ELBOW + 0.4 + 1.0)
    air_path[(bed, 700, "bound")] = dp1 + dp2 + dp3a + dp3b
    print(f"  bed {bed} DN700 bound: {b1} + {b2} + {ba + 1} + {bb} bends, the vessel nozzles counted, S4 density: "
          f"{dp1:.3g} + {dp2:.3g} + {dp3a:.3g} + {dp3b:.3g} = {dp1 + dp2 + dp3a + dp3b:.3g} kPa")
for dn in (600, 700):
    worst = max(air_path[(b, dn, "local")] for b in AIR_PATHS)
    bound = max(air_path[(b, dn, "S4")] for b in AIR_PATHS)
    budget = kpa("S3") - kpa("S4")
    print(f"  front end DN{dn}, longer bed: lines {worst:.3g} kPa (D-073 basis {bound:.3g}) + bed {BED_DP:g} + F-2101 "
          f"{F2101_DP:g} = {worst + BED_DP + F2101_DP:.3g} kPa against S3 -> S4 {budget:g} kPa (D-079): margin "
          f"{budget - worst - BED_DP - F2101_DP:+.3g} kPa (D-073 basis {budget - bound - BED_DP - F2101_DP:+.3g})"
          + (f"; the bound {max(air_path[(b, 700, 'bound')] for b in AIR_PATHS):.3g} kPa: margin "
             f"{budget - max(air_path[(b, 700, 'bound')] for b in AIR_PATHS) - BED_DP - F2101_DP:+.3g} kPa"
             if dn == 700 else ""))
# what one kPa more at the MAC discharge costs: electric power pro rata to ln(p2 / p1) of the three
# stages (ideal-gas compression at the same efficiencies, D-066 E1)
p_mac = kpa("S2") + spec("K1101", "pressure_drop") * 100.0
print(f"  MAC: +1 kPa at the discharge ({p_mac:g} kPa(a)) ~ {E1 / math.log(p_mac / kpa('S1')) / p_mac:.3g} kW electric "
      f"(E1 {E1:g} kW pro rata to ln(p2/p1))")
# the MAC interstage hot legs (MAC package): velocities at the section 1 stage discharge states, wet air
# ideal gas (Z ~ 1 at 1.8-3.3 bara)
for line, r, dn in (("AIR-1005", mac[0], 0.9), ("AIR-1006", mac[1], 0.7)):
    rho = r["p_out"] * r["mw"] / (R * r["t_out"])
    q = r["m_kg_h"] / rho / 3600.0
    print(f"  {line} (K-1101 stage {r['stage']} discharge {r['t_out'] - 273.15:.4g} C, {r['p_out']:.4g} kPa(a), "
          f"{r['m_kg_h']:.6g} kg/h): rho {rho:.4g} kg/m3 (ideal gas), {q:.4g} m3/s, "
          f"{q / (math.pi / 4 * dn * dn):.3g} m/s in {dn * 1000:g} mm (DN as the diameter, D-016)")
for line, v, dn in (("CHW-1001", v_dcac + v_3105, 0.15), ("CHWR-1001", v_dcac, 0.15),
                    ("CHW-3001 / CHWR-3001", v_3105, 0.05), ("CW-1003 make-up", 1.5, 0.15)):
    print(f"  {line}: {v:.4g} m3/h, {v / 3600 / (math.pi / 4 * dn * dn):.3g} m/s in {dn * 1000:g} mm")
for key, (q, text) in vaporizer_duties.items():
    print(f"  (summary) {key} duty {q:.4g} kW ({text})")
