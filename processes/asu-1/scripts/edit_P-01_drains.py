"""One-off edit of pid/P-01.xml (hand-maintained): the MAC condensate drains of D-058 / D-064.

Provenance only, never rerun over the sheet: after this edit the XML is the source (AGENTS.md).
Run once with `cheme run scripts/edit_P-01_drains.py pid/P-01.xml`, after the drain nozzles
E1102_N5 / E1103_N5 were pasted from `cheme fragment nozzle` and the E-1102 label and TIA-1111
were moved with `cheme move`.

It adds, with the authoring API (the builders of `cheme fragment`):
- the STEAM_TRAP_SHAPE symbol to the catalogue (no trap symbol in the cheme-as-code
  catalogue; ISO 10628-2 number not checked, so the name is the registration number);
- line CD-1001: E-1102 N5 (integral moisture separator drain) -> gate valve -> trap -> off-page
  "to drain";
- line CD-1002: E-1103 N5, the same.
The traps are built as ball valves (the builder's valve classes) and then re-classed by hand to
Plant/Piping.SteamTrap with STEAM_TRAP_SHAPE: two attribute edits per trap, see D-064.
"""

import sys

from chemeascode.domains.piping.authoring import Sheet, line, offpage, valve
from chemeascode.domains.piping.authoring.shapes import PIPE_RGB, ShapeDef


def _trap(p):
    # Inline: ends at x = -5 and 5 (scale 1, like the valves), a float trap: body and float.
    p.rect(-5, -5, 5, 5, width=0.25)
    p.ellipse(0, 0, 2.5)


TRAP = ShapeDef(
    "STEAM_TRAP_SHAPE",
    "Shape_SteamTrap",
    "steam or condensate drain trap (float type): square body with the float; ends at x = -5 and 5",
    "0.4 inline (ends 2 mm from the centre), like a valve",
    _trap,
    rgb=PIPE_RGB,
)

sheet = Sheet.load(sys.argv[1])
if "STEAM_TRAP_SHAPE" not in sheet.shapes:
    sheet.add_shape(TRAP.element())

# E-1102 drain: right of the cooler, down at x 110 below the E-1102 label.
line(
    sheet,
    "CD-1001",
    dn=25,
    fluid="Condensate",
    id="Line_CD1001",
    route=[
        "E1102_N5",
        (110, 118),
        valve("Valve_CD1001_Iso", "GateValve", at=(110, 125)),
        valve("Trap_CD1001", "BallValve", at=(110, 132)),
        offpage("out", at=(110, 139), id="OPC_CD1001", note="to drain", rotation=90),
    ],
    label_at=(113, 127),
)

# E-1103 drain: right under AIR-1002, down at x 148 (TIA-1111 moved east to make room).
line(
    sheet,
    "CD-1002",
    dn=25,
    fluid="Condensate",
    id="Line_CD1002",
    route=[
        "E1103_N5",
        (148, 73),
        valve("Valve_CD1002_Iso", "GateValve", at=(148, 80)),
        valve("Trap_CD1002", "BallValve", at=(148, 87)),
        offpage("out", at=(148, 94), id="OPC_CD1002", note="to drain", rotation=90),
    ],
    label_at=(151, 82),
)

sheet.save()
