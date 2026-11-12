"""Shared helpers of the P&ID generators scripts/draft_P-0n.py of lng-terminal-1.

Shared by the generators of the eight generated sheets (plant.yaml, D-021). Builders
from cheme-as-code's authoring API with ISO 6708 sizes (DIN 2448 in DEXPI stops at DN 200);
three shapes the catalogue lacks (a full-containment LNG tank, a marine loading arm, a
restriction orifice, D-036), built from
cheme-as-code's own XML element helpers; the relief valves drawn as globe valves and turned
into spring-loaded safety valves (as ammonia-1 D-027 does); the off-page connectors put on an
edge of the drawing area (`edge_offpage`, core 1.11, D-038). Each draft records the lines,
instruments and relief devices it draws (`Lists`), so the lists are written from the same
values as the sheet (`scripts/build_lists.py`, DESIGN.md D-021).
"""

from __future__ import annotations

import json
import sys
from functools import partial
from pathlib import Path

from chemeascode.domains.piping import authoring
from chemeascode.domains.piping.authoring import (  # noqa: F401  (re-exported for the drafts)
    Nozzle,
    label,
    Sheet,
    instrument,
    note,
    offpage,
    tee,
    valve,
)
from chemeascode.domains.piping.authoring._xml import comps, obj, points, stroke, string

equipment = partial(authoring.equipment, standard="Iso6708")
_line = partial(authoring.line, standard="Iso6708")

BLACK = (0, 0, 0)

# Off-page connectors on an edge of the drawing area (core 1.11 cheme.offpage-not-on-edge, core ADR
# 0049; D-038). The drawing area of every frame is the inside of the border, x 4..416 and y 4..258 mm
# (down to the top of the title block); a connector is on an edge within 10 mm of it. Its node sits
# here, so that its 7 mm arrow (scale 0.7) ends 3 mm (left, top, right) or 9 mm (bottom) inside it.
EDGE = {"left": 14, "right": 405, "top": 14, "bottom": 242}
_EDGE_FLOW = {("in", "left"): 0, ("out", "left"): 180, ("in", "right"): 180, ("out", "right"): 0,
              ("in", "top"): 90, ("out", "top"): 270, ("in", "bottom"): 270, ("out", "bottom"): 90}


def edge_offpage(direction: str, side: str, at: float, note: str | None = None, note_at=None):
    """An off-page connector on the *side* edge (left, right, top, bottom) of the drawing area: *at*
    is its place along that edge (y on the left or right edge, x on the top or bottom one), its arrow
    points across the edge, into the sheet for ``in`` and out of it for ``out`` (D-038). Give
    *note_at* (the centre of the note): the default would put the note beyond the edge."""
    xy = (EDGE[side], at) if side in ("left", "right") else (at, EDGE[side])
    return offpage(direction, at=xy, note=note, note_at=note_at, rotation=_EDGE_FLOW[(direction, side)])


def _polyline(pid: str, pts, width=0.35, closed=False):
    pts = list(pts) + ([pts[0]] if closed else [])
    return obj(pid, "Core/Diagram.PolyLine", points("Points", pts), stroke(BLACK, width))


def _shape(sheet: Sheet, sid: str, name: str, lines) -> str:
    if name in sheet.shapes:
        return sheet.shapes[name]
    prims = [_polyline(f"{sid}_P{i + 1}", pts, w, c) for i, (pts, w, c) in enumerate(lines)]
    sheet.add_shape(obj(sid, "Core/Diagram.Shape", comps("Primitives", *prims), string("Name", name),
                        string("SymbolRegistrationNumber", f"cheme-as-code lng-terminal-1 {name} (own drawing)")))
    return sheet.shapes[name]


def tank_shape(sheet: Sheet) -> str:
    """Full-containment LNG tank: concrete outer tank with its dome, the 9 % Ni inner tank
    (dashed) and the suspended deck; 60 x 54 mm at scale 1, centre at mid height."""
    dome = [(-30, -14), (-26, -19), (-18, -23.5), (-8, -25.6), (0, -26), (8, -25.6), (18, -23.5),
            (26, -19), (30, -14)]
    outer = [(-30, 28)] + dome + [(30, 28)]
    inner = [(-26, 26), (-26, -12), (26, -12), (26, 26)]
    deck = [(-27.5, -13.5), (27.5, -13.5)]
    return _shape(sheet, "ShapeLNG_Tank", "FULL_CONTAINMENT_TANK_SHAPE",
                  [(outer, 0.5, True), (inner, 0.25, True), (deck, 0.18, False)])


def arm_shape(sheet: Sheet) -> str:
    """Marine loading arm: riser on its base, inboard arm, outboard arm, counterweight and the
    triple swivel at the presentation flange; shore flange at (0, 14), ship flange at (16, 8)."""
    riser = [(0, 14), (0, -8)]
    base = [(-4, 14), (4, 14)]
    inboard = [(-6, -6), (0, -8), (10, -14)]
    outboard = [(10, -14), (16, 4)]
    swivel = [(14.5, 4), (17.5, 4), (17.5, 6), (14.5, 6)]
    weight = [(-9, -8), (-5, -8), (-5, -4), (-9, -4)]
    drop = [(16, 6), (16, 8)]
    return _shape(sheet, "ShapeLNG_Arm", "MARINE_LOADING_ARM_SHAPE",
                  [(riser, 0.5, False), (base, 0.5, False), (inboard, 0.35, False),
                   (outboard, 0.35, False), (swivel, 0.25, True), (weight, 0.35, True),
                   (drop, 0.35, False)])


def to_safety_valve(sheet: Sheet, vid: str, cls: str = "SpringLoadedGlobeSafetyValve") -> None:
    """Turn the globe valve *vid* (drawn by `line`) into a safety valve with its symbol."""
    element = sheet.find(vid)
    element.set("type", f"Plant/Piping.{cls}")
    number = element.find("Data[@property='PipingComponentNumber']")
    if number is not None:  # a safety valve carries its tag as PositionNumber
        number.set("property", "PositionNumber")
    shape = sheet.use_shape("SAFETY_VALVE_SPRING_LOADED_SHAPE")
    usage = sheet.find(f"{vid}_SymbolShape")
    usage.find("References[@property='Shape']").set("objects", f"#{shape}")


def orifice_shape(sheet: Sheet) -> str:
    """Restriction orifice: the pipe through two short plates across it; 10 mm long at scale 1
    like the valve symbols, so it takes a valve's ports (the catalogue has no orifice shape)."""
    run = [(-5, 0), (5, 0)]
    plate_a = [(-0.9, -3.5), (-0.9, 3.5)]
    plate_b = [(0.9, -3.5), (0.9, 3.5)]
    return _shape(sheet, "ShapeLNG_Orifice", "RESTRICTION_ORIFICE_SHAPE",
                  [(run, 0.35, False), (plate_a, 0.5, False), (plate_b, 0.5, False)])


def to_orifice(sheet: Sheet, vid: str) -> None:
    """Turn the globe valve *vid* (drawn by `line`) into a restriction orifice with its own
    symbol (checker of D-036: FO-4151 / FO-4152 were drawn and modelled as globe valves)."""
    element = sheet.find(vid)
    element.set("type", "Plant/Piping.RestrictionOrifice")
    shape = orifice_shape(sheet)
    usage = sheet.find(f"{vid}_SymbolShape")
    usage.find("References[@property='Shape']").set("objects", f"#{shape}")


def set_dn(sheet: Sheet, node_ids: list[str], dn: int, segments: list[str] = ()) -> None:
    """Give the piping nodes *node_ids* and the segments *segments* the size DN *dn* (a segment
    smaller than its line: a pump column that starts a header, a reducing tee)."""
    for node_id in [*node_ids, *segments]:
        node = sheet.find(node_id)
        for prop, value in [("NominalDiameterNumericalValueRepresentation", str(dn)),
                            ("NominalDiameterRepresentation", f"DN {dn}")]:
            data = node.find(f"Data[@property='{prop}']/String")
            if data is not None:
                data.text = value
        enum = node.find("Data[@property='NominalDiameterStandard']/DataReference")
        if enum is not None:
            enum.set("data", f"Plant/Enumerations.NominalDiameterStandardClassification.Iso6708ObjectDn{dn}")


class Lists:
    """The list entries a draft draws: lines, instruments, relief devices (D-021)."""

    def __init__(self, sheet_id: str):
        self.sheet_id = sheet_id
        self.lines: list[dict] = []
        self.instruments: list[dict] = []
        self.items: list[dict] = []
        self.psvs: list[tuple[str, str, tuple | None]] = []

    def line(self, sheet, number, *, dn, fluid, route, frm, to, notes="", insulation="cold (PIR)",
             pclass="Class 150", label_at=None, labels=True, segments=None):
        made = _line(sheet, number, dn=dn, fluid=fluid, route=route, label_at=label_at,
                     labels=labels)
        entry = {"number": number, "from": frm, "to": to, "nominal_diameter": f"DN{dn}",
                 "pressure_class": pclass, "fluid": fluid, "insulation": insulation,
                 "sheet": self.sheet_id, "notes": notes}
        if segments:
            entry["segments"] = segments
        self.lines.append(entry)
        return made

    def inst(self, sheet, tag, service, notes="", **kw):
        made = instrument(sheet, tag, **kw)
        entry = {"tag": tag, "service": service, "sheet": self.sheet_id}
        if notes:
            entry["notes"] = notes
        self.instruments.append(entry)
        return made

    def relief(self, vid, tag, line_no, set_barg, case, notes, cls="SpringLoadedGlobeSafetyValve",
               label_at=None):
        """A relief valve drawn as a globe valve, turned into a safety valve by finish(); its tag
        is printed at *label_at* (default 6 mm above the symbol)."""
        self.psvs.append((vid, cls, label_at))
        self.items.append({"tag": tag, "type": cls, "line": line_no, "sheet": self.sheet_id,
                           "set_pressure_barg": set_barg, "relief_case": case, "notes": notes})
        return valve(vid, "GlobeValve", tag=tag)

    def finish(self, sheet: Sheet, target: Path) -> None:
        for vid, cls, at in self.psvs:
            to_safety_valve(sheet, vid, cls)
            label(sheet, vid, "PositionNumber", at=at)
        sheet.save(target)
        out = Path("build") / f"lists_{self.sheet_id}.json"
        out.parent.mkdir(exist_ok=True)
        out.write_text(json.dumps({"lines": self.lines, "instruments": self.instruments,
                                   "piping_items": self.items}, indent=1), encoding="utf-8")
        for message in sheet.notes:
            if "NominalDiameterStandard" not in message:
                print(f"note: {message}", file=sys.stderr)
        print(f"wrote {target} and {out}")
