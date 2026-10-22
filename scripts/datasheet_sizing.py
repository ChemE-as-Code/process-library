"""Hand sizing of the datasheet values `cheme datasheets fill` cannot reach (DESIGN.md D-053).

Provenance only: it prints each value with its basis; the values are written into
equipment/datasheets/<TAG>.yaml by hand, with the source "scripts/datasheet_sizing.py <section>".
It uses only cheme-as-code's own methods (the property adapter, the sizing and line-loss functions,
the fill's routed-pipe network) and IAPWS-95 for water (chemicals, the props extra), so the
numbers are reproducible:

    cheme run scripts/datasheet_sizing.py

Every input that is an assumption is named here and in D-053.
"""

from __future__ import annotations

import math
from pathlib import Path

import yaml
from chemicals import iapws
from chemicals.viscosity import mu_IAPWS
from chemeascode.domains.equipment import sizing
from chemeascode.domains.equipment.fill import Param, _key, _Network, _route
from chemeascode.domains.process.model import load
from chemeascode.domains.process.props import Adapter, Inputs
from chemeascode.domains.process.separations import shortcut

ROOT = Path.cwd()
R = sizing.R
CW_IN, CW_OUT = 298.15, 308.15  # process/design-basis.yaml cooling water 25 -> 35 C
U = sizing.typical_u("cooler/gases-water")  # D-053: the gas coolers' U row, ASSUMED

process, _ = load(ROOT)
adapter = Adapter(process)
model = yaml.safe_load((ROOT / "layout/plant-model.yaml").read_text(encoding="utf-8"))
network = _Network(model)
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


class _Stub:
    """What fill._route asks of a datasheet: its tag and its declared parameters."""

    def __init__(self, tag: str, params: dict[str, Param]) -> None:
        self.tag, self.params = tag, params

    def param(self, name: str) -> Param | None:
        return self.params.get(name)


class _Ctx:
    network = network


def pump(tag: str, m: float, rho: float, mu: float, suction: list[str], discharge: list[str],
         params: dict[str, Param]):
    stub = _Stub(tag, params)
    s = _route(stub, _Ctx, "suction_nozzle", suction, None, m, rho, mu, "suction")
    d = _route(stub, _Ctx, "discharge_nozzle", discharge, s.nozzle, m, rho, mu, "discharge")
    print(f"  {s.text}\n  {d.text}")
    print(
        f"  suction static {s.elevation_target - s.elevation_pump:.4g} m (source nozzle z "
        f"{s.elevation_target:.3f} - pump z {s.elevation_pump:.3f}), suction loss "
        f"{s.loss.head:.4g} m; discharge static {d.elevation_target - s.elevation_target:.4g} m, "
        f"discharge loss {d.loss.head:.4g} m"
    )
    return s, d


print("== D-053 (8) LOX / LIN backup pumps: NPSH available along the routed suction lines")
schedule = Param("10S", "DESIGN.md D-053 (ASSUMED: stainless cryogenic lines)", True)
for tag, sid, flow, rho, tank, vap in (
    ("P-4101A", "S10", 5200.0, 1141.0, "T-4101", "E-4105A"),
    ("P-4101B", "S10", 5200.0, 1141.0, "T-4101", "E-4105B"),
    ("P-4102A", "S11", 6300.0, 806.0, "T-4102", "E-4106A"),
    ("P-4102B", "S11", 6300.0, 806.0, "T-4102", "E-4106B"),
):
    x = fractions(sid)
    t_sat = adapter.saturation_temperature(150.0, x, 0.0)
    mu, basis = adapter.liquid_viscosity(t_sat, x)
    print(f"{tag}: {flow:g} kg/h, rho {rho:g} (D-042, NIST), saturated at 150 kPa(a) {t_sat:.4g} K, "
          f"mu {mu * 1000:.4g} mPa s ASSUMED ({basis})")
    s, d = pump(tag, flow / 3600.0, rho, mu, [tank], [vap], {"pipe_schedule": schedule})
    npsh = sizing.npsh_available(150.0, 150.0, rho, s.elevation_target - s.elevation_pump,
                                 s.loss.head)
    print(f"  NPSHa (saturated liquid, p_tank = p_vap, no liquid level counted) = {npsh:.4g} m")

print("== D-053 (9) DCAC cooling water pumps P-1101A/B and chilled water pumps P-1102A/B")
bl = next(p for p in model["pipes"] if p["id"] == "P-01/Line_CW1001_S1")
bl_point = tuple(float(v) for v in bl["points"][0])
network.label[_key(bl_point)] = "BL/CW-1001"
network.nozzles["BL/CW-1001"] = bl_point
network.by_ref["BL/CW-1001"] = _key(bl_point)
allowance = 100.0  # kPa, D-053: control valve + liquid distributor + strainer, ASSUMED
eta = 0.75  # D-053, ASSUMED
for tag, t, flow, p_src, p_dst, src, dst in (
    ("P-1101A", 298.15, 250.0, 501.3, 580.0, "BL", "C-1101"),
    ("P-1101B", 298.15, 250.0, 501.3, 580.0, "BL", "C-1101"),
    ("P-1102A", 283.15, 100.0, 105.0, 570.0, "C-1102", "C-1101"),
    ("P-1102B", 283.15, 100.0, 105.0, 570.0, "C-1102", "C-1101"),
):
    rho = iapws.iapws95_rho(t, p_src * 1000.0)
    pv = iapws.iapws95_Psat(t) / 1000.0
    mu = mu_IAPWS(t, rho)
    m = flow * rho / 3600.0
    print(f"{tag}: {flow:g} m3/h water at {t - 273.15:g} C: rho {rho:.5g} kg/m3, p_vap {pv:.4g} "
          f"kPa(a), mu {mu * 1000:.4g} mPa s (IAPWS-95 / IAPWS 2008 viscosity, chemicals)")
    s, d = pump(tag, m, rho, mu, [src], [dst], {})
    static = d.elevation_target - s.elevation_target
    head = (sizing.pressure_head(p_dst - p_src, rho) + static + s.loss.head + d.loss.head
            + sizing.pressure_head(allowance, rho))
    npsh = sizing.npsh_available(p_src, pv, rho, s.elevation_target - s.elevation_pump,
                                 s.loss.head)
    power = sizing.hydraulic_power(m, head) / eta
    print(
        f"  H = ({p_dst:g} - {p_src:g}) kPa / (rho g) {sizing.pressure_head(p_dst - p_src, rho):.4g}"
        f" m + static {static:.4g} m + losses {s.loss.head + d.loss.head:.4g} m + allowance "
        f"{allowance:g} kPa {sizing.pressure_head(allowance, rho):.4g} m = {head:.4g} m; "
        f"NPSHa {npsh:.4g} m; P = m g H / {eta:g} = {power:.4g} kW"
    )
