"""Relief loads of the eight drawn relief valves of ammonia-1 (S8, DESIGN.md D-033).

Run with `cheme run scripts/relief_loads.py`. Prints the relieving rate of every relief case
that can be calculated from the repository (design case of process/flowsheet.yaml, the
equipment list, the placement) and says why the others cannot. Writes nothing: the numbers
are copied, with this script as their source, into safety/relief/relief-study.md.

Methods (each a published equation used in our own form; ASSUMED inputs marked):
- set pressure = design pressure of the protected item (equipment/equipment-list.yaml, D-032),
  MAWP awaited from the vessel design (ASSUMED);
- relieving pressure = set + 10 % accumulation (single valve, process cases) or + 21 %
  (fire case), as ASME VIII / API 520 Part I state them;
- external pool fire on a wetted wall: Q = C F A^0.82 [W], A in m2, C = 43 200 with adequate
  drainage and fire fighting, 70 900 without (API Std 521, 6th ed., 4.4.13.2.4, SI form);
  wetted area counted up to 7.6 m above grade; F = 1 (bare vessel, no insulation credit);
- relieving rate of a boiling liquid = Q / latent heat at the relieving pressure (thermo 0.6.1,
  pure water or pure ammonia as the boiling component, ASSUMED);
- gas through an opening (tube rupture): choked ideal-gas orifice flow, discharge coefficient 1;
  a double-ended rupture of one tube gives two tube bores (API Std 521, 4.4.14);
- gas blow-by through a fully open liquid control valve: IEC 60534-2-1 compressible flow,
  W = N6 Kv Y sqrt(x p1 rho1), N6 = 27.3 (kg/h, bar, kg/m3), choked at x = F_gamma xT,
  Y = 2/3; xT = 0.7 ASSUMED (globe valve, no valve selected).
"""

import math
from pathlib import Path

import yaml
from thermo import Chemical

ROOT = Path(".")
FS = yaml.safe_load((ROOT / "process" / "flowsheet.yaml").read_text())
MAT = yaml.safe_load((ROOT / "process" / "materials.yaml").read_text())
EQ = {e["tag"]: e for e in yaml.safe_load((ROOT / "equipment" / "equipment-list.yaml").read_text())["equipment"]}
STREAMS = {s["id"]: s for s in FS["streams"]}
MW = {c["id"]: c["molar_mass"] for c in MAT["components"]}
CAS = {c["id"]: c["cas"] for c in MAT["components"]}
R = 8.314462  # J/(mol K)
P_ATM = 1.01325  # bar
FIRE_HEIGHT = 7.6  # m above grade (API 521)
C_DRAINED, C_UNDRAINED = 43200.0, 70900.0  # W / m2^0.82
X_T = 0.7  # ASSUMED pressure differential ratio factor, globe valve
N6 = 27.3


def state(sid):
    return STREAMS[sid]["state"]["design"]


def val(sid, key):
    return state(sid)[key]["value"]


def gas(sid):
    """Molar mass (kg/kmol), ideal-gas k, ideal-gas density (kg/m3), p (bar), T (K) of a stream."""
    comp = state(sid)["composition"]["values"]
    t, p = val(sid, "temperature"), val(sid, "pressure") / 100.0
    mw = sum(x * MW[c] for c, x in comp.items())
    cp = sum(x * Chemical(CAS[c], T=t, P=1e5).Cpgm for c, x in comp.items() if x > 0)
    k = cp / (cp - R)
    rho = p * 1e5 * mw / 1000.0 / (R * t)
    return mw, k, rho, p, t


def choked_orifice(area_m2, sid):
    mw, k, _, p, t = gas(sid)
    crit = (2.0 / (k + 1.0)) ** ((k + 1.0) / (k - 1.0))
    return area_m2 * p * 1e5 * math.sqrt(k * mw / 1000.0 / (R * t) * crit) * 3600.0  # kg/h


def kv_blowby(sid):
    """kg/h of gas per unit Kv through a fully open valve, choked (IEC 60534-2-1)."""
    _, k, rho, p, _ = gas(sid)
    x = min(k / 1.40 * X_T, 1.0)
    return N6 * (2.0 / 3.0) * math.sqrt(x * p * rho)


def wetted_area(tag):
    d = EQ[tag]["dimensions"]
    dia = d["diameter"]
    head = 1.084 * dia**2  # 2:1 ellipsoidal head surface
    if "length" in d:  # horizontal drum at grade: whole surface below 7.6 m
        return math.pi * dia * d["length"] + 2 * head, "horizontal, whole shell below 7.6 m"
    h = min(d["height"], FIRE_HEIGHT)
    return math.pi * dia * h + head, f"vertical, bottom head and {h:.1f} m of shell above grade"


def fire(tag, component, set_barg):
    p1 = 1.21 * set_barg + P_ATM
    area, how = wetted_area(tag)
    q_d, q_u = C_DRAINED * area**0.82, C_UNDRAINED * area**0.82
    ch = Chemical(component, P=p1 * 1e5)
    if p1 * 1e5 >= ch.Pc:
        return (f"{tag} fire: A = {area:.1f} m2 ({how}), Q = {q_d / 1e6:.2f} / {q_u / 1e6:.2f} MW "
                f"(drained / undrained); relieving pressure {p1:.1f} bar(a) is above the critical "
                f"pressure of {component} ({ch.Pc / 1e5:.1f} bar): no latent heat, not sized here")
    tsat = ch.Tsat(p1 * 1e5)
    hv = Chemical(component, T=tsat - 0.01, P=p1 * 1e5).Hvap  # J/kg
    return (f"{tag} fire: A = {area:.1f} m2 ({how}), relieving {p1:.2f} bar(a), Tsat {tsat:.1f} K, "
            f"Hvap {hv / 1e3:.0f} kJ/kg ({component}); Q = {q_d / 1e6:.2f} MW drained -> "
            f"{q_d / hv * 3600:.0f} kg/h; Q = {q_u / 1e6:.2f} MW undrained -> {q_u / hv * 3600:.0f} kg/h")


def liquid_kv(m3h, sg, dp_bar, opening=0.7):
    """Kv of a liquid duty (non-flashing) and the full-open Kv at an ASSUMED opening of 70 %."""
    kv = m3h * math.sqrt(sg / dp_bar)
    return kv, kv / opening


def main():
    print("== Blocked outlet / blocked discharge (rated flow of the source, design case)")
    for psv, sid, what in [
        ("PSV-1212", "S13", "K-101 discharge, compressed process air"),
        ("PSV-1310", "S24", "front-end gas at the V-201 gas outlet"),
        ("PSV-1513", "S28", "regenerator CO2 at the vent (PV-1505 closed)"),
        ("PSV-1704", "S38", "K-501 make-up gas"),
        ("PSV-1912", "S53", "V-502 let-down gas (PV-1906 closed)"),
        ("PSV-2010", "S88", "V-701 flash gas (K-701 flash-gas stages stopped)"),
        ("PSV-2210", "S6", "MP process steam (FV-1006 closed)"),
        ("PSV-2210", "S68", "MP steam export (PV-2203 closed)"),
    ]:
        mw, k, rho, p, t = gas(sid)
        print(f"{psv}: {what}: {sid} {val(sid, 'flow'):.0f} kg/h, {p:.2f} bar(a), {t:.1f} K, "
              f"M {mw:.2f}, k {k:.3f}")

    print("\n== External fire (wetted wall, boiling liquid)")
    print(fire("V-201", "water", 33.0))
    print(fire("C-302", "water", 2.5))
    print(fire("V-501", "ammonia", 161.0))
    print(fire("V-502", "ammonia", 26.5))
    print(fire("V-701", "ammonia", 26.5))

    print("\n== Tube rupture, gas side into the low-pressure side (ratio of design pressures, barg)")
    di = (19.05 - 2 * 2.11) / 1000.0  # ASSUMED 19.05 mm OD, 2.11 mm wall (14 BWG), no tube layout yet
    area = 2 * math.pi / 4 * di**2
    for ex, sid, low, low_dp in [("E-202", "S21", "aMDEA side, C-302 (PSV-1513)", 2.5),
                                 ("E-502", "S43", "MP steam side, U-801 (PSV-2210)", 49.5)]:
        mw, k, rho, p, t = gas(sid)
        print(f"{ex} into the {low}: {sid} {p:.1f} bar(a), {t:.1f} K, M {mw:.2f}, k {k:.3f}; "
              f"low/high design pressure {low_dp} / {EQ[ex]['design_pressure_barg']} barg = "
              f"{low_dp / EQ[ex]['design_pressure_barg']:.2f}; tube ID {di * 1000:.2f} mm (ASSUMED), "
              f"two bores {area * 1e4:.2f} cm2: {choked_orifice(area, sid):.0f} kg/h")

    print("\n== Gas blow-by through a fully open level valve (kg/h per unit Kv; Kv not sized)")
    for psv, lv, sid in [("PSV-1513", "LV-1405", "S24"), ("PSV-1912", "LV-1903", "S49"),
                         ("PSV-2010", "LV-1907", "S53")]:
        mw, k, rho, p, t = gas(sid)
        print(f"{psv} / {lv}: gas {sid} {p:.1f} bar(a), {t:.1f} K, M {mw:.2f}, k {k:.3f}, "
              f"rho {rho:.1f} kg/m3: {kv_blowby(sid):.0f} kg/h per Kv")

    print("\n== Indicative full-open Kv from the normal liquid duty (non-flashing, 70 % open, ASSUMED)")
    # LV-1405: rich solvent, D-009 ratio 18 m3/t CO2 (ASSUMED), SG 1.04 ASSUMED, 3100 -> ~250 kPa(a)
    comp = state("S28")["composition"]["values"]
    w_co2 = comp["CO2"] * MW["CO2"] / sum(x * MW[c] for c, x in comp.items())
    m3h = 18.0 * val("S28", "flow") * w_co2 / 1000.0
    kv, kvmax = liquid_kv(m3h, 1.04, 31.0 - 2.5)
    print(f"LV-1405: {m3h:.0f} m3/h, Kv {kv:.0f}, full open {kvmax:.0f} -> blow-by "
          f"{kvmax * kv_blowby('S24'):.0f} kg/h")
    nh3 = Chemical("ammonia", T=val("S52", "temperature"), P=val("S52", "pressure") * 1e3)
    m3h = val("S52", "flow") / nh3.rho
    kv, kvmax = liquid_kv(m3h, nh3.rho / 1000.0, (val("S52", "pressure") - val("S99", "pressure")) / 100.0)
    print(f"LV-1903: {m3h:.0f} m3/h (rho {nh3.rho:.0f} kg/m3), Kv {kv:.1f}, full open {kvmax:.1f} -> "
          f"blow-by {kvmax * kv_blowby('S49'):.0f} kg/h")


if __name__ == "__main__":
    main()
