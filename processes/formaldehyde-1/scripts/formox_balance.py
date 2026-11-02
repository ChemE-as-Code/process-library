"""Heat and material balance of the formaldehyde-1 Formox loop (concept stage).

Provenance only: the stream values it prints are entered in process/flowsheet.yaml as
`assumed` with this script as source, where cheme cannot compute them (the absorber, the
liquid enthalpies, the recycle loop). Reactor and ECS outlets, mixers and the splitter are
recomputed by `cheme process propagate`, which must reproduce these numbers.

Every input is in INPUTS with its basis (DESIGN.md decision ids). Run: python3 scripts/formox_balance.py
"""

import math

R = 8.314462618  # kJ/(kmol K)
NM3 = 22.414     # Nm3/kmol at 273.15 K, 101.325 kPa (ideal gas)

MW = {"CH3OH": 32.0419, "O2": 31.9988, "HCHO": 30.026, "H2O": 18.0153, "N2": 28.0134,
      "AR": 39.948, "CO": 28.0101, "CO2": 44.0095, "DME": 46.0684}
# ideal-gas formation enthalpy at 298.15 K (kJ/kmol) and cp/R polynomials, as in
# process/materials.yaml (chemicals: ATcT, Poling 5th ed.)
HF = {"CH3OH": -200700.0, "O2": 0.0, "HCHO": -109160.0, "H2O": -241822.0, "N2": 0.0,
      "AR": 0.0, "CO": -110525.0, "CO2": -393474.0, "DME": -184020.0}
CP = {"CH3OH": [4.714, -0.006986, 4.211e-05, -4.443e-08, 1.535e-11],
      "O2": [3.33121, 3.73673e-05, 2.68405e-06, -2.58548e-09, 7.32021e-13],
      "HCHO": [3.96137, -0.00377287, 2.16401e-05, -2.1261e-08, 6.89138e-12],
      "H2O": [3.95742, -0.000363702, 2.42862e-06, -1.27073e-09, 2.12761e-13],
      "N2": [3.539, -0.000261, 7e-08, 1.57e-09, -9.9e-13],
      "AR": [2.5],
      "CO": [3.912, -0.003913, 1.182e-05, -1.3e-08, 5.15e-12],
      "CO2": [3.259, 0.001356, 1.502e-05, -2.374e-08, 1.056e-11],
      "DME": [4.361, 0.00607, 2.899e-05, -3.581e-08, 1.282e-11]}

INPUTS = {
    "product_kg_h": 20000.0,        # D-002 ASSUMED capacity: 20 t/h formalin
    "w_hcho": 0.50,                 # D-002 product 50 wt% HCHO (BREF LVOC 2017 s. 6.2.3: 37-60 wt%)
    "yield": 0.930,                 # D-004 methanol to HCHO in product (BREF Table 6.10: 91-94 %)
    "conversion": 0.993,            # D-004 methanol, plant (BREF s. 6.2.3: > 99 mol%)
    "dme_kmol_h": 1.0,              # D-004 ASSUMED DME make (vent 6-10000 mg/Nm3, BREF Table 6.6)
    "y_meoh_reactor": 0.085,        # D-005 ASSUMED reactor inlet methanol (EPA 1991: 5-10 vol%)
    "y_o2_offgas": 0.060,           # D-005 absorber off-gas O2 (BREF Table 6.6: 5-7 %)
    "hcho_offgas_mg_nm3": 300.0,    # D-006 (BREF Table 6.6: 150-700)
    "meoh_offgas_mg_nm3": 1000.0,   # D-006 (BREF Table 6.6: 500-2000)
    "air_h2o": 0.010,               # D-005 ASSUMED humid air 1.0 mol% water
    "t_air": 298.15, "t_meoh": 298.15, "t_pw": 298.15,
    "p_suction": 100.5, "p_blower": 150.0,  # D-005 ASSUMED kPa(a)
    "eta_blower": 0.75, "eta_motor": 0.95,  # D-007 ASSUMED
    "t_offgas": 303.15, "p_offgas": 112.0,  # D-006 ASSUMED absorber top
    "t_reactor_out": 553.15,                # D-005 ASSUMED (BREF 270-430 C catalyst)
    "t_vap_hot_out": 403.15,                # D-005 ASSUMED reaction gas to absorber
    "t_product": 333.15,                    # D-006 ASSUMED kept warm against paraform
    "t_stack": 423.15,                      # D-008 ASSUMED
    "ecs_conv": {"CO": 0.998, "HCHO": 0.995, "CH3OH": 0.995, "DME": 0.990},  # D-008 ASSUMED
    # D-006: liquid-side heats (kJ/kmol): water and methanol vaporisation at 298 K
    # (NIST WebBook), heat of solution of HCHO gas in water ASSUMED (order of magnitude, to source)
    "dhvap_h2o": 43990.0, "dhvap_meoh": 37430.0, "dhsol_hcho": 62000.0,
    "cp_liq_kj_kgk": 3.3,                   # ASSUMED formalin 50 wt%
}
AIR_DRY = {"N2": 0.78084, "O2": 0.20946, "AR": 0.00934}  # dry air, CO2 neglected (D-005)


def cp_int(c, t0, t1):
    """integral of cp dT (kJ/kmol) from t0 to t1."""
    def f(t):
        return R * sum(a * t ** (i + 1) / (i + 1) for i, a in enumerate(c))
    return f(t1) - f(t0)


def h_gas(flows, t):
    return sum(n * (HF[k] + cp_int(CP[k], 298.15, t)) for k, n in flows.items())


def cp_mix(flows, t):
    return sum(n * R * sum(a * t ** i for i, a in enumerate(CP[k])) for k, n in flows.items())


def t_for_h(flows, h, guess):
    t = guess
    for _ in range(50):
        t -= (h_gas(flows, t) - h) / cp_mix(flows, t)
    return t


def add(*ds):
    out = {}
    for d in ds:
        for k, v in d.items():
            out[k] = out.get(k, 0.0) + v
    return out


def scale(d, f):
    return {k: v * f for k, v in d.items()}


def main():
    I = INPUTS
    s = sum(AIR_DRY.values())
    air_frac = {k: v / s for k, v in AIR_DRY.items()}
    hcho_prod = I["product_kg_h"] * I["w_hcho"] / MW["HCHO"]
    meoh_feed = hcho_prod / I["yield"]
    meoh_conv = meoh_feed * I["conversion"]
    meoh_left = meoh_feed - meoh_conv
    z_h = I["hcho_offgas_mg_nm3"] * 1e-6 * NM3 / MW["HCHO"]
    z_m = I["meoh_offgas_mg_nm3"] * 1e-6 * NM3 / MW["CH3OH"]
    z_w = math.exp(16.3872 - 3885.70 / (I["t_offgas"] - 273.15 + 230.170)) / I["p_offgas"]  # Antoine, kPa
    dme = I["dme_kmol_h"]

    v = 1000.0
    for _ in range(50):
        hcho_formed = hcho_prod + v * z_h
        co = meoh_conv - hcho_formed - 2 * dme
        xi1, xi2, xi3 = hcho_formed + co, co, dme
        o2_used = 0.5 * xi1 + 0.5 * xi2
        # off-gas O2 fraction: (a_O*A - o2_used) / V = y, V = NC / (1 - zw - zm - zh)
        cond = 1 - z_w - z_m - z_h
        # NC = A + co + dme - o2_used (air dry flows sum to A)
        y = I["y_o2_offgas"]
        a = (o2_used * (1 - y / cond) + y / cond * (co + dme)) / (air_frac["O2"] - y / cond)
        nc = a + co + dme - o2_used
        v = nc / cond
    air = scale(air_frac, a)
    air["H2O"] = a * I["air_h2o"] / (1 - I["air_h2o"])
    vent_nc = {"N2": air["N2"], "AR": air["AR"], "O2": air["O2"] - o2_used, "CO": co, "DME": dme}
    offgas_frac = {k: n / v for k, n in vent_nc.items()}
    offgas_frac.update({"H2O": z_w, "CH3OH": z_m, "HCHO": z_h})
    # recycle R: (meoh_feed + R z_m) / (A_wet + R + meoh_feed) = y_meoh
    ym = I["y_meoh_reactor"]
    a_wet = sum(air.values())
    rec = (ym * (a_wet + meoh_feed) - meoh_feed) / (z_m - ym)
    recycle = scale(offgas_frac, rec)
    vent = scale(offgas_frac, v)
    gas3 = add(air, recycle)                       # blower suction (S2) and discharge (S3)
    feed_r = add(gas3, {"CH3OH": meoh_feed})       # reactor inlet (S6)
    x_pass = meoh_conv / feed_r["CH3OH"]
    react = {"CH3OH": -meoh_conv, "O2": -o2_used, "HCHO": hcho_formed, "CO": co, "DME": dme,
             "H2O": xi1 + xi2 + xi3}
    out_r = add(feed_r, react)                     # S8
    meoh_prod = meoh_left - v * z_m
    w_prod = (I["product_kg_h"] - hcho_prod * MW["HCHO"] - meoh_prod * MW["CH3OH"]) / MW["H2O"]
    product = {"HCHO": hcho_prod, "CH3OH": meoh_prod, "H2O": w_prod}
    pw = w_prod + (rec + v) * z_w - out_r["H2O"]

    # blower
    t_in = t_for_h(gas3, h_gas(air, I["t_air"]) + h_gas(recycle, I["t_offgas"]), 300)
    n_tot = sum(gas3.values())
    cpm = cp_mix(gas3, t_in) / n_tot
    k = cpm / (cpm - R)
    t2s = t_in * (I["p_blower"] / I["p_suction"]) ** ((k - 1) / k)
    w_s = h_gas(gas3, t2s) - h_gas(gas3, t_in)
    w = w_s / I["eta_blower"]
    t_out = t_for_h(gas3, h_gas(gas3, t_in) + w, t2s)
    p_shaft = w / 3600
    p_el = p_shaft / I["eta_motor"]
    # vaporiser E101: hot S8 (t_reactor_out) -> S9 (t_vap_hot_out); cold S5 -> S6
    q_e101 = h_gas(out_r, I["t_reactor_out"]) - h_gas(out_r, I["t_vap_hot_out"])
    h_s5 = h_gas(gas3, t_out) + meoh_feed * (HF["CH3OH"] - I["dhvap_meoh"])  # liquid at 298 K
    t6 = t_for_h(feed_r, h_s5 + q_e101, 400)
    # reactor R101: heat to hot oil (positive = released)
    q_r101 = h_gas(feed_r, t6) - h_gas(out_r, I["t_reactor_out"])
    # absorber C201: cooling duty
    offgas_all = scale(offgas_frac, rec + v)
    h_in = h_gas(out_r, I["t_vap_hot_out"]) + pw * (HF["H2O"] - I["dhvap_h2o"]) \
        + pw * MW["H2O"] * 4.18 * (I["t_pw"] - 298.15)
    h_prod = hcho_prod * (HF["HCHO"] - I["dhsol_hcho"]) + meoh_prod * (HF["CH3OH"] - I["dhvap_meoh"]) \
        + w_prod * (HF["H2O"] - I["dhvap_h2o"]) + I["product_kg_h"] * I["cp_liq_kj_kgk"] * (I["t_product"] - 298.15)
    q_c201 = h_in - h_gas(offgas_all, I["t_offgas"]) - h_prod
    # ECS R301
    c = I["ecs_conv"]
    e = {kk: vent[kk] * c[kk] for kk in c}
    ecs = {"CO": -e["CO"], "HCHO": -e["HCHO"], "CH3OH": -e["CH3OH"], "DME": -e["DME"],
           "O2": -(0.5 * e["CO"] + e["HCHO"] + 1.5 * e["CH3OH"] + 3 * e["DME"]),
           "CO2": e["CO"] + e["HCHO"] + e["CH3OH"] + 2 * e["DME"],
           "H2O": e["HCHO"] + 2 * e["CH3OH"] + 3 * e["DME"]}
    stack = add(vent, ecs)
    q_r301 = h_gas(vent, I["t_offgas"]) - h_gas(stack, I["t_stack"])

    def show(name, d, t=None):
        tot = sum(d.values())
        mass = sum(n * MW[kk] for kk, n in d.items())
        comp = ", ".join(f"{kk}: {n / tot:.6f}" for kk, n in d.items() if n > 1e-12)
        ts = f" T={t:.2f} K" if t else ""
        print(f"{name}: {tot:.3f} kmol/h, {mass:.1f} kg/h{ts}\n   {{{comp}}}")

    print(f"methanol feed {meoh_feed:.3f} kmol/h = {meoh_feed * MW['CH3OH']:.1f} kg/h; "
          f"per-pass conversion {x_pass:.7f}")
    sel = {"HCHO": hcho_formed / meoh_conv, "CO": co / meoh_conv, "DME": dme / meoh_conv}
    print("selectivity per kmol methanol converted:", {kk: round(vv, 7) for kk, vv in sel.items()})
    print(f"dry air {a:.2f} kmol/h, recycle {rec:.2f} kmol/h, vent {v:.2f} kmol/h, "
          f"split to recycle {rec / (rec + v):.6f}; vent {v * NM3:.0f} Nm3/h = "
          f"{v * NM3 / (hcho_prod * MW['HCHO'] / 1000):.0f} Nm3/t HCHO")
    show("S1 air", air, I["t_air"])
    show("S10 recycle", recycle, I["t_offgas"])
    show("S3 blower out", gas3, t_out)
    show("S6 reactor in", feed_r, t6)
    show("S8 reactor out", out_r, I["t_reactor_out"])
    show("S11 off-gas", offgas_all, I["t_offgas"])
    show("S13 vent to ECS", vent, I["t_offgas"])
    show("S14 stack", stack, I["t_stack"])
    show("S12 product", product, I["t_product"])
    print(f"process water {pw:.3f} kmol/h = {pw * MW['H2O']:.1f} kg/h")
    print(f"inlet O2 {feed_r['O2'] / sum(feed_r.values()):.4f}, blower T in {t_in:.2f} out {t_out:.2f}")
    print(f"K101 shaft {p_shaft:.1f} kW, electric {p_el:.1f} kW")
    print(f"E101 duty {q_e101 / 3600:.1f} kW; R101 heat to hot oil {q_r101 / 3600:.1f} kW; "
          f"C201 cooling {q_c201 / 3600:.1f} kW; R301 heat to steam {q_r301 / 3600:.1f} kW")
    for kk in ("CO", "HCHO", "CH3OH", "DME"):
        print(f"stack {kk}: {stack[kk] * MW[kk] * 1e6 / (sum(stack.values()) * NM3):.2f} mg/Nm3 (wet)")
    # the values process/flowsheet.yaml cites from this script (balance-output contract), by the
    # flowsheet's stream ids: its S10 is the absorber off-gas (printed "S11"), its S14 the
    # formalin product (printed "S12"); compositions as mole fractions
    def state(d):
        return {"flow": {"value": sum(n * MW[kk] for kk, n in d.items()), "basis": "mass"},
                "composition": {"values": {kk: n / sum(d.values()) for kk, n in d.items()},
                                "basis": "mole_fraction"}}

    write_balance_output({"design": {
        "S1": state(air), "S2": {"temperature": t_in}, "S3": {"temperature": t_out},
        "S4": {"flow": {"value": meoh_feed * MW["CH3OH"], "basis": "mass"}},
        "S6": {"temperature": t6}, "S9": {"flow": {"value": pw * MW["H2O"], "basis": "mass"}},
        "S10": state(offgas_all), "S14": state(product),
        "Q1": {"duty": p_el}, "Q3": {"duty": q_r101 / 3600}, "Q4": {"duty": q_r301 / 3600},
        "Q5": {"duty": q_c201 / 3600}, "Q6": {"duty": q_e101 / 3600}}})
    mass_in = (sum(n * MW[kk] for kk, n in air.items()) + meoh_feed * MW["CH3OH"] + pw * MW["H2O"])
    mass_out = I["product_kg_h"] + sum(n * MW[kk] for kk, n in vent.items())
    print(f"plant mass in {mass_in:.2f} out {mass_out:.2f} kg/h")


def write_balance_output(cases):
    """With BALANCE_OUTPUT set, write the values the flowsheet cites from this script as JSON.

    The process library's balance-output contract (docs/adr/0027 of the library): case ->
    stream id -> quantity, in the flowsheet's units and basis. The library's
    scripts/check_balance_scripts.py re-runs this script and compares them with
    process/flowsheet.yaml.
    """
    import json
    import os
    from pathlib import Path

    target = os.environ.get("BALANCE_OUTPUT")
    if target:
        doc = {"contract": "balance-output/1", "script": f"scripts/{Path(__file__).name}",
               "cases": cases}
        Path(target).write_text(json.dumps(doc, indent=1, default=float), encoding="utf-8")


if __name__ == "__main__":
    main()
