"""Concept heat and material balance of hydroxylamine-1 (hydroxylammonium sulfate solution by
catalytic NO hydrogenation, NO from ammonia oxidation with oxygen and steam).

Independent of cheme's solvers: it fixes the feeds, the recycle and purge, the separator outlets
and the duties that process/flowsheet.yaml carries as ASSUMED values (DESIGN.md D-006). The
reactor outlets in the flowsheet are calculated by cheme from process/reactions.yaml and must
agree with this script within the flowsheet tolerance.

Run: cheme run scripts/has_balance.py   (prints the stream table and duties; writes nothing)

Ideal-gas enthalpies: thermo/chemicals (Hfg and ideal-gas heat capacities). Aqueous reaction
enthalpies: NBS tables values (Wagman et al. 1982), see D-005 (to verify: open input O-4).
"""
import sys

from thermo import Chemical

# --------------------------------------------------------------------------- basis
NH2OH_KG_H = 3750.0          # D-002: 30 kt/a NH2OH contained, 8000 h/a (ASSUMED)
W_HAS = 0.254                # product, US 4,997,635 Example: 254 g/kg hydroxylammonium sulfate
W_AS = 0.0186                # 18.6 g/kg ammonium sulfate
W_FREE = 0.0130              # 13.0 g/kg free sulfuric acid

# Burner (US 3,110,563 Example a): NH3:O2:steam = 14 : 18.6 : 67.4 by volume, Pt/Rh.
O2_PER_NH3 = 18.6 / 14.0
STEAM_PER_NH3 = 67.4 / 14.0
X_NOX = 0.98                 # NH3-N to NO (+NO2/HNO3), US 3,110,563 Example a (82+15+1 %)
# N2O formed: IPCC 2006 Vol.3 Ch.3 Table 3.3, atmospheric-pressure plants 5 kg N2O/t HNO3,
# referred to NH3 through N: N2O-N / HNO3-N times the NOx yield (D-005)
X_N2O = (5.0 / 44.0128 * 2) / (1000.0 / 63.0128) * X_NOX
X_N2 = 1.0 - X_NOX - X_N2O
GOX_AR = 0.005               # asu-1 GOX >= 99.5 mol% O2, rest argon (ASSUMED)
X_O2_HYD = 0.90              # EP 0 945 401 Example: 90 % of the excess O2 hydrogenated (Ag-Mn)

# Hydrogenation cascade (D-007)
S_N2O = 0.020                # US 4,895,711 Examples 1-3: N2O selectivity 1.9-2.2 %
R_NH4_HA = (2 * W_AS / 132.1395) / (2 * W_HAS / 164.1383)   # product NH4+/NH3OH+ (US 4,997,635)
S_HA = (1 - S_N2O) / (1 + R_NH4_HA)
S_NH3 = 1 - S_N2O - S_HA
X_PASS = 0.90                # NO converted per pass of the cascade gas (ASSUMED)
H2_NO_IN = 2.0               # EP 1 343 719: H2:NO 1.5-2.5 per stage, especially 2:1
PURGE = 0.30                 # fraction of the cascade off-gas purged (ASSUMED, D-007)
if len(sys.argv) > 1:        # sensitivity: cheme run scripts/has_balance.py <purge fraction>
    PURGE = float(sys.argv[1])
A_W = 0.90                   # water activity of the product solution (ASSUMED)

T0 = 298.15
MW = {"NH3": 17.0305, "O2": 31.9988, "AR": 39.948, "N2": 28.0134, "H2O": 18.01528,
      "NO": 30.0061, "N2O": 44.0128, "H2": 2.01588, "HNO3": 63.0128, "H2SO4": 98.0785,
      "HAS": 164.1383, "AS": 132.1395}                 # from the atomic masses (formulae)
NAMES = {"NH3": "ammonia", "O2": "oxygen", "AR": "argon", "N2": "nitrogen", "H2O": "water",
         "NO": "nitric oxide", "N2O": "nitrous oxide", "H2": "hydrogen"}
CH = {k: Chemical(v) for k, v in NAMES.items()}
HF = {k: CH[k].Hfgm for k in CH}                      # J/mol, ideal gas 298.15 K


def h_gas(c, T):
    """Ideal-gas molar enthalpy J/mol incl. formation at 298.15 K."""
    return HF[c] + CH[c].HeatCapacityGas.T_dependent_property_integral(T0, T)


def H_gas(n, T):
    return sum(v * h_gas(c, T) for c, v in n.items() if c in CH) / 3.6e3   # kmol/h -> kW


def cp_gas(n, T):
    return sum(v * CH[c].HeatCapacityGas(T) for c, v in n.items()) / sum(n.values())


def solve_T(n, H_target, lo=250, hi=2500):
    for _ in range(80):
        mid = 0.5 * (lo + hi)
        if H_gas(n, mid) > H_target:
            hi = mid
        else:
            lo = mid
    return 0.5 * (lo + hi)


def add(*ds):
    out = {}
    for d in ds:
        for k, v in d.items():
            out[k] = out.get(k, 0.0) + v
    return out


def scale(d, f):
    return {k: v * f for k, v in d.items()}


def psat_water(T):                                     # kPa
    return CH["H2O"].VaporPressure(T) / 1e3


def compress(n, T1, P1, P2, eta):
    cp = cp_gas(n, T1)
    k = cp / (cp - 8.314462)
    T2s = T1 * (P2 / P1) ** ((k - 1) / k)
    T2 = T1 + (T2s - T1) / eta
    W = H_gas(n, T2) - H_gas(n, T1)
    return T2, W


# --------------------------------------------------------------------------- NO generation
def no_section(nh3):
    o2 = O2_PER_NH3 * nh3
    feed = {"NH3": nh3, "O2": o2, "AR": o2 * GOX_AR / (1 - GOX_AR), "H2O": STEAM_PER_NH3 * nh3}
    # burner feed temperature: NH3 vapour and O2 at 298 K, LP steam 500 kPa(a) saturated 425 K
    T_steam = 425.0
    H_feed = H_gas({"NH3": nh3, "O2": feed["O2"], "AR": feed["AR"]}, T0) + H_gas({"H2O": feed["H2O"]}, T_steam)
    T_mix = solve_T(feed, H_feed)
    burn = dict(feed)
    burn["NH3"] = 0.0
    e1, e2, e3 = X_NOX * nh3, X_N2O * nh3, X_N2 * nh3
    burn["NO"] = e1
    burn["N2O"] = e2 / 2
    burn["N2"] = e3 / 2
    burn["O2"] = o2 - 1.25 * e1 - 1.0 * e2 - 0.75 * e3
    burn["H2O"] = feed["H2O"] + 1.5 * nh3
    T_burn = solve_T(burn, H_feed)                         # adiabatic gauze
    T_whb = 543.15                                         # EP 0 945 401: 260-280 C after the boiler
    Q_whb = H_gas(burn, T_burn) - H_gas(burn, T_whb)
    # O2 hydrogenation: H2 stoichiometric for all of the O2, 90 % converted (EP 0 945 401)
    h2_o2 = 2.0 * burn["O2"]
    r102_in = add(burn, {"H2": h2_o2})
    H_in = H_gas(burn, T_whb) + H_gas({"H2": h2_o2}, T0)
    xi = X_O2_HYD * burn["O2"]
    r102 = add(r102_in, {"O2": -xi, "H2": -2 * xi, "H2O": 2 * xi})
    T_r102 = solve_T(r102, H_in)
    # condenser E102: residual O2 absorbed as nitric acid 4 NO + 3 O2 + 2 H2O -> 4 HNO3 (aq)
    xi2 = r102["O2"] / 3.0
    after = add(r102, {"O2": -3 * xi2, "NO": -4 * xi2, "H2O": -2 * xi2})
    hno3 = 4 * xi2
    P_v101, T_v101 = 115.0, 313.15
    dry = {k: v for k, v in after.items() if k != "H2O" and v > 0}
    y_w = psat_water(T_v101) / P_v101
    w_gas = y_w / (1 - y_w) * sum(dry.values())
    no_gas = add(dry, {"H2O": w_gas})
    cond_w = after["H2O"] - w_gas
    # E102 duty: gas in at T_r102 -> gas out + condensate (water liquid + HNO3 aq) at 313 K
    dHvap = CH["H2O"].EnthalpyVaporization(T_v101)
    H_out = H_gas(no_gas, T_v101) + cond_w * (h_gas("H2O", T_v101) - dHvap) / 3.6e3 \
        + hno3 * (-207.36e3 + 0.0) / 3.6e3                 # HNO3(aq), NBS tables
    # NBS-consistent: gas-phase enthalpies come from thermo; the HNO3(aq) term is small
    Q_e102 = H_gas(r102, T_r102) - H_out
    return dict(feed=feed, T_mix=T_mix, burn=burn, T_burn=T_burn, Q_whb=Q_whb, h2_o2=h2_o2,
                r102=r102, T_r102=T_r102, no_gas=no_gas, cond={"H2O": cond_w, "HNO3": hno3},
                Q_e102=Q_e102, P_v101=P_v101)


# --------------------------------------------------------------------------- cascade
P_R201 = 200.0
P_K101 = 220.0
T_R = 313.15
y_w_off = A_W * psat_water(T_R) / P_R201


def cascade(no_gas):
    """Gas loop: fresh NO gas + fresh H2 + recycle -> R201; off-gas purge / recycle."""
    rec = {}
    for _ in range(500):
        gas_in_wo_h2 = add(no_gas, rec)
        h2_fresh = H2_NO_IN * gas_in_wo_h2["NO"] - gas_in_wo_h2.get("H2", 0.0)
        gin = add(gas_in_wo_h2, {"H2": h2_fresh})
        no_in = gin["NO"]
        c = X_PASS * no_in
        ha, nh4, n2o_n = c * S_HA, c * S_NH3, c * S_N2O
        cons = {"NO": -c, "H2": -(1.5 * ha + 2.5 * nh4 + 0.5 * n2o_n)}
        form = {"N2O": n2o_n / 2, "H2O": nh4 + n2o_n / 2}
        out_gas_dry = {k: v for k, v in add(gin, cons, form).items() if k != "H2O"}
        out_gas_dry = {k: v for k, v in out_gas_dry.items() if v > 1e-12}
        w_off = y_w_off / (1 - y_w_off) * sum(out_gas_dry.values())
        off = add(out_gas_dry, {"H2O": w_off})
        new_rec = scale(off, 1 - PURGE)
        if rec and all(abs(new_rec[k] - rec.get(k, 0)) < 1e-10 for k in new_rec):
            break
        rec = new_rec
    return dict(gin=gin, h2_fresh=h2_fresh, ha=ha, nh4=nh4, n2o_n=n2o_n, c=c, off=off,
                rec=rec, purge=scale(off, PURGE), cons=cons, form=form)


def solve():
    nh3 = 140.0
    for _ in range(60):
        ns = no_section(nh3)
        cs = cascade(ns["no_gas"])
        target = NH2OH_KG_H / 33.0300
        nh3 *= target / cs["ha"]
    return nh3, ns, cs


def main():
    nh3, ns, cs = solve()
    ha_kmol = cs["ha"]
    has = ha_kmol / 2
    as_ = cs["nh4"] / 2
    m_has = has * MW["HAS"]
    M = m_has / W_HAS
    m_free = W_FREE * M
    m_as = as_ * MW["AS"]
    m_hno3 = ns["cond"]["HNO3"] * MW["HNO3"]
    m_w_prod = M - m_has - m_as - m_free - m_hno3
    h2so4 = has + as_ + m_free / MW["H2SO4"]
    acid_feed = h2so4 * MW["H2SO4"] / 0.985
    # water balance of the cascade liquid: water out = in (acid make-up) + gas water in - off-gas
    # water + formed
    gas_w_in = cs["gin"].get("H2O", 0.0)
    w_formed = cs["form"]["H2O"]
    w_off = cs["off"]["H2O"]
    w_acidmix = m_w_prod / MW["H2O"] - gas_w_in - w_formed + w_off          # kmol/h
    cond_w = ns["cond"]["H2O"]
    demin = w_acidmix - cond_w - acid_feed * 0.015 / MW["H2O"]
    acid_mix = {"H2SO4": h2so4 * MW["H2SO4"], "H2O": w_acidmix * MW["H2O"], "HNO3": m_hno3}
    w_acid = acid_mix["H2SO4"] / sum(acid_mix.values())

    def kg(d):
        return {k: v * MW[k] for k, v in d.items()}

    def show(name, d, T, P, molar=True):
        m = kg(d) if molar else d
        tot = sum(m.values())
        fr = {k: round(v / tot, 8) for k, v in m.items() if v > 0}
        print(f"{name}: T={T:.2f} K P={P} kPa  flow={tot:.2f} kg/h  w={fr}")
        return {"flow": tot, "temperature": T, "composition": fr}

    print(f"NH3 = {nh3:.4f} kmol/h = {nh3 * MW['NH3']:.2f} kg/h; X_N2O={X_N2O:.6f} X_N2={X_N2:.6f}")
    print(f"S_HA={S_HA:.6f} S_NH3={S_NH3:.6f} S_N2O={S_N2O}; pass conversions HAS={X_PASS*S_HA:.6f} "
          f"AS={X_PASS*S_NH3:.6f} N2O={X_PASS*S_N2O:.6f}")
    print(f"burner feed T={ns['T_mix']:.1f} K, gauze outlet {ns['T_burn']:.1f} K, R102 out {ns['T_r102']:.1f} K")
    f = ns["feed"]
    s = {}  # the shown streams by name, for the balance output
    s["S01"] = show("S01 NH3", {"NH3": f["NH3"]}, 298.15, 1200)
    s["S03"] = show("S03 O2 (GOX)", {"O2": f["O2"], "AR": f["AR"]}, 298.15, 300)
    s["S04"] = show("S04 steam", {"H2O": f["H2O"]}, 425.0, 500)
    show("burner out", ns["burn"], ns["T_burn"], 130)
    s["S08"] = show("S08 H2 to R102", {"H2": ns["h2_o2"]}, 298.15, 300)
    show("R102 out", ns["r102"], ns["T_r102"], 120)
    s["S11"] = show("V101 gas (NO gas)", ns["no_gas"], 313.15, 115)
    s["S12"] = show("V101 condensate", ns["cond"], 313.15, 115)
    T_k101, W_k101 = compress(ns["no_gas"], 313.15, 115.0, P_K101, 0.75)
    print(f"K101: out {T_k101:.1f} K, {W_k101:.1f} kW")
    s["S19"] = show("S15 fresh H2", {"H2": cs["h2_fresh"]}, 298.15, 300)
    off = cs["off"]
    T_k201, W_k201 = compress(cs["rec"], T_R, P_R201 - 5, P_R201 + 15, 0.70)
    print(f"K201: out {T_k201:.1f} K, {W_k201:.1f} kW")
    show("cascade gas in", cs["gin"], 0, 210)
    s["S22"] = show("V201 off-gas", off, T_R, 200)
    show("purge", cs["purge"], T_R, 200)
    show("recycle", cs["rec"], T_R, 200)
    yoff = {k: v / sum(off.values()) for k, v in off.items()}
    print("off-gas mole fractions:", {k: round(v, 4) for k, v in yoff.items()})
    prod = {"HAS": m_has, "AS": m_as, "H2SO4": m_free, "HNO3": m_hno3, "H2O": m_w_prod}
    s["S23"] = show("V201 liquid = product", prod, T_R, 200, molar=False)
    s["S14"] = show("S11 acid 98.5 %", {"H2SO4": acid_feed * 0.985, "H2O": acid_feed * 0.015}, 298.15, 300, molar=False)
    s["S15"] = show("S13 demin water", {"H2O": demin * MW["H2O"]}, 298.15, 300, molar=False)
    show("acid make-up", acid_mix, 313.15, 300, molar=False)
    print(f"acid make-up H2SO4 {w_acid*100:.2f} wt% (EP 0 945 401: 19 %)")

    # ---- duties
    nh3_kg = nh3 * MW["NH3"]
    Q_e100 = nh3 * CH["NH3"].EnthalpyVaporization(298.15) / 3.6e3
    # E201: dilution of 98.5 % acid to the make-up strength, about -74 kJ/mol H2SO4 (ASSUMED,
    # handbook order for ~20 mol water per mol acid); feeds enter at 298-313 K, out at 313 K
    Q_e201 = h2so4 * 74.0e3 / 3.6e3 - (demin * MW["H2O"] * 4.18 + acid_feed * 1.4) * (313.15 - 298.15) / 3600
    # R201: NBS aqueous enthalpies of formation (kJ/mol): NH3OH+ -137.3, NH4+ -132.51,
    # H2O(l) -285.83, NO(g) 90.29, N2O(g) 82.05
    dH_ha, dH_nh4, dH_n2o = -137.3 - 90.29, -132.51 - 285.83 - 90.29, (82.05 - 285.83 - 2 * 90.29) / 2
    Q_rx = -(cs["ha"] * dH_ha + cs["nh4"] * dH_nh4 + cs["n2o_n"] * dH_n2o) * 1e3 / 3.6e3
    # gas mixing temperature into R201 (fresh NO gas from K101, H2 at 298 K, recycle from K201)
    no_gas = ns["no_gas"]
    H_mix = H_gas(no_gas, T_k101) + H_gas({"H2": cs["h2_fresh"]}, T0) + H_gas(cs["rec"], T_k201)
    T_gin = solve_T(cs["gin"], H_mix)
    Q_sens = H_gas(cs["gin"], T_gin) - H_gas(cs["gin"], T_R)
    Q_evap = (off["H2O"] - cs["gin"].get("H2O", 0)) * CH["H2O"].EnthalpyVaporization(T_R) / 3.6e3
    STY = 0.97                                                  # mol NH2OH/(l h), US 4,895,711 (unit ASSUMED)
    V_liq = ha_kmol * 1e3 / STY / 1e3                           # m3
    W_agit = 2.0 * V_liq                                        # 2 kW/m3 ASSUMED
    Q_r201 = Q_rx + Q_sens - Q_evap + W_agit
    W_p201 = (sum(acid_mix.values()) / 1150.0) * 300.0 / 3600 / 0.6   # 300 kPa rise, eta 0.6
    # thermal oxidiser: air so that the flue gas leaves at 1173 K (no heat recovery, ASSUMED)
    pg = cs["purge"]
    air_unit = {"N2": 0.78084, "O2": 0.20946, "AR": 0.00934}
    o2_need = 0.5 * pg["H2"]
    lo, hi = o2_need / 0.20946, 50 * o2_need / 0.20946
    for _ in range(80):
        a = 0.5 * (lo + hi)
        air = scale(air_unit, a / sum(air_unit.values()))
        flue = add(pg, air, {"H2": -pg["H2"], "O2": -o2_need, "H2O": pg["H2"]})
        T = solve_T(flue, H_gas(pg, T_R) + H_gas(air, T0))
        if T > 1173.15:
            lo = a
        else:
            hi = a
    W_k301 = a * 22.414 / 3600 * 5.0 / 0.6 * 1.0                # m3/s x 5 kPa / 0.6 -> kW
    s["S28"] = show("air to oxidiser", air, 298.15, 106)
    show("flue gas", flue, 1173.15, 101.325)
    print("--- duties kW")
    for k, v in [("Q01 E100 NH3 vaporiser (LPS)", Q_e100), ("Q02 E101 to MP steam", ns["Q_whb"]),
                 ("Q03 E102 condenser", ns["Q_e102"]), ("Q04 K101", W_k101),
                 ("Q05 E201 acid cooler", Q_e201), ("Q06 P201", W_p201),
                 ("Q07 R201 to CW", Q_r201), ("   of which reaction", Q_rx), ("   gas sensible", Q_sens),
                 ("   evaporation", -Q_evap), ("Q08 R201 agitators", W_agit), ("Q09 K201", W_k201),
                 ("Q10 K301 air fan", W_k301)]:
        print(f"{k}: {v:.1f}")
    print(f"gas into R201 {T_gin:.1f} K; liquid hold-up {V_liq:.1f} m3")

    # the values process/flowsheet.yaml cites from this script (balance-output contract); the
    # flowsheet's ids differ from some printed labels (printed S11/S13/S15 are S14/S15/S19)
    out = {sid: {"flow": v["flow"], "composition": v["composition"]} for sid, v in s.items()}
    out["S05"] = {"temperature": ns["T_mix"]}
    out["S06"] = {"temperature": ns["T_burn"]}
    out["S09"] = {"temperature": ns["T_r102"]}
    out["S13"] = {"temperature": T_k101}
    out["S20"] = {"temperature": T_gin}
    out["S27"] = {"temperature": T_k201}
    duties = {"Q01": Q_e100, "Q02": ns["Q_whb"], "Q03": ns["Q_e102"], "Q04": W_k101,
              "Q05": Q_e201, "Q06": W_p201, "Q07": Q_r201, "Q08": W_agit, "Q09": W_k201,
              "Q10": W_k301}
    out.update({sid: {"duty": q} for sid, q in duties.items()})
    write_balance_output({"design": out})
    # ---- checks
    no_fresh = no_gas["NO"]
    print(f"NO utilisation {cs['c'] * 0 + (no_fresh - cs['purge']['NO']) / no_fresh:.4f}; "
          f"NH3 per kg NH2OH {nh3_kg / NH2OH_KG_H:.4f}; H2 total per kg NH2OH "
          f"{(cs['h2_fresh'] + ns['h2_o2']) * MW['H2'] / NH2OH_KG_H:.4f}")
    n2o_kg = cs["purge"]["N2O"] * MW["N2O"]
    print(f"N2O emitted {n2o_kg:.2f} kg/h = {n2o_kg / NH2OH_KG_H * 1e3:.2f} g/kg NH2OH; "
          f"NO emitted {cs['purge']['NO'] * MW['NO']:.2f} kg/h")
    tot_in = nh3_kg + sum(kg({"O2": f["O2"], "AR": f["AR"]}).values()) + f["H2O"] * MW["H2O"] \
        + (cs["h2_fresh"] + ns["h2_o2"]) * MW["H2"] + acid_feed + demin * MW["H2O"]
    tot_out = M + sum(kg(cs["purge"]).values())
    print(f"overall mass in {tot_in:.2f} out {tot_out:.2f} kg/h (oxidiser excluded)")


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
