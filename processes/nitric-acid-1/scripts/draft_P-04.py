"""Draft of P-04: NOx compressor K-102 with the bleacher gas junction (M102), anti-surge recycle
and the relief of the high-pressure system, NOx gas / tail gas exchanger E-106 and NOx gas
cooler E-107.

Provenance only: P-04 is hand-maintained (no `generator:` in plant.yaml); this script wrote
its first revision. Run: cheme run scripts/draft_P-04.py build/frames/P-04.xml pid/P-04.xml.
Equipment, lines, DN and instruments: DESIGN.md D-017 to D-020; streams S16, S19-S23, S25, S26
and the energy stream Q08 of process/flowsheet.yaml.
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
    COMPRESSOR,
    EDGE,
    HX,
    LEFT,
    TOP,
    TRAIN,
    equipment,
    line,
    make_safety_valve,
    save,
    valve_marks,
)

frame = Path(sys.argv[1])
target = Path(sys.argv[2]) if len(sys.argv) > 2 else frame
sheet = Sheet.load(frame)

GAS = 110       # nitrous gas through K-102, E-106, E-107
TAIL_IN = 200   # tail gas from C-101
TAIL_OUT = 40   # tail gas to E-103

# ---- equipment
k102 = equipment(sheet, "CentrifugalCompressor", "K-102", shape=COMPRESSOR, at=(95, GAS),
                 scale=2.0,
                 nozzles=[Nozzle("N1", (-15, 0), 900), Nozzle("N2", (15, 0), 800)],
                 label_at=(95, 88))
e106 = equipment(sheet, "TubularHeatExchanger", "E-106", shape=HX, at=(190, GAS), scale=1.4,
                 nozzles=[Nozzle("T1", (-24.5, 0), 800), Nozzle("T2", (24.5, 0), 700),
                          Nozzle("S2", (9.8, -9.8), 700), Nozzle("S3", (-9.8, 9.8), 600)],
                 label_at=(200, 130))
e107 = equipment(sheet, "TubularHeatExchanger", "E-107", shape=HX, at=(265, GAS), scale=1.4,
                 nozzles=[Nozzle("T1", (-24.5, 0), 700), Nozzle("T2", (24.5, 0), 700),
                          Nozzle("S3", (9.8, 9.8), 200), Nozzle("S4", (-9.8, 9.8), 200)],
                 label_at=(265, 95))

# ---- NOx gas from V-101 (P-03), bleacher gas joins (M102), anti-surge return, K-102
bleach_in = tee("T401", at=(35, GAS), branch="up", branch_dn=350)
recycle_in = tee("T402", at=(60, GAS), branch="down", branch_dn=300)
line(sheet, "NX-304", dn=900, fluid="Nitrous gas", route=[
    offpage("in", at=(LEFT, GAS), note="nitrous gas from V-101, P-03", note_at=(36, 116)),
    bleach_in, recycle_in, k102["N1"]], label_at=(48, 101))
line(sheet, "BG-503", dn=350, fluid="Bleacher gas", route=[
    offpage("in", at=(LEFT, 70), note="bleacher gas from C-102, P-05"), (35, 70),
    bleach_in.branch], label_at=(25, 78))

# ---- discharge: anti-surge take-off, check valve, relief, E-106 hot side
recycle_out = tee("T403", at=(122, GAS), branch="down", branch_dn=300)
relief = tee("T404", at=(146, GAS), branch="up", branch_dn=300)
line(sheet, "NX-401", dn=800, fluid="Nitrous gas", route=[
    k102["N2"], recycle_out, valve("CV401", "SwingCheckValve", at=(134, GAS)), relief,
    e106["T1"]], label_at=(156, 102))
uv401 = valve("UV401", "GlobeValve", tag="UV-401", at=(92, 155))
line(sheet, "NX-404", dn=300, fluid="Nitrous gas", route=[
    recycle_out.branch, (122, 155), uv401, (60, 155), recycle_in.branch], label_at=(108, 163))
psv404 = valve("PSV404", "GlobeValve", tag="PSV-404", at=(146, 80))
line(sheet, "RL-405", dn=300, fluid="Nitrous gas", route=[
    relief.branch, psv404,
    offpage("out", at=(146, TOP), note="to NOx vent stack", rotation=270, note_at=(128, 12))],
    label_at=(134, 55))
make_safety_valve(sheet, "PSV404", label_at=(158, 80))

# ---- E-106 hot side -> E-107 -> C-101 (P-05)
line(sheet, "NX-402", dn=700, fluid="Nitrous gas", route=[e106["T2"], e107["T1"]],
     label_at=(228, 102))
line(sheet, "NX-403", dn=700, fluid="Nitrous gas", route=[
    e107["T2"], offpage("out", at=(EDGE, GAS), note="nitrous gas to C-101, P-05")],
    label_at=(370, 102))

# ---- tail gas: C-101 (P-05) -> E-106 shell -> E-103 (P-03)
line(sheet, "TG-501", dn=600, fluid="Tail gas", route=[
    offpage("in", at=(LEFT, TAIL_IN), note="tail gas from C-101, P-05"),
    (180.2, TAIL_IN), e106["S3"]], label_at=(100, 192))
line(sheet, "TG-402", dn=700, fluid="Tail gas", route=[
    e106["S2"], (199.8, TAIL_OUT),
    offpage("out", at=(EDGE, TAIL_OUT), note="tail gas to E-103, P-03")], label_at=(250, 32))

# ---- cooling water through E-107
line(sheet, "CWS-406", dn=200, fluid="Cooling water", route=[
    offpage("in", at=(274.8, BOTTOM), note="CW supply (B/L)", rotation=270, note_at=(292, 252)),
    e107["S3"]], label_at=(285, 180))
line(sheet, "CWR-407", dn=200, fluid="Cooling water", route=[
    e107["S4"], offpage("out", at=(255.2, BOTTOM), note="CW return (B/L)", rotation=90,
                         note_at=(238, 252))], label_at=(244, 180))

# ---- instruments
instrument(sheet, "UIC-401", at=(92, 140), sensing="Line_NX304_S3", sensing_at=(70, GAS),
           sensing_points=[(70, 140)], signal_to=uv401, fail_action="FO")
instrument(sheet, "TI-402", at=(156, 130), sensing="Line_NX401_S3", sensing_at=(156, GAS))
instrument(sheet, "TI-405", at=(228, 130), sensing="Line_NX402_S1", sensing_at=(228, GAS))
instrument(sheet, "TI-406", at=(330, 130), sensing="Line_NX403_S1", sensing_at=(330, GAS))
instrument(sheet, "PI-403", at=(355, 130), sensing="Line_NX403_S1", sensing_at=(355, GAS),
           location="field")
instrument(sheet, "TI-407", at=(300, 55), sensing="Line_TG402_S1", sensing_at=(300, TAIL_OUT))

valve_marks(sheet, "Inst_UIC401", "UV401", (92, 155), "up")

note(sheet, "UIC-401: K-102 hot recycle (D-018), limited by TI-402 TAH and C&E I-401. " + TRAIN,
     at=(20, 262))
note(sheet, "PSV-404 protects the high-pressure system from K-102 to the X-101 inlet valves "
     "(E-106, E-107, C-101, E-103 cold side, R-102); set and case: piping/special-items.yaml",
     at=(20, 269))
note(sheet, "E-107 condensate (weak acid, D-016) drains with the gas to C-101. DN and spec: D-017",
     at=(20, 276))

save(sheet, target)
