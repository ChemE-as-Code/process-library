---
# Process narrative. Schema of this front matter: `cheme schema narrative`. Skill
# control-narrative. Each section gets a heading "## <id> <title>" below.
schema: cheme/narrative/v1
sections:
  - id: STORAGE
    title: Rundown, storage and in-tank pumps
    equipment: [T-2101, T-3101, P-2101A, P-2101B, P-2101C, P-2101D, P-2102, P-3101A, P-3101B, P-3101C, P-3101D, P-3102]
    blocks: [STORAGE, TK, PUMPS]
    cases: [average, loading, holding]
    modes: [normal]
    loops: [FIC-2111A, FIC-2111B, FIC-2111C, FIC-2111D, FIC-2112, FIC-3111A, FIC-3111B, FIC-3111C, FIC-3111D, FIC-3112]
    interlocks: [I-101, I-201, I-202, I-203, I-204, I-301, I-302, I-303, I-304]
  - id: TRANSFER
    title: Trestle loading and circulation lines
    equipment: []
    blocks: [TRANSFER, TRL]
    cases: [loading, holding]
    modes: [normal]
    loops: [FIC-4101, FIC-4102]
    sequences: [SEQ-HOLD]
  - id: JETTY
    title: Berths and loading arms
    equipment: [LA-5101, LA-5102, LA-5103, LA-5104, LA-6101, LA-6102, LA-6103, LA-6104, D-5101, P-5101, D-6101, P-6101]
    blocks: [JETTY, ARMS]
    cases: [loading]
    modes: [normal, abnormal]
    sequences: [SEQ-LOAD, SEQ-ESD]
    interlocks: [I-501, I-502, I-503, I-601, I-602, I-603]
  - id: BOG
    title: Tank vapour header, BOG compression and the flare
    equipment: [D-7101, K-7101A, K-7101B, K-7101C, D-8101, FL-8101]
    blocks: [BOG, DSH, COMP]
    cases: [average, loading, holding]
    modes: [normal, startup]
    loops: [PIC-1110, PIC-1111, PIC-7101, TIC-7103, LIC-7102, UIC-7104A, UIC-7104B, UIC-7104C]
    sequences: [SEQ-BOG-START]
    interlocks: [I-701, I-702]
unresolved: []
---

# Process narrative

> PROPOSED. This narrative describes the intended operation. It is not approved for
> implementation; its review status comes from the records in `reviews/`.

Values are in the operating cases of `process/flowsheet.yaml`, the setpoints in
`control/loops.yaml` and the trips in `control/cause-effect.yaml`.

## STORAGE Rundown, storage and in-tank pumps

The four trains run their subcooled LNG down a common header into one of the two
full-containment tanks, filled from the top or the bottom according to the density of the
rundown against the tank's density profile, so that the tank does not stratify (rollover).
Each tank carries four submerged-motor loading pumps and one circulation pump in pump columns
through the roof; each pump has its own minimum-flow return. A tank that reaches its high-high
level stops receiving; both full stop the rundown at the battery limit.

## TRANSFER Trestle loading and circulation lines

Two loading lines and two vapour return lines run about 2 km over the trestle to the loading
platform. While no carrier loads, one circulation pump sends LNG out along line A and back
along line B through the platform crossover, which keeps the lines cold against their heat
ingress. At loading both lines carry LNG to the berth that loads, at a rate the operator ramps
with the carrier.

## JETTY Berths and loading arms

Each berth has four arms: two liquid, one hybrid that normally runs as the third liquid arm,
and one vapour arm, which is connected first and disconnected last. The arms are leak tested
and purged with nitrogen, cooled down, and only then loaded at the full rate. Each arm has an
emergency release system; ESD-1 stops the loading through the ship-shore link and ESD-2
releases the arms. After loading the arms are drained to the jetty drain drum and purged.

## BOG Tank vapour header, BOG compression and the flare

The tank boil-off, the vapour the rundown displaces and the carrier's return vapour meet in
the tank vapour header. An LNG spray cools the return vapour before the suction drum, and the
BOG compressors send the gas back to the trains' fuel and end-flash system. The header pressure
loads the compressors first and opens the storage and loading flare only beyond them; make-up
gas protects the tanks against vacuum.
