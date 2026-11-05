"""Draft of P-05: absorption column C-101 (sieve trays with cooling and chilled-water coils) with
the process water, weak acid and NOx gas feeds, and the bleacher C-102 with the secondary air,
the bleacher gas return and the product acid.

Provenance only: P-05 is hand-maintained (no `generator:` in plant.yaml); this script wrote
its first revision. Run: cheme run scripts/draft_P-05.py build/frames/P-05.xml pid/P-05.xml.
Equipment, lines, DN and instruments: DESIGN.md D-017 to D-020; streams S09, S18, S19, S23-S25,
S30, S31 and the energy streams Q09-Q11 of process/flowsheet.yaml.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from chemeascode.domains.piping.authoring import (  # noqa: E402
    Marker,
    Nozzle,
    Sheet,
    instrument,
    note,
    offpage,
    valve,
)
from pid_common import (  # noqa: E402
    COLUMN,
    EDGE,
    LEFT,
    TOP,
    equipment,
    line,
    save,
    valve_marks,
)

frame = Path(sys.argv[1])
target = Path(sys.argv[2]) if len(sys.argv) > 2 else frame
sheet = Sheet.load(frame)

TRAYS = [Marker("COLUMN_TRAY_SHAPE", dy) for dy in (-50, -30, -10, 10, 30, 50)]
AIR = 246       # secondary air
RAW = 220       # raw acid to the bleacher
PRODUCT = 232   # product acid

# ---- equipment
c101 = equipment(sheet, "ProcessColumn", "C-101", shape=COLUMN, at=(170, 135), scale=(1.4, 3.0),
                 markers=TRAYS,
                 nozzles=[Nozzle("N1", (-14, 65), 700), Nozzle("N2", (0, -75), 600),
                          Nozzle("N3", (0, 75), 150), Nozzle("N4", (-14, -65), 65),
                          Nozzle("N5", (-14, -7), 80), Nozzle("N6", (-14, -47), 300),
                          Nozzle("N7", (-14, -29), 300), Nozzle("N8", (14, 15), 50),
                          Nozzle("N9", (-14, 15), 450), Nozzle("N10", (14, 45), 50),
                          Nozzle("N11", (14, 58), 50), Nozzle("N12", (14, -65), 50),
                          Nozzle("N13", (-14, 33), 450)],
                 label_at=(198, 120))
c102 = equipment(sheet, "ProcessColumn", "C-102", shape=COLUMN, at=(270, 180), scale=(1.2, 1.6),
                 markers=[Marker("COLUMN_TRAY_SHAPE", dy) for dy in (-20, 0, 20)],
                 nozzles=[Nozzle("N1", (-12, 30), 400), Nozzle("N2", (0, -40), 350),
                          Nozzle("N3", (0, 40), 150), Nozzle("N4", (-12, -28), 150),
                          Nozzle("N5", (12, 20), 50)],
                 label_at=(296, 160))

# ---- feeds to C-101 from the left: process water, chilled-water coils, weak acid, CW coils,
# NOx gas
fv505 = valve("FV505", "GlobeValve", tag="FV-505", at=(140, 48))
line(sheet, "PW-505", dn=65, fluid="Process water", route=[
    offpage("in", at=(140, TOP), note="process water (demin., B/L)", rotation=90,
            note_at=(162, 12)),
    fv505, (140, 70), c101["N4"]], label_at=(152, 30))
line(sheet, "CHR-112", dn=300, fluid="Chilled water", route=[
    offpage("in", at=(80, TOP), note="chilled water from E-101, P-01", rotation=90,
            note_at=(101, 12)),
    (80, 88), c101["N6"]], label_at=(118, 81))
line(sheet, "CHS-111", dn=300, fluid="Chilled water", route=[
    c101["N7"], (65, 106),
    offpage("out", at=(65, TOP), note="chilled water to E-101, P-01", rotation=270,
            note_at=(42, 12))], label_at=(118, 99))
line(sheet, "WA-306", dn=80, fluid="Weak acid", route=[
    offpage("in", at=(LEFT, 128), note="weak acid from P-101A/B, P-03"), c101["N5"]],
    label_at=(110, 121))
line(sheet, "CWS-506", dn=450, fluid="Cooling water", route=[
    offpage("in", at=(LEFT, 150), note="CW supply (B/L)"), c101["N9"]], label_at=(110, 143))
line(sheet, "CWR-507", dn=450, fluid="Cooling water", route=[
    c101["N13"], offpage("out", at=(LEFT, 168), note="CW return (B/L)", rotation=180)],
    label_at=(110, 161))
line(sheet, "NX-403", dn=700, fluid="Nitrous gas", route=[
    offpage("in", at=(LEFT, 200), note="nitrous gas from E-107, P-04"), c101["N1"]],
    label_at=(110, 193))

# ---- tail gas from the C-101 top to E-106 (P-04)
line(sheet, "TG-501", dn=600, fluid="Tail gas", route=[
    c101["N2"], (170, 35), offpage("out", at=(EDGE, 35), note="tail gas to E-106, P-04")],
    label_at=(370, 27))

# ---- raw acid: C-101 sump -> XV-507 -> LV-506 -> C-102 top
xv507 = valve("XV507", "BallValve", tag="XV-507", at=(200, RAW))
lv506 = valve("LV506", "GlobeValve", tag="LV-506", at=(225, RAW))
line(sheet, "AC-502", dn=150, fluid="Nitric acid", route=[
    c101["N3"], (170, RAW), xv507, lv506, (240, RAW), (240, 152), c102["N4"]],
    label_at=(230, 140))

# ---- secondary air into the C-102 bottom, bleacher gas to K-102 (P-04), product acid
fv509 = valve("FV509", "ButterflyValve", tag="FV-509", at=(220, AIR))
line(sheet, "PA-106", dn=400, fluid="Air", route=[
    offpage("in", at=(LEFT, AIR), note="secondary air from K-101, P-01"), fv509, (248, AIR),
    (248, 210), c102["N1"]], label_at=(110, 238))
line(sheet, "BG-503", dn=350, fluid="Bleacher gas", route=[
    c102["N2"], (270, 60), offpage("out", at=(EDGE, 60), note="bleacher gas to K-102, P-04")],
    label_at=(370, 52))
lv510 = valve("LV510", "GlobeValve", tag="LV-510", at=(320, PRODUCT))
line(sheet, "AC-504", dn=150, fluid="Nitric acid", route=[
    c102["N3"], (270, PRODUCT), lv510,
    offpage("out", at=(EDGE, PRODUCT), note="product acid to storage (B/L)")],
    label_at=(300, 240))

# ---- instruments
instrument(sheet, "FIC-505", at=(115, 48), sensing="Line_PW505_S1", sensing_at=(140, 30),
           sensing_points=[(115, 30)], signal_to=fv505, fail_action="FO")
instrument(sheet, "LIC-506", at=(225, 180), sensing=c101["N10"], signal_to=lv506,
           fail_action="FC")
instrument(sheet, "LZ-507", at=(200, 200), sensing=c101["N11"], sensing_points=[(200, 193)],
           signal_to=xv507, fail_action="FC")
instrument(sheet, "PI-503", at=(205, 80), sensing=c101["N12"])
instrument(sheet, "TI-508", at=(205, 150), sensing=c101["N8"])
instrument(sheet, "AI-511", at=(215, 50), sensing="Line_TG501_S1", sensing_at=(215, 35))
instrument(sheet, "AI-512", at=(240, 50), sensing="Line_TG501_S1", sensing_at=(240, 35))
instrument(sheet, "TI-513", at=(300, 48), sensing="Line_TG501_S1", sensing_at=(300, 35))
instrument(sheet, "FIC-509", at=(205, 233), sensing="Line_PA106_S1", sensing_at=(205, AIR),
           signal_to=fv509, fail_action="FO")
instrument(sheet, "LIC-510", at=(320, 210), sensing=c102["N5"], signal_to=lv510,
           fail_action="FC")
instrument(sheet, "AI-514", at=(343, 216), sensing="Line_AC504_S1", sensing_at=(343, PRODUCT))
instrument(sheet, "FI-515", at=(364, 216), sensing="Line_AC504_S1", sensing_at=(364, PRODUCT))

valve_marks(sheet, "Inst_FIC505", "FV505", (140, 48), "left")
valve_marks(sheet, "Inst_LIC506", "LV506", (225, RAW), "up")
valve_marks(sheet, "Inst_LZ507", "XV507", (200, RAW), "up")
valve_marks(sheet, "Inst_FIC509", "FV509", (220, AIR), "up")
valve_marks(sheet, "Inst_LIC510", "LV510", (320, PRODUCT), "up")

note(sheet, "FIC-505 (process water) sets the acid strength (AI-514); FIC-509 (secondary air) "
     "holds the tail-gas O2 (AI-512); set points by the operator (D-019)", at=(20, 262))
note(sheet, "LZ-507 closes XV-507 against gas blow-by from C-101 into C-102: C&E I-501. C-101 "
     "protected by PSV-404 (P-04); C-102 by PSV-111 (P-01) via the K-102 suction", at=(20, 269))
note(sheet, "C-101 coils: CW on the lower trays, chilled water (loop to E-101, circulation in the "
     "chilled-water package) on the upper trays; C-102 acid cooling: open (D-020)", at=(20, 276))

save(sheet, target)
