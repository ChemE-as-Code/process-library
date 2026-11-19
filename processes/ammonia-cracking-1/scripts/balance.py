"""What core does not calculate in the ammonia cracker (DESIGN.md D-008).

`cheme process propagate --fill` solves the material balance from process/flowsheet.yaml: the
ammonia feed and the combustion air (design specifications for 200 t/d of hydrogen and 2.0 mol%
oxygen in the flue gas), the equilibrium of R101 at its outlet, the PSA's split and the complete
combustion in H101; it writes H101's convection heat Q2 (the rest after Q1, `energy_port: conv`,
core ADR 0059). This script reads the streams propagate wrote and gives what core has no model
for, on one enthalpy basis, the ideal-gas data of process/materials.yaml (elements basis: the
formation enthalpy at 298.15 K plus the sensible heat), with liquid ammonia below it:

- Q1, the radiant heat the cracker tubes R-101 take: the enthalpy of the cracked gas S4 less
  that of the superheated ammonia S3 (core's equilibrium reactor writes no duty, L-1);
- Q4, the feed-effluent exchanger E-101: liquid ammonia S1 (293.15 K, 1500 kPa(a)) warmed to its
  saturation at 1350 kPa(a), vaporised and superheated to S2's 313.15 K. The liquid's heat
  capacity, the vapour pressure and the heat of vaporization are thermo 0.6.1's HEOS_FIT
  correlations for ammonia (DESIGN.md SRC-5); the vapour is taken as an ideal gas from the
  saturation point (its departure, about 1 kJ/mol at 1.35 MPa, is left out, L-2);
- the cracked gas temperature S5 after E-101 gives Q4 up, and the trim cooler's duty Q3 to S6;
- the combustion air fan K-101's discharge temperature S10 and power W1;
- the stack temperature S11 at which the tail gas's heat of combustion covers Q1 and the
  superheater coil's duty (S2 to S3): the furnace balance, which closes the heat that propagate
  writes on Q2 against the coil (D-006).

Run: cheme run scripts/balance.py (prints the table; writes the balance-output JSON of the
library's ADR 0027 when BALANCE_OUTPUT names a file).
"""

from __future__ import annotations

import json
import os
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
T0 = 298.15
R = 8.314462618  # kJ/(kmol K)
NH3_CAS = "7664-41-7"

# design choices (DESIGN.md D-006, D-008), ASSUMED
ETA_FAN = 0.75  # isentropic efficiency of the combustion air fan K-101
ETA_DRIVE = 0.95  # motor


def load():
    flowsheet = yaml.safe_load((ROOT / "process/flowsheet.yaml").read_text(encoding="utf-8"))
    materials = yaml.safe_load((ROOT / "process/materials.yaml").read_text(encoding="utf-8"))
    comps = {c["id"]: c for c in materials["components"]}
    streams = {s["id"]: s for s in flowsheet["streams"] if s.get("kind") != "energy"}
    return flowsheet, comps, streams


def state(stream, key):
    value = stream["state"]["design"].get(key)
    return value["value"] if value else None


def kmol(stream, comps):
    """Component flows, kmol/h, of a stream as propagate wrote it."""
    st = stream["state"]["design"]
    flow = st["flow"]["value"]
    comp = st["composition"]
    x = comp["values"]
    if comp["basis"] == "mole_fraction":
        mw = sum(x[c] * comps[c]["molar_mass"] for c in x)
        total = flow / mw
        return {c: total * x[c] for c in x if x[c] > 0}
    return {c: flow * x[c] / comps[c]["molar_mass"] for c in x if x[c] > 0}


def h_ig(comp, t):
    """Ideal-gas enthalpy, kJ/kmol, on the elements basis (formation enthalpy at 298.15 K)."""
    a = comp["ideal_gas"]["cp_R"]

    def integral(tt):
        return sum(a[i] * tt ** (i + 1) / (i + 1) for i in range(len(a)))

    return comp["ideal_gas"]["dHf_298"] + R * (integral(t) - integral(T0))


def enthalpy(flows, t, comps):
    """kW of an ideal-gas stream."""
    return sum(n * h_ig(comps[c], t) for c, n in flows.items()) / 3600.0


def cp_mix(flows, t, comps):
    """kJ/(kmol K) of a gas mixture at t."""
    total = sum(flows.values())
    out = 0.0
    for c, n in flows.items():
        a = comps[c]["ideal_gas"]["cp_R"]
        out += n / total * R * sum(a[i] * t**i for i in range(len(a)))
    return out


def solve_t(target_kw, flows, comps, lo=250.0, hi=1500.0):
    for _ in range(200):
        mid = (lo + hi) / 2
        if enthalpy(flows, mid, comps) > target_kw:
            hi = mid
        else:
            lo = mid
    return (lo + hi) / 2


def liquid_ammonia_to_vapour(t_liq, p_vap_kpa, t_vap, comps):
    """kJ/kmol to take liquid ammonia at t_liq to vapour at p_vap_kpa and t_vap (thermo 0.6.1)."""
    from scipy.optimize import brentq
    from thermo import EnthalpyVaporization, HeatCapacityLiquid, VaporPressure

    vp = VaporPressure(CASRN=NH3_CAS)
    hvap = EnthalpyVaporization(CASRN=NH3_CAS)
    cpl = HeatCapacityLiquid(CASRN=NH3_CAS)
    t_sat = brentq(lambda t: vp(t) - p_vap_kpa * 1000.0, 200.0, 400.0)
    sensible = cpl.T_dependent_property_integral(t_liq, t_sat)  # J/mol
    latent = hvap(t_sat)  # J/mol
    superheat = h_ig(comps["NH3"], t_vap) - h_ig(comps["NH3"], t_sat)  # kJ/kmol
    detail = {"t_sat": t_sat, "sensible": sensible, "latent": latent, "superheat": superheat,
              "methods": (vp.method, hvap.method, cpl.method)}
    return sensible + latent + superheat, detail


def main() -> None:
    fs, comps, streams = load()
    out: dict[str, dict[str, float]] = {}

    def flows(sid):
        return kmol(streams[sid], comps)

    # Q1: R-101's radiant heat, cracked gas S4 less superheated ammonia S3
    q1 = enthalpy(flows("S4"), state(streams["S4"], "temperature"), comps) - enthalpy(
        flows("S3"), state(streams["S3"], "temperature"), comps
    )
    out["Q1"] = {"duty": round(q1, 1)}

    # Q4: E-101's cold side, liquid S1 to vapour S2
    per_kmol, detail = liquid_ammonia_to_vapour(
        state(streams["S1"], "temperature"), state(streams["S2"], "pressure"),
        state(streams["S2"], "temperature"), comps,
    )
    n_nh3 = flows("S1")["NH3"]
    q4 = n_nh3 * per_kmol / 3600.0
    out["Q4"] = {"duty": round(q4, 1)}

    # S5: the cracked gas after giving Q4 up, then the trim cooler Q3 to S6
    gas = flows("S4")
    h4 = enthalpy(gas, state(streams["S4"], "temperature"), comps)
    t5 = solve_t(h4 - q4, gas, comps)
    out["S5"] = {"temperature": round(t5, 2)}
    q3 = enthalpy(gas, t5, comps) - enthalpy(gas, state(streams["S6"], "temperature"), comps)
    out["Q3"] = {"duty": round(q3, 1)}

    # K-101: adiabatic compression of the air S9 to S10's pressure
    air = flows("S9")
    t9 = state(streams["S9"], "temperature")
    ratio = state(streams["S10"], "pressure") / state(streams["S9"], "pressure")
    kappa_r = R / cp_mix(air, t9, comps)  # (k - 1) / k
    t10s = t9 * ratio**kappa_r
    t10 = t9 + (t10s - t9) / ETA_FAN
    w_shaft = enthalpy(air, t10, comps) - enthalpy(air, t9, comps)
    out["S10"] = {"temperature": round(t10, 2)}
    out["W1"] = {"duty": round(w_shaft / ETA_DRIVE, 1)}

    # E-102: the superheater coil, S2 to S3
    q2 = enthalpy(flows("S3"), state(streams["S3"], "temperature"), comps) - enthalpy(
        flows("S2"), state(streams["S2"], "temperature"), comps
    )

    # H-101: the stack temperature at which the tail gas S8 and the air S10 give Q1 + Q2
    h_in = enthalpy(flows("S8"), state(streams["S8"], "temperature"), comps) + enthalpy(
        air, t10, comps
    )
    t11 = solve_t(h_in - q1 - q2, flows("S11"), comps)
    out["S11"] = {"temperature": round(t11, 2)}

    lhv = {"H2": 241822.0, "NH3": 317175.0}  # kJ/kmol from the formation data: see DESIGN.md D-008
    fired = sum(flows("S8").get(c, 0.0) * v for c, v in lhv.items()) / 3600.0
    product = flows("S7")
    h2_lhv = product["H2"] * lhv["H2"] / 3600.0
    nh3_lhv = n_nh3 * lhv["NH3"] / 3600.0

    print(f"thermo methods (vapour pressure, heat of vaporization, liquid cp): {detail['methods']}")
    print(f"ammonia saturation at {state(streams['S2'], 'pressure')} kPa(a): {detail['t_sat']:.2f} K; "
          f"per kmol: liquid {detail['sensible']:.0f}, latent {detail['latent']:.0f}, "
          f"vapour {detail['superheat']:.0f} kJ")
    print(f"Q1 R-101 {q1:.1f} kW; E-102 coil {q2:.1f} kW (propagate's Q2 should match); "
          f"Q4 E-101 {q4:.1f} kW; Q3 E-103 {q3:.1f} kW; W1 K-101 {w_shaft / ETA_DRIVE:.1f} kW")
    print(f"S5 {t5:.2f} K; S10 {t10:.2f} K; stack S11 {t11:.2f} K")
    print(f"tail gas fired (LHV) {fired:.1f} kW; hydrogen product (LHV) {h2_lhv:.1f} kW; "
          f"ammonia fed (LHV) {nh3_lhv:.1f} kW; LHV efficiency {h2_lhv / nh3_lhv:.4f}")
    print(f"hydrogen recovery from the ammonia {product['H2'] / (1.5 * n_nh3):.4f}")
    for k in sorted(out):
        print(k, out[k])

    target = os.environ.get("BALANCE_OUTPUT")
    if target:
        doc = {"contract": "balance-output/1", "script": f"scripts/{Path(__file__).name}",
               "cases": {"design": out}}
        Path(target).write_text(json.dumps(doc, indent=1, default=float), encoding="utf-8")


if __name__ == "__main__":
    main()
