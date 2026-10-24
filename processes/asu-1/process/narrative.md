---
schema: cheme/narrative/v1
sections:
  - id: MAC
    title: Main air compression and precooling
    equipment: [F-1101, K-1101, E-1101, E-1102, E-1103, C-1101, C-1102, P-1101A, P-1101B, P-1102A, P-1102B]
    blocks: [MAC, K1101, C1101, C1101U, C1102]
    cases: [design]
    modes: [normal, startup, shutdown]
    loops: [FIC-1101, PIC-1103, UIC-1102, TIC-1105, LIC-1106, LIC-1107, FIC-1108, LIC-1114]
    sequences: [SEQ-MAC-START, SEQ-SHUTDOWN]
    interlocks: [I-03]
  - id: PUR
    title: Front-end purification (TSA)
    equipment: [V-2101A, V-2101B, E-2101, F-2101]
    blocks: [PUR, V2101, E2101]
    cases: [design]
    modes: [normal, startup]
    loops: [TIC-2104, FIC-2105]
    sequences: [SEQ-TSA]
  - id: CB
    title: Cold box
    equipment: [E-3101, E-3102, E-3103, C-3101, C-3102, K-3101, KT-3101, E-3104, E-3105, V-3101]
    blocks: [CB, X3102, K3101, E3104, E3105, E3101, KT3101, C3101, E3102, C3102, X3101]
    cases: [design]
    modes: [normal, startup, shutdown, compander trip]
    loops: [LIC-3101, LICA-3102, FIC-3106, SIC-3108, TIC-3109, UIC-3120, PIC-3110, FIC-3111, PIC-3113, TICA-3124]
    sequences: [SEQ-CB-START, SEQ-COMPANDER-TRIP, SEQ-SHUTDOWN]
    interlocks: [I-04]
  - id: PRD
    title: Product compression, storage and backup
    equipment: [K-4101, E-4101, E-4102, K-4102, E-4103, T-4101, T-4102, P-4101A, P-4101B, P-4102A, P-4102B, E-4105A, E-4105B, E-4106A, E-4106B]
    blocks: [PRD, K4101, K4102]
    cases: [design]
    modes: [normal, startup, shutdown, backup supply]
    loops: [PIC-4102, FIC-4148, PIC-4150, PIC-4101, UIC-4103, FIC-3107, PIC-4106, UIC-4131, PIC-4105, PICA-4109, PICA-4110, PIC-4111, PIC-4112]
    sequences: [SEQ-BACKUP-GOX, SEQ-BACKUP-GAN, SEQ-SHUTDOWN]
    interlocks: [I-01, I-02]
unresolved:
  - the turndown range of the plant and how fast the load may change (not defined yet)
  - the suppliers' start-up procedures (MAC, compander, cold box, product compressors), which set the step times of the sequences
---

# Process narrative: ASU-1

> PROPOSED (D-094). This narrative describes the intended operation at basic engineering. It
> is not approved for implementation; its review status comes from the records in `reviews/`.

The plant separates air into gaseous oxygen for a pipeline at 30 barg, pressurised nitrogen
and small liquid products, in a low-pressure double-column cycle (D-001). Values are not
repeated here: the operating case is `design` in `process/flowsheet.yaml`, the set points are
in `control/loops.yaml`, the trips in `control/cause-effect.yaml`, the operating steps in
`control/sequences.yaml`.

## MAC Main air compression and precooling

**Purpose.** K-1101 compresses the filtered air (F-1101) through its intercoolers and the
aftercooler E-1103. The direct contact aftercooler C-1101 then cools it in two sections:
cooling water below, chilled water above. The chilled water comes from the evaporative cooler
C-1102, which cools its water with the dry waste nitrogen from the cold box (D-005, D-067).

**Boundaries.** From the air intake (S1) to the precooled air leaving C-1101 to the TSA (S3).
The cooling water and the waste nitrogen to C-1102 (S12B) cross the boundary.

**Normal operation.** FIC-1101 sets the air flow on the inlet guide vanes, and with it the load
of the whole plant. PIC-1103 limits the discharge pressure through a low select on the same
guide vanes. UIC-1102 keeps the machine out of surge by blowing off to S-1101. TIC-1105 holds
the air leaving the DCAC by the chilled-water valve TV-1105. The levels are held by:
- LIC-1106: the DCAC sump;
- LIC-1107: the C-1102 make-up;
- LIC-1114: the chimney-tray water seal, which keeps the 5.9 bara air out of the atmospheric
  C-1102.

The seal's low-low protection is the trip I-03, on its own tapping.

**Modes.** Start-up (SEQ-MAC-START) first circulates the water and establishes the chimney-tray
seal, then starts the MAC on blow-off and loads it in steps. Until the
cold box sends waste nitrogen, C-1102 makes no chilled water, so the upper DCAC section runs warm
and TIC-1105 stays in manual. Shutdown is SEQ-SHUTDOWN.

## PUR Front-end purification (TSA)

**Purpose.** Two adsorbers, V-2101A and V-2101B, remove water, CO2, N2O and acetylene before the
cold box (D-006). One adsorbs while the other is regenerated with waste nitrogen heated in the
electric heater E-2101.

**Boundaries.** From the precooled air (S3) to the dry air to the cold box (S4); the
regeneration gas S12A in and S12D out.

**Normal operation.** The sequence controller KS-2101 runs the cycle (SEQ-TSA):
1. depressurise;
2. heat (TIC-2104 on the heater, FIC-2105 on the flow) until the heat pulse arrives (TI-2114A
   or TI-2114B);
3. cool through the heater bypass;
4. repressurise;
5. switch.

AIA-2102 (CO2) and AIA-2103 (dew point) watch the bed on line; a rising CO2 means that bed is
breaking through.

**Modes.** The cycle runs continuously. The intended answer to a CO2 high-high (an early bed
switch, or stopping the air to the cold box, D-010) is not yet an interlock (H02-A1); until
then it is an operator action on the alarm.

## CB Cold box

**Purpose.** The dry air is cooled against the products in E-3101 and separated in the HP column
C-3101 and the LP column C-3102. These are coupled by the condenser-reboiler E-3103 in the LP
sump (D-001). Part of the air is boosted by K-3101, cooled in E-3104 and the trim cooler E-3105,
and expanded in KT-3101 to the LP column as Lachmann air. This expansion makes the
refrigeration (D-003, D-067).

**Boundaries.** From the dry air (S4) to the warm products (S7 GOX, S9 GAN), the waste nitrogen
(S17), the liquids (S10, S11) and the purge to the drain vaporizer V-3101.

**Normal operation.**
- **Columns:**
  - LIC-3101 passes the rich liquid to the LP column at the rate it collects.
  - FIC-3106 sets the LN reflux, the main purity handle together with the air flow.
  - PIC-3110 holds the LP column pressure through the waste nitrogen: first to C-1102
    (PV-3110A), the surplus to the vent (PV-3110B) (D-095).
- **Refrigeration:**
  - SIC-3108 holds the compander speed.
  - TIC-3109 watches the expander outlet temperature against a low limit, so no liquid forms; what
    it acts on is open (H03-A18).
  - TICA-3124 holds the boosted air at 15 C into E-3101. The cold box's refrigeration margin
    depends on it.
- **Hydrocarbon safety (D-010):**
  - FIC-3111 withdraws the LOX product continuously; it is the hydrocarbon purge of the sump.
  - LICA-3102 keeps E-3103 submerged.
  - AIA-3103 watches the sump liquid.
- **Casing:** PIC-3113 keeps the casing under dry nitrogen.

**Modes.** Cool-down and start-up (SEQ-CB-START) take days and end with the product compressors.
A compander trip (SEQ-COMPANDER-TRIP) loses the refrigeration. The trip I-04 shuts the chilled
water to E-3105, and before the restart the E-3105 shell side is drained and checked dry and
E-3104 is checked (D-077, H03-A11). Normal shutdown keeps the liquid in the cold box for a warm restart.

## PRD Product compression, storage and backup

**Purpose.** K-4101 compresses the GOX to the pipeline (D-002); K-4102 compresses the GAN (D-004).
The liquids go to the tanks T-4101 (LOX) and T-4102 (LIN). Pumps and ambient-air vaporizers
supply both headers when the ASU does not (D-014).

**Boundaries.** From the warm products (S7, S9) and the liquids (S10, S11) to the battery limits
(S8, S9B) and the tank vents.

**Normal operation.**
- **GOX train:**
  - PIC-4102 holds the pipeline pressure on the K-4101 guide vanes, through a low select with
    the maximum draw FIC-4148 and the suction low limit PIC-4150 (D-096).
  - PIC-4101 vents the GOX through PV-4101B when K-4101 does not take it (D-019).
  - UIC-4103 is the anti-surge, on the suction flow (FT-4148).
- **GAN train:**
  - PIC-4105 holds the GAN export pressure by setting the set point of FIC-3107 on the K-4102
    guide vanes (cascade, D-096).
  - UIC-4131 is the anti-surge.
- **Tanks:** PICA-4109 and PICA-4110 vent the tanks' boil-off.

**Modes.** On low header pressure, the standby pump starts and PIC-4111 or PIC-4112 holds the
header (SEQ-BACKUP-GOX, SEQ-BACKUP-GAN); once the ASU supplies again the operator hands back.
The low-low tank levels trip the pumps (I-01, I-02). The low vaporizer outlet temperature is
meant to protect the carbon-steel pipeline (TSLL-4113, TSLL-4114; not yet in the C&E,
H04-A01).

## Open points

- The turndown range and the rate of load changes are not defined yet.
- The suppliers' start-up procedures, which set the step times of the sequences.
- The independent limits on the GOX draw and the GAN guide vanes (H04-A23, H04-A22).
- The role of PV-4105 and the signal drawn to it, the anti-surge flow measurement of K-4101
  (FT-4148 does not see the recycle), and the maximum GOX draw as a ratio to the air flow
  (D-096).
- PIC-4101's set-point window and the GOX vent at turndown (an O2 release at VNT-4003), the
  anti-windup and bumpless transfer of the low select and the GAN cascade, where the GAN goes
  while K-4102 stands, and whether the waste and vent valves take the full GOX make on a
  K-4101 trip (D-096).
- The trips named in the instrument list are not yet in the cause-and-effect list (D-094 lists
  them; HAZOP action H04-A01 and others).
