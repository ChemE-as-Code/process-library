"""Draft of P-03: heat-recovery train E-103 (tail-gas heater, with the R-102 inlet temperature
control on a tail-gas bypass), E-104 (economiser), E-105 (cooler-condenser), weak-acid
separator V-101 and the weak-acid pumps P-101A/B.

Provenance only: P-03 is hand-maintained (no `generator:` in plant.yaml); this script wrote
its first revision. Run: cheme run scripts/draft_P-03.py build/frames/P-03.xml pid/P-03.xml.
Equipment, lines, DN and instruments: DESIGN.md D-017 to D-020; streams S12-S18, S26, S27 and
the energy streams Q06, Q07 of process/flowsheet.yaml.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from chemeascode.domains.piping.authoring import (  # noqa: E402
    Nozzle,
    Sheet,
    instrument,
    note,
    offpage,
    tee,
    valve,
)
from pid_common import (  # noqa: E402
    BOTTOM,
    DRUM,
    EDGE,
    HX,
    LEFT,
    PUMP,
    TOP,
    equipment,
    line,
    make_safety_valve,
    save,
    valve_marks,
)

frame = Path(sys.argv[1])
target = Path(sys.argv[2]) if len(sys.argv) > 2 else frame
sheet = Sheet.load(frame)

GAS = 115       # nitrous gas through E-103, E-104, E-105
TAIL = 45       # hot tail gas to R-102
BYPASS = 33     # tail-gas bypass of E-103


def exchanger(tag, x, s1, s2, s3):
    """A shell-and-tube exchanger on the gas axis: tubes T1/T2, shell nozzles S1 (top left),
    S2 (top right) and S3 (bottom right) with their DN."""
    return equipment(sheet, "TubularHeatExchanger", tag, shape=HX, at=(x, GAS), scale=1.4,
                     nozzles=[Nozzle("T1", (-24.5, 0), None), Nozzle("T2", (24.5, 0), None),
                              Nozzle("S1", (-9.8, -9.8), s1), Nozzle("S2", (9.8, -9.8), s2),
                              Nozzle("S3", (9.8, 9.8), s3)],
                     label_at=(x, GAS + 20))


e103 = exchanger("E-103", 85, 700, 900, None)
e104 = exchanger("E-104", 165, 100, None, 100)
e105 = exchanger("E-105", 245, None, 700, 700)
v101 = equipment(sheet, "Vessel", "V-101", shape=DRUM, at=(320, 125), scale=(1.2, 1.6),
                 nozzles=[Nozzle("N1", (-12, -10), 900), Nozzle("N2", (0, -24), 900),
                          Nozzle("N3", (0, 24), 100), Nozzle("N4", (12, 12), 50),
                          Nozzle("N5", (-12, 15), 50)],
                 label_at=(346, 116))
p101a = equipment(sheet, "CentrifugalPump", "P-101A", shape=PUMP, at=(310, 225),
                  nozzles=[Nozzle("N1", (-7.5, 0), 100), Nozzle("N2", (7.5, 0), 80)],
                  label_at=(306, 240))
p101b = equipment(sheet, "CentrifugalPump", "P-101B", shape=PUMP, at=(370, 225),
                  nozzles=[Nozzle("N1", (-7.5, 0), 100), Nozzle("N2", (7.5, 0), 80)],
                  label_at=(370, 240))

# ---- nitrous gas: E-102 (P-02) -> E-103 tubes -> E-104 -> E-105 -> V-101 -> K-102 (P-04)
line(sheet, "NX-203", dn=1400, fluid="Nitrous gas", route=[
    offpage("in", at=(LEFT, GAS), note="nitrous gas from E-102, P-02"), e103["T1"]],
    label_at=(35, 123))
line(sheet, "NX-301", dn=1100, fluid="Nitrous gas", route=[e103["T2"], e104["T1"]],
     label_at=(125, 106))
line(sheet, "NX-302", dn=1000, fluid="Nitrous gas", route=[e104["T2"], e105["T1"]],
     label_at=(205, 106))
line(sheet, "NX-303", dn=900, fluid="Nitrous gas and weak acid", route=[
    e105["T2"], v101["N1"]], label_at=(288, 123))
relief = tee("T304", at=(368, 90), branch="down", branch_dn=300)
line(sheet, "NX-304", dn=900, fluid="Nitrous gas", route=[
    v101["N2"], (320, 90), relief,
    offpage("out", at=(EDGE, 90), note="nitrous gas to K-102, P-04")], label_at=(344, 98))
# relief of the low-pressure nitrous gas system (D-021): E-102/E-104 tube rupture, E-103 leak,
# C-101 blow-by through C-102; discharge to the NOx vent stack, never to atmosphere at grade
psv316 = valve("PSV316", "GlobeValve", tag="PSV-316", at=(368, 100))
line(sheet, "RL-317", dn=300, fluid="Nitrous gas", route=[
    relief.branch, psv316, (368, 110),
    offpage("out", at=(EDGE, 110), note="to NOx vent stack")], label_at=(388, 117))
make_safety_valve(sheet, "PSV316", label_at=(380, 100))

# ---- tail gas: E-106 (P-04) -> E-103 shell -> R-102 (P-06), bypass TV-301
split = tee("T301", at=(40, BYPASS), branch="right", branch_dn=400)
line(sheet, "TG-402", dn=700, fluid="Tail gas", route=[
    offpage("in", at=(40, TOP), note="tail gas from E-106, P-04", rotation=90, note_at=(62, 12)),
    split, (40, 75), (75.2, 75), e103["S1"]], label_at=(29, 60))
join = tee("T302", at=(115, TAIL), branch="up", branch_dn=400)
line(sheet, "TG-310", dn=900, fluid="Tail gas", route=[
    e103["S2"], (94.8, TAIL), join,
    offpage("out", at=(EDGE, TAIL), note="tail gas to R-102, P-06")], label_at=(250, 37))
tv301 = valve("TV301", "GlobeValve", tag="TV-301", at=(75, BYPASS))
line(sheet, "TG-311", dn=400, fluid="Tail gas", route=[
    split.branch, tv301, (115, BYPASS), join.branch], label_at=(62, 40))

# ---- boiler feed water through the economiser to E-102 (P-02)
line(sheet, "BW-312", dn=100, fluid="Boiler feed water", route=[
    offpage("in", at=(174.8, BOTTOM), note="BFW from BFW pumps (B/L)", rotation=270,
            note_at=(196, 252)),
    e104["S3"]], label_at=(183, 190))
line(sheet, "BW-313", dn=100, fluid="Boiler feed water", route=[
    e104["S1"], (155.2, 60), offpage("out", at=(EDGE, 60), note="BFW to E-102, P-02")],
    label_at=(250, 52))

# ---- cooling water through the cooler-condenser
line(sheet, "CWS-314", dn=700, fluid="Cooling water", route=[
    offpage("in", at=(254.8, BOTTOM), note="CW supply (B/L)", rotation=270, note_at=(270, 252)),
    e105["S3"]], label_at=(243, 200))
line(sheet, "CWR-315", dn=700, fluid="Cooling water", route=[
    e105["S2"], (254.8, 75), offpage("out", at=(EDGE, 75), note="CW return (B/L)")],
    label_at=(243, 90))

# ---- weak acid: V-101 -> P-101A/B -> LV-305 -> C-101 (P-05)
pumps = tee("T305", at=(278, 225), branch="down", branch_dn=100)
line(sheet, "WA-305", dn=100, fluid="Weak acid", route=[
    v101["N3"], (320, 160), (270, 160), (270, 225), pumps,
    valve("HV305A", "GateValve", at=(285, 225)), valve("SR305A", "Strainer", at=(293, 225)),
    p101a["N1"]], label_at=(288, 205))
line(sheet, "WA-307", dn=100, fluid="Weak acid", route=[
    pumps.branch, (278, 245), (340, 245), (340, 225),
    valve("HV307", "GateValve", at=(346, 225)), valve("SR307", "Strainer", at=(354, 225)),
    p101b["N1"]], label_at=(310, 251))
header = tee("T306", at=(325, 190), branch="right", branch_dn=80)
lv305 = valve("LV305", "GlobeValve", tag="LV-305", at=(355, 180))
line(sheet, "WA-306", dn=80, fluid="Weak acid", route=[
    p101a["N2"], (325, 225), valve("CV306A", "SwingCheckValve", at=(325, 211)),
    valve("HV306A", "GateValve", at=(325, 203)), header, (325, 180), lv305,
    offpage("out", at=(EDGE, 180), note="weak acid to C-101, P-05")], label_at=(340, 172))
line(sheet, "WA-308", dn=80, fluid="Weak acid", route=[
    p101b["N2"], (385, 225), valve("CV308", "SwingCheckValve", at=(385, 211)),
    valve("HV308", "GateValve", at=(385, 203)), (385, 190), header.branch], label_at=(397, 206))

# ---- instruments
instrument(sheet, "TIC-301", at=(160, 22), sensing="Line_TG310_S2", sensing_at=(160, TAIL),
           signal_to=tv301, fail_action="FC")
instrument(sheet, "TI-302", at=(125, 140), sensing="Line_NX301_S1", sensing_at=(125, GAS))
instrument(sheet, "TI-303", at=(205, 140), sensing="Line_NX302_S1", sensing_at=(205, GAS))
instrument(sheet, "TI-304", at=(288, 100), sensing="Line_NX303_S1", sensing_at=(288, GAS))
instrument(sheet, "LIC-305", at=(355, 155), sensing=v101["N4"], sensing_points=[(355, 137)],
           signal_to=lv305, fail_action="FC")
instrument(sheet, "LZ-306", at=(290, 140), sensing=v101["N5"])
instrument(sheet, "PI-307", at=(345, 200), sensing="Line_WA306_S1", sensing_at=(325, 196),
           location="field")

valve_marks(sheet, "Inst_TIC301", "TV301", (75, BYPASS), "up")
valve_marks(sheet, "Inst_LIC305", "LV305", (355, 180), "up")

note(sheet, "TIC-301 holds the R-102 inlet temperature (N2O decomposition, SCR) with the E-103 "
     "tail-gas bypass TV-301 (D-019). LZ-306 stops P-101A/B: C&E I-301", at=(20, 262))
note(sheet, "PSV-316 protects the nitrous gas side from the gauze to the K-102 suction (E-102/E-104 "
     "tube rupture, E-103 leak, C-101 blow-by via C-102), D-021; BFW side: boiler package", at=(20, 269))
note(sheet, "P-101A/B: one running, one spare (D-018); minimum-flow protection open (relief "
     "study). DN and spec: D-017", at=(20, 276))

save(sheet, target)
