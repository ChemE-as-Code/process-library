"""Draft of P-106: CO2 regenerator C-302 (aMDEA) with the lean/rich solvent exchanger E-301,
the overhead condenser E-303, the reflux drum V-302 and the reflux pumps P-302A/B.

Provenance only: P-106 is hand-maintained (no `generator:` in plant.yaml); this script wrote
its first revision. Run: cheme run scripts/draft_P-106.py <frame> [<out>]. Equipment, lines,
DN and instruments: DESIGN.md D-028; streams S26, S28 of process/flowsheet.yaml (the solvent
loop and the overhead are lumped in step C301, D-009: their lines have ASSUMED DN).
"""

import sys
from functools import partial
from pathlib import Path

from chemeascode.domains.piping import authoring
from chemeascode.domains.piping.authoring import (
    Marker,
    Nozzle,
    Sheet,
    instrument,
    note,
    offpage,
    tee,
    valve,
)

# DN 250 and above are ISO 6708 sizes (DIN 2448 in DEXPI stops at DN 200)
equipment = partial(authoring.equipment, standard="Iso6708")
line = partial(authoring.line, standard="Iso6708")

frame = Path(sys.argv[1])
target = Path(sys.argv[2]) if len(sys.argv) > 2 else frame
sheet = Sheet.load(frame)

EDGE = 400
PUMP = "CENTRIFUGAL_PUMP_SHAPE"

# Regenerator: trayed stripping column, kettle reboiler E-202 on P-104
c302 = equipment(sheet, "ProcessColumn", "C-302", shape="COLUMN_SHAPE", at=(180, 140),
                 scale=(1.2, 3.2),
                 nozzles=[Nozzle("N1", (0, -80), 1200), Nozzle("N2", (12, -68), 100),
                          Nozzle("N3", (-12, -50), 600), Nozzle("N4", (0, 80), 600),
                          Nozzle("N5", (12, 55), 800), Nozzle("N6", (12, 70), 50),
                          Nozzle("N7", (-12, -74), 150)],
                 markers=[Marker("COLUMN_TRAYS_SHAPE", 0, 2.0)],
                 label_at=(204, 160))
e301 = equipment(sheet, "PlateHeatExchanger", "E-301", shape="HEAT_EXCHANGER_PLATE_SHAPE",
                 at=(90, 150), scale=1.5,
                 nozzles=[Nozzle("C1", (-10, -6), 600), Nozzle("C2", (10, -6), 600),
                          Nozzle("H1", (10, 6), 600), Nozzle("H2", (-10, 6), 600)],
                 label_at=(62, 150))
e303 = equipment(sheet, "TubularHeatExchanger", "E-303", shape="HEAT_EXCHANGER_FIXED_TUBES_SHAPE",
                 at=(255, 45),
                 nozzles=[Nozzle("T1", (-17.5, 0), 1200), Nozzle("T2", (17.5, 0), 1200),
                          Nozzle("S1", (-7, -7), 400), Nozzle("S2", (7, -7), 400)],
                 label_at=(255, 57))
v302 = equipment(sheet, "Vessel", "V-302", shape="VESSEL_WITH_DISHED_HEADS_SHAPE", at=(350, 95),
                 scale=(1.0, 1.2),
                 nozzles=[Nozzle("N1", (-10, -8), 1200), Nozzle("N2", (0, -18), 900),
                          Nozzle("N3", (0, 18), 100), Nozzle("N4", (10, -5), 25),
                          Nozzle("N5", (-10, 8), 50)],
                 label_at=(372, 120))
p302a = equipment(sheet, "CentrifugalPump", "P-302A", shape=PUMP, at=(230, 150),
                  nozzles=[Nozzle("N1", (-7.5, 0), 100), Nozzle("N2", (0, -7.5), 100)],
                  label_at=(230, 162))
p302b = equipment(sheet, "CentrifugalPump", "P-302B", shape=PUMP, at=(270, 150),
                  nozzles=[Nozzle("N1", (-7.5, 0), 100), Nozzle("N2", (0, -7.5), 100)],
                  label_at=(285, 160))

# Rich solvent from C-301 (P-105) -> E-301 (cold side) -> C-302
line(sheet, "AM-1057", dn=600, fluid="aMDEA solution (rich)", route=[
    offpage("in", at=(12, 100), note="from C-301, P-105"), (80, 100), e301["C1"]],
    label_at=(40, 91.5))
line(sheet, "AM-1065", dn=600, fluid="aMDEA solution (rich)", route=[
    e301["C2"], (100, 90), c302["N3"]], label_at=(140, 81.5))
# Lean solvent from the E-202 kettle (P-104) -> E-301 (hot side) -> P-301A/B (P-105)
line(sheet, "AM-1051", dn=600, fluid="aMDEA solution (lean)", route=[
    offpage("in", at=(EDGE, 252), note="from E-202, P-104", rotation=180), (100, 252),
    e301["H1"]], label_at=(250, 243.5))
line(sheet, "AM-1058", dn=600, fluid="aMDEA solution (lean)", route=[
    e301["H2"], (80, 200), offpage("out", at=(12, 200), note="to P-301A/B, P-105",
                                   rotation=180)], label_at=(40, 191.5))
# Regenerator bottoms to and reboiler vapour from E-202 (P-104)
line(sheet, "AM-1049", dn=600, fluid="aMDEA solution", route=[
    c302["N4"], (180, 238), offpage("out", at=(EDGE, 238), note="to E-202, P-104")],
    label_at=(300, 229.5))
line(sheet, "AM-1050", dn=800, fluid="aMDEA vapour", route=[
    offpage("in", at=(EDGE, 195), note="from E-202, P-104", rotation=180), c302["N5"]],
    label_at=(300, 186.5))

# Overhead: C-302 -> E-303 -> V-302; CO2 to the vent stack on regenerator pressure control
line(sheet, "CO2-1066", dn=1200, fluid="CO2 and water vapour", route=[
    c302["N1"], (180, 45), e303["T1"]], label_at=(205, 36.5))
line(sheet, "CO2-1067", dn=1200, fluid="CO2 and water (two-phase)", route=[
    e303["T2"], (320, 45), (320, 87), v302["N1"]], label_at=(296, 49.5))
pv1505 = valve("PV1505", "ButterflyValve", tag="PV-1505", at=(350, 40))
line(sheet, "CO2-1068", dn=900, fluid="CO2", route=[
    v302["N2"], pv1505, (350, 15), offpage("out", at=(EDGE, 15), note="to atmosphere (vent stack)")],
    label_at=(375, 24))
line(sheet, "CWS-1074", dn=400, fluid="Cooling water", route=[
    offpage("in", at=(200, 22), note="from CW supply", note_at=(190, 16)), (248, 22), e303["S1"]],
    label_at=(225, 13.5))
line(sheet, "CWR-1075", dn=400, fluid="Cooling water", route=[
    e303["S2"], (262, 30), offpage("out", at=(300, 30), note="to CW return", note_at=(306, 24))],
    label_at=(282, 21.5))

# Reflux: V-302 -> P-302A/B -> C-302 (level control of V-302 on the reflux)
suction = tee("T1069", at=(250, 170), branch="up", branch_dn=100)
line(sheet, "PC-1069", dn=100, fluid="Reflux water", route=[
    v302["N3"], (350, 170), suction, (215, 170), (215, 150), p302a["N1"]], label_at=(320, 174.5))
line(sheet, "PC-1070", dn=100, fluid="Reflux water", route=[
    suction.branch, (250, 150), p302b["N1"]], label_at=(250, 140))
join = tee("T1071", at=(230, 125), branch="right", branch_dn=100)
lv1506 = valve("LV1506", "GlobeValve", tag="LV-1506", at=(230, 100))
line(sheet, "PC-1071", dn=100, fluid="Reflux water", route=[
    p302a["N2"], valve("CV1071", "SwingCheckValve", at=(230, 135)), join, lv1506, (230, 72),
    c302["N2"]], label_at=(211, 76.5))
line(sheet, "PC-1072", dn=100, fluid="Reflux water", route=[
    p302b["N2"], valve("CV1072", "SwingCheckValve", at=(270, 135)), (270, 125), join.branch],
    label_at=(285, 128))

# Make-up water (demineralised) to the reflux drum
fv1508 = valve("FV1508", "GlobeValve", tag="FV-1508", at=(380, 90))
line(sheet, "DW-1073", dn=25, fluid="Demineralised water", route=[
    offpage("in", at=(EDGE, 90), note="from DMW", rotation=180, note_at=(396, 84)), fv1508,
    v302["N4"]], label_at=(380, 74))

# Regenerator relief (gas blow-by from C-301 among the cases, S8): globe valve placeholder
# made a SpringLoadedGlobeSafetyValve with SAFETY_VALVE_SPRING_LOADED_SHAPE (tag in
# PositionNumber) by hand, as in D-027
sheet.use_shape("SAFETY_VALVE_SPRING_LOADED_SHAPE")
line(sheet, "CO2-1076", dn=150, fluid="CO2", route=[
    c302["N7"], (150, 66), valve("PSV1513", "GlobeValve", tag="PSV-1513", at=(150, 48)),
    offpage("out", at=(150, 25), note="to atmosphere", rotation=270, note_at=(150, 17))],
    label_at=(132, 40))

# Instruments
instrument(sheet, "PIC-1505", at=(378, 52), sensing="Line_CO21068_S1", sensing_at=(350, 62),
           signal_to=pv1505)
instrument(sheet, "LIC-1506", at=(295, 103), sensing=v302["N5"], signal_to=lv1506)
instrument(sheet, "LI-1507", at=(215, 212), sensing=c302["N6"])
instrument(sheet, "FIC-1508", at=(382, 110), sensing="Line_DW1073_S1", sensing_at=(392, 90),
           signal_to=fv1508)
instrument(sheet, "TI-1509", at=(205, 58), sensing="Line_CO21066_S1", sensing_at=(205, 45))
instrument(sheet, "TI-1510", at=(130, 105), sensing="Line_AM1065_S1", sensing_at=(130, 90))
instrument(sheet, "TI-1511", at=(300, 75), sensing="Line_CO21067_S1", sensing_at=(320, 75))

note(sheet, "Make-up water (S26) balances the solvent water inventory; LI-1507 the solvent inventory",
     at=(20, 262))
note(sheet, "Overhead, reflux and solvent rates not calculated (D-009): DN ASSUMED (D-028)",
     at=(20, 269))
note(sheet, "PSV-1513: set pressure and relief case open (S8)", at=(20, 276))

sheet.save(target)
for message in sheet.notes:
    if "DEXPI's NominalDiameterStandard" not in message:
        print(f"note: {message}", file=sys.stderr)
print(f"wrote {target}")
