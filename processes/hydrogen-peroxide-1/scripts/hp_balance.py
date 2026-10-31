"""Steady-state mass and energy balance of the hydrogen-peroxide-1 anthraquinone (AO) process concept.

Provenance only (DESIGN.md D-006): the stream values of process/flowsheet.yaml that cheme cannot
calculate (separator outlets, duties) come from this script and are entered there as ASSUMED
with the decision ids. Run: cheme run scripts/hp_balance.py [--yaml]

Every specification below is a design choice (ASSUMED) or a sourced fact; the decision id says
which. Standard library only. Units: kg/h, kmol/h, kW, K, kPa(a).
"""
import sys

# --- molar masses (kg/kmol), IUPAC atomic weights
M = {"H2": 2.01588, "O2": 31.9988, "N2": 28.0134, "AR": 39.948, "H2O": 18.01528,
     "H2O2": 34.01468, "EAQ": 236.2652, "EAHQ": 238.2811, "TMB": 120.1916,
     "DIBC": 144.2545, "AL2O3": 101.9613}
C_FRAC = {"TMB": 9 * 12.0107 / M["TMB"], "DIBC": 9 * 12.0107 / M["DIBC"]}

# --- specifications
P_H2O2 = 50_000e3 / 8000          # kg/h H2O2 (100 %) in the product: 50 kt/a, 8000 h/a (D-002)
W_PROD = 0.50                      # product H2O2 mass fraction (D-002)
W_CRUDE = 0.40                     # crude H2O2 from the extractor, BREF 20-50 wt% (D-008)
CONV_HYD = 0.45                    # EAQ hydrogenated per pass, BREF < 60 % (D-005)
CONV_OXD = 1.0                     # EAHQ oxidised (D-005)
F_EXT = 0.97                       # H2O2 recovered into the crude (D-008)
X_EAQ, X_H2O_WS = 0.140, 0.0015    # WS to hydrogenation: EAQ and water mass fractions (D-004)
TMB_DIBC = (0.6, 0.4)              # solvent mass split (D-004)
RHO_WS = 930.0                     # kg/m3 WS (D-004)
X_H2O_RAF = 0.0030                 # water in the raffinate WS (D-008)
H2_VENT = 0.01                     # fraction of the H2 feed vented unreacted (D-005)
VENT_TMB = 0.100 / C_FRAC["TMB"]   # kg/h TMB in the H2 vent: 100 g C/h, BREF Table 12.2 (D-009)
O2_EXCESS = 0.30                   # excess O2 over the stoichiometric need, BREF 20-40 % (D-007)
AIR = {"N2": 0.78084, "O2": 0.20946, "AR": 0.00934}   # dry air, mole fractions (CO2 in N2) (D-007)
Y_OX = {"H2O": 0.018, "TMB": 0.0020, "DIBC": 0.0001}  # oxidiser off-gas, 328 K, 350 kPa (D-007)
Y_CD = {"H2O": 0.0165, "TMB": 0.00135, "DIBC": 0.00003}  # after the condenser, 308 K (D-009)
VOC_OUT = 20.0                     # mg C/Nm3 at the adsorber outlet, BREF Table 12.8 (D-009)
STEAM_PER_SOLV = 5.0               # kg steam/kg solvent desorbed, BREF 4-6 (D-009)
STEAM_EJ = 0.100 * P_H2O2          # kg/h motive steam of the WS dryer ejector (D-010)
SOL_W = {"TMB": 57e-6, "DIBC": 600e-6}  # dissolved organics in aqueous effluents, mass frac (D-011)
CRUDE_ORG = {"DIBC": 1500e-6, "TMB": 100e-6}  # dissolved organics in the crude (D-008)
PUR_REMOVAL = 0.95                 # organics removed from the crude by the solvent wash (D-008)
H2O2_DRYW = 0.005                  # H2O2 mass fraction in the water removed by the WS dryer (D-008)
H2O2_DIST = 0.0005                 # H2O2 mass fraction in the concentrator distillate (D-010)
EAQ_LOSS = 1.0e-3 * P_H2O2         # kg/h quinone degraded, BREF 0.7-1.6 kg/t (D-011)
ALU = 6.0e-3 * P_H2O2              # kg/h activated alumina, BREF 4-20 kg/t (D-011)
SOLV_SPENT = 2.0e-3 * P_H2O2       # kg/h solvent leaving on the spent alumina (D-011)
DH = {"HYD": -110.3e3, "HPD": -383.88e3, "OXD": -77.5e3}  # kJ/kmol (D-005)
NM3 = 22.414                       # Nm3/kmol (0 C, 1 atm)


def add(*ss):
    out = {}
    for s in ss:
        for k, v in s.items():
            out[k] = out.get(k, 0.0) + v
    return out


def scale(s, f):
    return {k: v * f for k, v in s.items()}


def tot(s):
    return sum(s.values())


def mol(s):
    return {k: v / M[k] for k, v in s.items()}


def from_mol(n):
    return {k: v * M[k] for k, v in n.items()}


def ws_spec(w):
    sol = 1.0 - X_EAQ - X_H2O_WS
    return {"EAQ": X_EAQ * w, "TMB": TMB_DIBC[0] * sol * w, "DIBC": TMB_DIBC[1] * sol * w,
            "H2O": X_H2O_WS * w}


def solve():
    w = 700e3  # WS to hydrogenation, kg/h; scaled to the product rate
    for _ in range(60):
        r = balance(w)
        w *= P_H2O2 / r["S20"]["H2O2"]
    return r


def balance(w):
    s = {}
    s["S04"] = ws_spec(w)                       # WS to hydrogenation (T101 out = P101 out)
    n_in = mol(s["S04"])
    # H2O2 not extracted returns with the dried WS; the loop is closed by fixed-point below
    h2o2_ret = balance.h2o2_ret
    s["S04"]["H2O2"] = h2o2_ret
    n_in["H2O2"] = h2o2_ret / M["H2O2"]
    xi_hyd = CONV_HYD * n_in["EAQ"]
    xi_hpd = n_in["H2O2"]
    h2_use = xi_hyd + xi_hpd
    n_h2 = h2_use / (1.0 - H2_VENT)
    s["S01"] = {"H2": n_h2 * M["H2"]}
    n_out = dict(n_in)
    n_out["EAQ"] -= xi_hyd
    n_out["EAHQ"] = xi_hyd
    n_out["H2O2"] = 0.0
    n_out["H2O"] += 2 * xi_hpd
    n_out["H2"] = n_h2 - h2_use
    s["S05"] = from_mol(n_out)                  # hydrogenator effluent (calculated by cheme)
    s["S06"] = {"H2": s["S05"]["H2"], "TMB": VENT_TMB}   # H2 vent
    s["S07"] = {k: v for k, v in s["S05"].items() if k != "H2"}
    s["S07"]["TMB"] -= VENT_TMB
    s["S07"] = {k: v for k, v in s["S07"].items() if v > 0}
    # oxidation
    xi_oxd = CONV_OXD * s["S07"]["EAHQ"] / M["EAHQ"]
    n_air = xi_oxd * (1 + O2_EXCESS) / AIR["O2"]
    s["S08"] = from_mol({k: n_air * y for k, y in AIR.items()})   # air
    s["S09"] = dict(s["S08"])                                    # compressed air
    s["S10"] = dict(s["S08"])                                    # cooled air to oxidiser
    n_ox = add(mol(s["S07"]), mol(s["S10"]))
    n_ox["EAHQ"] -= xi_oxd
    n_ox["O2"] -= xi_oxd
    n_ox["EAQ"] += xi_oxd
    n_ox["H2O2"] = n_ox.get("H2O2", 0.0) + xi_oxd
    s["S11"] = from_mol({k: v for k, v in n_ox.items() if abs(v) > 1e-12})  # oxidiser effluent
    n_dry = sum(n_ox[k] for k in ("N2", "O2", "AR"))
    n_gas = n_dry / (1 - sum(Y_OX.values()))
    g = {k: n_ox[k] for k in ("N2", "O2", "AR")}
    for k, y in Y_OX.items():
        g[k] = y * n_gas
    s["S12"] = from_mol(g)                       # oxidiser off-gas
    s["S13"] = {k: v - s["S12"].get(k, 0.0) for k, v in s["S11"].items()}
    s["S13"] = {k: v for k, v in s["S13"].items() if v > 1e-9}   # oxidised WS
    s["S14"] = dict(s["S12"])                    # off-gas after condenser (two-phase)
    n_gas2 = n_dry / (1 - sum(Y_CD.values()))
    g2 = {k: n_ox[k] for k in ("N2", "O2", "AR")}
    for k, y in Y_CD.items():
        g2[k] = y * n_gas2
    s["S15"] = from_mol(g2)                      # gas to adsorber
    s["S16"] = {k: s["S12"][k] - s["S15"][k] for k in Y_CD}      # condensate to WS tank
    # adsorber: outlet VOC as TMB
    nm3 = sum(mol(s["S15"]).values()) * NM3
    tmb_out = VOC_OUT * nm3 * 1e-6 / C_FRAC["TMB"]
    ads = {"TMB": s["S15"]["TMB"] - tmb_out, "DIBC": s["S15"]["DIBC"]}
    steam_a = STEAM_PER_SOLV * tot(ads)
    s["S17"] = {"H2O": steam_a}                  # direct steam to adsorber regeneration
    s["S18"] = {k: s["S15"][k] for k in ("N2", "O2", "AR", "H2O")}
    s["S18"]["TMB"] = tmb_out                    # treated off-gas
    cond_org = {k: SOL_W[k] * steam_a for k in SOL_W}
    s["S19"] = {"H2O": steam_a, **cond_org}     # regeneration condensate to WW
    s["S21"] = {k: ads[k] - cond_org[k] for k in ads}  # recovered solvent to WS tank
    # extraction: H2O2 split; crude composition fixed; water balance gives extraction water
    h2o2_ws = s["S13"]["H2O2"]
    d_h2o2 = balance.h2o2_dist
    crude_h2o2 = F_EXT * (h2o2_ws + d_h2o2)
    crude_org = {k: CRUDE_ORG[k] * crude_h2o2 / W_CRUDE for k in CRUDE_ORG}
    crude_w = crude_h2o2 / W_CRUDE - crude_h2o2 - tot(crude_org)
    s["S24"] = {"H2O2": crude_h2o2, "H2O": crude_w, **crude_org}   # crude
    raf = {k: v for k, v in s["S13"].items()}
    raf["H2O2"] = h2o2_ws + d_h2o2 - crude_h2o2
    for k in crude_org:
        raf[k] -= crude_org[k]
    raf_nonw = tot({k: v for k, v in raf.items() if k != "H2O"})
    raf["H2O"] = X_H2O_RAF * raf_nonw / (1 - X_H2O_RAF)
    s["S26"] = raf                                # raffinate
    ext_w = crude_w + raf["H2O"] - s["S13"]["H2O"]
    # purification
    rem = {k: PUR_REMOVAL * crude_org[k] for k in crude_org}
    s["S25"] = {k: v for k, v in s["S24"].items()}
    for k in rem:
        s["S25"][k] -= rem[k]                     # purified crude
    s["S27"] = rem                                # organics back to WS tank
    # concentration: product = H2O2 + water + residual organics
    org_p = {k: s["S25"][k] for k in crude_org}
    prod_w = P_H2O2 / W_PROD - P_H2O2 - tot(org_p)
    s["S20"] = {"H2O2": s["S25"]["H2O2"] - balance.h2o2_dist, "H2O": prod_w, **org_p}
    dist_w = s["S25"]["H2O"] - prod_w
    s["S28"] = {"H2O": dist_w, "H2O2": balance.h2o2_dist}       # distillate (recycle)
    balance.h2o2_dist = H2O2_DIST / (1 - H2O2_DIST) * dist_w
    s["S30"] = dict(s["S20"])                     # cooled product (S20 = column bottoms)
    s["S29"] = {"H2O": ext_w - dist_w}            # demineralised water
    s["S23"] = add(s["S28"], s["S29"])            # extraction water (calculated by cheme)
    # WS dryer: dried WS water set so that the WS tank outlet meets X_H2O_WS
    water_other = s["S16"]["H2O"]                 # condensate water to the tank
    dried_w = s["S04"]["H2O"] - water_other
    s["S31"] = {"H2O": STEAM_EJ}                  # ejector motive steam
    dry_water = raf["H2O"] - dried_w              # water removed from the WS
    dry_h2o2 = H2O2_DRYW * dry_water
    dry_org = {k: SOL_W[k] * dry_water for k in SOL_W}
    s["S32"] = {"H2O": dry_water + STEAM_EJ, "H2O2": dry_h2o2, **dry_org}   # dryer effluent
    s["S33"] = {k: v for k, v in raf.items()}
    s["S33"]["H2O"] = dried_w
    s["S33"]["H2O2"] = raf["H2O2"] - dry_h2o2
    for k in dry_org:
        s["S33"][k] -= dry_org[k]                 # dried WS
    balance.h2o2_ret = s["S33"]["H2O2"]
    # reversion: spent alumina carries the degraded quinone and solvent
    s["S34"] = {"AL2O3": ALU}
    spent_solv = {"TMB": TMB_DIBC[0] * SOLV_SPENT, "DIBC": TMB_DIBC[1] * SOLV_SPENT}
    s["S35"] = {"AL2O3": ALU, "EAQ": EAQ_LOSS, **spent_solv}
    s["S36"] = {k: v for k, v in s["S33"].items()}
    s["S36"]["EAQ"] -= EAQ_LOSS
    for k in spent_solv:
        s["S36"][k] -= spent_solv[k]              # regenerated WS
    # make-ups: what the WS tank needs to meet the spec
    back = add(s["S36"], s["S16"], s["S21"], s["S27"])
    s["S02"] = {"EAQ": s["S04"]["EAQ"] - back["EAQ"]}
    s["S03"] = {k: s["S04"][k] - back[k] for k in ("TMB", "DIBC")}
    s["_xi"] = {"HYD": xi_hyd, "HPD": xi_hpd, "OXD": xi_oxd}
    s["_ws_m3h"] = {"v": w / RHO_WS}
    return s


balance.h2o2_ret = 0.0
balance.h2o2_dist = 0.0


def duties(s):
    xi = s["_xi"]
    q = {}
    q["R101"] = -(xi["HYD"] * DH["HYD"] + xi["HPD"] * DH["HPD"]) / 3600
    q["R201"] = -(xi["OXD"] * DH["OXD"]) / 3600
    m_air = tot(s["S08"]) / 3600                  # kg/s
    pr = 450.0 / 101.325
    dh_is = 1.005 * 298.15 * (pr ** (0.4 / 1.4) - 1)
    w_k = dh_is / 0.80
    q["K201"] = m_air * w_k
    t_out = 298.15 + w_k / 1.005
    q["E201"] = m_air * 1.005 * (t_out - 313.15)
    lat = {"H2O": 2400.0, "TMB": 398.0, "DIBC": 380.0}   # kJ/kg (D-009)
    q["E202"] = (sum(s["S16"][k] * lat[k] for k in lat) / 3600
                 + tot(s["S15"]) / 3600 * 1.0 * (328.15 - 308.15))
    q["P101"] = s["_ws_m3h"]["v"] / 3600 * 800.0 / 0.70   # 800 kPa loop, eta 0.7 (D-010)
    q["C301"] = 10.0 * P_H2O2 / 1000                      # 10 kWh/t auxiliaries (D-010)
    q["C501_vac"] = 5.0 * P_H2O2 / 1000                   # 5 kWh/t vacuum pump (D-010)
    d = tot(s["S28"])
    v = 1.3 * d                                            # reflux ratio 0.3 (D-010)
    f = tot(s["S25"])
    q["C501_reb"] = (v * 2380.0 + f * 3.4 * (333.15 - 313.15)) / 3600
    q["C501_cond"] = v * 2380.0 / 3600
    q["E501"] = tot(s["S20"]) * 3.3 * (333.15 - 303.15) / 3600
    s["_t_k201"] = {"v": t_out}
    return q


def main():
    s = solve()
    q = duties(s)
    # the values process/flowsheet.yaml cites from this script (balance-output contract): the
    # streams (kg/h, mass fractions), the K-201 outlet temperature and the duties
    flowsheet = {k: {"flow": {"value": tot(s[k]), "basis": "mass"},
                     "composition": {"values": {c: v / tot(s[k]) for c, v in s[k].items()},
                                     "basis": "mass_fraction"}}
                 for k in s if not k.startswith("_")}
    flowsheet["S09"]["temperature"] = s["_t_k201"]["v"]
    flowsheet.update({qid: {"duty": q[k]} for qid, k in {
        "Q01": "K201", "Q02": "P101", "Q05": "C501_reb", "Q06": "R101", "Q07": "R201",
        "Q08": "E201", "Q09": "E202", "Q10": "C501_cond", "Q11": "E501"}.items()})
    write_balance_output({"design": flowsheet})
    if "--yaml" in sys.argv:
        for k in sorted(x for x in s if not x.startswith("_")):
            m = tot(s[k])
            comp = {c: round(v / m, 8) for c, v in sorted(s[k].items()) if v / m > 1e-9}
            print(f"{k}: flow {m:.2f} comp {comp}")
        for k, v in q.items():
            print(f"Q {k}: {v:.1f} kW")
        return
    p = P_H2O2
    print(f"WS to hydrogenation {tot(s['S04']):.0f} kg/h = {s['_ws_m3h']['v']:.0f} m3/h; "
          f"productivity {p / s['_ws_m3h']['v']:.2f} kg H2O2/m3")
    print(f"H2 feed {s['S01']['H2']:.1f} kg/h = {s['S01']['H2'] / p * 1000:.1f} kg/t "
          f"(stoichiometric {M['H2'] / M['H2O2'] * 1000:.1f})")
    print(f"air {tot(s['S08']):.0f} kg/h = {tot(s['S08']) / p:.2f} t/t; "
          f"{sum(mol(s['S08']).values()) * NM3 / p * 1000:.0f} Nm3/t; "
          f"off-gas {sum(mol(s['S18']).values()) * NM3:.0f} Nm3/h")
    print(f"demin water {tot(s['S29']) / p:.3f} t/t; WW {(tot(s['S19']) + tot(s['S32'])) / p:.3f} t/t; "
          f"TOC to WW {sum(C_FRAC[k] * (s['S19'].get(k, 0) + s['S32'].get(k, 0)) for k in C_FRAC) / p * 1000:.2f} kg/t")
    solv = tot(s["S03"])
    print(f"make-up EAQ {s['S02']['EAQ'] / p * 1000:.2f} kg/t, solvents {solv / p * 1000:.2f} kg/t")
    print(f"K201 outlet {s['_t_k201']['v']:.1f} K")
    el = q["K201"] + q["P101"] + q["C301"] + q["C501_vac"]
    st = q["C501_reb"] * 3.6 + (tot(s["S17"]) + tot(s["S31"])) * 2.7   # MJ/h, ~2.7 MJ/kg direct
    print(f"electricity {el:.0f} kW = {el / p * 1000:.0f} kWh/t; LP steam indirect "
          f"{q['C501_reb']:.0f} kW, direct {tot(s['S17']) + tot(s['S31']):.0f} kg/h; "
          f"steam energy ~{st / p:.2f} GJ/t; total ~{(st + el * 3.6) / p:.2f} GJ/t")
    cw = q["R101"] + q["R201"] + q["E201"] + q["E202"] + q["C501_cond"] + q["E501"]
    print(f"cooling water duty {cw:.0f} kW = {cw * 3.6 / p:.2f} GJ/t; "
          + ", ".join(f"{k} {v:.0f}" for k, v in q.items()))
    ins = tot(s["S01"]) + tot(s["S02"]) + tot(s["S03"]) + tot(s["S08"]) + tot(s["S17"]) \
        + tot(s["S29"]) + tot(s["S31"]) + tot(s["S34"])
    outs = tot(s["S06"]) + tot(s["S18"]) + tot(s["S19"]) + tot(s["S30"]) + tot(s["S32"]) + tot(s["S35"])
    print(f"overall in {ins:.2f} out {outs:.2f} kg/h, diff {ins - outs:.4f}")


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
