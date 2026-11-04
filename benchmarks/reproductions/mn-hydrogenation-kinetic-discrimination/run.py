# /// script
# requires-python = ">=3.12,<3.14"
# dependencies = [
#     "numpy==2.3.4",
#     "scipy==1.16.3",
#     "matplotlib==3.10.7",
#     "pyyaml==6.0.3",
#     "pypdf==5.1.0",
# ]
# ///
"""Mn-CNP hydrogenation: reproduce the published kinetic-model fits and select a discriminating run.

Issue #341 (tracker #333), protocol ADR 0030. Rerun from the repository root:

    uv run benchmarks/reproductions/mn-hydrogenation-kinetic-discrimination/run.py

The pinned SI PDF is downloaded into a cache outside git and verified by sha256; only its text is
read (pypdf), nothing in it is executed. Results go to results/ next to this file. The script
exits non-zero only if it cannot run; the reproduction verdict is recorded in comparison.json.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import sys
import urllib.request
from pathlib import Path

import numpy as np
import yaml

HERE = Path(__file__).resolve().parent
CASE_ID = HERE.name
RESULTS = HERE / "results"
R_KJ = 0.008314          # kJ/(mol K), model IV as written in the SI
R_J = 8.314              # J/(mol K)
T_OFFSET = 274.1         # K; Table S2 tabulates 1/(T_degC + 274.1 K), see inputs.yaml
SEED = 341

CREDIT = ("Data: van Schendel, Yang, Uslamin, Pidko, ChemCatChem 2021, 13, 4886, "
          "doi:10.1002/cctc.202101140, CC BY 4.0 (SI {tables}); fits and figure by run.py "
          "(see NOTICE.md)")
COLOURS = {"II": "#2a78d6", "III": "#eb6834", "IV": "#1baf7a"}
INK, INK2, GRID = "#0b0b0b", "#52514e", "#d9d8d4"


# ----------------------------------------------------------------------------- source data
def cache_dir() -> Path:
    base = Path(os.environ.get("XDG_CACHE_HOME") or Path.home() / ".cache")
    d = base / "cheme-reproductions" / CASE_ID
    d.mkdir(parents=True, exist_ok=True)
    return d


def fetch(entry: dict) -> Path:
    path = cache_dir() / entry["name"]
    if path.exists() and hashlib.sha256(path.read_bytes()).hexdigest() == entry["sha256"]:
        return path
    req = urllib.request.Request(entry["url"], headers={"User-Agent": "cheme-reproductions/1.0"})
    with urllib.request.urlopen(req, timeout=300) as r:
        data = r.read()
    digest = hashlib.sha256(data).hexdigest()
    if digest != entry["sha256"]:
        raise SystemExit(f"sha256 mismatch for {entry['url']}: {digest}")
    path.write_bytes(data)
    return path


NUM = re.compile(r"^-?\d+(\.\d+)?([eE][-+]?\d+)?$")


def numeric_rows(text: str, width: int) -> list[list[float]]:
    rows = []
    for line in text.splitlines():
        tok = line.split()
        if len(tok) == width and all(NUM.match(t) for t in tok):
            rows.append([float(t) for t in tok])
    return rows


def sections(text: str) -> list[str]:
    """Split a page into blocks that start at 'Table S..' captions."""
    parts = re.split(r"\n(?=Table S\s?\d)", text)
    return [p for p in parts if p.startswith("Table S")]


def parse_si(pdf: Path) -> dict:
    from pypdf import PdfReader

    pages = [p.extract_text() for p in PdfReader(str(pdf)).pages]
    pg = lambda n: pages[n - 1]  # noqa: E731
    s1 = np.array(numeric_rows(pg(4), 7))
    s2 = np.array(numeric_rows(pg(5), 5))
    s6 = np.array(numeric_rows(pg(9), 2))                   # yhat, y (model I)
    s10 = np.array(numeric_rows(pg(14), 3))                 # run, yhat, y (model II)
    s16 = np.array(numeric_rows(pg(20), 3))                 # run, yhat, y (model III)
    s21 = np.array(numeric_rows(pg(25), 3))                 # run, y, yhat (model IV)
    p28 = sections(pg(28))
    kin = {
        "S23": np.array(numeric_rows(p28[0], 2)),
        "S24": np.array(numeric_rows(p28[1], 2)),
        "S25": np.array(numeric_rows(p28[2], 2)),
        "S26": np.array(numeric_rows(pg(29), 2)),
    }
    shapes = {"S1": (30, 7), "S2": (30, 5), "S6": (30, 2), "S10": (26, 3), "S16": (25, 3),
              "S21": (24, 3), "S23": (8, 2), "S24": (8, 2), "S25": (9, 2), "S26": (7, 2)}
    got = {"S1": s1.shape, "S2": s2.shape, "S6": s6.shape, "S10": s10.shape, "S16": s16.shape,
           "S21": s21.shape, **{k: v.shape for k, v in kin.items()}}
    for k, shp in shapes.items():
        if got[k] != shp:
            raise SystemExit(f"SI parse: table {k} has shape {got[k]}, expected {shp}")
    return {"S1": s1, "S2": s2, "S6": s6, "S10": s10, "S16": s16, "S21": s21, **kin}


# ----------------------------------------------------------------------------- regression
def ols(X: np.ndarray, y: np.ndarray) -> dict:
    n, p = X.shape
    scale = np.abs(X).max(axis=0)
    scale[scale == 0] = 1.0
    Xs = X / scale
    q, r = np.linalg.qr(Xs)
    bs = np.linalg.solve(r, q.T @ y)
    b = bs / scale
    res = y - X @ b
    dfe = n - p
    mse = res @ res / dfe
    rinv = np.linalg.inv(r)
    cov = mse * (rinv @ rinv.T) / np.outer(scale, scale)
    h = np.sum(q**2, axis=1)
    sst = np.sum((y - y.mean()) ** 2)
    press = float(np.sum((res / (1 - h)) ** 2))
    r2 = 1 - res @ res / sst
    return {
        "b": b, "cov": cov, "se": np.sqrt(np.diag(cov)), "rmse": float(np.sqrt(mse)),
        "r2": float(r2), "adj_r2": float(1 - (1 - r2) * (n - 1) / dfe), "press": press,
        "pred_r2": float(1 - press / sst), "n": n, "dfe": dfe, "fitted": X @ b,
    }


def bisquare_irls(X: np.ndarray, y: np.ndarray, k: float = 4.685, tol: float = 1e-10) -> dict:
    """Robust linear fit with bisquare weights, leverage-adjusted residuals, MAD scale."""
    n, p = X.shape
    w = np.ones(n)
    q, _ = np.linalg.qr(X / np.abs(X).max(axis=0))
    h = np.minimum(np.sum(q**2, axis=1), 0.9999)
    adj = 1 / np.sqrt(1 - h)
    b = np.linalg.lstsq(X, y, rcond=None)[0]
    res_ols = y - X @ b
    ols_s = float(np.sqrt(res_ols @ res_ols / (n - p)))
    for _ in range(500):
        res = y - X @ b
        ra = res * adj
        rs = np.sort(np.abs(ra))
        s = np.median(rs[max(0, p - 1):]) / 0.6745
        u = ra / (k * s)
        w = np.where(np.abs(u) < 1, (1 - u**2) ** 2, 0.0)
        sw = np.sqrt(w)
        b_new = np.linalg.lstsq(X * sw[:, None], y * sw, rcond=None)[0]
        if np.max(np.abs(b_new - b) / np.maximum(np.abs(b), 1e-12)) < tol:
            b = b_new
            break
        b = b_new
    res = y - X @ b
    mse_w = float(np.sum(w * res**2) / (n - p))
    cov = mse_w * np.linalg.inv((X * w[:, None]).T @ X)
    # MATLAB robustfit / statrobustsigma convention (sensitivity only, not used by the checks):
    # Street-corrected robust sigma from the final adjusted residuals, shrunk towards OLS sigma.
    ra = res * adj
    mad_s = float(np.median(np.sort(np.abs(ra))[max(0, p - 1):]) / 0.6745)
    bis = lambda u: np.where(np.abs(u) < 1, (1 - u**2) ** 2, 0.0)  # noqa: E731
    st = mad_s * k
    u = ra / st
    phi = u * bis(u)
    dphi = ((u + 1e-4) * bis(u + 1e-4) - (u - 1e-4) * bis(u - 1e-4)) / 2e-4
    m1 = float(np.mean(dphi))
    m2 = float(np.sum((1 - h) * phi**2) / (n - p))
    K = 1 + (p / n) * (1 - m1) / m1
    robust_s = K * np.sqrt(m2) * st / m1
    matlab_s = float(max(robust_s, np.sqrt((ols_s**2 * p**2 + robust_s**2 * n) / (p**2 + n))))
    return {"b": b, "cov": cov, "se": np.sqrt(np.diag(cov)), "rmse": float(np.sqrt(mse_w)),
            "rmse_unweighted": float(np.sqrt(res @ res / (n - p))), "weights": w, "n": n,
            "dfe": n - p, "fitted_lin": X @ b,
            "matlab_convention": {"s": matlab_s, "robust_s": float(robust_s), "ols_s": ols_s,
                                  "mad_s": mad_s, "cov_scale": matlab_s**2 / mse_w}}


def line_fit(x: np.ndarray, y: np.ndarray) -> dict:
    X = np.column_stack([np.ones_like(x), x])
    f = ols(X, y)
    return {"slope": float(f["b"][1]), "slope_se": float(f["se"][1]), "r2": f["r2"]}


# ----------------------------------------------------------------------------- model terms
TERMS_I = ["Intercept", "x1", "x2", "x3", "x4", "x1:x2", "x1:x3", "x1:x4", "x2:x3", "x2:x4",
           "x3:x4", "x1^2", "x2^2", "x3^2", "x4^2"]
TERMS_II = ["Intercept", "x1", "x2", "x3", "x4", "x1:x3", "x2:x4", "x4^2"]
TERMS_III = ["Intercept", "x1", "x2", "x3", "x4", "x4^2"]
TERMS_IV = ["Intercept", "Ea_kJ_per_mol", "x2", "x3", "x4", "x6_per_s"]


def design(x1, x2, x3, x4, terms):
    cols = {"Intercept": np.ones_like(x1), "x1": x1, "x2": x2, "x3": x3, "x4": x4,
            "x1:x2": x1 * x2, "x1:x3": x1 * x3, "x1:x4": x1 * x4, "x2:x3": x2 * x3,
            "x2:x4": x2 * x4, "x3:x4": x3 * x4, "x1^2": x1**2, "x2^2": x2**2, "x3^2": x3**2,
            "x4^2": x4**2}
    return np.stack([cols[t] for t in terms], axis=-1)


def design_iv(x1, x2, x3, x4, t_s):
    return np.stack([np.ones_like(x1), -x1 / R_KJ, x2, x3, x4, t_s], axis=-1)


def integrated_iv(b, x1, x2, x3, x4, t_h, S0):
    """Model IV read as the integrated rate law of the source's Eq. 14.

    dP/dt = g0 exp(k t) S with g0 = exp(b0 - b1 x1/R + b2 x2 + b3 x3 + b4 x4) in 1/h and
    k = 3600 b5 in 1/h, so yield Y = 1 - exp(-g0 expm1(k t)/k) and y = ln(S0 Y / t).
    """
    X0 = design_iv(x1, x2, x3, x4, np.zeros_like(t_h))
    g0 = np.exp(X0 @ b)
    k = 3600.0 * b[5]
    with np.errstate(divide="ignore", invalid="ignore"):
        tau = np.where(np.abs(k) > 1e-12, np.expm1(k * t_h) / k, t_h)
    yl = -np.expm1(-g0 * tau)
    return np.log(S0 * yl / t_h), yl


def fit_integrated_iv(x1, x2, x3, x4, t_h, S0, y, starts):
    """Nonlinear least squares of the integrated reading to measured y (unweighted)."""
    from scipy.optimize import least_squares

    def resid(b):
        return integrated_iv(b, x1, x2, x3, x4, t_h, S0)[0] - y

    scale = np.array([10.0, 10.0, 0.01, 0.5, 0.5, 1e-5])
    best, by_start = None, []
    for b0 in starts:
        r = least_squares(lambda z: resid(z * scale), np.asarray(b0) / scale, method="lm",
                          xtol=1e-14, ftol=1e-14, gtol=1e-14, max_nfev=20000)
        by_start.append({"start": np.asarray(b0), "b": r.x * scale,
                         "rmse_dfe": float(np.sqrt(2 * r.cost / (len(y) - len(b0))))})
        if best is None or r.cost < best.cost:
            best = r
    b = best.x * scale
    J = best.jac / scale
    n, npar = J.shape
    res = resid(b)
    mse = float(res @ res / (n - npar))
    cov = mse * np.linalg.inv(J.T @ J)
    se = np.sqrt(np.diag(cov))
    # identifiable combination when the catalyst dies early: ln(g0 / |k|) = b0 - ln(3600 |b6|)
    gr = np.zeros(npar)
    gr[0], gr[5] = 1.0, -1.0 / b[5]
    return {"b": b, "cov": cov, "se": se, "rmse": float(np.sqrt(mse)),
            "max_abs_residual": float(np.max(np.abs(res))), "n": n, "dfe": n - npar,
            "corr_b0_b6": float(cov[0, 5] / (se[0] * se[5])), "by_start": by_start,
            "ln_g0_over_k": float(b[0] - np.log(3600 * abs(b[5]))),
            "ln_g0_over_k_se": float(np.sqrt(gr @ cov @ gr))}


# ----------------------------------------------------------------------------- checks
def coef_check(name, ours, ref, rule):
    out = []
    for i, term in enumerate(ref["terms"]):
        rb, rse = ref["coefficients"][term]
        ob, ose = float(ours["b"][i]), float(ours["se"][i])
        if rule == "I_II_III":
            tol = max(0.10 * rse, 0.005 * abs(rb))
            tol_txt = "max(0.10 SE, 0.5 %)"
            se_tol = 0.05
        else:
            tol = 0.25 * rse
            tol_txt = "0.25 SE"
            se_tol = 0.15
        out.append({"check": f"{name} coefficient {term}", "reference": rb, "ours": ob,
                    "deviation": ob - rb, "tolerance": f"abs {tol:.4g} ({tol_txt})",
                    "pass": bool(abs(ob - rb) <= tol)})
        rel = (ose - rse) / rse
        out.append({"check": f"{name} SE {term}", "reference": rse, "ours": ose,
                    "deviation": rel, "tolerance": f"rel {se_tol}", "pass": bool(abs(rel) <= se_tol)})
    return out


def rel_check(label, ours, ref, tol):
    d = (ours - ref) / ref
    return {"check": label, "reference": ref, "ours": ours, "deviation": d,
            "tolerance": f"rel {tol}", "pass": bool(abs(d) <= tol)}


def abs_check(label, ours, ref, tol):
    d = ours - ref
    return {"check": label, "reference": ref, "ours": ours, "deviation": d,
            "tolerance": f"abs {tol}", "pass": bool(abs(d) <= tol)}


# ----------------------------------------------------------------------------- predictions
class Predictor:
    """Predictions of y = ln(average rate, mol/(L h)) and final yield for a run of duration t."""

    def __init__(self, fits: dict, iv_mode: str = "fitted"):
        self.f = fits
        self.iv_mode = iv_mode

    @staticmethod
    def _x(T_c, p, cat_mM, base_mM, t_h, S0):
        x1 = 1.0 / (np.asarray(T_c, float) + T_OFFSET)
        x2 = np.asarray(p, float)
        x3 = np.log(np.asarray(cat_mM, float) * 1e-3)
        x4 = np.log(np.asarray(base_mM, float) * 1e-3)
        return np.broadcast_arrays(x1, x2, x3, x4, np.asarray(t_h, float), np.asarray(S0, float))

    def leverage(self, model, T_c, p, cat_mM, base_mM, t_h):
        """h = x' (X'X)^-1 x against the model's fitting set (linear design of the regressors)."""
        x1, x2, x3, x4, t_h, _ = self._x(T_c, p, cat_mM, base_mM, t_h, 1.0)
        if model == "IV":
            X = design_iv(x1, x2, x3, x4, 3600.0 * t_h)
        else:
            X = design(x1, x2, x3, x4, TERMS_II if model == "II" else TERMS_III)
        return np.einsum("...i,ij,...j->...", X, self.f[model]["XtX_inv"], X)

    def predict(self, model, T_c, p, cat_mM, base_mM, t_h, S0):
        x1, x2, x3, x4, t_h, S0 = self._x(T_c, p, cat_mM, base_mM, t_h, S0)
        fit = self.f[model]
        if model in ("II", "III"):
            X = design(x1, x2, x3, x4, TERMS_II if model == "II" else TERMS_III)
            y = X @ fit["b"]
            var = np.einsum("...i,ij,...j->...", X, fit["cov"], X)
            yld = np.exp(y) * t_h / S0
            return y, np.sqrt(var), yld
        if self.iv_mode == "fitted":
            X = design_iv(x1, x2, x3, x4, 3600.0 * t_h)
            lng = X @ fit["b"]
            var_lng = np.einsum("...i,ij,...j->...", X, fit["cov"], X)
            gt = np.exp(lng) * t_h
            yld = gt / (1 + gt)
            y = lng + np.log(S0) - np.log1p(gt)
            return y, (1 - yld) * np.sqrt(var_lng), yld
        # integrated reading (coefficients refitted to that form): see integrated_iv
        def y_of(b):
            return integrated_iv(b, x1, x2, x3, x4, t_h, S0)
        y, yld = y_of(fit["b"])
        grad = []
        for j in range(len(fit["b"])):
            h = 1e-6 * max(abs(fit["b"][j]), 1e-6)
            bp = fit["b"].copy()
            bp[j] += h
            grad.append((y_of(bp)[0] - y) / h)
        G = np.stack(grad, axis=-1)
        var = np.einsum("...i,ij,...j->...", G, fit["cov"], G)
        return y, np.sqrt(var), yld


PAIRS = [("II", "III"), ("II", "IV"), ("III", "IV")]


def discrimination(pred: Predictor, sigma_m: float, grid: dict, S0: float, window,
                   t_max_iv: float = np.inf, hull: np.ndarray | None = None):
    T, P, C, B, t = np.meshgrid(grid["T"], grid["p"], grid["cat"], grid["base"], grid["t"],
                                indexing="ij")
    out = {m: pred.predict(m, T, P, C, B, t, S0) for m in ("II", "III", "IV")}
    D = {}
    for a, b in PAIRS:
        ya, sa, _ = out[a]
        yb, sb, _ = out[b]
        D[f"{a}-{b}"] = (ya - yb) ** 2 / (2 * sigma_m**2 + sa**2 + sb**2)
    Dmin = np.minimum.reduce(list(D.values()))
    feas = np.ones_like(Dmin, bool)
    for m in out:
        feas &= (out[m][2] >= window[0]) & (out[m][2] <= window[1])
    feas &= t <= t_max_iv
    if hull is not None:
        feas &= in_hull(hull, T / 100.0, t / 10.0)
    return {"axes": (T, P, C, B, t), "pred": out, "D": D, "Dmin": Dmin, "feasible": feas}


def convex_hull(points: np.ndarray) -> np.ndarray:
    """Monotone-chain convex hull, counter-clockwise, of 2-D points."""
    pts = sorted(set(map(tuple, np.round(points, 9))))
    def cross(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])
    lower, upper = [], []
    for pt in pts:
        while len(lower) >= 2 and cross(lower[-2], lower[-1], pt) <= 0:
            lower.pop()
        lower.append(pt)
    for pt in reversed(pts):
        while len(upper) >= 2 and cross(upper[-2], upper[-1], pt) <= 0:
            upper.pop()
        upper.append(pt)
    return np.array(lower[:-1] + upper[:-1])


def in_hull(hull: np.ndarray, x: np.ndarray, y: np.ndarray, eps: float = 1e-9) -> np.ndarray:
    inside = np.ones(np.shape(x), bool)
    n = len(hull)
    for k in range(n):
        (x0, y0), (x1, y1) = hull[k], hull[(k + 1) % n]
        inside &= (x1 - x0) * (y - y0) - (y1 - y0) * (x - x0) >= -eps
    return inside


def condition_record(pred, sigma_m, T, p, c, b, t, S0):
    rec = {"T_degC": float(T), "p_bar": float(p), "catalyst_mmol_per_L": float(c),
           "base_mmol_per_L": float(b), "run_time_h": float(t), "S0_mol_per_L": float(S0),
           "models": {}}
    ys = {}
    for m in ("II", "III", "IV"):
        y, s, yld = pred.predict(m, T, p, c, b, t, S0)
        ys[m] = (float(y), float(s))
        rec["models"][m] = {"y_ln_rate": float(y), "s_param": float(s),
                            "band_95_y": [float(y - 1.96 * np.hypot(s, sigma_m)),
                                          float(y + 1.96 * np.hypot(s, sigma_m))],
                            "rate_mol_per_L_h": float(np.exp(y)), "yield": float(yld)}
    rec["D"] = {f"{a}-{b_}": float((ys[a][0] - ys[b_][0]) ** 2 /
                                  (2 * sigma_m**2 + ys[a][1] ** 2 + ys[b_][1] ** 2))
                for a, b_ in PAIRS}
    rec["D_min"] = min(rec["D"].values())
    rec["D_limit_infinite_replicates"] = {
        f"{a}-{b_}": float((ys[a][0] - ys[b_][0]) ** 2 / (ys[a][1] ** 2 + ys[b_][1] ** 2))
        for a, b_ in PAIRS}
    rec["D_min_limit_infinite_replicates"] = min(rec["D_limit_infinite_replicates"].values())
    if all("XtX_inv" in pred.f[m] for m in ("II", "III", "IV")):
        lev = {}
        for m in ("II", "III", "IV"):
            h = float(pred.leverage(m, T, p, c, b, t))
            hmax = float(pred.f[m]["h_max_data"])
            lev[m] = {"h": h, "h_max_fitting_data": hmax, "hidden_extrapolation": bool(h > hmax)}
        rec["leverage"] = lev
    return rec


def t50(pred, model, T, p, c, b, S0, t_end=200.0):
    """Time to 50 % yield (h), or None if the model does not reach it before t_end."""
    ts = np.linspace(0.01, t_end, 20000)
    _, _, yld = pred.predict(model, T, p, c, b, ts, S0)
    idx = np.nonzero(yld >= 0.5)[0]
    return float(ts[idx[0]]) if idx.size else None


# ----------------------------------------------------------------------------- figures
def setup_mpl():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams.update({
        "svg.hashsalt": CASE_ID, "svg.fonttype": "path", "font.size": 9,
        "axes.edgecolor": INK2, "axes.labelcolor": INK, "xtick.color": INK2, "ytick.color": INK2,
        "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.6, "axes.axisbelow": True,
        "axes.spines.top": False, "axes.spines.right": False, "lines.linewidth": 2,
        "legend.frameon": False, "figure.facecolor": "white", "axes.facecolor": "white",
    })
    return plt


def save(fig, name):
    fig.savefig(RESULTS / name, format="svg", metadata={"Date": None}, bbox_inches="tight")
    preview = os.environ.get("CHEME_PREVIEW_DIR")   # optional PNG copies for review, outside git
    if preview:
        fig.savefig(Path(preview) / name.replace(".svg", ".png"), dpi=110, bbox_inches="tight")


def fig_parity(plt, data, fits, ref_fitted):
    fig, axes = plt.subplots(1, 3, figsize=(10, 3.4), sharex=True, sharey=True)
    for ax, m in zip(axes, ("II", "III", "IV")):
        idx = data["used"][m]
        y = data["y"][idx]
        yhat = fits[m]["fitted"]
        lo, hi = -11, 1
        ax.plot([lo, hi], [lo, hi], color=INK2, lw=1)
        ax.scatter(y, yhat, s=30, color=COLOURS[m], edgecolor="white", linewidth=1,
                   label="our refit", zorder=3)
        rr = ref_fitted[m]
        ax.scatter(rr["y"], rr["yhat"], s=40, marker="x", color=INK, linewidth=1,
                   label="SI fitted values", zorder=4)
        ax.set_title(f"Model {m} (n = {len(idx)})", color=INK, fontsize=10, loc="left")
        ax.set_xlabel("measured y = ln(rate / mol L$^{-1}$ h$^{-1}$)")
        ax.set_xlim(lo, hi)
        ax.set_ylim(lo, hi)
    axes[0].set_ylabel("fitted y")
    axes[0].legend(loc="upper left")
    fig.suptitle("Reproduction: refits of the published models to the 30-run table (SI S1/S2)",
                 x=0.02, y=1.04, ha="left", fontsize=10, color=INK)
    fig.text(0.02, -0.06, CREDIT.format(tables="Tables S1, S2, S10, S16, S21"), fontsize=7,
             color=INK2, ha="left")
    save(fig, "fig1_parity.svg")
    plt.close(fig)


def fig_kinetics(plt, kin, res):
    fig, axes = plt.subplots(1, 3, figsize=(10, 3.2))
    ax = axes[0]
    for key, lab, c in (("S23", "50 ppm", COLOURS["II"]), ("S24", "200 ppm", COLOURS["III"])):
        x = -1000 * kin[key][:, 0] / R_J
        ax.scatter(x, kin[key][:, 1], s=28, color=c, edgecolor="white", zorder=3)
        f = res[key]
        xs = np.linspace(x.min(), x.max(), 10)
        b0 = np.mean(kin[key][:, 1]) - f["Ea"] * np.mean(x)
        ax.plot(xs, b0 + f["Ea"] * xs, color=c, label=f"{lab}: Ea = {f['Ea']:.1f} ± {f['Ea_se']:.1f} kJ/mol")
    ax.set_xlabel("-1000/(RT) / mol kJ$^{-1}$")
    ax.set_ylabel("ln k (initial rate)")
    ax.legend(loc="lower right", fontsize=8)
    ax.set_title("(a) Arrhenius, SI S23/S24", loc="left", fontsize=10, color=INK)
    ax = axes[1]
    d = kin["S25"]
    ax.scatter(d[:, 0], d[:, 1], s=28, color=COLOURS["II"], edgecolor="white", zorder=3)
    for sl, key in ((slice(0, 4), "base_low"), (slice(4, 9), "base_high")):
        x = d[sl, 0]
        f = np.polyfit(x, d[sl, 1], 1)
        ax.plot(x, np.polyval(f, x), color=INK2, lw=1.5)
        ax.annotate(f"order {res[key]['slope']:.2f}", (x.mean(), np.polyval(f, x.mean())),
                    textcoords="offset points", xytext=(6, -14), fontsize=8, color=INK)
    ax.set_xlabel("ln(base / ppm)")
    ax.set_ylabel("ln(initial rate)")
    ax.set_title("(b) base order, SI S25", loc="left", fontsize=10, color=INK)
    ax = axes[2]
    d = kin["S26"]
    ax.scatter(d[:6, 0], d[:6, 1], s=28, color=COLOURS["II"], edgecolor="white", zorder=3)
    ax.scatter(d[6:, 0], d[6:, 1], s=28, facecolor="white", edgecolor=COLOURS["II"], zorder=3,
               label="not fitted (source)")
    f = np.polyfit(d[:6, 0], d[:6, 1], 1)
    ax.plot(d[:6, 0], np.polyval(f, d[:6, 0]), color=INK2, lw=1.5)
    ax.annotate(f"order {res['cat']['slope']:.2f}", (2.5, np.polyval(f, 2.5)),
                textcoords="offset points", xytext=(6, -14), fontsize=8, color=INK)
    ax.set_xlabel("ln(catalyst / ppm)")
    ax.set_title("(c) catalyst order, SI S26", loc="left", fontsize=10, color=INK)
    ax.legend(loc="lower right", fontsize=8)
    fig.suptitle("Separate initial-rate kinetics (same authors): our straight-line fits",
                 x=0.02, ha="left", fontsize=10, color=INK)
    fig.tight_layout()
    fig.text(0.02, -0.03, CREDIT.format(tables="Tables S23-S26"), fontsize=7, color=INK2,
             ha="left")
    save(fig, "fig3_conventional_kinetics.svg")
    plt.close(fig)


def fig_design(plt, pred, pred_int, sigma_m, run_a, run_b, S0, data, window, thr, t_max_iv, hull):
    def cond(r):
        return tuple(r[k] for k in ("T_degC", "p_bar", "catalyst_mmol_per_L", "base_mmol_per_L",
                                    "run_time_h"))

    def txt(r):
        T0, p0, c0, b0, t0 = cond(r)
        return f"{T0:.0f} °C, {p0:.0f} bar, cat {c0:.3g} mM, base {b0:.3g} mM, {t0:.0f} h"

    fig, axes = plt.subplots(2, 2, figsize=(10.5, 8.2))
    T0, p0, c0, b0, t0 = cond(run_a)

    def bands(ax, xs, kw, xlabel, xlog, xmark, levels):
        for m in ("II", "III", "IV"):
            args = dict(T_c=T0, p=p0, cat_mM=c0, base_mM=b0, t_h=t0, S0=S0)
            args.update({kw: xs})
            y, s, _ = pred.predict(m, **args)
            tot = np.hypot(s, sigma_m)
            ax.fill_between(xs, y - 1.96 * tot, y + 1.96 * tot, color=COLOURS[m], alpha=0.10, lw=0)
            ax.fill_between(xs, y - 1.96 * s, y + 1.96 * s, color=COLOURS[m], alpha=0.30, lw=0)
            ax.plot(xs, y, color=COLOURS[m], label=f"model {m}")
        ax.axvline(xmark, color=INK, lw=1, ls="--")
        for lv in levels:
            ax.axvline(lv, color=INK2, lw=0.6, ls=":")
        if xlog:
            ax.set_xscale("log")
        ax.set_xlabel(xlabel)
        ax.set_ylabel("predicted y = ln(rate / mol L$^{-1}$ h$^{-1}$)")

    xs = np.geomspace(0.0625, 12.5, 200)
    bands(axes[0, 0], xs, "base_mM", "KOtBu / mmol L$^{-1}$ (dotted: design levels)", True, b0,
          [0.0625, 6.28, 12.5])
    axes[0, 0].set_title(f"(a) run A ({txt(run_a)}): vs base", loc="left", fontsize=9, color=INK)
    axes[0, 0].legend(loc="lower right", fontsize=8)
    xs = np.linspace(30, 100, 200)
    bands(axes[0, 1], xs, "T_c", "temperature / °C (dotted: design levels)", False, T0,
          [30, 65, 100])
    out = ~in_hull(hull, xs / 100.0, np.full_like(xs, t0) / 10.0)
    edges = np.flatnonzero(np.diff(np.r_[0, out.astype(int), 0]))
    for i0, i1 in zip(edges[::2], edges[1::2]):
        axes[0, 1].axvspan(xs[i0], xs[i1 - 1], color=GRID, alpha=0.35, lw=0)
    axes[0, 1].set_title(f"(b) run A: vs temperature, other factors fixed;\n"
                         f"shaded: (T, t = {t0:.0f} h) outside the design runs",
                         loc="left", fontsize=9, color=INK)

    ax = axes[1, 0]
    Tg = np.linspace(30, 100, 71)
    Bg = np.geomspace(0.0625, 12.5, 81)
    TT, BB = np.meshgrid(Tg, Bg, indexing="ij")
    pa = {m: pred.predict(m, TT, p0, c0, BB, t0, S0) for m in ("II", "III", "IV")}
    D23 = (pa["II"][0] - pa["III"][0]) ** 2 / (2 * sigma_m**2 + pa["II"][1] ** 2 + pa["III"][1] ** 2)
    feas = np.ones_like(D23, bool)
    for m in pa:
        feas &= (pa[m][2] >= window[0]) & (pa[m][2] <= window[1])
    feas &= in_hull(hull, TT / 100.0, np.full_like(TT, t0) / 10.0)
    cs = ax.contourf(BB, TT, np.clip(D23, 0, 8), levels=[0, 0.5, 1, 2, 3, 4, 6, 8],
                     cmap="Blues", extend="max")
    ax.contourf(BB, TT, (~feas).astype(float), levels=[0.5, 1.5], colors="none", hatches=["////"])
    ax.contour(BB, TT, D23, levels=[thr], colors=INK, linewidths=1)
    ax.scatter(np.exp(data["x4"]) * 1e3, data["T_c"], s=22, marker="s",
               facecolor="white", edgecolor=INK, zorder=3, label="design runs")
    ax.scatter([b0], [T0], s=110, marker="*", color=COLOURS["IV"], edgecolor=INK, zorder=4,
               label="run A")
    ax.set_xscale("log")
    ax.set_xlabel("KOtBu / mmol L$^{-1}$")
    ax.set_ylabel("temperature / °C")
    ax.grid(False)
    cb = fig.colorbar(cs, ax=ax)
    cb.set_label("D(II, III); black line D = 4")
    ax.legend(loc="lower right", fontsize=8, frameon=True, facecolor="white", edgecolor=GRID,
              framealpha=1)
    ax.set_title(f"(c) II vs III at {p0:.0f} bar, cat {c0:.3g} mM, {t0:.0f} h;\n"
                 "hatched: yield outside 2-90 % or (T, t) outside the design runs",
                 loc="left", fontsize=9, color=INK)

    ax = axes[1, 1]
    T1, p1, c1, b1, t1 = cond(run_b)
    ts = np.linspace(0.25, 24, 300)
    for m in ("II", "III", "IV"):
        _, _, yld = pred.predict(m, T1, p1, c1, b1, ts, S0)
        lo, hi = band_yield(pred, m, T1, p1, c1, b1, ts, S0, np.random.default_rng(SEED))
        ax.fill_between(ts, lo, hi, color=COLOURS[m], alpha=0.25, lw=0)
        ax.plot(ts, np.minimum(yld, 1.2), color=COLOURS[m], label=f"model {m}")
    yi = pred_int.predict("IV", T1, p1, c1, b1, ts, S0)[2]
    ax.plot(ts, yi, color=COLOURS["IV"], ls=(0, (4, 2)), lw=1.5,
            label="model IV, integrated form (refitted)")
    ax.axvspan(t_max_iv, ts.max(), color=GRID, alpha=0.35, lw=0)
    ax.annotate(f"model IV as fitted:\nyield falls after {t_max_iv:.1f} h\n(excluded)",
                (t_max_iv + 0.6, 0.05), fontsize=8, color=INK2)
    ax.axvline(t1, color=INK, lw=1, ls="--")
    ax.axhline(window[1], color=INK2, lw=0.8, ls=":")
    ax.set_ylim(0, 1.45)
    ax.set_xlabel("run time / h")
    ax.set_ylabel("predicted yield")
    ax.set_title(f"(d) run B ({txt(run_b)}):\nyield vs run time, 95 % parameter band",
                 loc="left", fontsize=9, color=INK)
    ax.legend(loc="upper center", fontsize=8, ncol=2)
    fig.suptitle("Hypothetical design extension: two runs that separate models II, III and IV "
                 "(bands: dark = parameter 95 %, light = with measurement σ)",
                 x=0.02, ha="left", fontsize=10, color=INK)
    fig.tight_layout()
    fig.text(0.02, -0.015, CREDIT.format(tables="Tables S1, S2; models refitted to them"),
             fontsize=7, color=INK2, ha="left")
    save(fig, "fig2_discrimination.svg")
    plt.close(fig)


def band_yield(pred, m, T, p, c, b, ts, S0, rng, n=1000):
    fit = pred.f[m]
    draws = rng.multivariate_normal(fit["b"], fit["cov"], size=n)
    out = []
    for d in draws:
        tmp = Predictor({m: {"b": d, "cov": np.zeros_like(fit["cov"])}})
        out.append(tmp.predict(m, T, p, c, b, ts, S0)[2])
    out = np.minimum(np.array(out), 1.2)
    return np.percentile(out, 2.5, axis=0), np.percentile(out, 97.5, axis=0)


# ----------------------------------------------------------------------------- main
def to_builtin(o):
    if isinstance(o, dict):
        return {k: to_builtin(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [to_builtin(v) for v in o]
    if isinstance(o, np.ndarray):
        return to_builtin(o.tolist())
    if isinstance(o, (np.floating, float)):
        return float(f"{float(o):.6g}")
    if isinstance(o, (np.integer,)):
        return int(o)
    if isinstance(o, np.bool_):
        return bool(o)
    return o


def main() -> int:
    src = yaml.safe_load((HERE / "source.yaml").read_text())
    inp = yaml.safe_load((HERE / "inputs.yaml").read_text())
    tolfile = HERE / "tolerances.yaml"
    tol = yaml.safe_load(tolfile.read_text())
    RESULTS.mkdir(exist_ok=True)

    si = parse_si(fetch(src["reference"]["files"][0]))
    s1, s2 = si["S1"], si["S2"]
    T_c, cat_raw, base_raw, p_raw, t_h, rate, yld_pct = s1.T
    x1, x2, x3, x4, _ = s2.T
    y = np.log(rate)
    if not (np.allclose(x2, p_raw) and np.allclose(1 / x1 - T_OFFSET, T_c, atol=0.1)):
        raise SystemExit("SI Tables S1 and S2 are not consistent")
    runs = np.arange(1, 31)
    S0_run = rate * t_h / (yld_pct / 100)
    S_end = S0_run * (1 - yld_pct / 100)
    S0_nom = float(np.median(S0_run))

    excl = {"I": [], "II": [14, 20, 22, 30], "III": [7, 16, 20, 22, 28, 30],
            "IV": [7, 10, 22, 25, 28, 30], "III_S16": [7, 16, 20, 22, 30]}
    used = {k: np.array([r - 1 for r in runs if r not in v]) for k, v in excl.items()}

    fits = {}
    for m, terms in (("I", TERMS_I), ("II", TERMS_II), ("III", TERMS_III), ("III_S16", TERMS_III)):
        idx = used[m]
        fits[m] = ols(design(x1[idx], x2[idx], x3[idx], x4[idx], terms), y[idx])
    idx = used["IV"]
    Xiv = design_iv(x1[idx], x2[idx], x3[idx], x4[idx], 3600 * t_h[idx])
    fiv = bisquare_irls(Xiv, y[idx] - np.log(S_end[idx]))
    fiv["fitted"] = fiv["fitted_lin"] + np.log(S_end[idx])
    fits["IV"] = fiv
    # leverage reference: (X'X)^-1 of each model's fitting set and the largest data leverage
    for m in ("II", "III", "IV"):
        i = used[m]
        Xm = Xiv if m == "IV" else design(x1[i], x2[i], x3[i], x4[i],
                                           TERMS_II if m == "II" else TERMS_III)
        fits[m]["XtX_inv"] = np.linalg.inv(Xm.T @ Xm)
        hd = np.einsum("ij,jk,ik->i", Xm, fits[m]["XtX_inv"], Xm)
        fits[m]["h_max_data"] = float(hd.max())
        fits[m]["h_max_data_run"] = int(runs[i][np.argmax(hd)])
    # model IV read as the integrated rate law (sensitivity): reused coefficients vs a refit
    y_iv_reused = integrated_iv(fiv["b"], x1[idx], x2[idx], x3[idx], x4[idx], t_h[idx],
                                S0_run[idx])[0]
    b_start0 = fiv["b"].copy()
    b_start0[5] = 0.0
    fint = fit_integrated_iv(x1[idx], x2[idx], x3[idx], x4[idx], t_h[idx], S0_run[idx], y[idx],
                             [fiv["b"], b_start0])
    fint["XtX_inv"] = fiv["XtX_inv"]
    fint["h_max_data"] = fiv["h_max_data"]
    fiv_as_fitted_res = y[idx] - fiv["fitted"]
    integrated_record = {
        "form": "y = ln(S0 Y / t), Y = 1 - exp(-g0 expm1(k t) / k), k = 3600 b6 (source Eq. 14 integrated)",
        "runs": [int(r) for r in runs[idx]],
        "as_fitted_form_rmse_vs_measured_y": float(np.sqrt(np.mean(fiv_as_fitted_res**2))),
        "as_fitted_form_max_abs_residual": float(np.max(np.abs(fiv_as_fitted_res))),
        "reused_coefficients_rmse_vs_measured_y": float(np.sqrt(np.mean((y[idx] - y_iv_reused) ** 2))),
        "reused_coefficients_max_abs_residual": float(np.max(np.abs(y[idx] - y_iv_reused))),
        "refit_method": "unweighted nonlinear least squares (Levenberg-Marquardt), same 24 runs, "
                        "per-run reconstructed S0",
        "refit_terms": TERMS_IV, "refit_b": fint["b"], "refit_se": fint["se"],
        "refit_rmse_dfe": fint["rmse"], "refit_dfe": fint["dfe"],
        "refit_rmse_vs_measured_y": float(fint["rmse"] * np.sqrt(fint["dfe"] / fint["n"])),
        "refit_max_abs_residual": fint["max_abs_residual"],
        "refit_deactivation_time_constant_h": float(-1 / (3600 * fint["b"][5])),
        "refit_corr_intercept_b6": fint["corr_b0_b6"],
        "refit_ln_g0_over_k": fint["ln_g0_over_k"], "refit_ln_g0_over_k_se": fint["ln_g0_over_k_se"],
        "refit_by_start": fint["by_start"],
        "reading": "the refit is not identifiable: the catalyst dies within about 0.3 h, so every run "
                   "is read as finished long before it was stopped and only ln(g0/|k|) (the final "
                   "yield) is determined; the run-time term then acts as a pure 1/t. Linear "
                   "prediction variances are meaningless, so no D values are computed from this "
                   "reading; only point predictions are reported",
    }
    # sensitivity: regressors from raw Table S1 levels
    x3r, x4r = np.log(cat_raw * 1e-3), np.log(base_raw * 1e-3)
    sens_raw = {}
    for m, terms in (("I", TERMS_I), ("II", TERMS_II), ("III", TERMS_III)):
        i = used[m]
        sens_raw[m] = ols(design(x1[i], x2[i], x3r[i], x4r[i], terms), y[i])

    # ------------------------------------------------------------------ checks
    rr = src["reported_results"]
    checks = []
    checks.append({"check": "run count", "reference": 30, "ours": int(s1.shape[0]),
                   "deviation": 0, "tolerance": "exact", "pass": s1.shape[0] == 30,
                   "group": "data_integrity"})
    dev_y = max(np.max(np.abs(si["S6"][:, 1] - y)),
                np.max(np.abs(si["S10"][:, 2] - y[si["S10"][:, 0].astype(int) - 1])),
                np.max(np.abs(si["S16"][:, 2] - y[si["S16"][:, 0].astype(int) - 1])),
                np.max(np.abs(si["S21"][:, 1] - y[si["S21"][:, 0].astype(int) - 1])))
    checks.append({"check": "ln(S1 rate) vs y of S6/S10/S16/S21 (max abs)", "reference": 0.0,
                   "ours": float(dev_y), "deviation": float(dev_y), "tolerance": "abs 1e-4",
                   "pass": bool(dev_y <= 1e-4), "group": "data_integrity"})
    centre = np.array([0, 1, 2, 3, 4, 10])
    pe_ms = float(np.var(y[centre], ddof=1))
    c = rel_check("pure-error mean square, centre runs 1-5, 11", pe_ms, rr["model_I"]["pure_error_ms"], 0.01)
    c["group"] = "data_integrity"
    checks.append(c)

    ref_fitted = {
        "I": {"runs": runs, "yhat": si["S6"][:, 0], "y": si["S6"][:, 1]},
        "II": {"runs": si["S10"][:, 0].astype(int), "yhat": si["S10"][:, 1], "y": si["S10"][:, 2]},
        "III": {"runs": si["S16"][:, 0].astype(int), "yhat": si["S16"][:, 1], "y": si["S16"][:, 2]},
        "IV": {"runs": si["S21"][:, 0].astype(int), "yhat": si["S21"][:, 2], "y": si["S21"][:, 1]},
    }

    def ours_fitted_at(m, rr_runs):
        f = fits[m]
        r = rr_runs - 1
        if m == "IV":
            X = design_iv(x1[r], x2[r], x3[r], x4[r], 3600 * t_h[r])
            return X @ f["b"] + np.log(S_end[r])
        terms = {"I": TERMS_I, "II": TERMS_II, "III": TERMS_III}[m]
        return design(x1[r], x2[r], x3[r], x4[r], terms) @ f["b"]

    for m, key, terms, grp in (("I", "model_I", TERMS_I, "model_I"),
                               ("II", "model_II", TERMS_II, "models_II_III"),
                               ("III", "model_III", TERMS_III, "models_II_III")):
        ref = dict(rr[key], terms=terms)
        for c in coef_check(f"model {m}", fits[m], ref, "I_II_III"):
            c["group"] = grp
            checks.append(c)
        for lab, ours, refv, kind, t in (("RMSE", fits[m]["rmse"], ref["rmse"], "rel", 0.02),
                                         ("R2", fits[m]["r2"], ref["r2"], "abs", 0.002),
                                         ("PRESS", fits[m]["press"], ref["press"], "rel", 0.02)):
            c = (rel_check if kind == "rel" else abs_check)(f"model {m} {lab}", ours, refv, t)
            c["group"] = grp
            checks.append(c)
        rf = ref_fitted[m]
        d = float(np.max(np.abs(ours_fitted_at(m, rf["runs"]) - rf["yhat"])))
        checks.append({"check": f"model {m} fitted values vs SI (max abs, {len(rf['runs'])} runs)",
                       "reference": 0.0, "ours": d, "deviation": d, "tolerance": "abs 0.02",
                       "pass": bool(d <= 0.02), "group": grp})
    ref = dict(rr["model_IV"], terms=TERMS_IV)
    for c in coef_check("model IV", fits["IV"], ref, "IV"):
        c["group"] = "model_IV"
        checks.append(c)
    c = rel_check("model IV RMSE (weighted)", fits["IV"]["rmse"], ref["rmse"], 0.10)
    c["group"] = "model_IV"
    checks.append(c)
    rf = ref_fitted["IV"]
    d = float(np.max(np.abs(ours_fitted_at("IV", rf["runs"]) - rf["yhat"])))
    checks.append({"check": "model IV fitted values vs SI (max abs, 24 runs)", "reference": 0.0,
                   "ours": d, "deviation": d, "tolerance": "abs 0.05", "pass": bool(d <= 0.05),
                   "group": "model_IV"})

    kin_res = {}
    ck = rr["conventional_kinetics"]
    for key, refkey in (("S23", "Ea_50ppm"), ("S24", "Ea_200ppm")):
        f = line_fit(-1000 * si[key][:, 0] / R_J, si[key][:, 1])
        kin_res[key] = {"Ea": f["slope"], "Ea_se": f["slope_se"], "r2": f["r2"]}
        for lab, ours, refv, t in (("Ea", f["slope"], ck[refkey]["value"], 1.0),
                                   ("Ea SE", f["slope_se"], ck[refkey]["se"], 1.0),
                                   ("r2", f["r2"], ck[refkey]["r2"], 0.006)):
            c = abs_check(f"conventional {refkey} {lab}", ours, refv, t)
            c["group"] = "conventional_kinetics"
            checks.append(c)
    for key, sl, tab, refkey in (("base_low", slice(0, 4), "S25", "base_order_low"),
                                 ("base_high", slice(4, 9), "S25", "base_order_high"),
                                 ("cat", slice(0, 6), "S26", "catalyst_order")):
        f = line_fit(si[tab][sl, 0], si[tab][sl, 1])
        kin_res[key] = f
        c = abs_check(f"conventional {refkey}", f["slope"], ck[refkey]["value"], 0.15)
        c["group"] = "conventional_kinetics"
        checks.append(c)

    def group_pass(groups):
        sel = [c for c in checks if c["group"] in groups]
        return all(c["pass"] for c in sel)

    all_pass = all(c["pass"] for c in checks)
    core_pass = group_pass({"data_integrity", "models_II_III", "conventional_kinetics"})
    verdict = "pass" if all_pass else ("partial" if core_pass else "fail")
    n_pass = sum(c["pass"] for c in checks)

    first_stage = {}
    for m, terms, tab in (("II", TERMS_II, "S10"), ("III", TERMS_III, "S16")):
        X30 = design(x1, x2, x3, x4, terms)
        f30 = ols(X30, y)
        r = si[tab][:, 0].astype(int) - 1
        dev = float(np.max(np.abs(X30[r] @ f30["b"] - si[tab][:, 1])))
        first_stage[m] = {"fit_on_all_30_runs_b": f30["b"], "fitted_vs_SI_table_max_abs": dev}
    sensitivity = {
        "si_fitted_value_tables_vs_first_stage_fit_on_30_runs": first_stage,
        "model_III_S16_set_25_runs": {"terms": TERMS_III, "b": fits["III_S16"]["b"],
                                      "se": fits["III_S16"]["se"], "rmse": fits["III_S16"]["rmse"],
                                      "fitted_vs_S16_max_abs": float(np.max(np.abs(
                                          design(x1, x2, x3, x4, TERMS_III)[ref_fitted["III"]["runs"] - 1]
                                          @ fits["III_S16"]["b"] - ref_fitted["III"]["yhat"])))},
        "raw_levels": {m: {"b": sens_raw[m]["b"], "rmse": sens_raw[m]["rmse"]} for m in sens_raw},
        "model_IV_rmse_unweighted": fits["IV"]["rmse_unweighted"],
        "model_IV_matlab_robust_sigma": {
            "note": "non-gating: MATLAB robustfit/statrobustsigma convention applied to our final "
                    "bisquare weights; the frozen RMSE check still compares the weighted RMSE",
            **fits["IV"]["matlab_convention"],
            "reference_rmse": rr["model_IV"]["rmse"],
            "s_deviation_rel": fits["IV"]["matlab_convention"]["s"] / rr["model_IV"]["rmse"] - 1,
            "se_scaled": fits["IV"]["se"] * np.sqrt(fits["IV"]["matlab_convention"]["cov_scale"]),
            "se_scaled_deviation_rel_vs_SI": [
                float(fits["IV"]["se"][j] * np.sqrt(fits["IV"]["matlab_convention"]["cov_scale"])
                      / rr["model_IV"]["coefficients"][t][1] - 1) for j, t in enumerate(TERMS_IV)],
        },
        "near_complete_runs_yield_ge_87pct": {
            "runs": [int(r) for r in runs[yld_pct >= 87]],
            "yield_pct": yld_pct[yld_pct >= 87],
            "in_fitting_set": {m: [int(r) for r in runs[used[m]] if yld_pct[r - 1] >= 87]
                               for m in ("II", "III", "IV")},
            "note": "average rates of near-complete runs are lower bounds on the rate; the source "
                    "regressed on them",
        },
        "model_IV_end_substrate_mass_balance": {
            "note": "S_end reconstructed as S0 (1 - Y), i.e. 100 % mass balance; the source used "
                    "GC-measured S_end and reports mass balances of 90-110 %. Shift of x5 = ln S_end "
                    "if 10 % of S0 is added to S_end (the downward shift is unbounded at Y >= 0.9)",
            "runs": [int(r) for r in runs[used["IV"]]],
            "yield": yld_pct[used["IV"]] / 100,
            "dx5_plus_10pct_S0": np.log1p(0.1 / (1 - yld_pct[used["IV"]] / 100)),
        },
        "model_IV_zero_weight_runs": [int(runs[used["IV"]][i]) for i in
                                      np.nonzero(fits["IV"]["weights"] == 0)[0]],
    }

    # ------------------------------------------------------------------ discrimination design
    dd = inp["discrimination_design"]
    sigma_m = float(dd["measurement_resolution_sigma_y"]["value"])
    sigma_m_ours = float(np.sqrt(pe_ms))
    thr = float(dd["discrimination_threshold"]["value"])
    window = tuple(dd["measurable_yield_window"]["value"])
    fits3 = {m: fits[m] for m in ("II", "III", "IV")}
    pred = Predictor(fits3, "fitted")
    pred_int = Predictor({**fits3, "IV": fint}, "integrated")
    t_max_iv = float(-1 / (3600 * fits["IV"]["b"][5]))   # h; model IV (as fitted) yield peaks here
    g = dd["grid"]
    grid = {"T": np.array(g["temperature_degC"], float), "p": np.array(g["pressure_bar"], float),
            "cat": np.geomspace(0.0625, 0.25, 7), "base": np.geomspace(0.0625, 12.5, 15),
            "t": np.array(g["run_time_h"], float)}

    # joint (temperature, run time) support of the 30 design runs, scaled to similar magnitudes
    hull = convex_hull(np.column_stack([T_c / 100.0, t_h / 10.0]))   # S1 set points
    hull_txt = [[float(round(a * 100, 2)), float(round(b * 10, 2))] for a, b in hull]

    def search(pr, sm, tmax, ntop=10, hl=hull):
        dis = discrimination(pr, sm, grid, S0_nom, window, tmax, hl)
        Dm = np.where(dis["feasible"], dis["Dmin"], -1)
        T, P, C, B, Tt = dis["axes"]
        top = []
        for flat in np.argsort(Dm, axis=None, kind="stable")[::-1][:ntop]:
            i = np.unravel_index(flat, Dm.shape)
            top.append(condition_record(pr, sm, T[i], P[i], C[i], B[i], Tt[i], S0_nom))
        pair_best = {}
        for k, Dk in dis["D"].items():
            D2 = np.where(dis["feasible"], Dk, -1)
            i = np.unravel_index(np.argmax(D2), D2.shape)
            pair_best[k] = {"T_degC": T[i], "p_bar": P[i], "catalyst_mmol_per_L": C[i],
                            "base_mmol_per_L": B[i], "run_time_h": Tt[i], "D": D2[i]}
        return {"top": top, "pair_best": pair_best, "grid_points": int(Dm.size),
                "feasible_points": int(dis["feasible"].sum()),
                "feasible_points_with_D_min_ge_threshold":
                    int((dis["feasible"] & (dis["Dmin"] >= thr)).sum())}

    def brief(rec):
        keys = ("T_degC", "p_bar", "catalyst_mmol_per_L", "base_mmol_per_L", "run_time_h", "D_min")
        return {k: rec[k] for k in keys}

    main_s = search(pred, sigma_m, t_max_iv)
    best = main_s["top"][0]
    dis_m = discrimination(pred, sigma_m, grid, S0_nom, window, t_max_iv, hull)
    Dinf = np.minimum.reduce([(dis_m["pred"][a][0] - dis_m["pred"][b][0]) ** 2 /
                              (dis_m["pred"][a][1] ** 2 + dis_m["pred"][b][1] ** 2)
                              for a, b in PAIRS])
    Dinf_best_feasible = float(np.max(np.where(dis_m["feasible"], Dinf, -1)))

    def replicates_needed(rec, target):
        """Smallest number of replicate runs n <= 12 for which every pair reaches D >= target."""
        for n in range(1, 13):
            ok = True
            for a, b in PAIRS:
                ma, mb = rec["models"][a], rec["models"][b]
                d = (ma["y_ln_rate"] - mb["y_ln_rate"]) ** 2 / (
                    2 * sigma_m**2 / n + ma["s_param"] ** 2 + mb["s_param"] ** 2)
                ok &= d >= target
            if ok:
                return n
        return None

    # two-run design: run A for the hardest pair (II-III), run B for model IV against both
    dis = discrimination(pred, sigma_m, grid, S0_nom, window, t_max_iv, hull)
    T, P, C, B, Tt = dis["axes"]

    def best_of(score):
        sc = np.where(dis["feasible"], score, -1)
        i = np.unravel_index(np.argmax(sc), sc.shape)
        return condition_record(pred, sigma_m, T[i], P[i], C[i], B[i], Tt[i], S0_nom)

    run_a = best_of(dis["D"]["II-III"])
    run_b = best_of(np.minimum(dis["D"]["II-IV"], dis["D"]["III-IV"]))
    two_run = {"run_A": run_a, "run_B": run_b,
               "D_pair_best_of_two": {k: max(run_a["D"][k], run_b["D"][k]) for k in run_a["D"]}}
    two_run["D_min"] = min(two_run["D_pair_best_of_two"].values())
    two_run["separates_all_pairs"] = bool(two_run["D_min"] >= thr)
    two_run["run_A_replicates_for_II_III_D_ge_9"] = None
    ma, mb = run_a["models"]["II"], run_a["models"]["III"]
    for n in range(1, 13):
        if (ma["y_ln_rate"] - mb["y_ln_rate"]) ** 2 / (2 * sigma_m**2 / n + ma["s_param"] ** 2
                                                       + mb["s_param"] ** 2) >= 9.0:
            two_run["run_A_replicates_for_II_III_D_ge_9"] = n
            break
    two_run["run_A_II_III_D_limit_infinite_replicates"] = float(
        (ma["y_ln_rate"] - mb["y_ln_rate"]) ** 2 / (ma["s_param"] ** 2 + mb["s_param"] ** 2))
    two_run["model_IV_integrated_reading_refit"] = integrated_record
    def int_point(r):
        y_, _, yl_ = pred_int.predict("IV", r["T_degC"], r["p_bar"], r["catalyst_mmol_per_L"],
                                      r["base_mmol_per_L"], r["run_time_h"], S0_nom)
        return {"y_ln_rate": float(y_), "rate_mol_per_L_h": float(np.exp(y_)), "yield": float(yl_),
                "note": "point prediction only (refit not identifiable, no D)"}

    two_run["run_A_model_IV_integrated_refit"] = int_point(run_a)
    two_run["run_B_model_IV_integrated_refit"] = int_point(run_b)

    dis_nh = discrimination(pred, sigma_m, grid, S0_nom, window, t_max_iv, None)
    outside = dis_nh["feasible"] & ~in_hull(hull, T / 100.0, Tt / 10.0)
    sc = np.where(outside, np.minimum(dis_nh["D"]["II-IV"], dis_nh["D"]["III-IV"]), -1)
    i = np.unravel_index(np.argmax(sc), sc.shape)
    run_b_outside_hull = condition_record(pred, sigma_m, T[i], P[i], C[i], B[i], Tt[i], S0_nom)
    run_b_outside_hull["extrapolated_factors"] = ["temperature-run time combination"]
    sens = {
        "run_B_outside_design_T_t_hull": run_b_outside_hull,
        "no_T_t_hull_restriction": brief(search(pred, sigma_m, t_max_iv, 1, None)["top"][0]),
        "no_run_time_limit_for_model_IV": brief(search(pred, sigma_m, np.inf, 1)["top"][0]),
        "single_run_model_IV_integrated_refit": int_point(best),
    }
    # model IV covariance scaled to MATLAB's robust sigma (non-gating sensitivity)
    fiv_m = dict(fits["IV"], cov=fits["IV"]["cov"] * fits["IV"]["matlab_convention"]["cov_scale"])
    pred_m = Predictor({**fits3, "IV": fiv_m}, "fitted")
    rec_m = {k: condition_record(pred_m, sigma_m, r["T_degC"], r["p_bar"], r["catalyst_mmol_per_L"],
                                 r["base_mmol_per_L"], r["run_time_h"], S0_nom)["D"]
             for k, r in (("run_A", run_a), ("run_B", run_b), ("single_best", best))}
    best_m = search(pred_m, sigma_m, t_max_iv, 1)["top"][0]
    sens["model_IV_cov_matlab_sigma"] = {
        "cov_scale": fits["IV"]["matlab_convention"]["cov_scale"], "D_at": rec_m,
        "two_run_D_min": min(max(rec_m["run_A"][k], rec_m["run_B"][k]) for k in rec_m["run_A"]),
        "best_single_run": brief(best_m)}
    sel_sigma = {f"{sm:.4g}": brief(search(pred, sm, t_max_iv, 1)["top"][0]) for sm in (0.1, 0.4)}
    sel_sigma[f"{sigma_m:.4g}"] = brief(best)

    existing = []
    for r in range(30):
        rec = condition_record(pred, sigma_m, 1 / x1[r] - T_OFFSET, x2[r], np.exp(x3[r]) * 1e3,
                               np.exp(x4[r]) * 1e3, t_h[r], S0_nom)
        existing.append({"run": r + 1, "run_time_h": float(t_h[r]), "D_min": rec["D_min"],
                         "D": rec["D"], "within_model_IV_time_limit": bool(t_h[r] <= t_max_iv)})
    best_existing = max((e for e in existing if e["within_model_IV_time_limit"]),
                        key=lambda e: e["D_min"])

    args = (run_a["T_degC"], run_a["p_bar"], run_a["catalyst_mmol_per_L"],
            run_a["base_mmol_per_L"], run_a["run_time_h"], S0_nom)
    rng = np.random.default_rng(SEED)
    mc = {}
    for m in ("II", "III", "IV"):
        dr = rng.multivariate_normal(fits[m]["b"], fits[m]["cov"], size=4000)
        ys = np.array([Predictor({m: {"b": d, "cov": np.zeros_like(fits[m]["cov"])}}).predict(m, *args)[0]
                       for d in dr])
        mc[m] = {"s_linear": run_a["models"][m]["s_param"], "s_monte_carlo": float(np.std(ys)),
                 "mean_linear": run_a["models"][m]["y_ln_rate"], "mean_monte_carlo": float(np.mean(ys))}
    t50s = {m: t50(pred, m, *args[:4], S0_nom, t_end=t_max_iv if m == "IV" else 200.0)
            for m in ("II", "III", "IV")}
    t50s["IV_integrated"] = t50(pred_int, "IV", *args[:4], S0_nom)
    ts = np.linspace(0.01, 200, 20000)
    yiv = pred.predict("IV", *args[:4], ts, S0_nom)[2]
    yiv_int = pred_int.predict("IV", *args[:4], ts, S0_nom)[2]
    iv_max = {"as_fitted_max_yield": float(yiv.max()), "as_fitted_at_h": float(ts[np.argmax(yiv)]),
              "t_max_h": t_max_iv, "integrated_yield_limit_200h": float(yiv_int[-1])}

    # extrapolation grid (one step beyond each bound, and substrate changed)
    eg = dd["extrapolation_grid"]
    Tx = list(grid["T"]) + eg["temperature_degC"]
    Px = list(grid["p"]) + eg["pressure_bar"]
    Cx = list(grid["cat"]) + eg["catalyst_mmol_per_L"]
    Bx = list(grid["base"]) + eg["base_mmol_per_L"]
    Sx = [1.0] + eg["substrate_factor"]
    TT, PP, CC, BB, tt, SS = np.meshgrid(Tx, Px, Cx, Bx, grid["t"], Sx, indexing="ij")
    S0g = SS * S0_nom
    outs = {m: pred.predict(m, TT, PP, CC, BB, tt, S0g) for m in ("II", "III", "IV")}
    Dl = [(outs[a][0] - outs[b][0]) ** 2 / (2 * sigma_m**2 + outs[a][1] ** 2 + outs[b][1] ** 2)
          for a, b in PAIRS]
    Dmx = np.minimum.reduce(Dl)
    fe = tt <= t_max_iv
    fe &= in_hull(hull, TT / 100.0, tt / 10.0) | (TT > 100)
    for m in outs:
        fe &= (outs[m][2] >= window[0]) & (outs[m][2] <= window[1])
    extrap = (TT > 100) | (PP > 50) | (CC > 0.25 + 1e-9) | (BB > 12.5 + 1e-9) | (SS != 1.0)
    D3 = np.where(fe & extrap, Dmx, -1)
    i = np.unravel_index(np.argmax(D3), D3.shape)
    flags = [n for n, f in (("temperature", TT[i] > 100), ("pressure", PP[i] > 50),
                            ("catalyst", CC[i] > 0.25 + 1e-9), ("base", BB[i] > 12.5 + 1e-9),
                            ("substrate", SS[i] != 1.0)) if f]
    best_ext = condition_record(pred, sigma_m, TT[i], PP[i], CC[i], BB[i], tt[i], S0g[i])
    best_ext["extrapolated_factors"] = flags

    # changed input: substrate halved at run A (extrapolation in substrate)
    changed = condition_record(pred, sigma_m, *args[:5], 0.5 * S0_nom)
    changed["extrapolated_factors"] = ["substrate"]

    extension = {
        "label": "HYPOTHETICAL design extension (not validated)",
        "sigma_y_measurement": sigma_m, "sigma_y_from_centre_runs": sigma_m_ours,
        "threshold_D": thr, "yield_window": window, "S0_nominal_mol_per_L": S0_nom,
        "S0_reconstructed_range": [float(S0_run.min()), float(S0_run.max())],
        "model_IV_run_time_limit_h": t_max_iv,
        "design_T_t_hull_degC_h": hull_txt,
        "grid_points": main_s["grid_points"], "feasible_points": main_s["feasible_points"],
        "feasible_points_with_D_min_ge_threshold": main_s["feasible_points_with_D_min_ge_threshold"],
        "selected_single_run": best,
        "single_run_replicates_for_D_min_ge_threshold": replicates_needed(best, thr),
        "single_run_replicates_searched_up_to": 12,
        "D_min_limit_infinite_replicates_best_feasible_grid_point": Dinf_best_feasible,
        "leverage_max_fitting_data": {m: {"h": fits[m]["h_max_data"], "run": fits[m]["h_max_data_run"]}
                                      for m in ("II", "III", "IV")},
        "two_run_design": two_run,
        "top10": main_s["top"], "best_per_pair": main_s["pair_best"],
        "selection_vs_sigma": sel_sigma, "sensitivity": sens,
        "at_run_A": {"monte_carlo_check": mc, "time_to_50pct_yield_h": t50s,
                     "model_IV_yield_limits": iv_max},
        "best_existing_run": best_existing,
        "existing_runs": existing, "best_extrapolated": best_ext,
        "changed_input_substrate_halved": changed,
    }

    comparison = {
        "case": CASE_ID, "issue": 341, "tracker": 333,
        "tolerances_file": tolfile.name, "tolerances_frozen": tol["frozen"],
        "source_file_sha256": src["reference"]["files"][0]["sha256"],
        "versions": {"python": sys.version.split()[0], "numpy": np.__version__,
                     "pypdf": __import__("pypdf").__version__,
                     "scipy": __import__("scipy").__version__,
                     "matplotlib": __import__("matplotlib").__version__},
        "verdict": verdict, "checks_passed": n_pass, "checks_total": len(checks),
        "checks": checks,
        "fits": {m: {"terms": {"I": TERMS_I, "II": TERMS_II, "III": TERMS_III, "IV": TERMS_IV}[m],
                     "n": fits[m]["n"], "b": fits[m]["b"], "se": fits[m]["se"],
                     "rmse": fits[m]["rmse"], "cov": fits[m]["cov"],
                     **({"r2": fits[m]["r2"], "press": fits[m]["press"],
                         "pred_r2": fits[m]["pred_r2"]} if m != "IV" else {})}
                 for m in ("I", "II", "III", "IV")},
        "derived": {
            "apparent_Ea_kJ_per_mol": {
                "model_II_at_cat_levels": {
                    f"{c:.4g} mmol/L": float(-R_KJ * (fits["II"]["b"][1]
                                                      + fits["II"]["b"][5] * np.log(c * 1e-3)))
                    for c in (0.0625, 0.157, 0.25)},
                "model_III": float(-R_KJ * fits["III"]["b"][1]),
                "model_IV": float(fits["IV"]["b"][1]),
            },
            "conventional_kinetics": kin_res,
        },
        "sensitivity": sensitivity,
        "extension": extension,
    }
    (RESULTS / "comparison.json").write_text(json.dumps(to_builtin(comparison), indent=1) + "\n")

    plt = setup_mpl()
    data = {"y": y, "x1": x1, "x4": x4, "T_c": T_c, "used": used}
    fig_parity(plt, data, fits, ref_fitted)
    fig_design(plt, pred, pred_int, sigma_m, run_a, run_b, S0_nom, data, window, thr, t_max_iv, hull)
    fig_kinetics(plt, si, kin_res)

    print(f"verdict: {verdict} ({n_pass}/{len(checks)} checks pass)")
    for c in checks:
        if not c["pass"]:
            print(f"  FAIL {c['check']}: ours {c['ours']:.6g} ref {c['reference']:.6g} ({c['tolerance']})")
    for lab, r in (("single best", best), ("run A", run_a), ("run B", run_b)):
        print(f"{lab}: {r['T_degC']:.0f} degC, {r['p_bar']:.0f} bar, "
              f"cat {r['catalyst_mmol_per_L']:.3g} mM, base {r['base_mmol_per_L']:.3g} mM, "
              f"{r['run_time_h']:.0f} h; D = " + ", ".join(f"{k} {v:.2f}" for k, v in r["D"].items()))
    print(f"two-run design D_min = {two_run['D_min']:.2f}")
    print(f"model IV integrated form: reused coefficients RMSE "
          f"{integrated_record['reused_coefficients_rmse_vs_measured_y']:.3f}, refit RMSE "
          f"{integrated_record['refit_rmse_vs_measured_y']:.3f} (vs measured y, n = 24)")
    print(f"model IV MATLAB-convention sigma {fits['IV']['matlab_convention']['s']:.5f}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
