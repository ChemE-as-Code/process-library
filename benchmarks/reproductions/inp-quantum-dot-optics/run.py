# /// script
# requires-python = ">=3.12,<3.14"
# dependencies = [
#     "numpy==2.3.4",
#     "scipy==1.16.3",
#     "matplotlib==3.10.7",
#     "pyyaml==6.0.3",
# ]
# [tool.uv]
# exclude-newer = "2026-11-04T00:00:00Z"
# ///
"""InP quantum-dot treatment and optical quality: reproduction and screen (#342, tracker #333).

Rerun from the repository root:

    uv run benchmarks/reproductions/inp-quantum-dot-optics/run.py

Reads source.yaml, inputs.yaml, tolerances.yaml and mapping.csv next to this file. Fetches the
pinned members of the 4TU archive by HTTP range requests into a cache outside git
($XDG_CACHE_HOME or ~/.cache, subfolder cheme-reproductions/inp-quantum-dot-optics/), checks
CRC-32 and sha256 of each, and never executes downloaded content. Writes results/ (JSON, CSV,
SVG) deterministically: comparison.json (checks, verdict, aggregates), details.json and
sample_metrics.csv (per-sample values) and fig_*.svg, all committed (results/NOTICE.md), and
local/ (a plot of the processed spectra; git-ignored). Exits non-zero when the script fails,
not when a check fails; the verdict
is in results/comparison.json.

Option --verify-archive streams the whole 3.47 GB archive once and checks its pinned sha256
(nothing is stored).
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import math
import os
import platform
import sys
import time
import urllib.error
import urllib.request
import zipfile
from pathlib import Path

import matplotlib
import numpy as np
import scipy
import yaml
from scipy.optimize import curve_fit
from scipy.signal import find_peaks, savgol_filter

matplotlib.use("svg")
import matplotlib.pyplot as plt  # noqa: E402

HERE = Path(__file__).resolve().parent
RESULTS = HERE / "results"
CASE_ID = "inp-quantum-dot-optics"
HC_EV_NM = 1239.842
USER_AGENT = "cheme-process-library-reproduction/1.0 (+https://github.com/ChemE-as-Code/process-library)"


# --------------------------------------------------------------------------- data access
def cache_dir() -> Path:
    base = os.environ.get("XDG_CACHE_HOME") or str(Path.home() / ".cache")
    d = Path(base) / "cheme-reproductions" / CASE_ID
    d.mkdir(parents=True, exist_ok=True)
    return d


def http_range(url: str, start: int, end: int, total: int) -> bytes:
    last = None
    for attempt in range(5):
        try:
            req = urllib.request.Request(url, headers={"Range": f"bytes={start}-{end}", "User-Agent": USER_AGENT})
            with urllib.request.urlopen(req, timeout=120) as r:
                if r.status != 206:
                    raise RuntimeError(f"server did not honour the range request (HTTP {r.status})")
                cr = r.headers.get("Content-Range", "")
                if not cr.endswith(f"/{total}"):
                    raise RuntimeError(f"archive size differs from the pinned size: Content-Range {cr!r}")
                data = r.read()
            if len(data) != end - start + 1:
                raise RuntimeError("short range read")
            return data
        except (urllib.error.URLError, TimeoutError, ConnectionError, RuntimeError) as e:
            last = e
            if isinstance(e, RuntimeError) and "pinned size" in str(e):
                raise
            time.sleep(2 * (attempt + 1))
    raise RuntimeError(f"range request failed after retries: {last}")


class RangeFile:
    """Read-only, seekable view of a remote file through HTTP range requests (1 MiB blocks)."""

    BLOCK = 1 << 20

    def __init__(self, url: str, size: int):
        self.url, self.size, self.pos, self.blocks = url, size, 0, {}

    def seekable(self):
        return True

    def tell(self):
        return self.pos

    def seek(self, offset, whence=0):
        self.pos = offset if whence == 0 else (self.pos + offset if whence == 1 else self.size + offset)
        return self.pos

    def _block(self, i):
        if i not in self.blocks:
            a = i * self.BLOCK
            self.blocks[i] = http_range(self.url, a, min(self.size, a + self.BLOCK) - 1, self.size)
        return self.blocks[i]

    def read(self, n=-1):
        if n is None or n < 0:
            n = self.size - self.pos
        n = max(0, min(n, self.size - self.pos))
        out = bytearray()
        while n > 0:
            i, off = divmod(self.pos, self.BLOCK)
            chunk = self._block(i)[off : off + n]
            out += chunk
            self.pos += len(chunk)
            n -= len(chunk)
        return bytes(out)


def fetch_members(src: dict) -> dict[str, bytes]:
    """Return {member path: bytes} for every pinned member, verified by sha256."""
    arch = next(f for f in src["dataset"]["files"] if f["name"].endswith(".zip"))
    root_prefix = arch["archive_root"]
    mdir = (cache_dir() / "members").resolve()
    out, missing = {}, []
    for m in src["dataset"]["members"]:
        p = (mdir / m["path"]).resolve()
        if mdir not in p.parents:
            raise RuntimeError(f"unsafe member path {m['path']!r}")
        if p.is_file():
            b = p.read_bytes()
            if hashlib.sha256(b).hexdigest() == m["sha256"]:
                out[m["path"]] = b
                continue
        missing.append((m, p))
    if missing:
        print(f"fetching {len(missing)} archive members by range request from {arch['url']}", file=sys.stderr)
        z = zipfile.ZipFile(RangeFile(arch["url"], int(arch["size"])))
        for m, p in missing:
            info = z.getinfo(root_prefix + m["path"])
            if f"{info.CRC:08x}" != m["crc32"] or info.file_size != m["size"]:
                raise RuntimeError(f"archive entry differs from the pin: {m['path']}")
            b = z.read(info)  # zipfile checks CRC-32 while reading
            if hashlib.sha256(b).hexdigest() != m["sha256"]:
                raise RuntimeError(f"sha256 mismatch for {m['path']}")
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_bytes(b)
            out[m["path"]] = b
    return out


def verify_archive(src: dict) -> None:
    arch = next(f for f in src["dataset"]["files"] if f["name"].endswith(".zip"))
    h, n = hashlib.sha256(), 0
    req = urllib.request.Request(arch["url"], headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=300) as r:
        while chunk := r.read(1 << 22):
            h.update(chunk)
            n += len(chunk)
    ok = h.hexdigest() == arch["sha256"] and n == int(arch["size"])
    print(f"archive: {n} bytes, sha256 {h.hexdigest()} -> {'matches pin' if ok else 'DOES NOT MATCH pin'}")
    if not ok:
        raise SystemExit(2)


# --------------------------------------------------------------------------- parsing
def _num(s: str):
    try:
        return float(s)
    except ValueError:
        return None


def parse_absorbance(b: bytes) -> dict:
    lines = b.decode("latin-1").splitlines()
    if not lines or not lines[0].startswith("PE UV"):
        raise ValueError("not a PerkinElmer ASCII absorbance file")
    i = lines.index("#DATA")
    d = np.array([[float(v) for v in ln.split()[:2]] for ln in lines[i + 1 :] if ln.strip()])
    d = d[np.argsort(d[:, 0])]
    yy, mm, dd = lines[3].strip().split("/")
    return {"internal_name": lines[2].strip(), "date": f"20{yy}-{mm}-{dd}", "time": lines[4].strip()[:8], "x": d[:, 0], "y": d[:, 1]}


def parse_fls(b: bytes) -> dict:
    """Edinburgh FLS980 export (tab or comma separated): header {key: [values]}, data columns."""
    header, rows = {}, []
    for ln in b.decode("latin-1").splitlines():
        sep = "\t" if "\t" in ln else ","
        tok = [t.strip() for t in ln.split(sep)]
        while tok and tok[-1] == "":
            tok.pop()
        if not tok:
            continue
        nums = [_num(t) for t in tok]
        if nums[0] is not None and len(nums) >= 2 and all(v is not None for v in nums):
            rows.append(nums)
        elif not rows:
            header[tok[0]] = tok[1:]
    d = np.array(rows)
    return {"header": header, "x": d[:, 0], "cols": d[:, 1:]}


SETTING_KEYS = ["Start", "Stop", "Step", "Fixed/Offset", "Scan Slit", "Fixed/Offset Slit", "Dwell Time", "Repeats", "Scan Corr. by File", "Fixed/Offset Corr. by File", "Detector"]


def pl_settings(h: dict) -> dict:
    return {k: (h.get(k) or [""])[0] for k in SETTING_KEYS}


# --------------------------------------------------------------------------- processing
def process_absorbance(a: dict, inp: dict) -> dict:
    ap = inp["absorbance_processing"]
    x, y = a["x"], a["y"]
    lo, hi = ap["baseline_window"]["value"]
    base = float(y[(x >= lo) & (x <= hi)].mean())
    yc = y - base
    lam_ex = ap["excitation_wavelength"]["value"]
    A_ex = float(np.interp(lam_ex, x, yc))
    ys = savgol_filter(yc, 21, 3)
    w0, w1 = ap["peak_window"]["value"]
    win = (x >= w0) & (x <= w1)
    xi, yi = x[win], ys[win]
    pk, _ = find_peaks(yi)
    if len(pk):
        j = pk[np.argmax(yi[pk])]
        peak, method = float(xi[j]), "local maximum"
        # sub-nm refinement by a parabola through the three points around the maximum
        if 0 < j < len(xi) - 1:
            y0, y1, y2 = yi[j - 1], yi[j], yi[j + 1]
            den = y0 - 2 * y1 + y2
            if den != 0:
                peak = float(xi[j] + 0.5 * (y0 - y2) / den * (xi[1] - xi[0]))
    else:
        d2 = savgol_filter(yc, 21, 3, deriv=2)[win]
        j = int(np.argmin(d2))
        peak, method = float(xi[j]), "second-derivative minimum"
    A_peak = float(np.interp(peak, x, ys))
    vwin = (x >= peak - 60) & (x <= peak)
    jv = int(np.argmin(ys[vwin]))
    A_valley = float(ys[vwin][jv])
    ptv = A_peak / A_valley if (method == "local maximum" and A_valley > 0 and float(x[vwin][jv]) < peak - 2) else None
    return {
        "baseline_od": base, "A_ex": A_ex, "A_ex_raw": float(np.interp(lam_ex, x, y)), "f_ex": 1 - 10 ** (-A_ex), "abs_peak_nm": peak, "abs_peak_method": method,
        "peak_to_valley": ptv, "A330": float(np.interp(330, x, yc)), "A450": float(np.interp(450, x, yc)),
        "A540": float(np.interp(540, x, yc)), "date": a["date"], "time": a["time"], "internal_name": a["internal_name"],
    }


def half_crossings(x, y, j, half):
    """Walk outward from index j; return interpolated x at the first points below half, or None."""
    left = right = None
    for k in range(j, 0, -1):
        if y[k - 1] < half <= y[k]:
            left = x[k - 1] + (half - y[k - 1]) / (y[k] - y[k - 1]) * (x[k] - x[k - 1])
            break
    for k in range(j, len(y) - 1):
        if y[k + 1] < half <= y[k]:
            right = x[k] + (y[k] - half) / (y[k] - y[k + 1]) * (x[k + 1] - x[k])
            break
    return left, right


def process_pl(p: dict, inp: dict, col: int = 0) -> dict:
    pp = inp["pl_processing"]
    x, y = p["x"], p["cols"][:, col]
    integral = float(np.trapezoid(y, x))
    bmask = x <= x[0] + 4.0
    base = float(y[bmask].mean())
    integral_base = float(np.trapezoid(y - base, x))
    ys = savgol_filter(y, 11, 3)
    w0, w1 = pp["peak_window"]["value"]
    win = np.where((x >= w0) & (x <= w1))[0]
    j = int(win[np.argmax(ys[win])])
    peak_nm, peak_val = float(x[j]), float(ys[j])
    at_edge = j in (int(win[0]), int(win[-1]))
    trap_dominated = bool(ys.max() > peak_val and x[int(np.argmax(ys))] > w1)
    l, r = half_crossings(x, ys, j, peak_val / 2)
    fwhm_nm = (r - l) if (l is not None and r is not None) else None
    IE = ys * x**2  # proportional to I(E); constant factor irrelevant
    jE = int(win[np.argmax(IE[win])])
    lE, rE = half_crossings(x, IE, jE, IE[jE] / 2)
    fwhm_meV = 1000 * (HC_EV_NM / lE - HC_EV_NM / rE) if (lE is not None and rE is not None) else None
    if at_edge:  # no band-edge maximum inside the window (trap-dominated): width not defined
        fwhm_nm = fwhm_meV = None
    return {
        "pl_integral": integral, "pl_integral_baseline": integral_base, "pl_peak_nm": None if at_edge else peak_nm,
        "pl_peak_eV": HC_EV_NM / float(x[jE]), "pl_fwhm_nm": fwhm_nm, "pl_fwhm_meV": fwhm_meV,
        "trap_dominated": trap_dominated, "range_nm": [float(x[0]), float(x[-1])], "settings": pl_settings(p["header"]),
    }


def plqy(s_abs, s_pl, r_abs, r_pl, inp, n_s=None, use_n=True, use_absorptance=True, baseline=False, abs_baseline=True):
    q = inp["plqy"]
    n_s = q["n_sample"]["value"] if n_s is None else n_s
    n_r = q["n_ref"]["value"]
    Fs = s_pl["pl_integral_baseline"] if baseline else s_pl["pl_integral"]
    Fr = r_pl["pl_integral_baseline"] if baseline else r_pl["pl_integral"]
    As, Ar = (s_abs["A_ex"], r_abs["A_ex"]) if abs_baseline else (s_abs["A_ex_raw"], r_abs["A_ex_raw"])
    fs = 1 - 10 ** (-As) if use_absorptance else As
    fr = 1 - 10 ** (-Ar) if use_absorptance else Ar
    return 100 * q["qy_ref"]["value"] * (Fs / Fr) * (fr / fs) * ((n_s / n_r) ** 2 if use_n else 1.0)


def biexp(t, a1, t1, a2, t2):
    return a1 * np.exp(-t / t1) + a2 * np.exp(-t / t2)


def process_decay(p: dict, inp: dict) -> dict:
    t, y = p["x"], p["cols"][:, 0]
    j = int(np.argmax(y))
    tt, yy = t[j:] - t[j], y[j:]
    m = yy > 0
    tt, yy = tt[m], yy[m]
    sv = inp["decay"]["start_values"]["value"]
    p0 = [yy[0] * 0.5, sv["t1"], yy[0] * 0.5, sv["t2"]]
    popt, _ = curve_fit(biexp, tt, yy, p0=p0, sigma=np.sqrt(np.maximum(yy, 1)), bounds=([0, 0.1, 0, 0.1], [np.inf, 5e3, np.inf, 5e3]), maxfev=20000)
    a1, t1, a2, t2 = popt
    tau = (a1 * t1**2 + a2 * t2**2) / (a1 * t1 + a2 * t2)
    res = (yy - biexp(tt, *popt)) / np.sqrt(np.maximum(yy, 1))
    (as_, ts), (al, tl) = sorted([(a1, t1), (a2, t2)], key=lambda c: c[1])
    return {"tau_avg_ns": float(tau), "A_short": float(as_), "tau_short_ns": float(ts), "A_long": float(al),
            "tau_long_ns": float(tl), "chi2_red": float((res**2).sum() / (len(yy) - 4)), "n_points": int(len(yy)),
            "record_end_ns": float(t[-1]), "peak_counts": float(y[j])}


def process_sphere(p: dict, inp: dict) -> dict:
    sp = inp["sphere"]
    x = p["x"]
    s0, s1 = sp["scatter_window"]["value"]
    e0, e1 = sp["emission_window"]["value"]
    ms, me = (x >= s0) & (x <= s1), (x >= e0) & (x <= e1)
    S = [float(np.trapezoid(p["cols"][ms, k], x[ms])) for k in range(2)]
    E = [float(np.trapezoid(p["cols"][me, k], x[me])) for k in range(2)]
    b = int(np.argmax(S))
    s = 1 - b
    labels = p["header"].get("Labels", ["?", "?"])
    return {"plqy_sphere_pct": 100 * (E[s] - E[b]) / (S[b] - S[s]), "blank_scan": labels[b], "sample_scan": labels[s],
            "absorbed_fraction": (S[b] - S[s]) / S[b]}


# --------------------------------------------------------------------------- helpers
def rnd(v, sig=6):
    if isinstance(v, float):
        if not math.isfinite(v):
            return None
        return float(f"{v:.{sig}g}")
    if isinstance(v, dict):
        return {k: rnd(w, sig) for k, w in v.items()}
    if isinstance(v, (list, tuple)):
        return [rnd(w, sig) for w in v]
    if isinstance(v, (np.floating,)):
        return rnd(float(v), sig)
    if isinstance(v, (np.integer,)):
        return int(v)
    if isinstance(v, np.bool_):
        return bool(v)
    return v


def band(reported: float, tol: dict) -> float:
    return max(tol["abs_pp"], tol["rel"] * reported)


# --------------------------------------------------------------------------- main
def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--verify-archive", action="store_true", help="stream the full archive and check its pinned sha256")
    args = ap.parse_args()

    src = yaml.safe_load((HERE / "source.yaml").read_text())
    inp = yaml.safe_load((HERE / "inputs.yaml").read_text())
    tol = yaml.safe_load((HERE / "tolerances.yaml").read_text())
    rows = list(csv.DictReader((HERE / "mapping.csv").open(newline="", encoding="utf-8")))
    if args.verify_archive:
        verify_archive(src)

    files = fetch_members(src)
    sha = {k: hashlib.sha256(v).hexdigest() for k, v in files.items()}
    rep = src["reported_results"]
    by_id = {r["id"]: r for r in rows}

    # ---- per-row processing
    metrics: dict[str, dict] = {}
    for r in rows:
        m: dict = {"id": r["id"], "kind": r["kind"], "flags_mapping": r["flags"]}
        if r["abs_member"]:
            a = parse_absorbance(files[r["abs_member"]])
            m["abs"] = process_absorbance(a, inp)
            m["abs"]["internal_name_matches_mapping"] = a["internal_name"] == r["abs_internal_name"]
        if r["pl_member"] and r["kind"] in ("sample", "reference"):
            m["pl"] = process_pl(parse_fls(files[r["pl_member"]]), inp)
        if r["kind"] == "decay":
            m["decay"] = process_decay(parse_fls(files[r["pl_member"]]), inp)
        if r["kind"] == "sphere":
            m["sphere"] = process_sphere(parse_fls(files[r["pl_member"]]), inp)
        metrics[r["id"]] = m

    # identical files across rows
    for r in rows:
        same = [o["id"] for o in rows if o["id"] != r["id"] and o["abs_member"] and r["abs_member"]
                and sha[o["abs_member"]] == sha[r["abs_member"]]]
        if same:
            metrics[r["id"]]["identical_abs_file_as"] = same

    od_t = inp["quality_screen"]["od387_target"]
    for r in rows:
        if r["kind"] != "sample" or "pl" not in metrics[r["id"]]:
            continue
        m = metrics[r["id"]]
        flags = []
        A = m["abs"]["A_ex"]
        if abs(A - od_t["value"]) > od_t["tolerance"]:
            flags.append(f"OD at 387 nm {A:.3f} outside {od_t['value']}+-{od_t['tolerance']}")
        if abs(m["abs"]["baseline_od"]) > 0.02:
            flags.append(f"absorbance baseline offset {m['abs']['baseline_od']:.3f} (scatter or drift)")
        if m["pl"]["trap_dominated"]:
            flags.append("emission maximum is trap emission above the band-edge window")
        if not r["ref_id"]:
            flags.append("no reference: PLQY not computable")
            m["confounder_flags"] = flags
            continue
        ref = metrics[r["ref_id"]]
        diff = {k: (m["pl"]["settings"][k], ref["pl"]["settings"][k]) for k in SETTING_KEYS
                if m["pl"]["settings"][k] != ref["pl"]["settings"][k]}
        if diff:
            flags.append("instrument settings differ from reference: " + "; ".join(f"{k} {a} vs {b}" for k, (a, b) in diff.items()))
        if m["abs"]["date"] != ref["abs"]["date"]:
            flags.append(f"reference recorded on another day ({ref['abs']['date']})")
        args_ = (m["abs"], m["pl"], ref["abs"], ref["pl"], inp)
        m["plqy_pct"] = plqy(*args_)
        m["plqy_sensitivity_pct"] = {
            "no_refractive_index_correction": plqy(*args_, use_n=False),
            "absorbance_instead_of_absorptance": plqy(*args_, use_absorptance=False),
            "constant_pl_baseline": plqy(*args_, baseline=True),
            "n_sample_hexadecane_1.434": plqy(*args_, n_s=1.434),
            # post hoc: added after the first comparison run to explain the 2022 deviations; not judged
            "posthoc_no_absorbance_baseline": plqy(*args_, abs_baseline=False),
        }
        m["session"] = m["abs"]["date"]
        m["confounder_flags"] = flags

    # ---- checks
    def val(sample, metric):
        m = metrics[sample]
        if metric == "plqy_pct":
            return m.get("plqy_pct")
        if metric == "abs_peak_nm":
            return m["abs"]["abs_peak_nm"]
        if metric in ("pl_fwhm_nm", "pl_fwhm_meV"):
            return m["pl"][metric]
        if metric == "tau_avg_ns":
            return m["decay"]["tau_avg_ns"]
        if metric == "plqy_sphere_pct":
            return m["sphere"]["plqy_sphere_pct"]
        raise KeyError(metric)

    results = {}
    for cid, c in tol["checks"].items():
        R = rep[c["reported"]]
        t = c["tol"]
        out = {"reported_key": c["reported"], "reported": R.get("value"), "reported_type": R["type"], "unit": R.get("unit"), "tolerance": t}
        try:
            if cid == "S3":
                a, b = val("F1-150-60", "abs_peak_nm"), val("F1-150-05", "abs_peak_nm")
                out.update(ours=a - b, samples=["F1-150-05", "F1-150-60"], status="pass" if a - b >= 1 else "fail")
            elif "samples" in c:
                vs = {s: val(s, c["metric"]) for s in c["samples"]}
                out["ours_by_sample"] = vs
                if any(v is None for v in vs.values()):
                    out["status"] = "not evaluable"
                elif t == "every value < 5":
                    out.update(ours=max(vs.values()), status="pass" if all(v < 5 for v in vs.values()) else "fail")
                elif t == "max value > 70":
                    out.update(ours=max(vs.values()), status="pass" if max(vs.values()) > 70 else "fail")
                elif t == "max value within plqy_band":
                    mx = max(vs.values())
                    bw = band(R["value"], tol["plqy_band"])
                    out.update(ours=mx, deviation=mx - R["value"], allowed=bw, status="pass" if abs(mx - R["value"]) <= bw else "fail")
                else:
                    raise ValueError(f"unknown tolerance form {t!r}")
            else:
                v = val(c["sample"], c["metric"])
                out["sample"] = c["sample"]
                out["ours"] = v
                if v is None:
                    out["status"] = "not evaluable"
                elif t == "plqy_band":
                    bw = band(R["value"], tol["plqy_band"])
                    out.update(deviation=v - R["value"], allowed=bw, status="pass" if abs(v - R["value"]) <= bw else "fail")
                elif t == "value < 0.2":
                    out["status"] = "pass" if v < 0.2 else "fail"
                elif isinstance(t, dict) and "abs" in t:
                    out.update(deviation=v - R["value"], allowed=t["abs"], status="pass" if abs(v - R["value"]) <= t["abs"] else "fail")
                elif isinstance(t, dict) and "rel" in t:
                    d = (v - R["value"]) / R["value"]
                    out.update(deviation_rel=d, allowed=t["rel"], status="pass" if abs(d) <= t["rel"] else "fail")
                else:
                    raise ValueError(f"unknown tolerance form {t!r}")
        except (KeyError, TypeError) as e:
            out["status"] = "not evaluable"
            out["error"] = str(e)
        out["group"] = "primary" if cid.startswith("P") else ("pair" if cid.startswith("X") else "secondary")
        results[cid] = out

    pair = [results["X1"]["status"], results["X2"]["status"]]
    pair_pass = pair.count("pass") == 1
    prim_pass = all(results[k]["status"] == "pass" for k in results if k.startswith("P"))
    sec_pass = all(results[k]["status"] == "pass" for k in results if k.startswith("S"))
    verdict = "pass" if (prim_pass and pair_pass and sec_pass) else ("partial" if prim_pass else "fail")
    n_units = sum(k[0] in "PS" for k in results) + 1
    n_pass = sum(results[k]["status"] == "pass" for k in results if k[0] in "PS") + int(pair_pass)

    # ---- diagnostics (not judged)
    def q(i):
        return metrics[i].get("plqy_pct")

    diagnostics = {
        "octylamine_vs_control_180min": {"control": q("S5-CTRL-180"), "octylamine": q("S5-AMINE-180")},
        "hcl_hbr_vs_hf_180min": {"HF700": q("S7-HF700-180"), "HCl700": q("S7-HCL700-180"), "HBr700": q("S7-HBR700-180"), "control": q("S8-CTRL-180")},
        "organic_acids_minus_control_pp": {k: q(k) - q("S8-CTRL-180") for k in ["S8-ACETIC-180", "S8-HEXANOIC-180", "S8-PALMITIC-180", "S8-HDA-180"]},
        "et3n": {"HF1400_60": q("S16-HF1400-60"), "HF1400_Et3N_60": q("S16-HF1400-ET3N-60"),
                 "A330_HF1400_60": metrics["S16-HF1400-60"]["abs"]["A330"], "A330_Et3N_60": metrics["S16-HF1400-ET3N-60"]["abs"]["A330"],
                 "A330_control_60": metrics["S16-CTRL-60"]["abs"]["A330"]},
        "dose_series_S4": {by_id[k]["bzf_per_qd"]: {"A330": metrics[k]["abs"]["A330"], "abs_peak_nm": metrics[k]["abs"]["abs_peak_nm"]}
                           for k in ["S4-0660", "S4-0770", "S4-0880", "S4-0990", "S4-1100"]},
        "fig1C_inset_469nm": {"F1-150-60": metrics["F1-150-60"]["abs"]["abs_peak_nm"], "F1-150-60W": metrics["F1-150-60W"]["abs"]["abs_peak_nm"], "reported": rep["abs_peak_inset_after"]["value"]},
        "sphere": metrics["SPH-ZNCL"]["sphere"],
        "decays": {k: metrics[k]["decay"] for k in ["D-AS", "D-200-60", "D-200Z"]},
        "posthoc_no_absorbance_baseline_pct": {
            "note": "added after the first comparison run; uses the raw OD at 387 nm for sample and reference; not judged",
            "values": {i: metrics[i]["plqy_sensitivity_pct"]["posthoc_no_absorbance_baseline"] for i in
                       ["F1-150-05", "F1-150-60", "F1-150-60W", "F1-200-05", "F1-200-30", "F1-200-60", "F1-200-60W", "F1-200Z", "F1-AS",
                        "F4-HU-HF", "F4-HU-InF3", "F4-HI-InF3", "S9-InF3-05", "S9-InF3-30", "S9-InF3-60"]},
        },
    }

    # ---- contrasts: which recorded conditions link to measurable optical changes
    CONTRASTS = [
        ("temperature at 5 min", "temperature_C", ["F1-RT-05", "F1-090-05", "F1-150-05"]),
        ("temperature at 60 min", "temperature_C", ["F1-RT-60", "F1-090-60", "F1-150-60"]),
        ("time at 150 C", "time_min", ["F1-150-00", "F1-150-05", "F1-150-30", "F1-150-60"], ["treatment"]),
        ("time at 200 C", "time_min", ["F1-200-05", "F1-200-30", "F1-200-60"]),
        ("washing at 150 C", "washed", ["F1-150-60", "F1-150-60W"], ["treatment_solvent"]),
        ("washing at 200 C", "washed", ["F1-200-60", "F1-200-60W"], ["treatment_solvent"]),
        ("150 C vs 200 C at 60 min", "temperature_C", ["F1-150-60", "F1-200-60"]),
        ("ZnCl2 addition at 200 C", "treatment", ["F1-200-05", "F1-200Z"]),
        ("synthesis route under pure InF3", "synthesis", ["F4-HI-InF3", "F4-HU-InF3"]),
        ("synthesis route under in situ HF", "synthesis", ["F4-HI-HF", "F4-HU-HF"]),
        ("InF3 vs in situ HF, hot injection", "treatment", ["F4-HI-InF3", "F4-HI-HF"], ["bzf_per_qd"]),
        ("reagent at 150 C, 180 min", "treatment", ["S5-CTRL-180", "S5-AMINE-180", "S5-HF1400-180"], ["bzf_per_qd"]),
        ("HF dose at 150 C, 180 min", "bzf_per_qd", ["S7-HF700-180", "S5-HF1400-180"]),
        ("in situ acid identity, 180 min", "treatment", ["S7-HF700-180", "S7-HCL700-180", "S7-HBR700-180"], ["bzf_per_qd"]),
        ("organic acid identity, 180 min", "treatment", ["S8-CTRL-180", "S8-ACETIC-180", "S8-HEXANOIC-180", "S8-PALMITIC-180", "S8-HDA-180"]),
        ("time at 150 C, HF1400", "time_min", ["S6-HF1400-05", "S16-HF1400-60", "S5-HF1400-180"]),
        ("triethylamine addition", "treatment", ["S16-HF1400-60", "S16-HF1400-ET3N-60"]),
        ("InF3 time at 150 C", "time_min", ["S9-InF3-05", "S9-InF3-30", "S9-InF3-60"]),
    ]
    FACTORS = ["synthesis", "treatment", "temperature_C", "time_min", "washed", "bzf_per_qd", "treatment_solvent"]
    CONTRAST_NOTES = {
        "HF dose at 150 C, 180 min": "benzoyl fluoride dose; the octylamine amount is stated for S5 ([octylamine]/[QD] = 2000) "
                                     "but not for S7, so the amine may also differ (not a recorded factor)",
    }
    contrasts = []
    pb = tol["plqy_band"]
    for name, factor, ids, *imp in CONTRASTS:
        implied = imp[0] if imp else []
        sess = sorted({metrics[i]["session"] for i in ids})
        refs = sorted({by_id[i]["ref_id"] for i in ids})
        others = [f for f in FACTORS if f != factor and f not in implied and len({by_id[i][f].replace(" (assumed)", "") for i in ids}) > 1]
        if len(sess) > 1:
            others.append("measurement session")
        amb = [i for i in ids if "AMBIGUOUS" in by_id[i]["flags"]]
        qs = [q(i) for i in ids]
        span = max(qs) - min(qs)
        measurable = span > band(max(qs), pb)
        pk = [metrics[i]["abs"]["abs_peak_nm"] for i in ids]
        fw = [metrics[i]["pl"]["pl_fwhm_meV"] for i in ids]
        contrasts.append({
            "contrast": name, "factor": factor, "samples": ids, "levels": [by_id[i][factor] for i in ids],
            "note": CONTRAST_NOTES.get(name, ""),
            "plqy_pct": qs, "abs_peak_nm": pk, "pl_fwhm_meV": fw, "pl_peak_nm": [metrics[i]["pl"]["pl_peak_nm"] for i in ids],
            "sessions": sess, "references": refs, "implied_by_factor": implied, "other_varying": others, "ambiguous_samples": amb,
            "plqy_change_measurable": bool(measurable),
            "link": ("linked: one session, one factor" if not others and not amb else
                     ("linked, with flagged sample identity" if not others else "confounded")),
        })

    # ---- quality screen
    qs_ids = [i for i, m in metrics.items() if m.get("plqy_pct") is not None and by_id[i]["kind"] == "sample"]
    qs_ids = [i for i in qs_ids if i != "F4-HI-HF"]  # identical files to F1-150-60W
    screen = []
    for tp in [30, 50, 70]:
        for tw in [250, 300, 350]:
            ok = [i for i in qs_ids if metrics[i]["plqy_pct"] >= tp and (metrics[i]["pl"]["pl_fwhm_meV"] or 1e9) <= tw]
            ok_od = [i for i in ok if abs(metrics[i]["abs"]["A_ex"] - od_t["value"]) <= od_t["tolerance"]]
            screen.append({"plqy_min_pct": tp, "fwhm_max_meV": tw, "meet": ok, "meet_and_od_in_window": ok_od,
                           "sessions_of_meeting": sorted({metrics[i]["session"] for i in ok})})

    # ---- extension (hypothetical)
    ex = inp["extension"]
    eps330 = ex["epsilon_330"]["value"] * 1e6  # M-1 cm-1 per as-synthesized QD
    A_t = ex["target_absorbance_450"]["value"]
    untreated = metrics[ex["untreated_case"]["value"]]["abs"]
    eps450_0 = eps330 * untreated["A450"] / untreated["A330"]
    ext_rows = {}
    for i in ["F1-150-00", "F1-150-05", "F1-150-30", "F1-150-60"]:
        a = metrics[i]["abs"]
        R450, R330 = a["A450"] / untreated["A450"], a["A330"] / untreated["A330"]
        n_cm2 = A_t / (1000 * eps450_0 * R450)  # mol starting QDs per cm2
        n_m2 = n_cm2 * 1e4
        ext_rows[i] = {
            "time_min": by_id[i]["time_min"], "plqy_pct": q(i), "retained_A330": R330, "retained_A450": R450,
            "starting_qd_nmol_per_m2": n_m2 * 1e9, "standard_batches_per_m2": n_m2 / (ex["batch_qd_amount"]["value"] * 1e-9),
            "blue_absorbed_fraction": 1 - 10 ** (-A_t), "blue_to_green_photon_yield_pct": (1 - 10 ** (-A_t)) * q(i),
            "relative_photons_per_InP_fed_thin_layer": q(i) / 100 * R450,
            "layer_A540_self_absorption": A_t * a["A540"] / a["A450"] if a["A450"] > 0 else None,
            "pl_peak_nm": metrics[i]["pl"]["pl_peak_nm"],
        }
    # Sensitivity, not a correction: the Methods add amine and benzoyl fluoride solutions after the
    # QDs are diluted; the 0 min aliquot is read as taken before benzoyl fluoride (mapping.csv). If
    # aliquots were handled alike, the 0 min aliquot is k times more concentrated than the later ones.
    vol = ex["reagent_volumes"]["value"]
    v_all = vol["qd_stock_uL"] + vol["solvent_uL"] + vol["amine_uL"] + vol["benzoyl_fluoride_uL"]
    k_range = [v_all / (vol["qd_stock_uL"] + vol["solvent_uL"] + vol["amine_uL"]), v_all / (vol["qd_stock_uL"] + vol["solvent_uL"])]
    volume_bias = {"k_range": k_range, "note": "retained fractions x k, stock and batches per m2 / k; 0 min row unchanged; not applied to extension.rows", "rows": {}}
    for i, r in ext_rows.items():
        if i == "F1-150-00":
            continue
        volume_bias["rows"][i] = {
            "retained_A330_range": [r["retained_A330"] * k for k in k_range],
            "retained_A450_range": [r["retained_A450"] * k for k in k_range],
            "starting_qd_nmol_per_m2_range": [r["starting_qd_nmol_per_m2"] / k for k in reversed(k_range)],
            "standard_batches_per_m2_range": [r["standard_batches_per_m2"] / k for k in reversed(k_range)],
        }
    base, chg = ext_rows[ex["base_case"]["value"]], ext_rows["F1-150-05"]
    extension = {
        "label": "HYPOTHETICAL design extension (not validated)",
        "epsilon_450_untreated_M-1cm-1": eps450_0, "target_absorbance_450": A_t, "rows": ext_rows,
        "aliquot_volume_bias": volume_bias,
        "base_case": ex["base_case"]["value"], "changed_input": ex["changed_input"]["value"],
        "change": {
            "plqy_pp": chg["plqy_pct"] - base["plqy_pct"],
            "batches_per_m2_rel": chg["standard_batches_per_m2"] / base["standard_batches_per_m2"] - 1,
            "blue_to_green_yield_pp": chg["blue_to_green_photon_yield_pct"] - base["blue_to_green_photon_yield_pct"],
        },
    }

    # ---- write results
    RESULTS.mkdir(exist_ok=True)
    (RESULTS / "local").mkdir(exist_ok=True)
    # comparison.json holds the checks, the verdict and aggregates. Per-sample values beyond the
    # one computed value per check (contrast values, quality-screen membership, diagnostics,
    # per-sample values behind the bound checks, extension rows) go to results/details.json.
    checks_committed = {k: {f: v for f, v in r.items() if f != "ours_by_sample"} for k, r in results.items()}
    comparison = {
        "case": CASE_ID, "issue": 342, "tracker": 333,
        "dataset_doi": src["dataset"]["doi"], "tolerances_file": "tolerances.yaml", "tolerances_frozen": tol["frozen"],
        "data_source": {"dataset": "Ubbink et al., 4TU.ResearchData, version 1, 2023", "doi": src["dataset"]["doi"],
                        "licence": "CC BY-NC-SA 4.0", "changes": "computed by run.py; no data file, row or spectrum included",
                        "notice": "results/NOTICE.md"},
        "environment": {"python": platform.python_version(), "numpy": np.__version__, "scipy": scipy.__version__,
                        "matplotlib": matplotlib.__version__, "pyyaml": yaml.__version__},
        "verdict": verdict, "checks_passed": n_pass, "checks_total": n_units,
        "pair_X": {"statuses": pair, "counts_as_pass": pair_pass},
        "checks": checks_committed,
        "contrasts_summary": [{k: c[k] for k in ("contrast", "factor", "samples", "sessions", "other_varying", "ambiguous_samples",
                                                  "plqy_change_measurable", "link")} for c in contrasts],
        "quality_screen_counts": [{"plqy_min_pct": r["plqy_min_pct"], "fwhm_max_meV": r["fwhm_max_meV"], "n_meet": len(r["meet"]),
                                   "n_meet_and_od_in_window": len(r["meet_and_od_in_window"]),
                                   "n_sessions_of_meeting": len(r["sessions_of_meeting"])} for r in screen],
        "extension": {k: extension[k] for k in ("label", "base_case", "changed_input", "target_absorbance_450", "change")},
        "details": "results/details.json",
        "mapping_verification": {
            "internal_name_mismatches": [i for i, m in metrics.items() if "abs" in m and not m["abs"]["internal_name_matches_mapping"]],
            "members_verified_sha256": len(files),
        },
    }
    (RESULTS / "comparison.json").write_text(json.dumps(rnd(comparison), indent=1, sort_keys=True) + "\n")
    details = {
        "note": "per-sample values computed from the CC BY-NC-SA 4.0 dataset (results/NOTICE.md)",
        "checks_ours_by_sample": {k: r["ours_by_sample"] for k, r in results.items() if "ours_by_sample" in r},
        "diagnostics": diagnostics, "contrasts": contrasts, "quality_screen": screen, "extension": extension,
    }
    (RESULTS / "details.json").write_text(json.dumps(rnd(details), indent=1, sort_keys=True) + "\n")

    cols = ["id", "kind", "figure", "session", "ref_id", "synthesis", "treatment", "temperature_C", "time_min", "washed", "bzf_per_qd",
            "A387", "abs_baseline", "abs_peak_nm", "abs_peak_method", "peak_to_valley", "A330", "pl_peak_nm", "pl_fwhm_nm", "pl_fwhm_meV",
            "plqy_pct", "plqy_no_n_pct", "plqy_with_A_pct", "plqy_baseline_pct", "plqy_posthoc_no_abs_baseline_pct", "confounder_flags", "mapping_flags"]
    with (RESULTS / "sample_metrics.csv").open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(cols)
        for r in rows:
            m = metrics[r["id"]]
            a, p, s = m.get("abs", {}), m.get("pl", {}), m.get("plqy_sensitivity_pct", {})
            vals = [r["id"], r["kind"], r["figure"], a.get("date", ""), r["ref_id"], r["synthesis"], r["treatment"], r["temperature_C"],
                    r["time_min"], r["washed"], r["bzf_per_qd"], a.get("A_ex"), a.get("baseline_od"), a.get("abs_peak_nm"),
                    a.get("abs_peak_method", ""), a.get("peak_to_valley"), a.get("A330"), p.get("pl_peak_nm"), p.get("pl_fwhm_nm"),
                    p.get("pl_fwhm_meV"), m.get("plqy_pct"), s.get("no_refractive_index_correction"), s.get("absorbance_instead_of_absorptance"),
                    s.get("constant_pl_baseline"), s.get("posthoc_no_absorbance_baseline"), " | ".join(m.get("confounder_flags", [])), r["flags"]]
            w.writerow(["" if v is None else (f"{v:.4g}" if isinstance(v, float) else v) for v in vals])

    make_figures(metrics, by_id, rep, tol, ext_rows, volume_bias, files, rows)
    print(f"verdict: {verdict} ({n_pass} of {n_units} checks pass); results in {RESULTS.relative_to(HERE.parents[2])}")
    for k, v in results.items():
        print(f"  {k:4s} {v['status']:14s} ours={v.get('ours')!s:.8} reported={v['reported']}")
    return 0


# --------------------------------------------------------------------------- figures
def _save(fig, path):
    fig.savefig(path, format="svg", metadata={"Date": None, "Creator": None})
    plt.close(fig)


def make_figures(metrics, by_id, rep, tol, ext_rows, volume_bias, files, rows):
    plt.rcParams.update({"svg.hashsalt": "cheme-342", "svg.fonttype": "none", "font.size": 9, "axes.spines.top": False, "axes.spines.right": False})
    pb = tol["plqy_band"]

    # 1. PLQY against treatment time (our computed values) with the reported values and bands
    fig, ax = plt.subplots(figsize=(8.0, 4.2))
    series = [("RT", ["F1-RT-00", "F1-RT-05", "F1-RT-30", "F1-RT-60"], "#7f7f7f"),
              ("90 C", ["F1-090-00", "F1-090-05", "F1-090-30", "F1-090-60"], "#2ca02c"),
              ("150 C", ["F1-150-00", "F1-150-05", "F1-150-30", "F1-150-60"], "#1f77b4"),
              ("200 C", ["F1-200-05", "F1-200-30", "F1-200-60"], "#d62728")]
    for lab, ids, c in series:
        ax.plot([float(by_id[i]["time_min"]) for i in ids], [metrics[i]["plqy_pct"] for i in ids], "o-", color=c, label=f"{lab} (computed)")
    ax.plot([62], [metrics["F1-150-60W"]["plqy_pct"]], "o", mfc="none", color="#1f77b4", label="150 C washed (computed)")
    ax.plot([62], [metrics["F1-200-60W"]["plqy_pct"]], "o", mfc="none", color="#d62728", label="200 C washed (computed)")
    ax.plot([5], [metrics["F1-200Z"]["plqy_pct"]], "s", color="#9467bd", label="200 C + ZnCl2 (computed)")
    pts = [(6.5, "plqy_150C_early", "150 C, ca. 40"), (3.5, "plqy_ZnCl2", "ZnCl2, 85"), (58.0, "plqy_150C_60min", "150 C, 55"),
           (60.0, "plqy_200C_60min_fig1F", "200 C (1F), 67"), (63.5, "plqy_150C_washed", "washed (text), 64"),
           (65.5, "plqy_fig4_hotinj_HF", "same file (4B), 54")]
    for k, (t, key, lab) in enumerate(pts):
        v = rep[key]["value"]
        ax.errorbar([t], [v], yerr=[band(v, pb)], fmt="x", color="black", capsize=3, lw=0.8, label="reported, with tolerance" if k == 0 else None)
        ax.annotate(lab, (t, v), xytext=(4, -3), textcoords="offset points", fontsize=6, color="#333333")
    ax.axhline(5, color="#7f7f7f", ls=":", lw=1)
    ax.axhline(70, color="#d62728", ls=":", lw=0.8)
    ax.text(12, 71, "reported for 200 C: > 70 %", fontsize=6.5, color="#d62728")
    ax.text(12, 6, "reported bound: RT and 90 C < 5 %", fontsize=6.5, color="#555555")
    ax.set_xlim(-2, 76)
    ax.set_xlabel("treatment time (min); washed samples drawn at 62 min")
    ax.set_ylabel("PLQY (%)")
    ax.set_ylim(0, 100)
    ax.set_title("InP QDs, in situ HF: PLQY computed from the archived spectra vs reported values", fontsize=9)
    ax.legend(fontsize=6.5, ncol=1, frameon=False, loc="center left", bbox_to_anchor=(1.01, 0.5))
    fig.subplots_adjust(right=0.72)
    _save(fig, RESULTS / "fig_plqy_time.svg")

    # 2. quality screen: PLQY against emission FWHM, by measurement session
    fig, ax = plt.subplots(figsize=(6.4, 4.4))
    ids = [i for i, m in metrics.items() if m.get("plqy_pct") is not None and by_id[i]["kind"] == "sample" and i != "F4-HI-HF"
           and m["pl"]["pl_fwhm_meV"] is not None]
    sessions = sorted({metrics[i]["session"] for i in ids})
    cmap = plt.get_cmap("tab10")
    for k, s in enumerate(sessions):
        sel = [i for i in ids if metrics[i]["session"] == s]
        ax.scatter([metrics[i]["pl"]["pl_fwhm_meV"] for i in sel], [metrics[i]["plqy_pct"] for i in sel], color=cmap(k % 10), s=22, label=s, zorder=3)
        for i in sel:
            ax.annotate(i, (metrics[i]["pl"]["pl_fwhm_meV"], metrics[i]["plqy_pct"]), fontsize=5.5, xytext=(3, 2), textcoords="offset points")
    for tw in [250, 300, 350]:
        ax.axvline(tw, color="#999999", lw=0.8, ls="--" if tw == 300 else ":")
    for tp in [30, 50, 70]:
        ax.axhline(tp, color="#999999", lw=0.8, ls="--" if tp == 50 else ":")
    ax.set_xlabel("emission FWHM (meV), band-edge peak")
    ax.set_ylabel("PLQY (%)")
    ax.set_title("Quality screen: dashed = base criteria (PLQY >= 50 %, FWHM <= 300 meV); dotted = varied", fontsize=8)
    ax.legend(title="measurement session", fontsize=6.5, title_fontsize=7, frameon=False, loc="center right", bbox_to_anchor=(1.32, 0.5))
    fig.subplots_adjust(right=0.78)
    _save(fig, RESULTS / "fig_quality_screen.svg")

    # 3. extension: absorbance retained, PLQY and batches per m2 against time at 150 C
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(7.2, 3.2))
    t = [float(r["time_min"]) for r in ext_rows.values()]
    a1.plot(t, [100 * r["retained_A450"] for r in ext_rows.values()], "o-", color="#1f77b4", label="absorbance at 450 nm retained (%)")
    a1.plot(t, [100 * r["retained_A330"] for r in ext_rows.values()], "^--", color="#ff7f0e", label="absorbance at 330 nm retained (%)")
    a1.plot(t, [r["plqy_pct"] for r in ext_rows.values()], "s-", color="#2ca02c", label="PLQY (%)")
    a1.set_xlabel("time at 150 C (min)")
    a1.set_ylim(0, 105)
    a1.legend(fontsize=7, frameon=False)
    a1.set_title("measured, one session", fontsize=8)
    tt = [r["time_min"] for k, r in ext_rows.items() if k != "F1-150-00"]
    a2.bar([f"{x} min" for x in tt], [r["standard_batches_per_m2"] for k, r in ext_rows.items() if k != "F1-150-00"], color="#999999")
    lo_hi = [volume_bias["rows"][k]["standard_batches_per_m2_range"] for k in ext_rows if k != "F1-150-00"]
    a2.vlines(range(len(lo_hi)), [v[0] for v in lo_hi], [v[1] for v in lo_hi], color="black", lw=1.2,
              label=f"range if the 0 min aliquot was {volume_bias['k_range'][0]:.2f}-{volume_bias['k_range'][1]:.2f} x more concentrated")
    a2.set_ylim(0, 1.3 * max(v[1] for v in lo_hi + [[0, r["standard_batches_per_m2"]] for r in ext_rows.values()]))
    a2.legend(fontsize=6.5, frameon=False, loc="upper left")
    for x, (k, r) in enumerate([(k, r) for k, r in ext_rows.items() if k != "F1-150-00"]):
        a2.text(x, r["standard_batches_per_m2"], f"{r['blue_to_green_photon_yield_pct']:.0f} % blue->green", ha="center", va="bottom", fontsize=7)
    a2.set_ylabel("41 nmol batches per m2 (A450 = 1)")
    a2.set_title("HYPOTHETICAL layer design (not validated)", fontsize=8)
    fig.tight_layout()
    _save(fig, RESULTS / "fig_extension.svg")

    # local only (git-ignored): processed spectra of the 150 C series, for inspection
    fig, (b1, b2) = plt.subplots(1, 2, figsize=(7.2, 3.2))
    for i in ["F1-150-00", "F1-150-05", "F1-150-30", "F1-150-60", "F1-150-60W"]:
        a = parse_absorbance(files[by_id[i]["abs_member"]])
        p = parse_fls(files[by_id[i]["pl_member"]])
        b1.plot(a["x"], a["y"] - metrics[i]["abs"]["baseline_od"], lw=1, label=i)
        y = p["cols"][:, 0]
        b2.plot(p["x"], y / y.max(), lw=1, label=i)
    b1.set_xlim(330, 650)
    b1.set_xlabel("wavelength (nm)")
    b1.set_ylabel("OD, baseline-corrected")
    b2.set_xlabel("wavelength (nm)")
    b2.set_ylabel("PL, normalised")
    b1.legend(fontsize=6, frameon=False)
    fig.tight_layout()
    _save(fig, RESULTS / "local" / "spectra_150C.svg")


if __name__ == "__main__":
    sys.exit(main())
