"""Draft of P-06: SCR ammonia vaporiser E-108 with the SCR ammonia dosing and its low-temperature
trip, tertiary reactor R-102 (N2O decomposition and SCR), the absorber pressure control and
the train trip valve at the tail-gas expander X-101, and the tail gas to the stack.

Provenance only: P-06 is hand-maintained (no `generator:` in plant.yaml); this script wrote
its first revision. Run: cheme run scripts/draft_P-06.py build/frames/P-06.xml pid/P-06.xml.
Equipment, lines, DN and instruments: DESIGN.md D-017 to D-020; streams S04, S05, S27-S29 and
the energy stream Q12 of process/flowsheet.yaml.
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
    DRUM,
    EDGE,
    HX,
    LEFT,
    TOP,
    TRAIN,
    TURBINE,
    equipment,
    line,
    make_safety_valve,
    save,
    valve_marks,
)

frame = Path(sys.argv[1])
target = Path(sys.argv[2]) if len(sys.argv) > 2 else frame
sheet = Sheet.load(frame)

NH3 = 55        # SCR ammonia
TAIL = 110      # hot tail gas to R-102
EXP = 215       # treated tail gas through X-101

# ---- equipment
e108 = equipment(sheet, "TubularHeatExchanger", "E-108", shape=HX, at=(85, NH3), scale=1.2,
                 nozzles=[Nozzle("T1", (-21, 0), 25), Nozzle("T2", (21, 0), 25),
                          Nozzle("S1", (-8.4, -8.4), 25), Nozzle("S3", (8.4, 8.4), 25)],
                 label_at=(72, 72))
r102 = equipment(sheet, "Vessel", "R-102", shape=DRUM, at=(240, 155), scale=(1.4, 1.8),
                 nozzles=[Nozzle("N1", (0, -27), 900), Nozzle("N2", (0, 27), 900),
                          Nozzle("N3", (14, 18), 50)],
                 label_at=(212, 155))
x101 = equipment(sheet, "Turbine", "X-101", shape=TURBINE, at=(305, EXP), scale=2.0,
                 nozzles=[Nozzle("N1", (-9, 0), 900), Nozzle("N2", (9, 0), 2000)],
                 label_at=(305, 237))

# ---- hot tail gas from E-103 (P-03) with the NH3 dosing point, to the R-102 top
dosing = tee("T601", at=(215, TAIL), branch="up", branch_dn=25)
line(sheet, "TG-310", dn=900, fluid="Tail gas", route=[
    offpage("in", at=(LEFT, TAIL), note="tail gas from E-103, P-03"),
    dosing, (240, TAIL), r102["N1"]], label_at=(170, 118))

# ---- SCR ammonia: liquid NH3 (P-01) -> E-108 -> XV-602 -> FV-603 -> into the tail gas
xv602 = valve("XV602", "BallValve", tag="XV-602", at=(145, NH3))
fv603 = valve("FV603", "GlobeValve", tag="FV-603", at=(188, NH3))
line(sheet, "NL-103", dn=25, fluid="Ammonia", route=[
    offpage("in", at=(LEFT, NH3), note="liquid NH3 from storage via P-01"), e108["T1"]],
    label_at=(38, 62))
# E-108 relief (D-021): blocked outlet with LP steam on, fire; upstream of XV-602, to the
# ammonia relief header
vaporiser_relief = tee("T602", at=(125, NH3), branch="up", branch_dn=25)
line(sheet, "NV-601", dn=25, fluid="Ammonia", route=[
    e108["T2"], vaporiser_relief, xv602, fv603, (215, NH3), dosing.branch], label_at=(228, 82))
psv616 = valve("PSV616", "GlobeValve", tag="PSV-616", at=(125, 40))
line(sheet, "RL-617", dn=25, fluid="Ammonia", route=[
    vaporiser_relief.branch, psv616,
    offpage("out", at=(125, TOP), note="to NH3 relief header (B/L)", rotation=270,
            note_at=(150, 12))], label_at=(137, 26))
make_safety_valve(sheet, "PSV616", label_at=(137, 40))

# ---- LP steam to E-108 with the vapour temperature control, condensate return
tv604 = valve("TV604", "GlobeValve", tag="TV-604", at=(76.6, 32))
line(sheet, "LS-604", dn=25, fluid="LP steam", route=[
    offpage("in", at=(76.6, TOP), note="LP steam (B/L)", rotation=90, note_at=(58, 12)),
    tv604, e108["S1"]], label_at=(66, 21))
line(sheet, "CD-605", dn=25, fluid="Condensate", route=[
    e108["S3"], (93.4, 85), valve("ST605", "SteamTrap", at=(55, 85)),
    offpage("out", at=(LEFT, 85), note="condensate return (B/L)", rotation=180)],
    label_at=(75, 93))

# ---- R-102 -> trip valve XV-610 -> absorber pressure valve PV-611 -> X-101 -> stack
xv610 = valve("XV610", "BallValve", tag="XV-610", at=(255, EXP))
pv611 = valve("PV611", "ButterflyValve", tag="PV-611", at=(278, EXP))
line(sheet, "TG-606", dn=900, fluid="Tail gas", route=[
    r102["N2"], (240, EXP), xv610, pv611, x101["N1"]], label_at=(228, 200))
line(sheet, "TG-607", dn=2000, fluid="Tail gas", route=[
    x101["N2"], offpage("out", at=(EDGE, EXP), note="treated tail gas to stack (B/L)")],
    label_at=(338, 205))

# ---- instruments
instrument(sheet, "TIC-604", at=(110, 32), sensing="Line_NV601_S1", sensing_at=(110, NH3),
           signal_to=tv604, fail_action="FC")
instrument(sheet, "FIC-603", at=(172, 78), sensing="Line_NV601_S2", sensing_at=(172, NH3),
           signal_to=fv603, fail_action="FC")
instrument(sheet, "TZ-605", at=(145, 85), sensing="Line_TG310_S1", sensing_at=(145, TAIL),
           signal_to=xv602, fail_action="FC")
instrument(sheet, "TI-608", at=(275, 173), sensing=r102["N3"])
instrument(sheet, "US-612", at=(255, 195), signal_to=xv610, fail_action="FC")
instrument(sheet, "PIC-611", at=(266, 238), sensing="Line_TG606_S1", sensing_at=(266, EXP),
           signal_to=pv611, fail_action="FO")
instrument(sheet, "TI-613", at=(335, 235), sensing="Line_TG607_S1", sensing_at=(335, EXP))
instrument(sheet, "AI-614", at=(360, 235), sensing="Line_TG607_S1", sensing_at=(360, EXP))
instrument(sheet, "AI-615", at=(385, 235), sensing="Line_TG607_S1", sensing_at=(385, EXP))

valve_marks(sheet, "Inst_TIC604", "TV604", (76.6, 32), "right")
valve_marks(sheet, "Inst_FIC603", "FV603", (188, NH3), "down")
valve_marks(sheet, "Inst_TZ605", "XV602", (145, NH3), "down")
valve_marks(sheet, "Inst_US612", "XV610", (255, EXP), "up")
valve_marks(sheet, "Inst_PIC611", "PV611", (278, EXP), "down")

note(sheet, "TZ-605 stops the SCR ammonia below the R-102 inlet temperature limit (ammonium "
     "nitrate deposits, NH3 slip): C&E I-601. FIC-603 set from AI-614 by the operator (D-019)",
     at=(20, 262))
note(sheet, "PIC-611 holds the absorber pressure at the X-101 inlet; US-612 (train trip, C&E I-602) "
     "closes XV-610; start-up runs through X-101 (SEQ-START-BURNER S1, S2), no bypass yet (D-022)",
     at=(20, 269))
note(sheet, "AI-614 (NOx), AI-615 (N2O): stack emission monitoring. R-102 protected by PSV-404 "
     "(P-04); E-108 by PSV-616 (D-021). " + TRAIN.split(";")[0], at=(20, 276))

save(sheet, target)
