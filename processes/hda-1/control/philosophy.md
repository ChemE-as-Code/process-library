---
# Control philosophy. Schema of this front matter: `cheme schema control_philosophy`.
# Skill control-narrative. S4 (D-026).
schema: cheme/control_philosophy/v1
objectives:
  - id: OBJ-1
    title: Produce the benzene of the operating case at the load set by the operator
    loops: [FIC-103, LIC-102, LIC-606, LIC-202]
  - id: OBJ-2
    title: Protect the heater coil, the reactor and E-101 (reactor inlet temperature, quench, H2/aromatics ratio)
    loops: [TIC-111, TIC-115, FIC-103]
  - id: OBJ-3
    title: Hold the reaction loop pressure and its hydrogen content
    loops: [PIC-205, FIC-108, AIC-210, FIC-211, PIC-301]
  - id: OBJ-4
    title: Keep the benzene on specification and recover the toluene
    loops: [TIC-502, FIC-507, LIC-506, TIC-402, TIC-602, FIC-607]
  - id: OBJ-5
    title: Keep the machines inside their operating range
    loops: [UIC-207, FIC-106, PIC-303]
  - id: OBJ-6
    title: Keep the liquid seals between pressure levels
    loops: [LIC-202, LIC-408, LIC-508, LIC-608]
  - id: OBJ-7
    title: Hold the drum and column pressures
    loops: [PIC-104, PIC-404, PIC-504, PIC-604, LIC-405]
failures:
  - id: F-AIR
    title: Loss of instrument air
    response: "Every actuated valve goes to the fail position drawn on the P&IDs and listed in control/loops.yaml (D-026). Closed: the toluene feed FV-103 and XV-120, the make-up hydrogen FV-108 and XV-121, the fuel TV-111, XV-112 and XV-125, the let-down LV-202 and XV-204, the purge FV-211, PV-301, the steam TV-402, TV-502 and TV-602, the column bottoms and product valves LV-408, LV-506, LV-508, LV-606 and LV-608, PV-604. Open: the fuel bleed XV-126, the depressuring valve XV-209, the anti-surge UV-207 and spillback PV-303, the minimum flow FV-106, the quench TV-115, the vents PV-104 and PV-504, the off-gas PV-404 and the refluxes LV-405, FV-507 and FV-607. The firing and the feed stop and the reaction loop is depressured to the flare; the columns lose their heat and stay on reflux. Restart follows SEQ-START-RXN once air is back."
    loops: [FIC-103, FIC-108, TIC-111, LIC-202, UIC-207, FIC-211, TIC-402, TIC-502, TIC-602]
    sequences: [SEQ-EDP, SEQ-START-RXN]
    interlocks: [I-101, I-102]
  - id: F-POWER
    title: Loss of electric power
    response: "All motors stop: P-101, P-102, K-101, K-102, the reflux and product pumps and PK-201 (all drives electric). The K-101 stop is a machine trip (I-203): the feed is cut at once and the coil flow trip I-101 stops the firing. The columns lose their reflux pumps; the operator closes the steam (TIC-402, TIC-502, TIC-602 to manual) and the column pressures are held by the vents and the relief devices behind them. The control system and the trip logic are on an uninterruptible supply (ASSUMED, D-026). The plant goes to SEQ-TRIP-RXN and is shut down (SEQ-SD-PLANT) if power is not back soon."
    loops: [TIC-402, TIC-502, TIC-602, PIC-404, PIC-504]
    sequences: [SEQ-TRIP-RXN, SEQ-SD-PLANT]
    interlocks: [I-101, I-203]
  - id: F-CW
    title: Loss of cooling water
    response: "E-102 loses its duty: V-101 runs hot and more aromatics go to K-101 with the loop gas; the condensers E-201, E-203 and E-205 and the coolers E-103 and E-207 lose theirs, and the column pressures rise. The operator cuts the load and the column steam at once and shuts the plant down (SEQ-SD-PLANT); the vents PV-404, PV-504 and the relief devices PSV-413, PSV-514 and PSV-615 are the layers behind. Gas detection on the cooling water returns is an S6/S9 item (D-025)."
    loops: [PIC-404, PIC-504, PIC-604, TIC-402, TIC-502, TIC-602, FIC-103]
    sequences: [SEQ-SD-PLANT]
  - id: F-STEAM
    title: Loss of a steam header (LP, MP or HP)
    response: "The column on that header loses its boil-up: C-201 (MP) sends light ends on, C-202 (LP) loses benzene recovery, C-203 (HP) sends toluene with the biphenyl. The reaction loop runs on at reduced load; the benzene product goes to the off-specification tank; if the steam is not back the plant is shut down (SEQ-SD-PLANT)."
    loops: [TIC-402, TIC-502, TIC-602, LIC-506, FIC-103]
    sequences: [SEQ-SD-PLANT]
  - id: F-FUEL
    title: Loss of the natural gas fuel
    response: "The fuel pressure low-low trip I-104 (or the burner management, I-105) stops the firing; the loop keeps circulating and the reactor cools, so the reaction stops. I-104 does not cut the feed: the operator stops the toluene (SEQ-TRIP-RXN). Whether I-104 and I-105 should also cut the feed, as I-101 does, is a question for the HAZOP (S6)."
    loops: [TIC-111, FIC-103]
    sequences: [SEQ-TRIP-RXN]
    interlocks: [I-104, I-105]
  - id: F-H2
    title: Loss of the make-up hydrogen supply
    response: "The loop pressure falls (PIC-205 low alarm) and with it the hydrogen partial pressure; FIC-108 saturates. The operator reduces the load FIC-103 to the hydrogen the PSA recovers and the ratio alarm FFI-217 allows, and shuts the loop down (SEQ-SD-PLANT) if the supply does not come back."
    loops: [PIC-205, FIC-108, FIC-103]
    sequences: [SEQ-SD-PLANT]
  - id: F-K101
    title: Trip of the recycle gas compressor K-101
    response: "I-203 (or I-202 for a carry-over) stops K-101 and cuts the toluene and the make-up hydrogen; the coil flow trip I-101 then stops the firing; UIC-207 opens UV-207 on the machine stop (vendor anti-surge function). The loop is held (SEQ-TRIP-RXN) and depressured if the reactor temperature does not fall (SEQ-EDP)."
    loops: [UIC-207, FIC-103, FIC-108, TIC-111]
    sequences: [SEQ-TRIP-RXN, SEQ-EDP]
    interlocks: [I-101, I-202, I-203]
  - id: F-PSA
    title: Trip of the PSA PK-101 or the tail gas compressor K-102
    response: "The purge is isolated (FV-211 closed, SEQ-TRIP-PSA); the loop runs on without purge while methane builds up over hours; the operator reduces the load if AIC-210 falls and restarts the PSA."
    loops: [AIC-210, FIC-211, PIC-303]
    sequences: [SEQ-TRIP-PSA, SEQ-START-PSA]
unresolved: []
---

# Control philosophy

> PROPOSED. Not approved for implementation; the review status comes from `reviews/`. Loops,
> sequences and trips are defined in `control/loops.yaml`, `control/sequences.yaml` and
> `control/cause-effect.yaml`; this text explains them and does not repeat their values.

## Operating objectives

In order of priority: protect people, the fired heater, the reactor and the machines (OBJ-2,
OBJ-5, OBJ-6), hold the reaction loop (OBJ-3) and the pressures (OBJ-7), then produce at the set
load (OBJ-1) with the benzene on specification (OBJ-4). The operating point is the `design` case
of `process/flowsheet.yaml`; no turndown case exists yet, so the loops are designed for that case
and their behaviour at part load is a review question (D-026).

## Control hierarchy

Three layers, kept apart:

1. **Regulatory control** (the 28 loops of `control/loops.yaml`, one per controller on P-01 to
   P-06) holds the operating point. A loop is never counted as a safeguard.
2. **Sequences** (`control/sequences.yaml`) take the plant between its modes: start-up of the
   reaction loop, of the PSA and of the distillation, normal shutdown, the hold after a loop or
   PSA trip, and emergency depressuring.
3. **Protective functions** (`control/cause-effect.yaml`) act on their own transmitters (the Z
   tags) and their own trip valves (the XV tags) or stop machines, separate from the loops they
   back up. Two trips act through vendor packages: the burner management of H-101 (I-105) and the
   machine protection of K-101 (I-203). The relief devices (`piping/special-items.yaml`) are the
   last layer; their cases are S8's.

The load is set at one point (FIC-103). The toluene is the limiting reactant and the recycle gas
is fixed by the compressor and the loop pressure, so the H2/aromatics ratio follows the load: it
is indicated and alarmed (FFI-217) rather than controlled (D-025, D-026), and the operator acts on
the load. Cascades: PIC-205 onto FIC-108 (loop pressure by the make-up hydrogen), AIC-210 onto
FIC-211 (hydrogen content by the purge). The fresh feed is on the feed drum level (LIC-102) and the
toluene recycle on the toluene column drum level (LIC-606), so the recycle is self-balancing.

## Normal operation and disturbances

- **Load change**: the operator moves FIC-103 in small steps; on a rise the recycle gas and the
  loop pressure are confirmed first, so that the ratio stays above its alarm.
- **Hydrogen consumption and methane make**: the make-up follows the loop pressure, the purge
  follows the hydrogen content; both act on their own flow slaves.
- **Reactor temperature**: the inlet is held by the firing (TIC-111), the outlet rises with the
  conversion; the operator watches TZ-113 and TI-124 and moves the inlet setpoint only inside the
  window of D-021.
- **Fouling of E-101**: H-101 takes the extra duty until its firing limit; the operator watches
  TV-111 and the E-101 outlet temperatures TI-109 and TI-116.
- **Feed composition**: benzene in the fresh toluene passes to the product; heavier impurities end
  in the biphenyl (D-020).
- **Columns**: the reflux on flow and the boil-up on a tray temperature hold each column; the
  operator trims the C-202 reflux from the purity AI-510. The control trays and their setpoints
  come with the column design (S7); the first setpoints are the simulated bottoms temperatures,
  ASSUMED.

## Operator and automatic actions

Automatic: all loops in their normal mode, the anti-surge and spillback loops, the trips and the
abort actions of the sequences. The operator: sets the load, the reactor inlet temperature and the
column refluxes; starts and stops machines and runs the start-up and shutdown sequences step by
step (every start-up step is `by: operator`); removes the start-up bypasses of I-101, I-103,
I-201, I-401, I-501 and I-601 at the step the sequence names; resets every latching trip after the
first-out cause has been found. No trip is reset automatically.

## Equipment and utility failures

The designed responses are in the front matter: loss of instrument air (F-AIR), power (F-POWER),
cooling water (F-CW), a steam header (F-STEAM), the natural gas fuel (F-FUEL), the make-up
hydrogen (F-H2), and the trips of K-101 (F-K101) and of the PSA or K-102 (F-PSA). Each valve's fail
position is chosen so that the failure goes to the safe side of its own hazard (D-026): feed, fuel
and hydrogen closed; steam closed; let-down and bottoms valves between pressure levels closed;
refluxes, quench, minimum flow, anti-surge and spillback open; vents and the depressuring valve
open. On a loss of instrument air the reaction loop is therefore depressured to the flare
(XV-209 fails open, review 2026-11-04-basic-pids#29).

## Assumptions and open points

Recorded in `DESIGN.md` D-026: the ASSUMED level setpoints, pad and vent pressures, minimum flow,
surge margin, tray setpoints, start-up rates, temperatures and step times and trip delays; the fail
positions (for the HAZOP to confirm); the connections the sequences need but the P&IDs do not show
(nitrogen purge points and loop vents, off-specification routing of the products, PSA start-up
routing, valve position feedback); the vendor scope of the heater burner management, the K-101
machine protection, the PSA cycle and the vacuum package; whether I-104 and I-105 should also cut
the feed; the uninterruptible supply of the control system. Trip setpoints, sensor voting and SIL
are the HAZOP / LOPA's (S6).
