# /// script
# requires-python = ">=3.12,<3.14"
# dependencies = [
#     "numpy==2.3.4",
#     "scipy==1.16.3",
#     "matplotlib==3.10.7",
#     "pyyaml==6.0.3",
#     "openpyxl==3.1.5",
# ]
# ///
"""Electrified distillation with flash vapour circulation: CS1 against CS2 (#335, tracker #333).

Reproduction of Cui et al. (2025), Chem. Eng. Res. Des. 220, 450-460 (CC BY 4.0), with a
transparent tray-by-tray model of our own. Rerun from the repository root:

    uv run benchmarks/reproductions/electrified-distillation-control/run.py

It downloads the paper's supporting-information workbook into a cache outside git, checks its
sha256, reads it as data (openpyxl, read-only, values only) and writes results/ next to this
file: comparison.json and SVG figures. Inputs and their labels: inputs.yaml. Tolerances (frozen
before the first comparison run): tolerances.yaml. Exit status is non-zero only when the script
itself fails; the verdict is in comparison.json.

Options: --quick skips the sensitivity study (for development only; the committed results are
from a full run).
"""

from __future__ import annotations

import hashlib
import json
import os
import platform
import sys
import time
import urllib.request
from dataclasses import dataclass, field, replace
from pathlib import Path

import numpy as np
import yaml
from scipy.integrate import solve_ivp
from scipy.optimize import least_squares, root

HERE = Path(__file__).resolve().parent
CASE_ID = "electrified-distillation-control"
RESULTS = HERE / "results"

SI_URL = "https://ars.els-cdn.com/content/image/1-s2.0-S0263876225003818-mmc1.xlsx"
SI_SHA256 = "4f57888ecfb2cb91918c437e4ecae7c235e65c391c55ab33a6ddeffc4d37a575"
SI_NAME = "1-s2.0-S0263876225003818-mmc1.xlsx"

CAL = 4.184                                 # J/cal
MW = np.array([32.04216, 18.01528])         # kg/kmol, methanol and water (standard atomic weights)
# NIST Chemistry WebBook Antoine sets, log10(P/bar) = A - B/(T/K + C) (inputs.yaml)
ANTOINE = np.array([[5.20409, 1581.341, -33.50],     # methanol, Ambrose and Sprake 1970
                    [5.08354, 1663.125, -45.622]])   # water, Bridgeman and Aldrich 1964
T0 = 298.15                                 # K, enthalpy reference temperature of the fit
NRTL_ALPHA = 0.3
SCENARIO_ORDER = ["CS1 +20% MeOH", "CS1 -20% MeOH", "CS2 +20% MeOH", "CS2 -20% MeOH",
                  "CS1 +20% F", "CS1 -20% F", "CS2 +20% F", "CS2 -20% F"]


# ----------------------------------------------------------------------------- data access
def cache_dir() -> Path:
    base = os.environ.get("XDG_CACHE_HOME") or str(Path.home() / ".cache")
    d = Path(base) / "cheme-reproductions" / CASE_ID
    d.mkdir(parents=True, exist_ok=True)
    return d


def fetch_si() -> Path:
    """Download the SI workbook once, verify its sha256; never execute it."""
    path = cache_dir() / SI_NAME
    if path.exists() and hashlib.sha256(path.read_bytes()).hexdigest() == SI_SHA256:
        return path
    req = urllib.request.Request(SI_URL, headers={"User-Agent": "cheme-reproductions/1.0 (process-library benchmark #335)"})
    with urllib.request.urlopen(req, timeout=120) as r:
        data = r.read()
    digest = hashlib.sha256(data).hexdigest()
    if digest != SI_SHA256:
        raise SystemExit(f"SI workbook sha256 mismatch: got {digest}, expected {SI_SHA256}")
    tmp = path.with_suffix(".part")
    tmp.write_bytes(data)
    tmp.replace(path)
    return path


def read_si(path: Path) -> dict:
    from openpyxl import load_workbook
    wb = load_workbook(path, read_only=True, data_only=True)
    out = {"streams": _read_streams(wb["Stream data"]), "column": _read_column(wb["Column data"]), "series": {}}
    for name in wb.sheetnames[2:]:
        out["series"][name] = _read_series(wb[name])
    wb.close()
    return out


def _read_streams(ws) -> dict:
    rows = [r for r in ws.iter_rows(values_only=True)]
    head = rows[0]
    cols = {str(v): j for j, v in enumerate(head) if j >= 2 and v is not None}
    streams = {k: {} for k in cols}
    group = None
    for r in rows[1:]:
        label = r[0]
        if label == "Vapor Phase":
            break
        if label in ("Mole Flows", "Mole Fractions", "Mass Flows", "Mass Fractions"):
            group = label
        key = {"Temperature": "T_C", "Pressure": "P_bar", "Molar Vapor Fraction": "vf",
               "Molar Enthalpy": "h_calmol", "Enthalpy Flow": "Hflow_kW", "Mole Flows": "F",
               "Volume Flow": "Qvol_lmin", "Mass Density": "rho_gcc"}.get(label)
        if label in ("METHA-01", "WATER") and group in ("Mole Flows", "Mole Fractions"):
            key = ("F_" if group == "Mole Flows" else "x_") + ("m" if label == "METHA-01" else "w")
        if key is None:
            continue
        for name, j in cols.items():
            v = r[j]
            if isinstance(v, (int, float)):
                streams[name][key] = float(v)
    return streams


def _read_column(ws) -> dict:
    rows = [r for r in ws.iter_rows(values_only=True)]
    st = [r for r in rows[2:45] if isinstance(r[0], (int, float))]
    st = sorted(st, key=lambda r: r[0])
    n = len(st)
    col = {k: np.array([float(r[j] or 0.0) for r in st]) for k, j in
           (("stage", 0), ("T_C", 1), ("P_bar", 2), ("L", 4), ("V", 5), ("Fliq", 6),
            ("hL_calmol", 11), ("hV_calmol", 12))}
    hdr = next(i for i, r in enumerate(rows) if r[0] == "Stage" and i > 40)
    x = {}
    hyd = {}
    for r in rows[hdr + 1:]:
        if isinstance(r[4], (int, float)) and isinstance(r[5], (int, float)):
            x[int(r[4])] = float(r[5])                       # liquid methanol mole fraction
        if isinstance(r[8], (int, float)) and isinstance(r[14], (int, float)):
            hyd[int(r[8])] = dict(rhoL=float(r[17]), MWL=float(r[15]), QV_lmin=float(r[14]),
                                  rhoV=float(r[18]))
    col["x"] = np.array([x[i] for i in range(1, n + 1)])
    col["hyd"] = hyd
    return col


def _read_series(ws) -> dict:
    rows = [r for r in ws.iter_rows(values_only=True)]
    head = rows[0]
    idx = [j for j, v in enumerate(head) if v == "Time"]
    out = {}
    for k, j in enumerate(idx):
        end = idx[k + 1] if k + 1 < len(idx) else len(head)
        data = [r for r in rows[2:] if isinstance(r[j], (int, float))]
        t = np.array([r[j] for r in data], float)
        for c in range(j + 1, end):
            if head[c] is not None:
                out[str(head[c])] = (t, np.array([float(r[c]) for r in data]))
    keys = {"D": 'STREAMS("MEOH").F', "B": 'STREAMS("WATER").F', "FVC": 'STREAMS("11").F',
            "xD": 'STREAMS("MEOH").Zn("METHA-01")', "xBw": 'STREAMS("WATER").Zn("WATER")',
            "W1": 'BLOCKS("COMP1").Bpower', "W2": 'BLOCKS("COMP2").Bpower', "W3": 'BLOCKS("COMP3").Bpower',
            "T35": 'BLOCKS("COLUMN").Stage(35).T', "RR": "RR.Input2"}
    s = {k: out[v] for k, v in keys.items()}
    t = s["xD"][0]
    res = {"t": t}
    for k, (tk, v) in s.items():
        res[k] = np.interp(t, tk, v)
    res["W"] = res["W1"] + res["W2"] + res["W3"]
    return res


# ----------------------------------------------------------------------------- thermodynamics
def psat(T):
    """Vapour pressures [bar] of methanol and water, T [K] array -> (n, 2)."""
    T = np.asarray(T, float)[..., None]
    return 10.0 ** (ANTOINE[:, 0] - ANTOINE[:, 1] / (T + ANTOINE[:, 2]))


def dlnpsat_dT(T):
    T = np.asarray(T, float)[..., None]
    return np.log(10.0) * ANTOINE[:, 1] / (T + ANTOINE[:, 2]) ** 2


def lngamma(x1, T, b):
    x1 = np.clip(np.asarray(x1, float), 1e-12, 1 - 1e-12)
    x2 = 1.0 - x1
    t12, t21 = b[0] / T, b[1] / T
    G12, G21 = np.exp(-NRTL_ALPHA * t12), np.exp(-NRTL_ALPHA * t21)
    l1 = x2 ** 2 * (t21 * (G21 / (x1 + x2 * G21)) ** 2 + t12 * G12 / (x2 + x1 * G12) ** 2)
    l2 = x1 ** 2 * (t12 * (G12 / (x2 + x1 * G12)) ** 2 + t21 * G21 / (x1 + x2 * G21) ** 2)
    return np.stack([l1, l2], axis=-1)


def bubble(x1, P, b, Tg=None):
    """Bubble temperature [K] and vapour methanol fraction at liquid methanol fraction x1, P [bar]."""
    x1 = np.clip(np.asarray(x1, float), 1e-12, 1 - 1e-12)
    P = np.broadcast_to(np.asarray(P, float), x1.shape)
    X = np.stack([x1, 1 - x1], axis=-1)
    T = np.full(x1.shape, 350.0) if Tg is None else np.array(Tg, float)
    for _ in range(50):
        g = np.exp(lngamma(x1, T, b))
        ps = psat(T)
        s = (X * g * ps).sum(-1)
        f = np.log(s / P)
        dfdT = (X * g * ps * dlnpsat_dT(T)).sum(-1) / s
        dT = -f / dfdT
        T = T + np.clip(dT, -20, 20)
        if np.max(np.abs(dT)) < 1e-9:
            break
    g = np.exp(lngamma(x1, T, b))
    y = x1 * g[..., 0] * psat(T)[..., 0] / P
    return T, np.clip(y, 0.0, 1.0)


@dataclass
class Thermo:
    b: np.ndarray            # NRTL b12, b21 [K]
    hl: np.ndarray           # liquid enthalpy parameters [kJ/kmol]
    hv: np.ndarray           # vapour enthalpy parameters [kJ/kmol]
    v: np.ndarray            # liquid molar volumes [m3/kmol]

    def h_L(self, x, T):
        x = np.asarray(x, float); d = np.asarray(T, float) - T0
        a = self.hl
        return x * (a[0] + a[1] * d) + (1 - x) * (a[2] + a[3] * d) + a[4] * x * (1 - x)

    def H_V(self, y, T):
        y = np.asarray(y, float); d = np.asarray(T, float) - T0
        a = self.hv
        return y * (a[0] + a[1] * d) + (1 - y) * (a[2] + a[3] * d)

    def vmol(self, x):
        return x * self.v[0] + (1 - x) * self.v[1]


def si_equilibrium_points(si) -> dict:
    """Stage x, y, T, P from the SI; y of the stages from the SI flows by component balance."""
    c, s = si["column"], si["streams"]
    n = len(c["x"])
    x = c["x"]
    L, V = c["L"], c["V"]
    xD, D = s["MEOH"]["x_m"], s["MEOH"]["F"]
    zF, F = s["FEED"]["x_m"], s["FEED"]["F"]
    y = np.empty(n)
    y[0] = s["2"]["x_m"]
    feed_stage = int(c["stage"][np.argmax(c["Fliq"])])
    for j in range(2, n + 1):                      # stage j (1-based)
        above = F * zF if feed_stage <= j - 1 else 0.0
        y[j - 1] = (L[j - 2] * x[j - 2] + D * xD - above) / V[j - 1]
    xs = np.r_[x, s["27"]["x_m"], s["13"]["x_m"]]
    ys = np.r_[y, s["25"]["x_m"], s["11"]["x_m"]]
    Ts = np.r_[c["T_C"], s["25"]["T_C"], s["11"]["T_C"]] + 273.15
    Ps = np.r_[c["P_bar"], s["25"]["P_bar"], s["11"]["P_bar"]]
    return dict(x=xs, y=ys, T=Ts, P=Ps, y_stage=y, feed_stage=feed_stage)


def fit_thermo(si) -> tuple[Thermo, dict]:
    eq = si_equilibrium_points(si)
    x, y, T, P = eq["x"], eq["y"], eq["T"], eq["P"]
    X = np.stack([x, 1 - x], -1)
    Y = np.stack([y, 1 - y], -1)
    lng_data = np.log(Y * P[:, None] / (X * psat(T)))
    mask = X >= 1e-3

    def resid(b):
        return (lngamma(x, T, b) - lng_data)[mask]

    fit = least_squares(resid, x0=[-50.0, 300.0], method="lm", xtol=1e-14, ftol=1e-14)
    b = fit.x
    Tb, yb = bubble(x, P, b, Tg=T)

    # enthalpies, kJ/kmol
    c, s = si["column"], si["streams"]
    rowsL, valL, rowsV, valV = [], [], [], []

    def addL(xm, TK, h):
        d = TK - T0
        rowsL.append([xm, xm * d, 1 - xm, (1 - xm) * d, xm * (1 - xm)]); valL.append(h * CAL)

    def addV(ym, TK, h):
        d = TK - T0
        rowsV.append([ym, ym * d, 1 - ym, (1 - ym) * d]); valV.append(h * CAL)

    for j in range(len(c["x"])):
        addL(c["x"][j], c["T_C"][j] + 273.15, c["hL_calmol"][j])
        addV(eq["y_stage"][j], c["T_C"][j] + 273.15, c["hV_calmol"][j])
    for k in ("1", "8", "9", "13", "19", "27"):
        addL(s[k]["x_m"], s[k]["T_C"] + 273.15, s[k]["h_calmol"])
    for k in ("2", "3", "4", "5", "6", "7", "11", "25"):
        addV(s[k]["x_m"], s[k]["T_C"] + 273.15, s[k]["h_calmol"])
    AL, bL = np.array(rowsL), np.array(valL)
    AV, bV = np.array(rowsV), np.array(valV)
    hl = np.linalg.lstsq(AL, bL, rcond=None)[0]
    hv = np.linalg.lstsq(AV, bV, rcond=None)[0]

    # liquid molar volume from the SI hydraulic table
    hyd = c["hyd"]
    xv, vv = [], []
    for j in range(1, len(c["x"]) + 1):
        if j in hyd:
            xv.append(c["x"][j - 1]); vv.append(hyd[j]["MWL"] / hyd[j]["rhoL"] / 1000.0)
    xv, vv = np.array(xv), np.array(vv)
    v = np.linalg.lstsq(np.stack([xv, 1 - xv], -1), vv, rcond=None)[0]

    th = Thermo(b=b, hl=hl, hv=hv, v=v)
    diag = {
        "nrtl_b12_K": float(b[0]), "nrtl_b21_K": float(b[1]), "nrtl_alpha": NRTL_ALPHA,
        "lngamma_rms": float(np.sqrt(np.mean(resid(b) ** 2))),
        "bubble_T_rms_K": float(np.sqrt(np.mean((Tb - T) ** 2))),
        "bubble_T_maxabs_K": float(np.max(np.abs(Tb - T))),
        "y_rms": float(np.sqrt(np.mean((yb - y) ** 2))),
        "enthalpy_liquid_rms_kJkmol": float(np.sqrt(np.mean((AL @ hl - bL) ** 2))),
        "enthalpy_vapour_rms_kJkmol": float(np.sqrt(np.mean((AV @ hv - bV) ** 2))),
        "enthalpy_liquid_params": hl.tolist(), "enthalpy_vapour_params": hv.tolist(),
        "latent_heat_25C_kJkmol": {"methanol": float(hv[0] - hl[0]), "water": float(hv[2] - hl[2])},
        "liquid_molar_volume_m3kmol": {"methanol": float(v[0]), "water": float(v[1])},
        "n_points_equilibrium": int(len(x)), "feed_stage_from_SI": eq["feed_stage"],
    }
    return th, diag


# ----------------------------------------------------------------------------- model parameters
@dataclass
class Params:
    th: Thermo
    n: int = 38
    feed_stage: int = 29
    P_top: float = 1.007
    dP: float = 0.007
    P_R: float = 1.276
    P_D: float = 1.007
    F: float = 100.0
    z: float = 0.80
    T_F: float = 303.15
    xD_spec: float = 0.99
    xB_spec: float = 1e-4            # methanol in bottoms (water 0.9999)
    tc_stage: int = 35
    # heat pump
    w: float = 0.0                   # kJ/kmol of compressed vapour
    q_c: float = 0.0                 # kJ/kmol
    kappa: float = 0.0
    hp_limit: bool = True
    split: tuple = (166.194, 68.4394, 68.4135)
    # hydraulics
    diameter: float = 0.76
    weir_h: float = 0.05
    weir_frac: float = 0.73
    active_frac: float = 0.80
    francis: float = 1.84
    # holdups (minutes of nominal flow at 50 % level)
    drum_min: float = 5.0
    sump_min: float = 5.0
    flashR_min: float = 5.0
    # control
    lc_gain: float = 2.0
    tc_dead_min: float = 1.0
    cc_dead_min: float = 3.0
    n_lags: int = 8

    @property
    def P(self):
        return self.P_top + self.dP * np.arange(self.n)

    @property
    def area(self):
        return np.pi * self.diameter ** 2 / 4.0


def f_feed(p: Params, F=None, z=None):
    Fv = np.zeros(p.n)
    Fv[p.feed_stage - 1] = p.F if F is None else F
    return Fv, (p.z if z is None else z)


# ----------------------------------------------------------------------------- steady state
def ss_flows(p: Params, x, xR, xD, D, RR, F=None, z=None):
    """Top-down flows from total and energy balances at given compositions (steady state)."""
    th = p.th
    Fv, zf = f_feed(p, F, z)
    Ftot = Fv.sum()
    T, y = bubble(x, p.P, th.b)
    TR, yR = bubble(np.array([xR]), np.array([p.P_R]), th.b)
    TD, yDv = bubble(np.array([xD]), np.array([p.P_D]), th.b)
    hF = th.h_L(zf, p.T_F)
    h = th.h_L(x, T); H = th.H_V(y, T)
    hR = th.h_L(xR, TR[0]); HR = th.H_V(yR[0], TR[0]); hD = th.h_L(xD, TD[0])
    R = RR * D
    L = np.empty(p.n); V = np.empty(p.n + 1)
    V[0] = R + D
    Lprev, hprev = R, hD
    for j in range(p.n):
        Hn = H[j + 1] if j + 1 < p.n else HR
        L[j] = (Lprev * (hprev - Hn) + V[j] * (Hn - H[j]) + Fv[j] * (hF - Hn)) / (h[j] - Hn)
        V[j + 1] = L[j] + V[j] - Lprev - Fv[j]
        Lprev, hprev = L[j], h[j]
    B = Ftot - D
    QR = V[p.n] * HR + B * hR - L[-1] * h[-1]          # kJ/h
    return dict(T=T, y=y, TR=TR[0], yR=yR[0], TD=TD[0], L=L, V=V, R=R, B=B, QR=QR, hD=hD, H=H, h=h,
                HR=HR, hR=hR, Ftot=Ftot, Fv=Fv, z=zf)


def ss_residual(u, p: Params, specs: dict, F=None, z=None):
    n = p.n
    x = u[:n]; xR, xD, D, RR = u[n], u[n + 1], u[n + 2], u[n + 3]
    s = ss_flows(p, x, xR, xD, D, RR, F, z)
    L, V, y = s["L"], s["V"], s["y"]
    xin = np.r_[xD, x[:-1]]
    Lin = np.r_[s["R"], L[:-1]]
    yin = np.r_[y[1:], s["yR"]]
    r = Lin * xin + V[1:] * yin + s["Fv"] * s["z"] - L * x - V[:-1] * y
    rR = L[-1] * x[-1] - V[n] * s["yR"] - s["B"] * xR
    rD = V[0] * y[0] - (s["R"] + D) * xD
    sp = []
    for k, v in specs.items():
        if k == "xD": sp.append((xD - v) * 100)
        elif k == "xB": sp.append((xR - v) * 1e4)
        elif k == "T35": sp.append(s["T"][p.tc_stage - 1] - v)
        elif k == "RR": sp.append((RR - v) * 10)
        else: raise KeyError(k)
    return np.r_[r / 10.0, rR / 10.0, rD / 10.0, sp]


def solve_ss(p: Params, specs: dict, guess, F=None, z=None):
    sol = root(ss_residual, guess, args=(p, specs, F, z), method="hybr", options={"xtol": 1e-12, "maxfev": 20000})
    if not sol.success or np.max(np.abs(sol.fun)) > 1e-6:
        sol2 = least_squares(ss_residual, sol.x, args=(p, specs, F, z), xtol=1e-15, ftol=1e-15, gtol=1e-15)
        if np.max(np.abs(sol2.fun)) < np.max(np.abs(sol.fun)):
            sol = sol2
    u = sol.x
    n = p.n
    s = ss_flows(p, u[:n], u[n], u[n + 1], u[n + 2], u[n + 3], F, z)
    s.update(x=u[:n].copy(), xR=float(u[n]), xD=float(u[n + 1]), D=float(u[n + 2]), RR=float(u[n + 3]),
             u=u.copy(), resid_max=float(np.max(np.abs(ss_residual(u, p, specs, F, z)))))
    return s


HP_SMOOTH_KW = 2.0     # width of the smooth minimum between full condensation and capacity (kW)


def _hp_forward(p: Params, mc, QR0_kW):
    qa = p.q_c / 3600.0 * mc
    if not p.hp_limit:
        return qa
    mc0 = QR0_kW / (p.q_c / 3600.0)
    qb = QR0_kW * (1 + p.kappa * ((mc / mc0) ** 2 - 1))
    e = HP_SMOOTH_KW
    return 0.5 * (qa + qb - np.sqrt((qa - qb) ** 2 + e * e)) + 0.5 * e   # equals qa = qb at the design load


def heat_pump(p: Params, QR_kW=None, W_kW=None, QR0_kW=None):
    """Quasi-steady heat-pump closure (inputs.yaml heat_pump), kW and kmol/h.

    W -> (m_c, Q_R) or Q_R -> (m_c, W). Full condensation (Q_R = q_c m_c) up to the nominal
    design load, capacity-limited above it (Q_cap = Q_R0 [1 + kappa ((m_c/m_c0)^2 - 1)]); a smooth
    minimum of width HP_SMOOTH_KW joins the two, shifted so that the design point is exact (it lies
    within 1 kW of either branch away from it).
    """
    from scipy.optimize import brentq
    if W_kW is not None:
        mc = W_kW / (p.w / 3600.0)
        return mc, _hp_forward(p, mc, QR0_kW)
    hi = QR_kW / (p.q_c / 3600.0) * 1.01
    while _hp_forward(p, hi, QR0_kW) < QR_kW:
        hi *= 1.5
        if hi > 1e5:
            return np.inf, np.inf
    mc = brentq(lambda m: _hp_forward(p, m, QR0_kW) - QR_kW, 1e-6, hi, xtol=1e-10)
    return mc, mc * p.w / 3600.0


# ----------------------------------------------------------------------------- dynamic model
@dataclass
class Ctrl:
    cs: int = 1
    Kc_T: float = 0.0          # kW/K
    tauI_T: float = 1.0        # h
    Kc_C: float = 0.0          # reflux ratio per mol/mol
    tauI_C: float = 1.0        # h
    xD_sp: float = 0.99
    xD_sp_step: tuple | None = None    # (time h, new set point)


class Plant:
    """Column, FLASH-R, FLASH-D, heat pump and the regulatory loops of CS1 / CS2."""

    def __init__(self, p: Params, ss: dict):
        self.p = p
        n = p.n
        self.ss = ss
        self.QR0 = ss["QR"] / 3600.0                        # kW, our nominal reboiler duty
        self.mc0 = self.QR0 / (p.q_c / 3600.0)
        self.W0 = self.mc0 * p.w / 3600.0
        self.RR0, self.D0, self.B0 = ss["RR"], ss["D"], ss["B"]
        self.L38_0 = ss["L"][-1]
        self.Tsp = ss["T"][p.tc_stage - 1]
        self.Lw = p.weir_frac * p.diameter
        self.Aa = p.active_frac * p.area
        v = p.th.vmol(ss["x"])
        how = (ss["L"][:-1] * v[:-1] / 3600.0 / (p.francis * self.Lw)) ** (2.0 / 3.0)
        self.M_tray0 = self.Aa * (p.weir_h + how) / v[:-1]
        self.M38_0 = p.sump_min / 60.0 * self.L38_0
        self.MR0 = p.flashR_min / 60.0 * self.L38_0
        self.MD0 = p.drum_min / 60.0 * (ss["R"] + ss["D"])
        self.nl = p.n_lags
        self.idx = dict(M=slice(0, n), x=slice(n, 2 * n), MR=2 * n, xR=2 * n + 1, MD=2 * n + 2, xD=2 * n + 3,
                        IT=2 * n + 4, zT=slice(2 * n + 5, 2 * n + 5 + self.nl), IC=2 * n + 5 + self.nl,
                        zC=slice(2 * n + 6 + self.nl, 2 * n + 6 + 2 * self.nl))
        self.nstate = 2 * n + 6 + 2 * self.nl
        self._Tg = ss["T"].copy()

    def initial_state(self):
        p, ss, I = self.p, self.ss, self.idx
        s = np.zeros(self.nstate)
        s[I["M"]] = np.r_[self.M_tray0, self.M38_0]
        s[I["x"]] = ss["x"]
        s[I["MR"]], s[I["xR"]], s[I["MD"]], s[I["xD"]] = self.MR0, ss["xR"], self.MD0, ss["xD"]
        s[I["zT"]] = self.Tsp
        s[I["zC"]] = ss["xD"]
        return s

    def evaluate(self, t, s, ctrl: Ctrl, dist, W_in=None, RR_in=None):
        p, th, I, n = self.p, self.p.th, self.idx, self.p.n
        M = s[I["M"]]; x = np.clip(s[I["x"]], 0.0, 1.0)
        MR, xR, MD, xD = s[I["MR"]], min(max(s[I["xR"]], 0.0), 1.0), s[I["MD"]], min(max(s[I["xD"]], 0.0), 1.0)
        Ffeed, z = dist(t)
        Fv = np.zeros(n); Fv[p.feed_stage - 1] = Ffeed
        T, y = bubble(x, p.P, th.b, Tg=self._Tg)
        self._Tg = T
        TR, yR = bubble(np.array([xR]), np.array([p.P_R]), th.b, Tg=[self.ss["TR"]])
        TD, _ = bubble(np.array([xD]), np.array([p.P_D]), th.b, Tg=[self.ss["TD"]])
        TR, yR, TD = TR[0], yR[0], TD[0]
        h, H = th.h_L(x, T), th.H_V(y, T)
        hR, HR, hD, hF = th.h_L(xR, TR), th.H_V(yR, TR), th.h_L(xD, TD), th.h_L(z, p.T_F)
        v = th.vmol(x[:-1])
        how = np.maximum(M[:-1] * v / self.Aa - p.weir_h, 0.0)
        L = np.empty(n)
        L[:-1] = 3600.0 * p.francis * self.Lw * how ** 1.5 / v
        k = p.lc_gain
        L[-1] = max(self.L38_0 * (1 + k * (M[-1] / self.M38_0 - 1)), 0.0)
        B = max(self.B0 * (1 + k * (MR / self.MR0 - 1)), 0.0)
        D = max(self.D0 * (1 + k * (MD / self.MD0 - 1)), 0.0)
        Tm = s[I["zT"]][-1]
        eT = self.Tsp - Tm
        W = self.W0 + ctrl.Kc_T * (eT + s[I["IT"]] / ctrl.tauI_T) if W_in is None else W_in
        W = max(W, 1.0)
        xsp = ctrl.xD_sp
        if ctrl.xD_sp_step is not None and t >= ctrl.xD_sp_step[0]:
            xsp = ctrl.xD_sp_step[1]
        eC = xsp - s[I["zC"]][-1]
        if RR_in is not None:
            RR = RR_in
        elif ctrl.cs == 2:
            RR = self.RR0 + ctrl.Kc_C * (eC + s[I["IC"]] / ctrl.tauI_C)
        else:
            RR = self.RR0
        RR = max(RR, 0.02)
        R = RR * D
        mc, QR = heat_pump(p, W_kW=W, QR0_kW=self.QR0)
        VR = (L[-1] * (h[-1] - hR) + QR * 3600.0) / (HR - hR)
        V = np.empty(n + 1); V[n] = VR
        Hn = HR
        for j in range(n - 1, -1, -1):
            Lin = L[j - 1] if j > 0 else R
            hin = h[j - 1] if j > 0 else hD
            V[j] = (Lin * (hin - h[j]) + V[j + 1] * (Hn - h[j]) + Fv[j] * (hF - h[j])) / (H[j] - h[j])
            Hn = H[j]
        return dict(M=M, x=x, MR=MR, xR=xR, MD=MD, xD=xD, T=T, y=y, yR=yR, TR=TR, TD=TD, L=L, V=V, B=B, D=D, R=R,
                    RR=RR, W=W, mc=mc, QR=QR, Fv=Fv, z=z, F=Ffeed, eT=eT, eC=eC, h=h, H=H, hD=hD,
                    FVC=mc - V[0], Qcond=(V[0] * (H[0] - hD)) / 3600.0 + W - QR)

    def rhs(self, t, s, ctrl: Ctrl, dist, W_in=None, RR_in=None):
        e = self.evaluate(t, s, ctrl, dist, W_in, RR_in)
        I, n = self.idx, self.p.n
        x, L, V, y = e["x"], e["L"], e["V"], e["y"]
        Lin = np.r_[e["R"], L[:-1]]; xin = np.r_[e["xD"], x[:-1]]
        Vin = V[1:]; yin = np.r_[y[1:], e["yR"]]
        ds = np.zeros_like(s)
        ds[I["M"]] = Lin + Vin + e["Fv"] - L - V[:-1]
        ds[I["x"]] = (Lin * (xin - x) + Vin * (yin - x) + e["Fv"] * (e["z"] - x) - V[:-1] * (y - x)) / e["M"]
        ds[I["MR"]] = L[-1] - V[n] - e["B"]
        ds[I["xR"]] = (L[-1] * (x[-1] - e["xR"]) - V[n] * (e["yR"] - e["xR"])) / e["MR"]
        ds[I["MD"]] = V[0] - e["R"] - e["D"]
        ds[I["xD"]] = V[0] * (y[0] - e["xD"]) / e["MD"]
        ds[I["IT"]] = e["eT"]
        tauT = self.p.tc_dead_min / 60.0 / self.nl
        zT = s[I["zT"]]
        ds[I["zT"]] = (np.r_[e["T"][self.p.tc_stage - 1], zT[:-1]] - zT) / tauT
        ds[I["IC"]] = e["eC"] if (ctrl.cs == 2 and RR_in is None) else 0.0
        tauC = self.p.cc_dead_min / 60.0 / self.nl
        zC = s[I["zC"]]
        ds[I["zC"]] = (np.r_[e["xD"], zC[:-1]] - zC) / tauC
        return ds

    def atol(self):
        a = np.full(self.nstate, 1e-8)
        I = self.idx
        a[I["M"]] = 1e-7
        a[I["x"]] = 1e-11
        a[I["xR"]] = 1e-12
        a[I["xD"]] = 1e-11
        a[I["zC"]] = 1e-11
        return a


def simulate(plant: Plant, ctrl: Ctrl, dist, t_end=10.0, t_step=0.5, dt_out=0.01, s0=None):
    s0 = plant.initial_state() if s0 is None else s0
    t_out = np.round(np.arange(0.0, t_end + 1e-9, dt_out), 10)
    ts, Ss = [], []
    segs = [(0.0, t_step), (t_step, t_end)]
    s = s0
    for a, b in segs:
        te = t_out[(t_out >= a - 1e-12) & (t_out <= b + 1e-12)]
        if a > 0:
            te = te[te > a + 1e-12]
            te = np.r_[a, te]
        sol = solve_ivp(lambda t, y: plant.rhs(t, y, ctrl, dist), (a, b), s, method="BDF", t_eval=te,
                        rtol=1e-7, atol=plant.atol(), max_step=0.1, first_step=1e-5)
        if not sol.success:
            raise RuntimeError(f"integration failed: {sol.message}")
        keep = slice(0, None) if a == 0 else slice(1, None)
        ts.append(sol.t[keep]); Ss.append(sol.y[:, keep])
        s = sol.y[:, -1]
    t = np.concatenate(ts); S = np.concatenate(Ss, axis=1)
    keys = ("xD", "xR", "W", "RR", "QR", "FVC", "D", "B", "R", "mc", "Qcond", "MD", "MR")
    out = {k: np.empty(len(t)) for k in keys}
    out["T35"] = np.empty(len(t)); out["V1"] = np.empty(len(t))
    for i in range(len(t)):
        e = plant.evaluate(t[i], S[:, i], ctrl, dist)
        for k in keys:
            out[k][i] = e[k]
        out["T35"][i] = e["T"][plant.p.tc_stage - 1] - 273.15
        out["V1"][i] = e["V"][0]
    out["t"] = t
    out["xBw"] = 1.0 - out["xR"]
    out["state_end"] = S[:, -1]
    return out


def step_dist(F0, z0, F1=None, z1=None, t_step=0.5):
    F1 = F0 if F1 is None else F1
    z1 = z0 if z1 is None else z1
    return lambda t: (F1, z1) if t >= t_step else (F0, z0)


# ----------------------------------------------------------------------------- tuning
def linearise(plant: Plant, s0, ctrl: Ctrl, dist, inp: str, out: str):
    u0 = plant.W0 if inp == "W" else plant.RR0
    kw = (lambda u: {"W_in": u}) if inp == "W" else (lambda u: {"RR_in": u})
    f0 = plant.rhs(0.0, s0, ctrl, dist, **kw(u0))
    n = len(s0)
    A = np.empty((n, n))
    for i in range(n):
        d = 1e-6 * max(abs(s0[i]), 1e-3)
        sp = s0.copy(); sp[i] += d
        sm = s0.copy(); sm[i] -= d
        A[:, i] = (plant.rhs(0.0, sp, ctrl, dist, **kw(u0)) - plant.rhs(0.0, sm, ctrl, dist, **kw(u0))) / (2 * d)
    du = 1e-4 * max(abs(u0), 1e-3)
    Bm = (plant.rhs(0.0, s0, ctrl, dist, **kw(u0 + du)) - plant.rhs(0.0, s0, ctrl, dist, **kw(u0 - du))) / (2 * du)
    C = np.zeros(n)
    C[plant.idx["zT"].stop - 1 if out == "T" else plant.idx["zC"].stop - 1] = 1.0
    return A, Bm, C, float(np.max(np.abs(f0)))


def ultimate(A, Bm, C):
    """Ultimate gain and period (h) from the frequency response of C (jwI - A)^-1 B."""
    w = np.logspace(-1.5, 4.0, 2500)               # rad/h
    n = A.shape[0]
    G = np.array([C @ np.linalg.solve(1j * wi * np.eye(n) - A, Bm) for wi in w])
    sign = np.sign(G[0].real)
    G = G * sign
    ph = np.unwrap(np.angle(G))
    k = np.where(ph < -np.pi)[0]
    if len(k) == 0:
        raise RuntimeError("no phase crossover found")
    k = k[0]
    f = (-np.pi - ph[k - 1]) / (ph[k] - ph[k - 1])
    wu = np.exp(np.log(w[k - 1]) + f * (np.log(w[k]) - np.log(w[k - 1])))
    mag = np.exp(np.log(abs(G[k - 1])) + f * (np.log(abs(G[k])) - np.log(abs(G[k - 1]))))
    return sign / mag, 2 * np.pi / wu, float(abs(G[0]) * sign)


def tune(plant: Plant, dist_nom, Kc_T_factor=1.0, tauI_T_factor=1.0, Kc_C_factor=1.0, tauI_C_factor=1.0):
    s0 = plant.initial_state()
    c1 = Ctrl(cs=1)
    A, Bm, C, f0 = linearise(plant, s0, c1, dist_nom, "W", "T")
    KuT, PuT, gT = ultimate(A, Bm, C)
    c1 = Ctrl(cs=1, Kc_T=KuT / 3.2 * Kc_T_factor, tauI_T=2.2 * PuT * tauI_T_factor)
    A2, B2, C2, _ = linearise(plant, s0, replace(c1, cs=2), dist_nom, "RR", "xD")
    KuC, PuC, gC = ultimate(A2, B2, C2)
    c2 = replace(c1, cs=2, Kc_C=KuC / 3.2 * Kc_C_factor, tauI_C=2.2 * PuC * tauI_C_factor)
    info = dict(TC=dict(Ku_kW_per_K=KuT, Pu_min=PuT * 60, Kc_kW_per_K=c1.Kc_T, tauI_min=c1.tauI_T * 60,
                        steady_gain_K_per_kW=gT),
                CC=dict(Ku_RR_per_molfrac=KuC, Pu_min=PuC * 60, Kc_RR_per_molfrac=c2.Kc_C, tauI_min=c2.tauI_C * 60,
                        steady_gain_molfrac_per_RR=gC),
                rhs_at_initial_state_maxabs=f0)
    return c1, c2, info


# ----------------------------------------------------------------------------- set-up from the SI
QR_PLUS20F_TEXT_KW = 1713.0      # article section 3.2, CS1 +20 % throughput reboiler duty (calibration of kappa)


def build_case(si, alpha=None, **overrides):
    """Thermodynamics, parameters, nominal steady state and plant, all from the SI."""
    global NRTL_ALPHA
    if alpha is not None:
        NRTL_ALPHA = alpha
    th, tdiag = fit_thermo(si)
    st, col = si["streams"], si["column"]
    W0_si = float(si["series"]["CS1 +20% F"]["W"][0])
    mc0_si = st["3"]["F"]
    QR0_si = sum(st[a]["Hflow_kW"] - st[b]["Hflow_kW"] for a, b in (("3", "4"), ("5", "6"), ("7", "8")))
    s20 = si["series"]["CS1 +20% F"]
    mc20 = float(s20["D"][-1] * (1 + s20["RR"][-1]) + s20["FVC"][-1])
    kappa = (QR_PLUS20F_TEXT_KW / QR0_si - 1) / ((mc20 / mc0_si) ** 2 - 1)
    hyd = col["hyd"]
    load = [hyd[j]["QV_lmin"] / 60000.0 * np.sqrt(hyd[j]["rhoV"] * 1000.0) for j in hyd]
    # stream 2 (vapour leaving stage 1): SI volume flow (l/min) and mass density (g/cc)
    load.append(st["2"]["Qvol_lmin"] / 60000.0 * np.sqrt(st["2"]["rho_gcc"] * 1000.0))
    F_factor = 2.44
    diameter = float(np.sqrt(4 * max(load) / (np.pi * F_factor)))
    p = Params(th=th, w=W0_si / mc0_si * 3600.0, q_c=QR0_si / mc0_si * 3600.0, kappa=kappa, diameter=diameter,
               feed_stage=tdiag["feed_stage_from_SI"],
               split=tuple(float(si["series"]["CS1 +20% F"][k][0]) for k in ("W1", "W2", "W3")))
    d_scale = overrides.pop("diameter_scale", 1.0)
    p = replace(p, diameter=p.diameter * d_scale, **overrides)
    guess = np.r_[col["x"], 1e-4, 0.99, 80.8, 0.646]
    ss = solve_ss(p, {"xD": p.xD_spec, "xB": p.xB_spec}, guess)
    plant = Plant(p, ss)
    hp = dict(W0_SI_kW=W0_si, mc0_SI_kmolh=mc0_si, QR0_SI_kW=QR0_si, w_kJkmol=p.w, q_c_kJkmol=p.q_c,
              kappa=kappa, mc_plus20F_SI_kmolh=mc20, QR_plus20F_text_kW=QR_PLUS20F_TEXT_KW,
              diameter_m=p.diameter, F_factor_Pa05=F_factor)
    return p, ss, plant, tdiag, hp


def scenarios():
    return {
        "CS1 +20% MeOH": (1, dict(z1=0.96)), "CS1 -20% MeOH": (1, dict(z1=0.64)),
        "CS2 +20% MeOH": (2, dict(z1=0.96)), "CS2 -20% MeOH": (2, dict(z1=0.64)),
        "CS1 +20% F": (1, dict(F1=120.0)), "CS1 -20% F": (1, dict(F1=80.0)),
        "CS2 +20% F": (2, dict(F1=120.0)), "CS2 -20% F": (2, dict(F1=80.0)),
    }


def settling(t, x, band=5e-4, t_step=0.5):
    out = np.where(np.abs(x - x[-1]) > band)[0]
    return float(t[out[-1]] - t_step) if len(out) else 0.0


def metrics(o):
    t = o["t"]
    return dict(xD=float(o["xD"][-1]), xBw=float(o["xBw"][-1]), RR=float(o["RR"][-1]), W=float(o["W"][-1]),
                FVC=float(o["FVC"][-1]), QR=float(o["QR"][-1]), D=float(o["D"][-1]),
                COP=float(o["QR"][-1] / o["W"][-1]),
                IAE_MeOH=float(np.trapezoid(np.abs(o["xD"] - 0.99), t)),
                IAE_water=float(np.trapezoid(np.abs(o["xBw"] - 0.9999), t)),
                settling_MeOH_h=settling(t, o["xD"]),
                xD_min=float(o["xD"].min()), xD_max=float(o["xD"].max()),
                W_max=float(o["W"].max()), W_min=float(o["W"].min()))


def run_all(plant, c1, c2, which=None):
    res = {}
    for name, (cs, kw) in scenarios().items():
        if which is not None and name not in which:
            continue
        ctrl = c1 if cs == 1 else c2
        dist = step_dist(plant.p.F, plant.p.z, F1=kw.get("F1"), z1=kw.get("z1"))
        res[name] = simulate(plant, ctrl, dist)
    return res


# ----------------------------------------------------------------------------- comparison
def rnd(v, s=6):
    if isinstance(v, dict):
        return {k: rnd(x, s) for k, x in v.items()}
    if isinstance(v, (list, tuple)):
        return [rnd(x, s) for x in v]
    if isinstance(v, (float, np.floating)):
        v = float(v)
        return float(f"{v:.{s}g}") if np.isfinite(v) else None
    if isinstance(v, (np.integer,)):
        return int(v)
    if isinstance(v, np.bool_):
        return bool(v)
    return v


def check(name, ref, ours, rel=None, abs_=None, unit=""):
    dev = ours - ref
    if rel is not None:
        ok = abs(dev) <= rel * abs(ref)
        tol = f"rel {rel:g}"
    else:
        ok = abs(dev) <= abs_
        tol = f"abs {abs_:g}{(' ' + unit) if unit else ''}"
    return dict(check=name, reference=ref, ours=ours, deviation=dev,
                deviation_rel=(dev / ref if ref else None), tolerance=tol, unit=unit, pass_=bool(ok))


def compare(si, ss, plant, res, tdiag):
    p = plant.p
    col = si["column"]
    sr = si["series"]
    V1 = ss["V"][0]
    lam = ss["H"][0] - ss["hD"]
    Tnom = ss["T"] - 273.15
    prim = []
    prim.append(check("nominal_reflux_ratio", 0.64636, ss["RR"], rel=0.10))
    prim.append(check("nominal_reboiler_duty", 1425.5, ss["QR"] / 3600, rel=0.05, unit="kW"))
    prim.append(check("nominal_conventional_condenser_duty", 1307.0, V1 * lam / 3600, rel=0.05, unit="kW"))
    prim.append(check("nominal_compressor_power", 303.05, plant.W0, rel=0.05, unit="kW"))
    prim.append(check("nominal_stage35_temperature", 88.911, Tnom[p.tc_stage - 1], abs_=2.0, unit="K"))
    prim.append(check("nominal_profile_temperature_rms", 0.0, float(np.sqrt(np.mean((Tnom - col["T_C"]) ** 2))), abs_=1.0, unit="K"))
    prim.append(check("nominal_profile_x_rms", 0.0, float(np.sqrt(np.mean((ss["x"] - col["x"]) ** 2))), abs_=0.02, unit="mol/mol"))
    m = {k: metrics(v) for k, v in res.items()}
    ref = {k: {"xD": float(v["xD"][-1]), "RR": float(v["RR"][-1]), "W": float(v["W"][-1]), "FVC": float(v["FVC"][-1]),
               "xBw": float(v["xBw"][-1]), "D": float(v["D"][-1]),
               "IAE_MeOH": float(np.trapezoid(np.abs(v["xD"] - 0.99), v["t"])),
               "IAE_water": float(np.trapezoid(np.abs(v["xBw"] - 0.9999), v["t"])),
               "settling_MeOH_h": settling(v["t"], v["xD"])} for k, v in sr.items()}
    prim.append(check("CS1_plus20_MeOH_xD", ref["CS1 +20% MeOH"]["xD"], m["CS1 +20% MeOH"]["xD"], abs_=0.002))
    prim.append(check("CS1_minus20_MeOH_xD", ref["CS1 -20% MeOH"]["xD"], m["CS1 -20% MeOH"]["xD"], abs_=0.003))
    prim.append(check("CS2_plus20_MeOH_xD", ref["CS2 +20% MeOH"]["xD"], m["CS2 +20% MeOH"]["xD"], abs_=0.001))
    prim.append(check("CS2_minus20_MeOH_xD", ref["CS2 -20% MeOH"]["xD"], m["CS2 -20% MeOH"]["xD"], abs_=0.001))
    prim.append(check("CS2_plus20_MeOH_RR", ref["CS2 +20% MeOH"]["RR"], m["CS2 +20% MeOH"]["RR"], rel=0.15))
    prim.append(check("CS2_minus20_MeOH_RR", ref["CS2 -20% MeOH"]["RR"], m["CS2 -20% MeOH"]["RR"], rel=0.10))
    for k, nm in (("CS1 +20% MeOH", "CS1_plus20_MeOH_power"), ("CS1 -20% MeOH", "CS1_minus20_MeOH_power"),
                  ("CS2 +20% MeOH", "CS2_plus20_MeOH_power"), ("CS2 -20% MeOH", "CS2_minus20_MeOH_power")):
        prim.append(check(nm, ref[k]["W"], m[k]["W"], rel=0.10, unit="kW"))
    ok1 = all(abs(m[f"CS2 {s} MeOH"]["xD"] - 0.99) < 0.25 * abs(m[f"CS1 {s} MeOH"]["xD"] - 0.99) for s in ("+20%", "-20%"))
    prim.append(dict(check="direction_CS2_recovers_purity", reference="|x_D,CS2-0.99| < 0.25 |x_D,CS1-0.99| at +-20 % MeOH",
                     ours={s: [m[f"CS1 {s} MeOH"]["xD"] - 0.99, m[f"CS2 {s} MeOH"]["xD"] - 0.99] for s in ("+20%", "-20%")},
                     pass_=bool(ok1)))
    ok2 = m["CS2 +20% MeOH"]["W"] < m["CS1 +20% MeOH"]["W"]
    prim.append(dict(check="direction_CS2_saves_power_plus20", reference="W_CS2 < W_CS1 at +20 % MeOH",
                     ours=[m["CS1 +20% MeOH"]["W"], m["CS2 +20% MeOH"]["W"]], pass_=bool(ok2)))

    sec = []
    for k in ("CS1 +20% MeOH", "CS1 -20% MeOH", "CS2 +20% MeOH", "CS2 -20% MeOH"):
        for q, band in (("IAE_MeOH", (0.5, 2.0)), ("IAE_water", (1 / 3, 3.0)), ("settling_MeOH_h", (0.5, 2.0))):
            r, o = ref[k][q], m[k][q]
            ratio = o / r if r > 0 else (np.inf if o > 0 else 1.0)
            sec.append(dict(check=f"{q} {k}", reference=r, ours=o, ratio=ratio, tolerance=f"ratio {band[0]:.2g}-{band[1]:.2g}",
                            pass_=bool(band[0] <= ratio <= band[1])))
        sec.append(check(f"FVC_final {k}", ref[k]["FVC"], m[k]["FVC"], abs_=5.0, unit="kmol/h"))
    sec.append(dict(check="direction_CS2_power_minus20", reference="W_CS2 > W_CS1 at -20 % MeOH",
                    ours=[m["CS1 -20% MeOH"]["W"], m["CS2 -20% MeOH"]["W"]],
                    pass_=bool(m["CS2 -20% MeOH"]["W"] > m["CS1 -20% MeOH"]["W"])))
    sec.append(check("CS1_minus20_F_power", ref["CS1 -20% F"]["W"], m["CS1 -20% F"]["W"], rel=0.10, unit="kW"))
    sec.append(check("CS1_minus20_F_xD", ref["CS1 -20% F"]["xD"], m["CS1 -20% F"]["xD"], abs_=0.002))
    sec.append(check("CS2_plus20_F_RR", ref["CS2 +20% F"]["RR"], m["CS2 +20% F"]["RR"], rel=0.05))
    sec.append(check("CS2_minus20_F_RR", ref["CS2 -20% F"]["RR"], m["CS2 -20% F"]["RR"], rel=0.05))
    # Table 2 (published IAE) against the SI series, a source-internal check
    t2 = yaml.safe_load((HERE / "source.yaml").read_text())["reported_results"]["table2_IAE"]
    src = []
    for cs in ("CS1", "CS2"):
        for key, nm in (("plus20_F", "+20% F"), ("minus20_F", "-20% F"), ("plus20_MeOH", "+20% MeOH"), ("minus20_MeOH", "-20% MeOH")):
            for q, col_ in (("MeOH", "IAE_MeOH"), ("water", "IAE_water")):
                src.append(dict(case=f"{cs} {nm}", quantity=q, table2=t2[cs][key][q], from_SI_series=ref[f"{cs} {nm}"][col_]))
    npass = sum(c["pass_"] for c in prim)
    dirs = [c for c in prim if c["check"].startswith("direction")]
    if npass == len(prim):
        verdict = "pass"
    elif npass >= 0.75 * len(prim) and all(c["pass_"] for c in dirs):
        verdict = "partial"
    else:
        verdict = "fail"
    return dict(primary=prim, secondary=sec, verdict=verdict, primary_passed=npass, primary_total=len(prim),
                secondary_passed=sum(c["pass_"] for c in sec), secondary_total=len(sec),
                ours=m, reference_SI_final=ref, table2_vs_SI=src)


# ----------------------------------------------------------------------------- sensitivity and extension
def sensitivity(si, base_c1, base_c2):
    comp = ["CS1 +20% MeOH", "CS1 -20% MeOH", "CS2 +20% MeOH", "CS2 -20% MeOH"]
    cs2only = ["CS2 +20% MeOH", "CS2 -20% MeOH"]
    V = [
        ("base", {}, None, comp),
        ("weir height 0.025 m", dict(weir_h=0.025), None, comp),
        ("weir height 0.10 m", dict(weir_h=0.10), None, comp),
        ("column diameter x0.75", dict(diameter_scale=0.75), None, comp),
        ("column diameter x1.25", dict(diameter_scale=1.25), None, comp),
        ("drum and sump holdup x0.5", dict(drum_min=2.5, sump_min=2.5), None, comp),
        ("drum and sump holdup x2", dict(drum_min=10.0, sump_min=10.0), None, comp),
        ("FLASH-R holdup x0.25", dict(flashR_min=1.25), None, comp),
        ("FLASH-R holdup x2", dict(flashR_min=10.0), None, comp),
        ("TC Kc x0.5", {}, dict(Kc_T=0.5), comp),
        ("TC Kc x2", {}, dict(Kc_T=2.0), comp),
        ("TC tau_I x0.5", {}, dict(tauI_T=0.5), comp),
        ("TC tau_I x2", {}, dict(tauI_T=2.0), comp),
        ("CC Kc x0.5", {}, dict(Kc_C=0.5), cs2only),
        ("CC Kc x2", {}, dict(Kc_C=2.0), cs2only),
        ("CC tau_I x0.5", {}, dict(tauI_C=0.5), cs2only),
        ("CC tau_I x2", {}, dict(tauI_C=2.0), cs2only),
        ("analyser deadtime 6 min (retuned)", dict(cc_dead_min=6.0), "retune", cs2only),
        ("analyser deadtime 10 min (retuned)", dict(cc_dead_min=10.0), "retune", cs2only),
        ("kappa 0.10", dict(kappa=0.10), None, comp),
        ("kappa 0.30", dict(kappa=0.30), None, comp),
        ("no exchanger capacity limit", dict(hp_limit=False), None, comp),
        ("NRTL alpha 0.20 (refitted, retuned)", dict(alpha=0.20), "retune", comp),
        ("NRTL alpha 0.40 (refitted, retuned)", dict(alpha=0.40), "retune", comp),
    ]
    out = []
    for label, ov, tun, cases in V:
        ov = dict(ov)
        alpha = ov.pop("alpha", None)
        try:
            p, ss, plant, _, _ = build_case(si, alpha=alpha, **ov)
            if tun == "retune":
                c1, c2, _ = tune(plant, step_dist(p.F, p.z))
            elif isinstance(tun, dict):
                f = {"Kc_T": "Kc_T", "tauI_T": "tauI_T", "Kc_C": "Kc_C", "tauI_C": "tauI_C"}
                c1 = replace(base_c1, **{f[k]: getattr(base_c1, f[k]) * v for k, v in tun.items() if k.endswith("_T")})
                c2 = replace(base_c2, **{f[k]: getattr(base_c2, f[k]) * v for k, v in tun.items()})
            else:
                c1, c2 = base_c1, base_c2
            res = run_all(plant, c1, c2, which=cases)
            row = dict(variant=label, nominal_RR=ss["RR"], nominal_W=plant.W0, cases={k: metrics(v) for k, v in res.items()}, error=None)
        except Exception as exc:        # a failed variant is reported, not hidden
            row = dict(variant=label, cases={}, error=f"{type(exc).__name__}: {exc}")
        finally:
            if alpha is not None:
                globals()["NRTL_ALPHA"] = 0.3
        c = row["cases"]
        if all(k in c for k in comp):
            row["CS2_recovers_purity"] = bool(all(abs(c[f"CS2 {s} MeOH"]["xD"] - 0.99) < 0.25 * abs(c[f"CS1 {s} MeOH"]["xD"] - 0.99) for s in ("+20%", "-20%")))
            row["CS2_saves_power_plus20"] = bool(c["CS2 +20% MeOH"]["W"] < c["CS1 +20% MeOH"]["W"])
        out.append(row)
    return out


def extension(plant, c2):
    """HYPOTHETICAL: CS2 distillate set point 0.99 -> 0.995 (inputs.yaml design_extension)."""
    p, ss0 = plant.p, plant.ss
    QR0 = plant.QR0
    mc_cal = 202.2

    def state(z, xsp, cs):
        specs = {"T35": plant.Tsp, "xD": xsp} if cs == 2 else {"T35": plant.Tsp, "RR": plant.RR0}
        s = solve_ss(p, specs, ss0["u"], z=z)
        mc, W = heat_pump(p, QR_kW=s["QR"] / 3600, QR0_kW=QR0)
        return dict(z=z, xD=s["xD"], xBw=1 - s["xR"], RR=s["RR"], QR=s["QR"] / 3600, W=W, mc=mc, FVC=mc - s["V"][0],
                    V_top=s["V"][0], resid=s["resid_max"],
                    flags=[f for f, c in (("compressor flow beyond the calibrated range (202 kmol/h)", mc > mc_cal),
                                          ("feed outside the source's composition cases 0.64-0.96", not (0.639 <= z <= 0.961)),
                                          ("reflux ratio below 0.303, the lowest the source reports", s["RR"] < 0.303)) if c])
    zs = np.round(np.arange(0.60, 0.9701, 0.01), 4)
    sweep = {"CS1 (RR fixed)": [], "CS2 x_D 0.99": [], "CS2 x_D 0.995": []}
    for z in zs:
        sweep["CS1 (RR fixed)"].append(state(float(z), None, 1))
        sweep["CS2 x_D 0.99"].append(state(float(z), 0.99, 2))
        sweep["CS2 x_D 0.995"].append(state(float(z), 0.995, 2))
    points = {f"{tag} z={z}": state(z, xsp, 2) for z in (0.64, 0.80, 0.96) for tag, xsp in (("0.99", 0.99), ("0.995", 0.995))}
    o = simulate(plant, replace(c2, xD_sp_step=(0.5, 0.995)), step_dist(p.F, p.z))
    dyn = dict(t=o["t"], xD=o["xD"], RR=o["RR"], W=o["W"], settling_h=settling(o["t"], o["xD"]),
               final=dict(xD=float(o["xD"][-1]), RR=float(o["RR"][-1]), W=float(o["W"][-1]), FVC=float(o["FVC"][-1])))
    return dict(sweep=sweep, points=points, setpoint_step=dyn)


# ----------------------------------------------------------------------------- figures (our own matplotlib code)
INK, INK2, GRID, SURF = "#0b0b0b", "#52514e", "#e4e3df", "#fcfcfb"
C_CS1, C_CS2, C_EXT = "#2a78d6", "#eb6834", "#1baf7a"     # categorical slots 1-3 (validated palette)


def _style():
    import matplotlib
    matplotlib.use("svg")
    import matplotlib.pyplot as plt
    plt.rcParams.update({
        "svg.hashsalt": "cheme-335", "svg.fonttype": "none", "font.size": 9, "font.family": "DejaVu Sans",
        "axes.edgecolor": INK2, "axes.labelcolor": INK, "axes.titlesize": 9.5, "axes.titleweight": "bold",
        "axes.titlecolor": INK, "xtick.color": INK2, "ytick.color": INK2, "axes.grid": True,
        "grid.color": GRID, "grid.linewidth": 0.6, "axes.spines.top": False, "axes.spines.right": False,
        "figure.facecolor": SURF, "axes.facecolor": SURF, "savefig.facecolor": SURF, "lines.linewidth": 1.8,
        "legend.frameon": False, "legend.fontsize": 8.5, "text.color": INK,
    })
    return plt


def _save(fig, name):
    fig.savefig(RESULTS / name, format="svg", metadata={"Date": None, "Creator": "run.py (#335)"}, bbox_inches="tight")
    preview = os.environ.get("CHEME_FIG_PREVIEW_DIR")       # development only: PNG copies outside git
    if preview:
        fig.savefig(Path(preview) / name.replace(".svg", ".png"), format="png", dpi=110, bbox_inches="tight")


def figures(si, ss, plant, res, sens, ext):
    plt = _style()
    sr = si["series"]
    col = si["column"]
    # 1. nominal profiles
    fig, ax = plt.subplots(1, 2, figsize=(7.6, 4.2), sharey=True)
    st = np.arange(1, plant.p.n + 1)
    ax[0].plot(ss["T"] - 273.15, st, color=C_CS1, label="our model, at the reported purity specifications")
    ax[0].plot(col["T_C"], st, "o", ms=4, mfc="none", mec=INK2, mew=1.0, label="Cui et al. (2025) SI, Aspen Plus")
    ax[1].plot(ss["x"], st, color=C_CS1)
    ax[1].plot(col["x"], st, "o", ms=4, mfc="none", mec=INK2, mew=1.0)
    ax[0].invert_yaxis()
    ax[0].set_xlabel("temperature (°C)"); ax[0].set_ylabel("stage (1 = top, feed on 29)")
    ax[1].set_xlabel("liquid methanol fraction (mol/mol)")
    ax[0].set_title("Temperature profile"); ax[1].set_title("Composition profile")
    for a in ax:
        a.axhline(plant.p.tc_stage, color=INK2, lw=0.8, ls=":")
    ax[0].text(ax[0].get_xlim()[0] + 1, plant.p.tc_stage - 0.6, "TC on stage 35", color=INK2, fontsize=8)
    fig.legend(*ax[0].get_legend_handles_labels(), loc="upper center", ncol=2, bbox_to_anchor=(0.5, 1.04))
    fig.suptitle("Nominal steady state: our tray-by-tray model against the source", y=1.09, fontsize=10.5, fontweight="bold")
    _save(fig, "fig_nominal_profiles.svg"); plt.close(fig)

    # 2. composition steps: purity, reflux ratio, compressor power
    fig, ax = plt.subplots(3, 2, figsize=(8.6, 7.4), sharex=True)
    for jc, sgn in enumerate(("+20%", "-20%")):
        for cs, colr in (("CS1", C_CS1), ("CS2", C_CS2)):
            k = f"{cs} {sgn} MeOH"
            o, r = res[k], sr[k]
            for i, (q, scale) in enumerate((("xD", 1.0), ("RR", 1.0), ("W", 1.0))):
                ax[i, jc].plot(o["t"], o[q] * scale, color=colr, lw=1.8, label=f"{cs}, our model")
                ax[i, jc].plot(r["t"], r[q] * scale, color=colr, lw=1.2, ls=(0, (4, 2)), label=f"{cs}, source SI (Aspen Dynamics)")
        ax[0, jc].axhline(0.99, color=INK2, lw=0.8, ls=":")
        ax[0, jc].set_title(f"Feed methanol {sgn} (0.80 to {'0.96' if sgn == '+20%' else '0.64'})")
        ax[2, jc].set_xlabel("time (h); step at 0.5 h")
    ax[0, 0].set_ylabel("distillate methanol (mol/mol)")
    ax[1, 0].set_ylabel("reflux ratio (-)")
    ax[2, 0].set_ylabel("total compressor power (kW)")
    h, l = ax[0, 0].get_legend_handles_labels()
    fig.legend(h, l, loc="upper center", ncol=2, bbox_to_anchor=(0.5, 1.035))
    fig.suptitle("CS1 (temperature control, fixed reflux ratio) against CS2 (plus composition control)",
                 y=1.065, fontsize=10.5, fontweight="bold")
    fig.tight_layout()
    _save(fig, "fig_composition_steps.svg"); plt.close(fig)

    # 3. throughput steps (context)
    fig, ax = plt.subplots(3, 2, figsize=(8.6, 7.4), sharex=True)
    for jc, sgn in enumerate(("+20%", "-20%")):
        for cs, colr in (("CS1", C_CS1), ("CS2", C_CS2)):
            k = f"{cs} {sgn} F"
            o, r = res[k], sr[k]
            for i, q in enumerate(("xD", "W", "FVC")):
                ax[i, jc].plot(o["t"], o[q], color=colr, lw=1.8, label=f"{cs}, our model")
                ax[i, jc].plot(r["t"], r[q], color=colr, lw=1.2, ls=(0, (4, 2)), label=f"{cs}, source SI")
        ax[0, jc].set_title(f"Feed flow {sgn}" + ("  (CS1: calibration case)" if sgn == "+20%" else ""))
        ax[2, jc].set_xlabel("time (h); step at 0.5 h")
    ax[0, 0].set_ylabel("distillate methanol (mol/mol)")
    ax[1, 0].set_ylabel("total compressor power (kW)")
    ax[2, 0].set_ylabel("flash vapour circulation (kmol/h)")
    h, l = ax[0, 0].get_legend_handles_labels()
    fig.legend(h, l, loc="upper center", ncol=2, bbox_to_anchor=(0.5, 1.035))
    fig.suptitle("Throughput steps (outside the question; shown for context)", y=1.065, fontsize=10.5, fontweight="bold")
    fig.tight_layout()
    _save(fig, "fig_throughput_steps.svg"); plt.close(fig)

    # 4. sensitivity
    if sens:
        rows = [r for r in sens if r["cases"]]
        labels = [r["variant"] for r in rows]
        y = np.arange(len(rows))[::-1]
        fig, ax = plt.subplots(1, 3, figsize=(10.0, 0.32 * len(rows) + 1.6), sharey=True)

        def val(r, k, q):
            return r["cases"][k][q] if k in r["cases"] else np.nan
        off1 = [abs(val(r, "CS1 -20% MeOH", "xD") - 0.99) for r in rows]
        off2 = [abs(val(r, "CS2 -20% MeOH", "xD") - 0.99) for r in rows]
        ax[0].scatter(np.maximum(off1, 1e-7), y, s=22, color=C_CS1, label="CS1", zorder=3)
        ax[0].scatter(np.maximum(off2, 1e-7), y, s=22, color=C_CS2, label="CS2", zorder=3)
        ax[0].set_xscale("log"); ax[0].set_xlabel("|x_D - 0.99| at 10 h,\n-20 % methanol (floor 1e-7)")
        ax[0].axvline(abs(sr["CS1 -20% MeOH"]["xD"][-1] - 0.99), color=C_CS1, lw=0.8, ls=(0, (4, 2)))
        ax[1].scatter([val(r, "CS1 +20% MeOH", "W") for r in rows], y, s=22, color=C_CS1, zorder=3)
        ax[1].scatter([val(r, "CS2 +20% MeOH", "W") for r in rows], y, s=22, color=C_CS2, zorder=3)
        ax[1].axvline(sr["CS1 +20% MeOH"]["W"][-1], color=C_CS1, lw=0.8, ls=(0, (4, 2)))
        ax[1].axvline(sr["CS2 +20% MeOH"]["W"][-1], color=C_CS2, lw=0.8, ls=(0, (4, 2)))
        ax[1].set_xlabel("compressor power at 10 h,\n+20 % methanol (kW)")
        ax[2].scatter([val(r, "CS1 +20% MeOH", "IAE_MeOH") for r in rows], y, s=22, color=C_CS1, zorder=3)
        ax[2].scatter([val(r, "CS2 +20% MeOH", "IAE_MeOH") for r in rows], y, s=22, color=C_CS2, zorder=3)
        ax[2].axvline(sr["CS2 +20% MeOH"]["xD"].size and np.trapezoid(np.abs(sr["CS2 +20% MeOH"]["xD"] - 0.99), sr["CS2 +20% MeOH"]["t"]),
                      color=C_CS2, lw=0.8, ls=(0, (4, 2)))
        ax[2].set_xscale("log"); ax[2].set_xlabel("IAE of x_D over 10 h,\n+20 % methanol (h)")
        ax[0].set_yticks(y); ax[0].set_yticklabels(labels)
        ax[0].legend(loc="lower left")
        fig.suptitle("Sensitivity to the reconstructed parameters (dashed: source SI values)", fontsize=10.5, fontweight="bold")
        fig.tight_layout()
        _save(fig, "fig_sensitivity.svg"); plt.close(fig)

    # 5. extension: operating map against feed methanol
    sw = ext["sweep"]
    fig, ax = plt.subplots(1, 3, figsize=(10.0, 3.6))
    for (lab, colr) in (("CS1 (RR fixed)", C_CS1), ("CS2 x_D 0.99", C_CS2), ("CS2 x_D 0.995", C_EXT)):
        z = [d["z"] for d in sw[lab]]
        ax[0].plot(z, [d["W"] for d in sw[lab]], color=colr, label=lab + (" (hypothetical)" if "0.995" in lab else ""))
        ax[1].plot(z, [d["RR"] for d in sw[lab]], color=colr)
        ax[2].plot(z, [d["xD"] for d in sw[lab]], color=colr)
    for k, mk, colr in (("CS1", "s", C_CS1), ("CS2", "D", C_CS2)):
        zz = [0.96, 0.64]
        ax[0].plot(zz, [sr[f"{k} +20% MeOH"]["W"][-1], sr[f"{k} -20% MeOH"]["W"][-1]], mk, ms=5, mfc="none", mec=colr, mew=1.2,
                   label=f"{k}, source SI at 10 h")
        ax[1].plot(zz, [sr[f"{k} +20% MeOH"]["RR"][-1], sr[f"{k} -20% MeOH"]["RR"][-1]], mk, ms=5, mfc="none", mec=colr, mew=1.2)
        ax[2].plot(zz, [sr[f"{k} +20% MeOH"]["xD"][-1], sr[f"{k} -20% MeOH"]["xD"][-1]], mk, ms=5, mfc="none", mec=colr, mew=1.2)
    for a in ax:
        a.axvspan(0.60, 0.64, color=GRID, alpha=0.6, lw=0); a.axvspan(0.96, 0.97, color=GRID, alpha=0.6, lw=0)
        a.set_xlabel("feed methanol fraction (mol/mol)")
    ax[0].set_ylabel("compressor power, steady (kW)"); ax[1].set_ylabel("reflux ratio (-)"); ax[2].set_ylabel("distillate methanol (mol/mol)")
    ax[0].set_title("Compressor power"); ax[1].set_title("Reflux ratio"); ax[2].set_title("Distillate purity")
    h, l = ax[0].get_legend_handles_labels()
    fig.legend(h, l, loc="upper center", ncol=3, bbox_to_anchor=(0.5, 1.12))
    fig.suptitle("Steady operating map, feed 100 kmol/h (grey: outside the source's cases)", y=1.17, fontsize=10.5, fontweight="bold")
    fig.tight_layout()
    _save(fig, "fig_extension_operating_map.svg"); plt.close(fig)


# ----------------------------------------------------------------------------- main
def series_out(o, step=10):
    keys = ("t", "xD", "xBw", "RR", "W", "FVC", "QR", "D", "B", "T35")
    return {k: rnd(np.asarray(o[k])[::step].tolist(), 6) for k in keys}


def main(argv):
    quick = "--quick" in argv
    t_start = time.time()
    RESULTS.mkdir(exist_ok=True)
    si = read_si(fetch_si())
    p, ss, plant, tdiag, hp = build_case(si)
    dn = step_dist(p.F, p.z)
    c1, c2, tinfo = tune(plant, dn)
    res = run_all(plant, c1, c2)
    cmp_ = compare(si, ss, plant, res, tdiag)
    ss_end = {}
    for name, (cs, kw) in scenarios().items():
        specs = {"T35": plant.Tsp, "RR": plant.RR0} if cs == 1 else {"T35": plant.Tsp, "xD": 0.99}
        s = solve_ss(p, specs, ss["u"], F=kw.get("F1"), z=kw.get("z1"))
        mc, W = heat_pump(p, QR_kW=s["QR"] / 3600, QR0_kW=plant.QR0)
        ss_end[name] = dict(xD=s["xD"], RR=s["RR"], W=W, QR=s["QR"] / 3600, FVC=mc - s["V"][0], resid=s["resid_max"])
    sens = [] if quick else sensitivity(si, c1, c2)
    ext = extension(plant, c2)
    figures(si, ss, plant, res, sens, ext)
    import matplotlib, scipy, openpyxl
    lam = ss["H"][0] - ss["hD"]
    out = {
        "case": CASE_ID, "issue": 335, "tracker": 333,
        "verdict": cmp_["verdict"], "pass_rule": "tolerances.yaml pass_rule",
        "primary_passed": cmp_["primary_passed"], "primary_total": cmp_["primary_total"],
        "secondary_passed": cmp_["secondary_passed"], "secondary_total": cmp_["secondary_total"],
        "software": {"python": platform.python_version(), "numpy": np.__version__, "scipy": scipy.__version__,
                     "matplotlib": matplotlib.__version__, "openpyxl": openpyxl.__version__, "pyyaml": yaml.__version__},
        "source_file": {"url": SI_URL, "sha256": SI_SHA256},
        "thermodynamics_fit": tdiag, "heat_pump_reconstruction": hp,
        "hydraulics": {"diameter_m": p.diameter, "weir_height_m": p.weir_h, "tray_holdup_kmol_top_mid_bottom":
                       [plant.M_tray0[0], plant.M_tray0[20], plant.M_tray0[-1]], "sump_kmol": plant.M38_0,
                       "FLASH_R_kmol": plant.MR0, "drum_kmol": plant.MD0},
        "tuning": tinfo,
        "nominal": {"RR": ss["RR"], "D_kmolh": ss["D"], "QR_kW": ss["QR"] / 3600, "W_kW": plant.W0,
                    "COP": ss["QR"] / 3600 / plant.W0, "V_top_kmolh": ss["V"][0], "FVC_kmolh": plant.mc0 - ss["V"][0],
                    "conventional_condenser_kW": ss["V"][0] * lam / 3600, "T35_C": ss["T"][p.tc_stage - 1] - 273.15,
                    "trim_condenser_kW": ss["V"][0] * lam / 3600 + plant.W0 - ss["QR"] / 3600,
                    "residual": ss["resid_max"]},
        "checks_primary": cmp_["primary"], "checks_secondary": cmp_["secondary"],
        "table2_vs_SI_series": cmp_["table2_vs_SI"],
        "scenarios_ours_final": cmp_["ours"], "scenarios_SI_final": cmp_["reference_SI_final"],
        "scenarios_steady_state_solution": ss_end,
        "series_ours_every_0p1h": {k: series_out(v) for k, v in res.items()},
        "sensitivity": sens,
        "extension_HYPOTHETICAL": {"label": "hypothetical design extension, not validated",
                                   "points": ext["points"], "setpoint_step_nominal_feed": {
                                       "settling_h": ext["setpoint_step"]["settling_h"], "final": ext["setpoint_step"]["final"]},
                                   "sweep": ext["sweep"]},
    }
    for k in list(out["checks_primary"]) + list(out["checks_secondary"]):
        k["pass"] = k.pop("pass_")
    (RESULTS / "comparison.json").write_text(json.dumps(rnd(out), indent=1, sort_keys=False) + "\n")
    print(f"verdict: {cmp_['verdict']} ({cmp_['primary_passed']}/{cmp_['primary_total']} primary, "
          f"{cmp_['secondary_passed']}/{cmp_['secondary_total']} secondary); {time.time() - t_start:.0f} s")
    for c in out["checks_primary"]:
        o = c["ours"] if not isinstance(c["ours"], float) else f"{c['ours']:.5g}"
        print(f"  {'PASS' if c['pass'] else 'FAIL'}  {c['check']}: ours {o}  ref {c['reference']}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
