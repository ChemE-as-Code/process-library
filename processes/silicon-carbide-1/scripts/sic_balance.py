"""Material and lumped energy balance of the Acheson silicon carbide plant (silicon-carbide-1).

Concept stage. The Acheson furnace is a batch electric resistance furnace; this balance is the
time average over many furnaces in rotation (charge, heat, cool, break), in kg/h. It is an
independent sequential balance on a component basis with imposed yields and splits (a sourced
conversion/recovery model, DESIGN.md D-006): no reaction kinetics, no furnace heat transfer
model. `cheme process furnace` supports limestone calcination only and refuses carbothermal
SiC (core #387), so the furnace electricity is a labelled specific-energy basis (D-004).

Every design parameter below is ASSUMED unless its comment names a source; DESIGN.md lists
them with the reasons. Run: `cheme run scripts/sic_balance.py` (standard library only). It
prints the streams (kg/h, mass fractions) in the YAML form of process/flowsheet.yaml, the
duties (kW), the element balance of every unit and the specific figures per kg of product.
"""

from __future__ import annotations

# kg/kmol (IUPAC 2021 standard atomic weights)
AW = {"Si": 28.085, "C": 12.011, "O": 15.999, "H": 1.008, "S": 32.06, "N": 14.007, "Al": 26.982}
ELEMENTS = {
    "SiO2": {"Si": 1, "O": 2}, "C": {"C": 1}, "SiC": {"Si": 1, "C": 1},
    "Al2O3": {"Al": 2, "O": 3}, "H2O": {"H": 2, "O": 1}, "CH4": {"C": 1, "H": 4},
    "S": {"S": 1}, "CO": {"C": 1, "O": 1}, "SiO": {"Si": 1, "O": 1},
    "CO2": {"C": 1, "O": 2}, "SO2": {"S": 1, "O": 2}, "N2": {"N": 2}, "O2": {"O": 2},
}
MW = {k: sum(AW[e] * n for e, n in v.items()) for k, v in ELEMENTS.items()}
ORDER = list(ELEMENTS)

# Standard enthalpies of formation at 298.15 K, kJ/mol (NIST-JANAF Thermochemical Tables,
# Chase 1998; values recalled for the concept stage, to be checked against the tables: D-007)
HF = {"SiO2": -910.9, "C": 0.0, "SiC": -71.6, "CO": -110.5, "SiO": -100.4, "CH4": -74.9,
      "CO2": -393.5, "SO2": -296.8, "H2O": -241.8, "S": 0.0, "O2": 0.0}

# --- design parameters (D-002 .. D-008) ----------------------------------------------------
P_CRUDE = 5000.0       # kg/h crushed crude crystalline SiC at the gate (D-002, ASSUMED basis)
W_CRUDE = {"SiC": 0.980, "SiO2": 0.008, "C": 0.007, "Al2O3": 0.005}   # crude grade (D-002, ASSUMED)
R_MET = 0.25           # metallurgical-grade SiC per kg crude crystalline SiC (D-006, ASSUMED)
W_MET = {"SiC": 0.88, "C": 0.06, "SiO2": 0.05, "Al2O3": 0.01}         # (D-006, ASSUMED)
R_REC = 3.0            # recycled unreacted mix per kg crude crystalline SiC (D-006, ASSUMED)
W_REC_SIC = 0.04       # SiC mass fraction of the recycled mix (D-006, ASSUMED)
CF_REC = 0.39          # C/(C+SiO2) mass ratio of the recycled mix (D-006, ASSUMED; Lima and
                       # Tenorio 2011 report charge carbon factors of about 38-39 %)
PURGE = 0.05           # share of the sorted unreacted mix purged as waste (D-006, ASSUMED)
SIO_LOSS = 0.005       # SiO escaping the charge, kmol per kmol SiC formed (D-006, ASSUMED)
DUST = 0.2e-3          # crushing dust to air after the bag filter, kg/kg product (ASSUMED)
SAND = {"SiO2": 0.985, "Al2O3": 0.005, "H2O": 0.010}                  # (D-005, ASSUMED)
COKE = {"C": 0.855, "CH4": 0.080, "S": 0.015, "Al2O3": 0.005, "H2O": 0.045}  # green petcoke (D-005)
X_CO = 0.70            # CO burnt at the charge surface (D-006, ASSUMED; cross-check IPCC CO factor)
X_CH4 = None           # CH4 burnt: set below so the slip is the IPCC Tier 1 factor (D-006)
EF_CH4 = 11.6e-3       # kg CH4 per kg SiC (IPCC 2006 Vol. 3 ch. 3.6 Tier 1, via EPA TSD 2009 Table 4)
LAMBDA = 2.0           # air over the burn-off stoichiometry (D-006, ASSUMED; dilution air not modelled)
O2_AIR = 0.2095        # O2 mole fraction of dry air, rest N2 (argon lumped with N2)
SEC = 7.5              # kWh electricity per kg crude SiC (crystalline + metallurgical) (D-004,
                       # ASSUMED inside 6.3-9.02 kWh/kg, Mehrwald 1992 via Lima and Tenorio 2011)
CW_FRAC = 0.02         # transformer and bus-bar losses to cooling water, share of furnace power (ASSUMED)
E_AUX = 0.15           # kWh/kg product: mixing, charging, handling, off-gas fans (D-008, ASSUMED)
E_CRUSH = 0.10         # kWh/kg product: crushing and screening (D-008, ASSUMED)
T_HOT, T_COOL = 1800.0, 323.15   # K, mean furnace contents at power-off and when broken (D-003, ASSUMED)
CP_MEAN = 1.3          # kJ/(kg K), mean heat capacity of the contents over that range (D-008, ASSUMED)
T_GAS, T_FLUE = 1000.0, 600.0    # K, raw gas at the charge surface (S5) and hood outlet (S7) (D-006, ASSUMED)
CP_GAS = 1.25          # kJ/(kg K), mean of S5 (mostly CO, some CH4 and steam) over 298-1000 K (D-008, ASSUMED)
CP_FLUE = 1.05         # kJ/(kg K), mean of S7 (N2, CO2, O2, steam) over 298-600 K (D-008, ASSUMED)


def kmol(stream):
    return {k: v / MW[k] for k, v in stream.items()}


def elements(stream):
    out = {}
    for k, n in kmol(stream).items():
        for e, a in ELEMENTS[k].items():
            out[e] = out.get(e, 0.0) + a * n
    return out


def add(*streams):
    out = {}
    for s in streams:
        for k, v in s.items():
            out[k] = out.get(k, 0.0) + v
    return out


def scale(frac, total):
    return {k: v * total for k, v in frac.items()}


def total(s):
    return sum(s.values())


# --- products -------------------------------------------------------------------------------
crude = scale(W_CRUDE, P_CRUDE)                         # S12 at the gate
dust = {"SiC": P_CRUDE * DUST}                          # S13
crude_sorted = add(crude, dust)                         # S9: crude before crushing
met = scale(W_MET, R_MET * P_CRUDE)                     # S10

# --- sorted unreacted mix: recycle and purge, same composition; Al2O3 (all oxide impurities)
# closes by the purge: in with sand and coke = out with crude, met and purge. Solved by
# fixed-point iteration on the fresh feeds.
rec_total = R_REC * P_CRUDE
purge_total = rec_total * PURGE / (1 - PURGE)
w_al = 0.01
for _ in range(200):
    w_rest = 1 - W_REC_SIC - w_al
    w_rec = {"SiO2": w_rest * (1 - CF_REC), "C": w_rest * CF_REC, "SiC": W_REC_SIC, "Al2O3": w_al}
    purge = scale(w_rec, purge_total)                   # S11
    rec = scale(w_rec, rec_total)                       # S3
    # SiC formed in the furnace = SiC leaving the loop (crude, dust, met, purge)
    sic_out = crude_sorted["SiC"] + met["SiC"] + purge["SiC"]
    xi1 = sic_out / MW["SiC"]                          # SiO2 + 3 C -> SiC + 2 CO
    xi2 = SIO_LOSS * xi1                               # SiO2 + C -> SiO(g) + CO
    sio2_fresh = (crude_sorted.get("SiO2", 0) + met["SiO2"] + purge["SiO2"]
                  + MW["SiO2"] * (xi1 + xi2))
    c_fresh = (crude_sorted.get("C", 0) + met["C"] + purge["C"] + MW["C"] * (3 * xi1 + xi2))
    sand_total = sio2_fresh / SAND["SiO2"]
    coke_total = c_fresh / COKE["C"]
    sand = scale(SAND, sand_total)                      # S1
    coke = scale(COKE, coke_total)                      # S2
    al_in = sand["Al2O3"] + coke["Al2O3"]
    w_al_new = (al_in - crude_sorted["Al2O3"] - met["Al2O3"]) / purge_total
    if abs(w_al_new - w_al) < 1e-12:
        break
    w_al = w_al_new

charge = add(sand, coke, rec)                           # S4
# Furnace: reactions RX1 (xi1), RX2 (xi2); water, volatiles (as CH4) and sulfur leave as gas
gas = {"CO": MW["CO"] * (2 * xi1 + xi2), "SiO": MW["SiO"] * xi2, "CH4": coke["CH4"],
       "S": coke["S"], "H2O": sand["H2O"] + coke["H2O"]}           # S5
ingot = {"SiC": charge["SiC"] + MW["SiC"] * xi1,
         "SiO2": charge["SiO2"] - MW["SiO2"] * (xi1 + xi2),
         "C": charge["C"] - MW["C"] * (3 * xi1 + xi2),
         "Al2O3": charge["Al2O3"]}                      # S8

# Burn-off at the charge surface and in the hood
n_co, n_ch4 = gas["CO"] / MW["CO"], gas["CH4"] / MW["CH4"]
ch4_slip = EF_CH4 * sic_out                             # kg/h
X_CH4 = 1 - ch4_slip / gas["CH4"]
b_co, b_ch4 = X_CO * n_co, X_CH4 * n_ch4                # kmol/h burnt
b_s, b_sio = gas["S"] / MW["S"], xi2
o2_need = 0.5 * b_co + 2 * b_ch4 + b_s + 0.5 * b_sio
o2_air = LAMBDA * o2_need
air = {"O2": o2_air * MW["O2"], "N2": o2_air * (1 - O2_AIR) / O2_AIR * MW["N2"]}   # S6
flue = {"CO2": (b_co + b_ch4) * MW["CO2"], "CO": (n_co - b_co) * MW["CO"],
        "CH4": ch4_slip, "SO2": b_s * MW["SO2"], "SiO2": b_sio * MW["SiO2"],
        "H2O": gas["H2O"] + 2 * b_ch4 * MW["H2O"],
        "O2": (o2_air - o2_need) * MW["O2"], "N2": air["N2"]}       # S7

# --- energy ---------------------------------------------------------------------------------
P_FUR = SEC * (P_CRUDE + total(met))
Q_CW = CW_FRAC * P_FUR
P_AUX = E_AUX * P_CRUDE
P_CRU = E_CRUSH * P_CRUDE
Q_COOL = total(ingot) * CP_MEAN * (T_HOT - T_COOL) / 3600   # kW to ambient air (natural cooling)
dh1 = HF["SiC"] + 2 * HF["CO"] - HF["SiO2"]             # kJ/mol
dh2 = HF["SiO"] + HF["CO"] - HF["SiO2"]
q_rx = (xi1 * dh1 + xi2 * dh2) * 1000 / 3600            # kW (kmol/h * kJ/mol * 1000 / 3600)
# Burn-off B101 (review R-03): heat released at 298 K by COX, CH4X, SOX, SIOX, plus the sensible
# heat S5 brings, minus what S7 carries at T_FLUE; the rest leaves to ambient (Q6): radiation
# from the burning charge surface and, in a real hood, the heating of dilution air (not modelled)
dh_cox = HF["CO2"] - HF["CO"]
dh_ch4x = HF["CO2"] + 2 * HF["H2O"] - HF["CH4"]
dh_sox = HF["SO2"] - HF["S"]
dh_siox = HF["SiO2"] - HF["SiO"]
q_burn = -(b_co * dh_cox + b_ch4 * dh_ch4x + b_s * dh_sox + b_sio * dh_siox) * 1000 / 3600   # kW
q_gas_in = total(gas) * CP_GAS * (T_GAS - 298.15) / 3600
q_flue = total(flue) * CP_FLUE * (T_FLUE - 298.15) / 3600
Q_LOSS = q_burn + q_gas_in - q_flue                     # kW to ambient

STREAMS = [
    ("S1", "Silica sand", sand), ("S2", "Petroleum coke (green)", coke),
    ("S3", "Recycled unreacted mix", rec), ("S4", "Furnace charge", charge),
    ("S5", "Raw furnace gas at the charge surface", gas), ("S6", "Air drawn over the furnace", air),
    ("S7", "Furnace flue gas to atmosphere", flue), ("S8", "Hot furnace contents (ingot and mix)", ingot),
    ("S8B", "Cooled furnace contents", ingot), ("S9", "Crude crystalline SiC (sorted)", crude_sorted),
    ("S10", "Metallurgical-grade SiC", met), ("S11", "Purged mix (waste)", purge),
    ("S12", "Crushed crude SiC", crude), ("S13", "Crushing dust after the bag filter", dust),
]


def fractions(s):
    t = total(s)
    fr = {k: round(v / t, 6) for k, v in s.items() if v / t >= 5e-7}
    big = max(fr, key=fr.get)
    fr[big] = round(fr[big] + 1 - sum(fr.values()), 6)
    return t, {k: fr[k] for k in ORDER if k in fr}


def check(name, ins, outs):
    ei, eo = elements(add(*ins)), elements(add(*outs))
    worst = max(abs(ei.get(e, 0) - eo.get(e, 0)) for e in set(ei) | set(eo))
    mi, mo = sum(map(total, ins)), sum(map(total, outs))
    print(f"  {name:6s} mass in {mi:10.1f} out {mo:10.1f} kg/h  worst element imbalance {worst:.2e} kmol/h")


def write_balance_output(cases):
    """With BALANCE_OUTPUT set, write the values the flowsheet cites from this script as JSON.

    The process library's balance-output contract (docs/adr/0024 of the library): case ->
    stream id -> quantity, in the flowsheet's units and basis. The library's
    scripts/check_balance_scripts.py re-runs this script and compares them with
    process/flowsheet.yaml.
    """
    import json
    import os
    from pathlib import Path

    target = os.environ.get("BALANCE_OUTPUT")
    if target:
        doc = {"contract": "balance-output/1", "script": f"scripts/{Path(__file__).name}",
               "cases": cases}
        Path(target).write_text(json.dumps(doc, indent=1, default=float), encoding="utf-8")


if __name__ == "__main__":
    print("# streams (kg/h, mass fractions)")
    for sid, title, s in STREAMS:
        t, fr = fractions(s)
        print(f"  {sid}: {title}: flow {t:.1f} composition {fr}")
    print("# balances")
    check("M101", [sand, coke, rec], [charge])
    check("R101", [charge], [gas, ingot])
    check("B101", [gas, air], [flue])
    check("Z101", [ingot], [crude_sorted, met, rec, purge])
    check("Z201", [crude_sorted], [crude, dust])
    check("plant", [sand, coke, air], [crude, dust, met, purge, flue])
    print("# extents (kmol/h)")
    print(f"  RX1 SiO2 + 3 C -> SiC + 2 CO: {xi1:.3f}; RX2 SiO2 + C -> SiO + CO: {xi2:.4f}")
    print(f"  burn-off: CO {b_co:.3f} (X {X_CO}), CH4 {b_ch4:.3f} (X {X_CH4:.4f}), S {b_s:.4f}, SiO {b_sio:.4f}")
    print("  conversions on the charge: SiO2 %.4f (RX1) %.5f (RX2); C %.4f (RX1) %.5f (RX2)" % (
        MW["SiO2"] * xi1 / charge["SiO2"], MW["SiO2"] * xi2 / charge["SiO2"],
        3 * MW["C"] * xi1 / charge["C"], MW["C"] * xi2 / charge["C"]))
    print("# duties (kW)")
    print(f"  Q1 furnace power {P_FUR:.1f}; Q2 transformer/bus-bar cooling water {Q_CW:.1f}; "
          f"Q3 auxiliaries {P_AUX:.1f}; Q4 crushing {P_CRU:.1f}; Q5 ingot cooling to ambient {Q_COOL:.1f}")
    print(f"  furnace closure: power {P_FUR:.0f} = reaction {q_rx:.0f} + contents at power-off "
          f"{Q_COOL:.0f} + off-gas and losses during heating {P_FUR - q_rx - Q_COOL:.0f} kW (lumped)")
    print(f"  burn-off B101: released {q_burn:.0f} + raw gas sensible {q_gas_in:.0f} = flue sensible "
          f"{q_flue:.0f} + Q6 to ambient {Q_LOSS:.1f} kW")
    print(f"  reaction enthalpy at 298 K: RX1 {dh1:.1f} kJ/mol, RX2 {dh2:.1f} kJ/mol, "
          f"total {q_rx:.0f} kW = {q_rx / P_FUR:.1%} of the furnace power")
    # the values process/flowsheet.yaml cites from this script (balance-output contract):
    # STREAMS plus S10B, the sorted unreacted mix (recycle and purge), and the duties
    flowsheet = {}
    for sid, title, s in STREAMS + [("S10B", "Sorted unreacted mix", add(rec, purge))]:
        flowsheet[sid] = {"flow": {"value": total(s), "basis": "mass"},
                          "composition": {"values": {k: v / total(s) for k, v in s.items()},
                                          "basis": "mass_fraction"}}
    flowsheet.update({qid: {"duty": q} for qid, q in {
        "Q1": P_FUR, "Q2": Q_CW, "Q3": P_AUX, "Q4": P_CRU, "Q5": Q_COOL, "Q6": Q_LOSS}.items()})
    write_balance_output({"design": flowsheet})
    print("# per kg crushed crude SiC (unallocated)")
    for name, v in [("sand", total(sand)), ("coke", total(coke)), ("metallurgical SiC", total(met)),
                    ("purge", total(purge)), ("CO2", flue["CO2"]), ("CO", flue["CO"]),
                    ("CH4", flue["CH4"]), ("SO2", flue["SO2"]), ("SiO2 fume", flue["SiO2"]),
                    ("electricity kWh", P_FUR + P_AUX + P_CRU)]:
        print(f"  {name:20s} {v / P_CRUDE:.4f}")
    print("# cross-checks")
    print(f"  SiC formed {sic_out:.1f} kg/h; coke per kg SiC formed {total(coke) / sic_out:.3f} "
          f"(IPCC defaults imply 2.62/2.30 = 1.14)")
    co2_all = (n_co + n_ch4) * MW["CO2"]
    print(f"  CO2 if all gas carbon is oxidised: {co2_all / sic_out:.3f} kg/kg SiC (IPCC Tier 1: 2.62); "
          f"{co2_all / total(coke):.3f} kg/kg coke (IPCC: 2.30)")
    c_in = elements(coke)["C"]
    print(f"  coke carbon retained in SiC {xi1 * (1) * 1 / c_in:.3f} of coke C fed (EPA TSD 2009: about 0.35)")
    print(f"  furnace charge {total(charge):.0f} kg/h; SiC formed / charge {sic_out / total(charge):.3f}")
