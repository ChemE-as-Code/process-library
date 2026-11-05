---
# Control philosophy. Schema of this front matter: `cheme schema control_philosophy`.
# Skill control-narrative. Basic stage (D-007 to D-017).
schema: cheme/control_philosophy/v1
objectives:
  - id: OBJ-1
    title: Load carriers at the rate of their cargo plan, up to 12,000 m3/h
    loops: [FIC-4101, FIC-4102]
  - id: OBJ-2
    title: Hold the tank pressure in its band with the BOG compressors, the flare only above their capacity
    loops: [PIC-1110, PIC-1111, PIC-7101]
  - id: OBJ-3
    title: Keep the in-tank pumps and the BOG compressors inside their operating range
    loops: [FIC-2111A, FIC-2111B, FIC-2111C, FIC-2111D, FIC-2112, FIC-3111A, FIC-3111B, FIC-3111C, FIC-3111D, FIC-3112, UIC-7104A, UIC-7104B, UIC-7104C]
  - id: OBJ-4
    title: Keep the compressor suction cold and dry
    loops: [TIC-7103, LIC-7102]
failures:
  - id: F-AIR
    title: Loss of instrument air
    response: "Every actuated valve goes to its fail position (control/loops.yaml, the P&IDs): the ESD and ERS valves and the fill valves close (loading and filling stop), PV-1110 and PV-1111 close, the minimum-flow and anti-surge valves open, FV-4101/4102 stay where they are. The tank pressure then rises on the boil-off: the compressors keep running on their guide vanes until the high-high trip I-203 / I-303 acts, and PSV-2131A/B / PSV-3131A/B are the last protection."
    loops: [PIC-1110, PIC-1111, FIC-4101, FIC-4102, UIC-7104A]
    interlocks: [I-203, I-303, I-501]
  - id: F-POWER
    title: Loss of electric power (BC Hydro grid)
    response: "The in-tank pumps and the BOG compressors stop. Loading stops (the carrier is told through the ship-shore link, on its own uninterruptible supply, ASSUMED). The tanks boil off into the vapour header and PIC-1110 vents to the storage and loading flare through PV-1110 (on the instrument air reserve). The control system, the ESD logic and the ship-shore link are on uninterruptible supplies (ASSUMED, D-020)."
    loops: [PIC-1110]
    interlocks: [I-203, I-303, I-501, I-601]
  - id: F-BOG
    title: Trip of the BOG compressors
    response: "The tank pressure rises; PIC-1110 moves into its upper split and opens PV-1110 to the flare (the design case of the storage and loading flare, D-017). At loading the operator reduces the rate or stops (ESD-1 if the pressure reaches its high-high trip)."
    loops: [PIC-1110, PIC-7101]
    interlocks: [I-203, I-303, I-701, I-702]
  - id: F-LINK
    title: Loss of the ship-shore link
    response: "ESD-1 of the berth (I-501 / I-601): loading pumps stop, the shore ESD valve closes against the surge limit, the carrier's ESD trips."
    interlocks: [I-501, I-601]
unresolved: []
---

# Control philosophy

> PROPOSED. Not approved for implementation; the review status comes from `reviews/`. Loops,
> sequences and trips are defined in `control/loops.yaml`, `control/sequences.yaml` and
> `control/cause-effect.yaml`; this text explains them and does not repeat their values.

## Operating objectives

The terminal takes the whole rundown of the trains into the tanks and loads carriers to their
cargo plan (OBJ-1) while it keeps the tanks in their narrow pressure band (OBJ-2). The flare
is the reserve of the BOG system, not part of normal control. The machines stay in their
operating range by their own minimum-flow and anti-surge loops (OBJ-3), and the compressors
take cold, dry gas (OBJ-4).

## Control hierarchy

Regulatory control holds the operating point: the tank vapour header pressure (one split-range
controller for both tanks), the loading rate per line and the machine protections. Sequences
change modes: holding with the lines circulating (SEQ-HOLD), loading a carrier (SEQ-LOAD),
starting a compressor (SEQ-BOG-START) and the response to an ESD (SEQ-ESD). The protective
layer is the cause and effect list: the independent tank level and pressure trips, ESD-1 and
ESD-2 of each berth, the drum level trip and the machine protection. No regulatory loop is
counted as a safeguard.

## Normal operation and disturbances

The rundown is not controlled here: the trains set it, and the terminal takes it into whichever
tank the operator lines up (top or bottom fill, from the rundown density against the tank
profile). In holding the boil-off and the vapour displaced by the rundown are compressed by
one machine; at loading the carrier's return comes back on its own compressor and two machines
run. A rising header pressure loads the compressors first and only then opens the flare; a
falling pressure admits make-up gas before the vacuum trips.

## Operator and automatic actions

The operator lines up the fill and the circulation, starts and stops the loading pumps and the
compressors by case, and ramps the loading rate with the carrier. The trips act automatically
and are reset by hand once the cause is cleared.

## Equipment and utility failures

See F-AIR, F-POWER, F-BOG and F-LINK in the front matter.

## Assumptions and open points

Setpoints are ASSUMED. The surge on an ESD closure and the vapour-arm capacity were estimated
in DESIGN.md D-023: the 25 s closure keeps the surge inside the line design, and a return
above one vapour arm's capacity is burnt on board or the loading rate is reduced; both are to
be confirmed against supplier and carrier data.
