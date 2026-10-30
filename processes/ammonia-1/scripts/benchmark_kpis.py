"""Key performance indicators of the final ammonia-1 design (runs/benchmark-kpis.md).

Reads only the design's own files: the stream table of process/flowsheet.yaml (through
`cheme process streams --json`), the component data of process/materials.yaml and the LCI
dataset lca/dataset.yaml. No reference or benchmark value is used. Heating values are the
lower heating values at 298.15 K from the formation enthalpies of materials.yaml (water as
vapour); steam enthalpies from IAPWS-IF97 (chemicals.iapws). Run: cheme run scripts/benchmark_kpis.py
"""

import json
import subprocess

import yaml
from chemicals import iapws

MAT = yaml.safe_load(open("process/materials.yaml"))
COMP = {c["id"]: c for c in MAT["components"]}
DATASET = yaml.safe_load(open("lca/dataset.yaml"))
EX = {e["key"]: e for e in DATASET["exchanges"]}
STREAMS = {
    s["id"]: s
    for s in json.loads(
        subprocess.run(["cheme", "process", "streams", "--json"], capture_output=True, text=True, check=True).stdout
    )["streams"]
}

# Lower heating value per kmol at 298.15 K, products CO2(g), H2O(g), N2: -(sum nu dHf)
HF = {k: c["ideal_gas"]["dHf_298"] for k, c in COMP.items()}  # kJ/kmol
COMBUSTION = {  # products per kmol of fuel: (CO2, H2O)
    "CH4": (1, 2), "C2H6": (2, 3), "C3H8": (3, 4), "H2": (0, 1), "CO": (1, 0), "NH3": (0, 1.5),
}
LHV_KMOL = {k: HF[k] - (c * HF["CO2"] + h * HF["H2O"]) for k, (c, h) in COMBUSTION.items()}  # kJ/kmol


def state(sid, key):
    return STREAMS[sid]["state"][key]["value"]


def moles(sid):
    """Molar flow (kmol/h) and mole fractions of a material stream."""
    comp = STREAMS[sid]["state"]["composition"]["values"]
    mw = sum(x * COMP[k]["molar_mass"] for k, x in comp.items())
    return state(sid, "flow") / mw, comp, mw


def lhv_mw(sid):
    n, x, _ = moles(sid)
    return n * sum(x.get(k, 0.0) * v for k, v in LHV_KMOL.items()) / 3.6e6  # kJ/h -> MW


def kg_of(sid, comp):
    n, x, _ = moles(sid)
    return n * x.get(comp, 0.0) * COMP[comp]["molar_mass"]


def duty(sid):
    return state(sid, "duty")  # kW


def h_iapws97(T, P_kPa):
    """Specific enthalpy kJ/kg, IAPWS-IF97 region 1 (liquid) or 2 (vapour)."""
    R = iapws.iapws97_R / 1000.0
    P = P_kPa / 1000.0  # MPa
    region = iapws.iapws97_identify_region_TP(T, P * 1e6)
    if region == 1:
        tau, pi = 1386.0 / T, P / 16.53
        return R * T * tau * iapws.iapws97_dG_dtau_region1(tau, pi)
    if region == 2:
        tau, pi = 540.0 / T, P
        return R * T * tau * (iapws.iapws97_dG0_dtau_region2(tau, pi) + iapws.iapws97_dGr_dtau_region2(tau, pi))
    raise ValueError(f"region {region}")


nh3_kg = EX["product:NH3"]["amount"]  # kg/h, S60
nh3_t = nh3_kg / 1000.0
per_t = lambda mw: mw * 3.6 / nh3_t  # MW -> GJ per t NH3

print("product NH3 S60 kg/h", nh3_kg, "contained NH3 kg/h", kg_of("S60", "NH3"))
print("LHV kJ/kmol", {k: round(v) for k, v in LHV_KMOL.items()})
_, x1, mw1 = moles("S1")
lhv_ng_kg = sum(x1.get(k, 0) * LHV_KMOL[k] for k in COMBUSTION) / mw1 / 1000.0  # MJ/kg
print(f"natural gas S1: M {mw1:.4f} kg/kmol, LHV {lhv_ng_kg:.4f} MJ/kg")

ng = {s: lhv_mw(s) for s in ("S1", "S2", "S3", "S59")}
print("LHV MW", {k: round(v, 2) for k, v in ng.items()})
power_ids = EX["feed:POWER"]["streams"]
power_mw = sum(duty(q) for q in power_ids) / 1000.0
print("power MW", round(power_mw, 4), "dataset kWh/h", EX["feed:POWER"]["amount"])

h_steam = h_iapws97(state("S68", "temperature"), state("S68", "pressure"))
h_dmw = h_iapws97(state("S70", "temperature"), state("S70", "pressure"))
h_ref = h_iapws97(298.15, 101.325)
h_bd = h_iapws97(state("S69", "temperature"), state("S69", "pressure"))
steam_kg = state("S68", "flow")
steam_mw = steam_kg * (h_steam - h_dmw) / 3.6e6
print(f"steam S68 {steam_kg} kg/h h {h_steam:.2f}; DMW S70 h {h_dmw:.2f}; liquid 298.15 K 1 atm h {h_ref:.2f}; blowdown h {h_bd:.2f}")
print(f"steam export above DMW: {steam_mw:.3f} MW = {per_t(steam_mw):.4f} GJ/t ({(h_steam - h_dmw) / 1000:.5f} MJ/kg)")
ex_steam = DATASET["allocation"]["properties"]["STEAM"]["exergy"]
print(f"steam export exergy (D-021, {ex_steam} kJ/kg): {steam_kg * ex_steam / 1e6 / nh3_t:.4f} GJ/t")
bd_mw = state("S69", "flow") * (h_bd - h_dmw) / 3.6e6
print(f"blowdown S69 enthalpy above DMW: {bd_mw:.3f} MW = {per_t(bd_mw):.4f} GJ/t (not counted as export)")
lp_mw = duty("Q29") / 1000.0
print(f"LP steam Q29 internal: {lp_mw:.4f} MW")

feed_fuel = per_t(ng["S1"])
gross = per_t(ng["S1"] + power_mw)
net = per_t(ng["S1"] + power_mw - steam_mw)
print(f"KPI1 net {net:.3f}  KPI2 gross {gross:.3f}  KPI3 NG feed+fuel {feed_fuel:.3f} GJ/t")
print(f"  feed S3 {per_t(ng['S3']):.3f}, fuel S2 {per_t(ng['S2']):.3f}, tail gas S59 (internal) {per_t(ng['S59']):.3f}, power {per_t(power_mw):.3f}")
print(f"  fired LHV S2+S59 {ng['S2'] + ng['S59']:.2f} MW")

co2_s28, co2_s87 = kg_of("S28", "CO2"), kg_of("S87", "CO2")
co2_proc = co2_s28 + co2_s87
co2_vent_ds = EX["product:CO2V"]["amount"] * EX["product:CO2V"]["composition"]["fractions"]["CO2"]
co2_stack = kg_of("S67", "CO2")
co2_stack_ds = EX["product:STACK"]["amount"] * EX["product:STACK"]["composition"]["fractions"]["CO2"]
co2_air = kg_of("S12", "CO2") + kg_of("S61", "CO2")
co2_air_proc = kg_of("S12", "CO2")
co2_ng = kg_of("S1", "CO2")
co2_ng_feed = kg_of("S3", "CO2")
print(f"process CO2: S28 {co2_s28:.1f} + S87 {co2_s87:.1f} = {co2_proc:.1f} kg/h (dataset {co2_vent_ds:.1f}) -> {co2_proc / nh3_kg:.4f} t/t")
print(f"  of which NG feed CO2 (S3) {co2_ng_feed:.1f}, process-air CO2 (S12) {co2_air_proc:.1f} kg/h; formed and removed {(co2_proc - co2_ng_feed - co2_air_proc) / nh3_kg:.4f} t/t")
print(f"  CO2 left in treated gas S27 (to methanation) {kg_of('S27', 'CO2'):.1f} kg/h")
print(f"stack CO2 S67 {co2_stack:.1f} kg/h (dataset {co2_stack_ds:.1f}) -> {co2_stack / nh3_kg:.4f} t/t")
co2_total = EX["emission:CO2"]["amount"]
print(f"KPI5 direct CO2 {co2_total:.1f} kg/h -> {co2_total / nh3_kg:.4f} t/t; atmospheric CO2 in air {co2_air:.1f} kg/h ({co2_air / nh3_kg:.5f} t/t); NG CO2 {co2_ng:.1f} kg/h")

n_fg, x_fg, _ = moles("S67")
dry = n_fg * (1.0 - x_fg["H2O"])
print(f"flue gas S67 {n_fg:.1f} kmol/h, dry {dry:.1f} kmol/h = {dry * 22.414:.0f} m3(n)/h dry (273.15 K, 101.325 kPa); O2 dry {x_fg['O2'] / (1 - x_fg['H2O']) * 100:.2f} vol%; NOx in S67: {x_fg.get('NO', 'no component')}")

n_in, x_in, _ = moles("S42")
n_out, x_out, _ = moles("S43")
print(f"converter S42 {state('S42', 'pressure')} kPa(a), {state('S42', 'temperature')} K; S43 {state('S43', 'pressure')} kPa(a)")
nh3_formed = n_out * x_out["NH3"] - n_in * x_in["NH3"]
syn_in = n_in * (x_in["H2"] + x_in["N2"])
print(f"n_in {n_in:.1f}, n_out {n_out:.1f} kmol/h; NH3 formed {nh3_formed:.1f} kmol/h (extent x2)")
print(f"conversion H2+N2 basis {2 * nh3_formed / syn_in * 100:.2f} %; H2 {1.5 * nh3_formed / (n_in * x_in['H2']) * 100:.2f} %; N2 {0.5 * nh3_formed / (n_in * x_in['N2']) * 100:.2f} %")
print(f"total gas basis (H2+N2 consumed / all gas in) {2 * nh3_formed / n_in * 100:.2f} %; mole reduction {(n_in - n_out) / n_in * 100:.2f} %")
print(f"NH3 mol% in {x_in['NH3'] * 100:.3f} out {x_out['NH3'] * 100:.3f}; H2/N2 in {x_in['H2'] / x_in['N2']:.4f}")
