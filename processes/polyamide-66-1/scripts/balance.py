"""What core cannot calculate in the polyamide 66 plant (DESIGN.md D-006, D-007, D-009).

Year-average flows (kg/h, the recipe's basis, D-003). cheme process propagate computes the
streams and the duties of the semi-batch neutraliser R101 (Q1) and the polycondensation R201
(Q4, a conversion step: the mass heated from 383.15 to 548.15 K with the reaction's heat). This
script gives the duties of the steps that are no model of core, from the streams propagate
wrote and the component data of process/materials.yaml:

- Q2, E101: the acid slurry S3 warmed from 298.15 to 338.15 K on the jacket (LP steam);
- Q3, X201: the concentration to 70 wt% salt: the salt solution S5 warmed from 338.15 to
  383.15 K and the water of S6 evaporated from liquid at 383.15 K to vapour at S6's 383.15 K and
  101.325 kPa (hot oil);
- Q5, X202: the steam bleed, depressurisation and finishing: the water of S9 taken from the
  liquid at 548.15 K that R201 (Q4) leaves to vapour at S9's declared 548.15 K and 101.325 kPa,
  and the diamine of S9 evaporated at 548.15 K (hot oil). Q4 heats the water as liquid from
  383.15 to 548.15 K at the constant 75.4 kJ/(kmol K) of materials.yaml, so Q5 is the water's
  IAPWS-95 enthalpy change from liquid at 383.15 K to S9's vapour state less that 75.4 x 165:
  Q3 + Q4 + Q5 then carry the water's real enthalpy change. The bleed valve's let-down is
  isenthalpic, so the steam leaves the autoclave with the enthalpy of S9's state (D-006, D-009);
- Q6, E-201: the vapours S6 and S9 condensed and the condensate cooled to 313.15 K (cooling
  water): the water from S6's and S9's declared vapour states to liquid at 313.15 K and
  101.325 kPa (IAPWS-95), the diamine's latent heat at 548.15 K and its liquid heat capacity;
- Q7, X-301: the melt S10 cooled from 548.15 to 323.15 K in the strand bath, whose water is
  cooled by cooling water; the heat of crystallisation is not counted (no open value, L-3).

The autoclave's and the dissolver's steel heated each batch is not counted (D-009).

Run: `cheme run scripts/balance.py`, after `cheme process propagate --fill`. With
BALANCE_OUTPUT set it writes the values the flowsheet cites (library ADR 0027).

Water's enthalpies (kJ/kmol): IAPWS-95 as the chemicals 1.5.2 package implements it
(iapws95_properties(T, P), DESIGN.md SRC-5; library ADR 0037), the specific enthalpy times
IAPWS-95's molar mass 18.015268 kg/kmol: liquid at 313.15 K and 101.325 kPa 3 019.65, liquid at
383.15 K and 1750 kPa 8 333.59 (the liquid's enthalpy changes by about 1 kJ/kg between its
saturation pressure, 143.4 kPa, and 1750 kPa), vapour at 383.15 K and 101.325 kPa 48 572.49,
vapour at 548.15 K and 101.325 kPa 54 484.32. Hexamethylenediamine's latent heat at 548.15 K,
41 968.0 kJ/kmol, is a single value queried from the thermo 0.6.1 package (method
MORGAN_KOBAYASHI, an estimation from the critical constants).
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
    ("HMDA", T_POLY): 41968.0,
}
H_W = {  # kJ/kmol, water by IAPWS-95 (chemicals 1.5.2, see the docstring)
    "liq_cond": 3019.65,  # liquid, 313.15 K, 101.325 kPa (the condensate)
    "liq_conc": 8333.59,  # liquid, 383.15 K, 1750 kPa (the mass at the concentration's end)
    "vap_s6": 48572.49,  # vapour, 383.15 K, 101.325 kPa (S6)
    "vap_s9": 54484.32,  # vapour, 548.15 K, 101.325 kPa (S9)
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
    """kW to evaporate the components other than water at t (water: _water)."""
    return sum(v * HVAP[(c, t)] for c, v in n.items() if v > 0.0 and c != "H2O") / 3600.0


def _water(n: dict[str, float], h_from: str, h_to: str) -> float:
    """kW to take the stream's water from IAPWS-95 state h_from to h_to."""
    return n.get("H2O", 0.0) * (H_W[h_to] - H_W[h_from]) / 3600.0


def main() -> None:
    fs, comps = _flowsheet(), _materials()
    s3 = _kmol(fs, comps, "S3")
    s5 = _kmol(fs, comps, "S5")
    s6 = _kmol(fs, comps, "S6")
    s9 = _kmol(fs, comps, "S9")
    s10 = _kmol(fs, comps, "S10")

    q2 = _sensible(s3, comps, T_FEED, T_SALT)
    q3_sens = _sensible(s5, comps, T_SALT, T_CONC)
    q3_lat = _water(s6, "liq_conc", "vap_s6")
    q3 = q3_sens + q3_lat
    # Q4 (core) heats S9's water as liquid at 75.4 kJ/(kmol K) from 383.15 to 548.15 K;
    # Q5 takes it from there to S9's vapour state, so the hot oil carries IAPWS-95's path.
    q4_water = s9["H2O"] * comps["H2O"]["liquid_heat_capacity"] * (T_POLY - T_CONC) / 3600.0
    q5_water = _water(s9, "liq_conc", "vap_s9") - q4_water
    q5 = q5_water + _latent(s9, T_POLY)
    s9_other = {c: v for c, v in s9.items() if c != "H2O"}
    q6 = (
        _water(s6, "liq_cond", "vap_s6")
        + _water(s9, "liq_cond", "vap_s9")
        + _latent(s9, T_POLY)
        + _sensible(s9_other, comps, T_COND, T_POLY)
    )
    q7 = _sensible(s10, comps, T_PELLET, T_POLY)

    print(f"Q2 E101 slurry warming:          {q2:.6g} kW")
    print(f"Q3 X201 concentration:           {q3:.6g} kW (sensible {q3_sens:.4g}, latent {q3_lat:.4g})")
    print(f"Q5 X202 steam bleed, finishing:  {q5:.6g} kW (water {q5_water:.4g}, net of the {q4_water:.4g} kW that Q4 heats it as liquid)")
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
