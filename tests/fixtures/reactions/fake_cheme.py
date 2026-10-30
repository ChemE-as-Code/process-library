"""A stand-in for ``cheme chemistry library [entry] --json`` (synthetic entries), for the
template matches of tests/test_reactions.py."""

import json
import sys

COMPONENTS = {
    "H2": {"id": "H2", "cas": "1333-74-0"},
    "O2": {"id": "O2", "cas": "7782-44-7"},
    "H2O": {"id": "H2O", "cas": "7732-18-5"},
    "N2": {"id": "N2", "cas": "7727-37-9"},
    "NH3": {"id": "NH3", "cas": "7664-41-7"},
}
ENTRIES = {
    "ammonia": {
        "title": "Fixture ammonia synthesis",
        "model_basis": {"kind": "equilibrium"},
        "reactions": [{"id": "NH3_SYN", "stoichiometry": {"N2": -1, "H2": -3, "NH3": 2}, "reversible": True}],
    },
    "burner": {
        "title": "Fixture hydrogen burner",
        "model_basis": {"kind": "stoichiometry_only"},
        "reactions": [{"id": "H2_COMB", "stoichiometry": {"H2": -2, "O2": -1, "H2O": 2}, "reversible": False}],
    },
}

args = [a for a in sys.argv[1:] if a != "--json"]
assert args[:2] == ["chemistry", "library"], args
if len(args) == 2:
    print(json.dumps({k: v["title"] for k, v in ENTRIES.items()}))
else:
    entry = ENTRIES[args[2]]
    used = {s for r in entry["reactions"] for s in r["stoichiometry"]}
    print(json.dumps({"id": args[2], **entry, "components": [COMPONENTS[s] for s in sorted(used)]}))
