# /// script
# requires-python = "==3.12.*"
# dependencies = [
#   "numpy==2.2.6",
#   "openpyxl==3.1.5",
#   "pyyaml==6.0.2",
#   "matplotlib==3.10.3",
# ]
# ///
"""Reproduce the GDE pressure-window benchmark (process-library#332, ADR 0030).

Downloads the pinned supporting information of Baumgartner et al. (2022) from Europe PMC,
verifies each file's sha256, rebuilds the flow-by pressure window of every gas diffusion
electrode from the tabulated breakthrough pressures (R1, R2), reproduces the paper's height
conversions (R3), classifies its height claims (K1) and the electrolysis operating pressures
against the open-circuit window (K2), and reports h_max with an uncertainty interval and the
frictional pressure drop of the catholyte channel. The rules are in tolerances.yaml; this script
only evaluates them. Run:
uv run --isolated benchmarks/reproductions/baumgartner-gde-pressure-window/reproduce.py
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import math
import platform
import re
import subprocess
import sys
import urllib.request
import zipfile
from pathlib import Path

import numpy as np
import yaml

HERE = Path(__file__).resolve().parent
G = 9.80665  # m/s2
MBAR = 100.0  # Pa

# Spelling in sheet deltaP (column A) and in the FE block titles -> the name used here.
MATERIALS = ["TGP-H-060", "TGP-H-090", "TGP-H-120", "SGL22BB", "SGL39BC", "LT1400W", "H23C6"]
FE_TITLE = {"Toray060": "TGP-H-060", "Toray090": "TGP-H-090", "Toray120": "TGP-H-120",
            "SGL 22BB": "SGL22BB", "SGL 39BC": "SGL39BC", "LT1400W": "LT1400W", "H23C6": "H23C6"}
CRACK_FREE = {"H23C6"}

# Plot operating point (comparison.md): SGL 39BC, a 1 m electrode, gas at the lab check-valve
# pressure, liquid set so that the top of the electrode sits exactly at gas breakthrough.
PLOT = {"material": "SGL39BC", "height_m": 1.0, "p_gas_mbar": 345.0}

# Frictional pressure-drop cases (tolerances.yaml reported_not_checked.friction).
MU = 1.1e-3  # Pa s, ASSUMED, 1 M KHCO3 at 20 degC
LAB = {"q_ml_min": 100.0, "width_m": 0.030, "gap_m": 0.0035}
SCALE_UP = {"gaps_m": [0.002, 0.005], "velocities_m_s": [0.01, 0.03, 0.1], "width_m": 1.0}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def fetch(source: dict, cache: Path) -> dict[str, Path]:
    """Download the Europe PMC zip once, extract its members and verify each one's sha256."""
    si = source["reference"]["supporting_information"]
    folder = cache / "x"
    wanted = {f["name"]: f for f in si["files"]}
    if not all((folder / n).exists() for n in wanted):
        cache.mkdir(parents=True, exist_ok=True)
        target = cache / "supplementaryFiles.zip"
        print("download supporting information (Europe PMC)", file=sys.stderr)
        urllib.request.urlretrieve(si["url"], target)
        with zipfile.ZipFile(target) as z:
            for name in wanted:  # extract only the pinned members, by exact name
                folder.mkdir(parents=True, exist_ok=True)
                (folder / name).write_bytes(z.read(name))
    out = {}
    for name, f in wanted.items():
        p = folder / name
        if sha256(p) != f["sha256"]:
            sys.exit(f"sha256 mismatch for {p}; delete the cache folder and rerun, or the record changed")
        out[name] = p
    return out


def numeric(v) -> bool:
    return isinstance(v, (int, float)) and not isinstance(v, bool) and math.isfinite(v)


def col(letter: str) -> int:
    from openpyxl.utils import column_index_from_string

    return column_index_from_string(letter) - 1


# --- sheets ---------------------------------------------------------------------------------


def read_deltap(wb, layout: dict) -> dict:
    ws = wb[layout["sheet"]]
    rows = {}
    for r in ws.iter_rows(min_row=3, max_row=9, values_only=True):
        name = r[0]
        if name not in MATERIALS:
            sys.exit(f"unexpected material {name!r} in sheet deltaP")
        rows[name] = {side: {k: r[col(c)] for k, c in cols.items()} for side, cols in layout["columns"].items()}
    return rows


def read_fe(wb) -> dict:
    """Per material: the experiment-overview rows (averaged values) of its FE block."""
    ws = wb["FE"]
    cells = [list(r) for r in ws.iter_rows(values_only=True)]
    blocks, current, header = {}, None, None
    for r in cells:
        a = r[0] if r else None
        if isinstance(a, str):
            m = re.fullmatch(r"\d{8} (.+?) Sample \d+", a.strip())
            if m:
                current, header = FE_TITLE[m.group(1)], None
                blocks[current] = {"title": a.strip(), "rows": []}
                continue
            if a.startswith("Experiment number"):
                header = r
                continue
            if a.startswith("GC injection overview"):
                header = None
                continue
        if current and header is not None and numeric(a):
            blocks[current]["rows"].append({
                "experiment": a,
                "j": r[col("AC")],
                "dp_reactor_gas_minus_liquid": r[col("I")],
                "dp_reactor_sd": r[col("J")],
                "gas_into_liquid_outlet_ml_min": r[col("AA")],
                "liquid_into_gas_outlet_ml_min": r[col("AB")],
                "fe_co": r[col("AI")],
                "fe_co_err": r[col("AJ")],
                "note": r[col("AG")] if isinstance(r[col("AG")], str) else None,
            })
    return blocks


# --- physics --------------------------------------------------------------------------------


def h_max_cm(dp_mbar: float, rho: float) -> float:
    return dp_mbar * MBAR / (rho * G) * 100.0


def fre_rectangular(aspect: float) -> float:
    """Darcy fRe of fully developed laminar flow in a rectangular duct (Shah and London 1978)."""
    a = min(aspect, 1.0 / aspect)
    return 96.0 * (1 - 1.3553 * a + 1.9467 * a**2 - 1.7012 * a**3 + 0.9564 * a**4 - 0.2537 * a**5)


def friction_case(u: float, gap: float, width: float, rho: float) -> dict:
    dh = 2 * gap * width / (gap + width)
    re_ = rho * u * dh / MU
    grad = fre_rectangular(gap / width) * MU * u / (2 * dh**2)  # Pa/m
    return {"u_m_s": u, "gap_m": gap, "width_m": width, "Dh_m": dh, "Re": re_, "laminar": re_ < 2000,
            "friction_Pa_per_m": grad, "hydrostatic_Pa_per_m": rho * G, "r": grad / (rho * G)}


# --- main -----------------------------------------------------------------------------------


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--cache", type=Path, default=Path.home() / ".cache/cheme-as-code/europepmc/PMC9006256")
    ap.add_argument("--no-record", action="store_true", help="do not write a run record to reruns/")
    args = ap.parse_args()

    import openpyxl

    # The rules of tolerances.yaml are implemented below as written there (prose, not parsed);
    # only the constants are read from it.
    source = yaml.safe_load((HERE / "source.yaml").read_text())
    tol = yaml.safe_load((HERE / "tolerances.yaml").read_text())
    rho_w = float(tol["constants"]["rho_water"])
    rho_c = float(tol["constants"]["rho_catholyte"]["value"])
    rho_lo, rho_hi = map(float, tol["constants"]["rho_catholyte"]["range"])
    if abs(float(tol["constants"]["g"]) - G) > 1e-9:
        sys.exit("g in tolerances.yaml differs from the script")
    files = fetch(source, args.cache)
    wb = openpyxl.load_workbook(files["sc2c00195_si_002.xlsx"], data_only=True)
    pub = source["published"]
    table = read_deltap(wb, source["file_to_table"]["breakthrough_pressures"])
    fe = read_fe(wb)
    results: dict = {}
    status = lambda ok: "pass" if ok else "fail"  # noqa: E731

    # R1 ---------------------------------------------------------------------------------------
    r1, r1_gdl = [], []
    for m in MATERIALS:
        g = table[m]["gde"]
        ours = float(g["dp_L"]) - float(g["dp_G"])
        row = {"material": m, "dp_G": g["dp_G"], "dp_L": g["dp_L"], "window_ours": ours,
               "vs_sheet": {"published": g["window"], "deviation": ours - float(g["window"]),
                            "status": status(abs(ours - float(g["window"])) <= 0.5)}}
        text = pub["windows_stated_in_text"].get(m)
        if text:
            dev = ours - float(text["value"])
            row["vs_text"] = {"published": text["value"], "deviation": dev, "status": status(abs(dev) <= 0.5)}
        r1.append(row)
        u = table[m]["gdl"]
        s3 = source["file_to_table"]["gdl_liquid_breakthrough_si"]["values"][m]
        r1_gdl.append({"material": m, "dp_L_sheet": u["dp_L"], "dp_L_table_s3": s3,
                       "window_sheet": u["window"], "dp_G_assumed": u["dp_G"],
                       "status": status(abs(float(u["dp_L"]) - s3) <= 0.5
                                        and abs(float(u["window"]) - (float(u["dp_L"]) - float(u["dp_G"]))) <= 0.5)})
    results["R1"] = {"gde": r1, "gdl_consistency": r1_gdl}

    # R2 ---------------------------------------------------------------------------------------
    r2 = []
    for m in MATERIALS:
        g = table[m]["gde"]
        s = math.hypot(float(g["s_G"]), float(g["s_L"]))
        row = {"material": m, "s_G": g["s_G"], "s_L": g["s_L"], "s_ours": s,
               "vs_sheet": {"published": g["s_window"], "status": status(abs(s - float(g["s_window"])) <= 0.5)}}
        if m not in CRACK_FREE:
            row["vs_text"] = {"published": pub["window_sd"]["value"],
                              "status": status(abs(s - float(pub["window_sd"]["value"])) <= 0.5)}
        r2.append(row)
    results["R2"] = r2

    # R3 ---------------------------------------------------------------------------------------
    r3 = []
    for h in pub["heights"]:
        ours = h_max_cm(float(h["from_window"]), rho_w)
        r3.append({"id": h["id"], "window_mbar": h["from_window"], "published_cm": h["to_height"],
                   "ours_water_cm": ours, "deviation_cm": ours - h["to_height"],
                   "status": status(abs(ours - h["to_height"]) <= 1.0),
                   "ours_catholyte_cm": h_max_cm(float(h["from_window"]), rho_c)})
    results["R3"] = r3

    # h_max per GDE (reported) -----------------------------------------------------------------
    window = {r["material"]: r["window_ours"] for r in r1}
    sd = {r["material"]: r["s_ours"] for r in r2}
    hmax = {}
    for m in MATERIALS:
        w, s = window[m], sd[m]
        hmax[m] = {"window_mbar": w, "s_mbar": s,
                   "water_cm": h_max_cm(w, rho_w), "catholyte_cm": h_max_cm(w, rho_c),
                   "interval_2s_cm": [max(h_max_cm(w - 2 * s, rho_hi), 0.0), h_max_cm(w + 2 * s, rho_lo)],
                   "water_minus_2s_cm": max(h_max_cm(w - 2 * s, rho_w), 0.0)}
    results["h_max"] = hmax

    # K1 ---------------------------------------------------------------------------------------
    cracked = [m for m in MATERIALS if m not in CRACK_FREE]
    n_in = sum(39.5 <= window[m] <= 80.5 for m in cracked)
    fe200 = {}
    for m, b in fe.items():
        rows = [r for r in b["rows"] if numeric(r["j"]) and 180 <= abs(r["j"]) <= 220 and numeric(r["fe_co"])]
        fe200[m] = {"fe_co": float(np.mean([r["fe_co"] for r in rows])) if rows else None, "rows": len(rows),
                    "text": pub["fe_co_stated_in_text"].get(m)}
    c1_set = [m for m in cracked if fe200.get(m, {}).get("fe_co") is not None and fe200[m]["fe_co"] > 50]
    c1_missing = [m for m in cracked if fe200.get(m, {}).get("fe_co") is None]
    c1_over = [m for m in c1_set if hmax[m]["water_cm"] > 51.5]
    if c1_missing:
        c1 = "unresolved"
    else:
        c1 = "contradicted" if c1_over else "supported"
    h23 = hmax["H23C6"]
    results["K1"] = {
        "range": {"in_40_80": n_in, "of": len(cracked), "classification": "supported" if n_in > 3 else "contradicted",
                  "windows": {m: window[m] for m in cracked}},
        "C1": {"set_fe_above_50": c1_set, "fe_co_200": fe200, "above_51_5_cm": c1_over,
               "h_water_cm": {m: hmax[m]["water_cm"] for m in c1_set},
               "h_catholyte_cm": {m: hmax[m]["catholyte_cm"] for m in c1_set},
               "missing": c1_missing, "classification": c1},
        "C2": {"h_water_cm": h23["water_cm"], "h_water_minus_2s_cm": h23["water_minus_2s_cm"],
               "classification": "supported" if h23["water_cm"] > 100 else "contradicted"},
        "C3": {"h_water_cm": h23["water_cm"], "h_water_minus_2s_cm": h23["water_minus_2s_cm"],
               "classification": "supported" if h23["water_cm"] > 200 else "contradicted"},
    }

    # K2 ---------------------------------------------------------------------------------------
    k2 = []
    for m in MATERIALS:
        g = table[m]["gde"]
        lo, hi = float(g["dp_G"]), float(g["dp_L"])
        for r in fe.get(m, {"rows": []})["rows"]:
            if not (numeric(r["j"]) and 180 <= abs(r["j"]) <= 220 and numeric(r["dp_reactor_gas_minus_liquid"])):
                continue
            dp = -float(r["dp_reactor_gas_minus_liquid"])
            out = max(lo - dp, dp - hi, 0.0)
            cls = "inside" if out == 0 else ("edge" if out <= 10 else "outside")
            k2.append({"material": m, "experiment": r["experiment"], "j": r["j"], "dp_op": dp,
                       "dp_op_sd": r["dp_reactor_sd"], "window": [lo, hi], "outside_by": out,
                       "classification": cls, "gas_into_liquid_ml_min": r["gas_into_liquid_outlet_ml_min"],
                       "liquid_into_gas_ml_min": r["liquid_into_gas_outlet_ml_min"], "fe_co": r["fe_co"],
                       "note": r["note"]})
    results["K2"] = k2
    # Informational, not a frozen check (added after the first run): the overview rows outside
    # the 200 mA/cm2 scope of K2, classified the same way. H23C6 has only a 100 mA/cm2 row.
    other = []
    for m in MATERIALS:
        g = table[m]["gde"]
        lo, hi = float(g["dp_G"]), float(g["dp_L"])
        for r in fe.get(m, {"rows": []})["rows"]:
            if numeric(r["j"]) and not 180 <= abs(r["j"]) <= 220 and numeric(r["dp_reactor_gas_minus_liquid"]):
                dp = -float(r["dp_reactor_gas_minus_liquid"])
                other.append({"material": m, "j": r["j"], "dp_op": dp, "window": [lo, hi],
                              "outside_by": max(lo - dp, dp - hi, 0.0), "fe_co": r["fe_co"],
                              "gas_into_liquid_ml_min": r["gas_into_liquid_outlet_ml_min"],
                              "liquid_into_gas_ml_min": r["liquid_into_gas_outlet_ml_min"]})
    results["informational"] = {"K2_other_current_densities": other}

    # friction (reported) ----------------------------------------------------------------------
    u_lab = LAB["q_ml_min"] * 1e-6 / 60 / (LAB["width_m"] * LAB["gap_m"])
    results["friction"] = {
        "assumed": {"mu_Pa_s": MU, "rho": rho_c, "lab": LAB, "scale_up": SCALE_UP},
        "lab": friction_case(u_lab, LAB["gap_m"], LAB["width_m"], rho_c),
        "scale_up_1m": [friction_case(u, b, SCALE_UP["width_m"], rho_c)
                        for b in SCALE_UP["gaps_m"] for u in SCALE_UP["velocities_m_s"]],
        "lab_hydrostatic_over_exposed_electrode_mbar": rho_c * G * 0.022 / MBAR,
    }

    plots(results, table, rho_c, HERE / "figures")
    report(results)
    if not args.no_record:
        record(results, source, files)
    failed = [k for k in ("R1", "R2", "R3") if any_fail(results[k])]
    return 1 if failed else 0


def any_fail(obj) -> bool:
    if isinstance(obj, dict):
        return obj.get("status") == "fail" or any(any_fail(v) for v in obj.values())
    if isinstance(obj, list):
        return any(any_fail(v) for v in obj)
    return False


def report(results: dict) -> None:
    print("R1  window dp* = dp_L* - dp_G* per coated GDE (mbar)")
    print("    material    dp_G*   dp_L*   ours    sheet  st    text  st")
    for r in results["R1"]["gde"]:
        t = r.get("vs_text")
        ts = f"{t['published']:>5}  {t['status']}" if t else "    -"
        print(f"    {r['material']:<10} {r['dp_G']:>6} {r['dp_L']:>7} {r['window_ours']:>6g} "
              f"{r['vs_sheet']['published']:>6} {r['vs_sheet']['status']}  {ts}")
    g = results["R1"]["gdl_consistency"]
    print(f"    uncoated GDL: sheet vs SI Table S3 consistent for {sum(r['status'] == 'pass' for r in g)} of {len(g)}")
    print("R2  window sd by Gaussian propagation (mbar)")
    for r in results["R2"]:
        t = r.get("vs_text")
        print(f"    {r['material']:<10} ours {r['s_ours']:.2f}  sheet {r['vs_sheet']['published']:.2f} {r['vs_sheet']['status']}"
              + (f"  text {t['published']} {t['status']}" if t else ""))
    print("R3  height conversions h = dp* / (rho_water g)")
    for r in results["R3"]:
        print(f"    {r['id']}: {r['window_mbar']} mbar -> ours {r['ours_water_cm']:.2f} cm, published {r['published_cm']} cm, "
              f"dev {r['deviation_cm']:+.2f}  {r['status']}   (1 M KHCO3: {r['ours_catholyte_cm']:.2f} cm)")
    print("h_max per GDE (cm): water, 1 M KHCO3, interval over dp* +/- 2 s and rho range")
    for m, h in results["h_max"].items():
        print(f"    {m:<10} {h['window_mbar']:>6g} mbar  {h['water_cm']:6.1f}  {h['catholyte_cm']:6.1f}  "
              f"[{h['interval_2s_cm'][0]:.1f}, {h['interval_2s_cm'][1]:.1f}]")
    k1 = results["K1"]
    print(f"K1  range 40-80 mbar: {k1['range']['in_40_80']} of {k1['range']['of']}: {k1['range']['classification']}")
    c1 = k1["C1"]
    print(f"    C1 (<51 cm for FE_CO > 50 %): set {c1['set_fe_above_50']}, above 51.5 cm {c1['above_51_5_cm']}: {c1['classification']}")
    for m, f in c1["fe_co_200"].items():
        fv = f"{f['fe_co']:.1f}" if f["fe_co"] is not None else "-"
        print(f"       {m:<10} FE_CO(sheet) {fv:>5} %  text {f['text']}")
    print(f"    C2 (H23C6 > 1 m): {k1['C2']['h_water_cm']:.0f} cm (at -2 s: {k1['C2']['h_water_minus_2s_cm']:.0f} cm): {k1['C2']['classification']}")
    print(f"    C3 (H23C6 > 200 cm): {k1['C3']['classification']}")
    print("K2  operating dp (liquid - gas) of the 200 mA/cm2 runs vs the open-circuit window")
    for r in results["K2"]:
        print(f"    {r['material']:<10} exp {r['experiment']:<4g} dp_op {r['dp_op']:7.1f} (sd {r['dp_op_sd']}) "
              f"window [{r['window'][0]:g}, {r['window'][1]:g}]  {r['classification']}"
              f"  breakthrough L->G {r['liquid_into_gas_ml_min']}, G->L {r['gas_into_liquid_ml_min']}")
    for r in results["informational"]["K2_other_current_densities"]:
        print(f"    (informational) {r['material']:<10} j {r['j']:.0f} mA/cm2: dp_op {r['dp_op']:.1f}, "
              f"window [{r['window'][0]:g}, {r['window'][1]:g}], outside by {r['outside_by']:.1f}, "
              f"breakthrough L->G {r['liquid_into_gas_ml_min']}, G->L {r['gas_into_liquid_ml_min']}")
    f = results["friction"]
    lab = f["lab"]
    print(f"friction  lab: u {lab['u_m_s'] * 1000:.1f} mm/s, Re {lab['Re']:.0f}, {lab['friction_Pa_per_m']:.1f} Pa/m vs rho g "
          f"{lab['hydrostatic_Pa_per_m']:.0f} Pa/m (r = {lab['r']:.1e})")
    for c in f["scale_up_1m"]:
        print(f"          1 m: gap {c['gap_m'] * 1000:.0f} mm, u {c['u_m_s']:.2f} m/s, Re {c['Re']:.0f}, "
              f"{c['friction_Pa_per_m']:.1f} Pa/m, r = {c['r']:.2e}")


def record(results: dict, source: dict, files: dict) -> None:
    import matplotlib
    import openpyxl

    def git(*a):
        return subprocess.run(["git", *a], cwd=HERE, capture_output=True, text=True).stdout.strip()

    rec = {
        "schema": "cheme-as-code/reproduction-run/v1",
        "reproduction": "baumgartner-gde-pressure-window",
        "run_at": dt.datetime.now(dt.UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "commit": git("rev-parse", "HEAD"),
        "dirty": bool(git("status", "--porcelain", "--", ".")),
        "tolerances_frozen_in": git("log", "--format=%H", "--diff-filter=A", "--", "tolerances.yaml"),
        "inputs": {f["name"]: f["sha256"] for f in source["reference"]["supporting_information"]["files"]},
        "versions": {"python": platform.python_version(), "numpy": np.__version__, "openpyxl": openpyxl.__version__,
                     "matplotlib": matplotlib.__version__, "platform": platform.platform()},
        "results": results,
    }
    out = HERE / "reruns" / f"{rec['run_at'][:10]}-run.json"
    out.parent.mkdir(exist_ok=True)
    k = 1
    while out.exists():  # never overwrite an earlier record
        k += 1
        out = out.with_name(f"{rec['run_at'][:10]}-run-{k}.json")
    out.write_text(json.dumps(rec, indent=1, default=float) + "\n")
    print(f"run record: {out.relative_to(HERE)}")


def plots(results: dict, table: dict, rho: float, outdir: Path) -> None:
    import matplotlib

    matplotlib.use("Agg")
    matplotlib.rcParams["svg.hashsalt"] = "baumgartner-gde-pressure-window"
    import matplotlib.pyplot as plt

    outdir.mkdir(exist_ok=True)
    meta = {"Date": None}

    # Pressure vs elevation for one GDE at the stated operating point.
    m = PLOT["material"]
    g = table[m]["gde"]
    dp_g, dp_l = float(g["dp_G"]), float(g["dp_L"])
    big_h = PLOT["height_m"] * 100.0  # cm
    p_gas = PLOT["p_gas_mbar"]
    z = np.linspace(0.0, big_h, 201)
    slope = rho * G / MBAR / 100.0  # mbar per cm
    p_liq = p_gas + dp_g + slope * (big_h - z)  # top of the electrode exactly at gas breakthrough
    h = results["h_max"][m]
    z_flood = big_h - h["catholyte_cm"]
    lo_cm, hi_cm = h["interval_2s_cm"]

    fig, ax = plt.subplots(figsize=(5.6, 5.6))
    ax.axhspan(max(z_flood, 0), big_h, color="C2", alpha=0.18, lw=0, label=f"flow-by band, h_max = {h['catholyte_cm']:.0f} cm")
    ax.axhspan(0, max(z_flood, 0), color="C3", alpha=0.08, lw=0, label="liquid breakthrough (flooding)")
    first = True
    for zz in (big_h - lo_cm, big_h - hi_cm):
        if 0 < zz < big_h:
            ax.axhline(zz, color="C2", lw=0.8, ls=":", label="end of the band, interval bounds" if first else None)
            first = False
    ax.plot([p_gas, p_gas], [0, big_h], color="C0", lw=1.8, label="gas pressure (uniform)")
    ax.plot(p_liq, z, color="C1", lw=1.8, label=f"liquid pressure, 1 M KHCO$_3$ ({rho:.0f} kg m$^{{-3}}$)")
    ax.plot([p_gas + dp_g] * 2, [0, big_h], color="0.35", lw=1, ls="--", label=f"gas breakthrough, p$_G$ + {dp_g:g} mbar")
    ax.plot([p_gas + dp_l] * 2, [0, big_h], color="0.1", lw=1, ls="-.", label=f"liquid breakthrough, p$_G$ + {dp_l:g} mbar")
    ax.annotate("", xy=(p_gas + dp_l + 8, big_h), xytext=(p_gas + dp_l + 8, max(z_flood, 0)),
                arrowprops={"arrowstyle": "<->", "color": "C2"})
    ax.text(p_gas + dp_l + 11, (big_h + max(z_flood, 0)) / 2, "h$_{max}$", color="C2", va="center")
    ax.set(xlabel="pressure / mbar (gauge)", ylabel="elevation above electrode bottom / cm", ylim=(0, big_h),
           title=f"{m} GDE, 1 m flow-by electrode, gas at {p_gas:g} mbar,\n"
                 "liquid set so that the top is at gas breakthrough")
    ax.title.set_fontsize(10)
    ax.legend(frameon=False, fontsize=7, loc="upper center", bbox_to_anchor=(0.5, -0.13), ncol=2)
    fig.tight_layout()
    fig.savefig(outdir / "pressure-vs-elevation.svg", metadata=meta)
    plt.close(fig)

    # h_max per GDE with its interval.
    fig, ax = plt.subplots(figsize=(5.6, 4.4))
    names = list(results["h_max"])
    y = np.arange(len(names))
    for k, n in enumerate(names):
        hh = results["h_max"][n]
        ax.plot([max(hh["interval_2s_cm"][0], 1.0), hh["interval_2s_cm"][1]], [k, k], color="0.6", lw=3, solid_capstyle="butt",
                label="interval, $\\Delta p^*$ ± 2 s and density range" if k == 0 else None)
        ax.plot(hh["catholyte_cm"], k, "o", color="C1", label="1 M KHCO$_3$ density" if k == 0 else None)
        ax.plot(hh["water_cm"], k, "|", color="C0", ms=12, mew=2, label="water density (paper's basis)" if k == 0 else None)
    ax.axvline(51, color="0.3", lw=0.8, ls="--")
    ax.text(52, -0.6, "51 cm", fontsize=7, color="0.3")
    ax.set(yticks=y, yticklabels=names, xlabel="maximum flow-by electrode height / cm", xscale="log",
           title="h$_{max}$ = $\\Delta p^*$ / ($\\rho$ g), windows at open circuit")
    ax.set_ylim(len(names) - 0.5, -0.8)
    ax.title.set_fontsize(10)
    ax.legend(frameon=False, fontsize=7, loc="upper center", bbox_to_anchor=(0.5, -0.16), ncol=2)
    fig.tight_layout()
    fig.savefig(outdir / "h-max-per-gde.svg", metadata=meta)
    plt.close(fig)


if __name__ == "__main__":
    sys.exit(main())
