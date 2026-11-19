"""Design balance of demineralised-water-1: media filters, two-stage RO, mixed-bed polishing.

Run with `cheme run scripts/balance.py` in the process folder. It prints the year-average
balance of the design case and, with the environment variable BALANCE_OUTPUT set, writes every
value process/flowsheet.yaml cites from it (library ADR 0027, contract balance-output/1).

What core calculates itself (cheme process propagate): the raw-water flow that gives 50 000
kg/h of product (a spec), the filter split, the RO split and the mixed bed's split from their
fractions, the regeneration mixer and the neutralisation (a conversion step). This script gives
what core has no model for: the RO salt passage and feed pressure from the membrane's
permeability (DESIGN.md D-004), the media filter's backwash share (D-003), the mixed bed's resin
volume, regenerant doses and rinse water (D-005), the trim acid of the neutralisation (D-006)
and the pump powers (D-007). Every input is sourced (SRC-n) or ASSUMED in DESIGN.md; nothing is
read from a licensed source.
"""

from __future__ import annotations

import json
import math
import os
from pathlib import Path

# --- molar masses, kg/kmol (IUPAC 2021 standard atomic weights; as process/materials.yaml) ---
M = {"H2O": 18.015, "NaCl": 58.443, "HCl": 36.461, "NaOH": 39.997}

# --- design basis (D-002) ----------------------------------------------------------------
PRODUCT = 50_000.0          # kg/h demineralised water at the gate (50 m3/h), ASSUMED
HOURS = 8000.0              # h/a, ASSUMED
TDS_RAW = 500e-6            # kg NaCl per kg raw water: TDS lumped as NaCl, ASSUMED (D-002)
RHO = 1000.0                # kg/m3, water (taken as 1000 for volumes; ASSUMED rounding)

# --- media filters (D-003, SRC-1 p. 60) ----------------------------------------------------
V_FILT = 15.0               # m/h filtration velocity (SRC-1 p. 60: 10-20 m/h)
RUN_FILT = 24.0             # h between backwashes, ASSUMED
V_BW, T_BW = 45.0, 10 / 60  # m/h and h: backwash (SRC-1 p. 60: 40-50 m/h, about 10 min)
V_RINSE, T_RINSE = 15.0, 10 / 60  # m/h and h: rinse to drain at filtration velocity, ASSUMED 10 min

# --- reverse osmosis (D-004, SRC-1) --------------------------------------------------------
RECOVERY = 0.75             # water to permeate (SRC-1 p. 105 Table 25, p. 108: two stages, 55-75 %)
REJECTION = 0.99            # salt rejection on the mean feed-side concentration, ASSUMED (SRC-1 p. 11: 95 to >99 %)
FLUX = 23.8                 # L/(m2 h) design flux (SRC-1 p. 107: surface water, SDI < 5)
AREA = 37.2                 # m2 per 8-inch element (SRC-1 p. 107: 400 ft2 BW element)
Q_TEST = 1660.0             # L/h permeate of an 8-inch BW30 element at test (SRC-1 p. 22 Table 3, upper end)
P_TEST = 15.5               # bar, test pressure (SRC-1 p. 22 Table 4: 2000 ppm NaCl, 25 C, 15 % recovery)
PI_2000 = 1.4               # bar osmotic pressure of about 2000 mg/L TDS (SRC-1 p. 109)
FOULING = 0.85              # permeability kept after fouling and ageing, ASSUMED
DP_FEED = 3.0               # bar feed-to-concentrate pressure drop over both stages, ASSUMED
P_PERM = 0.5                # bar(g) permeate back-pressure (to the permeate tank), ASSUMED
P_ATM = 1.01325             # bar(a)
P_SUCTION = 2.0             # bar(a) at the high-pressure pump after filters and cartridge filters, ASSUMED

# --- mixed bed (D-005, SRC-2, SRC-3, SRC-4) -----------------------------------------------
SV = 20.0                   # bed volumes per hour in service, ASSUMED (set with RUN_MB by the capacity check, D-005)
CATION_SHARE = 0.4          # cation resin share of the bed volume, ASSUMED
RUN_MB = 36.0               # h service run between regenerations, ASSUMED (SRC-3: one or a few days on RO permeate)
CAP_SAC = (0.6, 1.7)        # eq/L operating capacity of strong acid cation resin (SRC-4)
CAP_SBA = (0.4, 0.9)        # eq/L operating capacity of strong base anion resin (SRC-4)
SALT_SHARE_MAX = 0.5        # the salt may use at most this share of the low-end operating capacity; the rest
                            # is kept for the CO2 and silica the model does not carry (L-2), ASSUMED (D-005)
HCL_LEVEL = 100.0           # g HCl per L cation resin (SRC-2: 80-120 g/L in mixed beds)
NAOH_LEVEL = 110.0          # g NaOH per L anion resin (SRC-2: 80-140 g/L in mixed beds)
HCL_CONC = 0.05             # regenerant strength (SRC-2: HCl 5 %)
NAOH_CONC = 0.04            # regenerant strength (SRC-2: NaOH 4 %)
RINSE_BV = 15.0             # bed volumes of backwash, displacement and rinse water per regeneration, ASSUMED
NACL_TO_PRODUCT = 0.002     # share of the permeate's salt the bed lets through, ASSUMED (D-005)
ACID_33 = 0.33              # hydrochloric acid from hydrogen-chloride-1 (33 wt-%)
CAUSTIC_50 = 0.50           # caustic soda from chlor-alkali-1 (50 wt-%)
TRIM = 1.001                # acid equivalents per caustic equivalent after the trim (SRC-5: equal or slightly above)

# --- pumps (D-007) -------------------------------------------------------------------------
P_RAW_OUT = 4.0             # bar(a) raw-water pump discharge (SRC-1 p. 60: pressure filters 2 to >4 bar), ASSUMED
P_PRODUCT = 6.0             # bar(a) mixed-bed feed / forwarding pump: 1 bar over the bed to a 5 bar(a) header, ASSUMED
ETA = 0.70                  # pump and motor efficiency, ASSUMED
AUX_KW = 3.0                # dosing, regeneration and air-mixing blower, filter backwash pump and air scour,
                            # instruments, year average, ASSUMED (D-007)
A_FILTER = 2.5              # m2 per filter, three filters, two in service (equipment list F-101), ASSUMED
N_FILTERS = 3
P_BW = 2.0                  # bar rise of the backwash pump P-103, ASSUMED
CP_WATER = 4.18             # kJ/(kg K), liquid water at 25 degC (D-007; chemicals 1.5.2, see DESIGN.md)
DH_NEUT = -285.830 - (-230.015 + 0.0)  # kJ/mol, H+(aq) + OH-(aq) -> H2O(l) (SRC-6)


def pump_kw(flow_kg_h: float, p_in: float, p_out: float) -> float:
    """Shaft-to-wire power of a water pump, kW: V dP / eta (bar -> kPa)."""
    return flow_kg_h / RHO / 3600.0 * (p_out - p_in) * 100.0 / ETA


def design() -> dict:
    r = {}
    # mixed bed: resin volume from the service flow, chemicals per regeneration
    bed = PRODUCT / RHO / SV                              # m3 resin
    v_cat, v_an = CATION_SHARE * bed, (1 - CATION_SHARE) * bed
    hcl_regen = HCL_LEVEL * v_cat * 1000 / 1000 / RUN_MB  # kg/h HCl (100 %), g/L x L -> kg
    naoh = NAOH_LEVEL * v_an * 1000 / 1000 / RUN_MB       # kg/h NaOH (100 %)
    acid_regen = hcl_regen / ACID_33
    caustic = naoh / CAUSTIC_50
    dil_hcl = hcl_regen / HCL_CONC - acid_regen
    dil_naoh = naoh / NAOH_CONC - caustic
    rinse = RINSE_BV * bed * RHO / RUN_MB
    regen_water = dil_hcl + dil_naoh + rinse
    # trim acid into the pit: acid equivalents 1.001 x caustic equivalents
    n_naoh = naoh / M["NaOH"]
    n_hcl_regen = hcl_regen / M["HCl"]
    hcl_trim = (TRIM * n_naoh - n_hcl_regen) * M["HCl"]
    acid_trim = hcl_trim / ACID_33
    r.update(bed=bed, v_cat=v_cat, v_an=v_an, hcl_regen=hcl_regen, naoh=naoh, acid_regen=acid_regen,
             caustic=caustic, dil_hcl=dil_hcl, dil_naoh=dil_naoh, rinse=rinse, regen_water=regen_water,
             hcl_trim=hcl_trim, acid_trim=acid_trim, regenerations=HOURS / RUN_MB)

    # RO: salt passage on the log-mean feed-side concentration of a plug-flow array
    cf = -math.log(1 - RECOVERY) / RECOVERY               # mean feed-side concentration factor
    passage = (1 - REJECTION) * cf * RECOVERY             # share of the feed salt to the permeate
    # permeate = product water + regeneration water (taken from the permeate tank), salts aside
    # water balance backwards: product H2O = service H2O; the bed lets NACL_TO_PRODUCT of the salt through
    # solve the raw flow F: filtered = F (the backwash leaves after the filter, as a share of it)
    bw_share = (V_BW * T_BW + V_RINSE * T_RINSE) / (V_FILT * RUN_FILT)
    # product = (1 - s) * perm_H2O + NaCl leak; s = regeneration share of the permeate (mass)
    # iterate: the product's salt is tiny, so two passes suffice
    f_raw = PRODUCT / ((1 - bw_share) * RECOVERY)
    for _ in range(50):
        ro_feed = f_raw * (1 - bw_share)
        h2o_feed, nacl_feed = ro_feed * (1 - TDS_RAW), ro_feed * TDS_RAW
        perm_h2o, perm_nacl = RECOVERY * h2o_feed, passage * nacl_feed
        perm = perm_h2o + perm_nacl
        split_regen = regen_water / perm
        svc_h2o, svc_nacl = (1 - split_regen) * perm_h2o, (1 - split_regen) * perm_nacl
        product = svc_h2o + NACL_TO_PRODUCT * svc_nacl
        f_raw *= PRODUCT / product
    r.update(cf=cf, passage=passage, bw_share=bw_share, raw=f_raw, ro_feed=ro_feed, perm=perm,
             perm_nacl=perm_nacl, conc=ro_feed - perm, split_regen=split_regen, product=product,
             product_nacl_mgkg=NACL_TO_PRODUCT * svc_nacl / product * 1e6,
             perm_tds_mgkg=perm_nacl / perm * 1e6, ions=(1 - NACL_TO_PRODUCT) * svc_nacl)
    r["ionic_eq"] = r["ions"] / M["NaCl"]                 # kmol/h of NaCl held on the bed
    r["ratio_hcl"] = n_hcl_regen / r["ionic_eq"]
    r["ratio_naoh"] = n_naoh / r["ionic_eq"]
    # capacity check (D-005): the salt taken up in one run (kmol = keq for NaCl) against the
    # operating capacity of each resin (eq/L x m3 = keq / 1000 x 1000)
    r["salt_run_kmol"] = r["ionic_eq"] * RUN_MB
    r["use_sba_low"] = r["salt_run_kmol"] / (CAP_SBA[0] * v_an)
    r["use_sba_high"] = r["salt_run_kmol"] / (CAP_SBA[1] * v_an)
    r["use_sac_low"] = r["salt_run_kmol"] / (CAP_SAC[0] * v_cat)
    r["use_sac_high"] = r["salt_run_kmol"] / (CAP_SAC[1] * v_cat)
    r["run_max"] = SALT_SHARE_MAX * min(CAP_SBA[0] * v_an, CAP_SAC[0] * v_cat) / r["ionic_eq"]
    assert RUN_MB <= r["run_max"], "the run exceeds the salt's share of the resins' operating capacity (D-005)"

    # RO feed pressure from the element's permeability at test
    pi_feed = PI_2000 * TDS_RAW * 1e6 / 2000.0
    a_test = Q_TEST / AREA / (P_TEST - PI_2000)           # L/(m2 h bar), test NDP with the feed's osmotic pressure
    ndp = FLUX / (a_test * FOULING)
    p_feed_g = ndp + pi_feed * cf + DP_FEED / 2 + P_PERM  # bar(g)
    p_feed = p_feed_g + P_ATM
    elements = math.ceil(r["perm"] / RHO * 1000 / FLUX / AREA)
    # installed: whole vessels of six; the feed pressure stays at the design flux, a margin (D-004)
    vessels = math.ceil(elements / 6)
    flux_inst = r["perm"] / RHO * 1000 / (6 * vessels * AREA)
    ndp_inst = flux_inst / (a_test * FOULING)
    r.update(pi_feed=pi_feed, a_test=a_test, ndp=ndp, p_feed=p_feed, elements=elements,
             vessels=vessels, flux_inst=flux_inst, ndp_inst=ndp_inst)

    # pumps
    r["E1"] = pump_kw(r["raw"], P_ATM, P_RAW_OUT)
    r["E2"] = pump_kw(r["ro_feed"], P_SUCTION, p_feed)
    r["E3"] = pump_kw(r["perm"] * (1 - r["split_regen"]), P_ATM, P_PRODUCT)
    r["E4"] = AUX_KW
    r["kwh_m3"] = (r["E1"] + r["E2"] + r["E3"] + r["E4"]) / (PRODUCT / RHO)

    # flows not in the energy balance, sized for D-007 (all inside E4 or left as heat in the water)
    r["filter_area"] = r["raw"] / RHO / V_FILT                        # m2 in service
    r["bw_flow"] = V_BW * A_FILTER                                     # m3/h, one filter at a time
    r["bw_pump_kw"] = r["bw_flow"] / 3600 * P_BW * 100 / ETA          # kW while backwashing
    r["bw_pump_avg"] = r["bw_pump_kw"] * N_FILTERS * T_BW / RUN_FILT   # kW year average
    r["dt_letdown"] = (p_feed - DP_FEED - P_ATM) * 100 / (RHO * CP_WATER / 1000) / 1000  # K, concentrate throttled
    n_neut = min(HCL_LEVEL * v_cat / M["HCl"], NAOH_LEVEL * v_an / M["NaOH"])  # kmol per regeneration
    r["q_neut_regen"] = -DH_NEUT * n_neut                              # MJ per regeneration
    effluent_regen = (r["regen_water"] + acid_regen + caustic + acid_trim + r["ions"]) * RUN_MB  # kg
    r["effluent_regen"] = effluent_regen
    r["dt_pit"] = r["q_neut_regen"] * 1000 / (effluent_regen * CP_WATER)  # K, the pit's whole batch
    regenerants = (hcl_regen / HCL_CONC + naoh / NAOH_CONC) * RUN_MB  # kg of the two dilute regenerants
    r["dt_regenerants"] = r["q_neut_regen"] * 1000 / (regenerants * CP_WATER)  # K, if they meet alone
    return r


def write_balance_output(cases):
    """With BALANCE_OUTPUT set, write the values the flowsheet cites from this script as JSON
    (the library's balance-output contract, ADR 0027)."""
    target = os.environ.get("BALANCE_OUTPUT")
    if target:
        doc = {"contract": "balance-output/1", "script": f"scripts/{Path(__file__).name}", "cases": cases}
        Path(target).write_text(json.dumps(doc, indent=1, default=float), encoding="utf-8")


def main() -> None:
    r = design()
    for k, v in r.items():
        print(f"{k:>18}: {v:.6g}")
    acid_total = r["acid_regen"] + r["acid_trim"]
    print(f"{'HCl 33 % per m3':>18}: {acid_total / (PRODUCT / RHO):.5f} kg")
    print(f"{'NaOH 50 % per m3':>18}: {r['caustic'] / (PRODUCT / RHO):.5f} kg")
    print(f"{'raw water per m3':>18}: {r['raw'] / PRODUCT:.5f} m3")
    w = lambda x: round(x, 6)  # noqa: E731
    write_balance_output({"design": {
        "S9": {"flow": round(r["regen_water"], 2)},
        "S13": {"flow": round(r["acid_regen"], 4), "composition": {"HCl": ACID_33, "H2O": w(1 - ACID_33)}},
        "S14": {"flow": round(r["caustic"], 4), "composition": {"NaOH": CAUSTIC_50, "H2O": w(1 - CAUSTIC_50)}},
        "S16": {"flow": round(r["acid_trim"], 4), "composition": {"HCl": ACID_33, "H2O": w(1 - ACID_33)}},
        "S5": {"pressure": round(r["p_feed"] * 100, 1)},
        "E1": {"duty": round(r["E1"], 3)},
        "E2": {"duty": round(r["E2"], 3)},
        "E3": {"duty": round(r["E3"], 3)},
        "E4": {"duty": round(r["E4"], 3)},
    }})


if __name__ == "__main__":
    main()
