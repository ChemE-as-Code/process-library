"""Draft of P-08: the storage and loading flare header, its knock-out drum D-8101 and pumps to
the liquid burner, the storage and loading flare FL-8101 with purge and pilot gas; the LNG
spill impoundment sumps of the tank area and the jetty; the N2 and instrument-air headers.

Generator of P-08 (plant.yaml `generator:`, frame pid/frames/P-08.xml): `cheme regen P-08`
rebuilds the sheet; change this script, never the XML (D-021).
Decisions D-017, D-018, D-020, D-021; flares from BCER air permit PA-110588 (S-02).

Rev C (review 2026-11-05-basic-design-2 #7, D-026.9, .11, .12): discharge isolation HV-8108A/B
downstream of the check valves CV-8102A/B, the thermal relief PSV-8109 stays on the common
section LNG-8001; the pumps' motor start/stop functions HS-8101A/B, each tied to its pump by a
measuring line, are driven by the signal chain LIC-8101 -> HS-8101A -> HS-8101B (the authoring API
draws one signal per function, to a valve or to an instrument function, not to a pump); FL-7001 (PSV-7105, removed on P-07) and its flare header tee T8F1 removed, so FL-8001 on P-08
starts with the FL-7002 tee and has one segment fewer.

Rev D (review 2026-11-05-basic-design-3 #3 and its adversarial check, D-026.14): sheet note on the
suction isolations HV-8106A/B (cryogenic ball valves, cavity vented to the drum side, so a pump
blocked in between HV-8106x and HV-8108x relieves into D-8101; drain to the drum before
maintenance), with a "cavity vent: drum side" text at each valve; the I-802 notes say that it
starts both pumps (whichever is not running) and yields to I-803, not "the standby". The left
note column starts one row higher (y 252) to take the extra line; the new notes come after the
existing ones, so the ids Note1 to Note11 are kept.
"""

import sys
from dataclasses import replace
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from chemeascode.domains.piping.authoring import label  # noqa: E402
from lng_pid import Lists, Nozzle, Sheet, equipment, note, offpage, tee, valve  # noqa: E402

target = Path(sys.argv[1])
sheet = Sheet.load(target)
L = Lists("P-08")
UP, DOWN, LEFT = 270, 90, 180
HY = 60
NOTE_Y = 22  # off-page notes of the top-edge arrows (arrows y 27-34), clear above the arrow heads

drum = equipment(sheet, "PressureVessel", "D-8101", shape="VESSEL_WITH_DISHED_HEADS_SHAPE",
                 at=(150, 100), rotation=90, scale=1.5,
                 nozzles=[Nozzle("N1", (-15, -15), 900), Nozzle("N2", (15, -15), 900),
                          Nozzle("N3", (0, 15), 100), Nozzle("N4", (-12, 15), 50),
                          Nozzle("N5", (-22.5, 7), 50), Nozzle("N6", (22.5, -5), 50),
                          Nozzle("N7", (22.5, 7), 50), Nozzle("N8", (22.5, 1.5), 25)],
                 label_at=(150, 78))
flare = equipment(sheet, "Flare", "FL-8101", shape="FLARE_SHAPE", at=(300, 95), scale=2.0,
                  nozzles=[Nozzle("N1", (0, 24.7), 900), Nozzle("N2", (25, 0), 50)], label_at=(316, 74))
pa = equipment(sheet, "CentrifugalPump", "P-8101A", shape="CENTRIFUGAL_PUMP_SHAPE", at=(130, 165),
               nozzles=[Nozzle("N1", (-7.5, 0), 100), Nozzle("N2", (7.5, 0), 80)], label_at=(117, 177))
pb = equipment(sheet, "CentrifugalPump", "P-8101B", shape="CENTRIFUGAL_PUMP_SHAPE", at=(190, 165),
               nozzles=[Nozzle("N1", (-7.5, 0), 100), Nozzle("N2", (7.5, 0), 80)], label_at=(175, 177))

# ---- flare header and knock-out drum -------------------------------------------------------------
FX = {"FL-7002": 52, "FL-7003": 74, "BOG-4013": 96, "FG-8001": 118}
t2 = tee("T8F2", at=(FX["FL-7002"], HY), branch="up", branch_dn=200)
t4 = tee("T8F4", at=(FX["FL-7003"], HY), branch="up", branch_dn=80)
t5 = tee("T8F5", at=(FX["BOG-4013"], HY), branch="up", branch_dn=300)
t3 = tee("T8F3", at=(FX["FG-8001"], HY), branch="up", branch_dn=50)
hdr = L.line(sheet, "FL-8001", dn=900, fluid="Flare gas", frm="BOG-1001 (PV-1110)", to="D-8101", insulation="none",
             notes="Storage and loading flare header from the tank pressure control valve PV-1110 (P-01) to the "
                   "knock-out drum D-8101; joined on P-08 by the BOG discharge relief valve PSV-7111 "
                   "(FL-7002), the BOG compressor depressurising vents (FL-7003, P-07), the carrier de-inerting and "
                   "cool-down vapour (BOG-4013, P-04) and the fuel-gas purge FG-8001. Drawn on P-01 and P-08.",
             route=[offpage("in", at=(12, HY), note="from PV-1110 (P-01)", note_at=(20, HY + 7)), t2, t4, t5, t3,
                    (135, HY), drum["N1"]],
             label_at=(63, HY + 8))
for tt, txt, num, frm in [(t2, "PSV-7111 (P-07)", "FL-7002", "BOG-7002 (PSV-7111)")]:
    x = FX[num]
    L.line(sheet, num, dn=200, fluid="Flare gas", frm=frm, to="FL-8001", insulation="none",
           notes="see P-07",
           route=[offpage("in", at=(x, 34), note=txt, note_at=(x, NOTE_Y), rotation=DOWN), tt.branch], labels=False)
L.line(sheet, "FL-7003", dn=80, fluid="Flare gas", frm="K-7101A/B/C depressurising vents", to="FL-8001",
       insulation="none",
       notes="BOG compressor depressurising vents to the storage and loading flare header. Drawn on P-07 and P-08.",
       route=[offpage("in", at=(FX["FL-7003"], 34), note="from P-07", note_at=(FX["FL-7003"], NOTE_Y), rotation=DOWN),
              t4.branch], label_at=(FX["FL-7003"] + 9, 46))
L.line(sheet, "BOG-4013", dn=300, fluid="Boil-off gas", frm="BOG-4001", to="D-8101 (FL-8001)",
       insulation="cold (PIR)",
       notes="Carrier de-inerting and cool-down vapour from the vapour return (XV-4131, joined by BOG-4014 on P-04) "
             "into the flare header FL-8001 to the knock-out drum D-8101 (D-017, S-02, review 2026-11-05 #19). "
             "Drawn on P-04 and P-08.",
       route=[offpage("in", at=(FX["BOG-4013"], 34), note="from P-04", note_at=(FX["BOG-4013"], NOTE_Y), rotation=DOWN),
              t5.branch], label_at=(FX["BOG-4013"] + 10, 46))
L.line(sheet, "FG-8001", dn=50, fluid="Fuel gas", frm="BL (fuel gas)", to="FL-8001", insulation="none",
       notes="Continuous purge of the flare header (part of the 6.0 m3/min routine limit with pilots and seal gas, S-02).",
       route=[offpage("in", at=(FX["FG-8001"], 34), note="purge gas", note_at=(FX["FG-8001"], NOTE_Y), rotation=DOWN),
              valve("FO8111", "GlobeValve", tag="FO-8111", at=(FX["FG-8001"], 46)), t3.branch], labels=False)
L.line(sheet, "FL-8002", dn=900, fluid="Flare gas", frm="D-8101", to="FL-8101", insulation="none",
       notes="Knock-out drum to the storage and loading flare stack on the 122 m derrick (stack inner diameter 1.42 m, S-02).",
       route=[drum["N2"], (165, 70), (240, 70), (240, 140), (300, 140), flare["N1"]],
       label_at=(205, 63))
L.line(sheet, "FG-8002", dn=50, fluid="Fuel gas", frm="BL (fuel gas)", to="FL-8101", insulation="none",
       notes="Pilot gas to the flare tip.",
       route=[offpage("in", at=(405, 95), note="pilot gas (BL)", note_at=(392, 89), rotation=LEFT),
              valve("PV8132", "GlobeValve", tag="PCV-8132", at=(360, 95)), flare["N2"]],
       label_at=(372, 103))
L.line(sheet, "DR-7001", dn=50, fluid="LNG", frm="D-7101", to="D-8101",
       notes="see P-07",
       route=[offpage("in", at=(12, 107), note="from D-7101 (P-07)", note_at=(22, 113)), drum["N5"]],
       label_at=(100, 113))

# ---- knock-out drum pumps to the liquid burner ---------------------------------------------------
t_s = tee("T8S1", at=(150, 126), branch="right", branch_dn=100)
L.line(sheet, "LNG-8002", dn=100, fluid="LNG", frm="D-8101", to="P-8101A",
       notes="Knock-out drum pump suction header; HV-8106A isolates P-8101A (cryogenic ball valve, cavity vented to the drum side, D-026.14).",
       route=[drum["N3"], t_s, (150, 135), (116, 135),
              valve("HV8106A", "BallValve", tag="HV-8106A", at=(116, 150)), (116, 165), pa["N1"]],
       label_at=(104, 141))
L.line(sheet, "LNG-8003", dn=100, fluid="LNG", frm="LNG-8002", to="P-8101B",
       notes="P-8101B suction; HV-8106B isolates P-8101B (cryogenic ball valve, cavity vented to the drum side, D-026.14).",
       route=[t_s.branch, (176, 126), valve("HV8106B", "BallValve", tag="HV-8106B", at=(176, 150)), (176, 165),
              pb["N1"]], labels=False)
t_d = tee("T8D1", at=(205, 190), branch="up", branch_dn=80)
t_m = tee("T8D2", at=(225, 190), branch="up", branch_dn=50)
RX = 232  # thermal relief PSV-8109 riser, between LNG-8005 (x 225) and FL-8002 (x 240)
t_r = tee("T8D3", at=(RX, 190), branch="up", branch_dn=25)
L.line(sheet, "LNG-8001", dn=80, fluid="LNG", frm="P-8101A", to="BL (liquid burner)",
       notes="Liquids to the 60 m liquid burner derrick of the site (9 burners, S-02), 30 m3/h. P-8101A "
             "discharge: check valve CV-8102A, then the discharge isolation HV-8108A (review 2 #7). Thermal relief "
             "PSV-8109 (LNG-8006) to D-8101 on the common section downstream of HV-8108A/B (H-05 A3).",
       route=[pa["N2"], (145, 165), valve("CV8102A", "SwingCheckValve", at=(145, 172)),
              valve("HV8108A", "BallValve", tag="HV-8108A", at=(145, 182)), (145, 190), t_d, t_m,
              t_r, offpage("out", at=(285, 190), note="to liquid burner (BL)", note_at=(268, 196))],
       label_at=(257, 184))
psv8109 = L.relief("PSV8109", "PSV-8109", "LNG-8006", 15.0,
                   "thermal expansion of LNG blocked in the common discharge LNG-8001 between the discharge "
                   "isolations HV-8108A/B (or the check valves CV-8102A/B) and the battery-limit valve (pumps "
                   "stopped, liquid burner isolated)",
                   "Thermal relief of the knock-out drum pump common discharge LNG-8001 back to D-8101 "
                   "through LNG-8006 (HAZOP H-05 A3); DN 25, set at the 15 barg design of the line.",
                   label_at=(RX + 12, 166))
L.line(sheet, "LNG-8004", dn=80, fluid="LNG", frm="P-8101B", to="LNG-8001",
       notes="P-8101B discharge: check valve CV-8102B, then the discharge isolation HV-8108B (review 2 #7).",
       route=[pb["N2"], (205, 165), valve("CV8102B", "SwingCheckValve", at=(205, 172)),
              valve("HV8108B", "BallValve", tag="HV-8108B", at=(205, 182)), t_d.branch], labels=False)
L.line(sheet, "LNG-8005", dn=50, fluid="LNG", frm="LNG-8001", to="D-8101",
       notes="Minimum-flow return of the running knock-out drum pump P-8101A/B to D-8101 through the "
             "restriction orifice FO-8107 (continuous, sized for the pump's minimum continuous flow, TBD with "
             "the pump vendor); taken downstream of the check valves, so it serves either pump.",
       route=[t_m.branch, valve("FO8107", "GlobeValve", tag="FO-8107", at=(225, 150)), (225, 107),
              drum["N7"]],
       label_at=(212, 122))
L.line(sheet, "LNG-8006", dn=25, fluid="LNG", frm="LNG-8001 (PSV-8109)", to="D-8101",
       notes="Thermal relief outlet of PSV-8109 (common discharge LNG-8001 between HV-8108A/B and the battery "
             "limit) back to the knock-out drum D-8101, own nozzle N8 (HAZOP H-05 A3).",
       route=[t_r.branch, replace(psv8109, at=(RX, 165)), (RX, 101.5), drum["N8"]],
       label_at=(RX + 14, 150))
for vid, at in [("HV8106A", (106, 152)), ("HV8106B", (166, 152)), ("FO8107", (215, 152)),
                ("HV8108A", (154, 182)), ("HV8108B", (214, 182))]:
    label(sheet, vid, "PipingComponentNumber", at=at)

# ---- spill impoundment sumps -------------------------------------------------------------------
sump = equipment(sheet, "Tank", "T-8101", shape="TANK_OPEN_SHAPE", at=(40, 222),
                 nozzles=[Nozzle("N1", (15, 6), 150), Nozzle("N2", (-15, -4), 50), Nozzle("N3", (-15, 6), 50)],
                 label_at=(40, 238))
spump = equipment(sheet, "CentrifugalPump", "P-8102", shape="CENTRIFUGAL_PUMP_SHAPE", at=(80, 228),
                  nozzles=[Nozzle("N1", (-7.5, 0), 150), Nozzle("N2", (0, -7.5), 100)], label_at=(80, 240))
L.line(sheet, "W-8001", dn=150, fluid="Rainwater", frm="T-8101", to="P-8102", insulation="none",
       pclass="Class 150", notes="Sump rainwater to the pump.", route=[sump["N1"], spump["N1"]], labels=False)
L.line(sheet, "W-8002", dn=100, fluid="Rainwater", frm="P-8102", to="BL (oily water)", insulation="none",
       notes="Rainwater from the tank-area sump to the site oily water system; interlocked off on LNG in the sump (C&E I-801).",
       route=[spump["N2"], (80, 210), (120, 210),
              offpage("out", at=(130, 210), note="to oily water (BL)", note_at=(128, 204))],
       label_at=(104, 216))
jsump = equipment(sheet, "Tank", "T-8102", shape="TANK_OPEN_SHAPE", at=(160, 225), nozzles=[Nozzle("N1", (-15, 0), 50)],
                  label_at=(160, 240))

# ---- N2 and instrument-air headers ----------------------------------------------------------------
tn = tee("T8N1", at=(240, 210), branch="down", branch_dn=50)
n2 = L.line(sheet, "N-8001", dn=80, fluid="Nitrogen", frm="BL (site N2)", to="LNG-5001", insulation="none",
            notes="Terminal N2 header from the site system, 7 barg, to Berth 2 (and via N-8002 to Berth 1): purging the arms and headers to < 1 % O2 before and < 2 % HC after loading, the leak test at 5 bar (liquid) / 2.5 bar (vapour arm) (S-01), seal gas, blanketing (D-020). Drawn on P-08 and P-05.",
            route=[offpage("in", at=(205, 210), note="N2 (BL)", note_at=(210, 204)), tn,
                   offpage("out", at=(285, 210), note="to Berth 2 (P-05)", note_at=(270, 204))],
            label_at=(260, 216))
L.line(sheet, "N-8002", dn=50, fluid="Nitrogen", frm="N-8001", to="LNG-6001", insulation="none",
       notes="N2 to Berth 1. Drawn on P-08 and P-06.", route=[tn.branch, (240, 228),
                                     offpage("out", at=(285, 228), note="to Berth 1 (P-06)", note_at=(270, 234))],
       labels=False)
ia = L.line(sheet, "IA-8001", dn=50, fluid="Instrument air", frm="BL (site instrument air)", to="instrument users",
            insulation="none", notes="Instrument-air header of the terminal, 7 barg (D-020).",
            route=[offpage("in", at=(205, 246), note="IA (BL)", note_at=(210, 240)),
                   offpage("out", at=(285, 246), note="to users", note_at=(276, 240))],
            label_at=(245, 240))

# ---- instruments ----------------------------------------------------------------------------------
L.inst(sheet, "PI-8112", "Flare header pressure", at=(105, 74), sensing=hdr.segments[-1], sensing_at=(105, HY))
L.inst(sheet, "FI-8111", "Flare header purge gas flow", "Purge set by the orifice FO-8111.",
       at=(FX["FG-8001"] + 14, 40), sensing="Line_FG8001_S1", sensing_at=(FX["FG-8001"], 40))
# Motor control of the KO drum pumps (D-026.11). HS-8101A/B are the DCS start/stop functions of the
# pump motors, each tied to its pump by a measuring line from the pump casing (run feedback; the
# authoring API takes a nozzle as the sensing location of a machine, here the discharge nozzle N2),
# as ZSO-7121x is tied to its valve. The API draws one signal per instrument function, ending at a
# valve or at another function, so the drive is a chain: LIC-8101 -> HS-8101A -> HS-8101B (the
# duty/standby selection passes the start/stop command on to P-8101B). I-802 (start both, whichever
# is not running; yields to I-803, D-026.14) and I-803 (stop both) act on the pumps from the C&E.
# LIC-8101 sits below DR-7001 on its nozzle N4 under the drum; its signal line reaches HS-8101A
# round the left of P-8101A without crossing a pipe (the pumps, the minimum flow and the thermal
# relief each close a loop with the drum). HS-8101B sits below the discharge header, reached from
# HS-8101A along y 200; its measuring line up to P-8101B crosses LNG-8001 once: P-8101B lies inside
# the loops drum - pumps - minimum flow, so no line from outside reaches it without one crossing
# (accepted in checks/checks.yaml).
LIC_AT = (124, 124)
TRUNK_X = 90
LZT_AT = (192, 95)
HS_AT = {"A": (130, 186), "B": (190, 200)}
HS_SENSE = {"A": (130, 172.5), "B": (190, 172.5)}  # on the lower edge of the pump casings
HS_ROLE = {
    "A": "Duty pump in auto: started and stopped by LIC-8101 on its level band (signal line); passes the "
         "start/stop command on to HS-8101B when P-8101B is selected as the duty pump (signal line)",
    "B": "Standby pump in auto: started and stopped from LIC-8101 through HS-8101A when selected as the duty "
         "pump (signal line)",
}
pumps = {"A": pa, "B": pb}
for s in "BA":  # HS-8101B first: HS-8101A's signal line ends at it
    L.inst(sheet, f"HS-8101{s}", f"P-8101{s} motor start/stop (DCS)",
           f"Tied to P-8101{s} (run feedback). {HS_ROLE[s]}; I-802 starts both pumps at high-high level "
           f"(whichever is not running) and yields to I-803, which stops both at low-low level (LZT-8105, "
           f"D-026.14). Hand-off-auto selector at the MCC, local stop at the pump (D-026.11).",
           at=HS_AT[s], sensing=pumps[s]["N2"], sensing_at=HS_SENSE[s],
           **({"signal_to": "Inst_HS8101B", "signal_points": [(HS_AT["A"][0], HS_AT["B"][1])]} if s == "A"
              else {}))
L.inst(sheet, "LIC-8101", "Flare knock-out drum level",
       "Starts and stops the duty pump on its level band (signal line to HS-8101A, on to HS-8101B); I-803 "
       "stops both at low-low level (LZT-8105); I-802 starts both at high-high (whichever is not running) "
       "and yields to I-803 (D-026.14).",
       at=LIC_AT, sensing=drum["N4"], signal_to="Inst_HS8101A",
       signal_points=[(TRUNK_X, LIC_AT[1]), (TRUNK_X, HS_AT["A"][1])])
L.inst(sheet, "LZT-8105", "Flare knock-out drum level high-high and low-low (independent of LIC-8101)",
       "Own nozzle N6 on D-8101, independent of LIC-8101: high-high (LAHH, C&E I-802) starts both pumps "
       "P-8101A/B (whichever is not running) and closes LV-7102 against liquid carry-over to FL-8101, "
       "non-latching and yielding to I-803; low-low (LALL, C&E I-803) stops P-8101A/B (D-026.14).",
       at=LZT_AT, sensing=drum["N6"])
L.inst(sheet, "FI-8133", "Flare flow (ultrasonic)", "Monthly-average routine flow against the permit limit (S-02).",
       at=(255, 128), sensing="Line_FL8002_S1", sensing_at=(240, 128))
L.inst(sheet, "TI-8131", "Pilot flame temperature (thermocouples)", "Pilot failure alarm.", at=(340, 115),
       sensing="Line_FG8002_S1", sensing_at=(340, 95))
L.inst(sheet, "TSL-8102", "Tank-area sump low temperature (LNG in the sump)",
       "Stops P-8102 and starts the high-expansion foam (C&E I-801).", at=(20, 208),
       sensing=sump["N2"])
L.inst(sheet, "LI-8103", "Tank-area sump level", "Starts and stops P-8102.", at=(20, 238), sensing=sump["N3"])
L.inst(sheet, "TSL-8104", "Jetty sump low temperature (LNG in the sump)",
       "Alarm and high-expansion foam on the platform (D-018).", at=(130, 240), sensing=jsump["N1"])
L.inst(sheet, "PI-8121", "N2 header pressure", at=(225, 220), sensing=n2.segments[0], sensing_at=(225, 210))
L.inst(sheet, "PI-8122", "Instrument-air header pressure", at=(232, 236),
       sensing=ia.segments[0], sensing_at=(232, 246))

note(sheet, "FL-8101: the storage and loading flare, one of four flares on the site's 122 m vapour flare derrick", at=(12, 252))
note(sheet, "(warm/wet, cold/dry, storage and loading, spare); derrick and liquid burner are site scope (S-02, D-001, D-017).", at=(12, 258))
note(sheet, "T-8101 / T-8102: LNG spill impoundment sumps, tank area and trestle troughs / loading platform (D-018).", at=(12, 264))
note(sheet, "TSL-8102: see C&E I-801. LZT-8105 (independent of LIC-8101): I-802 at high-high starts both pumps", at=(12, 270))
note(sheet, "P-8101A/B (whichever is not running) and closes LV-7102; non-latching, it yields to I-803.", at=(12, 276))
note(sheet, "FL-8001 also receives BOG-4013 (carrier de-inerting and cool-down vapour, P-04) and FL-7003", at=(150, 252))
note(sheet, "(BOG compressor depressurising vents, P-07). FO-8107: minimum-flow orifice of P-8101A/B.", at=(150, 258))
note(sheet, "T-8102: no fixed pump; rainwater is removed by a portable pump once TSL-8104 confirms no LNG", at=(150, 264))
note(sheet, "in the sump (D-018). FL-8101 pilot ignition (flame-front generator) and re-ignition on pilot", at=(150, 270))
note(sheet, "failure (TI-8131) are part of the site's flare derrick package (S-02).", at=(150, 276))
note(sheet, "HV-8106A/B, HV-8108A/B: suction and discharge isolation of P-8101A/B for maintenance.", at=(150, 282))
# Rev D notes after the existing ones (ids Note12 on). The third I-802/I-803 line of the left column:
note(sheet, "I-803 at low-low stops P-8101A/B (D-026.14). HS-8101A/B: motor control.", at=(12, 282))
# HV-8106A/B cavity vent (D-026.14): in the free field right of the outgoing headers, above the
# title block, and a text at each valve on its drum (upstream, upper) side.
VN = (300, 236)
for i, txt in enumerate([
        "HV-8106A/B: cryogenic ball valves with the cavity vented to the drum side, so a pump",
        "blocked in between HV-8106x and HV-8108x relieves into D-8101; drain the pump to the",
        "drum before maintenance (D-026.14)."]):
    note(sheet, txt, at=(VN[0], VN[1] + 6 * i))
for x in (116, 176):  # HV-8106A, HV-8106B
    note(sheet, "cavity vent: drum side", at=(x + 3, 146))

L.finish(sheet, target)
