"""Concept sizing and mass balance of lng-terminal-1 (DESIGN.md D-005 to D-012).

An independent model, outside cheme: core has no property package for LNG or boil-off gas
(DESIGN.md D-006), so the stream values of process/flowsheet.yaml are carried as `assumed`
with `source: scripts/terminal_sizing.py: ...`, and this script writes them under the
library's balance-output contract (docs/adr/0027) when BALANCE_OUTPUT names a file. Run with
`cheme run scripts/terminal_sizing.py`; it prints the sizing summary and writes nothing else.

Properties: CoolProp HEOS mixtures (Kunz-Wagner GERG-2008 departure functions for the
natural-gas pairs), the reference equation of state for natural gas; liquid states are
bubble-point states at the stated pressure, vapour states single-phase at T and P.

Inputs, each in DESIGN.md with its source or marked ASSUMED there:
- capacity 28 MTPA from 4 trains (LNG Canada Phase 1 + 2), availability 95 % (ASSUMED, D-003);
- feed gas composition of the EA application GHG technical data report (2014), the LNG
  derived from it: CO2, He and C5+ removed in the trains, N2 to 0.3 mol% (ASSUMED, D-004);
- tank pressure 115 kPa(a), boil-off 0.05 %/d of a full tank (ASSUMED, D-007);
- 2 x 225,000 m3 working (LNG Canada), loading 12,000 m3/h (EA application, D-008);
- line lengths from the site geometry (OSM/imagery measurements, D-013), insulation ASSUMED;
- ship return vapour, ship heat-in and pressures ASSUMED (D-009, D-010).
"""

import math

import CoolProp.CoolProp as CP

# --- components (flowsheet ids -> CoolProp names) -------------------------------------------
NAMES = {"CH4": "Methane", "C2H6": "Ethane", "C3H8": "Propane", "IC4": "IsoButane",
         "NC4": "n-Butane", "N2": "Nitrogen"}

# Feed gas, mol fraction, EA application GHG technical data report (2014), D-004
FEED = {"CH4": 0.9215, "C2H6": 0.0443, "C3H8": 0.0134, "IC4": 0.0021, "NC4": 0.0029,
        "N2": 0.0055}           # (+ iC5, nC5, C6, CO2, He removed in the trains)
LNG_N2 = 0.0030                 # ASSUMED: end flash leaves N2 at 0.3 mol% in the LNG (D-004)


def lng_composition():
    hc = {k: v for k, v in FEED.items() if k != "N2"}
    s = sum(hc.values())
    x = {k: v / s * (1.0 - LNG_N2) for k, v in hc.items()}
    x["N2"] = LNG_N2
    return x


def state(x):
    st = CP.AbstractState("HEOS", "&".join(NAMES[k] for k in x))
    st.set_mole_fractions(list(x.values()))
    return st


def bubble(x, p):
    st = state(x)
    st.update(CP.PQ_INPUTS, p, 0.0)
    y = dict(zip(x, st.mole_fractions_vapor()))
    return st.T(), st.rhomass(), st.hmass(), st.cpmass(), y


def vapour(y, p, t):
    st = state(y)
    st.update(CP.PT_INPUTS, p, t)
    return st.rhomass(), st.hmass(), st.cpmass(), st.molar_mass()


def molar_mass(x):
    return sum(v * CP.PropsSI("M", NAMES[k]) for k, v in x.items()) * 1000.0  # kg/kmol


def mass_fractions(x):
    m = {k: v * CP.PropsSI("M", NAMES[k]) for k, v in x.items()}
    s = sum(m.values())
    return {k: v / s for k, v in m.items()}


def pipe_heat_per_m(od, ins, k=0.025, t_in=-160.0, t_amb=5.0, factor=1.2):
    """Heat ingress W/m through cylindrical insulation; factor for supports and valves."""
    r1, r2 = od / 2, od / 2 + ins
    return factor * 2 * math.pi * k * (t_amb - t_in) / math.log(r2 / r1)


def dp_line(q_m3h, rho, d_in, length, mu=1.2e-4, rough=4.5e-5):
    """Darcy pressure drop, Pa (Swamee-Jain friction factor)."""
    v = q_m3h / 3600 / (math.pi / 4 * d_in ** 2)
    re = rho * v * d_in / mu
    f = 0.25 / math.log10(rough / (3.7 * d_in) + 5.74 / re ** 0.9) ** 2
    return f * length / d_in * rho * v ** 2 / 2, v


# --- basis -----------------------------------------------------------------------------------
P_TANK = 115e3                  # Pa(a), tank operating pressure, ASSUMED (D-007)
P_BOG_OUT = 600e3               # Pa(a), BOG at the battery limit (train end-flash/fuel), ASSUMED (D-010)
MTPA = 28.0                     # LNG Canada Phase 1 + 2 (D-003)
AVAILABILITY = 0.95             # ASSUMED (D-003)
TANK_WORKING = 225_000.0        # m3 each, 2 tanks (D-007)
BOR = 0.0005                    # 1/d of a full tank, ASSUMED (D-007)
Q_LOAD = 12_000.0               # m3/h, maximum loading rate (EA application, D-008)
T_RUNDOWN = -161.5              # degC, subcooled rundown from the trains, ASSUMED (D-005)
T_TANK_VAP = -150.0             # degC, tank vapour to the BOG header, ASSUMED (D-009)
T_SHIP_VAP = -120.0             # degC, ship return vapour at the jetty, ASSUMED (D-009)
T_BOG_SUCTION = -140.0          # degC, after the desuperheater, ASSUMED (D-010)
SHIP_HEAT_KW = 1500.0           # ship cargo tanks and piping heat-in while loading, ASSUMED (D-009)
L_LOADING = 2_450.0             # m per loading line, tank to arm base (D-013)
L_VAPOUR = 2_450.0              # m per vapour return line (D-013)
DN_LOAD, OD_LOAD, ID_LOAD = 800, 0.813, 0.787    # 2 loading lines (D-008)
DN_VAP, OD_VAP, ID_VAP = 750, 0.762, 0.743       # 2 vapour return lines (D-009)
INS_LOAD, INS_VAP = 0.20, 0.15                   # m PIR/PUF, ASSUMED (D-012)
DT_CIRC = 3.0                   # K allowed temperature rise in circulation, ASSUMED (D-008)
PUMP_RATED = 3_000.0            # m3/h per in-tank loading pump, ASSUMED: 4 run for 12,000 (D-011)
ETA_PUMP = 0.75                 # ASSUMED
ETA_COMP = 0.78                 # polytropic, ASSUMED
P_SHIP_MANIFOLD = 350e3         # Pa(a) needed at the ship manifold (spray headers, tank top), ASSUMED (D-011)
DZ_SHIP = 30.0                  # m, manifold above the low tank liquid level, ASSUMED (D-011)
# Pa, everything but the 2.45 km line friction, ASSUMED (D-011 as revised by D-034, review
# 2026-11-05-basic-design-7 #1): the governing line-up (T-3101 alone to Berth 1) of the recorded
# loading hydraulics in D-034 needs 834 kPa; besides the line friction above that is the pump column
# and check valve, the pump header at 12,000 m3/h, both crossovers, the expansion loops of the
# trestle, 25 kPa kept across the loading-line control valve, the strainer at its alarm, the berth
# header and the arm path (arm, swivels, ERS, coupler). Was 120 kPa for arms, ERS, strainers, valves.
DP_JETTY = 378e3


def main():
    x = lng_composition()
    t_b, rho_l, h_l, cp_l, y_bog = bubble(x, P_TANK)
    m_lng = molar_mass(x)
    m_bog = molar_mass(y_bog)
    h_vap_pure = (CP.PropsSI("H", "P", P_TANK, "Q", 1, "Methane")
                  - CP.PropsSI("H", "P", P_TANK, "Q", 0, "Methane"))   # J/kg latent, BOG basis
    rho_tv, h_tv, _, _ = vapour(y_bog, P_TANK, T_TANK_VAP + 273.15)
    rho_sv, h_sv, cp_sv, _ = vapour(y_bog, 106e3, T_SHIP_VAP + 273.15)

    # rundown (D-003, D-005)
    rundown_kgh = MTPA * 1e9 / (8760 * AVAILABILITY)
    rundown_m3h = rundown_kgh / rho_l

    # tank boil-off at holding (D-007)
    bog_tanks_kgh = 2 * TANK_WORKING * BOR * rho_l / 24.0

    # line heat ingress (D-012)
    q_load = pipe_heat_per_m(OD_LOAD, INS_LOAD) * L_LOADING * 2 / 1000      # kW, both lines
    q_vap = pipe_heat_per_m(OD_VAP, INS_VAP, t_in=-130.0) * L_VAPOUR * 2 / 1000

    # circulation: one small pump keeps both loading lines cold (EA application, D-008)
    circ_kgh = q_load * 1000 / (cp_l * DT_CIRC) * 3600
    circ_m3h = circ_kgh / rho_l

    # loading hydraulics, per line 6,000 m3/h (D-011)
    dp_l, v_l = dp_line(Q_LOAD / 2, rho_l, ID_LOAD, L_LOADING)
    dp_pump = (P_SHIP_MANIFOLD - P_TANK) + rho_l * 9.81 * DZ_SHIP + dp_l + DP_JETTY
    head = dp_pump / (rho_l * 9.81)
    n_pumps = math.ceil(Q_LOAD / PUMP_RATED)
    p_pump_kw = Q_LOAD / 3600 * dp_pump / ETA_PUMP / 1000          # all loading pumps
    p_circ_kw = circ_m3h / 3600 * (dp_l * (circ_m3h / (Q_LOAD / 2)) ** 2 * 2 + 150e3) / 0.6 / 1000

    # --- holding: rundown fills the tanks, nothing loaded (D-009) --------------------------
    flash_hold = (q_load + p_circ_kw) * 1000 / h_vap_pure * 3600    # kg/h flashed in the tank
    displaced_hold = rundown_m3h * rho_tv                           # tank vapour pushed out by filling
    bog_hold = bog_tanks_kgh + flash_hold + displaced_hold
    fill_hold = rundown_kgh - bog_hold                              # tank inventory gain
    # rundown is subcooled: its sensible heat to the bubble point condenses part of the BOG
    # (credited conservatively as nil, D-005)

    # --- loading one ship at 12,000 m3/h while the rundown continues (D-009) -------------
    load_kgh = Q_LOAD * rho_l
    pump_heat_kgh = p_pump_kw * 1000 / h_vap_pure * 3600            # pump work ends as flash
    line_flash_kgh = q_load * 1000 / h_vap_pure * 3600
    ship_flash_kgh = SHIP_HEAT_KW * 1000 / h_vap_pure * 3600
    ship_return_kgh = Q_LOAD * rho_sv + ship_flash_kgh + 0.85 * (pump_heat_kgh + line_flash_kgh)
    # 85 % of the pump and line heat flashes on board (the LNG arrives warmer), 15 % in the tank
    tank_absorbs_kgh = (Q_LOAD - rundown_m3h) * rho_tv              # vapour space growing
    bog_tank_load = max(0.0, bog_tanks_kgh + 0.15 * (pump_heat_kgh + line_flash_kgh)
                        - tank_absorbs_kgh)
    # vapour return is cooled by an LNG spray to the compressor suction (D-010)
    rho_bs, h_bs, _, _ = vapour(y_bog, 108e3, T_BOG_SUCTION + 273.15)
    spray_kgh = ship_return_kgh * (h_sv - h_bs) / (h_bs - h_l)
    bog_load = bog_tank_load + ship_return_kgh + spray_kgh
    draw_load = load_kgh + spray_kgh + bog_tank_load - rundown_kgh   # tank inventory loss

    # --- annual average: loading fraction that keeps the inventory steady (D-009) ----------
    # f * draw_load = (1 - f) * fill_hold, and the cargo delivered is f * load_kgh
    f_load = fill_hold / (fill_hold + draw_load)
    avg = {k: f_load * a + (1 - f_load) * b for k, a, b in [
        ("load", load_kgh, 0.0), ("ship_return", ship_return_kgh, 0.0),
        ("spray", spray_kgh, 0.0), ("bog_tank", bog_tank_load, bog_hold),
        ("bog_out", bog_load, bog_hold), ("circ", 0.0, circ_kgh)]}
    net_cargo_tpa = (avg["load"] - avg["ship_return"]) * 8760 * AVAILABILITY / 1e9

    # BOG compressors: 3 x 50 % of the loading case with 10 % margin (D-010)
    k_design_kgh = 1.1 * max(bog_load, bog_hold)
    k_each = k_design_kgh / 2
    cp_v = 2.05e3                                                   # J/kg K methane-rich vapour
    gam = 1.31
    r = P_BOG_OUT / 108e3
    t_s = T_BOG_SUCTION + 273.15
    n_exp = (gam - 1) / (gam * ETA_COMP)
    t_d = t_s * r ** n_exp
    p_comp_kw = k_each / 3600 * cp_v * (t_d - t_s) / 1000

    # trestle line velocities
    v_vap = (ship_return_kgh + spray_kgh) / 2 / rho_bs / 3600 / (math.pi / 4 * ID_VAP ** 2)

    # surge on an ESD closure of the loading line (D-023): wave speed of LNG in a thin-walled
    # steel pipe ~1,150 m/s (ASSUMED); a closure slower than the line period 2L/a gives the
    # slow-closure estimate dP ~ 2 rho L v / t_close (Michaud), the instant one rho a v
    a_wave, t_close = 1150.0, 25.0                                  # m/s, s (ASSUMED)
    period = 2 * L_LOADING / a_wave
    dp_instant = rho_l * a_wave * v_l
    dp_slow = 2 * rho_l * L_LOADING * v_l / t_close
    p_surge = P_TANK + dp_pump + dp_slow
    # vapour arm (D-023): one 16 inch arm (ID ~0.381 m) at a 40 m/s limit (ASSUMED)
    arm_area = math.pi / 4 * 0.381 ** 2
    arm_cap_kgh = 40.0 * arm_area * rho_sv * 3600

    rows = [
        ("LNG composition (mol)", {k: round(v, 5) for k, v in x.items()}),
        ("LNG molar mass, kg/kmol", round(m_lng, 3)),
        ("bubble point at 115 kPa(a), degC", round(t_b - 273.15, 2)),
        ("LNG density, kg/m3", round(rho_l, 1)),
        ("BOG incipient vapour (mol)", {k: round(v, 5) for k, v in y_bog.items() if v > 1e-6}),
        ("BOG molar mass, kg/kmol", round(m_bog, 3)),
        ("latent heat (methane), kJ/kg", round(h_vap_pure / 1000, 1)),
        ("tank vapour density -150 C, kg/m3", round(rho_tv, 3)),
        ("ship return vapour density -120 C, kg/m3", round(rho_sv, 3)),
        ("rundown, t/h", round(rundown_kgh / 1000, 1)),
        ("rundown, m3/h", round(rundown_m3h)),
        ("tank boil-off both tanks, t/h", round(bog_tanks_kgh / 1000, 2)),
        ("heat ingress loading lines, kW", round(q_load)),
        ("heat ingress vapour lines, kW", round(q_vap)),
        ("circulation flow, m3/h", round(circ_m3h)),
        ("circulation pump power, kW", round(p_circ_kw)),
        ("loading line velocity, m/s", round(v_l, 2)),
        ("loading line dp per line, kPa", round(dp_l / 1000)),
        ("pump differential, kPa / head, m", (round(dp_pump / 1000), round(head))),
        ("loading pumps running", n_pumps),
        ("loading pump power all, kW", round(p_pump_kw)),
        ("holding BOG, t/h (tanks, flash, displaced)",
         (round(bog_hold / 1000, 2), round(bog_tanks_kgh / 1000, 2), round(flash_hold / 1000, 2),
          round(displaced_hold / 1000, 2))),
        ("loading: ship return, spray, tank BOG, total, t/h",
         (round(ship_return_kgh / 1000, 2), round(spray_kgh / 1000, 2),
          round(bog_tank_load / 1000, 2), round(bog_load / 1000, 2))),
        ("vapour return velocity per line, m/s", round(v_vap, 1)),
        ("loading fraction of time (annual)", round(f_load, 3)),
        ("net cargo, Mt/a", round(net_cargo_tpa, 2)),
        ("BOG compressor each (3 x 50 %), t/h", round(k_each / 1000, 1)),
        ("BOG compressor discharge, degC / power each, kW", (round(t_d - 273.15, 1), round(p_comp_kw))),
        ("surge: line period 2L/a, s / closure, s", (round(period, 1), t_close)),
        ("surge: instant / slow-closure dP, kPa", (round(dp_instant / 1000), round(dp_slow / 1000))),
        ("surge: peak pressure at the ESD valve, kPa(a) / barg", (round(p_surge / 1000), round((p_surge - 101.3e3) / 1e5, 1))),
        ("vapour arm capacity at 40 m/s, t/h", round(arm_cap_kgh / 1000, 1)),
    ]
    for k, v in rows:
        print(f"{k:52s} {v}")

    # --- the values process/flowsheet.yaml cites (balance-output/1) ------------------------
    wl = mass_fractions(x)
    wv = mass_fractions(y_bog)
    p_dis = P_TANK + dp_pump
    t_l, t_rd = round(t_b, 2), round(T_RUNDOWN + 273.15, 2)

    def rounded(comp, digits=5):
        """Mass fractions rounded so that they still sum to exactly 1 (methane takes the rest)."""
        r = {k: round(v, digits) for k, v in comp.items() if k != "CH4"}
        return {"CH4": round(1.0 - sum(r.values()), digits)} | r

    def s(flow, t, p, comp):
        return {"flow": {"value": round(flow, 1), "basis": "mass"}, "temperature": t,
                "pressure": round(p / 1000, 1),
                "composition": {"values": rounded(comp), "basis": "mass_fraction"}}

    kw_per_kgh_comp = p_comp_kw / k_each                           # same pressure ratio at any flow
    ETA_MOTOR = 0.95                                               # ASSUMED

    def case(load, ship_ret, spray, bog_tank, bog_out, circ, draw, fill, hold_frac):
        # The tank liquid weathers: the N2-rich boil-off leaves it slightly heavier than the
        # rundown. Every liquid leaving the tanks (and the inventory change) carries the
        # weathered composition w, from the component balance of the tanks (D-009).
        w = {k: (rundown_kgh * wl[k] - bog_tank * wv[k]) / (rundown_kgh - bog_tank) for k in wl}
        # S9 mixes the vapours with the evaporated LNG spray (component balance of BOG)
        w9 = {k: ((bog_tank + ship_ret) * wv[k] + spray * w[k]) / bog_out if bog_out else wv[k]
              for k in wl}
        e_pumps = ((1 - hold_frac) * p_pump_kw + hold_frac * p_circ_kw) / ETA_MOTOR
        e_comp = bog_out * kw_per_kgh_comp / ETA_MOTOR
        tail = {"S13": s(load + circ + spray, t_l, P_TANK, w),        # tank liquid to the pumps
                "S14": s(bog_out, T_BOG_SUCTION + 273.15, 108e3, w9),  # BOG after the desuperheater
                "E1": {"duty": round(e_pumps, 1)}, "E2": {"duty": round(e_comp, 1)}}
        return tail | {
            "S1": s(rundown_kgh, t_rd, P_TANK + 100e3, wl),        # rundown from the trains
            "S2": s(load + circ, t_l, p_dis, w),                   # pumped LNG to the trestle
            "S3": s(load, t_l, p_dis - dp_l, w),                   # LNG at the jetty
            "S4": s(load, t_l, P_SHIP_MANIFOLD, w),                # LNG to the ship
            "S5": s(ship_ret, T_SHIP_VAP + 273.15, 106e3, wv),     # ship return vapour
            "S6": s(ship_ret, T_SHIP_VAP + 273.15, 104e3, wv),     # vapour return over the trestle
            "S7": s(spray, t_l, p_dis, w),                         # desuperheater spray
            "S8": s(bog_tank, T_TANK_VAP + 273.15, P_TANK, wv),    # tank boil-off
            "S9": s(bog_out, round(t_d, 2), P_BOG_OUT, w9),        # BOG to the trains
            "S10": s(circ, t_l + DT_CIRC, P_TANK + 150e3, w),      # circulation return
            "S11": s(draw, t_l, P_TANK, w),                        # tank inventory drawn down
            "S12": s(fill, t_l, P_TANK, w),                        # tank inventory filled up
        }

    cases = {
        "average": case(avg["load"], avg["ship_return"], avg["spray"], avg["bog_tank"],
                        avg["bog_out"], avg["circ"], 0.0, 0.0, 1 - f_load),
        "loading": case(load_kgh, ship_return_kgh, spray_kgh, bog_tank_load, bog_load, 0.0,
                        draw_load, 0.0, 0.0),
        "holding": case(0.0, 0.0, 0.0, bog_hold, bog_hold, circ_kgh, 0.0, fill_hold, 1.0),
    }
    write_balance_output(cases)
    return cases


def write_balance_output(cases):
    """With BALANCE_OUTPUT set, write the values the flowsheet cites from this script as JSON.

    The process library's balance-output contract (docs/adr/0027 of the library): case ->
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
