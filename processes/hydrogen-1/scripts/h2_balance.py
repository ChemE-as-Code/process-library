"""Heat and material balance of the SMR hydrogen plant (hydrogen-1), concept stage.

Run with `cheme run scripts/h2_balance.py` from the process folder. It prints the stream
values and duties that process/flowsheet.yaml gives as `assumed` with the source
"scripts/h2_balance.py" (DESIGN.md D-006), and the checks of DESIGN.md D-011.

What it calculates (every input is a design-basis value, ASSUMED, DESIGN.md):
- reformer outlet: ideal-gas equilibrium of steam methane reforming and water-gas shift (ethane
  and propane reformed completely), K evaluated at T_out + approach (cheme's convention), from
  the ideal-gas data of process/materials.yaml; cheme process propagate recalculates it;
- HT shift outlet: adiabatic ideal-gas equilibrium of the water-gas shift, the outlet
  temperature solved here (cheme recalculates the composition at that temperature);
- cooling train and separator: water the only condensable (Raoult's law, CoolProp IAPWS
  saturation pressure and heat of vaporisation), gases insoluble in the condensate;
- PSA: a specified split (hydrogen recovery and product purity, D-008), not a cycle model;
- furnace: complete combustion with a specified excess air; the trim natural gas is what
  closes the radiant section's energy balance at the specified bridgewall temperature;
- steam system: CoolProp IAPWS-IF97 enthalpies of water and steam.
Enthalpies of gases: ideal gas on the elements basis at 298.15 K (formation enthalpy plus
sensible heat), as cheme process reactors uses. Accuracy: a concept estimate.
"""

import math
from pathlib import Path

import yaml
from CoolProp.CoolProp import PropsSI
from scipy.optimize import brentq

ROOT = Path(__file__).resolve().parents[1]
MAT = yaml.safe_load((ROOT / "process" / "materials.yaml").read_text())
COMP = {c["id"]: c for c in MAT["components"]}
R = 8.314462618  # kJ/(kmol K)
T0 = 298.15
P_STD = 100.0  # kPa, standard state of the formation data

# ---- design basis (ASSUMED, DESIGN.md) ------------------------------------------------------
NG = {"CH4": 0.930, "C2H6": 0.035, "C3H8": 0.007, "CO2": 0.013, "N2": 0.015}  # D-004
AIR = {"N2": 0.7812, "O2": 0.2095, "AR": 0.0093}  # dry air (D-009)
PRODUCT_NM3H = 100000.0  # product gas to battery limit, Nm3/h at 273.15 K, 101.325 kPa (D-002)
NM3_PER_KMOL = 22.414
H2_PURITY = 0.999  # mol fraction, remainder N2 (D-008)
PSA_RECOVERY = 0.88  # H2 to product / H2 in feed (D-008)
RECYCLE = 0.03  # kmol product gas recycled to the HDS per kmol natural gas feedstock (D-005)
S_TO_C = 3.0  # kmol steam per kmol hydrocarbon carbon (D-007)
T_REF_OUT, P_REF_OUT, APPROACH_REF = 1143.15, 3200.0, -10.0  # D-007
T_HTS_IN, APPROACH_HTS = 623.15, 10.0  # D-007
T_HDS = 643.15  # D-005
T_MIX_PREHEAT = 893.15  # reformer inlet (D-007)
T_STEAM, P_STEAM = 673.15, 4300.0  # D-010
P_DRUM, T_ECON_OUT, P_BFW = 4500.0, 503.15, 5000.0  # D-010
BLOWDOWN = 0.01  # of the feed water (D-010)
T_SEP, P_SEP = 313.15, 2950.0  # D-007
T_BW, T_STACK = 1273.15, 423.15  # bridgewall and stack (D-009)
T_ECO_FLUE = 553.15  # flue gas entering the economizer coil, 22 K above drum saturation (D-010)
EXCESS_AIR = 0.10  # D-009
T_AMB = 288.15
ETA_COMP, ETA_FAN, ETA_PUMP = 0.75, 0.70, 0.70  # D-012
DP_FD, DP_ID = 5.0, 4.0  # kPa (D-012)


def cp_r(c, T):
    return sum(a * T**i for i, a in enumerate(COMP[c]["ideal_gas"]["cp_R"]))


def h_ig(c, T):
    """kJ/kmol, elements basis."""
    co = COMP[c]["ideal_gas"]["cp_R"]
    integ = sum(a / (i + 1) * (T ** (i + 1) - T0 ** (i + 1)) for i, a in enumerate(co))
    return COMP[c]["ideal_gas"]["dHf_298"] + R * integ


def s_ig(c, T):
    co = COMP[c]["ideal_gas"]["cp_R"]
    integ = co[0] * math.log(T / T0) + sum(a / i * (T**i - T0**i) for i, a in enumerate(co) if i)
    return COMP[c]["ideal_gas"]["S_298"] + R * integ


def g_ig(c, T):
    return h_ig(c, T) - T * s_ig(c, T)


def lnK(stoich, T):
    return -sum(nu * g_ig(c, T) for c, nu in stoich.items()) / (R * T)


def H(n, T):
    return sum(v * h_ig(c, T) for c, v in n.items())


def cp_mix(n, T):
    return R * sum(v * cp_r(c, T) for c, v in n.items())


def T_of_H(n, Htarget, lo=250.0, hi=1600.0):
    return brentq(lambda T: H(n, T) - Htarget, lo, hi)


def add(*ds):
    out = {}
    for d in ds:
        for k, v in d.items():
            out[k] = out.get(k, 0.0) + v
    return out


def scale(d, f):
    return {k: v * f for k, v in d.items()}


def mass(n):
    return sum(v * COMP[c]["molar_mass"] for c, v in n.items())


def frac(n):
    tot = sum(n.values())
    return {k: v / tot for k, v in n.items() if v > 0}


SMR = {"CH4": -1, "H2O": -1, "CO": 1, "H2": 3}
WGS = {"CO": -1, "H2O": -1, "CO2": 1, "H2": 1}
ETH = {"C2H6": -1, "H2O": -2, "CO": 2, "H2": 5}
PRO = {"C3H8": -1, "H2O": -3, "CO": 3, "H2": 7}


def react(n, stoich, xi):
    out = dict(n)
    for c, nu in stoich.items():
        out[c] = out.get(c, 0.0) + nu * xi
    return out


def _resid(n, r, lk, P):
    tot = sum(n.values())
    return sum(nu * math.log(max(n[c], 1e-300) / tot * P / P_STD) for c, nu in r.items()) - lk


def _solve_one(n_in, r, lk, P):
    """Extent of one reaction at equilibrium (bracketed between the reactants' limits)."""
    lo = -min(n_in.get(c, 0.0) / nu for c, nu in r.items() if nu > 0)
    hi = min(n_in.get(c, 0.0) / -nu for c, nu in r.items() if nu < 0)
    eps = 1e-12 * max(1.0, hi - lo)
    xi = brentq(lambda x: _resid(react(n_in, r, x), r, lk, P), lo + eps, hi - eps, xtol=1e-14)
    return react(n_in, r, xi)


def equilibrium(n_in, T, P, reactions, approach):
    """Ideal-gas equilibrium at T, K evaluated at T + approach. One reaction, or SMR + WGS."""
    Tk = T + approach
    if len(reactions) == 1:
        return _solve_one(n_in, reactions[0], lnK(reactions[0], Tk), P)
    smr, wgs = reactions
    lk1, lk2 = lnK(smr, Tk), lnK(wgs, Tk)

    def inner(x1):
        return _solve_one(react(n_in, smr, x1), wgs, lk2, P)

    hi = min(n_in["CH4"], n_in["H2O"])
    x1 = brentq(lambda x: _resid(inner(x), smr, lk1, P), 1e-9 * hi, hi * (1 - 1e-9), xtol=1e-14)
    return inner(x1)


def psat(T):
    if T >= 640.0:
        return math.inf
    return PropsSI("P", "T", T, "Q", 0, "Water") / 1000.0


def dhvap(T):  # kJ/kmol
    return (PropsSI("H", "T", T, "Q", 1, "Water") - PropsSI("H", "T", T, "Q", 0, "Water")) / 1000.0 * 18.0153


def split_water(n, T, P):
    """Vapour and liquid at T, P: water the only condensable."""
    dry = sum(v for c, v in n.items() if c != "H2O")
    if psat(T) >= P:
        return dict(n), 0.0
    nw_v = psat(T) * dry / (P - psat(T))
    nw = n.get("H2O", 0.0)
    if nw_v >= nw:
        return dict(n), 0.0
    vap = dict(n)
    vap["H2O"] = nw_v
    return vap, nw - nw_v


def H_wet(n, T, P):
    vap, liq = split_water(n, T, P)
    return H(n, T) - (liq * dhvap(T) if liq else 0.0)


def compress(n, T1, P1, P2, eta):
    """Ideal-gas compression: outlet T and shaft power (kW) for n kmol/h."""
    cp = cp_mix(n, T1) / sum(n.values())
    T2s = T1 * (P2 / P1) ** (R / cp)
    T2 = T1 + (T2s - T1) / eta
    T2 = brentq(lambda T: H(n, T) - H(n, T1) - (H(n, T2s) - H(n, T1)) / eta, T1, T2 + 200)
    return T2, (H(n, T2) - H(n, T1)) / 3600.0


def hw(T, P):  # water/steam, kJ/kg, IAPWS-IF97
    return PropsSI("H", "T", T, "P", P * 1000.0, "IF97::Water") / 1000.0


def plant(ng_proc):
    s = {}
    q = {}
    # feedstock and recycle
    ng = scale(NG, ng_proc)
    rec = {"H2": H2_PURITY * RECYCLE * ng_proc, "N2": (1 - H2_PURITY) * RECYCLE * ng_proc}
    T_rec, q["K101"] = compress(rec, T_SEP, 2850.0, 4100.0, ETA_COMP)
    feed = add(ng, rec)
    T_m101 = T_of_H(feed, H(ng, T_AMB) + H(rec, T_rec))
    q["E101"] = (H(feed, T_HDS) - H(feed, T_m101)) / 3600.0
    carbon = ng["CH4"] + 2 * ng["C2H6"] + 3 * ng["C3H8"]
    steam = {"H2O": S_TO_C * carbon}
    mixed = add(feed, steam)
    T_m102 = T_of_H(mixed, H(feed, T_HDS) + H(steam, T_STEAM))
    q["E102"] = (H(mixed, T_MIX_PREHEAT) - H(mixed, T_m102)) / 3600.0
    # reformer: C2+ reformed completely, then SMR + WGS equilibrium
    pre = react(react(mixed, ETH, mixed["C2H6"]), PRO, mixed["C3H8"])
    pre["C2H6"] = pre["C3H8"] = 0.0
    ref = equilibrium(pre, T_REF_OUT, P_REF_OUT, [SMR, WGS], APPROACH_REF)
    q["R102"] = (H(ref, T_REF_OUT) - H(mixed, T_MIX_PREHEAT)) / 3600.0
    q["E104"] = (H(ref, T_REF_OUT) - H(ref, T_HTS_IN)) / 3600.0
    # HT shift, adiabatic
    def hts_res(T):
        out = equilibrium(ref, T, 3050.0, [WGS], APPROACH_HTS)
        return H(out, T) - H(ref, T_HTS_IN)
    T_hts = brentq(hts_res, T_HTS_IN + 1, T_HTS_IN + 200)
    hts = equilibrium(ref, T_hts, 3050.0, [WGS], APPROACH_HTS)
    # separator
    vap, cond = split_water(hts, T_SEP, P_SEP)
    # PSA
    h2_prod = PSA_RECOVERY * vap["H2"]
    prod = {"H2": h2_prod, "N2": h2_prod * (1 - H2_PURITY) / H2_PURITY}
    tail = {c: v - prod.get(c, 0.0) for c, v in vap.items()}
    s.update(ng=ng, rec=rec, feed=feed, steam=steam, mixed=mixed, ref=ref, hts=hts, vap=vap,
             cond={"H2O": cond}, prod=prod, tail=tail)
    t = dict(T_rec=T_rec, T_m101=T_m101, T_m102=T_m102, T_hts=T_hts)
    return s, q, t


def furnace(s, q):
    """Trim natural gas and air that close the radiant balance; convection duty."""
    T_tail, T_trim = T_SEP, T_AMB

    def burn(x):
        trim = scale(NG, x)
        fuel = add(s["tail"], trim)
        o2 = (2 * fuel.get("CH4", 0) + 3.5 * fuel.get("C2H6", 0) + 5 * fuel.get("C3H8", 0)
              + 0.5 * fuel.get("H2", 0) + 0.5 * fuel.get("CO", 0))
        air = scale(AIR, (1 + EXCESS_AIR) * o2 / AIR["O2"])
        flue = add(fuel, air)
        flue["CO2"] += fuel.get("CH4", 0) + 2 * fuel.get("C2H6", 0) + 3 * fuel.get("C3H8", 0) + fuel.get("CO", 0)
        flue["H2O"] = flue.get("H2O", 0) + 2 * fuel.get("CH4", 0) + 3 * fuel.get("C2H6", 0) + 4 * fuel.get("C3H8", 0) + fuel.get("H2", 0)
        flue["O2"] -= o2
        for c in ("CH4", "C2H6", "C3H8", "H2", "CO"):
            flue[c] = 0.0
        T_air, w_fd = compress(air, T_AMB, 101.325, 101.325 + DP_FD, ETA_FAN)
        T_fuel = T_of_H(fuel, H(s["tail"], T_tail) + H(trim, T_trim))
        q_abs = (H(fuel, T_fuel) + H(air, T_air) - H(flue, T_BW)) / 3600.0
        return trim, fuel, air, flue, T_air, w_fd, T_fuel, q_abs

    x = brentq(lambda x: burn(x)[-1] - q["R102"], 0.0, 5 * sum(s["ng"].values()))
    trim, fuel, air, flue, T_air, w_fd, T_fuel, _ = burn(x)
    q["K301"] = w_fd
    q["E305"] = (H(flue, T_BW) - H(flue, T_STACK)) / 3600.0
    T_flue_out, q["K302"] = compress(flue, T_STACK, 99.0, 99.0 + DP_ID, ETA_FAN)
    s.update(trim=trim, fuel=fuel, air=air, flue=flue)
    return dict(T_air=T_air, T_fuel=T_fuel, T_flue_out=T_flue_out)


def steam_system(s, q, t):
    m_cond = mass(s["cond"])  # kg/h
    # D-010: the cold end of the convection section (flue gas 553 -> 423 K) heats the boiler
    # feed water (economizer coil E-402) and the low-temperature part of the feed preheat coil;
    # boiling and superheating (steam coil) take the rest above it.
    feed, n_feed_T0 = s["feed"], t["T_m101"]
    q_e101_low = (H(feed, T_ECO_FLUE - 20.0) - H(feed, n_feed_T0)) / 3600.0
    q["E402"] = (H(s["flue"], T_ECO_FLUE) - H(s["flue"], T_STACK)) / 3600.0 - q_e101_low
    q["E401_coil"] = q["E305"] - q["E101"] - q["E102"] - q["E402"]  # convection steam coil
    h_s, h_bd = hw(T_STEAM, P_STEAM), PropsSI("H", "P", P_DRUM * 1e3, "Q", 0, "IF97::Water") / 1e3
    h_eco = hw(T_ECON_OUT, P_BFW)
    q_drum = (q["E104"] + q["E401_coil"]) * 3600.0  # kJ/h
    m_fw = q_drum / ((1 - BLOWDOWN) * h_s + BLOWDOWN * h_bd - h_eco)
    m_s, m_bd = (1 - BLOWDOWN) * m_fw, BLOWDOWN * m_fw
    m_ps = mass(s["steam"])
    m_mu = m_fw - m_cond
    h_mix = (m_mu * hw(298.15, 300.0) + m_cond * hw(T_SEP, 300.0)) / m_fw
    T_mix = PropsSI("T", "H", h_mix * 1e3, "P", 300e3, "IF97::Water")
    rho = PropsSI("D", "H", h_mix * 1e3, "P", 300e3, "IF97::Water")
    q["P401"] = m_fw / rho * (P_BFW - 300.0) / ETA_PUMP / 3600.0  # kW
    h_pump = h_mix + q["P401"] * 3600.0 / m_fw
    T_pump = PropsSI("T", "H", h_pump * 1e3, "P", P_BFW * 1e3, "IF97::Water")
    q["E201"] = m_fw * (h_eco - h_pump) / 3600.0 - q["E402"]
    h_int = h_pump + q["E402"] * 3600.0 / m_fw  # the feed water passes E-402 first, then E-401
    if h_int >= hw(T_STACK - 10.0, P_BFW):
        raise SystemExit("E-402: feed water leaves hotter than the stack gas allows")
    t["T_bfw_int"] = PropsSI("T", "H", h_int * 1e3, "P", P_BFW * 1e3, "IF97::Water")
    # process side of E-201 and E-202
    hts, T_hts = s["hts"], t["T_hts"]
    H201 = H_wet(hts, T_hts, 3000.0) - q["E201"] * 3600.0
    T201 = brentq(lambda T: H_wet(hts, T, 3000.0) - H201, T_SEP, T_hts)
    q["E202"] = (H201 - H_wet(hts, T_SEP, P_SEP)) / 3600.0
    t.update(T_mix_w=T_mix, T_pump=T_pump, T201=T201)
    return dict(m_cond=m_cond, m_fw=m_fw, m_s=m_s, m_bd=m_bd, m_ps=m_ps, m_ex=m_s - m_ps, m_mu=m_mu,
                T_bd=PropsSI("T", "P", P_DRUM * 1e3, "Q", 0, "IF97::Water"))


def lhv(n):  # kJ/h at 298.15 K, water as vapour
    o2 = 2 * n.get("CH4", 0) + 3.5 * n.get("C2H6", 0) + 5 * n.get("C3H8", 0) + 0.5 * n.get("H2", 0) + 0.5 * n.get("CO", 0)
    burnt = {"CO2": n.get("CH4", 0) + 2 * n.get("C2H6", 0) + 3 * n.get("C3H8", 0) + n.get("CO", 0),
             "H2O": 2 * n.get("CH4", 0) + 3 * n.get("C2H6", 0) + 4 * n.get("C3H8", 0) + n.get("H2", 0)}
    fuel = {c: n.get(c, 0) for c in ("CH4", "C2H6", "C3H8", "H2", "CO")}
    return H(add(fuel, {"O2": o2}), T0) - H(burnt, T0)


def fmt(n):
    return "{" + ", ".join(f"{c}: {v:.8f}" for c, v in frac(n).items()) + "}"


def main():
    s1, _, _ = plant(1.0)
    export1 = sum(s1["prod"].values()) - RECYCLE
    ng_proc = PRODUCT_NM3H / NM3_PER_KMOL / export1
    s, q, t = plant(ng_proc)
    t.update(furnace(s, q))
    w = steam_system(s, q, t)
    export = scale(s["prod"], 1 - RECYCLE * ng_proc / sum(s["prod"].values()))

    print(f"natural gas feedstock {ng_proc:.3f} kmol/h, export product {sum(export.values()):.2f} kmol/h")
    rows = [
        ("S1 NG feedstock", s["ng"], T_AMB, 4000.0),
        ("S2 recycle H2 (compressed)", s["rec"], t["T_rec"], 4100.0),
        ("S3 NG + H2", s["feed"], t["T_m101"], 4000.0),
        ("S4 to HDS", s["feed"], T_HDS, 3900.0),
        ("S5 desulfurised feed", s["feed"], T_HDS, 3850.0),
        ("S6 process steam", s["steam"], T_STEAM, P_STEAM),
        ("S7 mixed feed", s["mixed"], t["T_m102"], 3800.0),
        ("S8 reformer inlet", s["mixed"], T_MIX_PREHEAT, 3500.0),
        ("S9 reformed gas", s["ref"], T_REF_OUT, P_REF_OUT),
        ("S10 HTS inlet", s["ref"], T_HTS_IN, 3150.0),
        ("S11 HTS outlet", s["hts"], t["T_hts"], 3050.0),
        ("S12 after E-201", s["hts"], t["T201"], 3000.0),
        ("S13 to separator", s["hts"], T_SEP, P_SEP),
        ("S14 PSA feed", s["vap"], T_SEP, P_SEP),
        ("S15 process condensate", s["cond"], T_SEP, P_SEP),
        ("S16 PSA product", s["prod"], T_SEP, 2850.0),
        ("S17 H2 product", export, T_SEP, 2850.0),
        ("S18 recycle H2", s["rec"], T_SEP, 2850.0),
        ("S19 PSA tail gas", s["tail"], T_SEP, 130.0),
        ("S20 trim NG", s["trim"], T_AMB, 4000.0),
        ("S21 fuel", s["fuel"], t["T_fuel"], 130.0),
        ("S22 air", s["air"], T_AMB, 101.325),
        ("S23 air to burners", s["air"], t["T_air"], 101.325 + DP_FD),
        ("S24 flue gas radiant", s["flue"], T_BW, 101.0),
        ("S25 flue gas to ID fan", s["flue"], T_STACK, 99.0),
        ("S26 flue gas to stack", s["flue"], t["T_flue_out"], 99.0 + DP_ID),
    ]
    for name, n, T, P in rows:
        print(f"{name:28s} T {T:8.2f} P {P:8.2f} m {mass(n):12.2f} kg/h n {sum(n.values()):10.3f} kmol/h {fmt(n)}")
    print("water side (kg/h):", {k: round(v, 2) for k, v in w.items()})
    print("temperatures:", {k: round(v, 2) for k, v in t.items()})
    print("duties kW:", {k: round(v, 1) for k, v in q.items()})
    # checks
    c_in = sum((v * k) for v, k in [(s["ng"]["CH4"] + s["trim"]["CH4"], 1), (s["ng"]["C2H6"] + s["trim"]["C2H6"], 2),
                                     (s["ng"]["C3H8"] + s["trim"]["C3H8"], 3), (s["ng"]["CO2"] + s["trim"]["CO2"], 1)])
    print(f"carbon in {c_in:.3f} kmol/h, CO2 out (flue) {s['flue']['CO2']:.3f} kmol/h")
    m_h2 = mass(export)
    co2_proc = (s["ng"]["CH4"] + 2 * s["ng"]["C2H6"] + 3 * s["ng"]["C3H8"] + s["ng"]["CO2"]) * 44.0095
    co2_fuel = (s["trim"]["CH4"] + 2 * s["trim"]["C2H6"] + 3 * s["trim"]["C3H8"] + s["trim"]["CO2"]) * 44.0095
    print(f"product {m_h2:.1f} kg/h; CO2 feedstock carbon {co2_proc / m_h2:.3f}, trim-fuel carbon {co2_fuel / m_h2:.3f} kg/kg product")
    lhv_ng = lhv(s["ng"]) + lhv(s["trim"])
    print(f"NG LHV in {lhv_ng / 3.6e6:.2f} MW ({lhv_ng / m_h2 / 1000:.1f} MJ/kg product); H2 LHV out {lhv(export) / 3.6e6:.2f} MW;"
          f" tail gas LHV {lhv(s['tail']) / 3.6e6:.2f} MW; trim LHV {lhv(s['trim']) / 3.6e6:.2f} MW; export steam {w['m_ex'] / m_h2:.2f} kg/kg")
    print(f"ln(Q/K) check reformer approach {APPROACH_REF}, HTS approach {APPROACH_HTS}; steam/dry-gas, CH4 slip dry {s['ref']['CH4'] / (sum(s['ref'].values()) - s['ref']['H2O']):.4f}")

    # the values process/flowsheet.yaml cites from this script (balance-output contract)
    out = {}
    for name, n, T, P in rows:
        out[name.split()[0]] = {"flow": mass(n), "temperature": T, "pressure": P,
                                "composition": frac(n)}
    out["S27"] = {"flow": w["m_mu"], "temperature": 298.15}
    out["S28"] = {"flow": w["m_fw"], "temperature": t["T_mix_w"]}
    out["S29"] = {"flow": w["m_fw"], "temperature": t["T_pump"]}
    out["S30"] = {"flow": w["m_fw"], "temperature": t["T_bfw_int"]}
    out["S32"] = {"flow": w["m_s"], "temperature": T_STEAM}
    out["S34"] = {"flow": w["m_bd"], "temperature": w["T_bd"]}
    duties = {"Q1": "K101", "Q2": "E101", "Q3": "E102", "Q4": "R102", "Q5": "E104",
              "Q6": "E401_coil", "Q7": "E402", "Q8": "E201", "Q9": "E202", "Q10": "K301",
              "Q11": "K302", "Q12": "P401"}
    out.update({sid: {"duty": q[k]} for sid, k in duties.items()})
    write_balance_output({"design": out})


def write_balance_output(cases):
    """With BALANCE_OUTPUT set, write the values the flowsheet cites from this script as JSON.

    The process library's balance-output contract (docs/adr/0024 of the library): case ->
    stream id -> quantity, in the flowsheet's units and basis. The library's
    scripts/check_balance_scripts.py re-runs this script and compares them with
    process/flowsheet.yaml.
    """
    import json
    import os

    target = os.environ.get("BALANCE_OUTPUT")
    if target:
        doc = {"contract": "balance-output/1", "script": f"scripts/{Path(__file__).name}",
               "cases": cases}
        Path(target).write_text(json.dumps(doc, indent=1, default=float), encoding="utf-8")


if __name__ == "__main__":
    main()
