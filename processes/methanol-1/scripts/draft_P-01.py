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
                          Nozzle("N5", (14, 8), 50)],
                 label_at=(100, 170))
k101 = equipment(sheet, "CentrifugalCompressor", "K-101", shape=COMPRESSOR, at=(195, Y),
                 scale=2.0,
                 nozzles=[Nozzle("N1", (-15, 0), 600), Nozzle("N2", (15, 0), 400)],
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
    labels=False)

# ---- drum gas to the compressor suction; the anti-surge return joins at T131
asr_in = tee("T131", at=(150, Y), branch="down", branch_dn=300)
line(sheet, "SG-130", dn=600, fluid="Synthesis gas", route=[
    v103["N2"], (100, Y), asr_in, k101["N1"]], label_at=(165, 109))

# ---- discharge: relief take-off, aftercooler, anti-surge take-off, check valve, to P-02
psv_out = tee("T111", at=(248, Y), branch="up", branch_dn=150)
line(sheet, "SG-102", dn=400, fluid="Synthesis gas", route=[
    k101["N2"], psv_out, e101["T1"]], label_at=(264, 126))
asr_out = tee("T131B", at=(345, Y), branch="down", branch_dn=300)
line(sheet, "SG-103", dn=350, fluid="Synthesis gas", route=[
    e101["T2"], asr_out, valve("CV103", "SwingCheckValve", at=(365, Y)),
    offpage("out", at=(EDGE, Y), note="to K-102 suction, P-02", note_at=(386, 113))],
    label_at=(385, 128))
uv104 = valve("UV104", "GlobeValve", tag="UV-104", at=(195, ASR))
line(sheet, "SG-131", dn=300, fluid="Synthesis gas", route=[
    asr_out.branch, (345, ASR), uv104, (150, ASR), asr_in.branch], label_at=(290, 208))

# ---- relief to the flare header: K-101 discharge and the E-101 cooling water side
flare_join = tee("T134", at=(248, 40), branch="right", branch_dn=80)
psv111 = valve("PSV111", "GlobeValve", tag="PSV-111", at=(248, 85))
line(sheet, "FL-132", dn=150, fluid="Relief gas", route=[
    psv_out.branch, psv111, flare_join,
    offpage("out", at=(248, TOP), note="to flare header", rotation=270, note_at=(232, 20))],
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
instrument(sheet, "PIC-102", at=(120, 102), sensing="Line_SG130_S1", sensing_at=(120, Y))
uic = instrument(sheet, "UIC-104", at=(195, 170), signal_to=uv104, fail_action="FO")
instrument(sheet, "FT-103", at=(165, 140), sensing="Line_SG130_S2", sensing_at=(165, Y),
           signal_to=uic, signal_points=[(165, 170)])
instrument(sheet, "PT-105", at=(222, 140), sensing="Line_SG102_S1", sensing_at=(222, Y),
           signal_to=uic, signal_points=[(222, 170)])
instrument(sheet, "TI-106", at=(232, 102), sensing="Line_SG102_S1", sensing_at=(232, Y))
instrument(sheet, "TI-107", at=(330, 140), sensing="Line_SG103_S1", sensing_at=(330, Y))
fail_label(sheet, "Inst_LZ109", (62, FEED), "down")
fail_label(sheet, "Inst_UIC104", (195, ASR), "up")

notes(sheet,
      "PIC-102: K-101 suction pressure (the front end's back pressure) sets the speed of the "
      "variable-speed drive. UIC-104: anti-surge on UV-104 from FT-103, PT-105 and PIC-102 (D-017)",
      "LZ-109: V-103 level high-high closes XV-110 and stops K-101 (C&E I-101). K-101 lube oil, "
      "seals, vibration and machine trips are in the compressor package (D-017)",
      "PSV-111: K-101 discharge (blocked outlet, settle-out); PSV-112: E-101 cooling water side "
      "(tube rupture). Set pressures and loads with the relief study (piping/special-items.yaml)")

save(sheet, target)
