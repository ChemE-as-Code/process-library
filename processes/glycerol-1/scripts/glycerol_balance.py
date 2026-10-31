"""Independent mass and energy balance of the glycerol-1 refinery (DESIGN.md D-006, D-007).

A sequential, specified-split balance: the reactors are full-conversion neutralisations
(process/reactions.yaml), every separator is a set of ASSUMED split and purity parameters
(PARAMETERS below, each with its decision), and the duties are lumped latent plus sensible heat
estimates with the property values in PROPS. Nothing here is a phase-equilibrium or
electrolyte calculation: core cannot yet qualify glycerol-water-methanol-NaCl mixtures (core
#315, #364, #365). The results are copied into process/flowsheet.yaml as `assumed` values with
this script as their source; cheme recalculates the reactor outlets and pass-through streams
itself (`cheme process propagate --fill`) and its balances must agree.

Run: cheme run scripts/glycerol_balance.py   (writes build/glycerol_balance.yaml, prints a summary)
"""
from __future__ import annotations

from pathlib import Path

# Molar masses, kg/kmol (IUPAC 2021 standard atomic weights; formulas in materials.yaml)
MW = {
    "GLY": 92.094, "MEOH": 32.042, "H2O": 18.015, "NAOME": 54.024, "FAME": 296.495,
    "NAOH": 39.997, "HCL": 36.461, "NACL": 58.443, "AC": 12.011,
}
# Element counts per formula, for the element balance
ELEM = {
    "GLY": {"C": 3, "H": 8, "O": 3}, "MEOH": {"C": 1, "H": 4, "O": 1}, "H2O": {"H": 2, "O": 1},
    "NAOME": {"C": 1, "H": 3, "Na": 1, "O": 1}, "FAME": {"C": 19, "H": 36, "O": 2},
    "NAOH": {"Na": 1, "O": 1, "H": 1},
    "HCL": {"H": 1, "Cl": 1}, "NACL": {"Na": 1, "Cl": 1}, "AC": {"C": 1},
}
COMPS = list(MW)

# Crude glycerol feed, mass fractions (D-004): glycerol layer of sodium-methylate catalysed
# soybean-oil transesterification, Thompson & He (2006): layer 16.16 g, of which glycerol by
# difference 10.96 g (Table 3), catalyst NaOCH3 0.46 g (Table 1), so methanol 4.74 g; fatty
# matter 7.98 % of the layer (Table 6, "fat"), taken out of the by-difference glycerol.
_LAYER, _GLY_BD, _CAT, _FAT = 16.16, 10.96, 0.46, 0.0798
FEED = {"MEOH": round((_LAYER - _GLY_BD - _CAT) / _LAYER, 5), "NAOME": round(_CAT / _LAYER, 5), "FAME": _FAT}
FEED["GLY"] = round(1.0 - sum(FEED.values()), 5)

PARAMETERS = {
    "product_kg_h": 1250.0,        # D-002: refined glycerol, 10 000 t/a at 8000 h/a (ASSUMED)
    "hcl_excess": 0.10,            # D-005: 10 % over the alkali (NaOH + soap) to reach pH ~3-4
    "hcl_wt": 0.32,                # D-005: commercial 32 wt% hydrochloric acid
    "naoh_wt": 0.50,               # D-005: 50 wt% caustic soda for the neutraliser
    "fa_to_layer": 0.97,           # D-006: fatty acids and FAME reporting to the fatty-acid layer
    "fa_layer_meoh": 0.05,         # D-006: methanol mass fraction of the fatty-acid layer
    "fa_layer_gly": 0.01,          # D-006: glycerol mass fraction of the fatty-acid layer
    "meoh_recovery": 0.995,        # D-007: methanol to the distillate of C-201
    "meoh_purity": 0.995,          # D-007: distillate methanol mass fraction (rest water)
    "reflux_ratio": 1.0,           # D-007: C-201 reflux ratio (ASSUMED)
    "evap_gly_carryover": 0.001,   # D-008: glycerol entrained into the evaporator condensate
    "evap_water_out": 0.01,        # D-008: water mass fraction of the dewatered glycerol (10 kPa(a), 403 K)
    "strip_steam": 0.10,           # D-009: live steam, kg per kg glycerol fed to the still
    "ejector_motive": 1.5,         # D-009: MP motive steam of the booster ejectors, kg per kg vapour drawn
    "still_distillate": 0.95,      # D-009: glycerol of the still feed to the distillate
    "still_overhead": 0.005,       # D-009: glycerol of the still feed lost to the vacuum condenser
    "product_water": 0.003,        # D-003: water mass fraction of the distillate and product
    "salt_crystals": 0.90,         # D-010: NaCl of the still residue separated as crystals
    "cake_liquor": 0.25,           # D-010: mother liquor held in the cake, kg per kg crystals
    "ac_dose": 0.002,              # D-011: activated carbon, kg per kg distilled glycerol
    "ac_holdup": 1.0,              # D-011: glycerol held in the spent carbon, kg per kg carbon
    "power_kwh_t": {"ACD": 10.0, "MRC": 5.0, "DEW": 10.0, "DST": 20.0, "BLC": 5.0},  # D-012
}

# Property values for the lumped duties (D-012); all at the stated basis, ASSUMED where marked
PROPS = {
    "dhvap_meoh": 35.21 / 32.042 * 1000,   # kJ/kg, 35.21 kJ/mol at the normal boiling point (NIST WebBook)
    "dhvap_water_vac": 2333.0,             # kJ/kg, saturated water at about 70 C (steam tables, IAPWS-IF97)
    "dhvap_water_still": 2380.0,           # kJ/kg, water evaporated near 50 C partial pressure (ASSUMED)
    "dhvap_gly": 85.0 / 92.094 * 1000,     # kJ/kg, 85 kJ/mol near 450 K (ASSUMED within the NIST WebBook range)
    "dh_neut": -55.8,                      # kJ/mol, NEUT1 and NEUT2, dilute-water value (ASSUMED, D-005)
    "cp": {"GLY": 2.43, "MEOH": 2.53, "H2O": 4.18, "NACL": 0.86, "FAME": 2.0,
           "NAOME": 2.0, "NAOH": 3.2, "HCL": 3.0, "AC": 0.7},  # kJ/(kg K), liquids near 298 K (ASSUMED for the lumps)
}

# c201_bot: about 93 wt% glycerol (salt-free) boils near 418-425 K at 1 atm (review
# 2026-10-28-pfd-lci-review#3), a few K more at 120 kPa(a) with salt: ASSUMED 425 K (D-007)
T = {"feed": 333.15, "hcl": 298.15, "c201_bot": 425.15, "evap": 403.15, "still": 448.15, "bleach": 363.15, "product": 313.15}


def total(s):
    return sum(s.values())


def add(a, b):
    out = dict(a)
    for k, v in b.items():
        out[k] = out.get(k, 0.0) + v
    return out


def sub(a, b):
    out = dict(a)
    for k, v in b.items():
        out[k] = out.get(k, 0.0) - v
        if out[k] < -1e-9:
            raise ValueError(f"negative {k}")
        out[k] = max(out[k], 0.0)
    return out


def scale(s, f):
    return {k: v * f for k, v in s.items()}


def cp_mix(s):
    return sum(PROPS["cp"][k] * v for k, v in s.items()) / total(s)


def balance(feed_kg_h):
    p = PARAMETERS
    st = {}
    st["S1"] = scale(FEED, feed_kg_h)
    n_cat = st["S1"]["NAOME"] / MW["NAOME"]
    n_hcl = (1 + p["hcl_excess"]) * n_cat
    m_hcl = n_hcl * MW["HCL"]
    st["S2"] = {"HCL": m_hcl, "H2O": m_hcl * (1 - p["hcl_wt"]) / p["hcl_wt"]}
    # R-101: NEUT1 (NaOCH3 + HCl -> NaCl + CH3OH), full conversion of the catalyst
    s3 = add(st["S1"], st["S2"])
    s3["NAOME"] = 0.0
    s3["HCL"] -= n_cat * MW["HCL"]
    s3["NACL"] = n_cat * MW["NACL"]
    s3["MEOH"] += n_cat * MW["MEOH"]
    st["S3"] = s3
    # V-102: fatty layer (fatty matter freed by the acid: split soaps, esters, glycerides)
    fa = p["fa_to_layer"] * s3["FAME"]
    layer = fa / (1 - p["fa_layer_meoh"] - p["fa_layer_gly"])
    st["S4"] = {"FAME": fa, "MEOH": p["fa_layer_meoh"] * layer, "GLY": p["fa_layer_gly"] * layer}
    st["S5"] = sub(s3, st["S4"])
    # R-102: NEUT2 neutralises the excess HCl with 50 wt% NaOH
    n_ex = st["S5"]["HCL"] / MW["HCL"]
    m_naoh = n_ex * MW["NAOH"]
    st["S6"] = {"NAOH": m_naoh, "H2O": m_naoh * (1 - p["naoh_wt"]) / p["naoh_wt"]}
    s7 = add(st["S5"], st["S6"])
    s7["HCL"] = 0.0
    s7["NAOH"] = 0.0
    s7["NACL"] += n_ex * MW["NACL"]
    s7["H2O"] += n_ex * MW["H2O"]
    st["S7"] = s7
    # C-201: methanol column
    d_meoh = p["meoh_recovery"] * s7["MEOH"]
    st["S8"] = {"MEOH": d_meoh, "H2O": d_meoh * (1 - p["meoh_purity"]) / p["meoh_purity"]}
    st["S9"] = sub(s7, st["S8"])
    # E-301: dewatering evaporator; all residual methanol to the vapour
    s9 = st["S9"]
    gly_v = p["evap_gly_carryover"] * s9["GLY"]
    rest = total(s9) - s9["H2O"] - s9["MEOH"] - gly_v       # concentrate without water
    water_c = rest * p["evap_water_out"] / (1 - p["evap_water_out"])
    st["S10"] = {"MEOH": s9["MEOH"], "GLY": gly_v, "H2O": s9["H2O"] - water_c}
    st["S11"] = sub(s9, st["S10"])
    # C-401: vacuum still with live steam
    s11 = st["S11"]
    st["S14"] = {"H2O": p["strip_steam"] * s11["GLY"]}
    g_d = p["still_distillate"] * s11["GLY"]
    st["S17"] = {"GLY": g_d, "H2O": g_d * p["product_water"] / (1 - p["product_water"])}
    g_o = p["still_overhead"] * s11["GLY"]
    st["S15"] = {"GLY": g_o, "H2O": s11["H2O"] + st["S14"]["H2O"] - st["S17"]["H2O"]}
    st["S16"] = sub(add(s11, st["S14"]), add(st["S17"], st["S15"]))
    # Vacuum system (D-009): the vapour left after the glycerol condenser E-402 cannot condense
    # on cooling water at 1.5 kPa(a); two booster ejectors on MP motive steam compress it to
    # 8 kPa(a), where the intercondenser E-403 condenses vapour and motive steam together
    st["S22"] = {"H2O": p["ejector_motive"] * total(st["S15"])}
    st["S15"] = add(st["S15"], st["S22"])
    # S-402: salt centrifuge on the still residue
    s16 = st["S16"]
    crystals = p["salt_crystals"] * s16["NACL"]
    mother = sub(s16, {"NACL": crystals})
    liquor = scale(mother, p["cake_liquor"] * crystals / total(mother))
    st["S12"] = add({"NACL": crystals}, liquor)
    st["S13"] = sub(mother, liquor)
    # V-501: activated carbon
    s17 = st["S17"]
    ac = p["ac_dose"] * total(s17)
    st["S18"] = {"AC": ac}
    held = scale(s17, p["ac_holdup"] * ac / total(s17))
    st["S19"] = add({"AC": ac}, held)
    st["S20"] = sub(s17, held)
    st["S21"] = dict(st["S20"])
    return st


def duties(st):
    pr = PROPS
    R = PARAMETERS["reflux_ratio"]
    q = {}
    d = st["S8"]
    vap = (1 + R) * (d["MEOH"] * pr["dhvap_meoh"] + d["H2O"] * 2257.0)
    # R-101 and R-102 adiabatic (D-005): mixing temperature plus the neutralisation heat
    n1 = st["S1"]["NAOME"] / MW["NAOME"]
    m3 = total(st["S3"])
    t0 = 298.15                                             # sensible enthalpy reference, K
    h_in = total(st["S1"]) * cp_mix(st["S1"]) * (T["feed"] - t0) + total(st["S2"]) * cp_mix(st["S2"]) * (T["hcl"] - t0)
    q["Q_NEUT1"] = -pr["dh_neut"] * n1 * 1000.0
    T["S3"] = t0 + (h_in + q["Q_NEUT1"]) / (m3 * cp_mix(st["S3"]))
    n2 = st["S6"]["NAOH"] / MW["NAOH"]
    q["Q_NEUT2"] = -pr["dh_neut"] * n2 * 1000.0
    h5 = total(st["S5"]) * cp_mix(st["S5"]) * (T["S3"] - t0) + total(st["S6"]) * cp_mix(st["S6"]) * (T["hcl"] - t0)
    T["S7"] = t0 + (h5 + q["Q_NEUT2"]) / (total(st["S7"]) * cp_mix(st["S7"]))
    q["Q_C201_REB"] = vap + total(st["S7"]) * cp_mix(st["S7"]) * (T["c201_bot"] - T["S7"])
    q["Q_C201_CND"] = vap
    v = st["S10"]
    lat = v["H2O"] * pr["dhvap_water_vac"] + v["MEOH"] * pr["dhvap_meoh"] + v["GLY"] * pr["dhvap_gly"]
    q["Q_E301"] = lat + total(st["S9"]) * cp_mix(st["S9"]) * (T["evap"] - T["c201_bot"])
    q["Q_E302"] = lat
    s11 = st["S11"]
    g_vap = st["S17"]["GLY"] + st["S15"]["GLY"]
    q["Q_C401_REB"] = (g_vap * pr["dhvap_gly"] + s11["H2O"] * pr["dhvap_water_still"]
                       + total(s11) * cp_mix(s11) * (T["still"] - T["evap"]))
    q["Q_E402"] = st["S17"]["GLY"] * pr["dhvap_gly"] + total(st["S17"]) * cp_mix(st["S17"]) * (T["still"] - T["bleach"])
    # intercondenser at 8 kPa(a): process vapour, live steam and motive steam (ASSUMED 2400 kJ/kg
    # with the motive steam's superheat after expansion)
    q["Q_E403"] = st["S15"]["H2O"] * 2400.0 + st["S15"]["GLY"] * pr["dhvap_gly"]
    q["Q_E501"] = total(st["S20"]) * cp_mix(st["S20"]) * (T["bleach"] - T["product"])
    q = {k: v / 3600.0 for k, v in q.items()}       # kJ/h -> kW
    prod_t_h = total(st["S21"]) / 1000.0
    for blk, kwh_t in PARAMETERS["power_kwh_t"].items():
        q[f"W_{blk}"] = kwh_t * prod_t_h
    return q


def elements(s):
    out = {}
    for k, m in s.items():
        for e, n in ELEM[k].items():
            out[e] = out.get(e, 0.0) + m / MW[k] * n
    return out


def main():
    probe = balance(1000.0)
    feed = 1000.0 * PARAMETERS["product_kg_h"] / total(probe["S21"])
    st = balance(feed)
    q = duties(st)
    ins = ["S1", "S2", "S6", "S14", "S18", "S22"]
    outs = ["S4", "S8", "S10", "S12", "S13", "S15", "S19", "S21"]
    m_in = sum(total(st[s]) for s in ins)
    m_out = sum(total(st[s]) for s in outs)
    e_in, e_out = {}, {}
    for s in ins:
        e_in = add(e_in, elements(st[s]))
    for s in outs:
        e_out = add(e_out, elements(st[s]))
    lines = ["# generated by scripts/glycerol_balance.py; kg/h and mass fractions", "streams:"]
    for sid, s in st.items():
        m = total(s)
        comp = {k: round(v / m, 8) for k, v in s.items() if v > 1e-9}
        lines.append(f"  {sid}: {{flow: {m:.2f}, composition: {comp}}}")
    lines.append("duties_kW:")
    for k, v in q.items():
        lines.append(f"  {k}: {v:.1f}")
    out = Path("build/glycerol_balance.yaml")
    out.parent.mkdir(exist_ok=True)
    out.write_text("\n".join(lines) + "\n")
    print(f"feed {feed:.2f} kg/h, product {total(st['S21']):.2f} kg/h, mass in {m_in:.3f} out {m_out:.3f}")
    print("elements in/out kmol/h:", {e: (round(e_in[e], 5), round(e_out.get(e, 0), 5)) for e in e_in})
    gly_rec = st["S21"]["GLY"] / st["S1"]["GLY"]
    print(f"glycerol recovery {gly_rec:.4f}")
    heat = (q["Q_C201_REB"] + q["Q_E301"] + q["Q_C401_REB"]) / (total(st["S21"]) / 1000)
    print(f"indirect steam heat {heat:.1f} kWh/t product; live steam {st['S14']['H2O']:.1f} kg/h; "
          f"motive steam {st['S22']['H2O']:.1f} kg/h")
    print(f"S3 {T['S3']:.2f} K, S7 {T['S7']:.2f} K")
    # the values process/flowsheet.yaml cites from this script (balance-output contract): the
    # streams and duties of build/glycerol_balance.yaml, the S3 and S7 temperatures
    flowsheet = {sid: {"flow": {"value": total(s), "basis": "mass"},
                       "composition": {"values": {k: v / total(s) for k, v in s.items()},
                                       "basis": "mass_fraction"}}
                 for sid, s in st.items()}
    flowsheet["S3"]["temperature"], flowsheet["S7"]["temperature"] = T["S3"], T["S7"]
    flowsheet.update({qid: {"duty": q[k]} for qid, k in {
        "Q1": "Q_C201_REB", "Q2": "Q_C201_CND", "Q3": "Q_E301", "Q4": "Q_E302",
        "Q5": "Q_C401_REB", "Q6": "Q_E402", "Q7": "Q_E403", "Q8": "Q_E501"}.items()})
    write_balance_output({"design": flowsheet})
    print("\n".join(lines))


def write_balance_output(cases):
    """With BALANCE_OUTPUT set, write the values the flowsheet cites from this script as JSON.

    The process library's balance-output contract (docs/adr/0024 of the library): case ->
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
