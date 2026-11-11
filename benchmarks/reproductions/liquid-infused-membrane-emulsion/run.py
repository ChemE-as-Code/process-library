# /// script
# requires-python = ">=3.12,<3.14"
# dependencies = [
#     "numpy==2.3.4",
#     "matplotlib==3.10.7",
#     "pyyaml==6.0.3",
# ]
# ///
"""Liquid-infused membrane, oil-in-water emulsion: selective operating window (#340).

Reproduces the entry-pressure (gating) results of Bazyar, van de Beek and Lammertink,
Langmuir 35 (2019) 9513, doi:10.1021/acs.langmuir.9b01055, from the inputs restated in
inputs.yaml, compares them with the reported results in source.yaml under the frozen
tolerances.yaml, sweeps the transmembrane pressure, estimates membrane area for the one case
with flux data, and runs the hypothetical design extension (pore radius).

Rerun from the repository root:

    uv run benchmarks/reproductions/liquid-infused-membrane-emulsion/run.py

Writes results/ next to this file. The article XML is fetched into a cache outside git
($XDG_CACHE_HOME or ~/.cache, cheme-reproductions/<id>/) and checked against its pinned sha256;
it is parsed as data and never executed. Without network the check is recorded as skipped.
Exit status is non-zero only if the script itself fails, not if the reproduction fails.
"""

from __future__ import annotations

import hashlib
import json
import math
import os
import platform
import sys
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

import matplotlib
import numpy as np
import yaml

matplotlib.use("svg")
import matplotlib.pyplot as plt  # noqa: E402

CASE_ID = "liquid-infused-membrane-emulsion"
HERE = Path(__file__).resolve().parent
RESULTS = HERE / "results"
BAR = 1.0e5  # Pa

# Colours: categorical slots 1-3 and status colours of the reference palette (dataviz skill).
C_SERIES = ["#2a78d6", "#eb6834", "#1baf7a"]
C_GOOD, C_CRIT, C_NEUTRAL = "#0ca30c", "#d03b3b", "#d9d8d4"
C_TEXT, C_TEXT2, C_SURFACE = "#0b0b0b", "#52514e", "#fcfcfb"


# ----------------------------------------------------------------------------- inputs
def load_yaml(name: str) -> dict:
    with open(HERE / name, encoding="utf-8") as fh:
        return yaml.safe_load(fh)


INP = load_yaml("inputs.yaml")
SRC = load_yaml("source.yaml")
TOL = load_yaml("tolerances.yaml")
REP = SRC["reported_results"]

SURFS = ["SDS", "CTAB"]
LEVELS = ["10", "50"]
OILS = ["hexadecane", "K101"]


def v(node):
    return node["value"] if isinstance(node, dict) else node


CMC = {s: v(INP["surfactants"]["cmc"][s]) for s in SURFS}  # mol/m3
LEVEL = {lv: v(INP["surfactants"]["concentration_levels"][lv]) for lv in LEVELS}
GSTAR = {o: v(INP["interfacial_tension"]["gamma_star"][o]) * 1e-3 for o in OILS}  # N/m
G23 = v(INP["interfacial_tension"]["gamma_hexadecane_K101"]) * 1e-3  # N/m
SZ = INP["interfacial_tension"]["szyszkowski"]
RAD = INP["entry_pressure_model"]["curvature_radius"]
FIT_RANGE = v(INP["interfacial_tension"]["fit_range"])
THETA = math.radians(v(INP["entry_pressure_model"]["contact_angle"]))


def radius(surf: str, oil: str, shift: float = 0.0) -> float:
    """Fitted curvature radius in m; shift in units of the half confidence interval."""
    node = RAD[f"{surf}_{oil}"]
    return (node["value"] + shift * node["hci"]) * 1e-6


def gamma(surf: str, oil: str, c: float, a_shift: float = 0.0, b_shift: float = 0.0) -> float:
    """Szyszkowski IFT (N/m) of the aqueous solution against the oil at concentration c (mol/m3)."""
    p = SZ[f"{surf}_{oil}"]
    a = p["a"] + a_shift * p["a_hci"]
    b = p["b"] + b_shift * p["b_hci"]
    # clipped at zero: the fit corners (a - hci, b + hci) can give a negative IFT at high C
    return max(0.0, GSTAR[oil] * (1.0 - b * math.log1p(c / a)))


def entry(gam: float, r: float) -> float:
    """Young-Laplace entry pressure (bar), eq 1."""
    return 2.0 * gam * abs(math.cos(THETA)) / r / BAR


def conc(surf: str, frac: float) -> float:
    return frac * CMC[surf]


# --------------------------------------------------------------------- source check
def cache_dir() -> Path:
    base = os.environ.get("XDG_CACHE_HOME") or str(Path.home() / ".cache")
    d = Path(base) / "cheme-reproductions" / CASE_ID
    d.mkdir(parents=True, exist_ok=True)
    return d


def source_check() -> dict:
    spec = SRC["reference"]["files"][0]
    url, want = spec["url"], spec["sha256"]
    path = cache_dir() / "PMC6750837.1.xml"
    out = {"url": url, "sha256_pinned": want,
           "cache_file": f"cheme-reproductions/{CASE_ID}/{path.name} under $XDG_CACHE_HOME or ~/.cache"}
    try:
        if not path.exists():
            req = urllib.request.Request(url, headers={"User-Agent": "cheme-reproductions/1"})
            with urllib.request.urlopen(req, timeout=60) as resp:
                data = resp.read()
            tmp = path.with_suffix(".part")
            tmp.write_bytes(data)
            tmp.replace(path)
        data = path.read_bytes()
    except Exception as exc:  # network or file errors: the check is a gap, not a failure
        out["status"] = f"skipped: {type(exc).__name__}: {exc}"
        return out
    got = hashlib.sha256(data).hexdigest()
    out["sha256_found"] = got
    if got != want:
        out["status"] = "hash mismatch (the PMC record may have been reissued); anchors not checked"
        return out
    root = ET.fromstring(data)  # parsed as data only
    body = root.find(".//body")
    text = " ".join("".join(body.itertext()).split())
    anchors = {
        "hexadecane LEP through K101-infused, 0.08 bar": "0.08 bar",
        "gamma23 = 8.7 +- 0.08 mN/m": "8.7 ± 0.08 mN/m",
        "combined LEP 0.26 and 0.15 bar": "0.26 and 0.15 bar",
        "CTAB50 LEP 0.05 bar": "0.05 bar",
        "SDS50 LEP 0.15 bar": "0.15 bar",
        "TMP at most 0.1 bar": "≤0.1 bar",
        "largest pore radius 1.92 um": "1.92 μm",
        "r CTAB-hexadecane 1.63": "1.63 ± 6.96 × 10–2",
        "r CTAB-K101 1.82": "1.82 ± 3.41 × 10–2",
        "r SDS-hexadecane 1.66": "1.66 ± 9.25 × 10–2",
        "r SDS-K101 1.82": "1.82 ± 4.06 × 10–2",
        "a CTAB-hexadecane 4.02e-3": "4.02 × 10–3",
        "a SDS-hexadecane 2.08": "2.08 ± 8.31",
        "a SDS-K101 2.24": "2.24 ± 2.64",
        "cmc SDS 8.1": "8.1 (at 20–25 °C)",
        "cmc CTAB 0.92": "0.92 (at 20–25 °C)",
    }
    found = {k: (s in text) for k, s in anchors.items()}
    # Table 3 rows: emulsion, K101-infused, dry
    rows = []
    for tw in root.iter("table-wrap"):
        label = tw.find("label")
        if label is not None and "".join(label.itertext()).strip() == "Table 3":
            for tr in tw.iter("tr"):
                rows.append([" ".join("".join(td.itertext()).split()) for td in tr])
    wf = REP["water_fraction_in_permeate"]
    for em in ["SDS10", "SDS50", "CTAB10", "CTAB50"]:
        name = em[:-2] + " " + em[-2:]
        want_row = [name, f"{wf['K101_infused'][em]:g}", f"{wf['dry'][em]:g}"]
        found[f"Table 3 row {name}"] = want_row in rows
    out["anchors"] = found
    out["status"] = "ok" if all(found.values()) else "anchor missing"
    return out


# ------------------------------------------------------------------------- checks
def band_pass(value, ref, tol):
    return abs(value - ref) <= tol


def check_ift() -> list[dict]:
    meas = REP["ift_measured"]
    rows = []
    for s in SURFS:
        for o in OILS:
            for lv in LEVELS:
                c = conc(s, LEVEL[lv])
                g = gamma(s, o, c) * 1e3
                g_lo = gamma(s, o, c, a_shift=-1, b_shift=+1) * 1e3
                g_hi = gamma(s, o, c, a_shift=+1, b_shift=-1) * 1e3
                m = meas[f"{s}{lv}_{o}"]
                # an IFT cannot be negative: the reported lower bound is clipped at 0 (the
                # comparison itself is unchanged, every measured value is positive)
                lo, hi = max(0.0, g_lo - 2 * m["sd"]), g_hi + 2 * m["sd"]
                dev = g - m["value"]
                rows.append({
                    "quantity": f"IFT {s}{lv} / {o}", "unit": "mN/m",
                    "reference": m["value"], "computed": round(g, 3),
                    "deviation": round(dev, 3),
                    "tolerance": f"in [{lo:.2f}, {hi:.2f}] (fit CI box +- 2 sd)",
                    "pass": bool(lo <= m["value"] <= hi),
                    # informational, not in the pass rule: the band tests consistency with the
                    # fit's box uncertainty, not with the measurement's own standard deviation
                    "deviation_pct": round(dev / m["value"] * 100, 2),
                    "abs_deviation_in_measurement_sd": round(abs(dev) / m["sd"], 2),
                })
    return rows


def check_fig4b() -> list[dict]:
    pts = REP["lep_figure4b_digitised"]["points"]
    tol = TOL["checks"]["lep_figure4b"]["abs_bar"]
    rows = []

    def add(name, ref, comp, t, note=""):
        rows.append({
            "quantity": f"LEP {name} (Fig. 4b, digitised)", "unit": "bar",
            "reference": ref, "computed": round(comp, 4), "deviation": round(comp - ref, 4),
            "tolerance": f"abs {t}", "pass": band_pass(comp, ref, t), "note": note,
        })

    for s in SURFS:
        add(f"water / hexadecane-infused ({s} fit radius)", pts["water_hexadecane_infused"]["value"],
            entry(GSTAR["hexadecane"], radius(s, "hexadecane")), tol["default"],
            "one digitised value for both series (overlapping markers)")
    add("water / K101-infused", pts["water_K101_infused"]["value"],
        entry(GSTAR["K101"], radius("SDS", "K101")), tol["default"], "both K101 fits have r = 1.82 um")
    for s in SURFS:
        for lv in LEVELS:
            for o, key in [("hexadecane", "hexadecane_infused"), ("K101", "K101_infused")]:
                ref = pts[f"{s}{lv}_{key}"]["value"]
                comp = entry(gamma(s, o, conc(s, LEVEL[lv])), radius(s, o))
                t = tol["CTAB_hexadecane"] if (s == "CTAB" and o == "hexadecane") else tol["default"]
                add(f"{s}{lv} / {o}-infused", ref, comp, t, pts[f"{s}{lv}_{key}"].get("note", ""))
    return rows


def lep_water_combined(s: str, lv: str, r_oil: str = "hexadecane") -> float:
    c = conc(s, LEVEL[lv])
    return entry(gamma(s, "hexadecane", c) + G23, radius(s, r_oil))


def check_stated() -> list[dict]:
    st = REP["lep_stated_in_text"]
    t1 = TOL["checks"]["lep_stated_hexadecane_infused"]["abs_bar"]
    t2 = TOL["checks"]["lep_combined_interface"]["abs_bar"]
    t3 = TOL["checks"]["lep_hexadecane_K101"]["abs_bar"]
    rows = []
    for s, key in [("SDS", "SDS50_through_hexadecane_infused"), ("CTAB", "CTAB50_through_hexadecane_infused")]:
        comp = entry(gamma(s, "hexadecane", conc(s, LEVEL["50"])), radius(s, "hexadecane"))
        ref = st[key]["value"]
        rows.append({"quantity": f"LEP {s}50 / hexadecane-infused (text)", "unit": "bar", "reference": ref,
                     "computed": round(comp, 4), "deviation": round(comp - ref, 4),
                     "tolerance": f"abs {t1[s + '50']}", "pass": band_pass(comp, ref, t1[s + "50"])})
    comb = st["combined_interface_K101_infused_under_hexadecane"]
    for s in SURFS:
        comp = lep_water_combined(s, "50")
        ref = comb[f"{s}50"]["value"]
        rows.append({"quantity": f"LEP {s}50 / K101-infused under hexadecane, gamma12 + gamma23 (text)",
                     "unit": "bar", "reference": ref, "computed": round(comp, 4),
                     "deviation": round(comp - ref, 4), "tolerance": f"abs {t2}",
                     "pass": band_pass(comp, ref, t2)})
    comp = entry(G23, radius("SDS", "K101"))
    ref = st["hexadecane_through_K101_infused"]["value"]
    rows.append({"quantity": "LEP hexadecane / K101-infused (text)", "unit": "bar", "reference": ref,
                 "computed": round(comp, 4), "deviation": round(comp - ref, 4),
                 "tolerance": f"abs {t3}", "pass": band_pass(comp, ref, t3)})
    return rows


DARCY = v(INP["constants"]["darcy"])
MU_OIL = v(INP["fluids"]["hexadecane_viscosity"]) * 1e-3
L_MEM = v(INP["membrane"]["thickness"]) * 1e-6
TMP_RUN = v(INP["operation"]["tmp_flux_case"]) * BAR  # SI flux calculation, SDS10 / K101-infused
TMP_TABLE3 = v(INP["operation"]["tmp_table3_upper_bound"])  # bar; assumed upper bound for Table 3
ACC = v(INP["operation"]["controller_accuracy"]) * 1e-3  # bar
J_OIL = v(INP["operation"]["oil_flux_SDS10_K101"])
KAPPA = {k: v(n) for k, n in INP["lld"]["kappa_darcy"].items()}


def check_permeability() -> list[dict]:
    rows = []
    kappa = J_OIL * MU_OIL * L_MEM / TMP_RUN / DARCY
    ref = REP["emulsion_run_oil_flux"]["permeability_reported"]["value"]
    rel = TOL["checks"]["emulsion_run_permeability"]["rel"]
    rows.append({"quantity": "oil permeability, emulsion run SDS10 / K101-infused", "unit": "Darcy",
                 "reference": ref, "computed": float(f"{kappa:.4g}"),
                 "deviation": f"{(kappa - ref) / ref * 100:+.2f} %", "tolerance": f"rel {rel}",
                 "pass": abs(kappa - ref) / ref <= rel})
    t = TOL["checks"]["lld_active_fraction"]["abs"]
    for cyc in [1, 2, 3]:
        frac = KAPPA[f"K101_cycle{cyc}"] / KAPPA["dry"]
        ref = REP["lld_permeability"][f"K101_cycle{cyc}"]["active_fraction"]
        rows.append({"quantity": f"active pore fraction, LLD cycle {cyc}", "unit": "-", "reference": ref,
                     "computed": round(frac, 4), "deviation": round(frac - ref, 4),
                     "tolerance": f"abs {t}", "pass": band_pass(frac, ref, t)})
    return rows


# ------------------------------------------------------------------ window model
def window(s: str, lv: str, membrane: str, scale: float = 1.0, band: int = 0) -> tuple[float, float]:
    """Oil and water entry pressures (bar) for an emulsion on a membrane.

    membrane: 'dry' (hexadecane-filled in operation), 'K101' (under a hexadecane layer),
    'K101_direct' (aqueous phase on K101). band: 0 nominal, -1 low (r + hci, IFT low),
    +1 high (r - hci, IFT high). scale multiplies every curvature radius.
    """
    c = conc(s, LEVEL[lv])
    ash, bsh, rsh = (band, -band, -band)
    if membrane == "dry":
        p_oil = 0.0
        p_w = entry(gamma(s, "hexadecane", c, ash, bsh), radius(s, "hexadecane", rsh) * scale)
    elif membrane == "K101":
        # the oil-entry bound moves opposite to the water bound in a worst case: low band -> high p_oil
        p_oil = entry(G23, radius(s, "K101", band) * scale)
        p_w = entry(gamma(s, "hexadecane", c, ash, bsh) + G23, radius(s, "hexadecane", rsh) * scale)
    elif membrane == "K101_direct":
        p_oil = entry(G23, radius(s, "K101", band) * scale)
        p_w = entry(gamma(s, "K101", c, ash, bsh), radius(s, "K101", rsh) * scale)
    else:
        raise ValueError(membrane)
    return p_oil, p_w


CASES = [(s, lv, m) for m in ["dry", "K101"] for s in SURFS for lv in LEVELS]


def classify_table3() -> dict:
    tmp = TMP_TABLE3
    wf = REP["water_fraction_in_permeate"]
    rows, agree, undecided = [], 0, 0
    for s, lv, m in CASES:
        p_oil, p_w = window(s, lv, m)
        lo = window(s, lv, m, band=-1)[1]
        hi = window(s, lv, m, band=+1)[1]
        pred_water = tmp >= p_w
        obs = wf["K101_infused" if m == "K101" else "dry"][f"{s}{lv}"]
        ok = pred_water == (obs > 0)
        agree += ok
        inside = lo <= tmp <= hi
        near = (lo - ACC) <= tmp <= (hi + ACC)
        clipped = gamma(s, "hexadecane", conc(s, LEVEL[lv]), -1, +1) == 0.0
        undecided += inside
        rows.append({"emulsion": f"{s}{lv}", "membrane": "K101-infused" if m == "K101" else "dry",
                     "oil_entry_bar": round(p_oil, 4), "water_entry_bar": round(p_w, 4),
                     "water_entry_band_bar": [round(lo, 4), round(hi, 4)],
                     "predicted_water_at_0.1_bar": pred_water, "observed_water_fraction": obs,
                     "agrees": ok, "tmp_inside_water_entry_band": inside,
                     "tmp_within_one_controller_accuracy_of_band": near,
                     "band_low_edge_has_water_hexadecane_ift_clipped_to_zero": clipped})
    high = [r for r in rows if r["emulsion"].endswith("50")]
    order_entry = [r["emulsion"] + "/" + r["membrane"] for r in sorted(high, key=lambda r: r["water_entry_bar"])]
    order_water = [r["emulsion"] + "/" + r["membrane"] for r in sorted(high, key=lambda r: -r["observed_water_fraction"])]
    return {"tmp_bar": tmp, "controller_accuracy_bar": ACC, "rows": rows, "agree": agree, "of": len(rows),
            "cases_with_tmp_inside_band": undecided,
            "disagreements_with_tmp_inside_band": sum(1 for r in rows if not r["agrees"] and r["tmp_inside_water_entry_band"]),
            "50pct_cmc_order_by_rising_water_entry": order_entry,
            "50pct_cmc_order_by_falling_water_fraction": order_water,
            "50pct_cmc_orders_identical": order_entry == order_water}


def entry_with_measured_ift() -> dict:
    """Water entry pressures with the measured SI Table S2 IFTs in place of the Szyszkowski fit.

    Informational sensitivity, not in the pass rule: same radii and configuration rules as window().
    """
    meas = REP["ift_measured"]
    out = {}
    for s, lv, m in CASES:
        g_meas = meas[f"{s}{lv}_hexadecane"]["value"] * 1e-3
        g_add = G23 if m == "K101" else 0.0
        p_meas = entry(g_meas + g_add, radius(s, "hexadecane"))
        p_fit = window(s, lv, m)[1]
        out[f"{s}{lv}|{m}"] = {"water_entry_fit_bar": round(p_fit, 4),
                               "water_entry_measured_ift_bar": round(p_meas, 4),
                               "shift_bar": round(p_meas - p_fit, 4)}
    return out


def sweep() -> tuple[np.ndarray, dict]:
    sw = INP["sweep"]
    tmp = np.round(np.arange(v(sw["tmp_min"]), v(sw["tmp_max"]) + 1e-12, v(sw["tmp_step"])), 6)
    out = {}
    for s, lv, m in CASES:
        p_oil, p_w = window(s, lv, m)
        p_oil_hi = window(s, lv, m, band=-1)[0]
        p_w_lo = window(s, lv, m, band=-1)[1]
        state = np.where(tmp < p_oil, 0, np.where(tmp < p_w, 1, 2))
        out[f"{s}{lv}|{m}"] = {
            "oil_entry_bar": round(p_oil, 4), "water_entry_bar": round(p_w, 4),
            "selective_window_bar": [round(p_oil, 4), round(p_w, 4)],
            "selective_window_width_bar": round(p_w - p_oil, 4),
            "robust_window_bar": [round(p_oil_hi, 4), round(p_w_lo, 4)],
            "robust_window_empty": bool(p_w_lo <= p_oil_hi),
            "selective_tmp_points": int((state == 1).sum()),
            "state": state,
        }
    return tmp, out


# ------------------------------------------------------------------ area estimate
RHO_OIL = v(INP["fluids"]["hexadecane_density"])
RHO_C = v(INP["fluids"]["continuous_phase_density"])
W_OIL = v(INP["fluids"]["oil_mass_fraction"])
MU_C = v(INP["fluids"]["continuous_phase_viscosity"]) * 1e-3
G = v(INP["constants"]["g"])


def oil_volume_fraction() -> float:
    vo, vc = W_OIL / RHO_OIL, (1 - W_OIL) / RHO_C
    return vo / (vo + vc)


def area_estimate() -> dict:
    phi = oil_volume_fraction()
    q_feed = v(INP["area_estimate"]["feed_flow"]) / 3600.0
    q_oil = q_feed * phi * v(INP["area_estimate"]["oil_recovered_fraction"])
    area = q_oil / J_OIL
    d_cell = v(INP["membrane"]["cell_diameter"]) * 1e-3
    a_cell = math.pi * d_cell**2 / 4
    j_cap = KAPPA["K101_cycle1"] * DARCY * TMP_RUN / (MU_OIL * L_MEM)
    # SI p. S7 states 1 mPa s for the Table S3 permeabilities although hexadecane (3.2 mPa s) was
    # pushed through; if so, the permeabilities on a hexadecane basis are MU_OIL / MU_LLD higher
    mu_lld_alt = v(INP["lld"]["viscosity_basis_stated"]) * 1e-3
    f_alt = MU_OIL / mu_lld_alt
    u_max = REP["creaming_rate_SDS10"]["value_range"][1] * 1e-6
    return {
        "case": "K101-infused membrane, SDS10 emulsion, TMP 0.1 bar, dead-end with feed refreshing",
        "oil_volume_fraction": round(phi, 5),
        "feed_flow_m3_h": v(INP["area_estimate"]["feed_flow"]),
        "oil_flow_m3_s": float(f"{q_oil:.4g}"),
        "oil_flux_used_m3_m2_s": J_OIL,
        "oil_flux_used_L_m2_h": round(J_OIL * 3.6e6, 2),
        "membrane_area_m2_per_m3h_feed": round(area, 3),
        "cell_area_m2": float(f"{a_cell:.4g}"),
        "cell_oil_rate_mL_h": round(J_OIL * a_cell * 3.6e9, 2),
        "darcy_capacity_flux_lld_cycle1_m3_m2_s": float(f"{j_cap:.4g}"),
        "capacity_to_observed_ratio": round(j_cap / J_OIL, 1),
        "capacity_to_observed_ratio_if_table_s3_used_1_mPa_s": round(f_alt * j_cap / J_OIL, 1),
        "creaming_supply_flux_largest_droplets_m3_m2_s": float(f"{phi * u_max:.4g}"),
        "limits": [
            "batch dead-end figure: flux depends on refresh frequency and oil concentration (source)",
            "flux is supply-limited (Darcy capacity of the open pores is far higher), so the area does not scale with TMP",
            "no flux data for any other case; no area estimated for them",
            "does not carry over to a continuous crossflow module",
        ],
    }


def creaming_radii() -> dict:
    drho = RHO_C - RHO_OIL
    out = {}
    for u in REP["creaming_rate_SDS10"]["value_range"]:
        a = math.sqrt(9 * MU_C * u * 1e-6 / (2 * drho * G))
        out[f"{u} um/s"] = {"droplet_radius_um": round(a * 1e6, 3), "droplet_diameter_um": round(2 * a * 1e6, 3)}
    out["assumptions"] = f"Stokes law, delta rho = {drho:g} kg/m3, mu = {MU_C * 1e3:g} mPa s"
    return out


# ------------------------------------------------------------------ design extension
def extension() -> dict:
    ext = INP["extension"]
    s, lv = "SDS", "10"
    acc = ACC
    tmp_obs = TMP_TABLE3  # highest TMP at which the source ran emulsions
    margin = ext["control_margin"]["value"] * acc
    out = {"label": "HYPOTHETICAL design extension (not validated)",
           "design_case": "SDS10 emulsion, K101-infused membrane under a hexadecane layer",
           "changed_input": "every curvature radius scaled by pore_radius_scale",
           "controller_accuracy_bar": acc, "margin_each_side_bar": margin}
    for tag, sc in [("base", ext["pore_radius_scale"]["base"]), ("changed", ext["pore_radius_scale"]["changed"])]:
        p_oil, p_w = window(s, lv, "K101", scale=sc)
        p_oil_r, p_w_r = window(s, lv, "K101", scale=sc, band=-1)
        usable = (p_w_r - margin) - (p_oil_r + margin)
        k = KAPPA["K101_cycle1"] * DARCY * sc**2
        top = (p_w_r - margin) * BAR
        out[tag] = {
            "pore_radius_scale": sc,
            "mean_pore_radius_um": round(v(INP["membrane"]["pore_radius_mean"]) * sc, 3),
            "oil_entry_bar": round(p_oil, 4), "water_entry_bar": round(p_w, 4),
            "window_width_bar": round(p_w - p_oil, 4),
            "pressure_ratio_water_to_oil": round(p_w / p_oil, 4),
            "robust_window_bar": [round(p_oil_r, 4), round(p_w_r, 4)],
            "usable_tmp_range_bar": [round(p_oil_r + margin, 4), round(p_w_r - margin, 4)],
            "tolerable_tmp_variation_bar": round(usable, 4),
            "controller_steps_in_usable_range": int(usable // acc),
            "darcy_capacity_at_top_of_usable_range_m3_m2_s": float(f"{k * top / (MU_OIL * L_MEM):.4g}"),
            "usable_range_entirely_above_observed_tmp": bool(p_oil_r + margin > tmp_obs),
        }
    b, c = out["base"], out["changed"]
    out["consequence"] = {
        "window_width_ratio_changed_to_base": round(c["window_width_bar"] / b["window_width_bar"], 3),
        "tolerable_tmp_variation_ratio": round(c["tolerable_tmp_variation_bar"] / b["tolerable_tmp_variation_bar"], 3),
        "darcy_capacity_ratio": round(c["darcy_capacity_at_top_of_usable_range_m3_m2_s"]
                                      / b["darcy_capacity_at_top_of_usable_range_m3_m2_s"], 3),
    }
    out["flags"] = [
        "radii scaled in proportion: assumes the liquid lining scales with the pore; not measured",
        "Darcy capacity assumes kappa = phi r^2 / 24 at unchanged porosity and active fraction; a capacity bound, not a flux prediction (the measured flux is supply-limited)",
        "surfactant depletion by adsorption in the pore grows as r falls (SI eq S8); at 0.9 um its effect on the LEP is not known",
        "within the threshold model the water/oil entry ratio is independent of r; whether real leakage (not captured at 50 % cmc) depends on pore size is not known",
        f"operating-pressure extrapolation: the usable TMP ranges (base {out['base']['usable_tmp_range_bar'][0]:.3f}-{out['base']['usable_tmp_range_bar'][1]:.3f} bar, "
        f"changed {out['changed']['usable_tmp_range_bar'][0]:.3f}-{out['changed']['usable_tmp_range_bar'][1]:.3f} bar) lie entirely above the highest TMP at which the source ran emulsions "
        f"({tmp_obs:g} bar); selective behaviour, leakage and the supply-limited flux were never observed there",
    ]
    out["observed_tmp_max_bar"] = tmp_obs
    scales = np.round(np.linspace(0.25, 2.0, 141), 5)
    curve = {"scale": scales.tolist(), "oil_entry_bar": [], "water_entry_bar": [],
             "usable_low_bar": [], "usable_high_bar": []}
    for sc in scales:
        p_oil, p_w = window(s, lv, "K101", scale=float(sc))
        p_oil_r, p_w_r = window(s, lv, "K101", scale=float(sc), band=-1)
        curve["oil_entry_bar"].append(round(p_oil, 5))
        curve["water_entry_bar"].append(round(p_w, 5))
        curve["usable_low_bar"].append(round(p_oil_r + margin, 5))
        curve["usable_high_bar"].append(round(p_w_r - margin, 5))
    out["curve"] = curve
    above = [float(sc) for sc, lo in zip(scales, curve["usable_low_bar"]) if lo > tmp_obs]
    out["curve_usable_range_above_observed_tmp"] = {
        "scales_affected": f"{min(above):g} to {max(above):g}" if above else "none",
        "note": "the whole usable range lies above the observed TMP for these pore-radius scales "
                "(the oil bound rises as r falls)"}
    return out


# ------------------------------------------------------------------------- figures
def style():
    plt.rcParams.update({
        "svg.hashsalt": CASE_ID, "svg.fonttype": "none", "font.family": "DejaVu Sans",
        "font.size": 9, "axes.edgecolor": C_TEXT2, "axes.labelcolor": C_TEXT,
        "xtick.color": C_TEXT2, "ytick.color": C_TEXT2, "axes.grid": True,
        "grid.color": "#e6e5e1", "grid.linewidth": 0.6, "axes.spines.top": False,
        "axes.spines.right": False, "figure.facecolor": C_SURFACE, "axes.facecolor": C_SURFACE,
        "legend.frameon": False, "lines.linewidth": 2,
    })


def save(fig, name):
    fig.savefig(RESULTS / name, format="svg", metadata={"Date": None, "Creator": None})
    plt.close(fig)


def fig_entry_pressure(fig4b_rows):
    pts = REP["lep_figure4b_digitised"]["points"]
    fig, axes = plt.subplots(1, 2, figsize=(9.2, 3.9), sharey=True)
    frac = np.linspace(0, 1.0, 201)
    for ax, s in zip(axes, SURFS):
        series = [
            ("hexadecane-infused (dry membrane in use)", lambda f: entry(gamma(s, "hexadecane", conc(s, f)), radius(s, "hexadecane")), "hexadecane_infused"),
            ("K101-infused, aqueous phase on K101", lambda f: entry(gamma(s, "K101", conc(s, f)), radius(s, "K101")), "K101_infused"),
            ("K101-infused under hexadecane (gamma12 + gamma23)", lambda f: entry(gamma(s, "hexadecane", conc(s, f)) + G23, radius(s, "hexadecane")), None),
        ]
        for i, (lab, fn, key) in enumerate(series):
            y = np.array([fn(f) for f in frac])
            inside = frac <= FIT_RANGE + 1e-9
            ax.plot(frac[inside], y[inside], color=C_SERIES[i], label=lab)
            ax.plot(frac[~inside], y[~inside], color=C_SERIES[i], ls="--", lw=1.4)
            if key:
                xs, ys = [0.0], [pts[f"water_{key}"]["value"]]
                for lv in LEVELS:
                    xs.append(LEVEL[lv]); ys.append(pts[f"{s}{lv}_{key}"]["value"])
                ax.plot(xs, ys, ls="none", marker="o", ms=7, mfc=C_SURFACE, mec=C_SERIES[i], mew=1.6)
        comb = REP["lep_stated_in_text"]["combined_interface_K101_infused_under_hexadecane"][f"{s}50"]["value"]
        ax.plot([0.5], [comb], ls="none", marker="D", ms=7, mfc=C_SURFACE, mec=C_SERIES[2], mew=1.6)
        p_oil = entry(G23, radius(s, "K101"))
        p_oil_meas = REP["lep_stated_in_text"]["hexadecane_through_K101_infused"]["value"]
        ax.axhline(p_oil, color=C_TEXT2, lw=1, ls=":")
        ax.plot([0.0], [p_oil_meas], ls="none", marker="s", ms=6, mfc=C_SURFACE, mec=C_TEXT2, mew=1.4, clip_on=False)
        ax.text(0.02, p_oil + 0.012, f"oil entry, K101-infused: model {p_oil:.3f}, measured {p_oil_meas} bar (square)",
                ha="left", va="bottom", fontsize=7, color=C_TEXT2)
        ax.axhline(0.1, color=C_TEXT, lw=1, ls="-.")
        ax.text(0.99, 0.1 - 0.012, "TMP of the emulsion runs, 0.1 bar", ha="right", va="top", fontsize=7, color=C_TEXT)
        ax.axvspan(FIT_RANGE, 1.0, color="#f0efec", zorder=0)
        ax.text(0.75, 0.66, "extrapolated\n(beyond fitted range)", ha="center", va="top", fontsize=7.5, color=C_TEXT2)
        ax.set_title(f"{s} solutions", fontsize=10, color=C_TEXT, loc="left")
        ax.set_xlabel("surfactant concentration [fraction of cmc]")
        ax.set_xlim(0, 1.0); ax.set_ylim(0, 0.7)
    axes[0].set_ylabel("entry pressure of the aqueous phase [bar]")
    h, l = axes[0].get_legend_handles_labels()
    from matplotlib.lines import Line2D
    h += [Line2D([], [], ls="none", marker="o", mfc=C_SURFACE, mec=C_TEXT2, mew=1.6),
          Line2D([], [], ls="none", marker="D", mfc=C_SURFACE, mec=C_TEXT2, mew=1.6)]
    l += ["measured LEP (digitised from the source's Fig. 4b)", "authors' stated combined estimate"]
    fig.legend(h, l, loc="upper center", ncol=2, fontsize=7.5, bbox_to_anchor=(0.5, 1.0))
    fig.text(0.01, 0.005, "Lines: Young-Laplace (theta = 180 deg) with the source's Szyszkowski and radius fits; our calculation. "
             "Source: Bazyar et al., Langmuir 2019, doi:10.1021/acs.langmuir.9b01055.", fontsize=6.5, color=C_TEXT2)
    fig.tight_layout(rect=(0, 0.03, 1, 0.86))
    save(fig, "entry_pressure_vs_concentration.svg")


def fig_window(tmp, sw, cls):
    fig, ax = plt.subplots(figsize=(9.2, 4.2))
    labels = []
    obs = {(r["emulsion"], r["membrane"]): r["observed_water_fraction"] for r in cls["rows"]}
    for i, (s, lv, m) in enumerate(CASES):
        d = sw[f"{s}{lv}|{m}"]
        y = len(CASES) - 1 - i
        p_oil, p_w = d["selective_window_bar"]
        tmax = float(tmp[-1])
        ax.barh(y, p_oil, left=0, color=C_NEUTRAL, height=0.62, edgecolor=C_SURFACE, lw=2)
        ax.barh(y, p_w - p_oil, left=p_oil, color=C_GOOD, height=0.62, edgecolor=C_SURFACE, lw=2)
        ax.barh(y, tmax - p_w, left=p_w, color=C_CRIT, height=0.62, edgecolor=C_SURFACE, lw=2)
        lo, hi = d["robust_window_bar"]
        ax.plot([lo, lo], [y - 0.31, y + 0.31], color=C_TEXT, lw=1)
        ax.plot([hi, hi], [y - 0.31, y + 0.31], color=C_TEXT, lw=1)
        mem = "K101-infused" if m == "K101" else "dry"
        labels.append(f"{s} {lv} % cmc, {mem}")
        ax.text(tmax + 0.01, y, f"water {obs[(f'{s}{lv}', mem)]:.2f}", va="center", fontsize=7.5, color=C_TEXT)
    ax.set_yticks(range(len(CASES))[::-1], labels)
    ax.axvline(0.1, color=C_TEXT, lw=1.2, ls="-.")
    ax.text(0.102, len(CASES) - 0.45, "TMP of the runs (at most 0.1 bar)", fontsize=7.5, color=C_TEXT, va="bottom")
    ax.set_xlim(0, float(tmp[-1])); ax.set_ylim(-0.6, len(CASES) - 0.2)
    ax.set_xlabel("transmembrane pressure [bar]")
    ax.grid(axis="y", visible=False)
    from matplotlib.patches import Patch
    ax.legend([Patch(color=C_NEUTRAL), Patch(color=C_GOOD), Patch(color=C_CRIT)],
              ["no permeation", "selective: oil only", "breakthrough: water also permeates"],
              loc="upper center", bbox_to_anchor=(0.45, 1.16), ncol=3, fontsize=8)
    fig.text(0.01, 0.01, "Bands: threshold model from the source's fits (our calculation). Thin ticks: window narrowed by the fits' half confidence intervals.\n"
             "Right: water fraction in the permeate observed at TMP <= 0.1 bar (Bazyar et al., Langmuir 2019, Table 3).", fontsize=6.5, color=C_TEXT2)
    fig.subplots_adjust(left=0.25, right=0.89, top=0.86, bottom=0.2)
    save(fig, "operating_window.svg")


def fig_extension(ext):
    cv = ext["curve"]
    r0 = v(INP["membrane"]["pore_radius_mean"])
    x = np.array(cv["scale"]) * r0
    fig, ax = plt.subplots(figsize=(6.4, 4.0))
    ax.fill_between(x, cv["oil_entry_bar"], cv["water_entry_bar"], color=C_GOOD, alpha=0.18, lw=0)
    ax.plot(x, cv["water_entry_bar"], color=C_SERIES[0], label="water entry (gamma12 + gamma23)")
    ax.plot(x, cv["oil_entry_bar"], color=C_SERIES[1], label="oil entry (gamma23)")
    ax.plot(x, cv["usable_high_bar"], color=C_SERIES[0], lw=1, ls="--", label="usable bounds (CI and control margin)")
    ax.plot(x, cv["usable_low_bar"], color=C_SERIES[1], lw=1, ls="--")
    for tag in ["base", "changed"]:
        d = ext[tag]
        xr = d["mean_pore_radius_um"]
        lo, hi = d["usable_tmp_range_bar"]
        ax.plot([xr, xr], [lo, hi], color=C_TEXT, lw=2.5)
        ax.text(xr + 0.04, hi, f"{'base' if tag == 'base' else 'changed'}: r = {xr:.2f} um\nusable {lo:.2f}-{hi:.2f} bar",
                fontsize=7.5, color=C_TEXT, va="bottom")
    tmp_obs = ext["observed_tmp_max_bar"]
    ax.axhspan(tmp_obs, 2.0, color="#f0efec", zorder=0, lw=0)
    ax.axhline(tmp_obs, color=C_TEXT, lw=1, ls="-.")
    ax.text(x[-1] - 0.03, 0.9, f"grey, above the dash-dot line: TMP higher than any at which\nthe source ran emulsions ({tmp_obs:g} bar); never observed",
            ha="right", va="bottom", fontsize=7, color=C_TEXT)
    ax.set_xlabel("mean pore radius [um] (all curvature radii scaled together)")
    ax.set_ylabel("transmembrane pressure [bar]")
    ax.set_ylim(0, 2.0); ax.set_xlim(x[0], x[-1])
    ax.set_title("HYPOTHETICAL: SDS 10 % cmc on a K101-infused membrane", fontsize=9.5, loc="left", color=C_TEXT)
    ax.legend(fontsize=7.5, loc="upper right")
    fig.text(0.01, 0.01, "Design extension, not validated. Green: selective window from the threshold model. "
             "Grey: above the observed TMP range (extrapolation).", fontsize=6.5, color=C_TEXT2)
    fig.tight_layout(rect=(0, 0.03, 1, 1))
    save(fig, "extension_pore_radius.svg")


# --------------------------------------------------------------------------- main
def main() -> int:
    RESULTS.mkdir(exist_ok=True)
    style()
    src = source_check()
    groups = {
        "ift_szyszkowski": check_ift(),
        "lep_figure4b": check_fig4b(),
        "lep_stated": check_stated(),
        "permeability": check_permeability(),
    }
    all_rows = [r for g in groups.values() for r in g]
    n_pass = sum(r["pass"] for r in all_rows)
    verdict = "PASS" if n_pass == len(all_rows) else "FAIL"
    cls = classify_table3()
    tmp, sw = sweep()
    area = area_estimate()
    ext = extension()
    variant = {f"{s}50": round(lep_water_combined(s, "50", r_oil="K101"), 4) for s in SURFS}
    phi_dry = 24 * KAPPA["dry"] * DARCY / (v(INP["membrane"]["pore_radius_mean"]) * 1e-6) ** 2
    f_alt = MU_OIL / (v(INP["lld"]["viscosity_basis_stated"]) * 1e-3)
    direct = {f"{s}{lv}": round(window(s, lv, "K101_direct")[1], 4) for s in SURFS for lv in LEVELS}

    with open(RESULTS / "sweep.csv", "w", encoding="utf-8") as fh:
        keys = list(sw)
        fh.write("# state: 0 no permeation, 1 selective oil permeation, 2 water breakthrough (threshold model)\n")
        fh.write("tmp_bar," + ",".join(keys) + "\n")
        for i, t in enumerate(tmp):
            fh.write(f"{t:.3f}," + ",".join(str(int(sw[k]["state"][i])) for k in keys) + "\n")

    fig_entry_pressure(groups["lep_figure4b"])
    fig_window(tmp, sw, cls)
    fig_extension(ext)

    result = {
        "case": CASE_ID,
        "issue": "#340 (tracker #333)",
        "reference": SRC["reference"]["doi"],
        "tolerances_file": "tolerances.yaml",
        "environment": {"python": platform.python_version(), "numpy": np.__version__,
                        "matplotlib": matplotlib.__version__, "pyyaml": yaml.__version__},
        "source_check": src,
        "reproduction": {"verdict": verdict, "checks_passed": n_pass, "checks_total": len(all_rows),
                         "pass_rule": TOL["pass_rule"].strip(), "checks": groups},
        "informational": {
            "table3_classification_at_0.1_bar": cls,
            "combined_interface_with_K101_radius_bar": variant,
            "water_entry_aqueous_on_K101_bar": direct,
            "creaming_implied_droplet_size_SDS10": creaming_radii(),
            "dry_membrane_porosity_from_kappa_phi_r2_over_24": round(phi_dry, 4),
            "dry_membrane_porosity_if_table_s3_used_1_mPa_s": round(phi_dry * f_alt, 4),
            "water_entry_with_measured_table_s2_ift": entry_with_measured_ift(),
        },
        "pressure_sweep": {k: {kk: vv for kk, vv in d.items() if kk != "state"} for k, d in sw.items()},
        "area_estimate": area,
        "design_extension": {k: vv for k, vv in ext.items() if k != "curve"},
        "figures": ["entry_pressure_vs_concentration.svg", "operating_window.svg", "extension_pore_radius.svg"],
    }
    with open(RESULTS / "comparison.json", "w", encoding="utf-8") as fh:
        json.dump(result, fh, indent=2, ensure_ascii=False)
        fh.write("\n")
    print(f"{CASE_ID}: reproduction {verdict} ({n_pass}/{len(all_rows)} checks); "
          f"Table 3 classification {cls['agree']}/{cls['of']}; source check: {src['status']}")
    for r in all_rows:
        print(f"  {'pass' if r['pass'] else 'FAIL'}  {r['quantity']}: ref {r['reference']} ours {r['computed']} dev {r['deviation']}")
    print(f"results written to {RESULTS}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
