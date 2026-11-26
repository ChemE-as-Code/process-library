"""P-401 stage S7 fixes to the S6 review (provenance script, run once; the XML is the source).

    cheme run scripts/fix_P-401_s7.py pid/P-401.xml

E-401D sump level (S6#4, D-040): the density loop DIC-4002 on DV-4002 is replaced by the level
loop LIC-4011D on the product draw valve (DV-4002 retagged LV-4011D by `cheme set` first), and
DIC-4002 is redrawn on the concentrate suction 80-CL-4014; its output is the set point of the
steam flow FIC-4001 (cascade, control/loops.yaml), written as a note instead of a signal line
across the sheet. The old DIC-4002 objects are removed by id. The new measuring line no longer
runs through the valve actuator (S6#6).
"""

import sys
from pathlib import Path

from chemeascode.domains.piping.authoring import Sheet, instrument, note

target = Path(sys.argv[1] if len(sys.argv) > 1 else "pid/P-401.xml")
sheet = Sheet.load(target)

for object_id in ("Inst_DIC4002_System", "Inst_DIC4002", "Inst_DIC4002_Drawing", "Inst_DIC4002_Actuator_Drawing"):
    element = sheet.find(object_id)
    element.getparent().remove(element)

instrument(sheet, "LIC-4011D", at=(334, 118), sensing="E401D_L1", sensing_points=[(318, 90), (318, 118)],
           signal_to="DV4002", signal_points=[(334, 224)])
instrument(sheet, "DIC-4002", at=(262, 200), sensing="Line_80CL4014_S1", sensing_at=(280, 200), id="Inst_DIC4002R")
note(sheet, "DIC-4002: SP of FIC-4001", at=(250, 209), size=2.0)

sheet.save()
for message in sheet.notes:
    print(f"note: {message}", file=sys.stderr)
print(f"wrote {target}")
