---
# Control philosophy. Schema of this front matter: `cheme schema control_philosophy`.
# Skill control-narrative.
schema: cheme/control_philosophy/v1
objectives:
  - id: OBJ-1
    title: Produce the ammonia of the operating case at the load set by the operator
    loops: [FIC-1002, FIC-1006, FIC-1201, LIC-2005]
  - id: OBJ-2
    title: Protect the catalysts (steam to carbon ratio, shift and converter inlet temperatures)
    loops: [FIC-1006, TIC-1103, TIC-1207, TIC-1601, TIC-1803]
  - id: OBJ-3
    title: Keep the synthesis gas on specification (H2/N2 ratio, CO2 slip, inerts)
    loops: [AIC-1804, FIC-1201, FIC-1407, TIC-1408, FIC-1905]
  - id: OBJ-4
    title: Fire the reformer furnace safely and efficiently
    loops: [PIC-1101, PIC-1107, AIC-1109, FIC-1110]
  - id: OBJ-5
    title: Keep the machines out of surge
    loops: [UIC-1202, UIC-1703, UIC-1802]
  - id: OBJ-6
    title: Keep the liquid seals between pressure levels
    loops: [LIC-1307, LIC-1405, LIC-1609, LIC-1903, LIC-1907]
  - id: OBJ-7
    title: Balance steam raising, process steam and export
    loops: [LIC-2201, LIC-2202, PIC-2203, PIC-2206]
failures:
  - id: F-AIR
    title: Loss of instrument air
    response: Every control valve goes to the fail position of control/loops.yaml (D-030). The feed gas, fuel, process air, letdown and product valves close; the process steam, combustion air damper, anti-surge, cooling water, BFW, make-up to the deaerator and converter bypass valves open. The trip valves close (the C&E). The plant comes down without an operator action; restart follows SEQ-START-REF.
    loops: [FIC-1002, FIC-1006, PIC-1101, FIC-1110, FIC-1201, UIC-1202, UIC-1703, UIC-1802, TIC-1803, LIC-1903, LIC-2201]
    sequences: [SEQ-TRIP-FE, SEQ-START-REF]
    interlocks: [I-101, I-102, I-103, I-105, I-106, I-107]
  - id: F-POWER
    title: Loss of electric power
    response: All machines stop (all drives are electric, D-016) - K-101, K-102, K-103, K-501, K-502, K-701, the solvent pumps and P-801. The loss of the fans trips the firing through I-102 or the burner management; the loss of steam raising and BFW leads to I-101. The plant is shut down; the steam drum must not be refilled hot without the boiler supplier's procedure.
    loops: [PIC-1107, LIC-2201, FIC-1407]
    sequences: [SEQ-TRIP-FE, SEQ-SD-PLANT]
    interlocks: [I-101, I-102]
  - id: F-CW
    title: Loss of cooling water
    response: The cooling water loops open fully; the loop separator warms, the K-701 condenser and the machine coolers lose duty. The operator reduces the load and shuts the loop down (SEQ-SD-PLANT) before the relief devices on the loop and the refrigeration side are reached.
    loops: [TIC-1306, TIC-1408, TIC-1608]
    sequences: [SEQ-SD-PLANT]
  - id: F-STEAM
    title: Loss of process steam
    response: I-101 stops the feed gas and the process air; the firing is reduced by hand and the tubes are kept above the condensation temperature or changed over to nitrogen (SEQ-TRIP-FE).
    loops: [FIC-1006, PIC-2203]
    sequences: [SEQ-TRIP-FE]
    interlocks: [I-101]
  - id: F-K501
    title: Trip of the synthesis gas compressor K-501
    response: The front-end gas goes to the front-end vent (not drawn, D-030); the loop is held on circulation by K-502 with the converter cooling slowly; the operator reduces the front-end load and decides between restart and shutdown (SEQ-TRIP-FE, step S3 onwards).
    loops: [UIC-1703, FIC-1002, TIC-1803]
    sequences: [SEQ-TRIP-FE, SEQ-SD-PLANT]
  - id: F-K701
    title: Trip of the refrigeration compressor K-701
    response: The chiller and the product flash lose their cold; the separator warms and less ammonia condenses, so the loop pressure rises. The operator reduces the load and raises the purge; if K-701 cannot be restarted the loop is shut down (SEQ-SD-PLANT).
    loops: [LIC-1908, FIC-1905, LIC-2005]
    sequences: [SEQ-SD-PLANT]
unresolved: []
---

# Control philosophy

> PROPOSED. Not approved for implementation; the review status comes from `reviews/`. Loops,
> sequences and trips are defined in `control/loops.yaml`, `control/sequences.yaml` and
> `control/cause-effect.yaml`; this text explains them and does not repeat their values.

## Operating objectives

In order of priority: protect people, the catalysts and the machines (OBJ-2, OBJ-5, OBJ-6), keep
the synthesis gas on specification (OBJ-3), fire the furnace safely (OBJ-4), then produce at the
set load (OBJ-1) and balance the steam (OBJ-7). The operating point is the `design` case of
`process/flowsheet.yaml`; no turndown case exists yet, so the loops are designed for that case
and their behaviour at part load is a review question (D-030).

## Control hierarchy

Three layers, kept apart:

1. **Regulatory control** (the loops of `control/loops.yaml`) holds the operating point. A loop is
   never counted as a safeguard.
2. **Sequences** (`control/sequences.yaml`) take the plant between its modes: start-up of the
   front end, of the CO2 removal and of the loop, normal shutdown and the hold after a trip.
3. **Protective functions** (`control/cause-effect.yaml`) act on their own transmitters (the Z
   tags) and their own valves (the XV tags), separate from the loops they back up. The S3a draft
   of I-104 acted on the control valve of LIC-1307; S4 removed that effect (D-030). The relief
   devices (`piping/special-items.yaml`) are the last layer; their cases are S8's.

The load is set at one point (FIC-1002) and the steam and air follow as ratios; the slow
composition loop of the synthesis loop (AIC-1804) trims the air ratio. Cascades: TIC-1103 onto
PIC-1101 (firing), AIC-1109 onto FIC-1110 (excess air), AIC-1804 onto FIC-1201 (H2/N2).

## Normal operation and disturbances

- **Load change**: the operator moves FIC-1002; the steam and air follow through their ratios.
  Steam leads on a rise and gas leads on a fall, so the steam to carbon ratio is never below its
  setpoint during the change (lead-lag, D-030).
- **Natural gas composition**: a heavier gas lowers the steam to carbon ratio at a fixed mass
  ratio; the ratio of FIC-1006 is set with a margin, and the operator adjusts it from the gas
  analysis (no gas analyser on the feed, D-030).
- **Catalyst ageing**: the shift and converter inlet setpoints (TIC-1207, TIC-1601, TIC-1803) are
  moved by the operator over the catalyst life.
- **Inerts and H2/N2**: inerts build up slowly; the operator raises the purge (FIC-1905) when the
  loop pressure rises at constant load. AIC-1804 corrects the H2/N2 ratio over the loop's hold-up
  time.
- **Fouling of the waste heat boilers and coolers**: the bypasses (TIC-1207, TIC-1601) and the
  cooling water valves absorb it until their valves saturate; the operator watches the valve
  positions.

## Operator and automatic actions

Automatic: all loops in their normal mode, the anti-surge loops, the trips and the trip-driven
steps of SEQ-TRIP-FE. The operator: sets the load, the ratios and the purge; moves temperature
setpoints with the catalyst age; starts and stops machines and runs the start-up and shutdown
sequences step by step (every start-up step is `by: operator`); grants the timed start-up bypasses
of I-105 and I-107; resets every latching trip after the first-out cause has been found. No trip
is reset automatically except the I-104 alarm.

## Equipment and utility failures

The designed responses are in the front matter: loss of instrument air (F-AIR), power (F-POWER),
cooling water (F-CW), process steam (F-STEAM) and the trips of K-501 (F-K501) and K-701 (F-K701).
Each valve's fail position is chosen so that the failure goes to the safe side of its own
hazard (D-030): fuel and feed closed, steam and cooling open, let-down valves between pressure
levels closed, anti-surge open, the converter bypass open (cooler feed).

## Assumptions and open points

Recorded in `DESIGN.md` D-030: the ASSUMED level setpoints, surge margins, furnace draft, trip
delays and start-up rates; the fail positions (for the HAZOP to confirm); the connections the
sequences need but the P&IDs do not show (start-up nitrogen, front-end vent to flare, converter
start-up heater); burner management; three-element drum level control and a drum low-low trip;
machine protection inside the vendor packages; no loop pressure control and no feed gas
analyser; no turndown case. SIL screening is the HAZOP's (S6).
