"""Shared helpers of the P&ID generators scripts/draft_P-0n.py of lng-terminal-1.

Provenance only (the sheets are hand-maintained after their first run, AGENTS.md). Builders
from cheme-as-code's authoring API with ISO 6708 sizes (DIN 2448 in DEXPI stops at DN 200);
two shapes the catalogue lacks (a full-containment LNG tank, a marine loading arm), built from
cheme-as-code's own XML element helpers; the relief valves drawn as globe valves and turned
into spring-loaded safety valves (as ammonia-1 D-027 does). Each draft records the lines,
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
        self.psvs: list[str] = []

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

    def relief(self, vid, tag, line_no, set_barg, case, notes, cls="SpringLoadedGlobeSafetyValve"):
        self.psvs.append((vid, cls))
        self.items.append({"tag": tag, "type": cls, "line": line_no, "sheet": self.sheet_id,
                           "set_pressure_barg": set_barg, "relief_case": case, "notes": notes})
        return valve(vid, "GlobeValve", tag=tag)

    def finish(self, sheet: Sheet, target: Path) -> None:
        for vid, cls in self.psvs:
            to_safety_valve(sheet, vid, cls)
        sheet.save(target)
        out = Path("build") / f"lists_{self.sheet_id}.json"
        out.parent.mkdir(exist_ok=True)
        out.write_text(json.dumps({"lines": self.lines, "instruments": self.instruments,
                                   "piping_items": self.items}, indent=1), encoding="utf-8")
        for message in sheet.notes:
            if "NominalDiameterStandard" not in message:
                print(f"note: {message}", file=sys.stderr)
        print(f"wrote {target} and {out}")
