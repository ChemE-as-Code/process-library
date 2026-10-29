"""Draft of P-105: CO2 absorber C-301 (aMDEA), the lean solvent pumps P-301A/B and the lean
solvent cooler E-302.

Provenance only: P-105 is hand-maintained (no `generator:` in plant.yaml); this script wrote
its first revision. Run: cheme run scripts/draft_P-105.py <frame> [<out>]. Equipment, lines,
DN and instruments: DESIGN.md D-028; streams S24, S27 of process/flowsheet.yaml (the solvent
loop is lumped in step C301, D-009: its lines have ASSUMED DN).
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

# Absorber: two packed beds (bulk and fine absorption), gas up, lean solvent down
c301 = equipment(sheet, "ProcessColumn", "C-301", shape="COLUMN_SHAPE", at=(150, 130),
                 scale=(1.2, 3.2),
                 nozzles=[Nozzle("N1", (-12, 60), 400), Nozzle("N2", (0, -80), 350),
                          Nozzle("N3", (12, -62), 500), Nozzle("N4", (0, 80), 600),
                          Nozzle("N5", (-12, 66), 50), Nozzle("N6", (-12, 74), 50),
                          Nozzle("N7", (-12, -40), 25)],
                 markers=[Marker("COLUMN_PACKED_BED_SHAPE", -30, 1.6),
                          Marker("COLUMN_PACKED_BED_SHAPE", 25, 1.6)],
                 label_at=(126, 58))
p301a = equipment(sheet, "CentrifugalPump", "P-301A", shape=PUMP, at=(300, 195),
                  nozzles=[Nozzle("N1", (-7.5, 0), 600), Nozzle("N2", (0, -7.5), 500)],
                  label_at=(311, 208))
p301b = equipment(sheet, "CentrifugalPump", "P-301B", shape=PUMP, at=(300, 232),
                  nozzles=[Nozzle("N1", (-7.5, 0), 600), Nozzle("N2", (0, -7.5), 500)],
                  label_at=(285, 244))
e302 = equipment(sheet, "TubularHeatExchanger", "E-302", shape="HEAT_EXCHANGER_FIXED_TUBES_SHAPE",
                 at=(235, 150),
                 nozzles=[Nozzle("T1", (-17.5, 0), 500), Nozzle("T2", (17.5, 0), 500),
                          Nozzle("S1", (-7, -7), 400), Nozzle("S2", (7, -7), 400)],
                 label_at=(235, 162))

# Raw synthesis gas from V-201 (P-104) in, treated gas to E-401 (P-107)
line(sheet, "PG-1047", dn=400, fluid="Process gas", route=[
    offpage("in", at=(12, 190), note="from V-201, P-104"), c301["N1"]], label_at=(60, 181.5))
line(sheet, "PG-1056", dn=350, fluid="Process gas", route=[
    c301["N2"], (150, 25), offpage("out", at=(EDGE, 25), note="to E-401, P-107")],
    label_at=(300, 16.5))

# Rich solvent on level control to the regenerator; XV-1406 closes on low-low level
xv1406 = valve("XV1406", "BallValve", tag="XV-1406", at=(120, 250))
lv1405 = valve("LV1405", "GlobeValve", tag="LV-1405", at=(85, 250))
line(sheet, "AM-1057", dn=600, fluid="aMDEA solution (rich)", route=[
    c301["N4"], (150, 250), xv1406, lv1405,
    offpage("out", at=(12, 250), note="to E-301, P-106", rotation=180)], label_at=(50, 241.5))

# Lean solvent from E-301 (P-106) -> P-301A/B -> E-302 -> C-301
suction = tee("T1058", at=(280, 195), branch="down", branch_dn=600)
line(sheet, "AM-1058", dn=600, fluid="aMDEA solution (lean)", route=[
    offpage("in", at=(EDGE, 250), note="from E-301, P-106", rotation=180), (270, 250),
    (270, 195), suction, p301a["N1"]], label_at=(350, 241.5))
line(sheet, "AM-1061", dn=600, fluid="aMDEA solution (lean)", route=[
    suction.branch, (280, 232), p301b["N1"]], label_at=(291, 213))
join = tee("T1059", at=(300, 160), branch="right", branch_dn=500)
line(sheet, "AM-1059", dn=500, fluid="aMDEA solution (lean)", route=[
    p301a["N2"], valve("CV1059", "SwingCheckValve", at=(300, 176)), join, (300, 150),
    e302["T2"]], label_at=(275, 141.5))
line(sheet, "AM-1062", dn=500, fluid="aMDEA solution (lean)", route=[
    p301b["N2"], (300, 215), (320, 215), valve("CV1062", "SwingCheckValve", at=(320, 190)),
    (320, 160), join.branch], label_at=(334, 192))
fv1407 = valve("FV1407", "GlobeValve", tag="FV-1407", at=(200, 135))
line(sheet, "AM-1060", dn=500, fluid="aMDEA solution (lean)", route=[
    e302["T1"], (200, 150), fv1407, (200, 68), c301["N3"]], label_at=(185, 59.5))

# Cooling water to E-302 (lean solvent temperature on the return valve)
line(sheet, "CWS-1063", dn=400, fluid="Cooling water", route=[
    offpage("in", at=(EDGE, 125), note="from CW supply", rotation=180), (242, 125),
    e302["S2"]], label_at=(350, 129.5))
tv1408 = valve("TV1408", "GlobeValve", tag="TV-1408", at=(228, 128))
line(sheet, "CWR-1064", dn=400, fluid="Cooling water", route=[
    e302["S1"], tv1408, (228, 110), offpage("out", at=(EDGE, 110), note="to CW return")],
    label_at=(350, 101.5))

# Instruments
instrument(sheet, "FI-1401", at=(60, 205), sensing="Line_PG1047_S1", sensing_at=(60, 190))
instrument(sheet, "PDI-1402", at=(110, 90), sensing=c301["N7"])
instrument(sheet, "AI-1403", at=(200, 40), sensing="Line_PG1056_S1", sensing_at=(200, 25))
instrument(sheet, "PI-1404", at=(250, 40), sensing="Line_PG1056_S1", sensing_at=(250, 25))
instrument(sheet, "LIC-1405", at=(85, 222), sensing=c301["N5"], signal_to=lv1405)
instrument(sheet, "LZ-1406", at=(120, 230), sensing=c301["N6"], signal_to=xv1406)
instrument(sheet, "FIC-1407", at=(178, 110), sensing="Line_AM1060_S1", sensing_at=(200, 110),
           signal_to=fv1407)
instrument(sheet, "TIC-1408", at=(213, 135), sensing="Line_AM1060_S1", sensing_at=(200, 88),
           signal_to=tv1408)
instrument(sheet, "TI-1409", at=(330, 40), sensing="Line_PG1056_S1", sensing_at=(330, 25))

note(sheet, "LZ-1406: see C&E I-105 (gas blow-by to C-302)", at=(20, 262))
note(sheet, "Solvent rate not calculated (D-009): AM line DN ASSUMED (D-028)", at=(20, 269))
note(sheet, "P-301A/B: lean solvent pumps, one running, one spare; make-up water joins in V-302",
     at=(20, 276))

sheet.save(target)
for message in sheet.notes:
    if "DEXPI's NominalDiameterStandard" not in message:
        print(f"note: {message}", file=sys.stderr)
print(f"wrote {target}")
