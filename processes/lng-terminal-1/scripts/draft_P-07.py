"""Draft of P-07: BOG desuperheater and suction drum D-7101, the BOG compressors K-7101A/B/C
(3 x 50 %) with their suction ESD valves, anti-surge recycles and discharge check valves, the
discharge header to the trains with the make-up take-off, relief to the flare and the drum drain.

Provenance only: P-07 is hand-maintained after this first revision. Run:
cheme run scripts/draft_P-07.py pid/P-07.xml (on the empty A3 frame).
Streams S7, S8, S9, S14; decisions D-010, D-017, D-021.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lng_pid import Lists, Nozzle, Sheet, equipment, note, offpage, set_dn, tee, valve  # noqa: E402

target = Path(sys.argv[1])
sheet = Sheet.load(target)
L = Lists("P-07")
UP, DOWN = 270, 90
HDR_Y, K_Y, DIS_Y, REC_Y = 60, 130, 185, 160
KX = {"A": 170, "B": 250, "C": 330}             # compressor centres
SX = {k: x - 20 for k, x in KX.items()}         # suction branch x
DX = {k: x + 30 for k, x in KX.items()}         # discharge leg x

drum = equipment(sheet, "PressureVessel", "D-7101", shape="VESSEL_WITH_DISHED_HEADS_SHAPE",
                 at=(90, 140), scale=(1.2, 1.6),
                 nozzles=[Nozzle("N1", (-12, -12), 750), Nozzle("N2", (0, -24), 750),
                          Nozzle("N3", (0, 24), 50), Nozzle("N4", (-12, 10), 50), Nozzle("N5", (-12, 18), 50)],
                 label_at=(112, 140))
k = {s: equipment(sheet, "CentrifugalCompressor", f"K-7101{s}", shape="COMPRESSOR_CENTRIFUGAL_SHAPE",
                  at=(x, K_Y), scale=1.5,
                  nozzles=[Nozzle("N1", (-11.25, 0), 500), Nozzle("N2", (11.25, 0), 300)],
                  label_at=(x, 148)) for s, x in KX.items()}

# ---- inlet: relief tee, spray desuperheater, suction drum ---------------------------------------
t_psv = tee("T7P1", at=(30, 120), branch="up", branch_dn=200)
t_spr = tee("T7S1", at=(50, 120), branch="up", branch_dn=80)
inlet = L.line(sheet, "BOG-1001", dn=750, fluid="Boil-off gas", frm="T-2101", to="D-7101",
               notes="see P-01",
               route=[offpage("in", at=(12, 120), note="from P-01", note_at=(19, 113)), t_psv, t_spr,
                      (66, 120), (66, 128), drum["N1"]],
               label_at=(38, 128))
tv = valve("TV7103", "GlobeValve", tag="TV-7103", at=(50, 80))
L.line(sheet, "LNG-4008", dn=80, fluid="LNG", frm="LNG-2002", to="BOG-1001 (TV-7103)",
       notes="see P-04",
       route=[offpage("in", at=(50, 40), note="spray from P-04", note_at=(64, 36), rotation=DOWN),
              tv, t_spr.branch], label_at=(62, 58))
psv5 = L.relief("PSV7105", "PSV-7105", "FL-7001", 2.5,
                "blocked outlet of D-7101 (compressors tripped, flare valve PV-1110 failed closed); fire on D-7101",
                "D-7101 / suction system relief to the storage and loading flare (D-017). Set ASSUMED.")
L.line(sheet, "FL-7001", dn=200, fluid="Flare gas", frm="BOG-1001 (PSV-7105)", to="FL-8001",
       notes="PSV-7105 outlet to the storage and loading flare header. Drawn on P-07 and P-08.", insulation="none",
       route=[t_psv.branch, psv5, offpage("out", at=(30, 78), note="to flare (P-08)", note_at=(24, 72), rotation=UP)],
       labels=False)

# ---- suction header and branches -----------------------------------------------------------------
tsa = tee("T7HA", at=(SX["A"], HDR_Y), branch="down", branch_dn=500)
tsb = tee("T7HB", at=(SX["B"], HDR_Y), branch="down", branch_dn=500)
rec_t = {s: tee(f"T7R{s}", at=(SX[s], 100), branch="left", branch_dn=250) for s in KX}
xv = {s: valve(f"XV7121{s}", "BallValve", tag=f"XV-7121{s}", at=(SX[s], 80)) for s in KX}
suct = L.line(sheet, "BOG-7001", dn=750, fluid="Boil-off gas", frm="D-7101", to="K-7101C",
              notes="Compressor suction header, 49.1 t/h at loading, -140 degC, 108 kPa(a) (S14, D-010); ends as the K-7101C suction.",
              segments=[{"number": "S3", "nominal_diameter": "DN500", "notes": "K-7101C suction branch"},
                        {"number": "S4", "nominal_diameter": "DN500", "notes": "K-7101C suction after the recycle tee"}],
              route=[drum["N2"], (90, HDR_Y), tsa, tsb, (SX["C"], HDR_Y), xv["C"], rec_t["C"], (SX["C"], K_Y),
                     k["C"]["N1"]],
              label_at=(138, HDR_Y - 8))
set_dn(sheet, ["T7HB_N2", "XV7121C_N1", "XV7121C_N2", "T7RC_N1", "T7RC_N2"], 500,
       segments=["Line_BOG7001_S3", "Line_BOG7001_S4"])
for s, tt in [("A", tsa), ("B", tsb)]:
    L.line(sheet, f"BOG-700{4 if s == 'A' else 5}", dn=500, fluid="Boil-off gas", frm="BOG-7001",
           to=f"K-7101{s}", notes=f"K-7101{s} suction, 27 t/h design (D-010).",
           route=[tt.branch, xv[s], rec_t[s], (SX[s], K_Y), k[s]["N1"]], label_at=(SX[s] - 12, 90))

# ---- discharge header, make-up take-off, relief -----------------------------------------------
t_mu = tee("T7MU", at=(220, DIS_Y), branch="down", branch_dn=150)
tdb = tee("T7DB", at=(DX["B"], DIS_Y), branch="up", branch_dn=300)
tdc = tee("T7DC", at=(DX["C"], DIS_Y), branch="up", branch_dn=300)
t_dp = tee("T7DP", at=(378, DIS_Y), branch="up", branch_dn=200)
rec_d = {s: tee(f"T7Q{s}", at=(DX[s], REC_Y), branch="left", branch_dn=250) for s in KX}
cv = {s: valve(f"CV7122{s}", "SwingCheckValve", at=(KX[s] + 20, K_Y)) for s in KX}
dis = L.line(sheet, "BOG-7002", dn=500, fluid="Boil-off gas", frm="K-7101A", to="BL (trains)",
             notes="Compressed BOG to the trains' end-flash / fuel gas system, 600 kPa(a), about -49 degC (S9, D-010); segment S1 is the DN 300 discharge of K-7101A, where the header starts.",
             segments=[{"number": "S1", "nominal_diameter": "DN300", "notes": "K-7101A discharge"},
                       {"number": "S2", "nominal_diameter": "DN300", "notes": "K-7101A discharge after the recycle tee"}],
             route=[k["A"]["N2"], cv["A"], (DX["A"], K_Y), rec_d["A"], (DX["A"], DIS_Y), t_mu, tdb, tdc, t_dp,
                    offpage("out", at=(405, DIS_Y), note="to trains (BL)", note_at=(394, DIS_Y + 6))],
             label_at=(258, DIS_Y + 9))
set_dn(sheet, ["CV7122A_N1", "CV7122A_N2", "T7QA_N1", "T7QA_N2", "T7MU_N1"], 300,
       segments=["Line_BOG7002_S1", "Line_BOG7002_S2"])
for s, tt in [("B", tdb), ("C", tdc)]:
    L.line(sheet, f"BOG-700{6 if s == 'B' else 7}", dn=300, fluid="Boil-off gas", frm=f"K-7101{s}",
           to="BOG-7002", notes=f"K-7101{s} discharge.",
           route=[k[s]["N2"], cv[s], (DX[s], K_Y), rec_d[s], tt.branch], labels=False)
uv = {}
for s in KX:
    uv[s] = valve(f"UV7104{s}", "GlobeValve", tag=f"UV-7104{s}", at=(KX[s], REC_Y))
    L.line(sheet, f"BOG-70{8 + 'ABC'.index(s):02d}", dn=250, fluid="Boil-off gas", frm=f"K-7101{s} discharge",
           to=f"K-7101{s} suction", notes=f"K-7101{s} anti-surge recycle (UV-7104{s}) to its suction downstream of the drum (D-010).",
           route=[rec_d[s].branch, uv[s], (SX[s] - 10, REC_Y), (SX[s] - 10, 100), rec_t[s].branch],
           labels=False)
L.line(sheet, "BOG-1009", dn=150, fluid="Boil-off gas", frm="BOG-7002", to="BOG-1001",
       notes="see P-01",
       route=[t_mu.branch, offpage("out", at=(220, 215), note="make-up (P-01)", note_at=(238, 220), rotation=DOWN)],
       label_at=(208, 204))
psv11 = L.relief("PSV7111", "PSV-7111", "FL-7002", 7.5,
                 "blocked outlet of the discharge header with the compressors running (train fuel system tripped)",
                 "BOG discharge relief to the storage and loading flare (D-017). Set ASSUMED (design 9 barg).")
L.line(sheet, "FL-7002", dn=200, fluid="Flare gas", frm="BOG-7002 (PSV-7111)", to="FL-8001",
       notes="PSV-7111 outlet to the flare header. Drawn on P-07 and P-08.", insulation="none",
       route=[t_dp.branch, psv11, offpage("out", at=(378, 150), note="to flare (P-08)", note_at=(392, 146), rotation=UP)],
       labels=False)
lv = valve("LV7102", "GlobeValve", tag="LV-7102", at=(90, 182))
L.line(sheet, "DR-7001", dn=50, fluid="LNG", frm="D-7101", to="D-8101",
       notes="D-7101 liquid (spray carry-over) to the flare knock-out drum. Drawn on P-07 and P-08.",
       route=[drum["N3"], lv, offpage("out", at=(90, 205), note="to D-8101 (P-08)", note_at=(104, 210), rotation=DOWN)],
       label_at=(76, 196))

# ---- instruments --------------------------------------------------------------------------------
L.inst(sheet, "TIC-7103", "BOG temperature after the desuperheater",
       "LNG spray TV-7103 to -140 degC at the drum inlet (D-010).",
       at=(68, 100), sensing=inlet.segments[2], sensing_at=(58, 120), signal_to=tv, fail_action="FC")
L.inst(sheet, "PIC-7101", "BOG suction header pressure",
       "Acts on the inlet guide vanes of K-7101A/B/C; setpoint from PIC-1110 (P-01) (D-010).",
       at=(120, 45), sensing=suct.segments[0], sensing_at=(120, HDR_Y))
L.inst(sheet, "LIC-7102", "D-7101 level", "Drains carry-over to D-8101 by LV-7102.",
       at=(62, 190), sensing=drum["N4"], signal_to=lv, fail_action="FC")
L.inst(sheet, "LZT-7106", "D-7101 level high-high", "Trips the BOG compressors (C&E I-701).",
       at=(56, 170), sensing=drum["N5"])
for s in KX:
    L.inst(sheet, f"UIC-7104{s}", f"K-7101{s} anti-surge control",
           "Vendor anti-surge system; opens UV on the surge line (D-010).",
           at=(KX[s], 172), signal_to=uv[s], fail_action="FO")
    L.inst(sheet, f"UZ-7121{s}", f"K-7101{s} suction ESD valve XV-7121{s}",
           "Closes on a compressor trip (C&E I-701, I-702).", at=(SX[s] + 14, 80), signal_to=xv[s],
           fail_action="FC")
    L.inst(sheet, f"VZ-7110{s}", f"K-7101{s} vibration and bearing monitoring",
           "Machine protection (C&E I-702).", at=(KX[s] + 8, 112))
for tag, service, x in [("PI-7108", "BOG discharge pressure", 300), ("TI-7107", "BOG discharge temperature", 320),
                        ("FI-7109", "BOG to the trains", 340)]:
    L.inst(sheet, tag, service, at=(x, 200), sensing=dis.segments[3], sensing_at=(x, DIS_Y))

note(sheet, "K-7101A/B/C: 3 x 50 % centrifugal (C the installed spare), 27 t/h each, 108 -> 600 kPa(a), ~1.4 MW,", at=(12, 252))
note(sheet, "electric motors 6.6 kV (D-010). Holding: one machine; loading: two. Recycles BOG-7008..7010 (DN 250);", at=(12, 258))
note(sheet, "discharges BOG-7006, BOG-7007 (DN 300). LZT-7106: see C&E I-701; VZ-7110x: see C&E I-702.", at=(12, 264))

L.finish(sheet, target)
