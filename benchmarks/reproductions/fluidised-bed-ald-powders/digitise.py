# /// script
# requires-python = ">=3.12,<3.14"
# dependencies = [
#     "numpy==2.3.4",
#     "pymupdf==1.24.14",
# ]
# ///
"""Digitise reference curves of the Grillo (2018) thesis, chapter 7, from their vector paths.

This is how the `digitised` values in source.yaml were obtained. It is not needed to run the
reproduction (run.py reads the values from source.yaml). It downloads the open thesis PDF from
its pinned URL into a cache outside git, checks its sha256, and reads the line paths of two
figures with PyMuPDF. Nothing downloaded is executed and nothing of the PDF is written to the
repository; only numbers are printed.

Method: the plotted curves are stored in the PDF as polylines (50 segments each). The axis
frame and the tick-label centres give a linear map from page points to data units. Each curve
is then linearly interpolated at the requested abscissae.

    uv run benchmarks/reproductions/fluidised-bed-ald-powders/digitise.py [--unrounded]
"""

from __future__ import annotations

import hashlib
import json
import os
import sys
import urllib.request
from pathlib import Path

import fitz  # PyMuPDF
import numpy as np

CASE = "fluidised-bed-ald-powders"
URL = "https://repository.tudelft.nl/file/File_054098c0-4b65-41b2-9b62-721326918bc1"
SHA256 = "1b41aef7c0da355335566dfa7c8c7c16791f16346f253dc53a7631906737b802"
FILENAME = "Grillo-2018-thesis-Thesis_Final_FG.pdf"


def cache_dir() -> Path:
    base = os.environ.get("XDG_CACHE_HOME") or str(Path.home() / ".cache")
    d = Path(base) / "cheme-reproductions" / CASE
    d.mkdir(parents=True, exist_ok=True)
    return d


def fetch() -> Path:
    path = cache_dir() / FILENAME
    if not path.exists():
        print(f"downloading {URL}", file=sys.stderr)
        tmp = path.with_suffix(".part")
        with urllib.request.urlopen(URL, timeout=300) as r, open(tmp, "wb") as f:
            while chunk := r.read(1 << 20):
                f.write(chunk)
        tmp.rename(path)
    h = hashlib.sha256(path.read_bytes()).hexdigest()
    if h != SHA256:
        raise SystemExit(f"sha256 mismatch for {path}: {h}")
    return path


def polylines(page) -> list[tuple[tuple, np.ndarray]]:
    out = []
    for d in page.get_drawings():
        if len(d["items"]) < 40:
            continue
        pts = []
        for it in d["items"]:
            if it[0] == "l":
                pts += [it[1], it[2]]
            elif it[0] == "c":
                pts += [it[1], it[4]]
        xy = np.array([(p.x, p.y) for p in pts])
        # drop repeated vertices (each segment repeats the previous end point)
        keep = np.r_[True, np.any(np.diff(xy, axis=0) != 0, axis=1)]
        out.append((tuple(round(c, 3) for c in d["color"]), xy[keep]))
    return out


def label_centres(page, y_lo: float, y_hi: float) -> list[tuple[str, float, float]]:
    out = []
    for b in page.get_text("dict")["blocks"]:
        for line in b.get("lines", []):
            for s in line["spans"]:
                x0, y0, x1, y1 = s["bbox"]
                if y_lo < y0 < y_hi:
                    out.append((s["text"].strip(), (x0 + x1) / 2, (y0 + y1) / 2))
    return out


def axis_map(p0: float, v0: float, p1: float, v1: float):
    return lambda p: v0 + (np.asarray(p) - p0) * (v1 - v0) / (p1 - p0)


def interp(xy: np.ndarray, fx, fy, at: list[float]) -> list[float]:
    x, y = fx(xy[:, 0]), fy(xy[:, 1])
    order = np.argsort(x)
    return [float(v) for v in np.interp(at, x[order], y[order])]


UNROUNDED = "--unrounded" in sys.argv


def main() -> None:
    doc = fitz.open(fetch())
    result: dict = {"source_sha256": SHA256}

    # Fig. 7.4 (PDF page 221, printed page 198): H* vs d_b.
    page = doc[220]
    # Label centres rounded to whole points, as when the source.yaml values were read (the
    # rounding is inside the stated +-0.5 pt uncertainty); --unrounded shows the sensitivity.
    lab = label_centres(page, 280, 440)
    if not UNROUNDED:
        lab = [(t, round(x), round(y)) for t, x, y in lab]

    def find(text, xmin, xmax, which):
        # exactly one label must match, otherwise the calibration would be ambiguous
        c = [(x, y) for t, x, y in lab if t == text and xmin < x < xmax]
        assert len(c) == 1, (text, xmin, xmax, c)
        return c[0][which]
    # panel a: x ticks 0 and 4 cm, y ticks 0 and 250 cm; panel b: x 0 and 4 cm, y 0 and 6 cm.
    # The x-tick "0" (centre x = 162.4) and the y-tick "0" (x = 157.1) are told apart by x.
    # (A first version of this script matched both and picked one in set order; the
    # source.yaml values were read with the x-tick, which coincides with the curves' origin.)
    ax = axis_map(find("0", 160, 170, 0), 0.0, find("4", 250, 260, 0), 4.0)
    ay = axis_map(find("0", 150, 160, 1), 0.0, find("250", 140, 165, 1), 250.0)
    bx = axis_map(find("0", 290, 300, 0), 0.0, find("4", 380, 395, 0), 4.0)
    by = axis_map(find("0", 285, 293, 1), 0.0, find("6", 285, 293, 1), 6.0)
    curves = polylines(page)
    at = [1.0, 2.0, 3.0, 4.0, 4.5]
    a_names = {(0.008, 0.0, 0.875): "umf_0.01", (0.561, 0.898, 0.357): "umf_0.1",
               (0.381, 0.381, 0.381): "umf_2.5", (1.0, 0.0, 0.0): "umf_5"}
    fig74a, fig74b = {}, []
    for color, xy in curves:
        if xy[:, 0].min() < 200:  # panel a
            fig74a[a_names[color]] = dict(zip(map(str, at), interp(xy, ax, ay, at)))
        else:
            fig74b.append(interp(xy, bx, by, at))
    fig74b = np.array(fig74b)
    result["fig7_4a_Hstar_cm"] = {"d_b_cm": at, **{k: [round(v, 2) for v in d.values()] for k, d in fig74a.items()}}
    result["fig7_4b_Hstar_cm"] = {"d_b_cm": at, "min": fig74b.min(0).round(3).tolist(), "max": fig74b.max(0).round(3).tolist()}

    # Fig. 7.3 (PDF page 220, printed page 197): C_TMA,b / C_TMA,in vs z/H at 11 times.
    page = doc[219]
    lab = label_centres(page, 40, 260)
    zx0 = [x for t, x, y in lab if t == "0" and y > 245][0]
    zx1 = [x for t, x, y in lab if t == "1" and y > 245][0]
    cy0 = [y for t, x, y in lab if t == "0" and x < 134][0]
    cy1 = [y for t, x, y in lab if t == "1" and x < 134][0]
    fx, fy = axis_map(zx0, 0.0, zx1, 1.0), axis_map(cy0, 0.0, cy1, 1.0)
    times = [0, 0.1, 0.2, 0.9, 9.9, 19.9, 43.9, 44.9, 45.9, 47.9, 49.9]  # caption order
    curves = polylines(page)
    assert len(curves) == len(times), len(curves)
    zs = [0.02, 0.1, 0.2, 0.3, 0.4, 0.6, 1.0]
    result["fig7_3_Cb_over_Cin"] = {"z_over_H": zs}
    for t, (color, xy) in zip(times, curves):
        result["fig7_3_Cb_over_Cin"][f"t_{t}s"] = [round(v, 4) for v in interp(xy, fx, fy, zs)]
    print(json.dumps(result, indent=1))


if __name__ == "__main__":
    main()
