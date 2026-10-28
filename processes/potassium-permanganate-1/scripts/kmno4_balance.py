"""Independent sequential mass and energy balance of potassium-permanganate-1 (DESIGN.md D-006).

Route (D-001): MnO2 ore + KOH roasted with air to K2MnO4 (R-201), leaching with recycled mother
liquor and silicate removal with lime (M-301), residue filtration with condensate wash (F-301),
electrolytic oxidation K2MnO4 -> KMnO4 in divided cells (EL-401), cooling crystallisation
(X-501), centrifuge (C-501), steam dryer (DR-501), mother-liquor split (S-601) to the leach, to
the KOH evaporator (E-601, concentrate back to the roaster) and to the purge.

Every design parameter below is ASSUMED unless its comment names a source; the numbers are
copied into process/flowsheet.yaml as `assumed` with this script as their source. Liquors are
carried as neutral molecules (no speciation, core #364). Run: python3 -I scripts/kmno4_balance.py
(standard library only); it writes build/kmno4_balance.json and build/streams.yaml.
"""

from __future__ import annotations

import json
import math
from pathlib import Path

# ---- molar masses, kg/kmol (IUPAC 2021 standard atomic weights)
M = {
    "H2O": 18.015, "KOH": 56.105, "MnO2": 86.936, "K2MnO4": 197.130, "KMnO4": 158.032,
    "O2": 31.998, "N2": 28.014, "H2": 2.016, "Fe2O3": 159.687, "SiO2": 60.084,
    "K2SiO3": 154.278, "CaOH2": 74.092, "CaSiO3": 116.160,
}
F = 96485.33  # C/mol

# ---- design parameters
P_TARGET = 1250.0          # kg/h dried product, 10 kt/a at 8000 h (ASSUMED, D-002)
ORE = {"MnO2": 0.78, "Fe2O3": 0.08, "SiO2": 0.12, "H2O": 0.02}  # ASSUMED (D-003); US5011672: 70-80 % MnO2 ore usable
X_OX = 0.90                # MnO2 -> K2MnO4 in the roaster (ASSUMED, D-004); US5011672 claims > 95 % for its atomiser
X_SI = 0.25                # SiO2 attacked by KOH to K2SiO3 (ASSUMED, D-004)
KOH_MNO2 = 2.5             # mol KOH per mol MnO2 fed to the roaster (US5011672: 2-3, optimum ~2.5)
AIR_O2_EXCESS = 2.0        # O2 fed / O2 for OX (ASSUMED, D-004)
AIR_O2_W = 0.232           # O2 mass fraction of dry air (N2 counted with Ar)
CAKE_H2O = 0.03            # water mass fraction of the oxidised cake (ASSUMED)
LIME_EXCESS = 1.10         # Ca(OH)2 / K2SiO3 (ASSUMED, D-005)
RES_LIQ = 0.60             # kg liquid per kg dry residue solids (ASSUMED, D-005)
WASH_LOSS = 0.10           # solutes left in the washed cake liquid / filtrate mass fraction (ASSUMED, D-005)
X_EL = 0.90                # K2MnO4 -> KMnO4 per pass in the cells (ASSUMED, D-006)
CE = 0.85                  # current efficiency (ASSUMED, D-006); the rest evolves O2
V_CELL = 2.5               # V per cell (ASSUMED in the 2.0-3.5 V of US5660712, D-006)
ML_KMNO4 = 0.015           # KMnO4 mass fraction of the mother liquor at 303 K (US5660712: 15-20 g/l likely)
ML_KOH = 0.13              # KOH mass fraction of the mother liquor (US5660712: 125-175 g/l likely)
CAKE_LIQ = 0.06            # liquid mass fraction of the centrifuge cake (ASSUMED, D-007)
PROD_H2O = 0.002           # moisture of the dried product (ASSUMED, D-007)
PURGE = 0.03               # fraction of the mother liquor purged (ASSUMED, D-008)
CF_K2MNO4 = 0.06           # K2MnO4 mass fraction of the cell feed (ASSUMED, D-006)
CONC_KOH = 0.50            # KOH mass fraction of the evaporator concentrate (ASSUMED, D-008)


def add(*streams):
    out: dict[str, float] = {}
    for s in streams:
        for k, v in s.items():
            out[k] = out.get(k, 0.0) + v
    return out


def scale(s, f):
    return {k: v * f for k, v in s.items()}


def tot(s):
    return sum(s.values())


def frac(s):
    t = tot(s)
    return {k: v / t for k, v in s.items() if v > 1e-9}


def kmol(s, c):
    return s.get(c, 0.0) / M[c]


SOLIDS_RES = ("MnO2", "Fe2O3", "SiO2", "CaSiO3", "CaOH2")


def solve(ore_flow, pw, mu, f_ev, ml):
    """One steady state for given ore, process water, KOH make-up (kg/h KOH) and fraction of
    the mother liquor to the evaporator; the mother liquor is the tear stream, solved by
    successive substitution (the purge anchors the inventory)."""
    ore = scale(ORE, ore_flow)
    for _ in range(20000):
        ml = {c: max(v, 0.0) for c, v in ml.items()}
        f_le = 1.0 - PURGE - f_ev
        ml_ev, ml_le, purge = scale(ml, f_ev), scale(ml, f_le), scale(ml, PURGE)
        # ---- E-601 evaporator: concentrate to CONC_KOH
        conc = dict(ml_ev)
        conc["H2O"] = 0.0
        conc["H2O"] = max(0.0, conc["KOH"] / CONC_KOH - tot(conc))
        evap = ml_ev["H2O"] - conc["H2O"]
        mu_s = {"KOH": mu * 1.0, "H2O": mu * 1.0}  # 50 wt% KOH make-up
        # ---- R-201 roaster
        feed = add(ore, conc, mu_s)
        r = dict(feed)
        # REDKM: 4 KMnO4 + 4 KOH -> 4 K2MnO4 + O2 + 2 H2O (complete)
        e_red = kmol(r, "KMnO4") / 4
        # OX: 2 MnO2 + 4 KOH + O2 -> 2 K2MnO4 + 2 H2O
        koh_free = kmol(r, "KOH") - 4 * e_red
        e_ox = min(X_OX * kmol(r, "MnO2") / 2, 0.8 * koh_free / 4)  # cap only while iterating
        # SIL: SiO2 + 2 KOH -> K2SiO3 + H2O
        e_si = min(X_SI * kmol(r, "SiO2"), 0.5 * (koh_free - 4 * e_ox) / 2)
        o2_air = AIR_O2_EXCESS * e_ox * M["O2"]
        air = {"O2": o2_air, "N2": o2_air * (1 - AIR_O2_W) / AIR_O2_W}
        r = add(r, air)
        for c, nu in {"KMnO4": -4, "KOH": -4, "K2MnO4": 4, "O2": 1, "H2O": 2}.items():
            r[c] = r.get(c, 0) + nu * e_red * M[c]
        for c, nu in {"MnO2": -2, "KOH": -4, "O2": -1, "K2MnO4": 2, "H2O": 2}.items():
            r[c] = r.get(c, 0) + nu * e_ox * M[c]
        for c, nu in {"SiO2": -1, "KOH": -2, "K2SiO3": 1, "H2O": 1}.items():
            r[c] = r.get(c, 0) + nu * e_si * M[c]
        cake = {c: v for c, v in r.items() if c not in ("O2", "N2", "H2O")}
        cake["H2O"] = CAKE_H2O / (1 - CAKE_H2O) * tot(cake)
        offgas = {"O2": r["O2"], "N2": r["N2"], "H2O": r["H2O"] - cake["H2O"]}
        # ---- M-301 leach and lime: K2SiO3 + Ca(OH)2 -> CaSiO3 + 2 KOH
        lime = {"CaOH2": LIME_EXCESS * (kmol(cake, "K2SiO3") + kmol(ml_le, "K2SiO3")) * M["CaOH2"]}
        water = {"H2O": pw}
        sl = add(cake, ml_le, lime, water)
        e_lime = kmol(sl, "K2SiO3")
        for c, nu in {"K2SiO3": -1, "CaOH2": -1, "CaSiO3": 1, "KOH": 2}.items():
            sl[c] = sl.get(c, 0) + nu * e_lime * M[c]
        # ---- F-301 residue filter, washed with the evaporator condensate
        solids = {c: sl.get(c, 0) for c in SOLIDS_RES}
        liq = {c: v for c, v in sl.items() if c not in SOLIDS_RES}
        wash = {"H2O": evap}
        lc = RES_LIQ * tot(solids)
        lf = frac(liq)
        cake_liq = {c: WASH_LOSS * w * lc for c, w in lf.items() if c != "H2O"}
        cake_liq["H2O"] = lc - tot(cake_liq)
        residue = add(solids, cake_liq)
        cellfeed = add(liq, wash, scale(cake_liq, -1))
        # ---- EL-401 cells: 2 K2MnO4 + 2 H2O -> 2 KMnO4 + 2 KOH + H2 (n = 2)
        e_el = X_EL * kmol(cellfeed, "K2MnO4") / 2
        i_main = 2 * e_el * 1000 * F / 3600  # A
        i_tot = i_main / CE
        e_ws = (i_tot - i_main) * 3600 / (4 * F) / 1000  # 2 H2O -> 2 H2 + O2, n = 4
        cl = dict(cellfeed)
        for c, nu in {"K2MnO4": -2, "H2O": -2, "KMnO4": 2, "KOH": 2}.items():
            cl[c] = cl.get(c, 0) + nu * e_el * M[c]
        cl["H2O"] -= 2 * e_ws * M["H2O"]
        h2 = {"H2": (e_el + 2 * e_ws) * M["H2"]}
        o2 = {"O2": e_ws * M["O2"]}
        # ---- X-501 crystalliser (pass-through), C-501 centrifuge
        T = tot(cl)
        cryst = (cl["KMnO4"] - ML_KMNO4 * T) / (1 - ML_KMNO4)
        liquor = dict(cl)
        liquor["KMnO4"] -= cryst
        cl_liq = (CAKE_LIQ / (1 - CAKE_LIQ)) * cryst
        lq = frac(liquor)
        cake_c = {c: w * cl_liq for c, w in lq.items()}
        wet = add(cake_c, {"KMnO4": cryst})
        ml_new = add(liquor, scale(cake_c, -1))
        # ---- DR-501 dryer
        dry = {c: v for c, v in wet.items() if c != "H2O"}
        dry["H2O"] = PROD_H2O / (1 - PROD_H2O) * tot(dry)
        vap = {"H2O": wet["H2O"] - dry["H2O"]}
        # ---- K make-up: K lost with product, residue and purge (kmol K)
        def k_of(s):
            return kmol(s, "KOH") + 2 * kmol(s, "K2MnO4") + kmol(s, "KMnO4") + 2 * kmol(s, "K2SiO3")
        k_out = k_of(dry) + k_of(residue) + k_of(purge)
        k_in = mu / M["KOH"]
        err = sum(abs(ml_new.get(c, 0) - ml.get(c, 0)) for c in set(ml) | set(ml_new))
        ml = ml_new
        if err < 1e-9:
            break
    S = dict(ore=ore, koh=mu_s, air=air, conc=conc, cake=cake, offgas=offgas, lime=lime,
             ml_le=ml_le, water=water, slurry=sl, wash=wash, residue=residue, cellfeed=cellfeed,
             cell=cl, h2=h2, o2=o2, wet=wet, ml=ml, prod=dry, vap=vap, ml_ev=ml_ev, purge=purge)
    X = dict(e_red=e_red, e_ox=e_ox, e_si=e_si, e_lime=e_lime, e_el=e_el, e_ws=e_ws, i_tot=i_tot,
             cryst=cryst, f_ev=f_ev, f_le=f_le, evap=evap, k_in=k_in, k_out=k_out)
    return S, X


def main():
    # Newton on log(ore, process water, make-up, evaporator fraction) for the four specs:
    # product flow, KOH in the mother liquor, K2MnO4 in the cell feed, KOH/MnO2 of the roaster.
    v = [math.log(x) for x in (1000.0, 1600.0, 600.0, 0.18)]
    ml = {"H2O": 30000.0, "KOH": 5000.0, "K2MnO4": 300.0, "KMnO4": 500.0}

    def resid(v, ml):
        S, X = solve(*[math.exp(x) for x in v], ml)
        ratio = (kmol(S["conc"], "KOH") + kmol(S["koh"], "KOH")) / kmol(S["ore"], "MnO2")
        r = [math.log(tot(S["prod"]) / P_TARGET),
             math.log(max(frac(S["ml"]).get("KOH", 1e-9), 1e-9) / ML_KOH),
             math.log(frac(S["cellfeed"])["K2MnO4"] / CF_K2MNO4),
             math.log(ratio / KOH_MNO2)]
        return r, S

    for it in range(50):
        r, S = resid(v, ml)
        ml = S["ml"]
        if max(abs(x) for x in r) < 1e-11:
            break
        J = []
        for j in range(4):
            vj = list(v)
            vj[j] += 1e-6
            rj, _ = resid(vj, ml)
            J.append([(rj[i] - r[i]) / 1e-6 for i in range(4)])
        A = [[J[j][i] for j in range(4)] + [-r[i]] for i in range(4)]  # A[i][j] = dr_i/dv_j
        for c in range(4):  # Gaussian elimination with partial pivoting
            piv = max(range(c, 4), key=lambda i: abs(A[i][c]))
            A[c], A[piv] = A[piv], A[c]
            for i in range(c + 1, 4):
                f = A[i][c] / A[c][c]
                A[i] = [a - f * b for a, b in zip(A[i], A[c])]
        dv = [0.0] * 4
        for i in reversed(range(4)):
            dv[i] = (A[i][4] - sum(A[i][j] * dv[j] for j in range(i + 1, 4))) / A[i][i]
        step = max(abs(x) for x in dv)
        v = [a + b * min(1.0, 0.3 / step) for a, b in zip(v, dv)]
    else:
        raise SystemExit(f"not converged: residuals {r}")
    print(f"converged after {it} Newton steps")
    ore_flow, pw, mu, f_ev = [math.exp(x) for x in v]
    S, X = solve(ore_flow, pw, mu, f_ev, ml)

    # ---- energy (lumped, D-009; ASSUMED heat capacities and latent heats)
    kw = 1 / 3600.0
    # R-201: evaporation + sensible heat to 523 K - reaction heat, 15 % losses
    w_evap = S["offgas"]["H2O"]
    q_evap = w_evap * (2257 + 4.18 * (373 - 298) + 2.0 * (523 - 373))
    q_sens = (tot(S["cake"]) * 1.0 * (523 - 330)  # feed at ~330 K mixed, salts cp ~1.0 kJ/kgK
              + (S["air"]["O2"] + S["air"]["N2"]) * 1.05 * (523 - 298))
    q_rx = X["e_ox"] * 112740 + X["e_red"] * 172200  # kJ/h released (formation enthalpies, D-009)
    q_r201 = (q_evap + q_sens - q_rx) / 0.85 * kw
    # M-301 leach cooling: melt 523 K, ML 303 K, wash/water 298 K -> 333 K; KOH(s) dissolution -57.6 kJ/mol
    q_leach = (tot(S["cake"]) * 1.0 * (523 - 333) - tot(S["ml_le"]) * 3.4 * (333 - 303)
               - (S["water"]["H2O"] + S["wash"]["H2O"]) * 4.18 * (333 - 298)
               + kmol(S["cake"], "KOH") * 57600) * kw
    # EL-401: P = I V ; Q = P - sum(extent dH)
    p_dc = X["i_tot"] * V_CELL / 1000  # kW (cells in series share the voltage sum; I x V per cell x n = total)
    q_cell = p_dc - (X["e_el"] * 334880 + X["e_ws"] * 571660) * kw
    p_ac = p_dc / 0.97
    q_rect = p_ac - p_dc
    # X-501: cooling 333 -> 303 K, cp 3.4, crystallisation heat 43.56 kJ/mol released
    q_x501 = (tot(S["cell"]) * 3.4 * (333 - 303) + X["cryst"] / M["KMnO4"] * 43560) * kw
    # E-601: double effect, 2400 kJ/kg vapour, economy 1.8; last-effect condenser = steam heat
    q_e601 = X["evap"] * 2400 / 1.8 * kw
    q_e601c = q_e601
    # DR-501: 2600 kJ/kg water removed, dryer thermal efficiency 0.65
    q_d501 = S["vap"]["H2O"] * 2600 / 0.65 * kw
    p_aux = 150 * P_TARGET / 1000  # 150 kWh/t product (ASSUMED)
    E = dict(q_r201=q_r201, q_leach=q_leach, p_dc=p_dc, p_ac=p_ac, q_rect=q_rect, q_cell=q_cell,
             q_x501=q_x501, q_e601=q_e601, q_e601c=q_e601c, q_d501=q_d501, p_aux=p_aux,
             current_kA=X["i_tot"] / 1000)

    out = {"streams": {k: {"flow": tot(v), "w": frac(v), "kg": v} for k, v in S.items()},
           "extents": X, "energy": E, "ore_flow": ore_flow, "pw": pw}
    Path("build").mkdir(exist_ok=True)
    Path("build/kmno4_balance.json").write_text(json.dumps(out, indent=1))
    for k, v in S.items():
        print(f"{k:9s} {tot(v):11.2f}  " + ", ".join(f"{c}: {w:.6f}" for c, w in frac(v).items()))
    print(json.dumps({k: round(v, 4) for k, v in X.items()}))
    print(json.dumps({k: round(v, 2) for k, v in E.items()}))
    # stream table for process/flowsheet.yaml: (id, key, title, from, to, P kPa(a), T K, note)
    table = [
        ("S1", "ore", "Manganese ore, dried and ground", "ORE.out", "R201.ore", 101.325, 298.15, "D-003"),
        ("S2", "koh", "KOH make-up (50 wt% solution)", "KOH.out", "R201.koh", 300, 298.15, "K balance closure: K leaving with product, residue and purge (D-008)"),
        ("S3", "air", "Roaster air", "AIR.out", "R201.air", 101.325, 298.15, "2.0 x the O2 of the oxidation (D-004)"),
        ("S4", "conc", "Concentrated KOH liquor to the roaster", "E601.conc", "R201.conc", 101.325, 413.15, "50 wt% KOH (D-008)"),
        ("S5", "cake", "Oxidised roaster cake (K2MnO4 melt)", "R201.cake", "M301.cake", 101.325, 523.15, "X(MnO2) 0.90, 3 wt% water (D-004)"),
        ("S6", "offgas", "Roaster off-gas to the scrubber stack", "R201.gas", "OFFGAS.in", 101.325, 523.15, "D-004"),
        ("S7", "lime", "Hydrated lime", "LIME.out", "M301.lime", 101.325, 298.15, "1.10 x K2SiO3 (D-005)"),
        ("S8", "ml_le", "Mother liquor to the leach", "S601.leach", "M301.ml", 300, 303.15, "D-008"),
        ("S9", "water", "Process water to the leach", "PW.out", "M301.water", 300, 298.15, "sets 6.0 wt% K2MnO4 in the cell feed (D-006)"),
        ("S10", "slurry", "Leach slurry", "M301.out", "F301.in", 300, 333.15, "D-005"),
        ("S11", "wash", "Evaporator condensate as residue wash", "E601.cond", "F301.wash", 300, 318.15, "D-005, D-008"),
        ("S12", "residue", "Washed leach residue to disposal", "F301.residue", "RESIDUE.in", 101.325, 333.15, "0.6 kg liquid/kg solids, 90 % solute recovery (D-005)"),
        ("S13", "cellfeed", "Clarified manganate liquor (cell feed)", "F301.filtrate", "EL401.feed", 300, 333.15, "D-006"),
        ("S14", "cell", "Cell liquor with KMnO4", "EL401.liquor", "X501.in", 200, 333.15, "X(K2MnO4) 0.90 per pass (D-006)"),
        ("S15", "h2", "Cathode hydrogen to vent", "EL401.h2", "H2V.in", 101.325, 333.15, "D-006, dry basis"),
        ("S16", "o2", "Anode oxygen to vent", "EL401.o2", "O2V.in", 101.325, 333.15, "D-006, dry basis"),
        ("S17", "cell", "Crystalliser slurry", "X501.out", "C501.in", 200, 303.15, "D-007"),
        ("S18", "wet", "Wet KMnO4 crystals", "C501.cake", "DR501.in", 101.325, 303.15, "6 wt% liquid (D-007)"),
        ("S19", "ml", "Mother liquor", "C501.ml", "S601.in", 200, 303.15, "1.5 wt% KMnO4, 13 wt% KOH (D-007)"),
        ("S20", "prod", "Potassium permanganate product", "DR501.prod", "KMNO4.in", 101.325, 353.15, "design basis 1250 kg/h (D-002)"),
        ("S21", "vap", "Dryer exhaust vapour", "DR501.vap", "DRYV.in", 101.325, 383.15, "D-007"),
        ("S22", "ml_ev", "Mother liquor to the KOH evaporator", "S601.evap", "E601.in", 300, 303.15, "D-008"),
        ("S23", "purge", "Mother-liquor purge to effluent treatment", "S601.purge", "PURGE.in", 300, 303.15, "3 % of the mother liquor (D-008)"),
    ]
    src = "scripts/kmno4_balance.py"
    lines = []
    for sid, key, title, fr, to, p_, t_, note in table:
        s = S[key]
        comp = ", ".join(f"{c}: {round(w, 6)}" for c, w in frac(s).items() if round(w, 6) > 0)
        lines += [
            f"  - id: {sid}", f"    title: {title}", f"    from: {fr}", f"    to: {to}",
            "    template: kmno4", "    state:", "      design:",
            f"        pressure: {{value: {p_}, provenance: assumed, source: \"D-009\"}}",
            f"        temperature: {{value: {t_}, provenance: assumed, source: \"D-009\"}}",
            f"        flow: {{value: {round(tot(s), 2)}, basis: mass, provenance: assumed, source: \"{src} ({note})\"}}",
            f"        composition: {{basis: mass_fraction, values: {{{comp}}}, provenance: assumed, source: \"{src}\"}}",
        ]
    Path("build/streams.yaml").write_text("\n".join(lines) + "\n")
    ins = sum(tot(S[k]) for k in ("ore", "koh", "air", "lime", "water"))
    outs = sum(tot(S[k]) for k in ("offgas", "residue", "h2", "o2", "prod", "vap", "purge"))
    print(f"overall in {ins:.3f} out {outs:.3f} kg/h")


if __name__ == "__main__":
    main()
