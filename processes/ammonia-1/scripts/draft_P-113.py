"""Draft of P-113: steam system U-801 (deaerator, condensate stripper, steam drum, superheater
and LP let-down, lumped as in the flowsheet, D-015) with the boiler feed water pump P-801, the
boiler water circuits of the waste heat boilers and steam coils (E-107, E-105, E-201, E-502),
the MP steam header (process steam, export, relief), LP steam to X-601, condensate returns,
make-up water and blowdown.

Provenance only: P-113 is hand-maintained (no `generator:` in plant.yaml); this script wrote
its first revision. Run: cheme run scripts/draft_P-113.py <frame> [<out>]. Equipment, lines,
DN and instruments: DESIGN.md D-029; streams S6, S25, S33, S35, S68-S70, S87 and the duties
Q8, Q10, Q13, Q23, Q29, Q31 of process/flowsheet.yaml.
"""

import sys
from functools import partial
from pathlib import Path

from chemeascode.domains.piping import authoring
from chemeascode.domains.piping.authoring import (
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
LEFT = [110, 128, 146, 164, 182]
RIGHT = [110, 128, 146, 164, 182]

u801 = equipment(sheet, "Vessel", "U-801", shape="VESSEL_WITH_DISHED_HEADS_SHAPE", at=(200, 150),
                 scale=(4.0, 4.0),
                 nozzles=[
                     # boiler water circuits (top)
                     Nozzle("B1", (-35, -60), 200), Nozzle("B2", (-25, -60), 200),
                     Nozzle("B3", (-15, -60), 450), Nozzle("B4", (-5, -60), 300),
                     Nozzle("B5", (5, -60), 200), Nozzle("B6", (15, -60), 125),
                     Nozzle("B7", (25, -60), 400), Nozzle("B8", (35, -60), 250),
                     # make-up water and condensates (left)
                     Nozzle("C1", (-40, LEFT[0] - 150), 200), Nozzle("C2", (-40, LEFT[1] - 150), 125),
                     Nozzle("C3", (-40, LEFT[2] - 150), 25), Nozzle("C4", (-40, LEFT[3] - 150), 25),
                     Nozzle("C5", (-40, LEFT[4] - 150), 25),
                     # steam, blowdown and vent (right)
                     Nozzle("S1", (40, RIGHT[0] - 150), 350), Nozzle("S2", (40, RIGHT[2] - 150), 65),
                     Nozzle("S3", (40, RIGHT[3] - 150), 32), Nozzle("S4", (40, RIGHT[4] - 150), 65),
                     # BFW pump suction and return, levels
                     Nozzle("P1", (-20, 60), 250), Nozzle("P2", (20, 60), 200),
                     Nozzle("L1", (30, 60), 25), Nozzle("L2", (-40, -50), 25)],
                 label_at=(200, 217))
p801 = equipment(sheet, "CentrifugalPump", "P-801", shape="CENTRIFUGAL_PUMP_SHAPE", at=(290, 235),
                 nozzles=[Nozzle("N1", (-7.5, 0), 250), Nozzle("N2", (0, -7.5), 200)],
                 label_at=(305, 245))

# Boiler water circuits: nested so that no two lines cross
line(sheet, "BW-1024", dn=200, fluid="Boiler feed water", route=[
    u801["B1"], (165, 78), offpage("out", at=(12, 78), note="to E-107, P-102", rotation=180)],
    label_at=(100, 71.5))
line(sheet, "BW-1025", dn=200, fluid="Boiler feed water", route=[
    offpage("in", at=(12, 62), note="from E-107, P-102"), (175, 62), u801["B2"]],
    label_at=(100, 55.5))
line(sheet, "BW-1037", dn=450, fluid="Boiler water", route=[
    u801["B3"], (185, 46), offpage("out", at=(12, 46), note="to E-105, P-103", rotation=180)],
    label_at=(100, 39.5))
line(sheet, "SM-1038", dn=300, fluid="Steam-water mixture", route=[
    offpage("in", at=(12, 30), note="from E-105, P-103"), (195, 30), u801["B4"]],
    label_at=(100, 23.5))
line(sheet, "BW-1039", dn=200, fluid="Boiler water", route=[
    u801["B5"], (205, 30), offpage("out", at=(EDGE, 30), note="to E-201, P-103")],
    label_at=(300, 23.5))
line(sheet, "SM-1040", dn=125, fluid="Steam-water mixture", route=[
    offpage("in", at=(EDGE, 46), note="from E-201, P-103", rotation=180), (215, 46), u801["B6"]],
    label_at=(300, 39.5))
line(sheet, "BW-1100", dn=400, fluid="Boiler water", route=[
    u801["B7"], (225, 62), offpage("out", at=(EDGE, 62), note="to E-502, P-109")],
    label_at=(300, 55.5))
line(sheet, "SM-1101", dn=250, fluid="Steam-water mixture", route=[
    offpage("in", at=(EDGE, 78), note="from E-502, P-109", rotation=180), (235, 78), u801["B8"]],
    label_at=(300, 71.5))

# Make-up water and condensate returns to the deaerator / condensate stripper
lv2202 = valve("LV2202", "GlobeValve", tag="LV-2202", at=(140, LEFT[0]))
line(sheet, "DW-1137", dn=200, fluid="Demineralised water", route=[
    offpage("in", at=(12, LEFT[0]), note="from DMW (battery limit)"), lv2202, u801["C1"]],
    label_at=(100, LEFT[0] - 8.5))
line(sheet, "PC-1048", dn=125, fluid="Process condensate", route=[
    offpage("in", at=(12, LEFT[1]), note="from V-201, P-104"), u801["C2"]],
    label_at=(100, LEFT[1] - 8.5))
line(sheet, "PC-1083", dn=25, fluid="Process condensate", route=[
    offpage("in", at=(12, LEFT[2]), note="from V-401, P-107"), u801["C3"]],
    label_at=(100, LEFT[2] - 8.5))
line(sheet, "PC-1084", dn=25, fluid="Process condensate", route=[
    offpage("in", at=(12, LEFT[3]), note="from X-401, P-107"), u801["C4"]],
    label_at=(100, LEFT[3] - 8.5))
line(sheet, "PC-1136", dn=25, fluid="Steam condensate", route=[
    offpage("in", at=(12, LEFT[4]), note="from X-601, P-112"), u801["C5"]],
    label_at=(100, LEFT[4] - 8.5))

# MP steam header with the process steam branch (P-101), the header relief and the export on
# header pressure; LP steam, blowdown, vent
process = tee("T1005", at=(250, RIGHT[0]), branch="down", branch_dn=300)
relief = tee("T1143", at=(300, RIGHT[0]), branch="up", branch_dn=150)
pv2203 = valve("PV2203", "GlobeValve", tag="PV-2203", at=(335, RIGHT[0]))
line(sheet, "SM-1140", dn=350, fluid="MP steam", route=[
    u801["S1"], process, relief, pv2203,
    offpage("out", at=(EDGE, RIGHT[0]), note="to MP steam export (battery limit)")],
    label_at=(275, RIGHT[0] - 8.5))
line(sheet, "SM-1005", dn=300, fluid="MP steam", route=[
    process.branch, (250, RIGHT[1]),
    offpage("out", at=(EDGE, RIGHT[1]), note="to process steam, P-101")],
    label_at=(285, RIGHT[1] + 7))
pv2206 = valve("PV2206", "GlobeValve", tag="PV-2206", at=(330, RIGHT[2]))
line(sheet, "SL-1135", dn=65, fluid="LP steam", route=[
    u801["S2"], pv2206, offpage("out", at=(EDGE, RIGHT[2]), note="to X-601, P-112")],
    label_at=(275, RIGHT[2] + 7))
line(sheet, "BD-1141", dn=32, fluid="Boiler blowdown", route=[
    u801["S3"], offpage("out", at=(EDGE, RIGHT[3]), note="to blowdown (battery limit)")],
    label_at=(275, RIGHT[3] + 7))
line(sheet, "CO2-1142", dn=65, fluid="Stripper overhead (CO2)", route=[
    u801["S4"], offpage("out", at=(EDGE, RIGHT[4]), note="to CO2 vent stack")],
    label_at=(275, RIGHT[4] + 7))

# Boiler feed water pump (spare: open, D-029)
line(sheet, "BW-1138", dn=250, fluid="Boiler feed water", route=[
    u801["P1"], (180, 235), p801["N1"]], label_at=(225, 243.5))
lv2201 = valve("LV2201", "GlobeValve", tag="LV-2201", at=(240, 222))
line(sheet, "BW-1139", dn=200, fluid="Boiler feed water", route=[
    p801["N2"], (290, 222), valve("CV1139", "SwingCheckValve", at=(270, 222)), lv2201,
    (220, 222), u801["P2"]], label_at=(255, 213))

# Relief of the MP steam header and drum to atmosphere; globe valve placeholder made
# SpringLoadedGlobeSafetyValve with SAFETY_VALVE_SPRING_LOADED_SHAPE by hand, as in D-027
sheet.use_shape("SAFETY_VALVE_SPRING_LOADED_SHAPE")
line(sheet, "SM-1143", dn=150, fluid="MP steam", route=[
    relief.branch, valve("PSV2210", "GlobeValve", tag="PSV-2210", at=(300, 103)), (300, 96),
    offpage("out", at=(EDGE, 96), note="to atmosphere (silencer)")], label_at=(340, 88.5))

# Instruments
instrument(sheet, "LIC-2201", at=(262, 199), sensing=u801["L1"], signal_to=lv2201)
instrument(sheet, "LIC-2202", at=(140, 96), sensing=u801["L2"], signal_to=lv2202)
instrument(sheet, "PIC-2203", at=(318, 120), sensing="Line_SM1140_S3", sensing_at=(310, RIGHT[0]),
           signal_to=pv2203)
instrument(sheet, "FQI-2204", at=(362, 120), sensing="Line_SM1140_S3", sensing_at=(362, RIGHT[0]))
instrument(sheet, "TI-2205", at=(258, 99), sensing="Line_SM1140_S1", sensing_at=(245, RIGHT[0]))
instrument(sheet, "PIC-2206", at=(315, 155), sensing="Line_SL1135_S1", sensing_at=(350, RIGHT[2]),
           signal_to=pv2206)
instrument(sheet, "FI-2207", at=(330, 173), sensing="Line_BD1141_S1", sensing_at=(330, RIGHT[3]))
instrument(sheet, "FI-2208", at=(60, 119), sensing="Line_DW1137_S1", sensing_at=(60, LEFT[0]))
instrument(sheet, "FI-2209", at=(300, 210), sensing="Line_BW1139_S1", sensing_at=(290, 225))

note(sheet, "U-801 (lumped, D-015): deaerator, condensate stripper, steam drum 4600 kPa(a), superheater to 673 K, LP let-down",
     at=(20, 255))
note(sheet, "LIC-2201 steam drum level on the BFW (three-element control, S4); LIC-2202 deaerator level on the make-up water",
     at=(20, 262))
note(sheet, "PIC-2203 MP header pressure on the export; PIC-2206 LP steam 450 kPa(a) ASSUMED; P-801 spare open",
     at=(20, 269))
note(sheet, "PSV-2210: MP steam header relief, set pressure open (S8); drum and deaerator relief inside the package",
     at=(20, 276))

sheet.save(target)
for message in sheet.notes:
    if "DEXPI's NominalDiameterStandard" not in message:
        print(f"note: {message}", file=sys.stderr)
print(f"wrote {target}")
