"""Concept heat and material balance of thionyl-chloride-1 (DESIGN.md D-006).

Independent of cheme-as-code's property packages, none of which is qualified for the sulfur
chlorides, thionyl chloride or the alkaline scrubber liquor (DESIGN.md D-006).

Model (every choice is a decision in DESIGN.md):
- ideal gas with the Cp/R polynomials and formation enthalpies of process/materials.yaml;
- liquid enthalpy = ideal-gas enthalpy minus the heat of vaporization of the `thermo` package
  (thermo.Chemical(...).EnthalpyVaporization); liquid sulfur from approximate condensed-phase
  data (D-006);
- condensation by Raoult's law with the vapour pressures of the `thermo` package, O2 insoluble;
- reactors as conversion models: every reaction converts its fraction of the key component's
  inlet flow (the rule of cheme's conversion reactor);
- the recycle loops (sulfur chlorides through purification, SO2/Cl2 gas through the degasser
  and compressor) closed by successive substitution.

Run: cheme run scripts/balance.py [--yaml build/streams.yaml]
(prints the stream table and duties; with --yaml also writes the flowsheet streams to build/)
"""

import sys

from thermo import Chemical

R = 8.314462618e-3  # kJ/(mol K)

MW = {"SOCL2": 118.97, "SCL2": 102.971, "S2CL2": 135.036, "SO2": 64.064, "CL2": 70.906,
      "O2": 31.999, "S": 32.065, "H2O": 18.015, "NAOH": 39.997, "NA2SO3": 126.043,
      "NA2SO4": 142.042, "NACL": 58.443, "NAOCL": 74.442, "NA2S2O3": 158.108}
CAS = {"SOCL2": "7719-09-7", "SCL2": "10545-99-0", "S2CL2": "10025-67-9", "SO2": "7446-09-5",
       "CL2": "7782-50-5", "H2O": "7732-18-5"}
# ideal gas: dHf kJ/mol, cp/R polynomial (cheme chemistry thermo; materials.yaml)
IG = {
    "SOCL2": (-212.5, [4.42692, 0.0189314, -2.92695e-05, 2.22068e-08, -6.64823e-12]),
    "SCL2": (-17.57, [3.65028, 0.0140413, -2.46912e-05, 2.02375e-08, -6.34247e-12]),
    "S2CL2": (-16.74, [5.51588, 0.0180999, -3.01972e-05, 2.32692e-08, -6.82476e-12]),
    "SO2": (-296.8, [4.417, -0.002234, 2.344e-05, -3.271e-08, 1.393e-11]),
    "CL2": (0.0, [3.056, 0.0053708, -8.098e-06, 5.693e-09, -1.5256e-12]),
    "O2": (0.0, [3.63, -0.001794, 6.58e-06, -6e-09, 1.79e-12]),
    "H2O": (-241.822, [4.395, -0.004186, 1.405e-05, -1.564e-08, 6.32e-12]),
}
CONDENSABLE = ["SOCL2", "SCL2", "S2CL2", "SO2", "CL2"]
_CHEM = {c: Chemical(CAS[c]) for c in CAS}

# --- design inputs (DESIGN.md decisions) ------------------------------------------------------
PRODUCT_KG_H = 3750.0                                             # D-002, ASSUMED 30 kt/a
W_PRODUCT = {"SOCL2": 0.997, "SCL2": 0.001, "S2CL2": 0.002}       # D-002, ASSUMED spec
Y_O2_FEED = 0.001                                                  # D-003, Cl2 feed 0.1 mol% O2
X_R101_S = 1.0          # D-004: 2 S + Cl2 -> S2Cl2, sulfur fully converted
X_R102 = 0.90           # D-004: S2Cl2 + Cl2 -> 2 SCl2, of the inlet S2Cl2, ASSUMED
CL2_EXCESS = 1.05       # D-005: Cl2 at the reactor inlet 5 % over stoichiometric (US2431823: 0-10 %)
SO2_EXCESS = 2.00       # D-005: SO2 100 % over stoichiometric (US2431823)
X_R201_S2 = 0.95        # D-005: S2Cl2 + Cl2 -> 2 SCl2 in the reactor, ASSUMED
X_R201 = 0.75           # D-005: SCl2 + SO2 + Cl2 -> 2 SOCl2, of the inlet SCl2 (DE2430631A1: 70-75 %)
T_R101, T_R102, T_VAP, T_PRE, T_R201 = 343.15, 313.15, 383.15, 398.15, 473.15
T_COND1, T_SEP, T_DEG_COND = 308.15, 263.15, 263.15
# T201 bottoms (S22, S30): Raoult bubble point of the lights-free crude at P_DEG, computed in
# main() (D-007; review 2026-10-28 R-01: a fixed 345 K lay below it and would leave SO2/Cl2)
P_R201_IN, P_R201_OUT, P_SEP, P_DEG, P_K201 = 170.0, 140.0, 130.0, 125.0, 180.0
PURGE = 0.01            # D-007: fraction of the recycle gas purged to the scrubber, ASSUMED
S_EXCESS_PURIF = 1.10   # D-008: sulfur dosed 10 % over the SCl2 converted in T301, ASSUMED
W_SOCL2_BOTTOMS = 0.20  # D-008: SOCl2 left in the T301 bottoms, ASSUMED
REFLUX = 2.0            # D-008: T301 reflux ratio, ASSUMED (no column design yet)
T_DIST, T_BOT, T_PROD = 349.15, 386.15, 308.15
STRIP_FACTOR = 1.5      # D-007: T201 boil-up = 1.5 x the latent heat of the stripped lights, ASSUMED
X_SCRUB = 0.999         # D-009: destruction in the caustic scrubber, ASSUMED
NAOH_EXCESS = 1.20      # D-009
W_NAOH_SCRUB = 0.10     # D-009: scrubbing liquor 10 wt% NaOH
T_SCRUB, P_SCRUB = 303.15, 105.0


def cp_int(a, t0, t1):
    def H(t):
        return sum(a[i] * t ** (i + 1) / (i + 1) for i in range(5))
    return R * (H(t1) - H(t0))


def hvap(c, T):
    return _CHEM[c].EnthalpyVaporization(T) / 1000.0  # kJ/mol


def psat(c, T):
    return _CHEM[c].VaporPressure(T) / 1000.0  # kPa


def bubble_t(liq, P, lo=250.0, hi=450.0):
    """Raoult bubble temperature (K) of a liquid {component: kmol/h} at P kPa, by bisection."""
    x = {c: n / sum(liq.values()) for c, n in liq.items() if n > 0}
    for _ in range(60):
        mid = 0.5 * (lo + hi)
        if sum(xc * psat(c, mid) for c, xc in x.items()) > P:
            hi = mid
        else:
            lo = mid
    return 0.5 * (lo + hi)


def h_sulfur(T):
    """Condensed sulfur, kJ/mol, rhombic at 298.15 K = 0 (approximate data, D-006)."""
    h = 0.0228 * (min(T, 368.3) - 298.15)
    if T > 368.3:
        h += 0.401 + 0.0240 * (min(T, 388.36) - 368.3)
    if T > 388.36:
        h += 1.721 + 0.0310 * (T - 388.36)
    return h


def h_comp(c, T, phase):
    if c == "S":
        return h_sulfur(T)
    dhf, a = IG[c]
    h = dhf + cp_int(a, 298.15, T)
    if phase == "l" and c != "O2":
        h -= hvap(c, T)
    return h


def H(stream, T, phase):
    """kW for a stream {comp: kmol/h}; phase 'g' or 'l' (O2 always gas)."""
    return sum(n * h_comp(c, T, phase) for c, n in stream.items() if n) / 3.6


def add(*ss):
    out = {}
    for s in ss:
        for c, n in s.items():
            out[c] = out.get(c, 0.0) + n
    return out


def scale(s, f):
    return {c: n * f for c, n in s.items()}


def tot(s):
    return sum(s.values())


def mass(s):
    return sum(n * MW[c] for c, n in s.items())


def flash(feed, T, P):
    """Raoult flash, O2 insoluble. Returns (vapour, liquid) in kmol/h."""
    K = {c: psat(c, T) / P for c in feed if c in CONDENSABLE}
    z = {c: n / tot(feed) for c, n in feed.items()}
    def rr(v):
        s = sum(z[c] * (K[c] - 1) / (1 + v * (K[c] - 1)) for c in K)
        s += sum(z[c] / v for c in z if c not in K) if v > 0 else 1e9
        return s
    lo, hi = 1e-9, 1.0
    if rr(hi) > 0:  # all vapour
        return dict(feed), {c: 0.0 for c in feed}
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        if rr(mid) > 0:
            lo = mid
        else:
            hi = mid
    v = 0.5 * (lo + hi)
    F = tot(feed)
    liq = {c: (F * (1 - v) * z[c] / (1 + v * (K[c] - 1)) if c in K else 0.0) for c in feed}
    vap = {c: feed[c] - liq[c] for c in feed}
    return vap, liq


def t_adiabatic_mix(streams_phases, P, guess=330.0):
    """Gas mixture temperature from the enthalpy of the inlets (all vapour at outlet)."""
    hin = sum(H(s, T, ph) for s, T, ph in streams_phases)
    mix = add(*[s for s, _, _ in streams_phases])
    lo, hi = 200.0, 600.0
    for _ in range(100):
        mid = 0.5 * (lo + hi)
        if H(mix, mid, "g") > hin:
            hi = mid
        else:
            lo = mid
    return mix, 0.5 * (lo + hi)


def solve():
    prod = {c: PRODUCT_KG_H * w / MW[c] for c, w in W_PRODUCT.items()}
    cl2_feed_total_guess = 0.0
    s_a = 0.5 * prod["SOCL2"] * 0.7       # sulfur to R101, kmol/h (iterated)
    bottoms = {"S2CL2": 0.0, "S": 0.0, "SOCL2": 0.0}
    rec_gas = {c: 0.0 for c in ["SO2", "CL2", "O2", "SOCL2", "SCL2", "S2CL2"]}
    o2_in = 0.0
    for it in range(5000):
        # R101: 2 S + Cl2 -> S2Cl2 (sulfur from the feed and dissolved in the bottoms recycle)
        s_in = s_a + bottoms["S"]
        cl2_r101 = 0.5 * X_R101_S * s_in
        r101_out = add(bottoms, {"S": -X_R101_S * s_in, "S2CL2": 0.5 * X_R101_S * s_in})
        # R102: S2Cl2 + Cl2 -> 2 SCl2, of the inlet S2Cl2
        xi = X_R102 * r101_out["S2CL2"]
        cl2_r102 = xi
        r102_out = add(r101_out, {"S2CL2": -xi, "SCL2": 2 * xi})
        r102_out = {c: n for c, n in r102_out.items() if c != "S" or n > 1e-12}
        r102_out.pop("S", None)
        # O2 of the chlorine feed: carried in the liquid as dissolved gas (D-003)
        # reactor inlet specification (D-005)
        n_scl2 = r102_out.get("SCL2", 0) + rec_gas["SCL2"]
        n_s2 = r102_out.get("S2CL2", 0) + rec_gas["S2CL2"]
        cl2_stoich = n_scl2 + 3 * n_s2
        so2_stoich = n_scl2 + 2 * n_s2
        cl2_m201 = CL2_EXCESS * cl2_stoich - rec_gas["CL2"]
        so2_fresh = SO2_EXCESS * so2_stoich - rec_gas["SO2"]
        cl2_total = cl2_r101 + cl2_r102 + cl2_m201
        o2_in = cl2_total * Y_O2_FEED / (1 - Y_O2_FEED)
        o2_split = {"r101": o2_in * cl2_r101 / cl2_total, "r102": o2_in * cl2_r102 / cl2_total,
                    "m201": o2_in * cl2_m201 / cl2_total}
        scl2_liq = add(r102_out, {"O2": o2_split["r101"] + o2_split["r102"]})
        feed_r201 = add(scl2_liq, {"CL2": cl2_m201, "O2": o2_split["m201"]}, {"SO2": so2_fresh},
                        rec_gas)
        # R201 (parallel conversion of inlet flows)
        x1 = X_R201_S2 * feed_r201.get("S2CL2", 0)
        x2 = X_R201 * feed_r201.get("SCL2", 0)
        out_r201 = add(feed_r201, {"S2CL2": -x1, "CL2": -x1, "SCL2": 2 * x1},
                       {"SCL2": -x2, "SO2": -x2, "CL2": -x2, "SOCL2": 2 * x2})
        # condensation
        vap1, liq1 = flash(out_r201, T_COND1, P_SEP + 5)
        gas, crude_raw = flash(out_r201, T_SEP, P_SEP)
        # T201 degasser: lights overhead, heavies at Raoult over the lights-free crude at the
        # overhead condenser (D-007)
        lights = {c: crude_raw.get(c, 0) for c in ["SO2", "CL2", "O2"]}
        heavy = {c: crude_raw.get(c, 0) for c in ["SOCL2", "SCL2", "S2CL2"]}
        xh = {c: n / tot(heavy) for c, n in heavy.items()}
        yh = {c: xh[c] * psat(c, T_DEG_COND) / P_DEG for c in heavy}
        n_ovh_heavy_tot = tot(lights) * sum(yh.values()) / (1 - sum(yh.values()))
        ovh_heavy = {c: n_ovh_heavy_tot * yh[c] / sum(yh.values()) for c in heavy}
        deg_ovh = add(lights, ovh_heavy)
        crude = {c: heavy[c] - ovh_heavy[c] for c in heavy}
        # recycle gas and purge
        gas_mix = add(gas, deg_ovh)
        purge = scale(gas_mix, PURGE)
        new_rec = scale(gas_mix, 1 - PURGE)
        # T301: sulfur treatment SCl2 + S -> S2Cl2, then distillation
        scl2_conv = crude["SCL2"] - prod["SCL2"]
        s_b = S_EXCESS_PURIF * scl2_conv
        t301_in = add(crude, {"S": s_b})
        t301_out = add(t301_in, {"SCL2": -scl2_conv, "S": -scl2_conv, "S2CL2": scl2_conv})
        bot = {"S2CL2": t301_out["S2CL2"] - prod["S2CL2"], "S": t301_out["S"], "SCL2": 0.0}
        m_nonsocl2 = bot["S2CL2"] * MW["S2CL2"] + bot["S"] * MW["S"]
        bot["SOCL2"] = m_nonsocl2 * W_SOCL2_BOTTOMS / (1 - W_SOCL2_BOTTOMS) / MW["SOCL2"]
        dist_socl2 = t301_out["SOCL2"] - bot["SOCL2"]
        # update
        ratio = prod["SOCL2"] / dist_socl2
        s_a *= ratio ** 0.7
        bottoms = {"S2CL2": bot["S2CL2"], "S": bot["S"], "SOCL2": bot["SOCL2"]}
        err = max(abs(new_rec[c] - rec_gas[c]) for c in rec_gas) + abs(ratio - 1)
        rec_gas = {c: new_rec.get(c, 0.0) for c in rec_gas}
        if "--debug" in sys.argv and it % 20 == 0:
            print(it, f"{err:.3e}", f"s_a {s_a:.4f}", f"so2_fresh {so2_fresh:.4f}",
                  {c: round(v, 3) for c, v in rec_gas.items()})
        if it > 5 and err < 1e-9:
            break
    else:
        raise RuntimeError("not converged")
    return locals()


def scrubber(purge):
    """Caustic scrubber T401 (D-009). Returns NaOH feed, water, gas out, liquor."""
    g = {c: purge.get(c, 0.0) for c in ["SO2", "CL2", "SOCL2", "SCL2", "S2CL2", "O2"]}
    conv = {c: X_SCRUB * g[c] for c in g if c != "O2"}
    # SO2 + 2 NaOH -> Na2SO3 + H2O ; SOCl2 + 4 NaOH -> Na2SO3 + 2 NaCl + 2 H2O
    # 2 SCl2 + 6 NaOH -> Na2S2O3 + 4 NaCl + 3 H2O ; 2 S2Cl2 + 6 NaOH -> Na2S2O3 + 2 S + 4 NaCl + 3 H2O
    # Cl2 + Na2SO3 + 2 NaOH -> Na2SO4 + 2 NaCl + H2O (with sulfite), rest Cl2 + 2 NaOH -> NaCl + NaOCl + H2O
    sulfite = conv["SO2"] + conv["SOCL2"]
    cl2_a = min(conv["CL2"], sulfite)
    cl2_b = conv["CL2"] - cl2_a
    naoh_use = (2 * conv["SO2"] + 4 * conv["SOCL2"] + 3 * conv["SCL2"] + 3 * conv["S2CL2"]
                + 2 * cl2_a + 2 * cl2_b)
    naoh_feed = NAOH_EXCESS * naoh_use
    w50 = naoh_feed * MW["NAOH"] / MW["H2O"]            # water in the 50 wt% caustic, kmol
    m_liquor = naoh_feed * MW["NAOH"] / W_NAOH_SCRUB
    water_dil = (m_liquor - naoh_feed * MW["NAOH"]) / MW["H2O"] - w50
    liq = {"NAOH": naoh_feed - naoh_use,
           "NA2SO3": sulfite - cl2_a,
           "NA2SO4": cl2_a,
           "NACL": 2 * conv["SOCL2"] + 2 * conv["SCL2"] + 2 * conv["S2CL2"] + 2 * cl2_a + cl2_b,
           "NAOCL": cl2_b,
           "NA2S2O3": 0.5 * conv["SCL2"] + 0.5 * conv["S2CL2"],
           "S": conv["S2CL2"],
           "H2O": w50 + water_dil + conv["SO2"] + 2 * conv["SOCL2"] + 1.5 * conv["SCL2"]
                  + 1.5 * conv["S2CL2"] + cl2_a + cl2_b}
    gas_out = {c: g[c] - conv.get(c, 0.0) for c in g}
    y_h2o = _CHEM["H2O"].VaporPressure(T_SCRUB) / 1000.0 / P_SCRUB
    n_h2o = tot(gas_out) * y_h2o / (1 - y_h2o)
    gas_out["H2O"] = n_h2o
    liq["H2O"] -= n_h2o
    reac = {"SO2": conv["SO2"], "SOCL2": conv["SOCL2"], "SCL2": conv["SCL2"],
            "S2CL2": conv["S2CL2"], "CL2_sulfite": cl2_a, "CL2_hypo": cl2_b}
    return naoh_feed, w50, water_dil, gas_out, liq, reac


def main():
    r = solve()
    prod = r["prod"]
    out = {}
    # feeds
    s_a, s_b = r["s_a"], r["s_b"]
    cl2_r101, cl2_r102, cl2_m201 = r["cl2_r101"], r["cl2_r102"], r["cl2_m201"]
    o2 = r["o2_split"]
    cl2_tot = cl2_r101 + cl2_r102 + cl2_m201
    T_CRUDE = bubble_t(r["crude"], P_DEG)
    st = {}
    st["S1"] = ({"S": s_a + s_b}, 413.15, "l")
    st["S1A"] = ({"S": s_a}, 413.15, "l")
    st["S1B"] = ({"S": s_b}, 413.15, "l")
    st["S2"] = ({"CL2": cl2_tot, "O2": r["o2_in"]}, 313.15, "g")
    st["S2A"] = ({"CL2": cl2_r101, "O2": o2["r101"]}, 313.15, "g")
    st["S2B"] = ({"CL2": cl2_r102, "O2": o2["r102"]}, 313.15, "g")
    st["S2C"] = ({"CL2": cl2_m201, "O2": o2["m201"]}, 313.15, "g")
    st["S3"] = ({"SO2": r["so2_fresh"]}, 298.15, "l")
    st["S10"] = (add(r["r101_out"], {"O2": o2["r101"]}), T_R101, "l")
    st["S10"][0].pop("S", None)
    st["S11"] = (r["scl2_liq"], T_R102, "l")
    st["S12"] = (r["scl2_liq"], T_VAP, "g")
    st["S13"] = ({"SO2": r["so2_fresh"]}, 313.15, "g")
    mix_in = [(st["S12"][0], T_VAP, "g"), (st["S2C"][0], 313.15, "g"), (st["S13"][0], 313.15, "g")]
    k_in = r["new_rec"]
    # K201 compressor: isentropic from P_DEG to P_K201, efficiency 0.70 (D-007)
    t_k_in = T_SEP
    cp_mix = sum(n * R * sum(IG[c][1][i] * t_k_in ** i for i in range(5)) for c, n in k_in.items()) / tot(k_in)
    kappa = cp_mix / (cp_mix - R)
    t_is = t_k_in * (P_K201 / P_DEG) ** ((kappa - 1) / kappa)
    t_k_out = t_k_in + (t_is - t_k_in) / 0.70
    w_k201 = (H(k_in, t_k_out, "g") - H(k_in, t_k_in, "g")) / 0.95
    st["S24"] = (k_in, t_k_out, "g")
    mix_in.append((k_in, t_k_out, "g"))
    feed_mix, t_mix = t_adiabatic_mix(mix_in, P_R201_IN)
    st["S14"] = (feed_mix, t_mix, "g")
    st["S15"] = (feed_mix, T_PRE, "g")
    st["S16"] = (r["out_r201"], T_R201, "g")
    st["S17"] = (r["out_r201"], T_COND1, "2")
    st["S18"] = (r["out_r201"], T_SEP, "2")
    st["S19"] = (r["gas"], T_SEP, "g")
    st["S20"] = (r["crude_raw"], T_SEP, "l")
    st["S21"] = (r["deg_ovh"], T_DEG_COND, "g")
    st["S22"] = (r["crude"], T_CRUDE, "l")
    st["S23"] = (r["gas_mix"], T_SEP, "g")
    st["S25"] = (r["purge"], T_SEP, "g")
    st["S30"] = (r["t301_in"], T_CRUDE, "l")
    st["S31"] = (prod, T_PROD, "l")
    st["S32"] = (r["bottoms"], T_BOT, "l")
    naoh, w50, wdil, gas_out, liq, reac = scrubber(r["purge"])
    st["S40"] = ({"NAOH": naoh, "H2O": w50}, 313.15, "aq")
    st["S41"] = ({"H2O": wdil}, 298.15, "aq")
    st["S42"] = ({"NAOH": naoh, "H2O": w50 + wdil}, 303.15, "aq")
    st["S43"] = (gas_out, T_SCRUB, "g")
    st["S44"] = (liq, T_SCRUB + 5, "aq")

    # duties (kW); positive = heat into the process
    def Hs(k, phase=None, T=None):
        s, t, ph = st[k]
        return H(s, T or t, phase or ph)

    def H2(stream, T, P):  # two-phase by Raoult flash
        v, l = flash(stream, T, P)
        return H(v, T, "g") + H(l, T, "l")

    duty = {}
    duty["R101"] = Hs("S10") - Hs("S1A") - Hs("S2A") - Hs("S32")
    duty["R102"] = Hs("S11") - Hs("S10") - Hs("S2B")
    duty["E201"] = Hs("S12") - Hs("S11")
    duty["E202"] = Hs("S13") - Hs("S3")
    duty["E203"] = H(feed_mix, T_PRE, "g") - H(feed_mix, t_mix, "g")
    duty["R201"] = H(r["out_r201"], T_R201, "g") - H(feed_mix, T_PRE, "g")
    h17 = H2(r["out_r201"], T_COND1, P_SEP + 5)
    h18 = H(r["gas"], T_SEP, "g") + H(r["crude_raw"], T_SEP, "l")
    duty["E204"] = h17 - H(r["out_r201"], T_R201, "g")
    duty["E205"] = h18 - h17
    # T201: reboiler heats the crude to T_CRUDE and boils off the lights (x STRIP_FACTOR);
    # the overhead condenser at T_DEG_COND takes the extra boil-up back (D-007)
    lat = sum(n * hvap(c, T_SEP) for c, n in r["lights"].items() if c != "O2") / 3.6
    q_reb = (H(r["crude"], T_CRUDE, "l") - H(r["crude"], T_SEP, "l")) + STRIP_FACTOR * lat \
        + (H(r["ovh_heavy"], T_DEG_COND, "g") - H(r["ovh_heavy"], T_SEP, "l"))
    q_cond = -(STRIP_FACTOR - 1.0) * lat
    q_bal = Hs("S21") + Hs("S22") - Hs("S20")
    duty["T201_reb"] = q_reb
    duty["T201_cond"] = q_bal - q_reb
    duty["K201"] = w_k201
    # T301: condenser (R+1) D latent at the top + subcooling of the product; reboiler closes
    # the balance including the heat of SCl2 + S -> S2Cl2 (D-008)
    D = tot(prod)
    q_c = -(REFLUX + 1) * D * hvap("SOCL2", T_DIST) / 3.6 + (H(prod, T_PROD, "l") - H(prod, T_DIST, "l"))
    q_reb301 = Hs("S31") + Hs("S32") - Hs("S30") - Hs("S1B") - q_c
    duty["T301_cond"] = q_c
    duty["T301_reb"] = q_reb301
    # pumps (D-010): hydraulic power V dp / 0.6 / 0.95, liquid density ASSUMED
    def pump(kg_h, rho, dp_kpa):
        return kg_h / rho / 3600 * dp_kpa / 0.6 / 0.95
    duty["P101"] = pump(mass(st["S11"][0]), 1550, 400)          # SCl2 to the vaporiser
    duty["P201"] = pump(mass(st["S22"][0]), 1600, 300)          # crude to T301
    duty["P301"] = pump(mass(st["S32"][0]), 1650, 300) + pump((REFLUX + 1) * mass(prod), 1640, 300)
    duty["P401"] = pump(5000.0, 1100, 300)                      # scrubber circulation 5 m3/h

    # report
    tot_in = mass(st["S1"][0]) + mass(st["S2"][0]) + mass(st["S3"][0])
    tot_out = mass(st["S31"][0]) + mass(st["S25"][0])
    print(f"iterations {r['it']}, product {mass(prod):.3f} kg/h")
    print(f"process loop: in {tot_in:.3f} kg/h, out (product + purge) {tot_out:.3f} kg/h")
    for k, (s, T, ph) in st.items():
        m = mass(s)
        comp = ", ".join(f"{c} {n * MW[c] / m:.5f}" for c, n in s.items() if n > 0)
        print(f"{k:5s} {T:7.2f} K {ph:3s} {m:11.3f} kg/h {tot(s):9.4f} kmol/h  w: {comp}")
    for k, q in duty.items():
        print(f"duty {k:10s} {q:10.2f} kW")
    print("scrubber reactions (kmol/h):", {k: round(v, 6) for k, v in reac.items()})
    print("y_O2 recycle gas:", round(r["gas_mix"]["O2"] / tot(r["gas_mix"]), 4),
          "recycle gas kg/h", round(mass(r["new_rec"]), 1))
    print("R201 inlet: SO2/stoich", round(r["feed_r201"]["SO2"] / r["so2_stoich"], 3),
          "Cl2/stoich", round(r["feed_r201"]["CL2"] / r["cl2_stoich"], 3))
    print("T301 sulfur kg/h", round(s_b * MW["S"], 2), "= wt% of SOCl2 in crude",
          round(100 * s_b * MW["S"] / (r["crude"]["SOCL2"] * MW["SOCL2"]), 2))
    return st, duty, r


if __name__ == "__main__":
    st, duty, r = main()
    if "--yaml" in sys.argv:
        # the streams: section of process/flowsheet.yaml, to be pasted by hand (build/ only)
        path = sys.argv[sys.argv.index("--yaml") + 1]
        st["S26"] = (st["S24"][0], T_SEP, "g")
        BAL = "scripts/balance.py"
        META = [  # id, title, from, to, template, pressure kPa(a), pressure/temperature source, flow source
            ("S1", "Molten sulfur feed", "SULFUR.out", "X102.in", "sulfur", 400, "battery limit (D-003)", "sulfur demand of R101 and T301 (D-004, D-008)"),
            ("S1A", "Sulfur to the S2Cl2 reactor", "X102.r101", "R101.s", "sulfur", 400, "D-003", "D-004"),
            ("S1B", "Sulfur dosed to the purification", "X102.t301", "M301.s", "sulfur", 400, "D-003", "1.10 x the SCl2 converted in T301 (D-008)"),
            ("S2", "Chlorine feed (chlor-alkali-1)", "CL2.out", "X101.in", "chlorine", 400, "chlor-alkali-1 chlorine product (D-003)", "R101 + R102 + reactor make-up (D-004, D-005)"),
            ("S2A", "Chlorine to the S2Cl2 reactor", "X101.r101", "R101.cl2", "chlorine", 400, "D-003", "stoichiometric for the sulfur (D-004)"),
            ("S2B", "Chlorine to the SCl2 chlorinator", "X101.r102", "R102.cl2", "chlorine", 400, "D-003", "stoichiometric for 90 % of the S2Cl2 (D-004)"),
            ("S2C", "Chlorine make-up to the reactor feed", "X101.m201", "M201.cl2", "chlorine", 400, "D-003", "reactor inlet Cl2 5 % over stoichiometric less the recycled Cl2 (D-005)"),
            ("S3", "Liquid sulfur dioxide feed", "SO2.out", "E202.in", "so2", 500, "battery limit, liquid SO2 (D-003)", "reactor inlet SO2 100 % over stoichiometric less the recycled SO2 (D-005)"),
            ("S10", "Disulfur dichloride liquor", "R101.out", "R102.in", "schl", 200, "D-004", "D-004"),
            ("S11", "Sulfur dichloride liquor", "R102.out", "E201.in", "schl", 300, "D-004", "D-004"),
            ("S12", "Sulfur chloride vapour", "E201.out", "M201.schl", "process", 190, "D-005", "D-005"),
            ("S13", "Sulfur dioxide vapour", "E202.out", "M201.so2", "so2", 180, "D-005", "D-005"),
            ("S24", "Recycle gas (compressed)", "K201.out", "M201.rec", "process", 180, "isentropic efficiency 0.70 (D-007)", "D-007"),
            ("S14", "Mixed reactor feed", "M201.out", "E203.in", "process", 175, "adiabatic mixing (D-006)", "D-005"),
            ("S15", "Preheated reactor feed", "E203.out", "R201.in", "process", 170, "preheat to 398 K as US2431823 (D-005)", "D-005"),
            ("S16", "Reactor outlet (crude thionyl chloride gas)", "R201.out", "E204.in", "process", 140, "outlet 473 K: at or below 200 C (US2431823, D-005)", "conversion model (D-005)"),
            ("S17", "Partly condensed reactor gas", "E204.out", "E205.in", "process", 135, "cooling-water condenser (D-007)", "D-005"),
            ("S18", "Condensed crude with non-condensed gas", "E205.out", "V201.in", "process", 130, "brine condenser (D-007)", "D-005"),
            ("S19", "Separator gas", "V201.gas", "M202.sep", "process", 130, "D-007", "Raoult flash at 263.15 K, 130 kPa(a), O2 insoluble (D-006)"),
            ("S20", "Raw crude liquid", "V201.liquid", "T201.in", "process", 130, "D-007", "Raoult flash (D-006)"),
            ("S21", "Degasser overhead gas", "T201.gas", "M202.deg", "process", 125, "overhead condenser 263 K (D-007)", "SO2, Cl2 stripped completely, heavies at Raoult over the crude (D-007)"),
            ("S22", "Degassed crude thionyl chloride", "T201.liquid", "M301.crude", "crude", 200, "bubble point of the crude, pumped (D-007)", "D-007"),
            ("S23", "Combined off-gas", "M202.out", "X201.in", "process", 125, "D-007", "D-007"),
            ("S25", "Purge gas to the scrubber", "X201.purge", "T401.gas_in", "process", 125, "D-007", "1 % of the off-gas purged for the O2 of the chlorine (D-007)"),
            ("S26", "Recycle gas to the compressor", "X201.recycle", "K201.in", "process", 125, "D-007", "D-007"),
            ("S30", "Crude with sulfur to the purification column", "M301.out", "T301.in", "crude", 200, "D-008", "D-008"),
            ("S31", "Thionyl chloride product", "T301.distillate", "SOCL2.in", "product", 300, "distillate subcooled to 308 K, to storage (D-008)", "design capacity and specification (D-002)"),
            ("S32", "Still bottoms (S2Cl2, sulfur, SOCl2) to R101", "T301.bottoms", "R101.rec", "schl", 300, "bubble point of the bottoms at 101 kPa about 386 K (D-008)", "20 wt% SOCl2 left in the bottoms (D-008)"),
            ("S40", "Caustic soda 50 wt%", "NAOH.out", "M401.naoh", "caustic", 400, "site caustic header (D-009)", "1.2 x the NaOH the purge consumes (D-009)"),
            ("S41", "Dilution water", "PW.out", "M401.water", "water", 400, "site water header", "dilution to 10 wt% NaOH (D-009)"),
            ("S42", "Scrubbing liquor 10 wt% NaOH", "M401.out", "T401.liq_in", "caustic", 400, "D-009", "D-009"),
            ("S43", "Scrubbed vent to atmosphere", "T401.gas_out", "STACK.in", "vent", 101.325, "D-009", "99.9 % of SO2, Cl2 and sulfur chlorides absorbed, water-saturated at 303 K (D-009)"),
            ("S44", "Spent scrubber liquor", "T401.liq_out", "EFF.in", "liquor", 200, "D-009", "D-009"),
        ]
        PH = {"l": "liquid", "g": "vapor", "2": "two-phase", "aq": "liquid"}
        with open(path, "w") as f:
            for sid, title, fr, to, tpl, p, psrc, fsrc in META:
                s, T, ph = st[sid]
                m, n = mass(s), tot(s)
                comp = ", ".join(f"{c}: {v / n:.8g}" for c, v in s.items() if v / n > 1e-12)
                f.write(f"  - id: {sid}\n    title: {title}\n    from: {fr}\n    to: {to}\n"
                        f"    template: {tpl}\n    state:\n      design:\n"
                        f"        pressure: {{value: {p}, provenance: assumed, source: \"{psrc}\"}}\n"
                        f"        temperature: {{value: {T:.2f}, provenance: assumed, source: \"{BAL} ({psrc})\"}}\n"
                        f"        phase: {{value: {PH[ph]}, provenance: assumed, source: \"{BAL}\"}}\n"
                        f"        flow: {{value: {m:.3f}, basis: mass, provenance: assumed, source: \"{BAL}: {fsrc}\"}}\n"
                        f"        composition: {{basis: mole_fraction, values: {{{comp}}}, provenance: assumed, source: \"{BAL}\"}}\n")
            for k, q in duty.items():
                f.write(f"Q_{k}: {abs(q):.2f}\n")
