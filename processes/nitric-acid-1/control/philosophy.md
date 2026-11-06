---
# Control philosophy. Schema of this front matter: `cheme schema control_philosophy`.
# Skill control-narrative. D-019 (first P&IDs, 2026-11-05).
schema: cheme/control_philosophy/v1
objectives:
  - id: OBJ-1
    title: Make the acid of the operating case at the load the operator sets on the air
    loops: [FIC-107, FFIC-201, LIC-102, PIC-104]
  - id: OBJ-2
    title: Keep the ammonia-air mixture at its design strength, never rich
    loops: [FFIC-201, FIC-107]
  - id: OBJ-3
    title: Absorb the NOx at the design pressure and acid strength
    loops: [PIC-611, FIC-505, FIC-509, LIC-506, LIC-510]
  - id: OBJ-4
    title: Meet the tail-gas N2O and NOx limits (tertiary reactor window, SCR dosing)
    loops: [TIC-301, FIC-603, TIC-604]
  - id: OBJ-5
    title: Keep the machine train inside its operating range
    loops: [UIC-110, UIC-401]
  - id: OBJ-6
    title: Keep the liquid seals between pressure levels and the liquids out of the machines
    loops: [LIC-305, LIC-506, LIC-510]
failures:
  - id: F-AIR
    title: Loss of instrument air
    response: "Every actuated valve goes to the fail position drawn on the P&IDs (control/instrument-list.yaml, D-019). Closed: the ammonia trip valves XV-101, XV-203, XV-204 and the ratio valve FV-201 (the burner goes out), the evaporator valves LV-102 and PV-104, the level valves LV-305, LV-506 and LV-510 and the shutdown valve XV-507 (the liquid seals hold), the SCR ammonia XV-602 and FV-603, the LP steam TV-604, the bypass TV-301 and the expander trip valve XV-610. Open: the air guide vanes FV-107 and the anti-surge valves UV-110 and UV-401 (the machines are protected), the process water FV-505, the secondary air FV-509 and the absorber pressure valve PV-611. With XV-610 closed and PV-611 open the high-pressure system is held by XV-610. The motor keeps running and K-102 is on full recycle against the closed expander inlet, which the package protection does not see. ZSC-610 shows XV-610 back on its closed seat while the train logic still commands it open, so I-603 trips the train within seconds (a 2 s confirmation, ASSUMED, against contact bounce and vibration once XV-610 has left its seat; the 30 s delay is for the opening stroke only, D-026), and I-602 follows and holds XV-610 closed (its solenoid de-energised) until it is reset: an air dip of any length that closes XV-610 does not let it reopen by itself (D-025, D-026). A dip too short to close XV-610 onto its seat is not seen by ZSC-610 and is left to the HAZOP (O-9). The full-recycle time trip I-401 (ZSC-610 and FZ-206) is behind it (D-024). Restart once air is back: a new train start and SEQ-START-BURNER, with its I-401 permissive (the time on full recycle is kept over a stop shorter than the cool-down, D-025). Because I-603 trips within seconds, the I-401 time carried after an F-AIR in operation is small and the permissive does not force a cool-down; the cool-down (60 min, ASSUMED) applies only when the carried I-401 time is high, as after minutes on full recycle in SEQ-START-BURNER S1-S2 (D-026)."
    loops: [FFIC-201, FIC-107, UIC-110, UIC-401, PIC-611]
    sequences: [SEQ-START-BURNER]
    interlocks: [I-201, I-401, I-602, I-603]
  - id: F-POWER
    title: Loss of electric power
    response: "The train motor stops: the train trips (I-602), the ammonia is cut (XV-101, XV-203, XV-204) and XV-610 isolates the expander. P-101A/B stop; V-101 fills from what is left in the gas train. The control system and the trip logic are on an uninterruptible supply (ASSUMED, D-019). The HP system settles out behind the check valve CV401 and XV-610; the low-pressure system behind CV105. Restart: SEQ-START-BURNER."
    loops: [LIC-305, PIC-611]
    sequences: [SEQ-START-BURNER]
    interlocks: [I-602]
  - id: F-CW
    title: Loss of cooling water
    response: "E-105 and E-107 lose their duty and C-101 its lower coils: the gas to K-102 and the absorber runs hot and wet, the absorption falls and the stack NOx rises (AI-614). The operator cuts the ammonia (load down on FIC-107 and FFIC-201) and shuts the burner down if the water is not back; a cooling-water low-pressure trip of the burner is a question for the HAZOP (D-019)."
    loops: [FIC-107, FFIC-201]
  - id: F-CHW
    title: Loss of the chilled-water loop (C-101 upper coils and E-101)
    response: "E-101 loses its heat source: PIC-104 falls, the ammonia vapour to the burner falls and FFIC-201 opens FV-201 to its limit; the mixture goes lean, the gauze cools and TZ-207 trips the burner (I-203) if the ammonia is not restored. The absorber upper trays run warm (more NOx in the tail gas). The circulation pump of the loop is in the chilled-water package (D-020)."
    loops: [PIC-104, FFIC-201]
    interlocks: [I-203]
  - id: F-TRAIN
    title: Machine train trip
    response: "I-602: XV-610 closes (no expander overspeed), the ammonia trip valves close and the burner goes out; the anti-surge valves open. The absorber stays pressurised; PSV-404 protects it if XV-610 and PV-611 are closed with K-102 coasting down. The train is also tripped when K-102 has run on full hot recycle (no forward flow) longer than its limit: the accumulated time since it last ran at its forward-flow temperature or cooled down stopped, which at a start of a cooled train is the time since train start; a stop shorter than the cool-down time does not reset it (I-401, D-023, D-024, D-025). An uncommanded closure of XV-610 also trips the train (I-603, D-025)."
    loops: [UIC-110, UIC-401, PIC-611]
    interlocks: [I-401, I-602, I-603]
    sequences: [SEQ-START-BURNER]
unresolved:
  - "Ignition burner of R-101 and its fuel (hydrogen torch), and the purge volume of SEQ-START-BURNER: vendor (D-019)"
  - "Flammability limit of NH3 in air at 520 kPa(a) and 462 K for the I-201 trip point (open input O-7)"
  - "Expander bypass for start-up and on an expander trip; until then SEQ-START-BURNER starts through X-101 (D-018, D-021, O-9)"
---

# Control philosophy

> PROPOSED. Not approved for implementation; the review status comes from `reviews/`. Loops,
> sequences and trips are defined in `control/loops.yaml`, `control/sequences.yaml` and
> `control/cause-effect.yaml`; this text explains them and does not repeat their values.

## Operating objectives

The plant makes the acid of the design case (OBJ-1) at a load the operator sets on the air
(FIC-107); everything else follows the air. The first safety objective is the ammonia-air
mixture (OBJ-2): it is held at its design strength by a ratio controller and kept away from the
flammable range by trips that do not share an instrument with that controller. The absorption
is held at its design pressure and strength (OBJ-3), the tail gas inside the tertiary reactor's
window (OBJ-4), the machine train inside its map (OBJ-5) and the liquid seals between the two
pressure levels intact (OBJ-6).

## Control hierarchy

Regulatory control (15 loops) holds the operating point; the burner start-up runs as a sequence
(SEQ-START-BURNER, on a train just started), and a relight on a running train with forward flow
as SEQ-RESTART-BURNER (D-024); eleven trips (I-101 to I-603) act on dedicated trip valves (XV) and machine
stops, never on a control valve, and the relief devices PSV-105, PSV-111, PSV-215, PSV-316, PSV-404 and
PSV-616 are the layer behind them (cases per device in `piping/special-items.yaml`, D-021). The machine protection of the train is the package's and reaches the
plant as one trip (I-602); the plant's own K-102 full-recycle time trip (I-401) and the XV-610
uncommanded-closure trip (I-603) end in the same trip (D-024, D-025). A regulatory loop is never counted as a safeguard.

## Normal operation and disturbances

Air leads, ammonia follows: FIC-107 moves the air and FFIC-201 brings the ammonia with it at the
design ratio, so a load change never passes through a richer mixture. The evaporator makes the
vapour on its level (LIC-102) and pressure (PIC-104) loops. The heat-recovery train runs
uncontrolled except for the tertiary reactor inlet temperature (TIC-301 on the E-103 tail-gas
bypass). The absorber pressure is held by back-pressure control at the expander inlet
(PIC-611); the acid strength by the process water (FIC-505) and the tail-gas oxygen by the
secondary air (FIC-509), both trimmed by the operator from the analysers. The SCR ammonia is
dosed on flow (FIC-603) and trimmed from the stack NOx.

## Operator and automatic actions

Automatic: the loops, the trips and the anti-surge controls. The operator sets the load and the
ratio, trims the process water, the secondary air and the SCR ammonia from the analysers
(AI-514, AI-512, AI-614), blows down the evaporator, runs SEQ-START-BURNER and
SEQ-RESTART-BURNER and resets every latched trip after the cause is cleared. The one exception
is the start-up bypasses of I-202 and I-203: the operator resets the I-202 latch in step S1 of
SEQ-START-BURNER (no air yet), and the I-203 latch in S1 or in step R1 of SEQ-RESTART-BURNER (a
cold gauze), while the cause is still there, because the bypass masks the cause at the latch
input until the sequence removes it (D-023, D-024, D-025). I-202 has no bypass in
SEQ-RESTART-BURNER: there it is a permissive and is reset after its cause is cleared. Cascades of the analysers onto FIC-505, FIC-509 and
FIC-603 are left for detail design (D-019).

## Equipment and utility failures

The designed responses are F-AIR (instrument air), F-POWER (electric power), F-CW (cooling
water), F-CHW (the chilled-water loop between the absorber and the evaporator) and F-TRAIN (a
machine train trip) in the front matter. Loss of LP steam only stops the SCR ammonia vaporiser
(TIC-604 low, FIC-603 falls); loss of boiler feed water is the boiler package's.

## Assumptions and open points

Fail positions, setpoints that are not a design-case value, trip delays and the start-up rates
are ASSUMED (D-019). Open: the trip point of I-201 (O-7), the ignition burner, the expander
bypass, the K-102 recycle (hot or cooled), a V-101 high-high level protection, the start-up
heat source of E-101 and the C-102 acid cooling (D-018 to D-020); the K-102 full hot recycle
limit (the I-401 retentive timer, ASSUMED 15 min, and its reset after 10 min of forward flow
or a 60-min stop), a train-start inhibit and the other restart rules of a hot train and the
TI-402 alarm setting from the train vendor, the I-603 opening-stroke delay (30 s) and
closed-position confirmation (2 s) from the XV-610 valve vendor, an air dip too short to close XV-610 onto its seat (HAZOP), the
SEQ-RESTART-BURNER R1 timeout, the FFZ-205
NH3 flow cutoff, the deviation alarm bands of FZ-206 and FFZ-205 and the I-202/I-203 start-up
bypass timers (all ASSUMED, D-023, D-024, D-025, D-026, O-9); sensor voting and SILs are the HAZOP / LOPA's.
