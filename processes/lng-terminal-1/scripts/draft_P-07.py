"""Draft of P-07: BOG desuperheater and suction drum D-7101, the BOG compressors K-7101A/B/C
(3 x 50 %) with their suction ESD valves, anti-surge recycles (taken upstream of the discharge
check valves, returned to BOG-1001 upstream of the spray TV-7103), discharge check and isolation
valves, high discharge temperature trips, depressurising vents to the flare (FL-7003), the
discharge header to the trains with its battery-limit ESD valve XV-7130, the discharge relief to
the flare and the drum drain.

Rev B (review 2026-11-05-basic-design #9, #10, #11, #12, #13, #26; HAZOP H-04 A8, A9, A11): the
check valves moved downstream of the recycle tees, the recycles returned upstream of the
desuperheater, TZT-7112A..C, XV-7123A..C with UZ-7123A..C, vents HV-7124A..C into FL-7003,
XV-7130 / UZ-7130; the make-up take-off BOG-1009 removed (the make-up now comes from the
trains' fuel gas FG-1001 on P-01).
Rev C (review 2026-11-05-basic-design-2, D-026.5 and .12): open-position switches ZSO-7121A..C
tied to the suction ESD valves XV-7121A..C and the suction header low-low PZT-7113 (C&E
I-705A..C); PSV-7105 and its outlet FL-7001 removed (D-7101 cannot be isolated from the tanks,
whose PSVs protect it), so the BOG-1001 tee T7P1 goes and BOG-1001 has four segments on P-07.
Rev B round 2: recycle isolation actuated, XV-7125A..C (fail closed, UZ-7125A..C) instead of
the hand valves HV-7125A..C; the vent tees moved between CV-7122x and XV-7123x (venting empties
the casing through the check valve and the CV/XV pocket); the vent header runs below the
discharge header, the K-7101B/C recycle BOG-7012 along the top of the sheet, the K-7101A
recycle BOG-7008 to its own return tee on BOG-1001.
Rev D (review 2026-11-05-basic-design-4 #8, D-028): the ZSO-7121A..C measuring lines start on the
valve symbols; UZ-7125C sits straight under its actuator so its signal line meets the bubble edge.

Generator of P-07 (plant.yaml `generator:`, frame pid/frames/P-07.xml): `cheme regen P-07`
rebuilds the sheet; change this script, never the XML (D-021).
Streams S7, S8, S9, S14; decisions D-010, D-017, D-021.

Crossings: each machine is a path from the suction header to the discharge header with its
recycle tee and its vent tee on it. Suction header, discharge header and the three machine
paths divide the sheet into three regions, each bounded by two machine paths only, so the
recycle tree and the vent tree each reach the third machine across one line at least. This
layout keeps that minimum of two right-angle crossings: the K-7101B recycle BOG-7009 crosses the
suction header BOG-7001 to reach BOG-7012 on top, the K-7101B/C vent FL-7004 crosses the
discharge header BOG-7002 to reach FL-7003 below it.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from chemeascode.domains.piping.authoring import label  # noqa: E402
from lng_pid import Lists, Nozzle, Sheet, equipment, note, offpage, set_dn, tee, valve  # noqa: E402

target = Path(sys.argv[1])
sheet = Sheet.load(target)
L = Lists("P-07")
UP, DOWN = 270, 90
TOP_Y = 22                          # K-7101B/C recycle BOG-7012 along the top
HDR_Y, K_Y = 40, 110                # suction header, compressor centres
XS_Y = 62                           # suction ESD valves
REC_Y = 136                         # recycle tees below the machines
CV_Y, XV_Y, DIS_Y = 147, 180, 194   # discharge check valve, discharge XV, discharge header
V_Y = {"A": 158, "B": 158, "C": 168}  # vent tees between the check valve and the discharge XV
VENT_Y = 220                        # vent header FL-7003 below the discharge header
A_Y = 238                           # K-7101A recycle BOG-7008 along the bottom
KX = {"A": 170, "B": 250, "C": 330}             # compressor centres
SX = {k: x - 20 for k, x in KX.items()}         # suction branch x
DX = {k: x + 28 for k, x in KX.items()}         # discharge leg x
RAX, RBX, RCX = 136, 222, 404                   # recycle drop of A, rise of B, riser of C
VAX, VBX = 172, 318                             # vent drop of A, vent drop of B/C
BLX = 400                                       # BOG-7002 battery-limit off-page

drum = equipment(sheet, "PressureVessel", "D-7101", shape="VESSEL_WITH_DISHED_HEADS_SHAPE",
                 at=(100, 140), scale=(1.2, 1.6),
                 nozzles=[Nozzle("N1", (-12, -12), 750), Nozzle("N2", (0, -24), 750),
                          Nozzle("N3", (0, 24), 50), Nozzle("N4", (-12, 10), 50), Nozzle("N5", (-12, 18), 50)],
                 label_at=(121, 140))
k = {s: equipment(sheet, "CentrifugalCompressor", f"K-7101{s}", shape="COMPRESSOR_CENTRIFUGAL_SHAPE",
                  at=(x, K_Y), scale=1.5,
                  nozzles=[Nozzle("N1", (-11.25, 0), 500), Nozzle("N2", (11.25, 0), 300)],
                  label_at=(x, K_Y + 17)) for s, x in KX.items()}

# ---- inlet: recycle returns, spray desuperheater, suction drum -----------------------------------
# No relief valve on D-7101 (D-026.12): the drum and its suction header have no valve between them
# and the tanks (BOG-1001, DN 750), so the tank PSVs PSV-2131/3131 protect them.
t_rec = tee("T7R0", at=(28, 120), branch="up", branch_dn=300)     # BOG-7012 (K-7101B/C)
t_reca = tee("T7R1", at=(38, 120), branch="down", branch_dn=250)  # BOG-7008 (K-7101A)
t_spr = tee("T7S1", at=(72, 120), branch="up", branch_dn=80)
inlet = L.line(sheet, "BOG-1001", dn=750, fluid="Boil-off gas", frm="T-2101", to="D-7101",
               notes="see P-01; receives the anti-surge recycles BOG-7012 (K-7101B/C) and BOG-7008 (K-7101A) "
                     "upstream of the spray TV-7103.",
               route=[offpage("in", at=(12, 120), note="from P-01", note_at=(18, 113)), t_rec, t_reca,
                      t_spr, (82, 120), (82, 128), drum["N1"]],
               label_at=(22, 132))
tv = valve("TV7103", "GlobeValve", tag="TV-7103", at=(72, 80))
L.line(sheet, "LNG-4008", dn=80, fluid="LNG", frm="LNG-2002", to="BOG-1001 (TV-7103)",
       notes="see P-04",
       route=[offpage("in", at=(72, 40), note="spray from P-04", note_at=(86, 36), rotation=DOWN),
              tv, t_spr.branch], label_at=(86, 60))

# ---- suction header and branches -----------------------------------------------------------------
tsa = tee("T7HA", at=(SX["A"], HDR_Y), branch="down", branch_dn=500)
tsb = tee("T7HB", at=(SX["B"], HDR_Y), branch="down", branch_dn=500)
xv = {s: valve(f"XV7121{s}", "BallValve", tag=f"XV-7121{s}", at=(SX[s], XS_Y)) for s in KX}
suct = L.line(sheet, "BOG-7001", dn=750, fluid="Boil-off gas", frm="D-7101", to="K-7101C",
              notes="Compressor suction header, 49.1 t/h at loading, -140 degC, 108 kPa(a) (S14, D-010); ends as the K-7101C suction.",
              segments=[{"number": "S3", "nominal_diameter": "DN500", "notes": "K-7101C suction branch"}],
              route=[drum["N2"], (100, HDR_Y), tsa, tsb, (SX["C"], HDR_Y), xv["C"], (SX["C"], K_Y),
                     k["C"]["N1"]],
              label_at=(190, HDR_Y + 10))
set_dn(sheet, ["T7HB_N2", "XV7121C_N1", "XV7121C_N2"], 500, segments=["Line_BOG7001_S3"])
for s, tt, lab in [("A", tsa, (SX["A"] - 12, 80)), ("B", tsb, (SX["B"] + 14, 84))]:
    L.line(sheet, f"BOG-700{4 if s == 'A' else 5}", dn=500, fluid="Boil-off gas", frm="BOG-7001",
           to=f"K-7101{s}", notes=f"K-7101{s} suction, 27 t/h design (D-010).",
           route=[tt.branch, xv[s], (SX[s], K_Y), k[s]["N1"]], label_at=lab)

# ---- discharges: recycle tee, check valve, vent tee, discharge XV -------------------------------
t_q = {s: tee(f"T7Q{s}", at=(DX[s], REC_Y), branch="right" if s == "C" else "left", branch_dn=250)
       for s in KX}
cv = {s: valve(f"CV7122{s}", "SwingCheckValve", at=(DX[s], CV_Y)) for s in KX}
t_vent = {s: tee(f"T7X{s}", at=(DX[s], V_Y[s]), branch="right" if s == "B" else "left", branch_dn=80 if s == "A" else 50)
          for s in KX}
xvd = {s: valve(f"XV7123{s}", "BallValve", tag=f"XV-7123{s}", at=(DX[s], XV_Y)) for s in KX}
t_dp = tee("T7DP", at=(214, DIS_Y), branch="up", branch_dn=200)
tdb = tee("T7DB", at=(DX["B"], DIS_Y), branch="up", branch_dn=300)
tdc = tee("T7DC", at=(DX["C"], DIS_Y), branch="up", branch_dn=300)
xv_bl = valve("XV7130", "BallValve", tag="XV-7130", at=(386, DIS_Y))


def machine_leg(s):
    """K-7101s discharge nozzle to its discharge XV: recycle tee, check valve, vent tee, XV."""
    return [k[s]["N2"], (DX[s], K_Y), t_q[s], cv[s], t_vent[s], xvd[s]]


dis = L.line(sheet, "BOG-7002", dn=500, fluid="Boil-off gas", frm="K-7101A", to="BL (trains)",
             notes="Compressed BOG to the trains' end-flash / fuel gas system, 600 kPa(a), about -49 degC (S9, D-010); "
                   "segments S1-S4 are the DN 300 discharge of K-7101A, where the header starts; battery-limit ESD "
                   "valve XV-7130 before the off-page.",
             segments=[{"number": "S1", "nominal_diameter": "DN300", "notes": "K-7101A discharge nozzle to the recycle tee"},
                       {"number": "S2", "nominal_diameter": "DN300",
                        "notes": "K-7101A discharge, recycle tee to the vent tee: CV-7122A"},
                       {"number": "S3", "nominal_diameter": "DN300",
                        "notes": "K-7101A discharge, vent tee to the relief tee: XV-7123A"},
                       {"number": "S4", "nominal_diameter": "DN300",
                        "notes": "K-7101A discharge, relief tee (PSV-7111) to the K-7101B tee"}],
             route=[*machine_leg("A"), (DX["A"], DIS_Y), t_dp, tdb, tdc, xv_bl,
                    offpage("out", at=(BLX, DIS_Y), note="to trains (BL)", note_at=(398, DIS_Y - 8))],
             label_at=(245, DIS_Y + 10))
set_dn(sheet, ["T7QA_N1", "T7QA_N2", "CV7122A_N1", "CV7122A_N2", "T7XA_N1", "T7XA_N2",
               "XV7123A_N1", "XV7123A_N2", "T7DP_N1", "T7DP_N2", "T7DB_N1"], 300,
       segments=["Line_BOG7002_S1", "Line_BOG7002_S2", "Line_BOG7002_S3", "Line_BOG7002_S4"])
for s, tt, lab in [("B", tdb, (DX["B"] - 12, 166)), ("C", tdc, (DX["C"] + 14, 164))]:
    L.line(sheet, f"BOG-700{6 if s == 'B' else 7}", dn=300, fluid="Boil-off gas", frm=f"K-7101{s}",
           to="BOG-7002", notes=f"K-7101{s} discharge: recycle tee, CV-7122{s}, vent tee, XV-7123{s}.",
           route=[*machine_leg(s), tt.branch], label_at=lab)

# ---- anti-surge recycles to BOG-1001 upstream of the spray -------------------------------------
UVX = {"A": KX["A"] + 10, "B": KX["B"] + 10, "C": 372}
XRX = {"A": KX["A"] - 10, "B": KX["B"] - 10, "C": 388}
uv = {s: valve(f"UV7104{s}", "GlobeValve", tag=f"UV-7104{s}", at=(UVX[s], REC_Y)) for s in KX}
xv_r = {s: valve(f"XV7125{s}", "BallValve", tag=f"XV-7125{s}", at=(XRX[s], REC_Y)) for s in KX}
t_mb = tee("T7MB", at=(RBX, TOP_Y), branch="down", branch_dn=250)
L.line(sheet, "BOG-7012", dn=300, fluid="Boil-off gas", frm="K-7101C discharge (T7QC)", to="BOG-1001",
       notes="Common anti-surge recycle of K-7101B/C to BOG-1001 upstream of the desuperheater spray TV-7103, "
             "so the recycle gas is quenched and separated in D-7101 (review #9, H-04 A11); segment S1 is the "
             "DN 250 K-7101C recycle (UV-7104C, XV-7125C), where the line starts.",
       segments=[{"number": "S1", "nominal_diameter": "DN250", "notes": "K-7101C anti-surge recycle"}],
       route=[t_q["C"].branch, uv["C"], xv_r["C"], (RCX, REC_Y), (RCX, TOP_Y), t_mb, (28, TOP_Y),
              t_rec.branch],
       label_at=(160, TOP_Y - 7))
set_dn(sheet, ["UV7104C_N1", "UV7104C_N2", "XV7125C_N1", "XV7125C_N2", "T7MB_N1"], 250,
       segments=["Line_BOG7012_S1"])
L.line(sheet, "BOG-7009", dn=250, fluid="Boil-off gas", frm="K-7101B discharge (T7QB)", to="BOG-7012",
       notes="K-7101B anti-surge recycle (UV-7104B, XV-7125B) to the common recycle BOG-7012, upstream of the "
             "discharge check valve CV-7122B (D-010, review #10).",
       route=[t_q["B"].branch, uv["B"], xv_r["B"], (RBX, REC_Y), t_mb.branch], label_at=(RBX - 14, 95))
L.line(sheet, "BOG-7008", dn=250, fluid="Boil-off gas", frm="K-7101A discharge (T7QA)", to="BOG-1001",
       notes="K-7101A anti-surge recycle (UV-7104A, XV-7125A) to BOG-1001 upstream of the spray TV-7103, "
             "upstream of the discharge check valve CV-7122A (D-010, review #9, #10).",
       route=[t_q["A"].branch, uv["A"], xv_r["A"], (RAX, REC_Y), (RAX, A_Y), (38, A_Y), t_reca.branch],
       label_at=(RAX - 12, 180))

# ---- depressurising vents to the flare, below the discharge header -------------------------------
hv_v = {"A": valve("HV7124A", "BallValve", tag="HV-7124A", at=(VAX, 202)),
        "B": valve("HV7124B", "BallValve", tag="HV-7124B", at=(292, V_Y["B"])),
        "C": valve("HV7124C", "BallValve", tag="HV-7124C", at=(340, V_Y["C"]))}
t_vb = tee("T7VB", at=(VBX, VENT_Y), branch="up", branch_dn=80)
t_vc = tee("T7VC", at=(VBX, V_Y["C"]), branch="right", branch_dn=50)
L.line(sheet, "FL-7003", dn=80, fluid="Flare gas", frm="K-7101A discharge (T7XA)", to="D-8101",
       notes="Depressurising vent header of K-7101A/B/C (HV-7124A..C, normally closed, each between the check "
             "valve CV-7122x and the discharge XV-7123x) to the flare knock-out drum D-8101 (review #11). Drawn on "
             "P-07 and P-08; DN 80 throughout (the K-7101A vent included).",
       insulation="none",
       route=[t_vent["A"].branch, (VAX, V_Y["A"]), hv_v["A"], (VAX, VENT_Y), t_vb,
              offpage("out", at=(BLX, VENT_Y), note="to D-8101 (P-08)", note_at=(396, VENT_Y + 7))],
       label_at=(245, VENT_Y + 8))
L.line(sheet, "FL-7004", dn=80, fluid="Flare gas", frm="K-7101B discharge (T7XB)", to="FL-7003",
       notes="K-7101B depressurising vent (HV-7124B, normally closed), with the K-7101C vent FL-7005, to FL-7003.",
       insulation="none", route=[t_vent["B"].branch, hv_v["B"], (VBX, V_Y["B"]), t_vc, t_vb.branch],
       label_at=(VBX - 12, 182),
       segments=[{"number": "S1", "nominal_diameter": "DN50", "notes": "K-7101B vent before the K-7101C vent joins"}])
set_dn(sheet, ["HV7124B_N1", "HV7124B_N2", "T7VC_N1"], 50, segments=["Line_FL7004_S1"])
L.line(sheet, "FL-7005", dn=50, fluid="Flare gas", frm="K-7101C discharge (T7XC)", to="FL-7004",
       notes="K-7101C depressurising vent (HV-7124C, normally closed) to FL-7004 and FL-7003.",
       insulation="none", route=[t_vent["C"].branch, hv_v["C"], t_vc.branch], label_at=(338, 176))

# ---- relief of the discharge header, drum drain ----------------------------------------------------
psv11 = L.relief("PSV7111", "PSV-7111", "FL-7002", 7.5,
                 "blocked outlet of the discharge header with the compressors running (train fuel system tripped, "
                 "XV-7130 closed)",
                 "BOG discharge relief to the storage and loading flare (D-017). Set ASSUMED (design 9 barg).",
                 label_at=(228, 181))
L.line(sheet, "FL-7002", dn=200, fluid="Flare gas", frm="BOG-7002 (PSV-7111)", to="FL-8001",
       notes="PSV-7111 outlet to the flare header. Drawn on P-07 and P-08.", insulation="none",
       route=[t_dp.branch, psv11, offpage("out", at=(214, 166), note="to flare (P-08)", note_at=(214, 155), rotation=UP)],
       labels=False)
lv = valve("LV7102", "GlobeValve", tag="LV-7102", at=(100, 182))
L.line(sheet, "DR-7001", dn=50, fluid="LNG", frm="D-7101", to="D-8101",
       notes="D-7101 liquid (spray carry-over) to the flare knock-out drum. Drawn on P-07 and P-08.",
       route=[drum["N3"], lv, offpage("out", at=(100, 205), note="to D-8101 (P-08)", note_at=(114, 210), rotation=DOWN)],
       label_at=(86, 198))

# ---- valve tags of the hand valves -------------------------------------------------------------------
label(sheet, hv_v["A"].id, "PipingComponentNumber", at=(VAX - 12, 202))
label(sheet, hv_v["B"].id, "PipingComponentNumber", at=(292, V_Y["B"] + 6))
label(sheet, hv_v["C"].id, "PipingComponentNumber", at=(340, V_Y["C"] - 6))

# ---- instruments --------------------------------------------------------------------------------
L.inst(sheet, "TIC-7103", "BOG temperature after the desuperheater",
       "LNG spray TV-7103 to -140 degC at the drum inlet, also quenching the anti-surge recycles BOG-7012 and "
       "BOG-7008 (D-010).",
       at=(88, 100), sensing=inlet.segments[3], sensing_at=(77, 120), signal_to=tv, fail_action="FC")
L.inst(sheet, "PIC-7101", "BOG suction header pressure",
       "Acts on the inlet guide vanes of K-7101A/B/C; setpoint from PIC-1110 (P-01) (D-010).",
       at=(120, 54), sensing=suct.segments[0], sensing_at=(120, HDR_Y))
L.inst(sheet, "PZT-7113", "BOG compressor suction header pressure low-low (I-705A-C)",
       "Own tapping on the common suction header BOG-7001 between D-7101 and the machines, independent of "
       "PIC-7101: at low-low suction pressure a running machine stops (C&E I-705A/B/C, D-026.5).",
       at=(132, 31), sensing=suct.segments[0], sensing_at=(132, HDR_Y))
L.inst(sheet, "LIC-7102", "D-7101 level", "Drains carry-over to D-8101 by LV-7102.",
       at=(70, 188), sensing=drum["N5"], signal_to=lv, fail_action="FC")
L.inst(sheet, "LZT-7106", "D-7101 level high-high", "Trips the BOG compressors (C&E I-701).",
       at=(66, 148), sensing=drum["N4"])
for s in KX:
    L.inst(sheet, f"UIC-7104{s}", f"K-7101{s} anti-surge control",
           "Vendor anti-surge system; opens UV on the recycle (D-010).",
           at=(UVX[s], REC_Y + 12), signal_to=uv[s], fail_action="FO")
    L.inst(sheet, f"UZ-7125{s}", f"K-7101{s} recycle isolation valve XV-7125{s}",
           f"Fail open and open in operation and on a trip: the recycle keeps the tripped machine open to the tank "
           f"system (its relief path) and the anti-surge path open on a utility failure; closed by the operator "
           f"(HS) only to isolate K-7101{s} for maintenance (D-025).",
           at=(XRX[s], REC_Y + 12), signal_to=xv_r[s], fail_action="FO")  # under its actuator (review 4 #8b)
    L.inst(sheet, f"UZ-7121{s}", f"K-7101{s} suction ESD valve XV-7121{s}",
           "Closes on a compressor trip (C&E I-701, I-702) and on every compressor stop (H-04 A9).",
           at=(SX[s] + 14, XS_Y), signal_to=xv[s], fail_action="FC")
    # open-position switch on the valve itself (sensor at XV-7121s, as ZSC-5123 on P-05): the measuring
    # line starts on the lower right corner of the valve symbol, below its actuator (review 4 #8a)
    L.inst(sheet, f"ZSO-7121{s}", f"XV-7121{s} open position",
           f"C&E I-705{s}: a running machine stops when its suction valve leaves the open position.",
           at=(SX[s] + 14, XS_Y + 9), sensing=xv[s].id, sensing_at=(SX[s] + 1, XS_Y + 2),
           sensing_points=[(SX[s] + 3, XS_Y + 2), (SX[s] + 3, XS_Y + 9)])
    L.inst(sheet, f"UZ-7123{s}", f"K-7101{s} discharge isolation valve XV-7123{s}",
           "Fail closed; closes with XV-7121" + s + " on a compressor trip or stop, isolates the machine from "
           "the discharge header (review #11, H-04 A8/A9).",
           at=(DX[s] + (-13 if s in "AB" else 13), XV_Y), signal_to=xvd[s], fail_action="FC")
    L.inst(sheet, f"VZ-7110{s}", f"K-7101{s} vibration and bearing monitoring",
           f"Vendor unit control panel trips of K-7101{s} (C&E I-702{'' if s == 'A' else s}): vibration and "
           "bearings, dry gas seal, lube oil, motor protection, discharge pressure high-high below PSV-7111 "
           "(D-026.5; to be confirmed with the vendor).", at=(KX[s] + 16, 97))
L.inst(sheet, "TZT-7112A", "K-7101A discharge temperature high-high",
       "Trips K-7101A on high discharge temperature (review #9, H-04 A11; C&E I-703A/B/C).",
       at=(DX["A"] + 13, 122), sensing=dis.segments[0], sensing_at=(DX["A"], 122))
for s, number in [("B", "BOG-7006"), ("C", "BOG-7007")]:
    L.inst(sheet, f"TZT-7112{s}", f"K-7101{s} discharge temperature high-high",
           f"Trips K-7101{s} on high discharge temperature (review #9, H-04 A11; C&E I-703A/B/C).",
           at=(DX[s] + 13, 122), sensing=f"Line_{number.replace('-', '')}_S1", sensing_at=(DX[s], 122))
L.inst(sheet, "UZ-7130", "BOG-7002 battery-limit ESD valve XV-7130",
       "Fail closed; closes on ESD and on a trip of all compressors (review #11, H-04 A8).",
       at=(386, 207), signal_to=xv_bl, fail_action="FC")
for tag, service, x, seg in [("PI-7108", "BOG discharge pressure", 290, 4),
                             ("TI-7107", "BOG discharge temperature", 304, 4),
                             ("FI-7109", "BOG to the trains", 368, 5)]:
    L.inst(sheet, tag, service, at=(x, 207), sensing=dis.segments[seg], sensing_at=(x, DIS_Y))

note(sheet, "K-7101A/B/C: 3 x 50 % centrifugal (C the installed spare), 27 t/h each, 108 -> 600 kPa(a), ~1.4 MW, "
            "electric motors 6.6 kV (D-010). Holding: one machine; loading: two.", at=(12, 252))
note(sheet, "Anti-surge recycles (DN 250): BOG-7008 to BOG-1001; BOG-7009, BOG-7012 S1 via BOG-7012 (DN 300) "
            "to BOG-1001; both upstream of the spray TV-7103. Discharges BOG-7006, BOG-7007 (DN 300).", at=(12, 258))
note(sheet, "HV-7124A/B/C normally closed (depressurising to FL-7003); XV-7125A/B/C fail open, closed only for "
            "maintenance (D-025). N2 purge connections per machine: vendor package, not drawn (D-026.9).", at=(12, 264))
note(sheet, "LZT-7106: C&E I-701. VZ-7110x: vendor unit control panel trips I-702/702B/C (vibration and bearings, "
            "dry gas seal, lube oil, motor, discharge pressure high-high).", at=(12, 270))
note(sheet, "ZSO-7121x, PZT-7113: I-705A-C stop a running machine when its suction valve XV-7121x leaves the open "
            "position or the suction header is low-low. TZT-7112x: I-703A-C.", at=(12, 276))

L.finish(sheet, target)
