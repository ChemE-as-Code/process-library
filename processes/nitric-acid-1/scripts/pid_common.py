"""Shared bits of the nitric-acid-1 P&ID draft scripts (scripts/draft_P-0*.py, D-017).

Provenance only, like the draft scripts: every sheet is hand-maintained (no `generator:` in
plant.yaml). Run a draft with: cheme run scripts/draft_P-0n.py <frame> <out>, where <frame> is
the empty sheet `cheme sheet new` wrote (kept as build/frames/P-0n.xml while drafting).
"""

import sys
from functools import partial

from chemeascode.domains.piping import authoring

# DN 250 and above are ISO 6708 sizes (DIN 2448 in DEXPI stops at DN 200), as hda-1 does
equipment = partial(authoring.equipment, standard="Iso6708")
line = partial(authoring.line, standard="Iso6708")

EDGE = 404          # right-hand off-page connectors (frame border at x = 416)
LEFT = 12           # left-hand off-page connectors
TOP = 14            # top off-page connectors
BOTTOM = 250        # bottom off-page connectors (above the notes and title block)
PUMP = "CENTRIFUGAL_PUMP_SHAPE"
HX = "HEAT_EXCHANGER_FIXED_TUBES_SHAPE"
KETTLE = "KETTLE_REBOILER_SHAPE"
DRUM = "VESSEL_WITH_DISHED_HEADS_SHAPE"
COMPRESSOR = "COMPRESSOR_CENTRIFUGAL_SHAPE"
TURBINE = "TURBINE_SHAPE"
COLUMN = "COLUMN_SHAPE"
PSV_SHAPE = "SAFETY_VALVE_SPRING_LOADED_SHAPE"
TRAIN = ("K-101, K-102 and X-101 form one machine train with the electric motor (D-011); "
         "machine protection, lube oil and seals in the train package (D-018)")


def make_safety_valve(sheet, valve_id, label_at=None):
    """Turn the GlobeValve placeholder *valve_id* into a SpringLoadedGlobeSafetyValve.

    The authoring API's valve() has no safety-valve class (core#132), so the draft draws a
    GlobeValve and changes three values, as hda-1 does (scripts/pid_common.py there): the DEXPI
    class, the tag from PipingComponentNumber to PositionNumber, and the symbol to
    SAFETY_VALVE_SPRING_LOADED_SHAPE. No XML is written, only these values change.
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


def valve_marks(sheet, instrument_id, valve_id, xy, actuator, tag_at=None, fail_at=None):
    """Print an actuated valve's tag and its fail position (F.C./F.O.) beside it.

    *actuator* is the side the actuator points to (up, down, left, right: towards the bubble);
    the tag goes on the other side of the line, the fail position beside the actuator head.
    Both are labels of the model's values (PipingComponentNumber of the valve,
    FailActionRepresentation of the controlled actuator), not free text.
    """
    x, y = xy
    tag, fail = {
        "up": ((x, y + 4.5), (x + 6, y - 7)),
        "down": ((x, y - 4.5), (x + 6, y + 7)),
        "right": ((x - 8, y), (x + 7, y - 4.5)),
        "left": ((x + 8, y), (x - 7, y - 4.5)),
    }[actuator]
    authoring.label(sheet, valve_id, "PipingComponentNumber", at=tag_at or tag)
    authoring.label(sheet, f"{instrument_id}_Actuator", "FailActionRepresentation",
                    at=fail_at or fail)


def save(sheet, target):
    sheet.save(target)
    for message in sheet.notes:
        if "DEXPI's NominalDiameterStandard" not in message:
            print(f"note: {message}", file=sys.stderr)
    print(f"wrote {target}")
