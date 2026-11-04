"""Draft of P-01: toluene feed drum V-100, feed pumps P-101/P-101B, feed/effluent exchanger
E-101, fired heater H-101, reactor R-101 and the effluent quench.

Provenance only: P-01 is hand-maintained (no `generator:` in plant.yaml); this script wrote
its first revision. Run: cheme run scripts/draft_P-01.py <frame> [<out>]. Equipment, lines,
DN and instruments: DESIGN.md D-025; streams S1-S10, S27, S28 of process/flowsheet.yaml.
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
from pid_common import DRUM, HX, LEFT, PUMP, TOP, equipment, line, make_safety_valve, save  # noqa: E402

frame = Path(sys.argv[1])
target = Path(sys.argv[2]) if len(sys.argv) > 2 else frame
sheet = Sheet.load(frame)
BOTTOM = 248

# ---- equipment
v100 = equipment(sheet, "Vessel", "V-100", shape=DRUM, at=(60, 105), scale=(1.6, 1.3),
                 nozzles=[Nozzle("N1", (-16, -10), 80), Nozzle("N2", (16, -10), 40),
                          Nozzle("N3", (0, 19.5), 80), Nozzle("N4", (-16, 8), 50),
                          Nozzle("N5", (0, -19.5), 50), Nozzle("N6", (16, 8), 40),
                          Nozzle("N8", (10, -19.5), 80)],
                 label_at=(42, 136))
p101 = equipment(sheet, "CentrifugalPump", "P-101", shape=PUMP, at=(100, 172),
                 nozzles=[Nozzle("N1", (-7.5, 0), 80), Nozzle("N2", (0, -7.5), 80)],
                 label_at=(100, 184))
p101b = equipment(sheet, "CentrifugalPump", "P-101B", shape=PUMP, at=(145, 172),
                  nozzles=[Nozzle("N1", (-7.5, 0), 80), Nozzle("N2", (0, -7.5), 80)],
                  label_at=(145, 184))
e101 = equipment(sheet, "TubularHeatExchanger", "E-101", shape=HX, at=(215, 110), scale=1.2,
                 nozzles=[Nozzle("T1", (-21, 0), 350), Nozzle("T2", (21, 0), 450),
                          Nozzle("S1", (-7, -8.4), 300), Nozzle("S2", (7, 6), 400)],
                 label_at=(215, 128))
h101 = equipment(sheet, "Furnace", "H-101", shape="FURNACE_SHAPE", at=(300, 108), scale=1.6,
                 nozzles=[Nozzle("N1", (-16, 8), 400), Nozzle("N2", (16, 14), 400),
                          Nozzle("N3", (0, 20), 50)],
                 label_at=(300, 82))
r101 = equipment(sheet, "Vessel", "R-101", shape=DRUM, at=(362, 115), scale=(1.2, 1.6),
                 nozzles=[Nozzle("N1", (0, -24), 400), Nozzle("N2", (12, 20), 450),
                          Nozzle("N4", (-12, 18), 25)],
                 label_at=(375, 150))

# ---- recycle gas from K-101 (P-02): make-up hydrogen and toluene join it (M101), loop relief
h2_in = tee("T104", at=(208, 55), branch="left", branch_dn=80)
tol_in = tee("T103", at=(208, 80), branch="left", branch_dn=80)
relief = tee("T135", at=(208, 92), branch="right", branch_dn=150)
line(sheet, "HG-115", dn=300, fluid="Recycle gas", route=[
    offpage("in", at=(208, TOP), note="from K-101, P-02", rotation=90, note_at=(194, 12)),
    h2_in, tol_in, relief, e101["S1"]], label_at=(219, 28))
fv108 = valve("FV108", "GlobeValve", tag="FV-108", at=(182, 55))
line(sheet, "HG-104", dn=80, fluid="Hydrogen", route=[
    offpage("in", at=(150, TOP), note="from H2 supply (B/L)", rotation=90, note_at=(166, 12)),
    (150, 55), fv108, h2_in.branch], label_at=(159, 30))
psv119 = valve("PSV119", "GlobeValve", tag="PSV-119", at=(228, 70))
line(sheet, "FL-135", dn=150, fluid="Relief gas", route=[
    relief.branch, (228, 92), psv119,
    offpage("out", at=(228, TOP), note="to flare header, P-07", rotation=270, note_at=(245, 12))],
    label_at=(219, 64))

# ---- fresh and recycle toluene to V-100; V-100 blanketing, vent and relief
lv102 = valve("LV102", "GlobeValve", tag="LV-102", at=(32, 95))
line(sheet, "TO-101", dn=80, fluid="Toluene", route=[
    offpage("in", at=(LEFT, 95), note="from tanks (B/L)", note_at=(21, 109)),
    lv102, v100["N1"]], label_at=(22, 99.5))
line(sheet, "TO-123", dn=40, fluid="Toluene", route=[
    offpage("in", at=(88, TOP), note="from P-203A/B, P-06", rotation=90, note_at=(103, 12)),
    (88, 95), v100["N2"]], label_at=(97, 40))
vent_in = tee("T134", at=(70, 30), branch="left", branch_dn=50)
psv118 = valve("PSV118", "GlobeValve", tag="PSV-118", at=(70, 60))
line(sheet, "FL-133", dn=80, fluid="Relief gas", route=[
    v100["N8"], psv118, vent_in,
    offpage("out", at=(70, TOP), note="to flare header, P-07", rotation=270, note_at=(55, 12))],
    label_at=(79, 46))
pv104 = valve("PV104", "GlobeValve", tag="PV-104", at=(60, 62))
n2_in = tee("T136", at=(60, 76), branch="left", branch_dn=25)
line(sheet, "FL-134", dn=50, fluid="Relief gas", route=[
    v100["N5"], n2_in, pv104, (60, 30), vent_in.branch], label_at=(52, 40))
pcv105 = valve("PCV105", "GlobeValve", tag="PCV-105", at=(36, 76))
line(sheet, "N2-136", dn=25, fluid="Nitrogen", route=[
    offpage("in", at=(LEFT, 76), note="from N2 header, P-07", note_at=(24, 82)),
    pcv105, n2_in.branch], label_at=(24, 68))

# ---- feed pumps, minimum flow, reactor toluene feed
suction = tee("T102", at=(72, 172), branch="down", branch_dn=80)
line(sheet, "TO-102", dn=80, fluid="Toluene", route=[
    v100["N3"], (60, 172), suction, valve("HV102A", "GateValve", at=(79, 172)),
    valve("SR102A", "Strainer", at=(86, 172)), p101["N1"]], label_at=(69, 150))
line(sheet, "TO-130", dn=80, fluid="Toluene", route=[
    suction.branch, (72, 195), (125, 195), valve("HV130", "GateValve", at=(125, 188)),
    valve("SR130", "Strainer", at=(125, 180)), (125, 172), p101b["N1"]],
    label_at=(90, 198))
join = tee("T103A", at=(100, 145), branch="right", branch_dn=80)
minflow = tee("T103B", at=(100, 136), branch="left", branch_dn=40)
fv103 = valve("FV103", "GlobeValve", tag="FV-103", at=(100, 112))
line(sheet, "TO-103", dn=80, fluid="Toluene", route=[
    p101["N2"], valve("CV103", "SwingCheckValve", at=(100, 159)),
    valve("HV103", "GateValve", at=(100, 152)), join, minflow, fv103, (100, 80), tol_in.branch],
    label_at=(120, 75))
line(sheet, "TO-131", dn=80, fluid="Toluene", route=[
    p101b["N2"], valve("CV131", "SwingCheckValve", at=(145, 159)),
    valve("HV131", "GateValve", at=(145, 152)), (145, 145), join.branch], label_at=(158, 150))
fv106 = valve("FV106", "GlobeValve", tag="FV-106", at=(90, 136))
line(sheet, "TO-132", dn=40, fluid="Toluene", route=[
    minflow.branch, fv106, (80, 136), (80, 113), v100["N6"]], label_at=(89, 122))

# ---- feed / effluent exchanger, fired heater, reactor
line(sheet, "PG-106", dn=400, fluid="Reactor feed", route=[e101["S2"], h101["N1"]],
     label_at=(255, 120))
line(sheet, "PG-107", dn=400, fluid="Reactor feed", route=[
    h101["N2"], (335, 122), (335, 72), (362, 72), r101["N1"]], label_at=(338, 66))
quench = tee("T117", at=(300, 40), branch="up", branch_dn=40)
line(sheet, "PG-108", dn=450, fluid="Reactor effluent", route=[
    r101["N2"], (398, 135), (398, 40), quench, (240, 40), (240, 110), e101["T2"]],
    label_at=(375, 31))
tv115 = valve("TV115", "GlobeValve", tag="TV-115", at=(300, 27))
line(sheet, "AR-117", dn=40, fluid="Crude aromatics", route=[
    offpage("in", at=(300, TOP), note="from P-102/P-102B, P-02", rotation=90, note_at=(322, 12)),
    tv115, quench.branch], label_at=(310, 22))
line(sheet, "PG-110", dn=350, fluid="Reactor effluent", route=[
    e101["T1"], (185, 110),
    offpage("out", at=(185, BOTTOM), note="to E-102, P-02", rotation=90, note_at=(202, 252))],
    label_at=(194, 160))

# ---- fuel to the H-101 burners
xv112 = valve("XV112", "BallValve", tag="XV-112", at=(300, 222))
tv111 = valve("TV111", "GlobeValve", tag="TV-111", at=(300, 190))
line(sheet, "NG-137", dn=50, fluid="Natural gas", route=[
    offpage("in", at=(300, BOTTOM), note="from natural gas header, P-07", rotation=270,
            note_at=(325, 252)),
    xv112, tv111, h101["N3"]], label_at=(309, 150))

# ---- relief valves: placeholders made safety valves (pid_common.make_safety_valve)
make_safety_valve(sheet, "PSV118", label_at=(80, 60))
make_safety_valve(sheet, "PSV119", label_at=(218, 75))

# ---- instruments
instrument(sheet, "LIC-102", at=(25, 125), sensing=v100["N4"], signal_to=lv102,
           signal_points=[(32, 125)])
instrument(sheet, "FIC-103", at=(116, 120), sensing="Line_TO103_S3", sensing_at=(100, 124),
           signal_to=fv103)
instrument(sheet, "PIC-104", at=(45, 58), sensing="Line_FL134_S2", sensing_at=(60, 70),
           signal_to=pv104)
instrument(sheet, "FIC-106", at=(84, 152), sensing="Line_TO103_S1", sensing_at=(100, 148),
           signal_to=fv106)
instrument(sheet, "FIC-108", at=(166, 70), sensing="Line_HG104_S1", sensing_at=(166, 55),
           signal_to=fv108)
instrument(sheet, "TI-109", at=(268, 136), sensing="Line_PG106_S1", sensing_at=(268, 116))
instrument(sheet, "FZ-110", at=(246, 136), sensing="Line_PG106_S1", sensing_at=(246, 116))
instrument(sheet, "US-112", at=(325, 222), signal_to=xv112)
instrument(sheet, "TIC-111", at=(326, 150), sensing="Line_PG107_S1", sensing_at=(326, 122),
           signal_to=tv111, signal_points=[(326, 190)])
instrument(sheet, "TZ-113", at=(342, 160), sensing=r101["N4"], signal_to="Inst_US112",
           signal_points=[(342, 222)])
instrument(sheet, "TIC-115", at=(275, 27), sensing="Line_PG108_S2", sensing_at=(275, 40),
           signal_to=tv115)
instrument(sheet, "TI-116", at=(170, 205), sensing="Line_PG110_S1", sensing_at=(185, 205))

note(sheet, "E-101: two shells in series (D-017, D-024). H-101 burner management in the heater package; "
     "trips FZ-110, TZ-113: C&E I-101", at=(20, 262))
note(sheet, "PSV-119 protects the loop from E-101 inlet through H-101 coil, R-101 and E-101 tube side "
     "(no isolation valve between); set and case: S8", at=(20, 269))
note(sheet, "FIC-108 set point from PIC-205 (loop pressure, P-02). PCV-105: self-acting N2 blanket "
     "regulator. Spec and DN: D-025", at=(20, 276))

save(sheet, target)
