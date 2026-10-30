"""Equipment items above their cost correlation's range, priced as identical units within it
(S5c, DESIGN.md D-044).

Run with `cheme run scripts/split_equipment_costs.py`; it writes nothing and prints the
`items:` entries for estimate/cost-basis.yaml, which are pasted there by hand. `cheme assess
equipment` does not extrapolate a correlation and asks to "split it into units within the range
(and say so)": each item above the range is divided into n = ceil(size / max) equal units, each
priced with the package's Turton et al. (CAPCOST) correlation and bare module factor exactly as
`cheme assess equipment` prices an item in range (core's own functions), escalated with the
project's CEPCI, and the item's cost is n times that. Because cost grows less than in proportion
to size, n small units cost more than one large item: the split overstates the cost (an upper
estimate, said in each source).
"""

import math
from types import SimpleNamespace

from chemeascode.domains.assessment.equipment_cost import (
    BASIS_FILE,
    CostLine,
    _cost,
    capcost,
    load_basis,
)
from chemeascode.domains.equipment.datasheets import datasheet_paths, load
from chemeascode.foundation.workspace import Workspace
from pathlib import Path


def main():
    ws = Workspace(Path("."))
    equipment = ws.parsed_lists(("equipment",)).get("equipment")
    basis, _ = load_basis((ws.root / BASIS_FILE).read_text(encoding="utf-8"))
    sheets = {}
    for p in datasheet_paths(ws):
        loaded = load(ws, p)
        if loaded.sheet is not None:
            sheets[loaded.sheet.tag.strip()] = loaded.sheet
    data = capcost()
    ratio = basis.cost_index.value / float(data["base_cepci"]["value"])
    given = {i.tag: i for i in basis.items}
    for item in equipment.equipment:
        tag = item.tag.strip()
        mine = given.get(tag)
        if mine is not None and (mine.cost is not None or mine.exclude):
            continue
        line = CostLine(tag, item.type or "")
        found = []
        _cost(line, item, sheets.get(tag), mine, ratio, data, found)
        if not any(f.rule.endswith("estimate-equipment-range") for f in found):
            continue
        row = data["correlations"][line.correlation]
        size = line.size
        if size < row["min"]:
            print(f"# {tag}: below the range ({size:g} {row['unit']}), not split")
            continue
        n = math.ceil(size / row["max"])
        unit = SimpleNamespace(correlation=line.correlation, size=size / n,
                               size_source=f"{size:g} {row['unit']} / {n}", fbm=None, fm=None, fp=None,
                               factor_source=None, cost=None, exclude=None)
        part = CostLine(tag, item.type or "")
        found = []
        _cost(part, item, sheets.get(tag), unit, ratio, data, found)
        if part.bare_module is None:
            print(f"# {tag}: {n} units of {size / n:.4g} {row['unit']}: {part.status} ({part.notes}); not priced")
            continue
        total = n * part.bare_module
        print(f"  - {{tag: {tag}, cost: {total:.0f}, currency: USD, year: {basis.cost_index.year}, status: ASSUMED, "
              f"source: \"{n} identical units of {size / n:.4g} {row['unit']} (the item's {row['attribute']} {size:.4g} "
              f"{row['unit']}, {line.size_source}, over the correlation's maximum {row['max']:g}), each "
              f"{part.bare_module:.0f} USD bare module ({row['title']}, Turton et al. CAPCOST correlation of the package, "
              f"FBM {part.fbm:.3g}, CEPCI {basis.cost_index.value:g} / {float(data['base_cepci']['value']):g}); an upper "
              f"estimate: n small units cost more than one large item (D-044)\"}}")


if __name__ == "__main__":
    main()
