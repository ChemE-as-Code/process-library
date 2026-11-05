"""Draft of a berth sheet (P-05: Berth 2, as built; P-06: Berth 1, Phase 2): the platform
liquid header with the shore ESD valve, strainer and surge relief, the four 16 inch arms (two
liquid, one hybrid, one vapour) with their emergency release systems, the vapour line to the
trestle, the jetty drain drum and pump, and the N2 purge.

Provenance only: the sheets are hand-maintained after this first revision. Run:
cheme run scripts/draft_berth.py pid/P-05.xml 5   (or pid/P-06.xml 6), on the empty A3 frame.
Arm arrangement and procedures from the LNG Canada Terminal Information Guide (S-01): south to
north liquid, vapour, hybrid, liquid; vapour arm connected first; N2 leak test 5 / 2.5 bar.
Decisions D-014, D-016, D-017, D-021. The sheet draws the arms left to right L1, L2, H, V (the
platform order is in the note) so that the vapour line leaves the sheet without crossings.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lng_pid import (  # noqa: E402
    Lists, Nozzle, Sheet, arm_shape, equipment, note, offpage, set_dn, tee, valve)

target, n = Path(sys.argv[1]), sys.argv[2]
berth, line_in, vap_out = ("2", "LNG-4001", "BOG-4001") if n == "5" else ("1", "LNG-4002", "BOG-4002")
sheet = Sheet.load(target)
L = Lists(f"P-0{n}")
UP, DOWN, LEFT = 270, 90, 180
HDR_Y, ARM_Y, SC = 190, 100, 2.0
X = {"1": 110, "4": 170, "3": 230, "2": 290}      # LA-n101 L1, LA-n104 L2, LA-n103 H, LA-n102 V
KIND = {"1": "liquid", "4": "liquid", "3": "hybrid", "2": "vapour"}

arms = {}
for k, x in X.items():
    arms[k] = equipment(sheet, "LoadingUnloadingSystem", f"LA-{n}10{k}", shape=arm_shape(sheet),
                        at=(x, ARM_Y), scale=SC,
                        nozzles=[Nozzle("N1", (0, 28), 400), Nozzle("N2", (32, 16), 400)],
                        label_at=(x - 2, 66))

# ---- liquid header: shore ESD valve, strainer, surge relief, N2, drain --------------------
t_srg = tee(f"T{n}0S", at=(70, HDR_Y), branch="down", branch_dn=150)
t_n2 = tee(f"T{n}0N", at=(85, HDR_Y), branch="up", branch_dn=80 if n == "5" else 50)
t_dr = tee(f"T{n}0D", at=(98, HDR_Y), branch="down", branch_dn=100)
t_l1 = tee(f"T{n}01", at=(X["1"], HDR_Y), branch="up", branch_dn=400)
t_l2 = tee(f"T{n}04", at=(X["4"], HDR_Y), branch="up", branch_dn=400)
xv_esd = valve(f"XV{n}101", "BallValve", tag=f"XV-{n}101", at=(28, HDR_Y))
hdr = L.line(sheet, f"LNG-{n}001", dn=800, fluid="LNG", frm=line_in, to=f"LA-{n}103",
             notes=f"Berth {berth} liquid header on the loading platform, 12,000 m3/h at loading (S3); shore ESD valve XV-{n}101 and strainer SR-{n}102 (S-01: shore strainers; D-016).",
             route=[offpage("in", at=(12, HDR_Y), note=f"from {line_in} (P-04)", note_at=(24, HDR_Y + 7)), xv_esd,
                    valve(f"SR{n}102", "ConicalStrainer", tag=f"SR-{n}102", at=(46, HDR_Y)), t_srg, t_n2,
                    t_dr, t_l1, t_l2, (X["3"], HDR_Y),
                    valve(f"XV{n}123", "BallValve", tag=f"XV-{n}123", at=(X["3"], 181)),
                    tee(f"T{n}0H", at=(X["3"], 172), branch="right", branch_dn=400), arms["3"]["N1"]],
             label_at=(192, HDR_Y + 8),
             segments=[{"number": "S6", "nominal_diameter": "DN400", "notes": "to the hybrid arm, after the LA-n104 tee"},
                       {"number": "S7", "nominal_diameter": "DN400", "notes": "hybrid arm connection"}])
set_dn(sheet, [f"T{n}04_N2", f"XV{n}123_N1", f"XV{n}123_N2", f"T{n}0H_N1", f"T{n}0H_N2"], 400,
       segments=[f"Line_LNG{n}001_S6", f"Line_LNG{n}001_S7"])
for k, tt in [("1", t_l1), ("4", t_l2)]:
    L.line(sheet, f"LNG-{n}00{'2' if k == '1' else '3'}", dn=400, fluid="LNG", frm=f"LNG-{n}001",
           to=f"LA-{n}10{k}", notes=f"Liquid arm LA-{n}10{k} shore connection with its isolation valve.",
           route=[tt.branch, valve(f"XV{n}12{k}", "BallValve", tag=f"XV-{n}12{k}", at=(X[k], 168)),
                  arms[k]["N1"]],
           label_at=(X[k] - 12, 150))

# ---- vapour arm, hybrid vapour connection, vapour line to the trestle ---------------------------
t_vh = tee(f"T{n}0V", at=(X["2"], 172), branch="left", branch_dn=400)
t_vd = tee(f"T{n}0W", at=(330, 182), branch="down", branch_dn=100)
vap = L.line(sheet, f"BOG-{n}001", dn=400, fluid="Boil-off gas", frm=f"LA-{n}102", to=vap_out,
             notes=f"Berth {berth} vapour line from the vapour arm (and the hybrid arm) to vapour return line {'A' if n == '5' else 'B'}; 45.6 t/h at loading (S5/S6) is ~70 m/s in one 16 inch arm, so the hybrid arm is the second vapour path at high return (D-014).",
             route=[arms["2"]["N1"], valve(f"XV{n}122", "BallValve", tag=f"XV-{n}122", at=(X["2"], 150)),
                    t_vh, (X["2"], 182), t_vd,
                    offpage("out", at=(405, 182), note=f"to {vap_out} (P-04)", note_at=(388, 176))],
             label_at=(370, 190))
L.line(sheet, f"BOG-{n}003", dn=400, fluid="Boil-off gas", frm=f"LA-{n}103", to=f"BOG-{n}001",
       notes="Hybrid arm to the vapour line (hybrid used as a vapour arm).",
       route=[f"T{n}0H:T{n}0H_N3", valve(f"XV{n}125", "BallValve", tag=f"XV-{n}125", at=(258, 172)),
              t_vh.branch], labels=False)

# ---- ship side: emergency release system (two ball valves around the coupler) ------------------
for k, x in X.items():
    sx = x + 32
    ers = [valve(f"XV{n}13{k}", "BallValve", tag=f"XV-{n}13{k}", at=(sx, 125)),
           valve(f"XV{n}14{k}", "BallValve", tag=f"XV-{n}14{k}", at=(sx, 140))]
    if KIND[k] == "vapour":
        L.line(sheet, f"BOG-{n}01{k}", dn=400, fluid="Boil-off gas", frm="carrier vapour manifold",
               to=f"LA-{n}10{k}", notes="Vapour arm outboard: carrier manifold, ERS (XV-%s14%s, coupler, XV-%s13%s), arm." % (n, k, n, k),
               route=[offpage("in", at=(sx, 156), note="from carrier", note_at=(sx + 13, 160), rotation=UP),
                      *ers[::-1], arms[k]["N2"]], labels=False)
    else:
        L.line(sheet, f"LNG-{n}01{k}", dn=400, fluid="LNG", frm=f"LA-{n}10{k}", to="carrier manifold",
               notes=f"{KIND[k].capitalize()} arm outboard: arm, ERS (XV-{n}13{k}, emergency release coupler, XV-{n}14{k}), quick connect/disconnect coupler, carrier manifold (D-014).",
               route=[arms[k]["N2"], *ers,
                      offpage("out", at=(sx, 156), note="to carrier", note_at=(sx + 11, 160), rotation=DOWN)],
               labels=False)
    for v, y in [(f"XV{n}13{k}", 125), (f"XV{n}14{k}", 140)]:
        L.inst(sheet, f"UZ-{v[2:]}", f"LA-{n}10{k} ERS valve XV-{v[2:]}",
               f"Closes on ESD-1 / ESD-2 (C&E I-{n}01, I-{n}03); ESD-2 then releases the coupler (D-016).",
               at=(sx + 13, y), signal_to=v, fail_action="FC")
    L.inst(sheet, f"ZS-{n}15{k}", f"LA-{n}10{k} envelope monitoring (position of the outboard arm)",
           f"Pre-alarm, ESD-1, ESD-2 (C&E I-{n}03).", at=(x + 8, 56))

# ---- N2 purge and leak test, surge relief, drains, drain drum and pump -------------------------
L.line(sheet, "N-8001" if n == "5" else "N-8002", dn=80 if n == "5" else 50, fluid="Nitrogen",
       frm="BL (site N2)" if n == "5" else "N-8001", to=f"LNG-{n}001",
       insulation="none", pclass="Class 150",
       notes="see P-08",
       route=[offpage("in", at=(12, 160), note="N2 (P-08)", note_at=(16, 154)),
              valve(f"HV{n}151", "BallValve", tag=f"HV-{n}151", at=(32, 160)),
              valve(f"CV{n}151", "SwingCheckValve", at=(55, 160)), (85, 160), t_n2.branch],
       label_at=(55, 168))
drum = equipment(sheet, "PressureVessel", f"D-{n}101", shape="VESSEL_WITH_DISHED_HEADS_SHAPE",
                 at=(180, 235), rotation=90,
                 nozzles=[Nozzle("N1", (-10, -10), 100), Nozzle("N2", (10, -10), 100),
                          Nozzle("N3", (15, 0), 100), Nozzle("N4", (-15, 0), 50)],
                 label_at=(180, 251))
pump = equipment(sheet, "CentrifugalPump", f"P-{n}101", shape="CENTRIFUGAL_PUMP_SHAPE", at=(225, 245),
                 nozzles=[Nozzle("N1", (-7.5, 0), 100), Nozzle("N2", (0, -7.5), 80)], label_at=(240, 250))
t_ps = tee(f"T{n}0P", at=(98, 208), branch="left", branch_dn=150)
L.line(sheet, f"DR-{n}001", dn=100, fluid="LNG", frm=f"LNG-{n}001", to=f"D-{n}101",
       notes="Header and arm drain to the jetty drain drum after loading; receives the surge relief (D-016).",
       route=[t_dr.branch, t_ps, (98, 216), (170, 216), drum["N1"]], label_at=(135, 211))
psv = L.relief(f"PSV{n}131", f"PSV-{n}131", f"DR-{n}002", 15.5,
               "surge on an ESD closure at the full loading rate; thermal expansion of the blocked-in header",
               f"Surge relief of the Berth {berth} header into D-{n}101 (D-016); size from the surge analysis in detail engineering.")
L.line(sheet, f"DR-{n}002", dn=150, fluid="LNG", frm=f"LNG-{n}001 (PSV-{n}131)", to=f"DR-{n}001",
       notes=f"Surge relief discharge of PSV-{n}131 into the drain line.",
       route=[t_srg.branch, psv, (70, 208), t_ps.branch], labels=False)
L.line(sheet, f"BOG-{n}002", dn=100, fluid="Boil-off gas", frm=f"D-{n}101", to=f"BOG-{n}001",
       notes="Drain drum vent to the vapour line.",
       route=[drum["N2"], (190, 210), (330, 210), t_vd.branch], label_at=(300, 204))
L.line(sheet, f"LNG-{n}005", dn=100, fluid="LNG", frm=f"D-{n}101", to=f"P-{n}101",
       notes="Drain pump suction.", route=[drum["N3"], (205, 235), (205, 245), pump["N1"]], labels=False)
L.line(sheet, f"LNG-{n}006", dn=80, fluid="LNG", frm=f"P-{n}101", to="LNG-4003",
       notes="Drain pump discharge into the platform crossover / circulation (P-04), ~60 m3/h.",
       route=[pump["N2"], (225, 230), (380, 230),
              offpage("out", at=(405, 230), note="to LNG-4003 (P-04)", note_at=(390, 224))],
       label_at=(300, 236))

# ---- instruments --------------------------------------------------------------------------
L.inst(sheet, f"UZ-{n}101", f"Berth {berth} shore ESD valve XV-{n}101",
       f"ESD-1 closes with the closure time set against surge (C&E I-{n}01, D-016).",
       at=(28, 178), signal_to=xv_esd, fail_action="FC")
L.inst(sheet, f"PDI-{n}102", f"Strainer SR-{n}102 differential pressure", at=(46, 202),
       sensing=hdr.segments[0], sensing_at=(52, HDR_Y))
L.inst(sheet, f"PZT-{n}103", f"Berth {berth} header pressure (high back-pressure)",
       f"High-high back-pressure at the shore manifold stops the loading (S-01; C&E I-{n}02).",
       at=(124, 202), sensing=hdr.segments[-2] if len(hdr.segments) > 2 else hdr.segments[0],
       sensing_at=(124, HDR_Y))
L.inst(sheet, f"TI-{n}104", f"Berth {berth} header temperature (cooldown)", at=(146, 202),
       sensing=hdr.segments[-2] if len(hdr.segments) > 2 else hdr.segments[0], sensing_at=(146, HDR_Y))
L.inst(sheet, f"HS-{n}121", f"LA-{n}101 isolation XV-{n}121", at=(X["1"] - 15, 168),
       signal_to=f"XV{n}121", fail_action="FC")
L.inst(sheet, f"HS-{n}124", f"LA-{n}104 isolation XV-{n}124", at=(X["4"] - 15, 168),
       signal_to=f"XV{n}124", fail_action="FC")
L.inst(sheet, f"HS-{n}123", f"LA-{n}103 liquid isolation XV-{n}123", at=(X["3"] - 15, 181),
       signal_to=f"XV{n}123", fail_action="FC")
L.inst(sheet, f"HS-{n}125", f"LA-{n}103 vapour isolation XV-{n}125 (hybrid as vapour arm)",
       at=(258, 184), signal_to=f"XV{n}125", fail_action="FC")
L.inst(sheet, f"HS-{n}122", f"LA-{n}102 vapour arm isolation XV-{n}122", at=(X["2"] + 15, 150),
       signal_to=f"XV{n}122", fail_action="FC")
L.inst(sheet, f"XS-{n}100", f"Berth {berth} ship-shore ESD link",
       f"Fibre-optic link (S-01): ESD-1 both ways (C&E I-{n}01).", at=(40, 56))
L.inst(sheet, f"PI-{n}105", f"Berth {berth} vapour line pressure", at=(352, 170),
       sensing=vap.segments[-1], sensing_at=(352, 182))
L.inst(sheet, f"TI-{n}106", f"Berth {berth} vapour line temperature", at=(374, 170),
       sensing=vap.segments[-1], sensing_at=(374, 182))
L.inst(sheet, f"LIC-{n}111", f"Jetty drain drum D-{n}101 level",
       f"Starts and stops P-{n}101; high-high level alarm (D-016).", at=(150, 240), sensing=drum["N4"])

note(sheet, f"Berth {berth} arms on the platform, south to north: LA-{n}101 liquid, LA-{n}102 vapour, LA-{n}103 hybrid, LA-{n}104 liquid", at=(12, 258))
note(sheet, "(S-01); drawn left to right L, L, H, V. 16 inch, ~4,000 m3/h per liquid arm; the hybrid runs as the third liquid arm (D-014).", at=(12, 264))
note(sheet, f"ERS per arm: two ball valves either side of the emergency release coupler. UZ: see C&E I-{n}01 (ESD-1), I-{n}03 (ESD-2).", at=(12, 270))
note(sheet, f"Vapour arm connected first and disconnected last (S-01). BOG-{n}003, DR-{n}002, LNG-{n}005: see the line list.", at=(12, 276))

L.finish(sheet, target)
