"""Draft of P-112: purge gas recovery package X-601 (collection M601, NH3 wash and
distillation, recovered NH3 chiller E601, cryogenic cold box X602, hydrogen-rich gas compressor
K601, all inside the package, D-013, D-026) with its process, steam and refrigerant
connections.

Provenance only: P-112 is hand-maintained (no `generator:` in plant.yaml); this script wrote
its first revision. Run: cheme run scripts/draft_P-112.py <frame> [<out>]. Equipment, lines,
DN and instruments: DESIGN.md D-029; streams S50, S53, S55, S36, S58, S59 of
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
    valve,
)

# DN 250 and above are ISO 6708 sizes (DIN 2448 in DEXPI stops at DN 200)
equipment = partial(authoring.equipment, standard="Iso6708")
line = partial(authoring.line, standard="Iso6708")

frame = Path(sys.argv[1])
target = Path(sys.argv[2]) if len(sys.argv) > 2 else frame
sheet = Sheet.load(frame)

EDGE = 400
Y = [96, 118, 140, 162, 184]

x601 = equipment(sheet, "Vessel", "X-601", shape="VESSEL_WITH_DISHED_HEADS_SHAPE", at=(210, 140),
                 scale=(2.0, 3.6),
                 nozzles=[Nozzle("N1", (-20, -44), 25), Nozzle("N2", (-20, -22), 40),
                          Nozzle("N3", (-20, 0), 40), Nozzle("N4", (-20, 22), 65),
                          Nozzle("N5", (-20, 44), 25), Nozzle("N6", (20, -44), 50),
                          Nozzle("N7", (20, -22), 125), Nozzle("N8", (20, 0), 25),
                          Nozzle("N9", (20, 22), 25), Nozzle("N10", (20, 44), 25)],
                 label_at=(210, 75))

# Feeds: loop purge (V-501), let-down gas (V-502), refrigeration inert vent (K-701)
line(sheet, "PG-1109", dn=25, fluid="Purge gas", route=[
    offpage("in", at=(12, Y[0]), note="from V-501, P-110"), x601["N1"]], label_at=(150, 88))
line(sheet, "PG-1113", dn=40, fluid="Let-down gas", route=[
    offpage("in", at=(12, Y[1]), note="from V-502, P-110"), x601["N2"]], label_at=(150, 110))
line(sheet, "PG-1126", dn=40, fluid="Inert vent", route=[
    offpage("in", at=(12, Y[2]), note="from K-701 package, P-111"), x601["N3"]],
    label_at=(150, 132))
# LP steam for the NH3 distillation and its condensate (U-801, P-113)
fv2106 = valve("FV2106", "GlobeValve", tag="FV-2106", at=(110, Y[3]))
line(sheet, "SL-1135", dn=65, fluid="LP steam", route=[
    offpage("in", at=(12, Y[3]), note="from U-801, P-113"), fv2106, x601["N4"]],
    label_at=(160, 154))
line(sheet, "PC-1136", dn=25, fluid="Steam condensate", route=[
    x601["N5"], offpage("out", at=(12, Y[4]), note="to U-801, P-113", rotation=180)],
    label_at=(150, 192.5))

# Products: hydrogen-rich gas to K-501 suction, tail gas to the reformer burners, recovered NH3
line(sheet, "PG-1087", dn=50, fluid="Hydrogen-rich gas", route=[
    x601["N6"], offpage("out", at=(EDGE, Y[0]), note="to K-501 suction, P-108")],
    label_at=(270, 88))
pv2104 = valve("PV2104", "GlobeValve", tag="PV-2104", at=(320, Y[1]))
line(sheet, "FG-1010", dn=125, fluid="Tail gas", route=[
    x601["N7"], pv2104, offpage("out", at=(EDGE, Y[1]), note="to H-101 burners, P-102")],
    label_at=(270, 110))
line(sheet, "AL-1129", dn=25, fluid="Liquid ammonia", route=[
    x601["N8"], offpage("out", at=(EDGE, Y[2]), note="to NH3 product, P-111")],
    label_at=(270, 132))
# Refrigerant for the recovered NH3 chiller E601 (K-701 package, P-111)
line(sheet, "AL-1124", dn=25, fluid="Ammonia refrigerant (liquid)", route=[
    offpage("in", at=(EDGE, Y[3]), note="from K-701 receiver, P-111", rotation=180), x601["N9"]],
    label_at=(270, 154))
line(sheet, "AG-1125", dn=25, fluid="Ammonia refrigerant (vapour)", route=[
    x601["N10"], offpage("out", at=(EDGE, Y[4]), note="to K-701 suction, P-111")],
    label_at=(270, 192.5))

# Instruments
instrument(sheet, "PI-2101", at=(90, 125), sensing="Line_PG1126_S1", sensing_at=(90, Y[2]))
instrument(sheet, "FI-2102", at=(60, 125), sensing="Line_PG1113_S1", sensing_at=(60, Y[1]))
instrument(sheet, "AI-2103", at=(300, 81), sensing="Line_PG1087_S1", sensing_at=(300, Y[0]))
instrument(sheet, "PIC-2104", at=(345, 132), sensing="Line_FG1010_S1", sensing_at=(290, Y[1]),
           signal_to=pv2104)
instrument(sheet, "FI-2105", at=(340, 81), sensing="Line_PG1087_S1", sensing_at=(340, Y[0]))
instrument(sheet, "FIC-2106", at=(70, 147), sensing="Line_SL1135_S1", sensing_at=(70, Y[3]),
           signal_to=fv2106)
instrument(sheet, "TI-2107", at=(300, 147), sensing="Line_AL1129_S1", sensing_at=(300, Y[2]))

note(sheet, "X-601 package: collection (M601), NH3 wash and distillation, E601 chiller, cold box, H2 compressor (D-013, D-026)",
     at=(20, 255))
note(sheet, "Recoveries ASSUMED (D-013); package controls, relief and the cold box purge inside the package",
     at=(20, 262))
note(sheet, "AI-2103: H2 content of the recovered gas; PIC-2104 tail gas pressure to the burners (400 kPa(a))",
     at=(20, 269))
note(sheet, "FIC-2106: LP steam to the NH3 distillation (D-013: 3 MJ/kg recovered NH3, ASSUMED)",
     at=(20, 276))

sheet.save(target)
for message in sheet.notes:
    if "DEXPI's NominalDiameterStandard" not in message:
        print(f"note: {message}", file=sys.stderr)
print(f"wrote {target}")
