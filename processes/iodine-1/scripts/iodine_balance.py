"""Heat and material balance of iodine-1 (brine blowing-out route), design case (DESIGN.md D-006).

Run with `cheme run scripts/iodine_balance.py build/streams.yaml`: prints the summary and writes
the `streams:` block of process/flowsheet.yaml to the scratch file given (never to the
repository). Every value it produces is ASSUMED: it rests on the sourced brine iodine content
(300 mg/kg I, D-003) and the ASSUMED design parameters below, each with its decision.

Dissolved species are carried as neutral molecules (NaI, NaCl, HI, HCl, H2SO4, Na2SO4, NaHCO3,
I2, Cl2, SO2, CO2 in water): an inventory basis, not a speciation (D-007). The
recycles (absorber gas loop, filtrate and spent melter acid to the brine head) are solved by
successive substitution; the plant is linear in the brine flow, which is then scaled to the
product rate.
"""
import sys

MW = {"H2O": 18.015, "NaCl": 58.443, "NaI": 149.894, "NaHCO3": 84.007, "Na2SO4": 142.04,
      "H2SO4": 98.079, "HCl": 36.461, "HI": 127.912, "I2": 253.809, "Cl2": 70.906,
      "SO2": 64.066, "CO2": 44.010, "N2": 28.014, "O2": 31.998, "NaOH": 39.997}
M_I = 126.904

# ---- design parameters (DESIGN.md D-002 .. D-009)
PRODUCT = 125.0             # kg/h iodine flakes: 1000 t/a at 8000 h/a (D-002, ASSUMED)
PURITY = 0.998              # mass fraction I2 in the product, rest water (D-002, ASSUMED)
I_BRINE = 300e-6            # kg I per kg brine, as iodide (D-003, sourced)
NACL = 0.10                 # mass fraction NaCl in the brine (D-003, ASSUMED)
ALK = 2.0e-3                # kmol NaHCO3 per t... per 1000 kg brine (alkalinity 2 meq/kg, D-003, ASSUMED)
RHO_BRINE = 1070.0          # kg/m3 at 313 K, 10 wt% NaCl (D-003, ASSUMED)
CL2_EXCESS = 1.05           # chlorine over the iodide-to-iodine stoichiometry in R-101 (D-004)
X_OXI = 0.98                # iodide oxidised in R-101 (NaI and HI) (D-004)
STRIP = 0.92                # fraction of the dissolved I2 blown out in T-201 (D-005)
AIR_RATIO = 130.0           # Nm3 dry gas into T-201 per m3 brine (D-005)
Y_H2O = 0.068               # water mole fraction of the saturated loop gas, 313 K / 103 kPa (D-005)
PURGE = 0.05                # fraction of the absorber exit gas purged to the vent (D-005)
ABS = 0.995                 # fraction of the I2 entering T-202 absorbed (D-005)
SO2_EXCESS = 1.02           # SO2 over the I2 + Cl2 absorbed (D-005)
HI_BLEED = 0.10             # mass fraction HI of the absorber bleed (D-005)
X_PREC = 0.995              # HI oxidised to I2 in R-301 (D-006)
SOLID = 0.99                # fraction of the I2 in R-301 that precipitates (D-006)
CAKE_LIQ = 0.10             # mother liquor in the filter cake, mass fraction (D-006)
ACID = 0.20                 # kg H2SO4 (100 %) per kg I2 into the melter, as 98.5 wt% acid (D-006)
H2SO4_W = 0.985

def kmol(s):
    return {k: v / MW[k] for k, v in s.items()}

def kg(n):
    return {k: v * MW[k] for k, v in n.items()}

def add(*ss):
    out = {}
    for s in ss:
        for k, v in s.items():
            out[k] = out.get(k, 0.0) + v
    return out

def scale(s, f):
    return {k: v * f for k, v in s.items()}

def total(s):
    return sum(s.values())

def solve(brine_kg):
    """All streams (kg/h by component) for a brine flow; recycles by substitution."""
    nai = brine_kg * I_BRINE / M_I                       # kmol/h
    s1 = {"NaI": nai * MW["NaI"], "NaCl": NACL * brine_kg, "NaHCO3": ALK * brine_kg / 1000 * MW["NaHCO3"]}
    s1["H2O"] = brine_kg - total(s1)
    s16, s19 = {}, {}
    s9 = {}
    vol = brine_kg / RHO_BRINE
    dry_air = AIR_RATIO * vol / 22.414                   # kmol/h dry gas into T-201
    for _ in range(200):
        # ---- R-101: acidification (ALK) and chlorination (OXI, OXH1)
        feed = kmol(add(s1, s16, s19))
        cl2 = CL2_EXCESS * 0.5 * (feed.get("NaI", 0) + feed.get("HI", 0))
        n = dict(feed)
        n["Cl2"] = n.get("Cl2", 0) + cl2
        a = n["NaHCO3"]                                   # ALK: 2 NaHCO3 + H2SO4 -> Na2SO4 + 2 CO2 + 2 H2O
        n["NaHCO3"] -= a; n["H2SO4"] = n.get("H2SO4", 0) - a / 2
        n["Na2SO4"] = n.get("Na2SO4", 0) + a / 2; n["CO2"] = n.get("CO2", 0) + a; n["H2O"] += a
        e1 = X_OXI * n["NaI"] / 2                         # OXI: 2 NaI + Cl2 -> 2 NaCl + I2
        n["NaI"] -= 2 * e1; n["Cl2"] -= e1; n["NaCl"] += 2 * e1; n["I2"] = n.get("I2", 0) + e1
        e2 = X_OXI * n.get("HI", 0) / 2                   # OXH1: 2 HI + Cl2 -> 2 HCl + I2
        n["HI"] = n.get("HI", 0) - 2 * e2; n["Cl2"] -= e2; n["HCl"] = n.get("HCl", 0) + 2 * e2; n["I2"] += e2
        s2 = {"Cl2": cl2 * MW["Cl2"]}
        s3 = kg(n)
        # ---- T-201: blowing-out (I2 92 %, Cl2, CO2 completely; water to saturate the purge)
        strip = {"I2": STRIP * s3["I2"], "Cl2": s3["Cl2"], "CO2": s3["CO2"]}
        s9n = kmol(s9) if s9 else {}
        recyc_dry = {k: v for k, v in s9n.items() if k != "H2O"}
        mk_n2 = 0.79 * (dry_air - recyc_dry.get("N2", 0) - recyc_dry.get("O2", 0))
        mk_o2 = 0.21 * (dry_air - recyc_dry.get("N2", 0) - recyc_dry.get("O2", 0))
        s10 = {"N2": mk_n2 * MW["N2"], "O2": mk_o2 * MW["O2"]}
        g1_dry = add(recyc_dry, kmol(s10), kmol(strip))
        g1_dry.pop("H2O", None)
        w = Y_H2O / (1 - Y_H2O) * total(g1_dry)          # kmol/h water in the saturated gas
        evap = w - s9n.get("H2O", 0)
        s5 = kg(add(g1_dry, {"H2O": w}))
        s4 = add(s3, scale(strip, -1), {"H2O": -evap * MW["H2O"]})
        # ---- T-202: absorption with SO2 (ABS on I2, CLS_A on Cl2), bleed at 10 wt% HI
        g = kmol(s5)
        i2a = ABS * g["I2"]; cla = g["Cl2"]
        so2 = SO2_EXCESS * (i2a + cla)
        bleed = {"HI": 2 * i2a, "HCl": 2 * cla, "H2SO4": i2a + cla, "SO2": so2 - i2a - cla}
        bleed_kg = kg(bleed)
        tot = bleed_kg["HI"] / HI_BLEED
        bleed_kg["H2O"] = tot - total(bleed_kg)
        water_used = 2 * (i2a + cla) * MW["H2O"]
        s12 = {"H2O": bleed_kg["H2O"] + water_used}
        s11 = {"SO2": so2 * MW["SO2"]}
        s13 = bleed_kg
        s6 = kg(add(g, {"I2": -i2a, "Cl2": -cla}))
        s6 = {k: v for k, v in s6.items() if abs(v) > 0}
        s7 = scale(s6, PURGE)
        s8 = scale(s6, 1 - PURGE)
        s9_new = s8
        # ---- R-301: oxidation and precipitation (OXH2 on HI, CLS_B on SO2)
        b = kmol(s13)
        e3 = X_PREC * b["HI"] / 2
        e4 = b["SO2"]
        cl2p = e3 + e4
        s14 = {"Cl2": cl2p * MW["Cl2"]}
        r = dict(b)
        r["HI"] -= 2 * e3; r["HCl"] += 2 * e3; r["I2"] = e3
        r["SO2"] = 0.0; r["H2O"] -= 2 * e4; r["H2SO4"] += e4; r["HCl"] += 2 * e4
        s15 = {k: v for k, v in kg(r).items() if v > 0}
        # ---- F-301: cake = precipitated I2 + 10 wt% mother liquor
        solid = SOLID * s15["I2"]
        liquor = add(s15, {"I2": -solid})
        liq_cake = CAKE_LIQ / (1 - CAKE_LIQ) * solid
        f = liq_cake / total(liquor)
        cake_liq = scale(liquor, f)
        s17 = add(cake_liq, {"I2": solid})
        s16_new = scale(liquor, 1 - f)
        # ---- M-301: melting under 98.5 wt% sulfuric acid
        acid = ACID * solid
        s18 = {"H2SO4": acid, "H2O": acid / H2SO4_W - acid}
        prod_w = solid * (1 - PURITY) / PURITY
        s20 = {"I2": solid, "H2O": prod_w}
        s19_new = add(cake_liq, s18, {"H2O": -prod_w})
        conv = abs(total(s16_new) - total(s16)) + abs(total(s9_new) - total(s9)) + abs(total(s19_new) - total(s19))
        s16, s19, s9 = s16_new, s19_new, s9_new
        if conv < 1e-10 * brine_kg:
            break
    # ---- R-401: neutralisation with 50 wt% caustic (NEU1-3), P-401 reinjection
    m = kmol(s4)
    naoh = 2 * m.get("H2SO4", 0) + m.get("HCl", 0) + m.get("HI", 0)
    s22 = {"NaOH": naoh * MW["NaOH"], "H2O": naoh * MW["NaOH"]}
    n = add(m, kmol(s22))
    h, c, hi = n.pop("H2SO4", 0), n.pop("HCl", 0), n.pop("HI", 0)
    n["NaOH"] -= naoh
    n["Na2SO4"] += h; n["NaCl"] += c; n["NaI"] += hi; n["H2O"] += 2 * h + c + hi
    n.pop("NaOH")
    s23 = kg(n)
    return dict(S1=s1, S2=s2, S3=s3, S4=s4, S5=s5, S6=s6, S7=s7, S8=s8, S9=s9, S10=s10, S11=s11,
                S12=s12, S13=s13, S14=s14, S15=s15, S16=s16, S17=s17, S18=s18, S19=s19, S20=s20,
                S21=s20, S22=s22, S23=s23, S24=s23), dict(naoh=naoh, dry_air=dry_air, vol=vol)

# The plant is linear in the brine flow: solve at 1 t/h, scale to the product.
base, _ = solve(1000.0)
brine = 1000.0 * PRODUCT * PURITY / base["S20"]["I2"]
S, aux = solve(brine)

# ---- energy (D-008), all ASSUMED
fan_m3s = total(kmol(S["S9"])) * 22.414 * 313.15 / 273.15 / 3600 * 101.325 / 106.0
q_fan = fan_m3s * 4.0 / 0.70                                   # kW: 4 kPa, efficiency 0.70
q_inj = aux["vol"] / 3600 * 3000.0 / 0.75                      # kW: 3000 kPa, efficiency 0.75
q_abs = 30.0 * 300.0 / 3600 / 0.60                             # kW: 30 m3/h absorbent, 300 kPa, 0.60
q_rec = 15.0                                                   # kW: filter, melter agitator, flaker drive
i2 = S["S20"]["I2"]
q_melt = (i2 * (0.23 * (387.0 - 313.15) + 61.2 + 0.45 * (393.15 - 387.0))
          + total(S["S17"]) * 0 + (total(S["S17"]) - i2 + total(S["S18"])) * 3.0 * 80.0) / 3600
q_steam = q_melt * 1.5                                          # 50 % losses
q_flake = i2 * (0.45 * (393.15 - 387.0) + 61.2 + 0.23 * (387.0 - 313.15)) / 3600

TP = {  # stream: (title, from, to, T K, P kPa(a), note)
    "S1": ("Raw brine from the wellfield", "BRINE.out", "R101.brine", 313.15, 300.0),
    "S2": ("Chlorine to the brine chlorination", "CL2.r101", "R101.cl2", 298.15, 400.0),
    "S3": ("Acidified chlorinated brine", "R101.out", "T201.brine", 313.15, 250.0),
    "S4": ("Stripped brine", "T201.brine_out", "R401.in", 313.15, 110.0),
    "S5": ("Iodine-laden air", "T201.gas", "T202.gas", 313.15, 104.0),
    "S6": ("Absorber exit gas", "T202.gas_out", "S201.in", 313.15, 102.0),
    "S7": ("Loop purge to the vent", "S201.purge", "VENT.in", 313.15, 102.0),
    "S8": ("Return air to the fan", "S201.rec", "K201.in", 313.15, 102.0),
    "S9": ("Circulating air to the blowing-out tower", "K201.out", "T201.gas_in", 313.15, 106.0),
    "S10": ("Make-up air", "AIR.out", "T201.air", 298.15, 101.325),
    "S11": ("Sulfur dioxide", "SO2.out", "T202.so2", 298.15, 300.0),
    "S12": ("Absorber make-up water", "PW.out", "T202.water", 298.15, 300.0),
    "S13": ("Absorber bleed (HI/H2SO4 liquor)", "T202.bleed", "R301.in", 313.15, 300.0),
    "S14": ("Chlorine to the iodine precipitation", "CL2.r301", "R301.cl2", 298.15, 400.0),
    "S15": ("Iodine slurry", "R301.out", "F301.in", 313.15, 200.0),
    "S16": ("Filtrate to the brine head", "F301.filtrate", "R101.filtrate", 313.15, 300.0),
    "S17": ("Crude iodine cake", "F301.cake", "M301.cake", 313.15, 101.325),
    "S18": ("Sulfuric acid 98.5 wt%", "H2SO4.out", "M301.acid", 298.15, 300.0),
    "S19": ("Spent melter acid to the brine head", "M301.acid_out", "R101.acid", 393.15, 300.0),
    "S20": ("Molten iodine", "M301.melt", "X301.in", 393.15, 101.325),
    "S21": ("Iodine flakes to packing", "X301.out", "IODINE.in", 313.15, 101.325),
    "S22": ("Caustic soda 50 wt%", "NAOH.out", "R401.naoh", 298.15, 300.0),
    "S23": ("Neutralised spent brine", "R401.out", "P401.in", 313.15, 110.0),
    "S24": ("Spent brine to reinjection", "P401.out", "SPENT.in", 313.15, 3100.0),
}
# streams propagate fills (pass-through, splitter): flow and composition left to cheme
PROPAGATED = {"S8", "S9", "S21", "S24"}
SRC = "scripts/iodine_balance.py (D-006)"

def fmt(x):
    return float(f"{x:.10g}")

out = ["streams:"]
for sid, (title, fr, to, T, P) in TP.items():
    s = {k: v for k, v in S[sid].items() if v > 1e-12}
    tot = total(s)
    st = [f"pressure: {{value: {P}, provenance: assumed, source: \"D-008\"}}",
          f"temperature: {{value: {T}, provenance: assumed, source: \"D-008\"}}"]
    if sid not in PROPAGATED:
        comp = ", ".join(f"{k}: {fmt(v / tot)}" for k, v in sorted(s.items(), key=lambda kv: -kv[1]))
        st.append(f"flow: {{value: {fmt(tot)}, basis: mass, provenance: assumed, source: \"{SRC}\"}}")
        st.append(f"composition: {{basis: mass_fraction, values: {{{comp}}}, provenance: assumed, source: \"{SRC}\"}}")
    out.append(f"  - id: {sid}\n    title: \"{title}\"\n    from: {fr}\n    to: {to}\n    template: iodine\n    state:\n      design:")
    out.extend(f"        {line}" for line in st)
Q = [("Q1", "K-201 fan power", "POWER.k201", "K201.power", q_fan, "4 kPa rise, efficiency 0.70 (D-008)"),
     ("Q2", "P-401 reinjection pump power", "POWER.p401", "P401.power", q_inj, "3000 kPa rise, efficiency 0.75 (D-008)"),
     ("Q3", "P-202 absorbent circulation pump power", "POWER.t202", "T202.power", q_abs, "30 m3/h, 300 kPa, efficiency 0.60 (D-008)"),
     ("Q4", "Filter, melter agitator and flaker drives", "POWER.rec", "F301.power", q_rec, "lumped estimate, not sized (D-008)"),
     ("Q5", "LP steam to the M-301 melter", "LPS.m301", "M301.heat", q_steam, "heating, fusion and acid heating with 50 % losses (D-008)"),
     ("Q6", "X-301 flaker cooling duty", "X301.cw", "CW.x301", q_flake, "solidification and cooling of the iodine (D-008)")]
for qid, title, fr, to, q, src in Q:
    out.append(f"  - {{id: {qid}, title: {title}, kind: energy, from: {fr}, to: {to}, state: {{design: {{duty: {{value: {q:.2f}, provenance: assumed, source: \"scripts/iodine_balance.py: {src}\"}}}}}}}}")

if len(sys.argv) > 1:
    with open(sys.argv[1], "w") as fh:
        fh.write("\n".join(out) + "\n")

# ---- summary
p = PRODUCT
print(f"brine {brine:.1f} kg/h ({aux['vol']:.1f} m3/h), iodine in {brine*I_BRINE:.3f} kg/h I")
print(f"product I2 {i2:.3f} kg/h; overall recovery {i2/(brine*I_BRINE/M_I*MW['I2']/2):.4f}")
spent_I = sum(S['S24'].get(k, 0) / MW[k] * (2 if k == 'I2' else 1) for k in ('NaI', 'HI', 'I2')) * M_I
print(f"iodine left in the spent brine {spent_I:.3f} kg/h = {spent_I/total(S['S24'])*1e6:.1f} mg/kg")
n3 = kmol(S["S3"])
hplus = 2 * n3.get("H2SO4", 0) + n3.get("HCl", 0) + n3.get("HI", 0)
print(f"free strong acid in S3 {hplus/total(S['S3'])*1e6:.2f} mmol H+/kg (pH about {-__import__('math').log10(hplus/total(S['S3'])*1e3*RHO_BRINE/1000):.2f}, ideal)")
for sid in ("S2", "S14", "S11", "S18", "S22", "S12", "S10", "S7", "S5"):
    print(f"{sid} {total(S[sid]):.3f} kg/h = {total(S[sid])/p:.5f} kg/kg  {({k: round(v, 4) for k, v in S[sid].items()})}")
print(f"Q fan {q_fan:.1f} kW, inj {q_inj:.1f} kW, abs {q_abs:.1f} kW, rec {q_rec:.1f}, steam {q_steam:.2f} kW, flaker {q_flake:.2f} kW")
ins = sum(total(S[k]) for k in ("S1", "S2", "S10", "S11", "S12", "S14", "S18", "S22"))
outs = sum(total(S[k]) for k in ("S7", "S21", "S24"))
print(f"plant in {ins:.3f} out {outs:.3f} diff {ins-outs:.2e} kg/h")


# the values process/flowsheet.yaml cites from this script (balance-output contract)
FLOWSHEET = {}
for sid in TP:
    if sid not in PROPAGATED:
        s = {k: v for k, v in S[sid].items() if v > 1e-12}
        FLOWSHEET[sid] = {"flow": total(s), "composition": {k: v / total(s) for k, v in s.items()}}
FLOWSHEET.update({qid: {"duty": q} for qid, title, fr, to, q, src in Q})


def write_balance_output(cases):
    """With BALANCE_OUTPUT set, write the values the flowsheet cites from this script as JSON.

    The process library's balance-output contract (docs/adr/0027 of the library): case ->
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


write_balance_output({"design": FLOWSHEET})
