"""First-pass line sizes of the PFD streams (DESIGN.md D-014). Prints, writes nothing.

Run: cheme run scripts/line_sizes.py

For each material stream of process/flowsheet.yaml (design case, the simulated values): a
thermo Peng-Robinson flash (ChemSep kij, as scripts/cumene_balance.py) at its temperature and
pressure gives the phase and bulk density; the velocity rule (ASSUMED, the hda-1 rule): liquid
1.5 m/s (0.6 m/s on pump suctions below 200 kPa(a)), two-phase 10 m/s, vapour 15 m/s above
1000 kPa(a) else 20 m/s; column products are taken as saturated liquid at their pressure
(DWSIM's and thermo's bubble points differ slightly, and thermo knows the real TIPB where DWSIM
has a surrogate); inside diameter taken as the DN, DN25 the smallest. Unqualified
property method (D-007); a concept size, not a hydraulic design.
"""
import math
from pathlib import Path

import yaml
from thermo import CEOSGas, CEOSLiquid, ChemicalConstantsPackage, FlashVL, PRMIX
from thermo.interaction_parameters import IPDB

ROOT = Path(__file__).resolve().parents[1]
C = ["C3H8", "C3H6", "BZ", "CUM", "DIPB", "TIPB"]
CAS = ["74-98-6", "115-07-1", "71-43-2", "98-82-8", "100-18-5", "717-74-8"]
consts, props = ChemicalConstantsPackage.from_IDs(CAS)
kijs = IPDB.get_ip_asymmetric_matrix("ChemSep PR", consts.CASs, "kij")
EOS = dict(Tcs=consts.Tcs, Pcs=consts.Pcs, omegas=consts.omegas, kijs=kijs)
FL = FlashVL(consts, props, liquid=CEOSLiquid(PRMIX, EOS, HeatCapacityGases=props.HeatCapacityGases),
             gas=CEOSGas(PRMIX, EOS, HeatCapacityGases=props.HeatCapacityGases))
DNS = [25, 40, 50, 65, 80, 100, 125, 150, 200, 250, 300, 350, 400, 450, 500, 600, 700, 800]
SUCTION = {"S3", "S13"}
SATURATED = {"S2", "S13", "S20", "S21", "S23", "S24", "S26", "S27"}

fs = yaml.safe_load((ROOT / "process/flowsheet.yaml").read_text())
for s in fs["streams"]:
    if s.get("kind") == "energy":
        continue
    st = s["state"]["design"]
    flow = st.get("flow", {}).get("value")
    if not flow:
        print(f"{s['id']}: no flow")
        continue
    z = st["composition"]["values"]
    zs = [max(z.get(c, 0.0), 0.0) for c in C]
    t = sum(zs)
    if s["id"] in SATURATED:  # column products: saturated liquid at the column pressure
        res = FL.flash(zs=[v / t for v in zs], VF=0.0, P=st["pressure"]["value"] * 1e3)
    else:
        res = FL.flash(zs=[v / t for v in zs], T=st["temperature"]["value"], P=st["pressure"]["value"] * 1e3)
    vf, rho = res.VF, res.rho_mass()
    p = st["pressure"]["value"]
    if vf < 1e-6 or s["id"] in SATURATED:
        u = 0.6 if s["id"] in SUCTION else 1.5
    elif vf < 1 - 1e-6:
        u = 10.0
    else:
        u = 15.0 if p > 1000 else 20.0
    d = 1000 * math.sqrt(4 * flow / 3600 / rho / u / math.pi)
    dn = next(x for x in DNS if x >= d)
    print(f"{s['id']}: VF {vf:.3f}, rho {rho:.1f} kg/m3, u {u} m/s, d {d:.0f} mm -> DN{dn}")
