"""Input validation and hydraulic topology; no simulator or UI imports."""

import math

REACTORS = ("A1", "A2", "A3", "A4", "O1", "O2", "O3")
GROUPS = {
    "ANAEROBIC": ("A1", "A2"),
    "ANOXIC": ("A3", "A4"),
    "AEROBIC": ("O1", "O2", "O3"),
    "CLARIFIER": ("C1",),
}


def validate_inputs(data):
    def positive(value, name, zero=False):
        if not isinstance(value, (int, float)) or not math.isfinite(value):
            raise ValueError(f"{name} must be a finite number")
        if value < 0 or (value == 0 and not zero):
            raise ValueError(f"{name} must be {'nonnegative' if zero else 'positive'}")

    if set(data["reactor_volumes_m3"]) != set(REACTORS):
        raise ValueError("The example requires exactly A1-A4 and O1-O3")
    for k, v in data["reactor_volumes_m3"].items():
        positive(v, k)
    positive(data["influent"]["flow_m3_d"], "influent flow")
    positive(data["influent"]["temperature_K"], "temperature")
    for k, v in data["influent"]["components_mg_L"].items():
        positive(v, k, zero=True)
    for k, v in data["recycles"].items():
        positive(v, k)
    if data["recycles"]["waste_sludge_m3_d"] >= data["influent"]["flow_m3_d"]:
        raise ValueError("Waste sludge flow must be less than influent flow")
    if set(data["aeration"]["kla_per_day"]) != {"O1", "O2", "O3"}:
        raise ValueError("Specify KLa for O1, O2 and O3")
    for k, v in data["aeration"]["kla_per_day"].items():
        positive(v, k + " KLa", zero=True)
    positive(data["aeration"]["do_saturation_mg_O2_L"], "oxygen saturation")
    for k in ("days", "rtol", "atol", "max_step_days"):
        positive(data["solver"][k], k)
    if data["solver"]["method"] not in ("BDF", "Radau", "LSODA"):
        raise ValueError("Supported solvers: BDF, Radau, LSODA")
    for k, v in data["screening"].items():
        positive(v, "screening." + k)


def connections(data):
    q = data["influent"]["flow_m3_d"]
    r = data["recycles"]
    qr, qi, qw = r["return_sludge_m3_d"], r["internal_m3_d"], r["waste_sludge_m3_d"]
    result = [
        ("INFLUENT", "INF", "A1", q),
        ("RAS", "C1", "A1", qr),
        ("INTERNAL", "O3", "A3", qi),
        ("TO_CLARIFIER", "O3", "C1", q + qr),
        ("EFFLUENT", "C1", "EFF", q - qw),
        ("WAS", "C1", "SLUDGE", qw),
    ]
    for a, b in zip(REACTORS[:-1], REACTORS[1:], strict=True):
        result.append((a + "_OUT", a, b, q + qr + (0 if a in ("A1", "A2") else qi)))
    return result
