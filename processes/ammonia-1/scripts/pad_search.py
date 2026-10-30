"""Provenance (D-033): for every blocked lift, try crane pads beside the item and report the
ones whose lane core's lifting rule finds clear and that stand on open ground (no rack,
structure, building, equipment or low pipe in plan). Writes nothing; prints candidate pads.

cheme run scripts/pad_search.py [SIZE]          search 1..14 m from each side, SIZE m pads
cheme run scripts/pad_search.py why TAG...      the obstacles and lane blockers of 8 m pads N/S/E/W
cheme run scripts/pad_search.py test X0,Y0,X1,Y1 ...   what a given rectangle overlaps

Uses core internals (lifting.study, EngineeringRules._lane) as they are at the S5b commit; it is
a search aid, the gate is `cheme layout lifting`.
"""
import sys
from pathlib import Path

from chemeascode.domains.spatial import lifting
from chemeascode.domains.spatial.engineering_rules import EngineeringRules
from chemeascode.domains.spatial.layout_validate import workspace_layout
from chemeascode.domains.spatial.model import read
from chemeascode.domains.spatial.model_rules import _Rules, declared_view
from chemeascode.foundation.workspace import Workspace

root = Path(".")
ws = Workspace(root)
model = read((root / "layout/plant-model.yaml").read_text())
layout = workspace_layout(ws, None)
eng = EngineeringRules(_Rules(declared_view(model), layout.routing.rules, layout.routing, layout.site_plan))
res = lifting.study(model, layout.routing, layout.site_plan, None)
blocked = [l for l in res.lifts if l.status.startswith("lane blocked")]

obst = []  # plan rectangles a pad may not overlap
for rack in model.get("racks", []):
    pts = rack["points"]
    w = rack["width"] / 2
    for a, b in zip(pts, pts[1:]):
        obst.append(("rack " + rack["id"], (min(a[0], b[0]) - w, min(a[1], b[1]) - w, max(a[0], b[0]) + w, max(a[1], b[1]) + w)))
for kind in ("structures", "buildings"):
    for o in model.get(kind, []):
        if o.get("footprint"):
            f = o["footprint"]
            obst.append((o["id"], (f[0], f[1], f[2], f[3]) if len(f) == 4 else (f[0], f[1], f[3], f[4])))
for e in model.get("equipment", []):
    x0, y0, _, x1, y1, _ = e["bbox"]
    obst.append((e["tag"], (x0, y0, x1, y1)))
for capsule, pipe, _ in eng.base.capsules:
    bb = capsule.aabb
    if bb[2] < 4.0:  # a pipe low enough to be under a crane's outriggers
        obst.append((pipe["id"], (bb[0], bb[1], bb[3], bb[4])))


def overlap(a, b):
    return min(a[2], b[2]) - max(a[0], b[0]) > 0.05 and min(a[3], b[3]) - max(a[1], b[1]) > 0.05


items = {e["tag"]: e for e in model.get("equipment", [])}
if len(sys.argv) > 1 and sys.argv[1] == "test":
    for arg in sys.argv[2:]:
        r = tuple(float(v) for v in arg.split(","))
        zones = [z["id"] for z in model.get("zones", []) if z["kind"] in ("crane_pad", "laydown")
                 for v in z.get("volumes", []) if v.get("shape") == "box"
                 and overlap(r, (v["box"][0], v["box"][1], v["box"][3], v["box"][4]))]
        print(arg, "obstacles:", [n for n, o in obst if overlap(r, o)], "pads/laydowns:", zones)
    sys.exit()
if len(sys.argv) > 1 and sys.argv[1] == "why":
    for tag in sys.argv[2:]:
        x0, y0, _, x1, y1, z1 = items[tag]["bbox"]
        print(tag, "bbox", [round(v, 1) for v in items[tag]["bbox"]])
        for side in "NSEW":
            for gap in (1.0, 5.0):
                s = 8.0
                cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
                c = {"N": (cx, y1 + gap + s / 2), "S": (cx, y0 - gap - s / 2),
                     "E": (x1 + gap + s / 2, cy), "W": (x0 - gap - s / 2, cy)}[side]
                pad = (c[0] - s / 2, c[1] - s / 2, c[0] + s / 2, c[1] + s / 2)
                print(f"  {side} gap {gap}: pad {[round(v,1) for v in pad]} on {sorted(set(n for n, o in obst if overlap(pad, o)))[:6]} lane {sorted(eng._lane(items[tag], pad))[:6]}")
    sys.exit()
size = float(sys.argv[1]) if len(sys.argv) > 1 else 10.0
for lift in blocked:
    tag = lift.tag.split(" ")[0]
    item = items[tag]
    x0, y0, _, x1, y1, _ = item["bbox"]
    found = []
    for gap in (1.0, 2.0, 4.0, 7.0, 10.0, 14.0):
        for side in ("N", "S", "E", "W"):
            for shift in (0.0, -0.5, 0.5):
                cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
                if side == "N":
                    c = (cx + shift * size, y1 + gap + size / 2)
                elif side == "S":
                    c = (cx + shift * size, y0 - gap - size / 2)
                elif side == "E":
                    c = (x1 + gap + size / 2, cy + shift * size)
                else:
                    c = (x0 - gap - size / 2, cy + shift * size)
                pad = (c[0] - size / 2, c[1] - size / 2, c[0] + size / 2, c[1] + size / 2)
                hits = [n for n, r in obst if overlap(pad, r)]
                if hits:
                    continue
                lane = eng._lane(item, pad, low=None)
                if not lane:
                    found.append((gap, side, shift, [round(v, 1) for v in pad]))
        if found:
            break
    minimal = sorted(eng._lane(item, (x0, y0, x1, y1), low=None))
    print(f"{lift.tag}: blockers now {len(lift.blockers)}; over the item itself: {minimal or 'none'}")
    for f in found[:3]:
        print("   candidate", f)
