# /// script
# requires-python = ">=3.12,<3.14"
# dependencies = [
#   "numpy==2.3.4",
#   "matplotlib==3.10.7",
#   "pyyaml==6.0.3",
#   "pypdf==5.1.0",
# ]
# ///
"""Microfluidic T-junction case (#338, tracker #333): reproduction and design extension.

Rerun from the repository root:  uv run benchmarks/reproductions/microfluidic-t-junction/run.py

1. Reproduction: the closed-form squeezing model of van Steijn, Kleijn & Kreutzer (Lab Chip
   2010) against the published size-versus-flow-ratio comparison at three junction shapes,
   taken from the vector replot in Nekouei & Vanapalli (arXiv:1703.00937v1, Fig. 5). The PDF is
   downloaded at runtime into the user cache, its sha256 checked, and the marker and line
   coordinates are read from its content stream as data (nothing in it is executed).
2. HYPOTHETICAL design extension: the model inverted for two target droplet volumes over a
   fabrication grid, with every design checked forward and out-of-regime requests flagged, and
   a dimensioned plan-view drawing (SVG) of each chosen junction.

Writes results/ deterministically. Exits non-zero only if the script itself fails (download,
checksum, extraction, or a design that does not reproduce its target); the reproduction verdict
is recorded in results/comparison.json.
"""

from __future__ import annotations

import hashlib
import json
import math
import os
import re
import sys
import urllib.request
from pathlib import Path

import matplotlib

matplotlib.use("svg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import yaml  # noqa: E402
from pypdf import PdfReader  # noqa: E402

HERE = Path(__file__).resolve().parent
RESULTS = HERE / "results"
CASE_ID = "microfluidic-t-junction"
PI = math.pi

SOURCE = yaml.safe_load((HERE / "source.yaml").read_text())
INPUTS = yaml.safe_load((HERE / "inputs.yaml").read_text())
TOL = yaml.safe_load((HERE / "tolerances.yaml").read_text())
QG = float(INPUTS["model_constants"]["q_gutter_over_q_c"]["value"])

# Categorical slots 1-3 of the reference palette (validated all-pairs for three series).
SERIES_STYLE = {
    "r0.33_h0.33": {"color": "#2a78d6", "marker": "o", "label": "w_in/w = 0.33, h/w = 0.33"},
    "r0.67_h0.11": {"color": "#eb6834", "marker": "^", "label": "w_in/w = 0.67, h/w = 0.11"},
    "r1.33_h0.17": {"color": "#1baf7a", "marker": "D", "label": "w_in/w = 1.33, h/w = 0.17"},
}
INK, INK2, GRID = "#0b0b0b", "#52514e", "#d9d8d4"


# --------------------------------------------------------------------------------------------
# Model (van Steijn et al. 2010, as restated; notation in source.yaml model)
# --------------------------------------------------------------------------------------------
def v_fill(r: float, eta: float) -> float:
    """Dimensionless filling volume V_fill/(h w^2); r = w_in/w, eta = h/w."""
    if r <= 1.0:
        return 3 * PI / 8 - (PI / 2) * (1 - PI / 4) * eta
    a = math.asin(1 - 1 / r)
    return ((PI / 4 - a / 2) * r**2 - 0.5 * (r - 1) * math.sqrt(2 * r - 1) + PI / 8
            - 0.5 * (1 - PI / 4) * ((PI / 2 - a) * r + PI / 2) * eta)


def v_fill_geometry(r: float, eta: float) -> float:
    """Same quantity from the geometric construction (w = 1): tip area x depth less 2 gutters."""
    w, w_in, h = 1.0, r, eta
    if r <= 1.0:
        area = PI * w**2 / 4 + PI * (w / 2) ** 2 / 2      # quarter disc radius w + half disc diameter w
        perimeter = PI * w / 2 + PI * w / 2               # quarter arc + half arc
    else:
        # quarter disc of radius w (upstream) plus the segment of the disc of radius w_in centred
        # on the far upstream inlet corner that lies within the main channel width w
        seg = w_in**2 * (PI / 4 - 0.5 * math.asin((w_in - w) / w_in)) - 0.5 * (w_in - w) * math.sqrt(w_in**2 - (w_in - w) ** 2)
        area = PI * w**2 / 8 + seg
        perimeter = PI * w / 2 + w_in * (PI / 2 - math.asin(1 - w / w_in))
    a_gutter = (1 - PI / 4) * h**2 / 4
    return (h * area - 2 * a_gutter * perimeter) / (h * w**2)


def alpha(r: float, eta: float, eps: float, qg: float = QG) -> float:
    """Squeezing coefficient; eps = corner roundness / w."""
    d = eta / (eta + 1) - eps                 # (2 r_pinch - eps)/w with 2 r_pinch = h w/(h + w)
    if r < d or d > 1:
        return math.nan                       # inlet narrower than the pinch-off neck: model undefined
    r_pinch = 1 + r - d + math.sqrt(2 * (r - d) * (1 - d))
    r_fill = max(1.0, r)
    return (1 - PI / 4) / (1 - qg) * (r_pinch**2 - r_fill**2 + PI / 4 * (r_pinch - r_fill) * eta)


def v_total(q: float, r: float, eta: float, eps: float) -> float:
    return v_fill(r, eta) + alpha(r, eta, eps) * q


# --------------------------------------------------------------------------------------------
# Reference data: download, verify, extract the vector figure
# --------------------------------------------------------------------------------------------
def cache_dir() -> Path:
    base = os.environ.get("XDG_CACHE_HOME") or str(Path.home() / ".cache")
    d = Path(base) / "cheme-reproductions" / CASE_ID
    d.mkdir(parents=True, exist_ok=True)
    return d


def fetch_pinned(spec: dict) -> Path:
    path = cache_dir() / spec["name"]
    if not path.exists() or hashlib.sha256(path.read_bytes()).hexdigest() != spec["sha256"]:
        req = urllib.request.Request(spec["url"], headers={"User-Agent": "cheme-reproductions/1.0"})
        with urllib.request.urlopen(req, timeout=120) as resp:
            data = resp.read()
        tmp = path.with_suffix(".part")
        tmp.write_bytes(data)
        tmp.replace(path)
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    if digest != spec["sha256"]:
        raise SystemExit(f"sha256 mismatch for {path}: {digest} != {spec['sha256']}")
    return path


NUM = r"[-+]?(?:\d+\.\d*|\.\d+|\d+)(?:[eE][-+]?\d+)?"
TOKEN = re.compile(rf"\[[^\]]*\]|/[^\s/\[\]<>()]+|{NUM}|[A-Za-z*'\"]+")


def extract_figure(pdf_path: Path) -> dict:
    """Read Fig. 5 of arXiv:1703.00937v1 (page 11, Form XObject /Meta61) as vector data."""
    page = PdfReader(str(pdf_path)).pages[10]
    form = page["/Resources"]["/XObject"]["/Meta61"].get_object()
    ops = form.get_data().decode("latin-1")
    stack, path, dash, shapes = [], [], "[]", []
    for tok in TOKEN.findall(ops):
        if re.fullmatch(NUM, tok) or tok[0] in "[/":
            stack.append(tok)
            continue
        if tok in ("m", "l"):
            path.append((tok, float(stack[-2]), float(stack[-1])))
        elif tok == "c":
            path.append(("c", float(stack[-2]), float(stack[-1])))
        elif tok == "re":
            x, y, w, h = map(float, stack[-4:])
            path += [("re", x, y), ("re", x + w, y + h)]
        elif tok == "h":
            path.append(("h", math.nan, math.nan))
        elif tok == "d":
            dash = stack[-2]
        elif tok in ("f", "f*", "S", "s", "B", "B*", "b", "n"):
            pts = [(x, y) for k, x, y in path if k != "h"]
            if pts and tok != "n":
                xs, ys = [p[0] for p in pts], [p[1] for p in pts]
                shapes.append({"paint": tok, "dash": dash, "kinds": "".join(p[0][0] for p in path),
                               "cx": (min(xs) + max(xs)) / 2, "cy": (min(ys) + max(ys)) / 2,
                               "w": max(xs) - min(xs), "pts": pts})
            path = []
        stack = []

    cal = {"x0": 54.379, "x1": 288.98, "y0": 50.647, "y1": 285.25}  # source.yaml digitisation
    # the calibration must coincide with the drawn axes: x axis from x0 to x1 at y0, y axis from y0 to y1 at x0
    axes_ok = any(s["kinds"] == "ml" and abs(s["pts"][0][0] - cal["x0"]) < 1e-3 and abs(s["pts"][1][0] - cal["x1"]) < 1e-3
                  and abs(s["pts"][0][1] - cal["y0"]) < 1e-3 for s in shapes) and \
        any(s["kinds"] == "ml" and abs(s["pts"][0][1] - cal["y0"]) < 1e-3 and abs(s["pts"][1][1] - cal["y1"]) < 1e-3
            and abs(s["pts"][0][0] - cal["x0"]) < 1e-3 for s in shapes)
    if not axes_ok:
        raise SystemExit("axis lines of the reference figure not found at the recorded calibration")

    def X(px): return (px - cal["x0"]) / (cal["x1"] - cal["x0"]) * 10.0
    def Y(py): return (py - cal["y0"]) / (cal["y1"] - cal["y0"]) * 35.0

    shape_of = {"mcccch": "o", "mllh": "^", "mlllh": "D"}
    series_of = {"o": "r0.33_h0.33", "^": "r0.67_h0.11", "D": "r1.33_h0.17"}
    out = {"experiment": {k: [] for k in SERIES_STYLE}, "vof_simulation": {k: [] for k in SERIES_STYLE},
           "model_lines": {}}
    filled_triangles = {(round(s["cx"], 3), round(s["cy"], 3)) for s in shapes
                        if s["kinds"] == "mllh" and s["paint"] == "f"}
    lines = []
    for s in shapes:
        m = shape_of.get(s["kinds"])
        if m:
            key = (round(s["cx"], 3), round(s["cy"], 3))
            if s["paint"] == "S" and m == "^" and key in filled_triangles:
                continue                                   # outline of a filled triangle
            kind = "experiment" if s["paint"] == "S" else "vof_simulation"
            out[kind][series_of[m]].append([round(X(s["cx"]), 3), round(Y(s["cy"]), 3)])
        elif s["dash"] != "[]" and s["kinds"] == "ml":
            (xa, ya), (xb, yb) = s["pts"]
            lines.append([[round(X(xa), 3), round(Y(ya), 3)], [round(X(xb), 3), round(Y(yb), 3)]])
    # assign each dashed line to the series whose experimental points it passes closest to
    for ln in lines:
        (qa, va), (qb, vb) = ln
        slope = (vb - va) / (qb - qa)
        def rms(k):
            return math.sqrt(sum((v - (va + slope * (q - qa))) ** 2 for q, v in out["experiment"][k]) / len(out["experiment"][k]))
        out["model_lines"][min(SERIES_STYLE, key=rms)] = ln
    for kind in ("experiment", "vof_simulation"):
        for k in out[kind]:
            out[kind][k].sort()
    return out


def compare_digitisation(extracted: dict, recorded: dict, tol: dict) -> dict:
    worst_q = worst_v = 0.0
    ok = True
    for kind in ("experiment", "vof_simulation", "model_lines"):
        for k in SERIES_STYLE:
            a, b = extracted[kind].get(k, []), sorted(recorded[kind][k]) if kind != "model_lines" else recorded[kind][k]
            if len(a) != len(b):
                ok = False
                continue
            for (qa, va), (qb, vb) in zip(a, b):
                worst_q, worst_v = max(worst_q, abs(qa - qb)), max(worst_v, abs(va - vb))
    ok = ok and worst_q <= tol["abs_q"] and worst_v <= tol["abs_v"]
    return {"max_abs_dev_q": worst_q, "max_abs_dev_v": worst_v, "tolerance": tol, "status": "pass" if ok else "fail"}


# --------------------------------------------------------------------------------------------
# Reproduction checks
# --------------------------------------------------------------------------------------------
def reproduction(fig: dict) -> dict:
    t = TOL["checks"]
    res: dict = {}

    # internal: closed form vs geometric construction
    worst = 0.0
    for r in np.linspace(0.2, 3.5, 34):
        for eta in np.linspace(0.02, 0.6, 30):
            a, b = v_fill(float(r), float(eta)), v_fill_geometry(float(r), float(eta))
            worst = max(worst, abs(a - b) / abs(b))
    res["fill_closed_vs_geometry"] = {"max_rel_dev": worst, "tolerance_rel": t["model_internal"]["fill_closed_vs_geometry"]["rel"],
                                      "grid": "w_in/w 0.2-3.5 (34 values) x h/w 0.02-0.6 (30 values)",
                                      "status": "pass" if worst <= t["model_internal"]["fill_closed_vs_geometry"]["rel"] else "fail"}

    # independent evaluation of alpha (Nekouei & Vanapalli)
    ref = SOURCE["reported_results"]["alpha_independent"]
    cases = INPUTS["reproduction"]["alpha_checks"]
    res["alpha_independent"] = {}
    for name, refkey in (("case_a", "w_in_over_w_1_h_over_w_0.33"), ("case_b", "w_in_over_w_1_h_over_w_1")):
        c = cases[name]
        ours = alpha(c["w_in_over_w"], c["h_over_w"], c["eps_over_w"])
        dev = ours - ref[refkey]["value"]
        tol = t["model_alpha_independent"][name]["abs"]
        res["alpha_independent"][name] = {"w_in_over_w": c["w_in_over_w"], "h_over_w": c["h_over_w"], "eps_over_w": c["eps_over_w"],
                                          "reference": ref[refkey]["value"], "ours": ours, "deviation": dev,
                                          "tolerance_abs": tol, "status": "pass" if abs(dev) <= tol else "fail"}

    # model lines and model vs experiment, per series
    series = INPUTS["reproduction"]["series"]
    res["model_lines"], res["model_vs_experiment"], res["vof_informational"] = {}, {}, {}
    for k, s in series.items():
        r, eta, eps = s["w_in_over_w"]["value"], s["h_over_w"]["value"], s["eps_over_w"]["value"]
        (qa, va), (qb, vb) = fig["model_lines"][k]
        slope_ref = (vb - va) / (qb - qa)
        icpt_ref = va - slope_ref * qa
        icpt, slope = v_fill(r, eta), alpha(r, eta, eps)
        ti, ts = t["model_lines"]["intercept"]["abs"], t["model_lines"]["slope"]["rel"]
        res["model_lines"][k] = {
            "intercept": {"reference": icpt_ref, "ours": icpt, "deviation": icpt - icpt_ref, "tolerance_abs": ti,
                          "status": "pass" if abs(icpt - icpt_ref) <= ti else "fail"},
            "slope": {"reference": slope_ref, "ours": slope, "rel_deviation": slope / slope_ref - 1, "tolerance_rel": ts,
                      "status": "pass" if abs(slope / slope_ref - 1) <= ts else "fail"},
            "slope_if_eps_0": alpha(r, eta, 0.0),
        }
        pts = []
        for q, v in fig["experiment"][k]:
            vm = v_total(q, r, eta, eps)
            pts.append({"q": q, "v_reference": v, "v_model": vm, "rel_deviation": vm / v - 1})
        mean_abs = sum(abs(p["rel_deviation"]) for p in pts) / len(pts)
        max_abs = max(abs(p["rel_deviation"]) for p in pts)
        tm, tp = t["model_vs_experiment"]["per_series_mean_abs_rel"]["max"], t["model_vs_experiment"]["per_point_abs_rel"]["max"]
        res["model_vs_experiment"][k] = {"points": pts, "mean_abs_rel_deviation": mean_abs, "max_abs_rel_deviation": max_abs,
                                         "tolerance_mean": tm, "tolerance_point": tp,
                                         "status_mean": "pass" if mean_abs <= tm else "fail",
                                         "status_points": "pass" if max_abs <= tp else "fail"}
        vof = [{"q": q, "v_vof": v, "v_model": v_total(q, r, eta, eps), "rel_deviation": v_total(q, r, eta, eps) / v - 1}
               for q, v in fig["vof_simulation"][k]]
        res["vof_informational"][k] = {"points": vof, "mean_abs_rel_deviation": sum(abs(p["rel_deviation"]) for p in vof) / len(vof),
                                       "note": "not part of the pass rule: a third-party VOF simulation, not experiment"}

    model_ok = (res["fill_closed_vs_geometry"]["status"] == "pass"
                and all(c["status"] == "pass" for c in res["alpha_independent"].values())
                and all(c["intercept"]["status"] == "pass" and c["slope"]["status"] == "pass" for c in res["model_lines"].values()))
    exp_ok = all(c["status_mean"] == "pass" and c["status_points"] == "pass" for c in res["model_vs_experiment"].values())
    res["verdict"] = "pass" if (model_ok and exp_ok) else ("partial" if model_ok else "fail")
    res["counts"] = {
        "checks_total": 1 + 2 + 6 + 6,
        "checks_passed": (res["fill_closed_vs_geometry"]["status"] == "pass")
        + sum(c["status"] == "pass" for c in res["alpha_independent"].values())
        + sum((c["intercept"]["status"] == "pass") + (c["slope"]["status"] == "pass") for c in res["model_lines"].values())
        + sum((c["status_mean"] == "pass") + (c["status_points"] == "pass") for c in res["model_vs_experiment"].values()),
    }
    return res


# --------------------------------------------------------------------------------------------
# HYPOTHETICAL design extension
# --------------------------------------------------------------------------------------------
D = INPUTS["design_extension"]
FL = D["fluids"]
MU_C, MU_D, GAMMA = FL["mu_c"]["value"], FL["mu_d"]["value"], FL["gamma"]["value"]
EPS_D = D["eps_over_w"]["value"]
VAL = D["validity"]
RULE = D["design_rule"]
BETA = VAL["leaking_bound"]["beta"]
UM, NL = 1e-6, 1e-12


def regime_flags(h: float, w: float, r: float, q: float | None, ca: float | None) -> list[str]:
    flags = []
    eta = h / w
    if not (VAL["h_over_w"]["min"] <= eta <= VAL["h_over_w"]["max"]):
        flags.append(f"h/w = {eta:.3g} outside the validated range {VAL['h_over_w']['min']}-{VAL['h_over_w']['max']}")
    if not (VAL["w_in_over_w"]["min"] - 1e-9 <= r <= VAL["w_in_over_w"]["max"] + 1e-9):
        flags.append(f"w_in/w = {r:.3g} outside the validated range")
    if q is not None and not (VAL["q"]["min"] <= q <= VAL["q"]["max"]):
        flags.append(f"q_d/q_c = {q:.3g} outside the validated range {VAL['q']['min']}-{VAL['q']['max']}")
    if ca is not None and ca > VAL["Ca_max"]["value"]:
        flags.append(f"Ca = {ca:.3g} above the squeezing limit {VAL['Ca_max']['value']}: shear-assisted break-up, model over-predicts the size")
    if ca is not None and q is not None and q * ca < 10 * BETA:
        flags.append(f"q Ca = {q * ca:.3g} below 10 beta = {10 * BETA:.3g}: leaking regime, size grows as Ca falls")
    if MU_D / MU_C > VAL["viscosity_ratio_max"]["value"]:
        flags.append("viscosity ratio above the assumed limit")
    return flags


def design_point(V: float, h: float, w: float, r: float, ca: float) -> dict:
    eta = h / w
    v = V / (h * w**2)
    vf, a = v_fill(r, eta), alpha(r, eta, EPS_D)
    q = (v - vf) / a
    qc = ca * GAMMA * w * h / MU_C                  # Ca = mu_c U_c / gamma, U_c = q_c/(w h)
    qd = q * qc
    return {"h_um": h / UM, "w_um": w / UM, "w_in_over_w": r, "w_in_um": r * w / UM, "h_over_w": eta,
            "v_target": v, "v_fill": vf, "alpha": a, "q": q, "Ca": ca, "q_c_uL_min": qc * 6e10,
            "q_d_uL_min": qd * 6e10, "frequency_Hz": qd / V if q > 0 else 0.0,
            "length_over_w": V / (h * w) / w, "length_um": V / (h * w) / UM}


def invert(V: float) -> dict:
    grid = D["fabrication_grid"]
    hs = [x * UM for x in grid["h"]["value"]]
    ws = [x * UM for x in range(50, 501, 5)]
    rs = grid["w_in_over_w"]["value"]
    ca = RULE["Ca_operating"]["value"]
    feasible, nominal = [], []
    for h in hs:
        for w in ws:
            for r in rs:
                p = design_point(V, h, w, r, ca)
                if not math.isfinite(p["q"]):
                    continue
                p["flags"] = regime_flags(h, w, r, p["q"], ca)
                if p["q"] <= 0:
                    continue
                if not p["flags"]:
                    feasible.append(p)
                    if RULE["q_window_nominal"]["min"] <= p["q"] <= RULE["q_window_nominal"]["max"]:
                        nominal.append(p)
    best = max(nominal, key=lambda p: (round(p["frequency_Hz"], 9), -p["w_um"], -p["h_um"])) if nominal else None
    # forward check of every feasible design
    worst = 0.0
    for p in feasible:
        Vf = v_total(p["q"], p["w_in_over_w"], p["h_over_w"], EPS_D) * (p["h_um"] * UM) * (p["w_um"] * UM) ** 2
        worst = max(worst, abs(Vf / V - 1))
    per_h = {}
    for p in nominal:
        k = f"{p['h_um']:.0f}"
        if k not in per_h or p["frequency_Hz"] > per_h[k]["frequency_Hz"]:
            per_h[k] = p
    return {"V_nL": V / NL, "n_feasible": len(feasible), "n_nominal": len(nominal), "best": best,
            "best_per_depth": per_h, "forward_check_max_rel_dev": worst,
            "feasible_ranges": {
                "w_um": [min(p["w_um"] for p in feasible), max(p["w_um"] for p in feasible)] if feasible else None,
                "h_um": sorted({p["h_um"] for p in feasible}),
                "q": [min(p["q"] for p in feasible), max(p["q"] for p in feasible)] if feasible else None}}


def smallest_validated_droplet() -> dict:
    grid = D["fabrication_grid"]
    best = None
    for h in grid["h"]["value"]:
        for r in grid["w_in_over_w"]["value"]:
            w = h / VAL["h_over_w"]["max"]              # smallest width the aspect-ratio bound allows
            w = math.ceil(w / 5) * 5
            hm, wm = h * UM, w * UM
            V = v_total(VAL["q"]["min"], r, hm / wm, EPS_D) * hm * wm**2
            if best is None or V < best["V_nL"] * NL:
                best = {"V_nL": V / NL, "h_um": h, "w_um": w, "w_in_over_w": r, "q": VAL["q"]["min"]}
    return best


def design_extension() -> dict:
    t1, t2 = D["targets"]["V1"]["value"] * NL, D["targets"]["V2"]["value"] * NL
    inv1, inv2 = invert(t1), invert(t2)
    tol = TOL["checks"]["design_forward_check"]["rel"]
    d1, d2 = inv1["best"], inv2["best"]
    for d, V in ((d1, t1), (d2, t2)):
        Vf = v_total(d["q"], d["w_in_over_w"], d["h_over_w"], EPS_D) * (d["h_um"] * UM) * (d["w_um"] * UM) ** 2
        d["forward_V_nL"] = Vf / NL
        d["forward_rel_dev"] = Vf / V - 1
    for d in (d1, d2):
        hw2 = (d["h_um"] * UM) * (d["w_um"] * UM) ** 2
        d["V_range_validated_q_nL"] = [v_total(VAL["q"][b], d["w_in_over_w"], d["h_over_w"], EPS_D) * hw2 / NL for b in ("min", "max")]
    forward_ok = max(inv1["forward_check_max_rel_dev"], inv2["forward_check_max_rel_dev"],
                     abs(d1["forward_rel_dev"]), abs(d2["forward_rel_dev"])) <= tol

    # changed-input example: same junction as D1, target changed from V1 to V2
    ch = design_point(t2, d1["h_um"] * UM, d1["w_um"] * UM, d1["w_in_over_w"], RULE["Ca_operating"]["value"])
    ch["flags"] = regime_flags(d1["h_um"] * UM, d1["w_um"] * UM, d1["w_in_over_w"], ch["q"], ch["Ca"])
    changed = {"description": "junction D1 kept, target volume changed from V1 to V2; only the flow-rate ratio is changed",
               "V1_q": d1["q"], "V2_q": ch["q"], "V1_length_um": d1["length_um"], "V2_length_um": ch["length_um"],
               "V1_frequency_Hz": d1["frequency_Hz"], "V2_frequency_Hz": ch["frequency_Hz"],
               "q_d_uL_min": [d1["q_d_uL_min"], ch["q_d_uL_min"]], "q_c_uL_min": ch["q_c_uL_min"], "flags": ch["flags"]}
    rev = design_point(t1, d2["h_um"] * UM, d2["w_um"] * UM, d2["w_in_over_w"], RULE["Ca_operating"]["value"])
    changed["reverse"] = {"description": "junction D2 kept, target V1: below the filling volume if q < 0",
                          "v_target": rev["v_target"], "v_fill": rev["v_fill"], "q": rev["q"],
                          "smallest_V_in_range_nL": v_total(VAL["q"]["min"], d2["w_in_over_w"], d2["h_over_w"], EPS_D)
                          * (d2["h_um"] * UM) * (d2["w_um"] * UM) ** 2 / NL}

    # flagged requests
    flagged = {}
    smin = smallest_validated_droplet()
    f1 = invert(0.02 * NL)
    flagged["F1"] = {"request": "V = 0.02 nL with the fabrication grid", "n_feasible": f1["n_feasible"],
                     "smallest_validated_droplet": smin,
                     "verdict": "not achievable inside the validated range" if f1["n_feasible"] == 0 else "achievable"}
    f_req = 1000.0
    qd_req = f_req * t2
    qc_req = qd_req / d2["q"]
    ca_req = MU_C * qc_req / (GAMMA * d2["w_um"] * UM * d2["h_um"] * UM)
    flagged["F2"] = {"request": "V2 from D2 at 1000 droplets per second", "Ca_required": ca_req,
                     "q_c_uL_min": qc_req * 6e10, "flags": regime_flags(d2["h_um"] * UM, d2["w_um"] * UM, d2["w_in_over_w"], d2["q"], ca_req),
                     "max_frequency_in_regime_Hz": d2["frequency_Hz"] * VAL["Ca_max"]["value"] / RULE["Ca_operating"]["value"]}
    f3 = design_point(t2, 100 * UM, 100 * UM, 1.0, RULE["Ca_operating"]["value"])
    f3["flags"] = regime_flags(100 * UM, 100 * UM, 1.0, f3["q"], f3["Ca"])
    flagged["F3"] = {"request": "V2 in a square channel h = w = 100 um, w_in = w", **f3}
    f4 = design_point(t1, d1["h_um"] * UM, d1["w_um"] * UM, d1["w_in_over_w"], 1e-4)
    f4["flags"] = regime_flags(d1["h_um"] * UM, d1["w_um"] * UM, d1["w_in_over_w"], f4["q"], 1e-4)
    flagged["F4"] = {"request": "D1 operated at Ca = 1e-4", **f4}

    return {"label": "HYPOTHETICAL design extension (not validated)", "fluids": FL["system"],
            "targets_nL": [t1 / NL, t2 / NL], "V1": inv1, "V2": inv2, "D1": d1, "D2": d2,
            "forward_check": {"tolerance_rel": tol, "status": "pass" if forward_ok else "fail"},
            "changed_input": changed, "flagged_requests": flagged}


# --------------------------------------------------------------------------------------------
# Figures
# --------------------------------------------------------------------------------------------
def style_axes(ax):
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    for s in ("left", "bottom"):
        ax.spines[s].set_color(INK2)
    ax.tick_params(colors=INK2, labelsize=8)
    ax.grid(True, color=GRID, linewidth=0.6)
    ax.set_axisbelow(True)


def fig_reproduction(fig: dict, path: Path):
    f, ax = plt.subplots(figsize=(6.4, 4.6))
    q = np.linspace(0, 10, 201)
    for k, s in INPUTS["reproduction"]["series"].items():
        st = SERIES_STYLE[k]
        r, eta, eps = s["w_in_over_w"]["value"], s["h_over_w"]["value"], s["eps_over_w"]["value"]
        ax.plot(q, [v_total(x, r, eta, eps) for x in q], color=st["color"], lw=2, label=f"model, {st['label']}")
        (qa, va), (qb, vb) = fig["model_lines"][k]
        ax.plot([qa, qb], [va, vb], color=st["color"], lw=1, ls=(0, (2, 3)), alpha=0.9)
        e = np.array(fig["experiment"][k])
        ax.plot(e[:, 0], e[:, 1], ls="none", marker=st["marker"], ms=7, mfc="white", mec=st["color"], mew=1.6)
        vf = np.array(fig["vof_simulation"][k])
        ax.plot(vf[:, 0], vf[:, 1], ls="none", marker=st["marker"], ms=4, color=st["color"], alpha=0.45)
    ax.plot([], [], color=INK2, lw=1, ls=(0, (2, 3)), label="model as drawn in the replot (Nekouei & Vanapalli Fig. 5)")
    ax.plot([], [], ls="none", marker="o", ms=7, mfc="white", mec=INK2, label="experiment, van Steijn 2010 (digitised)")
    ax.plot([], [], ls="none", marker="o", ms=4, color=INK2, alpha=0.45, label="VOF, Nekouei & Vanapalli (informational)")
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 35)
    ax.set_xlabel("flow-rate ratio q_d/q_c (-)", color=INK)
    ax.set_ylabel("droplet volume V/(h w²) (-)", color=INK)
    ax.set_title("T-junction squeezing model vs published bubble volumes", fontsize=10, color=INK, loc="left")
    style_axes(ax)
    ax.legend(fontsize=7, frameon=False, loc="upper left")
    f.tight_layout()
    save(f, path)


def fig_design_map(ext: dict, path: Path):
    f, axes = plt.subplots(1, 2, figsize=(9.0, 3.9), sharey=True)
    colors = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300", "#6250d6"]
    rs = D["fabrication_grid"]["w_in_over_w"]["value"]
    for ax, key, dkey in ((axes[0], "V1", "D1"), (axes[1], "V2", "D2")):
        V = ext[key]["V_nL"] * NL
        d = ext[dkey]
        h = d["h_um"] * UM
        ax.axhspan(VAL["q"]["min"], VAL["q"]["max"], color="#eeede9", zorder=0)
        ax.axhspan(RULE["q_window_nominal"]["min"], RULE["q_window_nominal"]["max"], color="#dcdbd5", zorder=0)
        w_right = 0.0
        for i, r in enumerate(rs):
            ws = np.arange(h / VAL["h_over_w"]["max"], h / VAL["h_over_w"]["min"], 1 * UM)
            qs = np.array([(V / (h * w**2) - v_fill(r, h / w)) / alpha(r, h / w, EPS_D) for w in ws])
            ax.plot(ws / UM, qs, color=colors[i], lw=1.6, label=f"w_in/w = {r:.2f}")
            if (qs >= 0.05).any():
                w_right = max(w_right, ws[qs >= 0.05].max() / UM)
        ax.set_xlim(h / VAL["h_over_w"]["max"] / UM - 5, w_right * 1.1)
        ax.plot([d["w_um"]], [d["q"]], marker="*", ms=12, color=INK, ls="none")
        ax.annotate(f"{dkey}: w = {d['w_um']:.0f} µm, w_in/w = {d['w_in_over_w']:.2f},\nq = {d['q']:.2f}, {d['frequency_Hz']:.0f} Hz",
                    (d["w_um"], d["q"]), xytext=(8, 8), textcoords="offset points", fontsize=7, color=INK)
        ax.set_yscale("log")
        ax.set_ylim(0.05, 20)
        ax.set_xlabel("main channel width w (µm)", color=INK)
        ax.set_title(f"V = {ext[key]['V_nL']:.2g} nL, depth h = {d['h_um']:.0f} µm", fontsize=9, color=INK, loc="left")
        style_axes(ax)
    axes[0].set_ylabel("required q_d/q_c (-)", color=INK)
    f.text(0.01, 0.005, "Light band: validated q range 0.1-10; darker band: design window 0.5-5. Curves start at the largest validated h/w (0.48). "
           "Star: chosen design (highest droplet frequency at Ca = 0.003).", fontsize=6.5, color=INK2)
    handles, labels = axes[0].get_legend_handles_labels()
    f.legend(handles, labels, fontsize=7, frameon=False, loc="lower center", ncol=7, bbox_to_anchor=(0.5, 0.035))
    f.suptitle("HYPOTHETICAL design map (not validated): flow-rate ratio needed for each target volume", fontsize=9, color=INK, x=0.01, ha="left")
    f.tight_layout(rect=(0, 0.1, 1, 1))
    save(f, path)


def save(f, path: Path):
    f.savefig(path, format="svg", metadata={"Date": None, "Creator": None})
    plt.close(f)


def drawing_svg(d: dict, name: str, V_nL: float) -> str:
    """Dimensioned plan view of the T-junction with a section view, drawn from the design values."""
    w, win, h, Ldrop = d["w_um"], d["w_in_um"], d["h_um"], d["length_um"]
    L_um = max(8 * w, Ldrop + 6 * w)                  # drawn length of the main channel (um)
    Li_um = max(2.2 * w, 1.5 * win)                   # drawn length of the side inlet (um)
    s = 620.0 / L_um                                  # px per um, same in both directions (to scale)
    W, Wi, L, Li, H = w * s, win * s, L_um * s, Li_um * s, h * s
    ox = 80.0
    oy = 120.0 + Li                                   # top wall of the main channel
    xi = ox + 2.0 * W                                 # upstream wall of the side inlet
    width = ox + L + 40
    height = oy + W + 70 + max(H, 30) + 110
    ink, ink2, blue, orange = "#0b0b0b", "#52514e", "#2a78d6", "#eb6834"

    def t(x, y, txt, size=12, anchor="middle", fill=ink, rot=None):
        tr = f' transform="rotate({rot} {x:.1f} {y:.1f})"' if rot is not None else ""
        return f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" text-anchor="{anchor}" fill="{fill}"{tr}>{txt}</text>'

    def ext(x1, y1, x2, y2):
        return f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{ink2}" stroke-width="0.6"/>'

    def dim(x1, y1, x2, y2):
        return (f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{ink2}" stroke-width="1" '
                'marker-start="url(#a)" marker-end="url(#a)"/>')

    def flow(x1, y1, x2, y2):
        return f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{blue}" stroke-width="2" marker-end="url(#f)"/>'

    p = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width:.0f}" height="{height:.0f}" '
         f'viewBox="0 0 {width:.0f} {height:.0f}" font-family="Helvetica, Arial, sans-serif">',
         f'<title>{name}: T-junction plan view, target {V_nL:g} nL (hypothetical design)</title>',
         '<defs><marker id="a" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="7" markerHeight="7" '
         f'orient="auto-start-reverse"><path d="M0,2 L10,5 L0,8 z" fill="{ink2}"/></marker>'
         '<marker id="f" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto">'
         f'<path d="M0,1 L10,5 L0,9 z" fill="{blue}"/></marker></defs>',
         '<rect width="100%" height="100%" fill="#fcfcfb"/>',
         t(20, 28, f"{name}: T-junction, plan view (HYPOTHETICAL design, not validated)", 15, "start"),
         t(20, 48, f"target droplet volume {V_nL:g} nL; drawn to scale; all channels {h:.0f} µm deep (section A-A)", 11, "start", ink2)]
    # channel: main channel with the side inlet entering from the top; open ends left unstroked
    p.append(f'<path d="M{ox:.1f},{oy:.1f} H{xi:.1f} V{oy - Li:.1f} H{xi + Wi:.1f} V{oy:.1f} H{ox + L:.1f} '
             f'V{oy + W:.1f} H{ox:.1f} Z" fill="#e3eefb" stroke="none"/>')
    p.append(f'<path d="M{ox:.1f},{oy:.1f} H{xi:.1f} V{oy - Li:.1f} M{xi + Wi:.1f},{oy - Li:.1f} V{oy:.1f} H{ox + L:.1f} '
             f'M{ox + L:.1f},{oy + W:.1f} H{ox:.1f}" fill="none" stroke="{ink}" stroke-width="1.6"/>')
    # flows
    p.append(flow(ox + 6, oy + W / 2, xi - 8, oy + W / 2))
    p.append(t(ox + 6, oy + W + 18, f"continuous phase q_c = {d['q_c_uL_min']:.3g} µL/min", 11, "start", blue))
    p.append(flow(xi + Wi / 2, oy - Li + 8, xi + Wi / 2, oy - 0.3 * Li))
    p.append(t(xi + Wi + 10, oy - 0.6 * Li, f"dispersed phase q_d = {d['q_d_uL_min']:.3g} µL/min", 11, "start", blue))
    p.append(flow(ox + L - 3.2 * W, oy + W / 2, ox + L - 6, oy + W / 2))
    # droplet of the predicted length (plug with rounded caps), downstream of the junction
    x0 = xi + Wi + 1.5 * W
    p.append(f'<rect x="{x0:.1f}" y="{oy + 0.1 * W:.1f}" width="{Ldrop * s:.1f}" height="{0.8 * W:.1f}" rx="{0.4 * W:.1f}" '
             f'fill="#fdebe3" stroke="{orange}" stroke-width="1.4"/>')
    p.append(ext(x0, oy + W + 4, x0, oy + W + 34))
    p.append(ext(x0 + Ldrop * s, oy + W + 4, x0 + Ldrop * s, oy + W + 34))
    p.append(dim(x0, oy + W + 28, x0 + Ldrop * s, oy + W + 28))
    p.append(t(x0 + Ldrop * s / 2, oy + W + 46, f"droplet length ≈ {Ldrop:.0f} µm (V/(h w), predicted)", 11, "middle", orange))
    # dimension w (left of the main channel)
    xd = ox - 26
    p.append(ext(ox - 34, oy, ox - 4, oy))
    p.append(ext(ox - 34, oy + W, ox - 4, oy + W))
    p.append(dim(xd, oy, xd, oy + W))
    p.append(t(xd - 8, oy + W / 2, f"w = {w:.0f} µm", 12, "middle", ink, -90))
    # dimension w_in (above the side inlet)
    yd = oy - Li - 16
    p.append(ext(xi, oy - Li - 24, xi, oy - Li - 4))
    p.append(ext(xi + Wi, oy - Li - 24, xi + Wi, oy - Li - 4))
    p.append(dim(xi, yd, xi + Wi, yd))
    p.append(t(xi + Wi / 2, yd - 8, f"w_in = {win:.0f} µm", 12))
    # section marks A-A across the main channel downstream
    xa = ox + L - 1.5 * W
    p.append(f'<line x1="{xa:.1f}" y1="{oy - 14:.1f}" x2="{xa:.1f}" y2="{oy + W + 14:.1f}" stroke="{ink2}" stroke-width="0.8" stroke-dasharray="8 3 2 3"/>')
    p.append(t(xa + 8, oy - 6, "A", 11, "start"))
    p.append(t(xa + 8, oy + W + 22, "A", 11, "start"))
    # section A-A: w x h, same scale
    ys = oy + W + 80
    xs = ox + L - W - 40
    p.append(t(xs + W / 2, ys - 10, "section A-A", 11))
    p.append(f'<rect x="{xs:.1f}" y="{ys:.1f}" width="{W:.1f}" height="{H:.1f}" fill="#e3eefb" stroke="{ink}" stroke-width="1.4"/>')
    p.append(dim(xs, ys + H + 12, xs + W, ys + H + 12))
    p.append(t(xs + W / 2, ys + H + 28, f"w = {w:.0f} µm", 11))
    p.append(dim(xs + W + 12, ys, xs + W + 12, ys + H))
    p.append(t(xs + W + 20, ys + H / 2 + 4, f"h = {h:.0f} µm", 11, "start"))
    # design table
    rows = [f"w_in/w = {d['w_in_over_w']:.2f}, h/w = {d['h_over_w']:.3f}, corner roundness eps = {EPS_D:g} w",
            f"flow-rate ratio q_d/q_c = {d['q']:.3f} at Ca = {d['Ca']:g} (FC-40 droplets in hexadecane)",
            f"forward check: predicted V = {d.get('forward_V_nL', V_nL):.6g} nL; about {d['frequency_Hz']:.0f} droplets per second",
            "model: van Steijn, Kleijn and Kreutzer, Lab Chip 2010 (squeezing regime); case #338"]
    for i, row in enumerate(rows):
        p.append(t(ox, ys + 6 + 18 * i, row, 11, "start", ink if i < 3 else ink2))
    p.append("</svg>")
    return "\n".join(p) + "\n"


# --------------------------------------------------------------------------------------------
def main() -> int:
    plt.rcParams.update({"svg.hashsalt": "cheme-338", "svg.fonttype": "none", "font.family": "DejaVu Sans"})
    RESULTS.mkdir(exist_ok=True)
    spec = SOURCE["sources"]["comparison_data"]["file"]
    pdf = fetch_pinned(spec)
    fig = extract_figure(pdf)
    digi = compare_digitisation(fig, SOURCE["reference_figure"]["digitised"], TOL["checks"]["model_internal"]["digitisation_rerun"])
    if digi["status"] != "pass":
        print("digitisation rerun does not match source.yaml:", digi, file=sys.stderr)
        return 2
    rep = reproduction(fig)
    ext = design_extension()
    if ext["forward_check"]["status"] != "pass":
        print("design forward check failed", file=sys.stderr)
        return 3

    fig_reproduction(fig, RESULTS / "fig_reproduction.svg")
    fig_design_map(ext, RESULTS / "fig_design_map.svg")
    for key, tkey in (("D1", 0), ("D2", 1)):
        (RESULTS / f"drawing_{key}.svg").write_text(drawing_svg(ext[key], key, ext["targets_nL"][tkey]))

    out = {
        "case": CASE_ID, "issue": 338, "tracker": 333,
        "tolerances": "tolerances.yaml (frozen 2026-11-04)",
        "reference_pdf": {"url": spec["url"], "sha256": spec["sha256"]},
        "digitisation_rerun": digi,
        "reproduction": rep,
        "design_extension": ext,
        "versions": {"python": sys.version.split()[0], "numpy": np.__version__, "matplotlib": matplotlib.__version__,
                     "pyyaml": yaml.__version__, "pypdf": __import__("pypdf").__version__},
    }
    (RESULTS / "comparison.json").write_text(json.dumps(out, indent=2, sort_keys=True, default=float) + "\n")

    # short console summary
    print(f"reproduction verdict: {rep['verdict']} ({rep['counts']['checks_passed']}/{rep['counts']['checks_total']} checks)")
    for k, c in rep["model_vs_experiment"].items():
        print(f"  {k}: mean |dev| {c['mean_abs_rel_deviation']:.3f}, max |dev| {c['max_abs_rel_deviation']:.3f}")
    for k in ("D1", "D2"):
        d = ext[k]
        print(f"  {k}: h {d['h_um']:.0f} um, w {d['w_um']:.0f} um, w_in/w {d['w_in_over_w']:.2f}, q {d['q']:.3f}, f {d['frequency_Hz']:.1f} Hz")
    print(f"results written to {RESULTS.relative_to(HERE.parents[2])}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
