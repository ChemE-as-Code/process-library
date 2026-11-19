"""What core cannot calculate in the maleic anhydride plant (DESIGN.md D-003, D-007 to D-010).

cheme process propagate computes every flow and composition from the feeds (pass-through
steps, the mixers, the purge splitter, the conversion steps R201 and R501, the component
separators A301, T302 and C401), solves the feeds for 25 000 t/a and the solvent make-up for
the circulation ratio (core ADR 0070), converges the solvent loop at the tear S17 (ADR 0060)
and writes the duties of R201 (Q2) and R501 (Q9) from the heats of reaction and the ideal-gas
data of process/materials.yaml (ADR 0059). This script gives, from the streams propagate wrote:

- the humid air per kg of butane that gives the reactor feed of SRC-1 (1.8 mol% butane, 1.7
  mol% water): the `with:` ratio of the spec `rate`;
- the air compressor K-102: outlet temperature (S4) and shaft and motor power (P1);
- the mixed temperatures S5 (butane and air), S16 (lean solvent and make-up) and S21 (the
  oxidiser's feeds), and the stack temperature S23 after the draught fan;
- the duties core has no model for: the butane vaporiser Q1, the reactor gas cooler Q3 (ideal
  gas, the data of materials.yaml), the absorber's pump-around coolers Q10, the stripper's
  reboiler and condenser Q4 and Q5, the lean solvent cooler Q6, the column's reboiler and
  condenser Q7 and Q8 (liquid heat capacities and heats of vaporisation from thermo 0.6.1 /
  chemicals 1.5.2, MA's heat of vaporisation from the NIST WebBook); each separator's duties
  close its heat balance from its inlet to its outlets at their stated temperatures;
- the oxidiser F-501's burn: the adiabatic temperature of its feed as it comes, and the
  recuperator duty that preheats the feed so that it burns at T_BURN (internal to F-501, no
  utility; core's Q9 is the heat left for the waste-heat boiler and economiser);
- the powers of the pumps and vacuum systems (P2, P3) and the oxidiser fan (P4).

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
from thermo import Chemical

ROOT = Path(__file__).resolve().parent.parent
R = 8.314462618  # J/(mol K)

# reactor feed (SRC-1, US 7 589 217 B2: 1.8 vol% butane, 1.7 vol% water in air)
Y_BUTANE, Y_WATER = 0.018, 0.017
DRY_AIR = {"N2": 0.78084, "O2": 0.20946, "AR": 0.00934}  # mol fractions, CO2 left out

P_AMB, T_AMB = 101.325, 298.15  # kPa(a), K (design basis)
P_AIR = 260.0  # kPa(a), compressor discharge (D-003)
ETA_COMP, ETA_MOTOR = 0.80, 0.96  # isentropic efficiency of K-102 and its motor (D-010)

T_SALT = 675.15  # K, salt bath (SRC-1, Example 3: 402 C)
# stripper T-302 (SRC-2, US 4 118 403 A): reboiler at 244 to 248 C, overhead condensed at
# 66 to 70 C, external reflux 2:1
T_STRIP_BOTTOM, T_STRIP_COND, REFLUX_STRIP = 519.15, 341.15, 2.0
T_CRUDE_DRAW = 400.0  # K, the crude's side draw before it is cooled to S10's 348 K (ASSUMED)
# column C-401: SRC-2 names about 100 torr and 140 C; reflux ratio ASSUMED
T_COL_BOTTOM, REFLUX_COL = 433.15, 1.5
HVAP_MA = 54.8e3  # J/mol, NIST WebBook (Winstrom and Kulp 1949, 326 to 350 K)
# pumps and vacuum (D-010)
ETA_PUMP = 0.60
# absorber A-301: pump-around coolers on cooling water (D-007), the circulating liquid cooled
# by 40 K and pumped by 250 kPa, ASSUMED
PUMPAROUND_DT, PUMPAROUND_DP = 40.0, 250.0
# thermal oxidiser F-501 (D-009): combustion chamber temperature, ASSUMED for the ASSUMED
# destruction without a catalyst; the feed preheated in a recuperator against the flue gas
T_BURN = 1073.15
VACUUM_STRIP_KW, VACUUM_COL_KW = 30.0, 15.0  # liquid-ring vacuum pumps, ASSUMED allowances
FAN_DP_KPA, ETA_FAN = 5.0, 0.70  # oxidiser draught fan, ASSUMED

CAS = {"NC4": "106-97-8", "H2O": "7732-18-5", "MA": "108-31-6", "AA": "64-19-7",
       "ACR": "79-10-7", "DBP": "84-74-2"}


def load(name: str) -> dict:
    return yaml.safe_load((ROOT / "process" / name).read_text(encoding="utf-8"))


MATERIALS = {c["id"]: c for c in load("materials.yaml")["components"]}
MW = {k: float(v["molar_mass"]) for k, v in MATERIALS.items()}


def component_flows(streams: dict, sid: str) -> dict[str, float]:
    """kg/h of each component of a stream (mass or mole fractions as the flowsheet gives)."""
    state = streams[sid]["state"]["design"]
    flow = float(state["flow"]["value"])
    comp = state["composition"]
    x = {k: float(v) for k, v in comp["values"].items()}
    if comp["basis"] == "mole_fraction":
        mass = {k: v * MW[k] for k, v in x.items()}
        total = sum(mass.values())
        x = {k: v / total for k, v in mass.items()}
    return {k: flow * v for k, v in x.items()}


def kmol(flows: dict[str, float]) -> dict[str, float]:
    return {k: v / MW[k] for k, v in flows.items()}


def h_ig(cid: str, t: float) -> float:
    """Ideal-gas sensible enthalpy, kJ/kmol, from 298.15 K (materials.yaml cp_R)."""
    a = MATERIALS[cid]["ideal_gas"]["cp_R"]
    return R * sum(c / (i + 1) * (t ** (i + 1) - 298.15 ** (i + 1)) for i, c in enumerate(a))


def h_gas(flows: dict[str, float], t: float) -> float:
    """kW of a gas stream's sensible heat from 298.15 K."""
    return sum(n * h_ig(k, t) for k, n in kmol(flows).items()) / 3600.0


def gas_temperature(inlets: list[tuple[dict, float]]) -> float:
    """Adiabatic mixing temperature of gases (ideal gas)."""
    h = sum(h_gas(f, t) for f, t in inlets)
    total: dict[str, float] = {}
    for f, _ in inlets:
        for k, v in f.items():
            total[k] = total.get(k, 0.0) + v
    lo, hi = 250.0, 900.0
    for _ in range(80):
        mid = 0.5 * (lo + hi)
        lo, hi = (mid, hi) if h_gas(total, mid) < h else (lo, mid)
    return 0.5 * (lo + hi)


def cpl(cid: str, t: float) -> float:
    """Liquid heat capacity, kJ/(kg K), thermo 0.6.1."""
    return Chemical(CAS[cid], T=t, P=101325.0).Cpl / 1000.0


def liquid_heat(flows: dict[str, float], t1: float, t2: float) -> float:
    """kW to heat a liquid from t1 to t2 (heat capacities at the mean temperature)."""
    tm = 0.5 * (t1 + t2)
    return sum(m * cpl(k, tm) for k, m in flows.items() if m > 0) * (t2 - t1) / 3600.0


def hvap(cid: str, t: float) -> float:
    """Heat of vaporisation, kJ/kg: MA from the NIST WebBook, the rest from thermo 0.6.1."""
    if cid == "MA":
        return HVAP_MA / MW["MA"]
    return Chemical(CAS[cid], T=t, P=101325.0).Hvap / 1000.0


def latent(flows: dict[str, float], t: float) -> float:
    return sum(m * hvap(k, t) for k, m in flows.items() if m > 0) / 3600.0


def pump_kw(mass: float, dp_kpa: float, rho: float = 1050.0) -> float:
    return mass / 3600.0 / rho * dp_kpa / ETA_PUMP


def main() -> None:
    sheet = load("flowsheet.yaml")
    streams = {s["id"]: s for s in sheet["streams"]}
    out: dict[str, dict] = {}

    # humid air per kg of butane (spec rate's `with:`)
    s_dry = sum(DRY_AIR.values())
    y_air_water = Y_WATER / (1.0 - Y_BUTANE)
    air = {k: v / s_dry * (1.0 - y_air_water) for k, v in DRY_AIR.items()}
    air["H2O"] = y_air_water
    m_air = sum(air[k] * MW[k] for k in air)
    ratio = (1.0 - Y_BUTANE) / Y_BUTANE * m_air / MW["NC4"]
    print(f"humid air {', '.join(f'{k} {v:.6f}' for k, v in air.items())}; "
          f"{ratio:.4f} kg per kg of butane")

    # K-102: isentropic compression of the humid air, then the efficiency
    s3 = component_flows(streams, "S3")
    n3 = kmol(s3)
    ntot = sum(n3.values())

    def s_ig(t: float) -> float:  # kJ/(kmol K) of the mixture, entropy change from 298.15 K
        tot = 0.0
        for k, n in n3.items():
            a = MATERIALS[k]["ideal_gas"]["cp_R"]
            ds = a[0] * math.log(t / 298.15)
            ds += sum(c / i * (t ** i - 298.15 ** i) for i, c in enumerate(a) if i > 0)
            tot += n / ntot * R * ds
        return tot

    target =s_ig(T_AMB) + R * math.log(P_AIR / P_AMB)
    lo, hi = T_AMB, 700.0
    for _ in range(80):
        mid = 0.5 * (lo + hi)
        lo, hi = (mid, hi) if s_ig(mid) < target else (lo, mid)
    t_is = 0.5 * (lo + hi)
    w_is = h_gas(s3, t_is) - h_gas(s3, T_AMB)
    w = w_is / ETA_COMP
    lo, hi = T_AMB, 800.0
    for _ in range(80):
        mid = 0.5 * (lo + hi)
        lo, hi = (mid, hi) if h_gas(s3, mid) - h_gas(s3, T_AMB) < w else (lo, mid)
    t4 = 0.5 * (lo + hi)
    p1 = w / ETA_MOTOR
    print(f"K-102: isentropic {t_is:.1f} K, outlet {t4:.1f} K, shaft {w:.1f} kW, motor {p1:.1f} kW "
          f"({p1 / sum(s3.values()) * 1000:.4f} kWh/t air)")
    out["S4"] = {"temperature": round(t4, 1)}
    out["P1"] = {"duty": round(p1, 1)}

    # E-101: butane vaporised at 400 kPa(a) and superheated to S2's temperature
    s1 = component_flows(streams, "S1")
    t2 = float(streams["S2"]["state"]["design"]["temperature"]["value"])
    p2 = float(streams["S2"]["state"]["design"]["pressure"]["value"])
    bu = Chemical(CAS["NC4"])
    tsat = bu.VaporPressure.solve_property(p2 * 1000.0)
    q1 = (liquid_heat(s1, T_AMB, tsat) + latent(s1, tsat) + h_gas(s1, t2) - h_gas(s1, tsat))
    print(f"E-101: saturation {tsat:.1f} K at {p2} kPa(a), duty {q1:.1f} kW")
    out["Q1"] = {"duty": round(q1, 1)}

    # S5: adiabatic mixing of the butane vapour and the compressed air
    t5 = gas_temperature([(component_flows(streams, "S2"), t2), (s3, t4)])
    print(f"S5: {t5:.1f} K")
    out["S5_t"] = t5
    out["S5"] = {"temperature": round(t5, 1)}

    # cross-check of R201's duty (core writes Q2): heat of reaction at 298 K and sensible heats
    s5, s6 = component_flows(streams, "S5"), component_flows(streams, "S6")
    t6 = float(streams["S6"]["state"]["design"]["temperature"]["value"])
    hf = {k: MATERIALS[k]["ideal_gas"]["dHf_298"] for k in MATERIALS}
    q2 = (sum(n * (hf[k] + h_ig(k, t5)) for k, n in kmol(s5).items())
          - sum(n * (hf[k] + h_ig(k, t6)) for k, n in kmol(s6).items())) / 3600.0
    print(f"R201 cross-check: {q2:.1f} kW to the salt (core writes Q2)")
    # loss of salt cooling at full conversion: the reaction heat stays in the gas (D-011)
    lo, hi = t6, 2000.0
    for _ in range(80):
        mid = 0.5 * (lo + hi)
        lo, hi = (mid, hi) if h_gas(s6, mid) - h_gas(s6, t6) < q2 else (lo, mid)
    print(f"R201 adiabatic: the gas would leave at {0.5 * (lo + hi):.0f} K "
          f"({0.5 * (lo + hi) - t6:.0f} K above {t6} K; cp extrapolated beyond 1000 K)")

    # E-202: reactor gas cooled to the absorber's inlet
    t7 = float(streams["S7"]["state"]["design"]["temperature"]["value"])
    q3 = h_gas(s6, t6) - h_gas(s6, t7)
    print(f"E-202: {q3:.1f} kW")
    out["Q3"] = {"duty": round(q3, 1)}

    # A-301: heat balance at SRC-2's four end temperatures. The gas is cooled from S7 to S8's
    # temperature, the absorbate (what S8 does not carry on) condensed there and heated with the
    # lean solvent to S9's temperature; the rest goes to the pump-around coolers (Q10)
    s7, s8, s17 = (component_flows(streams, k) for k in ("S7", "S8", "S17"))
    t8 = float(streams["S8"]["state"]["design"]["temperature"]["value"])
    t17 = float(streams["S17"]["state"]["design"]["temperature"]["value"])
    t9 = float(streams["S9"]["state"]["design"]["temperature"]["value"])
    absorbed = {k: s7[k] - s8.get(k, 0.0) for k in ("MA", "H2O", "AA", "ACR")}  # the gases pass
    gas_cool = h_gas(s7, t7) - h_gas(s7, t8)
    condense = latent(absorbed, t8)
    liq_heat = liquid_heat(s17, t17, t9) + liquid_heat(absorbed, t8, t9)
    q10 = gas_cool + condense - liq_heat
    cp_pa = (sum(m * cpl(k, 0.5 * (t9 + t17)) for k, m in s17.items() if m > 0)
             / sum(s17.values()))  # kJ/(kg K), the lean solvent's
    m_pa = q10 / (cp_pa * PUMPAROUND_DT) * 3600.0  # kg/h circulated through the coolers
    print(f"A-301: gas cooled {gas_cool:.1f} kW, absorbate condensed {condense:.1f} kW, liquids "
          f"heated {liq_heat:.1f} kW; pump-around coolers {q10:.1f} kW "
          f"({m_pa / 1000:.0f} t/h circulated, {PUMPAROUND_DT:.0f} K range)")
    out["Q10"] = {"duty": round(q10, 1)}

    # T-302: the part of the rich solvent that leaves as lean solvent heated to the reboiler's
    # temperature, the crude to its draw near the top and the lights to their outlet; the crude
    # and the lights boiled up (the lights at the external reflux 2); the condensers take the
    # overhead's latent heat and cool the crude from its draw to S10. Q4 - Q5 is then the
    # outlets' enthalpy less the inlet's
    s9, s10, s11, s12 = (component_flows(streams, k) for k in ("S9", "S10", "S11", "S12"))
    t10 = float(streams["S10"]["state"]["design"]["temperature"]["value"])
    t11 = float(streams["S11"]["state"]["design"]["temperature"]["value"])
    sens = (liquid_heat(s12, t9, T_STRIP_BOTTOM) + liquid_heat(s10, t9, T_CRUDE_DRAW)
            + liquid_heat(s11, t9, t11))
    boil = latent(s10, T_CRUDE_DRAW) + (1.0 + REFLUX_STRIP) * latent(s11, T_STRIP_COND)
    q4 = sens + boil
    q5 = boil + liquid_heat(s10, t10, T_CRUDE_DRAW)
    print(f"T-302: rich solvent {sens:.1f} kW, boil-up {boil:.1f} kW; reboiler {q4:.1f} kW, "
          f"condensers {q5:.1f} kW")
    out["Q4"] = {"duty": round(q4, 1)}
    out["Q5"] = {"duty": round(q5, 1)}

    # S16 and E-305: lean solvent with the make-up, cooled to S17
    s14, s15 = component_flows(streams, "S14"), component_flows(streams, "S15")
    t14 = float(streams["S14"]["state"]["design"]["temperature"]["value"])
    t15 = float(streams["S15"]["state"]["design"]["temperature"]["value"])
    m14 = sum(m * cpl(k, t14) for k, m in s14.items() if m > 0)
    m15 = sum(m * cpl(k, t15) for k, m in s15.items() if m > 0)
    t16 = (m14 * t14 + m15 * t15) / (m14 + m15)
    s16 = component_flows(streams, "S16")
    t17 = float(streams["S17"]["state"]["design"]["temperature"]["value"])
    q6 = liquid_heat(s16, t17, t16)
    print(f"S16 {t16:.1f} K; E-305 {q6:.1f} kW")
    out["S16"] = {"temperature": round(t16, 1)}
    out["Q6"] = {"duty": round(q6, 1)}

    # C-401: the residue heated to the bottom, the product and lights to the top and boiled up
    # at the reflux; the condenser takes the overhead's latent heat and cools the product and
    # the lights to their outlets (Q7 - Q8 is the outlets' enthalpy less the crude's)
    s18, s19, s20 = (component_flows(streams, k) for k in ("S18", "S19", "S20"))
    over = {k: s18.get(k, 0.0) + s19.get(k, 0.0) for k in set(s18) | set(s19)}
    boil_c = (1.0 + REFLUX_COL) * latent(over, 413.15)
    q7 = liquid_heat(s20, t10, T_COL_BOTTOM) + liquid_heat(over, t10, 413.15) + boil_c
    t18 = float(streams["S18"]["state"]["design"]["temperature"]["value"])
    t19 = float(streams["S19"]["state"]["design"]["temperature"]["value"])
    q8 = boil_c + liquid_heat(s18, t18, 413.15) + liquid_heat(s19, t19, 413.15)
    print(f"C-401: reboiler {q7:.1f} kW, condenser and product cooling {q8:.1f} kW")
    out["Q7"] = {"duty": round(q7, 1)}
    out["Q8"] = {"duty": round(q8, 1)}

    # pumps and vacuum
    s12 = component_flows(streams, "S12")
    p2_kw = (pump_kw(sum(s9.values()), 350.0) + pump_kw(sum(s12.values()), 300.0)
             + pump_kw(sum(s10.values()), 200.0, 1300.0) + pump_kw(m_pa, PUMPAROUND_DP)
             + VACUUM_STRIP_KW) / ETA_MOTOR
    p3_kw = (pump_kw(sum(s18.values()), 200.0, 1300.0) + VACUUM_COL_KW) / ETA_MOTOR
    s22 = component_flows(streams, "S22")
    v22 = sum(kmol(s22).values()) / 3600.0 * R * 453.15 / 101.325  # m3/s
    p4 = v22 * FAN_DP_KPA / ETA_FAN / ETA_MOTOR
    print(f"P2 {p2_kw:.1f} kW, P3 {p3_kw:.1f} kW, P4 {p4:.1f} kW ({v22:.1f} m3/s flue gas)")
    out["P2"] = {"duty": round(p2_kw, 1)}
    out["P3"] = {"duty": round(p3_kw, 1)}
    out["P4"] = {"duty": round(p4, 1)}
    # S23: the fan's shaft work heats the flue gas (after the boiler: no steam from it)
    w_fan = p4 * ETA_MOTOR
    lo, hi = 453.15, 600.0
    for _ in range(80):
        mid = 0.5 * (lo + hi)
        lo, hi = (mid, hi) if h_gas(s22, mid) - h_gas(s22, 453.15) < w_fan else (lo, mid)
    t23 = 0.5 * (lo + hi)
    print(f"S23 {t23:.1f} K after the fan")
    out["S23"] = {"temperature": round(t23, 1)}

    # S21: the oxidiser's feeds mixed (gases and the small liquid streams as ideal gas: a
    # concept estimate, the liquids are 0.1 % of the mass)
    feeds = [(component_flows(streams, k),
              float(streams[k]["state"]["design"]["temperature"]["value"]))
             for k in ("S8", "S11", "S13", "S19", "S20")]
    t21 = gas_temperature(feeds)
    print(f"S21 {t21:.1f} K")
    out["S21"] = {"temperature": round(t21, 1)}

    # F-501: total enthalpy (formation + sensible, ideal gas as core counts it, L-4) of the feed
    # S21 and the flue gas S22's composition. The adiabatic temperature of the feed as it comes,
    # the preheat that gives T_BURN, the recuperator's duty and the flue gas into the boiler
    s21 = component_flows(streams, "S21")

    def h_tot(flows: dict[str, float], t: float) -> float:
        return sum(n * (hf[k] + h_ig(k, t)) for k, n in kmol(flows).items()) / 3600.0

    def solve_t(flows: dict[str, float], h: float, lo: float, hi: float) -> float:
        for _ in range(80):
            mid = 0.5 * (lo + hi)
            lo, hi = (mid, hi) if h_tot(flows, mid) < h else (lo, mid)
        return 0.5 * (lo + hi)

    t_ad = solve_t(s22, h_tot(s21, t21), t21, 2000.0)
    t_pre = solve_t(s21, h_tot(s22, T_BURN), t21, T_BURN)
    q_rec = h_gas(s21, t_pre) - h_gas(s21, t21)
    t_boil = solve_t(s22, h_tot(s22, T_BURN) - q_rec, 453.15, T_BURN)
    q9_check = h_tot(s21, t21) - h_tot(s22, 453.15)
    print(f"F-501: adiabatic {t_ad:.0f} K from {t21:.1f} K (too cold to burn out); preheat to "
          f"{t_pre:.0f} K burns at {T_BURN:.0f} K; recuperator {q_rec:.0f} kW, flue gas to the "
          f"boiler at {t_boil:.0f} K; heat to the boiler and economiser {q9_check:.1f} kW "
          f"(core writes Q9)")

    # summary per kg of product
    prod = sum(s18.values())
    q2c = float(next(s for s in sheet["streams"] if s["id"] == "Q2")["state"]["design"]["duty"]["value"])
    q9c = float(next(s for s in sheet["streams"] if s["id"] == "Q9")["state"]["design"]["duty"]["value"])
    steam_out = q2c + q3 + q9c
    print(f"per kg MA: butane {sum(s1.values()) / prod:.4f} kg, power {(p1 + p2_kw + p3_kw + p4) / prod:.4f} kWh, "
          f"HP steam raised {steam_out / prod:.4f} kWh, HP steam used {(q4 + q7) / prod:.4f} kWh, "
          f"LP steam {q1 / prod:.4f} kWh, cooling water {(q10 + q5 + q6 + q8) / prod:.4f} kWh")

    out.pop("S5_t")
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
