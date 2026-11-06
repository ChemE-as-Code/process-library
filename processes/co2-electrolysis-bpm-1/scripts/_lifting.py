"""Weights and unit lifts of the two pilot skids (#330, DESIGN.md D-043): regen steps 21 and 23.

Step 21, :func:`item_weights`: the empty weight of every listed item from
layout/lifting-basis.yaml (all ASSUMED: the list's outline volume times a bulk density, a tank's
shell, bottom and flat roof at one wall thickness plus its fittings, or a vendor's weight where
the basis gives one), written by regen into the equipment list's ``dimensions.weight``, where
core's lifting rule and ``cheme layout lifting`` read it.

Step 23, :func:`unit_study`: the lifts core's study cannot express, because it lifts listed
items only and each at its one empty weight: each skid as a 20 ft unit (its items, its frame's
own members and deck grating, the base frame's structure core does not draw, an allowance for
what neither the list nor the model weighs), drained and with its tanks full, and the reservoir
T-101 alone, drained and full. A drained tank keeps its heel: what stands below the highest
point of its drain line (or of its lowest outlet where it has no drain), which gravity cannot
empty. Each lift is worked
out with core's criteria and core's arithmetic (``cheme layout lifting --json``: dynamic factor,
rigging, chart utilisation, clearance, lane margin, crane reach, heavy-lift threshold) on the
committed model: the nearest crane pad within reach whose lane is clear (else the nearest), the
lane from the pad's nearest point over the load to its far side, as wide as the load across the
direction of travel plus the lane margin each side, and the laydown. What the load carries (a
skid's items, in-line items, pipes, frame; a tank's own pipes and supports, disconnected first)
is not in its own lane. A load below ``heavy_lift_t`` that is not a skid, and that the basis does not name a crane lift
(``method: crane``), is moved by hoist or forklift: its
carry lane runs from the laydown over it, and the carry height is the highest top in it plus the
clearance; above the basis's ``carry_limit_m`` the lane is blocked for that method (a crane
lift). Written into layout/lifting-study-units.csv and .md, deterministic.

Core is reached through scripts/_core.py only (the model through its model_* readers, the take-
off's mass per metre of each section through ``cheme assess mto --json``).
"""

from __future__ import annotations

import math
from typing import Any

import _core

BASIS = "layout/lifting-basis.yaml"
UNITS_CSV = "layout/lifting-study-units.csv"
UNITS_MD = "layout/lifting-study-units.md"
COLUMNS = (
    "id",
    "kind",
    "method",
    "items_t",
    "frame_t",
    "allowance_t",
    "contents_t",
    "heel_t",
    "weight_t",
    "gross_t",
    "pad",
    "radius_m",
    "moment_tm",
    "required_t",
    "lift_height_m",
    "hook_height_m",
    "lane",
    "laydown",
    "carry_height_m",
    "status",
)
#: the criteria of core's study this one uses (``cheme layout lifting --json``)
CRITERIA = (
    "heavy_lift_t",
    "crane_reach_m",
    "lane_margin_m",
    "lift_clearance_m",
    "lift_dynamic_factor",
    "lift_rigging_fraction",
    "lift_rigging_height_m",
    "lift_chart_utilisation",
)
_EPS = 1e-6


class BasisError(ValueError):
    """layout/lifting-basis.yaml cannot give what the step needs (regen reports it)."""


# -- step 21: the item weights --------------------------------------------------------------------


def outline_volume_m3(dims: dict[str, Any]) -> float:
    """The list outline's volume: pi/4 D^2 H (or L) of a round item, L W H of a box."""
    if dims.get("diameter") is not None:
        d = float(dims["diameter"])
        return math.pi / 4 * d * d * float(dims.get("height") or dims.get("length"))
    across = dims.get("width") if dims.get("width") is not None else dims.get("depth")
    return float(dims["length"]) * float(across) * float(dims["height"])


def _rules(basis: dict[str, Any]) -> dict[str, tuple[str, dict[str, Any]]]:
    w = basis.get("weights") or {}
    rules: dict[str, tuple[str, dict[str, Any]]] = {}
    for kind, entries in (
        ("bulk", w.get("bulk_density_kg_m3") or []),
        ("tank", w.get("tanks") or []),
        ("vendor", w.get("vendor") or []),
    ):
        for entry in entries:
            for tag in entry.get("tags") or [entry.get("tag")]:
                # a vendor weight replaces an estimate; two estimates for one tag are an error
                if tag in rules and kind != "vendor":
                    raise BasisError(f"{BASIS}: {tag} has two weight rules")
                rules[tag] = (kind, entry)
    return rules


def item_weights(equipment: list[dict[str, Any]], basis: dict[str, Any]) -> dict[str, dict]:
    """Per listed tag: ``weight_t`` (rounded up to ``round_up_kg``), ``kg`` (unrounded) and
    ``basis`` (the arithmetic and its source)."""
    step = float((basis.get("weights") or {}).get("round_up_kg") or 1.0)
    rules = _rules(basis)
    out: dict[str, dict] = {}
    for item in equipment:
        tag = item["tag"]
        dims = item.get("dimensions") or {}
        if tag not in rules:
            raise BasisError(f"{BASIS}: no weight rule for {tag}")
        kind, rule = rules[tag]
        if kind == "vendor":
            kg = float(rule["weight_t"]) * 1000.0
            text = f"vendor {kg:g} kg ({rule.get('source', '')})"
        elif kind == "bulk":
            vol = outline_volume_m3(dims)
            rho = float(rule["value"])
            kg = vol * rho
            text = f"outline {vol:.4g} m3 x {rho:g} kg/m3 = {kg:.1f} kg ({rule['basis']})"
        else:
            d, h = float(dims["diameter"]), float(dims["height"])
            area = math.pi * d * h + 2 * math.pi / 4 * d * d
            rho, wall = float(rule["density_kg_m3"]), float(rule["wall_m"])
            fit = float(rule.get("fittings_fraction") or 0.0)
            kg = area * wall * rho * (1 + fit)
            text = (
                f"shell, bottom and roof {area:.4g} m2 x {wall * 1000:g} mm x {rho:g} kg/m3 x "
                f"(1 + {fit:g}) = {kg:.1f} kg ({rule['basis']})"
            )
        rounded = math.ceil(kg / step - 1e-9) * step
        out[tag] = {"weight_t": round(rounded / 1000.0, 6), "kg": kg, "basis": text}
    return out


def tank_contents_t(dims: dict[str, Any], density_kg_m3: float) -> float:
    """A full tank's contents: its whole outline volume at the contents' density, t."""
    return outline_volume_m3(dims) * density_kg_m3 / 1000.0


# -- step 23: the unit lifts ------------------------------------------------------------------------


def _rect_distance(a: tuple[float, ...], b: tuple[float, ...]) -> float:
    dx = max(a[0] - b[2], b[0] - a[2], 0.0)
    dy = max(a[1] - b[3], b[1] - a[3], 0.0)
    return math.hypot(dx, dy)


def _holds(box: tuple[float, ...], plan: tuple[float, ...]) -> bool:
    have = sorted((box[2] - box[0], box[3] - box[1]))
    need = sorted((plan[2] - plan[0], plan[3] - plan[1]))
    return have[0] >= need[0] - _EPS and have[1] >= need[1] - _EPS


def lane(origin: tuple[float, ...], load: tuple[float, ...], margin: float) -> dict[str, Any]:
    """Core's crane lane in plan (EngineeringRules._lane): from the origin's point nearest the
    load's centre over the load to its far side, the load's width across the travel plus the
    margin each side. A rectangle {centre, length, width, angle_deg}."""
    x0, y0, x1, y1 = load
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    px = min(max(cx, origin[0]), origin[2])
    py = min(max(cy, origin[1]), origin[3])
    length = math.hypot(cx - px, cy - py)
    angle = 0.0 if length < 1e-6 else math.atan2(cy - py, cx - px)
    ux, uy = math.cos(angle), math.sin(angle)
    ex, ey = (x1 - x0) / 2, (y1 - y0) / 2
    along = abs(ux) * ex + abs(uy) * ey
    across = abs(uy) * ex + abs(ux) * ey
    total = length + along
    return {
        "centre": (px + ux * total / 2, py + uy * total / 2),
        "length": total,
        "width": 2 * across + 2 * margin,
        "angle": angle,
    }


def _meets(rect: dict[str, Any], box: list[float]) -> bool:
    """An oriented rectangle against an axis-aligned plan box (separating axes); a box of no
    width (a vertical member's plan, a straight run along an axis) meets it when it lies inside
    it on that axis."""
    cx, cy = rect["centre"]
    ux, uy = math.cos(rect["angle"]), math.sin(rect["angle"])
    hl, hw = rect["length"] / 2, rect["width"] / 2
    corners = [
        (cx + sl * hl * ux - sw * hw * uy, cy + sl * hl * uy + sw * hw * ux)
        for sl in (-1, 1)
        for sw in (-1, 1)
    ]
    bx = [(box[0], box[1]), (box[2], box[1]), (box[2], box[3]), (box[0], box[3])]
    for ax, ay in ((1.0, 0.0), (0.0, 1.0), (ux, uy), (-uy, ux)):
        a = [px * ax + py * ay for px, py in corners]
        b = [px * ax + py * ay for px, py in bx]
        if max(b) <= min(a) + _EPS or max(a) <= min(b) + _EPS:
            return False
    return True


def _group(owner: str) -> str:
    """A solid's owner as reported: a rack or frame by its id, a pipe or item by its own."""
    head = owner.split("/")[0]
    return head if head.startswith(("PR-", "SKID-")) else owner


def _in_lane(solids, own, rect) -> dict[str, float]:
    tops: dict[str, float] = {}
    for s in solids:
        if own(s) or not _meets(rect, s["plan"]):
            continue
        name = _group(s["owner"])
        tops[name] = max(tops.get(name, -math.inf), float(s["z"][1]))
    return tops


def _num(x: float | None) -> str:
    return "" if x is None else format(round(float(x), 3), "g")


def _section_masses(take_off: dict[str, Any]) -> dict[str, float]:
    """kg per metre of each steel section from the take-off (frame members first)."""
    out: dict[str, float] = {}
    rows = [r for r in take_off["rows"] if r.get("category") == "steel" and r.get("length_m")]
    for row in sorted(rows, key=lambda r: r.get("group") != "structure"):
        out.setdefault(row["item"], float(row["quantity"]) * 1000.0 / float(row["length_m"]))
    return out


def heel(model: dict[str, Any], tag: str, entry: dict[str, Any], density_kg_m3: float) -> dict[str, Any]:
    """A drained tank's heel: the liquid below the drain's highest point (its drain line's
    centreline, the line rising to its coupling included, or the named outlet nozzle), which
    gravity cannot empty; ``level_m`` above the tank floor (clipped to the tank), t."""
    item = next(e for e in model.get("equipment") or [] if e["tag"] == tag)
    dims = item.get("dimensions") or {}
    floor, top = float(item["bbox"][2]), float(item["bbox"][5])
    if entry.get("drain_line"):
        zs = [float(pt[2]) for p in model.get("pipes") or [] if p.get("line") == entry["drain_line"] for pt in p["points"]]
        if not zs:
            raise BasisError(f"{BASIS}: heel of {tag}: no routed pipe of {entry['drain_line']} in the model")
        z, how = max(zs), f"the highest point of {entry['drain_line']}"
    else:
        noz = next((n for n in item.get("nozzles") or [] if n.get("name") == entry.get("nozzle")), None)
        if noz is None:
            raise BasisError(f"{BASIS}: heel of {tag}: no nozzle {entry.get('nozzle')} in the model")
        z, how = float(noz["point"][2]), f"its outlet {entry['nozzle']}"
    level = min(max(z - floor, 0.0), top - floor)
    d = float(dims["diameter"])
    volume = math.pi / 4 * d * d * level
    return {"tag": tag, "level_m": level, "how": how, "volume_m3": volume, "t": volume * density_kg_m3 / 1000.0, "basis": entry.get("basis", "")}


def _frame_mass(model, frame_id, masses, grating_kg_m2) -> tuple[float, float, list[str]]:
    """The frame's own members (not its access steps) and deck grating, t."""
    entry = next(s for s in model.get("structures") or [] if s.get("id") == frame_id)
    steel_kg, grating_m2, unknown = 0.0, 0.0, []
    for part in entry.get("parts") or []:
        if part.get("kind") == "member" and part.get("material") in ("steel", "handrail"):
            a, b = part["start"], part["end"]
            length = math.dist(a, b)
            section = part.get("section")
            if section not in masses:
                unknown.append(str(section))
                continue
            steel_kg += length * masses[section]
        elif part.get("kind") == "box" and part.get("material") == "grating":
            grating_m2 += float(part["size"][0]) * float(part["size"][1])
    return steel_kg / 1000.0, grating_m2 * grating_kg_m2 / 1000.0, sorted(set(unknown))


def unit_study(
    model: dict[str, Any],
    basis: dict[str, Any],
    criteria: dict[str, Any],
    take_off: dict[str, Any],
    densities: dict[str, float],
) -> dict[str, Any]:
    """The unit lifts (module text): rows (COLUMNS), each lift's weight build-up, findings."""
    c = {name: float(criteria[name]["value"]) for name in CRITERIA}
    units = basis.get("units") or {}
    grating_kg_m2 = float(units.get("grating_kg_m2") or 0.0)
    base_kg_m2 = float(units.get("base_frame_kg_m2") or 0.0)
    allowance = float(units.get("allowance_fraction") or 0.0)
    carry_limit = units.get("carry_limit_m")
    heel_basis = {h["tag"]: h for h in units.get("heels") or []}
    masses = _section_masses(take_off)
    solids = _core.model_solids(model)
    pads, laydowns = [], []
    for zone in model.get("zones") or []:
        for volume in zone.get("volumes") or []:
            if volume.get("shape") != "box":
                continue
            x0, y0, _, x1, y1, _ = volume["box"]
            if zone["kind"] == "crane_pad":
                pads.append((zone["id"], (x0, y0, x1, y1), zone.get("reach_m") or c["crane_reach_m"]))
            elif zone["kind"] == "laydown":
                laydowns.append((zone["id"], (x0, y0, x1, y1)))
    equipment = {e["tag"]: e for e in model.get("equipment") or []}
    rows, build, findings, heels = [], [], [], []
    for lift in units.get("lifts") or []:
        lid, kind = lift["id"], lift["kind"]
        contents = 0.0
        full = set(lift.get("full") or [])
        for tag in sorted(full):
            if tag not in densities:
                raise BasisError(f"{BASIS}: no contents density for {tag}")
            contents += tank_contents_t(equipment[tag]["dimensions"], densities[tag])
        on_lift = (
            {i["tag"] for i in _core.model_items_on(model, lift["frame"])} if kind == "skid" else {lift["tag"]}
        )
        heel_t = 0.0
        for tag in sorted(t for t in on_lift if t in heel_basis and t not in full):
            if tag not in densities:
                raise BasisError(f"{BASIS}: no contents density for the heel of {tag}")
            h = heel(model, tag, heel_basis[tag], densities[tag])
            heel_t += h["t"]
            heels.append({"lift": lid, **h})
        frame_t = allowance_t = 0.0
        if kind == "skid":
            frame = lift["frame"]
            items = _core.model_items_on(model, frame)
            tags = {i["tag"] for i in items}
            inline = {x["tag"] for x in _core.model_inline_of(model, f"pid/{lift['sheet']}.xml")}
            inline |= {x["id"] for x in _core.model_inline_of(model, f"pid/{lift['sheet']}.xml")}
            fp = _core.model_structure(model, frame)["footprint"]
            trays = {t["id"] for t in model.get("trays") or []}

            steps = f"{frame}/ST-"

            def over(p, fp=fp):
                return p[0] < fp[2] - _EPS and p[2] > fp[0] + _EPS and p[1] < fp[3] - _EPS and p[3] > fp[1] + _EPS

            def off(s, trays=trays, steps=steps, over=over):
                # a run of a cable tray over the frame: site-fitted above the envelope (D-045),
                # its cables disconnected at the frame edge and the run taken off before the unit
                # lift (the trays come in from the rack north of the skids, D-047); the access
                # steps beside the frame travel loose (layout/lifting-basis.yaml)
                return s["owner"].startswith(steps) or (s["owner"] in trays and over(s["plan"]))

            def own(s, tags=tags, inline=inline, frame=frame, sheet=lift["sheet"], off=off, over=over):
                # the frame, its items, its in-line items and the sheet's pipes over the frame (a
                # pipe of an item off the frame, the oxidiser's flue, stays: D-047)
                return (
                    s["owner"] in tags
                    or s["owner"] in inline
                    or s["owner"].startswith(f"{frame}/")
                    or (s["owner"].startswith(f"{sheet}/") and over(s["plan"]))
                    or off(s)
                )

            mine = [s for s in solids if own(s) and not off(s)]
            plan = (
                min([fp[0]] + [s["plan"][0] for s in mine]),
                min([fp[1]] + [s["plan"][1] for s in mine]),
                max([fp[2]] + [s["plan"][2] for s in mine]),
                max([fp[3]] + [s["plan"][3] for s in mine]),
            )
            z0, z1 = 0.0, max(s["z"][1] for s in mine)
            missing = sorted(t for t in tags if (equipment[t].get("dimensions") or {}).get("weight") is None)
            if missing:
                findings.append(f"{lid}: no weight in the equipment list for {', '.join(missing)}")
            items_t = sum(float((equipment[t].get("dimensions") or {}).get("weight") or 0.0) for t in tags)
            steel_t, grating_t, unknown = _frame_mass(model, frame, masses, grating_kg_m2)
            if unknown:
                findings.append(f"{lid}: no mass per metre in the take-off for {', '.join(unknown)}")
            # the base frame's structure core does not draw (cross-members, grating bearers,
            # lifting lugs or corner fittings), per m2 of the frame's footprint; not in the
            # allowance's base (the allowance is for what the items and the drawn frame carry)
            base_t = base_kg_m2 * (fp[2] - fp[0]) * (fp[3] - fp[1]) / 1000.0
            allowance_t = allowance * (items_t + steel_t + grating_t)
            frame_t = steel_t + grating_t + base_t
            build.append(
                {
                    "id": lid,
                    "items": len(tags),
                    "items_t": items_t,
                    "steel_t": steel_t,
                    "grating_t": grating_t,
                    "base_t": base_t,
                    "allowance_t": allowance_t,
                    "contents_t": contents,
                    "heel_t": heel_t,
                    "plan": plan,
                    "height_m": z1 - z0,
                }
            )
        else:
            tag = lift["tag"]
            item = equipment[tag]
            ends = {
                p["id"]
                for p in model.get("pipes") or []
                if any(str(e.get("ref", "")).startswith(f"{tag}/") for e in p.get("ends") or [])
            }

            # the tank's own pipes and their supports (SP-* of the pipe) go out with it; what
            # the basis names off_first (a site-fitted tray branch over the lane) is taken off
            # before the lift
            first = set(lift.get("off_first") or [])

            def own(s, tag=tag, ends=ends, first=first):
                owner = s["owner"]
                return owner == tag or owner in ends or owner.rsplit("/", 1)[0] in ends or owner in first

            x0, y0, z0, x1, y1, z1 = (float(v) for v in item["bbox"])
            plan = (x0, y0, x1, y1)
            items_t = float((item.get("dimensions") or {}).get("weight") or 0.0)
            if not items_t:
                findings.append(f"{lid}: no weight in the equipment list for {tag}")
        weight = items_t + frame_t + allowance_t + contents + heel_t
        # a skid, a load of heavy_lift_t or more, or a lift the basis names a crane lift
        # (T-101 from the crane hardstanding to the road, D-047)
        crane = kind == "skid" or weight >= c["heavy_lift_t"] - 1e-9 or lift.get("method") == "crane"
        row = {k: "" for k in COLUMNS}
        row.update(
            id=lid,
            kind=kind,
            items_t=_num(items_t),
            frame_t=_num(frame_t) if kind == "skid" else "",
            allowance_t=_num(allowance_t) if kind == "skid" else "",
            contents_t=_num(contents) if contents else "",
            heel_t=_num(heel_t) if heel_t else "",
            weight_t=_num(weight),
        )
        status = [] if lift.get("permitted", True) else ["not permitted (drain first)"]
        if crane:
            gross = weight * c["lift_dynamic_factor"] * (1 + c["lift_rigging_fraction"])
            row["method"] = "mobile crane" + (" (unit lift)" if kind == "skid" else "")
            near = sorted(
                (_rect_distance(rect, plan), pid, rect, reach)
                for pid, rect, reach in pads
                if _rect_distance(rect, plan) <= reach + _EPS
            )
            if not near:
                status.append("no crane pad")
            else:
                low = z1 + c["lift_clearance_m"]
                lanes = []
                for _, pid, rect, reach in near:
                    tops = _in_lane(solids, own, lane(rect, plan, c["lane_margin_m"]))
                    blockers = sorted(n for n, t in tops.items() if t > low + _EPS)
                    lanes.append((pid, rect, reach, tops, blockers))
                pid, rect, reach, tops, blockers = next((x for x in lanes if not x[4]), lanes[0])
                pcx, pcy = (rect[0] + rect[2]) / 2, (rect[1] + rect[3]) / 2
                radius = math.hypot((plan[0] + plan[2]) / 2 - pcx, (plan[1] + plan[3]) / 2 - pcy)
                lift_h = max(max(tops.values(), default=0.0) + c["lift_clearance_m"], z0)
                row.update(
                    gross_t=_num(gross),
                    pad=pid,
                    radius_m=_num(radius),
                    moment_tm=_num(gross * radius),
                    required_t=_num(gross / c["lift_chart_utilisation"]),
                    lift_height_m=_num(lift_h),
                    hook_height_m=_num(lift_h + (z1 - z0) + c["lift_rigging_height_m"]),
                    lane=" ".join(blockers) if blockers else "clear",
                )
                status.append("lane blocked" if blockers else "lane clear")
                fits = [
                    (round(_rect_distance(box, rect), 3), lid_, box)
                    for lid_, box in laydowns
                    if _rect_distance(box, rect) <= reach + _EPS and _holds(box, plan)
                ]
                wanted = lift.get("laydown")
                if wanted:
                    fits = [f for f in fits if f[1] == wanted]
                if fits:
                    row["laydown"] = min(fits)[1]
                else:
                    status.append("no laydown")
        else:
            row["method"] = "hoist or forklift (below heavy_lift_t)"
            fits = [(lid_, box) for lid_, box in laydowns if _holds(box, plan)]
            wanted = lift.get("laydown")
            if wanted:
                fits = [f for f in fits if f[0] == wanted]
            if not fits:
                status.append("no laydown")
            else:
                ld, box = min(fits, key=lambda f: (_rect_distance(f[1], plan), f[0]))
                tops = _in_lane(solids, own, lane(box, plan, c["lane_margin_m"]))
                carry = max(max(tops.values(), default=0.0) + c["lift_clearance_m"], z0)
                highest = sorted(tops.items(), key=lambda kv: (-kv[1], kv[0]))[:3]
                row.update(
                    laydown=ld,
                    carry_height_m=_num(carry),
                    lane=" ".join(f"{n} {_num(t)}" for n, t in highest) if highest else "clear",
                )
                if carry_limit is not None and carry > float(carry_limit) + _EPS:
                    status.append(
                        f"lane blocked: carry {_num(carry)} m above the hoist or forklift limit "
                        f"{_num(float(carry_limit))} m (a crane lift)"
                    )
                else:
                    status.append(f"carried to {ld} over {_num(carry)} m")
        row["status"] = ", ".join(status)
        rows.append(row)
    return {"rows": rows, "build": build, "heels": heels, "criteria": c, "findings": findings}


def study_csv(result: dict[str, Any]) -> str:
    lines = [",".join(COLUMNS)]
    for row in result["rows"]:
        cells = []
        for k in COLUMNS:
            v = str(row[k])
            cells.append(f'"{v}"' if "," in v else v)
        lines.append(",".join(cells))
    return "\n".join(lines) + "\n"


def study_markdown(
    result: dict[str, Any],
    basis: dict[str, Any],
    weights: dict[str, dict],
    criteria: dict[str, Any],
    model_sha256: str,
    duration_h: float,
) -> str:
    titles = {lift["id"]: lift["title"] for lift in (basis.get("units") or {}).get("lifts") or []}
    units = basis.get("units") or {}
    out = [
        "# Lifting study: the skids as units and T-101 full and empty",
        "",
        "Generated by `scripts/regen.py` step 23 (`scripts/_lifting.py`, DESIGN.md D-043) from "
        f"`layout/plant-model.yaml` (model output_sha256 `{model_sha256}`) and "
        f"`{BASIS}`, for the {duration_h:,.0f} h campaign. It completes core's "
        "`layout/lifting-study.md` (`cheme layout lifting`), which lifts listed items only, each "
        "at its one empty weight: here each skid is lifted as a 20 ft unit and the reservoir "
        "T-101 alone, drained and full, with core's criteria (below) and core's arithmetic: "
        "gross load = weight x dynamic factor x (1 + rigging fraction); capacity needed = gross "
        "/ chart utilisation; radius from the pad's centre to the load's centre; lift height = "
        "highest top in the lane + clearance; hook height = lift height + load height + rigging "
        "height. The lane runs from the pad's nearest point over the load to its far side, the "
        "load's width across the travel plus the lane margin each side; what the load carries "
        "(a skid's items, in-line items, pipes and frame; a tank's own pipes and their "
        "supports, disconnected first) is not in its own lane, nor are the runs of the cable "
        "trays over a skid's frame, taken off before its unit lift (site-fitted above the "
        "envelope, DESIGN.md D-045; the runs between the rack and the frame stay) or a tray "
        "branch the basis names `off_first` for an item's lift (swung off first, D-047), and anything else in it higher "
        "than the load's top "
        "plus the clearance blocks it. A load below `heavy_lift_t` that is not a skid is moved "
        "by hoist or forklift to its laydown: the carry height is the highest top in the lane "
        "from the laydown over it plus the clearance (the three highest in the lane column); "
        f"above {_num(units.get('carry_limit_m'))} m the lane is blocked for that method "
        f"({units.get('carry_limit_basis', '')}).",
        "",
        "Every weight is ASSUMED (no vendor weight exists): see the build-up below. A lift "
        "marked not permitted is the bound of a lift that is not made: a tank is drained "
        "before it or its skid is moved. A drained tank keeps its heel (below), which is in "
        "the drained lifts' weight.",
        "",
        "| lift | method | weight t | gross t | pad | radius m | moment t m | needed t | lift "
        "height m | hook height m | lane | laydown | carry height m | status |",
        "|---|---|---:|---:|---|---:|---:|---:|---:|---:|---|---|---:|---|",
    ]
    for r in result["rows"]:
        out.append(
            f"| {r['id']}: {titles.get(r['id'], '')} | {r['method']} | {r['weight_t']} | "
            f"{r['gross_t']} | {r['pad']} | {r['radius_m']} | {r['moment_tm']} | "
            f"{r['required_t']} | {r['lift_height_m']} | {r['hook_height_m']} | {r['lane']} | "
            f"{r['laydown']} | {r['carry_height_m']} | {r['status']} |"
        )
    out += [
        "",
        "## Weight build-up of the unit lifts (ASSUMED)",
        "",
        f"Items: the equipment list's `dimensions.weight` (regen step 21, table below). Frame: "
        f"the frame's own members at core's take-off mass per metre of each section "
        f"(`estimate/mto.csv`; the access steps ST-x1 and ST-x2 stand on grade and travel "
        f"loose) and its deck grating at {units.get('grating_kg_m2'):g} kg/m2 (ASSUMED): core "
        f"draws only the frame's perimeter members, corner posts and guard rail, so the drawn "
        f"frame steel is not the skid's structure (its guard rail, which the design deletes on "
        f"the 0.15 m deck, D-047, is kept in the weight as a margin). Base frame: "
        f"{units.get('base_frame_kg_m2'):g} kg/m2 of the frame's footprint, "
        f"{units.get('base_frame_basis', '')}. Allowance: {units.get('allowance_basis', '')} "
        f"(on the items, the drawn frame steel and the grating). Heel: what a drained tank keeps "
        f"(below).",
        "",
        "| lift | items | items t | drawn frame steel t | deck grating t | base frame (not drawn) t "
        "| allowance t | contents t | heel t | total t | plan m | height m |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|---:|",
    ]
    for b in result["build"]:
        x0, y0, x1, y1 = b["plan"]
        total = (
            b["items_t"] + b["steel_t"] + b["grating_t"] + b["base_t"] + b["allowance_t"]
            + b["contents_t"] + b["heel_t"]
        )
        out.append(
            f"| {b['id']} | {b['items']} | {_num(b['items_t'])} | {_num(b['steel_t'])} | "
            f"{_num(b['grating_t'])} | {_num(b['base_t'])} | {_num(b['allowance_t'])} | "
            f"{_num(b['contents_t'])} | {_num(b['heel_t'])} | "
            f"{_num(total)} | {_num(x1 - x0)} x {_num(y1 - y0)} | {_num(b['height_m'])} |"
        )
    out += [
        "",
        "## Heels of the drained tanks (ASSUMED)",
        "",
        "A drained tank empties by gravity only down to the highest point of its drain line (a "
        "line that rises to its hose coupling keeps the tank full to that level) or, with no "
        "drain, to its lowest outlet; what stands below stays in the tank and is lifted with "
        "it. Each tank's bottom outlet with its capped camlock pump-out (P&ID revision B, "
        "DESIGN.md D-055) empties the heel at the end of a run; the drained lifts do not "
        "credit it, so the heel by gravity stays in their weight as a margin.",
        "",
        "| lift | tank | drains to | level above the floor m | volume m3 | heel t | basis |",
        "|---|---|---|---:|---:|---:|---|",
    ]
    for h in result.get("heels") or []:
        out.append(
            f"| {h['lift']} | {h['tag']} | {h['how']} | {_num(h['level_m'])} | "
            f"{_num(h['volume_m3'])} | {_num(h['t'])} | {h['basis']} |"
        )
    contents = basis.get("contents") or []
    out += [
        "",
        "A full tank holds its whole outline volume (pi/4 D^2 H, the working volume with its "
        "freeboard) at the density of its contents: "
        + "; ".join(f"{e['tag']} {e['basis']}" for e in contents)
        + ".",
        "",
        "## Item weights (regen step 21, written into equipment/equipment-list.yaml)",
        "",
        "| tag | weight t | basis |",
        "|---|---:|---|",
    ]
    for tag in sorted(weights):
        out.append(f"| {tag} | {_num(weights[tag]['weight_t'])} | {weights[tag]['basis']} |")
    out += ["", "## Criteria (core's, `cheme layout lifting --json`)", ""]
    for name in CRITERIA:
        entry = criteria[name]
        out.append(f"- `{name}` {format(float(entry['value']), 'g')}: {entry['basis']}")
    out += [
        "",
        "Not covered: the crane's choice (no load chart: `layout/crane-chart.yaml`), outrigger "
        "spread and ground bearing on the hardstanding (CP-x, sized but not designed, D-047), "
        "the rigging and the skid's lifting points (a 20 ft frame lifted at its corner castings "
        "or lugs, the fabricator's), slewing clearances, wind and the road closure: the "
        "lifting plan (competent person, crane contractor).",
        "",
    ]
    for f in result["findings"]:
        out.append(f"Finding: {f}")
    if result["findings"]:
        out.append("")
    return "\n".join(out)


def summary(result: dict[str, Any]) -> list[dict[str, Any]]:
    """The rows the calculation record keeps (results/scenarios/<H>h/record.json)."""
    keep = ("id", "method", "weight_t", "heel_t", "pad", "required_t", "hook_height_m", "lane",
            "laydown", "carry_height_m", "status")  # fmt: skip
    return [{k: r[k] for k in keep} for r in result["rows"]]
