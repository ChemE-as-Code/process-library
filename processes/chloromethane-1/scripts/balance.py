"""Concept mass and energy balance of chloromethane-1 (methanol hydrochlorination).

Provenance of the assumed stream values in process/flowsheet.yaml: every specification
below is a decision of DESIGN.md (D-numbers) or ASSUMED there. Plain Python (no pyDEXPI):
`python3 scripts/balance.py` prints the stream table and the duties. The recycle loops
(stripper overhead, HCl column overhead) are converged by direct substitution.

The mixer, reactor and splitter outlets are recalculated by `cheme process propagate`; this
script must use the same reactor model (selectivity step) so that they agree.
"""

import math

M = {"MEOH": 32.042, "HCL": 36.461, "MECL": 50.488, "DME": 46.068, "H2O": 18.015,
     "N2": 28.014, "H2SO4": 98.079}
COMP = list(M)

# ---- specifications (DESIGN.md)
PRODUCT_KG_H = 12500.0          # D-002 ASSUMED: 100 kt/a / 8000 h, product stream total
R_HCL = 1.10                    # D-004 ASSUMED: HCl/MeOH at the reactor inlet
X_MEOH = 0.976                  # D-004: Schmidt et al. 2014 (abstract), 340 C, near equilibrium
S_MECL = 0.988                  # D-004: same source, kmol CH3Cl per kmol MeOH converted
S_DME = (1.0 - S_MECL) / 2.0    # D-004: remainder to DME, 2 MeOH -> DME + H2O
X_N2_HCL = 0.001                # D-003 ASSUMED: inerts in the anhydrous HCl feed, as N2
W_MEOH_FEED = {"MEOH": 0.9995, "H2O": 0.0005}   # D-003: methanol-1 product target
# quench / acid condensation Q201 at 313.15 K, 200 kPa(a)
P_Q = 200.0
Y_HCL_GAS = 0.005               # D-006 ASSUMED, inside 0.3-4 vol% (US 4,794,204)
Y_MEOH_GAS = 0.0002             # D-006, below the < 0.03 % of US 4,794,204
A_W = 0.70                      # D-006 ASSUMED water activity over ~22 wt% HCl
PSAT_W_313 = 7.384              # kPa, water at 313.15 K (IAPWS-IF97)
Y_H2O_GAS = A_W * PSAT_W_313 / P_Q
F_MECL_AQ = 0.005               # D-006 ASSUMED: CH3Cl dissolved in the quench acid
F_DME_AQ = 0.05                 # D-006 ASSUMED: DME dissolved in the quench acid
# methanol stripper C202
REC_MEOH = 0.99                 # D-007 ASSUMED
OVH_W_PER_MEOH = 0.5            # D-007 ASSUMED kg water per kg methanol overhead
OVH_HCL_PER_MEOH = 0.15         # D-007 ASSUMED kg HCl per kg methanol overhead
# sulfuric acid drying T301
W_ACID = 0.96                   # D-008: 95 % most common (US 4,794,204); 96 wt% chosen
W_DME_SPENT = 0.08              # D-008 ASSUMED inside the 5-10 % limit (US 4,794,204)
F_DME_ABS = 0.99                # D-008 ASSUMED
F_MECL_ABS = 0.001              # D-008 ASSUMED CH3Cl dissolved in the spent acid
# HCl column C401 (1000 kPa(a), partial condenser on cooling water)
Y_MECL_OVH = 0.70               # D-009 ASSUMED CH3Cl in the overhead vapour
PURGE = 0.10                    # D-009 ASSUMED purge fraction of the overhead vapour


def zero():
    return {c: 0.0 for c in COMP}


def add(*ds):
    out = zero()
    for d in ds:
        for c, v in d.items():
            out[c] += v
    return out


def mass(d):
    return {c: d[c] * M[c] for c in COMP}


def total(d):
    return sum(d.values())


def solve(fresh_meoh_kmol):
    rec_strip = zero()
    rec_col = zero()
    for _ in range(500):
        meoh_liq = {"MEOH": fresh_meoh_kmol * W_MEOH_FEED["MEOH"] / M["MEOH"] * M["MEOH"]}
        meoh_feed = zero()
        kg = fresh_meoh_kmol * M["MEOH"] / W_MEOH_FEED["MEOH"]   # kg/h of feed
        meoh_feed["MEOH"] = kg * W_MEOH_FEED["MEOH"] / M["MEOH"]
        meoh_feed["H2O"] = kg * W_MEOH_FEED["H2O"] / M["H2O"]
        # fresh HCl tops up the reactor inlet to R_HCL
        meoh_in = meoh_feed["MEOH"] + rec_strip["MEOH"] + rec_col["MEOH"]
        hcl_need = R_HCL * meoh_in - rec_strip["HCL"] - rec_col["HCL"]
        hcl_feed = zero()
        hcl_feed["HCL"] = hcl_need
        hcl_feed["N2"] = hcl_need * X_N2_HCL / (1 - X_N2_HCL)
        rin = add(meoh_feed, hcl_feed, rec_strip, rec_col)
        conv = X_MEOH * rin["MEOH"]
        rout = dict(rin)
        rout["MEOH"] -= conv
        rout["MECL"] += S_MECL * conv
        rout["DME"] += S_DME * conv
        rout["HCL"] -= S_MECL * conv
        rout["H2O"] += S_MECL * conv + S_DME * conv
        # quench: gas holds N2, most CH3Cl and DME, set fractions of HCl, MeOH, water
        dry = rout["N2"] + rout["MECL"] * (1 - F_MECL_AQ) + rout["DME"] * (1 - F_DME_AQ)
        ysum = Y_HCL_GAS + Y_MEOH_GAS + Y_H2O_GAS
        ngas = dry / (1 - ysum)
        gas = zero()
        gas["N2"] = rout["N2"]
        gas["MECL"] = rout["MECL"] * (1 - F_MECL_AQ)
        gas["DME"] = rout["DME"] * (1 - F_DME_AQ)
        gas["HCL"] = Y_HCL_GAS * ngas
        gas["MEOH"] = Y_MEOH_GAS * ngas
        gas["H2O"] = Y_H2O_GAS * ngas
        aq = {c: rout[c] - gas[c] for c in COMP}
        # stripper
        ovh = zero()
        ovh["MEOH"] = REC_MEOH * aq["MEOH"]
        ovh["MECL"] = aq["MECL"]
        ovh["DME"] = aq["DME"]
        mkg = ovh["MEOH"] * M["MEOH"]
        ovh["H2O"] = OVH_W_PER_MEOH * mkg / M["H2O"]
        ovh["HCL"] = OVH_HCL_PER_MEOH * mkg / M["HCL"]
        bot = {c: aq[c] - ovh[c] for c in COMP}
        # drying: water, methanol, DME (99 %), a little CH3Cl into the acid
        absorbed = zero()
        absorbed["H2O"] = gas["H2O"]
        absorbed["MEOH"] = gas["MEOH"]
        absorbed["DME"] = F_DME_ABS * gas["DME"]
        absorbed["MECL"] = F_MECL_ABS * gas["MECL"]
        abs_kg = mass(absorbed)
        # spent acid DME mass fraction fixes the acid rate
        other_kg = abs_kg["H2O"] + abs_kg["MEOH"] + abs_kg["MECL"]
        spent_kg = abs_kg["DME"] / W_DME_SPENT
        acid_kg = spent_kg - abs_kg["DME"] - other_kg
        acid = zero()
        acid["H2SO4"] = acid_kg * W_ACID / M["H2SO4"]
        acid["H2O"] = acid_kg * (1 - W_ACID) / M["H2O"]
        spent = add(acid, absorbed)
        drygas = {c: gas[c] - absorbed[c] for c in COMP}
        # HCl column: overhead holds all N2 and HCl and CH3Cl at Y_MECL_OVH
        top = zero()
        top["N2"] = drygas["N2"]
        top["HCL"] = drygas["HCL"]
        top["MECL"] = Y_MECL_OVH / (1 - Y_MECL_OVH) * (top["N2"] + top["HCL"])
        prod = {c: drygas[c] - top[c] for c in COMP}
        purge = {c: PURGE * top[c] for c in COMP}
        new_rec_col = {c: (1 - PURGE) * top[c] for c in COMP}
        err = sum(abs(new_rec_col[c] - rec_col[c]) + abs(ovh[c] - rec_strip[c]) for c in COMP)
        rec_col, rec_strip = new_rec_col, ovh
        if err < 1e-12:
            break
    return dict(meoh_feed=meoh_feed, hcl_feed=hcl_feed, rin=rin, rout=rout, gas=gas, aq=aq,
                ovh=ovh, bot=bot, acid=acid, spent=spent, drygas=drygas, top=top, prod=prod,
                purge=purge, rec_col=rec_col, conv=conv)


def find_capacity():
    lo, hi = 100.0, 1000.0
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        r = solve(mid)
        if total(mass(r["prod"])) > PRODUCT_KG_H:
            hi = mid
        else:
            lo = mid
    return solve(0.5 * (lo + hi))


def cp_ig(c, T):
    """Ideal-gas cp, kJ/kmol K, Poling polynomials as printed by cheme chemistry thermo."""
    a = {"MEOH": [4.714, -0.006986, 4.211e-05, -4.443e-08, 1.535e-11],
         "HCL": [3.827, -0.002936, 8.79e-06, -1.031e-08, 4.39e-12],
         "MECL": [3.578, -0.00175, 3.071e-05, -3.714e-08, 1.408e-11],
         "DME": [4.361, 0.00607, 2.899e-05, -3.581e-08, 1.282e-11],
         "H2O": [4.395, -0.004186, 1.405e-05, -1.564e-08, 6.32e-12],
         "N2": [3.539, -0.000261, 7.0e-08, 1.57e-09, -9.9e-13],
         "H2SO4": [0, 0, 0, 0, 0]}[c]
    return 8.314 * sum(a[i] * T ** i for i in range(5))


def dh_gas(d, T1, T2, n=50):
    """Sensible enthalpy change of an ideal-gas mixture d (kmol/h), kJ/h."""
    s = 0.0
    for i in range(n):
        T = T1 + (i + 0.5) * (T2 - T1) / n
        s += sum(d[c] * cp_ig(c, T) for c in COMP) * (T2 - T1) / n
    return s


def report():
    r = find_capacity()
    kw = 1.0 / 3600.0
    streams = {
        "S01 fresh methanol": r["meoh_feed"], "S02 anhydrous HCl": r["hcl_feed"],
        "S05 reactor feed": r["rin"], "S06 reactor effluent": r["rout"],
        "S07 crude gas": r["gas"], "S08 quench acid": r["aq"],
        "S09 stripper overhead (recycle)": r["ovh"], "S10 dilute HCl": r["bot"],
        "S11 sulfuric acid": r["acid"], "S12 spent acid": r["spent"],
        "S13 dry gas": r["drygas"], "S16 column overhead": r["top"],
        "S17 product": r["prod"], "S18 purge": r["purge"], "S19 recycle": r["rec_col"]}
    for name, d in streams.items():
        m = mass(d)
        tm = total(m)
        wf = {c: round(m[c] / tm, 6) for c in COMP if m[c] > 1e-9}
        print(f"{name:34s} {tm:12.3f} kg/h {total(d):10.4f} kmol/h  {wf}")
    # ---- checks
    prod_kg = total(mass(r["prod"]))
    meoh_kg = total(mass(r["meoh_feed"]))
    hcl_kg = total(mass(r["hcl_feed"]))
    print(f"\nfresh MeOH {meoh_kg/prod_kg:.4f} kg/kg product; fresh HCl {hcl_kg/prod_kg:.4f} kg/kg")
    print(f"overall CH3Cl yield on MeOH {r['prod']['MECL']/r['meoh_feed']['MEOH']:.4f} mol/mol")
    aqm = mass(r["aq"])
    print(f"quench acid HCl {aqm['HCL']/total(aqm):.3f} wt%/100; DME in crude gas "
          f"{r['gas']['DME']/total(r['gas']):.4f} mol/mol")
    sp = mass(r["spent"])
    print(f"spent acid strength H2SO4/(H2SO4+H2O) {sp['H2SO4']/(sp['H2SO4']+sp['H2O']):.3f}")
    ins = total(mass(add(r["meoh_feed"], r["hcl_feed"], r["acid"])))
    outs = total(mass(add(r["prod"], r["purge"], r["bot"], r["spent"])))
    print(f"overall mass in {ins:.3f} out {outs:.3f} kg/h")
    # ---- duties (kW), ASSUMED hand estimates (D-010)
    T_REF = 298.15
    dHr1, dHr2 = -31569.0, -24442.0         # kJ/kmol, from the ideal-gas dHf (cheme chemistry thermo)
    ext1 = S_MECL * r["conv"]
    ext2 = S_DME * r["conv"]
    q_rxn = -(ext1 * dHr1 + ext2 * dHr2)    # kJ/h released
    # E101: methanol 313 K liquid to saturated vapour at 400 kPa(a) (385 K)
    nm = r["meoh_feed"]["MEOH"] + r["meoh_feed"]["H2O"]
    q_e101 = nm * (81.0 * (385.0 - 313.15) + 33500.0)        # cp_l, dHvap(385 K) ASSUMED round
    # plus the condensed stripper overhead (D-007), revaporised: methanol, water, dissolved gases
    q_ovh_latent = (r["ovh"]["MEOH"] * 37000.0 + r["ovh"]["H2O"] * 41000.0
                    + r["ovh"]["HCL"] * 63000.0 + (r["ovh"]["MECL"] + r["ovh"]["DME"]) * 20000.0)
    q_e101 += q_ovh_latent
    # E102: reactor feed superheat from the mixed temperature (taken 375 K) to 523 K
    q_e102 = dh_gas(r["rin"], 375.0, 523.15)
    # R101: outlet 613 K; net heat to the coolant loop
    q_sens = dh_gas(r["rout"], 523.15, 613.15)
    q_r101 = q_rxn - q_sens
    # Q201: effluent 613 K to 313 K, water and methanol condensed, HCl absorbed
    q_q201 = (dh_gas(r["rout"], 313.15, 613.15) + r["aq"]["H2O"] * 43000.0
              + r["aq"]["MEOH"] * 37000.0 + r["aq"]["HCL"] * 63000.0)
    # C202: feed 313 -> 383 K (cp 3.4 kJ/kg K), overhead vaporised
    aqkg = total(mass(r["aq"]))
    q_c202 = aqkg * 3.4 * 70.0 + q_ovh_latent
    q_c202_cond = q_ovh_latent              # overhead condensed on cooling water, returned as liquid
    # T301: water and methanol absorbed in the acid (condensation plus dilution), DME absorption
    q_t301 = (r["spent"]["H2O"] - r["acid"]["H2O"]) * 70000.0 + (
        r["spent"]["MEOH"] * 50000.0 + r["spent"]["DME"] * 30000.0)
    # K401: two stages 190 -> 1050 kPa(a), intercooled to 313 K, isentropic eff. 0.75
    n = total(r["drygas"])
    cp = sum(r["drygas"][c] * cp_ig(c, 313.15) for c in COMP) / n
    k = cp / (cp - 8.314)
    pr = math.sqrt(1050.0 / 190.0)
    w_stage = n * cp * 313.15 * (pr ** ((k - 1) / k) - 1) / 0.75
    q_k401_cw = w_stage                     # intercooler takes stage-1 work
    p_k401 = 2 * w_stage / 0.95             # motor efficiency 0.95
    # E401: stage-2 desuperheat and condensation of the CH3Cl (19.3 kJ/mol at 313 K)
    q_e401 = w_stage + r["drygas"]["MECL"] * 19300.0
    # C401: boil-up 0.3 kmol per kmol bottoms; overhead leaves as vapour
    q_c401_reb = 0.3 * total(r["prod"]) * 19000.0
    q_c401_cond = q_c401_reb - r["top"]["MECL"] * 19300.0 - (r["top"]["HCL"] * 16000.0)
    p_pumps = 0.10 * p_k401
    # D-010: the reactor coolant loop superheats the feed (E102) and gives its surplus to the
    # methanol vaporiser (E101); LP steam supplies the rest of E101
    q_r101_e101 = q_r101 - q_e102
    duties = {"Q01 E101 LP steam": q_e101 - q_r101_e101, "Q02 R101 coolant to E102": q_e102,
              "Q03 R101 coolant to E101": q_r101_e101, "Q04 Q201 to CW": q_q201,
              "Q05 C202 LP steam": q_c202, "Q06 T301 to CW": q_t301,
              "Q07 K401 power": p_k401, "Q08 K401 intercooler CW": q_k401_cw,
              "Q09 E401 CW": q_e401, "Q10 C401 LP steam": q_c401_reb,
              "Q11 C401 condenser CW": q_c401_cond, "Q12 pumps power": p_pumps,
              "Q13 C202 condenser CW": q_c202_cond}
    print(f"\nreaction heat {q_rxn*kw:.1f} kW; reactor sensible {q_sens*kw:.1f} kW")
    for name, q in duties.items():
        print(f"{name:30s} {q*kw:10.1f} kW  {q*kw/prod_kg:.5f} kWh/kg")
    # the values process/flowsheet.yaml cites from this script (balance-output contract), by the
    # flowsheet's stream ids (its S03 is the anhydrous HCl printed as "S02" above)
    ids = {"S01": "meoh_feed", "S03": "hcl_feed", "S07": "gas", "S08": "aq", "S09": "ovh",
           "S10": "bot", "S11": "acid", "S12": "spent", "S13": "drygas", "S16": "top",
           "S17": "prod", "S18": "purge", "S19": "rec_col"}
    flowsheet = {}
    for sid, key in ids.items():
        m = mass(r[key])
        flowsheet[sid] = {"flow": {"value": total(m), "basis": "mass"},
                          "composition": {"values": {c: m[c] / total(m) for c in COMP},
                                          "basis": "mass_fraction"}}
    flowsheet.update({name.split()[0]: {"duty": q * kw} for name, q in duties.items()})
    write_balance_output({"design": flowsheet})


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
    report()
