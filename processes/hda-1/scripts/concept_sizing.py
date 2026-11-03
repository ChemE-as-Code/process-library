"""Concept sizing of the hda-1 equipment for the plot plan and the class 5 estimate (D-017).

Run: cheme run scripts/concept_sizing.py

Reads the simulated duties and stream values of process/simulation-run.json (DWSIM, D-014) and
the C-201 duties of process/flowsheet.yaml (scripts/hda_balance.py, D-014), and prints

- exchanger areas A = Q / (U * LMTD), counter-current, with the ASSUMED overall heat transfer
  coefficients of this design (no rating, no fouling margin: a concept size);
- column diameters from the vapour load at an ASSUMED F-factor (u * sqrt(rho_v)) and an ASSUMED
  active-area fraction, heights from the theoretical stages at an ASSUMED tray efficiency;
- the HP separator diameter from a Souders-Brown velocity at an ASSUMED K;
- the feed drum volume from an ASSUMED residence time.

Every coefficient below is a concept choice of this design (ASSUMED), not taken from a
publication. Densities of gases are ideal-gas values at the stream's T, P and molar mass;
latent heats are the simulated condenser duties over the condensed vapour (C-202 benzene, C-203
toluene), and the liquid density is an ASSUMED round value (cheme-as-code's interpreter has no
property package to evaluate them).
The results are rounded up into equipment/equipment-list.yaml `dimensions` and
estimate/cost-basis.yaml `size`; datasheets replace them at basic engineering.
"""

from __future__ import annotations

import json
import math
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
R = 8.314462618  # kJ/(kmol K)
MW = {"H2": 2.01588, "CH4": 16.0425, "TOL": 92.13842, "BZ": 78.11184, "BIPH": 154.2078}

# ---- ASSUMED concept coefficients (D-017)
U = {  # W/(m2 K), overall, clean
    "E-101": 300,  # gas/gas at about 3.5 MPa with condensation and vaporisation of the aromatics
    "E-102": 400,  # cooling the loop gas against cooling water, aromatics condensing
    "E-201": 300,  # partial condenser, mostly non-condensable H2/CH4 vapour
    "E-202": 800,  # MP-steam reboiler, aromatics
    "E-203": 700,  # benzene condenser against cooling water
    "E-204": 800,  # LP-steam reboiler, aromatics
    "E-205": 600,  # toluene condenser under vacuum
    "E-206": 700,  # HP-steam reboiler, biphenyl
    "E-207": 500,  # benzene liquid product cooled against cooling water (D-022)
}
F_FACTOR = 2.0       # Pa^0.5, sieve trays at the design vapour load
ACTIVE = 0.85        # active-area fraction of the column cross-section
TRAY_EFF = 0.7       # overall tray efficiency
TRAY_SPACING = 0.6   # m
COLUMN_EXTRA = 5.0   # m: sump, top disengagement and skirt
K_SB = 0.07          # m/s, Souders-Brown K of a vertical separator with a mesh pad
V100_RESIDENCE_MIN = 10.0  # min of liquid hold-up at half full
V101_LIQUID_MIN = 5.0      # min of liquid hold-up
CW_IN, CW_OUT = 298.15, 308.15  # D-010
RHO_LIQ = 850.0      # kg/m3, aromatics liquid near 313 K
STEAM_T = {"MPS": 471.4, "LPS": 420.8, "HPS": 526.4}  # D-010, saturated


def lmtd(dt1: float, dt2: float) -> float:
    if abs(dt1 - dt2) < 1e-9:
        return dt1
    return (dt1 - dt2) / math.log(dt1 / dt2)


def main() -> None:
    run = json.loads((ROOT / "process/simulation-run.json").read_text())["cases"]["design"]
    units = {u["id"]: u.get("results", {}) for u in run["units"]}
    streams = {s["id"]: s["values"] for s in run["streams"]}
    flowsheet = yaml.safe_load((ROOT / "process/flowsheet.yaml").read_text())
    duty = {s["id"]: s["state"]["design"]["duty"]["value"] for s in flowsheet["streams"]
            if s.get("kind") == "energy"}

    def t(sid: str) -> float:
        return streams[sid]["temperature"]["value"]

    def molar_mass(sid: str) -> float:
        comp = streams[sid]["composition"]["values"]
        return sum(x * MW[k] for k, x in comp.items())

    # latent heats from the simulation: condenser duty over the condensed vapour V = D (R + 1)
    latent = {
        "BZ": units["C202"]["condenser_kW"] * 3600.0 / (streams["S26"]["flow"]["value"] * 3.18),
        "TOL": units["C203"]["condenser_kW"] * 3600.0 / (streams["S23"]["flow"]["value"] * 1.5),
    }
    # biphenyl bottoms of C-203: the toluene value, ASSUMED (no simulated biphenyl latent heat)
    latent["BIPH"] = latent["TOL"]
    out_latent = ", ".join(f"{k} {v:.0f} kJ/kg" for k, v in latent.items())

    def hvap(key: str, temp: float) -> float:  # kJ/kg; temperature not used (concept value)
        return latent[key]

    def rho_liq(key: str, temp: float, p_kpa: float) -> float:
        return RHO_LIQ

    out = [("latent heats", out_latent)]
    # ---- exchangers
    ex = {
        "E-101": (units["E101"]["duty_kW"], lmtd(t("S9") - t("S6"), t("S10") - t("S5")),
                  "S9 -> S10 against S5 -> S6"),
        "E-102": (abs(units["E102"]["duty_kW"]), lmtd(t("S10") - CW_OUT, t("S11") - CW_IN),
                  "S10 -> S11 against CW"),
        # C-201 partial condenser: top vapour taken at the S20 bubble side is not simulated; the
        # condensing range is ASSUMED 350 -> 313.15 K (the D-008 condenser outlet)
        "E-201": (duty["Q6"], lmtd(350.0 - CW_OUT, 313.15 - CW_IN), "ASSUMED 350 -> 313.15 K against CW"),
        "E-202": (duty["Q5"], STEAM_T["MPS"] - t("S20"), "MP steam against S20 bubble point"),
        "E-203": (duty["Q8"], lmtd(t("S26") - CW_IN, t("S26") - CW_OUT), "condensing at the S26 temperature"),
        "E-204": (duty["Q7"], STEAM_T["LPS"] - t("S22"), "LP steam against S22"),
        "E-205": (duty["Q10"], lmtd(t("S23") - CW_IN, t("S23") - CW_OUT), "condensing at the S23 temperature"),
        "E-206": (duty["Q9"], STEAM_T["HPS"] - t("S24"), "HP steam against S24"),
        "E-207": (abs(units["E207"]["duty_kW"]), lmtd(t("S26") - CW_OUT, 313.15 - CW_IN),
                  "S26 -> 313.15 K against CW (D-022)"),
    }
    for tag, (q, dt, basis) in ex.items():
        area = q * 1000 / (U[tag] * dt)
        out.append((tag, f"Q {q:.1f} kW, LMTD {dt:.1f} K ({basis}), U {U[tag]} W/(m2 K) -> A {area:.1f} m2"))

    # ---- columns: vapour load at the top (V = D (R + 1)) and below the feed (reboiler duty /
    # latent heat of the bottoms' main component)
    def column(tag: str, top_kg_h: float, top_mw: float, top_t: float, top_p: float,
               reb_kw: float, bot_key: str, bot_t: float, bot_p: float, bot_mw: float,
               stages: float) -> None:
        loads = []
        for label, kg_h, mw, temp, p in (
            ("top", top_kg_h, top_mw, top_t, top_p),
            ("bottom", reb_kw / hvap(bot_key, bot_t) * 3600.0, bot_mw, bot_t, bot_p),
        ):
            rho = mw * p / (R * temp)
            q = kg_h / 3600.0 / rho
            area = q / (F_FACTOR / math.sqrt(rho)) / ACTIVE
            loads.append((label, kg_h, rho, math.sqrt(4 * area / math.pi)))
        dmax = max(d for *_, d in loads)
        trays = math.ceil(stages / TRAY_EFF)
        height = trays * TRAY_SPACING + COLUMN_EXTRA
        text = "; ".join(f"{lab} vapour {kg:.0f} kg/h, rho_v {rho:.2f} kg/m3 -> D {d:.2f} m"
                         for lab, kg, rho, d in loads)
        out.append((tag, f"{text}; {stages:.1f} theoretical stages / {TRAY_EFF} = {trays} trays x "
                         f"{TRAY_SPACING} m + {COLUMN_EXTRA} m -> H {height:.1f} m"))

    s19, s26, s23 = streams["S19"], streams["S26"], streams["S23"]
    column("C-201", s19["flow"]["value"] * (1.0 + 1.0), molar_mass("S19"), 313.15, 800.0,
           duty["Q5"], "BZ", t("S20"), 800.0, molar_mass("S20"), max(units["C201"]["stages"], 8.0))
    column("C-202", s26["flow"]["value"] * (1.0 + 2.18), molar_mass("S26"), t("S26"), 150.0,
           duty["Q7"], "TOL", t("S22"), 170.0, molar_mass("S22"), units["C202"]["stages"])
    column("C-203", s23["flow"]["value"] * (1.0 + 0.5), molar_mass("S23"), t("S23"), 30.0,
           duty["Q9"], "BIPH", t("S24"), 45.0, molar_mass("S24"), 10.0)

    # ---- HP separator V-101
    gas = streams["S12"]
    rho_v = molar_mass("S12") * gas["pressure"]["value"] / (R * t("S12"))
    rho_l = rho_liq("BZ", t("S16"), 3250.0)
    u = K_SB * math.sqrt((rho_l - rho_v) / rho_v)
    qv = gas["flow"]["value"] / 3600.0 / rho_v
    d = math.sqrt(4 * qv / u / math.pi)
    liq = streams["S16"]["flow"]["value"] / rho_l / 60.0 * V101_LIQUID_MIN
    out.append(("V-101", f"gas {qv:.3f} m3/s, rho_v {rho_v:.1f}, rho_l {rho_l:.0f} kg/m3, K {K_SB} -> "
                         f"u {u:.3f} m/s, D {d:.2f} m; liquid {V101_LIQUID_MIN} min = {liq:.2f} m3"))

    # ---- feed drum V-100
    rho_t = rho_liq("TOL", t("S2"), 150.0)
    vol = streams["S2"]["flow"]["value"] / rho_t / 60.0 * V100_RESIDENCE_MIN * 2.0
    out.append(("V-100", f"liquid {streams['S2']['flow']['value']:.0f} kg/h / {rho_t:.0f} kg/m3, "
                         f"{V100_RESIDENCE_MIN} min at half full -> {vol:.2f} m3"))

    # ---- R-101: no rate law (D-005), so no volume follows from the model; gas flow at the inlet
    s7 = streams["S7"]
    q7 = s7["flow"]["value"] / molar_mass("S7") / 3600.0 * R * t("S7") / s7["pressure"]["value"]
    out.append(("R-101", f"inlet gas {q7:.3f} m3/s (ideal gas, S7); volume not from a model (D-005)"))

    # ---- machines and fired heater: simulated duties
    out.append(("P-102", f"{units['P102']['duty_kW']:.2f} kW (DWSIM, D-022)"))
    out.append(("P-101", f"{units['P101']['duty_kW']:.1f} kW (DWSIM, D-014)"))
    out.append(("K-101", f"{units['K101']['duty_kW']:.1f} kW (DWSIM, D-014)"))
    out.append(("H-101", f"{units['H101']['duty_kW']:.1f} kW absorbed (DWSIM, D-014)"))

    for tag, text in out:
        print(f"{tag}: {text}")


if __name__ == "__main__":
    main()
