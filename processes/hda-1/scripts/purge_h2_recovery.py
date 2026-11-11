"""Screening test of a PSA on the purge S13: incremental NPV and break-even capital (D-023, I-07).

Superseded by D-024: the PSA is now in the flowsheet (block HRU), simulated, priced and in the
TEA, whose own run gives the incremental test (DESIGN.md D-024). This script is the record of
the S2 screening and reads the S2 flowsheet, where S13 was the purge at the K-101 suction; on the
current flowsheet it stops. To reproduce D-023, run it on commit 45b79e1a (the merge of PR #326).

Run (on the S2 flowsheet): cheme run scripts/purge_h2_recovery.py

The question is whether a PSA's own benefit pays for its own cost, not whether it closes the
plant's LCOP gap. The script reads the purge S13 of process/flowsheet.yaml and the price, tax
and finance premises of estimate/tea.yaml, and prints

- the hydrogen recovered at an ASSUMED PSA recovery, its net value (make-up hydrogen saved less
  the fuel credit it no longer earns);
- the power it adds: the recovered hydrogen into the K-101 suction (a small boost from the
  PSA product pressure, then the extra K-101 throughput) and the tail-gas compressor into the
  site fuel gas header (ideal gas, polytropic with the D-010 efficiency);
- the incremental cash flow on the convention of `cheme assess tea` (construction 40/60 in
  years 0 and 1, 25 years of operation, straight-line depreciation over the life, the TEA's tax
  rate, maintenance and insurance as fractions of the fixed capital), its NPV at the D-019
  discount rate for a list of fixed-capital values, and the fixed capital at which it is zero.

Every value marked ASSUMED is a choice of this screening, not a published number. The PSA's
capital cost itself is not estimated here (no openly readable PSA cost correlation was found,
D-023): the break-even capital is the result, compared with the ASSUMED range of D-023.
"""

from __future__ import annotations

import math
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
R = 8.314462618  # kJ/(kmol K)
MW = {"H2": 2.01588, "CH4": 16.0425, "TOL": 92.13842, "BZ": 78.11184, "BIPH": 154.2078}

# ---- premises
RECOVERY = 0.85  # ASSUMED: middle of the PSA range 75-92 % (Matijasevic and Petric 2016, Table 1)
P_FEED = 3250.0  # kPa(a), S13 (D-007)
P_PRODUCT = 3150.0  # kPa(a), ASSUMED: PSA product about 100 kPa below its feed
P_TAIL = 130.0  # kPa(a), ASSUMED: PSA tail gas (desorption) pressure
P_HEADER = 450.0  # kPa(a), ASSUMED: site fuel gas header pressure (no site data, I-05)
T_GAS = 313.15  # K, S13
K_CP_CV = 1.30  # ASSUMED ratio of heat capacities of the methane-rich tail gas
ETA = 0.75  # compressor isentropic efficiency, ASSUMED (D-010)
# LHV of hydrogen, own calculation: the formation enthalpy of H2O(g), -241.826 kJ/mol (Cox,
# Wagman, Medvedev 1989, CODATA Key Values), over the molar mass of H2 (H2 and O2 are elements)
LHV_H2 = 241.826 / MW["H2"]  # MJ/kg


def poly_power(n_kmol_h: float, p_in: float, p_out: float) -> float:
    """Shaft power, kW, adiabatic compression of an ideal gas at ETA."""
    e = (K_CP_CV - 1.0) / K_CP_CV
    return n_kmol_h / 3600.0 * R * T_GAS / e * ((p_out / p_in) ** e - 1.0) / ETA


def main() -> None:
    fs = yaml.safe_load((ROOT / "process/flowsheet.yaml").read_text(encoding="utf-8"))
    if any(step["id"] == "X101" for step in fs["steps"]):
        raise SystemExit("the flowsheet holds the PSA (D-024): this S2 screening (D-023) applies to "
                         "the flowsheet without it; see DESIGN.md D-024 for the incremental test")
    tea = yaml.safe_load((ROOT / "estimate/tea.yaml").read_text(encoding="utf-8"))
    st = {s["id"]: s["state"]["design"] for s in fs["streams"]}
    s13, s14 = st["S13"], st["S14"]

    def kmol(state):
        x = state["composition"]["values"]
        mw = sum(x[c] * MW[c] for c in x)
        n = state["flow"]["value"] / mw
        return n, {c: n * x[c] for c in x}

    n13, c13 = kmol(s13)
    n14, _ = kmol(s14)
    h2_rec_kmol = RECOVERY * c13["H2"]
    h2_rec = h2_rec_kmol * MW["H2"]  # kg/h
    n_tail = n13 - h2_rec_kmol

    price = {(p["key"], p.get("component")): p["value"] for p in tea["prices"]}
    h2_price = price[("feed:H2MU", "H2")] / 1000.0  # EUR/kg
    gas = price[("product:FUELGAS", None)]  # EUR/GJ LHV
    power_price = price[("feed:POWER", None)] / 1000.0  # EUR/kWh
    hours = tea["operation"]["hours_per_year"]
    life = tea["operation"]["life_years"]
    rate = tea["finance"]["discount_rate"]["value"]
    tax = tea["finance"]["tax_rate"]["value"]
    split = tea["finance"]["construction"]
    fixed_frac = tea["fixed_opex"]["maintenance"]["value"] + tea["fixed_opex"]["insurance_tax"]["value"]

    credit_lost = LHV_H2 / 1000.0 * gas  # EUR/kg
    net_per_kg = h2_price - credit_lost
    gross = h2_rec * hours * net_per_kg  # EUR/a

    w_boost = poly_power(h2_rec_kmol, P_PRODUCT, P_FEED)
    k101 = 231.0  # kW, DWSIM K-101 shaft power (D-022)
    w_k101 = k101 * h2_rec_kmol / n14  # same pressure ratio, more moles
    w_tail = poly_power(n_tail, P_TAIL, P_HEADER)
    w_total = w_boost + w_k101 + w_tail
    power_cost = w_total * hours * power_price

    print(f"S13: {s13['flow']['value']:.1f} kg/h, {n13:.2f} kmol/h, H2 {c13['H2']:.2f} kmol/h "
          f"({c13['H2'] * MW['H2']:.1f} kg/h)")
    print(f"recovered H2 at {RECOVERY:.2f}: {h2_rec:.1f} kg/h ({h2_rec * hours / 1000:.0f} t/a); "
          f"tail gas {n_tail:.2f} kmol/h")
    print(f"LHV H2 {LHV_H2:.2f} MJ/kg; make-up {h2_price:.4f} - fuel credit {credit_lost:.4f} "
          f"= {net_per_kg:.4f} EUR/kg; gross {gross / 1e6:.3f} MEUR/a "
          f"({gross / (12.5 * hours):.2f} EUR/t benzene)")
    print(f"power: product boost {w_boost:.1f} kW, K-101 extra {w_k101:.1f} kW, tail-gas "
          f"compressor {w_tail:.1f} kW; total {w_total:.1f} kW, {power_cost / 1e6:.3f} MEUR/a")
    margin = gross - power_cost
    print(f"net before capital-related cost: {margin / 1e6:.3f} MEUR/a")

    def npv(capital: float) -> float:
        dep = capital / life
        v = 0.0
        for t, f in enumerate(split):
            v -= capital * f / (1 + rate) ** t
        t0 = len(split)
        for k in range(life):
            pre_tax = margin - fixed_frac * capital
            cash = pre_tax - tax * (pre_tax - dep)
            v += cash / (1 + rate) ** (t0 + k)
        return v

    for cap in (3.5e6, 9.5e6, 12e6):  # D-023: compressor 1.52 + PSA 2 to 8 MEUR (ASSUMED)
        print(f"fixed capital {cap / 1e6:5.1f} MEUR: incremental NPV {npv(cap) / 1e6:7.2f} MEUR")
    lo, hi = 0.0, 1e9
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        lo, hi = (mid, hi) if npv(mid) > 0 else (lo, mid)
    print(f"break-even fixed capital (incremental NPV 0 at {rate:.2f}): {lo / 1e6:.2f} MEUR")
    # simple payback on the pre-tax margin less maintenance and insurance
    for cap in (3.5e6, 9.5e6):
        print(f"simple payback at {cap / 1e6:.1f} MEUR: {cap / (margin - fixed_frac * cap):.1f} a")


if __name__ == "__main__":
    main()
