---
topic: datasheets
reviewed_commit: aede0049709922c068e0142ead8cd308023882d3
scope: [equipment/datasheets, equipment/equipment-list.yaml, scripts/complete_datasheets.py, DESIGN.md, PROGRESS.md]
reviewer: review-agent
reviewer_kind: agent
branch: stage/detail-datasheets
merge: pending
---

# Review: S7 equipment datasheets (PR #260, round 1)

This is an independent review of `stage/detail-datasheets` at `aede004`, against `origin/main`.
The section's target (runs/plan.md, S7): a datasheet for every equipment-list item, sized from the
simulation with core's tools, provenance on every value; gate `datasheets`.

## What changed

`cheme diff origin/main --list`:

```
No P&ID changed.
```

`git diff --stat origin/main...HEAD` lists 112 files:
- 52 `equipment/datasheets/<TAG>.yaml` with their `<TAG>.svg` outline drawings;
- `equipment/equipment-list.yaml`: design pressure, design temperature and material class added per item;
- `scripts/complete_datasheets.py` (new, 708 lines);
- DESIGN.md D-032 and the source register;
- PROGRESS.md;
- `layout/plant-model.yaml` (fingerprint only);
- the run record.

## Checks re-run by the reviewer

| command | result |
|---|---|
| `cheme validate` | 101 files, 0 errors, 251 warnings. The 12 `cheme.datasheet-*` warnings are all `datasheet-dimension-layout` on the convection coils (see #6). |
| `cheme check` | `[detail] datasheets` **ok**. Concept: all ok. Basic: design-review, layout-3d, lifting-study, mto, maturity-balanced and layout-review fail, as before this branch. Detail: layout-detail and electrical fail (S9). |
| `checks/checks.yaml` | unchanged on the branch. The `datasheets` gate is the template gate, with its `require:` list still commented. No gate was relaxed. |
| `cheme maturity` | calculation maturity none, the same failures as on main (carried as simulation#1). `engineering.consistency` is unsupported by the command. |
| `cheme datasheets fill --dry-run` | every sheet `kept (not a draft)`. Nothing is left for the fill. |

## Spot checks

**Cited values:**
- NH3 vapour pressure at 313.15 K: 1554.5 kPa(a) (thermo, re-run). It matches the sheets and D-032.
- MP steam saturation at 4600 kPa(a): 531.93 K (thermo, re-run). It matches E-502 and D-032.
- The design-margin rule ("10 % or 10-25 psi, whichever is greater"; +50 degF) agrees with the Walas rules of thumb as generally quoted.
- The Sinnott Table 12.1 flue gases/steam row is 30-100 W/(m2 K), as written.

**Calculations re-done by hand:**
- E-501: LMTD 34.86 K (38.76 / 31.24 K ends) and area 44,5xx m2 at U 30 W/(m2 K) are both reproduced.
- E-502: LMTD 30.77 K (171.2 / 0.67 K ends) is reproduced.
- P-801: 5500 kPa / (992 kg/m3 x g) = 565 m; 157.7 m3/h x 5500 kPa / 0.70 = 344 kW. Both are reproduced.
- K-101: 4 intercooled stages from 313 K, ratio 2.44 per stage, k 1.4, efficiency 0.78. This gives 430 K, against 429.7 K on the sheet.
- V-701: pi/4 x 3^2 x 5.3 = 37.5 m3 is reproduced.
- P-301 flow: 18 m3/t x 72.95 t/h = 1313 m3/h is reproduced.
- E-501 and E-502 duties are about 81.7 kg/s x 3 kJ/(kg K) x dT, which is plausible against the simulated 46.6 and 43.2 MW.

**Provenance:**
- Every size field I opened names its source: stream, run-record unit, decision or table.
- Assumptions carry `assumed: true`.
- Open fields are `supplier` with what is awaited. None hides a value the fill could calculate (R-201 bed, P-301 head, P-302 power were checked).

**Licences:** nothing third-party was copied. The sheets use short factual rules and table ranges, with citations.

## Findings

| id | file:line | finding | severity | status | fix |
|---|---|---|---|---|---|
| 2026-10-30-datasheets#1 | equipment/datasheets/E-501.yaml:169, E-502.yaml:130 (also E-504, E-505 and the other gas services above 10 barg) | The areas of the high-pressure gas exchangers use Table 12.1 rows that are meant for gases near atmospheric pressure (gases/gases 10-50, flue gases/steam 30-100 W/(m2 K)). In a 150 bar loop the gas film coefficients are several times higher. E-501 at 44,544 m2 and E-502 at 21,610 m2 are an order of magnitude above what a converter feed/effluent exchanger or a waste heat boiler of this duty usually needs. The sheets and D-032 call these upper bounds, so the disclosure is honest. Still, the sheets are now final and an estimate (`cheme assess equipment`, S9/mto) will read the areas. | medium | open | Give these items a sourced high-pressure coefficient through `--param overall_u_w_m2k` with its source. Otherwise, add a sheet-level `estimate_basis`/note that an estimate must not take the area, and keep `area_m2` out of the estimate until a rating exists. Record the choice in D-032. |
| 2026-10-30-datasheets#2 | DESIGN.md:895; equipment/datasheets/E-502.yaml:130 | The E-502 process outlet (532.6 K) is 0.67 K above the MP steam saturation temperature (531.93 K). That is not a feasible boiler design point, and it makes E-502's area (and E-501's inlet) meaningless. It comes from the D-026 retune (S4), not from this section, which surfaced it correctly. No issue or open input tracks it, so it rests on a DESIGN.md sentence. | medium | open | Open it as an issue in `plant.yaml` `issues:` or as an I-xx input, owned by the flowsheet: for example an outlet limit of about 10-15 K above saturation, a lower steam level, or BFW preheat at the cold end. Re-size E-502 and E-501 once it is resolved. |
| 2026-10-30-datasheets#3 | DESIGN.md:907; all 52 datasheets (no `draft: true`) | The sheets were made final so that the gate counts them. Skill step 9 allows a sheet whose only open fields are `supplier` markers to be final. However, the skill's "Required human judgment" section says a filled datasheet "is still a draft until an engineer has checked its values". No engineer has checked them, and #1 and #2 show values an engineer would not pass. This is disclosed in the header, D-032 and the PR, so it is not hidden, and the detail sign-off needs a human anyway. Making the sheets final also stops `cheme datasheets fill` from refreshing them after a flowsheet change: every sheet is "kept". | medium | open | Before the detail sign-off, a human approver checks the datasheets (at least the exchanger areas, design conditions and material classes) and records it in this record or the sign-off review. Until then, D-032 should state that a flowsheet change requires `scripts/complete_datasheets.py` to be rerun, not the fill alone. |
| 2026-10-30-datasheets#4 | equipment/datasheets/E-502.yaml:242 (also equipment-list.yaml:59 and other loop items) | The datasheet notes copy the list's pre-simulation values. E-502's note says "703 -> 547 K, 39.8 MW", while the same sheet carries the simulated outlet of 532.6 K and 43.2 MW. The sheet contradicts itself. This is the datasheet form of pids-loop#3. | low | open | Drop the duty and temperatures from the datasheet notes, or point them at the stream and energy ids. Fix the list notes with pids-loop#3. |
| 2026-10-30-datasheets#5 | equipment/datasheets/R-201.yaml:158, R-501.yaml:166 | `duty_kw` on adiabatic beds holds the fill's ideal-gas residual: R-201 8 kW, R-501 454 kW. The simulation gives 237 and 31 kW. A reader or an estimate can take 454 kW as a cooling duty. | low | open | Say in the field's source or the notes that this is a residual of an adiabatic bed and no utility duty, or mark the field `not_applicable` with that reason if the schema allows. |
| 2026-10-30-datasheets#6 | equipment/datasheets/E-101.yaml:112 (E-101 to E-104, E-106, E-107) | The branch adds 12 `cheme.datasheet-dimension-layout` warnings: the coil banks are 4 x 14 m in the list and 14 x 4 m in the layout model. They were left as an S5 question, but no open record carries them. | low | open | Align the list's length and width with the placement rotation, or the rotation with the list. Rebuild the layout model. |
| 2026-10-30-datasheets#7 | equipment/equipment-list.yaml:13-64 | The new design pressure, design temperature and material values are marked ASSUMED only in the file's header comment, not on each entry. AGENTS.md asks for assumed values to be marked in the YAML. | low | open | Add "Design conditions and material ASSUMED (D-032)." to each entry's notes, or keep the header and point each entry at D-032. |
| 2026-10-30-datasheets#8 | scripts/complete_datasheets.py | AGENTS.md says repository files are changed with Edit/Write only. The 52 datasheets and the list columns were written by a script run under `cheme run`. The exception is disclosed and the script is committed, deterministic and reviewable, so this is a process note. | low | open | Record the exception in DESIGN.md D-032 as a decision (the PR body alone is not the design record), or ask the plan owner to allow committed generator scripts for datasheets. |

## Previous findings

None of these is addressed by this section; they are carried unchanged.

| id | finding | severity | status | evidence |
|---|---|---|---|---|
| 2026-10-30-hazop-r2#1 | tube rupture of E-302 (solvent vs CW) and E-105/E-201 (steam vs process side) missing from the HAZOP | medium | open | safety/ unchanged on this branch. The new datasheets now give E-105 a design pressure of 36.5 barg on the process side and 49.5 barg on the steam side. That ratio of 1.36 is above the usual 10/13 criterion, so a tube rupture is a credible relief case for S8. |
| 2026-10-29-pids-loop#1 | E-502 riser SM-1101 smaller than downcomer BW-1100 | medium | open | line list unchanged |
| 2026-10-29-pids-loop#2 | tube-rupture cases of E-504, E-503, E-701, E-502 | medium | open | P&IDs unchanged; datasheets give `relief_protection: supplier` (S8) |
| 2026-10-29-pids-loop#3 | list notes carry pre-simulation values | low | open | notes unchanged; header now points at the datasheets; see #4 |
| 2026-10-29-pids-loop#4 | PSV-2210 silencer not drawn or listed | low | open | unchanged |
| 2026-10-29-control-lists#1 | start permissives require resetting trips whose causes are still present | medium | open | unchanged |
| 2026-10-29-control-lists#2 | no front-end pressure / K-501 capacity control; no front-end vent | medium | open | unchanged |
| 2026-10-29-pids-front#1 | SM-1038/SM-1040 risers smaller than downcomers | medium | open | unchanged |
| 2026-10-29-pids-front#2 | I-101 does not close tail-gas XV-1105 | medium | open | unchanged |
| 2026-10-29-pids-front#3 | I-104 uses LV-1307 as trip element | medium | open | unchanged |
| 2026-10-29-pids-front#4 | CW velocity basis as written vs used | low | open | unchanged |
| 2026-10-29-pids-front#5 | FV-1108 carries PZ-1108's loop number | low | open | unchanged |
| 2026-10-29-pids-front#6 | E-203/E-105 notes give concept duties | low | open | unchanged |
| 2026-10-29-simulation#1 | maturity-balanced fails on model-basis | medium | open | `cheme maturity` unchanged |
| 2026-10-29-simulation#2 | D-026 maturity list omits energy closure | low | open | unchanged |
| 2026-10-29-simulation#3 | R102B/R201/R202 bed residual duties | low | open | unchanged; see #5 |
| 2026-10-29-simulation#4 | steam, refrigeration, furnace stay script packages (no adjust) | low | open | unchanged; E-107 left unsized for the same reason (D-032) |
| 2026-10-29-concept#1 | X-601 32 m from A-900 without separation criterion | medium | open | layout unchanged |
| 2026-10-29-concept#2 | TEA: DMW, BD, CW free without `free:` | low | open | unchanged |
| 2026-10-29-concept#3 | steam credit omits avoided carbon cost | low | open | unchanged |
| 2026-10-29-concept#4 | ETS price from a secondary source | low | open | unchanged |
| 2026-10-27-pfd-lci-review#3 | natural-gas composition and pressure not sourced | medium | open | unchanged |
| 2026-10-27-pfd-lci-review#5 | block reaction extents not unique | low | open | unchanged |

## Verdict

**Approved.** No critical or high finding is open. The `datasheets` gate passes on the template
definition, and no gate was relaxed. Every equipment-list item has a datasheet, sized from the
simulated case where core or the same method applied in the committed script allows it. Every
value has its provenance, and every open field names what is awaited.

The medium findings concern credibility, not completeness:
- the high-pressure gas exchanger areas (#1);
- the E-502 pinch inherited from S4 (#2);
- the agent-checked "final" status (#3).

All three are disclosed by the author and can be closed in a follow-up or before the detail
sign-off. Merge: by the reviewer after CI; `merge` stays `pending` in this record.
