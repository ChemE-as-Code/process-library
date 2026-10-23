"""Hand sizing of the datasheet values `cheme datasheets fill` cannot reach (DESIGN.md D-053,
D-060).

Provenance only: it prints each value with its basis; the values are written into
equipment/datasheets/<TAG>.yaml by hand, with the source "scripts/datasheet_sizing.py <section>".
It uses only cheme-as-code's own methods (the property adapter, the sizing and line-loss functions,
the public pump sizing `chemeascode.domains.equipment.pumps` along the routed pipes of the layout
model), IAPWS-95 for water and the Yoon-Thodos gas viscosity (chemicals, the props extra), so the
numbers are reproducible:

    cheme run scripts/datasheet_sizing.py

Every input that is an assumption is named here and in D-053 / D-060.
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
R = sizing.R
CW_IN, CW_OUT = 298.15, 308.15  # process/design-basis.yaml cooling water 25 -> 35 C
U = sizing.typical_u("cooler/gases-water")  # D-053: the gas coolers' U row, ASSUMED

process, _ = load(ROOT)
adapter = Adapter(process)
network = pumps.network(ROOT)
streams = {s.id: s for s in process.flowsheet.streams}


def sheet(tag: str) -> dict:
    return yaml.safe_load((ROOT / f"equipment/datasheets/{tag}.yaml").read_text(encoding="utf-8"))


def num(tag: str, key: str) -> float:
    return float(sheet(tag)["type_specific"][key]["value"])


def fractions(stream_id: str) -> dict[str, float]:
    return dict(streams[stream_id].state["design"].composition.values)


def molar_mass(x: dict[str, float]) -> float:
    comps = process.components()
    return sum(v * comps[k].molar_mass for k, v in x.items())


def h(stream_id: str, t: float | None = None, p: float | None = None) -> float:
    """Molar enthalpy kJ/kmol of a stream (or its composition at t K, p kPa(a))."""
    state = streams[stream_id].state["design"]
    t = t if t is not None else state.temperature.value + 273.15
    p = p if p is not None else state.pressure.value * 100.0
    return adapter.flash(Inputs(t, p, fractions(stream_id))).enthalpy


def cooler(name: str, duty: float, hot_in: float, hot_out: float) -> float:
    """Area of one gas cooler against cooling water, 1-2 shell and tube (D-053)."""
    dt = sizing.lmtd(hot_in, hot_out, CW_IN, CW_OUT, "1-2")
    f = sizing.correction_factor(hot_in, hot_out, CW_IN, CW_OUT, "1-2")
    area = sizing.exchanger_area(duty, U.value, f, dt)
    water = iapws.iapws95_properties(303.15, 4.5e5)  # CW at its mean 30 C, ~4.5 bara
    cw = duty / (water[5] / 1000.0 * (CW_OUT - CW_IN)) / water[0] * 3600.0
    print(
        f"  {name}: Q {duty:.4g} kW, hot {hot_in:.5g} -> {hot_out:.5g} K, CW 298.15 -> 308.15 K, "
        f"1-2 LMTD {dt:.4g} K, F {f:.4g}, U {U.value:g} W/(m2 K) (middle of {U.low:g}-{U.high:g}, "
        f"{U.source}), A = Q / (U F LMTD) = {area:.4g} m2; CW {cw:.4g} m3/h (IAPWS-95 cp "
        f"{water[5] / 1000:.4g} kJ/(kg K), rho {water[0]:.4g} kg/m3 at 30 C)"
    )
    return area


def machine(tag: str, stream_id: str, k: float, intercooled: float | None):
    """Stage outlet temperatures and duties of an ideal-gas machine as the fill sized it."""
    s = sheet(tag)["type_specific"]
    m = streams[stream_id].state["design"].flow.value / 3600.0
    x = fractions(stream_id)
    mw = molar_mass(x)
    t = streams[stream_id].state["design"].temperature.value + 273.15
    n, ratio = int(s["number_of_stages"]["value"]), float(s["stage_pressure_ratio"]["value"])
    eta = float(s["isentropic_efficiency"]["value"])
    cp = R * k / ((k - 1.0) * mw)
    out = []
    for _ in range(n):
        stage = sizing.ideal_gas_stage(t, ratio, k, mw, eta, "isentropic")
        out.append(stage.outlet_temperature)
        t = intercooled if intercooled else t
    print(
        f"{tag}: m {m * 3600:.6g} kg/h ({stream_id}), M {mw:.4g}, k {k:.4g}, cp {cp:.4g} kJ/(kg K), "
        f"{n} x ratio {ratio:.4g}, eta_s {eta:g}; stage outlets {[round(v, 2) for v in out]} K"
    )
    return m, cp, out


print("== D-053 (1) MAC K-1101 coolers E-1101 / E-1102 / E-1103 (dry-gas sensible duty)")
m, cp, outs = machine("K-1101", "S1", num("K-1101", "heat_capacity_ratio"), 313.15)
areas = [cooler(f"E-110{i + 1}", m * cp * (t - 313.15), t, 313.15) for i, t in enumerate(outs)]
p1 = streams["S1"].state["design"].pressure.value * 100.0
ratio = num("K-1101", "stage_pressure_ratio")
x_h2o = fractions("S1")["H2O"]
psat40 = iapws.iapws95_Psat(313.15) / 1000.0
for i in range(3):
    p = p1 * ratio ** (i + 1)
    print(
        f"  stage {i + 1} outlet {p:.4g} kPa(a): water partial pressure {x_h2o * p:.3g} kPa "
        f"(S1 x_H2O {x_h2o}) vs saturation {psat40:.4g} kPa at 40 C (IAPWS-95): "
        f"{'condenses' if x_h2o * p > psat40 else 'no condensate'}"
    )
# the design basis' 80 % RH at 30 C instead of the flowsheet's 0.25 mol%
x80 = 0.8 * iapws.iapws95_Psat(303.15) / 1000.0 / 101.3
n_air = streams["S1"].state["design"].flow.value / molar_mass(fractions("S1"))
dry = n_air * (1 - x_h2o)
hv = iapws.iapws95_properties(313.15, psat40 * 999.0)[3]
hl = iapws.iapws95_properties(313.15, psat40 * 1001.0)[3]
latent = (hv - hl) / 1000.0
water = dry * x80 / (1 - x80)
for i in range(3):
    p = p1 * ratio ** (i + 1)
    xs = psat40 / p
    left = dry * xs / (1 - xs)
    cond = max(0.0, water - left)
    print(
        f"  80 % RH (x_H2O {x80:.4f}): after cooler {i + 1} at {p:.4g} kPa(a), 40 C: "
        f"{cond * 18.015:.4g} kg/h condensed, {cond * 18.015 / 3600 * latent:.4g} kW latent "
        f"(IAPWS-95 latent heat {latent:.4g} kJ/kg at 40 C)"
    )
    water -= cond

print("== D-053 (2) GOX compressor K-4101 coolers E-4101 (4 intercoolers) / E-4102")
k = adapter.heat_capacity_ratio(Inputs(298.15, 115.0, fractions("S7")))
m, cp, outs = machine("K-4101", "S7", k, 313.15)
ic = [cooler(f"E-4101 intercooler {i + 1}", m * cp * (t - 313.15), t, 313.15)
      for i, t in enumerate(outs[:-1])]
print(f"  E-4101 total: Q {sum(m * cp * (t - 313.15) for t in outs[:-1]):.4g} kW, "
      f"A {sum(ic):.4g} m2")
cooler("E-4102", m * cp * (outs[-1] - 313.15), outs[-1], 313.15)

print("== D-053 (3) GAN compressor K-4102 aftercooler E-4103")
k = adapter.heat_capacity_ratio(Inputs(298.15, 520.0, fractions("S9")))
m, cp, outs = machine("K-4102", "S9", k, None)
cooler("E-4103", m * cp * (outs[-1] - 313.15), outs[-1], 313.15)

print("== D-053 (4) Booster aftercooler E-3104")
k = adapter.heat_capacity_ratio(Inputs(288.15, 560.0, fractions("S4B")))
m, cp, outs = machine("K-3101", "S4B", k, None)
print(f"  E-3104: Q = m cp (T_out - 313.15) = {m * cp * (outs[-1] - 313.15):.4g} kW")

print("== D-053 (5) Main heat exchanger E-3101: warm and cold sides")
warm = 0.0
for a, b in (("S4A", "S5"), ("S4D", "S5B")):
    flow = streams[a].state["design"].flow.value
    ha = h("S4") if a == "S4A" else h(a)
    hb = h(b)
    q = flow / molar_mass(fractions(b)) * (ha - hb) / 3600.0
    warm += q
    print(f"  warm {a} -> {b}: {flow:g} kg/h, h {ha:.6g} -> {hb:.6g} kJ/kmol: {q:.5g} kW")
cold = 0.0
for a, b, p in (("S14", "S9", 540.0), ("S15", "S7", 130.0), ("S16", "S17", 130.0)):
    x = fractions(a)
    t_dew = adapter.saturation_temperature(p, x, 1.0)
    ha = adapter.flash(Inputs(t_dew + 0.01, p, x)).enthalpy
    flow = streams[a].state["design"].flow.value
    q = flow / molar_mass(x) * (h(b) - ha) / 3600.0
    cold += q
    print(
        f"  cold {a} -> {b}: {flow:g} kg/h, saturated vapour at {p:g} kPa(a) (ASSUMED, column "
        f"pressure) dew {t_dew:.4g} K, h {ha:.6g} -> {h(b):.6g} kJ/kmol: {q:.5g} kW"
    )
print(f"  warm side {warm:.5g} kW, cold side {cold:.5g} kW, difference {warm - cold:.4g} kW")

print("== D-053 (6) HP column C-3101 Fenske / Underwood (N2 / O2 keys, Ar a non-key)")
z = fractions("S5")
xd = dict(fractions("S14"))
xb_o2 = 0.38  # DESIGN.md 1: rich liquid ~38 % O2
b = z["O2"] / xb_o2  # B/F, kmol/kmol (distillate O2 10 ppm neglected)
xb = {"O2": xb_o2, "AR": (z["AR"] - (1 - b) * xd["AR"]) / b}
xb["N2"] = 1 - xb["O2"] - xb["AR"]
t_top, k_top = adapter.k_values(540.0, xd, 1.0)
t_bot, k_bot = adapter.k_values(550.0, xb, 0.0)
alphas = {c: math.sqrt((k_top[c] / k_top["O2"]) * (k_bot[c] / k_bot["O2"])) for c in z}
res = shortcut.fug(alphas, z, xd, xb, 0.0, "N2", "O2")
print(
    f"  feed S5 {z}, q 0 (saturated vapour, ASSUMED: 'cooled close to its dew point', DESIGN.md 1);"
    f" distillate S14 {xd} at 540 kPa(a) (dew {t_top:.4g} K); bottoms rich liquid {xb} "
    f"(x_O2 0.38 DESIGN.md 1, B/F {b:.4g} by O2 and Ar balance) at 550 kPa(a) (bubble "
    f"{t_bot:.4g} K); alpha N2/O2 {alphas['N2']:.4g}, Ar/O2 {alphas['AR']:.4g} (geometric "
    f"mean top/bottom, property adapter); Nmin {res.min_stages:.4g}, theta {res.theta:.5g}, "
    f"Rmin {res.min_reflux:.4g}; {shortcut.SOURCES}"
)

print("== D-053 (7) LP column C-3102 Fenske (minimum stages only)")
top, bot = fractions("S16"), fractions("S15")
t_top, k_top = adapter.k_values(130.0, top, 1.0)
t_bot, k_bot = adapter.k_values(135.0, bot, 0.0)
for lk in ("N2", "AR"):
    a = math.sqrt((k_top[lk] / k_top["O2"]) * (k_bot[lk] / k_bot["O2"]))
    nmin = shortcut.fenske(top[lk], top["O2"], bot[lk], bot["O2"], a)
    print(
        f"  keys {lk}/O2: waste S16 {top} at 130 kPa(a) (dew {t_top:.4g} K), GOX S15 {bot} at "
        f"135 kPa(a) (bubble {t_bot:.4g} K; sump pressure ASSUMED); alpha {a:.4g}; Nmin "
        f"{nmin:.4g}"
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


def temperature_at(pressure: float, enthalpy: float, x: dict[str, float], lo: float, hi: float):
    """The temperature K of a single-phase state of molar *enthalpy* at *pressure* kPa(a)."""
    return brentq(lambda t: adapter.flash(Inputs(t, pressure, x)).enthalpy - enthalpy, lo, hi,
                  xtol=1e-6)


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
for tag, sid, flow, rho, tank, vap, tie_in, header, cas, mw_gas in (
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
    m = flow / 3600.0
    t_sat = adapter.saturation_temperature(150.0, x, 0.0)
    mu, basis = adapter.liquid_viscosity(t_sat, x)
    gas = adapter.flash(Inputs(T_VAP_OUT, header + DP_VALVE, x))
    mu_gas = Yoon_Thodos(T_VAP_OUT, critical.Tc(cas), critical.Pc(cas), mw_gas)
    line = pumps.route_line(network, vap, f"pipe:{tie_in}:end", nozzle="N2", mass_flow_kg_s=m,
                            density_kg_m3=gas.density, viscosity_pa_s=mu_gas, what="discharge")
    p_vap_in = header + line.pressure_drop_kpa + DP_VALVE + DP_VAPORIZER
    print(f"{tag}: {flow:g} kg/h, rho {rho:g} (D-042, NIST), saturated at 150 kPa(a) {t_sat:.4g} K, "
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
for tag, t, flow, p_src, p_dst, src, dst in (
    ("P-1101A", 298.15, 250.0, 501.3, 580.0, "pipe:P-01/Line_CW1001_S1:start", "C-1101"),
    ("P-1101B", 298.15, 250.0, 501.3, 580.0, "pipe:P-01/Line_CW1001_S1:start", "C-1101"),
    ("P-1102A", 283.15, 100.0, 105.0, 570.0, "C-1102", "C-1101"),
    ("P-1102B", 283.15, 100.0, 105.0, 570.0, "C-1102", "C-1101"),
):
    rho = iapws.iapws95_rho(t, p_src * 1000.0)
    pv = iapws.iapws95_Psat(t) / 1000.0
    mu = mu_IAPWS(t, rho)
    m = flow * rho / 3600.0
    print(f"{tag}: {flow:g} m3/h water at {t - 273.15:g} C: rho {rho:.5g} kg/m3, p_vap {pv:.4g} "
          f"kPa(a), mu {mu * 1000:.4g} mPa s (IAPWS-95 / IAPWS 2008 viscosity, chemicals)")
    duty = pumps.size_pump(
        network, tag, suction_from=src, discharge_to=dst, mass_flow_kg_s=m, density_kg_m3=rho,
        viscosity_pa_s=mu, suction_pressure_kpa=p_src, discharge_pressure_kpa=p_dst,
        vapour_pressure_kpa=pv, efficiency=eta, allowance_kpa=allowance,
    )
    show_pump(duty)

print("== D-060 (3) DCAC C-1101 and evaporative cooler C-1102: duty and hydraulic loads")
s2 = fractions("S2")
n_tot = streams["S2"].state["design"].flow.value / molar_mass(s2)
dry = {k: v for k, v in s2.items() if k in ("N2", "O2", "AR")}
dry_sum = sum(dry.values())
dry = {k: v / dry_sum for k, v in dry.items()}
n_dry = n_tot * dry_sum
q_dry = n_dry * (adapter.flash(Inputs(313.15, 580.0, dry)).enthalpy
                 - adapter.flash(Inputs(285.15, 570.0, dry)).enthalpy) / 3600.0
y_sat = iapws.iapws95_Psat(285.15) / 1000.0 / 570.0
n_w_in = n_tot * s2["H2O"]
n_w_out = n_dry * y_sat / (1.0 - y_sat)
cond = max(0.0, n_w_in - n_w_out)
hv =iapws.iapws95_properties(298.15, iapws.iapws95_Psat(298.15) * 0.999)[3] / 1000.0
hl = iapws.iapws95_properties(298.15, iapws.iapws95_Psat(298.15) * 1.001)[3] / 1000.0
latent = hv - hl
q_water = n_w_in * 18.015 * 1.87 * 28.0 / 3600.0  # vapour sensible, cp ~1.87 kJ/(kg K) IAPWS-95
q_cond = cond * 18.015 * latent / 3600.0
print(
    f"  C-1101 duty: dry gas {n_dry:.6g} kmol/h ({dry}) 313.15 K 580 kPa(a) -> 285.15 K 570 kPa(a)"
    f" {q_dry:.4g} kW (property adapter); water vapour {n_w_in:.4g} kmol/h (S2 x_H2O "
    f"{s2['H2O']}) sensible {q_water:.3g} kW; saturation at 12 C, 570 kPa(a) y {y_sat:.4g} "
    f"(IAPWS-95): {cond:.3g} kmol/h condense, {q_cond:.3g} kW (latent {latent:.4g} kJ/kg at 25 C);"
    f" total {q_dry + q_water + q_cond:.4g} kW (CO2 neglected)"
)
for tag, flow, t, p, d, liquids in (
    ("C-1101 bottom", streams["S2"].state["design"].flow.value, 313.15, 580.0, 4.0,
     (("lower section CW", 250.0), ("upper section chilled water", 100.0))),
    ("C-1102", streams["S12B"].state["design"].flow.value, 298.15, 105.0, 4.5,
     (("water", 100.0),)),
):
    xg = dry if tag.startswith("C-1101") else fractions("S12B")
    rho_g = adapter.flash(Inputs(t, p, xg)).density
    area = math.pi / 4.0 * d * d
    u = flow / 3600.0 / rho_g / area
    loads = ", ".join(f"{name} {q:g} m3/h: {q / area:.3g} m3/(m2 h)" for name, q in liquids)
    print(
        f"  {tag}: gas {flow:g} kg/h at {t:.2f} K, {p:g} kPa(a): rho {rho_g:.4g} kg/m3 (property "
        f"adapter, dry gas), D {d:g} m (equipment list), area {area:.4g} m2, u {u:.3g} m/s, "
        f"F = u rho^0.5 {u * rho_g ** 0.5:.3g} Pa^0.5; liquid loads {loads}"
    )
# lowest water temperature the dry waste N2 can reach: its adiabatic saturation temperature
# (energy balance, liquid fed at that temperature), the bound of an evaporative cooler
xn = fractions("S12B")
n_n2 = streams["S12B"].state["design"].flow.value / molar_mass(xn)
h_n2_in = adapter.flash(Inputs(298.15, 105.0, xn)).enthalpy


def _as(t: float) -> float:
    psat = iapws.iapws95_Psat(t) / 1000.0
    y = psat / 105.0
    w = n_n2 * y / (1.0 - y) * 18.015  # kg/h water taken up
    hv_t = iapws.iapws95_properties(t, psat * 999.0)[3] / 1000.0
    hl_t = iapws.iapws95_properties(t, psat * 1001.0)[3] / 1000.0
    return n_n2 * (h_n2_in - adapter.flash(Inputs(t, 105.0, xn)).enthalpy) - w * (hv_t - hl_t)


t_as = brentq(_as, 275.0, 298.0)
print(
    f"  C-1102: adiabatic saturation temperature of S12B (dry, 25 C, 105 kPa(a)) {t_as - 273.15:.3g} C"
    f" (energy balance N2 enthalpy, property adapter / water IAPWS-95; Perry's 8th ed. Section 12,"
    f" psychrometry): the 10 C chilled water lies {283.15 - t_as:.3g} K above it"
)

print("== D-060 (4) Main heat exchanger E-3101: composite curves")


def _side(sid: str, flow: float, t_in: float, t_out: float, p_in: float, p_out: float):
    x = fractions(sid)
    n = flow / molar_mass(x) / 3600.0

    def heat(t: float) -> float:
        f = (t - t_in) / (t_out - t_in)
        return n * adapter.flash(Inputs(t, p_in + (p_out - p_in) * f, x)).enthalpy

    return {"heat": heat, "lo": min(t_in, t_out), "hi": max(t_in, t_out), "t_in": t_in,
            "t_out": t_out}


WARM = [_side("S5", 83190, 288.15, 100.15, 560, 550), _side("S5B", 14870, 313.15, 155.15, 800, 780)]


def cold_sides(superheat: float, t_out: float = 298.15):
    sides = []
    for sid, flow, p_in, p_out in (("S14", 12510, 540, 520), ("S15", 20860, 130, 115),
                                   ("S16", 63750, 130, 115)):
        dew = adapter.saturation_temperature(p_in, fractions(sid), 1.0)
        sides.append(_side(sid, flow, dew + superheat, t_out, p_in, p_out))
    return sides


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
    warm_end = d[: len(d) // 10]
    return qw[-1], qc[-1], float(d.min()), float(q[i]), float(warm_end.min()), ua


q_warm = total(WARM)
print(f"  warm side S4A -> S5 and S4D -> S5B (flowsheet states): {q_warm:.5g} kW")
qw_, qc_, dmin, qat, dwarm, ua = approach(WARM, cold_sides(0.01))
print(f"  cold side from saturated vapour (ASSUMED column pressures 540 / 130 / 130 kPa(a)) to the "
      f"flowsheet's 25 C: {qc_:.5g} kW; minimum approach {dmin:.3g} K, warm-end tenth {dwarm:.3g} K")
for t_out in (298.15, 286.15):
    sh = brentq(lambda s, t_out=t_out: total(cold_sides(s, t_out)) - q_warm, 0.01, 60.0)
    qw_, qc_, dmin, qat, dwarm, ua = approach(WARM, cold_sides(sh, t_out))
    print(
        f"  cold outlets {t_out - 273.15:.3g} C, cold inlets {sh:.3g} K above their dew points "
        f"(balance closed, heat leak neglected; ASSUMED): duty {qc_:.5g} kW, minimum approach "
        f"{dmin:.3g} K at {qat:.4g} kW from the warm end, warm-end tenth {dwarm:.3g} K, "
        f"UA = sum dQ / LMTD over 600 intervals {ua:.4g} kW/K"
    )

print("== D-060 (7) Compander K-3101 / KT-3101: power balance")
air = fractions("S4B")
mw_air = molar_mass(air)
m_air = streams["S4B"].state["design"].flow.value / 3600.0
k_air = adapter.heat_capacity_ratio(Inputs(288.15, 560.0, air))
ETA_M = 0.97  # D-053, ASSUMED, each machine's bearings


def expander(p_in: float, t_in: float, p_out: float = 135.0, eta: float = 0.85):
    h_in = adapter.flash(Inputs(t_in, p_in, air)).enthalpy
    h_is = adapter.flash_ps(p_out, adapter.entropy(Inputs(t_in, p_in, air)), air).enthalpy
    h_out = h_in - eta * (h_in - h_is)
    return m_air / mw_air * (h_in - h_out), temperature_at(p_out, h_out, air, 90.0, 314.0)


def booster(p2: float, p1: float = 560.0, t1: float = 288.15, eta: float = 0.8):
    stage = sizing.ideal_gas_stage(t1, p2 / p1, k_air, mw_air, eta, "isentropic")
    return m_air * stage.work, stage.outlet_temperature


def balance(p2: float, t5b: float | None = None):
    if t5b is None:
        t5b = brentq(lambda t: expander(p2 - 20.0, t)[1] - 95.15, 146.0, 200.0, xtol=1e-4)
    w_e, t_ex = expander(p2 - 20.0, t5b)
    w_b, t2 = booster(p2)
    return w_b - ETA_M**2 * w_e, t5b, w_e, t_ex, w_b, t2


def report(label: str, p2: float, t5b: float | None = None) -> None:
    gap, t5b, w_e, t_ex, w_b, t2 = balance(p2, t5b)
    cp = R * k_air / ((k_air - 1.0) * mw_air)
    q3104 = m_air * cp * (t2 - 313.15)
    cw = q3104 / (4.18 * 10.0) / 0.996 * 3.6
    print(
        f"  {label}: booster 560 -> {p2:.4g} kPa(a), discharge {t2:.4g} K ({t2 - 273.15:.3g} C), "
        f"gas power {w_b:.4g} kW (ideal gas, k {k_air:.4g}, eta_s 0.80); expander {p2 - 20:.4g} "
        f"kPa(a), {t5b:.4g} K ({t5b - 273.15:.4g} C) -> 135 kPa(a), exhaust {t_ex:.4g} K "
        f"({t_ex - 273.15:.4g} C), gas power {w_e:.4g} kW (real gas, eta_s 0.85); booster - "
        f"{ETA_M}^2 x expander = {gap:.3g} kW; E-3104 {q3104:.3g} kW to 40 C, CW ~{cw:.2g} m3/h"
        f" at 10 K"
    )


report("flowsheet (S4C 8.0 bara, S5B 7.8 bara -118 C)", 800.0, 155.15)
p_a = brentq(lambda p: balance(p, 155.15)[0], 800.0, 1000.0)
report("balanced, expander inlet kept at -118 C", p_a, 155.15)
p_b = brentq(lambda p: balance(p)[0], 800.0, 950.0)
report("balanced, exhaust kept at -178 C (S6)", p_b)
for key, (q, text) in vaporizer_duties.items():
    print(f"  (summary) {key} duty {q:.4g} kW ({text})")
