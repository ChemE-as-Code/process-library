"""Shared bits of the methanol-1 P&ID draft scripts (scripts/draft_P-0*.py, D-016).

Provenance only, like the draft scripts: every sheet is hand-maintained (no `generator:` in
plant.yaml). Run a draft with: cheme run scripts/draft_P-0n.py <frame> [<out>], where <frame>
is the empty sheet `cheme sheet new` wrote.
"""

import sys
from functools import partial

from chemeascode.domains.piping import authoring

# DN 250 and above are ISO 6708 sizes (DIN 2448 in DEXPI stops at DN 200)
equipment = partial(authoring.equipment, standard="Iso6708")
line = partial(authoring.line, standard="Iso6708")

# Sheet geometry (A3 frame of the template, sheet mm, Y down): the drawing area runs from the
# left border (x = 4) to the right border (x = 416), the title block takes x >= 295 below
# y = 257 and the notes go below the drawing at the left.
EDGE = 404          # right-hand off-page connectors
LEFT = 12           # left-hand off-page connectors
TOP = 14            # top off-page connectors
BOTTOM = 248        # bottom off-page connectors (left of the title block)
NOTE_X = 20         # left edge of the notes
NOTE_Y = (262, 269, 276)
PUMP = "CENTRIFUGAL_PUMP_SHAPE"
HX = "HEAT_EXCHANGER_FIXED_TUBES_SHAPE"
DRUM = "VESSEL_WITH_DISHED_HEADS_SHAPE"
COMPRESSOR = "COMPRESSOR_CENTRIFUGAL_SHAPE"
COLUMN = "COLUMN_SHAPE"
PSV_SHAPE = "SAFETY_VALVE_SPRING_LOADED_SHAPE"


def make_safety_valve(sheet, valve_id, label_at=None):
    """Turn the GlobeValve placeholder *valve_id* into a SpringLoadedGlobeSafetyValve.

    The authoring API's valve() has no safety-valve class, so the draft draws a GlobeValve and
    changes three values, as hda-1 and ammonia-1 do: the DEXPI class, the tag property from
    PipingComponentNumber to PositionNumber, and the symbol. No XML is written by hand.
    """
    element = sheet.find(valve_id)
    element.set("type", "Plant/Piping.SpringLoadedGlobeSafetyValve")
    for data in element.findall("Data"):
        if data.get("property") == "PipingComponentNumber":
            data.set("property", "PositionNumber")
    shape_id = sheet.use_shape(PSV_SHAPE)
    usage = sheet.find(f"{valve_id}_SymbolShape")
    for ref in usage.findall("References"):
        if ref.get("property") == "Shape":
            ref.set("objects", f"#{shape_id}")
    if label_at is not None:
        authoring.label(sheet, valve_id, "PositionNumber", at=label_at)


FAIL_OFFSET = {"up": (4.5, -7.2), "down": (4.5, 7.2), "left": (-7.2, -3.5), "right": (7.2, -3.5),
               "up-left": (-4.5, -7.2), "down-left": (-4.5, 7.2),
               "left-below": (-7.2, 3.5), "right-below": (7.2, 3.5)}


def fail_label(sheet, instrument_id, valve_at, side):
    """The fail position (F.C., F.O.) beside the actuator of *instrument_id*'s valve.

    `instrument(fail_action=...)` records the FailAction on the actuator but draws no text; this
    adds the label showing its FailActionRepresentation, beside the actuator tip on *side* (the
    side the actuator points to: up, down, left, right), as a FailActionLabel.
    """
    dx, dy = FAIL_OFFSET[side]
    label_id = authoring.label(sheet, f"{instrument_id}_Actuator", "FailActionRepresentation",
                               at=(valve_at[0] + dx, valve_at[1] + dy))
    sheet.find(label_id).set("type", "Plant/Diagram.FailActionLabel")


def tag_label(sheet, valve_id, at):
    """The tag (PipingComponentNumber) of a shutdown or anti-surge valve printed beside it."""
    authoring.label(sheet, valve_id, "PipingComponentNumber", at=at)


def notes(sheet, *texts):
    """The sheet notes, one per row below the drawing, left-aligned."""
    for text, y in zip(texts, NOTE_Y, strict=False):
        authoring.note(sheet, text, at=(NOTE_X, y))


def save(sheet, target):
    sheet.save(target)
    for message in sheet.notes:
        if "DEXPI's NominalDiameterStandard" not in message:
            print(f"note: {message}", file=sys.stderr)
    print(f"wrote {target}")
