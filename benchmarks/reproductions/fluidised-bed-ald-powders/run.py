# /// script
# requires-python = ">=3.12,<3.14"
# dependencies = [
#     "numpy==2.3.4",
#     "scipy==1.16.3",
#     "matplotlib==3.10.7",
#     "pyyaml==6.0.3",
# ]
# ///
"""Fluidised-bed ALD on powders: reproduction and hypothetical design extension (#336).

Re-implements, from the published equations, the reactor model of Grillo, Kreutzer and van
Ommen (CEJ 268 (2015) 384; open version: Grillo 2018 TU Delft thesis, chapter 7) for the TMA
half-reaction on P-25 TiO2 agglomerates, compares it with the reported results frozen in
source.yaml under tolerances.yaml, and then scales the batch up at fixed target coverage.

    uv run benchmarks/reproductions/fluidised-bed-ald-powders/run.py

Inputs: inputs.yaml (every value labelled). No third-party data are downloaded: all reference
numbers are restated in source.yaml (digitise.py documents how the digitised ones were read).
Writes results/ deterministically. Exits non-zero only if the script itself fails; the
reproduction verdict is recorded in results/comparison.json.
"""

from __future__ import annotations

import json
import math
import platform
import sys
from pathlib import Path

import matplotlib
import numpy as np
import scipy
import yaml
from scipy.integrate import solve_ivp
from scipy.sparse import lil_matrix

matplotlib.use("svg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib import patches  # noqa: E402

HERE = Path(__file__).resolve().parent
OUT = HERE / "results"
plt.rcParams.update({
    "svg.hashsalt": "cheme-336",
    "svg.fonttype": "none",
    "font.size": 9,
    "axes.spines.top": False,
    "axes.spines.right": False,
})
SVG_META = {"Date": None, "Creator": "cheme reproductions #336 run.py"}

INP = yaml.safe_load((HERE / "inputs.yaml").read_text())
SRC = yaml.safe_load((HERE / "source.yaml").read_text())
TOL = yaml.safe_load((HERE / "tolerances.yaml").read_text())


def v(section: str, key: str):
    return INP[section][key]["value"]


R = v("constants", "R")
NA = v("constants", "N_A")
G = v("constants", "g")
T = v("base_case", "T")
P_ATM, P_MBAR = v("base_case", "P")
M_TMA = v("precursor", "M_TMA")  # g/mol
D_ATM = v("precursor", "D_TMA_N2")  # m2/s at 1.013 bar, 500 K
S_BET = v("base_case", "S_BET") * 1e3  # m2/kg
RHO_B = v("base_case", "rho_b")
UMF = v("base_case", "u_mf")
U0 = v("base_case", "u0")
EPS_MF = v("base_case", "eps_mf")
DT0 = v("base_case", "d_t")
H0 = v("base_case", "H0_over_dt") * DT0
H_EXP = v("base_case", "H_over_H0")
H_BASE = H_EXP * H0
DB = v("base_case", "d_b")
MASS0 = v("base_case", "batch_mass") / 1e3  # kg
N_MAX = v("site_capacity", "n_max_Al") * 1e18 / NA  # mol/m2
AG = INP["agglomerate_structure"]
D_AG = AG["d3"]["value"]
R_C = D_AG / 2
R_SA = AG["d2"]["value"] / 2
EPS_AG = AG["eps_ag"]["value"]
EPS_C = AG["eps_c"]["value"]
EPS_SA = AG["eps_sa"]["value"]
LAM_C = AG["lambda_c"]["value"]
LAM_SA = AG["lambda_sa"]["value"]
TAU_RXN = SRC["reported_results"]["time_scales_table_7_4"]["tau_rxn"]


def sig(x: float, n: int = 6) -> float:
    """Round to n significant figures (keeps comparison.json stable across platforms)."""
    if x == 0 or not math.isfinite(x):
        return float(x)
    return float(f"{x:.{n}g}")


# ----------------------------------------------------------------------------------------
# Correlations of Table 7.1 and diffusivities of Eqs. 7.12-7.15
# ----------------------------------------------------------------------------------------
def D_mol(P: float) -> float:
    return D_ATM * P_ATM / P


def D_knudsen(lam: float) -> float:
    return 48.5 * lam * math.sqrt(T / M_TMA)


def hydro(u0: float, umf: float, db: float, D: float, eps_mf: float = EPS_MF) -> dict:
    ub = u0 - umf + 0.711 * math.sqrt(G * db)
    delta = (u0 - umf) / (ub - umf)
    kbe = 6.0 / db * (umf / 3.0 + math.sqrt(4.0 * D * eps_mf * ub / (math.pi * db)))
    return {"u_b": ub, "delta": delta, "K_be": kbe}


def h_star(u0: float, umf: float, db: float, D: float, eta: float) -> float:
    h = hydro(u0, umf, db, D)
    return h["u_b"] / h["K_be"] * math.log(h["u_b"] * h["delta"] / (u0 * (1.0 - eta)))


def eta_qss(u0: float, umf: float, db: float, D: float, H: float) -> float:
    h = hydro(u0, umf, db, D)
    return 1.0 - h["u_b"] * h["delta"] / u0 * math.exp(-H * h["K_be"] / h["u_b"])


def wilke_lee_D(P: float) -> float:
    """Cross-check of D_TMA-N2 (Wilke-Lee; not used by the model)."""
    sig_a, sig_b = INP["precursor"]["sigma_TMA"]["value"] * 1e10, 3.798  # angstrom
    eps_a, eps_b = 1.15 * 398.0, 71.4  # K
    m_ab = 2.0 / (1.0 / M_TMA + 1.0 / 28.014)
    s_ab = 0.5 * (sig_a + sig_b)
    ts = T / math.sqrt(eps_a * eps_b)
    omega = (1.06036 / ts**0.15610 + 0.19300 / math.exp(0.47635 * ts)
             + 1.03587 / math.exp(1.52996 * ts) + 1.76474 / math.exp(3.89411 * ts))
    d_cm2 = (3.03 - 0.98 / math.sqrt(m_ab)) * 1e-3 * T**1.5 / (P / 1e5 * math.sqrt(m_ab) * s_ab**2 * omega)
    return d_cm2 * 1e-4


# ----------------------------------------------------------------------------------------
# Analytical reproduction targets (G1-G4)
# ----------------------------------------------------------------------------------------
def time_scales(P: float) -> dict:
    D = D_mol(P)
    h = hydro(U0, UMF, DB, D)
    kga = 2.0 * D / D_AG
    if P > 1e4:  # 1.013 bar: complex level Fickian, simple level transition
        Dc = EPS_C**2 * D
        Dsa = EPS_SA**2 / (1.0 / D + 1.0 / D_knudsen(LAM_SA))
        thiele = R_C * math.sqrt((1.0 / TAU_RXN["1.013_bar"]) / Dc)
    else:  # 1 mbar: complex level transition, simple level Knudsen
        Dc = EPS_C**2 / (1.0 / D + 1.0 / D_knudsen(LAM_C))
        Dsa = EPS_SA**2 * D_knudsen(LAM_SA)
        thiele = R_SA * math.sqrt((1.0 / TAU_RXN["1_mbar"]) / Dsa)
    return {
        "tau_em": H_BASE * (1 - h["delta"]) * EPS_MF / UMF,
        "tau_em_as_printed_eq_7_19": H_BASE * (1 - h["delta"]) / UMF,
        "tau_b": H_BASE / h["u_b"],
        "tau_int": 1.0 / h["K_be"],
        "tau_ga": R_C / kga,
        "tau_c": R_C**2 / Dc,
        "tau_sa": R_SA**2 / Dsa,
        "thiele_star": thiele,
        "D_m2_s": D, "D_c": Dc, "D_sa": Dsa, "K_ga": kga, **h,
    }


def tau_sat_min(P_tma: float, H0_: float = H0, u0: float = U0) -> float:
    c_in = P_tma / (R * T)
    return RHO_B * S_BET * N_MAX * H0_ / (u0 * c_in)


# ----------------------------------------------------------------------------------------
# Dynamic model (Tables 7.1 and 7.2 at 1.013 bar) with lumped site kinetics (inputs.yaml)
# ----------------------------------------------------------------------------------------
def dynamic(mass: float, H0_: float, dt: float, db: float, P_tma: float, u0: float = U0,
            nz: int = 400, nr: int = 40, t_end: float | None = None, t_profile: float | None = None):
    D = D_mol(P_ATM)
    h = hydro(u0, UMF, db, D)
    ub, delta, kbe = h["u_b"], h["delta"], h["K_be"]
    H = H_EXP * H0_
    area = math.pi / 4 * dt**2
    c_in = P_tma / (R * T)
    kga = 2.0 * D / D_AG
    Dc = EPS_C**2 * D
    nu = v("dynamic_model", "nu_max")
    sites = mass * S_BET * N_MAX  # mol
    v_ag = area * H * (1 - delta) * (1 - EPS_MF)  # m3 agglomerate
    q = sites / v_ag  # mol sites / m3 agglomerate
    dz = H / nz
    dr = R_C / nr
    k = np.arange(nr)
    vol = ((k + 1) ** 3 - k**3) * dr**3 / 3.0  # shell volumes / (4 pi)
    face = ((k + 1) * dr) ** 2  # outer face areas / (4 pi)
    a_em = 6 * (1 - EPS_MF) / (EPS_MF * D_AG)  # agglomerate surface per emulsion gas volume
    ib, iem = slice(0, nz), nz
    ic, ith, icum = slice(nz + 1, nz + 1 + nr), slice(nz + 1 + nr, nz + 1 + 2 * nr), nz + 1 + 2 * nr
    n = icum + 1

    def surface(cem, clast):
        cs = (2 * Dc / dr * clast + kga * cem) / (2 * Dc / dr + kga)
        return cs, kga * (cem - cs)  # inward flux per external area (scaled by C_in)

    def rhs(t, y):
        cb, cem, c, th = y[ib], y[iem], y[ic], y[ith]
        dy = np.empty(n)
        cbn = np.concatenate(([1.0], cb))
        dy[ib] = -ub * (cbn[1:] - cbn[:-1]) / dz - kbe * (cb - cem)
        integral = dz * float(np.sum(cb - cem))  # cell sum, consistent with the bubble-cell losses
        cs, nin = surface(cem, c[-1])
        dy[iem] = (UMF / (H * EPS_MF) * (1 - cem) + kbe * delta / (H * EPS_MF * (1 - delta)) * integral
                   - a_em * nin)
        flux = np.zeros(nr + 1)  # flux into cell from outside face, per 4 pi
        flux[1:nr] = face[:-1] * Dc * (c[1:] - c[:-1]) / dr
        flux[nr] = face[-1] * nin
        rate = nu * (1 - th) * c
        dy[ic] = ((flux[1:] - flux[:-1]) / vol - rate) / EPS_AG
        dy[ith] = rate * c_in / q
        dy[icum] = (UMF * (1 - delta) * cem + ub * delta * cb[-1]) / u0
        return dy

    S = lil_matrix((n, n), dtype=np.int8)
    for j in range(nz):
        S[j, j] = 1
        S[j, iem] = 1
        if j:
            S[j, j - 1] = 1
    S[iem, :nz] = 1
    S[iem, iem] = 1
    S[iem, nz + nr] = 1
    for kk in range(nr):
        r_, t_ = nz + 1 + kk, nz + 1 + nr + kk
        for o in (-1, 0, 1):
            if 0 <= kk + o < nr:
                S[r_, nz + 1 + kk + o] = 1
        S[r_, t_] = 1
        S[t_, r_] = 1
        S[t_, t_] = 1
    S[nz + nr, iem] = 1
    S[icum, iem] = 1
    S[icum, nz - 1] = 1

    def mean_theta(y):
        return float(vol @ y[ith] / vol.sum())

    target = v("extension", "target_coverage")
    ev = lambda t, y: mean_theta(y) - target  # noqa: E731
    ev.terminal = False
    ev.direction = 1
    tmin = sites / (u0 * area * c_in)
    t_end = t_end or 1.35 * tmin
    t_eval = np.linspace(0, t_end, 1351)
    if t_profile is not None:
        t_eval = np.unique(np.concatenate((t_eval, [t_profile])))
    y0 = np.zeros(n)
    sol = solve_ivp(rhs, (0, t_end), y0, method="BDF", t_eval=t_eval, jac_sparsity=S.tocsr(),
                    rtol=1e-6, atol=1e-10, events=ev, dense_output=False)
    if not sol.success:
        raise RuntimeError(sol.message)
    Y = sol.y
    c_out = (UMF * (1 - delta) * Y[iem] + ub * delta * Y[nz - 1]) / u0
    th_mean = (vol @ Y[ith]) / vol.sum()
    th_centre = Y[nz + 1 + nr]
    t99 = float(sol.t_events[0][0]) if len(sol.t_events[0]) else float("nan")
    # mass balance at t_end (per bed cross-section, in units of C_in * m)
    fed = u0 * sol.t[-1]
    out = u0 * Y[icum, -1]
    hold = (delta * dz * float(np.sum(Y[ib, -1])) + H * (1 - delta) * EPS_MF * Y[iem, -1]
            + H * (1 - delta) * (1 - EPS_MF) * EPS_AG * float(vol @ Y[ic, -1] / vol.sum()))
    filled = sites * th_mean[-1] / (area * c_in)
    mb = (fed - out - hold - filled) / fed
    res = {
        "geometry": {"mass_kg": mass, "H0_m": H0_, "d_t_m": dt, "H_m": H, "area_m2": area, "d_b_m": db},
        "hydro": {"u0": u0, **h, "H_Kbe_over_ub": H * kbe / ub},
        "C_in_mol_m3": c_in, "sites_mol": sites, "q_mol_m3_agglomerate": q,
        "tau_sat_min_s": tmin, "t99_s": t99,
        "eta_qss": eta_qss(u0, UMF, db, D, H),
        "mass_balance_rel": mb,
        "t": sol.t, "c_out": c_out, "theta_mean": th_mean, "theta_centre": th_centre,
        "cem": Y[iem], "nfev": int(sol.nfev),
    }
    if t99 == t99:
        cum_out_99 = float(np.interp(t99, sol.t, Y[icum]))
        res["at_t99"] = {
            "c_out": float(np.interp(t99, sol.t, c_out)),
            "theta_centre": float(np.interp(t99, sol.t, th_centre)),
            "utilisation_over_pulse": 1.0 - cum_out_99 / t99,
            "TMA_fed_mol": u0 * area * c_in * t99,
            "TMA_lost_mol": u0 * area * c_in * cum_out_99,
        }
    if t_profile is not None:
        ip = int(np.argmin(abs(sol.t - t_profile)))
        zn = np.linspace(0, H, nz + 1) / H
        res["profile"] = {"t": float(sol.t[ip]), "z_over_H": zn, "cb": np.concatenate(([1.0], Y[ib, ip])),
                          "cem": float(Y[iem, ip]), "eta_dyn": float(1 - c_out[ip])}
    return res


# ----------------------------------------------------------------------------------------
# Extension geometry
# ----------------------------------------------------------------------------------------
def darton_db(h: float, u0: float = U0) -> float:
    a0 = v("extension", "A0")
    return 0.54 * (u0 - UMF) ** 0.4 * (h + 4 * math.sqrt(a0)) ** 0.8 * G**-0.2


def scaled_geometry(mass: float, strategy: str) -> dict:
    vol0 = mass / RHO_B
    if strategy == "A":
        h0 = H0
        dt = math.sqrt(4 * vol0 / (math.pi * h0))
    else:
        dt = (4 * vol0 / math.pi) ** (1 / 3)
        h0 = dt
    H = H_EXP * h0
    db = darton_db(H / 2)
    tdh = 1000 * U0**2 / G
    return {"mass_kg": mass, "strategy": strategy, "H0_m": h0, "d_t_m": dt, "H_m": H,
            "H0_over_dt": h0 / dt, "d_b_darton_m": db, "TDH_m": tdh,
            "plenum_m": v("extension", "plenum"), "filter_m": v("extension", "filter_section"),
            "vessel_height_m": v("extension", "plenum") + H + tdh + v("extension", "filter_section")}


# ----------------------------------------------------------------------------------------
# Figures (our own code)
# ----------------------------------------------------------------------------------------
def save(fig, name):
    fig.savefig(OUT / name, format="svg", metadata=SVG_META, bbox_inches="tight")
    plt.close(fig)


COL = ["#2b6cb0", "#2f855a", "#b7791f", "#c53030"]


def fig_hstar(ours_a, ours_b, ref):
    fig, axs = plt.subplots(1, 2, figsize=(8.0, 3.4))
    dbs = np.linspace(0.05, 4.5, 90)
    umfs = INP["fig_7_4_conditions"]["u_mf_values"]["value"]
    ra = ref["panel_a_1.013_bar"]
    keys = ["umf_0.01_cms", "umf_0.1_cms", "umf_2.5_cms", "umf_5_cms"]
    for c, umf, key in zip(COL, umfs, keys):
        hs = [100 * h_star(1.5 * umf, umf, d / 100, D_mol(P_ATM), 0.9999) for d in dbs]
        axs[0].plot(dbs, hs, color=c, lw=1.5, label=f"ours, u_mf = {umf * 100:g} cm/s")
        axs[0].plot(ref["d_b_cm"], ra[key], "o", mfc="none", color=c, ms=5)
    axs[0].plot([], [], "o", mfc="none", color="0.3", label="source Fig. 7.4a (digitised)")
    axs[0].set(xlabel="average bubble diameter d_b [cm]", ylabel="required bed height H* [cm]",
               title="1.013 bar, eta* = 0.9999, u0 = 1.5 u_mf", xlim=(0, 4.6), ylim=(0, 260))
    axs[0].legend(frameon=False, fontsize=7)
    for c, umf in zip(COL, umfs):
        hs = [100 * h_star(1.5 * umf, umf, d / 100, D_mol(P_MBAR), 0.9999) for d in dbs]
        axs[1].plot(dbs, hs, color=c, lw=1.2)
    rb = ref["panel_b_1_mbar"]
    axs[1].fill_between(ref["d_b_cm"], rb["min"], rb["max"], color="0.6", alpha=0.6, lw=0)
    axs[1].plot(ref["d_b_cm"], [(a + b) / 2 for a, b in zip(rb["min"], rb["max"])], "s", mfc="none",
                color="0.2", ms=5, label="source Fig. 7.4b (digitised envelope)")
    axs[1].plot([], [], color="0.4", label="ours, u_mf = 0.01 to 5 cm/s")
    axs[1].set(xlabel="average bubble diameter d_b [cm]", ylabel="H* [cm]", title="1 mbar",
               xlim=(0, 4.6), ylim=(0, 8))
    axs[1].legend(frameon=False, fontsize=7)
    fig.suptitle("Bed height for 99.99 % TMA utilisation (Eq. 7.52), ours vs source", fontsize=10)
    save(fig, "fig1-required-bed-height.svg")


def fig_profile(base, ref):
    fig, ax = plt.subplots(figsize=(4.6, 3.3))
    p = base["profile"]
    ax.plot(p["z_over_H"], p["cb"], color=COL[0], lw=1.5, label=f"ours, dynamic model, t = {p['t']:.1f} s")
    zz = np.linspace(0, 1, 101)
    h = base["hydro"]
    ax.plot(zz, np.exp(-h["H_Kbe_over_ub"] * zz), color="0.5", lw=1, ls="--",
            label="ours, quasi-steady exp(-K_be z/u_b)")
    ax.plot(ref["z_over_H"], ref["t_19.9_s"], "o", mfc="none", color=COL[3], label="source Fig. 7.3, t = 19.9 s (digitised)")
    ax.set(xlabel="z/H [-]", ylabel="C_TMA,bubble / C_TMA,in [-]", ylim=(0, 1.02), xlim=(0, 1))
    ax.legend(frameon=False, fontsize=7)
    ax.set_title("Bubble-phase TMA profile, 22 g P-25, 1.013 bar, d_b = 1 cm", fontsize=9)
    save(fig, "fig2-bubble-profile.svg")


def fig_pulse(runs):
    fig, axs = plt.subplots(1, 2, figsize=(8.4, 3.6), sharey=False)
    styles = {"base": ("lab, 22 g", COL[0], 3.2, "-"), "A": ("1 kg, strategy A", COL[1], 1.2, "-"),
              "B": ("1 kg, strategy B", COL[3], 1.5, "-")}
    for key, r in runs.items():
        lab, c, lw, ls = styles[key]
        axs[0].plot(r["t"], np.maximum(r["c_out"], 1e-6), color=c, lw=lw, ls=ls, alpha=0.9, label=lab)
        axs[1].plot(r["t"], r["theta_mean"], color=c, lw=lw, alpha=0.9, label=f"{lab}, volume mean")
        axs[1].plot(r["t"], r["theta_centre"], color=c, lw=1, ls=":", label=f"{lab}, agglomerate centre")
        for ax in axs:
            ax.axvline(r["t99_s"], color=c, lw=0.8, ls="--")
    axs[0].set(xlabel="time from start of TMA pulse [s]", ylabel="outlet TMA C_out / C_in [-]",
               title="Outlet precursor (log scale)", yscale="log", ylim=(1e-5, 2))
    axs[1].set(xlabel="time from start of TMA pulse [s]", ylabel="site coverage theta [-]",
               title="Coverage", ylim=(-0.02, 1.02))
    axs[0].legend(frameon=False, fontsize=7, loc="upper left")
    axs[1].legend(frameon=False, fontsize=6.5, loc="upper left")
    fig.text(0.5, -0.04, "Dashed vertical lines: pulse end at 99 % volume-mean coverage. Lab and strategy A "
             "nearly coincide (same H0).", ha="center", fontsize=7.5)
    fig.suptitle("TMA pulse, P_TMA,in = 40 mbar, 1.013 bar, 500 K (our dynamic model; HYPOTHETICAL for 1 kg)", fontsize=9)
    save(fig, "fig3-pulse-breakthrough-coverage.svg")


def fig_sweep(sweep):
    fig, axs = plt.subplots(1, 2, figsize=(8.0, 3.2))
    for s, c in (("A", COL[1]), ("B", COL[3])):
        m = [x["mass_kg"] for x in sweep[s]]
        axs[0].plot(m, [x["pulse_estimate_s"] for x in sweep[s]], "o-", color=c, label=f"strategy {s}")
        axs[1].plot(m, [max(1 - x["eta_qss"], 1e-12) for x in sweep[s]], "o-", color=c, label=f"strategy {s}")
    axs[0].set(xscale="log", xlabel="batch mass [kg]", ylabel="TMA pulse to 99 % coverage [s]",
               title="Pulse time (tau_sat_min x 0.99 / eta)")
    axs[1].set(xscale="log", yscale="log", xlabel="batch mass [kg]", ylabel="precursor slip 1 - eta [-]",
               title="Quasi-steady precursor slip (Eq. 7.51)", ylim=(1e-6, 1e-3))
    for ax in axs:
        ax.legend(frameon=False, fontsize=7)
    fig.suptitle("A: H0 = 6 cm, d_t widened; B: H0/d_t = 1.  d_b from Darton (HYPOTHETICAL)", fontsize=9)
    save(fig, "fig4-batch-sweep.svg")


def section_view(geoms: list[dict], name: str):
    """Dimensioned section of the scaled vessels, drawn to one scale (mm)."""
    fig, ax = plt.subplots(figsize=(8.4, 7.2))
    x0 = 0.0
    gap = 0.55
    for g in geoms:
        dt, H0_, H = g["d_t_m"], g["H0_m"], g["H_m"]
        pl, tdh, fl = g["plenum_m"], g["TDH_m"], g["filter_m"]
        wall = 0.008
        tot = pl + H + tdh + fl
        # walls
        for xw in (x0 - wall, x0 + dt):
            ax.add_patch(patches.Rectangle((xw, 0), wall, tot, color="0.25", lw=0))
        ax.add_patch(patches.Rectangle((x0 - wall, tot), dt + 2 * wall, wall, color="0.25", lw=0))
        ax.add_patch(patches.Rectangle((x0 - wall, -wall), dt + 2 * wall, wall, color="0.25", lw=0))
        # distributor
        ax.add_patch(patches.Rectangle((x0, pl - 0.006), dt, 0.006, facecolor="white", edgecolor="0.2",
                                       hatch="////", lw=0.6))
        # expanded bed and settled level
        ax.add_patch(patches.Rectangle((x0, pl), dt, H, facecolor="#e2c79a", edgecolor="none", alpha=0.8))
        rng = np.random.default_rng(336)
        nb = int(30 * dt * H / 0.02) + 3
        bx, by = x0 + rng.uniform(0.1, 0.9, nb) * dt, pl + rng.uniform(0.08, 0.92, nb) * H
        bd = g["d_b_darton_m"]
        for xb, yb in zip(bx, by):
            ax.add_patch(patches.Ellipse((xb, yb), bd, 0.8 * bd, facecolor="white", edgecolor="0.5", lw=0.3))
        ax.plot([x0, x0 + dt], [pl + H0_] * 2, color="0.1", lw=0.8, ls="--")
        # filter candles
        nc = max(2, int(dt / 0.08))
        for i in range(nc):
            cx = x0 + (i + 0.5) * dt / nc
            ax.add_patch(patches.Rectangle((cx - 0.012, tot - fl + 0.01), 0.024, fl - 0.02,
                                           facecolor="#cbd5e0", edgecolor="0.3", lw=0.5))
        ax.plot([x0, x0 + dt], [tot - fl] * 2, color="0.4", lw=0.6, ls=":")
        # nozzles
        ax.annotate("", xy=(x0 + dt / 2, 0.0), xytext=(x0 + dt / 2, -0.12),
                    arrowprops=dict(arrowstyle="-|>", color="#2b6cb0", lw=1.2))
        ax.text(x0 + dt / 2, -0.15, "N2 + TMA (or H2O)\npulsed feed", ha="center", va="top", fontsize=7, color="#2b6cb0")
        ax.annotate("", xy=(x0 + dt / 2, tot + 0.13), xytext=(x0 + dt / 2, tot + wall),
                    arrowprops=dict(arrowstyle="-|>", color="0.3", lw=1.2))
        ax.text(x0 + dt / 2 + 0.02, tot + 0.08, "off-gas to\nscrubber", fontsize=7, va="center")

        def dim_v(x, y1, y2, label, side=1):
            ax.annotate("", xy=(x, y1), xytext=(x, y2), arrowprops=dict(arrowstyle="<|-|>", lw=0.7, color="0.1",
                                                                        shrinkA=0, shrinkB=0))
            ax.text(x + 0.012 * side, (y1 + y2) / 2, label, rotation=90, va="center",
                    ha="left" if side > 0 else "right", fontsize=7)

        xr = x0 + dt + wall + 0.04
        if H0_ < 0.12:  # short bed: arrow inside the bed, label above it
            dim_v(x0 + 0.03, pl, pl + H0_, "")
            ax.text(x0 + 0.02, pl + H + 0.015, f"H0 {H0_ * 1e3:.0f} (settled, dashed)", fontsize=7, va="bottom")
        else:
            dim_v(xr, pl, pl + H0_, f"H0 {H0_ * 1e3:.0f}")
        dim_v(xr + 0.07, pl, pl + H, f"H {H * 1e3:.0f}")
        dim_v(xr + 0.07, pl + H, pl + H + tdh, f"TDH {tdh * 1e3:.0f}")
        dim_v(xr + 0.07, pl + H + tdh, tot, f"{fl * 1e3:.0f}")
        dim_v(xr + 0.07, 0, pl, f"{pl * 1e3:.0f}")
        dim_v(x0 - wall - 0.05, 0, tot, f"overall {tot * 1e3:.0f}", side=-1)
        ax.annotate("", xy=(x0, tot + 0.2), xytext=(x0 + dt, tot + 0.2),
                    arrowprops=dict(arrowstyle="<|-|>", lw=0.7, color="0.1", shrinkA=0, shrinkB=0))
        ax.text(x0 + dt / 2, tot + 0.215, f"d_t {dt * 1e3:.0f} (ID)", ha="center", va="bottom", fontsize=7)
        ax.text(x0 + dt / 2, tot + 0.30,
                f"Strategy {g['strategy']}: {g['mass_kg']:g} kg P-25\nH0/d_t = {g['H0_over_dt']:.2f}, d_b = {g['d_b_darton_m'] * 100:.1f} cm",
                ha="center", va="bottom", fontsize=8, weight="bold")
        x0 += dt + gap
    txt = ("HYPOTHETICAL design extension, not validated.  Dimensions in mm, drawn to scale.\n"
           "Assumptions: u0 = 7 cm/s (1.4 u_mf, u_mf = 5 cm/s at lab scale); bubbling (ABF) fluidisation of\n"
           "P-25 agglomerates (d_ag 300 um, rho_ag 47 kg/m3: Geldart group A by size and density, indicative);\n"
           "bed expansion H/H0 = 1.7 (lab value); d_b from Darton et al. (1977) at mid-bed; freeboard =\n"
           "TDH = 1000 u0^2/g (Fournol et al. 1973, group A); 150 mm filter section; 100 mm plenum.\n"
           "Dashed line: settled bed H0.  Bubbles drawn at d_b to scale.")
    ax.text(0.0, -0.32, txt, fontsize=7, va="top", family="monospace")
    ax.set_aspect("equal")
    ax.set_xlim(-0.25, x0 - gap + 0.35)
    ax.set_ylim(-0.62, max(g["vessel_height_m"] for g in geoms) + 0.45)
    ax.axis("off")
    ax.set_title("Fluidised-bed ALD reactor for 1 kg P-25 batches: section views (our drawing)", fontsize=10)
    save(fig, name)


# ----------------------------------------------------------------------------------------
# Main
# ----------------------------------------------------------------------------------------
def check(name, group, ref, ours, tol_key, unit=""):
    tol = TOL["checks"][tol_key]
    if "rel" in tol:
        dev = (ours - ref) / ref
        ok = abs(dev) <= tol["rel"]
        tol_s = {"rel": tol["rel"]}
    else:
        dev = ours - ref
        ok = abs(dev) <= tol["abs"]
        tol_s = {"abs": tol["abs"]}
    return {"name": name, "group": group, "reference": sig(ref), "ours": sig(ours), "unit": unit,
            "deviation": sig(dev, 4), "deviation_kind": "rel" if "rel" in tol else "abs",
            "tolerance": tol_s, "tolerance_key": tol_key, "status": "pass" if ok else "fail"}


def main() -> int:
    OUT.mkdir(exist_ok=True)
    rr = SRC["reported_results"]
    checks = []

    # G1
    t100 = tau_sat_min(1e4)
    t01 = tau_sat_min(10.0) / 3600
    checks.append(check("tau_sat_min at P_TMA = 100 mbar", "G1", rr["tau_sat_min"]["at_P_TMA_100_mbar"]["value"], t100, "tau_sat_min_100mbar", "s"))
    checks.append(check("tau_sat_min at P_TMA = 0.1 mbar", "G1", rr["tau_sat_min"]["at_P_TMA_0.1_mbar"]["value"], t01, "tau_sat_min_0.1mbar", "h"))

    # G2
    ts = rr["time_scales_table_7_4"]
    atm, mb = time_scales(P_ATM), time_scales(P_MBAR)
    g2 = [
        ("tau_em, 1.013 bar", ts["tau_em"]["1.013_bar"], atm["tau_em"], "tau_em_atm", "s"),
        ("tau_b, 1.013 bar", ts["tau_b"]["1.013_bar"], atm["tau_b"], "tau_b_atm", "s"),
        ("tau_int, 1.013 bar", ts["tau_int"]["1.013_bar"], atm["tau_int"], "tau_int_atm", "s"),
        ("tau_int, 1 mbar", ts["tau_int"]["1_mbar"], mb["tau_int"], "tau_int_mbar", "s"),
        ("tau_ga, 1 mbar", ts["tau_ga"]["1_mbar"], mb["tau_ga"], "tau_ga_mbar", "s"),
        ("tau_c, 1.013 bar", ts["tau_c"]["1.013_bar"], atm["tau_c"], "tau_c_atm", "s"),
        ("tau_c, 1 mbar", ts["tau_c"]["1_mbar"], mb["tau_c"], "tau_c_mbar", "s"),
        ("tau_sa, 1.013 bar", ts["tau_sa"]["1.013_bar"], atm["tau_sa"], "tau_sa_atm", "s"),
        ("tau_sa, 1 mbar", ts["tau_sa"]["1_mbar"], mb["tau_sa"], "tau_sa_mbar", "s"),
        ("Thiele phi*, 1.013 bar (complex level)", ts["thiele_star"]["1.013_bar"], atm["thiele_star"], "thiele_atm", "-"),
        ("Thiele phi*, 1 mbar (simple level)", ts["thiele_star"]["1_mbar"], mb["thiele_star"], "thiele_mbar", "-"),
    ]
    for name, ref, ours, key, unit in g2:
        checks.append(check(name, "G2", ref, ours, key, unit))

    # G3
    txt = rr["required_height_text"]
    ha = 100 * h_star(1.5 * 0.05, 0.05, 0.045, D_mol(P_ATM), 0.9999)
    hm = 100 * h_star(1.5 * 0.05, 0.05, 0.045, D_mol(P_MBAR), 0.9999)
    checks.append(check("H*, d_b = 4.5 cm, u_mf = 5 cm/s, 1.013 bar", "G3", txt["atm_db_4.5cm_umf_5cms"]["value"], ha, "Hstar_text_atm", "cm"))
    checks.append(check("H*, d_b = 4.5 cm, u_mf = 5 cm/s, 1 mbar", "G3", txt["mbar_db_4.5cm"]["value"], hm, "Hstar_text_mbar", "cm"))

    # G4
    f74 = rr["required_height_fig_7_4"]
    umfs = INP["fig_7_4_conditions"]["u_mf_values"]["value"]
    keys = ["umf_0.01_cms", "umf_0.1_cms", "umf_2.5_cms", "umf_5_cms"]
    for umf, key in zip(umfs, keys):
        for i, d in enumerate(f74["d_b_cm"][:4]):
            ours = 100 * h_star(1.5 * umf, umf, d / 100, D_mol(P_ATM), 0.9999)
            checks.append(check(f"H* Fig. 7.4a, u_mf = {umf * 100:g} cm/s, d_b = {d:g} cm", "G4",
                                f74["panel_a_1.013_bar"][key][i], ours, "Hstar_fig_7_4a", "cm"))
    for i, d in enumerate(f74["d_b_cm"][:4]):
        ref = 0.5 * (f74["panel_b_1_mbar"]["min"][i] + f74["panel_b_1_mbar"]["max"][i])
        ours = float(np.mean([100 * h_star(1.5 * u, u, d / 100, D_mol(P_MBAR), 0.9999) for u in umfs]))
        checks.append(check(f"H* Fig. 7.4b (mean over u_mf), d_b = {d:g} cm", "G4", ref, ours, "Hstar_fig_7_4b", "cm"))

    # G5: dynamic model, base case
    P_tma = v("dynamic_model", "P_TMA_in")
    base = dynamic(MASS0, H0, DT0, DB, P_tma, t_profile=19.9)
    prof = rr["bubble_profile_fig_7_3"]
    for zq in (0.1, 0.2, 0.4):
        ref = prof["t_19.9_s"][prof["z_over_H"].index(zq)]
        ours = float(np.interp(zq, base["profile"]["z_over_H"], base["profile"]["cb"]))
        checks.append(check(f"C_b/C_in at z/H = {zq:g}, t = 19.9 s", "G5", ref, ours, "bubble_profile_fig_7_3", "-"))

    # internal checks
    internal = [
        check("dynamic eta at t = 19.9 s vs Eq. 7.51", "internal", base["eta_qss"], base["profile"]["eta_dyn"], "dynamic_vs_qss_eta", "-"),
        {"name": "dynamic mass balance closure (base)", "group": "internal", "reference": 0.0,
         "ours": sig(base["mass_balance_rel"], 4), "tolerance": {"rel": TOL["checks"]["dynamic_mass_balance"]["rel"]},
         "status": "pass" if abs(base["mass_balance_rel"]) <= TOL["checks"]["dynamic_mass_balance"]["rel"] else "fail"},
    ]
    # grid study (base, coarse grid)
    coarse = dynamic(MASS0, H0, DT0, DB, P_tma, nz=200, nr=20, t_profile=19.9)

    # verdict
    n_all = len(checks)
    n_pass = sum(c["status"] == "pass" for c in checks)
    head_ok = all(c["status"] == "pass" for c in checks if c["group"] in ("G1", "G3"))
    if not all(c["status"] == "pass" for c in internal):
        verdict = "invalid run"
    elif n_pass == n_all:
        verdict = "PASS"
    elif n_pass >= 0.75 * n_all and head_ok:
        verdict = "PARTIAL"
    else:
        verdict = "FAIL"
    by_group = {}
    for c in checks:
        gname = c["group"]
        by_group.setdefault(gname, [0, 0])
        by_group[gname][0] += c["status"] == "pass"
        by_group[gname][1] += 1

    # ------------------------------------------------------------------ extension
    m1 = v("extension", "batch_mass")
    geo = {s: scaled_geometry(m1, s) for s in ("A", "B")}
    runA = dynamic(m1, geo["A"]["H0_m"], geo["A"]["d_t_m"], geo["A"]["d_b_darton_m"], v("extension", "P_TMA_in"))
    runB = dynamic(m1, geo["B"]["H0_m"], geo["B"]["d_t_m"], geo["B"]["d_b_darton_m"], v("extension", "P_TMA_in"))
    sweep = {"A": [], "B": []}
    for s in ("A", "B"):
        for m in v("extension", "batch_sweep"):
            g = scaled_geometry(m, s)
            eta = eta_qss(U0, UMF, g["d_b_darton_m"], D_mol(P_ATM), g["H_m"])
            tmin = tau_sat_min(v("extension", "P_TMA_in"), g["H0_m"])
            hreq = h_star(U0, UMF, g["d_b_darton_m"], D_mol(P_ATM), 0.9999)
            sweep[s].append({**{k: sig(x) if isinstance(x, float) else x for k, x in g.items()},
                             "eta_qss": sig(eta, 10), "tau_sat_min_s": sig(tmin),
                             "pulse_estimate_s": sig(0.99 * tmin / eta), "H_star_9999_m": sig(hreq)})
    gB = geo["B"]
    sens_db = [{"d_b_cm": d * 100, "eta_qss": sig(eta_qss(U0, UMF, d, D_mol(P_ATM), gB["H_m"]), 10),
                "H_star_9999_cm": sig(100 * h_star(U0, UMF, d, D_mol(P_ATM), 0.9999), 4)}
               for d in (0.01, gB["d_b_darton_m"], 0.045, 0.08)]
    geldart = {"rho_ag_g_cm3": AG["rho3"]["value"] / 1000, "d_ag_um": D_AG * 1e6,
               "product": AG["rho3"]["value"] / 1000 * D_AG * 1e6, "A_B_boundary_product": 225,
               "group": "A (indicative; behaves as ABF, agglomerate bubbling fluidisation)"}

    def summary(r, g=None):
        out = {"geometry": {k: sig(x) for k, x in r["geometry"].items()},
               "hydro": {k: sig(x) for k, x in r["hydro"].items()},
               "C_in_mol_m3": sig(r["C_in_mol_m3"]), "sites_mol": sig(r["sites_mol"]),
               "q_mol_m3_agglomerate": sig(r["q_mol_m3_agglomerate"]),
               "tau_sat_min_s": sig(r["tau_sat_min_s"]), "t99_s": sig(r["t99_s"]),
               "eta_qss": sig(r["eta_qss"], 10), "mass_balance_rel": sig(r["mass_balance_rel"], 3),
               "at_t99": {k: sig(x) for k, x in r.get("at_t99", {}).items()},
               "TMA_flow_g_min": sig(r["hydro"]["u0"] * r["geometry"]["area_m2"] * r["C_in_mol_m3"] * M_TMA * 60),
               "TMA_per_batch_g": sig(r["at_t99"]["TMA_fed_mol"] * M_TMA) if "at_t99" in r else None}
        if g:
            out["vessel"] = {k: sig(x) if isinstance(x, float) else x for k, x in g.items()}
        return out

    result = {
        "case": "fluidised-bed-ald-powders", "issue": "#336", "tracker": "#333",
        "run": {"python": platform.python_version(), "numpy": np.__version__, "scipy": scipy.__version__,
                "matplotlib": matplotlib.__version__, "pyyaml": yaml.__version__},
        "tolerances_file": "tolerances.yaml", "tolerances_frozen": TOL["frozen"],
        "verdict": verdict, "checks_passed": n_pass, "checks_total": n_all,
        "by_group": {k: f"{a}/{b}" for k, (a, b) in sorted(by_group.items())},
        "headline_checks_G1_G3_all_pass": head_ok,
        "checks": checks, "internal_checks": internal,
        "not_evaluable": [
            {"target": "saturation time 46.4 s of the full dynamic model (Fig. 7.3)", "reason": "TMA inlet concentration not stated; our P_TMA,in is reconstructed from this value"},
            {"target": "cumulative CH4 about 1.5 per TMA (Fig. 7.1a)", "reason": "Travis rate laws and parameters not given; our kinetics are lumped"},
            {"target": "tau_rxn (Table 7.4)", "reason": "kinetic; used as input"},
            {"target": "tau_ga at 1.013 bar (Table 7.4)", "reason": "used to reconstruct D (circular)"},
        ],
        "supplementary": {
            "D_TMA_N2_reconstructed_m2_s": D_ATM,
            "D_TMA_N2_wilke_lee_m2_s": sig(wilke_lee_D(P_ATM)),
            "D_ratio_wilke_lee_over_reconstructed": sig(wilke_lee_D(P_ATM) / D_ATM, 4),
            "tau_em_as_printed_eq_7_19_s": sig(atm["tau_em_as_printed_eq_7_19"]),
            "time_scales_1.013_bar": {k: sig(x) for k, x in atm.items()},
            "time_scales_1_mbar": {k: sig(x) for k, x in mb.items()},
            "fig_7_3_slope_H_Kbe_over_ub_ours": sig(base["hydro"]["H_Kbe_over_ub"], 4),
            "fig_7_3_slope_from_digitised_z0.1_z0.2": sig(-(math.log(prof["t_19.9_s"][2]) - math.log(prof["t_19.9_s"][1])) / 0.1, 4),
            "Hstar_1mbar_text_anchor_by_umf_cm": {f"{u * 100:g}": sig(100 * h_star(1.5 * u, u, 0.045, D_mol(P_MBAR), 0.9999), 4) for u in umfs},
            "grid_study": {"t99_fine_s": sig(base["t99_s"]), "t99_coarse_s": sig(coarse["t99_s"]),
                           "cb_z0.1_fine": sig(float(np.interp(0.1, base["profile"]["z_over_H"], base["profile"]["cb"])), 4),
                           "cb_z0.1_coarse": sig(float(np.interp(0.1, coarse["profile"]["z_over_H"], coarse["profile"]["cb"])), 4)},
        },
        "dynamic_base": summary(base),
        "extension": {
            "label": "HYPOTHETICAL design extension (not validated)",
            "changed_input": f"batch mass {MASS0 * 1e3:.2f} g -> {m1:g} kg at fixed target mean coverage {v('extension', 'target_coverage')}",
            "strategy_A": summary(runA, geo["A"]), "strategy_B": summary(runB, geo["B"]),
            "darton_db_lab_bed_m": sig(darton_db(H_BASE / 2)),
            "geldart": geldart, "sweep": sweep, "sensitivity_db_strategy_B": sens_db,
        },
        "figures": ["fig1-required-bed-height.svg", "fig2-bubble-profile.svg",
                    "fig3-pulse-breakthrough-coverage.svg", "fig4-batch-sweep.svg",
                    "fig5-section-view-1kg.svg"],
    }
    (OUT / "comparison.json").write_text(json.dumps(result, indent=1) + "\n")

    fig_hstar(None, None, f74)
    fig_profile(base, prof)
    fig_pulse({"base": base, "A": runA, "B": runB})
    fig_sweep(sweep)
    section_view([geo["A"], geo["B"]], "fig5-section-view-1kg.svg")

    print(f"verdict: {verdict} ({n_pass}/{n_all}); by group {result['by_group']}")
    for c in checks + internal:
        print(f"  [{c['status']:4}] {c['name']}: ref {c['reference']} ours {c['ours']} dev {c.get('deviation')}")
    for s, r in (("base", base), ("A", runA), ("B", runB)):
        print(f"  {s}: d_t {r['geometry']['d_t_m']:.3f} m, H {r['geometry']['H_m']:.3f} m, d_b {r['geometry']['d_b_m'] * 100:.2f} cm,"
              f" tau_min {r['tau_sat_min_s']:.1f} s, t99 {r['t99_s']:.1f} s, eta_qss {r['eta_qss']:.6f}, mb {r['mass_balance_rel']:.1e}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
