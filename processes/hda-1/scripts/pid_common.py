"""Shared bits of the hda-1 P&ID draft scripts (scripts/draft_P-0*.py, S3b, D-025).

Provenance only, like the draft scripts: every sheet is hand-maintained (no `generator:` in
plant.yaml). Run a draft with: cheme run scripts/draft_P-0n.py <frame> <out>.
"""

import sys
from functools import partial

from chemeascode.domains.piping import authoring

# DN 250 and above are ISO 6708 sizes (DIN 2448 in DEXPI stops at DN 200), as ammonia-1 does
equipment = partial(authoring.equipment, standard="Iso6708")
line = partial(authoring.line, standard="Iso6708")

EDGE = 404          # right-hand off-page connectors (frame border at x = 416)
LEFT = 12           # left-hand off-page connectors
TOP = 14            # top off-page connectors
PUMP = "CENTRIFUGAL_PUMP_SHAPE"
HX = "HEAT_EXCHANGER_FIXED_TUBES_SHAPE"
DRUM = "VESSEL_WITH_DISHED_HEADS_SHAPE"
PSV_SHAPE = "SAFETY_VALVE_SPRING_LOADED_SHAPE"


def make_safety_valve(sheet, valve_id, label_at=None):
    """Turn the GlobeValve placeholder *valve_id* into a SpringLoadedGlobeSafetyValve.

    The authoring API's valve() has no safety-valve class (core#132), so
    the draft draws a GlobeValve and changes three things, the edit ammonia-1 made by hand
    (its D-027): the DEXPI class, the tag from PipingComponentNumber to PositionNumber, and the
    symbol to SAFETY_VALVE_SPRING_LOADED_SHAPE. No XML is written, only these values change.
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


def save(sheet, target):
    sheet.save(target)
    for message in sheet.notes:
        if "DEXPI's NominalDiameterStandard" not in message:
            print(f"note: {message}", file=sys.stderr)
    print(f"wrote {target}")
