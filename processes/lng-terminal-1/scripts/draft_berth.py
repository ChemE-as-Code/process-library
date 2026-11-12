"""Draft of a berth sheet (P-05: Berth 2, as built; P-06: Berth 1, Phase 2): the platform
liquid header with the shore ESD valve, strainer and surge relief, the four 16 inch arms (two
liquid, one hybrid, one vapour) with their emergency release systems and thermal relief, the
vapour line to the trestle, the jetty drain drum and pump, and the N2 purge.

Generator of P-05 and P-06 through scripts/draft_P-05.py / draft_P-06.py, which pass the digit
(frames pid/frames/P-05.xml, P-06.xml): `cheme regen P-05 P-06` rebuilds them (D-021).
Arm arrangement and procedures from the LNG Canada Terminal Information Guide (S-01): south to
north liquid, vapour, hybrid, liquid; vapour arm connected first; N2 leak test 5 / 2.5 bar.
Decisions D-014, D-016, D-017, D-021, D-023. The sheet draws the arms left to right L1, L2, H, V
(the platform order is in the note) so that the vapour line leaves the sheet without crossings.

Revision after the basic-design review (reviews/2026-11-05-basic-design.md #1, #2, #3, #7, #17,
#18, #21, #23, #25) and HAZOP H-03 (A3, A4, A5, A7, A13): the drain DR-n001 has its block valve
XV-n161 with the relief outlets downstream of it; the drain drum D-n101 is drawn above the
header (it sits at the platform low point) so that the arm thermal relief reaches it without
crossing the header; drain pump isolation, check valve and minimum flow; position switches on
the hybrid arm valves; N2 double block and bleed; an independent high-high level on D-n101.

Round 2: thermal relief PSV-n118 of the drain pump discharge between CV-n116 and HV-n117 (DR-n006
into DR-n001); the drain pump vent/drain HV-n119 between its isolation valves (DR-n007 into
DR-n001); DR-n001 at DN 150 throughout (it receives the DN 150 surge relief DR-n002); the tags
of all relief valves printed; sheet notes on the hybrid arm key interlock and the arm package.

Round 3 (reviews/2026-11-05-basic-design-2.md, D-026.2, .3, .13): ZSC-n123/n125 are closed-position
switches, the start permissives of the other isolation (C&E I-n04/I-n05); ESD-2 (I-n03) trips ESD-1
at once and the ERS valves close 5 s later by I-n07; the arm purge outlet (before loading into the
carrier's manifold, after loading through D-n101 and its vent BOG-n002 into the vapour return).

Round 4 (reviews/2026-11-05-basic-design-3.md, D-026.14): ZSC-n123 / ZSC-n125 sense the valves
XV-n123 / XV-n125 themselves (as ZSO-7121A on P-07), not the pipe beside them; HS-n123 / HS-n125
note that their open command is blocked by I-n04 / I-n05 and never closes an open valve; HS-n161
notes that XV-n161 is also open for the N2 purge after loading (D-026.13).

Round 5 (reviews/2026-11-05-basic-design-4.md #1, #2, #8 and its adversarial check, D-028): the
closure of the jetty valves on an instrument-air failure. XV-n101 and the liquid arm isolations hold
on a non-return valve and a local air accumulator, with a speed controller setting the same closure
time for a commanded closure and one on air loss; the ERS valves are hydraulic from the arm
vendor's power unit and do not move on an air failure; the air-header trip I-804 (P-08) initiates
ESD-1 first. PSV-n131 takes the air-failure closure in its relief case. The O2 reject I-n14 is named
in the HS-n122 notes and a sheet note. ZSC-n125 senses XV-n125 from the valve's lower corner, and
HS-n125 sits under its actuator so its signal line meets the bubble edge (#8a, #8b).

Round 6 (reviews/2026-11-05-basic-design-5.md #2, #3, #4 and its adversarial check, D-030): an
open-position switch ZSO-n122 on the vapour arm isolation XV-n122 itself; "vapour path not proven
open during a liquid transfer" trips ESD-1 (I-n01), which also makes XV-n122, the first jetty valve
to move on a platform-end air loss, the detector of that loss; the O2 reject I-n14 is armed on the
plant state (no liquid transfer), the O2 high-high trips ESD-1 during a transfer; the ERS valves are
de-energise-to-trip on two solenoids in series (2oo2, line-monitored) and the couplers
energise-to-release, so one circuit fault neither closes nor releases; PSV-n131 names the spurious
ERS closure at full flow.

Round 7 (reviews/2026-11-05-basic-design-6.md #1, #2, #4, #5, #7 and its adversarial check, D-032): a
closed-position switch ZSC-n101 on the shore ESD valve XV-n101 itself, so the liquid transfer state
that arms the ESD-1 causes and the O2 reject is made of safety-system inputs only (ZSC-n101 and the
SIS output UZ-n101), not of the flow loops; a berth O2 analyser AI-n126 on BOG-n001 downstream of
both vapour isolations, so the O2 reject acts before the vapour enters the 2.45 km return; the
ESD-1 causes as tags (HS-n100 manual ESD-1, XS-n108 platform fire and gas, XA-n130A / B the two ERS
solenoid supplies) and HS-n107 manual ESD-2; the ERS solenoid channels on two supplies, the coupler
release on a timer after the ERS close command; the idle berth's 'no carrier connected' link mode;
the vapour arm is needed for every transfer (no 'spare' path). PDI-n102 moves right to make room.

Round 8 (reviews/2026-11-05-basic-design-7.md #2 to #5, #7 to #9, D-034): the berth O2 analyser
AI-n126 samples the vapour arm side of XV-n122 (BOG-n001 S1), so it reads the carrier's vapour with
the isolations closed and gives I-n14 its reset; the 'no carrier connected' link mode ends by itself;
the coupler releases UY-n135..n138 (one per arm) are tagged and drawn as effects of I-n07, released
on both ERS valves of the arm proven closed or on a timeout from the vendor's closure time, with the
arm isolations closed by I-n07 as well; the ERS function test enable HS-n109 (permissive I-n09); the
manual ESD-1 / ESD-2 stations each have their own tag (HS-n100A/B/C, HS-n107A/B/C), wired normally
closed (de-energise-to-trip); the vapour arm N2 test point and the O2 sample in the notes.

Round 9 (reviews/2026-11-05-basic-design-8.md #1, #7, #8 and layout review 2026-11-05-basic-layout-6 #2,
D-036): the drain pump discharge LNG-n006 enters the berth header downstream of XV-n101 (new tee T-n0K
between the N2 tee and the surge relief tee, which moves 3 mm right), no longer the platform crossover on
the trestle side, so the header segments after T-n0N are renumbered by one (S7..S9 are the DN 400 hybrid
arm pieces); PZT-n103 carries its PAHH set point against the carrier's manifold design pressure; the UZ
and UY notes name I-n10 for the coupler release; AI-n126's fast-loop isolation is a leak-test permissive.

Round 9, checker of D-036: the carrier manifold protection moves to the arms' outboard ends, PZT-n181 /
PZT-n184 on LNG-n011 / LNG-n014 (1oo2, PAHH 5.0 barg, C&E I-n02), where the normal pressure is the
carrier's manifold pressure; PZT-n103 stays as the header indication and an uncredited backstop. FO-n118
is drawn as a restriction orifice (lng_pid.to_orifice).

Migration to core 1.11.0 (D-038), drawing only: the vapour arm's carrier connection BOG-n012 comes in on
the right edge above the vapour line's instruments; the three liquid arms' carrier connections stay
under their arms, inside the berth header (D-038).
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from chemeascode.domains.piping.authoring import label  # noqa: E402
from lng_pid import (  # noqa: E402
    Lists, Nozzle, Sheet, arm_shape, edge_offpage, equipment, note, offpage, set_dn, tee, to_orifice, valve)

target, n = Path(sys.argv[1]), sys.argv[2]
berth, line_in, vap_out = ("2", "LNG-4001", "BOG-4001") if n == "5" else ("1", "LNG-4002", "BOG-4002")
sheet = Sheet.load(target)
L = Lists(f"P-0{n}")
UP, DOWN, LEFT = 270, 90, 180
HDR_Y, ARM_Y, SC = 190, 100, 2.0
X = {"1": 110, "4": 170, "3": 230, "2": 290}      # LA-n101 L1, LA-n104 L2, LA-n103 H, LA-n102 V
KIND = {"1": "liquid", "4": "liquid", "3": "hybrid", "2": "vapour"}
RLF_Y = 150                                       # thermal relief tees on the arm risers
DRX = 88                                          # drain / relief line DR-n001 (up to the drum)
TOP_R, TOP_V = 40, 20                             # relief header and drum vent above the arms
CHAN = {"4": X["4"] - 21.5, "3": X["3"] - 21.5}   # relief risers between two arms
VCH = X["2"] - 21.5                               # drum vent down between the hybrid and vapour arm

arms = {}
for k, x in X.items():
    arms[k] = equipment(sheet, "LoadingUnloadingSystem", f"LA-{n}10{k}", shape=arm_shape(sheet),
                        at=(x, ARM_Y), scale=SC,
                        nozzles=[Nozzle("N1", (0, 28), 400), Nozzle("N2", (32, 16), 400)],
                        label_at=(x - 2, 66))

# ---- liquid header: shore ESD valve, strainer, N2, surge relief, drain ---------------------
t_n2 = tee(f"T{n}0N", at=(62, HDR_Y), branch="up", branch_dn=80 if n == "5" else 50)
# drain pump return downstream of XV-n101 (layout review 2026-11-05-basic-layout-6 #2, D-036): was a tie-in
# into the platform crossover LNG-4003 on the trestle side of the shore ESD valve
t_dk = tee(f"T{n}0K", at=(67, HDR_Y), branch="up", branch_dn=80)
t_srg = tee(f"T{n}0S", at=(77, HDR_Y), branch="up", branch_dn=150)
t_dr = tee(f"T{n}0D", at=(DRX, HDR_Y), branch="up", branch_dn=150)
t_l1 = tee(f"T{n}01", at=(X["1"], HDR_Y), branch="up", branch_dn=400)
t_l2 = tee(f"T{n}04", at=(X["4"], HDR_Y), branch="up", branch_dn=400)
t_rh = tee(f"T{n}R3", at=(X["3"], RLF_Y), branch="left", branch_dn=25)
xv_esd = valve(f"XV{n}101", "BallValve", tag=f"XV-{n}101", at=(28, HDR_Y))
hdr = L.line(sheet, f"LNG-{n}001", dn=800, fluid="LNG", frm=f"{line_in} (P-04)", to=f"LA-{n}103",
             notes=f"Berth {berth} liquid header on the loading platform, 12,000 m3/h at loading (S3); shore ESD valve XV-{n}101 and strainer SR-{n}102 (S-01: shore strainers; D-016).",
             route=[offpage("in", at=(12, HDR_Y), note=f"from trestle line {'A' if n == '5' else 'B'} (P-04)", note_at=(24, HDR_Y + 7)), xv_esd,
                    valve(f"SR{n}102", "ConicalStrainer", tag=f"SR-{n}102", at=(46, HDR_Y)), t_n2, t_dk, t_srg,
                    t_dr, t_l1, t_l2, (X["3"], HDR_Y),
                    valve(f"XV{n}123", "BallValve", tag=f"XV-{n}123", at=(X["3"], 181)),
                    tee(f"T{n}0H", at=(X["3"], 172), branch="right", branch_dn=400), t_rh,
                    arms["3"]["N1"]],
             label_at=(192, HDR_Y + 8),
             segments=[{"number": "S7", "nominal_diameter": "DN400", "notes": "to the hybrid arm, after the LA-n104 tee"},
                       {"number": "S8", "nominal_diameter": "DN400", "notes": "hybrid arm connection, to the thermal relief tee"},
                       {"number": "S9", "nominal_diameter": "DN400", "notes": "hybrid arm connection, thermal relief tee to the arm"}])
set_dn(sheet, [f"T{n}04_N2", f"XV{n}123_N1", f"XV{n}123_N2", f"T{n}0H_N1", f"T{n}0H_N2",
               f"T{n}R3_N1", f"T{n}R3_N2"], 400,
       segments=[f"Line_LNG{n}001_S7", f"Line_LNG{n}001_S8", f"Line_LNG{n}001_S9"])
t_rl = {}
for k, tt in [("1", t_l1), ("4", t_l2)]:
    t_rl[k] = tee(f"T{n}R{k}", at=(X[k], RLF_Y), branch="left", branch_dn=25)
    L.line(sheet, f"LNG-{n}00{'2' if k == '1' else '3'}", dn=400, fluid="LNG", frm=f"LNG-{n}001",
           to=f"LA-{n}10{k}", notes=f"Liquid arm LA-{n}10{k} shore connection with its isolation valve and the thermal relief tee of the arm section.",
           route=[tt.branch, valve(f"XV{n}12{k}", "BallValve", tag=f"XV-{n}12{k}", at=(X[k], 168)),
                  t_rl[k], arms[k]["N1"]],
           label_at=(X[k] + 14, 150))
t_rl["3"] = t_rh

# ---- vapour arm, hybrid vapour connection, vapour line to the trestle ---------------------------
t_vw = tee(f"T{n}0W", at=(X["2"], 165), branch="left", branch_dn=100)
t_vh = tee(f"T{n}0V", at=(X["2"], 172), branch="left", branch_dn=400)
vap = L.line(sheet, f"BOG-{n}001", dn=400, fluid="Boil-off gas", frm=f"LA-{n}102", to=f"{vap_out} (P-04)",
             notes=f"Berth {berth} vapour line from the vapour arm (and the hybrid arm) to vapour return line {'A' if n == '5' else 'B'}; one 16 inch vapour arm carries ~23.5 t/h of the -120 degC return at 40 m/s (D-023). The vapour arm is needed for every transfer (XV-{n}122 proven open by ZSO-{n}122); the hybrid arm normally runs as the third liquid arm and is the second vapour path of line-up (b) only; above the vapour arm's capacity the carrier burns gas on board or the loading rate is reduced (D-023, D-026.6, D-032). Receives the drain drum vent BOG-{n}002; the berth O2 analyser AI-{n}126 samples it downstream of both vapour isolations (D-032).",
             route=[arms["2"]["N1"], valve(f"XV{n}122", "BallValve", tag=f"XV-{n}122", at=(X["2"], 150)),
                    t_vw, t_vh, (X["2"], 182),
                    offpage("out", at=(405, 182), note=f"to vapour return {'A' if n == '5' else 'B'} (P-04)", note_at=(388, 176))],
             label_at=(370, 190))
L.line(sheet, f"BOG-{n}003", dn=400, fluid="Boil-off gas", frm=f"LA-{n}103", to=f"BOG-{n}001",
       notes="Hybrid arm to the vapour line: the second vapour path of line-up (b), beside the vapour arm, never instead of it (D-026.6, D-032); XV-%s125 opens only with XV-%s123 closed (ZSC-%s123 / ZSC-%s125)." % (n, n, n, n),
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
               # from the right edge, above the vapour line's instruments (core 1.11
               # cheme.offpage-not-on-edge, D-038); the liquid arms' carrier connections stay under their arms
               route=[edge_offpage("in", "right", 160, note="from carrier", note_at=(392, 155)), (sx, 160),
                      *ers[::-1], arms[k]["N2"]], labels=False)
    else:
        outb = L.line(sheet, f"LNG-{n}01{k}", dn=400, fluid="LNG", frm=f"LA-{n}10{k}", to="carrier manifold",
                      notes=f"{KIND[k].capitalize()} arm outboard: arm, ERS (XV-{n}13{k}, emergency release coupler, XV-{n}14{k}), quick connect/disconnect coupler, carrier manifold (D-014)."
                            + (f" PZT-{n}18{k} on its shore side of the inboard ERS valve, at the arm's outboard end (C&E I-{n}02, D-036)." if k in ("1", "4") else ""),
                      route=[arms[k]["N2"], *ers,
                             offpage("out", at=(sx, 156), note="to carrier", note_at=(sx - 11 if k == "3" else sx + 11, 160), rotation=DOWN)],
                      labels=False)
        if k in ("1", "4"):
            # carrier manifold protection measured where the normal pressure is lowest (checker of D-036): at the
            # outboard end of each of the two liquid arms that every transfer uses, on the arm side of the ERS
            other = "4" if k == "1" else "1"
            L.inst(sheet, f"PZT-{n}18{k}", f"LA-{n}10{k} outboard pressure at the carrier manifold (high back-pressure)",
                   f"Carrier manifold protection (checker of D-036, D-016, D-023 (6)): pressure at the outboard end of the "
                   f"liquid arm, on the arm side of the inboard ERS valve XV-{n}13{k} (ASSUMED ~2 m above the carrier's "
                   f"manifold flange, so ~0.1 bar of static between them; transmitter, cable and seal on the arm in the arm "
                   f"vendor's package, ASSUMED, H-02). PAHH 5.0 barg (ASSUMED), 1oo2 with PZT-{n}18{other}, a discrepancy "
                   f"between the two alarms: C&E I-{n}02 stops the loading pumps, trips the carrier through the link and "
                   f"closes XV-{n}101. The normal pressure here is the carrier's manifold pressure, ~2.5-3.0 barg at "
                   f"12,000 m3/h (350 kPa(a) of the pump rating, D-011, with the ERS and coupler losses; the highest a "
                   f"carrier asks for is confirmed in the ship-shore compatibility study), against ~5.2-5.5 barg on the "
                   f"berth header at PZT-{n}103 (S3, 647.9 kPa(a) at XV-{n}101), so a set point 2 bar above normal leaves "
                   f"room for the closure rise of a carrier ESD valve below the carrier's 10 barg (ASSUMED): 5.0 + "
                   f"2.7-3.2 bar (2 rho L v / t over the trestle line and the berth header for a 30-25 s closure) + "
                   f"~0.1 bar = ~8.3 barg at most (D-036). Both liquid arms LA-{n}101 / LA-{n}104 carry liquid in every "
                   f"transfer (the hybrid may be in vapour service), so the 1oo2 never rests on an arm that is not "
                   f"flowing; an arm not connected reads ~0 and leaves the other as 1oo1, alarmed.",
                   at=(sx - 15, 113), sensing=outb.segments[0], sensing_at=(sx, 119))
    for v, y in [(f"XV{n}13{k}", 125), (f"XV{n}14{k}", 140)]:
        L.inst(sheet, f"UZ-{v[2:]}", f"LA-{n}10{k} ERS valve XV-{v[2:]}",
               f"Closes on ESD-2 by C&E I-{n}07 (5 s after I-{n}03), not on ESD-1; I-{n}10 then releases the coupler (D-016, D-026, D-034). "
               f"Hydraulic actuator on the arm vendor's hydraulic power unit with its accumulator (ASSUMED, vendor): instrument air "
               f"does not move it, so an air failure does not close it; it closes only on I-{n}07, from the accumulator also on a "
               f"loss of the power unit, in a closure time set with the arm vendor against the surge of the arm (ASSUMED 5 s, D-023, "
               f"D-028). De-energise-to-trip on two solenoid valves (2oo2, each line-monitored, a discrepancy alarms): "
               f"one coil, wire or output fault de-energises one solenoid only and does not move the valve; channel A is fed "
               f"from UPS A, channel B from UPS B (separate distribution, ASSUMED), each monitored (XA-{n}130A / XA-{n}130B), and "
               f"the loss of either, or of one channel of any ERS valve (line monitoring of its solenoid circuit), during a "
               f"liquid transfer trips ESD-1 at once (I-{n}01); the two channels are on separate SIS output modules "
               f"(ASSUMED, H-06). A solenoid stuck energised is found by the ERS function "
               f"test of SEQ-LOAD S1 before every transfer (HS-{n}109, permitted only with no transfer and every arm stowed, "
               f"C&E I-{n}09). The coupler release UY-{n}13{4 + int(k)} is energise-to-release, commanded by I-{n}10 when both "
               f"ERS valves of the arm are proven closed or, if one fails to close, at a timeout from the vendor's confirmed "
               f"closure time with margin (ASSUMED 1.5 x, H-02), whichever comes first, never before the ERS close command and "
               f"the closure of the arm isolations by I-{n}07; no circuit or supply fault releases it (review 2026-11-05-basic-design-5 "
               f"#3, review 6 #2, review 7 #4 / #5, D-016, D-032, D-034).",
               at=(sx - 13, y), signal_to=v, fail_action="FC")
    L.inst(sheet, f"ZS-{n}15{k}", f"LA-{n}10{k} envelope monitoring (position of the outboard arm)",
           f"Pre-alarm, ESD-1 at stage 1 (C&E I-{n}01), ESD-2 at stage 2 (C&E I-{n}03, ERS by I-{n}07). With the arm stowed "
           f"in its parking position (no carrier connected) it reads stowed, not a stage (ASSUMED, arm vendor's envelope "
           f"system, H-02), so an idle berth trips nothing; leaving the stowed position ends the link's 'no carrier "
           f"connected' mode (review 2026-11-05-basic-design-6 #5, review 7 #3, D-016, D-034).", at=(x + 8, 56))

# ---- N2 purge and leak test: double block and bleed into the header ---------------------------
t_bl = tee(f"T{n}0B", at=(32, 160), branch="up", branch_dn=25)
L.line(sheet, "N-8001" if n == "5" else "N-8002", dn=80 if n == "5" else 50, fluid="Nitrogen",
       frm="BL (site N2)" if n == "5" else "N-8001", to=f"LNG-{n}001",
       insulation="none", pclass="Class 150",
       notes="see P-08",
       route=[offpage("in", at=(12, 160), note="N2 (P-08)", note_at=(14, 154)),
              valve(f"HV{n}151", "BallValve", tag=f"HV-{n}151", at=(20, 160)), t_bl,
              valve(f"HV{n}152", "BallValve", tag=f"HV-{n}152", at=(42, 160)),
              valve(f"CV{n}151", "SwingCheckValve", at=(52, 160)), (62, 160), t_n2.branch],
       label_at=(48, 174))
L.line(sheet, f"N-{n}001", dn=25, fluid="Nitrogen", frm=f"N-800{'1' if n == '5' else '2'} (between HV-{n}151 and HV-{n}152)",
       to="atmosphere", insulation="none", pclass="Class 150",
       notes=f"Bleed of the N2 double block and bleed HV-{n}151 / HV-{n}153 / HV-{n}152: open to atmosphere while the N2 tie-in is isolated, so that LNG cannot reach the N2 system (review #18, H-03 A7).",
       route=[t_bl.branch, valve(f"HV{n}153", "BallValve", tag=f"HV-{n}153", at=(32, 150)),
              offpage("out", at=(32, 141), note="to atmosphere", note_at=(46, 138), rotation=UP)],
       labels=False)

# ---- jetty drain drum (drawn above the header) and drain pump ----------------------------------
drum = equipment(sheet, "PressureVessel", f"D-{n}101", shape="VESSEL_WITH_DISHED_HEADS_SHAPE",
                 at=(50, 55), rotation=90,
                 nozzles=[Nozzle("N1", (8, -10), 150), Nozzle("N2", (-8, -10), 100),
                          Nozzle("N3", (-5, 10), 100), Nozzle("N4", (-15, 4), 50),
                          Nozzle("N5", (-15, -4), 50), Nozzle("N6", (15, 0), 50)],
                 label_at=(50, 56))
pump = equipment(sheet, "CentrifugalPump", f"P-{n}101", shape="CENTRIFUGAL_PUMP_SHAPE", at=(65, 92),
                 nozzles=[Nozzle("N1", (-7.5, 0), 100), Nozzle("N2", (0, -7.5), 80)], label_at=(56, 104))

# ---- header drain with its block valve, surge and thermal relief downstream of it -------------
t_ps = tee(f"T{n}0P", at=(DRX, 175), branch="left", branch_dn=150)
t_r1 = tee(f"T{n}0Q", at=(DRX, RLF_Y), branch="right", branch_dn=25)
t_rp = tee(f"T{n}0U", at=(DRX, 95), branch="left", branch_dn=25)    # PSV-n118 outlet
t_rv = tee(f"T{n}0X", at=(DRX, 72), branch="left", branch_dn=25)    # drain pump vent HV-n119
t_rr = tee(f"T{n}0R", at=(DRX, TOP_R), branch="right", branch_dn=25)
xv_dr = valve(f"XV{n}161", "BallValve", tag=f"XV-{n}161", at=(DRX, 183))
L.line(sheet, f"DR-{n}001", dn=150, fluid="LNG", frm=f"LNG-{n}001", to=f"D-{n}101",
       notes=f"Header and arm drain to the jetty drain drum after loading through XV-{n}161 (fail closed, closed in cooldown and loading, opened for the drain in SEQ-LOAD S6). Downstream of XV-{n}161 it receives the surge relief PSV-{n}131 (DR-{n}002, DN 150, so DR-{n}001 is DN 150 throughout), the arm thermal relief PSV-{n}171 (DR-{n}004), PSV-{n}173 and PSV-{n}174 (DR-{n}003, DR-{n}005), the drain pump thermal relief PSV-{n}118 (DR-{n}006) and the drain pump vent/drain HV-{n}119 (DR-{n}007), so the relief outlets stay open to D-{n}101 (D-016, review #1).",
       route=[t_dr.branch, xv_dr, t_ps, t_r1, t_rp, t_rv, t_rr, (DRX, 30), (58, 30), drum["N1"]],
       label_at=(DRX + 11, 115))
psv = L.relief(f"PSV{n}131", f"PSV-{n}131", f"DR-{n}002", 15.0,
               "surge on a fast closure: the ERS valves on ESD-2; a spurious ERS closure at full flow ahead of the pump stop "
               "(both channels of a valve or both of the two independent solenoid supplies lost within the ESD-1 response, "
               "D-016, D-023.5, D-032; rechecked in D-034 for 3.4 m/s in both trestle lines: one arm's ERS closing in 5 s "
               "~11 barg peak, inside the 15 barg design, every ERS of the berth ~23 barg, above it); XV-%s101 or an arm isolation "
               "closing on an instrument-air failure faster than commanded (non-return valve or accumulator failed, header lost "
               "faster than the I-804 trip); thermal expansion of the blocked-in header (D-023, D-028, D-030); if the surge "
               "analysis shows a spring PSV cannot answer the transient, a design change, not a sizing item" % n,
               f"Surge and thermal relief of the Berth {berth} header into D-{n}101 through DR-{n}001 downstream of XV-{n}161 (D-016, D-023); set at the 15 barg design of the header and arms; size from the surge analysis in detail engineering.",
               label_at=(78, 171.5))
L.line(sheet, f"DR-{n}002", dn=150, fluid="LNG", frm=f"LNG-{n}001 (PSV-{n}131)", to=f"DR-{n}001",
       notes=f"Surge relief discharge of PSV-{n}131 into the drain line downstream of XV-{n}161.",
       route=[t_srg.branch, psv, (77, 175), t_ps.branch], labels=False)

# thermal relief of each liquid arm section (arm isolation valve to inboard ERS valve), DN 25
ARM_VALVES = {"1": ("121", "131"), "4": ("124", "134"), "3": ("123", "133")}
psv_arm = {}
for k in ("1", "4", "3"):
    iso, ers = ARM_VALVES[k]
    extra = f", XV-{n}125" if k == "3" else ""
    psv_arm[k] = L.relief(
        f"PSV{n}17{k}", f"PSV-{n}17{k}", {"1": f"DR-{n}004", "4": f"DR-{n}005", "3": f"DR-{n}003"}[k], 15.0,
        f"thermal expansion of LNG blocked in LA-{n}10{k} between XV-{n}{iso}{extra} and the inboard ERS valve XV-{n}{ers} (instrument air failure, isolated arm after ESD-2)",
        f"Thermal relief of the {KIND[k]} arm section LA-{n}10{k} into D-{n}101 (review #7); DN 25, set at the 15 barg design of the arm; cavity relief of the ERS ball valves to be confirmed with the arm vendor.",
        label_at={"1": (99, 144), "4": (159.25, 144), "3": (219.25, 144)}[k])
L.line(sheet, f"DR-{n}004", dn=25, fluid="LNG", frm=f"LNG-{n}002 (PSV-{n}171)", to=f"DR-{n}001",
       notes=f"Thermal relief of LA-{n}101 through PSV-{n}171 into DR-{n}001 downstream of XV-{n}161.",
       route=[t_rl["1"].branch, psv_arm["1"], t_r1.branch], labels=False)
t_r4 = tee(f"T{n}0T", at=(CHAN["4"], TOP_R), branch="down", branch_dn=25)
L.line(sheet, f"DR-{n}003", dn=25, fluid="LNG", frm=f"LNG-{n}001 (PSV-{n}173)", to=f"DR-{n}001",
       notes=f"Thermal relief header of the arms: PSV-{n}173 (hybrid arm LA-{n}103) and PSV-{n}174 (DR-{n}005, LA-{n}104) into DR-{n}001 downstream of XV-{n}161, to D-{n}101; drawn above the arms.",
       route=[t_rl["3"].branch, psv_arm["3"], (CHAN["3"], RLF_Y), (CHAN["3"], TOP_R), t_r4, t_rr.branch],
       label_at=(178, TOP_R - 6))
L.line(sheet, f"DR-{n}005", dn=25, fluid="LNG", frm=f"LNG-{n}003 (PSV-{n}174)", to=f"DR-{n}003",
       notes=f"Thermal relief of LA-{n}104 through PSV-{n}174 into the relief header DR-{n}003.",
       route=[t_rl["4"].branch, psv_arm["4"], (CHAN["4"], RLF_Y), t_r4.branch], labels=False)

# ---- drum vent (no valve: the relief path of the drum), pump suction, discharge, minimum flow --
L.line(sheet, f"BOG-{n}002", dn=100, fluid="Boil-off gas", frm=f"D-{n}101", to=f"BOG-{n}001",
       notes=f"Drain drum vent to the vapour line, downstream of XV-{n}122; no valve: it is the relief path of D-{n}101 and stays open (review #1). After loading it also carries the hydrocarbon purge N2 of the arms, drained to D-{n}101, into the vapour return (to the flare while AI-413{'3' if n == '5' else '4'} reads off-specification; D-026.13).",
       route=[drum["N2"], (42, TOP_V), (VCH, TOP_V), (VCH, 165), t_vw.branch], label_at=(230, TOP_V + 5))
L.line(sheet, f"LNG-{n}005", dn=100, fluid="LNG", frm=f"D-{n}101", to=f"P-{n}101",
       notes=f"Drain pump suction with its isolation valve HV-{n}115.",
       route=[drum["N3"], valve(f"HV{n}115", "BallValve", tag=f"HV-{n}115", at=(45, 79)), (45, 92), pump["N1"]],
       labels=False)
t_mf = tee(f"T{n}0M", at=(72, 78), branch="up", branch_dn=50)
t_vd = tee(f"T{n}0Z", at=(76, 78), branch="up", branch_dn=25)    # vent/drain HV-n119
t_pd = tee(f"T{n}0Y", at=(80, 95), branch="right", branch_dn=25)  # thermal relief PSV-n118
L.line(sheet, f"LNG-{n}006", dn=80, fluid="LNG", frm=f"P-{n}101", to=f"LNG-{n}001",
       notes=f"Drain pump discharge into the Berth {berth} header LNG-{n}001 downstream of the shore ESD valve XV-{n}101 (tee T{n}0K), ~60 m3/h: D-{n}101 is emptied into the cooldown flow to the arms and the carrier in SEQ-LOAD S3 of the next transfer, with XV-{n}101 open (D-036; was a tie-in into the platform crossover LNG-4003 on the trestle side of XV-{n}101, layout review 2026-11-05-basic-layout-6 #2, so its flanged check and isolation valves are no longer fed by the trestle line after an ESD). Minimum-flow take-off and the vent/drain HV-{n}119 upstream of the check valve CV-{n}116, then the thermal relief PSV-{n}118 and the isolation valve HV-{n}117 (review #2, H-03 A4). Drawn on P-0{n} only.",
       route=[pump["N2"], (65, 78), t_mf, t_vd, (80, 78),
              valve(f"CV{n}116", "SwingCheckValve", tag=f"CV-{n}116", at=(80, 87)),
              t_pd,
              valve(f"HV{n}117", "BallValve", tag=f"HV-{n}117", at=(80, 102.5)), (80, 110), (67, 110),
              t_dk.branch],
       labels=False)
psv_dp = L.relief(f"PSV{n}118", f"PSV-{n}118", f"DR-{n}006", 15.0,
                  "thermal expansion of the blocked-in drain pump discharge",
                  f"Thermal relief of the drain pump P-{n}101 discharge between the check valve CV-{n}116 and the isolation valve HV-{n}117 into DR-{n}001 downstream of XV-{n}161, to D-{n}101; DN 25, set at the 15 barg design.",
                  label_at=(97, 97.5))
L.line(sheet, f"DR-{n}006", dn=25, fluid="LNG", frm=f"LNG-{n}006 (PSV-{n}118)", to=f"DR-{n}001",
       notes=f"Thermal relief of the drain pump discharge through PSV-{n}118 into DR-{n}001 downstream of XV-{n}161.",
       route=[t_pd.branch, psv_dp, t_rp.branch], labels=False)
L.line(sheet, f"DR-{n}007", dn=25, fluid="LNG", frm=f"LNG-{n}006 (HV-{n}119)", to=f"DR-{n}001",
       notes=f"Vent/drain of the drain pump P-{n}101 between its suction isolation HV-{n}115 and discharge isolation HV-{n}117, through the normally closed HV-{n}119 into DR-{n}001 downstream of XV-{n}161, to D-{n}101 (review #2).",
       route=[t_vd.branch, (76, 72), valve(f"HV{n}119", "BallValve", tag=f"HV-{n}119", at=(82, 72)),
              t_rv.branch], labels=False)
L.line(sheet, f"LNG-{n}007", dn=50, fluid="LNG", frm=f"LNG-{n}006", to=f"D-{n}101",
       notes=f"Drain pump minimum flow back to D-{n}101 through the restriction orifice FO-{n}118 (review #2).",
       route=[t_mf.branch, valve(f"FO{n}118", "GlobeValve", tag=f"FO-{n}118", at=(72, 66)), (72, 55), drum["N6"]],
       labels=False)
to_orifice(sheet, f"FO{n}118")

# ---- instruments --------------------------------------------------------------------------
AIR_HOLD = ("non-return valve and local air accumulator on the actuator supply (one closing stroke and a hold of at "
            "least 5 min after a loss of the air header, ASSUMED) and a speed controller on the actuator exhaust that "
            "sets the same closure time for a commanded closure and for one on air loss; on an instrument-air failure "
            "the valve holds until the air-header trip I-804 has stopped the pumps and tripped the carrier through "
            "ESD-1; it closes afterwards, on its command or as the accumulator decays, never faster than its set "
            "speed (D-016, D-028)")
L.inst(sheet, f"UZ-{n}101", f"Berth {berth} shore ESD valve XV-{n}101",
       f"ESD-1 closes it in 25-30 s (ASSUMED, D-023) after the pumps have been stopped (C&E I-{n}01, D-016); {AIR_HOLD}. "
       f"Its SIS output holding the valve open is, with ZSC-{n}101, the liquid transfer state of Berth {berth} (C&E I-{n}01, "
       f"I-{n}14; D-032).",
       at=(28, 178), signal_to=xv_esd, fail_action="FC")
# closed-position switch on XV-n101 itself, below the valve (its actuator and UZ-n101 are above); the
# measuring line runs right under the pipe and down beside the off-page note (review 6 #1)
L.inst(sheet, f"ZSC-{n}101", f"XV-{n}101 closed position",
       f"Closed-position switch on the shore ESD valve XV-{n}101: XV-{n}101 not proven closed, or held open by UZ-{n}101, "
       f"is the liquid transfer state of Berth {berth} that arms the transfer causes of ESD-1 (I-{n}01); proven closed and "
       f"not held open arms the O2 reject I-{n}14 (C&E; review 2026-11-05-basic-design-6 #1, D-032). Safety-system inputs "
       f"only, so no loop transmitter or DCS command disarms ESD-1. Reading closed while UZ-{n}101 holds the valve open for "
       f"longer than its stroke time raises a discrepancy alarm.",
       at=(39, 205), sensing=xv_esd.id, sensing_at=(28, HDR_Y + 1.5),
       sensing_points=[(28, HDR_Y + 3.5), (39, HDR_Y + 3.5)])
L.inst(sheet, f"PDI-{n}102", f"Strainer SR-{n}102 differential pressure", at=(56, 202),
       sensing=hdr.segments[0], sensing_at=(56, HDR_Y))
L.inst(sheet, f"PZT-{n}103", f"Berth {berth} header pressure (high back-pressure)",
       f"Berth header pressure downstream of XV-{n}101: indication, the PAH, and in C&E I-{n}02 an uncredited backstop "
       f"at PAHH 7.0 barg (ASSUMED). Normal ~5.2-5.5 barg at 12,000 m3/h (S3, 647.9 kPa(a) at XV-{n}101, less the "
       f"strainer). Corrected after the checker of D-036: on the header no set point fits between that normal pressure "
       f"and the carrier's 10 barg (ASSUMED) once the closure rise of a carrier ESD valve (2.7-3.2 bar, not ~0.3 bar) is "
       f"allowed for; the carrier's manifold is protected by PZT-{n}181 / PZT-{n}184 at the arms' outboard ends, where "
       f"the normal pressure is lowest (1oo2, PAHH 5.0 barg, D-036). Shore shut-off with a full tank ~12.1 barg here "
       f"(scripts/terminal_sizing.py).",
       at=(124, 202), sensing=hdr.segments[5], sensing_at=(124, HDR_Y))
L.inst(sheet, f"TI-{n}104", f"Berth {berth} header temperature (cooldown)", at=(146, 202),
       sensing=hdr.segments[5], sensing_at=(146, HDR_Y))
ARM_HOLD = ("Fail closed; closure time at least 25 s (ASSUMED, D-023) with the " + AIR_HOLD.replace(
    "the valve holds until", "it holds until"))
L.inst(sheet, f"HS-{n}121", f"LA-{n}101 isolation XV-{n}121", ARM_HOLD + ".", at=(X["1"] + 14, 168),
       signal_to=f"XV{n}121", fail_action="FC")
L.inst(sheet, f"HS-{n}124", f"LA-{n}104 isolation XV-{n}124", ARM_HOLD + ".", at=(X["4"] - 15, 168),
       signal_to=f"XV{n}124", fail_action="FC")
L.inst(sheet, f"HS-{n}123", f"LA-{n}103 liquid isolation XV-{n}123",
       f"Open command blocked by C&E I-{n}04 unless the other isolation XV-{n}125 is proven closed (ZSC-{n}125) and XV-{n}123 itself is proven closed (ZSC-{n}123); an open valve is never closed by it (D-026.3, D-026.14, D-028). {ARM_HOLD}.",
       at=(X["3"] - 15, 181), signal_to=f"XV{n}123", fail_action="FC")
# HS-n125 straight under its actuator (the actuator of XV-n125 hangs below the valve at x 258), so
# the signal line meets the bubble edge (review 2026-11-05-basic-design-4 #8b)
L.inst(sheet, f"HS-{n}125", f"LA-{n}103 vapour isolation XV-{n}125 (hybrid as vapour arm)",
       f"Open command blocked by C&E I-{n}05 unless the other isolation XV-{n}123 is proven closed (ZSC-{n}123) and XV-{n}125 itself is proven closed (ZSC-{n}125); an open valve is never closed by it (D-026.3, D-026.14, D-028). The O2 reject I-{n}14 closes it with XV-{n}122 while XV-{n}101 is proven closed (gassing-up; D-028, D-030, D-032). Fail closed without an accumulator (opening it on an air failure could join the liquid and vapour paths of the hybrid arm); in line-up (b) its closure leaves the vapour arm XV-{n}122, proven open by ZSO-{n}122, as the return.",
       at=(258, 186), signal_to=f"XV{n}125", fail_action="FC")
# closed-position switches on the valves themselves (sensor at XV-n123 / XV-n125, as ZSO-7121A on P-07)
L.inst(sheet, f"ZSC-{n}123", f"XV-{n}123 closed position",
       f"Closed-position switch of the hybrid arm liquid isolation: start permissive of the other isolation, XV-{n}125 may open only with XV-{n}123 proven closed (C&E I-{n}05); never trips an open valve (review #3, H-03 A13, D-026).",
       at=(242, 187), sensing=f"XV{n}123", sensing_at=(X["3"], 181),
       sensing_points=[(X["3"] + 5, 181), (X["3"] + 5, 187)])
# ZSC-n125 starts on the lower right corner of the XV-n125 symbol (valve at (258, 172), its actuator
# below), stays below BOG-n003 and clear of the actuator (review 2026-11-05-basic-design-4 #8a)
L.inst(sheet, f"ZSC-{n}125", f"XV-{n}125 closed position",
       f"Closed-position switch of the hybrid arm vapour isolation: start permissive of the other isolation, XV-{n}123 may open only with XV-{n}125 proven closed (C&E I-{n}04); never trips an open valve (review #3, H-03 A13, D-026).",
       at=(278, 181), sensing=f"XV{n}125", sensing_at=(260, 173),
       sensing_points=[(260, 175), (278, 175)])
ai_o2 = "AI-4133" if n == "5" else "AI-4134"
L.inst(sheet, f"HS-{n}122", f"LA-{n}102 vapour arm isolation XV-{n}122",
       f"Fail closed, without an accumulator. Closed, latching, with XV-{n}125 by the O2 reject I-{n}14 when AI-{n}126 "
       f"(or {ai_o2}) reads above 5 vol % O2 while XV-{n}101 is proven closed (gassing-up); during a liquid transfer "
       f"(cooldown and loading) the O2 high-high trips ESD-1, I-{n}01 (D-026.7, D-028, D-030, D-032). Proven open by ZSO-{n}122: not open "
       f"during a liquid transfer trips ESD-1 at the start of any closure (spurious command, solenoid or output fault, "
       f"air loss at the platform end of the air main), before the liquid-path valves, which hold on their "
       f"accumulators, move (review 2026-11-05-basic-design-5 #2 and adversarial check, D-030). The drum vent "
       f"BOG-{n}002 joins downstream of it, so the jetty relief path stays open.",
       at=(X["2"] + 15, 150), signal_to=f"XV{n}122", fail_action="FC")
# open-position switch on XV-n122 itself, left of the valve (its actuator and HS-n122 are on the right),
# clear of the drum vent BOG-n002 at x VCH (review 2026-11-05-basic-design-5 adversarial check)
L.inst(sheet, f"ZSO-{n}122", f"XV-{n}122 open position",
       f"Open-position switch on the vapour arm isolation XV-{n}122: not open during a liquid transfer at Berth "
       f"{berth} trips ESD-1 (C&E I-{n}01) at the start of the closure; proves the vapour path open in SEQ-LOAD "
       f"S1, S3 and S4 (D-030, D-032). A switch failing to not-open trips ESD-1 (safe); one stuck open is found by the "
       f"command discrepancy alarm. A failed switch may be overridden for the transfer in progress only, under a permit "
       f"with XV-{n}122 checked open locally (C&E I-{n}01 bypass, review 2026-11-05-basic-design-6 #4); the vapour arm "
       f"is needed for every transfer.",
       at=(279, 150), sensing=f"XV{n}122", sensing_at=(288, 150))
# berth O2 analyser on the vapour arm side of XV-n122 (BOG-n001 S1), so it reads the carrier's vapour
# also with the isolations it closes shut, and I-n14 can be reset on its reading (review
# 2026-11-05-basic-design-7 #2, D-034; was downstream of both isolations, D-032)
L.inst(sheet, f"AI-{n}126", f"Berth {berth} vapour O2 (two cells)",
       f"O2 of the carrier vapour at the berth, on the vapour arm side of XV-{n}122 (sample point and cells ASSUMED, "
       f"analyser vendor), so it measures the carrier's vapour whether XV-{n}122 is open or closed; the hybrid vapour path "
       f"of line-up (b) comes from the same carrier vapour header and is only ever open beside the vapour arm (D-032), so "
       f"the one point serves both. Sample fast loop returned into BOG-{n}001 downstream of XV-{n}122 (~1 Nm3/h, "
       f"ASSUMED, analyser package), isolated during the vapour arm leak test of SEQ-LOAD S1 by the analyser package's "
       f"fast-loop isolation valve (vendor tag), proven closed by the package as a permissive of the leak test (review "
       f"2026-11-05-basic-design-8 #7, D-036). Two O2 cells voted 2oo2 with "
       f"a discrepancy alarm: above 5 vol % O2 the reject C&E I-{n}14 closes XV-{n}122 / XV-{n}125 and sends the return to "
       f"the tanks while XV-{n}101 is proven closed (gassing-up), and I-{n}14 is reset only once it reads below 5 vol %; "
       f"during a liquid transfer it trips ESD-1 (I-{n}01). {ai_o2} at the tank end is the backup (D-026.7, D-032, D-034).",
       at=(279, 138), sensing=vap.segments[0], sensing_at=(290, 138))
L.inst(sheet, f"HS-{n}161", f"Header drain isolation XV-{n}161 to D-{n}101",
       f"Opened for the header and arm drain and for the N2 purge after loading (SEQ-LOAD S6, D-026.13); fail closed (review #1, H-03 A3).",
       at=(DRX + 12, 183), signal_to=xv_dr, fail_action="FC")
L.inst(sheet, f"XS-{n}100", f"Berth {berth} ship-shore ESD link",
       f"Fibre-optic link (S-01): ESD-1 both ways: a carrier ESD trips I-{n}01 (cause), and I-{n}01, also when "
       f"initiated by ESD-2 (I-{n}03) or the air-header trip (I-804), trips the carrier's ESD through it (effect; "
       f"D-028). With no carrier connected the link is in its own 'no carrier connected' mode, selectable only with every "
       f"arm stowed and XV-{n}101 proven closed (ZSC-{n}101): not a trip and not a bypass, so an idle berth does not trip "
       f"I-{n}01, the shared pumps or holding; a departing carrier's link is set to it after the arms are stowed and "
       f"before the cable is disconnected (SEQ-LOAD S6; review 2026-11-05-basic-design-6 #5, D-016). The mode ends by "
       f"itself when a carrier's link cable is connected and healthy or when any arm leaves its stowed position "
       f"(ZS-{n}151..{n}154); ended with no healthy link it reads trip (I-{n}01). The open command of XV-{n}101 is "
       f"permitted only with the link in carrier mode and healthy (C&E I-{n}08), and the mode is alarmed whenever an "
       f"arm is not stowed (review 2026-11-05-basic-design-7 #3, D-034).", at=(22, 28))
# the ESD-1 / ESD-2 causes that are not process measurements, as tags (review 2026-11-05-basic-design-6 #4);
# one tag per station, wired normally closed (review 2026-11-05-basic-design-7 #7, D-034)
STATION = {"A": "control room", "B": "jetty head", "C": "loading platform"}
causes = []
for s, where in STATION.items():
    causes.append((f"HS-{n}100{s}", f"Berth {berth} manual ESD-1 push button, {where}",
                   f"Hard-wired ESD-1 push button in the {where}, on its own SIS input with a normally closed contact "
                   f"(de-energise-to-trip, the input line-monitored), so a broken wire trips or alarms and the SOE names "
                   f"the station: a cause of C&E I-{n}01 (review 2026-11-05-basic-design-7 #7, D-034)."))
for s, where in STATION.items():
    causes.append((f"HS-{n}107{s}", f"Berth {berth} manual ESD-2 push button, {where}",
                   f"Hard-wired ESD-2 push button in the {where}, own normally closed SIS input as HS-{n}100{s}: a cause "
                   f"of C&E I-{n}03 (ESD-1 at once, ERS by I-{n}07; review 7 #7, D-034)."))
causes += [
    (f"XS-{n}108", f"Berth {berth} platform fire and gas confirmed",
     f"Voted output of the fire and gas system for the loading platform (voting ASSUMED, F&G vendor): a cause of C&E "
     f"I-{n}01."),
    (f"XA-{n}130A", f"Berth {berth} ERS solenoid channel A",
     f"Monitoring of channel A of the ERS solenoids: the UPS A supply (separate distribution, ASSUMED) and the line "
     f"monitoring of every channel A solenoid circuit; a loss of either during a liquid transfer trips ESD-1, C&E I-{n}01 "
     f"(review 2026-11-05-basic-design-6 #2, review 7 #5, D-016, D-034)."),
    (f"XA-{n}130B", f"Berth {berth} ERS solenoid channel B",
     f"As XA-{n}130A for channel B (UPS B).")]
for i, (tag, service, text) in enumerate(causes):
    L.inst(sheet, tag, service, text, at=(24 + 18 * i, 222))
# coupler releases (effects of I-n07, review 7 #4) and the ERS function test enable (I-n09, review 7 #5)
for i, k in enumerate("1234"):
    L.inst(sheet, f"UY-{n}13{4 + int(k)}", f"LA-{n}10{k} emergency release coupler release",
           f"Energise-to-release from the arm vendor's HPU accumulator (vendor package): commanded by C&E I-{n}10 when "
           f"both ERS valves of LA-{n}10{k} are proven closed (vendor position switches, ASSUMED) or at the timeout "
           f"(vendor closure time x 1.5, ASSUMED, H-02), whichever comes first; I-{n}07 closes the arm isolations at the same "
           f"time (review 2026-11-05-basic-design-7 #4, D-016, D-034).", at=(24 + 18 * i, 236))
L.inst(sheet, f"HS-{n}109", f"Berth {berth} ERS function test enable (arm vendor panel)",
       f"Enables the arm vendor's ERS test function of SEQ-LOAD S1; permitted only with XV-{n}101 proven closed "
       f"(ZSC-{n}101), UZ-{n}101 de-energised and every arm stowed (ZS-{n}151..{n}154), C&E I-{n}09, so the test can "
       f"never close an ERS valve during a transfer (review 2026-11-05-basic-design-7 #5, D-034).", at=(96, 236))
L.inst(sheet, f"PI-{n}105", f"Berth {berth} vapour line pressure", at=(352, 170),
       sensing=vap.segments[-1], sensing_at=(352, 182))
L.inst(sheet, f"TI-{n}106", f"Berth {berth} vapour line temperature", at=(374, 170),
       sensing=vap.segments[-1], sensing_at=(374, 182))
L.inst(sheet, f"LIC-{n}111", f"Jetty drain drum D-{n}101 level",
       f"Starts and stops P-{n}101 (level control, D-016); the high-high level is the independent LZT-{n}112. Since "
       f"D-036 P-{n}101 returns into the berth header downstream of XV-{n}101, so its start is permitted only with "
       f"XV-{n}101 open and the cooldown or loading flow established (SEQ-LOAD S3 / S4): the drum is emptied into the "
       f"flow to the arms and the carrier at the start of the next transfer, never against the closed header.",
       at=(20, 66), sensing=drum["N4"])
L.inst(sheet, f"LZT-{n}112", f"Jetty drain drum D-{n}101 independent high-high level",
       f"Own nozzle, independent of LIC-{n}111: stops the drain (closes XV-{n}161) and alarms (C&E; review #21, H-03 A5).",
       at=(20, 44), sensing=drum["N5"])

for vid, at in [(f"HV{n}151", (20, 165)), (f"HV{n}152", (42, 165)), (f"HV{n}153", (24, 149)),
                (f"HV{n}115", (36, 79)), (f"FO{n}118", (63, 70)), (f"HV{n}119", (97, 72))]:
    label(sheet, vid, "PipingComponentNumber", at=at)

NOTES = [
    f"Berth {berth} arms on the platform, south to north: LA-{n}101 liquid, LA-{n}102 vapour, LA-{n}103 hybrid, LA-{n}104 liquid (S-01); drawn left to right L, L, H, V.",
    f"16 inch, ~4,000 m3/h per liquid arm; the hybrid runs as the third liquid arm or, in line-up (b), the second vapour path; the vapour arm LA-{n}102 is needed for every transfer (D-032).",
    f"ESD-2 trips ESD-1 at once (C&E I-{n}03 into I-{n}01); the ERS valves (two ball valves either side of the emergency release coupler) close 5 s later by I-{n}07, not on ESD-1;",
    # Round 6 (D-030), round 7 (D-032): the trip principle of the ERS valves and couplers, continuing the note above
    f"ERS valves de-energise-to-trip on 2oo2 solenoids, channels A / B (XA-{n}130A / B, either lost: ESD-1); couplers UY-{n}135..{n}138 release on ERS closed or timeout (D-034).",
    f"Thermal relief (15.0 barg) to D-{n}101: PSV-{n}171 / {n}173 / {n}174 per liquid arm section, PSV-{n}118 on the drain pump discharge. Vapour arm connected first, disconnected last (S-01).",
    f"D-{n}101 sits at the platform low point (drawn above the header). Its vent BOG-{n}002 has no valve: it is the drum's relief path and stays open.",
    f"XV-{n}123 / XV-{n}125: open-command permissives, each opens only with the other proven closed (ZSC-{n}123 / ZSC-{n}125, C&E I-{n}04 / I-{n}05), never trip an open valve; key interlock at the arm (vendor).",
    f"Arm purge (D-026): before loading the N2 goes into the carrier's manifold (S-01); after loading the arms drain to D-{n}101 and the purge N2 leaves by the drum vent BOG-{n}002 into the vapour return.",
    f"HV-{n}119 normally closed (pump vent/drain). BOG-{n}003, DR-{n}002 to DR-{n}007, LNG-{n}005 to LNG-{n}007, N-{n}001: see the line list. Arm vents, drains, vapour arm N2 test point: arm package; O2: AI-{n}126.",
    # Round 5 (D-028), after the existing notes so their ids are kept
    f"Air failure: PZT-8123A/B/C (P-08, C&E I-804) trip ESD-1 first; XV-{n}101 and the arm isolations hold on accumulators, closing at their set speed; ERS valves hydraulic (HPU).",
    f"O2 above 5 vol % (AI-{n}126): C&E I-{n}14 closes XV-{n}122 / XV-{n}125 with XV-{n}101 proven closed (ZSC-{n}101), else ESD-1 (I-{n}01); ZSO-{n}122 not open in a transfer: ESD-1.",
    # Round 7 (D-032)
    f"ESD-1: HS-{n}100A/B/C, XS-{n}108, XA-{n}130A / B; ESD-2: HS-{n}107A/B/C. XS-{n}100 'no carrier' mode ends on an arm unstowed or link healthy (D-034).",
    # Round 9 (D-036)
    f"LNG-{n}006: P-{n}101 returns D-{n}101 into the header downstream of XV-{n}101 in the next cooldown (D-036). PZT-{n}181 / {n}184 1oo2 5.0 barg: C&E I-{n}02.",
]
for i, text in enumerate(NOTES):
    note(sheet, text, at=(12, 246.5 + 3.5 * i))  # one row higher since D-036 (13 notes)

L.finish(sheet, target)
