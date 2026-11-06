---
# Process narrative. Schema of this front matter: `cheme schema narrative`. Skill
# control-narrative. Each section gets a heading "## <id> <title>" below.
schema: cheme/narrative/v1
sections:
  - id: ELA
    title: Skid A stacks and anolyte loop
    equipment: [E-101A, E-101B, E-101C, E-101D, T-101, P-101, E-111, U-101]
    blocks: [ELA]
    cases: [skid-a]
    modes: [normal, startup, shutdown, abnormal]
    loops: [FIC-101, TIC-111, JIC-101, AI-101]
    sequences: [SEQ-A-FILL, SEQ-A-START, SEQ-A-STOP, SEQ-A-TRIP, SEQ-A-GAS, SEQ-A-DRAIN]
    interlocks: [I-101, I-102, I-103, I-104, I-105, I-106]
  - id: GCA
    title: Skid A cathode gas conditioning
    equipment: [V-121, K-131, X-131, X-132]
    blocks: [GCA]
    cases: [skid-a]
    modes: [normal, startup, shutdown]
    loops: [FIC-102, PIC-121, LIC-122, PIC-131]
  - id: ELB
    title: Skid B stacks, anolyte loop, KOH dosing and bleed
    equipment: [E-201A, E-201B, E-201C, E-201D, T-201, P-201, E-211, T-202, P-202, U-201]
    blocks: [ELB]
    cases: [skid-b]
    modes: [normal, startup, shutdown, abnormal]
    loops: [FIC-201, TIC-211, JIC-201, AIC-201, FIC-203, LIC-201]
    sequences: [SEQ-B-FILL, SEQ-B-START, SEQ-B-STOP, SEQ-B-TRIP, SEQ-B-GAS, SEQ-B-DRAIN]
    interlocks: [I-201, I-202, I-203, I-204, I-205, I-206, I-207, I-208]
  - id: GCB
    title: Skid B cathode gas conditioning
    equipment: [V-221, K-231, X-231, X-232]
    blocks: [GCB]
    cases: [skid-b]
    modes: [normal, startup, shutdown]
    loops: [FIC-202, PIC-221, LIC-222, PIC-231]
unresolved:
  - "The pH probe reads activity pH; the duty model, the trip value and AIC-201's setpoint are concentration-basis pH (control/philosophy.md): an offset or a calibration is needed before use."
  - "FE, WDE, U and kWh/kg are held constant by assumption, not supported by measurement: the measured runs last 1 h in fresh 1 M KOH (DESIGN.md D-014)."
  - "Relief, the HAZOP and the area classification are not done (DESIGN.md D-017, D-019)."
---

# Process narrative

> PROPOSED. This narrative describes the intended operation of the two CO2-to-CO pilot skids of
> #330. It is not approved for implementation; its review status comes from the records in
> `reviews/` (none yet).

The values are not repeated here: the operating cases are `skid-a` and `skid-b` of
`process/flowsheet.yaml`, the duties `D-A` and `D-B` of `process/duties.yaml`, the setpoints in
`control/loops.yaml`, the trips in `control/cause-effect.yaml` and the sequences in
`control/sequences.yaml`. The calculated results per campaign are in
`results/scenarios/<H>h/record.json` and `results/resize-1000h-10000h.md`.

## ELA Skid A stacks and anolyte loop

**Purpose.** Four stacks of seven 100 cm2 cells (E-101A to D) on a 48 V DC bus from the
rectifier U-101 reduce CO2 to CO at 200 mA/cm2. The bipolar membranes supply hydroxide to the
Ni anodes from a recirculated KOH anolyte held in T-101.

**Boundaries.** From the KOH fill hose connection at the frame's west end to the spent anolyte
drain there; the O2 vent of T-101 to atmosphere; cooling water to E-111; AC power to U-101.

**Normal operation.** T-101 is filled once with fresh 1 M KOH sized by `cheme process stack`
so that the anolyte reaches the pH threshold at the end of the campaign (DESIGN.md D-009).
P-101 recirculates the anolyte through the stacks at the bench ratio (FIC-101), E-111 cools the
stack inlet so that the stacks return the anolyte at 25 degC (TIC-111), JIC-101 holds the stack
current. Nothing is dosed or bled: the pH falls steadily as K+ crosses to the cathode and
carbonate to the anolyte. AI-101 indicates the pH with an alarm before the end of the campaign.

**Modes.** Fill (SEQ-A-FILL), start-up (SEQ-A-START: recirculation and cooling before the
current), the normal stop at the end of the campaign H (SEQ-A-STOP), the response to a process
trip (SEQ-A-TRIP) or to a gas detection trip (SEQ-A-GAS) and the end-of-run drain
(SEQ-A-DRAIN). The pH low-low trip (I-101) acts at the threshold itself, if the anolyte gets
there before H; level, temperature and flow trips stop the current (I-102, I-105, I-106); the
CO and H2 detectors (I-103, I-104) also isolate the cathode gas train. The skid is open and
naturally ventilated, with no enclosure and no fan (DESIGN.md D-050).

**Assumptions and open points.** The scale-up from 5 to 100 cm2 and the measured performance
over the whole campaign (DESIGN.md D-007, D-014); the reservoir has no time margin, so a WDE one
standard deviation lower ends the campaign early (`results/scenarios/<H>h/uncertainty.json`).
At 10,000 h the reservoir no longer fits the skid envelope (D-015).

## GCA Skid A cathode gas conditioning

**Purpose.** Deliver the CO at the skid boundary at its purity and pressure and burn the rest.

**Boundaries.** From the stack cathode outlets to the CO product connection, the oxidiser flue
and the condensate drain; fresh CO2 and air at the battery limit.

**Normal operation.** FIC-102 feeds the fresh CO2, PIC-121 holds the cathode back-pressure, V-121
separates the carbonate condensate on level (LIC-122), K-131 compresses the gas, the PSA package
X-131 delivers the CO (PIC-131) and returns CO2 to the cathode feed, and X-132 burns the tail
gas with air (DESIGN.md D-012).

**Modes.** Started and stopped with the stacks (SEQ-A-START, SEQ-A-STOP, SEQ-A-TRIP); a gas
detection closes the CO2 and stops the compressor, and the train is purged to the oxidiser only
once the leak is found and the trip reset (SEQ-A-GAS).

**Assumptions and open points.** The packages are black boxes (recovery, recycle, energy
ASSUMED); relief and the cathode salt precipitation are not designed.

## ELB Skid B stacks, anolyte loop, KOH dosing and bleed

**Purpose.** The same stacks as Skid A (E-201A to D, U-201) on a small reservoir T-201 that is
held at a steady anolyte composition instead of being used up.

**Boundaries.** As ELA, plus the 5 M KOH delivery to the day tank T-202, make-up water and the
bleed to the site effluent at the battery limit.

**Normal operation.** As ELA for the recirculation, cooling and current (FIC-201, TIC-211,
JIC-201). P-202 doses 5 M KOH from T-202 continuously at the duty's rate, trimmed by the pH
(AIC-201); the bleed leaves T-201 at its flow setpoint (FIC-203) and make-up water holds the
level (LIC-201), so carbonate leaves as fast as it enters (DESIGN.md D-010). T-202 is refilled
weekly.

**Modes.** Fill, start-up, normal stop, process and gas trip response and end-of-run drain
(SEQ-B-FILL, SEQ-B-START, SEQ-B-STOP, SEQ-B-TRIP, SEQ-B-GAS, SEQ-B-DRAIN). The
dosing and the bleed stop with the current (I-207); a low-low day tank level stops the dosing
pump (I-208); the other trips as Skid A (I-201 to I-206).

**Assumptions and open points.** The setpoints and the 50 L hold-up are ASSUMED; the dose is
open-loop in the model (the AIC-201 trim is not simulated); Skid B uses more KOH per kg CO than
Skid A (`results/resize-1000h-10000h.md`).

## GCB Skid B cathode gas conditioning

**Purpose, boundaries, operation and modes.** As GCA, with FIC-202, PIC-221, LIC-222 and PIC-231
on V-221, K-231, X-231 and X-232.

**Assumptions and open points.** As GCA.
