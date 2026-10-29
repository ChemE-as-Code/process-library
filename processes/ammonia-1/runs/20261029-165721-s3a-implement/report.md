I've drawn the front end as four P&ID sheets, and all five gates for this section pass: pids-exist, pids-valid, drawing-clean, process-basic and process-links. Everything is committed on `stage/basic-pids-front` in three commits on top of `main`. The branch still needs the independent review and a merge by the reviewer.

**The four sheets** (A3, maintained by hand; the decisions are recorded as D-027 in `DESIGN.md`):
- **P-101, feed gas and prereforming:** gas inlet and feed trip valve, feed flow control, fuel split, desulphuriser V-101, steam addition on ratio to the feed, prereformer R-100.
- **P-102, reformer furnace:** H-101 with the catalyst tubes R-101 drawn inside it, the six convection coils in flue gas order, the two fans, fuel and tail gas trip valves, and control of fuel pressure, excess air and draft.
- **P-103, secondary reformer and high-temperature shift:** air compressor K-101 with anti-surge blow-off and a relief valve, the process air trip valve with a check valve, secondary reformer R-102, waste heat boiler E-105 with a hot bypass, R-201 and E-201.
- **P-104, low-temperature shift and gas cooling:** R-202, the gas side of the regenerator reboiler E-202, final cooler E-203, and separator V-201 with level control and a relief valve.

I split the sheets by flowsheet block. That puts E-202, E-203 and V-201 here rather than with the CO2 removal, so the mid sheets should start at the absorber and regenerator. D-027 lists the line numbers those sheets must continue.

**Lists and links:**
- The 22 front-end equipment items now name their sheet. I changed E-106 from an air cooler type to a tubular exchanger, which changes the earlier section's list.
- The line list has 51 lines, the instrument list 44 instruments, and a new `piping/special-items.yaml` holds the two relief valves.
- I proposed four trips in the cause-and-effect list: low steam flow, furnace pressure high, secondary reformer outlet temperature high, separator level high.
- 36 streams are linked to their lines, and the flow diagrams and layout model are rebuilt.

**Validation:** `cheme validate` gives 0 errors and 106 warnings. All but one come from the rebuilt layout model now routing the new lines (38 pipe clashes, 16 lines no pipe rack reaches, access and headroom); layout is S5's work. The one other is the existing energy-balance warning on K601 from S2. The drawing checks report nothing on any of the four sheets, and no off-page connector mismatches. The gates that failed before still fail (design review, the layout gates, maturity), and calculation maturity is still none, as after S2.

**Things that needed workarounds:**
- The drawing tool takes one pipe size per line. The steam-and-gas mixed feed (NG-1004) is DN 400 with a DN 200 first part, so I set those sizes afterwards with `cheme set`.
- The tool has no relief-valve builder. I drew the two relief valves as globe valves and converted them by editing the XML by hand.

**ASSUMED values I added:**
- Pipe sizes come from assumed velocities (20 m/s for gas, 30 m/s for steam, 15 m/s for ducts, 1.5 m/s for liquids). Air and flue gas ducts above DN 1600 carry an assumed equivalent diameter.
- A natural circulation ratio of 5 for the boiler water lines of the two waste heat boilers.
- Pipe sizes for lines the simulation gives no flow for: the reboiler's solvent side, the compressor blow-off, the waste heat boiler bypass, the relief lines, the boiler feed water lines to E-107, and cooling water (assumed 10 K rise).

**Still open:**
- Only two relief valves are drawn, with no set pressure or relief case. Whether the reformers and converters need their own depends on design pressures that are not set yet.
- Not drawn: furnace burner management, block and bypass valves around control valves, vents, drains and sample points, the compressor's intercoolers and drive, the stack, the steam drums.
- Control loops, setpoints and trip details (delay, reset, SIL) are left for S4.
- The PR description is in `build/pr-body.md`.

STATUS: DONE