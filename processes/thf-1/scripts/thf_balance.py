"""Independent heat and material balance of thf-1 (DESIGN.md D-006). Run: cheme run scripts/thf_balance.py

Provenance of the ASSUMED stream and duty values in process/flowsheet.yaml: core cannot yet
qualify a polar activity-coefficient mixture (THF / water / BDO) or a liquid-phase reactor's
energy balance, so the values are calculated here and entered as ASSUMED.

Method (all concept-level, stated in DESIGN.md):
- VLE: thermo, NRTL liquid with the ChemSep THF/water parameters packaged in thermo, ideal gas,
  Psat basis (no Poynting); the azeotrope at each column pressure by bisection on y - x.
- Columns: binary McCabe-Thiele with constant molar overflow for the minimum reflux (feed
  condition q from the feed enthalpy), reflux = 1.3 x minimum (ASSUMED), total condenser,
  distillate and bottoms at their bubble points; condenser duty from the dew-point vapour to the
  bubble-point liquid, reboiler duty from the column's energy balance.
- Reactor: overall energy balance of the reactor and its rectifying column with the liquid
  formation enthalpies of chemicals (BDO, THF, water); DHBE and p-TSA (no data in thermo) take
  BDO's specific enthalpy per kg (they are < 0.6 % of the mass, D-006).
"""

from chemicals import Hfg, Hfl
from thermo import ChemicalConstantsPackage, FlashVL, GibbsExcessLiquid, IdealGas
from thermo.interaction_parameters import IPDB
from thermo.nrtl import NRTL

# --- design specifications (DESIGN.md D-002 .. D-008) ---------------------------------------
PRODUCT_KG_H = 6250.0  # 50 kt/a / 8000 h (ASSUMED, D-002)
W_WATER_PRODUCT = 0.0005  # 0.05 wt% water in THF (ASSUMED spec, D-002)
S_THF = 0.995  # kmol THF per kmol BDO converted (ASSUMED, D-005); the rest to DHBE
W_BLEED = {"DHBE": 0.30, "PTSA": 0.02, "W": 0.05, "BDO": 0.63}  # reactor liquid bleed (ASSUMED, D-005)
T_REACT = 418.15  # 145 C reactor liquid (patent US9284289 examples, D-004)
P_REACT = 130e3  # reactor / rectifier, Pa (ASSUMED, within the patent's 100-500 kPa, D-004)
R_REACTOR = 0.5  # reflux ratio of the reactor's rectifying column (ASSUMED, patent range, D-004)
T_COND = 313.15  # condensate / coolers outlet (ASSUMED)
P_LP, P_HP = 110e3, 800e3  # column pressures, Pa (ASSUMED, D-007)
DX_AZ = 0.03  # distillates kept 0.03 mol/mol on the feasible side of each azeotrope (ASSUMED)
X_THF_WW = 2e-5  # THF mole fraction in the LP column bottoms (wastewater, ASSUMED, D-007)
RR_FACTOR = 1.3  # reflux / minimum reflux (ASSUMED, D-007)
R_FLOOR = 0.3  # lowest reflux ratio taken: margin for the CMO error, THF and water latent heats differ (ASSUMED, D-007)
ETA_PUMP = 0.6  # pump efficiency (ASSUMED, D-008)
T_BDO = 303.15  # BDO feed temperature (ASSUMED, design basis)

MW = {"THF": 72.10572, "W": 18.01528, "BDO": 90.121, "DHBE": 162.23, "PTSA": 172.20162}

constants, props = ChemicalConstantsPackage.from_IDs(["tetrahydrofuran", "water"])
bij = IPDB.get_ip_asymmetric_matrix("ChemSep NRTL", constants.CASs, "bij")
alpha = IPDB.get_ip_asymmetric_matrix("ChemSep NRTL", constants.CASs, "alphaij")


def make_flasher(cas_props, cons, ge=True):
    T, P, zs = 350.0, 1e5, [1.0 / cons.N] * cons.N
    kw = {}
    if ge:
        kw["GibbsExcessModel"] = NRTL(T=T, xs=zs, tau_bs=bij, alpha_cs=alpha)
    liq = GibbsExcessLiquid(
        VaporPressures=cas_props.VaporPressures,
        HeatCapacityGases=cas_props.HeatCapacityGases,
        VolumeLiquids=cas_props.VolumeLiquids,
        EnthalpyVaporizations=cas_props.EnthalpyVaporizations,
        equilibrium_basis="Psat", caloric_basis="Psat", T=T, P=P, zs=zs, **kw)
    gas = IdealGas(HeatCapacityGases=cas_props.HeatCapacityGases, T=T, P=P, zs=zs)
    return FlashVL(cons, cas_props, liquid=liq, gas=gas)


F = make_flasher(props, constants)


def bubble(x, P):
    """Bubble point of the modified Raoult model (NRTL, ideal gas): T, y_THF and the liquid's H
    (J/mol, ideal gas at 298.15 K reference). Solved directly: thermo's PVF flash fails here."""
    xs, lo, hi = [x, 1 - x], 250.0, 600.0
    for _ in range(45):  # bisection on T: sum(x gamma Psat) - P rises with T
        T = 0.5 * (lo + hi)
        g = F.liquid.to(T=T, P=P, zs=xs).gammas()
        ks = [gi * props.VaporPressures[i](T) for i, gi in enumerate(g)]
        s = xs[0] * ks[0] + xs[1] * ks[1]
        if s > P:
            hi = T
        else:
            lo = T
    return T, xs[0] * ks[0] / s, F.liquid.to(T=T, P=P, zs=xs).H()


def dew_h(x, P, branch):
    """Dew point of vapour x: the liquid on the branch (lo, hi) of the azeotrope whose y = x."""
    lo, hi = branch
    for _ in range(60):
        m = 0.5 * (lo + hi)
        if bubble(m, P)[1] > x:
            hi = m
        else:
            lo = m
    T = bubble(0.5 * (lo + hi), P)[0]
    return T, F.gas.to(T=T, P=P, zs=[x, 1 - x]).H()


def h_tp(x, T, P):
    return F.liquid.to(T=T, P=P, zs=[x, 1 - x]).H()


def azeotrope(P):
    lo, hi = 0.3, 0.99
    for _ in range(60):
        m = 0.5 * (lo + hi)
        if bubble(m, P)[1] - m > 0:
            lo = m
        else:
            hi = m
    return 0.5 * (lo + hi)


def rmin(xd, xb, xf, q, P, light_is_thf):
    """Minimum reflux of a binary column, McCabe-Thiele, CMO, in light-component coordinates."""
    def y_eq(xl):
        x_thf = xl if light_is_thf else 1 - xl
        y_thf = bubble(x_thf, P)[1]
        return y_thf if light_is_thf else 1 - y_thf

    def feasible(R):
        # q-line / rectifying line intersection
        if abs(q - 1.0) < 1e-9:
            xq = xf
        else:
            xq = (xd / (R + 1) + xf / (q - 1)) / (q / (q - 1) - R / (R + 1))
        yq = R / (R + 1) * xq + xd / (R + 1)
        n = 40
        for i in range(n + 1):  # rectifying section
            x = xq + (xd - xq) * i / n
            if R / (R + 1) * x + xd / (R + 1) > y_eq(x) + 1e-9 and i < n:
                return False
        s = (yq - xb) / (xq - xb)  # stripping line through (xb, xb) and (xq, yq)
        for i in range(1, n + 1):
            x = xb + (xq - xb) * i / n
            if xb + s * (x - xb) > y_eq(x) + 1e-9:
                return False
        return True

    lo, hi = 0.0, 50.0
    for _ in range(40):
        m = 0.5 * (lo + hi)
        if feasible(m):
            hi = m
        else:
            lo = m
    return hi


def column(name, feed_n, feed_x, feed_h, xd, xb, P, light_is_thf, branch):
    """Molar flows (kmol/h), THF mole fractions; duties in kW."""
    D = feed_n * (feed_x - xb) / (xd - xb)
    B = feed_n - D
    Tb_d, _, hd = bubble(xd, P)
    Tb_b, _, hb = bubble(xb, P)
    Tdew, hv = dew_h(xd, P, branch)
    hl_f = bubble(feed_x, P)[2]
    hv_f = dew_h(feed_x, P, branch)[1]
    q = (hv_f - feed_h) / (hv_f - hl_f)
    xl = lambda x: x if light_is_thf else 1 - x
    Rm = rmin(xl(xd), xl(xb), xl(feed_x), q, P, light_is_thf)
    R = max(RR_FACTOR * Rm, R_FLOOR)
    Qc = (R + 1) * D * (hv - hd) / 3600.0  # kW (kmol/h * J/mol = kJ/h * 1e3/1e3)
    Qr = (D * hd + B * hb - feed_n * feed_h) / 3600.0 + Qc
    print(f"{name}: P {P/1e3:.0f} kPa, feed {feed_n:.3f} kmol/h x {feed_x:.5f} q {q:.3f}")
    print(f"  D {D:.3f} kmol/h x {xd:.5f} at {Tb_d:.2f} K (dew {Tdew:.2f}); B {B:.3f} kmol/h x {xb:.6f} at {Tb_b:.2f} K")
    print(f"  Rmin {Rm:.3f}, R {R:.3f}; condenser {Qc:.1f} kW, reboiler {Qr:.1f} kW")
    return dict(D=D, B=B, hd=hd, hb=hb, Td=Tb_d, Tb=Tb_b, Qc=Qc, Qr=Qr, R=R, Rmin=Rm, q=q)


def kg(n, x):  # kmol/h binary THF/water -> kg/h
    return n * (x * MW["THF"] + (1 - x) * MW["W"])


def wfrac(x):
    return x * MW["THF"] / (x * MW["THF"] + (1 - x) * MW["W"])


# --- azeotropes -----------------------------------------------------------------------------
x_az_lp, x_az_hp = azeotrope(P_LP), azeotrope(P_HP)
for P, xa in ((101325.0, azeotrope(101325.0)), (P_LP, x_az_lp), (P_HP, x_az_hp)):
    print(f"azeotrope {P/1e3:.1f} kPa: x_THF {xa:.4f} ({wfrac(xa)*100:.2f} wt%), T {bubble(xa, P)[0]:.2f} K")
xd_lp, xd_hp = x_az_lp - DX_AZ, x_az_hp + DX_AZ

# --- product and reactor balance --------------------------------------------------------------
P_THF = PRODUCT_KG_H * (1 - W_WATER_PRODUCT) / MW["THF"]
P_W = PRODUCT_KG_H * W_WATER_PRODUCT / MW["W"]
x_p = P_THF / (P_THF + P_W)
n_p = P_THF + P_W
# bleed per kmol BDO converted (c): DHBE 0.5 (1 - S) c kmol
m_bleed_per_c = 0.5 * (1 - S_THF) * MW["DHBE"] / W_BLEED["DHBE"]
w_bleed_per_c = m_bleed_per_c * W_BLEED["W"] / MW["W"]
# THF: S c = P_THF + x_ww n_ww ; water: (S + (1-S)/2) c - w_bleed c = P_W + (1 - x_ww) n_ww
a11, a12, b1 = S_THF, -X_THF_WW, P_THF
a21, a22, b2 = S_THF + 0.5 * (1 - S_THF) - w_bleed_per_c, -(1 - X_THF_WW), P_W
det = a11 * a22 - a12 * a21
c = (b1 * a22 - a12 * b2) / det
n_ww = (a11 * b2 - a21 * b1) / det
m_bleed = m_bleed_per_c * c
bleed = {k: m_bleed * v for k, v in W_BLEED.items()}  # kg/h
bdo_feed_kmol = c + bleed["BDO"] / MW["BDO"]
bdo_feed = bdo_feed_kmol * MW["BDO"]
ptsa = bleed["PTSA"]
conv = c / bdo_feed_kmol
oh_thf = S_THF * c
oh_w = (S_THF + 0.5 * (1 - S_THF)) * c - bleed["W"] / MW["W"]
n_oh, x_oh = oh_thf + oh_w, oh_thf / (oh_thf + oh_w)
print(f"BDO converted {c:.4f} kmol/h, fed {bdo_feed_kmol:.4f} kmol/h = {bdo_feed:.2f} kg/h, conversion {conv:.9f}")
print(f"p-TSA make-up {ptsa:.3f} kg/h; bleed {m_bleed:.3f} kg/h {bleed}")
print(f"overhead {n_oh:.4f} kmol/h = {kg(n_oh, x_oh):.2f} kg/h, x_THF {x_oh:.5f} ({wfrac(x_oh)*100:.2f} wt%)")
print(f"THF yield on BDO fed {S_THF * c / bdo_feed_kmol:.5f} mol/mol; kg BDO per kg product {bdo_feed / PRODUCT_KG_H:.5f}")

# reactor energy balance: each pure liquid at 298.15 K carries its liquid formation enthalpy
# (chemicals Hfl); thermo gives the change from there (heat capacity, excess and vaporisation
# enthalpy), so the vaporisation enthalpies are thermo's own on both sides.
bdo_c, bdo_p = ChemicalConstantsPackage.from_IDs(["1,4-butanediol"])
FB = make_flasher(bdo_p, bdo_c, ge=False)
T0 = 298.15
hfl_bdo, hfl_thf, hfl_w = Hfl("110-63-4"), Hfl("109-99-9"), Hfl("7732-18-5")
h0_t = F.liquid.to(T=T0, P=P_REACT, zs=[1 - 1e-12, 1e-12]).H()
h0_w = F.liquid.to(T=T0, P=P_REACT, zs=[1e-12, 1 - 1e-12]).H()


def h_bdo(T):
    return hfl_bdo + FB.liquid.to(T=T, P=P_REACT, zs=[1.0]).H() - FB.liquid.to(T=T0, P=P_REACT, zs=[1.0]).H()


def h_bin(x, T, P, phase):
    ph = F.liquid if phase == "l" else F.gas
    return x * hfl_thf + (1 - x) * hfl_w + ph.to(T=T, P=P, zs=[x, 1 - x]).H() - x * h0_t - (1 - x) * h0_w


h_oh_liq = h_bin(x_oh, T_COND, P_REACT, "l")  # condensate, 313 K
T_dew_oh, _ = dew_h(x_oh, P_REACT, (0.0, azeotrope(P_REACT)))
hv_oh = h_bin(x_oh, T_dew_oh, P_REACT, "g")
Q_cond_r = (1 + R_REACTOR) * n_oh * (hv_oh - h_oh_liq) / 3600.0
# bleed: water part as water at T_REACT (liquid), the rest per kg as BDO at T_REACT
H_bleed = bleed["W"] / MW["W"] * h_bin(1e-12, T_REACT, 10e5, "l") + (m_bleed - bleed["W"]) / MW["BDO"] * h_bdo(T_REACT)
H_in = bdo_feed_kmol * h_bdo(T_BDO) + ptsa / MW["BDO"] * h_bdo(T_BDO)
H_out = n_oh * h_oh_liq + H_bleed
Q_R = (H_out - H_in) / 3600.0 + Q_cond_r
print(f"reactor: overhead dew point {T_dew_oh:.2f} K at {P_REACT/1e3:.0f} kPa; steam duty {Q_R:.1f} kW, condenser {Q_cond_r:.1f} kW, H_out - H_in {(H_out - H_in)/3600:.1f} kW")
print(f"  heat of reaction, liquids at 298 K: {(hfl_thf + hfl_w - hfl_bdo)/1e3:.2f} kJ/mol; ideal gas {(Hfg('109-99-9') + Hfg('7732-18-5') - Hfg('110-63-4'))/1e3:.2f} kJ/mol")

# --- pressure-swing columns with the recycle ---------------------------------------------------
# HP: feed = LP distillate (x xd_lp), bottoms product x_p, distillate xd_hp -> recycle R
n_rec = n_p * (x_p - xd_lp) / (xd_lp - xd_hp)
n_d1 = n_p + n_rec
h_oh_bin = h_tp(x_oh, T_COND, P_LP)  # condensate on the binary's reference
T_rec_bub, _, h_rec = bubble(xd_hp, P_HP)
n_f1 = n_oh + n_rec
x_f1 = (n_oh * x_oh + n_rec * xd_hp) / n_f1
h_f1 = (n_oh * h_oh_bin + n_rec * h_rec) / n_f1
lp = column("C-201 LP column", n_f1, x_f1, h_f1, xd_lp, X_THF_WW, P_LP, True, (0.0, x_az_lp))
# P-201: LP distillate to the HP column
T_d1 = lp["Td"]
v_d1 = n_d1 * F.liquid.to(T=T_d1, P=P_LP, zs=[xd_lp, 1 - xd_lp]).V() * 1000.0  # m3/h
W_pump2 = v_d1 / 3600.0 * (P_HP + 30e3 - P_LP) / ETA_PUMP / 1e3
h_d1_hp = lp["hd"] + W_pump2 * 3600.0 / n_d1  # pump work into the liquid
hp = column("C-202 HP column", n_d1, xd_lp, h_d1_hp, xd_hp, x_p, P_HP, False, (x_az_hp, 1.0))
print(f"  recycle {n_rec:.3f} kmol/h; HP column feed {n_d1:.3f} kmol/h")
# BDO feed pump P-101 (300 -> 150 kPa needs none: delivered at 300 kPa(a), ASSUMED); p-TSA dosing ignored
rho_bdo = MW["BDO"] / 1000.0 / FB.liquid.to(T=T_BDO, P=P_REACT, zs=[1.0]).V()
W_pump1 = bdo_feed / rho_bdo / 3600.0 * (400e3 - 300e3) / ETA_PUMP / 1e3
print(f"pumps: P-101 {W_pump1:.2f} kW (BDO {rho_bdo:.0f} kg/m3), P-201 {W_pump2:.2f} kW ({v_d1:.2f} m3/h)")
# coolers
Q_prod = n_p * (hp["hb"] - h_tp(x_p, T_COND, P_HP)) / 3600.0
Q_ww = n_ww * (lp["hb"] - h_tp(X_THF_WW, T_COND, P_LP)) / 3600.0
print(f"coolers: E-203 THF product {Q_prod:.1f} kW, E-204 wastewater {Q_ww:.1f} kW")
print(f"check: LP bottoms {lp['B']:.4f} vs wastewater {n_ww:.4f} kmol/h")

# --- stream table (kg/h, mass fractions) -------------------------------------------------------
def line(sid, n, x):
    m = kg(n, x)
    print(f"{sid}: {m:.3f} kg/h, x_THF {x:.6f} mol, w_THF {wfrac(x):.8f}")

line("S5 condensate", n_oh, x_oh)
line("S8 HP recycle", n_rec, xd_hp)
line("S9 LP feed", n_f1, x_f1)
line("S10 LP distillate", n_d1, xd_lp)
line("S12 wastewater", lp["B"], X_THF_WW)
line("S14 product", n_p, x_p)
tot_in = bdo_feed + ptsa
tot_out = kg(lp["B"], X_THF_WW) + kg(n_p, x_p) + m_bleed
print(f"overall: in {tot_in:.3f} kg/h, out {tot_out:.3f} kg/h, diff {tot_in - tot_out:.4f}")
print(f"temperatures: reactor top dew {T_dew_oh:.2f}; LP top {lp['Td']:.2f} bottom {lp['Tb']:.2f}; HP top {hp['Td']:.2f} bottom {hp['Tb']:.2f}; recycle bubble {T_rec_bub:.2f}")
print(f"heat integration: HP condenser {hp['Qc']:.1f} kW at {hp['Td']:.2f} K vs LP reboiler {lp['Qr']:.1f} kW at {lp['Tb']:.2f} K")
q_int = min(hp["Qc"], lp["Qr"])
print(f"  E-201 (HP condenser / LP reboiler) {q_int:.1f} kW; LP steam trim {lp['Qr'] - q_int:.1f} kW; HP condenser to CW {hp['Qc'] - q_int:.1f} kW")
steam = Q_R + hp["Qr"] + lp["Qr"] - q_int
cw = Q_cond_r + lp["Qc"] + hp["Qc"] - q_int + Q_prod + Q_ww
print(f"utilities: steam {steam:.1f} kW = {steam * 3.6 / PRODUCT_KG_H:.4f} MJ/kg THF; CW {cw:.1f} kW; power {W_pump1 + W_pump2:.2f} kW")
# overall energy balance (liquid formation enthalpy basis): in + steam + power = out + CW
h_ww = h_bin(X_THF_WW, T_COND, P_LP, "l")
h_prod = h_bin(x_p, T_COND, P_HP, "l")
E_in = H_in / 3600.0 + steam + W_pump1 + W_pump2
E_out = (n_ww * h_ww + n_p * h_prod + H_bleed) / 3600.0 + cw
print(f"energy closure: in {E_in:.1f} kW, out {E_out:.1f} kW, difference {E_in - E_out:.1f} kW ({(E_in - E_out) / steam * 100:.2f} % of steam)")


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


# the values process/flowsheet.yaml cites from this script (balance-output contract), by the
# flowsheet's stream ids (its S6 is the condensate printed as "S5" above); binary THF/water
# streams as mass flow and mass fractions, temperatures at the columns' bubble points
def _binary(n, x):
    return {"flow": {"value": kg(n, x), "basis": "mass"},
            "composition": {"values": {"THF": wfrac(x), "H2O": 1 - wfrac(x)},
                            "basis": "mass_fraction"}}


FLOWSHEET = {
    "S1": {"flow": {"value": bdo_feed, "basis": "mass"}},
    "S2": {"flow": {"value": ptsa, "basis": "mass"}},
    "S6": _binary(n_oh, x_oh),
    "S7": {"flow": {"value": m_bleed, "basis": "mass"}},
    "S8": {**_binary(n_rec, xd_hp), "temperature": hp["Td"]},
    "S10": {**_binary(n_d1, xd_lp), "temperature": lp["Td"]},
    "S12": {**_binary(lp["B"], X_THF_WW), "temperature": lp["Tb"]},
    "S14": {**_binary(n_p, x_p), "temperature": hp["Tb"]},
    "Q1": {"duty": W_pump1}, "Q2": {"duty": W_pump2}, "Q3": {"duty": Q_R},
    "Q4": {"duty": Q_cond_r}, "Q5": {"duty": lp["Qr"] - q_int}, "Q6": {"duty": q_int},
    "Q7": {"duty": lp["Qc"]}, "Q8": {"duty": hp["Qr"]}, "Q9": {"duty": Q_prod},
    "Q10": {"duty": Q_ww},
}
write_balance_output({"design": FLOWSHEET})
