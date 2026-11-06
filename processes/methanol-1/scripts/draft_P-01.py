"""Draft of P-01: make-up gas suction knock-out drum V-103, make-up gas compressor K-101 with its
cooled anti-surge recycle, aftercooler E-101.

Provenance only: P-01 is hand-maintained (no `generator:` in plant.yaml); this script wrote
its first revision. Run: cheme run scripts/draft_P-01.py <frame> [<out>]. Equipment, lines,
DN and instruments: DESIGN.md D-016, D-017; streams S1-S3 of process/flowsheet.yaml.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from chemeascode.domains.piping.authoring import (  # noqa: E402
    Nozzle,
    Sheet,
    instrument,
    offpage,
    tee,
    valve,
)
from pid_common import (  # noqa: E402
    BOTTOM,
    COMPRESSOR,
    DRUM,
    EDGE,
    HX,
    LEFT,
    TOP,
    equipment,
    fail_label,
    line,
    make_safety_valve,
    notes,
    save,
    tag_label,
)

frame = Path(sys.argv[1])
target = Path(sys.argv[2]) if len(sys.argv) > 2 else frame
sheet = Sheet.load(frame)
Y = 120          # compressor and aftercooler centre line
ASR = 200        # anti-surge recycle run
FEED = 164       # make-up gas into the knock-out drum

# ---- equipment
v103 = equipment(sheet, "Vessel", "V-103", shape=DRUM, at=(100, 170), scale=(1.4, 1.6),
                 nozzles=[Nozzle("N1", (-14, -6), 600), Nozzle("N2", (0, -24), 600),
                          Nozzle("N3", (0, 24), 50), Nozzle("N4", (-14, 14), 50),
                          Nozzle("N5", (14, 8), 50), Nozzle("N6", (-8, -23), 150)],
                 label_at=(100, 170))
k101 = equipment(sheet, "CentrifugalCompressor", "K-101", shape=COMPRESSOR, at=(195, Y),
                 scale=2.0,
                 nozzles=[Nozzle("N1", (-15, 0), 600), Nozzle("N2", (15, 0), 400),
                          Nozzle("N3", (0, -15))],
                 label_at=(195, 143))
e101 = equipment(sheet, "TubularHeatExchanger", "E-101", shape=HX, at=(300, Y), scale=1.2,
                 nozzles=[Nozzle("T1", (-21, 0), 400), Nozzle("T2", (21, 0), 350),
                          Nozzle("S1", (10, -8.4), 600), Nozzle("S2", (-10, -8.4), 600)],
                 label_at=(300, 136))

# ---- make-up gas from the battery limit through the shutdown valve to the knock-out drum
xv110 = valve("XV110", "BallValve", tag="XV-110", at=(62, FEED))
line(sheet, "SG-101", dn=600, fluid="Synthesis gas", route=[
    offpage("in", at=(LEFT, FEED), note="from front end (B/L)"),
    xv110, v103["N1"]], label_at=(75, 150))
line(sheet, "DR-135", dn=50, fluid="Drain", route=[
    v103["N3"], valve("HV135", "GateValve", at=(100, 215)),
    offpage("out", at=(100, BOTTOM), note="to closed drain", rotation=90, note_at=(116, 244))],
    label_at=(112, 228))

# ---- suction side relief (V-103, SG-130, K-101 suction: settle-out through UV-104, fire)
psv115 = valve("PSV115", "GlobeValve", tag="PSV-115", at=(92, 128))
line(sheet, "FL-136", dn=150, fluid="Relief gas", route=[
    v103["N6"], psv115,
    offpage("out", at=(92, TOP), note="to HP flare header", rotation=270, note_at=(74, 20))],
    label_at=(80, 60))
make_safety_valve(sheet, "PSV115", label_at=(80, 128))

# ---- drum gas to the compressor suction; the anti-surge return joins at T131
asr_in = tee("T131", at=(150, Y), branch="down", branch_dn=300)
line(sheet, "SG-130", dn=600, fluid="Synthesis gas", route=[
    v103["N2"], (100, Y), asr_in, k101["N1"]], label_at=(165, 109))

# ---- discharge: relief take-off, aftercooler, anti-surge take-off, check valve, to P-02
psv_out = tee("T111", at=(248, Y), branch="up", branch_dn=150)
line(sheet, "SG-102", dn=400, fluid="Synthesis gas", route=[
    k101["N2"], psv_out, e101["T1"]], label_at=(264, 126))
asr_out = tee("T131B", at=(345, Y), branch="down", branch_dn=300)
xv116 = valve("XV116", "BallValve", tag="XV-116", at=(380, Y))
line(sheet, "SG-103", dn=350, fluid="Synthesis gas", route=[
    e101["T2"], asr_out, valve("CV103", "SwingCheckValve", tag="CV-103", at=(363, Y)), xv116,
    offpage("out", at=(EDGE, Y), note="to K-102 suction, P-02", note_at=(386, 113))],
    label_at=(356, 128))
uv104 = valve("UV104", "GlobeValve", tag="UV-104", at=(195, ASR))
line(sheet, "SG-131", dn=300, fluid="Synthesis gas", route=[
    asr_out.branch, (345, ASR), uv104, (150, ASR), asr_in.branch], label_at=(290, 208))

# ---- relief to the flare header: K-101 discharge and the E-101 cooling water side
flare_join = tee("T134", at=(248, 40), branch="right", branch_dn=80)
psv111 = valve("PSV111", "GlobeValve", tag="PSV-111", at=(248, 85))
line(sheet, "FL-132", dn=150, fluid="Relief gas", route=[
    psv_out.branch, psv111, flare_join,
    offpage("out", at=(248, TOP), note="to HP flare header", rotation=270, note_at=(228, 20))],
    label_at=(234, 60))
cw_relief = tee("T133", at=(290, 70), branch="left", branch_dn=80)
line(sheet, "CWR-133", dn=600, fluid="Cooling water return", route=[
    e101["S2"], cw_relief,
    offpage("out", at=(290, TOP), note="CW return", rotation=270, note_at=(278, 20))],
    label_at=(279, 88))
line(sheet, "CWS-132", dn=600, fluid="Cooling water", route=[
    offpage("in", at=(310, TOP), note="CW supply", rotation=90, note_at=(324, 20)),
    e101["S1"]], label_at=(323, 70))
psv112 = valve("PSV112", "GlobeValve", tag="PSV-112", at=(270, 55))
line(sheet, "FL-134", dn=80, fluid="Relief gas", route=[
    cw_relief.branch, (270, 70), psv112, (270, 40), flare_join.branch], label_at=(259, 31))
make_safety_valve(sheet, "PSV111", label_at=(236, 85))
make_safety_valve(sheet, "PSV112", label_at=(259, 55))

# ---- instruments
instrument(sheet, "FI-101", at=(32, 146), sensing="Line_SG101_S1", sensing_at=(32, FEED))
instrument(sheet, "LZ-109", at=(62, 184), sensing=v103["N4"], signal_to=xv110, fail_action="FC")
instrument(sheet, "LI-108", at=(134, 178), sensing=v103["N5"])
sic = instrument(sheet, "SIC-113", at=(195, 98), sensing=k101["N3"])
# N3 is the speed pick-up of SIC-113 on the casing, not a process connection: an instrument
# nozzle, so that the nozzle lists and datasheets do not count it as a process nozzle (round 4).
sheet.find("K101_N3").set("type", "Plant/ProcessEquipment.InstrumentNozzle")
us116 = instrument(sheet, "US-116", at=(380, 140), signal_to=xv116, fail_action="FC")
fail_label(sheet, "Inst_US116", (380, Y), "down-left")
# K-101 run status from the drive package into US-116: every K-101 stop (package machine trip,
# power failure, operator stop) closes XV-116, not only the C&E trips (C&E I-102, D-022).
instrument(sheet, "YS-117", at=(380, 165), signal_to=us116)
instrument(sheet, "PIC-102", at=(120, 98), sensing="Line_SG130_S1", sensing_at=(120, Y),
           signal_to=sic)
uic = instrument(sheet, "UIC-104", at=(195, 170), signal_to=uv104, fail_action="FO")
instrument(sheet, "FT-103", at=(158, 140), sensing="Line_SG130_S2", sensing_at=(158, Y),
           signal_to=uic, signal_points=[(158, 170)])
instrument(sheet, "PT-114", at=(172, 152), sensing="Line_SG130_S2", sensing_at=(172, Y),
           signal_to=uic, signal_points=[(172, 160), (195, 160)])
instrument(sheet, "PT-105", at=(222, 140), sensing="Line_SG102_S1", sensing_at=(222, Y),
           signal_to=uic, signal_points=[(222, 170)])
instrument(sheet, "TI-106", at=(232, 102), sensing="Line_SG102_S1", sensing_at=(232, Y))
instrument(sheet, "TI-107", at=(330, 140), sensing="Line_SG103_S1", sensing_at=(330, Y))
fail_label(sheet, "Inst_LZ109", (62, FEED), "down")
fail_label(sheet, "Inst_UIC104", (195, ASR), "up")
tag_label(sheet, "XV110", (62, 158))
tag_label(sheet, "UV104", (195, 206))
tag_label(sheet, "XV116", (391, 128))
tag_label(sheet, "CV103", (363, 113))

notes(sheet,
      "PIC-102 sets the speed controller SIC-113 (drive package, speed measured at K-101, output to "
      "its variable-speed drive). UIC-104: anti-surge on UV-104 from FT-103, PT-114, PT-105 (D-017)",
      "LZ-109: V-103 level high-high closes XV-110, stops K-101 (C&E I-101). US-116 closes XV-116 on "
      "every K-101 stop: I-101, I-201, I-202, I-302 and YS-117 not running (package trip, power; I-102)",
      "PSV-115: suction side (settle-out through UV-104, leak-back past XV-116, fire); PSV-111: K-101 "
      "discharge; PSV-112: E-101 CW side (tube rupture). To the HP flare header (D-022)")

save(sheet, target)
