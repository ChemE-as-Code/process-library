# /// script
# requires-python = ">=3.12,<3.14"
# dependencies = [
#   "numpy==2.3.4",
#   "scipy==1.16.3",
#   "pillow==11.3.0",
#   "pypdf==5.9.0",
#   "pyyaml==6.0.3",
# ]
# [tool.uv]
# exclude-newer = "2026-11-04T00:00:00Z"
# ///
"""Re-derive the digitised Figure 7 markers in source.yaml (reference_figure) from the pinned PDF.

Run from the repository root (optional; run.py does not need it):

    uv run benchmarks/reproductions/mof-water-harvester-cau10/digitise_figure7.py

Downloads the pinned TU Delft copy of the article into the same cache as run.py, checks its
sha256, reads the embedded raster of Figure 7 (page 11 of the PDF) into memory, and locates the
CAU-10-H markers (legend colour RGB 255,30,64) with a fixed-radius circle Hough transform on the
red/white boundary pixels. It prints the centres found and compares them with the pixel centres
recorded in source.yaml. It also repeats the search with the radius, the colour threshold and the
boundary width varied, and reports the spread of each centre, which is the basis of the stated
digitisation uncertainty. Nothing from the PDF or the image is written to disk or to git.
"""

from __future__ import annotations

import hashlib
import io
import itertools
import os
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

import numpy as np
import yaml
from PIL import Image
from pypdf import PdfReader
from scipy import ndimage

CASE_ID = "mof-water-harvester-cau10"
HERE = Path(__file__).resolve().parent
RED = np.array([255, 30, 64])
# Search windows (x0, x1, y0, y1) around the CAU-10-H markers in the two panels of the raster.
WINDOWS = {"a": (300, 420, 640, 850), "b": (450, 650, 1860, 2060)}
LEGEND = (1200, 1260, 0, 60)  # the legend marker of panel a, used to measure the marker radius


def fetch_pdf(paper: dict) -> bytes:
    base = os.environ.get("XDG_CACHE_HOME") or str(Path.home() / ".cache")
    target = Path(base) / "cheme-reproductions" / CASE_ID / "article_tudelft.pdf"
    target.parent.mkdir(parents=True, exist_ok=True)
    want = paper["open_copy"]["sha256"]
    if target.exists() and hashlib.sha256(target.read_bytes()).hexdigest() == want:
        return target.read_bytes()
    last = None
    for attempt in range(4):
        try:
            req = urllib.request.Request(paper["open_copy"]["url"], headers={"User-Agent": f"cheme-reproductions/{CASE_ID}"})
            with urllib.request.urlopen(req, timeout=120) as r:
                data = r.read()
            if hashlib.sha256(data).hexdigest() != want:
                raise RuntimeError(f"sha256 mismatch for the article PDF ({len(data)} bytes)")
            target.write_bytes(data)
            return data
        except (urllib.error.URLError, RuntimeError, TimeoutError) as exc:
            last = exc
            time.sleep(5 * (attempt + 1))
    raise SystemExit(f"could not download the article PDF: {last}")


def figure7(pdf: bytes) -> np.ndarray:
    page = PdfReader(io.BytesIO(pdf)).pages[10]  # page 11 of the PDF (cover page included)
    imgs = [i for i in page.images if i.name == "Im8.jpg"]
    if len(imgs) != 1:
        raise SystemExit("Figure 7 raster not found where expected")
    im = np.asarray(imgs[0].image.convert("RGB")).astype(int)
    if im.shape[:2] != (2386, 1500):
        raise SystemExit(f"unexpected raster size {im.shape}")
    return im


def find_ticks(im: np.ndarray) -> dict:
    """Tick marks as dark pixel runs beside the axis lines; the vertical axis lines themselves."""
    grey = im.mean(-1)
    dark = grey < 110

    def runs(v, off):
        lab, n = ndimage.label(v)
        return [float(np.nonzero(lab == i)[0].mean() + off) for i in range(1, n + 1)]

    out = {}
    for name, yax in (("a", 1035), ("b", 2245)):  # x-axis rows of panels a and b
        out[f"{name}_x"] = runs(dark[yax + 4: yax + 14, 165:1400].sum(0) >= 6, 165)
    out["y"] = runs(dark[0:2300, 146:157].sum(1) >= 6, 0)
    out["vertical_axis_cols"] = [x for x in range(im.shape[1]) if (grey[:, x] < 100).sum() > 600]
    return out


def check_calibration(cal: dict, ticks: dict) -> bool:
    ok = True
    want = [("a_x", cal["panel_a_x"]["tick_px"]), ("b_x", cal["panel_b_x"]["tick_px"]),
            ("y", list(cal["panel_a_y"]["decade_px"].values()) + list(cal["panel_b_y"]["decade_px"].values()))]
    for key, px in want:
        for x in px:
            near_tick = min(abs(t - x) for t in ticks[key]) <= 0.5
            on_axis = key != "y" and min(abs(c - x) for c in ticks["vertical_axis_cols"]) <= 1.0  # origin on the axis line
            if not (near_tick or on_axis):
                ok = False
                print(f"  calibration tick {key} at {x} px not found")
    return ok


def find_markers(im: np.ndarray, colour_tol: float, boundary: int, dr: int) -> dict:
    red = np.sqrt(((im - RED) ** 2).sum(-1)) < colour_tol
    white = im.min(-1) > 225
    edge = red & ndimage.binary_dilation(white, iterations=boundary)
    x0, x1, y0, y1 = LEGEND
    lab, _ = ndimage.label(red[y0:y1, x0:x1])
    ys, xs = np.nonzero(lab == 1)
    radius = round((xs.max() - xs.min() + ys.max() - ys.min() + 2) / 4) + dr
    th = np.linspace(0, 2 * np.pi, 180, endpoint=False)
    out = {}
    for panel, (x0, x1, y0, y1) in WINDOWS.items():
        acc = np.zeros((y1 - y0, x1 - x0))
        ys, xs = np.nonzero(edge[y0:y1, x0:x1])
        for rr in (radius - 1, radius, radius + 1):
            cy = (ys[:, None] - rr * np.sin(th)).round().astype(int)
            cx = (xs[:, None] - rr * np.cos(th)).round().astype(int)
            ok = (cy >= 0) & (cy < acc.shape[0]) & (cx >= 0) & (cx < acc.shape[1])
            np.add.at(acc, (cy[ok], cx[ok]), 1)
        acc = ndimage.gaussian_filter(acc, 1.0)
        peaks = []
        for _ in range(5):
            iy, ix = np.unravel_index(acc.argmax(), acc.shape)
            peaks.append((int(ix + x0), int(iy + y0), bool(red[iy + y0, ix + x0])))
            acc[max(0, iy - 12): iy + 13, max(0, ix - 12): ix + 13] = 0
        out[panel] = peaks
    return out


def main() -> int:
    src = yaml.safe_load((HERE / "source.yaml").read_text())
    im = figure7(fetch_pdf(src["paper"]))
    recorded = {m["id"]: {"a": tuple(m["panel_a_px"]), "b": tuple(m["panel_b_px"])}
                for m in src["reference_figure"]["cau10_h_markers"]}

    ok = check_calibration(src["reference_figure"]["calibration"], find_ticks(im))
    print("calibration ticks reproduced" if ok else "calibration ticks NOT reproduced")
    nominal = find_markers(im, colour_tol=60, boundary=2, dr=0)
    for panel in ("a", "b"):
        found = {(x, y) for x, y, _ in nominal[panel]}
        rec = {v[panel] for v in recorded.values()}
        print(f"panel {panel}: found {sorted(found)}")
        if found != rec:
            ok = False
            print(f"  differs from source.yaml: {sorted(rec)}")

    # Spread of each recorded centre over the variations (nearest peak in each variant).
    print("centre spread over variations (colour threshold 40/60/80, boundary 1/2/3 px, radius -1/0/+1 px):")
    variants = [find_markers(im, ct, bd, dr) for ct, bd, dr in itertools.product((40, 60, 80), (1, 2, 3), (-1, 0, 1))]
    for mid, pos in recorded.items():
        for panel in ("a", "b"):
            x_r, y_r = pos[panel]
            near = [min(np.hypot(x - x_r, y - y_r) for x, y, _ in v[panel]) for v in variants]
            hit = [d for d in near if d <= 10]  # a peak further than 10 px away is a different marker
            centre_red = next(c for x, y, c in nominal[panel] if (x, y) == (x_r, y_r))
            print(f"  {mid} panel {panel}: found in {len(hit)} of {len(near)} variants, max shift {max(hit):.1f} px; "
                  f"centre pixel in marker colour (not covered): {centre_red}")
    print("recorded centres and calibration reproduced" if ok else "NOT reproduced (see above)")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
