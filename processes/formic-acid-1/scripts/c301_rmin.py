"""Minimum reflux of C-301 (water / formic acid at 203 kPa(a)), DESIGN.md D-011, review R-01.

Shortcut, ASSUMED model: pure-component vapour pressures from thermo (ideal vapour, the
association of formic acid vapour not modelled), liquid activity from a one-parameter
(symmetric) Margules equation whose parameter is fitted so that the maximum-boiling azeotrope
lies at 80 wt% formic acid at 203 kPa(a) (SRC-3, D-009). The minimum reflux of the binary is
the largest (xD - y)/(y - x) over the equilibrium curve between the feed and the distillate
(feed pinch or tangent pinch; saturated liquid feed, q = 1).

Run: cheme run scripts/c301_rmin.py
"""

import math

from thermo import Chemical

P = 203e3                      # Pa, C-301 top (D-009)
W_AZ = 0.80                    # formic acid mass fraction of the azeotrope at 203 kPa(a) (SRC-3)
W_FEED, W_TOP, W_BOT = 0.489, 0.005, 0.77   # S25, S26 and S27 formic acid mass fractions (D-009)
MW_W, MW_F = 18.015, 46.025

water, acid = Chemical("water"), Chemical("formic acid")


def psat(chem, t):
    return chem.VaporPressure(t)


def xw(w_fa):
    """Water mole fraction of a water / formic acid liquid of formic acid mass fraction w_fa."""
    nw, nf = (1 - w_fa) / MW_W, w_fa / MW_F
    return nw / (nw + nf)


def bubble(x, a):
    """Bubble temperature (K) and vapour water fraction at P for liquid water fraction x."""
    lo, hi = 330.0, 450.0
    for _ in range(80):
        t = (lo + hi) / 2
        gw, gf = math.exp(a * (1 - x) ** 2), math.exp(a * x ** 2)
        p = x * gw * psat(water, t) + (1 - x) * gf * psat(acid, t)
        lo, hi = (t, hi) if p < P else (lo, t)
    return t, x * gw * psat(water, t) / P


def fit_margules(x_az):
    """Margules A (negative, maximum-boiling) placing the azeotrope at x_az: y = x there."""
    lo, hi = -5.0, -0.01
    for _ in range(80):
        a = (lo + hi) / 2
        _, y = bubble(x_az, a)
        # y > x at the azeotrope's composition means the azeotrope lies at lower water content,
        # i.e. the attraction (|A|) is too weak
        lo, hi = (lo, a) if y > x_az else (a, hi)
    return a


x_az, x_f, x_d = xw(W_AZ), xw(W_FEED), xw(W_TOP)
A = fit_margules(x_az)
t_az, _ = bubble(x_az, A)
print(f"azeotrope x_water {x_az:.4f} at {t_az - 273.15:.1f} C; Margules A {A:.3f}")

r_min, x_pinch = -1.0, None
n = 400
for i in range(n + 1):
    x = x_f + (x_d - x_f) * i / n
    _, y = bubble(x, A)
    if y <= x:
        raise SystemExit(f"no separation at x_water {x:.4f}: y {y:.4f}")
    r = (x_d - y) / (y - x)
    if r > r_min:
        r_min, x_pinch = r, x
t_f, y_f = bubble(x_f, A)
alpha_f = (y_f / x_f) / ((1 - y_f) / (1 - x_f))
print(f"feed x_water {x_f:.4f}, y {y_f:.4f}, alpha {alpha_f:.3f} at {t_f - 273.15:.1f} C; distillate x_water {x_d:.4f}")
print(f"rectifying section: R_min {r_min:.3f} (pinch at x_water {x_pinch:.4f})")

# stripping section: the operating line through (xB, xB) with slope L'/V' must stay under the
# equilibrium curve between the bottoms and the feed; with q = 1, V' = (R + 1) D, L' = R D + F
x_b = xw(W_BOT)
f_d = (x_d - x_b) / (x_f - x_b)          # F / D from the component balance
s_max = min((bubble(x, A)[1] - x_b) / (x - x_b)
            for x in (x_b + (x_f - x_b) * i / n for i in range(1, n + 1)))
r_min_s = (f_d - s_max) / (s_max - 1)
print(f"stripping section: bottoms x_water {x_b:.4f}, F/D {f_d:.3f}, L'/V' max {s_max:.4f}, R_min {r_min_s:.3f}")
r_min = max(r_min, r_min_s)
print(f"R_min {r_min:.3f}; 1.2 R_min {1.2 * r_min:.3f}")
