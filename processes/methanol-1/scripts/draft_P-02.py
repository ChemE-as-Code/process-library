"""Draft of P-02: recycle circulator K-102 with its spillback, feed/effluent exchanger E-102 with
the cold bypass, boiling-water converter R-101 and its steam drum V-104.

Provenance only: P-02 is hand-maintained (no `generator:` in plant.yaml); this script wrote
its first revision. Run: cheme run scripts/draft_P-02.py <frame> [<out>]. Equipment, lines,
DN and instruments: DESIGN.md D-016, D-018; streams S3-S8 and duty Q4 of
process/flowsheet.yaml.
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
Y = 150          # circulator and feed/effluent exchanger centre line
ASR = 205        # spillback run
BYP = 120        # E-102 cold bypass run
STEAM = 22       # MP steam to the header

# ---- equipment
k102 = equipment(sheet, "CentrifugalCompressor", "K-102", shape=COMPRESSOR, at=(110, Y),
                 scale=2.0,
                 nozzles=[Nozzle("N1", (-15, 0), 700), Nozzle("N2", (15, 0), 700)],
                 label_at=(110, 173))
e102 = equipment(sheet, "TubularHeatExchanger", "E-102", shape=HX, at=(230, Y), scale=1.4,
                 nozzles=[Nozzle("T1", (-24.5, 0), 700), Nozzle("T2", (24.5, 0), 900),
                          Nozzle("S1", (12, 9.8), 900), Nozzle("S2", (-12, 9.8), 900)],
                 label_at=(230, 170))
r101 = equipment(sheet, "TubularHeatExchanger", "R-101", shape=HX, at=(300, 135), scale=1.6,
                 rotation=90,
                 nozzles=[Nozzle("T1", (0, -28), 900), Nozzle("T2", (0, 28), 900),
                          Nozzle("S1", (11.2, -20), 800), Nozzle("S2", (11.2, 20), 600)],
                 label_at=(279, 135))
v104 = equipment(sheet, "Vessel", "V-104", shape=DRUM, at=(335, 55), scale=(1.0, 1.8),
                 rotation=90,
                 nozzles=[Nozzle("N1", (-19, -10), 500), Nozzle("N2", (-9, -10), 150),
                          Nozzle("N3", (15, -10), 200), Nozzle("N4", (27, -3), 50),
                          Nozzle("N5", (-27, -5), 800), Nozzle("N6", (13, 10), 600),
                          Nozzle("N7", (23, 10), 50), Nozzle("N9", (27, 5), 50)],
                 label_at=(335, 55))

# ---- recycle gas from V-101 (P-03) and make-up gas from E-101 (P-01) to the circulator
mix = tee("T104A", at=(40, Y), branch="up", branch_dn=350)
asr_in = tee("T104B", at=(65, Y), branch="down", branch_dn=600)
line(sheet, "SG-110", dn=700, fluid="Synthesis gas", route=[
    offpage("in", at=(LEFT, Y), note="from V-101, P-03"),
    mix, asr_in, k102["N1"]], label_at=(52, 140))
line(sheet, "SG-103", dn=350, fluid="Synthesis gas", route=[
    offpage("in", at=(LEFT, 110), note="from E-101, P-01"), (40, 110), mix.branch],
    label_at=(27, 124))

# ---- circulator discharge: spillback take-off, check valve, bypass take-off, E-102 cold side
asr_out = tee("T231", at=(145, Y), branch="down", branch_dn=600)
byp_out = tee("T230A", at=(190, Y), branch="up", branch_dn=350)
line(sheet, "SG-105", dn=700, fluid="Synthesis gas", route=[
    k102["N2"], asr_out, valve("CV105", "SwingCheckValve", at=(165, Y)), byp_out, e102["T1"]],
    label_at=(172, 140))
uv203 = valve("UV203", "GlobeValve", tag="UV-203", at=(110, ASR))
line(sheet, "SG-231", dn=600, fluid="Synthesis gas", route=[
    asr_out.branch, (145, ASR), uv203, (65, ASR), asr_in.branch], label_at=(130, 214))

# ---- converter feed: E-102 cold outlet, bypass return, R-101 tubes from the top
byp_in = tee("T230B", at=(268, BYP), branch="left", branch_dn=350)
line(sheet, "SG-106", dn=900, fluid="Synthesis gas", route=[
    e102["T2"], (268, Y), byp_in, (268, 90), (300, 90), r101["T1"]], label_at=(256, 100))
tv205 = valve("TV205", "GlobeValve", tag="TV-205", at=(232, BYP))
line(sheet, "SG-230", dn=350, fluid="Synthesis gas", route=[
    byp_out.branch, (190, BYP), tv205, byp_in.branch], label_at=(211, 128))

# ---- converter effluent to the E-102 shell, then to the loop cooler E-103 (P-03)
line(sheet, "PG-107", dn=900, fluid="Converter effluent", route=[
    r101["T2"], (300, 180), (242, 180), e102["S1"]], label_at=(318, 176))
line(sheet, "PG-108", dn=900, fluid="Converter effluent", route=[
    e102["S2"], (218, 228), offpage("out", at=(EDGE, 228), note="to E-103, P-03")],
    label_at=(330, 236))

# ---- steam system: riser and downcomer between R-101 shell and V-104, BFW, MP steam, blowdown
# The riser enters the drum head above the normal liquid level (drum centre line); only the
# downcomer leaves from the drum bottom. BFW, MP steam and the relief valve are on the drum top.
line(sheet, "SW-232", dn=800, fluid="Steam-water mixture", route=[
    r101["S1"], (318, 115), (318, 74), (298, 74), (298, 50), v104["N5"]],
    label_at=(333, 92))
line(sheet, "BW-233", dn=600, fluid="Boiler water", route=[
    v104["N6"], (348, 155), r101["S2"]], label_at=(362, 118))
pv207 = valve("PV207", "GlobeValve", tag="PV-207", at=(316, 24))
line(sheet, "MS-234", dn=500, fluid="MP steam", route=[
    v104["N1"], pv207,
    offpage("out", at=(316, TOP), note="MP steam header", rotation=270, note_at=(290, 17))],
    label_at=(305, 39))
lv209 = valve("LV209", "GlobeValve", tag="LV-209", at=(350, 24))
line(sheet, "BF-235", dn=200, fluid="Boiler feed water", route=[
    offpage("in", at=(350, TOP), note="BFW header", rotation=90, note_at=(370, 12)),
    lv209, v104["N3"]], label_at=(361, 32))
psv208 = valve("PSV208", "GlobeValve", tag="PSV-208", at=(326, 28))
line(sheet, "MS-236", dn=150, fluid="MP steam", route=[
    v104["N2"], psv208,
    offpage("out", at=(326, TOP), note="to atm", rotation=270, note_at=(338, 19))],
    label_at=(338, 37))
line(sheet, "BD-237", dn=50, fluid="Blowdown", route=[
    v104["N7"], (358, 78), valve("HV237", "GlobeValve", at=(382, 78)),
    offpage("out", at=(EDGE, 78), note="to blowdown (B/L)", note_at=(392, 72))],
    label_at=(372, 85))
make_safety_valve(sheet, "PSV208", label_at=(338, 28))

# ---- instruments
uic = instrument(sheet, "UIC-203", at=(110, 190), signal_to=uv203, fail_action="FO")
instrument(sheet, "FT-201", at=(82, 172), sensing="Line_SG110_S3", sensing_at=(82, Y),
           signal_to=uic, signal_points=[(82, 190)])
instrument(sheet, "PT-202", at=(135, 172), sensing="Line_SG105_S1", sensing_at=(135, Y),
           signal_to=uic, signal_points=[(135, 190)])
instrument(sheet, "TIC-205", at=(288, 72), sensing="Line_SG106_S2", sensing_at=(288, 90),
           signal_to=tv205, signal_points=[(232, 72)], fail_action="FO")
instrument(sheet, "TI-206", at=(285, 198), sensing="Line_PG107_S1", sensing_at=(285, 180))
instrument(sheet, "TZ-210", at=(262, 198), sensing="Line_PG107_S1", sensing_at=(262, 180))
instrument(sheet, "PIC-207", at=(298, 31), sensing="Line_MS234_S1", sensing_at=(316, 31),
           signal_to=pv207, signal_points=[(298, 24)], fail_action="FO")
instrument(sheet, "LIC-209", at=(378, 38), sensing=v104["N4"], sensing_points=[(378, 52)],
           signal_to=lv209, signal_points=[(378, 24)], fail_action="FO")
instrument(sheet, "LZ-211", at=(386, 60), sensing=v104["N9"])
fail_label(sheet, "Inst_UIC203", (110, ASR), "up")
fail_label(sheet, "Inst_TIC205", (232, BYP), "up")
fail_label(sheet, "Inst_PIC207", (316, 24), "left")
fail_label(sheet, "Inst_LIC209", (350, 24), "right")
tag_label(sheet, "UV203", (110, 211))

notes(sheet,
      "TIC-205: converter inlet temperature on the E-102 cold bypass TV-205. PIC-207: steam drum "
      "pressure, which sets the boiling temperature and so the converter temperature (D-018)",
      "UIC-203: K-102 spillback UV-203 from FT-201 and PT-202 (uncooled, about 10 K rise, D-018). "
      "LIC-209: drum level on the BFW LV-209. TZ-210: C&E I-201; LZ-211: C&E I-202",
      "No isolation valve in the loop from K-102 to V-101: PSV-302 on V-101 (P-03) protects K-102 "
      "discharge, E-102, R-101 tubes and E-103 (D-019). PSV-208: V-104 and R-101 shell")

save(sheet, target)
