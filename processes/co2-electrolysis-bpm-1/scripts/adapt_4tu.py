"""Measured WDE series of the reverse-bias BPM cell from the pinned 4TU raw data (#329).

Downloads (once) RawData_Experiments_rBPME_WDE.zip of the 4TU record
10.4121/5c4fc325-a71b-4ca8-9c1b-01c0405936a2.v1, refuses it unless its sha256 matches, and
evaluates every 1 M KOH titration sheet of the current-density study with the paper's
equations 3 to 10 (DESIGN.md D-002). Writes data/measured/wde-1m-koh.yaml and
figures/wde-1m-koh.svg. Uses only the raw sheets: no published result and nothing of
benchmarks/reproductions/ enters (ADR 0032).

Run from the process folder: cheme run scripts/adapt_4tu.py [--cache DIR]
"""

from __future__ import annotations

import argparse
import hashlib
import re
import statistics
import urllib.request
import zipfile
from pathlib import Path

import yaml

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
            "wde": wde, "n_k": n_k, "n_c": n_c, "notes": notes}


def series(zip_path: Path) -> list[dict]:
    runs = []
    with zipfile.ZipFile(zip_path) as z:
        for name in sorted(n for n in z.namelist() if n.startswith(SHEETS) and n.endswith(".docx")):
            runs.append(run(name, paragraphs(z.read(name))))
    if not runs:
        raise SystemExit(f"no titration sheets under {SHEETS} in {zip_path.name}")
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


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--cache", type=Path, default=Path.home() / ".cache/cheme-as-code/4tu/5c4fc325-v1")
    args = ap.parse_args()
    rows = series(fetch(args.cache))
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


if __name__ == "__main__":
    main()
