---
# Control philosophy. Schema of this front matter: `cheme schema control_philosophy`.
# Skill control-narrative.
schema: cheme/control_philosophy/v1
objectives:
  - {id: OBJ-1, title: "Hold the stacks at the measured operating point (current density, anolyte flow and temperature)", loops: [JIC-101, JIC-201, FIC-101, FIC-201, TIC-111, TIC-211]}
  - {id: OBJ-2, title: Feed the cathodes with CO2 at the measured feed ratio and hold their back-pressure, loops: [FIC-102, FIC-202, PIC-121, PIC-221, LIC-122, LIC-222]}
  - {id: OBJ-3, title: Deliver the CO at the boundary pressure, loops: [PIC-131, PIC-231]}
  - {id: OBJ-4, title: "Skid A: run the campaign on one fill and end it at H, as the anolyte reaches the pH threshold", loops: [AI-101]}
  - {id: OBJ-5, title: "Skid B: hold the anolyte at its hydroxide and carbonate setpoints by dosing, bleed and make-up", loops: [AIC-201, FIC-203, LIC-201]}
failures:
  - id: F-AIR
    title: Loss of instrument air
    response: TV-x11 fail open (full tempered-water flow), FV-x02 closed (no CO2), PV-x21 open (the cathode is not pressurised against the compressor), LV-x22 closed (no gas to the effluent), PV-x31 closed (open point), XV-x33 closed (no tail gas to the oxidiser), Skid B LV-201 and FV-203 closed. Without CO2 the stacks make H2, and with XV-x33 closed the cathode gas has no outlet; the operator trips the current (SEQ-A-TRIP, SEQ-B-TRIP).
    loops: [TIC-111, TIC-211, FIC-102, FIC-202, PIC-121, PIC-221, LIC-122, LIC-222, PIC-131, PIC-231, LIC-201, FIC-203]
    sequences: [SEQ-A-TRIP, SEQ-B-TRIP]
  - id: F-POWER
    title: Loss of electric power
    response: The rectifiers, pumps and compressors stop; the current, and with it the gas production, stops at once. The CO2 purge and the oxidiser need power or a safe purge source (open point).
    loops: [JIC-101, JIC-201, FIC-101, FIC-201, AIC-201]
    sequences: [SEQ-A-TRIP, SEQ-B-TRIP]
  - id: F-CW
    title: Loss of the tempered water (cooling in operation, heating when idle)
    response: "In operation TIC-x11 saturates open; the stack outlet temperature rises at about 2.2 kW of stack heat until TSHH-x12 trips the current (I-105, I-205). On an idle skid in frost the anolyte cools: TIC-x11's low alarm calls the operator to restore the heating, keep P-x01 circulating or drain the loop (SEQ-A-DRAIN, SEQ-B-DRAIN; DESIGN.md D-052)."
    loops: [TIC-111, TIC-211]
    interlocks: [I-105, I-205]
    sequences: [SEQ-A-DRAIN, SEQ-B-DRAIN]
  - id: F-FLOW
    title: Loss of anolyte recirculation
    response: The low-low flow trips the current (I-106, I-206); a low-low level also stops the pump (I-102, I-202).
    loops: [FIC-101, FIC-201]
    interlocks: [I-106, I-206, I-102, I-202]
  - id: F-GAS
    title: CO or H2 released at an open skid
    response: The detector trips the current (the rectifier's AC feeder opened at SDB-1), closes the CO2 feed and the tail-gas trip valve XV-x33 and stops the compressor (I-103, I-104, I-203, I-204); the open, naturally ventilated skid has no fan (DESIGN.md D-050). Nobody approaches until the detectors are clear, and then with a personal CO monitor and a check for CO2 at grade and at the low points. The cathode gas train stays isolated with its CO and H2 until the leak is found and the trips are reset; then it is purged to the oxidiser (SEQ-A-GAS, SEQ-B-GAS).
    interlocks: [I-103, I-104, I-203, I-204]
    sequences: [SEQ-A-GAS, SEQ-B-GAS]
  - id: F-TG
    title: A flame held on the tail-gas arrester, or the oxidiser not firing
    response: "The arrester's temperature on its unprotected side (TSHH-x33; I-109, I-209) or the oxidiser's burner management system (I-110, I-210) closes XV-x33 on the protected side of the detonation arrester FA-x33; with the tail gas closed the train has no outlet, so the current trips, the compressor stops and the CO2 feed closes, as on a gas release (SEQ-A-GAS, SEQ-B-GAS; DESIGN.md D-054). The check valve and the vendor's burner arrester and burner management system (EN 746-2, pre-purge) are the other barriers against a flame or air entering TG-x01."
    interlocks: [I-109, I-110, I-209, I-210]
    sequences: [SEQ-A-GAS, SEQ-B-GAS]
  - id: F-DOSE
    title: "Skid B: loss of the KOH dose"
    response: AIC-201 alarms as the pH falls; the day tank's low-low level stops P-202 (I-208); at pH 12.2 the current trips (I-201).
    loops: [AIC-201]
    interlocks: [I-201, I-208]
unresolved:
  - "pH basis: the probe reads activity pH; the duty model's criterion (pH 12), the trip value it runs to (pH 12.2, D-058) and Skid B's setpoint (pH 13.7) are concentration-basis pH at an ionic strength of about 1 mol/L. The alarm, trip and setpoint values need an offset or a calibration against titrated anolyte before they are set (H01-A109); the 0.2 pH trip margin is then checked against the probe's uncertainty."
  - "The fail position of PV-x31 against the PSA package's own pressure protection (vendor)."
  - "Relief: K-x31 (a positive-displacement compressor) and the cathode gas train have no relief device drawn; the relief study is open (D-017)."
  - "The reservoir vent O2V-x01 carries the anode O2 with any H2 that crosses the membrane; the H2 in O2 is not measured. A gas analyser on the vent, or a dilution, is a HAZOP question."
  - "The CO2 purge and the oxidiser after a power loss (F-POWER)."
  - "The detonation arrester's EU-type examination for the actual tail gas (H2, CO, CO2, H2O) at its temperature and pressure, its certified burning time (the TSHH-x33 set point and XV-x33's closing time follow from it), the detonation pressure rating of TG-x01 and the oxidiser vendor's integration (DESIGN.md D-054)."
  - "SIL screening and HAZOP of every trip (control/cause-effect.yaml, sil: null)."
---

# Control philosophy

> PROPOSED. Not approved for implementation; the review status comes from `reviews/`. Loops,
> sequences and trips are defined in `control/loops.yaml`, `control/sequences.yaml` and
> `control/cause-effect.yaml`; this text explains them and does not repeat their values.

The two pilot skids of #330 (DESIGN.md D-007) have the same control, Skid A with the 1xx tags
on P-01 and Skid B with the 2xx tags on P-02. Skid B adds the dosing, the bleed and the make-up.

## Operating objectives

1. OBJ-1: the stacks run at the operating point of the measured series: the current density
   by the rectifier current (JIC-x01), the anolyte flow per area (FIC-x01) and 25 °C
   (TIC-x11). Every result of the design (FE, WDE, U, kWh/kg) assumes this point (D-014).
2. OBJ-2: the cathodes get CO2 at the measured feed ratio (FIC-x02, fresh CO2 with the PSA
   recycle), the cathode gas is held at its back-pressure (PIC-x21) and dried of condensate
   (LIC-x22).
3. OBJ-3: the CO leaves at the boundary pressure (PIC-x31).
4. OBJ-4: Skid A runs on one fill until the anolyte reaches the pH threshold at the end of the
   campaign (D-009); nothing is manipulated on pH, the pH is shown with an alarm (AI-101).
5. OBJ-5: Skid B holds the anolyte at its setpoints (D-010): the dose follows the current and
   AIC-201 trims it, the bleed (FIC-203) carries the carbon out, the make-up on level
   (LIC-201) closes the water balance.

## Control hierarchy

Regulatory control (the loops) holds the operating point. Sequences take a skid from its fill
to a running campaign and from a trip or the end of the run to its drain. Protective functions
are the interlocks of the cause and effect list; a regulatory loop is never counted as a
safeguard. Several trips share their transmitter with a loop (FIC-x01, AIC-201): the HAZOP
has to judge that. Skid B's level trip has its own transmitter (LIA-202).

## Normal operation and disturbances

The rectifier runs at constant current: the stack voltage follows the stacks as they age or
as the anolyte changes. The anolyte changes over the campaign on both skids:

- Skid A: the anolyte pH falls from fresh 1 M KOH to the threshold over H as the hydroxide is
  consumed and carbonate builds up (V proportional to H, D-009). The only control action on
  pH is the end of the run.
- Skid B: after the fill the anolyte moves to its steady state within a few residence times
  (about 27 h, D-010). The dose base rate follows the current (feedforward); AIC-201 trims it
  for the drift of WDE and of the co-ion crossover that the model holds constant. The trim is
  not simulated: the model doses at the fixed steady-state rate.

**The pH basis.** The probe measures activity pH. The duty model's pH is a concentration-basis
pH (an ideal-solution pH at an ionic strength of about 1 mol/L, core ADR 0043), so the
criterion (pH 12, D-003), the trips at pH 12.2 (I-101, I-201; D-058) and the Skid B setpoint
(pH 13.7) are not meter readings. Before any
alarm, trip or setpoint is set, the probe is calibrated against titrated anolyte (hydroxide and
carbonate, as the measured series was) or an offset is determined; until then the values in
`control/` are the model's. The threshold is a design criterion, not a corrosion limit.

## Operator and automatic actions

Automatic: the loops in their normal modes, the trips, the dosing and bleed permissive I-207.
Operator: the fill, the start-up steps and the current ramp (SEQ-x-START), the humidification
water by hand (FI-x03), the reset of a trip once its cause is found, the end of a campaign at H
(SEQ-x-STOP, then SEQ-x-DRAIN), the weekly refill of the Skid B day tank.

## Equipment and utility failures

See `failures` in the front matter: instrument air (F-AIR), electric power (F-POWER),
the tempered water (F-CW), the anolyte recirculation (F-FLOW), a gas release (F-GAS), a
flame at the tail-gas arrester or the oxidiser not firing (F-TG) and, on Skid B, the KOH dose
(F-DOSE).

## Assumptions and open points

Every setpoint, alarm and trip value is ASSUMED or taken from the duty model (each with its
source in the YAML). The open points are in `unresolved` in the front matter: the pH basis,
the fail position of PV-x31, relief, H2 in the anode O2, the purge after a power loss, the
tail-gas arrester's type examination and burning time, SIL and HAZOP.
