"""Write an English evidence page; it never changes a model or a saved result."""

import csv
import json
from html import escape
from pathlib import Path
from string import Template


def write_saved_report(run: Path, data: dict, result: dict) -> None:
    """Present persisted values; preserve historical reports and table precision."""

    def rows(name):
        with (run / name).open(encoding="utf-8-sig", newline="") as handle:
            return [
                {
                    k: (v if k in ("stream", "from", "to", "reactor") else float(v))
                    for k, v in row.items()
                }
                for row in csv.DictReader(handle)
            ]

    write_report(run, data, result, rows("streams.csv"), rows("reactors.csv"))


def write_report(run, data, result, streams, reactors):

    def table(headers, rows):
        return (
            '<div class="scroll"><table><thead><tr>'
            + "".join(f"<th>{escape(str(h))}</th>" for h in headers)
            + "</tr></thead><tbody>"
            + "".join(
                "<tr>" + "".join(f"<td>{escape(str(x))}</td>" for x in row) + "</tr>"
                for row in rows
            )
            + "</tbody></table></div>"
        )

    def n(value):
        return f"{value:,.5f}"

    base = "./"
    eff = table(
        ["Quantity", "Influent", "Effluent", "Unit"],
        [
            (k, n(result["influent"][k]), n(v), result["metric_units"][k])
            for k, v in result["effluent"].items()
        ],
    )
    checks = table(
        ["Check", "Result"],
        [
            (k.replace("_", " "), "passed" if v else "FAILED")
            for k, v in result["basic_checks"].items()
        ],
    )
    zone = table(
        ["Calculation tank", "Volume (m3)", "DO (mg O2/L)", "NO3 (mg N/L)", "NH4 (mg N/L)"],
        [
            (
                r["reactor"],
                n(r["volume_m3"]),
                n(r["DO_mg_O2_L"]),
                n(r["NO3_mg_N_L"]),
                n(r["NH4_mg_N_L"]),
            )
            for r in reactors
        ],
    )
    flows = table(
        ["Stream", "From → to", "m3/day", "COD (mg COD/L)", "TN (mg N/L)", "TP (mg P/L)"],
        [
            (
                s["stream"],
                s["from"] + " → " + s["to"],
                n(s["flow"]),
                n(s["COD"]),
                n(s["TN"]),
                n(s["TP"]),
            )
            for s in streams
        ],
    )
    inp = data["influent"]
    inputs = table(
        ["Input", "Value", "Basis"],
        [
            ("Influent flow", f"{inp['flow_m3_d']:g} m3/day", "EXPOsan software example"),
            ("Temperature", f"{inp['temperature_K'] - 273.15:g} °C", "EXPOsan software example"),
            (
                "Anaerobic zone",
                "A1 + A2: " + str(sum(data["reactor_volumes_m3"][x] for x in ("A1", "A2"))) + " m3",
                "EXPOsan software example",
            ),
            (
                "Anoxic zone",
                "A3 + A4: " + str(sum(data["reactor_volumes_m3"][x] for x in ("A3", "A4"))) + " m3",
                "EXPOsan software example",
            ),
            (
                "Aerobic zone",
                "O1 + O2 + O3: "
                + str(sum(data["reactor_volumes_m3"][x] for x in ("O1", "O2", "O3")))
                + " m3",
                "EXPOsan software example",
            ),
            (
                "KLa",
                str(data["aeration"]["kla_per_day"]) + " /day",
                "Example oxygen transfer; not fixed DO",
            ),
            (
                "Internal recycle",
                f"{data['recycles']['internal_m3_d']:g} m3/day",
                "EXPOsan software example",
            ),
            (
                "Return sludge",
                f"{data['recycles']['return_sludge_m3_d']:g} m3/day",
                "EXPOsan software example",
            ),
            (
                "Waste sludge",
                f"{data['recycles']['waste_sludge_m3_d']:g} m3/day",
                "EXPOsan software example",
            ),
            ("Integration", str(data["solver"]), "Local numerical settings"),
        ],
    )
    filenames = [
        "inputs.json",
        "model_parameters.json",
        "influent_components.csv",
        "reactors.csv",
        "streams.csv",
        "trajectory.csv",
        "result.json",
        "adapter-result.json",
        "adapter_validation.log",
        "manifest.json",
        "run.log",
    ]
    links = " ".join(
        f'<a class="button" href="{base}{f}" target="_blank">{f}</a>'
        for f in filenames
        if (run / f).is_file()
    )
    remaining = "".join(
        (
            f"<li>{escape(k.replace('_', ' '))}: <b>{escape(v.replace('_', ' '))}</b></li>"
            for k, v in result["verification"].items()
        )
    )
    limitations = "".join(f"<li>{escape(x)}</li>" for x in result["limitations"])
    html = Template(
        (Path(__file__).parent / "templates/report.html").read_text(encoding="utf-8")
    ).substitute(
        field_0=escape(run.name),
        field_1=format(data["solver"]["days"], "g"),
        field_2=result["versions"]["qsdsan"],
        field_3=result["versions"]["exposan"],
        field_4=escape(result["status"]),
        field_5="passed" if all(result["basic_checks"].values()) else "FAILED",
        field_6=result["steady_state_screen"]["status"].replace("_", " "),
        field_7=format(result["steady_state_screen"]["window_days"], "g"),
        field_8=eff,
        field_9=checks,
        field_10=base,
        field_11=escape(data["basis"]["source"]),
        field_12=inputs,
        field_13=escape(json.dumps(data, indent=2)),
        field_14=zone,
        field_15=flows,
        field_16=remaining,
        field_17=escape(json.dumps(result["steady_state_screen"], indent=2)),
        field_18=limitations,
        field_19=format(result["elapsed_total_s"], ".2f"),
        field_20=links,
        field_21=escape(json.dumps(result["versions"], indent=2)),
    )
    (run / "report.html").write_text(html, encoding="utf-8")
