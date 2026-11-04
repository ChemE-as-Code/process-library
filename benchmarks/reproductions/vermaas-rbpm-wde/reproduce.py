# /// script
# requires-python = "==3.12.*"
# dependencies = [
#   "numpy==2.2.6",
#   "scipy==1.15.3",
#   "openpyxl==3.1.5",
#   "pyyaml==6.0.2",
#   "matplotlib==3.10.3",
# ]
# ///
"""Reproduce the rBPM WDE benchmark (process-library#329, ADR 0030).

Downloads the pinned 4TU files, verifies their sha256, rebuilds the 1 M KOH WDE series from the
raw titration sheets (R1), runs the authors' unmodified model module against Fig. 5a (R2), checks
the volume dependence of its pH stop event (D1) and validates it against the measured pH of
Fig. 3c (V1). The checks and their tolerances are in tolerances.yaml; this script only evaluates
them. Run: uv run --isolated benchmarks/reproductions/vermaas-rbpm-wde/reproduce.py

Every run extracts the checksum-verified zips into a new temporary folder. The run record names
the commit, whether the folder had uncommitted changes before the run wrote anything, the
sha256 of this script, source.yaml and tolerances.yaml, and whether tolerances.yaml still equals
its frozen version. With uncommitted changes no record is written unless --allow-dirty is given
(the record is then marked provisional). --no-record writes nothing to the folder.
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
import tempfile
import urllib.request
import zipfile
from pathlib import Path

import numpy as np
import yaml

HERE = Path(__file__).resolve().parent
F = 96485.33212  # C/mol, CODATA 2018
C_HCL = 0.1  # mol/L, the paper's standardised titrant
V_TANK_ML = 90.0  # mL, anolyte of the 1 h WDE runs (paper, Methods)
T_CP = 3600.0  # s, constant-current duration of a WDE run
AREA = 5.0  # cm2
READ_RES_ML = 1e-4  # mL, last digit of the burette volumes in the sheets

# Runs the authors' module from file in a separate `python -I` interpreter, so nothing from the
# download's folder lands on sys.path. Reads cases as JSON on stdin, writes results on stdout.
# The module is executed unmodified. A thin shim around scipy.integrate.solve_ivp keeps the
# solver's returned object, because the authors' result dictionary holds only the t_eval grid
# and drops the event (t_events, y_events) that tolerances.yaml asks to report beside it.
RUNNER = r"""
import importlib.util, json, sys
import numpy as np
import scipy.integrate

_solve_ivp = scipy.integrate.solve_ivp
_solutions = []


def _capture(*args, **kwargs):
    sol = _solve_ivp(*args, **kwargs)
    _solutions.append(sol)
    return sol


scipy.integrate.solve_ivp = _capture
spec = importlib.util.spec_from_file_location("authors_model", sys.argv[1])
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
model = mod.MassBalanceAnode("main")
out = []
for case in json.load(sys.stdin):
    c0 = np.array(case["c0"], dtype=float)
    _solutions.clear()
    res = model.massBalanceTanks(case["j"], case["wde"], case["c_xover"], c0 * case["v_tank"],
                                 case["v_tank"], case["t_op_h"] * 3600.0)
    if len(_solutions) != 1:
        raise SystemExit(f"expected one solve_ivp call per case, got {len(_solutions)}")
    sol = _solutions[0]
    keep = slice(None) if case.get("trajectory") else slice(-2, None)
    row = {k: np.asarray(res[k])[keep].tolist() for k in ("time", "pH", "c_OH_tank", "c_H_tank")}
    events = sol.t_events[0] if sol.t_events is not None and len(sol.t_events) else []
    row["event_t_h"] = float(events[0]) / 3600.0 if len(events) else None
    row["event_n"] = [float(x) for x in sol.y_events[0][0]] if len(events) else None
    row["solver_status"] = int(sol.status)
    out.append(row)
json.dump(out, sys.stdout)
"""


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def fetch(source: dict, cache: Path, work: Path) -> tuple[dict[str, Path], dict[str, str]]:
    """Download (once) and verify every pinned file; extract each zip fresh into `work`.

    A download goes to `<name>.part` and is renamed into the cache only after its sha256
    matches, so an interrupted download never sits at the cache path. A cached file that fails
    the check is downloaded once more. Zips are extracted on every run from the file whose
    sha256 was just checked, into a new per-run folder: nothing extracted earlier is reused.
    """
    cache.mkdir(parents=True, exist_ok=True)
    out, state = {}, {}
    for f in source["reference"]["dataset"]["files"]:
        target = cache / f["name"]
        state[f["name"]] = "cache hit"
        if target.exists() and sha256(target) != f["sha256"]:
            print(f"cached {f['name']} fails its sha256; downloading again", file=sys.stderr)
            target.unlink()
        if not target.exists():
            part = target.with_name(target.name + ".part")
            part.unlink(missing_ok=True)
            print(f"download {f['name']}", file=sys.stderr)
            urllib.request.urlretrieve(f["url"], part)
            if sha256(part) != f["sha256"]:
                part.unlink(missing_ok=True)
                sys.exit(f"sha256 mismatch for the download of {f['name']}; the record may have changed")
            part.replace(target)
            state[f["name"]] = "downloaded"
        if target.suffix == ".zip":
            folder = work / target.stem
            with zipfile.ZipFile(target) as z:
                z.extractall(folder)
            out[f["name"]] = folder
        else:
            out[f["name"]] = target
    return out, state


# --- R1: titration sheets -------------------------------------------------------------------


def docx_paragraphs(path: Path) -> list[str]:
    xml = zipfile.ZipFile(path).read("word/document.xml").decode()
    paras = []
    for p in re.findall(r"<w:p[ >].*?</w:p>", xml, re.S):
        text = "".join(re.findall(r"<w:t[^>]*>([^<]*)</w:t>", p)).strip()
        if text:
            paras.append(text)
    return paras


def header_ml(paras: list[str], key: str) -> float | None:
    line = next((p for p in paras if p.startswith(key)), "")
    m = re.search(r"([\d.]+)\s*m[lL]", line)
    return float(m.group(1)) if m else None


def parse_sheet(path: Path) -> dict:
    paras = docx_paragraphs(path)
    volumes = {"V0": [], "V1": [], "V2": []}
    mode = None
    for tok in paras[paras.index("Data Extraction for Calculation") + 1 :]:
        if tok[:2] in volumes:
            mode = tok[:2]
        elif re.fullmatch(r"\d+(\.\d+)?", tok) and mode:
            volumes[mode].append(float(tok))
    if len(volumes["V1"]) != len(volumes["V2"]):
        raise ValueError(f"{path.name}: V1 and V2 counts differ")
    notes = []
    v_titrate = header_ml(paras, "Sampling Volume per Titration")
    if v_titrate is None:
        notes.append("sample volume blank; 1 mL used")
        v_titrate = 1.0
    v_tank = header_ml(paras, "eCO2R test electrolyte Volume")
    if v_tank is None:
        notes.append("electrolyte volume blank; 90 mL used")
    elif v_tank != V_TANK_ML:
        notes.append(f"electrolyte volume stated {v_tank:g} mL; 90 mL used (Methods)")
    name = path.name
    return {
        "file": name,
        "date": name[:8],
        "j": float(re.search(r"_j(\d+)_", name).group(1)),
        "v_titrate_ml": v_titrate,
        "notes": notes,
        **volumes,
    }


def sheet_matrix(s: dict) -> dict:
    """Every V0 with every (V1, V2) pair, paper equations 3 to 10."""
    scale = C_HCL * 1e-3 * V_TANK_ML / s["v_titrate_ml"]  # mol in the tank per mL of titrant
    n_e = s["j"] * 1e-3 * AREA * T_CP / F
    wde, k_loss, hco3 = [], [], []
    for v0 in s["V0"]:
        for v1, v2 in zip(s["V1"], s["V2"]):
            n_k = (v0 - v2) * scale  # K+ lost: c_K = V * c_HCl / V_titrate before (V0) and after (V2)
            n_c = (v2 - v1) * scale  # carbon gained, as CO3--
            k_loss.append(n_k)
            hco3.append(n_c)
            wde.append(1.0 - (n_k + n_c) / n_e)
    return {"wde": wde, "n_k": k_loss, "n_hco3": hco3, "n_e": n_e}


def r1(raw: Path) -> dict:
    sheets = [parse_sheet(p) for p in sorted((raw / "TitrationToWDE" / "CurrentDensity").glob("*.docx"))]
    by_j: dict[float, list] = {}
    for s in sheets:
        s.update(sheet_matrix(s))
        by_j.setdefault(s["j"], []).append(s)
    rows = {}
    for j, runs in sorted(by_j.items()):
        pooled = np.concatenate([r["wde"] for r in runs])
        n_k = np.concatenate([r["n_k"] for r in runs])
        n_c = np.concatenate([r["n_hco3"] for r in runs])
        run_means = [float(np.mean(r["wde"])) for r in runs]
        rows[j] = {
            "runs": [r["file"] for r in runs],
            # The runs (dates) are the replicates. The (V0, V1/V2) pairs of one run share their
            # V0 and V1/V2 readings, so they are not independent replicates.
            "n_runs": len(runs),
            "pairs": int(pooled.size),
            "pairs_per_run": [len(r["wde"]) for r in runs],
            # The R1 check uses the pooled mean over every pair of every run (as implemented
            # before the first run); the run-level statistics are reported beside it.
            "wde_mean": float(pooled.mean()),
            "wde_sd": float(pooled.std(ddof=1)) if pooled.size > 1 else None,
            "wde_run_means": run_means,
            "wde_mean_of_run_means": float(np.mean(run_means)),
            "wde_sd_of_run_means": float(np.std(run_means, ddof=1)) if len(runs) > 1 else None,
            "wde_mean_of_run_sds": float(np.mean([np.std(r["wde"], ddof=1) for r in runs if len(r["wde"]) > 1])),
            "c_xover": float(n_c.sum() / (n_c.sum() + n_k.sum())),
            "j_coion": float((1.0 - pooled.mean()) * j),
            "notes": sorted({f"{r['file']}: {n}" for r in runs for n in r["notes"]}),
            "d_res": 2 * READ_RES_ML * C_HCL * 1e-3 * V_TANK_ML / runs[0]["v_titrate_ml"] * F / (j * 1e-3 * AREA * T_CP),
        }
    return rows


# --- source data ----------------------------------------------------------------------------


def sheet_rows(path: Path, sheet: str, first_row: int) -> list[list]:
    import openpyxl

    ws = openpyxl.load_workbook(path, data_only=True)[sheet]
    return [list(r) for r in ws.iter_rows(min_row=first_row, values_only=True)]


def numeric(v) -> bool:
    return isinstance(v, (int, float)) and not isinstance(v, bool) and math.isfinite(v)


def fraction_scale(wde: float) -> float:
    """1 for a WDE given as a fraction, 100 for one given in percent (applied to its sd too)."""
    return 100.0 if wde > 1.5 else 1.0


# --- model runs -----------------------------------------------------------------------------


def run_model(module: Path, cases: list[dict]) -> list[dict]:
    with tempfile.TemporaryDirectory() as tmp:
        runner = Path(tmp) / "runner.py"
        runner.write_text(RUNNER)
        proc = subprocess.run(
            [sys.executable, "-I", str(runner), str(module)],
            input=json.dumps(cases),
            capture_output=True,
            text=True,
            cwd=tmp,
            check=False,
        )
    if proc.returncode:
        sys.exit(f"model run failed:\n{proc.stderr}")
    return json.loads(proc.stdout)


def c0(c_oh: float, defaults: dict) -> list[float]:
    ic = defaults["initial_concentrations_M"]
    return [c_oh, ic["CO3--"], ic["HCO3-"], ic["CO2"], 1e-14 / c_oh, c_oh]


def first_crossing(t, ph, level=12.0) -> float | None:
    t, ph = np.asarray(t), np.asarray(ph)
    below = np.nonzero(ph <= level)[0]
    if below.size == 0:
        return None
    i = below[0]
    if i == 0:
        return float(t[0])
    return float(t[i - 1] + (level - ph[i - 1]) * (t[i] - t[i - 1]) / (ph[i] - ph[i - 1]))


DESIGN_DATA = HERE.parents[2] / "processes" / "co2-electrolysis-bpm-1" / "data" / "measured" / "wde-1m-koh.yaml"


def git(*a) -> str:
    return subprocess.run(["git", *a], cwd=HERE, capture_output=True, text=True, check=False).stdout.strip()


def provenance() -> dict:
    """State of the code and the frozen rules, taken before the run writes anything."""
    files = {p.name: sha256(p) for p in (Path(__file__).resolve(), HERE / "source.yaml", HERE / "tolerances.yaml")}
    added = git("log", "--format=%H", "--diff-filter=A", "--", "tolerances.yaml").splitlines()
    freeze = added[-1] if added else ""
    at_freeze = subprocess.run(["git", "show", f"{freeze}:./tolerances.yaml"], cwd=HERE, capture_output=True,
                               check=False).stdout
    frozen_sha = hashlib.sha256(at_freeze).hexdigest() if freeze and at_freeze else None
    return {
        "commit": git("rev-parse", "HEAD"),
        # Uncommitted changes in this folder or in the design data it compares with, before any
        # output of this run (figures, record) exists.
        "dirty": bool(git("status", "--porcelain", "--", ".", str(DESIGN_DATA))),
        "files_sha256": files,
        "tolerances_frozen_in": freeze,
        "tolerances_last_changed_in": git("log", "-1", "--format=%H", "--", "tolerances.yaml"),
        "tolerances_sha256_at_freeze": frozen_sha,
        "tolerances_unchanged_since_freeze": frozen_sha == files["tolerances.yaml"],
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--cache", type=Path, default=Path.home() / ".cache/cheme-as-code/4tu/5c4fc325-v1")
    ap.add_argument("--no-record", action="store_true",
                    help="write nothing to this folder: no run record in reruns/, no figures")
    ap.add_argument("--allow-dirty", action="store_true",
                    help="write a record (marked provisional) although the folder has uncommitted changes")
    args = ap.parse_args()

    prov = provenance()
    if not prov["tolerances_unchanged_since_freeze"]:
        print("warning: tolerances.yaml differs from its frozen version", file=sys.stderr)
    # The rules of tolerances.yaml are implemented below as written there (prose, not parsed).
    source = yaml.safe_load((HERE / "source.yaml").read_text())
    with tempfile.TemporaryDirectory(prefix="vermaas-rbpm-wde-") as work:
        files, cache_state = fetch(source, args.cache, Path(work))
        results, plot_data = evaluate(source, files)
    report(results)
    if args.no_record:
        print("--no-record: no figures and no run record written")
    elif prov["dirty"] and not args.allow_dirty:
        print("the folder has uncommitted changes: no record written (commit first, or pass --allow-dirty)")
    else:
        plots(results, *plot_data, HERE / "figures")
        record(results, source, prov, cache_state)
    failed = [k for k in ("R1", "R2") if any(r["status"] == "fail" for r in results[k])]
    failed += ["V1"] if results["V1"]["status"] == "fail" else []
    return 1 if failed else 0


def evaluate(source: dict, files: dict) -> tuple[dict, tuple]:
    raw = files["RawData_Experiments_rBPME_WDE.zip"]
    manuscript = files["SourceData_Manuscript.zip"]
    module = files["Model_rBPM_WDE_longterm.zip"] / "Model_rBPM_stability_crossover_pHstop.py"
    module_nostop = files["Model_rBPM_WDE_longterm.zip"] / "Model_rBPM_stability_crossover.py"
    defaults = source["file_to_figure"]["model_code"]["default_inputs"]
    t_op_h = 10000.0
    dt_grid = t_op_h / 9999
    results: dict = {}

    # R1 -----------------------------------------------------------------------------------
    ours = r1(raw)
    pub = {}
    for row in sheet_rows(manuscript / "PratsVergel_SourceData_Fig3.xlsx", "Fig3a", 2):
        if numeric(row[0]) and numeric(row[1]):
            s = fraction_scale(row[1])
            pub[float(row[0])] = {"wde": row[1] / s, "sd": row[2] / s, "j_coion": float(row[3])}
    r1_rows = []
    for j, p in sorted(pub.items()):
        o = ours.get(j)
        if o is None:
            r1_rows.append({"j": j, "status": "gap", "reason": "no raw sheet at this current density"})
            continue
        limit = max(0.25 * p["sd"], o["d_res"])
        dev = o["wde_mean"] - p["wde"]
        r1_rows.append({"j": j, "published": p, "ours": o, "deviation": dev, "limit": limit,
                        "status": "pass" if abs(dev) <= limit else "fail"})
    results["R1"] = r1_rows

    # R2 and D1 ----------------------------------------------------------------------------
    fig5 = [[r[0] / fraction_scale(r[0]), *r[1:]]
            for r in sheet_rows(manuscript / "PratsVergel_SourceData_Fig5.xlsx", "Fig5a", 3) if numeric(r[0])]
    cases = []
    for r in fig5:
        for v in (1.0, 10.0):
            cases.append({"j": 200, "wde": float(r[0]), "c_xover": defaults["C_xover"], "c0": c0(1.0, defaults),
                          "v_tank": v, "t_op_h": t_op_h})
    d1_cases = [{"j": 200, "wde": 0.95, "c_xover": 0.66, "c0": c0(1.0, defaults), "v_tank": v, "t_op_h": t_op_h}
                for v in (1.0, 10.0)]
    runs = run_model(module, cases + d1_cases)
    fig5_runs, d1_runs = runs[: len(cases)], runs[len(cases):]

    def time_rule(t_ours, t_pub):
        limit = max(dt_grid, 1e-3 * t_pub)
        if t_pub >= t_op_h - dt_grid:
            return limit, "pass" if t_ours >= t_op_h - dt_grid else "fail"
        return limit, "pass" if abs(t_ours - t_pub) <= limit else "fail"

    r2_rows, d1_10l = [], []
    for k, r in enumerate(fig5):
        for col, v, sink in ((1, 1.0, r2_rows), (2, 10.0, d1_10l)):
            run = fig5_runs[2 * k + (0 if v == 1.0 else 1)]
            t_ours = run["time"][-1]  # the frozen t_ours: last point of the returned grid
            t_event = run["event_t_h"]  # reported beside it (tolerances.yaml R2.t_ours)
            if not numeric(r[col]):
                sink.append({"wde": float(r[0]), "ours_h": t_ours, "event_h": t_event,
                             "status": "gap", "reason": "no published value"})
                continue
            t_pub = float(r[col])
            limit, status = time_rule(t_ours, t_pub)
            sink.append({"wde": float(r[0]), "published_h": t_pub, "ours_h": t_ours,
                         "deviation_h": t_ours - t_pub, "deviation_pct": 100 * (t_ours - t_pub) / t_pub,
                         "limit_h": limit, "status": status,
                         "event_h": t_event,
                         "event_deviation_h": None if t_event is None else t_event - t_pub,
                         "event_deviation_pct": None if t_event is None else 100 * (t_event - t_pub) / t_pub})
    results["R2"] = r2_rows

    # D1 classifies on the state at the stop: the solver's located event (t_events, y_events),
    # with the event-location error checked against the band, as the frozen reason requires.
    # The last grid sample of the result dictionary, which the first two records used, is
    # reported beside it with its sampling error.
    band = 0.05
    d1 = {}
    for v, run in zip((1.0, 10.0), d1_runs):
        n = run["event_n"]
        entry = {"stop_h": run["event_t_h"], "grid_stop_h": run["time"][-1]}
        if n is not None:
            entry.update({
                "pH_conc_at_stop": 14 + math.log10(n[0] / v),
                "pH_from_H_at_stop": -math.log10(n[4] / v),
                # the event function is -log10(n_H) - 12; its value at the located event, in pH
                "event_location_error_pH": abs(-math.log10(n[4]) - 12.0),
            })
        entry.update({
            "grid_pH_conc_at_stop": run["pH"][-1],
            "grid_pH_from_H_at_stop": -math.log10(run["c_H_tank"][-1]),
            "grid_sampling_error_pH": run["pH"][-2] - run["pH"][-1],
        })
        d1[f"{v:g} L"] = entry

    def classify(one, ten, error):
        near = lambda x, y: abs(x - y) <= band  # noqa: E731
        if one is None or ten is None or error >= band:
            return "unresolved"
        if near(one, 12) and near(ten, 13):
            return "confirmed"
        if near(one, 12) and near(ten, 12):
            return "rejected"
        return "unresolved"

    have_events = all("pH_conc_at_stop" in e for e in d1.values())
    event_error = max((e["event_location_error_pH"] for e in d1.values() if "event_location_error_pH" in e),
                      default=math.inf)
    verdict = classify(d1["1 L"].get("pH_conc_at_stop"), d1["10 L"].get("pH_conc_at_stop"),
                       event_error if have_events else math.inf)
    grid_error = max(e["grid_sampling_error_pH"] for e in d1.values())
    grid_verdict = classify(d1["1 L"]["grid_pH_conc_at_stop"], d1["10 L"]["grid_pH_conc_at_stop"], grid_error)
    one = d1["1 L"].get("pH_conc_at_stop")
    h_ok = one is not None and abs(d1["1 L"]["pH_from_H_at_stop"] - one) <= band
    # Informational, not frozen checks (added after the first run to explain its deviations):
    # the concentration-basis time to pH 12 from the model without stop condition at the D1
    # inputs, and the WDE 0.999 row of Fig. 5a with a horizon long enough to reach the threshold.
    info_cases = [{**c, "trajectory": True} for c in d1_cases]
    info_cases.append({"j": 200, "wde": 0.999, "c_xover": defaults["C_xover"], "c0": c0(1.0, defaults),
                       "v_tank": 1.0, "t_op_h": 30000.0, "trajectory": True})
    info = run_model(module_nostop, info_cases)
    for v, run in zip((1.0, 10.0), info[:2]):
        d1[f"{v:g} L"]["t12_concentration_basis_h"] = first_crossing(run["time"], run["pH"])
    results["D1"] = {"runs": d1, "classification": verdict, "band_pH": band,
                     "event_location_error_pH": event_error if have_events else None,
                     "h_state": "consistent" if h_ok else "numerically unresolved",
                     "grid_sample_classification": grid_verdict,
                     "grid_sampling_error_pH": grid_error,
                     "published_10L": d1_10l}
    results["informational"] = {
        "wde_0.999_1L_t12_h_long_horizon": first_crossing(info[2]["time"], info[2]["pH"]),
        # The published Fig. 5a rows as read, all three volumes (for the irregularities noted
        # in comparison.md and source.yaml).
        "fig5a_published": [{"wde": float(r[0]), "t_1L_h": r[1], "t_10L_h": r[2], "t_100L_h": r[3]} for r in fig5],
    }

    # V1 -----------------------------------------------------------------------------------
    fig3c = [(float(t), float(p)) for t, p, *_ in sheet_rows(manuscript / "PratsVergel_SourceData_Fig3.xlsx", "Fig3c", 3)
             if numeric(t) and numeric(p)]
    t_meas, ph_meas = map(np.array, zip(*fig3c))
    a = next(r for r in sheet_rows(manuscript / "PratsVergel_SourceData_Fig4.xlsx", "Fig4a", 2)
             if numeric(r[0]) and abs(r[0] - 0.1) < 1e-9)
    c = next(r for r in sheet_rows(manuscript / "PratsVergel_SourceData_Fig4.xlsx", "Fig4c", 2)
             if numeric(r[0]) and abs(r[0] - 0.1) < 1e-9)
    wde, wde_sd = a[1] / fraction_scale(a[1]), a[2] / fraction_scale(a[1])
    jh, jh_sd, jk, jk_sd = map(float, c[1:5])
    cx = jh / (jh + jk)
    cx_sd = math.hypot(jk * jh_sd, jh * jk_sd) / (jh + jk) ** 2
    t_op_v = 2.0 * float(t_meas.max())
    corners = [(wde, cx)] + [(min(wde + sw * 2 * wde_sd, 1.0), min(max(cx + sc * 2 * cx_sd, 0.0), 1.0))
                             for sw in (-1, 1) for sc in (-1, 1)]
    v_runs = run_model(module_nostop, [{"j": 100, "wde": w, "c_xover": x, "c0": c0(0.1, defaults), "v_tank": 0.020,
                                        "t_op_h": t_op_v, "trajectory": True} for w, x in corners])
    t12_model = [first_crossing(r["time"], r["pH"]) for r in v_runs]
    t12_meas = first_crossing(t_meas, ph_meas)
    nominal = v_runs[0]
    in_range = t_meas <= max(nominal["time"])
    rmse = float(np.sqrt(np.mean((np.interp(t_meas[in_range], nominal["time"], nominal["pH"]) - ph_meas[in_range]) ** 2)))
    finite = [t for t in t12_model if t is not None]
    if t12_meas is None or len(finite) < len(t12_model):
        v1_status = "gap"
    else:
        v1_status = "pass" if min(finite) <= t12_meas <= max(finite) else "fail"
    results["V1"] = {"inputs": {"wde": wde, "wde_sd": wde_sd, "c_xover": cx, "c_xover_sd": cx_sd},
                     "t12_measured_h": t12_meas, "t12_model_h": t12_model[0],
                     "envelope_h": [min(finite, default=None), max(finite, default=None)],
                     "corners": [{"wde": w, "c_xover": x, "t12_h": t} for (w, x), t in zip(corners, t12_model)],
                     "pH_rmse": rmse, "status": v1_status}

    results["design_data_consistency"] = design_data_consistency(ours)
    return results, (ours, pub, t_meas, ph_meas, v_runs)


def design_data_consistency(ours: dict) -> dict:
    """Compare the R1 rebuild with the design case's own series (ADR 0031: the two parsers must
    agree on the same inputs). Reads the design data; the design never reads this folder.
    Not a frozen check: reported, and it does not change any verdict or the exit code."""
    if not DESIGN_DATA.exists():
        return {"status": "gap", "reason": f"{DESIGN_DATA.name} not found"}
    doc = yaml.safe_load(DESIGN_DATA.read_text())
    diffs, n = [], 0
    for row in doc["series"]:
        j = float(row["current_density"]["value"])
        o = ours.get(j)
        if o is None:
            diffs.append(f"j {j:g}: not in the rebuild")
            continue
        checks = [("wde mean", o["wde_mean"], row["wde"]["mean"], 1e-5),
                  ("wde sd", o["wde_sd"], row["wde"]["sd"], 1e-5),
                  ("pairs", o["pairs"], row["wde"]["n_pairs"], 0),
                  ("carbon fraction", o["c_xover"], row["coion_carbon_fraction"]["value"], 1e-3)]
        checks += [(f"run {r['date']} mean", m, r["wde_mean"], 1e-5) for m, r in zip(o["wde_run_means"], row["runs"])]
        checks += [(f"run {r['date']} pairs", k, r["n_pairs"], 0) for k, r in zip(o["pairs_per_run"], row["runs"])]
        if len(row["runs"]) != o["n_runs"]:
            diffs.append(f"j {j:g}: {len(row['runs'])} runs in the design data, {o['n_runs']} here")
        for what, a, b, tol in checks:
            n += 1
            if abs(a - b) > tol:
                diffs.append(f"j {j:g}: {what} {a} here, {b} in the design data")
    missing = sorted(set(ours) - {float(r["current_density"]["value"]) for r in doc["series"]})
    diffs += [f"j {j:g}: not in the design data" for j in missing]
    return {"file": str(DESIGN_DATA.relative_to(HERE.parents[2])), "sha256": sha256(DESIGN_DATA),
            "values_compared": n, "differences": diffs, "status": "consistent" if not diffs else "differs"}


def report(results: dict) -> None:
    def fmt(x, spec):
        return "-" if x is None else format(x, spec)

    print("R1  WDE vs j, 1 M KOH (ours from raw titrations vs Fig. 3a; pooled pairs, run means beside)")
    print("    j    published   sd       ours     dev      limit    pairs runs status   mean of run means")
    for r in results["R1"]:
        if r["status"] == "gap":
            print(f"    {r['j']:<4g} gap: {r['reason']}")
            continue
        p, o = r["published"], r["ours"]
        print(f"    {r['j']:<4g} {p['wde']:.5f}    {p['sd']:.5f}  {o['wde_mean']:.5f}  {r['deviation']:+.5f} "
              f"{r['limit']:.5f}  {o['pairs']:<5d} {o['n_runs']:<4d} {r['status']:<8s} "
              f"{o['wde_mean_of_run_means']:.5f} ({o['wde_mean_of_run_means'] - p['wde']:+.5f})")
    print("R2  time to pH 12 at 1 L (authors' model, unmodified, vs Fig. 5a); grid time decides, event time beside")
    for r in results["R2"]:
        if "published_h" not in r:
            print(f"    WDE {r['wde']:.4f}: grid {r['ours_h']:.1f} h, {r.get('reason', '')}  {r['status']}")
            continue
        print(f"    WDE {r['wde']:.4f}: published {r['published_h']:.1f} h; grid {r['ours_h']:.3f} h "
              f"({r['deviation_pct']:+.2f} %) {r['status']}; event {fmt(r['event_h'], '.3f')} h "
              f"({fmt(r['event_deviation_pct'], '+.2f')} %)")
    d1 = results["D1"]
    print(f"D1  pH stop event: {d1['classification']} (event-location error {fmt(d1['event_location_error_pH'], '.2e')} pH, "
          f"band {d1['band_pH']}; H+ state {d1['h_state']})")
    for v, run in d1["runs"].items():
        print(f"    {v}: event {fmt(run['stop_h'], '.3f')} h, pH(OH-) {fmt(run.get('pH_conc_at_stop'), '.4f')}, "
              f"pH(H+) {fmt(run.get('pH_from_H_at_stop'), '.4f')}; last grid sample {run['grid_stop_h']:.3f} h, "
              f"pH(OH-) {run['grid_pH_conc_at_stop']:.4f}, sampling error {run['grid_sampling_error_pH']:.4f}; "
              f"concentration-basis t12 {fmt(run['t12_concentration_basis_h'], '.3f')} h (informational)")
    print(f"    on the last grid samples: {d1['grid_sample_classification']} "
          f"(sampling error {d1['grid_sampling_error_pH']:.4f} against the band {d1['band_pH']})")
    n10 = sum(r["status"] == "pass" for r in d1["published_10L"])
    print(f"    10 L column: {n10} of {len(d1['published_10L'])} rows match the unmodified model under the R2 rule")
    t_long = results["informational"]["wde_0.999_1L_t12_h_long_horizon"]
    print(f"    WDE 0.999, 1 L, 30000 h horizon: t12 {fmt(t_long, '.1f')} h (informational)")
    v1 = results["V1"]
    print(f"V1  validation vs Fig. 3c: measured t12 {v1['t12_measured_h']}, model {v1['t12_model_h']}, "
          f"envelope {v1['envelope_h']}, pH RMSE {v1['pH_rmse']:.3f}: {v1['status']}")
    dd = results["design_data_consistency"]
    print(f"design data ({dd.get('file', '?')}): {dd['status']}"
          + (f", {dd['values_compared']} values compared" if "values_compared" in dd else "")
          + "".join(f"\n    {d}" for d in dd.get("differences", [])))


def record(results: dict, source: dict, prov: dict, cache_state: dict) -> None:
    import scipy

    rec = {
        "schema": "cheme-as-code/reproduction-run/v1",
        "reproduction": "vermaas-rbpm-wde",
        "run_at": dt.datetime.now(dt.UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
        **prov,
        "provisional": prov["dirty"],
        "inputs": {f["name"]: f["sha256"] for f in source["reference"]["dataset"]["files"]},
        "cache_state": cache_state,
        "versions": {"python": platform.python_version(), "numpy": np.__version__, "scipy": scipy.__version__,
                     "platform": platform.platform()},
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


def plots(results, ours, pub, t_meas, ph_meas, v_runs, outdir: Path) -> None:
    import matplotlib

    matplotlib.use("Agg")
    matplotlib.rcParams["svg.hashsalt"] = "vermaas-rbpm-wde"
    import matplotlib.pyplot as plt

    outdir.mkdir(exist_ok=True)
    meta = {"Date": None}

    fig, ax = plt.subplots(figsize=(5, 3.5))
    js = sorted(pub)
    ax.errorbar(js, [pub[j]["wde"] for j in js], yerr=[pub[j]["sd"] for j in js], fmt="o", capsize=3, label="published (Fig. 3a)")
    jo = sorted(ours)
    ax.errorbar([j + 3 for j in jo], [ours[j]["wde_mean"] for j in jo], yerr=[ours[j]["wde_sd"] or 0 for j in jo],
                fmt="s", capsize=3, label="rebuilt from raw titrations")
    ax.set(xlabel="current density / mA cm$^{-2}$", ylabel="water dissociation efficiency", title="R1: 1 M KOH, 90 mL, 1 h")
    ax.legend(frameon=False)
    fig.tight_layout()
    fig.savefig(outdir / "r1-wde-vs-current-density.svg", metadata=meta)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(5, 3.5))
    for key, label, rows in (("1 L", "1 L", results["R2"]), ("10 L", "10 L", results["D1"]["published_10L"])):
        rows = [r for r in rows if "published_h" in r]
        ax.plot([r["wde"] for r in rows], [r["published_h"] for r in rows], "o", mfc="none", label=f"published, {label}")
        ax.plot([r["wde"] for r in rows], [r["ours_h"] for r in rows], "x", label=f"authors' model rerun, {label}")
    ax.set(xlabel="water dissociation efficiency", ylabel="time to anolyte pH 12 / h", yscale="log",
           title="R2 and D1: 200 mA cm$^{-2}$, 1 M KOH, 5 cm$^2$")
    ax.legend(frameon=False, fontsize=8)
    fig.tight_layout()
    fig.savefig(outdir / "r2-time-to-ph12.svg", metadata=meta)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(5, 3.5))
    for k, r in enumerate(v_runs):
        ax.plot(r["time"], r["pH"], color="C1", lw=1.6 if k == 0 else 0.6, alpha=1 if k == 0 else 0.5,
                label="model, nominal inputs" if k == 0 else ("model, inputs ± 2 sd" if k == 1 else None))
    ax.plot(t_meas, ph_meas, ".", ms=2, color="C0", label="measured (Fig. 3c)")
    ax.axhline(12, color="0.5", lw=0.8, ls="--")
    ax.set(xlabel="time / h", ylabel="anolyte pH", xlim=(0, max(t_meas) * 1.05),
           title="V1: 20 mL 0.1 M KOH, 100 mA cm$^{-2}$")
    ax.legend(frameon=False, fontsize=8)
    fig.tight_layout()
    fig.savefig(outdir / "v1-ph-validation.svg", metadata=meta)
    plt.close(fig)


if __name__ == "__main__":
    sys.exit(main())
