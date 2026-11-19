"""What core cannot calculate in the salicylic acid plant (DESIGN.md D-005, D-009, D-011).

Year-average flows (kg/h, the recipe's basis, D-003). cheme process propagate computes the
streams and the duties of the semi-batches, the acidifier, the crystallizers; core reports the
dryers' duties (L-6). This script gives what no model of core gives, from the streams propagate
wrote:

- the duties of the three coolers that are not models of core (class Cooling, D-009):
  Q8, E-102 condensing the drying vapour S6 at the latent heats D101 uses and the condensate
  cooled to 313.15 K; Q9, the crude S9 and R-102's metal cooled in the kneader from 463.15 to
  373.15 K before the water fill (US 4 376 867 A, Example I: cooled to 100 C, then filled with
  water); Q10, E-202 condensing the product dryer's vapour S23 at D201's latent heats and the
  condensate cooled to 303.15 K;
- the CO2 dose of R102 (D-004, D-005): what Example I takes up per mol of NaOH and what fills
  R-102's free volume at the end of the hold (ideal gas), the ratio the design specification
  `rate` uses for S7 and the `absorbed` fraction of the dose;
- the vent's load when the head space is let down after the hold (D-011).

Run: `cheme run scripts/balance.py`, after `cheme process propagate --fill` and with the
recipe's batch size. With BALANCE_OUTPUT set it writes the values the flowsheet cites (library
ADR 0027).

Every parameter below is ASSUMED unless its comment names a source.
"""

from __future__ import annotations

import json
import os
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
R = 8.314462618  # kJ/(kmol K)

T_REACT = 463.15  # K, D101's end and R102 (SRC-1 Example I: 190 C)
T_FILL = 373.15  # K, the crude cooled before the water fill (SRC-1 Example I: 100 C)
T_BOIL = 373.15  # K, where most of the drying water boils off at ambient pressure (D-006)
T_E102 = 313.15  # K, E-102's condensate (S29)
T_D201 = 333.15  # K, D201's drying temperature
T_E202 = 303.15  # K, E-202's condensate (S30)
METAL_R102 = 6300.0  # kJ/K, R-102's metal, D101's vessel_heat_capacity (D-006)
VESSEL_R102 = 6.3  # m3, R-102 (recipe, D-003)
P_HOLD = 500.0  # kPa(a), SRC-1 Example I's 5 bar at the end, read as absolute (ASSUMED)
VENT_TIME = 0.25  # h, the recipe's vent operation (D-003)
# mol CO2 taken up per mol NaOH: Example I's 20.48 mol of acids from 23.0 mol of NaOH, 0.999 of
# the NaOH as phenoxide (D-005): 0.81838 x 25/23 of the earlier dose
UPTAKE = 0.81838 * 25.0 / 23.0


def _flowsheet() -> dict:
    return yaml.safe_load((ROOT / "process" / "flowsheet.yaml").read_text())


def _materials() -> dict:
    data = yaml.safe_load((ROOT / "process" / "materials.yaml").read_text())
    return {c["id"]: c for c in data["components"]}


def _stream(fs: dict, sid: str) -> dict:
    return next(s for s in fs["streams"] if s["id"] == sid)["state"]["design"]


def _moles(fs: dict, comps: dict, sid: str) -> dict[str, float]:
    """kmol/h of each component of stream *sid* (its flow in kg/h, its mole fractions)."""
    st = _stream(fs, sid)
    x = st["composition"]["values"]
    assert st["composition"]["basis"] == "mole_fraction", sid
    mw = sum(v * comps[k]["molar_mass"] for k, v in x.items())
    total = st["flow"]["value"] / mw
    return {k: v * total for k, v in x.items() if v > 0}


def _latent(fs: dict, step: str) -> dict[str, float]:
    node = next(s for s in fs["steps"] if s["id"] == step)
    return node["dryer"]["energy"]["latent_heat"]


def _condenser(fs, comps, sid, step, t_in, t_out) -> float:
    """kW: the vapour's components condensed at the dryer's latent heats (kJ/kg) and the
    condensate cooled from *t_in* to *t_out* at its liquid heat capacities."""
    n = _moles(fs, comps, sid)
    lat = _latent(fs, step)
    latent = sum(v * comps[k]["molar_mass"] * lat[k] for k, v in n.items())
    sensible = sum(v * comps[k]["liquid_heat_capacity"] for k, v in n.items()) * (t_in - t_out)
    return (latent + sensible) / 3600.0


def main() -> None:
    fs = _flowsheet()
    comps = _materials()
    recipe = yaml.safe_load((ROOT / "process" / "recipe.yaml").read_text())
    rate = _stream(fs, "S22")["flow"]["value"]
    hours = recipe["batch_size"]["value"] / rate  # h of flows per batch

    q8 = _condenser(fs, comps, "S6", "D101", T_BOIL, T_E102)
    q10 = _condenser(fs, comps, "S23", "D201", T_D201, T_E202)
    crude = _moles(fs, comps, "S9")
    cp_crude = sum(v * comps[k]["liquid_heat_capacity"] for k, v in crude.items())  # kJ/(h K)
    q9_crude = cp_crude * (T_REACT - T_FILL) / 3600.0
    q9_metal = METAL_R102 * (T_REACT - T_FILL) / hours / 3600.0
    q9 = q9_crude + q9_metal

    # the CO2 dose: uptake plus the head space at the end of the hold
    s3 = _stream(fs, "S3")
    naoh_kg = s3["flow"]["value"] * s3["composition"]["values"]["NAOH"]
    naoh_batch = naoh_kg / comps["NAOH"]["molar_mass"] * hours  # kmol a batch
    out = _moles(fs, comps, "S9")
    content = sum(v * comps[k]["liquid_molar_volume"] for k, v in out.items()) * hours  # m3
    free = VESSEL_R102 - content
    head = P_HOLD * free / (R * T_REACT)  # kmol a batch
    dose = UPTAKE + head / naoh_batch  # mol per mol NaOH
    absorbed = UPTAKE / dose
    s7_ratio = 0.5 / comps["NAOH"]["molar_mass"] * dose * comps["CO2"]["molar_mass"]
    vent_m3_h = head / VENT_TIME * R * T_REACT / 101.325

    print(f"batch: {hours:.4g} h of flows, {naoh_batch:.5g} kmol NaOH")
    print(f"Q8  E-102 condenser:       {q8:.6g} kW")
    print(f"Q9  crude {q9_crude:.4g} + metal {q9_metal:.4g} = {q9:.6g} kW")
    print(f"Q10 E-202 condenser:       {q10:.6g} kW")
    print(
        f"R102: content {content:.4g} m3, free {free:.4g} m3, head space {head:.4g} kmol CO2 "
        f"({head * comps['CO2']['molar_mass']:.4g} kg) at {P_HOLD:g} kPa(a); dose {dose:.5f} "
        f"mol/mol NaOH, absorbed {absorbed:.5f}, S7 {s7_ratio:.5f} kg per kg of caustic"
    )
    print(f"vent let-down: {vent_m3_h:.3g} m3/h at {T_REACT} K and 101.325 kPa(a) over {VENT_TIME} h")

    target = os.environ.get("BALANCE_OUTPUT")
    if target:
        Path(target).write_text(
            json.dumps(
                {
                    "contract": "balance-output/1",
                    "script": "scripts/balance.py",
                    "cases": {
                        "design": {
                            "Q8": {"duty": round(q8, 4)},
                            "Q9": {"duty": round(q9, 4)},
                            "Q10": {"duty": round(q10, 4)},
                        }
                    },
                },
                indent=2,
            )
        )


if __name__ == "__main__":
    main()
