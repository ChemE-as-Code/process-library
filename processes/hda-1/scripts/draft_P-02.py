"""Draft of P-02: effluent trim cooler E-102, high-pressure separator V-101, quench pumps
P-102/P-102B, recycle gas compressor K-101 with anti-surge recycle, purge take-off to the PSA
and loop depressuring.

Provenance only: P-02 is hand-maintained (no `generator:` in plant.yaml); this script wrote
its first revision. Run: cheme run scripts/draft_P-02.py <frame> [<out>]. Equipment, lines,
DN and instruments: DESIGN.md D-025; streams S10-S18, S27, S31 of process/flowsheet.yaml.
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
from pid_common import DRUM, EDGE, HX, LEFT, PUMP, TOP, equipment, line, make_safety_valve, save  # noqa: E402

frame = Path(sys.argv[1])
target = Path(sys.argv[2]) if len(sys.argv) > 2 else frame
sheet = Sheet.load(frame)
BOTTOM = 248

# ---- equipment
e102 = equipment(sheet, "TubularHeatExchanger", "E-102", shape=HX, at=(80, 80), scale=1.2,
                 nozzles=[Nozzle("T1", (-21, 0), 350), Nozzle("T2", (21, 0), 300),
                          Nozzle("S1", (-7, 8.4), 350), Nozzle("S2", (7, -8.4), 350)],
                 label_at=(62, 95))
v101 = equipment(sheet, "Vessel", "V-101", shape=DRUM, at=(150, 100), scale=(1.4, 1.6),
                 nozzles=[Nozzle("N1", (-14, -12), 300), Nozzle("N2", (0, -24), 250),
                          Nozzle("N3", (0, 24), 100), Nozzle("N4", (-10, -24), 150),
                          Nozzle("N5", (-14, 4), 50), Nozzle("N6", (-14, 18), 50),
                          Nozzle("N7", (14, 0), 25), Nozzle("N8", (14, -14), 50),
                          Nozzle("N9", (-8, 24), 50)],
                 label_at=(150, 100))
k101 = equipment(sheet, "CentrifugalCompressor", "K-101", shape="COMPRESSOR_CENTRIFUGAL_SHAPE",
                 at=(270, 50), scale=2.0,
                 nozzles=[Nozzle("N1", (-15, 0), 250), Nozzle("N2", (15, 0), 300)],
                 label_at=(270, 71))
p102 = equipment(sheet, "CentrifugalPump", "P-102", shape=PUMP, at=(200, 205),
                 nozzles=[Nozzle("N1", (-7.5, 0), 50), Nozzle("N2", (0, -7.5), 40)],
                 label_at=(200, 217))
p102b = equipment(sheet, "CentrifugalPump", "P-102B", shape=PUMP, at=(240, 205),
                  nozzles=[Nozzle("N1", (-7.5, 0), 50), Nozzle("N2", (0, -7.5), 40)],
                  label_at=(240, 217))

# ---- effluent from E-101 (P-01) through the trim cooler to the separator
line(sheet, "PG-110", dn=350, fluid="Reactor effluent", route=[
    offpage("in", at=(LEFT, 80), note="from E-101, P-01", note_at=(24, 86)), e102["T1"]],
    label_at=(30, 72))
line(sheet, "PG-111", dn=300, fluid="Reactor effluent", route=[
    e102["T2"], (120, 80), (120, 88), v101["N1"]], label_at=(112, 92))
line(sheet, "CWS-230", dn=350, fluid="Cooling water", route=[
    offpage("in", at=(LEFT, 110), note="from CW supply, P-08", note_at=(26, 116)),
    (73, 110), e102["S1"]], label_at=(45, 104))
cw_relief = tee("T238", at=(87, 55), branch="right", branch_dn=80)
line(sheet, "CWR-231", dn=350, fluid="Cooling water", route=[
    e102["S2"], cw_relief, (87, 40),
    offpage("out", at=(LEFT, 40), note="to CW return, P-08", rotation=180, note_at=(26, 34))],
    label_at=(45, 46))
psv215 = valve("PSV215", "GlobeValve", tag="PSV-215", at=(100, 40))
line(sheet, "CWR-238", dn=80, fluid="Cooling water", route=[
    cw_relief.branch, (100, 55), psv215,
    offpage("out", at=(100, TOP), note="to atmosphere (safe location)", rotation=270,
            note_at=(84, 9))],
    label_at=(110, 46))

# ---- separator gas to K-101: depressuring, PSA hydrogen (M102), anti-surge return
dep_out = tee("T233", at=(170, 50), branch="up", branch_dn=100)
h2_in = tee("T125", at=(195, 50), branch="up", branch_dn=40)
asr_in = tee("T232A", at=(222, 50), branch="down", branch_dn=200)
line(sheet, "HG-112", dn=250, fluid="Recycle gas", route=[
    v101["N2"], (150, 50), dep_out, h2_in, asr_in, k101["N1"]], label_at=(238, 41))
line(sheet, "HG-125", dn=40, fluid="Hydrogen", route=[
    offpage("in", at=(195, TOP), note="from PK-101, P-03", rotation=90, note_at=(212, 12)),
    h2_in.branch], label_at=(203, 30))
dep_in = tee("T234", at=(140, 28), branch="right", branch_dn=100)
psv214 = valve("PSV214", "GlobeValve", tag="PSV-214", at=(140, 60))
line(sheet, "FL-234", dn=150, fluid="Relief gas", route=[
    v101["N4"], psv214, dep_in,
    offpage("out", at=(140, TOP), note="to flare header, P-07", rotation=270, note_at=(122, 12))],
    label_at=(130, 40))
xv209 = valve("XV209", "BallValve", tag="XV-209", at=(170, 38))
line(sheet, "FL-233", dn=100, fluid="Relief gas", route=[
    dep_out.branch, xv209, (170, 28), dep_in.branch], label_at=(181, 22))

# ---- K-101 discharge: anti-surge take-off, check valve, purge to the PSA, recycle to P-01
asr_out = tee("T232B", at=(295, 50), branch="down", branch_dn=200)
purge = tee("T113", at=(335, 50), branch="down", branch_dn=80)
line(sheet, "HG-115", dn=300, fluid="Recycle gas", route=[
    k101["N2"], asr_out, valve("CV115", "SwingCheckValve", at=(315, 50)), purge,
    offpage("out", at=(EDGE, 50), note="to M101 (E-101), P-01", note_at=(385, 44))],
    label_at=(372, 56))
uv207 = valve("UV207", "GlobeValve", tag="UV-207", at=(258, 85))
line(sheet, "HG-232", dn=200, fluid="Recycle gas", route=[
    asr_out.branch, (295, 85), uv207, (222, 85), asr_in.branch], label_at=(240, 91))
fv211 = valve("FV211", "GlobeValve", tag="FV-211", at=(335, 78))
line(sheet, "HG-113", dn=80, fluid="Purge gas", route=[
    purge.branch, fv211, (335, 100),
    offpage("out", at=(EDGE, 100), note="to PK-101, P-03", note_at=(388, 94))],
    label_at=(372, 106))

# ---- separator liquid: let-down to C-201 (P-04), quench pumps P-102/P-102B
to_pumps = tee("T235", at=(150, 132), branch="right", branch_dn=50)
lv202 = valve("LV202", "GlobeValve", tag="LV-202", at=(118, 140))
xv204 = valve("XV204", "BallValve", tag="XV-204", at=(138, 140))
line(sheet, "AR-116", dn=100, fluid="Crude aromatics", route=[
    v101["N3"], to_pumps, (150, 140), xv204, lv202, (40, 140),
    offpage("out", at=(40, BOTTOM), note="to C-201, P-04", rotation=90, note_at=(57, 252))],
    label_at=(80, 146))
suction = tee("T239", at=(170, 205), branch="down", branch_dn=50)
line(sheet, "AR-235", dn=50, fluid="Crude aromatics", route=[
    to_pumps.branch, (165, 132), (165, 205), suction, valve("HV235", "GateValve", at=(178, 205)),
    valve("SR235", "Strainer", at=(185, 205)), p102["N1"]], label_at=(156, 175))
line(sheet, "AR-239", dn=50, fluid="Crude aromatics", route=[
    suction.branch, (170, 230), (225, 230), valve("HV239", "GateValve", at=(225, 223)),
    valve("SR239", "Strainer", at=(225, 215)), (225, 205), p102b["N1"]], label_at=(195, 236))
join = tee("T236", at=(200, 175), branch="right", branch_dn=40)
minflow = tee("T237", at=(200, 165), branch="left", branch_dn=25)
line(sheet, "AR-117", dn=40, fluid="Crude aromatics", route=[
    p102["N2"], valve("CV117", "SwingCheckValve", at=(200, 190)),
    valve("HV117", "GateValve", at=(200, 183)), join, minflow, (200, 155),
    offpage("out", at=(EDGE, 155), note="to TV-115 (quench), P-01", note_at=(380, 149))],
    label_at=(300, 161))
line(sheet, "AR-236", dn=40, fluid="Crude aromatics", route=[
    p102b["N2"], valve("CV236", "SwingCheckValve", at=(240, 190)),
    valve("HV236", "GateValve", at=(240, 183)), (240, 175), join.branch], label_at=(252, 180))
line(sheet, "AR-237", dn=25, fluid="Crude aromatics", route=[
    minflow.branch, valve("HV237", "GlobeValve", at=(186, 165)), (175, 165), (175, 100),
    v101["N7"]], label_at=(184, 120))

# ---- drain to the closed drain system
line(sheet, "DR-240", dn=50, fluid="Drain", route=[
    v101["N9"], valve("HV240", "GateValve", at=(142, 130)),
    offpage("out", at=(142, 137), note="to closed drain", rotation=90,
            note_at=(128, 141))], labels=False)

# ---- relief valves
make_safety_valve(sheet, "PSV214", label_at=(128, 64))
make_safety_valve(sheet, "PSV215", label_at=(112, 34))

# ---- instruments
instrument(sheet, "TI-201", at=(110, 65), sensing="Line_PG111_S1", sensing_at=(110, 80))
instrument(sheet, "LIC-202", at=(110, 104), sensing=v101["N5"], signal_to=lv202,
           signal_points=[(100, 104), (100, 130), (118, 130)])
instrument(sheet, "LZ-203", at=(124, 118), sensing=v101["N6"], signal_to=xv204,
           signal_points=[(124, 128), (138, 128)])
instrument(sheet, "LZ-206", at=(182, 86), sensing=v101["N8"])
instrument(sheet, "PIC-205", at=(163, 66), sensing="Line_HG112_S1", sensing_at=(150, 66))
instrument(sheet, "UIC-207", at=(240, 66), sensing="Line_HG112_S4", sensing_at=(240, 50),
           signal_to=uv207)
instrument(sheet, "HS-209", at=(183, 38), signal_to=xv209)
instrument(sheet, "FIC-211", at=(362, 84), sensing="Line_HG113_S1", sensing_at=(360, 100),
           signal_to=fv211)
instrument(sheet, "AIC-210", at=(385, 68), sensing="Line_HG115_S3", sensing_at=(385, 50),
           signal_to="Inst_FIC211")

note(sheet, "PIC-205: loop pressure at V-101, sets FIC-108 (make-up hydrogen, P-01). AIC-210: H2 in the "
     "recycle gas, sets the purge FIC-211. LZ-203 (XV-204): C&E I-201; LZ-206: C&E I-202", at=(20, 262))
note(sheet, "K-101: anti-surge UIC-207/UV-207; lube oil, seals and machine protection in the package; no "
     "discharge PSV (D-025). HS-209 opens XV-209: manual loop depressuring", at=(20, 269))
note(sheet, "PSV-214: V-101 fire and loop blocked outlet; PSV-215: E-102 tube rupture (42 barg into CW); "
     "HV-237: continuous minimum flow of P-102/P-102B (D-025)", at=(20, 276))

save(sheet, target)
