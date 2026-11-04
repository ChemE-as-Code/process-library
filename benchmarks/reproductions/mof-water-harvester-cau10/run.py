# /// script
# requires-python = ">=3.12,<3.14"
# dependencies = [
#   "numpy==2.3.4",
#   "scipy==1.16.3",
#   "matplotlib==3.10.7",
#   "pyyaml==6.0.3",
# ]
# [tool.uv]
# exclude-newer = "2026-11-04T00:00:00Z"
# ///
"""CAU-10-H water harvester case (#334, tracker #333): reproduction and design extension.

Rerun from the repository root:

    uv run benchmarks/reproductions/mof-water-harvester-cau10/run.py

1. Downloads the pinned 4TU isotherm files into a cache outside git and checks their sha256.
2. Confirms the sample mapping (file 8 = CAU-10-H at 313 K) from the dataset's Metadata.txt.
3. Reproduces the Figure 7 descriptors (alpha, delta_p_75_25) of the CAU-10-H uptake series
   and compares them with our digitisation under the frozen tolerances.yaml.
4. Sizes an adsorbent bed: working capacity, adsorbent mass and packed volume against inlet
   relative humidity for the stated yield and recovery, regeneration heat, infeasible region.

Writes results/comparison.json (committed: scalar results only), results/sweep.json (the full
RH sweep, resampled from the CC BY-SA 4.0 isotherm, not committed) and three SVG figures (not
committed; README.md). Exits non-zero only if the script fails; the reproduction verdict is
recorded in comparison.json.
"""

from __future__ import annotations

import hashlib
import json
import math
import os
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

import matplotlib

matplotlib.use("svg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import scipy  # noqa: E402
import yaml  # noqa: E402
from scipy.optimize import brentq  # noqa: E402

CASE_ID = "mof-water-harvester-cau10"
HERE = Path(__file__).resolve().parent
RESULTS = HERE / "results"
R_GAS = 8.314462618  # J/(mol K), CODATA 2018 exact
MMHG_PA = 133.322387415  # Pa per mmHg
V_STP = 22.413969  # cm3(STP)/mmol, ideal gas at 273.15 K and 101.325 kPa

# Colours: reference categorical palette (dataviz skill), text inks and surface.
C_ADS = "#2a78d6"
C_DES = "#eb6834"
C_REF = "#1baf7a"
INK = "#0b0b0b"
INK2 = "#52514e"
SURFACE = "#fcfcfb"
SHADE_INFEASIBLE = "#d9d8d4"
SHADE_STEP = "#ecebe7"

# Reporting rule for interpolated loadings (not a model input): a point is "loosely constrained"
# when its adsorption-branch segment spans more than 10 % change in uptake or more than 0.01 in
# p/p0. The isotherm is monotonic, so the uptake lies between the two measured end points of the
# segment; those end points are reported as bounds beside the linear value.
LOOSE_REL_UPTAKE = 0.10
LOOSE_DX = 0.01
# Design points reported as scalars in comparison.json (extension.md table).
DESIGN_POINTS_RH = (0.15, 0.18, 0.19, 0.195, 0.20, 0.22, 0.30, 0.42)
# Largest allowed difference between the bed temperature and the isotherm temperature: loadings
# are read from the 313 K isotherm only (inputs.yaml adsorption_state.bed_temperature).
MAX_T_OFFSET_K = 0.5


# ---------------------------------------------------------------------------- data access
def cache_dir() -> Path:
    base = os.environ.get("XDG_CACHE_HOME") or str(Path.home() / ".cache")
    d = Path(base) / "cheme-reproductions" / CASE_ID
    d.mkdir(parents=True, exist_ok=True)
    return d


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def fetch(entry: dict) -> Path:
    """Download one pinned file (data only, never executed) and verify its sha256."""
    target = cache_dir() / entry["name"]
    if target.exists() and sha256(target) == entry["sha256"]:
        return target
    last = None
    for attempt in range(6):
        try:
            req = urllib.request.Request(entry["url"], headers={"User-Agent": f"cheme-reproductions/{CASE_ID}"})
            with urllib.request.urlopen(req, timeout=60) as r:
                data = r.read()
            tmp = target.with_suffix(target.suffix + ".part")
            tmp.write_bytes(data)
            if hashlib.sha256(data).hexdigest() != entry["sha256"]:
                tmp.unlink()
                raise RuntimeError(f"sha256 mismatch for {entry['name']} (got {len(data)} bytes)")
            tmp.replace(target)
            return target
        except (urllib.error.URLError, RuntimeError, TimeoutError) as exc:  # 429 throttling included
            last = exc
            time.sleep(5 * (attempt + 1))
    raise SystemExit(f"could not download {entry['name']}: {last}")


def read_isotherm(path: Path) -> dict:
    """Parse the 3Flex export: header line, a ';;' line, then p/p0; p (mmHg); q (mmol/g)."""
    rows = []
    for line in path.read_bytes().decode("latin-1").splitlines()[1:]:
        parts = [p.strip() for p in line.split(";")]
        if len(parts) != 3 or not parts[0]:
            continue
        rows.append([float(p) for p in parts])
    a = np.array(rows)
    i_top = int(np.argmax(a[:, 0]))
    ads, des = a[: i_top + 1], a[i_top:]
    if not (np.all(np.diff(ads[:, 0]) > 0) and np.all(np.diff(ads[:, 2]) > 0)):
        raise SystemExit("adsorption branch is not monotonic; linear inverse interpolation invalid")
    # The desorption branch is not monotonic in p/p0 on the step (0.185 to 0.189). Lookups are
    # allowed only on its low-pressure tail, where the reversed p/p0 values strictly increase.
    xs = des[::-1, 0]
    bad = np.nonzero(np.diff(xs) <= 0)[0]
    n_mono = int(bad[0]) + 1 if len(bad) else len(xs)
    return {"all": a, "ads": ads, "des": des, "des_monotonic_up_to": float(xs[n_mono - 1]),
            "des_monotonic_n": n_mono}


def check_mapping(meta: Path, inputs: dict) -> dict:
    text = meta.read_bytes().decode("latin-1")
    start = text.index("8. CAU-10-H")
    block = text[start : text.index("12. Co-CUK-1", start)]
    t_bath = float(block.split("Analysis bath temp.:")[1].split("K")[0])
    sample = block.split("Sample:")[1].split("Operator:")[0].strip()
    if abs(t_bath - inputs["isotherm"]["temperature"]["value"]) > 1e-6 or "CAU-10-H" not in sample:
        raise SystemExit(f"sample mapping changed: {sample!r} at {t_bath} K")
    return {"file": "8 - CAU-10-H.csv", "metadata_entry": "8. CAU-10-H", "sample": sample, "bath_temperature_K": t_bath}


# ---------------------------------------------------------------------------- properties
_N = [0.0, 0.11670521452767e4, -0.72421316703206e6, -0.17073846940092e2, 0.12020824702470e5,
      -0.32325550322333e7, 0.14915108613530e2, -0.48232657361591e4, 0.40511340542057e6,
      -0.23855557567849, 0.65017534844798e3]


def p_sat(T: float) -> float:
    """IAPWS-IF97 saturation pressure of water, Pa (region 4, 273.15 K to 647.096 K)."""
    th = T + _N[9] / (T - _N[10])
    A = th * th + _N[1] * th + _N[2]
    B = _N[3] * th * th + _N[4] * th + _N[5]
    C = _N[6] * th * th + _N[7] * th + _N[8]
    return (2 * C / (-B + math.sqrt(B * B - 4 * A * C))) ** 4 * 1e6


# IAPWS R7-97(2012), Table 35: computer-program verification values of the saturation pressure.
IF97_VERIFICATION_PA = {300.0: 0.353658941e4, 500.0: 0.263889776e7, 600.0: 0.123443146e8}


def check_p_sat() -> dict:
    out = {}
    for T, ref in IF97_VERIFICATION_PA.items():
        dev = p_sat(T) / ref - 1
        if abs(dev) > 1e-8:
            raise SystemExit(f"p_sat({T} K) deviates from the IF97 verification value by {dev:.2e}")
        out[f"{T:.0f}_K"] = {"reference_Pa": ref, "ours_Pa": round(p_sat(T), 4), "deviation_rel": float(f"{dev:.2e}")}
    return out


def vapour_density(T: float, rh: float) -> float:
    """Water vapour mass concentration in g/m3 (ideal gas)."""
    return rh * p_sat(T) * 0.018015 / (R_GAS * T) * 1000


# ---------------------------------------------------------------------------- isotherm tools
def x_at_loading(ads: np.ndarray, q: float) -> float:
    return float(np.interp(q, ads[:, 2], ads[:, 0]))


def q_ads(ads: np.ndarray, x):
    lo, hi = ads[0, 0], ads[-1, 0]
    x = np.asarray(x, dtype=float)
    if np.any(x < lo - 1e-12) or np.any(x > hi + 1e-12):
        raise ValueError("adsorption-branch request outside the measured range")
    return np.interp(x, ads[:, 0], ads[:, 2])


def q_des(iso: dict, x: float) -> float:
    des = iso["des"]
    xs, qs = des[::-1, 0], des[::-1, 2]
    if not (xs[0] <= x <= iso["des_monotonic_up_to"]):
        raise ValueError(f"desorption-branch request at p/p0 {x} outside the monotonic measured tail "
                         f"({xs[0]:.4f} to {iso['des_monotonic_up_to']:.4f})")
    n = iso["des_monotonic_n"]
    return float(np.interp(x, xs[:n], qs[:n]))


def ads_segment(ads: np.ndarray, x):
    """Measured adsorption points bracketing x: (x_lo, x_hi, q_lo, q_hi), in mmol/g; vectorised."""
    x = np.atleast_1d(np.asarray(x, dtype=float))
    i = np.clip(np.searchsorted(ads[:, 0], x, side="left"), 1, len(ads) - 1)
    exact = np.isclose(ads[i, 0], x, rtol=0, atol=1e-12) | np.isclose(ads[i - 1, 0], x, rtol=0, atol=1e-12)
    j = np.where(np.isclose(ads[i - 1, 0], x, rtol=0, atol=1e-12), i - 1, i)
    lo = np.where(exact, j, i - 1)
    hi = np.where(exact, j, i)
    return ads[lo, 0], ads[hi, 0], ads[lo, 2], ads[hi, 2]


# ---------------------------------------------------------------------------- reproduction
def reproduce(iso: dict, src: dict, tol: dict, T_iso: float, M_w: float) -> dict:
    ads, a = iso["ads"], iso["all"]
    cap = float(ads[-1, 2])
    alpha = x_at_loading(ads, 0.5 * cap)
    x25, x75 = x_at_loading(ads, 0.25 * cap), x_at_loading(ads, 0.75 * cap)
    dp = x75 - x25

    # Data integrity: implied p0 from the two pressure columns against IF97 at the bath temperature.
    sel = a[:, 0] > 0.01
    p0_implied = float(np.median(a[sel, 1] / a[sel, 0] * MMHG_PA))
    p0_if97 = p_sat(T_iso)
    p0_spread = float(np.max(np.abs(a[sel, 1] / a[sel, 0] * MMHG_PA / p0_implied - 1)))

    # Figure 7 markers: nearest alpha in panel b, partner in panel a by K_H.
    markers = src["reference_figure"]["cau10_h_markers"]
    cal = src["reference_figure"]["calibration"]

    def px_to(m):
        xa, ya = m["panel_a_px"]
        xb, yb = m["panel_b_px"]
        return {
            "id": m["id"],
            "delta_p_75_25": (xa - cal["panel_a_x"]["tick_px"][0]) / cal["panel_a_x"]["px_per_unit"],
            "alpha": (xb - cal["panel_b_x"]["tick_px"][0]) / cal["panel_b_x"]["px_per_unit"],
            "log10_KH_a": 3 + (cal["panel_a_y"]["decade_px"]["1e3"] - ya) / cal["panel_a_y"]["px_per_decade"],
            "log10_KH_b": 3 + (cal["panel_b_y"]["decade_px"]["1e3"] - yb) / cal["panel_b_y"]["px_per_decade"],
        }

    dig = [px_to(m) for m in markers]
    for d, m in zip(dig, markers):  # the recorded rounded values must follow from the pixels
        assert abs(d["alpha"] - m["alpha"]) < 6e-4 and abs(d["delta_p_75_25"] - m["delta_p_75_25"]) < 6e-4
    t_alpha = tol["checks"]["alpha"]["abs"]
    t_dp = tol["checks"]["delta_p_75_25"]["abs"]
    within = [d for d in dig if abs(d["alpha"] - alpha) <= t_alpha]
    nearest = min(dig, key=lambda d: abs(d["alpha"] - alpha))
    pair_ok = abs(nearest["log10_KH_a"] - nearest["log10_KH_b"]) <= 0.03
    ident_ok = len(within) == 1 and pair_ok
    second = sorted(dig, key=lambda d: abs(d["alpha"] - alpha))[1]

    # Candidate K_H (definition unavailable): ratio at the lowest measured point.
    kh_candidate = float(ads[0, 2] * V_STP / ads[0, 0])

    checks = {
        "alpha": {
            "reference": round(nearest["alpha"], 4), "ours": round(alpha, 4),
            "deviation": round(alpha - nearest["alpha"], 4), "tolerance_abs": t_alpha,
            "status": "pass" if abs(alpha - nearest["alpha"]) <= t_alpha else "fail",
        },
        "delta_p_75_25": {
            "reference": round(nearest["delta_p_75_25"], 4), "ours": round(dp, 4),
            "deviation": round(dp - nearest["delta_p_75_25"], 4), "tolerance_abs": t_dp,
            "status": "pass" if abs(dp - nearest["delta_p_75_25"]) <= t_dp else "fail",
        },
        "marker_identification": {
            "matched_marker": nearest["id"], "markers_within_alpha_tolerance": [d["id"] for d in within],
            "second_nearest": {"id": second["id"], "alpha": round(second["alpha"], 4),
                               "distance": round(abs(second["alpha"] - alpha), 4)},
            "panel_pair_log10_KH_difference": round(nearest["log10_KH_a"] - nearest["log10_KH_b"], 4),
            "status": "pass" if ident_ok else "fail",
        },
        "saturation_pressure": {
            "reference_Pa": round(p0_if97, 1), "ours_Pa": round(p0_implied, 1),
            "deviation_rel": round(p0_implied / p0_if97 - 1, 5),
            "tolerance_rel": tol["checks"]["saturation_pressure"]["rel"],
            "max_point_spread_rel": round(p0_spread, 5),
            "status": "pass" if abs(p0_implied / p0_if97 - 1) <= tol["checks"]["saturation_pressure"]["rel"] else "fail",
        },
    }
    st = {k: v["status"] for k, v in checks.items()}
    if all(s == "pass" for s in st.values()):
        verdict = "pass"
    elif st["saturation_pressure"] == "pass" and (st["alpha"] == "pass" or st["delta_p_75_25"] == "pass"):
        verdict = "partial"
    else:
        verdict = "fail"

    # Context comparisons (outside the pass rule).
    q_end_step = float(q_ads(ads, 0.25)) * M_w / 1000
    x10 = x_at_loading(ads, 0.10 * cap)
    x90 = x_at_loading(ads, 0.90 * cap)
    A_alpha = R_GAS * T_iso * math.log(1 / alpha)
    x_298 = math.exp(-A_alpha / (R_GAS * 298.15))
    context = {
        "henry_constant": {
            "reference_cm3_per_g": round(10 ** nearest["log10_KH_b"], -1),
            "candidate_ours_cm3_per_g": round(kh_candidate, 0),
            "candidate_definition": "q/(p/p0) at the lowest measured point, q in cm3(STP)/g",
            "status": "not evaluable (definition in SI Section 7 not available)",
        },
        "step_vs_pxrd_40C": {"reference": "0.15 to 0.165", "ours_alpha": round(alpha, 4),
                             "ours_step_10_to_90_percent": [round(x10, 4), round(x90, 4)],
                             "deviation_from_upper_end": round(alpha - 0.165, 4)},
        "uptake_after_step_vs_powder": {"reference_g_per_g": 0.32, "ours_at_0.25_g_per_g": round(q_end_step, 4),
                                        "deviation_rel": round(q_end_step / 0.32 - 1, 4)},
        "step_at_298K_characteristic_curve": {"reference": 0.18, "ours": round(x_298, 4),
                                              "deviation": round(x_298 - 0.18, 4)},
        "vapour_density_checks_g_per_m3": {
            "article_16pct_40C": 8, "ours_16pct_40C": round(vapour_density(313.15, 0.16), 2),
            "article_18pct_ambient": 4, "ours_18pct_25C": round(vapour_density(298.15, 0.18), 2),
        },
    }
    return {
        "descriptors": {"total_capacity_mmol_per_g": round(cap, 4),
                        "total_capacity_g_per_g": round(cap * M_w / 1000, 4),
                        "total_capacity_at_p_over_p0": round(float(ads[-1, 0]), 4),
                        "alpha": alpha, "x25": x25, "x75": x75, "x10": x10, "x90": x90,
                        "delta_p_75_25": dp},
        "digitised_markers": [{k: (round(v, 4) if isinstance(v, float) else v) for k, v in d.items()} for d in dig],
        "checks": checks, "verdict": verdict, "context_not_in_pass_rule": context,
    }


# ---------------------------------------------------------------------------- design
def design(iso: dict, inp: dict, desc: dict, M_w: float) -> dict:
    ads, des = iso["ads"], iso["des"]
    v = lambda *k: _get(inp, *k)["value"]  # noqa: E731
    T_ads = v("adsorption_state", "bed_temperature")
    T_iso = v("isotherm", "temperature")
    sw = v("adsorption_state", "inlet_relative_humidity_sweep")
    rh = np.round(np.arange(sw["from"], sw["to"] + 1e-9, sw["step"]), 6)
    x_reg = v("regeneration_state", "relative_pressure")
    T_cond = v("regeneration_state", "condenser_temperature")
    eta = v("recovery", "collection_recovery")
    Y = v("target", "water_yield_per_cycle")
    rho = v("bed", "packed_density")
    f_neg = v("feasibility", "negligible_working_capacity_fraction")
    cp_s = v("regeneration_heat", "adsorbent_heat_capacity")
    cp_w = v("regeneration_heat", "water_heat_capacity")
    h_fg = v("regeneration_heat", "vaporisation_enthalpy_313K")

    # Loadings are read from the isotherm at T_iso only; the design is defined for a bed at T_iso.
    if abs(T_ads - T_iso) > MAX_T_OFFSET_K:
        raise SystemExit(f"bed temperature {T_ads} K differs from the isotherm temperature {T_iso} K by more than "
                         f"{MAX_T_OFFSET_K} K: loadings at other temperatures are not supported (inputs.yaml)")

    g = M_w / 1000  # mmol/g -> g/g
    q_reg = q_des(iso, x_reg) * g
    q_hi = q_ads(ads, rh) * g
    dq = np.clip(q_hi - q_reg, 0.0, None)
    dq_ref = dq[-1]
    negligible = dq < f_neg * dq_ref
    with np.errstate(divide="ignore"):
        mass = np.where(dq > 0, Y / (eta * dq), np.inf)
    vol_L = mass / rho * 1000
    # Monotone bounds on the sweep: uptake between the measured end points of each segment.
    _, _, s_qlo, s_qhi = ads_segment(ads, rh)
    dq_lo = np.clip(s_qlo * g - q_reg, 0.0, None)
    dq_hi = np.clip(s_qhi * g - q_reg, 0.0, None)
    with np.errstate(divide="ignore"):
        mass_lo = np.where(dq_hi > 0, Y / (eta * dq_hi), np.inf)
        mass_hi = np.where(dq_lo > 0, Y / (eta * dq_lo), np.inf)

    # Threshold crossings solved on the interpolant (not on the sweep grid), with their segments.
    thr = f_neg * dq_ref
    rh_neg = x_at_loading(ads, (thr + q_reg) / g)
    rh_zero = x_at_loading(ads, q_reg / g)
    seg_neg = ads_segment(ads, rh_neg)
    seg_zero = ads_segment(ads, rh_zero)
    i_gap = int(np.argmax(np.diff(ads[:, 0])))

    # Regeneration temperature by the characteristic curve (equal adsorption potential).
    A_reg = R_GAS * T_iso * math.log(1 / x_reg)
    p_cond = p_sat(T_cond)
    T_reg = brentq(lambda T: R_GAS * T * math.log(p_sat(T) / p_cond) - A_reg, T_cond + 1, 450.0)
    # Adsorption enthalpy estimate (Dubinin): h_fg + A at the step.
    dh_ads = h_fg + R_GAS * T_iso * math.log(1 / desc["alpha"]) / M_w  # kJ/kg (J/mol / g/mol = kJ/kg)

    def heat_per_kg_collected(dq_i, qhi_i):
        sensible = (cp_s + qhi_i * cp_w) * (T_reg - T_ads) / dq_i  # kJ per kg desorbed
        return (sensible + dh_ads) / eta, sensible / eta, dh_ads / eta

    def bounds(rh_i):
        """Monotone bracket from the two measured adsorption points around rh_i."""
        xl, xh, ql, qh_ = (float(a[0]) for a in ads_segment(ads, rh_i))
        ql, qh_ = ql * g, qh_ * g
        wide = bool((qh_ / ql - 1) > LOOSE_REL_UPTAKE or (xh - xl) > LOOSE_DX)
        dl, dh = max(ql - q_reg, 0.0), max(qh_ - q_reg, 0.0)
        out = {"segment_p_over_p0": [round(xl, 4), round(xh, 4)], "segment_uptake_g_per_g": [round(ql, 4), round(qh_, 4)],
               "wide_segment": wide, "working_capacity_g_per_g": [round(dl, 4), round(dh, 4)],
               "adsorbent_mass_kg": [round(Y / (eta * dh), 1) if dh > 0 else None,
                                     round(Y / (eta * dl), 1) if dl > 0 else None]}
        if dh > 0:
            heat = [heat_per_kg_collected(dh, qh_)[0] / 3600, heat_per_kg_collected(dl, ql)[0] / 3600 if dl > 0 else None]
            out["regeneration_heat_kWh_per_kg_water"] = [round(heat[0], 2), round(heat[1], 2) if heat[1] else None]
        return out

    def case(rh_i):
        qh = float(q_ads(ads, rh_i)) * g
        d = max(qh - q_reg, 0.0)
        out = {"inlet_relative_humidity": rh_i, "vapour_density_g_per_m3": round(vapour_density(T_ads, rh_i), 2),
               "uptake_end_of_adsorption_g_per_g": round(qh, 4), "working_capacity_g_per_g": round(d, 4),
               "negligible": bool(d < f_neg * dq_ref)}
        if d > 0:
            m = Y / (eta * d)
            tot, sens, lat = heat_per_kg_collected(d, qh)
            out.update({"adsorbent_mass_kg": round(m, 2), "packed_volume_L": round(m / rho * 1000, 1),
                        "regeneration_heat_MJ_per_kg_water": round(tot / 1000, 3),
                        "of_which_sensible_MJ_per_kg": round(sens / 1000, 3),
                        "of_which_desorption_MJ_per_kg": round(lat / 1000, 3),
                        "regeneration_heat_kWh_per_kg_water": round(tot / 3600, 3),
                        "mean_heat_duty_W": round(tot * Y * 1000 / (v("cycle", "desorption_time") * 3600), 0)})
        else:
            out.update({"adsorbent_mass_kg": None, "note": "no net uptake above the regeneration loading"})
        out["interpolation_bounds"] = bounds(rh_i)
        return out

    base = case(v("changed_input_example", "base_relative_humidity"))
    changed = case(v("changed_input_example", "changed_relative_humidity"))
    ratio = (changed["adsorbent_mass_kg"] / base["adsorbent_mass_kg"]) if changed["adsorbent_mass_kg"] else None
    cb = changed["interpolation_bounds"]["adsorbent_mass_kg"]
    ratio_bounds = [round(x / base["adsorbent_mass_kg"], 1) if x else None for x in cb]

    # One-at-a-time sensitivity of the base case (all within measured data or plain scaling).
    rh_b = v("changed_input_example", "base_relative_humidity")
    qh_b = float(q_ads(ads, rh_b)) * g
    sens = {}
    for x_alt in (float(des[-1, 0]), float(des[-2, 0])):  # the two lowest measured desorption points
        d_alt = qh_b - q_des(iso, x_alt) * g
        sens[f"regeneration_p_over_p0_{x_alt:.4f}"] = {"adsorbent_mass_kg": round(Y / (eta * d_alt), 2)}
    for eta_alt in (0.6, 0.9):
        sens[f"recovery_{eta_alt}"] = {"adsorbent_mass_kg": round(Y / (eta_alt * base["working_capacity_g_per_g"]), 2)}
    for rho_alt in (400, 800):
        sens[f"packed_density_{rho_alt}"] = {"packed_volume_L": round(base["adsorbent_mass_kg"] / rho_alt * 1000, 1)}
    # Adsorption enthalpy: Dubinin estimate with an assumed +-10 % range (inputs.yaml).
    for f in (0.9, 1.1):
        row = {}
        for name in ("base", "changed"):
            qh = float(q_ads(ads, v("changed_input_example", f"{name}_relative_humidity"))) * g
            sens_part = (cp_s + qh * cp_w) * (T_reg - T_ads) / (qh - q_reg)
            row[f"{name}_regeneration_heat_kWh_per_kg_water"] = round((sens_part + f * dh_ads) / eta / 3600, 3)
        sens[f"adsorption_enthalpy_x{f}"] = row

    return {
        "label": "HYPOTHETICAL design extension (not validated)",
        "supported_states": {
            "isotherm_temperature_K": T_iso,
            "adsorption": f"bed and inlet air at {T_ads} K, inlet RH {float(ads[0,0]):.4f} to {float(ads[-1,0]):.4f} (measured adsorption branch)",
            "regeneration": f"relative pressure {x_reg} on the measured desorption branch (lowest point {float(des[-1,0]):.4f})",
            "not_supported": f"inlet RH above {float(ads[-1,0]):.4f}; any loading at a temperature other than {T_iso} K",
            "bed_temperature_check": f"|T_bed - T_iso| = {abs(T_ads - T_iso):.2f} K <= {MAX_T_OFFSET_K} K (enforced; "
                                     "run.py stops otherwise)",
            "desorption_lookups_up_to_p_over_p0": round(iso["des_monotonic_up_to"], 4),
        },
        "adsorption_branch_largest_gap_p_over_p0": [round(float(ads[i_gap, 0]), 4), round(float(ads[i_gap + 1, 0]), 4)],
        "regeneration_loading_g_per_g": round(q_reg, 4),
        "regeneration_temperature_K": round(T_reg, 2),
        "regeneration_temperature_C": round(T_reg - 273.15, 1),
        "regeneration_temperature_flag": "extrapolated: characteristic-curve transfer outside the measured 288 K to 313 K",
        "condenser_temperature_K": T_cond, "condenser_vapour_pressure_Pa": round(p_cond, 1),
        "adsorption_enthalpy_kJ_per_kg": round(dh_ads, 1),
        "adsorption_enthalpy_kJ_per_mol": round(dh_ads * M_w / 1000, 2),
        "working_capacity_at_highest_rh_g_per_g": round(float(dq_ref), 4),
        "negligible_threshold_g_per_g": round(float(f_neg * dq_ref), 4),
        "minimum_feasible_inlet_rh": round(rh_neg, 4),
        "minimum_feasible_inlet_rh_segment": [round(float(seg_neg[0][0]), 4), round(float(seg_neg[1][0]), 4)],
        "minimum_feasible_inlet_rh_note": "working capacity equals the negligible threshold; solved on the linear "
                                          "interpolant; the monotone bracket is the measured segment",
        "zero_working_capacity_rh_linear": round(rh_zero, 4),
        "zero_working_capacity_rh_segment": [round(float(seg_zero[0][0]), 4), round(float(seg_zero[1][0]), 4)],
        "zero_working_capacity_note": "no measured adsorption point in this segment; the crossing can lie anywhere in it",
        "step_region_rh": [round(desc["x10"], 4), round(desc["x90"], 4)],
        "step_inflection_rh": round(desc["alpha"], 4),
        "interpolation_bounds_rule": (
            "bounds use the uptake at the measured adsorption points either side (the isotherm is monotonic); "
            f"wide_segment marks a segment with more than {LOOSE_REL_UPTAKE:.0%} change in uptake or more than "
            f"{LOOSE_DX} in p/p0; a null upper mass bound means the lower end of the segment has no net uptake"),
        "base_case": base, "changed_case": changed,
        "mass_ratio_changed_over_base": round(ratio, 2) if ratio else None,
        "mass_ratio_changed_over_base_bounds": ratio_bounds,
        "sensitivity_of_base_case": sens,
        "design_points": [case(x) for x in DESIGN_POINTS_RH],
        # Per-point resampling of the CC BY-SA 4.0 isotherm: written to results/sweep.json, not committed.
        "sweep": {"inlet_relative_humidity": rh.tolist(),
                  "working_capacity_g_per_g": np.round(dq, 5).tolist(),
                  "adsorbent_mass_kg": [None if not np.isfinite(m) else round(float(m), 3) for m in mass],
                  "adsorbent_mass_bounds_kg": [[None if not np.isfinite(a) else round(float(a), 3),
                                                None if not np.isfinite(b) else round(float(b), 3)]
                                               for a, b in zip(mass_lo, mass_hi)],
                  "packed_volume_L": [None if not np.isfinite(x) else round(float(x), 2) for x in vol_L],
                  "negligible": negligible.tolist()},
    }


def _get(d, *keys):
    for k in keys:
        d = d[k]
    return d


# ---------------------------------------------------------------------------- figures
def _style():
    plt.rcParams.update({
        "svg.hashsalt": CASE_ID, "svg.fonttype": "path", "font.size": 9,
        "axes.edgecolor": INK2, "axes.labelcolor": INK, "xtick.color": INK2, "ytick.color": INK2,
        "axes.spines.top": False, "axes.spines.right": False, "figure.facecolor": SURFACE,
        "axes.facecolor": SURFACE, "axes.grid": True, "grid.color": "#e6e5e1", "grid.linewidth": 0.6,
        "lines.linewidth": 2, "legend.frameon": False,
    })


def _save(fig, name):
    fig.savefig(RESULTS / name, format="svg", metadata={"Date": None, "Creator": None}, facecolor=SURFACE)
    plt.close(fig)


def fig_isotherm(iso, desc, des_reg, M_w):
    g = M_w / 1000
    ads, des = iso["ads"], iso["des"]
    fig, ax = plt.subplots(figsize=(6.4, 4.2))
    ax.plot(ads[:, 0], ads[:, 2] * g, "-o", color=C_ADS, ms=3.5, lw=1.5, label="adsorption branch")
    ax.plot(des[:, 0], des[:, 2] * g, "-o", color=C_DES, ms=3.5, lw=1.5, mfc=SURFACE, label="desorption branch")
    cap = desc["total_capacity_mmol_per_g"] * g
    for f, x, lab in [(0.25, desc["x25"], "25 %"), (0.5, desc["alpha"], "α (50 %)"), (0.75, desc["x75"], "75 %")]:
        ax.plot([x], [f * cap], "D", color=INK, ms=4.5, zorder=5)
        ax.annotate(f"{lab}: p/p0 = {x:.4f}", (x, f * cap), xytext=(12, -3), textcoords="offset points", color=INK, fontsize=8)
    ax.plot([des_reg[0]], [des_reg[1]], "s", color=INK2, ms=5, zorder=5)
    ax.annotate(f"regeneration state\n(desorption branch)\np/p0 = {des_reg[0]}", des_reg, xytext=(-10, 40), textcoords="offset points",
                color=INK2, fontsize=8, arrowprops={"arrowstyle": "-", "color": INK2, "lw": 0.6})
    ax.axvspan(ads[-1, 0], 0.5, color=SHADE_STEP, lw=0)
    ax.text(0.462, 0.02, "not\nmeasured", color=INK2, fontsize=8, ha="center")
    ax.set_xlim(0, 0.5)
    ax.set_ylim(0, 0.33)
    ax.set_xlabel("relative pressure p/p0 (-)")
    ax.set_ylabel("water uptake (g per g pellet)")
    ax.set_title("CAU-10-H pellets, 313 K: measured water uptake (4TU 10.4121/22009211, sample 8)", fontsize=9, color=INK, loc="left")
    ax.legend(loc="lower right", bbox_to_anchor=(0.86, 0.06))
    _save(fig, "isotherm_cau10h_313K.svg")


def fig_reproduction(rep, tol):
    fig, ax = plt.subplots(figsize=(5.2, 4.0))
    dig = rep["digitised_markers"]
    ax.errorbar([d["alpha"] for d in dig], [d["delta_p_75_25"] for d in dig], xerr=0.0013, yerr=0.0016,
                fmt="o", color=C_REF, ms=6, capsize=2, label="Figure 7, CAU-10-H markers (digitised)")
    for d in dig:
        ax.annotate(d["id"], (d["alpha"], d["delta_p_75_25"]), xytext=(5, 5), textcoords="offset points", color=INK2, fontsize=8)
    a, dp = rep["descriptors"]["alpha"], rep["descriptors"]["delta_p_75_25"]
    ta, td = tol["checks"]["alpha"]["abs"], tol["checks"]["delta_p_75_25"]["abs"]
    ax.add_patch(plt.Rectangle((a - ta, dp - td), 2 * ta, 2 * td, fill=False, ec=C_ADS, ls="--", lw=1.2))
    ax.plot([a], [dp], "D", color=C_ADS, ms=7, label="computed from sample 8 (box: frozen tolerance)")
    ax.set_xlabel("α, relative pressure at half capacity (-)")
    ax.set_ylabel("Δp/p0 between 75 % and 25 % of capacity (-)")
    ax.set_xlim(0.13, 0.21)
    ax.set_ylim(-0.004, 0.022)
    ax.set_title(f"Reproduction of Figure 7 descriptors: verdict {rep['verdict'].upper()}", fontsize=9, color=INK, loc="left")
    ax.legend(loc="upper left", fontsize=8)
    _save(fig, "reproduction_figure7.svg")


def fig_headline(dsn, iso_top):
    sw = dsn["sweep"]
    rh = np.array(sw["inlet_relative_humidity"])
    m = np.array([np.nan if x is None else x for x in sw["adsorbent_mass_kg"]])
    neg = np.array(sw["negligible"])
    fig, ax = plt.subplots(figsize=(6.8, 4.4))
    rh_min = dsn["minimum_feasible_inlet_rh"]
    ax.axvspan(0.0, rh_min, color=SHADE_INFEASIBLE, lw=0)
    ax.text(0.115, 7, f"INFEASIBLE\nworking capacity\n< {dsn['negligible_threshold_g_per_g']:.3f} g/g:\nbelow the step", color=INK, fontsize=8, ha="center", va="center")
    s0, s1 = dsn["step_region_rh"]
    ax.axvspan(s0, s1, color=SHADE_STEP, lw=0, hatch="///", ec="#b9b8b3")
    ax.axvspan(iso_top, 0.45, color=SHADE_STEP, lw=0)
    ax.text(0.437, 7, "not\nmeasured", color=INK2, fontsize=8, ha="center", va="center")
    b = np.array([[np.nan if x is None else x for x in pair] for pair in sw["adsorbent_mass_bounds_kg"]], dtype=float)
    b[np.isnan(b[:, 1]), 1] = 1e4  # unbounded above: no net uptake at the lower end of the segment
    ax.fill_between(rh, b[:, 0], b[:, 1], color=C_ADS, alpha=0.15, lw=0,
                    label="bounds from the measured points either side")
    g0, g1 = dsn["adsorption_branch_largest_gap_p_over_p0"]
    ax.annotate("", xy=(g0, 1500), xytext=(g1, 1500), arrowprops={"arrowstyle": "<->", "color": INK2, "lw": 0.6})
    ax.text(0.5 * (g0 + g1), 1300, f"no measured adsorption\npoints, p/p0 {g0:.3f} to {g1:.3f}", color=INK2, fontsize=7.5,
            ha="center", va="top")
    ax.plot(rh[~neg], m[~neg], color=C_ADS, label="required adsorbent mass (linear interpolation)")
    ax.plot(rh[neg], m[neg], color=C_ADS, lw=1, ls=":")
    for c, lab, off in [(dsn["base_case"], "base", (8, 8)), (dsn["changed_case"], "changed input", (-122, -40))]:
        if c["adsorbent_mass_kg"]:
            ax.plot([c["inlet_relative_humidity"]], [c["adsorbent_mass_kg"]], "o", color=INK, ms=6, zorder=5)
            lo, hi = c["interpolation_bounds"]["adsorbent_mass_kg"]
            span = f"\n(bounds {lo:.0f} to {hi:.0f} kg)" if c["interpolation_bounds"]["wide_segment"] and hi and hi / lo > 1.2 else ""
            ax.annotate(f"{lab}: RH {c['inlet_relative_humidity']:.2f}\n{c['adsorbent_mass_kg']:.3g} kg, {c['packed_volume_L']:.0f} L{span}",
                        (c["inlet_relative_humidity"], c["adsorbent_mass_kg"]), xytext=off, textcoords="offset points", color=INK, fontsize=8)
    ax.annotate(f"step {s0:.3f} to {s1:.3f}\n(mass very sensitive to RH)", (0.5 * (s0 + s1), 40), xytext=(22, 0),
                textcoords="offset points", color=INK2, fontsize=8, va="center", arrowprops={"arrowstyle": "-", "color": INK2, "lw": 0.6})
    ax.set_yscale("log")
    ax.set_ylim(2, 2000)
    ax.set_xlim(0.05, 0.45)
    ax.set_xlabel("inlet relative humidity at the bed, 313 K (-)")
    ax.set_ylabel("adsorbent mass per cycle (kg pellets)")
    ax.set_title("CAU-10-H harvester: adsorbent for 1 kg water per cycle at 80 % recovery\n"
                 "(regeneration at p/p0 0.05; packed volume = mass / 600 kg/m3)", fontsize=9, color=INK, loc="left")
    ax.legend(loc="center right", bbox_to_anchor=(1.0, 0.62), fontsize=8)
    _save(fig, "harvester_mass_vs_rh.svg")


# ---------------------------------------------------------------------------- main
def main() -> int:
    src = yaml.safe_load((HERE / "source.yaml").read_text())
    inp = yaml.safe_load((HERE / "inputs.yaml").read_text())
    tol = yaml.safe_load((HERE / "tolerances.yaml").read_text())
    if9_check = check_p_sat()
    files = {f["name"]: f for f in src["dataset"]["files"]}
    csv = fetch(files["8 - CAU-10-H.csv"])
    meta = fetch(files["Metadata.txt"])
    mapping = check_mapping(meta, inp)
    iso = read_isotherm(csv)
    T_iso = inp["isotherm"]["temperature"]["value"]
    M_w = inp["isotherm"]["molar_mass_water"]["value"]

    rep = reproduce(iso, src, tol, T_iso, M_w)
    dsn = design(iso, inp, rep["descriptors"], M_w)

    RESULTS.mkdir(exist_ok=True)
    _style()
    x_reg = inp["regeneration_state"]["relative_pressure"]["value"]
    fig_isotherm(iso, rep["descriptors"], (x_reg, dsn["regeneration_loading_g_per_g"]), M_w)
    fig_reproduction(rep, tol)
    fig_headline(dsn, float(iso["ads"][-1, 0]))  # uses dsn["sweep"], which goes to sweep.json below

    rep["descriptors"] = {k: (round(v, 5) if isinstance(v, float) else v) for k, v in rep["descriptors"].items()}
    sweep = dsn.pop("sweep")
    dsn["sweep_file"] = "results/sweep.json (written by run.py, git-ignored: per-point resampling of the CC BY-SA 4.0 data)"
    data_source = {
        "doi": src["dataset"]["doi"], "title": src["dataset"]["title"], "authors": src["dataset"]["authors"],
        "repository": src["dataset"]["repository"], "file": "8 - CAU-10-H.csv",
        "licence": src["dataset"]["licence"]["name"], "licence_url": src["dataset"]["licence"]["url"],
        "use": "interpolated and transformed by run.py (descriptors, working capacities, sizing); the data file is not "
               "redistributed",
    }
    (RESULTS / "sweep.json").write_text(json.dumps({"case": CASE_ID, "data_source": data_source,
                                                    "label": dsn["label"], "sweep": sweep}, indent=2,
                                                   ensure_ascii=False) + "\n")
    out = {
        "case": CASE_ID, "issue": 334, "tracker": 333,
        "command": f"uv run benchmarks/reproductions/{CASE_ID}/run.py",
        "versions": {"python": sys.version.split()[0], "numpy": np.__version__, "scipy": scipy.__version__,
                     "matplotlib": matplotlib.__version__, "pyyaml": yaml.__version__},
        "data_source": data_source,
        "tolerances_file": "tolerances.yaml",
        "if97_verification": if9_check,
        "inputs_sha256": {n: sha256(HERE / n) for n in ("source.yaml", "inputs.yaml", "tolerances.yaml")},
        "data_sha256_verified": {n: f["sha256"] for n, f in files.items()},
        "sample_mapping": mapping,
        "measured_series": {"adsorption_points": int(len(iso["ads"])), "desorption_points": int(len(iso["des"]) - 1),
                            "p_over_p0_range_adsorption": [float(iso["ads"][0, 0]), float(iso["ads"][-1, 0])],
                            "p_over_p0_lowest_desorption": float(iso["des"][-1, 0]),
                            "desorption_monotonic_up_to_p_over_p0": iso["des_monotonic_up_to"]},
        "reproduction": rep,
        "design_extension": dsn,
        "figures": ["isotherm_cau10h_313K.svg", "reproduction_figure7.svg", "harvester_mass_vs_rh.svg"],
    }
    (RESULTS / "comparison.json").write_text(json.dumps(out, indent=2, ensure_ascii=False) + "\n")

    c = rep["checks"]
    print(f"verdict {rep['verdict']}: alpha {c['alpha']['ours']} vs {c['alpha']['reference']} ({c['alpha']['status']}), "
          f"dp75-25 {c['delta_p_75_25']['ours']} vs {c['delta_p_75_25']['reference']} ({c['delta_p_75_25']['status']}), "
          f"marker {c['marker_identification']['matched_marker']} ({c['marker_identification']['status']}), "
          f"p0 {c['saturation_pressure']['ours_Pa']} vs {c['saturation_pressure']['reference_Pa']} Pa ({c['saturation_pressure']['status']})")
    b, ch = dsn["base_case"], dsn["changed_case"]
    print(f"design: RH {b['inlet_relative_humidity']} -> {b['adsorbent_mass_kg']} kg; RH {ch['inlet_relative_humidity']} -> "
          f"{ch['adsorbent_mass_kg']} kg (bounds {ch['interpolation_bounds']['adsorbent_mass_kg']}); "
          f"feasible from RH {dsn['minimum_feasible_inlet_rh']}; T_reg {dsn['regeneration_temperature_C']} °C")
    print(f"wrote {RESULTS}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
