"""Independent heat and material balance of the HDA plant (DESIGN.md D-006).

This is NOT a cheme-as-code calculation. Core has no qualified property package for aromatics
with hydrogen and methane (the packaged ones cover air and syngas), so flashes,
column splits and duties are computed here and enter process/flowsheet.yaml as `assumed`
values with this script as their source. cheme then checks them: mass, component and element
balances, the reactor extents (cheme computes the reactor outlet itself from the same
conversion and selectivity), mixers and splitters (cheme propagate).

Model (every choice is a DESIGN.md decision, ASSUMED where marked there):
- feeds (D-020): fresh toluene at the benzene limit of a published commercial toluene
  specification (500 mg/kg benzene, the rest toluene), make-up hydrogen of PSA purity
  (99.9 mol% H2, the rest taken as methane);
- reactor R-101 (D-021): adiabatic; toluene conversion per pass X = 0.75 (the per-pass
  conversion of a published thermal HDA process, US 3,291,849); the biphenyl reaction
  2 BZ <=> BIPH + H2 at chemical equilibrium at the adiabatic outlet (ideal gas, formation data
  of process/materials.yaml), the upper bound of the biphenyl formed from the benzene;
  outlet temperature from the energy balance. Superseded (D-005): the Douglas (1988)
  selectivity correlation, which could not be read at its source (I-06);
- quench: part of the separator liquid mixed into the effluent to QUENCH_T (D-004);
- flashes, enthalpies, compressor and pump: thermo Peng-Robinson with the ChemSep kij set,
  ideal-gas heat capacities of thermo; formation enthalpies of process/materials.yaml added for
  the reactor energy balance (unqualified for this mixture, see above);
- loop specs: H2/aromatics at the reactor inlet RATIO and purge-gas H2 mole fraction Y_PURGE_H2
  (D-007); the fresh toluene follows from the benzene product rate (the balance is scaled,
  exact because every split depends on composition, temperature and pressure only);
- columns: component splits from specifications; stabiliser overhead in equilibrium with an
  aromatic reflux at the partial condenser; benzene and toluene columns by Underwood minimum
  reflux at constant relative volatility, R = R_FACTOR * Rmin; duties from column energy
  balances with the arriving feed enthalpy and saturated products (D-008).

Run: cheme run scripts/hda_balance.py   (prints the stream table, duties and checks; JSON copy
in build/hda_balance.json)
"""

import json
import math
from pathlib import Path

import yaml
from scipy.optimize import brentq, fsolve
from thermo import CEOSGas, CEOSLiquid, ChemicalConstantsPackage, FlashVL, PRMIX
from thermo.interaction_parameters import IPDB

ROOT = Path(__file__).resolve().parents[1]
C = ["H2", "CH4", "TOL", "BZ", "BIPH"]
NAMES = ["hydrogen", "methane", "toluene", "benzene", "biphenyl"]
MAT = {c["id"]: c for c in yaml.safe_load((ROOT / "process/materials.yaml").read_text())["components"]}
MW = {c: MAT[c]["molar_mass"] for c in C}
HF = {c: MAT[c]["ideal_gas"]["dHf_298"] for c in C}  # kJ/kmol
AROM = ["TOL", "BZ", "BIPH"]

# ---- basis (DESIGN.md D-002 to D-010)
PRODUCT_KG_H = 100e6 / 8000          # D-002: 100 kt/a benzene product stream, 8000 h/a
X_D_BZ = 0.999                       # D-002/D-008: benzene product, mol fraction
REC_BZ = 0.995                       # D-008: benzene column recovery of benzene to the top
X_B_TOL_C203 = 0.02                  # D-008: toluene in the biphenyl bottoms, mol fraction
MAKEUP = {"H2": 0.999, "CH4": 0.001, "TOL": 0.0, "BZ": 0.0, "BIPH": 0.0}  # D-020: PSA purity
W_BZ_FEED = 500e-6                   # D-020: benzene in the fresh toluene, mass fraction (spec max)
X = 0.75                             # D-021: toluene conversion per pass (US 3,291,849)
RATIO = 5.0                          # D-007: H2 / aromatics at the reactor inlet, molar
Y_PURGE_H2 = 0.40                    # D-007: H2 mole fraction of the purge gas
T_RIN, P_RIN = 895.15, 3450.0        # D-004: reactor inlet
P_ROUT = 3380.0                      # D-004: reactor outlet (70 kPa bed and heater losses ASSUMED)
QUENCH_T = 893.15                    # D-004: quenched effluent
P_FEHE_HOT, T_SEP, P_SEP = 3310.0, 313.15, 3250.0   # D-004
P_MIX = 3600.0                       # D-004: compressor and pump discharge, mixer
P_FEHE_COLD, P_H2MU, T_H2MU = 3520.0, 3700.0, 313.15  # D-003, D-004
T_TOL_FEED, P_TOL_FEED = 303.15, 300.0               # D-003
P_TOLDRUM = 150.0                    # D-004: toluene feed drum (fresh + recycle), pump suction
T_FEHE_COLD_OUT = 840.0              # D-004: FEHE cold outlet = heater inlet
ETA_K, ETA_P = 0.75, 0.65            # D-010: isentropic compressor, pump efficiency
P_C201, T_C201_COND, R_C201 = 800.0, 313.15, 1.0   # D-008: stabiliser top, condenser, L/D molar
P_C202_TOP, P_C202_BOT = 150.0, 170.0              # D-008
P_C203_TOP, P_C203_BOT = 30.0, 45.0                # D-008
R_FACTOR = 1.3                       # D-008: R / Rmin
R_FLOOR = 0.5                        # D-008: least reflux ratio of an easy split (toluene/biphenyl)
T_PRODUCT = 313.15                   # D-008: benzene product cooled in the condenser train

# ---- thermo
consts, props = ChemicalConstantsPackage.from_IDs(NAMES)
kijs = IPDB.get_ip_asymmetric_matrix("ChemSep PR", consts.CASs, "kij")
EOS = dict(Tcs=consts.Tcs, Pcs=consts.Pcs, omegas=consts.omegas, kijs=kijs)
GAS = CEOSGas(PRMIX, EOS, HeatCapacityGases=props.HeatCapacityGases)
LIQ = CEOSLiquid(PRMIX, EOS, HeatCapacityGases=props.HeatCapacityGases)
FL = FlashVL(consts, props, liquid=LIQ, gas=GAS)


def tot(n):
    return sum(n.values())


def zs(n):
    t = tot(n)
    return [max(n[c], 0.0) / t for c in C]


def add(*ns):
    return {c: sum(n[c] for n in ns) for c in C}


def scale(n, f):
    return {c: n[c] * f for c in C}


def vec(z, t):
    return {c: z[i] * t for i, c in enumerate(C)}


def flash(n, **spec):  # spec in K and kPa
    if "P" in spec:
        spec["P"] = spec["P"] * 1e3
    return FL.flash(zs=zs(n), **spec)


def h_gas(n, t, p):  # kW, sensible (thermo reference: ideal gas 298.15 K) + formation
    if tot(n) == 0:
        return 0.0
    hs = GAS.to(T=t, P=p * 1e3, zs=zs(n)).H()  # J/mol
    return tot(n) / 3600 * (hs + sum(HF[c] * n[c] / tot(n) for c in C))


def h_fl(n, res):  # kW of a flash result (formation included)
    return tot(n) / 3600 * (res.H() + sum(HF[c] * n[c] / tot(n) for c in C))


def mass(n):
    return sum(n[c] * MW[c] for c in C)


R_GAS = 8.314462618                 # kJ/(kmol K)


def _g_ideal(c, t):
    """Ideal-gas Gibbs energy of formation basis (kJ/kmol) at t, 1 bar: dHf_298 + int cp dT
    - t (S_298 + int cp/T dT), cp/R polynomial of process/materials.yaml."""
    ig = MAT[c]["ideal_gas"]
    a = ig["cp_R"]
    t0 = 298.15
    dh = R_GAS * sum(a[i] / (i + 1) * (t ** (i + 1) - t0 ** (i + 1)) for i in range(len(a)))
    ds = R_GAS * (a[0] * math.log(t / t0) + sum(a[i] / i * (t ** i - t0 ** i) for i in range(1, len(a))))
    return ig["dHf_298"] + dh - t * (ig["S_298"] + ds)


def ln_k_biph(t):
    """ln K of 2 BZ <=> BIPH + H2 (ideal gas; no mole change, so no pressure effect)."""
    dg = _g_ideal("BIPH", t) + _g_ideal("H2", t) - 2 * _g_ideal("BZ", t)
    return -dg / (R_GAS * t)


def react(n_in, xi2):
    xi1 = X * n_in["TOL"]
    out = dict(n_in)
    out["TOL"] -= xi1
    out["H2"] += -xi1 + xi2
    out["BZ"] += xi1 - 2 * xi2
    out["CH4"] += xi1
    out["BIPH"] += xi2
    return out, xi1, xi2


def t_adiabatic(n, h, p, lo=600.0, hi=1200.0):
    return brentq(lambda t: h_gas(n, t, p) - h, lo, hi)


def reactor(n_in, h_in, p):
    """HDA at X, then BIPH at equilibrium at the adiabatic outlet: (outlet, xi1, xi2, T)."""

    def gap(xi2):
        out, _, _ = react(n_in, xi2)
        t = t_adiabatic(out, h_in, p)
        q = out["BIPH"] * out["H2"] / out["BZ"] ** 2
        return math.log(q) - ln_k_biph(t)

    bz_max = (n_in["BZ"] + X * n_in["TOL"]) / 2
    xi2 = brentq(gap, -n_in["BIPH"] + 1e-12 if n_in["BIPH"] > 0 else 1e-12, bz_max * 0.5)
    out, xi1, xi2 = react(n_in, xi2)
    return out, xi1, xi2, t_adiabatic(out, h_in, p)


def loop(v):
    """One pass of the reactor loop for the fresh toluene of 100 kmol/h.

    v: recycle gas flows (5), toluene recycle flows (5), make-up H2, purge fraction, quench
    fraction of the separator liquid."""
    g = dict(zip(C, v[0:5]))
    trec = dict(zip(C, v[5:10]))
    fh2, beta, phi = v[10], v[11], v[12]
    ftol = {"H2": 0, "CH4": 0, "TOL": 100.0, "BIPH": 0,
            "BZ": 100.0 * MW["TOL"] / MW["BZ"] * W_BZ_FEED / (1 - W_BZ_FEED)}
    mu = scale(MAKEUP, fh2)
    rin = add(ftol, trec, mu, g)
    h_rin = h_gas(rin, T_RIN, P_RIN)
    rout, xi1, xi2, t_rout = reactor(rin, h_rin, P_ROUT)
    return dict(g=g, trec=trec, fh2=fh2, beta=beta, phi=phi, ftol=ftol, mu=mu, rin=rin, rout=rout,
                xi1=xi1, xi2=xi2, t_rout=t_rout, h_rout=h_rin)


def downstream(st, sep_liq_guess=None):
    """Quench, separator, purge, liquid split and columns for a loop state."""
    rout, beta, phi = st["rout"], st["beta"], st["phi"]
    # quench liquid is a fraction phi of the separator liquid: solve the separator with it
    ql = sep_liq_guess
    for _ in range(200):
        qin = add(rout, ql)
        res = flash(qin, T=T_SEP, P=P_SEP)
        vap = vec(res.gas.zs, tot(qin) * res.VF) if res.gas else scale(qin, 0)
        liq = {c: qin[c] - vap[c] for c in C}
        ql_new = scale(liq, phi)
        if max(abs(ql_new[c] - ql[c]) for c in C) < 1e-9:
            break
        ql = ql_new
    st.update(quench=ql, qmix=qin, sep_res=res, sep_vap=vap, sep_liq=liq)
    st["purge"] = scale(vap, beta)
    st["recycle"] = scale(vap, 1 - beta)
    st["liq_out"] = scale(liq, 1 - phi)
    return st


def stabiliser(feed):
    """C-201: all H2 and CH4 overhead with the aromatics in equilibrium with the reflux."""
    light = {c: feed[c] if c in ("H2", "CH4") else 0.0 for c in C}
    # bottoms aromatics guess -> reflux composition (aromatics normalised) -> K-values
    arom = {c: feed[c] if c in AROM else 0.0 for c in C}
    xr = zs(arom)
    vap = dict(light)
    for _ in range(50):
        trial = add(scale(arom, 1.0), light)
        res = flash(trial, T=T_C201_COND, P=P_C201)
        # K of the aromatics from the liquid-vapour split of the trial flash
        ks = {c: (res.gas.zs[i] / res.liquid0.zs[i]) for i, c in enumerate(C)}
        y_arom = {c: ks[c] * xr[C.index(c)] for c in AROM}
        y_light = 1 - sum(y_arom.values())
        v_tot = tot(light) / y_light
        new = dict(light)
        for c in AROM:
            new[c] = v_tot * y_arom[c]
        if max(abs(new[c] - vap[c]) for c in C) < 1e-10:
            break
        vap = new
        bot = {c: feed[c] - vap[c] for c in C}
        xr = zs({c: (bot[c] if c in AROM else 0.0) for c in C})
    bot = {c: feed[c] - vap[c] if c in AROM else 0.0 for c in C}
    return vap, bot


def psat(c, t):
    return props.VaporPressures[C.index(c)](t) / 1e3


def bubble(n, p):
    return flash(n, VF=0.0, P=p)


def dew(n, p):
    return flash(n, VF=1.0, P=p)


def underwood(feed, dist, lk, hk, t_mean):
    """Rmin of a saturated-liquid feed at constant relative volatility (to the heavy key)."""
    alpha = {c: psat(c, t_mean) / psat(hk, t_mean) for c in AROM if feed[c] > 0 or dist[c] > 0}
    z = {c: feed[c] / tot(feed) for c in alpha}
    theta = brentq(lambda th: sum(alpha[c] * z[c] / (alpha[c] - th) for c in alpha) - 0.0,
                   1.0 + 1e-6, alpha[lk] - 1e-6)
    xd = {c: dist[c] / tot(dist) for c in alpha}
    return sum(alpha[c] * xd[c] / (alpha[c] - theta) for c in alpha) - 1, alpha


def column(feed, dist, bot, p_top, p_bot, lk, hk, h_feed, t_dist_out=None):
    """Duties of a column with a total condenser (kW): reboiler from the energy balance.

    h_feed: enthalpy of the feed as it arrives (the upstream column's bottoms, let down
    isenthalpically); Underwood takes the feed as saturated liquid (q = 1, a simplification)."""
    resf = bubble(feed, p_bot)
    resd_l = bubble(dist, p_top)
    resd_v = dew(dist, p_top)
    resb = bubble(bot, p_bot)
    t_mean = 0.5 * (resd_l.T + resb.T)
    rmin, alpha = underwood(feed, dist, lk, hk, t_mean)
    r = max(R_FACTOR * rmin, R_FLOOR)
    v_top = scale(dist, r + 1)
    q_cond = h_fl(v_top, resd_v) - h_fl(v_top, resd_l)
    h_d = h_fl(dist, resd_l)
    if t_dist_out is not None:  # product subcooled in the condenser train
        resd_sub = flash(dist, T=t_dist_out, P=p_top)
        q_cond += h_d - h_fl(dist, resd_sub)
        h_d = h_fl(dist, resd_sub)
    q_reb = q_cond + h_d + h_fl(bot, resb) - h_feed
    return dict(rmin=rmin, r=r, alpha=alpha, q_cond=q_cond, q_reb=q_reb, t_top=resd_l.T,
                t_bot=resb.T, t_feed=resf.T)


def solve():
    # initial guess (per 100 kmol/h fresh toluene)
    v0 = [700.0, 900.0, 0.5, 2.0, 0.0] + [0.0, 0.0, 33.0, 0.2, 0.0] + [180.0, 0.15, 0.3]
    cache = {"ql": {c: 0.0 for c in C}}

    def full(v):
        st = downstream(loop(v), cache["ql"])
        cache["ql"] = st["quench"]
        # quench temperature of the effluent + quench liquid (adiabatic mix)
        res_q = flash(st["quench"], T=T_SEP, P=P_SEP) if tot(st["quench"]) > 0 else None
        h_q = h_fl(st["quench"], res_q) if res_q else 0.0
        st["t_quench"] = t_adiabatic(st["qmix"], st["h_rout"] + h_q, P_ROUT, 500, 1200)
        # liquid train
        vap201, bot201 = stabiliser(st["liq_out"])
        bz_d = REC_BZ * bot201["BZ"]
        d202 = {"H2": 0, "CH4": 0, "BZ": bz_d, "TOL": bz_d * (1 - X_D_BZ) / X_D_BZ, "BIPH": 0}
        b202 = {c: bot201[c] - d202[c] for c in C}
        biph = b202["BIPH"]
        tol_b = X_B_TOL_C203 / (1 - X_B_TOL_C203) * biph
        b203 = {"H2": 0, "CH4": 0, "BZ": 0, "TOL": tol_b, "BIPH": biph}
        d203 = {c: b202[c] - b203[c] for c in C}
        st.update(vap201=vap201, bot201=bot201, d202=d202, b202=b202, d203=d203, b203=b203)
        return st

    def resid(v):
        st = full(v)
        r = [st["recycle"][c] - v[i] for i, c in enumerate(C)]
        r += [st["d203"][c] - v[5 + i] for i, c in enumerate(C)]
        arom = sum(st["rin"][c] for c in AROM)
        r += [st["rin"]["H2"] / arom - RATIO,
              st["purge"]["H2"] / tot(st["purge"]) - Y_PURGE_H2,
              (st["t_quench"] - QUENCH_T) / 10]
        return r

    v = fsolve(resid, v0, xtol=1e-11, full_output=True)
    sol, info, ier, msg = v
    if ier != 1:
        raise SystemExit(f"loop did not converge: {msg}")
    st = full(sol)
    worst = max(abs(x) for x in resid(sol))
    return st, worst


def main():
    st, worst = solve()
    f = PRODUCT_KG_H / mass(st["d202"])  # scale to the product rate
    S_ = {}  # streams in kmol/h after scaling
    names = {
        "S1": ("Fresh toluene", "ftol", T_TOL_FEED, P_TOL_FEED),
        "S4": ("Make-up hydrogen", "mu", T_H2MU, P_H2MU),
        "S7": ("Reactor feed (= S5, S6)", "rin", T_RIN, P_RIN),
        "S8": ("Reactor effluent", "rout", st["t_rout"], P_ROUT),
        "S9": ("Quenched effluent (= S10, S11)", "qmix", QUENCH_T, P_ROUT),
        "S12": ("Separator gas", "sep_vap", T_SEP, P_SEP),
        "S13": ("Purge gas", "purge", T_SEP, P_SEP),
        "S14": ("Recycle gas", "recycle", T_SEP, P_SEP),
        "S16": ("Separator liquid", "sep_liq", T_SEP, P_SEP),
        "S17": ("Quench liquid", "quench", T_SEP, P_SEP),
        "S18": ("Liquid to stabiliser", "liq_out", T_SEP, P_SEP),
        "S19": ("Stabiliser off-gas", "vap201", T_C201_COND, P_C201),
        "S20": ("Stabiliser bottoms", "bot201", None, P_C201),
        "S21": ("Benzene product", "d202", T_PRODUCT, P_C202_TOP),
        "S22": ("Benzene column bottoms", "b202", None, P_C202_BOT),
        "S23": ("Toluene recycle", "d203", None, P_C203_TOP),
        "S24": ("Biphenyl", "b203", None, P_C203_BOT),
    }
    for sid, (title, key, t, p) in names.items():
        S_[sid] = scale(st[key], f)

    # ---- energy
    q = {}
    # recycle compressor K-101 (S14 -> S15)
    rec = S_["S14"]
    g1 = GAS.to(T=T_SEP, P=P_SEP * 1e3, zs=zs(rec))
    s1 = g1.S()
    t2s = brentq(lambda t: GAS.to(T=t, P=P_MIX * 1e3, zs=zs(rec)).S() - s1, T_SEP, 600)
    dh_s = GAS.to(T=t2s, P=P_MIX * 1e3, zs=zs(rec)).H() - g1.H()
    dh = dh_s / ETA_K
    t_k = brentq(lambda t: GAS.to(T=t, P=P_MIX * 1e3, zs=zs(rec)).H() - g1.H() - dh, T_SEP, 600)
    q["K101"] = tot(rec) / 3600 * dh
    # toluene pump P-101: fresh toluene + recycle (S2 -> S3)
    tolmix = add(S_["S1"], S_["S23"])
    res_d203 = bubble(S_["S23"], P_C203_TOP)
    h_mixin = h_fl(S_["S1"], flash(S_["S1"], T=T_TOL_FEED, P=P_TOL_FEED)) + h_fl(S_["S23"], res_d203)
    t_tolmix = brentq(lambda t: h_fl(tolmix, flash(tolmix, T=t, P=P_TOLDRUM)) - h_mixin, 250, 420)
    rho = flash(tolmix, T=t_tolmix, P=P_MIX).liquid0.rho_mass()
    q["P101"] = mass(tolmix) / 3600 / rho * (P_MIX - P_C203_TOP) / ETA_P  # kW (kPa * m3/s)
    t_pump = t_tolmix + 0.0  # temperature rise of the pump neglected (ASSUMED)
    # mixer M-101 (S3 + S4 + S15 -> S5), adiabatic
    h_tol = h_fl(tolmix, flash(tolmix, T=t_pump, P=P_MIX))
    h_mu = h_gas(S_["S4"], T_H2MU, P_H2MU)
    h_rec = tot(rec) / 3600 * (GAS.to(T=t_k, P=P_MIX * 1e3, zs=zs(rec)).H() + sum(HF[c] * rec[c] / tot(rec) for c in C))
    mixed = add(tolmix, S_["S4"], rec)
    h_mix = h_tol + h_mu + h_rec
    t_mix = brentq(lambda t: h_fl(mixed, flash(mixed, T=t, P=P_MIX)) - h_mix, 250, 600)
    vf_mix = flash(mixed, T=t_mix, P=P_MIX).VF
    # feed/effluent exchanger E-101: cold S5 -> S6 at T_FEHE_COLD_OUT
    h_cold_out = h_gas(mixed, T_FEHE_COLD_OUT, P_FEHE_COLD)
    q["E101"] = h_cold_out - h_mix
    qm = S_["S9"]
    h_hot_in = h_gas(qm, QUENCH_T, P_ROUT)
    h_hot_out = h_hot_in - q["E101"]
    t_hot_out = brentq(lambda t: h_fl(qm, flash(qm, T=t, P=P_FEHE_HOT)) - h_hot_out, 300, 900)
    # FEHE internal approach (20 points along the duty)
    dts = []
    for i in range(21):
        dq = q["E101"] * i / 20
        th = brentq(lambda t: h_fl(qm, flash(qm, T=t, P=P_FEHE_HOT)) - (h_hot_out + dq), 300, 900)
        tc = brentq(lambda t: h_fl(mixed, flash(mixed, T=t, P=P_FEHE_COLD)) - (h_mix + dq), 250, 900)
        dts.append(th - tc)
    # fired heater H-101: S6 -> S7
    q["H101"] = h_gas(mixed, T_RIN, P_RIN) - h_cold_out
    # trim cooler E-102: S10 -> S11 (separator)
    res_sep = flash(qm, T=T_SEP, P=P_SEP)
    q["E102"] = h_hot_out - h_fl(qm, res_sep)
    # columns
    c201_feed = S_["S18"]
    vap, bot = S_["S19"], S_["S20"]
    resf = flash(c201_feed, T=T_SEP, P=P_SEP)
    resb = bubble(bot, P_C201)
    resv = flash(vap, T=T_C201_COND, P=P_C201)
    reflux = {c: bot[c] / tot(bot) * R_C201 * tot(vap) for c in C}  # aromatic reflux, molar L/D
    q201_cond = h_fl(reflux, dew(reflux, P_C201)) - h_fl(reflux, flash(reflux, T=T_C201_COND, P=P_C201))
    q201_reb = q201_cond + h_fl(vap, resv) + h_fl(bot, resb) - h_fl(c201_feed, resf)
    q["C201_cond"], q["C201_reb"] = q201_cond, q201_reb
    c202 = column(S_["S20"], S_["S21"], S_["S22"], P_C202_TOP, P_C202_BOT, "BZ", "TOL",
                  h_fl(bot, resb), T_PRODUCT)
    h_s22 = h_fl(S_["S22"], bubble(S_["S22"], P_C202_BOT))
    c203 = column(S_["S22"], S_["S23"], S_["S24"], P_C203_TOP, P_C203_BOT, "TOL", "BIPH", h_s22)
    q["C202_cond"], q["C202_reb"] = c202["q_cond"], c202["q_reb"]
    q["C203_cond"], q["C203_reb"] = c203["q_cond"], c203["q_reb"]

    temps = {"S8": st["t_rout"], "S20": resb.T, "S22": c202["t_bot"], "S23": c203["t_top"],
             "S24": c203["t_bot"]}
    out = {"streams": {}, "duties_kW": q, "checks": {}}
    for sid, (title, key, t, p) in names.items():
        n = S_[sid]
        out["streams"][sid] = {"title": title, "T_K": round(temps.get(sid, t), 2), "P_kPa": p,
                               "kmol_h": round(tot(n), 4), "kg_h": round(mass(n), 2),
                               "y": {c: round(n[c] / tot(n), 9) for c in C if n[c] > 1e-12}}
    out["streams"]["S2"] = {"title": "Toluene to pump (= S3 at P_MIX)", "T_K": round(t_tolmix, 2),
                            "P_kPa": P_TOLDRUM, "kg_h": round(mass(tolmix), 2),
                            "y": {c: round(tolmix[c] / tot(tolmix), 9) for c in C if tolmix[c] > 1e-12}}
    out["streams"]["S5"] = {"title": "Combined feed", "T_K": round(t_mix, 2), "VF": round(vf_mix, 4),
                            "kg_h": round(mass(mixed), 2)}
    out["streams"]["S6"] = {"title": "Preheated feed", "T_K": T_FEHE_COLD_OUT, "P_kPa": P_FEHE_COLD}
    out["streams"]["S10"] = {"title": "Effluent after FEHE", "T_K": round(t_hot_out, 2),
                             "P_kPa": P_FEHE_HOT}
    out["streams"]["S15"] = {"title": "Compressed recycle gas", "T_K": round(t_k, 2), "P_kPa": P_MIX}
    xi1, xi2 = st["xi1"] * f, st["xi2"] * f
    arom_in = sum(S_["S7"][c] for c in AROM)
    out["checks"] = {
        "loop_residual_max": worst,
        "selectivity_S": 1 - 2 * st["xi2"] / st["xi1"],
        "ln_Q_over_K_BIPH": math.log(st["rout"]["BIPH"] * st["rout"]["H2"] / st["rout"]["BZ"] ** 2)
        - ln_k_biph(st["t_rout"]),
        "extent_HDA_kmol_h": xi1, "extent_BIPH_kmol_h": xi2,
        "fresh_toluene_kg_h": mass(S_["S1"]), "makeup_H2_kg_h": mass(S_["S4"]),
        "purge_fraction": st["beta"], "quench_fraction": st["phi"],
        "H2_to_aromatics": S_["S7"]["H2"] / arom_in,
        "reactor_outlet_T_K": st["t_rout"],
        "FEHE_min_approach_K": min(dts), "FEHE_approach_profile_K": [round(d, 1) for d in dts],
        "C202": {k: v for k, v in c202.items() if k != "alpha"},
        "C203": {k: v for k, v in c203.items() if k != "alpha"},
        "C201_bottoms_T_K": resb.T,
        "benzene_yield_mol_per_mol_fresh_toluene": S_["S21"]["BZ"] / S_["S1"]["TOL"],
        "benzene_product_wt_purity": S_["S21"]["BZ"] * MW["BZ"] / mass(S_["S21"]),
        "recycle_gas_kmol_h": tot(S_["S14"]),
        "aromatics_lost_to_fuel_gas_kg_h": sum((S_["S13"][c] + S_["S19"][c]) * MW[c] for c in AROM),
    }
    # first-pass line sizes (D-012): velocity by phase on the PR bulk density
    tp = {sid: (temps.get(sid, t), p) for sid, (title, key, t, p) in names.items()}
    tp.update({"S2": (t_tolmix, P_TOLDRUM), "S3": (t_pump, P_MIX), "S5": (t_mix, P_MIX),
               "S6": (T_FEHE_COLD_OUT, P_FEHE_COLD), "S10": (t_hot_out, P_FEHE_HOT),
               "S11": (T_SEP, P_SEP), "S15": (t_k, P_MIX)})
    comp = dict(S_)
    comp.update({"S2": tolmix, "S3": tolmix, "S5": mixed, "S6": mixed, "S10": qm, "S11": qm,
                 "S15": rec})
    sizes = {}
    dns = [15, 20, 25, 40, 50, 65, 80, 100, 125, 150, 200, 250, 300, 350, 400, 450, 500, 600, 700, 800]
    for sid in sorted(tp, key=lambda s: int(s[1:])):
        t, p = tp[sid]
        n = comp[sid]
        res = flash(n, T=t, P=p)
        vf = res.VF
        rho = res.rho_mass()
        u = 1.5 if vf < 1e-6 else (10.0 if vf < 1 - 1e-6 else (15.0 if p > 1000 else 20.0))
        d_mm = 1000 * math.sqrt(4 * mass(n) / 3600 / rho / u / math.pi)
        sizes[sid] = {"VF": round(vf, 3), "rho": round(rho, 2), "u": u, "d_mm": round(d_mm, 1),
                      "DN": next(d for d in dns if d >= d_mm)}
    out["line_sizes"] = sizes
    mass_in = mass(S_["S1"]) + mass(S_["S4"])
    mass_out = mass(S_["S13"]) + mass(S_["S19"]) + mass(S_["S21"]) + mass(S_["S24"])
    out["checks"]["mass_in_kg_h"], out["checks"]["mass_out_kg_h"] = mass_in, mass_out
    # overall energy closure (kW, formation enthalpies included): feeds + heat and work in =
    # products + heat to cooling water; the pump's temperature rise is neglected (D-010)
    h_in = (h_fl(S_["S1"], flash(S_["S1"], T=T_TOL_FEED, P=P_TOL_FEED)) + h_mu
            + q["K101"] + q["P101"] + q["H101"] + q["C201_reb"] + q["C202_reb"] + q["C203_reb"])
    h_out = (h_gas(S_["S13"], T_SEP, P_SEP) + h_fl(vap, resv)
             + h_fl(S_["S21"], flash(S_["S21"], T=T_PRODUCT, P=P_C202_TOP))
             + h_fl(S_["S24"], bubble(S_["S24"], P_C203_BOT))
             + q["E102"] + q["C201_cond"] + q["C202_cond"] + q["C203_cond"])
    out["checks"]["energy_in_kW"], out["checks"]["energy_out_kW"] = h_in, h_out
    print(json.dumps(out, indent=1, default=float))
    (ROOT / "build").mkdir(exist_ok=True)
    (ROOT / "build/hda_balance.json").write_text(json.dumps(out, indent=1, default=float))

    # the values process/flowsheet.yaml cites from this script (balance-output contract)
    fs = {}
    for sid, (title, key, t, p) in names.items():
        n = S_[sid]
        fs[sid] = {"flow": mass(n), "temperature": temps.get(sid, t), "pressure": p,
                   "composition": {c: n[c] / tot(n) for c in C if n[c] > 1e-12}}
    fs["S2"] = {"temperature": t_tolmix}
    fs["S3"] = {"temperature": t_pump}
    fs["S5"] = {"temperature": t_mix}
    fs["S6"] = {"flow": mass(mixed), "composition": {c: mixed[c] / tot(mixed) for c in C}}
    fs["S10"] = {"flow": mass(qm), "temperature": t_hot_out,
                 "composition": {c: qm[c] / tot(qm) for c in C}}
    fs["S15"] = {"temperature": t_k}
    duties = {"Q1": "P101", "Q2": "K101", "Q3": "H101", "Q4": "E102", "Q5": "C201_reb",
              "Q6": "C201_cond", "Q7": "C202_reb", "Q8": "C202_cond", "Q9": "C203_reb",
              "Q10": "C203_cond"}
    fs.update({sid: {"duty": q[k]} for sid, k in duties.items()})
    write_balance_output({"design": fs})


def write_balance_output(cases):
    """With BALANCE_OUTPUT set, write the values the flowsheet cites from this script as JSON.

    The process library's balance-output contract (docs/adr/0027 of the library): case ->
    stream id -> quantity, in the flowsheet's units and basis. The library's
    scripts/check_balance_scripts.py re-runs this script and compares them with
    process/flowsheet.yaml.
    """
    import os

    target = os.environ.get("BALANCE_OUTPUT")
    if target:
        doc = {"contract": "balance-output/1", "script": f"scripts/{Path(__file__).name}",
               "cases": cases}
        Path(target).write_text(json.dumps(doc, indent=1, default=float), encoding="utf-8")


if __name__ == "__main__":
    main()
