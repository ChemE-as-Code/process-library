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
  - id: OBJ-5
    title: Keep the spill sumps dry, so spilled LNG never meets standing water, and empty the drain and knock-out drums
    loops: [LC-8103, LC-8106, LIC-5111, LIC-6111, LIC-8101]
failures:
  - id: F-AIR
    title: Loss of instrument air
    response: "The instrument-air header low-low trip I-804 (PZT-8123A/B/C on IA-8001, 2oo3, set above the pressure at which the spring-return actuators start to stroke) acts first: it stops the loading pumps and trips both carriers through XS-5100 / XS-6100 and the trains' rundown through XS-1100, and initiates ESD-1 of both berths (I-501 / I-601) and the rundown trip I-102. The liquid-path fail-closed valves (XV-5101 / XV-6101, XV-4101 / XV-4102, the arm isolations, the fill valves XV-1102 / XV-1103 and the battery-limit valves XV-1111..1114) hold on a non-return valve and a local air accumulator, so they move only after the pumps and the trains have been tripped, and then close no faster than their speed controllers allow (25-30 s at the berths, at least 30 s on the rundown; D-023, D-028); the ERS valves are on the arm vendor's hydraulic unit and do not move. Loading and filling stop without a surge. The other valves go to their fail position (control/loops.yaml, the P&IDs): the vapour arm XV-5122 / XV-6122 and the circulation return XV-2123 / XV-3123 close, the vapour return switch goes to the tanks (XV-4135 / XV-4136 open, XV-4131 / XV-4132 close), PV-1110, PV-1111 and the SIS vent XV-1115 close (XV-1115 still opens on I-203 / I-303 from its own air accumulator, energise-to-trip), the minimum-flow, anti-surge and recycle isolation valves open, FV-4101/4102 stay where they are. The BOG compressors do not keep running: their fail-closed suction valves XV-7121A-C leave the open position and I-705A-C stop every running machine (discharge XV-7123A-C closed, recycles open). No vent opens on the failure itself, so the tanks are not depressurised; the tank pressure rises on the boil-off and the vapour displaced before the fill stopped, I-203 / I-303 open XV-1115 to the storage and loading flare at high-high pressure, and PSV-2131A/B/C / PSV-3131A/B/C are the last protection (their relief case includes this utility failure, D-025). Restart only once the header is back: reset I-804, then the berths and the compressors by their sequences. An air loss at the platform end of the ~2.45 km jetty air main (a rupture on the trestle or the platform) need not pull IA-8001 below the I-804 trip: there the vapour arm isolations XV-5122 / XV-6122, which have no accumulator, are the first valves to move, and ZSO-5122 / ZSO-6122 losing the open position during a liquid transfer trips ESD-1 of the berth (I-501 / I-601) at the start of their stroke, while the liquid-path valves still hold on their accumulators (review 2026-11-05-basic-design-5 #2, D-030); voted transmitters at the platform end are a detail-engineering hold (D-030)."
    loops: [PIC-1110, PIC-1111, FIC-4101, FIC-4102, UIC-7104A]
    interlocks: [I-804, I-501, I-601, I-102, I-705A, I-705B, I-705C, I-203, I-303]
  - id: F-POWER
    title: Loss of electric power (BC Hydro grid)
    response: "The in-tank pumps and the BOG compressors stop. Loading stops (the carrier is told through the ship-shore link, on its own uninterruptible supply, ASSUMED). The tanks boil off into the vapour header and PIC-1110 vents to the storage and loading flare through PV-1110 (on the instrument air reserve). The control system, the ESD logic and the ship-shore link are on uninterruptible supplies (ASSUMED, D-020). The ERS valves and couplers (D-016, review 2026-11-05-basic-design-5 #3 and its adversarial check): the arm vendor's hydraulic power unit keeps its accumulator charged, and the two solenoid channels that hold each ERS valve open (de-energise-to-trip, 2oo2) are fed from two independent UPS, channel A from UPS A and channel B from UPS B on separate distribution (ASSUMED; review 2026-11-05-basic-design-6 #2, D-032), so a loss of the grid does not close the ERS valves while the pumps coast down; the couplers are energise-to-release and do not release on any power loss. The loss of either supply (XA-5130A / B, XA-6130A / B) during a liquid transfer trips ESD-1 (I-501 / I-601) at once, while the other channel still holds the ERS valves open, so the pumps are stopped first and no single supply fault closes the ERS valves at full flow; both supplies lost within the ESD-1 response, two independent faults, is the residual case (5) of D-023, a relief case of PSV-5131 / PSV-6131. On a drift-off the couplers release on a timer after the ERS close command, not on the ERS valves' proven-closed position (D-016). The air compressors are outside the battery limit; their loss is F-AIR."
    loops: [PIC-1110]
    interlocks: [I-203, I-303, I-501, I-601, I-507, I-607]
  - id: F-BOG
    title: Trip of the BOG compressors
    response: "The tank pressure rises; PIC-1110 moves into its upper split and opens PV-1110 to the flare (the design case of the storage and loading flare, D-017). At loading the operator reduces the rate or stops (ESD-1 if the pressure reaches its high-high trip)."
    loops: [PIC-1110, PIC-7101]
    interlocks: [I-203, I-303, I-701, I-702]
  - id: F-LINK
    title: Loss of the ship-shore link
    response: "ESD-1 of the berth (I-501 / I-601): loading pumps stop, the shore ESD valve closes against the surge limit, the carrier's ESD trips. A carrier ESD valve closing while its link signal is lost (link healthy-looking or lost at the same time, review 2026-11-05-basic-design-9 #7) is answered by the back-pressure trip at the arms: PZT-n181 / n184 at the outboard ends of the two liquid arms, 1oo2 at 5.0 barg (I-502 / I-602), stop the pumps, trip the carrier and close XV-n101, so the carrier's manifold stays below its 10 barg (ASSUMED) design (D-016, D-023 (6), D-036). After any ESD-1 the berth header and the arms stay open to the carrier's closed manifold valve; the arm thermal reliefs at 8.0 barg keep that shared section below the carrier's limit, and the operator lets it down into the drain drum after the reset (SEQ-ESD S2, D-039)."
    sequences: [SEQ-ESD]
    interlocks: [I-501, I-601, I-502, I-602]
  - id: F-TRESTLE-LEAK
    title: Leak on the trestle side of a shore ESD valve after ESD-1
    response: "After ESD-1 only the stem and bonnet seals of XV-n101, XV-4107 and XV-4103 are left on the trestle side (D-036). A leak there, found by the header bay detection and CCTV, is ended by SEQ-LINE-EMPTY: the I-n01 close outputs of XV-4101 / XV-4102 / XV-4107 are overridden for that sequence only (key-protected, every loading pump proven stopped), the leaking line is opened through the bottom-of-line platform crossover and the other line to a tank, and site N2 from the station at its tank end displaces it in ~2.3 h at ~4,000 Nm3/h; the leak is fed for ~3.5 h at most, inside the 240 min PFP of the header bay and the 40 m3 kept in T-8102. On low site N2 the displacement goes on at the reduced rate (at least ~3,500 Nm3/h keeps both limits); with no N2 entering (the displaced return flow on the line-in-service meter falling away), the leaking line is held pressurised and isolated under its N2 (crossover and return closed, the N2 blocks open behind the check valve and the 4.5 barg regulator), never vented and never left open to the full line, and the hold lasts until 3.5 h after the ESD-1 at most, by when the displacement is resumed (the other tank, the N2 back-up) (D-036, D-039, D-039.9)."
    sequences: [SEQ-ESD, SEQ-LINE-EMPTY]
    interlocks: [I-501, I-601, I-201]
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
starting a compressor (SEQ-BOG-START), changing a tank's fill point make-before-break
(SEQ-FILL-CHANGE), the response to an ESD (SEQ-ESD) and emptying a leaking trestle line back to a
tank with N2 (SEQ-LINE-EMPTY, F-TRESTLE-LEAK). The protective layer is the cause and effect list:
the independent tank level and pressure trips, ESD-1 and ESD-2 of each berth, the carrier's
back-pressure trip at the arms (I-502 / I-602, F-LINK), the drum level trips, the sump trips and
the machine protection. One override exists, on the ESD-1 close outputs of XV-4101 / XV-4102 /
XV-4107 for SEQ-LINE-EMPTY only (key-protected, with every loading pump proven stopped, removed by
the SIS itself). No regulatory loop is counted as a safeguard: where a level controls a pump, its
alarms and trips are on an independent transmitter (LZT-n112, LZT-8105, LZT-8113, LZT-8119).

Both spill sumps are kept dry (D-018, D-037.15 (a), D-039): rain collects in a floor pocket and a
pump on the pocket level takes it out (P-8102 in T-8101, P-8103 in T-8102, OBJ-5); LNG detection
that never stands under water (a probe above the pump's start level, a fast probe in the pump's
discharge and, at T-8101, gas at the pit rim) locks the pump out, and the sump's high level on the
independent transmitter is a transfer hold, its high-high an ESD-1 of the transferring berth.

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
and are reset by hand once the cause is cleared. Occupancy rules of the layout (D-018 (o),
D-035.14 (e), D-037.6; SEQ-LOAD S4): while a transfer runs on either berth nobody works at the
south end of the platform (the drain pumps and drums, the header bay's valves and strainers) or on
the jetty sump deck A9, and the arm work positions are occupied for connection, cooldown and
disconnection only; the strainers' differential pressure is read in the control room.

## Equipment and utility failures

See F-AIR, F-POWER, F-BOG, F-LINK and F-TRESTLE-LEAK in the front matter.

## Assumptions and open points

Setpoints are ASSUMED. The surge on an ESD closure and the vapour-arm capacity were estimated
in DESIGN.md D-023: the 25 s closure keeps the surge inside the line design, and a return
above one vapour arm's capacity is burnt on board or the loading rate is reduced; both are to
be confirmed against supplier and carrier data. The order "pumps (or trains) tripped first,
valves closed after, at a set speed" holds for the loading lines, the rundown and an
instrument-air failure alike (D-023, D-028; F-AIR).
