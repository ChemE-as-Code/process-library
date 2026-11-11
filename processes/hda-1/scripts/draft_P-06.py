"""Draft of P-06: toluene column C-203 (vacuum) with its condenser E-205, reflux drum V-203,
vacuum package PK-201, reflux and toluene recycle pumps P-203A/B, the thermosyphon reboiler
E-206 on HP steam and the biphenyl bottoms pumps P-204A/B to the battery limit.

Provenance only: P-06 is hand-maintained (no `generator:` in plant.yaml); this script wrote
its first revision. Run: cheme run scripts/draft_P-06.py <frame> [<out>]. Equipment, lines,
DN and instruments: DESIGN.md D-025; streams S22-S24 and duties Q9, Q10 of
process/flowsheet.yaml (the column, condenser, drum and reboiler are lumped in step C203).
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
from pid_common import DRUM, HX, LEFT, PUMP, TOP, equipment, line, make_safety_valve, save  # noqa: E402

frame = Path(sys.argv[1])
target = Path(sys.argv[2]) if len(sys.argv) > 2 else frame
sheet = Sheet.load(frame)

# ---- equipment
c203 = equipment(sheet, "ProcessColumn", "C-203", shape="COLUMN_SHAPE", at=(130, 135),
                 scale=(1.0, 2.4),
                 nozzles=[Nozzle("N1", (-10, -27), 50), Nozzle("N2", (0, -60), 400),
                          Nozzle("N3", (10, -48), 50), Nozzle("N4", (0, 60), 25),
                          Nozzle("N5", (-10, 45), 100), Nozzle("N6", (-10, 10), 700),
                          Nozzle("N7", (-10, -50), 150), Nozzle("N8", (-10, 55), 50),
                          Nozzle("N9", (-10, 0), 25), Nozzle("N10", (6, 58), 25)],
                 markers=[Marker("COLUMN_TRAYS_SHAPE", 0, 2.0)],
                 label_at=(130, 160))
e205 = equipment(sheet, "TubularHeatExchanger", "E-205", shape=HX, at=(180, 60),
                 nozzles=[Nozzle("T1", (-17.5, 0), 400), Nozzle("T2", (17.5, 0), 80),
                          Nozzle("S1", (-7, -7), 150), Nozzle("S2", (7, -7), 150)],
                 label_at=(180, 74))
v203 = equipment(sheet, "Vessel", "V-203", shape=DRUM, at=(240, 100), scale=(1.4, 1.0),
                 nozzles=[Nozzle("N1", (-14, -8), 80), Nozzle("N2", (0, -15), 50),
                          Nozzle("N3", (0, 15), 80), Nozzle("N4", (-14, 6), 50),
                          Nozzle("N5", (14, 6), 25), Nozzle("N6", (14, -5), 50), Nozzle("N7", (-8, 15), 50)],
                 label_at=(240, 100))
pk201 = equipment(sheet, "Compressor", "PK-201", shape="PUMP_VACUUM_SHAPE", at=(285, 40),
                  nozzles=[Nozzle("N1", (-7.5, 0), 50), Nozzle("N2", (7.5, 0), 50)],
                  label_at=(285, 54))
e206 = equipment(sheet, "TubularHeatExchanger", "E-206", shape=HX, at=(65, 150),
                 nozzles=[Nozzle("S1", (-7, -7), 50), Nozzle("S2", (-7, 7), 25),
                          Nozzle("T1", (7, 7), 100), Nozzle("T2", (7, -7), 700)],
                 label_at=(40, 160))
p203a = equipment(sheet, "CentrifugalPump", "P-203A", shape=PUMP, at=(277, 190),
                  nozzles=[Nozzle("N1", (-7.5, 0), 80), Nozzle("N2", (0, -7.5), 50)],
                  label_at=(277, 202))
p203b = equipment(sheet, "CentrifugalPump", "P-203B", shape=PUMP, at=(325, 190),
                  nozzles=[Nozzle("N1", (-7.5, 0), 80), Nozzle("N2", (0, -7.5), 50)],
                  label_at=(338, 202))
p204a = equipment(sheet, "CentrifugalPump", "P-204A", shape=PUMP, at=(75, 232),
                  nozzles=[Nozzle("N1", (-7.5, 0), 25), Nozzle("N2", (0, -7.5), 25)],
                  label_at=(56, 221))
p204b = equipment(sheet, "CentrifugalPump", "P-204B", shape=PUMP, at=(120, 232),
                  nozzles=[Nozzle("N1", (-7.5, 0), 25), Nozzle("N2", (0, -7.5), 25)],
                  label_at=(145, 240))

# ---- feed from LV-508 (P-05)
line(sheet, "TO-122", dn=50, fluid="Toluene / biphenyl", route=[
    offpage("in", at=(LEFT, 108), note="from LV-508, P-05", note_at=(26, 102)), c203["N1"]],
    label_at=(88, 102))

# ---- column relief to the flare
psv615 = valve("PSV615", "GlobeValve", tag="PSV-615", at=(100, 55))
line(sheet, "FL-645", dn=150, fluid="Relief gas", route=[
    c203["N7"], (100, 85), psv615,
    offpage("out", at=(100, TOP), note="to flare header, P-07", rotation=270, note_at=(80, 12))],
    label_at=(88, 40))

# ---- overhead, condenser, reflux drum, vacuum package
line(sheet, "PG-630", dn=400, fluid="Toluene vapour", route=[
    c203["N2"], (130, 60), e205["T1"]], label_at=(145, 52))
line(sheet, "TO-631", dn=80, fluid="Toluene", route=[
    e205["T2"], (215, 60), (215, 92), v203["N1"]], label_at=(205, 80))
cw_relief = tee("T644", at=(173, 40), branch="left", branch_dn=25)
line(sheet, "CWS-642", dn=150, fluid="Cooling water", route=[
    offpage("in", at=(173, TOP), note="from CW supply, P-08", rotation=90, note_at=(152, 9)),
    cw_relief, e205["S1"]], label_at=(165, 48))
line(sheet, "CWR-643", dn=150, fluid="Cooling water", route=[
    e205["S2"],
    offpage("out", at=(187, TOP), note="to CW return, P-08", rotation=270, note_at=(205, 18))],
    label_at=(198, 32))
psv616 = valve("PSV616", "GlobeValve", tag="PSV-616", at=(155, 30))
line(sheet, "CWS-644", dn=25, fluid="Cooling water", route=[
    cw_relief.branch, (155, 40), psv616,
    offpage("out", at=(155, 20), note="to atmosphere (safe location)", rotation=270,
            note_at=(130, 23))],
    label_at=(143, 36))
pv604 = valve("PV604", "GlobeValve", tag="PV-604", at=(258, 40))
line(sheet, "PG-647", dn=50, fluid="Non-condensables", route=[
    v203["N2"], (240, 40), pv604, pk201["N1"]], label_at=(250, 70))
line(sheet, "FL-646", dn=50, fluid="Relief gas", route=[
    pk201["N2"], (300, 40),
    offpage("out", at=(300, TOP), note="to flare header, P-07", rotation=270, note_at=(282, 7))],
    label_at=(310, 28))

# ---- reflux and toluene recycle: V-203 -> P-203A/B -> reflux FV-607, recycle LV-606 to V-100
suction = tee("T633", at=(247, 190), branch="down", branch_dn=80)
line(sheet, "TO-632", dn=80, fluid="Toluene", route=[
    v203["N3"], (240, 190), suction, valve("HV632", "GateValve", at=(255, 190)),
    valve("SR632", "Strainer", at=(262, 190)), p203a["N1"]], label_at=(228, 150))
line(sheet, "TO-633", dn=80, fluid="Toluene", route=[
    suction.branch, (247, 212), (310, 212), valve("HV633", "GateValve", at=(310, 205)),
    valve("SR633", "Strainer", at=(310, 198)), (310, 190), p203b["N1"]], label_at=(280, 218))
join = tee("T635", at=(277, 164), branch="right", branch_dn=50)
minflow = tee("T636", at=(277, 156), branch="left", branch_dn=25)
fv607 = valve("FV607", "GlobeValve", tag="FV-607", at=(295, 140))
recycle = tee("T123", at=(320, 140), branch="up", branch_dn=40)
line(sheet, "TO-634", dn=50, fluid="Toluene", route=[
    p203a["N2"], valve("CV634", "SwingCheckValve", at=(277, 176)),
    valve("HV634", "GateValve", at=(277, 170)), join, minflow, (277, 140), fv607, recycle,
    (380, 140), (380, 235), (150, 235), (150, 87), c203["N3"]], label_at=(300, 227))
line(sheet, "TO-635", dn=50, fluid="Toluene", route=[
    p203b["N2"], valve("CV635", "SwingCheckValve", at=(325, 176)),
    valve("HV635", "GateValve", at=(325, 170)), (325, 164), join.branch], label_at=(338, 168))
line(sheet, "TO-636", dn=25, fluid="Toluene", route=[
    minflow.branch, valve("HV636", "GlobeValve", at=(268, 156)), (262, 156), (262, 106),
    v203["N5"]], label_at=(270, 128))
lv606 = valve("LV606", "GlobeValve", tag="LV-606", at=(320, 115))
line(sheet, "TO-123", dn=40, fluid="Toluene", route=[
    recycle.branch, lv606,
    offpage("out", at=(320, TOP), note="to V-100, P-01", rotation=270, note_at=(338, 9))],
    label_at=(330, 70))

# ---- reboiler E-206 (thermosyphon) on HP steam, condensate to the header
line(sheet, "TO-638", dn=100, fluid="Biphenyl / toluene", route=[
    c203["N5"], (72, 180), e206["T1"]], label_at=(96, 171))
line(sheet, "PG-639", dn=700, fluid="Biphenyl / toluene (two-phase)", route=[
    e206["T2"], (72, 136), (110, 136), (110, 145), c203["N6"]], label_at=(90, 142))
tv602 = valve("TV602", "GlobeValve", tag="TV-602", at=(35, 120))
line(sheet, "HS-640", dn=50, fluid="HP steam", route=[
    offpage("in", at=(LEFT, 120), note="from HP steam header, P-08", note_at=(28, 137)),
    tv602, (58, 120), e206["S1"]], label_at=(46, 126))
line(sheet, "CD-641", dn=25, fluid="Condensate", route=[
    e206["S2"], valve("ST641", "SteamTrap", at=(58, 168)), (58, 175),
    offpage("out", at=(LEFT, 175), note="to condensate header, P-08", rotation=180,
            note_at=(32, 169))],
    label_at=(45, 182))

# ---- biphenyl bottoms: P-204A/B on the sump level to the battery limit (traced)
branch = tee("T649", at=(95, 245), branch="up", branch_dn=25)
line(sheet, "DP-648", dn=25, fluid="Biphenyl", route=[
    c203["N4"], (130, 245), branch, (40, 245), (40, 232),
    valve("HV648", "GateValve", at=(50, 232)), valve("SR648", "Strainer", at=(58, 232)),
    p204a["N1"]], label_at=(30, 238))
line(sheet, "DP-649", dn=25, fluid="Biphenyl", route=[
    branch.branch, (95, 232), valve("HV649", "GateValve", at=(101, 232)),
    valve("SR649", "Strainer", at=(106, 232)), p204b["N1"]], label_at=(100, 252))
join_b = tee("T650", at=(75, 206), branch="right", branch_dn=25)
lv608 = valve("LV608", "GlobeValve", tag="LV-608", at=(50, 200))
line(sheet, "DP-124", dn=25, fluid="Biphenyl", route=[
    p204a["N2"], valve("CV124", "SwingCheckValve", at=(75, 218)),
    valve("HV124", "GateValve", at=(75, 212)), join_b, (75, 200), lv608,
    offpage("out", at=(LEFT, 200), note="to biphenyl storage (B/L)", rotation=180,
            note_at=(30, 194))],
    label_at=(62, 206))
line(sheet, "DP-650", dn=25, fluid="Biphenyl", route=[
    p204b["N2"], valve("CV650", "SwingCheckValve", at=(120, 218)),
    valve("HV650", "GateValve", at=(120, 212)), (120, 206), join_b.branch], label_at=(100, 213))

# ---- drains to the closed drain system
line(sheet, "DR-651", dn=25, fluid="Drain", route=[
    c203["N10"], valve("HV651", "GateValve", at=(136, 199)),
    offpage("out", at=(136, 206), note="to drain", rotation=90,
            note_at=(141, 213))], labels=False)
line(sheet, "DR-652", dn=50, fluid="Drain", route=[
    v203["N7"], valve("HV652", "GateValve", at=(232, 121)),
    offpage("out", at=(232, 128), note="to drain", rotation=90,
            note_at=(222, 131))], labels=False)

# ---- relief valves
make_safety_valve(sheet, "PSV615", label_at=(88, 60))
make_safety_valve(sheet, "PSV616", label_at=(143, 27))

# ---- instruments
instrument(sheet, "TIC-602", at=(88, 124), sensing=c203["N9"], signal_to=tv602,
           signal_points=[(88, 113), (35, 113)])
instrument(sheet, "PI-603", at=(148, 72), sensing="Line_PG630_S1", sensing_at=(148, 60))
instrument(sheet, "PIC-604", at=(258, 25), sensing="Line_PG647_S1", sensing_at=(248, 40),
           signal_to=pv604)
instrument(sheet, "LIC-606", at=(290, 95), sensing=v203["N6"], signal_to=lv606,
           signal_points=[(305, 95), (305, 115)])
instrument(sheet, "FIC-607", at=(295, 125), sensing="Line_TO634_S3", sensing_at=(288, 140),
           signal_to=fv607)
instrument(sheet, "LIC-608", at=(95, 190), sensing=c203["N8"], signal_to=lv608,
           signal_points=[(50, 190)])
instrument(sheet, "FI-609", at=(345, 115), sensing="Line_TO123_S1", sensing_at=(320, 100))
instrument(sheet, "LZ-612", at=(200, 115), sensing=v203["N4"])

note(sheet, "C-203 at 30 kPa(a): PIC-604 on the PK-201 suction PV-604 (vacuum package, not sized, D-008). "
     "TIC-602 on the HP steam TV-602 (Q9). FIC-607: reflux (R 0.5, D-008)", at=(20, 262))
note(sheet, "LIC-606: V-203 level on the toluene recycle LV-606 (TO-123). LZ-612 low-low stops "
     "P-203A/B (C&E I-601). Biphenyl lines DP traced (melting point 342 K)", at=(20, 269))
note(sheet, "PSV-615: C-203 (fire; E-206 tube rupture, HP steam into the 3.5 barg column; CW failure); "
     "PSV-616: E-205 CW side blocked in. P-204A/B type and minimum flow open (D-025)", at=(20, 276))

save(sheet, target)
