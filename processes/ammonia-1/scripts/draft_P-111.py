"""Draft of P-111: product flash drum V-701, the ammonia refrigeration package K-701 (chiller
circuit compressor, flash-gas stages, receiver, vent chiller and knock-out inside the package)
with the refrigerant condenser E-701, and the liquid ammonia product to the storage interface
(battery limit) with the recovered ammonia from X-601 (M701).

Provenance only: P-111 is hand-maintained (no `generator:` in plant.yaml); this script wrote
its first revision. Run: cheme run scripts/draft_P-111.py <frame> [<out>]. Equipment, lines,
DN and instruments: DESIGN.md D-029; streams S54-S56, S58, S60, S88-S93 of
process/flowsheet.yaml.
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

k701 = equipment(sheet, "CentrifugalCompressor", "K-701", shape="COMPRESSOR_CENTRIFUGAL_SHAPE",
                 at=(220, 110), scale=3.0,
                 nozzles=[Nozzle("N1", (-22, 0), 900), Nozzle("N2", (22, -6), 450),
                          Nozzle("N3", (-14, 17), 400), Nozzle("N4", (22, 8), 200),
                          Nozzle("N5", (6, 22), 200), Nozzle("N6", (16, 16), 40),
                          Nozzle("N7", (-4, 22), 50), Nozzle("N8", (-10, -20), 125),
                          Nozzle("N9", (0, -22), 125)],
                 label_at=(248, 88))
e701 = equipment(sheet, "TubularHeatExchanger", "E-701", shape="HEAT_EXCHANGER_FIXED_TUBES_SHAPE",
                 at=(310, 60),
                 nozzles=[Nozzle("T1", (-17.5, 0), 700), Nozzle("T2", (17.5, 0), 700),
                          Nozzle("S1", (-7, 7), 450), Nozzle("S2", (7, 7), 200)],
                 label_at=(310, 47))
v701 = equipment(sheet, "Vessel", "V-701", shape="VESSEL_WITH_DISHED_HEADS_SHAPE", at=(90, 190),
                 scale=(1.0, 1.4),
                 nozzles=[Nozzle("N1", (-10, 5), 150), Nozzle("N2", (0, -21), 400),
                          Nozzle("N3", (0, 21), 150), Nozzle("N4", (10, -8), 50),
                          Nozzle("N5", (10, 8), 50), Nozzle("N6", (-10, -10), 80)],
                 label_at=(68, 212))

# Refrigerant circuit: chiller vapour (E-504, P-110) -> K-701 -> E-701 -> receiver (package)
x601_vap = tee("T1125", at=(150, 110), branch="up", branch_dn=25)
line(sheet, "AG-1118", dn=900, fluid="Ammonia refrigerant (vapour)", route=[
    offpage("in", at=(12, 110), note="from E-504, P-110"), x601_vap, k701["N1"]],
    label_at=(100, 120))
line(sheet, "AG-1125", dn=25, fluid="Ammonia refrigerant (vapour)", route=[
    offpage("in", at=(12, 95), note="from E601, X-601, P-112"), (150, 95), x601_vap.branch],
    label_at=(100, 86.5))
line(sheet, "AG-1122", dn=450, fluid="Ammonia refrigerant (vapour)", route=[
    k701["N2"], (303, 104), e701["S1"]], label_at=(272, 96))
line(sheet, "AL-1123", dn=200, fluid="Ammonia refrigerant (liquid)", route=[
    e701["S2"], (317, 118), k701["N4"]], label_at=(280, 126))
x601_liq = tee("T1124", at=(260, 175), branch="down", branch_dn=25)
line(sheet, "AL-1117", dn=200, fluid="Ammonia refrigerant (liquid)", route=[
    k701["N5"], (226, 175), x601_liq,
    offpage("out", at=(EDGE, 175), note="to E-504, P-110")], label_at=(330, 183.5))
line(sheet, "AL-1124", dn=25, fluid="Ammonia refrigerant (liquid)", route=[
    x601_liq.branch, (260, 200), offpage("out", at=(EDGE, 200), note="to E601, X-601, P-112")],
    label_at=(330, 208.5))

# Cooling water: E-701 and the flash-gas cooler in the package (headers on P-114)
line(sheet, "CWS-1130", dn=700, fluid="Cooling water", route=[
    offpage("in", at=(EDGE, 60), note="from CW supply, P-114", rotation=180), e701["T2"]],
    label_at=(360, 68))
line(sheet, "CWR-1131", dn=700, fluid="Cooling water", route=[
    e701["T1"], (280, 60), (280, 30), offpage("out", at=(EDGE, 30), note="to CW return, P-114")],
    label_at=(340, 38))
line(sheet, "CWS-1132", dn=125, fluid="Cooling water", route=[
    offpage("in", at=(12, 60), note="from CW supply, P-114"), (210, 60), k701["N8"]],
    label_at=(110, 68))
line(sheet, "CWR-1133", dn=125, fluid="Cooling water", route=[
    k701["N9"], (220, 45), offpage("out", at=(12, 45), note="to CW return, P-114", rotation=180)],
    label_at=(110, 37))

# Product flash: let-down liquid from V-502 (P-110); flash gas to the flash-gas stages of K-701,
# vent chiller condensate back; vent to X-601
line(sheet, "AL-1114", dn=150, fluid="Liquid ammonia", route=[
    offpage("in", at=(12, 195), note="from V-502, P-110"), v701["N1"]], label_at=(45, 203))
line(sheet, "AG-1121", dn=400, fluid="Flash gas", route=[
    v701["N2"], (90, 145), (206, 145), k701["N3"]], label_at=(150, 136.5))
line(sheet, "AL-1127", dn=50, fluid="Liquid ammonia", route=[
    k701["N7"], (216, 155), (110, 155), (110, 182), v701["N4"]], label_at=(160, 163.5))
fv2007 = valve("PV2007", "GlobeValve", tag="PV-2007", at=(330, 150))
line(sheet, "PG-1126", dn=40, fluid="Inert vent", route=[
    k701["N6"], (236, 150), fv2007, offpage("out", at=(EDGE, 150), note="to X-601, P-112")],
    label_at=(280, 158.5))

# Liquid ammonia product to storage (battery limit); recovered NH3 from X-601 joins (M701)
nh3_rec = tee("T1129", at=(170, 225), branch="down", branch_dn=25)
lv2005 = valve("LV2005", "GlobeValve", tag="LV-2005", at=(130, 225))
line(sheet, "AL-1128", dn=150, fluid="Liquid ammonia", route=[
    v701["N3"], (90, 225), lv2005, nh3_rec,
    offpage("out", at=(EDGE, 225), note="to NH3 storage (battery limit)")], label_at=(270, 233.5))
line(sheet, "AL-1129", dn=25, fluid="Liquid ammonia", route=[
    offpage("in", at=(12, 245), note="from X-601, P-112"), (170, 245), nh3_rec.branch],
    label_at=(110, 253.5))

# Relief of V-701 to the flare header (P-114); globe valve placeholder made
# SpringLoadedGlobeSafetyValve with SAFETY_VALVE_SPRING_LOADED_SHAPE by hand, as in D-027
sheet.use_shape("SAFETY_VALVE_SPRING_LOADED_SHAPE")
line(sheet, "AG-1134", dn=80, fluid="Ammonia vapour", route=[
    v701["N6"], valve("PSV2010", "GlobeValve", tag="PSV-2010", at=(62, 180)), (40, 180),
    (40, 165), offpage("out", at=(12, 165), note="to flare header, P-114", rotation=180)],
    label_at=(55, 172))

# Instruments
instrument(sheet, "PI-2001", at=(72, 150), sensing="Line_AG1121_S1", sensing_at=(90, 155))
instrument(sheet, "TI-2002", at=(110, 210), sensing="Line_AL1128_S1", sensing_at=(110, 225))
instrument(sheet, "FQI-2003", at=(330, 238), sensing="Line_AL1128_S2", sensing_at=(330, 225))
instrument(sheet, "PI-2004", at=(175, 125), sensing="Line_AG1118_S2", sensing_at=(175, 110))
instrument(sheet, "LIC-2005", at=(125, 200), sensing=v701["N5"], signal_to=lv2005)
instrument(sheet, "PIC-2007", at=(350, 138), sensing="Line_PG1126_S1", sensing_at=(300, 150),
           signal_to=fv2007)
instrument(sheet, "TI-2008", at=(335, 95), sensing="Line_AL1123_S1", sensing_at=(317, 95))

note(sheet, "K-701 package: chiller and flash-gas stages, intercooler, receiver, vent chiller and knock-out (D-017, D-026)",
     at=(20, 262))
note(sheet, "PIC-2007: receiver vent pressure 1700 kPa(a); LIC-2005 product flash drum level",
     at=(20, 269))
note(sheet, "PSV-2010: set pressure and relief case open (S8); product pumps and storage outside the battery limit",
     at=(20, 276))

sheet.save(target)
for message in sheet.notes:
    if "DEXPI's NominalDiameterStandard" not in message:
        print(f"note: {message}", file=sys.stderr)
print(f"wrote {target}")
