"""Draft of P-01: air compressor K-101 with inlet guide vanes, anti-surge blow-off and discharge
relief; ammonia evaporator E-101 with its level, pressure and high-high level trip; the SCR
ammonia branch to E-108 (P-06).

Provenance only: P-01 is hand-maintained (no `generator:` in plant.yaml); this script wrote
its first revision. Run: cheme run scripts/draft_P-01.py build/frames/P-01.xml pid/P-01.xml.
Equipment, lines, DN and instruments: DESIGN.md D-017 to D-019; streams S01-S09 of
process/flowsheet.yaml.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from chemeascode.domains.piping import authoring  # noqa: E402
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
    KETTLE,
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

AIR = 70        # main air line
NH3 = 190       # liquid ammonia feed line

# ---- equipment
k101 = equipment(sheet, "CentrifugalCompressor", "K-101", shape=COMPRESSOR, at=(150, AIR),
                 scale=2.0,
                 nozzles=[Nozzle("N1", (-15, 0), 1800), Nozzle("N2", (15, 0), 1100)],
                 label_at=(150, 94))
e101 = equipment(sheet, "TubularHeatExchanger", "E-101", shape=KETTLE, at=(175, 170), scale=1.6,
                 nozzles=[Nozzle("T1", (-28, -5.8), 300), Nozzle("T2", (-28, 2.6), 300),
                          Nozzle("S1", (4.2, 6.8), 80), Nozzle("V1", (9.8, -18.4), 250),
                          Nozzle("D1", (28, -1.6), 50), Nozzle("L1", (10, 6.8), 50),
                          Nozzle("L2", (24, 6.8), 50)],
                 label_at=(214, 183))

# ---- air: intake, inlet guide vanes, compressor, blow-off, relief, primary/secondary split
fv107 = valve("FV107", "ButterflyValve", tag="FV-107", at=(80, AIR))
line(sheet, "PA-104", dn=1800, fluid="Air", route=[
    offpage("in", at=(LEFT, AIR), note="from air intake filter (atmosphere)"),
    fv107, k101["N1"]], label_at=(105, 62))
blowoff = tee("T107", at=(185, AIR), branch="up", branch_dn=400)
relief = tee("T108", at=(245, AIR), branch="up", branch_dn=300)
secondary = tee("T106", at=(310, AIR), branch="down", branch_dn=400)
line(sheet, "PA-105", dn=1100, fluid="Air", route=[
    k101["N2"], blowoff, valve("CV105", "SwingCheckValve", at=(225, AIR)), relief, secondary,
    offpage("out", at=(EDGE, AIR), note="primary air to M-101, P-02")],
    label_at=(345, 62))
line(sheet, "PA-106", dn=400, fluid="Air", route=[
    secondary.branch, (310, 95),
    offpage("out", at=(EDGE, 95), note="secondary air to C-102, P-05")],
    label_at=(345, 87))
uv110 = valve("UV110", "GlobeValve", tag="UV-110", at=(185, 45))
line(sheet, "PA-107", dn=400, fluid="Air", route=[
    blowoff.branch, uv110, valve("SL114", "Silencer", tag="SL-114", at=(185, 28)),
    offpage("out", at=(185, TOP), note="to atmosphere", rotation=270, note_at=(171, 12))],
    labels=False)
psv111 = valve("PSV111", "GlobeValve", tag="PSV-111", at=(245, 45))
line(sheet, "PA-108", dn=300, fluid="Air", route=[
    relief.branch, psv111,
    offpage("out", at=(245, TOP), note="to atmosphere", rotation=270, note_at=(231, 12))],
    labels=False)

# ---- liquid ammonia: trip valve, evaporator level valve, evaporator, SCR branch
scr = tee("T103", at=(40, NH3), branch="down", branch_dn=25)
xv101 = valve("XV101", "BallValve", tag="XV-101", at=(110, NH3))
lv102 = valve("LV102", "GlobeValve", tag="LV-102", at=(150, NH3))
line(sheet, "NL-101", dn=80, fluid="Ammonia", route=[
    offpage("in", at=(LEFT, NH3), note="liquid NH3 from storage (B/L)"),
    scr, xv101, lv102, (179.2, NH3), e101["S1"]], label_at=(70, 182))
line(sheet, "NL-103", dn=25, fluid="Ammonia", route=[
    scr.branch, (40, 238),
    offpage("out", at=(EDGE, 238), note="liquid NH3 to E-108, P-06")],
    label_at=(300, 230))

# ---- ammonia vapour to the burner, evaporator relief, blowdown
psv_tee = tee("T102", at=(215, 140), branch="up", branch_dn=80)
line(sheet, "NV-102", dn=250, fluid="Ammonia", route=[
    e101["V1"], (184.8, 140), psv_tee,
    offpage("out", at=(EDGE, 140), note="NH3 vapour to M-101, P-02")],
    label_at=(300, 132))
psv105 = valve("PSV105", "GlobeValve", tag="PSV-105", at=(215, 128))
line(sheet, "RL-109", dn=80, fluid="Ammonia", route=[
    psv_tee.branch, psv105, (215, 118),
    offpage("out", at=(EDGE, 118), note="to NH3 relief header (B/L)")],
    label_at=(300, 110))
line(sheet, "DR-110", dn=50, fluid="Ammonia", route=[
    e101["D1"], valve("HV110", "GateValve", at=(240, 168.4)),
    offpage("out", at=(EDGE, 168.4), note="blowdown to NH3 drain pot (B/L)")],
    label_at=(300, 160))

# ---- chilled water from the absorber cooling coils (heat source of the evaporator)
pv104 = valve("PV104", "GlobeValve", tag="PV-104", at=(100, 164.2))
line(sheet, "CHS-111", dn=300, fluid="Chilled water", route=[
    offpage("in", at=(LEFT, 164.2), note="chilled water from C-101 coils, P-05"),
    pv104, e101["T1"]], label_at=(125, 158))
line(sheet, "CHR-112", dn=300, fluid="Chilled water", route=[
    e101["T2"], offpage("out", at=(LEFT, 172.6), note="chilled water to C-101 coils, P-05",
                         rotation=180, note_at=(38, 178))], label_at=(125, 178))

# ---- relief valves: placeholders made safety valves (pid_common.make_safety_valve)
make_safety_valve(sheet, "PSV105", label_at=(226, 128))
make_safety_valve(sheet, "PSV111", label_at=(256, 45))

# ---- instruments
instrument(sheet, "FIC-107", at=(50, 48), sensing="Line_PA104_S1", sensing_at=(50, AIR),
           signal_to=fv107, fail_action="FO")
instrument(sheet, "UIC-110", at=(205, 45), sensing="Line_PA105_S2", sensing_at=(205, AIR),
           signal_to=uv110, fail_action="FO")
instrument(sheet, "TI-112", at=(265, 88), sensing="Line_PA105_S3", sensing_at=(265, AIR))
instrument(sheet, "PI-113", at=(285, 52), sensing="Line_PA105_S3", sensing_at=(285, AIR),
           location="field")
instrument(sheet, "PIC-104", at=(100, 146), sensing="Line_NV102_S1", sensing_at=(184.8, 146),
           signal_to=pv104, fail_action="FC")
instrument(sheet, "TI-106", at=(245, 155), sensing="Line_NV102_S2", sensing_at=(245, 140))
instrument(sheet, "LIC-102", at=(150, 207), sensing=e101["L1"], signal_to=lv102,
           fail_action="FC")
instrument(sheet, "LZ-103", at=(110, 222), sensing=e101["L2"], signal_to=xv101,
           fail_action="FC")

valve_marks(sheet, "Inst_FIC107", "FV107", (80, AIR), "up")
valve_marks(sheet, "Inst_UIC110", "UV110", (185, 45), "right")
valve_marks(sheet, "Inst_PIC104", "PV104", (100, 164.2), "up")
valve_marks(sheet, "Inst_LIC102", "LV102", (150, NH3), "down")
valve_marks(sheet, "Inst_LZ103", "XV101", (110, NH3), "down")

note(sheet, TRAIN, at=(20, 262))
authoring.label(sheet, "SL114", "PipingComponentNumber", at=(195, 28))

note(sheet, "LZ-103, the burner trips and the train trip close XV-101: C&E I-101, I-201 to I-204, "
     "I-602. FIC-107 sets the plant air rate (load); UIC-110: K-101 anti-surge blow-off (D-018)",
     at=(20, 269))
note(sheet, "PSV-105 and PSV-111: set pressure and relief case in piping/special-items.yaml; "
     "load open (relief study). DN and spec: D-017", at=(20, 276))

save(sheet, target)
