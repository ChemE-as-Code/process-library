"""Draft of P-04: the trestle lines between the tank area and the loading platform: loading
lines A and B (DN 800) with their tank-end flow control and ESD valves, the tank-end and
platform crossovers, the circulation header with the spray take-off, the circulation return
to the tanks, thermal relief, and vapour return lines A and B (DN 750) with the switch of the
carrier de-inerting and cool-down vapour to the storage and loading flare (BOG-4013 / BOG-4014,
review 2026-11-05 #19); thermal relief of the tank-end crossover and the circulation return
(PSV-4113, PSV-4114, review #6, HAZOP H-02 A2); PSV-4111 / PSV-4112 at 15.0 barg (H-02 A11).

Generator of P-04 (plant.yaml `generator:`, frame pid/frames/P-04.xml): `cheme regen P-04`
rebuilds the sheet; change this script, never the XML (D-021).
Streams S2, S3, S6, S7, S10; decisions D-008, D-009, D-012, D-013, D-016, D-017, D-021.

Revision after the follow-up review 2026-11-05-basic-design-2 (#1, D-026.1 and D-026.11):
open-position switches ZSO-4131 / ZSO-4132 / ZSO-4135 / ZSO-4136 tied to their valves (sensor
on the valve's segment, as ZSC-5123 on P-05) for the make-before-break switch I-511..I-513 /
I-611..I-613; both switching valves fail open. The four DN 25 relief outlets BOG-4011, BOG-4012
(PSV-4111 / PSV-4112, now on the underside of the loading lines) and BOG-4015, BOG-4016
(PSV-4113 / PSV-4114) tie into vapour return A, BOG-4001, with their own tees on the tank
side of XV-4135 (between XV-4135 and the off-page to P-01), so they never depend on the
switch. All four go to BOG-4001: line B and BOG-4001 run across the whole sheet, so BOG-4002
could only be reached by crossing BOG-4001 as well; BOG-4011 and BOG-4015 cross loading line
B once each (the topological minimum for a relief from line A or the tank-end crossover).
XV-4135 / HS-4135 and the de-inerting tee T4V1 / XV-4131 / HS-4131 are drawn further right to
make room; BOG-4001 is resegmented (S1 unchanged, old S2 now S2-S6).

Revision after review 2026-11-05-basic-design-3 (#1, D-026.1 and D-026.14): the flare valves
XV-4131 / XV-4132 fail closed again (HS-4131 / HS-4132), the tank-side valves XV-4135 / XV-4136
stay fail open; ZSO-4131 / ZSO-4132 / ZSO-4135 / ZSO-4136 sense their valves themselves, as
ZSO-7121A on P-07, instead of the pipe segment beside them.

Revision after review 2026-11-05-basic-design-4 (D-028): notes only. AI-4133 / AI-4134 name their
O2 reject I-514 / I-614; the ZSO notes define "proven open" with the command discrepancy check
(review 3 #4); UZ-4101 / UZ-4102 carry the closure time and the air accumulator (#1).

Revision after review 2026-11-05-basic-design-5 (D-030): notes only. AI-4133 / AI-4134: the O2
reject is armed on the plant state (no liquid transfer) and trips ESD-1 during a transfer (#4); the
UZ-4101 / UZ-4102 sheet note names the air hold and I-804 (#7a); the UZ notes name the residual
fast-closure case of D-023 (4) (#6).

Revision after review 2026-11-05-basic-design-6 (D-032): notes only. AI-4133 / AI-4134 are the
backup of the berth O2 analysers AI-5126 / AI-6126; the O2 reject also opens XV-4135 / XV-4136, so
the switch sends an O2-rich slug to the tanks, never to the flare (adversarial check, missed medium).
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from dataclasses import replace  # noqa: E402

from lng_pid import Lists, Sheet, note, offpage, tee, valve  # noqa: E402

target = Path(sys.argv[1])
sheet = Sheet.load(target)
L = Lists("P-04")
UP, DOWN, LEFT = 270, 90, 180
YA, YB, YC, YVA, YVB = 70, 120, 28, 195, 235

# ---- loading line A ---------------------------------------------------------------------------
ta_c = tee("T4A1", at=(80, YA), branch="up", branch_dn=250)
ta_x = tee("T4A2", at=(100, YA), branch="down", branch_dn=800)
ta_t = tee("T4A3", at=(200, YA), branch="down", branch_dn=25)  # PSV-4111 to BOG-4001 (D-026)
ta_p = tee("T4A4", at=(330, YA), branch="down", branch_dn=250)
fv1 = valve("FV4101", "ButterflyValve", tag="FV-4101", at=(125, YA))
xv1 = valve("XV4101", "BallValve", tag="XV-4101", at=(150, YA))
la = L.line(sheet, "LNG-4001", dn=800, fluid="LNG", frm="LNG-2001 (P-02)", to="LNG-5001 (P-05)",
            insulation="cold (PIR 200 mm)",
            notes="Loading line A over the trestle, ~2.45 km; 6,000 m3/h at 3.4 m/s with both lines loading, ~91 kPa (S3, D-008, D-011); out-leg of the circulation loop in holding (S2 holding).",
            route=[offpage("in", at=(14, YA), note="from T-2101 pumps (P-02)", note_at=(30, YA - 6)),
                   ta_c, ta_x, fv1, xv1, ta_t, ta_p,
                   offpage("out", at=(405, YA), note="to Berth 2 (P-05)", note_at=(390, YA - 6))],
            label_at=(250, YA - 8))
# ---- loading line B ---------------------------------------------------------------------------
tb_r = tee("T4B1", at=(80, YB), branch="down", branch_dn=250)
tb_x = tee("T4B2", at=(100, YB), branch="up", branch_dn=800)
tb_t = tee("T4B3", at=(220, YB), branch="down", branch_dn=25)  # PSV-4112 to BOG-4001 (D-026)
tb_p = tee("T4B4", at=(330, YB), branch="up", branch_dn=250)
fv2 = valve("FV4102", "ButterflyValve", tag="FV-4102", at=(125, YB))
xv2 = valve("XV4102", "BallValve", tag="XV-4102", at=(150, YB))
lb = L.line(sheet, "LNG-4002", dn=800, fluid="LNG", frm="LNG-3001 (P-03)", to="LNG-6001 (P-06)",
            insulation="cold (PIR 200 mm)",
            notes="Loading line B, as LNG-4001; return leg of the circulation loop in holding through the platform crossover LNG-4003 (D-008).",
            route=[offpage("in", at=(14, YB), note="from T-3101 pumps (P-03)", note_at=(30, YB - 6)),
                   tb_r, tb_x, fv2, xv2, tb_t, tb_p,
                   offpage("out", at=(405, YB), note="to Berth 1 (P-06)", note_at=(390, YB - 6))],
            label_at=(275, YB - 8))
# crossovers
xv3 = valve("XV4103", "BallValve", tag="XV-4103", at=(330, 95))
t_d5 = tee("T4X5", at=(330, 82), branch="right", branch_dn=80)
t_d6 = tee("T4X6", at=(330, 108), branch="right", branch_dn=80)
L.line(sheet, "LNG-4003", dn=250, fluid="LNG", frm="LNG-4001", to="LNG-4002",
       notes="Platform crossover: circulation loop in holding (~314 m3/h, S10); open while loading so both lines reach the loading berth (D-008); receives the jetty drain pumps.",
       route=[ta_p.branch, t_d5, xv3, t_d6, tb_p.branch], label_at=(316, 102))
for nb, tt, y in [("5", t_d5, 82), ("6", t_d6, 108)]:
    L.line(sheet, f"LNG-{nb}006", dn=80, fluid="LNG", frm=f"P-{nb}101", to="LNG-4003",
           notes=f"Jetty drain pump P-{nb}101 discharge into the platform crossover, ~60 m3/h (D-016). Drawn on P-0{nb} and P-04.",
           route=[offpage("in", at=(372, y), note=f"from P-{nb}101 (P-0{nb})", note_at=(384, y - 6 if nb == "6" else y + 6), rotation=180), tt.branch],
           labels=False)
xv6 = valve("XV4106", "BallValve", tag="XV-4106", at=(100, 95))
t_x6 = tee("T4X7", at=(100, 84), branch="left", branch_dn=25)
L.line(sheet, "LNG-4006", dn=800, fluid="LNG", frm="LNG-4001", to="LNG-4002",
       notes="Tank-end crossover: either tank's pumps load through both lines (D-008, D-011); thermal relief PSV-4113.",
       route=[ta_x.branch, t_x6, xv6, tb_x.branch], label_at=(116, 108))

# ---- circulation header, spray take-off, circulation return ------------------------------------
tc3 = tee("T4C1", at=(40, YC), branch="up", branch_dn=250)
tcs = tee("T4C2", at=(60, YC), branch="up", branch_dn=80)
L.line(sheet, "LNG-2002", dn=250, fluid="LNG", frm="P-2102", to="LNG-4001",
       notes="see P-02",
       route=[offpage("in", at=(14, YC), note="from P-2102 (P-02)", note_at=(22, YC + 6)), tc3, tcs,
              (80, YC), ta_c.branch],
       label_at=(100, YC - 4))
L.line(sheet, "LNG-3002", dn=250, fluid="LNG", frm="P-3102", to="LNG-2002",
       notes="see P-03",
       route=[offpage("in", at=(40, 10), note="from P-3102 (P-03)", note_at=(22, 10), rotation=DOWN),
              tc3.branch], labels=False)
L.line(sheet, "LNG-4008", dn=80, fluid="LNG", frm="LNG-2002", to="BOG-1001 (TV-7103)",
       notes="Spray LNG to the BOG desuperheater TV-7103 (S7, 3.5 t/h at loading, D-010). Drawn on P-04 and P-07.",
       route=[tcs.branch, offpage("out", at=(60, 10), note="spray to P-07", note_at=(72, 10),
                                  rotation=UP)], labels=False)
tr2 = tee("T4R1", at=(80, 158), branch="left", branch_dn=250)
xv5 = valve("XV4105", "BallValve", tag="XV-4105", at=(80, 140))
tr_r = tee("T4R2", at=(80, 150), branch="right", branch_dn=25)
lr = L.line(sheet, "LNG-4005", dn=250, fluid="LNG", frm="LNG-4002", to="T-2101",
            notes="Circulation return from line B to the tanks (holding, S10); to T-2101 or, via LNG-4009, T-3101 (D-008); thermal relief PSV-4114 between XV-4105 and the tank valves.",
            route=[tb_r.branch, xv5, tr_r, tr2, (80, 172),
                   offpage("out", at=(80, 178), note="to T-2101 (P-02)", note_at=(66, 182), rotation=DOWN)],
            label_at=(66, 128))
L.line(sheet, "LNG-4009", dn=250, fluid="LNG", frm="LNG-4005", to="T-3101",
       notes="Circulation return branch to T-3101.",
       route=[tr2.branch, (50, 158), (50, 172),
              offpage("out", at=(50, 178), note="to T-3101 (P-03)", note_at=(36, 182), rotation=DOWN)],
       label_at=(36, 150))

# ---- thermal relief of the blocked-in lines (D-017) ------------------------------------------
# PSV-4111 / PSV-4112 on the underside of the loading lines; their outlets BOG-4011 / BOG-4012
# are drawn with the vapour return below (D-026.11)
psv_ab = {}
for k, line_no, side, at, lab in [("1", "LNG-4001", "A", (200, 85), (188, 85)),
                                  ("2", "LNG-4002", "B", (220, 132), (208, 132))]:
    psv_ab[k] = replace(L.relief(
        f"PSV411{k}", f"PSV-411{k}", f"BOG-401{k}", 15.0,
        f"thermal expansion of {line_no} blocked in between XV-410{k} and the platform ESD valve",
        f"Thermal relief of loading line {side} into vapour return line A, BOG-4001, on the tank side of XV-4135, independent of the de-inerting switch (D-017, D-026).",
        label_at=lab), at=at)

# thermal relief of the tank-end crossover and of the circulation return (review #6, H-02 A2)
v13 = L.relief("PSV4113", "PSV-4113", "BOG-4015", 15.0,
               "thermal expansion of the tank-end crossover LNG-4006 and the tank-end section of line A (pump check valves, FV-4101 / XV-4101, XV-4106) blocked in",
               "Thermal relief of the tank-end crossover into vapour return line A, BOG-4001, on the tank side of XV-4135, independent of the de-inerting switch (review 2026-11-05 #6, H-02 A2; D-026); set at the 15 barg design pressure of the LNG lines, ASSUMED.",
               label_at=(86, 78))
v14 = L.relief("PSV4114", "PSV-4114", "BOG-4016", 15.0,
               "thermal expansion of the circulation return LNG-4005 / LNG-4009 blocked in between XV-4105 and XV-2123 / XV-3123",
               "Thermal relief of the circulation return into vapour return line A, BOG-4001, on the tank side of XV-4135, independent of the de-inerting switch (review 2026-11-05 #6, H-02 A2; D-026); set at the 15 barg design pressure of the LNG lines, ASSUMED.",
               label_at=(90, 155))

# ---- vapour return lines ------------------------------------------------------------------------
YD = 213  # de-inerting line between the vapour return lines
tva = tee("T4V1", at=(176, YVA), branch="down", branch_dn=300)
tvb = tee("T4V2", at=(210, YVB), branch="up", branch_dn=300)
xv35 = valve("XV4135", "ButterflyValve", tag="XV-4135", at=(136, YVA))
xv36 = valve("XV4136", "ButterflyValve", tag="XV-4136", at=(120, YVB))
# relief tie-ins on the tank side of XV-4135, between XV-4135 and the off-page to P-01 (D-026.11)
r12 = tee("T4V7", at=(124, YVA), branch="up", branch_dn=25)   # BOG-4012 (PSV-4112)
r11 = tee("T4V6", at=(116, YVA), branch="up", branch_dn=25)   # BOG-4011 (PSV-4111)
r15 = tee("T4V5", at=(108, YVA), branch="up", branch_dn=25)   # BOG-4015 (PSV-4113)
r16 = tee("T4V4", at=(100, YVA), branch="up", branch_dn=25)   # BOG-4016 (PSV-4114)
va = L.line(sheet, "BOG-4001", dn=750, fluid="Boil-off gas", frm="BOG-5001 (Berth 2)", to="BOG-1001",
            insulation="cold (PIR 150 mm)",
            notes="Vapour return line A over the trestle (Berth 2) into the tank vapour header; 45.6 t/h at loading (S6), ~9 m/s (D-009, D-012); on the tank side of XV-4135 it receives the trestle thermal relief outlets BOG-4011, BOG-4012, BOG-4015 and BOG-4016, which so never depend on the de-inerting switch (D-026). Drawn on P-04 and P-01.",
            route=[offpage("in", at=(405, YVA), note="from Berth 2 (P-05)", note_at=(382, YVA - 6),
                           rotation=LEFT),
                   tva, xv35, r12, r11, r15, r16,
                   offpage("out", at=(14, YVA), note="to BOG header (P-01)", note_at=(30, YVA - 6),
                           rotation=LEFT)],
            label_at=(220, YVA - 8))
vb = L.line(sheet, "BOG-4002", dn=750, fluid="Boil-off gas", frm="BOG-6001 (Berth 1)", to="BOG-1001",
            insulation="cold (PIR 150 mm)",
            notes="Vapour return line B over the trestle (Berth 1), as BOG-4001.",
            route=[offpage("in", at=(405, YVB), note="from Berth 1 (P-06)", note_at=(382, YVB + 6),
                           rotation=LEFT),
                   tvb, xv36,
                   offpage("out", at=(14, YVB), note="to BOG header (P-01)", note_at=(30, YVB + 6),
                           rotation=LEFT)],
            label_at=(240, YVB + 8))

# ---- trestle thermal relief outlets into BOG-4001 on the tank side of XV-4135 (D-026.11) -------
# nested from the outside in, so that none crosses another: BOG-4012, BOG-4011, BOG-4015, BOG-4016
L.line(sheet, "BOG-4012", dn=25, fluid="Boil-off gas", frm="LNG-4002 (PSV-4112)", to="BOG-4001",
       notes="Thermal relief outlet of loading line B into vapour return line A, BOG-4001 (tee T4V7), on the tank side of XV-4135 between XV-4135 and the off-page to P-01: independent of the de-inerting switch (D-026).",
       route=[tb_t.branch, psv_ab["2"], (220, 172), (124, 172), r12.branch], labels=False)
L.line(sheet, "BOG-4011", dn=25, fluid="Boil-off gas", frm="LNG-4001 (PSV-4111)", to="BOG-4001",
       notes="Thermal relief outlet of loading line A into vapour return line A, BOG-4001 (tee T4V6), on the tank side of XV-4135 between XV-4135 and the off-page to P-01: independent of the de-inerting switch (D-026). Crosses loading line B on the sheet.",
       route=[ta_t.branch, psv_ab["1"], (200, 150), (116, 150), r11.branch], labels=False)
L.line(sheet, "BOG-4015", dn=25, fluid="Boil-off gas", frm="LNG-4006 (PSV-4113)", to="BOG-4001",
       notes="Thermal relief outlet of the tank-end crossover into vapour return line A, BOG-4001 (tee T4V5), on the tank side of XV-4135 between XV-4135 and the off-page to P-01: independent of the de-inerting switch (D-026). Crosses loading line B on the sheet.",
       route=[t_x6.branch, v13, (88, 84), (88, 132), (108, 132), r15.branch], labels=False)
L.line(sheet, "BOG-4016", dn=25, fluid="Boil-off gas", frm="LNG-4005 (PSV-4114)", to="BOG-4001",
       notes="Thermal relief outlet of the circulation return into vapour return line A, BOG-4001 (tee T4V4), on the tank side of XV-4135 between XV-4135 and the off-page to P-01: independent of the de-inerting switch (D-026).",
       route=[tr_r.branch, v14, (100, 150), r16.branch], labels=False)

# ---- carrier de-inerting and cool-down vapour to the storage and loading flare (review #19) ----
xv31 = valve("XV4131", "ButterflyValve", tag="XV-4131", at=(176, 204))
xv32 = valve("XV4132", "ButterflyValve", tag="XV-4132", at=(210, 224))
tvj = tee("T4V3", at=(210, YD), branch="down", branch_dn=300)
L.line(sheet, "BOG-4013", dn=300, fluid="Boil-off gas", frm="BOG-4001", to="D-8101 (FL-8001)",
       insulation="cold (PIR)",
       notes="Carrier de-inerting and cool-down vapour (N2, warm or off-spec vapour) from vapour return A at the tank end to the storage and loading flare knock-out drum, through XV-4131; joined by BOG-4014 from vapour return B (D-017, S-02, review 2026-11-05 #19). Drawn on P-04 and P-08.",
       route=[tva.branch, xv31, (176, YD), tvj,
              offpage("out", at=(405, YD), note="to D-8101 (P-08)", note_at=(388, YD - 5))],
       label_at=(245, YD - 7))
L.line(sheet, "BOG-4014", dn=300, fluid="Boil-off gas", frm="BOG-4002", to="BOG-4013",
       insulation="cold (PIR)",
       notes="Carrier de-inerting and cool-down vapour from vapour return B at the tank end through XV-4132 into BOG-4013 (review 2026-11-05 #19).",
       route=[tvb.branch, xv32, tvj.branch], label_at=(194, 219))

# make-before-break switch of each vapour return (C&E I-511..I-513, I-611..I-613; D-026.1): the
# open-position switches sense their valves themselves (sensing the valve, as ZSO-7121A on P-07)
L.inst(sheet, "HS-4131", "De-inerting vapour A to the flare XV-4131",
       "Flare valve of the make-before-break switch: I-511 opens it while AI-4133 reads off-specification vapour (not while ESD-1, I-501, or the O2 reject, I-514, is tripped); I-513 closes it only once ZSO-4135 proves XV-4135 open; fail closed: on an instrument-air failure the return goes to the tanks, never from the tank header to the flare (D-017; D-026.1, review 2026-11-05-basic-design-3#1).",
       at=(190, 204), signal_to=xv31, fail_action="FC")
L.inst(sheet, "HS-4132", "De-inerting vapour B to the flare XV-4132",
       "As HS-4131, with AI-4134, ZSO-4136 and XV-4136 (C&E I-611, I-613); fail closed: on an instrument-air failure the return goes to the tanks, never from the tank header to the flare (D-026.1, review 2026-11-05-basic-design-3#1).",
       at=(224, 224), signal_to=xv32, fail_action="FC")
L.inst(sheet, "HS-4135", "Vapour return A to the tank vapour header XV-4135",
       "Tank-side valve of the switch: I-512 closes it only while ZSO-4131 proves XV-4131 open; ESD-1 (I-501) and the O2 reject (I-514, D-032) open it; fail open keeps the carrier vapour return (D-026).",
       at=(150, 183), signal_to=xv35, fail_action="FO")
L.inst(sheet, "HS-4136", "Vapour return B to the tank vapour header XV-4136",
       "As HS-4135, with ZSO-4132 (C&E I-612) and ESD-1 of Berth 1 (I-601); fail open (D-026).",
       at=(134, 224), signal_to=xv36, fail_action="FO")
L.inst(sheet, "ZSO-4131", "XV-4131 open position",
       "Position switch on the flare valve XV-4131: XV-4135 may close only with XV-4131 proven open (C&E I-512, D-026). " + (ZDISC := "Proven open means the switch reads open and has no standing discrepancy: a switch that reads open while its valve has been commanded closed for longer than the stroke time raises a discrepancy alarm and blocks the interlock, so a switch stuck open cannot fake the open state (review 2026-11-05-basic-design-3#4, D-028)."),
       at=(162, 208), sensing=xv31.id, sensing_at=(176, 204),
       sensing_points=[(169, 204), (169, 208)])
L.inst(sheet, "ZSO-4135", "XV-4135 open position",
       "Position switch on the tank-side valve XV-4135: XV-4131 may close only with XV-4135 proven open (C&E I-513, D-026). " + ZDISC,
       at=(144, 205), sensing=xv35.id, sensing_at=(136, YVA))
L.inst(sheet, "ZSO-4132", "XV-4132 open position",
       "Position switch on the flare valve XV-4132: XV-4136 may close only with XV-4132 proven open (C&E I-612, D-026). " + ZDISC,
       at=(196, 229), sensing=xv32.id, sensing_at=(210, 224),
       sensing_points=[(203, 224), (203, 229)])
L.inst(sheet, "ZSO-4136", "XV-4136 open position",
       "Position switch on the tank-side valve XV-4136: XV-4132 may close only with XV-4136 proven open (C&E I-613, D-026). " + ZDISC,
       at=(108, YVB + 9), sensing=xv36.id, sensing_at=(120, YVB),
       sensing_points=[(120, YVB + 9)])
L.inst(sheet, "AI-4133", "Vapour return A composition at the tank end (N2 / O2 / CH4)",
       "Switches the carrier vapour make-before-break between the tank vapour header (XV-4135) and the flare (XV-4131) by C&E I-511..I-513: to the flare while N2 is high (de-inerting, gassing-up; to the flare only below 5 vol % O2), to the tanks once CH4 is on specification and O2 below 1 vol % (D-026). Two O2 cells (ASSUMED, analyser vendor), voted 2oo2 with a discrepancy alarm. The O2 reject is measured at the berth by AI-5126 (P-05), ahead of the 2.45 km transport delay to this analyser; AI-4133 is its backup: above 5 vol % O2 the O2 reject C&E I-514 closes the Berth 2 vapour arm XV-5122 and the hybrid vapour isolation XV-5125 and sends the return to the tanks (XV-4135 opens, I-513 closes XV-4131), so an O2-rich slug never goes to the flare, while XV-5101 is proven closed (ZSC-5101, gassing-up); during a liquid transfer (cooldown and loading) it trips ESD-1, I-501, which stops the flow and trips the carrier (D-026.7, D-028, D-030, D-032).",
       at=(185, 182), sensing=va.segments[0], sensing_at=(185, YVA))
L.inst(sheet, "AI-4134", "Vapour return B composition at the tank end (N2 / O2 / CH4)",
       "As AI-4133, with XV-4136 and XV-4132; backup of the berth analyser AI-6126 (P-06); its O2 reject is C&E I-614 on XV-6122 and XV-6125 with XV-4136 opened, while XV-6101 is proven closed (ZSC-6101), and ESD-1 I-601 during a transfer (D-028, D-030, D-032).",
       at=(262, 222), sensing=vb.segments[0], sensing_at=(262, YVB))

# ---- instruments ----------------------------------------------------------------------------------
L.inst(sheet, "FIC-4101", "Loading line A flow (loading rate)",
       "Ramps the loading up and down to the carrier's cargo plan; FV-4101 butterfly (D-011).",
       at=(170, 84), sensing=la.segments[2], sensing_at=(170, YA), signal_to=fv1, fail_action="FL")
L.inst(sheet, "FIC-4102", "Loading line B flow (loading rate)", "As FIC-4101.",
       at=(170, 134), sensing=lb.segments[2], sensing_at=(170, YB), signal_to=fv2, fail_action="FL")
TANK_END = ("ESD-1 closes it after the pumps have been stopped (C&E I-501, I-601), in 25-30 s (ASSUMED, D-023); "
            "non-return valve and local air accumulator on the actuator supply and a speed controller on its exhaust, so "
            "on an instrument-air failure it holds until the air-header trip I-804 has initiated ESD-1 and then closes "
            "no faster than its set speed (D-016, D-028). Residual case, the valve closing at spring speed with the pumps "
            "running because its non-return valve or accumulator failed: a rise in the pump header and a column "
            "separation in the trestle line, a check case of the transient analysis (D-023.4, D-030).")
L.inst(sheet, "UZ-4101", "Loading line A tank-end ESD valve XV-4101", TANK_END,
       at=(150, 57), signal_to=xv1, fail_action="FC")
L.inst(sheet, "UZ-4102", "Loading line B tank-end ESD valve XV-4102", TANK_END,
       at=(150, 107), signal_to=xv2, fail_action="FC")
L.inst(sheet, "HS-4103", "Platform crossover XV-4103", "Open in holding (circulation) and while loading (D-008).",
       at=(346, 95), signal_to=xv3, fail_action="FL")
L.inst(sheet, "HS-4106", "Tank-end crossover XV-4106", "Operator selection (D-008).",
       at=(114, 95), signal_to=xv6, fail_action="FL")
L.inst(sheet, "HS-4105", "Circulation return XV-4105", "Open in holding (D-008).",
       at=(66, 140), signal_to=xv5, fail_action="FL")
L.inst(sheet, "TI-4102", "Circulation return temperature at the tanks",
       "Holding: the loop is cold when the rise is under 3 K (D-008).",
       at=(66, 166), sensing=lr.segments[2], sensing_at=(80, 166))
# platform-end instruments, drawn towards the platform end of their segments
for tag, service, x, seg, y, yb in [
        ("PI-4105", "Loading line A pressure at the platform", 300, la.segments[-2], YA, 57),
        ("TI-4103", "Loading line A temperature at the platform (cooldown)", 316, la.segments[-2], YA, 57),
        ("PI-4106", "Loading line B pressure at the platform", 300, lb.segments[-2], YB, 134),
        ("TI-4104", "Loading line B temperature at the platform (cooldown)", 316, lb.segments[-2], YB, 134),
        ("PI-4121", "Vapour return A pressure at the platform", 350, va.segments[0], YVA, 182),
        ("TI-4122", "Vapour return A temperature at the platform", 366, va.segments[0], YVA, 182),
        ("PI-4123", "Vapour return B pressure at the platform", 350, vb.segments[0], YVB, YVB - 13),
        ("TI-4124", "Vapour return B temperature at the platform", 366, vb.segments[0], YVB, YVB - 13)]:
    L.inst(sheet, tag, service, at=(x, yb), sensing=seg, sensing_at=(x, y))

note(sheet, "Trestle ~1.98 km at 178 deg; ~2.45 km per line tank to platform (D-013). Expansion loops,", at=(232, 152))
note(sheet, "guides, drip trays to the impoundment sump and the low-point drains are not shown (D-021).", at=(232, 158))
note(sheet, "Circulation (holding): P-2102 / P-3102 -> LNG-2002 -> line A -> XV-4103 -> line B -> LNG-4005 (D-008).", at=(232, 164))
note(sheet, "UZ-4101 / UZ-4102: C&E I-501, I-601 (also ESD-2, I-503 / I-603, and the air trip I-804); air accumulator, closure 25-30 s (D-016).", at=(12, 252))
note(sheet, "LNG-3002 (DN 250): T-3101 circulation; LNG-4008 (DN 80): spray to the desuperheater; LNG-5006 / -6006 (DN 80): drains;", at=(12, 257))
note(sheet, "BOG-4011 / -4012 / -4015 / -4016 (DN 25): thermal relief PSV-4111 / -4112 / -4113 / -4114 (15.0 barg) into BOG-4001 on the tank side of XV-4135.", at=(12, 262))
note(sheet, "BOG-4013 / BOG-4014 (DN 300): carrier de-inerting and cool-down vapour to the flare; AI-4133 / AI-4134 (N2, O2, CH4) switch each vapour return", at=(12, 267))
note(sheet, "make-before-break between the tank vapour header (XV-4135 / XV-4136) and the flare (XV-4131 / XV-4132): C&E I-511..I-513 with ZSO-4131 / ZSO-4135,", at=(12, 272))
note(sheet, "I-611..I-613 with ZSO-4132 / ZSO-4136. ESD-1 (I-501 / I-601) opens XV-4135 / XV-4136 and never closes the vapour return, the relief path", at=(12, 277))
note(sheet, "of the berth; XV-4131 / XV-4132 close only once XV-4135 / XV-4136 are proven open (I-513 / I-613). XV-4135 / -4136 fail open, XV-4131 / -4132 fail closed (D-026.1).", at=(12, 282))

L.finish(sheet, target)
