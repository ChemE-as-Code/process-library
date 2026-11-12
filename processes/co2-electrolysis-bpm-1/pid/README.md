# P&ID sheets

DEXPI 2.0.1 XML, one file per sheet. Start a new one with the `pid-draft` skill.

- `P-01.xml`: Skid A of #330 (train 1xx), `P-02.xml`: Skid B (train 2xx). Both are generated
  (`plant.yaml` `generator:`) by `scripts/draft_P-01.py` and `draft_P-02.py` from the frames in
  `frames/` (the empty sheets with their title blocks, as `cheme sheet new` wrote them). Never
  edit them by hand: change the script and run `cheme regen P-01 P-02` (DESIGN.md D-017).
  Revision B (2026-11-06, the owner's decisions, D-054 to D-056): no extract fan (open skid);
  the tail gas through its trip valve, check valve and detonation arrester with the arrester's
  temperature trip; the cooler on a tempered-water unit (TWS-x01, TWR-x01); the loop's low-point
  drain, the cooler vent and the tanks' camlock pump-outs. The sheets are exactly what the
  scripts make (no drift acceptance).
  Revision C (2026-11-06, the design review 2026-11-06-design, D-060 to D-065): the cathode's
  bursting disc PSE-x01 (RL-x01) and pressure high-high PIA-x23, the compressor discharge
  PIA-x32, the anolyte pressure PIA-x13 and the H2-in-O2 analyser AIA-x14, the total cathode CO2
  FIC-x04, each stack's voltage EIA-x05A to D and current IIA-x06A to D, the independent
  condensate level LIA-x24 (V-x21 N5) with XV-x25, the check valves on CO2-x01, W-x01, CO2-x02
  (with XV-x34) and W-202, the instrument air PSLL-x51; on P-02 HV-210, BPV-202 and P-202's
  relief note. The relief device is drawn as a bursting disc (core 1.10's authoring API has no
  inline safety-valve symbol).
  Revision D (2026-11-07, the agent reviews 2026-11-06-design-r2 and 2026-11-06-layout-r4,
  D-067 to D-069): XV-x25 and XV-x34 drawn as trip valves with their fail-closed actuators and
  the safety I/O outputs XY-x25 and XY-x34; the anolyte at the stack outlet PIA-x15 and the
  cathode at the stack inlet PIA-x16 (the membrane's difference at each end); PSE-x01's burst
  indicator XS-x01; a drip leg with a valved, capped drain at each low point of the tail gas
  (DR-x02 / HV-x11, DR-x03 / HV-x12); the AV-x11 note clear of the cooler.
  Revision E (2026-11-11, core 1.11's `cheme.offpage-not-on-edge`, D-071): drawing only. AV-x11,
  PO-x01 and DR-x03 end on the drawing area's edge (bottom, west, east), routed without a new
  crossing; DR-x01 is an open end at its valve ("drain, capped"); CD-x01 stays inside the east
  edge (V-x21's outlet lies inside the cathode gas loop, any route to an edge crosses it),
  open for the owner (D-071).
  Revision F (2026-11-12, the owner's decisions on review 2026-11-11-design-r4, D-072): drawing
  only. CD-x01 runs from XV-x25 down just west of W-x01's drop, across the CO2 feed header, to
  the bottom edge; that one crossing per sheet is accepted in drawing-clean (ADR 0049). The
  capped vents, drains and pump-outs of D-055 (AV-x11, PO-x01, PO-202, DR-x01 to DR-x03) are
  open ends at their valves, their notes "vent, capped", "drain, capped", "pump-out by hose,
  capped" ("hose, capped" on PO-202); AV-x11, PO-x01 and DR-x03 (at the foot of TG-x01's drop)
  are drawn as in revision D again.
