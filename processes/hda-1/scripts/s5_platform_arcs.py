"""Provenance (S5, D-027): free arcs for the ring platforms of the vertical items.

For every platform `cheme layout build` proposed (or the placement declares), find the angles
around the item where a pipe runs over the platform's walkway lower than the access headroom
(2.1 m, the package's ASSUMED criterion): the same test as core's `layout-headroom` rule
(horizontal runs only; the first and last run at the item a pipe connects to are left out).
Print, per item, the platforms as an `access:` entry for layout/equipment-placement.yaml with
the arc cut to the largest free part of the proposal's arc that still holds the nozzles it
serves; a platform with no such free part is printed as dropped, with the reason. Writes
nothing; the declarations are reviewed and pasted by hand.

python scripts/s5_platform_arcs.py [TAG ...]
"""

import math
import sys

import yaml

HEADROOM = 2.1
ABOVE = 0.05
MARGIN_DEG = 6.0
MIN_ARC = 40.0


def norm(a):
    return a % 360.0


def in_arc(a, arc):
    a0, a1 = arc
    span = (a1 - a0) % 360 or 360.0
    return (a - a0) % 360 <= span


def main() -> None:
    model = yaml.safe_load(open("layout/plant-model.yaml", encoding="utf-8"))
    only = set(sys.argv[1:])
    items = {e["tag"]: e for e in model["equipment"]}
    nozzle_pts = {}
    for e in model["equipment"]:
        for n in e.get("nozzles", []):
            nozzle_pts[n["id"]] = n["point"]
    plats = {}
    for p in model.get("platforms", []):
        if p.get("kind") != "circular":
            continue
        plats.setdefault(p["tag"], []).append(p)
    for tag, ps in sorted(plats.items()):
        if only and tag not in only:
            continue
        e = items[tag]
        cx, cy = e["position"][0], e["position"][1]
        out = []
        for p in sorted(ps, key=lambda q: q["elevation"]):
            g = [part for part in p["parts"] if part.get("kind") == "annulus"][0]
            r0, r1 = g["radius"], g["radius_end"]
            z = p["elevation"]
            blocked = []
            for pipe in model["pipes"]:
                pts = pipe["points"]
                od = (pipe.get("od") or 0.1) + 2 * (pipe.get("insulation_mm") or 0) / 1000
                r = od / 2
                n = len(pts) - 1
                # ends at this item: the first/last run is exempt
                ends = pipe.get("ends") or []
                at_item = set()
                for k, end in enumerate(ends[:2] if isinstance(ends, list) else []):
                    ref = str(end.get("ref", "")) if isinstance(end, dict) else str(end)
                    if ref.startswith(tag + "/") or ref == tag:
                        at_item.add(k)
                for k in range(n):
                    if (k == 0 and 0 in at_item) or (k == n - 1 and 1 in at_item):
                        continue
                    a, b = pts[k], pts[k + 1]
                    if math.hypot(b[0] - a[0], b[1] - a[1]) < 1e-6:
                        continue
                    steps = max(1, math.ceil(math.dist(a, b) / 0.1))
                    for i in range(steps + 1):
                        q = [a[j] + (b[j] - a[j]) * i / steps for j in range(3)]
                        if q[2] + r <= z + ABOVE or q[2] - r >= z + HEADROOM:
                            continue
                        d = math.hypot(q[0] - cx, q[1] - cy)
                        if d < r0 - r or d > r1 + r:
                            continue
                        ang = math.degrees(math.atan2(q[1] - cy, q[0] - cx))
                        half = math.degrees(math.asin(min(1.0, (r + 0.05) / max(d, 0.1)))) + MARGIN_DEG
                        blocked.append((norm(ang - half), norm(ang + half), pipe["id"]))
            arc = p.get("arc_deg") or [0.0, 360.0]
            # sample the proposal arc at 1 degree and keep free degrees
            span = (arc[1] - arc[0]) % 360 or 360.0
            free = []
            for s in range(int(span) + 1):
                a = norm(arc[0] + s)
                if not any(in_arc(a, (b0, b1)) for b0, b1, _ in blocked):
                    free.append(s)
            runs, cur = [], []
            for s in free:
                if cur and s != cur[-1] + 1:
                    runs.append(cur)
                    cur = []
                cur.append(s)
            if cur:
                runs.append(cur)
            served = []
            for sid in p.get("serves") or []:
                if sid in nozzle_pts:
                    pt = nozzle_pts[sid]
                    served.append(norm(math.degrees(math.atan2(pt[1] - cy, pt[0] - cx))))
            best = None
            if runs and len(runs[0]) >= int(span) + 1:
                best = tuple(arc) if span < 360 else "all round"
                runs = []
            for run in sorted(runs, key=len, reverse=True):
                lo, hi = norm(arc[0] + run[0]), norm(arc[0] + run[-1])
                if len(run) >= MIN_ARC and all(in_arc(s, (lo - 15, hi + 15)) for s in served):
                    best = (round(lo, 1), round(hi, 1))
                    break
            names = sorted({b[2] for b in blocked})
            out.append((p["id"], round(z, 2), arc, best, p.get("serves"), names))
        print(f"== {tag}")
        for pid, z, arc, best, serves, names in out:
            print(f"  {pid} z {z} proposal {arc} -> {best} serves {serves}; blocked by {names}")


if __name__ == "__main__":
    main()
