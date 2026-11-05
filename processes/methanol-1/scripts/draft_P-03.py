"""Draft of P-03: loop cooler E-103, HP separator V-101 with the loop pressure / purge, the loop
depressuring and the crude let-down, LP flash drum V-102.

Provenance only: P-03 is hand-maintained (no `generator:` in plant.yaml); this script wrote
its first revision. Run: cheme run scripts/draft_P-03.py <frame> [<out>]. Equipment, lines,
DN and instruments: DESIGN.md D-016, D-019; streams S8-S15 of process/flowsheet.yaml.
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
GAS = 60         # separator gas / recycle run
PURGE = 105      # purge run
CRUDE = 175      # crude let-down run

# ---- equipment
e103 = equipment(sheet, "TubularHeatExchanger", "E-103", shape=HX, at=(80, 90), scale=1.2,
                 nozzles=[Nozzle("T1", (-21, 0), 900), Nozzle("T2", (21, 0), 800),
                          Nozzle("S1", (10, -8.4), 1100), Nozzle("S2", (-10, -8.4), 1100)],
                 label_at=(80, 104))
v101 = equipment(sheet, "Vessel", "V-101", shape=DRUM, at=(150, 120), scale=(1.4, 1.8),
                 nozzles=[Nozzle("N1", (-14, -12), 800), Nozzle("N2", (0, -27), 700),
                          Nozzle("N3", (0, 27), 250), Nozzle("N4", (-9, -25), 150),
                          Nozzle("N5", (14, 0), 50), Nozzle("N6", (14, 15), 50),
                          Nozzle("N7", (-14, 10), 50)],
                 label_at=(150, 120))
v102 = equipment(sheet, "Vessel", "V-102", shape=DRUM, at=(290, CRUDE), scale=(1.0, 1.8),
                 rotation=90,
                 nozzles=[Nozzle("N1", (-27, 0), 250), Nozzle("N2", (-18, -10), 80),
                          Nozzle("N3", (20, -10), 100), Nozzle("N4", (10, 10), 250),
                          Nozzle("N5", (27, 3), 50)],
                 label_at=(290, CRUDE))

# ---- converter effluent from E-102 (P-02) through the loop cooler to the HP separator
line(sheet, "PG-108", dn=900, fluid="Converter effluent", route=[
    offpage("in", at=(LEFT, 90), note="from E-102, P-02"), e103["T1"]], label_at=(32, 98))
line(sheet, "PG-109", dn=800, fluid="Converter effluent", route=[
    e103["T2"], (122, 90), (122, 108), v101["N1"]], label_at=(112, 100))
cw_relief = tee("T331", at=(70, 60), branch="left", branch_dn=80)
line(sheet, "CWR-331", dn=1100, fluid="Cooling water return", route=[
    e103["S2"], cw_relief,
    offpage("out", at=(70, TOP), note="CW return", rotation=270, note_at=(60, 20))],
    label_at=(81, 44))
line(sheet, "CWS-330", dn=1100, fluid="Cooling water", route=[
    offpage("in", at=(90, TOP), note="CW supply", rotation=90, note_at=(104, 20)),
    e103["S1"]], label_at=(101, 44))
psv312 = valve("PSV312", "GlobeValve", tag="PSV-312", at=(50, 45))
line(sheet, "FL-334", dn=80, fluid="Relief gas", route=[
    cw_relief.branch, (50, 60), psv312,
    offpage("out", at=(50, TOP), note="to HP flare header", rotation=270, note_at=(29, 20))],
    label_at=(37, 31))

# ---- separator gas: depressuring take-off, loop pressure, purge take-off, recycle to K-102
dep = tee("T332", at=(175, GAS), branch="up", branch_dn=150)
purge = tee("T111", at=(220, GAS), branch="down", branch_dn=100)
line(sheet, "SG-110", dn=700, fluid="Synthesis gas", route=[
    v101["N2"], (150, GAS), dep, purge,
    offpage("out", at=(EDGE, GAS), note="to K-102 suction, P-02")], label_at=(372, 68))
xv304 = valve("XV304", "BallValve", tag="XV-304", at=(175, 44))
flare_join = tee("T333", at=(175, 28), branch="left", branch_dn=150)
line(sheet, "FL-332", dn=150, fluid="Relief gas", route=[
    dep.branch, xv304, flare_join,
    offpage("out", at=(175, TOP), note="to HP flare header", rotation=270, note_at=(196, 20))],
    label_at=(188, 32))
psv302 = valve("PSV302", "GlobeValve", tag="PSV-302", at=(141, 76))
line(sheet, "FL-333", dn=150, fluid="Relief gas", route=[
    v101["N4"], psv302, (141, 28), flare_join.branch], label_at=(158, 33))
fv303 = valve("FV303", "GlobeValve", tag="FV-303", at=(300, PURGE))
line(sheet, "FG-111", dn=100, fluid="Purge gas", route=[
    purge.branch, (220, PURGE), fv303,
    offpage("out", at=(EDGE, PURGE), note="to reformer fuel (B/L)")], label_at=(372, 113))

# ---- separator liquid: low-low shutdown valve and level let-down to the LP flash drum
xv306 = valve("XV306", "BallValve", tag="XV-306", at=(182, CRUDE))
lv307 = valve("LV307", "GlobeValve", tag="LV-307", at=(205, CRUDE))
line(sheet, "CM-113", dn=250, fluid="Crude methanol", route=[
    v101["N3"], (150, CRUDE), xv306, lv307, v102["N1"]], label_at=(240, 168))

# ---- LP flash drum: flash gas to fuel on its pressure, relief, crude to C-201 on its level
pv309 = valve("PV309", "GlobeValve", tag="PV-309", at=(330, 140))
line(sheet, "FG-114", dn=80, fluid="Fuel gas", route=[
    v102["N2"], (272, 140), pv309,
    offpage("out", at=(EDGE, 140), note="to fuel gas header (B/L)")], label_at=(259, 149))
psv311 = valve("PSV311", "GlobeValve", tag="PSV-311", at=(330, 154))
line(sheet, "FL-335", dn=100, fluid="Relief gas", route=[
    v102["N3"], (310, 154), psv311,
    offpage("out", at=(EDGE, 154), note="to HP flare header")], label_at=(366, 161))
lv310 = valve("LV310", "GlobeValve", tag="LV-310", at=(338, 215))
line(sheet, "CM-115", dn=250, fluid="Crude methanol", route=[
    v102["N4"], (300, 215), lv310,
    offpage("out", at=(EDGE, 215), note="to C-201, P-04")], label_at=(372, 223))
make_safety_valve(sheet, "PSV302", label_at=(128, 76))
make_safety_valve(sheet, "PSV311", label_at=(330, 160))
make_safety_valve(sheet, "PSV312", label_at=(37, 45))

# ---- instruments
instrument(sheet, "TI-301", at=(112, 72), sensing="Line_PG109_S1", sensing_at=(112, 90))
instrument(sheet, "HS-304", at=(155, 44), signal_to=xv304, fail_action="FO")
instrument(sheet, "AI-305", at=(330, 42), sensing="Line_SG110_S3", sensing_at=(330, GAS))
fic = instrument(sheet, "FIC-303", at=(262, 88), sensing="Line_FG111_S1",
                 sensing_at=(262, PURGE), signal_to=fv303, signal_points=[(300, 88)],
                 fail_action="FC")
instrument(sheet, "PIC-308", at=(240, 76), sensing="Line_SG110_S3", sensing_at=(240, GAS),
           signal_to=fic, signal_points=[(240, 88)])
instrument(sheet, "LZ-306", at=(182, 135), sensing=v101["N6"], signal_to=xv306,
           fail_action="FC")
instrument(sheet, "LIC-307", at=(205, 120), sensing=v101["N5"], signal_to=lv307,
           fail_action="FC")
instrument(sheet, "PIC-309", at=(290, 124), sensing="Line_FG114_S1", sensing_at=(290, 140),
           signal_to=pv309, signal_points=[(330, 124)], fail_action="FO")
instrument(sheet, "LIC-310", at=(338, 178), sensing=v102["N5"], signal_to=lv310,
           fail_action="FC")
fail_label(sheet, "Inst_HS304", (175, 44), "left-below")
fail_label(sheet, "Inst_FIC303", (300, PURGE), "up")
fail_label(sheet, "Inst_LZ306", (182, CRUDE), "up-left")
fail_label(sheet, "Inst_LIC307", (205, CRUDE), "up")
fail_label(sheet, "Inst_PIC309", (330, 140), "up")
fail_label(sheet, "Inst_LIC310", (338, 215), "up")
instrument(sheet, "LZ-313", at=(115, 130), sensing=v101["N7"])
tag_label(sheet, "XV306", (182, 181))
tag_label(sheet, "XV304", (187, 44))

notes(sheet,
      "PIC-308: loop pressure at V-101, sets the purge FIC-303 (D-019). AI-305: H2, CO, CO2, CH4 "
      "of the loop gas (inerts, stoichiometric number). HS-304 opens XV-304: loop depressuring",
      "LZ-306: V-101 level low-low closes XV-306 against gas blow-by into V-102 (C&E I-301). LZ-313: "
      "V-101 level high-high stops K-102 and K-101 (C&E I-302). LIC-307, LIC-310: level let-down",
      "PSV-302: V-101 and the HP loop (fire, blocked recycle); PSV-311: V-102 (gas blow-by from "
      "V-101, fire); PSV-312: E-103 CW side (tube rupture); all to the HP flare header (D-019)")

save(sheet, target)
