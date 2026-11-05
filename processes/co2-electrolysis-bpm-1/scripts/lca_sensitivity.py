"""The sensitivities, the ranking and the README tables of the skid LCA (#331).

    cheme run scripts/lca_sensitivity.py [--check]

Reads only the scenarios' LCA records results/scenarios/<H>h/lca.json (scripts/regen.py step 20
writes them, scripts/_lca.py) and writes, once both design scenarios have one (regen does this in
step 17, beside the resize report; DESIGN.md D-026):

- lca/sensitivity-membrane-life.json: the replaced stack parts per kg CO (m2 of bipolar membrane,
  g of membrane, Ag and Ni) at a membrane life of 1,000, 4,000 and 20,000 h (ASSUMED levels; the
  design is 4,000 h). An inventory sensitivity only: its impact is not computable, the parts have
  no open factor (gaps) and core's scenarios cannot vary a consumable's amount (design core gap
  C4);
- lca/sensitivity-h2-coproduct.json: the H2 the tail gas carries per kg CO, if a separation (not
  designed) recovered it as a co-product: its share of the burden by mass and by lower heating
  value; substitution has no open factor (missing);
- lca/sensitivity-electricity-mix.json: both skids on the Ember 2025 grids of NL, the EU-27, DE,
  FR and the world (one profile: the electricity pairs differ in no dimension; the verdict is
  "proxy" through the UK water factor) and the DESNZ UK grid (another basis: not comparable),
  from the scenario records;
- lca/sensitivity-duration.json: the KOH, the spent anolyte and the bleed per kg CO at 1,000 and
  10,000 h, by exchange;
- lca/ranking.json: the flows that distinguish Skid A from Skid B, whether each has a documented
  factor, the characterised difference, the break-even KOH factor and the verdict: "ranking not
  determined" unless every distinguishing flow has a documented factor (library ADR 0029);
- the tables of lca/README.md between its markers.

Deterministic (no time stamp; floats to 10 significant figures), so --check compares bytes; it
exits 3 when a file differs.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import _results as res
import yaml

SCENARIO_LCA = "results/scenarios/{h}h/lca.json"
README = "lca/README.md"
BEGIN = "<!-- regen:lca begin (scripts/lca_sensitivity.py; do not edit) -->"
END = "<!-- regen:lca end -->"
SCHEMA = "process-library/skid-lca-sensitivity/1"
#: the membrane lives of the inventory sensitivity, h (ASSUMED levels, DESIGN.md D-026)
MEMBRANE_LIVES_H = (1000.0, 4000.0, 20000.0)
#: the electricity scenarios: (scenario id of Skid A, of Skid B, the grid)
MIXES = (
    ("baseline", "skid-b", "NL (Ember 2025)"),
    ("mix-eu27", "skid-b-mix-eu27", "EU-27 (Ember 2025)"),
    ("mix-de", "skid-b-mix-de", "DE (Ember 2025)"),
    ("mix-fr", "skid-b-mix-fr", "FR (Ember 2025)"),
    ("mix-glo", "skid-b-mix-glo", "world (Ember 2025)"),
    ("desnz-gb", None, "UK at the consumer (DESNZ 2026): cross-basis check"),
)
#: the KOH exchanges and the anolyte wastes (duration and ranking)
KOH = ("feed:KOH-FILL", "feed:KOH-DOSE")
WASTES = ("product:SPENT", "product:BLEED", "product:CONDENSATE")
NOT_DETERMINED = "ranking not determined"
#: the characterised flows of the totals (core's contributions) and the solutions' water the
#: record adds at the water factor (scripts/_lca.py solution_water)
CHARACTERISED = {"feed:POWER": "electricity", "emission:CO2": "vent CO2", "feed:WATER": "water"}
SOLUTION_WATER = "water in the KOH solutions"


def _tanks(doc: dict, skid: str) -> str:
    tanks = doc["skids"][skid]["tanks_m3"]
    return " and ".join(f"{v:.3g} m3 {tag}" for tag, v in sorted(tanks.items()))


def construction(doc: dict) -> str:
    """The construction cut-off with the duty-sized tanks of this scenario's record."""
    return (
        "construction (cut off: not expressible per case in core 1.5.0; Skid A's tanks "
        f"{_tanks(doc, 'A')} against Skid B's {_tanks(doc, 'B')})"
    )


def _scenarios(root: Path) -> tuple[float, list[float]]:
    basis = yaml.safe_load((root / "process" / "design-basis.yaml").read_text(encoding="utf-8"))
    duration = basis["capacity"]["pilot_skid"]["duration"]
    return float(duration["design"]["value"]), [float(x) for x in duration["scenarios"]]


def load(root: Path) -> dict[float, dict] | None:
    """The scenarios' LCA records, or None while one is missing."""
    _, hs = _scenarios(root)
    docs = {}
    for h in hs:
        path = root / SCENARIO_LCA.format(h=f"{h:g}")
        if not path.exists():
            return None
        docs[h] = json.loads(path.read_text(encoding="utf-8"))
    return docs


def _ex(doc: dict, skid: str, key: str, field: str = "amount") -> float:
    row = doc["skids"][skid]["exchanges"].get(key) or {}
    if field.startswith("components_kg."):
        return float((row.get("components_kg") or {}).get(field.split(".", 1)[1], 0.0))
    return float(row.get(field) or 0.0)


def _koh(doc: dict, skid: str) -> float:
    return sum(_ex(doc, skid, k, "components_kg.KOH") for k in KOH)


# -- the sensitivities --------------------------------------------------------------------------


def membrane_life(doc: dict) -> dict[str, Any]:
    p = doc["parts"]
    co = doc["skids"]["A"]["co_delivered_kg_h"]
    rows = []
    for life in MEMBRANE_LIVES_H:
        m2 = p["replaced_m2"] / (life * co)
        rows.append(
            {
                "membrane_life_h": life,
                "design": life == p["interval_h"],
                "membrane_m2_per_kg": m2,
                "membrane_g_per_kg": m2 * p["areal_kg_m2"]["membrane-bpm"] * 1e3,
                "ag_g_per_kg": m2 * p["areal_kg_m2"]["cathode-gde-ag"] * 1e3,
                "carbon_paper_g_per_kg": m2 * p["areal_kg_m2"]["cathode-gdl-carbon"] * 1e3,
                "ni_g_per_kg": m2 * p["areal_kg_m2"]["anode-ni-foam"] * 1e3,
            }
        )
    # the design row equals the datasets' consumables (both skids)
    design = next(r for r in rows if r["design"])
    check = {
        skid: {
            cid: _ex(doc, skid, f"consumable:{cid}") * 1e3
            for cid in ("membrane-bpm", "cathode-gde-ag", "cathode-gdl-carbon", "anode-ni-foam")
        }
        for skid in ("A", "B")
    }
    return {
        "schema": SCHEMA,
        "what": "membrane life (inventory sensitivity)",
        "duration_h": doc["duration_h"],
        "basis": (
            f"{p['cells']} cells x {p['cell_area_m2'] * 1e4:g} cm2 = {p['replaced_m2']:g} m2 replaced per life, over "
            "the CO delivered in it; areal masses ASSUMED (lca/lca.yaml consumables, DESIGN.md D-026)"
        ),
        "levels_assumed": True,
        "rows": rows,
        "design_life_h": p["interval_h"],
        "datasets_g_per_kg_at_design": check,
        "datasets_match": all(
            abs(check[s]["membrane-bpm"] - design["membrane_g_per_kg"]) <= 1e-6 * design["membrane_g_per_kg"]
            for s in check
        ),
        "impact": "not computable: gap (no open factor for the bipolar membrane, the Ag cathode, its carbon paper or the Ni foam; core's scenarios cannot vary a consumable's amount, design core gap C4)",
        "same_for_both_skids": True,
    }


def h2_coproduct(doc: dict) -> dict[str, Any]:
    lhv = {c: doc["lhv_kj_mol"][c] / doc["molar_mass"][c] for c in ("CO", "H2")}  # MJ/kg
    out = {
        "schema": SCHEMA,
        "what": "H2 recovered as a co-product (alternative disposition, not designed)",
        "duration_h": doc["duration_h"],
        "baseline": "H2 burnt with the PSA tail gas in the oxidiser X-x32, O2 vented: CO is the only product (allocation none, DESIGN.md D-024)",
        "lhv_mj_kg": lhv,
        "lhv_source": "CODATA Key Values (Cox, Wagman, Medvedev 1989): CO 282.98 kJ/mol (process/reactions.yaml COX), H2 to H2O(g) 241.826 kJ/mol",
        "skids": {},
        "substitution": "missing: no open factor for the hydrogen a co-product would displace",
        "status": "open: needs an H2 separation (the tail gas is mostly H2 and CO2) that is not designed; the oxidiser's heat would be lost too",
    }
    for skid in ("A", "B"):
        h2 = doc["skids"][skid]["h2_tail_kg_per_kg"]
        share_mass = h2 / (1.0 + h2)
        share_lhv = h2 * lhv["H2"] / (h2 * lhv["H2"] + lhv["CO"])
        total = doc["skids"][skid]["impacts"]["total"]
        out["skids"][skid] = {
            "h2_kg_per_kg_co": h2,
            "h2_share_mass": share_mass,
            "h2_share_lhv": share_lhv,
            "co_share_mass": 1.0 - share_mass,
            "co_share_lhv": 1.0 - share_lhv,
            "characterised_total": total,
            "co_characterised_by_mass": None if total is None else total * (1.0 - share_mass),
            "co_characterised_by_lhv": None if total is None else total * (1.0 - share_lhv),
            "note": "the characterised total with its gaps excluded (a partial footprint); the oxidiser would no longer burn the H2 (its flue CO2 from the CO slip and the unrecycled CO2 stays)",
        }
    return out


def electricity_mix(doc: dict) -> dict[str, Any]:
    sc = doc["scenarios"]
    rows = []
    for a_id, b_id, grid in MIXES:
        row: dict[str, Any] = {"grid": grid}
        for skid, sid in (("A", a_id), ("B", b_id)):
            if sid is None or sid not in sc:
                row[skid] = None
                continue
            s = sc[sid]
            power = s["contributions"].get("feed:POWER") or {}
            row[skid] = {
                "scenario": sid,
                "total": s["total"],
                "electricity": power.get("value"),
                "factor": power.get("basis"),
                "vent_co2": (s["contributions"].get("emission:CO2") or {}).get("value"),
                "verdict": s["verdict"],
                "reasons": s["reasons"],
                "electricity_pair_differences": [c["differences"] for c in s["compared"] if "electricity" in c["baseline"]],
            }
        if row["A"] and row["B"] and row["A"]["total"] is not None and row["B"]["total"] is not None:
            row["b_minus_a"] = row["B"]["total"] - row["A"]["total"]
        rows.append(row)
    return {
        "schema": SCHEMA,
        "what": "electricity mix (background sensitivity, from lca/scenarios/*.json)",
        "duration_h": doc["duration_h"],
        "note": (
            "Totals are the characterised sum with the gaps excluded (a partial screening footprint). The Ember "
            "grids come from one profile: the electricity pair has no differing dimension; the verdict 'proxy' "
            "comes from the water background only (a UK factor in every geography). DESNZ is another basis "
            "(at the consumer, AR5): not comparable."
        ),
        "rows": rows,
    }


def duration(docs: dict[float, dict]) -> dict[str, Any]:
    hs = sorted(docs)
    rows = []
    for skid in ("A", "B"):
        for key, field, label in (
            ("feed:KOH-FILL", "components_kg.KOH", "KOH fill (KOH 100 %), kg"),
            ("feed:KOH-DOSE", "components_kg.KOH", "KOH dosed (KOH 100 %), kg"),
            ("feed:KOH-FILL", "amount", "1 M fill solution, kg"),
            ("feed:KOH-DOSE", "amount", "5 M dosing solution, kg"),
            ("product:SPENT", "amount", "spent anolyte, kg"),
            ("product:BLEED", "amount", "bleed, kg"),
            ("product:CONDENSATE", "amount", "cathode condensate, kg"),
        ):
            values = {f"{h:g}": _ex(docs[h], skid, key, field) for h in hs}
            a, b = (values[f"{h:g}"] for h in hs)
            rows.append({"skid": skid, "exchange": key, "quantity": label + " per kg CO", "values": values,
                         "ratio": (b / a) if a else None})  # fmt: skip
        values = {f"{h:g}": _koh(docs[h], skid) for h in hs}
        rows.append({"skid": skid, "exchange": "KOH", "quantity": "KOH in all (fill + dosed), kg per kg CO", "values": values})
    totals = {
        skid: {f"{h:g}": docs[h]["skids"][skid]["impacts"]["total"] for h in hs} for skid in ("A", "B")
    }
    return {
        "schema": SCHEMA,
        "what": "campaign duration (1,000 h against 10,000 h), per kg CO",
        "rows": rows,
        "characterised_totals": totals,
        "note": "Skid A's fill and spent anolyte scale with the reservoir, which is sized to the horizon: per kg CO they do not change; Skid B's 50 L fill and final inventory are spread over ten times the CO. No KOH or waste flow has a factor, so the characterised totals do not change with the duration (results/resize-1000h-10000h.md has the KOH rows of #330).",
    }


def characterised(doc: dict, skid: str) -> dict[str, float]:
    """kg CO2e per kg CO by characterised flow: core's contributions, and the KOH solutions'
    water at the feed:WATER factor (inside the KOH gaps in core's total)."""
    s = doc["skids"][skid]
    c = s["impacts"]["contributions"]
    out = {label: float((c.get(k) or {}).get("value") or 0.0) for k, label in CHARACTERISED.items()}
    out[SOLUTION_WATER] = float(s["solution_water"]["kg_co2e"] or 0.0)
    return out


def _names(items: list[str]) -> str:
    return items[0] if len(items) == 1 else ", ".join(items[:-1]) + " and " + items[-1]


def ranking(doc: dict) -> dict[str, Any]:
    a, b = doc["skids"]["A"], doc["skids"]["B"]
    keys = sorted(set(a["exchanges"]) | set(b["exchanges"]))
    flows = []
    for k in keys:
        qa, qb = _ex(doc, "A", k), _ex(doc, "B", k)
        if abs(qa - qb) <= 1e-9 * max(abs(qa), abs(qb), 1e-300):
            continue
        sa = (a["exchanges"].get(k) or {}).get("status")
        sb = (b["exchanges"].get(k) or {}).get("status")
        documented = all(s not in (None, "gap") for s in (sa, sb))
        flows.append({"key": k, "A": qa, "B": qb, "B_minus_A": qb - qa, "unit": (a["exchanges"].get(k) or b["exchanges"][k])["unit"],
                      "status": {"A": sa, "B": sb}, "documented_factor": documented})  # fmt: skip
    tanks = {s: sum(doc["skids"][s]["tanks_m3"].values()) for s in ("A", "B")}
    flows.append({"key": "construction", "A": tanks["A"], "B": tanks["B"], "unit": "m3 of duty-sized tanks",
                  "status": {"A": "cutoff", "B": "cutoff"}, "documented_factor": False, "note": construction(doc)})  # fmt: skip
    undocumented = [f["key"] for f in flows if not f["documented_factor"]]
    ta, tb = a["impacts"]["total"], b["impacts"]["total"]
    wa, wb = a["solution_water"]["total_with_it"], b["solution_water"]["total_with_it"]
    koh = {"A": _koh(doc, "A"), "B": _koh(doc, "B")}
    waste = {s: sum(_ex(doc, s, k) for k in WASTES) for s in ("A", "B")}
    # the difference with the KOH solutions' water at the water factor: the KOH factor is then
    # per kg KOH 100 % (the water no longer inside it)
    diff = None if wa is None or wb is None else wb - wa
    break_even = None if diff is None or koh["A"] == koh["B"] else diff / (koh["A"] - koh["B"])
    by_flow = {s: characterised(doc, s) for s in ("A", "B")}
    side: dict[str, list[str]] = {"A": [], "B": [], "equal": []}
    for label in by_flow["A"]:
        va, vb = by_flow["A"][label], by_flow["B"][label]
        side["equal" if abs(va - vb) <= 1e-9 * max(abs(va), abs(vb), 1e-300) else ("B" if vb > va else "A")].append(label)
    # which skid carries more of each group of undocumented flows (the wastes share one route)
    groups = {"KOH": "KOH (fill and dose, KOH 100 %)", "wastes": "alkaline wastes to neutralisation (spent anolyte, bleed, condensate)",
              "construction": "construction (the duty-sized tanks)"}  # fmt: skip
    more = {
        groups["KOH"]: "B" if koh["B"] > koh["A"] else "A",
        groups["wastes"]: "B" if waste["B"] > waste["A"] else "A",
        groups["construction"]: "B" if tanks["B"] > tanks["A"] else "A",
    }
    if break_even is None:
        reading = "not computable"
    elif break_even < 0:
        # the skid with the higher characterised total also uses more KOH: no KOH factor reverses
        hi = "B" if diff > 0 else "A"
        lo = "A" if hi == "B" else "B"
        parts = [f"higher in {_names(side[hi])}"] if side[hi] else []
        parts += [f"lower in {_names(side[lo])}"] if side[lo] else []
        parts += [f"equal in {_names(side['equal'])}"] if side["equal"] else []
        wastes_too = more[groups["wastes"]] == hi
        lo_groups = [g for g, s in more.items() if s == lo]
        reading = (
            f"none: {break_even:.4g} kg CO2e per kg KOH, below zero. Skid {hi} has the higher characterised total "
            f"({abs(diff):.4g} kg CO2e/kg CO more with the KOH solutions' water; {'; '.join(parts)}) and uses "
            f"{koh[hi] / koh[lo]:.3g} times the KOH per kg CO, so no KOH factor reverses the order"
            + (
                f"; it makes {waste[hi] / waste[lo]:.3g} times the alkaline waste too, so no treatment factor does either"
                if wastes_too and waste[lo]
                else f"; Skid {lo} makes more alkaline waste, so a treatment factor could"
            )
            + (
                f"; of the flows without a factor only those Skid {lo} carries more of could: {_names(lo_groups)}"
                + (", which core 1.5.0 cannot state per case (cut off)" if groups["construction"] in lo_groups else "")
                if lo_groups
                else f"; Skid {lo} carries more of no flow without a factor"
            )
        )
    else:
        reading = f"{break_even:.4g} kg CO2e per kg KOH: above it the skid with less KOH is lower"
    return {
        "schema": SCHEMA,
        "what": "Skid A against Skid B: the ranking rule (DESIGN.md D-026)",
        "duration_h": doc["duration_h"],
        "rule": "A is ranked against B only if every flow that distinguishes them has a documented factor (library ADR 0029: gaps are listed, never stubbed)",
        "distinguishing_flows": flows,
        "undocumented": undocumented,
        "verdict": NOT_DETERMINED if undocumented else "ranked",
        "characterised": {
            "A": ta, "B": tb, "B_minus_A": None if ta is None or tb is None else tb - ta,
            "with_solution_water": {"A": wa, "B": wb, "B_minus_A": diff},
            "by_flow": by_flow,
            "higher": side,
            "note": "core's totals: electricity, the vent CO2 and the water, the gaps excluded; with_solution_water adds the KOH solutions' dilution water at the water factor (inside the KOH gaps in core's totals), the basis of the break-even",
        },  # fmt: skip
        "koh_kg_per_kg": koh,
        "break_even_koh_kg_co2e_per_kg": break_even,
        "break_even_basis": "the KOH factor per kg KOH 100 % at which the totals with the KOH solutions' water are equal: (B - A) / (KOH of A - KOH of B)",
        "break_even_reading": reading,
        "wastes_kg_per_kg": waste,
        "tanks_m3": tanks,
        "carried_more_by": more,
        "inventory_comparison": "lca/README.md and results/scenarios/<H>h/lca.json, per kg CO",
    }


# -- the README tables ----------------------------------------------------------------------------


def _f(x: float | None, digits: int = 4) -> str:
    if x is None:
        return "n/a"
    if x == 0:
        return "0"
    return f"{x:.{digits}g}"


def readme_tables(docs: dict[float, dict], design: float) -> str:
    d = docs[design]
    hs = sorted(docs)
    lines = [f"Generated from results/scenarios/<H>h/lca.json (design campaign {design:g} h unless stated). Per kg CO delivered.", ""]
    # inventory
    lines += ["**Inventory per kg CO** (both skids; the background or why it is a gap)", "",
              "| exchange | Skid A | Skid B | unit | background (A) |", "|---|---|---|---|---|"]  # fmt: skip
    keys = [k for k in d["skids"]["A"]["exchanges"] if not k.startswith("disposal:")]
    for k in keys:
        ra, rb = d["skids"]["A"]["exchanges"][k], d["skids"]["B"]["exchanges"].get(k, {})
        extra = ""
        if "KOH" in (ra.get("components_kg") or {}) or "KOH" in (rb.get("components_kg") or {}):
            extra = f" (KOH {_f(_ex(d, 'A', k, 'components_kg.KOH'))} / {_f(_ex(d, 'B', k, 'components_kg.KOH'))})"
        lines.append(f"| {k}{extra} | {_f(ra['amount'])} | {_f(rb.get('amount'))} | {ra['unit'].split('/')[0]} | {ra.get('status') or 'n/a'} |")
    lines.append("")
    # contributions
    lines += ["**Climate change, NL grid** (kg CO2e per kg CO; a partial screening carbon footprint, gaps excluded)", "",
              "| | Skid A | Skid B |", "|---|---|---|"]  # fmt: skip
    for k, label in (("feed:POWER", "electricity (Ember 2025 NL)"), ("emission:CO2", "vent CO2 (fossil)"), ("feed:WATER", "water (DESNZ, proxy)")):
        va = (d["skids"]["A"]["impacts"]["contributions"].get(k) or {}).get("value")
        vb = (d["skids"]["B"]["impacts"]["contributions"].get(k) or {}).get("value")
        lines.append(f"| {label} | {_f(va)} | {_f(vb)} |")
    lines.append(f"| characterised total | {_f(d['skids']['A']['impacts']['total'])} | {_f(d['skids']['B']['impacts']['total'])} |")
    sw = {s: d["skids"][s]["solution_water"] for s in ("A", "B")}
    lines.append(f"| water in the KOH solutions (inside the KOH gaps; at the water factor) | {_f(sw['A']['kg_co2e'])} | {_f(sw['B']['kg_co2e'])} |")
    lines.append(f"| total with that water (the ranking's basis) | {_f(sw['A']['total_with_it'], 7)} | {_f(sw['B']['total_with_it'], 7)} |")
    cc = {s: d["skids"][s]["carbonate_co2"] for s in ("A", "B")}
    lines.append(
        f"| not counted: fossil CO2 of the carbonate wastes, released when neutralised (inside the waste gaps; "
        f"{cc['A']['share_of_co2_fed'] * 100:.1f} % of the CO2 fed) | {_f(cc['A']['kg_co2_per_kg'])} | {_f(cc['B']['kg_co2_per_kg'])} |"
    )
    gaps = {s: (len(d["skids"][s]["impacts"]["gaps"]), len(d["skids"][s]["gaps_nonzero"])) for s in ("A", "B")}
    lines.append(
        "| gaps (exchanges without a factor; of them non-zero) | "
        + " | ".join(f"{n} ({nz} non-zero)" for n, nz in (gaps["A"], gaps["B"]))
        + " |"
    )
    lines.append("")
    # electricity mix
    mix = electricity_mix(d)
    lines += ["**Electricity mix** (characterised total, kg CO2e per kg CO; verdict against the baseline)", "",
              "| grid | Skid A | Skid B | verdict |", "|---|---|---|---|"]  # fmt: skip
    for r in mix["rows"]:
        va = r["A"]["total"] if r["A"] else None
        vb = r["B"]["total"] if r["B"] else None
        lines.append(f"| {r['grid']} | {_f(va)} | {_f(vb)} | {r['A']['verdict'] if r['A'] else 'n/a'} |")
    lines.append("")
    # duration
    dur = duration(docs)
    head = " | ".join(f"{h:g} h" for h in hs)
    lines += ["**Duration** (per kg CO)", "", f"| skid | quantity | {head} |", "|---|---|" + "---|" * len(hs)]
    for r in dur["rows"]:
        if r["exchange"] in ("feed:KOH-FILL", "feed:KOH-DOSE", "KOH") and ("solution" not in r["quantity"]):
            lines.append(f"| {r['skid']} | {r['quantity']} | " + " | ".join(_f(r["values"][f"{h:g}"]) for h in hs) + " |")
    lines.append("")
    # membrane life
    mem = membrane_life(d)
    lines += ["**Membrane life** (inventory only; impact not computable: gap)", "",
              "| life | m2 BPM | g membrane | g Ag | g carbon paper | g Ni |", "|---|---|---|---|---|---|"]  # fmt: skip
    for r in mem["rows"]:
        tag = " (design)" if r["design"] else ""
        lines.append(f"| {r['membrane_life_h']:,.0f} h{tag} | {_f(r['membrane_m2_per_kg'])} | {_f(r['membrane_g_per_kg'])} | {_f(r['ag_g_per_kg'])} | {_f(r['carbon_paper_g_per_kg'])} | {_f(r['ni_g_per_kg'])} |")
    lines.append("")
    # H2 co-product
    h2 = h2_coproduct(d)["skids"]["A"]
    h2_line = (
        f"**H2 as a co-product** (not designed): {_f(h2['h2_kg_per_kg_co'], 3)} kg H2 per kg CO would carry "
        f"{h2['h2_share_mass'] * 100:.1f} % of the burden by mass or {h2['h2_share_lhv'] * 100:.1f} % by LHV; "
        "substitution missing."
    )
    lines += [h2_line, ""]
    # ranking
    rk = ranking(d)
    be = rk["break_even_koh_kg_co2e_per_kg"]
    rank_line = (
        f"**Skid A against Skid B: {rk['verdict']}.** Distinguishing flows without a documented factor: "
        f"{', '.join(rk['undocumented'])}. Break-even KOH factor: {_f(be)} kg CO2e/kg KOH "
        f"({rk['break_even_reading'].split(':')[0]})."
    )
    lines += [rank_line, ""]
    # reconciliation
    ok = {
        f"{h:g} h": all(docs[h]["skids"][s]["reconciled"] and docs[h]["skids"][s]["lca_cases_agree"] for s in ("A", "B"))
        for h in hs
    }
    worst = max(r["rel"] for h in hs for s in ("A", "B") for r in docs[h]["skids"][s]["reconciliation"])
    states = ", ".join(f"{k} {'yes' if v else '**no**'}" for k, v in ok.items())
    rec_line = (
        f"**Reconciliation (E10)**: the datasets equal the duty totals per kg CO at {states} "
        f"(largest relative difference {worst:.1e}, tolerance 1e-6)."
    )
    lines += [rec_line, ""]
    return "\n".join(lines)


def texts(root: Path, docs: dict[float, dict] | None = None) -> dict[str, str]:
    """The files this script writes, by path (empty while a scenario's record is missing)."""
    docs = docs if docs is not None else load(root)
    if docs is None:
        return {}
    design, _ = _scenarios(root)
    d = docs[design]
    out = {
        "lca/sensitivity-membrane-life.json": res.dump(membrane_life(d)),
        "lca/sensitivity-h2-coproduct.json": res.dump(h2_coproduct(d)),
        "lca/sensitivity-electricity-mix.json": res.dump(electricity_mix(d)),
        "lca/sensitivity-duration.json": res.dump(duration(docs)),
        "lca/ranking.json": res.dump(ranking(d)),
    }
    readme = root / README
    if readme.exists():
        text = readme.read_text(encoding="utf-8")
        if BEGIN in text and END in text:
            head, rest = text.split(BEGIN, 1)
            _, tail = rest.split(END, 1)
            out[README] = f"{head}{BEGIN}\n{readme_tables(docs, design)}{END}{tail}"
    return out


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(prog="cheme run scripts/lca_sensitivity.py", description=__doc__.split("\n\n")[0])
    parser.add_argument("--check", action="store_true", help="compare, write nothing (exit 3 on a difference)")
    args = parser.parse_args(argv)
    root = Path.cwd()
    out = texts(root)
    if not out:
        print("lca_sensitivity: waits for the LCA record of every design scenario (scripts/regen.py)")
        return 2
    differ = []
    for rel, text in out.items():
        path = root / rel
        if args.check:
            if not path.exists() or path.read_text(encoding="utf-8") != text:
                differ.append(rel)
        else:
            path.write_text(text, encoding="utf-8")
            print(f"lca_sensitivity: {rel}")
    for rel in differ:
        print(f"lca_sensitivity: differs: {rel}")
    return 3 if differ else 0


if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    sys.exit(main(sys.argv[1:]))
