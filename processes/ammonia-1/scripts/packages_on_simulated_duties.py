"""The energy-only packages of ammonia-1 on the simulated duties (DESIGN.md D-026).

Since core v1.0.1 the whole process side is simulated (`cheme process simulate`, D-024, D-026).
Two packages stay energy balances that DWSIM through core cannot set (a flow from a duty needs an
adjust): the closed refrigeration circuit of the chillers (K701, D-017) and the steam system
(U801, D-015). This script evaluates both with the concept balance's own models
(scripts/plant_balance.py: 0.55 of Carnot, IAPWS-IF97) on the `calculated` duties and flows that
`cheme process simulate --fill` wrote to process/flowsheet.yaml, and prints the values the
flowsheet gives these packages as ASSUMED with this script as their source:

- K701: compressor power Q27 and condenser duty Q28 from the chiller E-504 (Q25, evaporating at
  258.15 K) and the duties served at the product level, 238.15 K (the product flash Q26, the
  receiver vent chiller Q34 and the recovered NH3 chiller Q30; the vent chiller's 258 K outlet
  is put on the colder level, which is conservative);
- X601: LP steam Q29 at 3 MJ/kg of recovered NH3 (S58, D-013);
- U801: MP steam raised from the boiler duties Q8, Q10, Q13, Q23, the export S68 after the
  process steam S6 and the LP let-down, blowdown S69, demineralised water S70 after the
  returned condensates (S25, S33, S35 less their dissolved gases), BFW pump power Q31, and the
  stripper vent S87 (the gases dissolved in the condensates).

Run with `cheme run scripts/packages_on_simulated_duties.py`; it writes nothing (with
`BALANCE_OUTPUT` set, the values above as JSON for the library's balance check).
"""

import sys
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))
import plant_balance as pb  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
FS = yaml.safe_load((ROOT / "process/flowsheet.yaml").read_text())
ST = {s["id"]: s["state"]["design"] for s in FS["streams"] if "state" in s}


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


def duty(sid):
    return abs(ST[sid]["duty"]["value"])


def kmol(sid):
    st = ST[sid]
    x = st["composition"]["values"]
    mw = sum(v * pb.MW[c] for c, v in x.items())
    n = st["flow"]["value"] / mw
    return {c: v * n for c, v in x.items() if v > 0}


# ---- refrigeration package K701 (D-017)
cop_ch = pb.REF_ETA * pb.T_EVAP_CH / (pb.T_COND - pb.T_EVAP_CH)
cop_pr = pb.REF_ETA * pb.T_EVAP_PR / (pb.T_COND - pb.T_EVAP_PR)
q_ch = duty("Q25")
q_pr = duty("Q26") + duty("Q34") + duty("Q30")
w_ref = q_ch / cop_ch + q_pr / cop_pr
q_cond = q_ch + q_pr + w_ref
print(f"K701: chiller {q_ch:.1f} kW (COP {cop_ch:.4f}), product level {q_pr:.1f} kW (COP {cop_pr:.4f})")
print(f"Q27 K-701 power {w_ref:.1f} kW; Q28 E-701 condenser {q_cond:.1f} kW")

# ---- purge recovery LP steam (D-013)
q_hru = pb.HRU_MJ_KG * ST["S58"]["flow"]["value"] / 3.6
print(f"Q29 LP steam to X-601 {q_hru:.1f} kW")

# ---- steam system U801 (D-015)
hv = pb.h_vap(pb.T_STEAM, pb.P_STEAM)
hfw = pb.h_liq(pb.T_FW, pb.P_STEAM + 1000)
hbd = pb.h_liq(531.0, pb.P_STEAM)
q_in = duty("Q8") + duty("Q10") + duty("Q13") + duty("Q23")
m_raised = q_in * 3600 / ((hv - hfw) + pb.BLOWDOWN * (hbd - hfw))
m_bd = pb.BLOWDOWN * m_raised
m_lp = q_hru * 3600 / (hv - hfw)   # no LP steam to the regenerator: E-202 supplies all of it (D-009)
m_proc = ST["S6"]["flow"]["value"]
m_export = m_raised - m_proc - m_lp
gas, water = {}, 0.0
for sid in ("S25", "S33", "S35"):
    for c, v in kmol(sid).items():
        if c == "H2O":
            water += v * pb.MW["H2O"]
        else:
            gas[c] = gas.get(c, 0.0) + v
m_dmw = m_proc + m_export + m_bd - water
w_bfw = (m_raised + m_bd) / 3600 * (pb.P_STEAM + 1000 - pb.P_AMB) / 1000 / pb.ETA_P
print(f"boiler duties {q_in:.1f} kW: MP steam raised {m_raised:.1f} kg/h, process {m_proc:.1f}, LP let-down {m_lp:.1f}")
print(f"S68 export {m_export:.1f} kg/h; S69 blowdown {m_bd:.1f} kg/h; S70 DMW {m_dmw:.1f} kg/h; Q31 BFW pumps {w_bfw:.1f} kW")
n = sum(gas.values())
m = sum(v * pb.MW[c] for c, v in gas.items())
print(f"S87 stripper vent {m:.2f} kg/h " + str({c: round(v / n, 7) for c, v in gas.items()}))
print(f"condensate water returned {water:.1f} kg/h")

# the values process/flowsheet.yaml cites from this script (balance-output contract)
write_balance_output({"design": {"S68": {"flow": m_export}, "S69": {"flow": m_bd},
                                 "Q27": {"duty": w_ref}, "Q28": {"duty": q_cond},
                                 "Q29": {"duty": q_hru}, "Q31": {"duty": w_bfw}}})
