---
schema: cheme/control_philosophy/v1
objectives:
  - {id: OBJ-1, title: "GOX to the pipeline at the specified rate, pressure and purity", loops: [FIC-1101, FIC-3106, PIC-4101, PIC-4102]}
  - {id: OBJ-2, title: GAN to the customer below 10 ppm O2, loops: [FIC-3107, FIC-4105, FIC-3106]}
  - {id: OBJ-3, title: No hydrocarbon accumulation in liquid oxygen, loops: [FIC-3111, LICA-3102, TIC-1105]}
  - {id: OBJ-4, title: The cold box's refrigeration balance held, loops: [SIC-3108, TIC-3109, TICA-3124]}
  - {id: OBJ-5, title: Supply continuity from storage when the ASU stops, loops: [PIC-4111, PIC-4112]}
  - {id: OBJ-6, title: No air into the atmospheric evaporative cooler, loops: [LIC-1114]}
failures:
  - id: F-AIR
    title: Loss of instrument air
    response: "Each valve goes to its fail position. Those stated so far: LV-1114 and XV-1115 closed (the chimney-tray seal holds), TV-3124 open (the trim is kept), UV-3120 and UV-4131 open (the anti-surge recycles). Most control valves have no fail position yet; for each, the HAZOP has to show the plant goes to a safe state, then the position is fixed."
    loops: [LIC-1114, TICA-3124, UIC-3120, UIC-4131]
    interlocks: [I-03]
  - id: F-POWER
    title: Loss of electric power
    response: "The machines stop and the plant takes the shutdown path without the controls (SEQ-SHUTDOWN). The backup supply needs power for its pumps: whether they have an emergency supply is open."
    sequences: [SEQ-SHUTDOWN, SEQ-BACKUP-GOX, SEQ-BACKUP-GAN]
  - id: F-CW
    title: Loss of cooling water
    response: "The MAC coolers and the DCAC lower section warm up (TIA-1110, TIA-1111 alarms); the MAC vendor's protection trips K-1101; the customers go to the backup supply."
    loops: [FIC-1108, TIC-1105]
    sequences: [SEQ-BACKUP-GOX, SEQ-BACKUP-GAN]
  - id: F-CHW
    title: Loss of chilled water (C-1102, P-1102A/B)
    response: "The TSA inlet warms (TIC-1105 high) and the booster air leaves E-3105 above 18.5 C (TICA-3124 high): turn the liquid production down to keep the cold box in balance (D-067, D-069)."
    loops: [TIC-1105, TICA-3124]
  - id: F-COMPANDER
    title: Compander trip
    response: "I-04 shuts the chilled water to E-3105; refrigeration is lost and the cold box warms slowly. Before the restart the E-3105 shell side is drained and checked dry (D-077)."
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
    response: "AIA-2102 alarms at 1 ppm CO2; on high-high the beds are switched early or the MAC trips, so no CO2 or acetylene reaches the cold box (D-006, D-010)."
    loops: [TIC-2104, FIC-2105]
    sequences: [SEQ-TSA]
  - id: F-HC
    title: Hydrocarbons rising in the LP sump
    response: "AIA-3103 alarms; keep or raise the LOX purge (FIC-3111), keep E-3103 submerged (LICA-3102), find the source (TSA, intake). The action limits and what they trip are open (EIGA Doc 65, ASSUMED)."
    loops: [FIC-3111, LICA-3102]
  - id: F-LEVEL
    title: Low-low level in a product tank
    response: The pumps trip and the tank outlet closes (I-01, I-02); the backup stops.
    sequences: [SEQ-BACKUP-GOX, SEQ-BACKUP-GAN]
    interlocks: [I-01, I-02]
unresolved:
  - the fail positions of most control valves and of the machines' guide vanes (vendors, HAZOP)
  - thirteen trips of the instrument list not yet in the cause-and-effect list
  - whether the backup pumps have an emergency power supply
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
5. **OBJ-4:** the refrigeration balance, which carries the liquid production. It is the first
   thing given up: the liquid production is turned down before the products are touched.

## Control hierarchy

There are three layers, kept apart:

1. **Regulatory control:** the loops of `control/loops.yaml`. It keeps the plant at its
   operating point.
2. **Sequences:** `control/sequences.yaml`. They take the plant between modes: start-up, the TSA
   cycle, backup supply, the compander trip, shutdown.
3. **Protective functions:** the interlocks of the cause-and-effect list. They act whatever the
   loops do.

A regulatory loop is never counted as a safeguard. Where a loop and an interlock share a
device, the register says so: TICA-3124 and I-04 share TV-3124, a control valve. That is
acceptable only because I-04 is not a SIF (D-077). Independence and SIL are judged in the HAZOP
and LOPA, not here.

The plant's throughput is set by the air flow (FIC-1101). The columns follow it. The purities
are trimmed by the LN reflux (FIC-3106). The LP column pressure is held by the waste nitrogen
(PIC-3110) and by the GOX suction (PIC-4101).

## Normal operation and disturbances

- **Ambient temperature and humidity.** These change the precooling. TIC-1105 holds the TSA
  inlet temperature, and the chilled-water margin is what limits it at 30 C ambient (D-005).
- **The customers' demand.** A changing GOX draw moves the GOX header. The operator follows with
  the air flow in steps the columns can take; the turndown range is still open (D-018).
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
  - every trip.
- **Operator:**
  - the plant load and the purity set points;
  - the start-up and shutdown steps, and every mode change of the main machines;
  - the reset of a trip once its cause has cleared;
  - the check of E-3105 before a compander restart;
  - the decision to turn the liquid production down;
  - the coordination with the customers before a planned stop.
- **Trip resets:** all trips latch and are reset by hand.

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
safe for the next hour without the operator, as LV-1114 (closed) and TV-3124 (open) already do.

## Assumptions and open points

- The fail positions of most control valves and of the machines' guide vanes are open; the
  register records each one as unresolved, not as a default.
- Thirteen trips named in the instrument list are not yet in the cause-and-effect list. They are
  the machine trips, the DCAC high-high level, the TSA trips and the vaporizer low temperatures.
  The sequences refer to them by tag until they are added.
- The step times, cool-down rates and machine start-up steps are the suppliers'.
- The hydrocarbon action limits are ASSUMED per EIGA Doc 65 until the analyzer and process
  review.
- Whether the backup pumps need an emergency power supply is open (F-POWER).
