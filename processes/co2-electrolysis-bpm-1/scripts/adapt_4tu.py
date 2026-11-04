"""Measured series of the reverse-bias BPM cell from the pinned 4TU raw data (#329, #330).

Downloads (once) RawData_Experiments_rBPME_WDE.zip of the 4TU record
10.4121/5c4fc325-a71b-4ca8-9c1b-01c0405936a2.v1, refuses it unless its sha256 matches, and
reads the zip directly (nothing is extracted):

- every 1 M KOH titration sheet of the current-density study, with the paper's equations 3 to
  10 (DESIGN.md D-002): data/measured/wde-1m-koh.yaml and figures/wde-1m-koh.svg;
- the same runs with their chronopotentiometry (CP), mass-flow meter (MFM) and gas chromatograph
  (GC) files, paired by date and current density (DESIGN.md D-005): the cell voltage, the
  outlet flow and mole fractions of CO and H2, and the titration of each run, in
  experiments/electrochemistry/rbpm-1m-koh.yaml (schema cheme/electrochemical-measurements/v1),
  which `cheme experiments electrochem` processes.

Uses only the raw files: no published result and nothing of benchmarks/reproductions/ enters
(ADR 0032). The spreadsheets are read by scripts/rawsheets.py (standard library only).

Run from the process folder: cheme run scripts/adapt_4tu.py [--cache DIR]
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import re
import statistics
import sys
import urllib.request
import zipfile
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))
import rawsheets  # the stdlib spreadsheet reader next to this script

ROOT = Path(__file__).resolve().parents[1]
DOI = "10.4121/5c4fc325-a71b-4ca8-9c1b-01c0405936a2.v1"
RAW = {
    "name": "RawData_Experiments_rBPME_WDE.zip",
    "url": "https://data.4tu.nl/file/5c4fc325-a71b-4ca8-9c1b-01c0405936a2/24f2fa03-878e-4af1-b398-98fdd3df10f9",
    "sha256": "3f7d70d9d7bbb5bf024dc27f4ff778a66e52211348263be37a47001b8a720c10",
}
SHEETS = "TitrationToWDE/CurrentDensity/"  # member path inside the zip
F = 96485.33212  # C/mol, CODATA 2018
C_HCL = 0.1  # mol/L titrant (paper, Methods)
V_TANK_ML = 90.0  # anolyte volume of the WDE runs (paper, Methods)
T_CP = 3600.0  # s
AREA = 5.0  # cm2


def fetch(cache: Path) -> Path:
    """Download (once) to <name>.part, rename into the cache only after the sha256 matches.

    A cached file that fails the check is downloaded once more. The zip is read directly; nothing
    is extracted.
    """
    cache.mkdir(parents=True, exist_ok=True)
    target = cache / RAW["name"]

    def digest(path: Path) -> str:
        return hashlib.sha256(path.read_bytes()).hexdigest()

    if target.exists() and digest(target) != RAW["sha256"]:
        print(f"cached {target.name} fails its sha256; downloading again")
        target.unlink()
    if not target.exists():
        part = target.with_name(target.name + ".part")
        part.unlink(missing_ok=True)
        urllib.request.urlretrieve(RAW["url"], part)
        got = digest(part)
        if got != RAW["sha256"]:
            part.unlink(missing_ok=True)
            raise SystemExit(f"sha256 mismatch for the download of {RAW['name']}: {got}; the record may have changed")
        part.replace(target)
    return target


def paragraphs(docx: bytes) -> list[str]:
    import io

    xml = zipfile.ZipFile(io.BytesIO(docx)).read("word/document.xml").decode()
    out = []
    for p in re.findall(r"<w:p[ >].*?</w:p>", xml, re.S):
        text = "".join(re.findall(r"<w:t[^>]*>([^<]*)</w:t>", p)).strip()
        if text:
            out.append(text)
    return out


def header_ml(paras: list[str], key: str) -> float | None:
    line = next((p for p in paras if p.startswith(key)), "")
    m = re.search(r"([\d.]+)\s*m[lL]", line)
    return float(m.group(1)) if m else None


def run(name: str, paras: list[str]) -> dict:
    """One sheet: every V0 with every (V1, V2) pair."""
    volumes = {"V0": [], "V1": [], "V2": []}
    mode = None
    for tok in paras[paras.index("Data Extraction for Calculation") + 1 :]:
        if tok[:2] in volumes:
            mode = tok[:2]
        elif re.fullmatch(r"\d+(\.\d+)?", tok) and mode:
            volumes[mode].append(float(tok))
    notes = []
    v_titrate = header_ml(paras, "Sampling Volume per Titration")
    if v_titrate is None:
        notes.append("sample volume blank in the sheet; 1 mL used")
        v_titrate = 1.0
    v_tank = header_ml(paras, "eCO2R test electrolyte Volume")
    if v_tank is None:
        notes.append("electrolyte volume blank in the sheet; 90 mL used")
    elif v_tank != V_TANK_ML:
        notes.append(f"sheet states {v_tank:g} mL electrolyte; 90 mL used (paper, Methods)")
    j = float(re.search(r"_j(\d+)_", name).group(1))
    scale = C_HCL * 1e-3 * V_TANK_ML / v_titrate  # mol in the tank per mL titrant
    n_e = j * 1e-3 * AREA * T_CP / F
    wde, n_k, n_c = [], [], []
    for v0 in volumes["V0"]:
        for v1, v2 in zip(volumes["V1"], volumes["V2"], strict=True):
            n_k.append((v0 - v2) * scale)
            n_c.append((v2 - v1) * scale)
            wde.append(1.0 - (n_k[-1] + n_c[-1]) / n_e)
    return {"file": name.rsplit("/", 1)[-1], "date": name.rsplit("/", 1)[-1][:8], "j": j,
            "wde": wde, "n_k": n_k, "n_c": n_c, "notes": notes, "volumes": volumes, "v_titrate": v_titrate}


def titration_runs(zip_path: Path) -> list[dict]:
    """Every 1 M KOH titration sheet of the current-density study, evaluated (run())."""
    runs = []
    with zipfile.ZipFile(zip_path) as z:
        for name in sorted(n for n in z.namelist() if n.startswith(SHEETS) and n.endswith(".docx")):
            runs.append(run(name, paragraphs(z.read(name))))
    if not runs:
        raise SystemExit(f"no titration sheets under {SHEETS} in {zip_path.name}")
    return runs


def series(runs: list[dict]) -> list[dict]:
    out = []
    for j in sorted({r["j"] for r in runs}):
        rs = [r for r in runs if r["j"] == j]
        wde = [w for r in rs for w in r["wde"]]
        n_k = sum(x for r in rs for x in r["n_k"])
        n_c = sum(x for r in rs for x in r["n_c"])
        out.append({
            "current_density": {"value": j, "unit": "mA/cm2"},
            "wde": {"mean": round(statistics.fmean(wde), 5), "sd": round(statistics.stdev(wde), 5),
                    "n_pairs": len(wde), "provenance": "calculated"},
            "coion_carbon_fraction": {"value": round(n_c / (n_c + n_k), 3), "provenance": "calculated",
                                      "note": "HCO3- share of the co-ion current, pooled over the pairs"},
            "runs": [{"file": r["file"], "date": r["date"], "n_pairs": len(r["wde"]),
                      "wde_mean": round(statistics.fmean(r["wde"]), 5), **({"notes": r["notes"]} if r["notes"] else {})}
                     for r in rs],
        })
    return out


def svg_plot(rows: list[dict]) -> str:
    """WDE vs current density with the replicate sd, plain SVG."""
    w, h, left, right, top, bottom = 480, 320, 64, 16, 32, 48
    x0, x1, y0, y1 = 0.0, 275.0, 0.55, 1.0
    sx = lambda x: left + (x - x0) / (x1 - x0) * (w - left - right)  # noqa: E731
    sy = lambda y: h - bottom - (y - y0) / (y1 - y0) * (h - top - bottom)  # noqa: E731
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
             'font-family="Helvetica, Arial, sans-serif" font-size="11">',
             f'<rect width="{w}" height="{h}" fill="white"/>',
             f'<text x="{w / 2}" y="18" text-anchor="middle" font-size="12">Measured WDE, 1 M KOH, 90 mL, 1 h, 5 cm2 '
             '(from the 4TU raw titrations)</text>',
             f'<line x1="{left}" y1="{h - bottom}" x2="{w - right}" y2="{h - bottom}" stroke="black"/>',
             f'<line x1="{left}" y1="{top}" x2="{left}" y2="{h - bottom}" stroke="black"/>']
    for x in range(0, 276, 50):
        parts.append(f'<line x1="{sx(x):.1f}" y1="{h - bottom}" x2="{sx(x):.1f}" y2="{h - bottom + 4}" stroke="black"/>'
                     f'<text x="{sx(x):.1f}" y="{h - bottom + 16}" text-anchor="middle">{x}</text>')
    for k in range(0, 10):
        y = 0.55 + 0.05 * k
        parts.append(f'<line x1="{left - 4}" y1="{sy(y):.1f}" x2="{left}" y2="{sy(y):.1f}" stroke="black"/>'
                     f'<text x="{left - 6}" y="{sy(y) + 4:.1f}" text-anchor="end">{y:.2f}</text>')
    parts.append(f'<text x="{(left + w - right) / 2}" y="{h - 10}" text-anchor="middle">current density / mA cm-2</text>')
    parts.append(f'<text transform="translate(16 {(top + h - bottom) / 2}) rotate(-90)" text-anchor="middle">'
                 'water dissociation efficiency</text>')
    for r in rows:
        x, m, s = r["current_density"]["value"], r["wde"]["mean"], r["wde"]["sd"]
        parts.append(f'<line x1="{sx(x):.1f}" y1="{sy(m - s):.1f}" x2="{sx(x):.1f}" y2="{sy(m + s):.1f}" stroke="#1f5f99"/>'
                     f'<circle cx="{sx(x):.1f}" cy="{sy(m):.1f}" r="4" fill="#1f5f99"/>')
    parts.append(f'<text x="{w - right}" y="{h - bottom - 8}" text-anchor="end" fill="#555">mean and sd over all '
                 'titration pairs of three runs</text>')
    parts.append("</svg>")
    return "\n".join(parts) + "\n"


# -- the measured series: voltage, Faradaic efficiency and WDE per run (DESIGN.md D-005) -------

CP_DIR, MFM_DIR, GC_DIR = "CP-RawData/", "MFM-RawData/", "GC-RawData/"
MONTHS = {"Sep": 9, "Oct": 10, "Nov": 11, "Dec": 12, "Jan": 1, "Feb": 2}  # Sep 2024 to Feb 2025
WINDOW = (1800.0, 3600.0)  # s after the current start: the second half of the 1 h run (D-005)
MFM_AVERAGE = 30.0  # s of meter readings before each injection (SI Note 5)
INJECTION_STEP = 4.0  # sccm: a step of the meter reading this large marks a GC injection
GC_INTERVAL = (290.0, 345.0)  # s between two injections of the GC program
INJECTIONS = range(2, 14)  # injection 2 at the current start (GC ReadMe) to 13
# Conversion factors of the CO2-calibrated thermal mass-flow meter (SI Note 5, eq. 38-39):
# Q_gas = Q_MFM C_mix / C_CO2 with 1 / C_mix = sum_i c_i / C_i
CONVERSION = {"CO2": 0.74, "CO": 1.00, "H2": 1.01, "H2O": 0.79}
# K, Pa: the meter's sccm basis; P from SI eq. 37, T ASSUMED (the meter's is not stated; D-005)
T_STD, P_STD = 273.15, 101325.0
R_GAS = 8.314462618  # J/(mol K), CODATA 2018
P_SAT_25C = 3169.9  # Pa, water at 25 degC (IAPWS-95): 100 % RH at the ASSUMED 25 degC
X_H2O = P_SAT_25C / P_STD
CO2_INLET = 50.0  # sccm, humidified CO2 to the cathode (paper, Methods)
ELECTRONS = {"CO": 2, "H2": 2}
# dH of CO2 -> CO + 1/2 O2 and H2O(l) -> H2 + 1/2 O2 at 298.15 K, J/mol (process/reactions.yaml)
DH = {"CO": 282980.0, "H2": 285830.0}


def _date_of(month: str, day: str) -> str:
    m = MONTHS[month]
    return f"{2024 if m >= 9 else 2025}{m:02d}{day}"


def raw_index(names: list[str]) -> tuple[dict[tuple[str, int], dict[str, list[str]]], list[str]]:
    """The CP, MFM and GC files of the 1 M KOH runs by (date, j); and every other file whose
    name says 1 M KOH (a missing day, a misspelt electrolyte, the doubled 1 of a repeat file
    such as 11MKOH, as the dataset's 2MKOH/22MKOH/222MKOH) but gives no run key."""
    index: dict[tuple[str, int], dict[str, list[str]]] = {}
    odd = []
    for n in names:
        base = n.rsplit("/", 1)[-1]
        if n.startswith((CP_DIR, MFM_DIR)):
            m = re.fullmatch(r"([A-Z][a-z]{2})(\d{2})_(CP|MFM)_j(\d+)_1MKOH\.xlsx", base)
            kind = n.split("-", 1)[0]
            if m and n.startswith(f"{m.group(3)}-RawData/"):
                index.setdefault((_date_of(m.group(1), m.group(2)), int(m.group(4))), {}).setdefault(kind, []).append(n)
            elif re.search(r"_1+M?KOH\.xlsx$", base):
                odd.append(n)
        elif n.startswith(GC_DIR) and n.endswith(".xls"):
            m = re.match(r"(\d{8})_P0\d_rBPMJuly_1MKOH_j(\d+)_", base)
            if m:
                index.setdefault((m.group(1), int(m.group(2))), {}).setdefault("GC", []).append(n)
    return index, odd


def _numeric_rows(cells: dict, ncols: int) -> list[tuple[float, ...]]:
    rows = {}
    for (r, c), v in cells.items():
        rows.setdefault(r, {})[c] = v
    out = []
    for r in sorted(rows):
        vals = [rows[r].get(c) for c in range(ncols)]
        if all(isinstance(v, float) for v in vals):
            out.append(tuple(vals))
    return out


def chronopotentiometry(cells: dict) -> list[tuple[float, float, float]]:
    """(t s, U V, I A) per sample: columns voltage, current, time index (CP ReadMe)."""
    return [(t, u, i) for u, i, t in _numeric_rows(cells, 3)]


def mass_flow(cells: dict) -> list[tuple[float, float]]:
    """(t s from the first reading, sccm) per reading: columns time of day, outlet flow (MFM
    ReadMe). A record that runs past midnight keeps counting."""
    out, day, last = [], 0.0, None
    for frac, q in _numeric_rows(cells, 2):
        t = round((frac % 1.0) * 86400.0) + day
        if last is not None and t < last - 3600:
            day += 86400.0
            t += 86400.0
        last = t
        out.append((t, q))
    t0 = out[0][0]
    return [(t - t0, q) for t, q in out]


def injection_times(flow: list[tuple[float, float]], name: str) -> dict[int, float]:
    """The GC injections as the steps they leave in the meter reading (the sample drawn), each
    the first of its cluster: injection 2 (the current start) to 13, every 5.3 min."""
    steps = [t1 for (_, q0), (t1, q1) in itertools.pairwise(flow) if abs(q1 - q0) > INJECTION_STEP]
    starts: list[float] = steps[:1]
    for t in steps[1:]:  # the next step on the program's interval; others (a flow upset) are skipped
        if len(starts) == len(INJECTIONS):
            break
        if GC_INTERVAL[0] <= t - starts[-1] <= GC_INTERVAL[1]:
            starts.append(t)
    if len(starts) < len(INJECTIONS):
        raise SystemExit(f"{name}: the GC injections cannot be located in the meter record ({starts})")
    return dict(zip(INJECTIONS, starts, strict=True))


def gc_injections(cells: dict, name: str) -> tuple[dict[int, dict], str]:
    """Mole fractions of CO and H2 per injection, and the sheet's own FE column with the
    current and flow it was computed with (where the export has them)."""
    head = {c: [str(cells.get((r, c), "")).strip() for r in range(4)] for c in range(40) if (0, c) in cells}

    def col(label: str, product: str | None = None) -> int | None:
        for c, h in sorted(head.items()):
            if h[0] == label and (product is None or h[3] == product):
                return c
        return None

    h2, co = col("Amount", "HYDROGEN"), col("Amount", "CARBON MONOXIDE")
    layout = "amounts with FE columns"
    if h2 is None:
        h2, co, layout = col("Amount", "Hydrogen"), col("Amount", "Carbon monoxide"), "areas and amounts"
    if h2 is None or co is None:
        raise SystemExit(f"{name}: no H2 and CO amount columns")
    fe, cur, flow = col("GAS FE"), col("Current"), col("MFM Flowrate corr")
    out = {}
    r = 4
    def num(r: int, c: int | None) -> float | None:
        v = cells.get((r, c)) if c is not None else None
        return v if isinstance(v, float) else None  # "n.a.": not detected or not computed

    while isinstance(cells.get((r, 0)), float):
        out[int(cells[(r, 0)])] = {"CO": num(r, co), "H2": num(r, h2), "sheet_fe_co": num(r, fe),
                                   "sheet_current": num(r, cur), "sheet_flow": num(r, flow)}
        r += 1
    return out, layout


def mixture_flow(q_mfm: float, x: dict[str, float]) -> tuple[float, float]:
    """The outlet flow (sccm) from the CO2-calibrated reading, SI eq. 38-39, and the factor."""
    xs = {"CO": x["CO"], "H2": x["H2"], "H2O": X_H2O}
    xs["CO2"] = 1.0 - sum(xs.values())
    c_mix = 1.0 / sum(v / CONVERSION[k] for k, v in xs.items())
    factor = c_mix / CONVERSION["CO2"]
    return q_mfm * factor, factor


def faradaic(x: float, flow_sccm: float, electrons: int, current: float) -> float:
    return electrons * F * x * flow_sccm * 1e-6 / 60.0 * P_STD / (R_GAS * T_STD) / current


def measured_run(z: zipfile.ZipFile, tit: dict, files: dict[str, list[str]]) -> dict:
    """One run: the mean cell voltage, the outlet flow and fractions and the titration."""
    j = tit["j"]
    current = j * 1e-3 * AREA  # A, nominal (D-002, D-005)
    res = {"date": tit["date"], "j": j, "titration_file": f"{SHEETS}{tit['file']}", "notes": list(tit["notes"])}
    for kind in ("CP", "MFM", "GC"):
        if len(files.get(kind, [])) > 1:
            raise SystemExit(f"{tit['date']} j{j:g}: more than one {kind} file: {files[kind]}")
    # chronopotentiometry: the window mean, the sign turned to a positive cell voltage
    cp_name = files["CP"][0]
    cp = chronopotentiometry(rawsheets.read_sheet(cp_name, z.read(cp_name)))
    inside = [(u, i) for t, u, i in cp if WINDOW[0] < t <= WINDOW[1]]
    first = [u for t, u, _ in cp if t <= WINDOW[0]]
    res["cp_file"] = cp_name
    res["voltage"] = -statistics.fmean(u for u, _ in inside)
    res["voltage_sd"] = statistics.stdev(u for u, _ in inside)
    res["voltage_first_half"] = -statistics.fmean(first)
    res["current_measured"] = -statistics.fmean(i for _, i in inside)
    res["cp_samples"] = (len(cp), cp[-1][0])
    # titration: the means of the sheet's readings (WDE is linear in them, D-002)
    if tit["v_titrate"] != 1.0:
        raise SystemExit(f"{tit['file']}: sample volume {tit['v_titrate']} mL; the file states 1 mL for all")
    vol = tit["volumes"]
    res["titration"] = {"V0": statistics.fmean(vol["V0"]), "V1": statistics.fmean(vol["V1"]),
                        "V2": statistics.fmean(vol["V2"])}
    scale = C_HCL * 1e-3 * V_TANK_ML / 1.0
    wde = 1.0 - (res["titration"]["V0"] - res["titration"]["V1"]) * scale * F / (current * T_CP)
    if abs(wde - statistics.fmean(tit["wde"])) > 1e-12:
        raise SystemExit(f"{tit['file']}: WDE of the mean volumes {wde} differs from the mean over the pairs")
    res["wde"] = wde
    res["titration_counts"] = (len(vol["V0"]), len(vol["V1"]))
    # gas: injections inside the window, the meter's mean over 30 s before each
    if "GC" not in files or "MFM" not in files:
        res["gas"] = None
        res["missing"] = [k for k in ("MFM", "GC") if k not in files]
        if "GC" in files:
            res["gc_file"] = files["GC"][0]
        return res
    mfm_name, gc_name = files["MFM"][0], files["GC"][0]
    flow = mass_flow(rawsheets.read_sheet(mfm_name, z.read(mfm_name)))
    gc_cells = rawsheets.read_sheet(gc_name, z.read(gc_name))
    gc, layout = gc_injections(gc_cells, gc_name)
    when = injection_times(flow, mfm_name)
    zero = when[INJECTIONS[0]]
    rows = []
    for k, t in when.items():
        if not WINDOW[0] <= t - zero <= WINDOW[1]:
            continue
        g = gc.get(k)
        if g is None or g["CO"] is None or g["H2"] is None:
            raise SystemExit(f"{gc_name}: injection {k} inside the window has no CO or H2 amount")
        q = [v for s, v in flow if t - MFM_AVERAGE <= s < t]
        x = {"CO": g["CO"] * 1e-6, "H2": g["H2"] * 1e-6}  # ppm (GC ReadMe)
        q_mfm = statistics.fmean(q)
        q_gas, factor = mixture_flow(q_mfm, x)
        rows.append({"k": k, "t": t - zero, "x": x, "q_mfm": q_mfm, "q_gas": q_gas, "factor": factor,
                     "fe": {p: faradaic(x[p], q_gas, ELECTRONS[p], current) for p in x},
                     "sheet_fe_co": g["sheet_fe_co"], "sheet_current": g["sheet_current"],
                     "sheet_flow": g["sheet_flow"]})
    q_bar = statistics.fmean(r["q_gas"] for r in rows)
    res["gas"] = {
        "mfm_file": mfm_name, "gc_file": gc_name, "layout": layout,
        "injections": [r["k"] for r in rows],
        "outlet_flow": q_bar,
        "q_mfm": statistics.fmean(r["q_mfm"] for r in rows),
        # the reading before the current start (the humidified CO2 feed alone, D-005 irregularities)
        "q_baseline": statistics.fmean(v for s, v in flow if s < zero),
        "factor": statistics.fmean(r["factor"] for r in rows),
        # flow-weighted: FE from these fractions and q_bar is the mean of the injections' FE
        "fractions": {p: sum(r["x"][p] * r["q_gas"] for r in rows) / (q_bar * len(rows)) for p in ("CO", "H2")},
        "fe": {p: statistics.fmean(r["fe"][p] for r in rows) for p in ("CO", "H2")},
        "fe_injections": {p: [r["fe"][p] for r in rows] for p in ("CO", "H2")},
        "rows": rows,
    }
    # format with clock times: the meter steps against the GC's own injection times
    if layout == "areas and amounts":
        res["gas"]["clock_offsets"] = _clock_check(gc_cells, mfm_name, z, when)
    return res


def _clock_check(gc_cells: dict, mfm_name: str, z: zipfile.ZipFile, when: dict[int, float]) -> list[float]:
    """Seconds between each located injection and the GC's Inject Time (MFM clock)."""
    col = next(c for c in range(40) if str(gc_cells.get((0, c), "")).strip() == "Inject Time")
    cells = rawsheets.read_sheet(mfm_name, z.read(mfm_name))
    t0 = round((_numeric_rows(cells, 2)[0][0] % 1.0) * 86400.0)
    out = []
    r = 4
    while isinstance(gc_cells.get((r, 0)), float):
        k = int(gc_cells[(r, 0)])
        v = gc_cells.get((r, col))
        if k in when and isinstance(v, float):
            out.append(when[k] - (round((v % 1.0) * 86400.0) - t0))
        r += 1
    return out


def measured_series(zip_path: Path, tits: list[dict]) -> tuple[list[dict], list[str], list[str]]:
    """Every run of the titration study with its CP, MFM and GC files; the files left over."""
    with zipfile.ZipFile(zip_path) as z:
        index, odd = raw_index(z.namelist())
        runs, used = [], set()
        for tit in tits:
            files = index.get((tit["date"], int(tit["j"])), {})
            if "CP" not in files:
                raise SystemExit(f"{tit['file']}: no chronopotentiometry file of that run")
            used.update(n for v in files.values() for n in v)
            runs.append(measured_run(z, tit, files))
    unmatched = sorted(n for files in index.values() for names in files.values() for n in names if n not in used)
    unmatched += sorted(odd)
    missing = [f"{r['date']} j{r['j']:g}: no {', '.join(r['missing'])} file" for r in runs if r.get("missing")]
    return runs, unmatched, missing


def measurement_doc(runs: list[dict]) -> dict:
    """The file experiments/electrochemistry/rbpm-1m-koh.yaml (cheme/electrochemical-measurements/v1)."""
    paper = "Prats Vergel et al., Nat. Chem. Eng. (2025), https://doi.org/10.1038/s44286-025-00306-7"
    points = []
    for j in sorted({r["j"] for r in runs}):
        reps = []
        for r in (r for r in runs if r["j"] == j):
            rep: dict = {"id": f"R{r['date']}", "voltage": {"value": round(r["voltage"], 4)}}
            loc = [f"{r['cp_file']} (mean of t {WINDOW[0]:g}-{WINDOW[1]:g} s, sign turned)"]
            if r["gas"]:
                g = r["gas"]
                rep["outlet_flow"] = round(g["outlet_flow"], 3)
                rep["fractions"] = {p: {"value": round(g["fractions"][p] * 1e6, 1), "unit": "ppm"} for p in ("CO", "H2")}
                loc.append(f"{g['mfm_file']} (meter reading {g['q_mfm']:.2f} sccm as CO2, mixture factor "
                           f"{g['factor']:.4f}, 30 s before each injection; {g['q_baseline']:.2f} sccm before "
                           f"the current start)")
                loc.append(f"{g['gc_file']} (injections {g['injections'][0]}-{g['injections'][-1]}, flow-weighted)")
            else:
                loc.append("no MFM file of this run in the dataset: no Faradaic efficiency"
                           + (f" ({r['gc_file']} unused)" if r.get("gc_file") else ""))
            t = r["titration"]
            rep["titration"] = {"V0": round(t["V0"], 6), "V1": round(t["V1"], 6), "V2": round(t["V2"], 6)}
            n0, n12 = r["titration_counts"]
            loc.append(f"{r['titration_file']} (means of {n0} V0 and {n12} (V1, V2) readings"
                       + (f"; {'; '.join(r['notes'])}" if r["notes"] else "") + ")")
            rep["source"] = "; ".join(loc)
            reps.append(rep)
        points.append({"id": f"P{j:03.0f}", "current_density": {"value": j, "unit": "mA/cm2"},
                       "duration": {"value": T_CP, "unit": "s"}, "replicates": reps})
    lo, hi = min(r["j"] for r in runs), max(r["j"] for r in runs)
    return {
        "schema": "cheme/electrochemical-measurements/v1",
        "kind": "electrochemical_measurements",
        "id": "rbpm-1m-koh",
        "title": "Reverse-bias BPM CO2 electrolysis cell, 1 M KOH anolyte, 25-250 mA/cm2",
        "provenance": "given",
        "origin": "measured",
        "source": (f"Prats Vergel, Mu, Kolobov, Biemolt, Vermaas, Burdyny, 4TU.ResearchData (2025), "
                   f"https://doi.org/{DOI}, {RAW['name']} (sha256 {RAW['sha256'][:12]}...); processed by "
                   f"scripts/adapt_4tu.py (DESIGN.md D-002, D-005); method: {paper}, Methods and SI Note 5"),
        "licence": "CC BY 4.0 (NOTICE.md)",
        "cell": {
            "active_area": {"value": AREA, "unit": "cm2", "source": f"{paper}, Methods"},
            "temperature": {"value": 25, "unit": "°C",
                            "source": "ASSUMED: room temperature; the paper and the dataset state none (DESIGN.md D-005)"},
            "electrolyte": {"name": "1 M KOH", "concentration": {"value": 1, "unit": "mol/L"}},
            "membrane": {"kind": "bipolar", "bias": "reverse", "name": "Fumasep FBM"},
        },
        "voltage_basis": "cell",
        "products": [
            {"id": p, "electrons": ELECTRONS[p], "electrode": "cathode", "reaction": rx,
             "thermoneutral_voltage": {"value": round(DH[p] / (ELECTRONS[p] * F), 5), "unit": "V",
                                       "source": f"dH / (2 F), dH of {rx} in process/reactions.yaml (CODATA)"}}
            for p, rx in (("CO", "CO2R"), ("H2", "WS"))
        ],
        "gas": {
            "flow_unit": "sccm",
            "standard_conditions": {
                "temperature": {"value": T_STD, "unit": "K",
                                "source": ("ASSUMED: 0 degC; the meter's reference temperature is not stated, and "
                                           "the only hint is the 22.4 L/mol of the authors' FE column, which D-005 "
                                           "rejects as a template; every FE scales with 1 / T: at 20 degC it would "
                                           "be 6.8 % lower, at 25 degC 8.4 % (DESIGN.md D-005)")},
                "pressure": {"value": P_STD / 1000, "unit": "kPa", "source": "SI Note 5, eq. 37: P = 101325 Pa"},
            },
            "flow_position": "outlet",
            "flow_correction": {
                "factor": 1.0,
                "source": ("outlet_flow is already the mixture flow: the CO2-calibrated meter reading times "
                           "C_mix / C_CO2 per replicate (SI Note 5, eq. 38-39; C_CO2 0.74, C_CO 1.00, C_H2 1.01, "
                           "C_H2O 0.79; 100 % RH at the ASSUMED 25 degC); the readings are in each source"),
            },
            "inlet": {"component": "CO2", "flow": CO2_INLET},
        },
        "titration": {
            "method": "warder-double-endpoint",
            "titrant_concentration": {"value": C_HCL, "unit": "mol/L"},
            "anolyte_volume": {"value": V_TANK_ML, "unit": "mL"},
            "aliquot_volume": {"value": 1.0, "unit": "mL"},
            "source": f"{paper}, Methods (eq. 3-10); DESIGN.md D-002",
        },
        "points": points,
        "validity": {
            "current_density": [lo * 10.0, hi * 10.0],
            "electrolyte": "1 M KOH",
            "duration": T_CP,
            "source": "the measured points: 1 h runs at 25-250 mA/cm2, three per current density",
        },
    }


def report_runs(runs: list[dict]) -> None:
    print("runs (window means):")
    for r in runs:
        g = r["gas"]
        gas = (f"Q {g['q_baseline']:.2f} before the current, {g['q_mfm']:.2f}->{g['outlet_flow']:.2f} sccm FE CO {g['fe']['CO']:.4f} H2 {g['fe']['H2']:.4f} "
               f"sum {g['fe']['CO'] + g['fe']['H2']:.4f}") if g else "no gas data"
        print(f"  {r['date']} j{r['j']:3.0f}: U {r['voltage']:.3f} V (sd {r['voltage_sd']:.3f}, first half "
              f"{r['voltage_first_half']:.3f}), I {r['current_measured']:.4f} A, WDE {r['wde']:.5f}; {gas}")
        if g and g.get("clock_offsets"):
            print(f"      meter steps vs GC inject times: {min(g['clock_offsets']):+.0f} to {max(g['clock_offsets']):+.0f} s")
    print("the GC sheets' own FE column (layout with FE columns):")
    for r in runs:
        g = r["gas"]
        if not g or g["layout"] != "amounts with FE columns":
            continue
        rows = g["rows"]
        vm = [2 * F * x["x"]["CO"] * x["sheet_flow"] * 1e-3 / 60 / (x["sheet_current"] * x["sheet_fe_co"] / 100)
              for x in rows if x["sheet_fe_co"]]
        print(f"  {r['date']} j{r['j']:3.0f}: sheet FE CO {statistics.fmean(x['sheet_fe_co'] for x in rows):6.2f} % "
              f"with I {rows[0]['sheet_current']} A, Q {rows[0]['sheet_flow']} sccm (implied molar volume "
              f"{min(vm):.3f}-{max(vm):.3f} L/mol); run current {r['j'] * AREA / 1000:.3f} A, ours "
              f"{100 * g['fe']['CO']:.2f} %")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--cache", type=Path, default=Path.home() / ".cache/cheme-as-code/4tu/5c4fc325-v1")
    args = ap.parse_args()
    raw = fetch(args.cache)
    tits = titration_runs(raw)
    rows = series(tits)
    doc = {
        "source": {
            "dataset": f"https://doi.org/{DOI}",
            "file": RAW["name"],
            "sha256": RAW["sha256"],
            "sheets": f"{RAW['name']}/{SHEETS}*.docx",
            "licence": "CC BY 4.0 (NOTICE.md)",
            "paper": "https://doi.org/10.1038/s44286-025-00306-7",
        },
        "method": ("paper Methods eq. 3-10: K+ lost = (V0 - V2) c_HCl V_tank / V_titrate, carbon gained = "
                   "(V2 - V1) c_HCl V_tank / V_titrate, WDE = 1 - F (n_K + n_C) / (j A t_CP); every V0 with "
                   "every (V1, V2) pair of a sheet, pooled over the runs at one current density (DESIGN.md D-002)"),
        "constants": {"c_HCl": "0.1 mol/L", "V_tank": "90 mL", "t_CP": "3600 s", "A": "5 cm2", "F": "96485.33212 C/mol"},
        "conditions": {"anolyte": "1 M KOH, recirculated", "cell": "process/design-basis.yaml capacity.reference_cell"},
        "validity": {"current_density": {"min": 25, "max": 250, "unit": "mA/cm2"}, "anolyte": "1 M KOH",
                     "duration": "1 h runs", "note": "no measurement outside this range; use beyond it is extrapolation"},
        "series": rows,
    }
    out = ROOT / "data" / "measured" / "wde-1m-koh.yaml"
    out.parent.mkdir(parents=True, exist_ok=True)
    header = ("# Measured water dissociation efficiency (WDE) of the reverse-bias BPM cell, 1 M KOH.\n"
              "# GENERATED by scripts/adapt_4tu.py from the pinned 4TU raw data; do not edit by hand.\n")
    out.write_text(header + yaml.safe_dump(doc, sort_keys=False, width=100, allow_unicode=True))
    fig = ROOT / "figures" / "wde-1m-koh.svg"
    fig.parent.mkdir(exist_ok=True)
    fig.write_text(svg_plot(rows))
    print(f"wrote {out.relative_to(ROOT)} and {fig.relative_to(ROOT)}")
    for r in rows:
        print(f"  j {r['current_density']['value']:5.0f} mA/cm2: WDE {r['wde']['mean']:.4f} +/- {r['wde']['sd']:.4f}"
              f" ({r['wde']['n_pairs']} pairs), carbon fraction {r['coion_carbon_fraction']['value']}")
    # the measured series of the cell: voltage, Faradaic efficiency and WDE per run (D-005)
    runs, unmatched, missing = measured_series(raw, tits)
    exp = ROOT / "experiments" / "electrochemistry" / "rbpm-1m-koh.yaml"
    exp.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Measured series of the reverse-bias BPM cell, 1 M KOH: cell voltage, outlet gas and anolyte",
        "# titration of every run of the current-density study (DESIGN.md D-005).",
        "# GENERATED by scripts/adapt_4tu.py from the pinned 4TU raw data; do not edit by hand.",
        "# Schema cheme/electrochemical-measurements/v1: `cheme experiments electrochem` processes it.",
        "# A run is the titration sheet of TitrationToWDE/CurrentDensity with the CP, MFM and GC files",
        "# of the same date and current density.",
        "# Runs without a file:",
        *[f"#   {m}" for m in missing],
        "# 1 M KOH raw files of no run of the study (other dates or current densities, or a name",
        "# without a day or with another electrolyte spelling), not used:",
        *[f"#   {n}" for n in unmatched],
    ]
    exp.write_text("\n".join(lines) + "\n" + yaml.safe_dump(measurement_doc(runs), sort_keys=False, width=100,
                                                            allow_unicode=True))
    print(f"wrote {exp.relative_to(ROOT)}")
    report_runs(runs)
    print("runs without a file:", missing)
    print(f"unmatched 1 M KOH files ({len(unmatched)}):", [n.rsplit('/', 1)[-1] for n in unmatched])


if __name__ == "__main__":
    main()
