---
schema: cheme/control_philosophy/v1
objectives:
  - {id: OBJ-1, title: "GOX to the pipeline at the specified rate, pressure and purity", loops: [FIC-1101, FIC-3106, FIC-4148, PIC-4102]}
  - {id: OBJ-2, title: GAN to the customer below 10 ppm O2, loops: [FIC-3107, PIC-4105, FIC-3106]}
  - {id: OBJ-3, title: No hydrocarbon accumulation in liquid oxygen, loops: [FIC-3111, LICA-3102, TIC-1105]}
  - {id: OBJ-4, title: The cold box's refrigeration balance held, loops: [SIC-3108, TICA-3124]}
  - {id: OBJ-5, title: Supply continuity from storage when the ASU stops, loops: [PIC-4111, PIC-4112]}
  - {id: OBJ-6, title: No air into the atmospheric evaporative cooler, loops: [LIC-1114]}
failures:
  - id: F-AIR
    title: Loss of instrument air
    response: "Each valve goes to its fail position. Stated so far: LV-1114 and XV-1115 closed (the chimney-tray seal holds); UV-3120 and UV-4131 open (the anti-surge recycles); TV-3124 open, which keeps the trim but means I-04 cannot close it on air loss (H03-A12, D-077). Most control valves have no fail position yet (HAZOP actions H01-A6, H02-A6, H03-A1, H04-A14); for each the HAZOP has to show the plant reaches a safe state before the position is fixed."
    loops: [LIC-1114, TICA-3124, UIC-3120, UIC-4131]
    interlocks: [I-03, I-04]
  - id: F-POWER
    title: Loss of electric power
    response: "The machines stop at once; the valves go to their fail positions and the C&E trips act. No operator sequence runs (SEQ-SHUTDOWN is the planned stop, not this). The backup supply needs power for its pumps: whether they have an emergency supply is open (H04-A14)."
    sequences: [SEQ-BACKUP-GOX, SEQ-BACKUP-GAN]
  - id: F-CW
    title: Loss of cooling water
    response: "The MAC coolers and the DCAC lower section warm up: TIA-1110 and TIA-1111 alarm (TAH ASSUMED). The design has no automatic MAC trip on cooling water; the operator unloads and stops the MAC (SEQ-SHUTDOWN), and the customers go to the backup supply. Whether a trip is needed is open."
    loops: [FIC-1108, TIC-1105]
    sequences: [SEQ-SHUTDOWN, SEQ-BACKUP-GOX, SEQ-BACKUP-GAN]
  - id: F-CHW
    title: Loss of chilled water (C-1102, P-1102A/B)
    response: "The TSA inlet warms (TIC-1105 high) and the booster air leaves E-3105 above 18.5 C (TICA-3124 high). The design's answer is to turn the liquid production down (D-067, D-069), but there is no loop for it yet: LIN-3001 has no flow control (H03-A7) and the LOX product is the hydrocarbon purge."
    loops: [TIC-1105, TICA-3124]
  - id: F-COMPANDER
    title: Compander trip
    response: "I-04 shuts the chilled water to E-3105; refrigeration is lost and the cold box warms slowly. Before the restart E-3105 is drained and E-3104 checked (D-077, H03-A11)."
    loops: [TICA-3124, SIC-3108]
    sequences: [SEQ-COMPANDER-TRIP]
    interlocks: [I-04]
  - id: F-GOXC
    title: GOX compressor trip
    response: "PIC-4101 vents the GOX through PV-4101B so the LP column pressure stays controlled (D-019); the GOX header falls and the LOX backup starts (SEQ-BACKUP-GOX)."
    loops: [PIC-4101, PIC-4111]
    sequences: [SEQ-BACKUP-GOX]
  - id: F-TSA
    title: TSA breakthrough (CO2 at the adsorber outlet)
    response: "AIA-2102 alarms at 1 ppm CO2 (ASSUMED). The intended answer to high-high (an early bed switch, or stopping the air to the cold box, D-006, D-010) is not yet a C&E interlock (H02-A1); until it is, it is an operator action on the alarm."
    loops: [TIC-2104, FIC-2105]
    sequences: [SEQ-TSA]
  - id: F-HC
    title: Hydrocarbons rising in the LP sump
    response: "AIA-3103 alarms; keep the LOX purge flowing (FIC-3111), keep E-3103 submerged (LICA-3102), find the source (TSA, intake). The action limits and what they trip are open (EIGA Doc 65, ASSUMED)."
    loops: [FIC-3111, LICA-3102]
  - id: F-LEVEL
    title: Low-low level in a product tank
    response: The pumps trip and the tank outlet closes (I-01, I-02); the backup stops.
    sequences: [SEQ-BACKUP-GOX, SEQ-BACKUP-GAN]
    interlocks: [I-01, I-02]
unresolved:
  - the fail positions of most control valves and of the machines' guide vanes (vendors, HAZOP)
  - the independent limit on the GOX draw (H04-A23) and the LP sump low-low (H03-A4)
  - the trips named in the instrument list but not yet in the cause-and-effect list (H04-A01, H02-A1, H02-A2)
  - a loop for the liquid production (H03-A7), which the chilled-water and compander failures rely on
  - whether the backup pumps have an emergency power supply (H04-A14)
  - the hydrocarbon action limits of AIA-3103 and AIA-4121 and what they trip
---

# Control philosophy: ASU-1

> PROPOSED (D-094). Not approved for implementation; the review status comes from `reviews/`.
> Loops, sequences and trips are defined in `control/loops.yaml`, `control/sequences.yaml` and
> `control/cause-effect.yaml`. This text explains them and does not repeat their values.

## Operating objectives

In order of priority when they conflict:

1. **OBJ-3:** no hydrocarbon accumulation in liquid oxygen. This is the dominant explosion hazard
   of an ASU (D-010). The LOX purge never stops, the reboiler stays submerged, and the TSA keeps
   CO2 and acetylene out.
2. **OBJ-6:** no air into the atmospheric C-1102.
3. **OBJ-1 and OBJ-2:** the GOX and GAN products at their specification. Off-spec GAN is diverted
   to the vent, never sent to the customer.
4. **OBJ-5:** supply continuity from storage when the ASU stops.
5. **OBJ-4:** the refrigeration balance, which carries the liquid production. The design gives
   up the liquid production first (D-067). That needs a handle the plant does not have yet:
   LIN-3001 has no flow control (H03-A7), and the LOX product is the hydrocarbon purge, which
   must not be cut.

## Control hierarchy

There are three layers, kept apart:

1. **Regulatory control:** the loops of `control/loops.yaml`. It keeps the plant at its
   operating point.
2. **Sequences:** `control/sequences.yaml`. They take the plant between modes: start-up, the TSA
   cycle, backup supply, the compander trip, shutdown.
3. **Protective functions:** the interlocks of the cause-and-effect list. They act whatever the
   loops do.

**Loops and safeguards.**
- A regulatory loop is not an interlock and never stands in for one.
- The HAZOP may credit a loop as a safeguard at most one order of magnitude, and nothing where
  it shares a device with the cause (the D-093 credit convention).
- Where a loop and an interlock share a device, the register says so. TICA-3124 and I-04 share
  TV-3124, a control valve; that is acceptable only because I-04 is not a SIF (D-077).
- Independence and SIL are judged in the HAZOP and the LOPA, not here.

**What sets what.**
- The air flow (FIC-1101) sets the plant's throughput, and the columns follow it.
- The LN reflux (FIC-3106) trims the purities.
- The LP column pressure is held by the waste nitrogen (PIC-3110, D-095).
- The GOX draw is set by flow (FIC-4148 on the K-4101 guide vanes). PIC-4101 only limits the
  suction: its low select throttles the draw before an over-draw boils the LP sump down
  (H04-S75), and its vent takes the GOX when K-4101 does not. The independent limit of HAZOP
  action H04-A23 comes on top of it.
- The GAN flow is set by FIC-3107 on the K-4102 guide vanes, and its export pressure by
  PIC-4105 on PV-4105 (D-095).

## Normal operation and disturbances

- **Ambient temperature and humidity.** These change the precooling. TIC-1105 holds the TSA
  inlet temperature, and the chilled-water margin is what limits it at 30 C ambient (D-005).
- **The customers' demand.** A changing GOX draw moves the GOX header. The operator follows with
  the air flow in steps the columns can take; the turndown range is not defined yet.
- **A TSA bed switch.** This gives a short pressure and flow swing into the cold box; the
  repressurisation step limits it.
- **Chilled-water upsets.** These reach the cold box through E-3105, so TICA-3124 alarms before
  the refrigeration margin is lost (D-067).

## Operator and automatic actions

- **Automatic:**
  - the loops in their normal modes;
  - the TSA cycle (KS-2101);
  - the backup pump start on low header pressure;
  - the anti-surge controls;
  - the trips of the C&E.
- **Operator:**
  - the plant load and the purity set points;
  - the start-up and shutdown steps, and every mode change of the main machines;
  - the reset of a trip once its cause has cleared;
  - the checks of E-3105 and E-3104 before a compander restart;
  - the hand-back from the backup supply;
  - the coordination with the customers before a planned stop.
- **Trip resets (proposed):** latched, reset by hand. The C&E does not state reset behaviour yet
  (H01-A3, H04-A01); the MAC's reset is its vendor's.

## Equipment and utility failures

The front matter lists the failures and their designed responses, by id:

- **F-AIR:** loss of instrument air.
- **F-POWER:** loss of electric power.
- **F-CW:** loss of cooling water.
- **F-CHW:** loss of chilled water.
- **F-COMPANDER:** compander trip.
- **F-GOXC:** GOX compressor trip.
- **F-TSA:** TSA breakthrough.
- **F-HC:** hydrocarbons in the sump.
- **F-LEVEL:** tank low-low level.

For instrument air, the fail position of each valve is the design decision still to be made for
most of them. The rule proposed here: a valve fails to the position that keeps the process
safe for the next hour without the operator, as LV-1114 (closed) does. TV-3124 (open) keeps the
trim but defeats I-04 on air loss (H03-A12), so it is not an example to follow without that
check.

## Assumptions and open points

- The fail positions of most control valves and of the machines' guide vanes are open; the
  register records each one as unresolved, with the HAZOP action that decides it.
- The two control conflicts found in the control review (the LP column pressure and the GOX
  draw; the GAN flow) are decided in D-095. Their limits (H04-A22, H04-A23) remain open.
- The liquid production has no handle yet (H03-A7).
- Trips named in the instrument list are not yet in the cause-and-effect list (H04-A01, H02-A1,
  H02-A2). The sequences refer to them by tag until they are added.
- The step times, cool-down rates and machine start-up steps are the suppliers'. The times in
  the sequences are placeholders.
- The hydrocarbon action limits are ASSUMED per EIGA Doc 65 until the analyzer and process
  review.
