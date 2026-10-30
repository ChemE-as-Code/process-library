"""Main dimensions of the ammonia-1 datasheets that the detail gate `datasheets` asks for (S5c,
DESIGN.md D-043).

Run with `cheme run scripts/datasheet_dimensions.py`. Provenance only, like
scripts/complete_datasheets.py (D-032): it writes into equipment/datasheets/*.yaml only the main
dimensions a sheet does not give yet, never over a value already there, each with its source;
assumptions are marked `assumed: true`, values awaited from a vendor or licensor are `supplier`
markers with what is awaited, and fields that do not apply are `not_applicable` with the reason.

- shell-and-tube exchangers with an area on the sheet (`cheme datasheets fill` from the simulated
  duty, D-032): tubes 19.05 mm OD, 6.096 m long, 2 passes on a 1.25 x OD triangular pitch
  (ASSUMED standard choices); tube count = area / (pi OD L); bundle diameter from the tube count
  with the constants K1 = 0.249, n1 = 2.207 for that pitch and 2 passes (Sinnott, Coulson and
  Richardson's Chemical Engineering Vol. 6, 4th ed., 2005, section 12.5.4, eq. 12.3b and
  Table 12.4); shell ID = bundle + 20 mm clearance (ASSUMED, fixed tube sheet); above a 2.5 m
  shell (ASSUMED limit) the area is split over identical shells in parallel;
- exchangers whose area is awaited (multi-stream nodes, D-032), the convection coils in the
  furnace duct (E-101..E-104, E-106, E-107: the furnace vendor's coil design, no shell), the
  reformer catalyst tubes R-101 (licensor) and the plate pack E-301: supplier / not_applicable;
- vessels and columns: 2:1 ellipsoidal heads (ASSUMED), a skirt for vertical and two saddles for
  horizontal vessels (ASSUMED); the columns' packed section between a 2 m sump and 3 m top
  disengagement (ASSUMED); packages U-801, X-401, X-601: not_applicable (several items, the
  envelope is given);
- machines: baseplate and shaft height are the vendor's general arrangement (supplier).
"""

import math
from pathlib import Path

import yaml

DS = Path("equipment/datasheets")
D043 = "DESIGN.md D-043"
COILS = {"E-101", "E-102", "E-103", "E-104", "E-106", "E-107"}
PACKAGES = {"U-801": "steam system package (D-015)", "X-401": "dryer package, two adsorbers and regeneration (D-010)",
            "X-601": "purge gas recovery package: NH3 wash and cold box (D-013)"}
TUBE_OD, TUBE_L, PASSES = 0.01905, 6.096, 2
K1, N1, CLEAR, MAX_SHELL = 0.249, 2.207, 0.020, 2.5
SINNOTT = ("Sinnott, Coulson and Richardson's Chemical Engineering Vol. 6, 4th ed. (2005), section 12.5.4, "
           "eq. 12.3b, Table 12.4 (triangular pitch 1.25 OD, 2 passes: K1 0.249, n1 2.207)")


def q(value, unit, source, assumed=False):
    out = {"value": value, "unit": unit, "source": source}
    if assumed:
        out["assumed"] = True
    return out


def marker(kind, reason):
    return {"value": kind, "reason": reason, "source": D043}


def given(v):
    return v not in (None, [], {}) and not (isinstance(v, dict) and v.get("value") in (None, "TBD"))


def area_of(d):
    a = (d.get("type_specific") or {}).get("area_m2")
    v = a.get("value") if isinstance(a, dict) else a
    return v if isinstance(v, (int, float)) else None


def shell_tube(tag, d, dims):
    tubes = dims.setdefault("tubes", {}) or {}
    dims["tubes"] = tubes
    area = area_of(d)
    if tag in COILS:
        why = "convection coil bank in the H-101 flue-gas duct: the furnace vendor's coil design (tubes, fins, rows)"
        dims.setdefault("inside_diameter", marker("not_applicable", "a coil bank in the convection duct has no shell"))
        for k in ("length", "count", "outside_diameter", "passes"):
            tubes.setdefault(k, marker("supplier", why))
        return "coil"
    if tag == "R-101":
        dims.setdefault("inside_diameter", marker("not_applicable", "the catalyst tubes hang in the H-101 radiant box; there is no shell"))
        for k in ("length", "count", "outside_diameter", "passes"):
            tubes.setdefault(k, marker("supplier", "reformer tube design (count, bore, heated length) by the licensor or furnace vendor"))
        return "licensor"
    if area is None:
        why = "the heat transfer area is awaited (multi-stream node, not calculated by cheme datasheets fill, D-032); the thermal design follows it"
        dims.setdefault("inside_diameter", marker("supplier", why))
        for k in ("length", "count", "outside_diameter", "passes"):
            tubes.setdefault(k, marker("supplier", why))
        return "supplier"
    n_total = math.ceil(area / (math.pi * TUBE_OD * TUBE_L))
    shells = 1
    while True:
        n = math.ceil(n_total / shells)
        bundle = TUBE_OD * (n / K1) ** (1 / N1)
        if bundle + CLEAR <= MAX_SHELL:
            break
        shells += 1
    ident = round(bundle + CLEAR, 2)
    split = f"; {shells} identical shells in parallel (each above {MAX_SHELL} m otherwise, ASSUMED limit)" if shells > 1 else ""
    basis = f"area {area:g} m2 from the datasheet (cheme datasheets fill, D-032)"
    dims.setdefault("inside_diameter", q(ident, "m", f"bundle diameter {bundle:.2f} m for {n} tubes per shell ({SINNOTT}) + {CLEAR * 1000:.0f} mm clearance (ASSUMED, fixed tube sheet); {basis}{split}; {D043}", True))
    if shells > 1:
        dims.setdefault("shell_passes", q(1, "", f"one shell pass per shell; {shells} shells in parallel; {D043}", True))
    tubes.setdefault("outside_diameter", q(TUBE_OD * 1000, "mm", f"3/4 in tube, a standard size (ASSUMED); {D043}", True))
    tubes.setdefault("length", q(TUBE_L, "m", f"20 ft tube, a standard length (ASSUMED); {D043}", True))
    tubes.setdefault("passes", q(PASSES, "", f"two tube passes (ASSUMED); {D043}", True))
    tubes.setdefault("pitch", q(round(1.25 * TUBE_OD * 1000, 2), "mm", f"triangular, 1.25 x OD (ASSUMED); {D043}", True))
    tubes.setdefault("count", q(n, "", f"{n_total} tubes = area / (pi x OD x length), {basis}{split}; per shell; {D043}"))
    return f"computed ({shells} shell{'s' if shells > 1 else ''}, ID {ident} m, {n} tubes each)"


def vessel(tag, d, dims, column=False):
    if tag in PACKAGES:
        why = f"{PACKAGES[tag]}: several items, its main dimensions are the package envelope (overall length, width, height)"
        for k in ("inside_diameter", "tangent_length", "head"):
            dims.setdefault(k, marker("not_applicable", why))
        dims.setdefault("support", {})
        dims["support"] = dims["support"] or {}
        dims["support"].setdefault("type", marker("not_applicable", why))
        return "package"
    dims.setdefault("head", q("ellipsoidal_2_1", "", f"2:1 ellipsoidal heads, the usual head of a pressure vessel (ASSUMED); {D043}", True))
    sup = dims.get("support") or {}
    dims["support"] = sup
    horizontal = dims.get("orientation") == "horizontal"
    if horizontal:
        sup.setdefault("type", q("saddles", "", f"horizontal vessel on two saddles (ASSUMED); {D043}", True))
        sup.setdefault("count", q(2, "", f"two saddles (ASSUMED); {D043}", True))
    else:
        sup.setdefault("type", q("skirt", "", f"vertical vessel on a skirt (ASSUMED); {D043}", True))
    if column and not dims.get("sections"):
        tl = dims.get("tangent_length")
        tl = tl.get("value") if isinstance(tl, dict) else tl
        sid = "absorption" if tag == "C-301" else "stripping"
        dims["sections"] = [{
            "id": sid,
            "internals": "packing (random or structured), the supplier's design for the aMDEA duty (D-009, ASSUMED)",
            "bottom": 2.0,
            "height": round(tl - 5.0, 2),
            "count": 1,
            "notes": f"one packed section between a 2 m sump and 3 m top disengagement (ASSUMED) on the tangent length {tl} m; {D043}",
        }]
    return "vessel"


def machine(tag, d, dims):
    why = "the vendor's general arrangement drawing (baseplate and shaft centre height)"
    base = dims.get("baseplate") or {}
    dims["baseplate"] = base
    base.setdefault("length", marker("supplier", why))
    base.setdefault("width", marker("supplier", why))
    dims.setdefault("shaft_height", marker("supplier", why))
    return "machine"


def main():
    from chemeascode.domains.equipment.outline import kind_of

    for path in sorted(DS.glob("*.yaml")):
        text = path.read_text()
        header = "".join(l + "\n" for l in text.splitlines() if l.startswith("#"))
        d = yaml.safe_load(text)
        tag, kind = d["tag"], kind_of(d["type"])
        dims = d.get("dimensions") or {}
        d["dimensions"] = dims
        if kind == "shell_tube":
            what = shell_tube(tag, d, dims)
        elif kind == "plate":
            plates = dims.get("plates") or {}
            dims["plates"] = plates
            for k in ("height", "width", "count"):
                plates.setdefault(k, marker("supplier", "plate pack by the vendor; the area is awaited (D-032)"))
            what = "supplier"
        elif kind in ("vessel", "column", "tank"):
            what = vessel(tag, d, dims, column=kind == "column")
        elif kind == "machine":
            what = machine(tag, d, dims)
        else:
            print(f"{tag}: {kind}, nothing to add")
            continue
        path.write_text(header + yaml.safe_dump(d, sort_keys=False, allow_unicode=True, width=100))
        print(f"{tag}: {kind}, {what}")


if __name__ == "__main__":
    main()
