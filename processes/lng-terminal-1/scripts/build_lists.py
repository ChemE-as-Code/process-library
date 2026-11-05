"""Write the line list, instrument list and special piping items from the P&ID drafts.

Provenance (DESIGN.md D-021): each scripts/draft_*.py records the lines, instruments and relief
devices it draws in build/lists_<sheet>.json; this script writes piping/line-list.yaml,
control/instrument-list.yaml and piping/special-items.yaml from them, keeping the notes of the
concept-stage instrument list where a tag is the same. After the first revision the lists are
maintained by hand with the sheets (skill lists-sync). Run: cheme run scripts/build_lists.py
"""

import json
from pathlib import Path

import yaml

SHEETS = [f"P-0{i}" for i in range(1, 9)]


def flow(entry: dict) -> str:
    """One list entry as a YAML flow mapping (the style of the other plant lists)."""
    text = yaml.safe_dump(entry, default_flow_style=True, sort_keys=False, width=10_000,
                          allow_unicode=True).strip()
    return "  - " + text


def main() -> None:
    data = {s: json.loads((Path("build") / f"lists_{s}.json").read_text()) for s in SHEETS}
    old = yaml.safe_load(Path("control/instrument-list.yaml").read_text()) or {}
    old_notes = {i["tag"]: i.get("notes", "") for i in old.get("instruments") or []}

    out = ["# Line list. Schema: `cheme schema lines`.",
           "# Written from the P&ID drafts by scripts/build_lists.py (D-021), then kept with the",
           "# sheets (skill lists-sync). Numbers per D-015 (<fluid>-<sheet digit><nnn>); DN per D-008",
           "# and the sizing script (concept estimates, ASSUMED). Pressure class ASME Class 150",
           "# (ASSUMED) for the LNG and vapour systems. BL = battery limit.",
           "schema: cheme/lines/v1", "lines:"]
    # A line continued on another sheet keeps its number (D-021): one entry, from the sheet
    # whose draft gives its full notes (the others say "see P-0x"), the sheets named in it.
    merged: dict[str, dict] = {}
    for s in SHEETS:
        for e in data[s]["lines"]:
            have = merged.get(e["number"])
            if have is None:
                merged[e["number"]] = e
                continue
            if have["nominal_diameter"] != e["nominal_diameter"]:
                print(f"DN differs for {e['number']}: {have['sheet']} {have['nominal_diameter']}, "
                      f"{s} {e['nominal_diameter']}")
            # the home sheet is the one its number names (LNG-4005 -> P-04); the fullest notes win
            home = f"P-0{e['number'].split('-')[1][0]}"
            notes = max((have["notes"], e["notes"]), key=lambda t: (not t.startswith("see "), len(t)))
            if e["sheet"] == home:
                merged[e["number"]] = {**e, "notes": notes}
            else:
                have["notes"] = notes
    for s in SHEETS:
        rows = [e for e in merged.values() if e["sheet"] == s]
        out.append(f"  # ---- {s}")
        out += [flow(e) for e in rows]
    Path("piping/line-list.yaml").write_text("\n".join(out) + "\n", encoding="utf-8")

    out = ["# Instrument list. Schema: `cheme schema instruments`.",
           "# Written from the P&ID drafts by scripts/build_lists.py (D-021), then kept with the",
           "# sheets. Tags per D-015 (ISA 5.1 letters + <sheet digit><nnn>); trips in",
           "# control/cause-effect.yaml.",
           "schema: cheme/instruments/v1", "instruments:"]
    for s in SHEETS:
        out.append(f"  # ---- {s}")
        for e in data[s]["instruments"]:
            if not e.get("notes") and old_notes.get(e["tag"]):
                e["notes"] = old_notes[e["tag"]]
            out.append(flow(e))
    Path("control/instrument-list.yaml").write_text("\n".join(out) + "\n", encoding="utf-8")

    out = ["# Special piping items. Schema: `cheme schema piping_items`.",
           "# Relief devices drawn on the P&IDs with their governing case (D-017; sizing in detail",
           "# engineering, set pressures ASSUMED). Written by scripts/build_lists.py (D-021).",
           "schema: cheme/piping_items/v1", "piping_items:"]
    for s in SHEETS:
        if data[s]["piping_items"]:
            out.append(f"  # ---- {s}")
            out += [flow(e) for e in data[s]["piping_items"]]
    Path("piping/special-items.yaml").write_text("\n".join(out) + "\n", encoding="utf-8")
    counts = {k: sum(len(d[k]) for d in data.values()) for k in ("lines", "instruments", "piping_items")}
    print(f"wrote the lists: {counts}")


if __name__ == "__main__":
    main()
