"""Independent concept balance of isobutene by MTBE cracking (DESIGN.md D-006).

Run: cheme run scripts/ib_balance.py  (needs thermo/chemicals from cheme's interpreter).
Prints the separator and column outlets, the feed flows and the duties that
process/flowsheet.yaml carries as ASSUMED values with this script as the source. Mixers,
splitters, pass-through steps and the reactor are recalculated by `cheme process propagate`.

Method (concept shortcut, not a rigorous simulation; core #315 has no qualified polar /
activity-coefficient package for MTBE / methanol / water / C4):
- separators: component split specifications (D-007), linear in the fresh feed, so the
  balance is solved for 1 kmol/h fresh MTBE and scaled to the product rate;
- reactor: conversion and selectivity per kmol MTBE converted (D-005), as cheme evaluates it;
- duties: ideal-gas enthalpies from the cp_R polynomials of process/materials.yaml; latent
  heats, liquid heat capacities and vapour pressures from thermo 0.6 / chemicals 1.5 (pure
  components, mole-fraction mixing, ideal Raoult bubble points); column condenser
  (R+1)*D*lambda_top and reboiler from the column energy balance on saturated liquids.
"""
from thermo import Chemical

C = ["MTBE", "IB", "MEOH", "DME", "H2O", "DIB"]
CAS = {"MTBE": "1634-04-4", "IB": "115-11-7", "MEOH": "67-56-1", "DME": "115-10-6",
       "H2O": "7732-18-5", "DIB": "107-39-1"}
MW = {"MTBE": 88.148, "IB": 56.106, "MEOH": 32.042, "DME": 46.068, "H2O": 18.015, "DIB": 112.21}
CP = {  # cp/R polynomials of process/materials.yaml (chemicals fit 298.15-700 K)
    "MTBE": [9.18733, -0.00698804, 0.000157748, -2.15719e-07, 9.34807e-11],
    "IB": [3.38712, 0.0179196, 3.76558e-05, -6.48818e-08, 3.03488e-11],
    "MEOH": [5.50344, -0.0151027, 7.0746e-05, -8.59838e-08, 3.65802e-11],
    "DME": [4.95853, 0.000138109, 4.94792e-05, -6.52517e-08, 2.78177e-11],
    "H2O": [4.38266, -0.00362257, 1.14244e-05, -1.19492e-08, 4.84609e-12],
    "DIB": [-3.79327, 0.104586, -7.31737e-05, 2.10597e-08],
}
HF = {"MTBE": -283700.0, "IB": -17600.0, "MEOH": -200700.0, "DME": -184020.0,
      "H2O": -241822.0, "DIB": -110500.0}  # kJ/kmol, ideal gas 298.15 K
R = 8.314462618  # kJ/(kmol K)
CH = {c: Chemical(CAS[c]) for c in C}

# ---- design specifications (DESIGN.md) -------------------------------------------------
PRODUCT_KG_H = 6250.0          # D-002: 50 kt/a at 8000 h
X_MTBE = 0.90                  # D-005: per-pass MTBE conversion
SEL = {"IB": 0.998, "DME": 0.010, "DIB": 0.001}  # D-005: kmol per kmol MTBE converted
T_RX = 553.15                  # D-004: reactor outlet (heated tubular reactor)
P = {"C101": 1000.0, "C201": 650.0, "C301": 100.0, "C402": 150.0, "C403": 900.0}  # kPa(a)
REFLUX = {"C101": 0.5, "C201": 0.7, "C301": 1.9, "C402": 1.5, "C403": 30.0}
WASH_RATIO = 0.15              # D-007: wash water / C-201 distillate, mass
PURGE = 0.05                   # D-007: wash-water loop blowdown fraction of C-402 bottoms


def mass(s):
    return sum(s[c] * MW[c] for c in C)


def zero():
    return {c: 0.0 for c in C}


def add(*ss):
    return {c: sum(s[c] for s in ss) for c in C}


def h_ig(c, T):  # kJ/kmol relative to 298.15 K ideal gas, without formation
    a = CP[c]
    f = lambda t: sum(a[k] * t ** (k + 1) / (k + 1) for k in range(len(a)))
    return R * (f(T) - f(298.15))


def H_ig(s, T):  # with formation enthalpy, kW for kmol/h
    return sum(s[c] * (HF[c] + h_ig(c, T)) for c in C) / 3600.0


def hvap(c, T):  # kJ/kmol
    return CH[c].EnthalpyVaporization(T)


def cpl(c, T):  # kJ/(kmol K); DIB liquid cp from 1.25 x ideal-gas cp when thermo has none
    v = CH[c].HeatCapacityLiquid(T)
    return v if v else 1.25 * R * sum(CP[c][k] * T ** k for k in range(len(CP[c])))


def h_liq(s, T):  # liquid sensible enthalpy from 298.15 K, kW
    return sum(s[c] * cpl(c, 0.5 * (T + 298.15)) * (T - 298.15) for c in C) / 3600.0


def bubble(s, Pk):  # ideal Raoult bubble point, K
    n = sum(s.values())
    x = {c: s[c] / n for c in C if s[c] > 0}
    lo, hi = 150.0, 650.0
    for _ in range(80):
        T = 0.5 * (lo + hi)
        ps = sum(x[c] * (CH[c].VaporPressure(min(T, CH[c].Tc - 0.5)) or 0) for c in x) / 1000
        lo, hi = (T, hi) if ps < Pk else (lo, T)
    return T


def lam(s, T):  # mole-weighted latent heat, kJ/kmol
    n = sum(s.values())
    return sum(s[c] / n * hvap(c, min(T, CH[c].Tc - 1)) for c in C if s[c] > 0)


def column(name, F, D, B, TF, extra_out=()):
    """Condenser and reboiler duties (kW) of a column with liquid outlets."""
    Ttop, Tbot = bubble(D, P[name]), bubble(B, P[name])
    Qc = (REFLUX[name] + 1) * sum(D.values()) * lam(D, Ttop) / 3600
    Hout = h_liq(D, Ttop) + h_liq(B, Tbot) + sum(h_liq(s, T) for s, T in extra_out)
    Qr = Qc + Hout - h_liq(F, TF)
    return Ttop, Tbot, Qc, Qr


def solve(fresh_kmol):
    fresh = zero(); fresh["MTBE"] = fresh_kmol
    rec = zero()
    recw, w403 = zero(), zero()
    makeup = 0.0
    for _ in range(400):
        f101 = add(fresh, rec)
        # C-101 heavies column: all DIB to the bottoms with MTBE at 60 wt% (D-007)
        b101 = zero(); b101["DIB"] = f101["DIB"]
        b101["MTBE"] = min(f101["MTBE"], 1.5 * f101["DIB"] * MW["DIB"] / MW["MTBE"])
        d101 = {c: f101[c] - b101[c] for c in C}
        # R-101: conversion with selectivities (as cheme: extents from the key and products)
        conv = X_MTBE * d101["MTBE"]
        e2, e3 = SEL["DME"] * conv, SEL["DIB"] * conv
        r = dict(d101)
        r["MTBE"] -= conv; r["IB"] += conv - 2 * e3; r["MEOH"] += conv - 2 * e2
        r["DME"] += e2; r["H2O"] += e2; r["DIB"] += e3
        # C-201 product column: isobutene overhead (D-007)
        d201 = zero()
        frac = {"IB": 0.998, "DME": 1.0, "H2O": 0.30, "MTBE": 0.001, "DIB": 0.0}
        for c, f in frac.items():
            d201[c] = f * r[c]
        mrest = mass(d201)
        d201["MEOH"] = min(r["MEOH"], 0.025 / 0.975 * mrest / MW["MEOH"])
        b201 = {c: r[c] - d201[c] for c in C}
        # C-301 methanol column: MTBE / methanol azeotrope (14 wt% methanol) overhead
        d301 = zero()
        for c in ("MTBE", "DIB", "IB", "DME"):
            d301[c] = b201[c]
        d301["MEOH"] = 0.14 / 0.86 * mass(d301) / MW["MEOH"]
        b301 = {c: b201[c] - d301[c] for c in C}
        rec_new = d301
        # C-401 water wash
        # wash water W: recycled loop water + decanted water + demineralised make-up
        W = WASH_RATIO * mass(d201)  # kg/h water
        makeup = W / MW["H2O"] - recw["H2O"] - w403["H2O"]
        mu = zero(); mu["H2O"] = makeup
        wash = add(recw, w403, mu)
        recw_old = recw
        raf = zero()
        raf["MEOH"] = 0.001 * d201["MEOH"]; raf["DME"] = 0.70 * d201["DME"]
        raf["MTBE"] = d201["MTBE"]; raf["DIB"] = d201["DIB"]
        ib_ext = 0.002 * W / MW["IB"]
        raf["IB"] = d201["IB"] - ib_ext
        raf["H2O"] = 0.0008 * mass(raf) / MW["H2O"]
        ext = {c: d201[c] + wash[c] - raf[c] for c in C}
        # C-402 methanol / water column: water bottoms (100 ppm methanol), vent of C4 and DME
        b402 = zero(); b402["H2O"] = ext["H2O"] - 0.0101 * ext["MEOH"] * MW["MEOH"] / MW["H2O"]
        b402["MEOH"] = 1e-4 * b402["H2O"] * MW["H2O"] / MW["MEOH"]
        v402 = zero(); v402["IB"] = ext["IB"]; v402["DME"] = ext["DME"]
        d402 = {c: ext[c] - b402[c] - v402[c] for c in C}
        # C-403 DME / water column: DME vapour distillate with equal mass of isobutene,
        # 99 % of the water decanted, isobutene product bottoms
        v403 = zero(); v403["DME"] = 0.99 * raf["DME"]
        v403["IB"] = v403["DME"] * MW["DME"] / MW["IB"]
        w403 = zero(); w403["H2O"] = 0.99 * raf["H2O"]
        b403 = {c: raf[c] - v403[c] - w403[c] for c in C}
        # wash-water loop
        recw = {c: (1 - PURGE) * b402[c] for c in C}
        if max(abs(rec_new[c] - rec[c]) + abs(recw[c] - recw_old[c]) for c in C) < 1e-14:
            break
        rec = rec_new
    return locals()


def main():
    s1 = solve(1.0)
    k = PRODUCT_KG_H / mass(s1["b403"])
    s = solve(k)
    out = {n: s[n] for n in ("fresh", "rec", "f101", "d101", "b101", "r", "d201", "b201",
                             "d301", "b301", "wash", "raf", "ext", "b402", "v402", "d402",
                             "v403", "w403", "b403", "recw")}
    print(f"scale: fresh MTBE {k:.6f} kmol/h = {k * MW['MTBE']:.3f} kg/h; make-up water "
          f"{s['makeup'] * MW['H2O']:.4f} kg/h (MeOH-free; loop water ASSUMED pure)")
    for n, st in out.items():
        m = mass(st); nt = sum(st.values())
        y = {c: round(st[c] / nt, 9) for c in C if st[c] > 0} if nt else {}
        print(f"{n:6s} {m:12.4f} kg/h  mol: {y}")
    # ---- energy -------------------------------------------------------------------------
    print("\nduties (kW):")
    TF101 = 303.15
    d101, b101, f101, r = s["d101"], s["b101"], s["f101"], s["r"]
    Ttop = bubble(d101, P["C101"]); Tbot = bubble(b101, P["C101"])
    # C-101: vapour distillate (partial condenser condenses the reflux only)
    Qc101 = REFLUX["C101"] * sum(d101.values()) * lam(d101, Ttop) / 3600
    Hd_vap = h_liq(d101, Ttop) + sum(d101.values()) * lam(d101, Ttop) / 3600
    Qr101 = Qc101 + Hd_vap + h_liq(b101, Tbot) - h_liq(f101, TF101)
    print(f"C-101 Ttop {Ttop:.1f} Tbot {Tbot:.1f} cond {Qc101:.1f} reb {Qr101:.1f}")
    T_e101 = 523.15
    Qe101 = H_ig(d101, T_e101) - H_ig(d101, Ttop)
    Qh101 = H_ig(d101, T_RX) - H_ig(d101, T_e101)
    Qrx = H_ig(r, T_RX) - H_ig(d101, T_RX)
    # effluent outlet of E-101
    lo, hi = 300.0, T_RX
    for _ in range(80):
        T = 0.5 * (lo + hi)
        q = H_ig(r, T_RX) - H_ig(r, T)
        lo, hi = (T, hi) if q > Qe101 else (lo, T)
    T_eff = T
    print(f"E-101 feed/effluent {Qe101:.1f} (feed {Ttop:.1f}->{T_e101}, effluent {T_RX}->{T_eff:.1f})")
    print(f"H-101 superheat {Qh101:.1f}; R-101 reaction duty at {T_RX} K {Qrx:.1f}; "
          f"fired absorbed {Qh101 + Qrx:.1f}")
    TF201 = 313.15
    Qe102 = H_ig(r, T_eff) - H_ig(r, TF201) + sum(r.values()) * lam(r, TF201) / 3600 \
        + h_liq(r, TF201) - 0.0
    print(f"E-102 effluent condenser {Qe102:.1f} ({T_eff:.1f} -> {TF201} K liquid)")
    for name, F, D, B, TF in (("C201", r, s["d201"], s["b201"], TF201),
                              ("C301", s["b201"], s["d301"], s["b301"], None),
                              ("C402", s["ext"], s["d402"], s["b402"], 313.15)):
        if TF is None:
            TF = bubble(F, P["C201"])
        Tt, Tb, Qc, Qr = column(name, F, D, B, TF)
        print(f"{name} Ttop {Tt:.1f} Tbot {Tb:.1f} feed {TF:.1f} cond {Qc:.1f} reb {Qr:.1f}")
    # C-403: partial condenser, vapour distillate small, reflux on (vapour + water) distillate
    raf, v403, w403, b403 = s["raf"], s["v403"], s["w403"], s["b403"]
    Dt = add(v403, w403)
    Tt = bubble(v403, P["C403"]); Tb = bubble(b403, P["C403"])
    lam_ib = hvap("IB", Tt)
    Qc = REFLUX["C403"] * sum(Dt.values()) * lam_ib / 3600
    Qr = Qc + h_liq(b403, Tb) + h_liq(w403, Tt) + h_liq(v403, Tt) + \
        sum(v403.values()) * lam(v403, Tt) / 3600 - h_liq(raf, 313.15)
    print(f"C403 Ttop {Tt:.1f} Tbot {Tb:.1f} cond {Qc:.1f} reb {Qr:.1f}")
    print(f"E-403 product cooler {h_liq(b403, Tb) - h_liq(b403, 313.15):.1f} ({Tb:.1f}->313.15)")
    b301 = s["b301"]; Tb301 = bubble(b301, P["C301"])
    print(f"E-301 methanol cooler {h_liq(b301, Tb301) - h_liq(b301, 313.15):.1f}")
    recw = s["recw"]; Tb402 = bubble(s["b402"], P["C402"])
    print(f"E-401 wash-water cooler {h_liq(recw, Tb402) - h_liq(recw, 313.15):.1f} "
          f"({Tb402:.1f}->313.15)")
    # pumps: V * dP / eta, eta 0.6 (ASSUMED)
    def vm(c, T):  # m3/kmol; 700 kg/m3 when thermo has no liquid volume (ASSUMED)
        v = CH[c].VolumeLiquid(min(T, CH[c].Tc - 5), 2e6)
        return v * 1000 if v else MW[c] / 700.0

    def vol(st, T=303.15):  # m3/s
        return sum(st[c] * vm(c, T) for c in C) / 3600
    pumps = {
        "P-101 MTBE feed 150->1100 kPa": vol(s["f101"]) * 950,
        "P-201 C-201 reflux + distillate 650->900": vol(s["d201"]) * (1 + REFLUX["C201"]) * 250,
        "P-202 C-201 bottoms to C-301": vol(s["b201"]) * 100,
        "P-301 C-301 reflux + recycle 100->1100": vol(s["d301"]) * (REFLUX["C301"] + 1) * 1000,
        "P-302 methanol product 100->500": vol(b301) * 400,
        "P-401 wash water 150->900": vol(s["wash"]) * 750,
        "P-402 C-402 reflux 150->350": vol(s["d402"]) * (REFLUX["C402"] + 1) * 200,
        "P-403 C-403 reflux 900->1100": vol(Dt) * REFLUX["C403"] * 200 / 3,
        "P-404 isobutene product 900->1500": vol(b403) * 600,
    }
    tot = 0.0
    for n, kw in pumps.items():
        print(f"  {n}: {kw / 0.6:.2f} kW")
        tot += kw / 0.6
    print(f"pumps total {tot:.1f} kW")
    # ---- first-pass line sizes (D-010): vapour 20 m/s, liquid 1.5 m/s, inside diameter = DN
    DN = [25, 32, 40, 50, 65, 80, 100, 125, 150, 200, 250, 300, 350, 400, 450, 500, 600]
    mw = lambda st: mass(st) / sum(st.values())
    lines = {  # stream: (state, T K, P kPa(a), phase)
        "S1": (s["fresh"], 303.15, 300, "L"), "S2": (s["f101"], 308.15, 300, "L"),
        "S4": (d101, 420.2, 1000, "V"), "S5": (b101, 435.9, 1010, "L"),
        "S6": (d101, 523.15, 950, "V"), "S7": (d101, 553.15, 900, "V"),
        "S8": (r, 553.15, 750, "V"), "S9": (r, 450.0, 720, "V"), "S10": (r, 313.15, 700, "L"),
        "S11": (s["d201"], 313.15, 900, "L"), "S12": (s["b201"], 394.0, 660, "L"),
        "S13": (s["d301"], 328.8, 300, "L"), "S14": (b301, 337.4, 500, "L"),
        "S15": (raf, 313.15, 880, "L"), "S16": (s["ext"], 313.15, 880, "L"),
        "S17": (s["d402"], 348.3, 500, "L"), "S18": (s["v402"], 313.15, 150, "V"),
        "S19": (s["b402"], 384.5, 300, "L"), "S23": (s["wash"], 313.15, 900, "L"),
        "S26": (v403, 323.0, 900, "V"), "S27": (b403, 339.2, 920, "L"),
        "S30": (add(b301, s["d402"]), 313.15, 480, "L"),
    }
    print("\nline sizes:")
    for sid, (st, T, Pk, ph) in lines.items():
        if ph == "V":
            q = sum(st.values()) / 3600 * R * T / Pk  # m3/s, ideal gas
            u = 20.0
        else:
            q = vol(st, T)
            u = 1.5
        d = (4 * q / (3.14159265 * u)) ** 0.5 * 1000
        dn = next(x for x in DN if x >= d)
        print(f"  {sid}: {q * 3600:.1f} m3/h, d {d:.0f} mm -> DN{dn}")


if __name__ == "__main__":
    main()
