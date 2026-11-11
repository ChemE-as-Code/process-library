"""Crop a sheet of ``cheme layout render`` to its drawing, for the skid figures (DESIGN.md D-041).

Core 1.5.0 draws every plan and section on an A1 sheet (841 x 594 mm) at the largest standard
scale that fits the drawn region, 1:50 at the most: a 20 ft skid (about 9 x 5 m with its
steps) then fills a fifth of the sheet's width, however tight the ``--crop``. This module takes
the SVG that core wrote and only changes its frame: the viewBox shrinks to the drawn region (the
clip rectangle ``#area`` of the drawing) plus a margin; the grid bubbles of the grid lines that
cross the drawing move along their own grid line to its edge; the scale bar, the north arrow and
the title block move into a strip under the drawing; the title names the view and says that the
A1 sheet is cropped. Nothing of the drawing itself is redrawn, moved or scaled: one SVG unit is
still one sheet millimetre, so the scale bar and the stated scale (1:50) stay true. The PNG is
the cropped SVG rasterised by resvg (the library core's ``--png`` uses), at
:data:`PNG_PX_PER_MM` pixels per sheet millimetre (core's sheets: 4).

Deterministic: the same SVG in gives the same bytes out (no time stamp, attribute order kept).
"""

from __future__ import annotations

import re
import xml.etree.ElementTree as ET

SVG_NS = "http://www.w3.org/2000/svg"
ET.register_namespace("", SVG_NS)
_Q = "{" + SVG_NS + "}"

#: white margin around the drawing (it holds the moved grid bubbles), mm
MARGIN = 20.0
#: the strip under the drawing for the scale bar, the north arrow and the title block, mm
STRIP = 48.0
#: core's title block (drawing2d.py: 180 x 40 mm) and the narrowest sheet that holds the strip
TITLE_W = 180.0
MIN_WIDTH = TITLE_W + 90.0
#: where core anchors its annotations on the A1 sheet (drawing2d.py, MARGIN 10, TITLE_H 40)
SCALE_BAR_AT = (15.0, 540.0)
NORTH_AT = (816.0, 28.0)
TITLE_AT = (651.0, 544.0)
#: grid bubbles this far outside the drawing at most are its own grid's (mm)
BUBBLE_REACH = 80.0
#: how far outside the drawing's edge a moved bubble's centre stands, mm
BUBBLE_OFFSET = 6.0
PNG_PX_PER_MM = 10.0


def _f(value: str) -> float:
    return float(value)


def _translate(element: ET.Element, dx: float, dy: float) -> None:
    move = f"translate({dx:.2f},{dy:.2f})"
    old = element.get("transform")
    element.set("transform", f"{move} {old}" if old else move)


def crop_sheet(svg: str, title: str) -> str:
    """The sheet *svg* of ``cheme layout render`` cropped to its drawing, titled *title*."""
    root = ET.fromstring(svg)
    clip = root.find(f"{_Q}defs/{_Q}clipPath[@id='area']/{_Q}rect")
    if clip is None:
        raise ValueError("not a cheme layout render sheet: no clipPath #area")
    x0, y0 = _f(clip.get("x")), _f(clip.get("y"))
    x1, y1 = x0 + _f(clip.get("width")), y0 + _f(clip.get("height"))
    # the bubbles of the grid lines through the drawing: moved along their line to its edge
    seen: set[tuple[float, float, str]] = set()
    for bubble in root.findall(f"{_Q}g[@class='bubble']"):
        circle = bubble.find(f"{_Q}circle")
        if circle is None:
            continue
        cx, cy = _f(circle.get("cx")), _f(circle.get("cy"))
        label = "".join(bubble.itertext()).strip()
        # the site's 10 m grid (labels 0, 10, 20, ...) one ring further out than a frame's grid
        # (1, 2, A, B), so that a site line next to a frame line keeps both bubbles readable
        off = 2.3 * BUBBLE_OFFSET if label.isdigit() and int(label) % 10 == 0 else BUBBLE_OFFSET
        if x0 <= cx <= x1 and y0 - BUBBLE_REACH <= cy < y0:
            dx, dy = 0.0, (y0 - off) - cy
        elif x0 <= cx <= x1 and y1 < cy <= y1 + BUBBLE_REACH:
            dx, dy = 0.0, (y1 + off) - cy
        elif y0 <= cy <= y1 and x0 - BUBBLE_REACH <= cx < x0:
            dx, dy = (x0 - off) - cx, 0.0
        elif y0 <= cy <= y1 and x1 < cx <= x1 + BUBBLE_REACH:
            dx, dy = (x1 + off) - cx, 0.0
        else:
            root.remove(bubble)  # another frame's grid, outside the cropped sheet
            continue
        key = (round(cx + dx, 1), round(cy + dy, 1), label)
        if key in seen:  # the same grid line's bubble twice (a grid of the site and a frame)
            root.remove(bubble)
            continue
        seen.add(key)
        _translate(bubble, dx, dy)
    vx0, vx1 = x0 - MARGIN, x1 + MARGIN
    if vx1 - vx0 < MIN_WIDTH:
        grow = (MIN_WIDTH - (vx1 - vx0)) / 2
        vx0, vx1 = vx0 - grow, vx1 + grow
    vy0, vy1 = y0 - MARGIN, y1 + MARGIN + STRIP
    strip_top = y1 + MARGIN
    for element in root.findall(f"{_Q}g"):
        gid = element.get("id")
        if gid == "scale-bar":
            _translate(element, vx0 + 6.0 - SCALE_BAR_AT[0], strip_top + 10.0 - SCALE_BAR_AT[1])
        elif gid == "north-arrow":
            _translate(element, vx0 + 70.0 - NORTH_AT[0], strip_top + 20.0 - NORTH_AT[1])
        elif gid == "title-block":
            _translate(element, vx1 - 6.0 - TITLE_W - TITLE_AT[0], strip_top + 4.0 - TITLE_AT[1])
            texts = element.findall(f"{_Q}text")
            if texts:
                texts[0].text = title
            for text in texts:
                if text.text and "(A1)" in text.text:
                    text.text = text.text.replace("(A1)", "(A1 sheet cropped to the drawing)")
    width, height = vx1 - vx0, vy1 - vy0
    root.set("width", f"{width:.2f}")
    root.set("height", f"{height:.2f}")
    root.set("viewBox", f"{vx0:.2f} {vy0:.2f} {width:.2f} {height:.2f}")
    # the white sheet behind everything covers the cropped sheet too
    for rect in root.findall(f"{_Q}rect"):
        if rect.get("x") == "0" and rect.get("y") == "0":
            rect.set("x", f"{vx0:.2f}")
            rect.set("y", f"{vy0:.2f}")
            rect.set("width", f"{width:.2f}")
            rect.set("height", f"{height:.2f}")
            break
    text = ET.tostring(root, encoding="unicode")
    return re.sub(r"\s+$", "", text) + "\n"


def svg_to_png(svg: str, zoom: float = PNG_PX_PER_MM) -> bytes:
    """The cropped sheet as PNG, rasterised by resvg (the ``png`` extra of core), at *zoom*
    pixels per sheet millimetre."""
    import resvg_py

    return bytes(resvg_py.svg_to_bytes(svg_string=svg, zoom=zoom, background="#ffffff"))


#: core's own PNG resolution of a sheet (``cheme layout render --png``), px per mm
CORE_PX_PER_MM = 4.0
_ROADS = re.compile(r'(?ms)^(?P<indent>[ \t]*)<g id="roads">.*?^(?P=indent)</g>\n')
_ZONES = re.compile(r'(?m)^[ \t]*<g id="zones">')


def roads_under_zones(svg: str) -> str:
    """Core's plot plan with its roads drawn before its zones (DESIGN.md D-043).

    Core 1.5.0 paints the road's grey fill over the zones, so a crane pad or laydown standing
    on the road is hidden. Only the order of the two groups changes: every element is kept as
    core wrote it. A sheet without either group is returned unchanged."""
    roads, zones = _ROADS.search(svg), _ZONES.search(svg)
    if roads is None or zones is None or roads.start() < zones.start():
        return svg
    block = roads.group(0)
    without = svg[: roads.start()] + svg[roads.end() :]
    at = _ZONES.search(without).start()
    return without[:at] + block + without[at:]
