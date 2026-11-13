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

Revision after review 2026-11-05-basic-design-7 #1 (D-034): the DN 800 platform crossover LNG-4010
with its own ESD valve XV-4107 (UZ-4107, fail closed, closed by ESD-1 of either berth after the
pumps have stopped, 25-30 s, air accumulator and speed controller as XV-4101), between new tees
T4A5 / T4B5 left of the DN 250 crossover, so both DN 800 lines reach the loading berth at 6,000
m3/h each (3.4 m/s). LNG-4003 / XV-4103 stays as the holding circulation bypass and takes the jetty
drain pumps; it is closed in loading. The LNG-4002 label moves left to clear the new crossover.

Revision after review 2026-11-05-basic-design-8 and layout review 2026-11-05-basic-layout-6 #2 (D-036):
nothing but valve stem and bonnet seals is left on the trestle side of the shore ESD valves. The jetty
drain pump returns LNG-5006 / LNG-6006 and their tees T4X5 / T4X6 leave LNG-4003 (they now enter the
berth headers downstream of XV-5101 / XV-6101, P-05 / P-06), so LNG-4003 is one segment; PI-4105 /
PI-4106 and TI-4103 / TI-4104 become non-intrusive (clamp-on strain and strap-on surface sensors under
the insulation, no process tapping). New tank-end N2 connections N-4001 / N-4002 (DN 80, tees T4A6 /
T4B6 on the trestle side of XV-4101 / XV-4102 at the PR1 joint, double block HV-4151 / HV-4152 and
HV-4153 / HV-4154 with the restriction orifice FO-4151 / FO-4152 and the check valve CV-4151 /
CV-4152, normally closed and blinded) displace an isolated trestle line back to the tanks downhill
through the platform crossover and the other line (SEQ-LINE-EMPTY). XV-4107 takes closed- and
open-position switches ZSC-4107 / ZSO-4107 (review 8 #5).

Revision after the checker of D-036: the N2 stations lose their blind and take the bleed HV-4161 /
HV-4162 (lines N-4003 / N-4004) between their blocks, PI-4155..PI-4158 either side of the orifices,
which are drawn as restriction orifices (lng_pid.to_orifice), and the spec break SB at their
battery-limit flange (austenitic from there); ~4,000 Nm3/h. The platform crossovers LNG-4003 /
LNG-4010 are bottom-of-line takeoffs and the trestle lines fall to them without a pocket (notes).

Migration to core 1.11.0 (D-038), drawing only: the circulation returns LNG-4005 / LNG-4009 end on
the left edge. N-4002's "N2 (BL)" stays in the field between the loading lines (D-038).

Revision after review 2026-11-05-basic-design-9 #3, #5, #6 (D-039): each N2 station takes a self-acting
pressure regulator PCV-4159 / PCV-4160 between its orifice and its check valve, set at 3.0 barg (ASSUMED),
so the line being emptied and then held under N2 (SEQ-LINE-EMPTY S3) never sees more than ~3 barg instead
of the 7 barg site N2; the bleeds HV-4161 / HV-4162 are locked closed (opened only under permit with a gas
test), and the new local gauges PI-4163 / PI-4164 between the blocks show a passing block on rounds and,
with the inner block opened (outer block and bleed closed, the check valve holding), the pressure of the
isolated trestle line at its tank end (SEQ-ESD S2, SEQ-LINE-EMPTY permissive). The station valves are
spaced closer to take the regulator; LNG-4010's label moves right.

Revision after the round-10 design check (D-039.9): the check valve CV-4151 / CV-4152 moves to the line side
of the inner block HV-4151 / HV-4153, so the section between them relieves forward through the check valve
into the line and no section of the station can be blocked in liquid-full; the bleed tee and PI-4156 /
PI-4158 stand between the blocks downstream of the regulator, and PI-4163 / PI-4164 move to the line side of
the check valve, where they read the line at its tank end without any valve being opened. PCV-4159 /
PCV-4160 are set at 4.5 barg (sheet note); HV-4161 / HV-4162 are marked LC. N-4002's battery-limit
connector moves to the top edge, beside N-4001's, its station 7 mm higher; its supply crosses LNG-4001
once (accepted in checks/checks.yaml), and LNG-4001's label moves left.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from dataclasses import replace  # noqa: E402

from lng_pid import Lists, Sheet, edge_offpage, label, note, offpage, tee, to_orifice, valve  # noqa: E402

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
ta_k = tee("T4A5", at=(290, YA), branch="down", branch_dn=800)   # platform crossover LNG-4010 (D-034)
ta_n = tee("T4A6", at=(185, YA), branch="up", branch_dn=80)      # tank-end N2 N-4001 (SEQ-LINE-EMPTY, D-036)
fv1 = valve("FV4101", "ButterflyValve", tag="FV-4101", at=(125, YA))
xv1 = valve("XV4101", "BallValve", tag="XV-4101", at=(150, YA))
la = L.line(sheet, "LNG-4001", dn=800, fluid="LNG", frm="LNG-2001 (P-02)", to="LNG-5001 (P-05)",
            insulation="cold (PIR 200 mm)",
            notes="Loading line A over the trestle, ~2.16 km routed (~2.45 km with the tank area and platform runs, D-013); 6,000 m3/h at 3.4 m/s in every 12,000 m3/h line-up, both lines reaching the loading berth through the DN 800 platform crossover LNG-4010; ~147 kPa over the trestle with its expansion loops (D-008, D-011, D-034); out-leg of the circulation loop in holding (S2 holding). Butt-welded from the PR1 joint to the shore ESD valve (no flanged joint, spool, drain, vent or tapping on the trestle and platform DN 800 runs, piping/pipe-specs.yaml Class 150, D-035.6); its only branches there are the relief tee T4A3 and the N2 tee T4A6 at the PR1 joint and the welded crossover tees at the platform (D-036). Falls without a pocket from the PR1 joint (+15.3 m CD grade) to the platform crossover tees, whose branches leave from the bottom of the line, so that in SEQ-LINE-EMPTY the liquid the N2 overruns drains along the bottom to them and not to a platform-end leak (expansion loops flat in the rack plane; checker of D-036).",
            route=[offpage("in", at=(14, YA), note="from T-2101 pumps (P-02)", note_at=(30, YA - 6)),
                   ta_c, ta_x, fv1, xv1, ta_n, ta_t, ta_k, ta_p,
                   offpage("out", at=(405, YA), note="to Berth 2 (P-05)", note_at=(390, YA - 6))],
            label_at=(225, YA - 8))   # left of N-4002's supply from the top edge (D-039.9)
# ---- loading line B ---------------------------------------------------------------------------
tb_r = tee("T4B1", at=(80, YB), branch="down", branch_dn=250)
tb_x = tee("T4B2", at=(100, YB), branch="up", branch_dn=800)
tb_t = tee("T4B3", at=(220, YB), branch="down", branch_dn=25)  # PSV-4112 to BOG-4001 (D-026)
tb_p = tee("T4B4", at=(330, YB), branch="up", branch_dn=250)
tb_k = tee("T4B5", at=(290, YB), branch="up", branch_dn=800)     # platform crossover LNG-4010 (D-034)
# tank-end N2 N-4002 (D-036): after T4B3, so that the crossing of BOG-4011 stays on segment S3 (accepted
# crossing id unchanged); its spool rises into the free field between the two loading lines
tb_n = tee("T4B6", at=(250, YB), branch="up", branch_dn=80)
fv2 = valve("FV4102", "ButterflyValve", tag="FV-4102", at=(125, YB))
xv2 = valve("XV4102", "BallValve", tag="XV-4102", at=(150, YB))
lb = L.line(sheet, "LNG-4002", dn=800, fluid="LNG", frm="LNG-3001 (P-03)", to="LNG-6001 (P-06)",
            insulation="cold (PIR 200 mm)",
            notes="Loading line B, as LNG-4001 (~2.31 km routed); reaches Berth 2 through the DN 800 platform crossover LNG-4010 / XV-4107, as line A reaches Berth 1 (D-034); return leg of the circulation loop in holding through the DN 250 platform crossover LNG-4003 (D-008). Butt-welded as LNG-4001, its PR1-joint branches the relief tee T4B3 and the N2 tee T4B6 (D-035.6, D-036); falls without a pocket to the bottom-of-line platform crossover tees as LNG-4001.",
            route=[offpage("in", at=(14, YB), note="from T-3101 pumps (P-03)", note_at=(30, YB - 6)),
                   tb_r, tb_x, fv2, xv2, tb_t, tb_n, tb_k, tb_p,
                   offpage("out", at=(405, YB), note="to Berth 1 (P-06)", note_at=(390, YB - 6))],
            label_at=(272, YB + 8))
# crossovers
xv7 = valve("XV4107", "BallValve", tag="XV-4107", at=(290, 95))
L.line(sheet, "LNG-4010", dn=800, fluid="LNG", frm="LNG-4001", to="LNG-4002",
       notes="Platform crossover DN 800 (review 2026-11-05-basic-design-7 #1, D-034): open in loading, so both DN 800 lines reach the loading berth at 6,000 m3/h each (3.4 m/s, ~6 kPa across it); ESD valve XV-4107 (UZ-4107, fail closed, closed by ESD-1 of either berth after the pumps have stopped, 25-30 s), closed in holding. Butt-weld ends on the valve and tees, ASSUMED (no gasketed joint on the trestle side of the shore ESD valves, D-034). Its tees T4A5 / T4B5 take it off the bottom of both loading lines, so it is also a crossover of SEQ-LINE-EMPTY when XV-4103 is the leaking item (D-036).",
       route=[ta_k.branch, xv7, tb_k.branch], label_at=(282, 107))
xv3 = valve("XV4103", "BallValve", tag="XV-4103", at=(330, 95))
L.line(sheet, "LNG-4003", dn=250, fluid="LNG", frm="LNG-4001", to="LNG-4002",
       notes="Platform crossover DN 250, the holding circulation bypass (~314 m3/h, S10; 500 m3/h at 2.7 m/s): open in holding, closed in loading, when the DN 800 crossover LNG-4010 carries line B to Berth 2 or line A to Berth 1 (D-008, D-034; 6,000 m3/h in DN 250 would be ~33 m/s, review 2026-11-05-basic-design-7 #1); the crossover of SEQ-LINE-EMPTY (~450 m3/h at ~2.5 m/s, D-036), so its tees T4A4 / T4B4 take it off the bottom of both loading lines, at the low point of the trestle run above the drops to the berth headers (checker of D-036: with a side or top takeoff the liquid below it, a stratified wedge of up to ~500 m at the line's ~0.16 % fall, would stay in the line and drain to the leak). Butt-weld ends, no tapping: the jetty drain pump returns enter the berth headers downstream of XV-5101 / XV-6101 since D-036 (layout review 2026-11-05-basic-layout-6 #2).",
       route=[ta_p.branch, xv3, tb_p.branch], label_at=(345, 108))
xv6 = valve("XV4106", "BallValve", tag="XV-4106", at=(100, 95))
t_x6 = tee("T4X7", at=(100, 84), branch="left", branch_dn=25)
L.line(sheet, "LNG-4006", dn=800, fluid="LNG", frm="LNG-4001", to="LNG-4002",
       notes="Tank-end crossover: either tank's pumps load through both lines (D-008, D-011); thermal relief PSV-4113.",
       route=[ta_x.branch, t_x6, xv6, tb_x.branch], label_at=(116, 108))

# ---- tank-end N2 connections for emptying an isolated trestle line (SEQ-LINE-EMPTY, D-036) ------------
# Site N2 at 7 barg (process/design-basis.yaml) into the trestle side of XV-4101 / XV-4102 at the PR1 joint
# (the tank end, the high end of each line, D-013 / D-035.8): it pushes the isolated line downhill to the
# platform, the liquid the gas overruns drains along the bottom of the line to the bottom-of-line crossover
# tees and leaves through XV-4103 (or XV-4107) up the other line, which stays liquid-full, back to the tank
# through the circulation return. Since the checker of D-036: the station is austenitic stainless steel from
# its battery-limit flange (the spec break), no blind (a blind to remove costs time in the emergency it
# serves): double block and bleed, the bleed HV-4161 / HV-4162 open while the station is isolated; the
# restriction orifice is drawn as one (to_orifice), with a PI upstream and downstream of it.
N2_NOTE = ("Tank-end N2 connection of loading line {side} for SEQ-LINE-EMPTY (layout review 2026-11-05-basic-layout-6 #2, "
           "D-036): site N2 at 7 barg into the trestle side of {xv} at the PR1 joint (the high end of the line), "
           "~4,000 Nm3/h set by the restriction orifice {fo} (choked, ~39 mm bore, ASSUMED), ~3.7 bar(a) at the line, so "
           "the line's ~1,030 m3 return downhill through the bottom-of-line platform crossover and the other loading line "
           "to the tanks in ~2.3 h (D-036); at least 3,500 Nm3/h (site N2 at 6 barg or more at {pu}) keeps the leak within "
           "the 240 min PFP and the 40 m3 kept in T-8102 (D-039). In the flow direction (round-10 design check, D-039.9): "
           "the outer block {hv2}, {pu} (the site N2 once {hv2} is open), {fo}, the self-acting pressure regulator {pcv}, "
           "{pd} (the regulator outlet), the bleed {hb} (line {bl}, locked closed), the inner block {hv1}, the check "
           "valve {cv} and {pb} (the line at its tank end), then the tee; no blind. {pcv} is set at 4.5 barg (ASSUMED, "
           "D-039.9; was 3.0 barg): the highest pressure the displacement needs at the tank end is ~3.4 barg (the "
           "receiving tank at its 29 kPa(g) design pressure, ~2.2 bar of LNG static, 48 m at 470 kg/m3, up to the roof "
           "inlet of the circulation return, and twice the ~45 kPa single-phase friction of the return for the two-phase "
           "flow at the crossover, ~0.9 bar, ASSUMED); with the regulator's offset at the design rate (0.5 bar, ~10 % of "
           "its set point, ASSUMED, vendor) it still delivers ~4.0 barg, ~0.6 bar above that, so it stands wide open "
           "throughout the displacement; it holds the emptied line at ~4.5 barg (lock-up ~4.7 barg, ASSUMED) in "
           "SEQ-LINE-EMPTY S3 instead of the 7 barg site N2; failed open it leaves 7 barg, below the 15 barg line "
           "design and PSV-4111 / 4112. At the design rate {pb} reads ~2.7 barg, {pd} ~2.8 barg (~0.1 bar across the open "
           "inner block and the check valve) and the orifice outlet is ~2.9 barg (~0.1 bar across the open regulator), "
           "so {fo} is choked (7 barg site N2 = 8 bar(a), at least 1.9 times its outlet in absolute terms); with every "
           "bound at once and site N2 at 6 barg it is just unchoked, ~3,400 Nm3/h (D-039.9). The check valve stands on "
           "the line side of the inner block (D-039.9), so no section of the station can be blocked in liquid-full: the "
           "section between {hv1} and {cv} can take LNG only back through the check valve's seat and relieves forward "
           "through it into the line, which PSV-4111 / 4112 protect, and LNG reaches the section between the blocks "
           "only through both {cv} and {hv1}, with which it then stays connected to the line; {hv1} with its cavity "
           "vented to the line side (ASSUMED, vendor). With the station isolated the section between the blocks holds "
           "N2: {pd} and {pu} are read on rounds, a rising reading showing a passing block (D-039). The bleed is opened "
           "only under permit with a gas test, to depressurise the section before maintenance. Spec break at the "
           "battery-limit flange upstream of {hv2}: the station is austenitic stainless steel, Class 150 (the material "
           "of the LNG service, piping/pipe-specs.yaml), because the section from {cv} to the tee holds LNG at "
           "-160 degC and the sections up to {hv2} can; the section from {hv1} to the tee takes cold insulation (PIR, as "
           "the loading lines' branches), the rest of the station may stay bare (piping detail). Drawn on P-04 only (the "
           "site N2 at the battery limit).")
# Round-10 design check (D-039.9): in the flow direction outer block, orifice, regulator, bleed tee, inner block,
# then the check valve on the line side of the inner block (its forward flow relieves the section between them into
# the line), PI-4163 / PI-4164 on the line side of the check valve.
n2_a = [valve("HV4152", "BallValve", tag="HV-4152", at=(185, 19)),
        valve("FO4151", "GlobeValve", tag="FO-4151", at=(185, 25.5)),
        valve("PCV4159", "GlobeValve", tag="PCV-4159", at=(185, 31.5))]   # D-039.9: set 4.5 barg
t_ba = tee("T4N1", at=(185, 41), branch="left", branch_dn=25)        # bleed HV-4161 (locked closed, D-039)
hv_a = valve("HV4151", "BallValve", tag="HV-4151", at=(185, 48))
cv_a = valve("CV4151", "SwingCheckValve", tag="CV-4151", at=(185, 55))
n2a = L.line(sheet, "N-4001", dn=80, fluid="Nitrogen", frm="BL (site N2)", to="LNG-4001", insulation="cold (PIR)",
             notes=N2_NOTE.format(side="A", xv="XV-4101", fo="FO-4151", hv1="HV-4151", hv2="HV-4152", cv="CV-4151",
                                  pu="PI-4155", pd="PI-4156", hb="HV-4161", bl="N-4003", pcv="PCV-4159", pb="PI-4163"),
             route=[offpage("in", at=(185, 12), note="N2 (BL)", note_at=(172, 10), rotation=DOWN), *n2_a, t_ba, hv_a,
                    cv_a, ta_n.branch], labels=False)
L.line(sheet, "N-4003", dn=25, fluid="Nitrogen", frm="N-4001 (between HV-4152 and HV-4151)", to="atmosphere",
       insulation="none",
       notes="Bleed of the N2 double block and bleed HV-4152 / HV-4161 / HV-4151 of N-4001, between the regulator "
             "PCV-4159 and the inner block (D-039.9). Locked closed since D-039 (review 2026-11-05-basic-design-9 #5: "
             "open, it vented any LNG passing the inner block continuously at grade): PI-4156 and PI-4155 between the "
             "blocks show a passing block on rounds instead, and the bleed is opened only under permit with a gas test, "
             "to depressurise the section before maintenance, its outlet at 2.5 m over the PR1 trough collection "
             "(D-037.15 (g)). LNG reaches this section only past both the check valve CV-4151 and the inner block, and "
             "then stays connected to the line through them (D-039.9; the station is Class 150 austenitic stainless). "
             "Austenitic stainless steel as N-4001.",
       route=[t_ba.branch, valve("HV4161", "BallValve", tag="HV-4161", at=(177, 41)),
              offpage("out", at=(169, 41), note="to atm.", note_at=(160, 46), rotation=LEFT)], labels=False)
n2_b = [valve("HV4154", "BallValve", tag="HV-4154", at=(250, 76.5)),
        valve("FO4152", "GlobeValve", tag="FO-4152", at=(250, 82)),
        valve("PCV4160", "GlobeValve", tag="PCV-4160", at=(250, 87.5))]   # D-039.9: set 4.5 barg
t_bb = tee("T4N2", at=(250, 97), branch="left", branch_dn=25)        # bleed HV-4162 (locked closed, D-039)
hv_b = valve("HV4153", "BallValve", tag="HV-4153", at=(250, 103.5))
cv_b = valve("CV4152", "SwingCheckValve", tag="CV-4152", at=(250, 110))
# the site N2 from the top edge beside N-4001's (D-039.9; was mid-sheet, D-038.3 (a)); it crosses LNG-4001 once
n2b = L.line(sheet, "N-4002", dn=80, fluid="Nitrogen", frm="BL (site N2)", to="LNG-4002", insulation="cold (PIR)",
             notes=N2_NOTE.format(side="B", xv="XV-4102", fo="FO-4152", hv1="HV-4153", hv2="HV-4154", cv="CV-4152",
                                  pu="PI-4157", pd="PI-4158", hb="HV-4162", bl="N-4004", pcv="PCV-4160", pb="PI-4164"),
             route=[edge_offpage("in", "top", 250, note="N2 (BL)", note_at=(237, 10)), *n2_b, t_bb, hv_b, cv_b,
                    tb_n.branch], labels=False)
L.line(sheet, "N-4004", dn=25, fluid="Nitrogen", frm="N-4002 (between HV-4154 and HV-4153)", to="atmosphere",
       insulation="none",
       notes="Bleed of the N2 double block and bleed HV-4154 / HV-4162 / HV-4153 of N-4002, as N-4003: locked closed, "
             "PI-4158 and PI-4157 between the blocks read on rounds (D-039, D-039.9).",
       route=[t_bb.branch, valve("HV4162", "BallValve", tag="HV-4162", at=(243, 97)),
              offpage("out", at=(236, 97), note="to atm.", note_at=(227, 102), rotation=LEFT)], labels=False)
for v in n2_a + n2_b + [hv_a, hv_b, cv_a, cv_b]:
    x, y = v.at
    label(sheet, v.id, "PipingComponentNumber", at=(x + 10, y))
to_orifice(sheet, "FO4151")
to_orifice(sheet, "FO4152")
label(sheet, "HV4161", "PipingComponentNumber", at=(172, 46.5))
label(sheet, "HV4162", "PipingComponentNumber", at=(241, 102.5))
note(sheet, "LC", at=(177, 37.5))      # locked closed (D-039.5, D-039.9)
note(sheet, "LC", at=(243, 93.5))
note(sheet, "SB", at=(190, 12))
note(sheet, "SB", at=(255, 12))
PI_N2 = ("Local pressure gauge of the SEQ-LINE-EMPTY N2 station (checker of D-036), between its blocks: {what}. In S2 "
         "{pu} (outer block open) reads the site N2, at 6 barg or more the ~3,500 Nm3/h minimum rate (D-039); {pd} reads "
         "~2.8 barg at the design rate, ~0.1 bar above the line at {pb}, and the orifice {fo} is choked while {pu} is at "
         "least ~1.9 times its outlet (~0.1 bar above {pd}) in absolute terms; {pd} at the regulator's lock-up (~4.7 "
         "barg) with the inner block closed shows the regulator {pcv} holding (D-039.9). With the station isolated both "
         "are read on rounds: a rising reading shows a passing block (the bleed is locked closed; D-039, D-039.9).")
PI_BB = ("Local pressure gauge of the N2 station of loading line {side} on the line side of the check valve {cv} (round-10 "
         "design check, D-039.9; was between the blocks), at the PR1 joint over the trough collection: it reads the "
         "loading line at its tank end at all times, with no valve to open, for SEQ-ESD S2 and the SEQ-LINE-EMPTY "
         "permissive and S2 (the line below the regulator's ~4.0 barg delivered pressure at the design rate, ~2.7 barg in "
         "the displacement). Wetted by LNG at -160 degC: Class 150 austenitic stainless with its root valve inside the "
         "cold insulation of the stub (ASSUMED).")
for tag, what, fo, seg, at, sense in [
        ("PI-4155", "site N2 pressure upstream of FO-4151", "FO-4151", n2a.segments[0], (167, 22.25), (185, 22.25)),
        ("PI-4156", "injection pressure downstream of FO-4151 and PCV-4159", "FO-4151", n2a.segments[0], (167, 34.5),
         (185, 34.5)),
        ("PI-4157", "site N2 pressure upstream of FO-4152", "FO-4152", n2b.segments[0], (231, 79.25), (250, 79.25)),
        ("PI-4158", "injection pressure downstream of FO-4152 and PCV-4160", "FO-4152", n2b.segments[0], (231, 90.5),
         (250, 90.5))]:
    a = fo == "FO-4151"
    L.inst(sheet, tag, f"N2 to loading line {'A' if a else 'B'}, {what}",
           PI_N2.format(what=what, fo=fo, pu="PI-4155" if a else "PI-4157", pd="PI-4156" if a else "PI-4158",
                        pb="PI-4163" if a else "PI-4164", pcv="PCV-4159" if a else "PCV-4160"),
           at=at, sensing=seg, sensing_at=sense)
for tag, side, cv, seg, at, sense in [
        ("PI-4163", "A", "CV-4151", n2a.segments[-1], (167, 62), (185, 62)),
        ("PI-4164", "B", "CV-4152", n2b.segments[-1], (231, 114.5), (250, 114.5))]:
    L.inst(sheet, tag, f"N2 to loading line {side}, loading line pressure at its tank end (line side of {cv})",
           PI_BB.format(side=side, cv=cv), at=at, sensing=seg, sensing_at=sense)
note(sheet, "PCV-4159 / -4160: self-acting pressure regulators, set 4.5 barg; HV-4161 / -4162 LC (D-039.9).", at=(232, 188))

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
       notes="Spray LNG to the BOG desuperheater TV-7103 (S7, 4.1 t/h at loading with the D-034 pump heat, D-010). Drawn on P-04 and P-07.",
       route=[tcs.branch, offpage("out", at=(60, 10), note="spray to P-07", note_at=(72, 10),
                                  rotation=UP)], labels=False)
tr2 = tee("T4R1", at=(80, 158), branch="left", branch_dn=250)
xv5 = valve("XV4105", "BallValve", tag="XV-4105", at=(80, 140))
tr_r = tee("T4R2", at=(80, 150), branch="right", branch_dn=25)
lr = L.line(sheet, "LNG-4005", dn=250, fluid="LNG", frm="LNG-4002", to="T-2101",
            notes="Circulation return from line B to the tanks (holding, S10); to T-2101 or, via LNG-4009, T-3101 (D-008); thermal relief PSV-4114 between XV-4105 and the tank valves.",
            route=[tb_r.branch, xv5, tr_r, tr2, (80, 181),
                   edge_offpage("out", "left", 181, note="to T-2101 (P-02)", note_at=(32, 176))],
            label_at=(66, 128))
# both circulation returns end on the left edge (core 1.11 cheme.offpage-not-on-edge, D-038), below
# LNG-4002 and above the vapour return BOG-4001 coming in from the left edge
L.line(sheet, "LNG-4009", dn=250, fluid="LNG", frm="LNG-4005", to="T-3101",
       notes="Circulation return branch to T-3101.",
       route=[tr2.branch, edge_offpage("out", "left", 158, note="to T-3101 (P-03)", note_at=(32, 153))],
       label_at=(36, 164))

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
            notes="Vapour return line A over the trestle (Berth 2) into the tank vapour header; 52.5 t/h at loading (S6, the design envelope with the D-034 pump heat; was 45.6), ~11 m/s (D-009, D-012, D-034); on the tank side of XV-4135 it receives the trestle thermal relief outlets BOG-4011, BOG-4012, BOG-4015 and BOG-4016, which so never depend on the de-inerting switch (D-026). Drawn on P-04 and P-01.",
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
       "Ramps the loading up and down to the carrier's cargo plan; FV-4101 butterfly (D-011). Its meter, on the "
       "trestle side of XV-4101, also reads the reverse flow (multipath ultrasonic, bidirectional, ASSUMED, instrument "
       "vendor): in SEQ-LINE-EMPTY with line B leaking it measures the LNG the N2 displaces back to the tank, ~450 m3/h "
       "at 4,000 Nm3/h (~390 m3/h at the 3,500 Nm3/h minimum), the N2 station flow seen from the control room; below "
       "~100 m3/h for 5 min before the line is displaced, no N2 is entering (the abort, D-039.9). FIC-4102 the same "
       "for line A leaking.",
       at=(170, 84), sensing=la.segments[2], sensing_at=(170, YA), signal_to=fv1, fail_action="FL")
L.inst(sheet, "FIC-4102", "Loading line B flow (loading rate)",
       "As FIC-4101; with line A leaking it reads the displaced LNG returning up line B in SEQ-LINE-EMPTY (D-039.9).",
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
L.inst(sheet, "UZ-4107", "Platform crossover ESD valve XV-4107 (DN 800)",
       "Opened in SEQ-LOAD S0, so line B reaches Berth 2 (line A Berth 1) at 6,000 m3/h; closed in holding (SEQ-HOLD). "
       + TANK_END.replace("ESD-1 closes it after the pumps have been stopped (C&E I-501, I-601)",
                          "ESD-1 of either berth closes it after the pumps have been stopped (C&E I-501, I-601), so after an ESD the two trestle lines are separated at the platform and a leak upstream of a shore ESD valve is fed by one line only")
                 .replace("a rise in the pump header and a column separation in the trestle line",
                          "a rise in the trestle line upstream of it and a down-surge in the berth header, which loses half its flow")
       + " Review 2026-11-05-basic-design-7 #1, D-034. Its position is proven by ZSC-4107 / ZSO-4107 on the valve "
         "(review 2026-11-05-basic-design-8 #5, D-036): a discrepancy between UZ-4107's command and the switches after "
         "the stroke time alarms, so a failure to close on ESD-1 (both trestle lines then feed a platform-end leak) is "
         "revealed at once.",
       at=(276, 95), signal_to=xv7, fail_action="FC")
ZPOS = ("Position switch on the DN 800 platform crossover XV-4107 itself (review 2026-11-05-basic-design-8 #5, D-036): "
        "the complete conditions of SEQ-LOAD S0 / S3 (open) and SEQ-HOLD S1 / SEQ-ESD (closed) use it; reading "
        "otherwise than UZ-4107 commands for longer than the stroke time raises a discrepancy alarm, so a failure "
        "to close on ESD-1 or a spurious closure in loading is revealed. ")
L.inst(sheet, "ZSC-4107", "XV-4107 closed position", ZPOS + "Closed: the two trestle lines are separated at the platform "
       "(the one-line inventory of a platform-end leak, D-034.3, D-036).",
       at=(304, 104), sensing=xv7.id, sensing_at=(291, 97), sensing_points=[(293, 97), (293, 104)])
L.inst(sheet, "ZSO-4107", "XV-4107 open position", ZPOS + "Open: both lines reach the loading berth (S0, S3).",
       at=(304, 88), sensing=xv7.id, sensing_at=(291, 93), sensing_points=[(293, 93), (293, 88)])
L.inst(sheet, "HS-4103", "Platform crossover XV-4103 (DN 250, holding bypass)",
       "Open in holding (circulation); closed in loading, when the DN 800 crossover XV-4107 carries the second line to the loading berth (D-008, D-034).",
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
    # the loading-line instruments upstream of the shore ESD valves have no process tapping since D-036
    # (layout review 2026-11-05-basic-layout-6 #2): only valve stem and bonnet seals stay on the trestle side
    nonintrusive = {"PI": ("Non-intrusive pressure indication: clamp-on strain sensor on the pipe wall under the cold "
                           "insulation, no process tapping (ASSUMED, instrument vendor), so no leak source is left on "
                           "the trestle side of the shore ESD valve (layout review 2026-11-05-basic-layout-6 #2, D-036); "
                           "indication only, the berth header pressure PZT-{b}103 (downstream of XV-{b}101) is the "
                           "measured value. Should no qualified clamp-on sensor exist for -160 degC, the instrument is "
                           "deleted, never tapped."),
                    "TI": ("Strap-on surface temperature sensor under the cold insulation, no process tapping or "
                           "thermowell (layout review 2026-11-05-basic-layout-6 #2, D-036): the cooldown of the line's "
                           "platform end and the passage of the gas front in SEQ-LINE-EMPTY (D-036).")}
    kind = tag.split("-")[0]
    berth = "5" if tag in ("PI-4105", "TI-4103") else "6"
    notes_ = nonintrusive[kind].format(b=berth) if tag in ("PI-4105", "TI-4103", "PI-4106", "TI-4104") else ""
    L.inst(sheet, tag, service, notes_, at=(x, yb), sensing=seg, sensing_at=(x, y))

note(sheet, "Trestle ~1.98 km at 178 deg; ~2.45 km per line tank to platform (D-013). Expansion loops (flat),", at=(232, 152))
note(sheet, "guides, drip trays not shown (D-021); no low-point drain or vent on the trestle runs (D-036).", at=(232, 158))
note(sheet, "Circulation (holding): P-2102 / P-3102 -> LNG-2002 -> line A -> XV-4103 -> line B -> LNG-4005 (D-008).", at=(232, 164))
note(sheet, "Loading: both lines to the loading berth, the second through LNG-4010 / XV-4107 (DN 800); XV-4103 closed (D-034).", at=(232, 170))
note(sheet, "Trestle side of XV-5101 / -6101: welded, no tapping (D-036). LNG-4003 / LNG-4010: bottom-of-line tees;", at=(232, 176))
note(sheet, "the loading lines fall to them, no pocket (D-036). SB: spec break.", at=(232, 182))
note(sheet, "UZ-4101 / UZ-4102: C&E I-501, I-601 (also ESD-2, I-503 / I-603, and the air trip I-804); air accumulator, closure 25-30 s (D-016).", at=(12, 252))
note(sheet, "LNG-3002 (DN 250): T-3101 circulation; LNG-4008 (DN 80): spray to the desuperheater; N-4001 / -4002 (DN 80): N2, SEQ-LINE-EMPTY, bleeds N-4003 / -4004;", at=(12, 257))
note(sheet, "BOG-4011 / -4012 / -4015 / -4016 (DN 25): thermal relief PSV-4111 / -4112 / -4113 / -4114 (15.0 barg) into BOG-4001 on the tank side of XV-4135.", at=(12, 262))
note(sheet, "BOG-4013 / BOG-4014 (DN 300): carrier de-inerting and cool-down vapour to the flare; AI-4133 / AI-4134 (N2, O2, CH4) switch each vapour return", at=(12, 267))
note(sheet, "make-before-break between the tank vapour header (XV-4135 / XV-4136) and the flare (XV-4131 / XV-4132): C&E I-511..I-513 with ZSO-4131 / ZSO-4135,", at=(12, 272))
note(sheet, "I-611..I-613 with ZSO-4132 / ZSO-4136. ESD-1 (I-501 / I-601) opens XV-4135 / XV-4136 and never closes the vapour return, the relief path", at=(12, 277))
note(sheet, "of the berth; XV-4131 / XV-4132 close only once XV-4135 / XV-4136 are proven open (I-513 / I-613). XV-4135 / -4136 fail open, XV-4131 / -4132 fail closed (D-026.1).", at=(12, 282))

L.finish(sheet, target)
