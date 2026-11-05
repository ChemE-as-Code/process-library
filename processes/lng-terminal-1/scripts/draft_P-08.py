"""Draft of P-08: the storage and loading flare header, its knock-out drum D-8101 and pumps to
the liquid burner, the storage and loading flare FL-8101 with purge and pilot gas; the LNG
spill impoundment sumps of the tank area and the jetty; the N2 and instrument-air headers.

Provenance only: P-08 is hand-maintained after this first revision. Run:
cheme run scripts/draft_P-08.py pid/P-08.xml (on the empty A3 frame).
Decisions D-017, D-018, D-020, D-021; flares from BCER air permit PA-110588 (S-02).
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lng_pid import Lists, Nozzle, Sheet, equipment, note, offpage, tee, valve  # noqa: E402

target = Path(sys.argv[1])
sheet = Sheet.load(target)
L = Lists("P-08")
UP, DOWN, LEFT = 270, 90, 180
HY = 60

drum = equipment(sheet, "PressureVessel", "D-8101", shape="VESSEL_WITH_DISHED_HEADS_SHAPE",
                 at=(150, 100), rotation=90, scale=1.5,
                 nozzles=[Nozzle("N1", (-15, -15), 900), Nozzle("N2", (15, -15), 900),
                          Nozzle("N3", (0, 15), 100), Nozzle("N4", (-22.5, -5), 50),
                          Nozzle("N5", (-22.5, 7), 50)],
                 label_at=(150, 78))
flare = equipment(sheet, "Flare", "FL-8101", shape="FLARE_SHAPE", at=(300, 95), scale=2.0,
                  nozzles=[Nozzle("N1", (0, 24.7), 900), Nozzle("N2", (25, 0), 50)], label_at=(316, 74))
pa = equipment(sheet, "CentrifugalPump", "P-8101A", shape="CENTRIFUGAL_PUMP_SHAPE", at=(130, 165),
               nozzles=[Nozzle("N1", (-7.5, 0), 100), Nozzle("N2", (7.5, 0), 80)], label_at=(124, 177))
pb = equipment(sheet, "CentrifugalPump", "P-8101B", shape="CENTRIFUGAL_PUMP_SHAPE", at=(190, 165),
               nozzles=[Nozzle("N1", (-7.5, 0), 100), Nozzle("N2", (7.5, 0), 80)], label_at=(184, 177))

# ---- flare header and knock-out drum -------------------------------------------------------------
t1 = tee("T8F1", at=(40, HY), branch="up", branch_dn=200)
t2 = tee("T8F2", at=(64, HY), branch="up", branch_dn=200)
t3 = tee("T8F3", at=(88, HY), branch="up", branch_dn=50)
hdr = L.line(sheet, "FL-8001", dn=900, fluid="Flare gas", frm="BOG-1001 (PV-1110)", to="D-8101", insulation="none",
             notes="see P-01",
             route=[offpage("in", at=(12, HY), note="from PV-1110 (P-01)", note_at=(20, HY + 7)), t1, t2, t3,
                    (135, HY), drum["N1"]],
             label_at=(112, HY - 8))
for tt, x, txt, num, frm in [(t1, 40, "PSV-7105", "FL-7001", "BOG-1001 (PSV-7105)"), (t2, 64, "PSV-7111", "FL-7002", "BOG-7002 (PSV-7111)")]:
    L.line(sheet, num, dn=200, fluid="Flare gas", frm=frm, to="FL-8001", insulation="none",
           notes="see P-07",
           route=[offpage("in", at=(x, 34), note=f"{txt} (P-07)", note_at=(x, 27), rotation=DOWN), tt.branch], labels=False)
L.line(sheet, "FG-8001", dn=50, fluid="Fuel gas", frm="BL (fuel gas)", to="FL-8001", insulation="none",
       notes="Continuous purge of the flare header (part of the 6.0 m3/min routine limit with pilots and seal gas, S-02).",
       route=[offpage("in", at=(88, 34), note="purge gas", note_at=(88, 27), rotation=DOWN),
              valve("FO8111", "GlobeValve", tag="FO-8111", at=(88, 46)), t3.branch], labels=False)
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
       notes="Knock-out drum pump suction header.",
       route=[drum["N3"], t_s, (150, 135), (116, 135), (116, 165), pa["N1"]], label_at=(104, 150))
L.line(sheet, "LNG-8003", dn=100, fluid="LNG", frm="LNG-8002", to="P-8101B",
       notes="P-8101B suction.", route=[t_s.branch, (176, 126), (176, 165), pb["N1"]], labels=False)
t_d = tee("T8D1", at=(205, 190), branch="up", branch_dn=80)
L.line(sheet, "LNG-8001", dn=80, fluid="LNG", frm="P-8101A", to="BL (liquid burner)",
       notes="Liquids to the 60 m liquid burner derrick of the site (9 burners, S-02), 30 m3/h.",
       route=[pa["N2"], (145, 165), valve("CV8102A", "SwingCheckValve", at=(145, 178)), (145, 190), t_d,
              offpage("out", at=(285, 190), note="to liquid burner (BL)", note_at=(268, 196))],
       label_at=(245, 184))
L.line(sheet, "LNG-8004", dn=80, fluid="LNG", frm="P-8101B", to="LNG-8001",
       notes="P-8101B discharge.", route=[pb["N2"], (205, 165), valve("CV8102B", "SwingCheckValve", at=(205, 178)), t_d.branch], labels=False)

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
L.inst(sheet, "PI-8112", "Flare header pressure", at=(112, 74), sensing=hdr.segments[-1], sensing_at=(112, HY))
L.inst(sheet, "FI-8111", "Flare header purge gas flow", "Purge set by the orifice FO-8111.", at=(102, 40),
       sensing="Line_FG8001_S1", sensing_at=(88, 40))
L.inst(sheet, "LIC-8101", "Flare knock-out drum level", "Starts and stops P-8101A/B; high-high alarm.",
       at=(110, 95), sensing=drum["N4"])
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

note(sheet, "FL-8101: the storage and loading flare, one of four flares on the site's 122 m vapour flare derrick", at=(12, 258))
note(sheet, "(warm/wet, cold/dry, storage and loading, spare); derrick and liquid burner are site scope (S-02, D-001, D-017).", at=(12, 264))
note(sheet, "T-8101 / T-8102: LNG spill impoundment sumps, tank area and trestle troughs / loading platform (D-018).", at=(12, 270))
note(sheet, "TSL-8102: see C&E I-801.", at=(12, 276))

L.finish(sheet, target)
