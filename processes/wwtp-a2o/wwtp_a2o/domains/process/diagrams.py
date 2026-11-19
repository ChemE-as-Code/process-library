"""Translate the shared input/topology to native ChemE engineering-view documents."""

from wwtp_a2o.domains.process.model import GROUPS, connections, validate_inputs


def project_documents(data: dict) -> dict:
    validate_inputs(data)
    group = {uid: name for name, ids in GROUPS.items() for uid in ids}
    block_ports = {name: [] for name in GROUPS}
    step_ports = {uid: [] for uid in group}
    streams = []
    for sid, a, b, _flow in connections(data):
        for uid, direction in ((a, "out"), (b, "in")):
            if uid not in group:
                continue
            p = {"id": sid, "direction": direction}
            if group.get(a) != group.get(b):
                p["delegates"] = sid
                block_ports[group[uid]].append({"id": sid, "direction": direction})
            step_ports[uid].append(p)
        streams.append(
            {
                "id": sid,
                "title": sid.replace("_", " ").title(),
                "from": f"{a}.{sid}" if a in group else f"{a}.out",
                "to": f"{b}.{sid}" if b in group else f"{b}.in",
                "template": "wastewater",
                "state": {},
            }
        )
    titles = {
        "ANAEROBIC": "Anaerobic zone (A1, A2)",
        "ANOXIC": "Anoxic zone (A3, A4)",
        "AEROBIC": "Aerobic zone (O1, O2, O3)",
        "CLARIFIER": "Secondary clarifier",
    }
    flowsheet = {
        "schema": "cheme/process/v1",
        "kind": "flowsheet",
        "title": "Generic A2/O waterline - EXPOsan ASM2d example",
        "cases": [
            {
                "id": data["case_id"],
                "default": True,
                "provenance": "assumed",
                "source": "process/case-inputs.json",
                "description": data["description"],
            }
        ],
        "feeds": [
            {
                "id": "INF",
                "title": "Wastewater influent",
                "category": "wastewater",
                "ports": [{"id": "out", "direction": "out"}],
            }
        ],
        "products": [
            {
                "id": uid,
                "title": title,
                "category": "wastewater",
                "ports": [{"id": "in", "direction": "in"}],
            }
            for uid, title in [("EFF", "Treated effluent"), ("SLUDGE", "Waste sludge")]
        ],
        "blocks": [
            {"id": name, "title": titles[name], "class": "ProcessStep", "ports": block_ports[name]}
            for name in GROUPS
        ],
        "steps": [
            {
                "id": uid,
                "block": group[uid],
                "class": "ProcessStep",
                "title": f"{uid}: {data['reactor_volumes_m3'][uid]:g} m3"
                if uid != "C1"
                else f"C1: {data['clarifier']['N_layer']}-layer nonreactive settler",
                "ports": step_ports[uid],
            }
            for uid in group
        ],
        "streams": streams,
    }
    materials = {
        "schema": "cheme/process/v1",
        "kind": "materials",
        "components": [
            {
                "id": "aqueous_carrier",
                "name": "Unspecified aqueous carrier; ASM fractions are recorded separately",
            }
        ],
        "templates": [
            {
                "id": "wastewater",
                "title": "Wastewater / mixed liquor / sludge",
                "components": ["aqueous_carrier"],
            }
        ],
    }
    plant = {
        "schema": "cheme/plant/v1",
        "name": "A2/O wastewater example",
        "requires": "cheme-as-code>=0.8",
        "units": "SI",
        "stage": "concept",
        "description": (
            "Local direct QSDsan connection. Generic example; no plant validation"
            " or design sign-off."
        ),
        "sheets": [
            {
                "id": x,
                "kind": x.lower(),
                "file": f"process/{x}.xml",
                "title": f"{x}: A2/O waterline",
            }
            for x in ("BFD", "PFD")
        ],
    }

    return {
        "process/flowsheet.yaml": flowsheet,
        "process/materials.yaml": materials,
        "plant.yaml": plant,
    }
