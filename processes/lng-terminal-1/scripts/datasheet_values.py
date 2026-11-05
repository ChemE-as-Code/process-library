"""Complete the equipment datasheets that `cheme datasheets draft` wrote (DESIGN.md D-022).

Provenance (run once: `cheme run scripts/datasheet_values.py`; the datasheets are maintained by
hand afterwards). `cheme datasheets fill` cannot size these items: no benchmarked property
package covers LNG or BOG (D-006), and most pumps and vessels have no flowsheet stream of their
own. The values come from scripts/terminal_sizing.py (GERG-2008 via CoolProp) and the
assumptions of DESIGN.md D-007 to D-018, each with its source; what only a supplier can give is
marked `supplier`. The draft flag is removed: these are basic-engineering datasheets with
ASSUMED values, not supplier data.
"""

from pathlib import Path

import yaml

RHO = 445.0          # kg/m3 LNG at 115 kPa(a), scripts/terminal_sizing.py (D-006)
G = 9.81
SZ = "scripts/terminal_sizing.py"


def q(value, unit, source, assumed=True):
    d = {"value": value, "unit": unit, "source": source}
    if assumed:
        d["assumed"] = True
    return d


def pump(flow_m3h, dp_kpa, eff, npsha_m, p_suc, t_suc, src, fluid="LNG", rho=RHO):
    head = dp_kpa * 1e3 / (rho * G)
    shaft = flow_m3h / 3600 * dp_kpa * 1e3 / eff / 1e3
    op = {"fluid": {"value": fluid, "source": src},
          "suction_pressure": q(p_suc, "kPa(a)", src), "suction_temperature": q(t_suc, "°C", src),
          "discharge_pressure": q(round(p_suc + dp_kpa, 1), "kPa(a)", src),
          "flow": q(flow_m3h, "m3/h", src)}
    ts = {"flow_m3_h": q(flow_m3h, "m3/h", src),
          "differential_head_m": q(round(head, 1), "m", f"{src}: dp {dp_kpa} kPa / (rho g), rho {rho} kg/m3"),
          "npsh_available_m": q(npsha_m, "m", src),
          "shaft_power_kw": q(round(shaft, 1), "kW", f"{src}: flow x dp / efficiency {eff} (ASSUMED)")}
    return op, ts


def vessel(p, t, flow, src):
    return {"pressure": q(p, "kPa(a)", src), "temperature": q(t, "°C", src), "flow": q(flow, "kg/h", src)}


def values(tag: str, kind: str):
    """(operating, type_specific) for one item."""
    if tag.startswith("P-") and tag[3] == "1" and tag[2] in "23" and tag[-1] in "ABCD":
        return pump(3000, 577, 0.75, 2.5, 115.0, -160.2,
                    f"{SZ}: 4 x 3,000 m3/h for 12,000 m3/h, differential 577 kPa (D-011); NPSHa the submergence at low-low level, ASSUMED")
    if tag in ("P-2102", "P-3102"):
        return pump(500, 262, 0.60, 2.5, 115.0, -160.2,
                    f"{SZ}: circulation ~314 m3/h, rated 500 m3/h; differential for the 2 x 2.45 km loop at circulation flow plus the return, ASSUMED (D-008, D-011)")
    if tag in ("P-5101", "P-6101"):
        return pump(60, 335, 0.50, 1.5, 110.0, -160.0,
                    "D-016: empties the jetty drain drum in ~1 h into the platform crossover (~445 kPa(a)); NPSHa the drum elevation above the pump, ASSUMED")
    if tag in ("P-8101A", "P-8101B"):
        return pump(30, 400, 0.50, 1.5, 105.0, -160.0,
                    "D-017: flare knock-out drum liquids to the site liquid burner at ~500 kPa(a), ASSUMED")
    if tag == "P-8102":
        return pump(50, 294, 0.60, 8.0, 101.3, 10.0,
                    "D-018: rainwater from the 6 m deep sump to the oily water system, 30 m head, ASSUMED",
                    fluid="Rainwater", rho=1000.0)
    if kind == "CentrifugalCompressor":
        src = f"{SZ}: 27 t/h each (50 % of the loading BOG + 10 %), 108 -> 600 kPa(a), -140 degC suction, polytropic 0.78, ideal gas (D-010)"
        op = {"fluid": {"value": "Boil-off gas (CH4 92 %, N2 8 % mol)", "source": SZ},
              "suction_pressure": q(108.0, "kPa(a)", src), "suction_temperature": q(-140.0, "°C", src),
              "discharge_pressure": q(600.0, "kPa(a)", src), "discharge_temperature": q(-49.1, "°C", src),
              "flow": q(27000, "kg/h", src)}
        ts = {"fluid_power_kw": q(1397, "kW", src),
              "shaft_power_kw": q(1426, "kW", f"{src}; mechanical efficiency 0.98 ASSUMED")}
        return op, ts
    if kind == "Tank" and tag in ("T-2101", "T-3101"):
        src = f"{SZ}: tank pressure 115 kPa(a), LNG at its bubble point (D-006, D-007)"
        return {"pressure": q(115.0, "kPa(a)", src), "temperature": q(-160.2, "°C", src),
                "working_volume": q(225000, "m3", "D-007: LNG Canada tank 1 (S-08); tank 2 ASSUMED equal", assumed=False)}, {}
    if kind == "Tank":
        return {"pressure": q(101.3, "kPa(a)", "D-018: open sump"), "temperature": q(-160.0, "°C",
                "D-018: design for an LNG spill; normally rainwater")}, {}
    if tag == "D-7101":
        return vessel(108.0, -140.0, 54000, f"{SZ}: loading BOG 49.1 t/h + 10 % (D-010)"), {}
    if tag in ("D-5101", "D-6101"):
        return vessel(110.0, -160.0, 0, "D-016: drains after loading and the surge relief; batch, ASSUMED"), {}
    if tag == "D-8101":
        return vessel(105.0, -150.0, 54000, "D-017: design case the BOG compressor trip at loading, ASSUMED"), {}
    if kind == "Flare":
        return vessel(105.0, -150.0, 54000, "D-017: storage and loading flare design case; routine 6.0 m3/min (S-02)"), {}
    if kind == "LoadingUnloadingSystem":
        if tag[-1] == "2":
            src = f"{SZ}: carrier return 45.6 t/h at -120 degC (D-009, D-014)"
            return {"fluid": {"value": "Boil-off gas", "source": src}, "pressure": q(106.0, "kPa(a)", src),
                    "temperature": q(-120.0, "°C", src), "flow": q(45600, "kg/h", src)}, {}
        src = f"{SZ}: 12,000 m3/h over three liquid-capable arms, ~4,000 m3/h each; 350 kPa(a) at the manifold (D-011, D-014)"
        return {"fluid": {"value": "LNG", "source": src}, "pressure": q(350.0, "kPa(a)", src),
                "temperature": q(-160.2, "°C", src), "flow": q(4000, "m3/h", src)}, {}
    raise KeyError(tag)


def fill_tbd(d: dict, new: dict) -> None:
    for k, v in new.items():
        if isinstance(d.get(k), dict) and d[k].get("value") == "TBD":
            d[k] = v
        elif k not in d:
            d[k] = v


def main() -> None:
    for path in sorted(Path("equipment/datasheets").glob("*.yaml")):
        ds = yaml.safe_load(path.read_text())
        op, ts = values(ds["tag"], ds["type"])
        operating = ds.get("operating") or {}
        operating.pop("conditions", None)
        fill_tbd(operating, op)
        ds["operating"] = operating
        if ts:
            ds.setdefault("type_specific", {})
            fill_tbd(ds["type_specific"], ts)
        ds.pop("supplier_data", None)
        if ds["type"] in ("CentrifugalPump", "CentrifugalCompressor", "LoadingUnloadingSystem", "Flare"):
            ds.setdefault("type_specific", {})["vendor_data"] = {
                "value": "supplier", "source": "vendor package: curves, seals, motor, envelope (enquiry in detail engineering)"}
        ds.pop("draft", None)
        ds["sizing_basis"] = [{"parameter": "basis", "value": "scripts/terminal_sizing.py (GERG-2008 via CoolProp) and the assumptions of DESIGN.md D-007 to D-018, ASSUMED where marked",
                               "reference": "D-022"}]
        head = ("# Equipment datasheet. Schema: `cheme schema datasheet`. Drafted by `cheme datasheets draft`,\n"
                "# completed by scripts/datasheet_values.py (D-022); maintained by hand from now on.\n")
        path.write_text(head + yaml.safe_dump(ds, sort_keys=False, width=100, allow_unicode=True), encoding="utf-8")
        print(f"wrote {path}")


if __name__ == "__main__":
    main()
