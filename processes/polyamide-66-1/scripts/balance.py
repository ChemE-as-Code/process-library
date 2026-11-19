"""What core cannot calculate in the polyamide 66 plant (DESIGN.md D-006, D-007, D-009).

Year-average flows (kg/h, the recipe's basis, D-003). cheme process propagate computes the
streams and the duties of the semi-batch neutraliser R101 (Q1) and the polycondensation R201
(Q4, a conversion step: the mass heated from 383.15 to 548.15 K with the reaction's heat). This
script gives the duties of the steps that are no model of core, from the streams propagate
wrote and the component data of process/materials.yaml:

- Q2, E101: the acid slurry S3 warmed from 298.15 to 338.15 K on the jacket (LP steam);
- Q3, X201: the concentration to 70 wt% salt: the salt solution S5 warmed from 338.15 to
  383.15 K and the water of S6 evaporated at 383.15 K (hot oil);
- Q5, X202: the steam bleed, depressurisation and finishing: the water and the diamine of S9
  evaporated at the mass's 548.15 K; R201 has already heated them as liquid to 548.15 K (hot
  oil);
- Q6, E-201: the vapours S6 and S9 condensed and the condensate cooled to 313.15 K (cooling
  water); the superheat of S9 after the let-down is taken as the latent heat at 548.15 K on the
  liquid path (the same state function, D-009);
- Q7, X-301: the melt S10 cooled from 548.15 to 323.15 K in the strand bath, whose water is
  cooled by cooling water; the heat of crystallisation is not counted (no open value, L-3).

The autoclave's and the dissolver's steel heated each batch is not counted (D-009).

Run: `cheme run scripts/balance.py`, after `cheme process propagate --fill`. With
BALANCE_OUTPUT set it writes the values the flowsheet cites (library ADR 0027).

Latent heats (kJ/kmol), single values queried from the thermo 0.6.1 package (DESIGN.md SRC-5;
library ADR 0037): water, method HEOS_FIT (thermo's fit to IAPWS-95), 40 167.7 at 383.15 K and
28 360.8 at 548.15 K; hexamethylenediamine, method MORGAN_KOBAYASHI (an estimation from the
critical constants), 41 968.0 at 548.15 K.
"""

from __future__ import annotations

import json
import os
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent

T_FEED = 298.15  # K, S1 and S2
T_SALT = 338.15  # K, R101 (SRC-1: the salt solution at 65 C)
T_CONC = 383.15  # K, X201 (SRC-1: the continuous concentrator at about 110 C)
T_POLY = 548.15  # K, R201 and X202 (SRC-1: the batch mass at about 275 C)
T_COND = 313.15  # K, E-201's condensate
T_PELLET = 323.15  # K, the pellets leaving the strand bath (ASSUMED, D-007)
HVAP = {  # kJ/kmol at temperature, thermo 0.6.1 (see the docstring)
    ("H2O", T_CONC): 40167.7,
    ("H2O", T_POLY): 28360.8,
    ("HMDA", T_POLY): 41968.0,
}


def _flowsheet() -> dict:
    return yaml.safe_load((ROOT / "process" / "flowsheet.yaml").read_text())


def _materials() -> dict:
    data = yaml.safe_load((ROOT / "process" / "materials.yaml").read_text())
    return {c["id"]: c for c in data["components"]}


def _kmol(fs: dict, comps: dict, sid: str) -> dict[str, float]:
    """kmol/h of each component of stream sid (design case)."""
    stream = next(s for s in fs["streams"] if s["id"] == sid)
    state = stream["state"]["design"]
    flow = state["flow"]["value"]
    comp = state["composition"]
    values = comp["values"]
    if comp["basis"] == "mole_fraction":
        mean = sum(x * comps[c]["molar_mass"] for c, x in values.items())
        return {c: flow * x / mean for c, x in values.items()}
    return {c: flow * x / comps[c]["molar_mass"] for c, x in values.items()}


def _sensible(n: dict[str, float], comps: dict, t0: float, t1: float) -> float:
    """kW to take the stream from t0 to t1 at the materials' liquid heat capacities."""
    return sum(v * comps[c]["liquid_heat_capacity"] for c, v in n.items()) * (t1 - t0) / 3600.0


def _latent(n: dict[str, float], t: float) -> float:
    return sum(v * HVAP[(c, t)] for c, v in n.items() if v > 0.0) / 3600.0


def main() -> None:
    fs, comps = _flowsheet(), _materials()
    s3 = _kmol(fs, comps, "S3")
    s5 = _kmol(fs, comps, "S5")
    s6 = _kmol(fs, comps, "S6")
    s9 = _kmol(fs, comps, "S9")
    s10 = _kmol(fs, comps, "S10")

    q2 = _sensible(s3, comps, T_FEED, T_SALT)
    q3_sens = _sensible(s5, comps, T_SALT, T_CONC)
    q3_lat = _latent(s6, T_CONC)
    q3 = q3_sens + q3_lat
    q5 = _latent(s9, T_POLY)
    q6 = (
        _latent(s6, T_CONC)
        + _sensible(s6, comps, T_COND, T_CONC)
        + _latent(s9, T_POLY)
        + _sensible(s9, comps, T_COND, T_POLY)
    )
    q7 = _sensible(s10, comps, T_PELLET, T_POLY)

    print(f"Q2 E101 slurry warming:          {q2:.6g} kW")
    print(f"Q3 X201 concentration:           {q3:.6g} kW (sensible {q3_sens:.4g}, latent {q3_lat:.4g})")
    print(f"Q5 X202 steam bleed, finishing:  {q5:.6g} kW")
    print(f"Q6 E-201 condenser:              {q6:.6g} kW")
    print(f"Q7 X-301 strand quench:          {q7:.6g} kW")

    target = os.environ.get("BALANCE_OUTPUT")
    if target:
        Path(target).write_text(
            json.dumps(
                {
                    "contract": "balance-output/1",
                    "script": "scripts/balance.py",
                    "cases": {
                        "design": {
                            "Q2": {"duty": round(q2, 4)},
                            "Q3": {"duty": round(q3, 4)},
                            "Q5": {"duty": round(q5, 4)},
                            "Q6": {"duty": round(q6, 4)},
                            "Q7": {"duty": round(q7, 4)},
                        }
                    },
                },
                indent=2,
            )
        )


if __name__ == "__main__":
    main()
