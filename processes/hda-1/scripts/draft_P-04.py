"""Draft of P-04: stabiliser C-201 with its partial condenser E-201, reflux drum V-201, reflux
pumps P-201A/B and the thermosyphon reboiler E-202 on MP steam.

Provenance only: P-04 is hand-maintained (no `generator:` in plant.yaml); this script wrote
its first revision. Run: cheme run scripts/draft_P-04.py <frame> [<out>]. Equipment, lines,
DN and instruments: DESIGN.md D-025; streams S18-S20 and duties Q5, Q6 of
process/flowsheet.yaml (the column, condenser and reboiler are lumped in step C201: the
overhead, reflux and reboiler circulation lines have ASSUMED DN).
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
    tee,
    valve,
)
from pid_common import DRUM, EDGE, HX, LEFT, PUMP, TOP, equipment, line, make_safety_valve, save  # noqa: E402

frame = Path(sys.argv[1])
target = Path(sys.argv[2]) if len(sys.argv) > 2 else frame
sheet = Sheet.load(frame)
BOTTOM = 248

# ---- equipment
c201 = equipment(sheet, "ProcessColumn", "C-201", shape="COLUMN_SHAPE", at=(130, 135),
                 scale=(1.0, 2.4),
                 nozzles=[Nozzle("N1", (-10, -27), 100), Nozzle("N2", (0, -60), 50),
                          Nozzle("N3", (10, -48), 25), Nozzle("N4", (0, 60), 80),
                          Nozzle("N5", (-10, 45), 150), Nozzle("N6", (-10, 25), 200),
                          Nozzle("N7", (-10, -50), 100), Nozzle("N8", (-10, 55), 50),
                          Nozzle("N9", (-10, 0), 25), Nozzle("N10", (6, 58), 50)],
                 markers=[Marker("COLUMN_TRAYS_SHAPE", 0, 2.0)],
                 label_at=(130, 150))
e201 = equipment(sheet, "TubularHeatExchanger", "E-201", shape=HX, at=(180, 60),
                 nozzles=[Nozzle("T1", (-17.5, 0), 50), Nozzle("T2", (17.5, 0), 50),
                          Nozzle("S1", (-7, -7), 65), Nozzle("S2", (7, -7), 65)],
                 label_at=(180, 74))
v201 = equipment(sheet, "Vessel", "V-201", shape=DRUM, at=(240, 100), scale=(1.4, 1.0),
                 nozzles=[Nozzle("N1", (-14, -8), 50), Nozzle("N2", (0, -15), 40),
                          Nozzle("N3", (0, 15), 25), Nozzle("N4", (-14, 6), 50),
                          Nozzle("N5", (14, 6), 25), Nozzle("N6", (14, -5), 50), Nozzle("N7", (-8, 15), 25)],
                 label_at=(240, 100))
e202 = equipment(sheet, "TubularHeatExchanger", "E-202", shape=HX, at=(65, 170),
                 nozzles=[Nozzle("S1", (-7, -7), 100), Nozzle("S2", (-7, 7), 50),
                          Nozzle("T1", (7, 7), 150), Nozzle("T2", (7, -7), 200)],
                 label_at=(48, 185))
p201a = equipment(sheet, "CentrifugalPump", "P-201A", shape=PUMP, at=(277, 190),
                  nozzles=[Nozzle("N1", (-7.5, 0), 25), Nozzle("N2", (0, -7.5), 25)],
                  label_at=(277, 202))
p201b = equipment(sheet, "CentrifugalPump", "P-201B", shape=PUMP, at=(325, 190),
                  nozzles=[Nozzle("N1", (-7.5, 0), 25), Nozzle("N2", (0, -7.5), 25)],
                  label_at=(338, 202))

# ---- feed from LV-202 (P-02)
line(sheet, "AR-116", dn=100, fluid="Crude aromatics", route=[
    offpage("in", at=(LEFT, 108), note="from LV-202, P-02", note_at=(26, 102)), c201["N1"]],
    label_at=(88, 102))

# ---- column relief to the flare
psv413 = valve("PSV413", "GlobeValve", tag="PSV-413", at=(100, 55))
line(sheet, "FL-443", dn=100, fluid="Relief gas", route=[
    c201["N7"], (100, 85), psv413,
    offpage("out", at=(100, TOP), note="to flare header, P-07", rotation=270, note_at=(80, 12))],
    label_at=(88, 40))

# ---- overhead, partial condenser, reflux drum, off-gas
line(sheet, "PG-430", dn=50, fluid="Stabiliser overhead", route=[
    c201["N2"], (130, 60), e201["T1"]], label_at=(145, 52))
line(sheet, "PG-431", dn=50, fluid="Stabiliser overhead", route=[
    e201["T2"], (215, 60), (215, 92), v201["N1"]], label_at=(226, 70))
pv404 = valve("PV404", "GlobeValve", tag="PV-404", at=(300, 40))
line(sheet, "FG-119", dn=40, fluid="Fuel gas", route=[
    v201["N2"], (240, 40), pv404,
    offpage("out", at=(EDGE, 40), note="to fuel gas header (B/L)", note_at=(380, 34))],
    label_at=(350, 46))
cw_relief = tee("T442", at=(173, 40), branch="left", branch_dn=25)
line(sheet, "CWS-440", dn=65, fluid="Cooling water", route=[
    offpage("in", at=(173, TOP), note="from CW supply, P-08", rotation=90, note_at=(152, 9)),
    cw_relief, e201["S1"]], label_at=(165, 48))
line(sheet, "CWR-441", dn=65, fluid="Cooling water", route=[
    e201["S2"],
    offpage("out", at=(187, TOP), note="to CW return, P-08", rotation=270, note_at=(212, 18))],
    label_at=(198, 32))
psv414 = valve("PSV414", "GlobeValve", tag="PSV-414", at=(155, 30))
line(sheet, "CWS-442", dn=25, fluid="Cooling water", route=[
    cw_relief.branch, (155, 40), psv414,
    offpage("out", at=(155, 20), note="to atmosphere (safe location)", rotation=270,
            note_at=(130, 23))],
    label_at=(143, 36))

# ---- reflux: V-201 -> P-201A/B -> C-201 (all the condensed liquid, on V-201 level)
suction = tee("T433", at=(247, 190), branch="down", branch_dn=25)
line(sheet, "AR-432", dn=25, fluid="Reflux", route=[
    v201["N3"], (240, 190), suction, valve("HV432", "GateValve", at=(255, 190)),
    valve("SR432", "Strainer", at=(262, 190)), p201a["N1"]], label_at=(228, 150))
line(sheet, "AR-433", dn=25, fluid="Reflux", route=[
    suction.branch, (247, 212), (310, 212), valve("HV433", "GateValve", at=(310, 205)),
    valve("SR433", "Strainer", at=(310, 198)), (310, 190), p201b["N1"]], label_at=(280, 218))
join = tee("T435", at=(277, 164), branch="right", branch_dn=25)
minflow = tee("T436", at=(277, 156), branch="left", branch_dn=25)
lv405 = valve("LV405", "GlobeValve", tag="LV-405", at=(330, 140))
line(sheet, "AR-434", dn=25, fluid="Reflux", route=[
    p201a["N2"], valve("CV434", "SwingCheckValve", at=(277, 176)),
    valve("HV434", "GateValve", at=(277, 170)), join, minflow, (277, 140), lv405, (380, 140),
    (380, 235), (150, 235), (150, 87), c201["N3"]], label_at=(300, 227))
line(sheet, "AR-435", dn=25, fluid="Reflux", route=[
    p201b["N2"], valve("CV435", "SwingCheckValve", at=(325, 176)),
    valve("HV435", "GateValve", at=(325, 170)), (325, 164), join.branch], label_at=(338, 168))
line(sheet, "AR-436", dn=25, fluid="Reflux", route=[
    minflow.branch, valve("HV436", "GlobeValve", at=(268, 156)), (262, 156), (262, 106),
    v201["N5"]], label_at=(270, 128))

# ---- reboiler E-202 (thermosyphon) on MP steam, condensate to the header
line(sheet, "AR-437", dn=150, fluid="Stabiliser bottoms", route=[
    c201["N5"], (72, 180), e202["T1"]], label_at=(96, 186))
line(sheet, "PG-438", dn=200, fluid="Stabiliser bottoms (two-phase)", route=[
    e202["T2"], (72, 160), c201["N6"]], label_at=(96, 154))
tv402 = valve("TV402", "GlobeValve", tag="TV-402", at=(35, 140))
line(sheet, "MS-439", dn=100, fluid="MP steam", route=[
    offpage("in", at=(LEFT, 140), note="from MP steam header, P-08", note_at=(30, 148)),
    tv402, (58, 140), e202["S1"]], label_at=(45, 132))
line(sheet, "CD-444", dn=50, fluid="Condensate", route=[
    e202["S2"], valve("ST444", "SteamTrap", at=(58, 200)), (58, 225),
    offpage("out", at=(LEFT, 225), note="to condensate header, P-08", rotation=180,
            note_at=(32, 219))],
    label_at=(45, 210))

# ---- bottoms to C-202 (P-05) on the sump level
lv408 = valve("LV408", "GlobeValve", tag="LV-408", at=(130, 222))
line(sheet, "AR-120", dn=80, fluid="Stabilised aromatics", route=[
    c201["N4"], lv408, (130, 245),
    offpage("out", at=(EDGE, 245), note="to C-202, P-05", note_at=(386, 239))],
    label_at=(200, 239))

# ---- drains to the closed drain system
line(sheet, "DR-445", dn=50, fluid="Drain", route=[
    c201["N10"], valve("HV445", "GateValve", at=(136, 199)),
    offpage("out", at=(136, 206), note="to drain", rotation=90,
            note_at=(141, 213))], labels=False)
line(sheet, "DR-446", dn=25, fluid="Drain", route=[
    v201["N7"], valve("HV446", "GateValve", at=(232, 121)),
    offpage("out", at=(232, 128), note="to drain", rotation=90,
            note_at=(222, 131))], labels=False)

# ---- relief valves
make_safety_valve(sheet, "PSV413", label_at=(88, 60))
make_safety_valve(sheet, "PSV414", label_at=(143, 27))

# ---- instruments
instrument(sheet, "FI-401", at=(60, 90), sensing="Line_AR116_S1", sensing_at=(60, 108))
instrument(sheet, "TIC-402", at=(95, 122), sensing=c201["N9"], signal_to=tv402,
           signal_points=[(35, 122)])
instrument(sheet, "PIC-404", at=(270, 60), sensing="Line_FG119_S1", sensing_at=(270, 40),
           signal_to=pv404, signal_points=[(300, 60)])
instrument(sheet, "LIC-405", at=(290, 95), sensing=v201["N6"], signal_to=lv405,
           signal_points=[(330, 95)])
instrument(sheet, "TI-407", at=(198, 96), sensing="Line_PG431_S1", sensing_at=(215, 86))
instrument(sheet, "LIC-408", at=(95, 210), sensing=c201["N8"], signal_to=lv408,
           signal_points=[(95, 222)])
instrument(sheet, "PI-409", at=(148, 72), sensing="Line_PG430_S1", sensing_at=(148, 60))
instrument(sheet, "LZ-411", at=(200, 115), sensing=v201["N4"])

note(sheet, "TIC-402: stabiliser tray temperature on the MP steam TV-402 (Q5). PIC-404: column pressure "
     "on the off-gas PV-404. LIC-405: all condensed liquid refluxed (D-008)", at=(20, 262))
note(sheet, "LZ-411: V-201 level low-low stops P-201A/B (C&E I-401). HV-436: continuous minimum flow of "
     "P-201A/B. Overhead, reflux and reboiler DN ASSUMED (D-025)", at=(20, 269))
note(sheet, "PSV-413: C-201 and V-201 (fire, CW failure, gas blow-by from V-101 if XV-204 and LV-202 "
     "fail open); PSV-414: E-201 CW side (tube rupture, blocked in)", at=(20, 276))

save(sheet, target)
