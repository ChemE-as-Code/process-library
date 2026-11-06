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
    interlocks: [I-101, I-102, I-103, I-104, I-105, I-106, I-114, I-116, I-117, I-120]
  - id: GCA
    title: Skid A cathode gas conditioning
    equipment: [V-121, K-131, X-131, X-132]
    blocks: [GCA]
    cases: [skid-a]
    modes: [normal, startup, shutdown]
    loops: [FIC-104, FIC-102, PIC-121, LIC-122, PIC-131]
    interlocks: [I-109, I-110, I-111, I-112, I-113, I-115, I-118, I-119]
  - id: ELB
    title: Skid B stacks, anolyte loop, KOH dosing and bleed
    equipment: [E-201A, E-201B, E-201C, E-201D, T-201, P-201, E-211, T-202, P-202, U-201]
    blocks: [ELB]
    cases: [skid-b]
    modes: [normal, startup, shutdown, abnormal]
    loops: [FIC-201, TIC-211, JIC-201, AIC-201, FIC-203, LIC-201]
    sequences: [SEQ-B-FILL, SEQ-B-START, SEQ-B-STOP, SEQ-B-TRIP, SEQ-B-GAS, SEQ-B-DRAIN]
    interlocks: [I-201, I-202, I-203, I-204, I-205, I-206, I-207, I-208, I-214, I-216, I-217, I-220, I-221]
  - id: GCB
    title: Skid B cathode gas conditioning
    equipment: [V-221, K-231, X-231, X-232]
    blocks: [GCB]
    cases: [skid-b]
    modes: [normal, startup, shutdown]
    loops: [FIC-204, FIC-202, PIC-221, LIC-222, PIC-231]
    interlocks: [I-209, I-210, I-211, I-212, I-213, I-215, I-218, I-219]
unresolved:
  - "The pH probe reads activity pH; the duty model, the trip value and AIC-201's setpoint are concentration-basis pH (control/philosophy.md): an offset or a calibration is needed before use."
  - "FE, WDE, U and kWh/kg are held constant by assumption, not supported by measurement: the measured runs last 1 h in fresh 1 M KOH (DESIGN.md D-014)."
  - "The relief study (sizing, outlets; its basis is DESIGN.md D-060), the HAZOP session and the area classification are not done (D-019, D-059)."
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
drain there; the O2 vent of T-101 to atmosphere; tempered water to E-111 from a unit off the
skid, outside the zone; AC power to U-101; the capped drain, vent and pump-out connections
(DR-101, AV-111, PO-101) used only at the end of a run.

**Normal operation.** T-101 is filled once with fresh 1 M KOH sized by `cheme process stack`
so that the anolyte reaches the pH threshold at the end of the campaign (DESIGN.md D-009).
P-101 recirculates the anolyte through the stacks at the bench ratio (FIC-101), E-111 cools the
stack inlet so that the stacks return the anolyte at 25 degC (TIC-111), JIC-101 holds the stack
current. The tempered-water unit cools in operation and heats at start-up and when the skid
stands idle outdoors, so the loop holds 25 degC and does not freeze (TIC-111's low alarm,
DESIGN.md D-052). Nothing is dosed or bled: the pH falls steadily as K+ crosses to the cathode and
carbonate to the anolyte. AI-101 indicates the pH with an alarm before the end of the campaign.

**Modes.** Fill (SEQ-A-FILL), start-up (SEQ-A-START: recirculation and cooling before the
current), the normal stop at the end of the campaign H (SEQ-A-STOP), the response to a process
trip (SEQ-A-TRIP) or to a gas detection trip (SEQ-A-GAS) and the end-of-run drain
(SEQ-A-DRAIN). The pH low-low trip (I-101) acts at the threshold itself, if the anolyte gets
there before H; level, temperature and flow trips stop the current (I-102, I-105, I-106); the
CO and H2 detectors (I-103, I-104) also isolate the cathode gas train. The skid is open and
naturally ventilated, with no enclosure and no fan (DESIGN.md D-050). The drain vents the loop
at the cooler, empties T-101 by gravity, the supply header's low point and the tank's heel by
the pump-out, flushes with demineralised water and caps every connection (D-055).

**Assumptions and open points.** The scale-up from 5 to 100 cm2 and the measured performance
over the whole campaign (DESIGN.md D-007, D-014); the reservoir has no time margin, so a WDE one
standard deviation lower ends the campaign early (`results/scenarios/<H>h/uncertainty.json`).
At 10,000 h the reservoir no longer fits the skid envelope (D-015).

## GCA Skid A cathode gas conditioning

**Purpose.** Deliver the CO at the skid boundary at its purity and pressure and burn the rest.

**Boundaries.** From the stack cathode outlets to the CO product connection, the oxidiser flue
and the condensate drain; fresh CO2 and air at the battery limit.

**Normal operation.** FIC-104 holds the total cathode CO2 by resetting the fresh CO2 of FIC-102
(D-062), PIC-121 holds the cathode back-pressure, V-121
separates the carbonate condensate on level (LIC-122), K-131 compresses the gas, the PSA package
X-131 delivers the CO (PIC-131) and returns CO2 to the cathode feed, and X-132 burns the tail
gas with air (DESIGN.md D-012). The tail gas TG-101 leaves the PSA through its trip valve
XV-133, a check valve and the detonation arrester FA-133, all inside X-131's zone, and runs
all-welded to the burner (D-054).

**Modes.** Started and stopped with the stacks (SEQ-A-START, SEQ-A-STOP, SEQ-A-TRIP): XV-133
opens only once the oxidiser fires and closes before it stops. A gas detection, a flame held on
the arrester (TSHH-133, I-109) or the oxidiser's own trip (I-110) closes the CO2 and the tail
gas and stops the compressor, and the train is purged to the oxidiser only once the cause is
found and the trip reset (SEQ-A-GAS); so do the compressor stopping with the current on
(I-113), its discharge high-high (I-112), the instrument air low-low (I-114) and the condensate
high-high (I-119). The start-up gives the train its outlet before the CO2 flows, and every stop
depressurises CG-103 and the PSA through the PSA's own stop to the oxidiser still firing
(D-061). The cathode side has the bursting disc PSE-101 and its pressure high-high (I-111,
D-060).

**Assumptions and open points.** The packages are black boxes (recovery, recycle, energy
ASSUMED); the relief study and the cathode salt precipitation are open; the arrester's type
examination for the actual tail gas and its burning time are the vendor's.

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

**Purpose, boundaries, operation and modes.** As GCA, with FIC-204, FIC-202, PIC-221, LIC-222 and
PIC-231 on V-221, K-231, X-231 and X-232, the tail gas through XV-233 and FA-233 (I-209, I-210)
and the trips I-211 to I-213, I-215, I-218 and I-219.

**Assumptions and open points.** As GCA.
