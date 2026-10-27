"""Independent heat and material balance of the methanol loop and purification (DESIGN.md D-006).

This is NOT a cheme-as-code calculation. Core cannot yet qualify the property regime of this
plant (core #315: no benchmarked package for syngas with methanol and water, hot converter gas
with CO above 500 K, or liquid methanol-water; DWSIM PR/NRTL are benchmarked only for N2/O2/Ar
and ethanol-water). Its results go into process/flowsheet.yaml as `assumed` values with this
script as their source, and cheme checks them: mass and element balances, the reaction
extents, and the converter outlet, which cheme computes itself (equilibrium reactor, the same
reactions and formation data) and which this script must reproduce.

Model (all choices are DESIGN.md decisions, ASSUMED where marked there):
- converter: chemical equilibrium of MEOH_CO and WGS (MEOH_CO2 is their sum) at the outlet
  temperature plus an approach, Peng-Robinson fugacity coefficients without interaction
  parameters, standard state 1 bar, formation data of process/materials.yaml: the same model
  as cheme's `reactor: equilibrium, fugacity: peng_robinson`;
- flashes, enthalpies and compressor discharge: thermo 0.6 Peng-Robinson with the ChemSep kij
  set, ideal-gas heat capacities of thermo (unqualified for this mixture, see above);
- topping and refining columns: component splits from specifications and assumed reflux.

Run: cheme run scripts/loop_balance.py [APPROACH_K]   (prints the stream values and line sizes;
JSON copy in build/; the flowsheet uses the default approach of 10 K, other values are the
D-005 sensitivity only)
"""

import json
import math
import sys
from pathlib import Path

import yaml
from scipy.optimize import fsolve
from thermo import CEOSGas, CEOSLiquid, ChemicalConstantsPackage, FlashVL, PRMIX
from thermo.interaction_parameters import IPDB

R = 8.314462618
P0 = 100.0  # kPa, the standard state of cheme's equilibrium constants
ROOT = Path(__file__).resolve().parents[1]
C = ["H2", "CO", "CO2", "CH4", "N2", "CH3OH", "H2O"]
GASES = ["H2", "CO", "CO2", "CH4", "N2"]
MAT = {c["id"]: c for c in yaml.safe_load((ROOT / "process/materials.yaml").read_text())["components"]}
MW = {c: MAT[c]["molar_mass"] for c in C}

# ---- basis (DESIGN.md D-002 to D-008)
PRODUCT_KG_H = 2500e3 / 24          # D-002: 2500 t/d of product stream
MAKEUP = {"H2": 0.680, "CO": 0.215, "CO2": 0.075, "CH4": 0.025, "N2": 0.005, "CH3OH": 0.0, "H2O": 0.0}  # D-004
T_MU, P_MU = 313.15, 2600.0         # makeup at the battery limit
P_K101 = 7550.0                     # makeup compressor discharge
P_LOOP = 7500.0                     # aftercooler outlet = circulator suction = HP separator
P_K102 = 8150.0                     # circulator discharge
P_RIN, P_ROUT = 8100.0, 7900.0      # converter inlet and outlet
P_FEHE_HOT = 7800.0                 # feed-effluent exchanger hot outlet
T_RIN, T_ROUT, APPROACH = 498.15, 528.15, 10.0
if len(sys.argv) > 1:                # sensitivity only: `cheme run scripts/loop_balance.py 20`
    APPROACH = float(sys.argv[1])
T_COOL = 313.15
ETA = 0.75                          # isentropic efficiency of both compressors
RECYCLE_RATIO = 4.0                 # recycle / makeup, molar
P_LP = 600.0                        # LP separator
T101_TOP_T, T101_TOP_P, T101_BOT_P, T101_REFLUX = 313.15, 150.0, 200.0, 0.3
T102_TOP_P, T102_BOT_P, T102_REFLUX = 110.0, 200.0, 1.5
T102_D_WATER_WT, T102_B_MEOH_WT = 0.0005, 0.0001
T_PRODUCT, P_PRODUCT = 313.15, 300.0

# ---- equilibrium (formation data of materials.yaml)
RXN = {"MEOH_CO": {"CO": -1, "H2": -2, "CH3OH": 1}, "WGS": {"CO": -1, "H2O": -1, "CO2": 1, "H2": 1}}


def g_rt(c, t):
    ig = MAT[c]["ideal_gas"]
    a = ig["cp_R"]
    h = ig["dHf_298"] / R + sum(a[k] / (k + 1) * (t ** (k + 1) - 298.15 ** (k + 1)) for k in range(5))
    s = ig["S_298"] / R + a[0] * math.log(t / 298.15) + sum(a[k] / k * (t**k - 298.15**k) for k in range(1, 5))
    return h / t - s


def ln_k(r, t):
    return -sum(nu * g_rt(c, t) for c, nu in RXN[r].items())


CRIT = [MAT[c]["critical"] for c in C]


def phis(t, p, zs):
    eos = PRMIX(T=t, P=p * 1e3, zs=zs, Tcs=[k["Tc"] for k in CRIT], Pcs=[k["Pc"] * 1e3 for k in CRIT],
                omegas=[k["omega"] for k in CRIT], kijs=[[0.0] * len(C) for _ in C])
    return eos.phis_g if hasattr(eos, "phis_g") else eos.phis_l


def equilibrate(n_in, t, p):
    lk = {r: ln_k(r, t + APPROACH) for r in RXN}

    def outlet(x):
        n = dict(n_in)
        for r, xi in zip(RXN, x):
            for c, nu in RXN[r].items():
                n[c] += nu * xi
        return n

    def f(x):
        n = outlet(x)
        if min(n[c] for c in ("H2", "CO", "CO2", "H2O", "CH3OH")) <= 0:
            return [1e3, 1e3]
        tot = sum(max(v, 1e-30) for v in n.values())
        zs = [max(n[c], 1e-30) / tot for c in C]
        ph = phis(t, p, zs)
        lna = {c: math.log(zs[i] * ph[i] * p / P0) for i, c in enumerate(C)}
        return [sum(nu * lna[c] for c, nu in RXN[r].items()) - lk[r] for r in RXN]

    x = fsolve(f, [0.5 * n_in["CO"], -0.02 * n_in["CO2"] + 1e-6 * n_in["H2"]], xtol=1e-13)
    out = outlet(x)
    assert min(out.values()) >= 0, out
    return out, dict(zip(RXN, x))


# ---- thermo flash (PR, ChemSep kij)
IDS = ["hydrogen", "carbon monoxide", "carbon dioxide", "methane", "nitrogen", "methanol", "water"]
CONSTS, PROPS = ChemicalConstantsPackage.from_IDs(IDS)
KIJ = IPDB.get_ip_asymmetric_matrix("ChemSep PR", CONSTS.CASs, "kij")
_KW = dict(Tcs=CONSTS.Tcs, Pcs=CONSTS.Pcs, omegas=CONSTS.omegas, kijs=KIJ)
FLASH = FlashVL(CONSTS, PROPS, liquid=CEOSLiquid(PRMIX, _KW, HeatCapacityGases=PROPS.HeatCapacityGases),
                gas=CEOSGas(PRMIX, _KW, HeatCapacityGases=PROPS.HeatCapacityGases))


def tot(n):
    return sum(n.values())


def zs_of(n):
    return [n[c] / tot(n) for c in C]


def flash(n, **spec):
    """spec in K, kPa, kW (enthalpy flow) or kW/K (entropy flow); returns T, P, vapour fraction,
    vapour and liquid kmol/h and the enthalpy flow in kW (thermo's ideal-gas 298.15 K basis)."""
    kw = {}
    if "T" in spec:
        kw["T"] = spec["T"]
    if "P" in spec:
        kw["P"] = spec["P"] * 1e3
    if "H" in spec:
        kw["H"] = spec["H"] * 3600 / tot(n)
    if "S" in spec:
        kw["S"] = spec["S"] * 3600 / tot(n)
    if "VF" in spec:
        kw["VF"] = spec["VF"]
    r = FLASH.flash(zs=zs_of(n), **kw)
    vf = r.VF
    vap = {c: vf * tot(n) * r.gas.zs[i] for i, c in enumerate(C)} if r.gas else {c: 0.0 for c in C}
    liq = {c: n[c] - vap[c] for c in C}
    return {"T": r.T, "P": r.P / 1e3, "VF": vf, "vap": vap, "liq": liq,
            "H": r.H() * tot(n) / 3600, "S": r.S() * tot(n) / 3600}


def compress(n, t, p_in, p_out):
    a = flash(n, T=t, P=p_in)
    s = flash(n, P=p_out, S=a["S"])
    h = a["H"] + (s["H"] - a["H"]) / ETA
    b = flash(n, P=p_out, H=h)
    return b, h - a["H"]


def hf(n):  # formation enthalpy flow, kW
    return sum(n[c] * MAT[c]["ideal_gas"]["dHf_298"] for c in C) / 3600


def add(*ns):
    return {c: sum(n[c] for n in ns) for c in C}


def scale(n, f):
    return {c: n[c] * f for c in C}


# ---- the loop: unknowns recycle (7) and purge fraction, makeup 1000 kmol/h
MU = {c: 1000.0 * MAKEUP[c] for c in C}


def loop(v):
    rec = {c: max(v[i], 0.0) for i, c in enumerate(C)}
    purge = v[-1]
    out, xi = equilibrate(add(MU, rec), T_ROUT, P_ROUT)
    sep = flash(out, T=T_COOL, P=P_LOOP)
    new = scale(sep["vap"], 1 - purge)
    return rec, purge, out, xi, sep, new


def residual(v):
    rec, purge, _, _, _, new = loop(v)
    return [new[c] - rec[c] for c in C] + [tot(rec) - RECYCLE_RATIO * tot(MU)]


guess = [RECYCLE_RATIO * 1000 * g for g in (0.80, 0.03, 0.06, 0.08, 0.02, 0.005, 0.0005)] + [0.05]
sol = fsolve(residual, guess, xtol=1e-12, maxfev=4000)
assert max(abs(r) for r in residual(sol)) < 1e-6, residual(sol)
rec, purge, rout, xi, sep, _ = loop(sol)
mix_n = add(MU, rec)

# ---- purification (per basis)
lp = flash(sep["liq"], P=P_LP, H=flash(sep["liq"], T=T_COOL, P=P_LOOP)["H"])
crude = lp["liq"]
psat = FLASH.flash(zs=[0, 0, 0, 0, 0, 1, 0], T=T101_TOP_T, VF=0).P / 1e3   # methanol vapour pressure, kPa
y_meoh = psat / T101_TOP_P
t101_top = {c: (crude[c] if c in GASES else 0.0) for c in C}
t101_top["CH3OH"] = tot(t101_top) * y_meoh / (1 - y_meoh)
t101_bot = {c: (crude[c] - t101_top[c]) if c in ("CH3OH", "H2O") else 0.0 for c in C}
# refining column: mass splits from the product and bottoms specifications
fm, fw = t101_bot["CH3OH"] * MW["CH3OH"], t101_bot["H2O"] * MW["H2O"]
# unknowns Dm, Dw: Dw = a Dm with a = wD/(1-wD); Bm = b Bw with b = wB/(1-wB)
a_, b_ = T102_D_WATER_WT / (1 - T102_D_WATER_WT), T102_B_MEOH_WT / (1 - T102_B_MEOH_WT)
bw = (fw - a_ * fm) / (1 - a_ * b_)
bm = b_ * bw
dm, dw = fm - bm, fw - bw
dist = {c: 0.0 for c in C} | {"CH3OH": dm / MW["CH3OH"], "H2O": dw / MW["H2O"]}
bott = {c: 0.0 for c in C} | {"CH3OH": bm / MW["CH3OH"], "H2O": bw / MW["H2O"]}

factor = PRODUCT_KG_H / (dm + dw)


def big(n):
    return scale(n, factor)


# ---- states and duties at plant scale
S = {}
D = {}
mu, recs, mixs = big(MU), big(rec), big(mix_n)
S["S1"] = (mu, T_MU, P_MU)
k101, D["K101"] = compress(mu, T_MU, P_MU, P_K101)
S["S2"] = (mu, k101["T"], P_K101)
D["E104"] = k101["H"] - flash(mu, T=T_COOL, P=P_LOOP)["H"]
S["S3"] = (mu, T_COOL, P_LOOP)
h_mix = flash(mu, T=T_COOL, P=P_LOOP)["H"] + flash(recs, T=T_COOL, P=P_LOOP)["H"]
mx = flash(mixs, P=P_LOOP, H=h_mix)
S["S4"] = (mixs, mx["T"], P_LOOP)
k102, D["K102"] = compress(mixs, mx["T"], P_LOOP, P_K102)
S["S5"] = (mixs, k102["T"], P_K102)
cold_out = flash(mixs, T=T_RIN, P=P_RIN)
D["E101"] = cold_out["H"] - k102["H"]
S["S6"] = (mixs, T_RIN, P_RIN)
routs = big(rout)
hot_in = flash(routs, T=T_ROUT, P=P_ROUT)
S["S7"] = (routs, T_ROUT, P_ROUT)
hot_out = flash(routs, P=P_FEHE_HOT, H=hot_in["H"] - D["E101"])
S["S8"] = (routs, hot_out["T"], P_FEHE_HOT)
seps = flash(routs, T=T_COOL, P=P_LOOP)
D["E102"] = hot_out["H"] - seps["H"]
S["S9"] = (routs, T_COOL, P_LOOP)
D["R101"] = (hf(mixs) + cold_out["H"]) - (hf(routs) + hot_in["H"])
S["S10"] = (seps["vap"], T_COOL, P_LOOP)
S["S11"] = (scale(seps["vap"], purge), T_COOL, P_LOOP)
S["S12"] = (scale(seps["vap"], 1 - purge), T_COOL, P_LOOP)
S["S13"] = (seps["liq"], T_COOL, P_LOOP)
lps = flash(seps["liq"], P=P_LP, H=flash(seps["liq"], T=T_COOL, P=P_LOOP)["H"])
S["S14"] = (lps["vap"], lps["T"], P_LP)
S["S15"] = (lps["liq"], lps["T"], P_LP)
top1, bot1 = big(t101_top), big(t101_bot)
b1 = flash(bot1, P=T101_BOT_P, VF=0)
S["S16"] = (top1, T101_TOP_T, T101_TOP_P)
S["S17"] = (bot1, b1["T"], T101_BOT_P)
meoh = {c: 0.0 for c in C} | {"CH3OH": 1.0}
dh_vap_meoh = (flash(meoh, T=T101_TOP_T, VF=1)["H"] - flash(meoh, T=T101_TOP_T, VF=0)["H"])  # kW per kmol/h
D["T101C"] = T101_REFLUX * tot(lps["liq"]) * dh_vap_meoh
h_feed1 = flash(lps["liq"], T=lps["T"], P=P_LP)["H"]
h_top1 = flash(top1, T=T101_TOP_T, P=T101_TOP_P)["H"]
D["T101R"] = D["T101C"] + h_top1 + b1["H"] - h_feed1
dists, botts = big(dist), big(bott)
top2 = flash(dists, P=T102_TOP_P, VF=1)
prod = flash(dists, T=T_PRODUCT, P=P_PRODUCT)
D["T102C"] = (1 + T102_REFLUX) * (top2["H"] - prod["H"])
b2 = flash(botts, P=T102_BOT_P, VF=0)
D["T102R"] = D["T102C"] + prod["H"] + b2["H"] - b1["H"]
S["S18"] = (dists, T_PRODUCT, P_PRODUCT)
S["S19"] = (botts, b2["T"], T102_BOT_P)


def mass(n):
    return sum(n[c] * MW[c] for c in C)


# ---- first-pass line size (D-011): bulk density of the PR flash, velocity by service (ASSUMED)
DN_SERIES = [15, 20, 25, 32, 40, 50, 65, 80, 100, 125, 150, 200, 250, 300, 350, 400, 450, 500,
             600, 700, 750, 800, 900, 1000, 1200]


def line_size(n, t, p):
    r = FLASH.flash(zs=zs_of(n), T=t, P=p * 1e3)
    rho = r.rho_mass()
    vf = r.VF
    v = 1.5 if vf < 0.01 else (10.0 if vf < 0.99 else (15.0 if p > 1000 else 20.0))
    d_mm = 1000 * math.sqrt(4 * mass(n) / 3600 / rho / v / math.pi)
    return rho, vf, v, d_mm, next(dn for dn in DN_SERIES if dn >= d_mm)


# ---- report
report = {
    "purge_fraction": purge, "recycle_ratio": tot(rec) / tot(MU), "scale": factor,
    "extents_kmol_h": {r: x * factor for r, x in xi.items()},
    "SN_makeup": (MAKEUP["H2"] - MAKEUP["CO2"]) / (MAKEUP["CO"] + MAKEUP["CO2"]),
    "carbon_to_crude": (sep["liq"]["CH3OH"]) / (MU["CO"] + MU["CO2"]),
    "carbon_to_product": dist["CH3OH"] / (MU["CO"] + MU["CO2"]),
    "per_pass_CO_conversion": 1 - rout["CO"] / mix_n["CO"],
    "per_pass_COx_to_methanol": (rout["CH3OH"] - mix_n["CH3OH"]) / (mix_n["CO"] + mix_n["CO2"]),
    "fehe_hot_out_vapour_fraction": hot_out["VF"], "hp_separator_vapour_fraction": seps["VF"],
    "lp_flash_T": lps["T"], "methanol_psat_313K_kPa": psat,
    "duties_kW": D,
    "streams": {k: {"T_K": t, "P_kPa": p, "kg_h": mass(n), "kmol_h": tot(n),
                    "y": {c: n[c] / tot(n) for c in C if tot(n) > 0}} for k, (n, t, p) in S.items()},
}
(ROOT / "build").mkdir(exist_ok=True)
(ROOT / f"build/loop_balance_approach{APPROACH:g}.json").write_text(json.dumps(report, indent=1))
print(f"# approach {APPROACH:g} K; make-up {mass(mu):.1f} kg/h for {PRODUCT_KG_H:.1f} kg/h product")
for k in ("purge_fraction", "recycle_ratio", "SN_makeup", "carbon_to_crude", "carbon_to_product",
          "per_pass_CO_conversion", "per_pass_COx_to_methanol", "fehe_hot_out_vapour_fraction",
          "hp_separator_vapour_fraction", "methanol_psat_313K_kPa", "extents_kmol_h"):
    print(f"# {k}: {report[k]}")
print("# duties kW: " + ", ".join(f"{k} {v:.0f}" for k, v in D.items()))
for k, (n, t, p) in S.items():
    comp = ", ".join(f"{c}: {n[c] / tot(n):.8f}" for c in C)
    print(f"{k}: T {t:.2f} K, P {p:.0f} kPa, {mass(n):.1f} kg/h, {tot(n):.2f} kmol/h, {{{comp}}}")
for k, (n, t, p) in S.items():
    rho, vf, v, d_mm, dn = line_size(n, t, p)
    print(f"# line {k}: rho {rho:.2f} kg/m3, vapour fraction {vf:.3f}, {v} m/s -> d {d_mm:.0f} mm, DN{dn}")
