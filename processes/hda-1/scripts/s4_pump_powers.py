"""Shaft powers of the pumps the P&IDs added (S4, D-026, review 2026-11-04-basic-pids#27).

The flowsheet lumps the reflux, distillate and bottoms pumps of the columns into the column
steps, so the simulation gives them no power. This script estimates the shaft power of each for
the class 5 cost basis (estimate/cost-basis.yaml): P = m / rho * dp / eta.

- m: the design-case flows of process/flowsheet.yaml (distillate S26 and S23, reflux = R x D with
  R from process/simulation.yaml, bottoms S24) and the C-201 reflux of scripts/concept_sizing.py
  (about 175 kg/h, D-025).
- rho: liquid density of the main component at the drum temperature, from the `thermo` package
  bundled with core (Chemical(...).rhol at T and 101.325 kPa).
- dp: ASSUMED (D-026), the pump differential head the P&ID routing needs, as stated per pump.
- eta: 0.65, the pump efficiency of D-010, ASSUMED.

Run: python scripts/s4_pump_powers.py (an environment with thermo, e.g. the core env).
"""

from thermo import Chemical

ETA = 0.65  # D-010

# tag: (component, T K, mass flow kg/h, dp kPa, basis of the flow, basis of dp)
PUMPS = {
    "P-201A/B": ("stabiliser reflux, taken as benzene", "benzene", 313.15, 175.0, 300.0,
                 "C-201 reflux about 175 kg/h (D-025, concept sizing)",
                 "about 12 m static head to the C-201 top plus the control valve, ASSUMED"),
    "P-202A/B": ("benzene", "benzene", 366.165, 2.18 * 12498.2 + 12498.2, 400.0,
                 "reflux R 2.18 x D + distillate D (S26 12498.2 kg/h)",
                 "38 m to the C-202 top and through E-207 to storage, about 400 kPa (equipment list note), ASSUMED"),
    "P-203A/B": ("toluene", "toluene", 344.883, 0.5 * 4884.74 + 4884.74, 370.0,
                 "reflux R 0.5 x D + recycle D (S23 4884.74 kg/h)",
                 "from the 30 kPa(a) drum to about 400 kPa(a) (C-203 top 14 m and V-100 at 150 kPa(a) with the control valves), ASSUMED"),
    "P-204A/B": ("biphenyl", "biphenyl", 456.978, 352.0, 400.0,
                 "biphenyl bottoms S24 352 kg/h",
                 "from the 45 kPa(a) sump to storage, about 400 kPa, ASSUMED"),
}


def main() -> None:
    for tag, (_, name, temperature, flow, dp, flow_basis, dp_basis) in PUMPS.items():
        rho = Chemical(name, T=temperature, P=101325.0).rhol
        volume = flow / 3600.0 / rho  # m3/s
        power = volume * dp * 1000.0 / ETA / 1000.0  # kW
        print(f"{tag}: {flow:.0f} kg/h, rho {rho:.1f} kg/m3 at {temperature:.2f} K, dp {dp:.0f} kPa"
              f" -> {power:.2f} kW shaft ({flow_basis}; {dp_basis})")


if __name__ == "__main__":
    main()
