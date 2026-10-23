"""Steel of the declared supports against each other and against the pipes they do not serve
(DESIGN.md D-065 (5); review10#2). cheme-as-code has no steel-against-steel rule between two
declared supports yet, so this scan stands in for it. Provenance only; it reads the committed
layout/plant-model.yaml and writes nothing:

    cheme run scripts/support_steel_scan.py [STEEL_LIMIT_M] [PIPE_LIMIT_M]

Every member (column, crossbar) is an axis-aligned box from its start / end and its profile;
every straight pipe run a box of its outer radius with insulation. The gap is the clear
distance between two boxes, negative when they overlap (the smallest penetration). Printed:
member pairs of two different declared supports or platforms below STEEL_LIMIT_M (default 0),
and pipe-support members (ids with `/Line_`) closer than PIPE_LIMIT_M (default 0.1 m) to a pipe
they do not serve.
"""

from __future__ import annotations

import sys

import yaml

STEEL = float(sys.argv[1]) if len(sys.argv) > 1 else 0.0
PIPE = float(sys.argv[2]) if len(sys.argv) > 2 else 0.1
model = yaml.safe_load(open("layout/plant-model.yaml", encoding="utf-8"))
supports, pipes = [], []


def walk(o) -> None:
    if isinstance(o, dict):
        if "serves" in o and "parts" in o and o.get("source") == "declared":
            supports.append(o)
            return
        if "points" in o and "od" in o and "line" in o:
            pipes.append(o)
            return
        for v in o.values():
            walk(v)
    elif isinstance(o, list):
        for v in o:
            walk(v)


walk(model)


def member_box(m: dict):
    s, e = m["start"], m["end"]
    w, d = m.get("profile", [0.2, 0.2])
    lo, hi = [], []
    for i in range(3):
        a, b = sorted((s[i], e[i]))
        if abs(b - a) < 1e-9:
            h = (w if i < 2 else d) / 2.0
            a, b = a - h, b + h
        lo.append(a)
        hi.append(b)
    return lo, hi


def gap(b1, b2) -> float:
    (l1, h1), (l2, h2) = b1, b2
    seps = [max(l2[i] - h1[i], l1[i] - h2[i]) for i in range(3)]
    if all(s < 0 for s in seps):
        return max(seps)
    return sum(max(s, 0.0) ** 2 for s in seps) ** 0.5


members = [(s, [(p["id"], member_box(p)) for p in s["parts"]
                if p.get("kind") == "member" and "start" in p]) for s in supports]
print(f"{len(supports)} declared supports and platforms, {len(pipes)} pipes")
n = 0
for i in range(len(members)):
    for j in range(i + 1, len(members)):
        for id1, b1 in members[i][1]:
            for id2, b2 in members[j][1]:
                g = gap(b1, b2)
                if g < STEEL:
                    n += 1
                    print(f"steel {g:+.3f} m  {id1}  <->  {id2}")
print(f"{n} steel pairs below {STEEL} m")

runs = []
for p in pipes:
    r = p["od"] / 2.0 + (p.get("insulation_mm") or 0.0) / 1000.0
    for a, b in zip(p["points"][:-1], p["points"][1:]):
        runs.append((p["id"], ([min(a[k], b[k]) - r for k in range(3)],
                               [max(a[k], b[k]) + r for k in range(3)])))
n = 0
for s, mem in members:
    if "/Line_" not in s["id"]:
        continue
    serves = set(s.get("serves", []))
    for mid, b in mem:
        for pid, pb in runs:
            if pid not in serves and (g := gap(b, pb)) < PIPE - 1e-6:
                n += 1
                print(f"pipe {g:+.3f} m  {mid}  <->  {pid}")
print(f"{n} pipe-support members below {PIPE} m from a pipe they do not serve ({len(runs)} runs)")
