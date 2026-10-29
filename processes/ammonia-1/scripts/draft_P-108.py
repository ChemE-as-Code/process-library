"""Draft of P-108: synthesis gas compressor K-501 (three stages, intercooled, aftercooler in
the package) with the recovered hydrogen junction (M501), anti-surge recycle and discharge
relief.

Provenance only: P-108 is hand-maintained (no `generator:` in plant.yaml); this script wrote
its first revision. Run: cheme run scripts/draft_P-108.py <frame> [<out>]. Equipment, lines,
DN and instruments: DESIGN.md D-028; streams S34, S36, S37, S38 of process/flowsheet.yaml.
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

k501 = equipment(sheet, "CentrifugalCompressor", "K-501", shape="COMPRESSOR_CENTRIFUGAL_SHAPE",
                 at=(200, 130), scale=2.0,
                 nozzles=[Nozzle("N1", (-15, 0), 350), Nozzle("N2", (15, 0), 200),
                          Nozzle("N3", (-6, 15), 450), Nozzle("N4", (6, 15), 450)],
                 label_at=(200, 108))

# Dry make-up gas from X-401 (P-107), recovered hydrogen from the X-601 package joins it (M501);
# the anti-surge recycle returns upstream of the suction flow element
h2_in = tee("T1087", at=(100, 130), branch="up", branch_dn=50)
recycle_in = tee("T1089", at=(140, 130), branch="up", branch_dn=150)
line(sheet, "PG-1081", dn=350, fluid="Synthesis gas", route=[
    offpage("in", at=(12, 130), note="from X-401, P-107"), h2_in, recycle_in, k501["N1"]],
    label_at=(50, 121.5))
line(sheet, "PG-1087", dn=50, fluid="Hydrogen-rich gas", route=[
    offpage("in", at=(12, 60), note="from X-601 (H2 compressor)"), (100, 60), h2_in.branch],
    label_at=(60, 51.5))

# Discharge (after the aftercooler in the package) to the synthesis loop
recycle_out = tee("T1088A", at=(240, 130), branch="up", branch_dn=150)
relief = tee("T1088B", at=(262, 130), branch="down", branch_dn=150)
line(sheet, "PG-1088", dn=200, fluid="Synthesis gas", route=[
    k501["N2"], recycle_out, relief, valve("CV1088", "SwingCheckValve", at=(290, 130)),
    offpage("out", at=(EDGE, 130), note="to the synthesis loop (M502)")], label_at=(340, 121.5))
uv1703 = valve("UV1703", "GlobeValve", tag="UV-1703", at=(190, 80))
line(sheet, "PG-1089", dn=150, fluid="Synthesis gas", route=[
    recycle_out.branch, (240, 80), uv1703, (140, 80), recycle_in.branch], label_at=(215, 71.5))
# Discharge relief: globe valve placeholder made a SpringLoadedGlobeSafetyValve with
# SAFETY_VALVE_SPRING_LOADED_SHAPE (tag in PositionNumber) by hand, as in D-027
sheet.use_shape("SAFETY_VALVE_SPRING_LOADED_SHAPE")
line(sheet, "PG-1090", dn=150, fluid="Synthesis gas", route=[
    relief.branch, valve("PSV1704", "GlobeValve", tag="PSV-1704", at=(262, 152)), (262, 175),
    offpage("out", at=(300, 175), note="to flare")], label_at=(280, 166.5))

# Cooling water to the intercoolers and aftercooler (in the package)
line(sheet, "CWS-1091", dn=450, fluid="Cooling water", route=[
    offpage("in", at=(12, 200), note="from CW supply"), (194, 200), k501["N3"]],
    label_at=(60, 191.5))
line(sheet, "CWR-1092", dn=450, fluid="Cooling water", route=[
    k501["N4"], (206, 215), offpage("out", at=(12, 215), note="to CW return", rotation=180)],
    label_at=(60, 219.5))

# Instruments
instrument(sheet, "PI-1701", at=(120, 150), sensing="Line_PG1081_S2", sensing_at=(120, 130))
instrument(sheet, "FI-1702", at=(70, 150), sensing="Line_PG1081_S1", sensing_at=(70, 130))
instrument(sheet, "UIC-1703", at=(160, 100), sensing="Line_PG1081_S3", sensing_at=(165, 130),
           signal_to=uv1703)
instrument(sheet, "PI-1704", at=(320, 150), sensing="Line_PG1088_S3", sensing_at=(320, 130))
instrument(sheet, "TI-1705", at=(350, 150), sensing="Line_PG1088_S3", sensing_at=(350, 130))
instrument(sheet, "FI-1706", at=(60, 75), sensing="Line_PG1087_S1", sensing_at=(60, 60))

note(sheet, "K-501: 3 stages, intercoolers and aftercooler in the package, electric drive (D-016)",
     at=(20, 262))
note(sheet, "UIC-1703: anti-surge control of K-501; capacity and speed control in the package",
     at=(20, 269))
note(sheet, "Spec break at the K-501 discharge (2850 to 14,600 kPa(a)); PSV-1704 set pressure open (S8)",
     at=(20, 276))

sheet.save(target)
for message in sheet.notes:
    if "DEXPI's NominalDiameterStandard" not in message:
        print(f"note: {message}", file=sys.stderr)
print(f"wrote {target}")
