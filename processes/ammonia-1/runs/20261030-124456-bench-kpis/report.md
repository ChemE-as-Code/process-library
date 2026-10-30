I've computed all ten KPIs from the design's own files and committed them to `bench/ammonia-1-kpis` as `cd7b04f`. That commit adds `runs/benchmark-kpis.md` and `scripts/benchmark_kpis.py`, which reproduces every number with `cheme run`. The LCI dataset check showed it was already current, so I didn't regenerate it.

| # | KPI | value | dataset expression (per `product:NH3`) |
|---|---|---|---|
| 1 | specific-energy-net | 26.97 GJ/t LHV | `(feed:NG * 49.0858 + feed:POWER * 3.6 - product:STEAM * 3.0985) / product:NH3` |
| 2 | specific-energy-gross | 30.13 GJ/t LHV | `(feed:NG * 49.0858 + feed:POWER * 3.6) / product:NH3` |
| 3 | natural-gas-feed-plus-fuel | 28.01 GJ/t LHV (feed 21.78, fuel 6.23) | `feed:NG * 49.0858 / product:NH3` |
| 4 | process-co2 | 1.164 t/t | `product:CO2V * 0.978874105 / product:NH3` |
| 5 | direct-co2-total | 1.558 t/t | `emission:CO2 / product:NH3` |
| 6 | steam-net-export | +3.16 GJ/t | `product:STEAM * 3.0985 / product:NH3` |
| 7 | synthesis-loop-pressure | 154.0 bar absolute (152.99 bar gauge), converter inlet S42 | no exchange |
| 8 | synthesis-conversion-per-pass | 30.2 % on H2+N2 (25.5 % on total gas) | no exchange |
| 9 | nox-concentration-reformer | not determined by the design | no exchange |
| 10 | nox-emission-factor | not determined by the design | no exchange |

**Conventions I chose** (all stated in the report):
- **Heating value:** lower heating value at 25 °C, from the formation enthalpies in `materials.yaml`. That gives 49.086 MJ/kg for the natural gas.
- **Electricity:** counted 1:1 at 3.6 GJ/MWh, with no power-plant factor. The design doesn't determine one.
- **Steam:** credited at its enthalpy above the make-up water, 3.0985 MJ/kg. If it were credited at its exergy instead (the D-021 value), the net energy would be 28.84 GJ/t.

**NOx (KPIs 9 and 10):** the design gives no value. The furnace is modelled with complete combustion, there is no NOx component, and no emission factor was chosen (D-014, open input I-07). The furnace is the only combustion source. The report gives the dry flue-gas flow and its O2 content, so a factor can be applied later.

**Blindness:** while searching the design files for "LHV", I saw one line in DESIGN.md (D-034) that quotes a published range as a check on the design. I didn't use it; every value comes from the streams.

**PROGRESS.md:** I left it unchanged, which departs from the AGENTS.md rule. My entry made the signed-off `design-review` and `layout-review` gates fail, because PROGRESS.md is in those reviews' scope. I removed the entry; this job's record is the report and the commit message.

**Checks:**
- `cheme validate`: 0 errors, 268 warnings.
- `cheme check`: every concept and basic gate passes. The detail gates `electrical` and `datasheets` fail; they also fail on `main` and this job doesn't touch them.
- `cheme maturity`: calculation maturity is balanced, and the evidence supports screening design maturity.

The PR description is in `build/pr-body.md`. Nothing is pushed, and the merge is pending a reviewer.

STATUS: DONE