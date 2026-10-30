"""Material, pressure and bare module factors the package data lacks, and the items still
priced as split units (S5d, DESIGN.md D-045).

Run with `cheme run scripts/estimate_factors_s5d.py`; it writes nothing and prints the `items:`
entries for estimate/cost-basis.yaml, which are pasted there by hand (as
scripts/split_equipment_costs.py did in S5c, D-044). Each item is priced with core's own
functions (Turton et al. CAPCOST correlation and B1/B2 of the package, the project's CEPCI); this
script only supplies the factors below, each with its source, and splits an item above its
correlation's range into n = ceil(size / max) identical units (an upper estimate).

Sources (read 2026-10-30; numbers used, nothing copied):
- Cr-Mo material factors: Seider, Seader, Lewin and Widagdo, Product and Process Design
  Principles, 3rd ed. (Wiley, 2009), ch. 22, as implemented with that citation in IDAES
  `idaes/models/costing/SSLW.py` (github.com/IDAES/idaes-pse, main): shell-and-tube
  FM = a + (A / 100 ft2)^b, Cr-Mo shell / Cr-Mo tubes a 1.70, b 0.07 (`hx_material_factor_dict`,
  "Eq. 22.44 in the reference"); pressure vessels, low-alloy steel 1.2 (`VesselMaterial.
  LowAlloySteel`). BioSTEAM `design_tools/specification_factors` gives the same 1.2 citing the
  4th ed. (2017), pp. 426-485.
- Exchanger pressure factor above 140 barg: Turton's equation of the package (Table A.2,
  5-140 barg) evaluated at the design pressure, an extrapolation of at most 21 % in pressure
  (ASSUMED). Cross-check: the 600-3000 psig form noted in IDAES SSLW.py (commented out, not
  verified against the book) gives a 13 % rise from 140 to 170 barg against Turton's 5 %.
- Reformer furnace: Turton et al., 5th ed. (2018), Table A.1, reformer furnace, duty 3000 to
  100000 kW, K 3.068, 0.6597, 0.0194, as reproduced in OpenPyTEA `src/openpytea/data/
  cost_correlations.csv` row `reformer_furnace_turton_2001` (MIT licence). Bare module factor
  and pressure factor of fired heaters: Turton et al., 3rd ed., App. A, Tables A.2 and A.6
  (FBM CS 2.13, Cr-Mo 2.51, SS 2.81; log10 Fp = 0.1347 - 0.2368 log10 P + 0.1021 (log10 P)^2,
  10-200 barg), as reproduced in eqcost `internal/core/catalog.toml` (github.com/Jubel075/eqcost).
- Fans: Hand's installation factor for compressors 2.5 (Hand, 1958), as tabulated in
  M. F. van Amsterdam, Factorial Techniques applied in Chemical Plant Cost Estimation, MSc thesis
  TU Delft (2018), Table 3.13, p. 36 (ASSUMED analogy: a fan is a gas mover).
"""

import math
from pathlib import Path
from types import SimpleNamespace

from chemeascode.domains.assessment.equipment_cost import (
    BASIS_FILE,
    CostLine,
    _cost,
    capcost,
    load_basis,
    pressure_factor,
    purchased_cost,
    vessel_pressure_factor,
)
from chemeascode.domains.equipment.datasheets import datasheet_paths, load
from chemeascode.foundation.workspace import Workspace

FT2_PER_M2 = 10.7639
SEIDER_HX = ("Seider et al. 3rd ed. (2009) ch. 22 shell-and-tube material factor FM = a + (A/100 ft2)^b, "
             "Cr-Mo/Cr-Mo a 1.70, b 0.07, per-unit area, via IDAES SSLW.py hx_material_factor_dict "
             "(ASSUMED: a Seider factor in Turton's B1 + B2 Fm Fp)")
SEIDER_VESSEL = ("Seider et al. 3rd ed. (2009) ch. 22, pressure vessel material factor low-alloy steel 1.2 "
                 "(IDAES SSLW.py VesselMaterial.LowAlloySteel; BioSTEAM specification_factors, 4th ed. "
                 "pp. 426-485) (ASSUMED: a Seider factor in Turton's B1 + B2 Fm Fp)")
TURTON_HX_FP = "Turton Table A.2 exchanger Fp (5-140 barg) at the design pressure {p:g} barg, extrapolated (ASSUMED)"

CRMO_HX = {"E-101", "E-104", "E-105", "E-201", "E-401", "E-402", "E-501", "E-502"}
CRMO_VESSELS = {"V-101", "R-100", "R-201", "R-202", "R-401", "R-501"}
# design pressure of the pumps, not in the equipment list: the receiving equipment's design
# pressure (D-032 rule), static head and line losses not counted (ASSUMED)
PUMP_P = {"P-301A": (33.0, "C-301 design pressure 33 barg"), "P-301B": (33.0, "C-301 design pressure 33 barg"),
          "P-801": (49.5, "U-801 steam system design pressure 49.5 barg")}


def overrides(tag, item, area_unit, data):
    """fm, fp, fbm and their source for one item (or one split unit of *area_unit*)."""
    fm = fp = fbm = None
    why = []
    if tag in CRMO_HX:
        fm = 1.70 + (area_unit * FT2_PER_M2 / 100) ** 0.07
        why.append(f"Fm {fm:.3f}: {SEIDER_HX}")
    if tag in CRMO_VESSELS:
        fm = 1.2
        why.append(f"Fm 1.2: {SEIDER_VESSEL}")
    if tag == "R-102":
        fm = 1.0
        why.append("Fm 1.0: refractory-lined, the lining holds the shell at a carbon-steel temperature; shell "
                   "priced as a CS vessel on its outside diameter, the lining itself not priced (ASSUMED, D-045)")
    if item.type == "TubularHeatExchanger" and (item.design_pressure_barg or 0) > 140:
        row = data["pressure"]["hx_fixed_tube"]
        fp = pressure_factor(row["C"], item.design_pressure_barg)
        why.append(f"Fp {fp:.3f}: " + TURTON_HX_FP.format(p=item.design_pressure_barg))
    if tag == "E-106":
        fp = 1.0
        why.append("Fp 1.0: combustion air and flue gas within a few kPa of atmospheric (K-102, K-103: 5 kPa); "
                   "Turton's exchanger Fp is 1 below 5 barg")
    if tag in PUMP_P:
        p, src = PUMP_P[tag]
        fp = pressure_factor(data["pressure"]["pump_centrifugal"]["C"], p)
        why.append(f"Fp {fp:.3f}: Turton Table A.2 pump Fp at {p:g} barg ({src}; D-032 rule, ASSUMED)")
    if tag in {"K-102", "K-103"}:
        fbm = 2.5
        why.append("FBM 2.5: Hand's factor for compressors (Hand 1958, van Amsterdam MSc thesis TU Delft 2018, "
                   "Table 3.13, p. 36), ASSUMED for a fan")
    if tag == "V-502":
        b1, b2 = data["bare_module"]["vessel_vertical"]["B"]
        fpv = vessel_pressure_factor(item.design_pressure_barg, item.dimensions.diameter)
        fbm = b1 + b2 * 1.0 * fpv
        why.append(f"FBM {fbm:.3f} = B1 {b1} + B2 {b2} x Fm 1 (LTCS as CS) x Fp {fpv:.3f} (Turton vessel Fp at "
                   f"{item.design_pressure_barg:g} barg, D {item.dimensions.diameter:g} m): the package's vertical "
                   "vessel B1, B2 for a horizontal vessel, whose own pair the package does not hold (ASSUMED)")
    return fm, fp, fbm, "; ".join(why)


def reformer_furnace(ratio):
    duty = 68616.0  # kW, H-101 datasheet type_specific.duty_kw (absorbed radiant duty, Q9)
    lg = math.log10(duty)
    cp0 = 10 ** (3.068 + 0.6597 * lg + 0.0194 * lg**2)
    p = 44.0  # barg, R-101 tube design pressure (equipment list)
    lp = math.log10(p)
    fp = 10 ** (0.1347 - 0.2368 * lp + 0.1021 * lp**2)
    fbm = 2.81
    cost = cp0 * fbm * fp * ratio
    print(f"  - {{tag: H-101, cost: {cost:.0f}, currency: USD, year: 2023, status: ASSUMED, source: \"reformer furnace, "
          f"Turton et al. 5th ed. Table A.1 (K 3.068, 0.6597, 0.0194; 3000-100000 kW; OpenPyTEA "
          f"cost_correlations.csv reformer_furnace_turton_2001) at the absorbed radiant duty {duty:g} kW (datasheet "
          f"type_specific.duty_kw): Cp0 {cp0:.0f} USD (CEPCI 397) x FBM {fbm} (fired heater, stainless tubes; Turton 3rd "
          f"ed. Table A.6 via eqcost catalog.toml; ASSUMED for the cast heat-resistant alloy tubes of R-101) x Fp "
          f"{fp:.3f} (Turton Table A.2 fired heater, R-101 tube design pressure {p:g} barg) x CEPCI 797.9 / 397; "
          f"includes the catalyst tubes R-101; the convection coils E-101 to E-107 are priced as their own items (D-045)\"}}")


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
    reformer_furnace(ratio)
    for item in equipment.equipment:
        tag = item.tag.strip()
        mine = given.get(tag)
        if mine is not None and (mine.cost is not None or mine.exclude):
            continue
        line = CostLine(tag, item.type or "")
        found = []
        _cost(line, item, sheets.get(tag), mine, ratio, data, found)
        if line.size is None or line.correlation is None:
            continue
        row = data["correlations"][line.correlation]
        size = line.size
        n = max(1, math.ceil(size / row["max"]))
        fm, fp, fbm, why = overrides(tag, item, size / n, data)
        if not why:
            continue
        if n == 1:
            fields = [f"tag: {tag}"]
            fields += [f"fm: {fm:.4g}"] if fm is not None else []
            fields += [f"fp: {fp:.4g}"] if fp is not None else []
            fields += [f"fbm: {fbm:.4g}"] if fbm is not None else []
            print(f"  - {{{', '.join(fields)}, factor_source: \"{why} (D-045)\"}}")
            continue
        unit = SimpleNamespace(correlation=line.correlation, size=size / n, size_source=f"{size:g} / {n}",
                               fbm=fbm, fm=fm, fp=fp, factor_source=why, cost=None, exclude=None)
        part = CostLine(tag, item.type or "")
        found = []
        _cost(part, item, sheets.get(tag), unit, ratio, data, found)
        if part.bare_module is None:
            print(f"# {tag}: {n} units of {size / n:.4g} {row['unit']}: {part.status} ({part.notes}); not priced")
            continue
        total = n * part.bare_module
        print(f"  - {{tag: {tag}, cost: {total:.0f}, currency: USD, year: {basis.cost_index.year}, status: ASSUMED, "
              f"source: \"{n} identical units of {size / n:.4g} {row['unit']} (the item's {row['attribute']} {size:.4g} "
              f"{row['unit']}, {line.size_source.split(' (')[0]}, over the correlation's maximum {row['max']:g}), each "
              f"{part.bare_module:.0f} USD bare module ({row['title']}, Turton et al. CAPCOST correlation of the package, "
              f"FBM {part.fbm:.3g} = B1 + B2 Fm Fp; {why}; CEPCI {basis.cost_index.value:g} / "
              f"{float(data['base_cepci']['value']):g}); an upper estimate: n small units cost more than one large "
              f"item (D-045)\"}}")


if __name__ == "__main__":
    main()
