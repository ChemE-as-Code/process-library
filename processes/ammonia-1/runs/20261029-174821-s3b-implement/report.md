S3b is done: four new P&ID sheets for the mid section are committed on `stage/basic-pids-mid`, and the section's five gates pass (pids-exist, pids-valid, drawing-clean, process-basic, process-links). `cheme validate` reports 0 errors, every sheet is drawing-clean, and I rendered and looked at all four.

| sheet | what it shows |
|---|---|
| P-105 | CO2 absorber C-301, lean solvent pumps P-301A/B and cooler E-302; rich solvent leaves on level control, with a trip valve that closes on low-low level (gas blow-by) |
| P-106 | CO2 regenerator C-302, lean/rich exchanger E-301, overhead condenser E-303, reflux drum V-302 and pumps P-302A/B, CO2 vent on pressure control, make-up water, relief valve PSV-1513 |
| P-107 | Methanator feed heater E-401 with a hot bypass (LT shift inlet temperature), methanator R-401 with a high-high temperature trip, cooler E-402, knock-out drum V-401, dryer package X-401 |
| P-108 | Synthesis gas compressor K-501 with the recovered-hydrogen junction, anti-surge recycle and discharge relief valve PSV-1704 |

- **Equipment I added:** the flowsheet lumps the whole solvent loop into one step, so the eight loop items above (E-301, E-302, E-303, V-302 and the two pump pairs) were not in the equipment list. I added them and placed them on the plot plan. Their sizes and positions are ASSUMED; no duties are calculated.
- **Lists:**
  - The eight items already in the equipment list now have their sheet.
  - 37 new lines, 33 instruments and 2 relief valves (set pressures left open for S8).
  - Two proposed trips in the cause-and-effect list: I-105 (absorber low-low level) and I-106 (methanator high-high temperature).
  - 13 flowsheet streams are linked to their lines, and the BFD/PFD are rebuilt.
- **Changes to S3a's sheets:**
  - The lean solvent line AM-1051 from the E-202 reboiler now goes to E-301 instead of the C-302 sump.
  - The off-page texts on P-103 and P-104 now name the new sheets, so connectors read the same from both sides.
- **No new external data:** stream values come from the simulated flowsheet. The solvent line sizes come from D-009's ASSUMED 18 m³ of solvent per t of CO2. The regenerator overhead and reflux sizes, the cooling-water basis and the bypass, anti-surge and relief line sizes are also ASSUMED. Each assumption is recorded in DESIGN.md D-028 and the line list.
- **Side effects outside this section:**
  - Routing the new lines in the 3D model doubled the layout warnings (110 to 218; pipe clashes 38 to 70). That is S5's layout work.
  - The gates that failed before (design-review, the layout gates, mto, maturity-balanced and the detail gates) still fail for the same reasons.
  - `cheme maturity` stays at none, for reasons this section does not touch.
- **Not drawn yet:**
  - a rich solvent flash drum (the flowsheet has no co-absorption model);
  - pump minimum-flow lines, control-valve block and bypass valves, vents and drains;
  - the dryer regeneration circuit and the K-501 auxiliaries;
  - further relief valves, which depend on design pressures not set yet.

  The methanator inlet temperature has no independent control loop yet (S4), and the recycle circulator K-502 is left to S3c.

The PR description is in `build/pr-body.md` and the working tree is clean. A merge is pending: the orchestrator pushes the branch and an independent reviewer merges it.

STATUS: DONE