# /// script
# requires-python = ">=3.12,<3.14"
# dependencies = [
#   "numpy==2.3.4",
#   "scipy==1.16.3",
#   "matplotlib==3.10.7",
#   "pyyaml==6.0.3",
# ]
# ///
"""Spray-drying stickiness case study (#337, tracker #333; ADR 0030, layout ADR 0031).

Single entry point. From the repository root:

    uv run benchmarks/reproductions/spray-drying-stickiness/run.py

What it does
  1. Case A: predicts the drying trajectory of the sessile MD12 droplet of Sewalt et al. (2022)
     from its stated conditions with a receding-interface diffusion model, and compares the
     initial d^2 rate, the locking time and the locked radius with the reported values.
  2. Case B: reproduces the modelled time to a glassy surface (t_glass) of the thesis model for
     DE 12 in the particle ejector (Sewalt 2024, Table 5.1).
  3. Extension (HYPOTHETICAL): runs the same droplet model at the outlet conditions of an assumed
     pilot co-current spray dryer, changes inlet humidity and feed solids, and overlays the
     surface (T - Tg) trajectory with a bounded residence-time window.

No third-party dataset exists for this case, so nothing is downloaded: every input is a fact
restated in source.yaml / inputs.yaml. Outputs go to results/ next to this file
(comparison.json, extension.json, SVG figures drawn by this script). The script exits non-zero
only if it fails to run; the reproduction verdict is recorded in comparison.json.
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
from scipy.integrate import quad, solve_ivp
from scipy.optimize import brentq
from scipy.sparse import lil_matrix

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

HERE = Path(__file__).resolve().parent
RESULTS = HERE / "results"

INPUTS = yaml.safe_load((HERE / "inputs.yaml").read_text())
SOURCE = yaml.safe_load((HERE / "source.yaml").read_text())
TOL = yaml.safe_load((HERE / "tolerances.yaml").read_text())


def v(d):
    """Value of an inputs.yaml entry."""
    return d["value"]


# ------------------------------------------------------------------------------------------
# Constants and material properties (inputs.yaml: constants, material)
# ------------------------------------------------------------------------------------------
C = INPUTS["constants"]
P_ATM = float(v(C["pressure"]))
R_GAS = float(v(C["gas_constant"]))
K_B = float(v(C["boltzmann"]))
M_W = float(v(C["molar_mass_water"]))
M_AIR = float(v(C["molar_mass_air"]))
CP_VAP = float(v(C["cp_water_vapour"]))

MAT = INPUTS["material"]
RHO_S = float(v(MAT["density_solute"]))
RHO_W = float(v(MAT["density_water"]))
CP_S = float(v(MAT["cp_solute"]))
CP_W = float(v(MAT["cp_water"]))
M_S = float(v(MAT["molar_mass_solute"]))  # g/mol
GT = MAT["glass_transition"]
TG_S = float(v(GT["Tg_solute"]))
TG_W = float(v(GT["Tg_water"]))
K_GT = float(v(GT["dCp_water"])) / float(v(GT["dCp_solute"]))
GAB = MAT["water_activity"]
GAB_WM, GAB_K, GAB_C = (float(v(GAB[k])) for k in ("w_m", "k", "c"))
VIS = MAT["viscosity"]
KH, K_MH, ALPHA_MH = (float(v(VIS[k])) for k in ("SMT_k_H", "SMT_K", "SMT_alpha"))
C1, C2, MU_G = (float(v(VIS[k])) for k in ("WLF_C1", "WLF_C2", "WLF_mu_g"))
P0, P1 = float(v(VIS["blend_P0"])), float(v(VIS["blend_P1"]))
DIF = MAT["diffusivity"]
D0_W = float(v(DIF["D0_water"]))
E_W = float(v(DIF["E_water"]))
VS_W, VS_S = float(v(DIF["V_star_water"])), float(v(DIF["V_star_solute"]))
K1_W, K1_S = float(v(DIF["K1_gamma_water"])), float(v(DIF["K1_gamma_solute"]))
K2_W, K2_S = float(v(DIF["K2_water"])), float(v(DIF["K2_solute"]))
TGW_FV, TGS_FV = float(v(DIF["Tg_water_fv"])), float(v(DIF["Tg_solute_fv"]))
ZETA, CHI = float(v(DIF["zeta"])), float(v(DIF["chi"]))
RH_S = float(v(DIF["r_h_solute"]))

# Post-hoc diagnostic overrides (empty for every scored run; see diagnostics()).
OVR: dict = {}

NUM = INPUTS["numerics"]
N_CELLS = int(v(NUM["cells"]))
RTOL = float(v(NUM["rtol"]))
ATOL = float(v(NUM["atol"]))

# Antoine coefficients for water (thesis Table 5.3, restated in source.yaml)
ANT = SOURCE["thesis_model_parameters"]["antoine_water"]


def psat(T):
    """Saturation pressure of water [Pa], T in K (Antoine, mmHg/degC form)."""
    T = np.asarray(T, dtype=float)
    lo, hi = ANT["low"], ANT["high"]
    tc = T - 273.15
    p_lo = 10.0 ** (lo["A"] - lo["B"] / (tc + lo["C"]))
    p_hi = 10.0 ** (hi["A"] - hi["B"] / (tc + hi["C"]))
    return 133.32 * np.where(T <= 373.15, p_lo, p_hi)


def latent_heat(T):
    return 2.501e6 - 2370.0 * (T - 273.15)


def d_vap(T):
    return 1.4850e-7 * T - 1.88805e-5


def mu_air(T):
    return -2.293e-11 * T**2 + 5.991782e-8 * T + 2.53901766e-6


def lam_air(T):
    return 6.7755124e-5 * T + 6.108642996e-3


def cp_air(T):
    return 2.98463495e-4 * T**2 - 0.124554461009 * T + 1016.8585391153


def rho_air(T):
    return P_ATM * M_AIR / (R_GAS * T)


def mu_water(T):
    return (-2.216134e-6 * T**3 + 2.313106525e-3 * T**2 - 0.809475788245 * T + 95.354362060802) * 1e-3


def mass_fraction_solute(phi):
    """Solute mass fraction from solute volume fraction (ideal mixing)."""
    return phi * RHO_S / (phi * RHO_S + (1.0 - phi) * RHO_W)


def phi_from_ws(ws):
    return (ws / RHO_S) / (ws / RHO_S + (1.0 - ws) / RHO_W)


def tg_gordon_taylor(ws):
    ww = 1.0 - ws
    return (ws * TG_S + K_GT * ww * TG_W) / (ws + K_GT * ww)


def water_activity(ws):
    """Inverse GAB: a_w from the solute mass fraction, capped at 1 (inputs.yaml)."""
    ws = np.clip(ws, 1e-9, 1.0 - 1e-12)
    w = (1.0 - ws) / ws  # water/solids mass ratio
    c, k, wm = GAB_C, GAB_K, GAB_WM
    b = w * (c - 2.0) - wm * c
    y = (b + np.sqrt(b * b + 4.0 * w * w * (c - 1.0))) / (2.0 * w * (c - 1.0))
    return np.minimum(y / k, 1.0)


def gab_moisture(a_w):
    """GAB water/solids ratio at activity a_w."""
    c, k, wm = GAB_C, GAB_K, GAB_WM
    return wm * c * k * a_w / ((1.0 - k * a_w) * (1.0 - k * a_w + c * k * a_w))


def viscosity(ws, T):
    """Solution viscosity [Pa s]: SMT (dilute) blended with WLF (concentrated)."""
    phi = phi_from_ws(ws)
    rho_mix = phi * (RHO_S - RHO_W) + RHO_W
    c_gdl = ws * rho_mix / 10.0  # kg/m3 -> g/dL
    eta_int = K_MH * M_S**ALPHA_MH  # dL/g
    y = eta_int * c_gdl
    mu_smt = (y * np.exp(KH * y) + 1.0) * mu_water(T)
    dT = np.maximum(T - tg_gordon_taylor(ws), -0.9 * C2)
    mu_wlf = MU_G * 10.0 ** (-C1 * dT / (C2 + dT))
    s = 1.0 / (1.0 + np.exp(-(ws - P0) / P1))
    return (1.0 - s) * mu_smt + s * mu_wlf


def diffusivity(phi, T):
    """Mutual diffusivity [m2/s] of the MD12-water mixture (generalised Darken)."""
    X = 1.0 - phi  # water volume fraction
    om_w = X * RHO_W / (X * RHO_W + phi * RHO_S)
    om_s = 1.0 - om_w
    num = om_w * VS_W + om_s * ZETA * VS_S
    den = om_w * K1_W * (K2_W + T - TGW_FV) + om_s * K1_S * (K2_S + T - TGS_FV)
    d_w = OVR.get("D0", D0_W) * np.exp(-E_W / (R_GAS * T)) * np.exp(-num / den)
    d_s = K_B * T / (6.0 * math.pi * viscosity(om_s, T) * RH_S)
    q = 1.0 - 2.0 * OVR.get("chi", CHI) * X * (1.0 - X)
    return ((1.0 - X) * d_w + X * d_s) * q


# ------------------------------------------------------------------------------------------
# Sessile-drop geometry (Popov 2005)
# ------------------------------------------------------------------------------------------
def popov_f(theta):
    first = math.sin(theta) / (1.0 + math.cos(theta))

    def integrand(tau):
        if tau == 0.0:
            return 0.0
        return (1.0 + math.cosh(2 * theta * tau)) / math.sinh(2 * math.pi * tau) * math.tanh((math.pi - theta) * tau)

    integ, _ = quad(integrand, 0.0, 60.0, limit=400)
    return first + 4.0 * integ


def sessile_geometry(theta):
    """Return (flux factor vs equal-volume sphere, R_curv/R_eq, contact radius/R_eq)."""
    g = ((2.0 + math.cos(theta)) * (1.0 - math.cos(theta)) ** 2 / 4.0) ** (1.0 / 3.0)  # R_eq / R_curv
    ratio_curv = math.sin(theta) * popov_f(theta) / 4.0  # J_sessile / J_sphere(R_curv)
    return ratio_curv / g, 1.0 / g, math.sin(theta) / g


# ------------------------------------------------------------------------------------------
# Droplet model: radial diffusion with a receding interface, finite volumes on xi = r/R(t)
# ------------------------------------------------------------------------------------------
class Droplet:
    def __init__(self, R0, w0, T0, T_gas, p_v_gas, u_rel=0.0, flux_factor=1.0, g_sub_per_R=0.0,
                 isothermal=False, n_cells=N_CELLS):
        self.R0, self.w0, self.T0 = R0, w0, T0
        self.T_gas, self.p_v_gas, self.u = T_gas, p_v_gas, u_rel
        self.F, self.g_sub, self.iso = flux_factor, g_sub_per_R, isothermal
        self.N = n_cells
        j = np.arange(self.N + 1)
        self.xf = 1.0 - (1.0 - j / self.N) ** 2  # faces, fine at the surface
        self.xc = 0.5 * (self.xf[1:] + self.xf[:-1])
        self.vfrac = self.xf[1:] ** 3 - self.xf[:-1] ** 3  # cell volume / (4/3 pi R^3)
        self.phi0 = float(phi_from_ws(w0))
        self.vs_total = self.phi0  # solute volume / (4/3 pi R0^3)

    # external transfer --------------------------------------------------------------------
    def transfer(self, R, T, a_w):
        Tf = 0.5 * (T + self.T_gas)
        mu, rho, dv, lam, cp = mu_air(Tf), rho_air(Tf), d_vap(Tf), lam_air(Tf), cp_air(Tf)
        re = rho * self.u * 2.0 * R / mu
        sc, pr = mu / (rho * dv), mu * cp / lam
        sh = 2.0 + 0.6 * math.sqrt(re) * sc ** (1.0 / 3.0)
        nu = 2.0 + OVR.get("nu_coef", 0.4) * math.sqrt(re) * pr ** (1.0 / 3.0)
        beta, h = sh * dv / (2.0 * R), nu * lam / (2.0 * R)
        area = 4.0 * math.pi * R * R
        mdot = self.F * area * beta * M_W * (a_w * psat(T) - self.p_v_gas) / (R_GAS * Tf)
        q_in = self.F * area * h * (self.T_gas - T) + self.g_sub * R * (self.T_gas - T)
        return float(mdot), float(q_in)

    # state: s_i = solute volume in cell i / (4/3 pi R0^3), then r = R/R0 and T. The sum of s_i
    # is a linear invariant, which the BDF integrator conserves to round-off.
    def phi_of(self, y):
        return y[:self.N] / (self.vfrac * y[self.N] ** 3)

    def rhs(self, t, y):
        N = self.N
        r, T = y[N], y[N + 1]
        phi = self.phi_of(y)
        R = r * self.R0
        a_w = water_activity(mass_fraction_solute(phi[-1]))
        mdot, q_in = self.transfer(R, T, a_w)
        Rdot = -mdot / (RHO_W * 4.0 * math.pi * R * R)
        # interior faces 1..N-1
        xf = self.xf[1:-1]
        area = 4.0 * math.pi * (R * xf) ** 2
        dr = R * (self.xc[1:] - self.xc[:-1])
        d_face = diffusivity(0.5 * (phi[1:] + phi[:-1]), T)
        w_face = xf * Rdot
        up = np.where(w_face <= 0.0, phi[:-1], phi[1:])
        flux = area * (-d_face * (phi[1:] - phi[:-1]) / dr - up * w_face)
        F_all = np.concatenate(([0.0], flux, [0.0]))
        vol = (4.0 / 3.0) * math.pi * R**3 * self.vfrac
        ds = (F_all[:-1] - F_all[1:]) / ((4.0 / 3.0) * math.pi * self.R0**3)
        if self.iso:
            dT = 0.0
        else:
            mass = vol * (phi * RHO_S + (1.0 - phi) * RHO_W)
            wsc = mass_fraction_solute(phi)
            heat_cap = float(np.sum(mass * (wsc * CP_S + (1.0 - wsc) * CP_W)))
            dT = (q_in - mdot * latent_heat(T)) / heat_cap
        return np.concatenate((ds, [Rdot / self.R0, dT]))

    def sparsity(self):
        N = self.N
        S = lil_matrix((N + 2, N + 2), dtype=int)
        for i in range(N):
            for j in (i - 1, i, i + 1):
                if 0 <= j < N:
                    S[i, j] = 1
        S[:, N - 1] = 1
        S[:, N] = 1
        S[:, N + 1] = 1
        S[N, :] = 1
        S[N + 1, :] = 1
        return S.tocsr()

    def solute_mass_error(self, y):
        return abs(float(np.sum(y[:self.N])) - self.vs_total) / self.vs_total

    def surface_margin(self, y):
        """T_d - Tg(surface) [K]."""
        return float(y[self.N + 1] - tg_gordon_taylor(mass_fraction_solute(self.phi_of(y)[-1])))

    def fields(self, y):
        """(phi cells, r, T) from a state vector or an array of states (columns)."""
        y = np.asarray(y)
        if y.ndim == 1:
            return self.phi_of(y), y[self.N], y[self.N + 1]
        return y[:self.N] / (self.vfrac[:, None] * y[self.N] ** 3), y[self.N], y[self.N + 1]

    def run(self, t_end, stop_at_glass=True):
        y0 = np.concatenate((self.phi0 * self.vfrac, [1.0, self.T0]))
        atol = np.concatenate((ATOL * self.vfrac, [ATOL, 1e-6]))
        events = None
        if stop_at_glass:
            def ev(t, y):
                return self.surface_margin(y)
            ev.terminal, ev.direction = True, -1
            events = [ev]
        sol = solve_ivp(self.rhs, (0.0, t_end), y0, method="BDF", rtol=RTOL, atol=atol,
                        jac_sparsity=self.sparsity(), events=events, dense_output=True)
        if sol.status < 0:
            raise RuntimeError(f"integration failed: {sol.message}")
        t_glass = float(sol.t_events[0][0]) if stop_at_glass and sol.t_events[0].size else None
        mass_err = max(self.solute_mass_error(sol.y[:, k]) for k in range(sol.y.shape[1]))
        return sol, t_glass, mass_err


def wet_bulb_rate(R, T_gas, p_v_gas, u, flux_factor=1.0):
    """Steady pure-water droplet: (T_wb, kappa = -dR^2/dt) for a free sphere."""
    d = Droplet(R, 1e-6, T_gas, T_gas, p_v_gas, u_rel=u, flux_factor=flux_factor)

    def balance(T):
        mdot, q = d.transfer(R, T, 1.0)
        return q - mdot * latent_heat(T)

    T_wb = brentq(balance, 200.0, T_gas)
    mdot, _ = d.transfer(R, T_wb, 1.0)
    kappa = 2.0 * R * mdot / (RHO_W * 4.0 * math.pi * R * R)
    return T_wb, kappa


# ------------------------------------------------------------------------------------------
# Case A: OCT sessile droplet
# ------------------------------------------------------------------------------------------
def case_a(n_cells=N_CELLS, k_sub=None, isothermal=False):
    A = INPUTS["case_A_oct"]
    theta = math.radians(float(v(A["contact_angle"])))
    flux_factor, rc_over_req, a_over_req = sessile_geometry(theta)
    k_s = float(v(A["substrate_conductivity"])) if k_sub is None else k_sub
    R0 = 0.5 * float(v(A["initial_equivalent_diameter"])) * 1e-6
    T_gas = float(v(A["gas_temperature"]))
    p_v = float(v(A["gas_relative_humidity"])) * float(psat(T_gas))
    drop = Droplet(R0, float(v(A["initial_mass_fraction_solute"])), float(v(A["initial_temperature"])),
                   T_gas, p_v, u_rel=float(v(A["gas_velocity"])), flux_factor=flux_factor,
                   g_sub_per_R=4.0 * k_s * a_over_req, isothermal=isothermal, n_cells=n_cells)
    sol, t_glass, merr = drop.run(600.0)
    t0, t1 = v(A["t_fit_window"])
    tt = np.linspace(t0, t1, 81)[1:]
    d2 = (2.0 * R0 * sol.sol(tt)[drop.N]) ** 2
    kappa = float(-np.sum((d2 - (2 * R0) ** 2) * tt) / np.sum(tt * tt))
    out = {"drop": drop, "sol": sol, "t_glass": t_glass, "mass_error": merr, "kappa_um2_s": kappa * 1e12,
           "flux_factor": flux_factor, "rc_over_req": rc_over_req, "R0": R0}
    if t_glass is not None:
        y = sol.sol(t_glass)
        out["R_curv_lock_um"] = float(y[drop.N] * R0 * rc_over_req * 1e6)
    return out


def oct_informational(res):
    drop, sol, R0 = res["drop"], res["sol"], res["R0"]
    info = {}
    y = sol.sol(60.0)
    phi, r, _ = drop.fields(y)
    R = r * R0
    info["centre_wt_percent_60s"] = float(100 * mass_fraction_solute(phi[0]))
    rr = drop.xc * R
    mask = rr >= R - 10e-6
    vol = drop.vfrac[mask]
    phi_mean = float(np.sum(phi[mask] * vol) / np.sum(vol))
    info["outer_10um_wt_percent_60s"] = float(100 * mass_fraction_solute(phi_mean))
    # end of constant rate: instantaneous d^2 rate 10 % below the fitted initial rate
    tt = np.linspace(1.0, res["t_glass"], 2000)
    d2 = (2.0 * R0 * sol.sol(tt)[drop.N]) ** 2
    rate = -np.gradient(d2, tt) * 1e12
    below = np.nonzero(rate < 0.9 * res["kappa_um2_s"])[0]
    below = below[tt[below] > 5.0]
    info["end_constant_rate_s_model_10pct_drop"] = float(tt[below[0]]) if below.size else None
    return info


# ------------------------------------------------------------------------------------------
# Case B: thesis model, particle ejector, DE 12
# ------------------------------------------------------------------------------------------
def reconstruct_velocity(R0, T_gas, t_full_target):
    def f(u):
        _, kappa = wet_bulb_rate(R0, T_gas, 0.0, u)
        return R0**2 / kappa - t_full_target

    u = brentq(f, 1e-6, 50.0, xtol=1e-10)
    _, kappa = wet_bulb_rate(R0, T_gas, 0.0, u)
    return u, R0**2 / kappa


def case_b(n_cells=N_CELLS, only=None):
    B = INPUTS["case_B_thesis_pe"]
    R0 = float(v(B["initial_radius"])) * 1e-6
    targets = {k: float(val["value"]) for k, val in B["t_full_targets"].items() if k.startswith("T")}
    vel = {}
    for key, t_target in targets.items():
        T_gas = 273.15 + float(key[1:])
        u, t_model = reconstruct_velocity(R0, T_gas, t_target)
        vel[key] = {"u_m_s": u, "t_full_target_s": t_target, "t_full_model_s": t_model}
    out = {"velocity": vel, "runs": {}}
    for name, cond in B["conditions"].items():
        if not isinstance(cond, dict) or (only and name != only):
            continue
        T_gas = float(cond["T_gas_K"])
        key = f"T{round(T_gas - 273.15)}"
        T0 = wet_bulb_rate(R0, T_gas, 0.0, vel[key]["u_m_s"])[0] if OVR.get("T0_wet_bulb") else float(v(B["initial_temperature"]))
        drop = Droplet(R0, float(cond["w0"]), T0, T_gas, 0.0,
                       u_rel=vel[key]["u_m_s"], n_cells=n_cells)
        sol, t_glass, merr = drop.run(400.0)
        y = sol.sol(t_glass)
        out["runs"][name] = {"t_glass_s": t_glass, "t_full_s": vel[key]["t_full_target_s"],
                             "t_glass_over_t_full": t_glass / vel[key]["t_full_target_s"],
                             "T_droplet_at_glass_K": float(y[drop.N + 1]),
                             "surface_wt_percent_at_glass": float(100 * mass_fraction_solute(drop.phi_of(y)[-1])),
                             "mass_error": merr, "sol": sol, "drop": drop}
    return out


# ------------------------------------------------------------------------------------------
# Extension: hypothetical pilot co-current spray dryer
# ------------------------------------------------------------------------------------------
def humidity_to_pv(Y):
    return Y * P_ATM / (M_W / M_AIR + Y)


def dryer_balance(Y_in, w0, G_kg_h=None):
    X = INPUTS["extension"]
    gas = X["drying_gas"]
    G = (float(v(gas["dry_mass_flow"])) if G_kg_h is None else G_kg_h) / 3600.0
    T_in, T_out = float(v(gas["inlet_temperature"])), float(v(gas["outlet_temperature"]))
    loss = float(v(gas["heat_loss_fraction"]))
    T_feed = float(v(X["feed"]["temperature"]))
    q_avail = G * (cp_air(0.5 * (T_in + T_out)) + Y_in * CP_VAP) * (T_in - T_out) * (1.0 - loss)
    per_kg_water = (2.501e6 + CP_VAP * (T_out - 273.15) - CP_W * (T_feed - 273.15)
                    + w0 / (1.0 - w0) * CP_S * (T_out - T_feed))
    E = q_avail / per_kg_water
    Y_out = Y_in + E / G
    p_v = humidity_to_pv(Y_out)
    ch = X["chamber"]
    D, H = float(v(ch["diameter"])), float(v(ch["cylinder_height"]))
    half = math.radians(float(v(ch["cone_included_angle"])) / 2.0)
    h_cone = (D / 2.0) / math.tan(half)
    V = math.pi * D**2 / 4.0 * H + math.pi * (D / 2.0) ** 2 * h_cone / 3.0
    Q_out = (G / M_AIR + G * Y_out / M_W) * R_GAS * T_out / P_ATM
    return {"evaporation_kg_h": E * 3600.0, "feed_kg_h": E / (1.0 - w0) * 3600.0,
            "powder_kg_h": E * w0 / (1.0 - w0) * 3600.0, "Y_out": Y_out, "p_v_out_Pa": p_v,
            "RH_out": p_v / float(psat(T_out)), "T_out_K": T_out, "chamber_volume_m3": V,
            "total_height_m": H + h_cone, "gas_flow_out_m3_s": Q_out, "tau_gas_s": V / Q_out}


def equilibrium_margin(T, RH):
    """T - Tg of powder in equilibrium with gas of relative humidity RH at T [K]."""
    w = gab_moisture(RH)
    ws = 1.0 / (1.0 + w)
    return float(T - tg_gordon_taylor(ws)), float(100 * (1 - ws))


def critical_RH(T, dT_c):
    return brentq(lambda a: equilibrium_margin(T, a)[0] - dT_c, 1e-4, 0.99)


def extension_run(d0_um, w0, Y_in):
    X = INPUTS["extension"]
    bal = dryer_balance(Y_in, w0)
    R0 = 0.5 * d0_um * 1e-6
    u = float(v(X["droplet"]["slip_velocity"]))
    T_wb, kappa = wet_bulb_rate(R0, bal["T_out_K"], bal["p_v_out_Pa"], u)
    t_full = R0**2 / kappa
    drop = Droplet(R0, w0, float(v(X["droplet"]["initial_temperature"])), bal["T_out_K"],
                   bal["p_v_out_Pa"], u_rel=u)
    sol, _, merr = drop.run(3.0 * t_full, stop_at_glass=False)
    tt = np.geomspace(1e-4 * t_full, 3.0 * t_full, 1500)
    ys = sol.sol(tt)
    phis, _, Ts = drop.fields(ys)
    margin = Ts - tg_gordon_taylor(mass_fraction_solute(phis[-1]))

    def first_below(level):
        idx = np.nonzero(margin <= level)[0]
        if not idx.size:
            return None, False
        k = idx[0]
        t_cross = float(np.interp(level, [margin[k], margin[k - 1]], [tt[k], tt[k - 1]])) if k > 0 else float(tt[0])
        stays = bool(np.all(margin[k:] <= level + 1e-6))
        return t_cross, stays

    lo, hi = v(X["stickiness"]["dT_c_band"])
    t_20, stays_20 = first_below(float(hi))
    t_0, stays_0 = first_below(float(lo))
    factor = float(v(X["stickiness"]["late_bound_factor"]))
    return {"d0_um": d0_um, "feed_solids": w0, "Y_in": Y_in, "RH_out": bal["RH_out"],
            "T_wet_bulb_K": T_wb, "t_full_s": t_full,
            "t_nonsticky_dTc20_s": t_20, "stays_below_dTc20": stays_20,
            "t_glass_surface_s": t_0, "stays_glassy": stays_0,
            "t_late_bound_s": None if t_0 is None else factor * t_0,
            "final_margin_K": float(margin[-1]),
            "final_mean_moisture_wt_percent": float(100 * (1 - mass_fraction_solute(
                np.sum(ys[:drop.N, -1]) / ys[drop.N, -1] ** 3))),
            "mass_error": merr, "_t": tt, "_margin": margin}



def diagnostics(a):
    """Post-hoc sensitivity of the case-B bias and the case-A radius (not scored, after the run)."""
    out = {"note": "post-hoc diagnosis after the comparison run; not scored, inputs.yaml unchanged"}
    variants = {
        "baseline": {},
        "nusselt_coefficient_0.6": {"nu_coef": 0.6},
        "D0_literal_1.48e-5": {"D0": 1.48e-5},
        "chi_0": {"chi": 0.0},
        "initial_T_at_wet_bulb": {"T0_wet_bulb": True},
    }
    ref = SOURCE["reference_B_thesis_model_tglass"]["reported_results_DE12"]
    out["B_tglass_s"] = {}
    for name, ovr in variants.items():
        OVR.clear()
        OVR.update(ovr)
        row = {}
        for cond in ("c10_T25", "c20_T25", "c30_T25"):
            t = case_b(only=cond)["runs"][cond]["t_glass_s"]
            row[cond] = {"t_glass_s": t, "deviation_rel": t / float(ref[cond]["t_glass_s"]) - 1.0}
        out["B_tglass_s"][name] = row
    OVR.clear()
    # case A: when does the model droplet pass the measured locked radius, and with what surface?
    drop, sol, R0 = a["drop"], a["sol"], a["R0"]
    r_target = 141e-6 / a["rc_over_req"] / R0
    t_hit = brentq(lambda t: sol.sol(t)[drop.N] - r_target, 1.0, a["t_glass"])
    phi, _, T = drop.fields(sol.sol(t_hit))
    out["A_model_at_measured_locked_radius"] = {
        "t_s": t_hit, "surface_wt_percent": float(100 * mass_fraction_solute(phi[-1])),
        "centre_wt_percent": float(100 * mass_fraction_solute(phi[0])),
        "surface_T_minus_Tg_K": float(T - tg_gordon_taylor(mass_fraction_solute(phi[-1])))}
    return out

# ------------------------------------------------------------------------------------------
# Checks
# ------------------------------------------------------------------------------------------
def rel_check(name, ref, val, rel):
    dev = (val - ref) / ref
    return {"check": name, "reference": ref, "computed": val, "deviation_rel": dev, "tolerance_rel": rel,
            "status": "pass" if abs(dev) <= rel else "fail"}


def verdict(checks):
    by = {c["check"]: c["status"] for c in checks}
    a = [by[k] for k in by if k.startswith("A")]
    b = [by[k] for k in by if k.startswith("B")]
    i = [by[k] for k in by if k.startswith("I")]
    if "gap" in a + b + i:
        pass
    if all(s == "pass" for s in a + b + i):
        return "PASS"
    if all(s == "pass" for s in i) and (all(s == "pass" for s in a) or all(s == "pass" for s in b)):
        return "PARTIAL"
    return "FAIL"


# ------------------------------------------------------------------------------------------
# Figures (our own drawing; light surface, categorical slots 1-3, ordinal blue ramp)
# ------------------------------------------------------------------------------------------
INK, INK2, GRID, SURF = "#0b0b0b", "#52514e", "#e4e3df", "#fcfcfb"
S1, S2, S3 = "#2a78d6", "#eb6834", "#1baf7a"
RAMP = ["#86b6ef", "#3987e5", "#256abf", "#184f95"]


def style():
    plt.rcParams.update({
        "svg.hashsalt": "repro-337", "svg.fonttype": "none", "font.size": 9,
        "axes.edgecolor": INK2, "axes.labelcolor": INK, "xtick.color": INK2, "ytick.color": INK2,
        "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.6, "axes.spines.top": False,
        "axes.spines.right": False, "figure.facecolor": SURF, "axes.facecolor": SURF,
        "legend.frameon": False, "lines.linewidth": 2.0, "text.color": INK,
    })


def save(fig, name):
    fig.savefig(RESULTS / name, format="svg", metadata={"Date": None}, facecolor=SURF)
    plt.close(fig)


def fig_oct(res, brackets):
    drop, sol, R0 = res["drop"], res["sol"], res["R0"]
    tg = res["t_glass"]
    tt = np.linspace(0.0, tg, 400)
    ys = sol.sol(tt)
    d2n = ys[drop.N] ** 2
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(6.4, 6.0), sharex=True)
    ref = SOURCE["reference_A_oct_sessile_droplet"]["reported_results"]
    kap = ref["initial_d2_rate"]["value"]
    d0 = 432.0
    t_lin = np.linspace(0, 213, 50)
    ax1.plot(t_lin, 1 - kap * t_lin / d0**2, color=INK2, lw=1.2, ls="--", label="measured initial rate (880 µm²/s), extrapolated")
    ax1.plot(tt, d2n, color=S1, label="model, k_s = 0.15 W/m/K (scored)")
    for key, col, lab in (("no_substrate", S2, "model bracket: no substrate heat"),
                          ("isothermal", S3, "model bracket: isothermal 20 °C")):
        b = brackets[key]
        t_b = np.linspace(0.0, b["t_glass"], 300)
        ax1.plot(t_b, b["sol"].sol(t_b)[b["drop"].N] ** 2, color=col, lw=1.2, label=lab)
    ax1.axvspan(150, 170, color=GRID, alpha=0.8, lw=0)
    ax1.annotate("measured locking ≈ 160 s", (160, 0.95), ha="center", fontsize=8, color=INK2)
    r_lock = ref["outer_radius_locked"]["value"]
    ax1.plot([160], [(r_lock / res["rc_over_req"] / (d0 / 2)) ** 2], "o", ms=8, color=INK,
             mec=SURF, mew=2, label="measured locked radius 141 µm (fitted at 250 s), at locking")
    ax1.plot([tg], [d2n[-1]], "D", ms=8, color=S1, mec=SURF, mew=2, label="model surface glass (t_glass)")
    ax1.set_ylabel("(d/d0)²")
    ax1.set_ylim(0, 1.05)
    ax1.legend(fontsize=7, loc="lower left")
    ax1.set_title("A. Sessile MD12 droplet, 10 wt%, 20 °C, 35 % RH: model vs OCT measurement", fontsize=9, loc="left")
    phis, _, _ = drop.fields(ys)
    ws_s = 100 * mass_fraction_solute(phis[-1])
    ws_c = 100 * mass_fraction_solute(phis[0])
    ax2.plot(tt, ws_s, color=S1, label="model surface")
    ax2.plot(tt, ws_c, color=S2, label="model centre")
    cm = ref["concentration_measurements"]
    ax2.errorbar([60], [cm["at_60_s_near_interface"]["value"]], yerr=[cm["at_60_s_near_interface"]["uncertainty"]],
                 fmt="o", color=INK, ms=6, capsize=3, label="OCT near interface, 60 s")
    ax2.errorbar([60], [cm["at_60_s_bulk"]["value"]], yerr=[cm["at_60_s_bulk"]["uncertainty"]],
                 fmt="s", color=INK2, ms=6, capsize=3, label="OCT bulk, 60 s")
    ax2.axhline(46, color=INK2, lw=0.8, ls=":")
    ax2.annotate("OCT upper measurable limit 46 wt%", (5, 48), fontsize=7, color=INK2)
    ax2.set_ylabel("MD12 mass fraction (wt%)")
    ax2.set_xlabel("time after dispensing (s)")
    ax2.set_ylim(0, 100)
    ax2.legend(fontsize=7, loc="upper left", bbox_to_anchor=(0.0, 0.88))
    fig.tight_layout()
    save(fig, "fig1_oct_trajectory.svg")


def fig_thesis(bres):
    ref = SOURCE["reference_B_thesis_model_tglass"]["reported_results_DE12"]
    names = [k for k in ref if k.startswith("c")]
    x = [ref[k]["t_glass_s"] for k in names]
    y = [bres["runs"][k]["t_glass_s"] for k in names]
    fig, ax = plt.subplots(figsize=(4.6, 4.4))
    lim = np.array([0, 70])
    ax.fill_between(lim, lim * 0.75, lim * 1.25, color=GRID, lw=0, label="±25 % (frozen tolerance)")
    ax.plot(lim, lim, color=INK2, lw=1.0)
    ax.plot(x, y, "o", ms=8, color=S1, mec=SURF, mew=2, label="this model")
    labels = {"c10_T25": "10 wt%, 25 °C", "c20_T25": "20 wt%, 25 °C", "c30_T25": "30 wt%, 25 °C",
              "c20_T45": "20 wt%, 45 °C", "c20_T65": "20 wt%, 65 °C"}
    offsets = {"c30_T25": (30, -26), "c20_T65": (-10, 28)}
    for k, xi, yi in zip(names, x, y):
        ax.annotate(labels[k], (xi, yi), xytext=offsets.get(k, (6, -10)), textcoords="offset points",
                    fontsize=7, color=INK2,
                    arrowprops={"arrowstyle": "-", "color": INK2, "lw": 0.6} if k in offsets else None)
    ax.set_xlim(*lim)
    ax.set_ylim(*lim)
    ax.set_xlabel("thesis model t_glass (s), Table 5.1")
    ax.set_ylabel("this model t_glass (s)")
    ax.set_title("B. Time to a glassy surface, MD12, R0 = 240 µm, dry gas", fontsize=9, loc="left")
    ax.legend(fontsize=7, loc="upper left")
    fig.tight_layout()
    save(fig, "fig2_thesis_tglass.svg")


def fig_dryer(ext, window):
    fig, axes = plt.subplots(2, 2, figsize=(9.0, 6.6), sharey=True)
    sweeps = (("feed_solids", "feed solids", lambda r: f"{100 * r['feed_solids']:.0f} wt%"),
              ("inlet_humidity", "inlet humidity", lambda r: f"{1000 * r['Y_in']:.0f} g/kg"))
    for row, d0 in enumerate((60, 150)):
        for col, (key, title, lab) in enumerate(sweeps):
            ax = axes[row, col]
            ax.axhspan(0, 20, color=GRID, alpha=0.9, lw=0)
            ax.axvspan(*window["core_pass_s"], color="#cde2fb", alpha=0.6, lw=0)
            ax.axvspan(*window["mean_gas_time_s"], color="#b7d3f6", alpha=0.6, lw=0)
            runs = [r for r in ext["sweeps"][key] if r["d0_um"] == d0]
            ramp = RAMP[-len(runs):] if len(runs) < 4 else RAMP
            for r, colr in zip(runs, ramp):
                ax.plot(r["_t"], r["_margin"], color=colr, label=lab(r))
            ax.set_xscale("log")
            ax.set_xlim(1e-3, 60)
            ax.set_ylim(-80, 320)
            ax.set_title(f"d0 = {d0} µm, changed input: {title}", fontsize=9, loc="left")
            if col == 0:
                ax.set_ylabel("surface T − Tg (K)")
            if row == 1:
                ax.set_xlabel("drying time (s), log scale")
            ax.legend(fontsize=7, loc="upper left", title=title, title_fontsize=7)
            ax.annotate("sticky threshold band (T − Tg)c = 0 to 20 K", (1.2e-3, -62), fontsize=7, color=INK2)
            ax.annotate("core\npass", (window["core_pass_s"][0] * 1.05, 255), fontsize=7, color=INK2)
            ax.annotate("mean gas\nresidence", (window["mean_gas_time_s"][0] * 0.55, 200), fontsize=7, color=INK2,
                        ha="right")
    fig.suptitle("Hypothetical pilot co-current dryer (outlet 85 °C): droplet surface stickiness vs residence-time window",
                 fontsize=9, x=0.02, ha="left")
    fig.tight_layout()
    save(fig, "fig3_dryer_stickiness.svg")


# ------------------------------------------------------------------------------------------
def strip(d):
    return {k: val for k, val in d.items() if not k.startswith("_") and k not in ("sol", "drop")}


def main():
    RESULTS.mkdir(exist_ok=True)
    style()
    checks, info = [], {}

    # sanity of the sessile factor (Popov): f(90 deg) = 2
    popov_90 = popov_f(math.pi / 2)

    # ---------------- Case A
    a = case_a()
    a_fine = case_a(n_cells=2 * N_CELLS)
    brackets = {"no_substrate": case_a(k_sub=0.0), "isothermal": case_a(isothermal=True)}
    refA = SOURCE["reference_A_oct_sessile_droplet"]["reported_results"]
    tA = TOL["checks"]
    checks.append(rel_check("A1_initial_d2_rate", float(refA["initial_d2_rate"]["value"]), a["kappa_um2_s"],
                            float(tA["A1_initial_d2_rate"]["rel"])))
    checks.append(rel_check("A2_locking_time", float(refA["locking_point"]["value"]), a["t_glass"],
                            float(tA["A2_locking_time"]["rel"])))
    checks.append(rel_check("A3_locked_radius", float(refA["outer_radius_locked"]["value"]), a["R_curv_lock_um"],
                            float(tA["A3_locked_radius"]["rel"])))
    info["A"] = oct_informational(a)
    info["A"]["brackets"] = {k: {"kappa_um2_s": b["kappa_um2_s"], "t_glass_s": b["t_glass"],
                                 "R_curv_lock_um": b.get("R_curv_lock_um")} for k, b in brackets.items()}
    info["A"]["sessile_flux_factor"] = a["flux_factor"]
    info["A"]["t_d2_extrapolated_model_s"] = (432.0**2) / a["kappa_um2_s"]

    # ---------------- Case B
    b = case_b()
    b_fine = case_b(n_cells=2 * N_CELLS, only="c20_T25")
    refB = SOURCE["reference_B_thesis_model_tglass"]["reported_results_DE12"]
    for i, k in enumerate(("c10_T25", "c20_T25", "c30_T25", "c20_T45", "c20_T65"), start=1):
        name = f"B{i}_tglass_{k}"
        checks.append(rel_check(name, float(refB[k]["t_glass_s"]), b["runs"][k]["t_glass_s"],
                                float(tA[name]["rel"])))
    ratio = b["runs"]["c30_T25"]["t_glass_s"] / b["runs"]["c10_T25"]["t_glass_s"]
    ref_ratio = float(str(tA["B6_solids_ratio_T25"]["reference"]))
    checks.append({"check": "B6_solids_ratio_T25", "reference": ref_ratio, "computed": ratio,
                   "deviation_abs": ratio - ref_ratio, "tolerance_abs": float(tA["B6_solids_ratio_T25"]["abs"]),
                   "status": "pass" if abs(ratio - ref_ratio) <= float(tA["B6_solids_ratio_T25"]["abs"]) else "fail"})

    # ---------------- Internal checks
    merrs = [a["mass_error"], a_fine["mass_error"]] + [r["mass_error"] for r in b["runs"].values()] \
        + [r["mass_error"] for r in b_fine["runs"].values()] + [x["mass_error"] for x in brackets.values()]
    m_max = max(merrs)
    checks.append({"check": "I1_solute_mass_conservation", "computed": m_max,
                   "tolerance_rel": float(tA["I1_solute_mass_conservation"]["rel"]),
                   "status": "pass" if m_max <= float(tA["I1_solute_mass_conservation"]["rel"]) else "fail"})
    g_a = abs(a_fine["t_glass"] - a["t_glass"]) / a["t_glass"]
    g_b = abs(b_fine["runs"]["c20_T25"]["t_glass_s"] - b["runs"]["c20_T25"]["t_glass_s"]) / b["runs"]["c20_T25"]["t_glass_s"]
    checks.append({"check": "I2_grid_convergence", "computed": max(g_a, g_b), "case_A": g_a, "case_B_c20_T25": g_b,
                   "tolerance_rel": float(tA["I2_grid_convergence"]["rel"]),
                   "status": "pass" if max(g_a, g_b) <= float(tA["I2_grid_convergence"]["rel"]) else "fail"})
    clos = max(abs(vv["t_full_model_s"] - vv["t_full_target_s"]) / vv["t_full_target_s"] for vv in b["velocity"].values())
    checks.append({"check": "I3_tfull_closure", "computed": clos, "tolerance_rel": float(tA["I3_tfull_closure"]["rel"]),
                   "status": "pass" if clos <= float(tA["I3_tfull_closure"]["rel"]) else "fail"})

    # ---------------- Informational
    refC = SOURCE["reference_C_thesis_locking_DE12"]["normalised_locking_time_mean_sd"]
    info["C_locking_vs_model"] = {k: {"measured_tl_over_tfull": refC[k][0], "sd": refC[k][1],
                                      "model_tglass_over_tfull": b["runs"][k]["t_glass_over_t_full"]} for k in refC}
    info["B_runs"] = {k: strip(r) for k, r in b["runs"].items()}
    info["B_reconstructed_velocity"] = b["velocity"]
    info["property_sanity"] = {
        "viscosity_10wt_20C_mPa_s": float(viscosity(0.10, 293.15) * 1e3), "stated_10wt_mPa_s": 1.1,
        "viscosity_46wt_20C_Pa_s": float(viscosity(0.46, 293.15)), "stated_46wt_Pa_s": 0.1,
        "water_self_diffusion_298K_m2_s": float(D0_W * math.exp(-E_W / (R_GAS * 298.15)) * math.exp(
            -VS_W / (K1_W * (K2_W + 298.15 - TGW_FV)))), "measured_water_self_diffusion_298K_m2_s": 2.30e-9,
        "popov_f_90deg": popov_90, "popov_f_90deg_exact": 2.0,
        "surface_wt_percent_glass_at_15C": float(100 * brentq(lambda w: tg_gordon_taylor(w) - 288.15, 0.3, 0.999)),
        "gab_aw_cap_solids_wt_percent": float(100 / (1 + gab_moisture(1.0))),
    }

    # ---------------- Extension (hypothetical)
    X = INPUTS["extension"]
    base_Y = float(v(X["drying_gas"]["base_inlet_humidity"]))
    base_w = float(v(X["feed"]["base_solids"]))
    sizes = v(X["droplet"]["initial_diameters"])
    ext = {"sweeps": {"inlet_humidity": [], "feed_solids": []}}
    cache = {}

    def run_cached(d0, w0, Y):
        key = (d0, w0, Y)
        if key not in cache:
            cache[key] = extension_run(d0, w0, Y)
        return cache[key]

    for d0 in sizes:
        for Y in X["changed_inputs"]["inlet_humidity"]["values"]:
            ext["sweeps"]["inlet_humidity"].append(run_cached(d0, base_w, float(Y)))
        for w0 in X["changed_inputs"]["feed_solids"]["values"]:
            ext["sweeps"]["feed_solids"].append(run_cached(d0, float(w0), base_Y))
    G = float(v(X["drying_gas"]["dry_mass_flow"]))
    G_lo, G_hi = X["drying_gas"]["dry_mass_flow"]["range"]
    bal = dryer_balance(base_Y, base_w)
    u_lo, u_hi = v(X["residence_time"]["core_velocity"])
    window = {"core_pass_s": [bal["total_height_m"] / u_hi, bal["total_height_m"] / u_lo],
              "mean_gas_time_s": [dryer_balance(base_Y, base_w, G_hi)["tau_gas_s"],
                                  dryer_balance(base_Y, base_w, G_lo)["tau_gas_s"]],
              "basis": "core pass = total chamber height / core velocity (1-3 m/s); mean gas time = V/Q at outlet, dry gas flow +-20 %"}
    T_out = bal["T_out_K"]
    eq = {}
    for Y in X["changed_inputs"]["inlet_humidity"]["values"]:
        bY = dryer_balance(float(Y), base_w)
        m, mo = equilibrium_margin(T_out, bY["RH_out"])
        eq[f"{float(Y):.3f}"] = {"RH_out": bY["RH_out"], "Y_out": bY["Y_out"], "evaporation_kg_h": bY["evaporation_kg_h"],
                                 "feed_kg_h": bY["feed_kg_h"], "equilibrium_moisture_wt_percent": mo,
                                 "equilibrium_T_minus_Tg_K": m}
    crit = {}
    for dTc in v(X["stickiness"]["dT_c_band"]):
        a_c = critical_RH(T_out, float(dTc))
        p_c = a_c * float(psat(T_out))
        Y_out_c = (M_W / M_AIR) * p_c / (P_ATM - p_c)
        crit[f"dTc_{dTc}K"] = {"RH_out": a_c, "Y_out": Y_out_c, "Y_in_equivalent": Y_out_c - (bal["Y_out"] - base_Y)}
    ext_out = {
        "label": "HYPOTHETICAL design extension, not validated",
        "dryer_base": bal, "dryer_gas_flow_kg_h": G, "residence_window": window,
        "equilibrium_powder_at_outlet": eq, "critical_outlet_humidity_for_stickiness": crit,
        "sweeps": {k: [strip(r) for r in rs] for k, rs in ext["sweeps"].items()},
    }
    for r in ext["sweeps"]["inlet_humidity"] + ext["sweeps"]["feed_solids"]:
        m_max = max(m_max, r["mass_error"])

    info["post_hoc_diagnostics"] = diagnostics(a)
    vd = verdict(checks)
    comp = {
        "case": "spray-drying-stickiness", "issue": 337, "tracker": 333,
        "tolerances_file": "tolerances.yaml (frozen 2026-11-04)",
        "verdict": vd, "pass_rule": TOL["pass_rule"], "checks": checks, "informational": info,
        "run": {"python": platform.python_version(), "numpy": np.__version__, "scipy": scipy.__version__,
                "matplotlib": matplotlib.__version__, "cells": N_CELLS, "rtol": RTOL},
        "max_solute_mass_error_all_runs_incl_extension": m_max,
    }
    (RESULTS / "comparison.json").write_text(json.dumps(comp, indent=2, sort_keys=True, default=float) + "\n")
    (RESULTS / "extension.json").write_text(json.dumps(ext_out, indent=2, sort_keys=True, default=float) + "\n")

    fig_oct(a, brackets)
    fig_thesis(b)
    fig_dryer(ext, window)

    print(f"verdict: {vd}")
    for c in checks:
        print(f"  {c['check']:32s} {c['status']:5s} computed={c['computed']:.4g}" +
              (f" reference={c['reference']:.4g}" if "reference" in c else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
