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
