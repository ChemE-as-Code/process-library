"""What core cannot calculate in the methylchlorosilanes plant (DESIGN.md D-003 to D-009).

cheme process propagate computes every flow and composition from the feeds (the mixer, the
pass-through steps, the conversion step R201 on the silicon, the component separators CY202,
C302, C401, C402 and C403), solves the silicon for 60 000 t/a of Me2SiCl2 and the fresh methyl
chloride for the reactor's methyl chloride ratio (core ADR 0070) and converges the methyl
chloride loop at the tear S2 (ADR 0060). This script gives, from the streams propagate wrote:

- the reaction shares of reactions.yaml from the ASSUMED crude distribution, and the methyl
  chloride consumed per mol of silicon fed, the basis of the spec `mecl` (D-003, D-004);
- the reactor R-201's heat (Q2): core's conversion step counts every inlet as an ideal gas and
  has no formation enthalpy of Me2SiCl2, so the energy balance is done here, the silicon and
  copper as solids (D-005, L-1, L-2);
- the vaporiser Q1, the crude gas cooler-condenser Q3, the recycle-gas compressor K-303 and the
  four columns' reboilers and condensers (Q4 to Q11), each column's heat balance closed from its
  feed to its outlets at their stated temperatures; the superfractionator's minimum reflux
  (Underwood) and stages (Fenske, Gilliland after Eduljee) at the relative volatility of SRC-3;
- the saturation temperatures the flowsheet states (S2, S12, S14, S16) and the mixed S3;
- the powers P1 to P3.

Data (DESIGN.md SRC-7, library ADR 0037): formation enthalpies of the gases from `chemicals`
1.5.2 (ATCT_G for methyl chloride, ethane and ethylene; CRC for MeSiCl3 and Me3SiCl; YAWS for
MeHSiCl2); Me2SiCl2's is ASSUMED, the mean of Me3SiCl's and MeSiCl3's (no value in `chemicals`
or the NIST WebBook), and the residue's follows from an ASSUMED heat per mol of silicon equal
to that of the Me2SiCl2 reaction. Ideal-gas, liquid and solid heat capacities, heats of
vaporisation and vapour pressures from thermo 0.6.1's default methods, except the gas heat
capacities of Me2SiCl2 and Me3SiCl, interpolated (ASSUMED) between MeSiCl3 and Me4Si
(WEBBOOK_SHOMATE) by the number of methyl groups, because thermo has only a group estimate
(LASTOVKA_SHAW) for them.

Run: `cheme run scripts/balance.py`, after `cheme process propagate --fill`. With BALANCE_OUTPUT
set it writes the values the flowsheet cites (library ADR 0027).

Every parameter below is ASSUMED unless its comment names a source.
"""

from __future__ import annotations

import json
import math
import os
from pathlib import Path

import yaml
from scipy.integrate import quad
from scipy.optimize import brentq
from thermo import Chemical

ROOT = Path(__file__).resolve().parent.parent
R_GAS = 8.314462618  # J/(mol K)
T_REF = 298.15

# crude silane distribution, wt% of the silanes (D-004): inside the ranges of SRC-4 and SRC-5,
# T/D and residue as SRC-1's Example 3 (US 4 500 724 A)
CRUDE_WT = {"DMDCS": 84.0, "MTCS": 7.0, "TMCS": 3.0, "MDCS": 1.5, "DISIL": 4.5}
X_SI = 0.95  # silicon conversion (SRC-4: 90 to 98 %)
X_MECL = 0.50  # methyl chloride conversion per pass (SRC-4: 30 to 90 %)

T_BED = 573.15  # K (SRC-1: 250 to 350 C, the examples about 300 C)
P_COND, P_C302 = 380.0, 722.0  # kPa(a): crude condensation; C-302 at about 90 psig (SRC-2)
P_K303 = 760.0  # kPa(a), compressor discharge into C-302
ETA_K303, ETA_MOTOR, ETA_PUMP = 0.75, 0.95, 0.60
P_DIST = 200.0  # kPa(a), C-401 to C-403 tops
T_STORE = 313.15  # K, products and residue cooled to storage
REFLUX = {"C302": 1.0, "C401": 0.5, "C402": 15.0}  # external reflux ratios, ASSUMED
ALPHA_TD = 1.17  # MeSiCl3/Me2SiCl2 relative volatility, 10/90 mol% mixture (SRC-3, Example 2)
R_OVER_RMIN = 1.2
SI_HANDLING_KWH_PER_T = 50.0  # silicon milling, conveying and lock hoppers, ASSUMED allowance
DP_PUMP = 400.0  # kPa, every liquid transfer, ASSUMED
RHO_LIQ = 1000.0  # kg/m3, every pumped liquid, ASSUMED

CAS = {"MECL": "74-87-3", "DMDCS": "75-78-5", "MTCS": "75-79-6", "TMCS": "75-77-4",
       "MDCS": "75-54-7", "DISIL": "4518-98-3", "C2H6": "74-84-0", "C2H4": "74-85-1",
       "SI": "7440-21-3", "CU": "7440-50-8"}
SOLIDS = {"SI", "CU"}
GASES = {"C2H6", "C2H4"}  # never condensed here (dissolved traces counted as gas)

# gas formation enthalpies, J/mol (header); Si and Cu are their standard (solid) states
HF = {"MECL": -82620.0, "C2H6": -83780.0, "C2H4": 52560.0, "MTCS": -528900.0,
      "TMCS": -352800.0, "MDCS": -402000.0, "SI": 0.0, "CU": 0.0}
HF["DMDCS"] = 0.5 * (HF["TMCS"] + HF["MTCS"])  # ASSUMED (header)
DH_DMF = HF["DMDCS"] - 2 * HF["MECL"]
HF["DISIL"] = 2 * DH_DMF + 4 * HF["MECL"] - HF["C2H6"]  # ASSUMED: same heat per mol Si as DMF


def load(name: str) -> dict:
    return yaml.safe_load((ROOT / "process" / name).read_text(encoding="utf-8"))


MATERIALS = {c["id"]: c for c in load("materials.yaml")["components"]}
_CHEM = {k: Chemical(v) for k, v in CAS.items()}
_ME4SI = Chemical("75-76-3")


def cp_gas(c: str, t: float) -> float:
    if c in ("DMDCS", "TMCS"):
        n = {"DMDCS": 1, "TMCS": 2}[c]  # methyl groups beyond MeSiCl3's one, of three to Me4Si
        a, b = _CHEM["MTCS"].HeatCapacityGas(t), _ME4SI.HeatCapacityGas(t)
        return a + (b - a) * n / 3.0
    return _CHEM[c].HeatCapacityGas(t)


def h_gas(c: str, t: float) -> float:
    """J/mol, ideal gas (solids: the solid) relative to the elements at 298.15 K."""
    if c in SOLIDS:
        return HF[c] + quad(_CHEM[c].HeatCapacitySolid, T_REF, t)[0]
    return HF[c] + quad(lambda x: cp_gas(c, x), T_REF, t)[0]


def hvap(c: str, t: float) -> float:
    return _CHEM[c].EnthalpyVaporization(t)


def h_liq(c: str, t: float) -> float:
    if c in GASES or c in SOLIDS:
        return h_gas(c, t)
    return h_gas(c, t) - hvap(c, t)


def tsat(c: str, p_kpa: float) -> float:
    hi = min(700.0, _CHEM[c].Tc - 0.5)
    return brentq(lambda t: _CHEM[c].VaporPressure(t) - p_kpa * 1e3, 150.0, hi)


def component_flows(sheet: dict, sid: str) -> dict[str, float]:
    """kg/h of each component of a stream."""
    s = next(x for x in sheet["streams"] if x["id"] == sid)["state"]["design"]
    flow = float(s["flow"]["value"])
    comp = s["composition"]
    x = {k: float(v) for k, v in comp["values"].items()}
    if comp["basis"] == "mole_fraction":
        mass = {k: v * MATERIALS[k]["molar_mass"] for k, v in x.items()}
        tot = sum(mass.values())
        x = {k: v / tot for k, v in mass.items()}
    return {k: flow * v for k, v in x.items() if flow * v > 0.0}


def mol_s(flows: dict[str, float]) -> dict[str, float]:
    """mol/s from kg/h."""
    return {k: v / MATERIALS[k]["molar_mass"] / 3.6 for k, v in flows.items()}


def enthalpy_kw(flows: dict[str, float], t: float, phase: dict[str, str] | None = None) -> float:
    """kW; phase per component 'g', 'l' (default gas, solids solid)."""
    total = 0.0
    for c, n in mol_s(flows).items():
        ph = (phase or {}).get(c, "g")
        total += n * (h_liq(c, t) if ph == "l" else h_gas(c, t))
    return total / 1000.0


def liquid(flows: dict[str, float]) -> dict[str, str]:
    return {c: "l" for c in flows}


def reaction_shares() -> dict[str, float]:
    m = {k: MATERIALS[k]["molar_mass"] for k in CRUDE_WT}
    n = {k: v / m[k] for k, v in CRUDE_WT.items()}
    si = {"DMF": n["DMDCS"], "MTF": n["MTCS"] - n["TMCS"], "TMF": 2 * n["TMCS"],
          "MDF": n["MDCS"], "DSF": 2 * n["DISIL"]}
    tot = sum(si.values())
    return {k: v / tot for k, v in si.items()}


def column(name: str, feed: dict, t_feed: float, feed_phase: dict, outlets: list,
           q_cond_kw: float) -> float:
    """Reboiler duty that closes the column: Q_reb = Q_cond + H_out - H_in."""
    h_in = enthalpy_kw(feed, t_feed, feed_phase)
    h_out = sum(enthalpy_kw(f, t, ph) for f, t, ph in outlets)
    q_reb = q_cond_kw + h_out - h_in
    print(f"{name}: condenser {q_cond_kw:.1f} kW, reboiler {q_reb:.1f} kW")
    return q_reb


def pump_kw(flows: dict[str, float], t: float) -> float:
    """kW at the motor for a liquid transfer of DP_PUMP (the dissolved gases left out), at an
    ASSUMED liquid density RHO_LIQ (the chlorosilanes about 1.07 g/cm3, SRC-5; methyl chloride
    lighter); t is kept for a later density model."""
    vol = sum(v for c, v in flows.items() if c not in GASES) / RHO_LIQ / 3600.0  # m3/s
    return vol * DP_PUMP / ETA_PUMP / ETA_MOTOR


def main() -> None:
    sheet = load("flowsheet.yaml")
    rx = {r["id"]: r for r in load("reactions.yaml")["reactions"]}
    out: dict[str, dict] = {}

    # reaction shares (D-004) and the methyl chloride ratio of the spec mecl (D-003)
    shares = reaction_shares()
    for k, v in shares.items():
        print(f"{k}: share {v:.5f}, conversion {X_SI * v:.5f} (reactions.yaml {rx[k]['conversion']['value']})")
    mecl_per_si = X_SI * sum(shares[k] * -rx[k]["stoichiometry"]["MECL"] / -rx[k]["stoichiometry"]["SI"] for k in shares)
    ratio = mecl_per_si / X_MECL * MATERIALS["MECL"]["molar_mass"] / MATERIALS["SI"]["molar_mass"]
    print(f"methyl chloride consumed {mecl_per_si:.5f} mol per mol Si fed; reactor feed ratio {ratio:.4f} kg/kg")

    s = {sid: component_flows(sheet, sid) for sid in
         ("S1", "S2", "S3", "S4", "S5", "S6", "S7", "S9", "S10", "S11", "S12", "S13", "S14",
          "S15", "S16", "S17", "S18")}

    # saturation temperatures (D-007, D-008)
    t2 = tsat("MECL", P_C302)
    t12 = tsat("DMDCS", P_C302)
    t14 = tsat("DMDCS", P_DIST)
    t_top402 = tsat("TMCS", P_DIST)
    t_top403 = tsat("MTCS", P_DIST)
    t_bot401 = tsat("DISIL", P_DIST)
    out["S2"] = {"temperature": round(t2, 1)}
    out["S12"] = {"temperature": round(t12, 1)}
    out["S14"] = {"temperature": round(t14, 1)}
    out["S16"] = {"temperature": round(t14, 1)}
    print(f"T sat: MeCl at {P_C302} kPa {t2:.1f} K; Me2SiCl2 at {P_C302} kPa {t12:.1f} K, at {P_DIST} kPa "
          f"{t14:.1f} K; Me3SiCl {t_top402:.1f} K, MeSiCl3 {t_top403:.1f} K, residue {t_bot401:.1f} K at {P_DIST} kPa")

    # S3: S1 (298.15 K) and S2 mixed as liquids
    h_mix = enthalpy_kw(s["S1"], 298.15, liquid(s["S1"])) + enthalpy_kw(s["S2"], t2, liquid(s["S2"]))
    t3 = brentq(lambda t: enthalpy_kw(s["S3"], t, liquid(s["S3"])) - h_mix, 280.0, 320.0)
    out["S3"] = {"temperature": round(t3, 1)}
    print(f"S3 {t3:.1f} K")

    # E-101 (Q1): the liquid vaporised and superheated to 453.15 K
    q1 = enthalpy_kw(s["S4"], 453.15) - enthalpy_kw(s["S3"], t3, liquid(s["S3"]))
    out["Q1"] = {"duty": round(q1, 1)}

    # R-201 (Q2): heat to the cooling coils, the bed at T_BED
    h_in = enthalpy_kw(s["S4"], 453.15) + enthalpy_kw(s["S5"], 298.15) + enthalpy_kw(s["S6"], 298.15)
    h_out = enthalpy_kw(s["S7"], T_BED)
    q2 = h_in - h_out
    out["Q2"] = {"duty": round(q2, 1)}
    si_reacted = (s["S5"]["SI"] - s["S7"].get("SI", 0.0)) / MATERIALS["SI"]["molar_mass"] / 3.6
    print(f"R-201: dH(DMF) {DH_DMF / 1000:.1f} kJ/mol; Q2 {q2:.1f} kW, {q2 / si_reacted:.1f} kJ per mol Si reacted")
    t_ad = brentq(lambda t: enthalpy_kw(s["S7"], t) - h_in, T_BED, 3000.0)
    print(f"R-201 without cooling: outlet {t_ad:.0f} K")

    # E-301 (Q3): the crude gas to 313.15 K, the silanes condensed, MeCl and hydrocarbons gas
    t10 = 313.15
    ph10 = {c: ("g" if c in GASES or c == "MECL" else "l") for c in s["S10"]}
    q3 = enthalpy_kw(s["S9"], T_BED) - enthalpy_kw(s["S10"], t10, ph10)
    out["Q3"] = {"duty": round(q3, 1)}

    # K-303: the gas of S10 (MeCl, hydrocarbons) from P_COND to P_K303
    gas = {c: v for c, v in s["S10"].items() if ph10[c] == "g"}
    n_gas = sum(mol_s(gas).values())
    cp = sum(n * cp_gas(c, t10) for c, n in mol_s(gas).items()) / n_gas
    t_is = t10 * (P_K303 / P_COND) ** (R_GAS / cp)
    w_k303 = n_gas * cp * (t_is - t10) / ETA_K303 / 1000.0
    t_k303 = t10 + (t_is - t10) / ETA_K303
    print(f"K-303: {sum(gas.values()):.0f} kg/h, {w_k303:.1f} kW shaft, outlet {t_k303:.1f} K")

    # C-302 (Q4, Q5): condenser at t2, the distillate (S2) and the vent's MeCl condensed at reflux R
    d_mecl = mol_s(s["S2"]).get("MECL", 0.0) + mol_s(s["S11"]).get("MECL", 0.0)
    q5 = (REFLUX["C302"] + 1.0) * d_mecl * hvap("MECL", t2) / 1000.0
    liq10 = {c: v for c, v in s["S10"].items() if ph10[c] == "l"}
    h_feed = enthalpy_kw(liq10, t10, liquid(liq10)) + enthalpy_kw(gas, t_k303)
    h_outs = (enthalpy_kw(s["S11"], t2) + enthalpy_kw(s["S2"], t2, {"MECL": "l"})
              + enthalpy_kw(s["S12"], t12, liquid(s["S12"])))
    q4 = q5 + h_outs - h_feed
    print(f"C-302: condenser {q5:.1f} kW, reboiler {q4:.1f} kW")
    out["Q4"], out["Q5"] = {"duty": round(q4, 1)}, {"duty": round(q5, 1)}

    # C-401 (Q6, Q7): overhead S14 at t14 condensed at reflux 0.5; residue cooled to storage
    d14 = sum(mol_s(s["S14"]).values())
    hv14 = sum(n * hvap(c, t14) for c, n in mol_s(s["S14"]).items() if c not in GASES) / d14
    qc401 = (REFLUX["C401"] + 1.0) * d14 * hv14 / 1000.0
    q_res_cool = enthalpy_kw(s["S13"], t_bot401, liquid(s["S13"])) - enthalpy_kw(s["S13"], T_STORE, liquid(s["S13"]))
    q7 = qc401 + q_res_cool
    q6 = column("C-401", s["S12"], t12, liquid(s["S12"]),
                [(s["S13"], T_STORE, liquid(s["S13"])), (s["S14"], t14, liquid(s["S14"]))], q7)
    out["Q6"], out["Q7"] = {"duty": round(q6, 1)}, {"duty": round(q7, 1)}

    # C-402 (Q8, Q9): lights at reflux 15, condensed at the top and cooled to storage
    d15 = sum(mol_s(s["S15"]).values())
    hv15 = sum(n * hvap(c, t_top402) for c, n in mol_s(s["S15"]).items() if c not in GASES) / d15
    q9 = (REFLUX["C402"] + 1.0) * d15 * hv15 / 1000.0 + (
        enthalpy_kw(s["S15"], t_top402, liquid(s["S15"])) - enthalpy_kw(s["S15"], T_STORE, liquid(s["S15"])))
    q8 = column("C-402", s["S14"], t14, liquid(s["S14"]),
                [(s["S15"], T_STORE, liquid(s["S15"])), (s["S16"], t14, liquid(s["S16"]))], q9)
    out["Q8"], out["Q9"] = {"duty": round(q8, 1)}, {"duty": round(q9, 1)}

    # C-403 (Q10, Q11): Underwood minimum reflux and Fenske-Gilliland stages, MeSiCl3 light key
    def x_light(flows: dict) -> float:
        n = mol_s(flows)
        return n.get("MTCS", 0.0) / (n.get("MTCS", 0.0) + n.get("DMDCS", 0.0))

    xf, xd, xb = x_light(s["S16"]), x_light(s["S17"]), x_light(s["S18"])
    a = ALPHA_TD
    r_min = (xd / xf - a * (1 - xd) / (1 - xf)) / (a - 1)  # saturated-liquid feed
    r403 = R_OVER_RMIN * r_min
    n_min = math.log(xd / (1 - xd) * (1 - xb) / xb) / math.log(a)
    xg = (r403 - r_min) / (r403 + 1)
    yg = 0.75 * (1 - xg ** 0.5668)
    n_stages = (n_min + yg) / (1 - yg)
    d17 = sum(mol_s(s["S17"]).values())
    q11c = (r403 + 1.0) * d17 * hvap("MTCS", t_top403) / 1000.0
    q_cool = (enthalpy_kw(s["S17"], t_top403, liquid(s["S17"])) - enthalpy_kw(s["S17"], T_STORE, liquid(s["S17"]))
              + enthalpy_kw(s["S18"], t14, liquid(s["S18"])) - enthalpy_kw(s["S18"], T_STORE, liquid(s["S18"])))
    q11 = q11c + q_cool
    print(f"C-403: x_F {xf:.4f}, x_D {xd:.4f}, x_B {xb:.5f} (mol MeSiCl3); R_min {r_min:.1f}, R {r403:.1f}; "
          f"N_min {n_min:.1f}, N {n_stages:.0f} theoretical stages; boil-up {(r403 + 1) * d17 * 3.6:.0f} kmol/h")
    q10 = column("C-403", s["S16"], t14, liquid(s["S16"]),
                 [(s["S17"], T_STORE, liquid(s["S17"])), (s["S18"], T_STORE, liquid(s["S18"]))], q11)
    out["Q10"], out["Q11"] = {"duty": round(q10, 1)}, {"duty": round(q11, 1)}

    # powers (D-009)
    p1 = SI_HANDLING_KWH_PER_T * s["S5"]["SI"] / 1000.0 + pump_kw(s["S3"], t3)
    p2 = w_k303 / ETA_MOTOR + pump_kw(s["S2"], t2) + pump_kw(liq10, t10)
    p3 = sum(pump_kw(s[k], 330.0) for k in ("S12", "S13", "S14", "S15", "S16", "S17", "S18"))
    for k, v in (("P1", p1), ("P2", p2), ("P3", p3)):
        out[k] = {"duty": round(v, 1)}

    prod = sum(s["S18"].values())
    steam_in = q1 + q4 + q6
    lps = q8 + q10
    cw = q3 + q5 + q7 + q9 + q11
    power = p1 + p2 + p3
    print(f"per kg Me2SiCl2: Si {s['S5']['SI'] / prod:.4f} kg, MeCl {sum(s['S1'].values()) / prod:.4f} kg, "
          f"Cu {s['S6']['CU'] / prod * 1000:.3f} g; MP steam raised {q2 / prod:.4f} kWh, MP steam used "
          f"{steam_in / prod:.4f} kWh, LP steam {lps / prod:.4f} kWh, cooling water {cw / prod:.4f} kWh, "
          f"power {power / prod:.4f} kWh")
    for k in sorted(out, key=lambda x: (x[0], int(x[1:]))):
        print(k, out[k])
    write_balance_output({"design": out})


def write_balance_output(cases: dict) -> None:
    """With BALANCE_OUTPUT set, write the values the flowsheet cites from this script as JSON.

    The process library's balance-output contract (docs/adr/0027 of the library): case ->
    stream id -> quantity, in the flowsheet's units and basis. The library's
    scripts/check_balance_scripts.py re-runs this script and compares them with
    process/flowsheet.yaml.
    """
    target = os.environ.get("BALANCE_OUTPUT")
    if target:
        doc = {"contract": "balance-output/1", "script": f"scripts/{Path(__file__).name}",
               "cases": cases}
        Path(target).write_text(json.dumps(doc, indent=1, default=float), encoding="utf-8")


if __name__ == "__main__":
    main()
