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

Rev E (review 2026-11-05-basic-design-4 #1, #5, #9, D-028): the instrument-air header low-low trip
PZT-8123A/B/C (2oo3, C&E I-804) on IA-8001, which initiates ESD-1 of both berths and the rundown
trip before any fail-closed valve moves; IA-8001 starts further left (x 178) to take the three
transmitters beside PI-8122. CV-8102A/B get a disc with a pressure-equalising hole, so the spool
between the check valve and HV-8108x relieves back to the pump side and through the HV-8106x cavity
vent into D-8101 (the note is corrected). N-8001: purge and leak test only, no blanketing (D-020).
The new notes come after the existing ones (ids kept).

Rev G (review 2026-11-05-basic-design-8 #3, #9 and the adversarial check of layout review
2026-11-05-basic-layout-6, D-036): the riser W-8002 of P-8102 takes a check valve CV-8114 and an
isolation valve HV-8115 above the pit cover, P-8102 is re-rated for the 19.5 m pit, TSL-8102's tip sits
below the pump intake and I-801 opens the pump's feeder; T-8102 takes the level transmitter LZT-8106
(radar through the cover, N2) with a high alarm for the pump-down and a high-high, C&E I-805, that keeps
the sump's room for the design spill and the trestle drain-down.

Rev H (D-037.16, the design owner's answer to D-037.15 (a), independent check of D-037): T-8102 is kept
dry at the start of and during every transfer. The fixed dry-sump pump P-8103 (vertical line-shaft pump,
its bowl in the ~0.25 m3 floor pocket, its motor on the sump cover, no motor in the sump) discharges
through W-8003 with the check valve CV-8116 and the isolation valve HV-8117 above the cover to the jetty
drain at the edge of the sump deck A9. LZT-8106 now reads the pocket: P-8103 start and stop (C&E I-806 /
I-807), LAH at the pocket rim as a transfer hold, LAHH 0.1 m above the sump floor (C&E I-805); TSL-8104
locks P-8103 out on LNG (C&E I-808). The portable pump stays a spare means, not the basis.
With D-037.17 (independent check of D-037.16, same revision, not yet issued): a second, independent LNG
detection TSL-8118 on the P-8103 discharge head (W-8003 upstream of CV-8116), voted 1oo2 with TSL-8104 in
I-808; TSL-8104's tip stated at 0.40 m in the pocket (above the pump start level); CV-8116 with a drain-back
hole in its disc so that nothing stands above the cover when the pump stops (freezing, -20 degC design
ambient); LZT-8106 a guided-wave radar in a stilling pipe down to the pocket.

Migration to core 1.11.0 (D-038), drawing only: LNG-8001 ends on the right edge; the N2 header comes in
on the right edge above its two outlets to the berths (tee T8N1 at x 300, PI-8121 on its drop); W-8002
and W-8003 go down to the bottom edge (TSL-8104 6 mm higher); IA-8001's outlet turns down onto it.

Rev J (review 2026-11-05-basic-design-9 #1, #4, #8 (d), its adversarial check and the P&ID part of layout
review 2026-11-05-basic-layout-7, D-039): T-8101 is kept dry as T-8102. P-8102 stands in a floor pocket of
the pit, its submergence in the pocket; LI-8103 is its level control (signal line to the new motor
start/stop function HS-8103, as LIC-8101 to HS-8101A); the new independent LZT-8113 (own nozzle N3) gives
the LAH at the pocket rim, the LAHH over the floor (C&E I-809) and the rate-of-rise inhibit of P-8102
(C&E I-810). LNG detection that sees LNG in a wet pit: TSL-8102's tip above the pump's start level in the
pocket, the new fast-response TSL-8120 in the P-8102 discharge (W-8002 upstream of CV-8114), and the rim
gas detection AT-8124 (own nozzle N4, F&G), any of them in C&E I-801, which also starts the foam from
detection that is never under water. CV-8114 takes a drain-back hole so that W-8002 empties when P-8102
stops (freezing). T-8102: the new LZT-8119 (own nozzle N3) gives the LAH transfer hold and I-805, so
LZT-8106 is the P-8103 control alone. The B-SUB intake gas detection AT-8141A/B/C with the AHU-1 damper
trip UZ-8142 / UZ-8143 and the fan stop UZ-8144 (C&E I-811) is drawn as stand-alone functions (no HVAC sheet).

Round-10 design check (D-039.9), notes only: P-8102 is fed through a VSD with its speed following the pocket
level between the start and the stop (HS-8103, loop LC-8103), so it runs on in steady rain instead of ~22
direct-on-line starts an hour; a bad LZT-8113 signal is taken as its LAH (a transfer hold); the small-inflow
coverage of I-801 is stated on TSL-8102 / TSL-8120.
"""

import sys
from dataclasses import replace
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from chemeascode.domains.piping.authoring import label  # noqa: E402
from lng_pid import (  # noqa: E402
    Lists, Nozzle, Sheet, edge_offpage, equipment, note, offpage, tee, to_orifice, valve)

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
             "PSV-8109 (LNG-8006) to D-8101 on the common section downstream of HV-8108A/B (H-05 A3); the spool "
             "between CV-8102A and HV-8108A relieves back through the pressure-equalising hole of the check valve "
             "disc and the HV-8106A cavity vent into D-8101 (review 2026-11-05-basic-design-4 #5, D-028).",
       route=[pa["N2"], (145, 165), valve("CV8102A", "SwingCheckValve", tag="CV-8102A", at=(145, 172)),
              valve("HV8108A", "BallValve", tag="HV-8108A", at=(145, 182)), (145, 190), t_d, t_m,
              t_r, edge_offpage("out", "right", 190, note="to liquid burner (BL)", note_at=(388, 185))],
       label_at=(257, 184))
psv8109 = L.relief("PSV8109", "PSV-8109", "LNG-8006", 15.0,
                   "thermal expansion of LNG blocked in the common discharge LNG-8001 between the discharge "
                   "isolations HV-8108A/B (or the check valves CV-8102A/B) and the battery-limit valve (pumps "
                   "stopped, liquid burner isolated)",
                   "Thermal relief of the knock-out drum pump common discharge LNG-8001 back to D-8101 "
                   "through LNG-8006 (HAZOP H-05 A3); DN 25, set at the 15 barg design of the line.",
                   label_at=(RX + 12, 166))
L.line(sheet, "LNG-8004", dn=80, fluid="LNG", frm="P-8101B", to="LNG-8001",
       notes="P-8101B discharge: check valve CV-8102B, then the discharge isolation HV-8108B (review 2 #7); the "
             "spool between them relieves back through the pressure-equalising hole of the CV-8102B disc and the "
             "HV-8106B cavity vent into D-8101 (D-028).",
       route=[pb["N2"], (205, 165), valve("CV8102B", "SwingCheckValve", tag="CV-8102B", at=(205, 172)),
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
for vid in ("FO8111", "FO8107"):     # restriction orifices drawn as such (checker of D-036)
    to_orifice(sheet, vid)

# ---- spill impoundment sumps -------------------------------------------------------------------
# T-8101 is a 19.5 m deep pit (D-035.2): no wall penetration. The rainwater pump P-8102 is a
# submersible pump on the pit floor with its riser W-8002 up through the pit cover; the level (radar,
# N1) and the low-temperature probe (N2) enter through the cover too (review 2026-11-05-basic-design-7
# #6 and its adversarial check, D-034; was a grade pump on a pit-bottom suction W-8001).
# Rev J (D-039): T-8101 kept dry as T-8102: N1 (LI-8103) and N2 (TSL-8102) move left so that HS-8103's
# measuring line can reach P-8102 through the open top; N3 is the independent level LZT-8113, N4 the rim gas
# detection AT-8124 (both on the left shell, through the cover in the field).
sump = equipment(sheet, "Tank", "T-8101", shape="TANK_OPEN_SHAPE", at=(40, 222),
                 nozzles=[Nozzle("N1", (-6, -11), 150), Nozzle("N2", (-12, -11), 50),
                          Nozzle("N3", (-15, 2), 100), Nozzle("N4", (-15, -9), 25)],
                 label_at=(40, 238))
spump = equipment(sheet, "CentrifugalPump", "P-8102", shape="CENTRIFUGAL_PUMP_SHAPE", at=(46, 226), scale=0.7,
                  nozzles=[Nozzle("N2", (0, -7.5), 100)], label_at=(66, 226))
# check valve and isolation valve on the riser above the pit cover (review 2026-11-05-basic-design-8 #3, D-036):
# no back-flow from the oily water system into the impoundment through a stopped pump, and the pump can be
# isolated and pulled on its guide rail; since D-039 CV-8114 has a drain-back hole (as CV-8116) so that the
# riser empties back into the pocket and the run on PR8 to the battery limit when the pump stops
w_cv = valve("CV8114", "SwingCheckValve", tag="CV-8114", at=(70, 209))
w_hv = valve("HV8115", "BallValve", tag="HV-8115", at=(84, 209))
L.line(sheet, "W-8002", dn=100, fluid="Rainwater", frm="P-8102", to="BL (oily water)", insulation="none",
       notes="Riser of the submersible rainwater pump P-8102 from the floor pocket of T-8101 (the pit kept dry, D-039) up through the pit cover, then along PR8 to the site oily water system; interlocked off on LNG in the sump (C&E I-801, the feeder isolated; TSL-8120 in its flow upstream of CV-8114). Static lift ~27.8 m from the pocket floor, 1.2 m below the 19.5 m pit floor, to the PR8 rack (D-036, D-039). Check valve CV-8114 and isolation valve HV-8115 above the pit cover (no back-flow into the impoundment, the pump pulled with the riser isolated). Self-draining against freezing (design ambient -20 degC; adversarial check of review 2026-11-05-basic-design-9, D-039, as W-8003 in D-037.17): CV-8114 has a drain-back hole in its disc (~6 mm, ASSUMED), so when P-8102 stops the riser drains back through the pump into the pocket (~0.23 m3, ~0.10 m of pocket level, below the start level) and the run on PR8 is laid to fall to the battery limit (ASSUMED, layout), so no water stands above the cover; no heat tracing. Austenitic stainless steel from the pump to the isolation valve, design -170 degC (the first item a spill reaches, D-036), ASSUMED.",
       # down to the bottom edge (core 1.11 cheme.offpage-not-on-edge, D-038), left of W-8003's drop
       route=[spump["N2"], (46, 209), w_cv, w_hv, (96, 209),
              edge_offpage("out", "bottom", 96, note="to oily water (BL)", note_at=(79, 245.5))],
       label_at=(83, 218))
for v in (w_cv, w_hv):
    label(sheet, v.id, "PipingComponentNumber", at=(v.at[0], 204))
# N3 (D-039): the trip level transmitter LZT-8119, independent of LZT-8106 (review 2026-11-05-basic-design-9 #4)
jsump = equipment(sheet, "Tank", "T-8102", shape="TANK_OPEN_SHAPE", at=(160, 225),
                  nozzles=[Nozzle("N1", (-15, 0), 50), Nozzle("N2", (15, -6), 50), Nozzle("N3", (-15, -3), 100)],
                  label_at=(160, 240))
# Dry-sump pump of T-8102 (D-037.16, answering D-037.15 (a)): a vertical line-shaft pump whose bowl stands
# in the floor pocket and whose motor stands on the sump cover, so no motor is in the sump; drawn in the
# sump with its discharge up through the cover, as P-8102 in T-8101. Check valve and isolation valve above
# the cover, then to the jetty drain at the edge of the sump deck A9 (battery limit).
dpump = equipment(sheet, "CentrifugalPump", "P-8103", shape="CENTRIFUGAL_PUMP_SHAPE", at=(166, 229), scale=0.7,
                  nozzles=[Nozzle("N2", (0, -7.5), 80)], label_at=(185, 227.5))
d_cv = valve("CV8116", "SwingCheckValve", tag="CV-8116", at=(161, 211))
d_hv = valve("HV8117", "BallValve", tag="HV-8117", at=(148, 211))
L.line(sheet, "W-8003", dn=80, fluid="Rainwater", frm="P-8103", to="BL (jetty drain)", insulation="none",
       notes="Discharge of the dry-sump pump P-8103 from the T-8102 floor pocket up through the sump cover to the "
             "jetty drain at the edge of the sump deck A9 (battery limit; its outfall, treatment and consent the "
             "civil and environmental owners', ASSUMED): ~20 m3/h of rain, ~1.1 m/s in DN 80. Check valve CV-8116 "
             "(no full reverse flow and reverse spin through a stopped pump) with a drain-back hole in its disc "
             "(~6 mm, ASSUMED) and isolation valve HV-8117 (the pump pulled with its column isolated) above the "
             "cover. Self-draining against freezing (design ambient -20 degC, D-037.17): when the pump stops, the "
             "column, the discharge head and the riser drain back through the disc hole and the bowl into the "
             "pocket (air enters from the open end at the drain), and the overhead run and the drop drain to the "
             "jetty drain (laid to a fall, ASSUMED), so no water stands above the cover; no heat tracing. Austenitic "
             "stainless steel from the pump to the battery limit, design -170 degC (an LNG spill reaches the pump "
             "first), ASSUMED. Started and stopped by LZT-8106 in the pocket (C&E I-806 / I-807), locked out on LNG "
             "by TSL-8104 in the pocket or TSL-8118 on the discharge head (1oo2, C&E I-808); D-037.15 (a), "
             "D-037.16, D-037.17.",
       # down to the bottom edge between W-8002's drop and TSL-8104 (core 1.11, D-038)
       route=[dpump["N2"], (166, 211), d_cv, d_hv, (113, 211),
              edge_offpage("out", "bottom", 113, note="jetty drain (BL)", note_at=(128, 245.5))],
       label_at=(155.5, 219))
for v in (d_cv, d_hv):
    label(sheet, v.id, "PipingComponentNumber", at=(v.at[0], 206.5))

# ---- N2 and instrument-air headers ----------------------------------------------------------------
# The site N2 comes in on the right edge above the two outlets to the berths, so that all three
# connectors sit on the edge without a crossing (core 1.11 cheme.offpage-not-on-edge, D-038)
tn = tee("T8N1", at=(300, 214), branch="down", branch_dn=50)
n2 = L.line(sheet, "N-8001", dn=80, fluid="Nitrogen", frm="BL (site N2)", to="LNG-5001", insulation="none",
            notes="Terminal N2 header from the site system, 7 barg, to Berth 2 (and via N-8002 to Berth 1): purging the arms and headers to < 1 % O2 before and < 2 % HC after loading and the leak test at 5 bar (liquid) / 2.5 bar (vapour arm) (S-01); these are its only users (D-020, D-028). Drawn on P-08 and P-05.",
            route=[edge_offpage("in", "right", 202, note="N2 (BL)", note_at=(394, 197)), (250, 202), (250, 214),
                   tn, edge_offpage("out", "right", 214, note="to Berth 2 (P-05)", note_at=(388, 209))],
            label_at=(272, 220))
L.line(sheet, "N-8002", dn=50, fluid="Nitrogen", frm="N-8001", to="LNG-6001", insulation="none",
       notes="N2 to Berth 1. Drawn on P-08 and P-06.", route=[tn.branch, (300, 226),
                                     edge_offpage("out", "right", 226, note="to Berth 1 (P-06)", note_at=(388, 221))],
       labels=False)
IA_X = 178  # IA-8001 starts left of the N2 header to take PI-8122 and PZT-8123A/B/C (D-028)
ia = L.line(sheet, "IA-8001", dn=50, fluid="Instrument air", frm="BL (site instrument air)", to="instrument users",
            insulation="none",
            notes="Instrument-air header of the terminal, 7 barg (D-020); low-low pressure trip PZT-8123A/B/C (2oo3, "
                  "C&E I-804) initiates ESD-1 of both berths and the rundown trip before the fail-closed valves "
                  "move (D-016, D-028).",
            # its outlet turns down onto the bottom edge (core 1.11 cheme.offpage-not-on-edge, D-038)
            route=[offpage("in", at=(IA_X, 246), note="IA (BL)", note_at=(IA_X + 5, 240)),
                   offpage("out", at=(288, 246), note="to users", note_at=(277, 250), rotation=DOWN)],
            label_at=(264, 240))

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
# T-8101 kept dry (review 2026-11-05-basic-design-9 #1 and its adversarial check, D-039): P-8102 in a floor pocket
# (~1.5 x 1.5 m, 1.2 m deep, ~2.7 m3, ASSUMED) into which the pit floor falls; levels from the pocket floor.
TSUMP = ("T-8101 is kept dry (D-039): water only in its floor pocket (~1.5 x 1.5 m, 1.2 m deep, ~2.7 m3, ASSUMED; "
         "the pit floor laid to fall to it, civil), where the submersible P-8102 stands with its ~0.5 m submergence. ")
L.inst(sheet, "HS-8103", "P-8102 motor start/stop and speed (DCS, VSD)",
       "Tied to P-8102 (run feedback). Started and stopped by LI-8103 on its level band in the pocket (signal line): "
       "start at 0.90 m, stop at 0.60 m above the pocket floor (ASSUMED; the stop keeps the ~0.5 m submergence of the "
       "submersible over its intake, vendor), its speed following the level in between through the VSD in MCC-1 "
       "(round-10 design check, D-039.9; as P-8103), loop LC-8103 (control/loops.yaml). Minimum speed ~75 % (ASSUMED), "
       "where the pump still delivers ~20 m3/h against the ~27.8 m static: at an inflow above that it runs on, below it "
       "it cycles at most ~9 times an hour (at ~9 m3/h of inflow, with the riser's ~0.23 m3 drain-back), each start a "
       "VSD ramp, against ~22 direct-on-line starts an hour at the ~20 m3/h design rain with the 0.30 m band; "
       "vendor limit taken as 15 starts an hour, evenly spaced (ASSUMED, submersible motor of this size, vendor to "
       "confirm). The feeder trip I-801 (LNG) and the rate-of-rise inhibit I-810 act on the pump from the C&E and have "
       "priority. Hand-off-auto selector at the MCC.",
       at=(42, 184), sensing=spump["N2"], sensing_at=(42, 222.6))  # down through the open top onto the casing
L.inst(sheet, "TSL-8102", "Tank-area sump low temperature in the P-8102 pocket (LNG in the sump)",
       TSUMP + "Probe hung from the pit cover (N2) into the pocket beside P-8102, no wall penetration (D-034); its tip "
       "1.0 m above the pocket floor (ASSUMED): above the pump's start level (0.90 m), so in normal service it stands "
       "in air and sees LNG flowing into the pocket or lying on its water, never under standing water, and below the "
       "rim (1.2 m) (was at the pit floor under the water, review 2026-11-05-basic-design-9 #1). Trips at -60 degC "
       "(ASSUMED: below the -20 degC design ambient of an empty pocket, far above LNG). 1oo2 with TSL-8120 on the "
       "discharge, with the rim gas detection AT-8124 as a third cause: any of them opens P-8102's motor feeder "
       "(latching, C&E I-801); the F&G system starts the T-8101 high-expansion foam on the same detections (D-018). "
       "Coverage (round-10 design check, D-039.9): it sees a large inflow, which raises the pocket to its tip or wets it "
       "as it falls in; a small inflow (a flange drip from the troughs) that keeps the pocket below 1.0 m is seen only "
       "by TSL-8120 once the pump draws it (1oo1; AT-8124 where its vapour reaches the rim, not credited), a residual "
       "for H-05 / H-06; no vapour cooling of the tip is credited.",
       at=(14, 203), sensing=sump["N2"])
L.inst(sheet, "LI-8103", "Tank-area sump pocket level: P-8102 level control",
       TSUMP + "Radar through the pit cover (N1) aimed at the pocket, no wall penetration (D-034). Control only (D-039): "
       "starts P-8102 at 0.90 m and stops it at 0.60 m above the pocket floor through HS-8103 (signal line; loop LC-8103, "
       "ASSUMED), its VSD speed following the level in between (D-039.9). The alarms and trips are on the independent LZT-8113, with a deviation alarm between the two.",
       at=(34, 196), sensing=sump["N1"], signal_to="Inst_HS8103", signal_points=[(34, 178), (42, 178)])
L.inst(sheet, "LZT-8113", "Tank-area sump level, independent: high (pocket rim), high-high and rate of rise",
       TSUMP + "Own nozzle N3, a second radar through the pit cover aimed at the pocket, independent of LI-8103 "
       "(D-039; ASSUMED, vendor); levels from the pocket floor. LAH at 1.20 m, the pocket rim (water on the pit floor: "
       "P-8102 failed, W-8002 blocked or the inflow above its 50 m3/h): a transfer hold (SEQ-LOAD S0 / S4) and the "
       "call to restore P-8102 (from road R13, outside the transfer area) or to lower the portable spare pump; LAHH at "
       "1.30 m, 0.1 m over the pit floor (~20 m3 with the pocket): C&E I-809 blocks the start of a transfer and during "
       "one trips ESD-1 of the transferring berth, since the governing tank-area spill is the loading pumps' run-out "
       "(D-034.3). Rate of rise (C&E I-810): a rise faster than an inflow of ~250 m3/h (ASSUMED, ~10 x the design rain "
       "on the troughs and the pit; the DCS converts the level rate with the pocket and floor areas) inhibits P-8102: a "
       "spill raises the level metres in minutes, rain millimetres. Deviation alarm against LI-8103. Bad signal "
       "(round-10 design check, D-039.9; as LZT-8119, D-039.4): alarmed and taken as its LAH, a transfer hold (no "
       "transfer starts, a transfer in progress is paused, SEQ-LOAD S0 / S4), not as the I-809 trip; a PR8 cable burnt "
       "in a tank-area fire comes with that fire's own confirmed fire and gas cause of ESD-1.",
       at=(12, 224), sensing=sump["N3"])
L.inst(sheet, "AT-8124", "T-8101 pit rim flammable gas (F&G)",
       "Flammable gas detection at the rim of the T-8101 pit (point IR heads round the rim at the cover, voted by the "
       "fire and gas system, ASSUMED, F&G vendor), drawn on its own nozzle N4: it is never under water. LNG in the pit "
       "boils off and its cold vapour fills the pit and spills over the rim, so it detects a spill without depending on "
       "a probe reaching the liquid; with TSL-8102 and TSL-8120 it starts the T-8101 high-expansion foam (F&G, D-018) "
       "and is a cause of C&E I-801 (P-8102's feeder opened) (review 2026-11-05-basic-design-9 #1, D-039).",
       at=(12, 213), sensing=sump["N4"])
L.inst(sheet, "TSL-8120", "P-8102 discharge low temperature (LNG drawn by the pit pump)",
       "Second, independent LNG detection of P-8102, as TSL-8118 on P-8103 (D-037.17, D-039): a fast-response probe "
       "with its tip in the flow of W-8002 upstream of CV-8114 (ASSUMED, no thermowell), own SIS input and cable. Trips "
       "at -60 degC (ASSUMED; the riser is empty and at ambient between runs since CV-8114 drains back). 1oo2 with "
       "TSL-8102 in C&E I-801 (either opens P-8102's feeder, latching), so LNG the pump draws from under water in the "
       "pocket stops it within seconds of reaching the riser, before it passes the check valve in any quantity "
       "(residual: those seconds of flow, H-05). For a small inflow that keeps the pocket below TSL-8102's tip it is "
       "the only credited detection (1oo1, D-039.9), a residual for H-05 / H-06.",
       at=(57, 197), sensing="Line_W8002_S1", sensing_at=(57, 209))
L.inst(sheet, "TSL-8104", "Jetty sump low temperature (LNG in the sump)",
       "Probe hung from the cover into the T-8102 floor pocket beside the P-8103 bowl, its tip 0.40 m above the pocket "
       "floor (ASSUMED): above the pump's start level (0.35 m), so in normal service it stands in air and sees LNG "
       "flowing into the pocket or lying on its water, and below the rim (0.50 m). Trips at -60 degC (ASSUMED: below "
       "the -20 degC design ambient of an empty pocket in winter, far above LNG). Alarm and high-expansion foam on the "
       "platform (D-018); C&E I-808 locks the dry-sump pump P-8103 out (its feeder opened, latching), 1oo2 with "
       "TSL-8118 on the discharge head, and the portable pump may be used only while it reads no LNG (D-034, D-036, "
       "D-037.16, D-037.17).", at=(130, 234), sensing=jsump["N1"])  # above the W-8003 note (D-038)
L.inst(sheet, "TSL-8118", "P-8103 discharge head low temperature (LNG drawn by the dry-sump pump)",
       "Second, independent LNG detection of the dry-sump pump (D-037.17): a fast-response probe with its tip in the "
       "flow of the discharge head, upstream of CV-8116 (ASSUMED, no thermowell), own SIS input and cable. Trips at "
       "-60 degC (ASSUMED, as TSL-8104; the head is empty and at ambient between runs, D-037.17). Voted 1oo2 with "
       "TSL-8104 in C&E I-808 (either opens P-8103's feeder, latching) and a start permissive of I-806, so a failure "
       "of TSL-8104 to see LNG in the pocket stops the pump within seconds of LNG reaching the head, before it passes "
       "the check valve in any quantity (residual: the seconds of flow, H-05).",
       at=(183, 212), sensing="Line_W8003_S1", sensing_at=(166, 212))
L.inst(sheet, "LZT-8106", "Jetty sump T-8102 pocket level: P-8103 start / stop (control)",
       "Guided-wave radar from the sump cover (N2, drawn on the shell for clarity), its probe in a stilling pipe from "
       "the cover bracket down to the floor of the pocket (~0.8 m across, 0.5 m deep, ~0.25 m3), so the P-8103 column "
       "and the TSL-8104 probe in the pocket give no false echo and the ~13.5 m drop needs no beam (D-037.17; ASSUMED, "
       "vendor), no wall penetration (D-036, D-037.15 (a), D-037.16). Levels from the pocket floor, "
       "ASSUMED: P-8103 starts at 0.35 m (C&E I-806) and stops at 0.10 m (C&E I-807, the bowl's submergence), its "
       "speed following the level in between (VSD); loop LC-8106 (control/loops.yaml). Control only since D-039 "
       "(review 2026-11-05-basic-design-9 #4): the LAH transfer hold and the LAHH trip I-805 are on the independent "
       "LZT-8119, so a failure of this transmitter (P-8103 not started, the initiating event of water on the sump floor) "
       "no longer defeats the hold and the trip; a deviation between the two alarms.",
       at=(192, 219), sensing=jsump["N2"])
L.inst(sheet, "LZT-8119", "Jetty sump T-8102 level, independent: high (transfer hold) and high-high (I-805)",
       "Own nozzle N3, a second guided-wave radar in its own stilling pipe from the cover down to the pocket floor, "
       "independent of LZT-8106 (review 2026-11-05-basic-design-9 #4, D-039; ASSUMED, vendor), own SIS input and cable. "
       "Levels from the pocket floor, ASSUMED: LAH at 0.50 m, the pocket rim (water on the sump floor: P-8103 failed or "
       "the inflow above its ~20 m3/h), a transfer hold: no transfer starts (SEQ-LOAD S0) and a transfer in progress is "
       "paused (SEQ-LOAD S4) until the level is back below it, no one going to A9 during a transfer (S-CW-A9, D-037.3); "
       "LAHH at 0.60 m (0.1 m over the sump floor, ~3 m3 with the pocket): C&E I-805 inhibits the start of SEQ-LOAD and "
       "during a transfer trips ESD-1 of the transferring berth (I-501 / I-601: carrier tripped through its own link, "
       "D-016). So no LNG lands on standing water, and the 257 m3 below the inlet hold the ~170 m3 platform spill and "
       "the trestle drain-down of D-036 (~36 m3, 40 m3 kept) with no rain allowance (D-037.15 (a)). Deviation alarm "
       "against LZT-8106.",
       at=(130, 222), sensing=jsump["N3"])
L.inst(sheet, "PI-8121", "N2 header pressure", at=(238, 208), sensing=n2.segments[0], sensing_at=(250, 208))
L.inst(sheet, "PI-8122", "Instrument-air header pressure",
       "Indication and low alarm only; the trip is PZT-8123A/B/C (C&E I-804, D-028).", at=(199, 236),
       sensing=ia.segments[0], sensing_at=(199, 246))
# instrument-air header low-low trip (review 2026-11-05-basic-design-4 #1, D-028): three transmitters on
# their own tappings, 2oo3, set above the pressure at which the spring-return actuators start to stroke
for s, x in zip("ABC", (215, 231, 247)):
    L.inst(sheet, f"PZT-8123{s}", f"Instrument-air header pressure low-low (I-804), transmitter {s} of 2oo3",
           "Own tapping on IA-8001, independent of PI-8122; 2oo3 with the other two: at 4.5 barg (ASSUMED; header "
           "7 barg, the fail-closed spring-return actuators start to stroke below about 3.5 barg, ASSUMED) it "
           "initiates ESD-1 of both berths (pumps stopped, carriers tripped) and the rundown trip (trains tripped, "
           "battery-limit valves closed) before the valves move (C&E I-804, D-016, D-028).",
           at=(x, 236), sensing=ia.segments[0], sensing_at=(x, 246))
# B-SUB refuge (layout review 2026-11-05-basic-layout-7, adversarial check; layout review 5 #6; D-035.10, D-039):
# the gas trip of the AHU-1 outdoor-air intake LV1 (layout/hvac.yaml), drawn as stand-alone functions in the free
# field: no sheet of this plant draws the HVAC.
BSUB = ("B-SUB is the temporary refuge (layout/building.yaml, D-037.5); its gas-tightness rests on this trip "
        "(layout/hvac.yaml AHU-1, D-035.10). ")
for s, x in zip("ABC", (322, 340, 358)):
    L.inst(sheet, f"AT-8141{s}", f"B-SUB AHU-1 outdoor-air intake LV1 flammable gas, detector {s} of 2oo3",
           BSUB + "Point IR detector in the LV1 intake duct downstream of the louvre (ASSUMED, F&G vendor), own input "
                  "and cable to CR-1. Alarm at 10 % LFL (any one); trip at 25 % LFL, 2oo3 (ASSUMED), C&E I-811: AHU-1 "
                  "stopped, the gas-tight dampers UZ-8142 (LV1) and UZ-8143 (LV2) closed, the building held on its "
                  "stored overpressure. A detector fault alarms and counts as tripped (2oo3 degrades to 1oo2).",
           at=(x, 152))
for tag, louvre, at in [("UZ-8142", "outdoor-air intake LV1 (east wall)", (331, 168)),
                        ("UZ-8143", "exhaust LV2 (south wall)", (349, 168))]:
    L.inst(sheet, tag, f"B-SUB AHU-1 gas-tight damper, {louvre}",
           BSUB + "SIS output to the spring-return actuator of the gas-tight damper (fail closed on loss of power, "
                  "ASSUMED, HVAC vendor), closed by C&E I-811 with AHU-1 stopped; reopened by hand after the reset, "
                  "once the intake reads below the alarm.", at=at)
# the fan stop as its own SIS output, so the C&E effect is a drawn tag (D-039)
L.inst(sheet, "UZ-8144", "B-SUB AHU-1 fan stop (SIS output to its starter)",
       BSUB + "SIS output, de-energise-to-trip, to the AHU-1 fan starter in B-SUB (ASSUMED, HVAC vendor): C&E I-811 "
              "stops the fan before the dampers UZ-8142 / UZ-8143 have closed, so the fan does not draw against a closing "
              "intake; restarted by hand after the reset, once the dampers are open again.", at=(367, 168))

note(sheet, "FL-8101: the storage and loading flare, one of four flares on the site's 122 m vapour flare derrick", at=(12, 252))
note(sheet, "(warm/wet, cold/dry, storage and loading, spare); derrick and liquid burner are site scope (S-02, D-001, D-017).", at=(12, 258))
note(sheet, "T-8101 / T-8102: LNG spill sumps, tank-area troughs / platform (D-018); kept dry, pumps in floor pockets (D-039).", at=(12, 264))
note(sheet, "T-8101: I-801, I-809, I-810. LZT-8105 (independent of LIC-8101): I-802 at high-high starts both pumps", at=(12, 270))
note(sheet, "P-8101A/B (whichever is not running) and closes LV-7102; non-latching, it yields to I-803.", at=(12, 276))
note(sheet, "FL-8001 also receives BOG-4013 (carrier de-inerting and cool-down vapour, P-04) and FL-7003", at=(150, 252))
note(sheet, "(BOG compressor depressurising vents, P-07). FO-8107: minimum-flow orifice of P-8101A/B.", at=(150, 258))
note(sheet, "T-8102 kept dry: P-8103 (drive on the cover), I-806 / I-807 on LZT-8106, I-808 lockout on TSL-8104 / 8118 (1oo2);", at=(150, 264))
note(sheet, "LAH transfer hold, LAHH I-805 (LZT-8119). FL-8101 pilot ignition (flame-front generator) and re-ignition on pilot", at=(150, 270))
note(sheet, "failure (TI-8131) are part of the site's flare derrick package (S-02).", at=(150, 276))
note(sheet, "HV-8106A/B, HV-8108A/B: suction and discharge isolation of P-8101A/B for maintenance.", at=(150, 282))
# Rev D notes after the existing ones (ids Note12 on). The third I-802/I-803 line of the left column:
note(sheet, "I-803 at low-low stops P-8101A/B (D-026.14). HS-8101A/B: motor control.", at=(12, 282))
# HV-8106A/B cavity vent (D-026.14): in the free field right of the outgoing headers, above the
# title block, and a text at each valve on its drum (upstream, upper) side.
VN = (300, 236)
for i, txt in enumerate([
        "HV-8106A/B: cryogenic ball valves, cavity vented to the drum side; CV-8102A/B have a",
        "pressure-equalising hole in the disc, so a pump blocked in between HV-8106x and",
        "HV-8108x relieves into D-8101; drain the pump to the drum first (D-026.14, D-028)."]):
    note(sheet, txt, at=(VN[0], VN[1] + 6 * i))
for x in (116, 176):  # HV-8106A, HV-8106B
    note(sheet, "cavity vent: drum side", at=(x + 3, 146))
# Rev E notes (D-028), after the existing ones
note(sheet, "PZT-8123A/B/C: instrument-air header low-low, 2oo3, see C&E I-804 (ESD-1 of both berths, rundown trip).",
     at=(12, 288))
# Rev J notes (D-039), after the existing ones (ids kept): the B-SUB intake gas trip above its functions
note(sheet, "B-SUB AHU-1 outdoor-air intake LV1 (layout/hvac.yaml): gas trip", at=(310, 138))
note(sheet, "AT-8141A/B/C 2oo3, C&E I-811: AHU-1 stopped (UZ-8144), UZ-8142 / UZ-8143 closed.", at=(310, 143))

L.finish(sheet, target)
