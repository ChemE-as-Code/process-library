---
# Process narrative. Schema of this front matter: `cheme schema narrative`. Skill
# control-narrative. Each section gets a heading "## <id> <title>" below. D-021.
schema: cheme/narrative/v1
sections:
  - id: CMP
    title: Make-up gas compression
    equipment: [V-103, K-101, E-101]
    blocks: [CMP, K101, E101]
    cases: [design]
    modes: [normal, startup, shutdown]
    loops: [PIC-102, SIC-113, UIC-104]
    sequences: [SEQ-K101-START]
    interlocks: [I-101, I-102]
  - id: SYN
    title: Synthesis loop
    equipment: [K-102, E-102, R-101, V-104, E-103, V-101]
    blocks: [SYN, M101, K102, E102, R101, E103, V101, SPL]
    cases: [design]
    modes: [normal, startup, shutdown]
    loops: [UIC-203, TIC-205, PIC-207, LIC-209, PIC-308, FIC-303]
    interlocks: [I-201, I-202, I-302]
  - id: SEP
    title: Crude let-down and LP flash
    equipment: [V-101, V-102]
    blocks: [V102]
    cases: [design]
    modes: [normal, startup, shutdown]
    loops: [LIC-307, PIC-309, LIC-310]
    interlocks: [I-301]
  - id: TOP
    title: Topping column
    equipment: [C-201, E-201, V-201, P-201A, P-201B, E-202, P-202A, P-202B]
    blocks: [C201]
    cases: [design]
    modes: [normal, startup, shutdown]
    loops: [TIC-402, PIC-404, LIC-405, LIC-408]
    interlocks: [I-401]
  - id: REF
    title: Refining column and product
    equipment: [C-202, E-203, V-202, P-203A, P-203B, E-204, P-204A, P-204B]
    blocks: [C202]
    cases: [design]
    modes: [normal, startup, shutdown]
    loops: [TIC-502, PIC-504, LIC-505, FIC-507, LIC-508]
    interlocks: [I-501]
unresolved:
  - "Start-up and shutdown sequences (control/sequences.yaml) are not written yet, except the K-101 start-up SEQ-K101-START (D-022): catalyst reduction, loop heat-up on the start-up heater (not in the boundary) and column start-up are basic-engineering work (D-021)."
---

# Process narrative

> PROPOSED. This narrative describes the intended operation. It is not approved for
> implementation; its review status comes from the records in `reviews/`.

Do not repeat values here: refer to the operating case in `process/flowsheet.yaml`, the
setpoints in `control/loops.yaml` and the trips in `control/cause-effect.yaml`.

## CMP Make-up gas compression

**Purpose.** Raise the make-up synthesis gas from the front end to the loop pressure (P-01).
**Boundaries.** From the battery limit (SG-101, stream S1) to the circulator suction (SG-103,
stream S3, on P-02).
**Normal operation.** The gas passes the suction knock-out drum V-103, is compressed in K-101 and
cooled in E-101 (design case). K-101 takes all the gas the front end delivers: PIC-102 holds its
suction pressure through the drive's speed controller SIC-113; UIC-104 recycles cooled gas when
the flow nears surge. Every K-101 stop closes the discharge shutdown valve XV-116 and the make-up
gas shutdown valve XV-110 (US-116): the trips that stop K-101 close both directly, and any other
stop (package machine trip, power failure, operator stop) through the run status YS-117 (I-102).
The suction side then sees only the settle-out of the discharge volume through UV-104 and the seat
leakage of the closed valves, against which PSV-115 protects it.
**Modes.** Start-up by SEQ-K101-START: with I-102 reset, UV-104 fully open and XV-110 and XV-116
closed, K-101 starts on full recycle at the suction side's own pressure, after a stop at or
above the front end's (the settle-out pressure, or as left by the suction-side pressuring
procedure); XV-116 opens (only with YS-117 reading running) once the
discharge pressure is above the loop pressure, and XV-110 once K-101 has drawn the suction
pressure down to the front end's, so no gas flows back through SG-101 and every stop from then on
trips I-102; then UIC-104 and PIC-102 take over the loading. The sequence starts only with the
suction side at or above the front-end pressure; below it (the first pressuring after
maintenance, or a stop that has left the suction side below the front end through seat or seal
leakage, or through a PSV-115 lift only if its blowdown, not recorded and ASSUMED open with
I-15, exceeds about 10.7 %) the suction-side pressuring procedure, not written (D-021), first
brings it up through XV-110 with K-101 standing (PSV-115 case 3, I-15). I-101 stops the machine on liquid in
V-103.
**Assumptions and open points.** Electric variable-speed drive, one casing (D-010, D-017);
surge control by the vendor; the settle-out pressure (I-10) and the front end's maximum pressure
(I-15) against the 28 barg suction side (D-022).

## SYN Synthesis loop

**Purpose.** Convert the make-up gas to methanol in the boiling-water converter R-101 and
separate the crude methanol (P-02, P-03).
**Boundaries.** From the circulator suction (SG-110 after the make-up gas joins) round the loop
to the HP separator V-101;
out: the purge FG-111 and the crude CM-113.
**Normal operation.** K-102 circulates the loop gas through E-102 to R-101; TIC-205 sets the
converter inlet temperature on the E-102 bypass and PIC-207 the steam drum pressure, which fixes
the converter temperature. LIC-209 feeds the drum. The effluent is cooled in E-102 and E-103 and
separated in V-101; PIC-308 holds the loop pressure by the purge FIC-303.
**Modes.** Start-up needs the catalyst reduced and the loop heated (outside this draft). I-201
and I-202 cut the make-up gas on a hot converter or a low drum level; I-302 stops K-102 and the
make-up gas on a high-high V-101 level.
**Assumptions and open points.** Single-element drum level (three-element at basic
engineering), uncooled spillback (D-018); purge on pressure or on inerts (D-019).

## SEP Crude let-down and LP flash

**Purpose.** Let the crude methanol down from the loop pressure and flash off the dissolved gas
(P-03).
**Boundaries.** From V-101 (CM-113) to the topping column feed (CM-115) and the flash gas FG-114.
**Normal operation.** LIC-307 lets the crude down into V-102; PIC-309 holds the V-102 pressure on
the flash gas and LIC-310 sends the crude on to C-201.
**Modes.** I-301 closes XV-306 on a low-low V-101 level against gas blow-by.
**Assumptions and open points.** The blow-by load on PSV-311 (D-019).

## TOP Topping column

**Purpose.** Strip the dissolved gases and light ends from the crude methanol (P-04).
**Boundaries.** From CM-115 to the stabilised methanol CM-117 and the off-gas FG-116.
**Normal operation.** TIC-402 holds a column temperature on the reboiler steam; PIC-404 holds the
pressure on the off-gas; LIC-405 returns all condensed liquid as reflux; LIC-408 sends the
bottoms to C-202 through P-202A/B.
**Modes.** I-401 stops the reflux pumps on a low-low drum level.
**Assumptions and open points.** Control tray and set point with the rigorous column (D-008).

## REF Refining column and product

**Purpose.** Separate Grade AA methanol from water (P-05).
**Boundaries.** From CM-117 to the product ME-118 and the bottoms water WW-119.
**Normal operation.** TIC-502 holds the stripping temperature on the reboiler steam; PIC-504 the
pressure on the vent; LIC-505 holds the reflux drum level by the reflux and FIC-507 the product
rate, corrected by the operator on AI-509; LIC-508 sends the bottoms water to the battery limit.
**Modes.** I-501 stops the reflux and product pumps on a low-low drum level.
**Assumptions and open points.** Fusel-oil draw (D-008), pressure control of the total condenser
(D-020), cooling of the bottoms water.
