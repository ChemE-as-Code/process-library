---
# Control philosophy. Schema of this front matter: `cheme schema control_philosophy`.
# Skill control-narrative. D-021.
schema: cheme/control_philosophy/v1
objectives:
  - {id: OBJ-1, title: Take all the make-up gas the front end delivers and keep both compressors out of surge, loops: [PIC-102, SIC-113, UIC-104, UIC-203]}
  - {id: OBJ-2, title: Hold the converter inside the catalyst window (inlet temperature and shell boiling temperature), loops: [TIC-205, PIC-207, LIC-209]}
  - {id: OBJ-3, title: Hold the loop pressure and its inerts by the purge, loops: [PIC-308, FIC-303]}
  - {id: OBJ-4, title: Keep the liquid seals between pressure levels, loops: [LIC-307, LIC-310, LIC-408, LIC-508]}
  - {id: OBJ-5, title: Make Grade AA methanol and a clean bottoms water, loops: [TIC-402, TIC-502, LIC-505, FIC-507]}
  - {id: OBJ-6, title: Hold the drum and column pressures, loops: [PIC-309, PIC-404, PIC-504, LIC-405]}
failures:
  - id: F-AIR
    title: Loss of instrument air
    response: "Every actuated valve goes to the fail position drawn on the P&IDs and listed in control/instrument-list.yaml (D-021). Closed: the make-up gas shutdown valve XV-110, the K-101 discharge shutdown valve XV-116, the purge FV-303, the crude let-down LV-307 and XV-306, LV-310, the column steam TV-402 and TV-502, the bottoms LV-408 and LV-508, the product FV-507. Open: the anti-surge UV-104 and UV-203, the converter bypass TV-205, the steam PV-207, the BFW LV-209, the depressuring XV-304, the vents PV-309, PV-404 and PV-504, the refluxes LV-405 and LV-505. The make-up gas stops, the loop depressures to the HP flare header (XV-304 fail open), the converter cools, the columns lose their heat and stay on reflux. Air failure does not stop K-101 (electric drive): with XV-110 and XV-116 closed it runs isolated in full recycle through the fail-open UV-104 and E-101 (still on cooling water), held out of surge, until the operator stops it; its discharge is not dead-headed while UV-104 is open, and K-101 running against the closed XV-116 with the recycle not open is PSV-111's case. XV-304 and the vents open at the same moment: a plant-wide air failure is a simultaneous flare load for the relief study. The column vent PV-504 and the column PSVs go to the LP flare header, not the HP one XV-304 depressures into (D-022). At the same time the reboiler steam valves TV-402 and TV-502 fail closed while the vents PV-404 and PV-504 fail open: the columns cool and go towards vacuum with an open path to the fuel gas and LP flare headers. The check valves CV-116 (FG-116) and CV-532 (VG-532) stop gas being drawn back from those headers, including PSV-413's blow-by gas on the LP header, and the column systems are designed for full vacuum (D-022); the header back pressures are for the flare study (I-13)."
    loops: [PIC-102, UIC-104, UIC-203, TIC-205, PIC-207, LIC-209, FIC-303, LIC-307, TIC-402, TIC-502]
  - id: F-POWER
    title: Loss of electric power
    response: "All drives stop: K-101, K-102 and the column pumps (electric drives ASSUMED, D-017). Without K-102 the converter has no flow while the shell stays at its boiling temperature; the make-up gas stops with K-101. The K-101 run status YS-117 drops and I-102 closes the discharge shutdown valve XV-116 and the make-up gas shutdown valve XV-110 (both de-energised to close), so the loop inventory and the front end are isolated from the K-101 suction side as on a C&E trip and PSV-115 sees only the settle-out and the seat leakages (D-022); the front end then has no outlet through the plant and relies on its own pressure control and relief (outside the boundary, I-15). The columns lose their reflux pumps; the operator closes the steam (TIC-402 and TIC-502 to manual) and the column pressures are held by the vents and the relief devices behind them. The control system and the trip logic are on an uninterruptible supply (ASSUMED)."
    loops: [TIC-402, TIC-502, PIC-404, PIC-504]
    interlocks: [I-102]
  - id: F-CW
    title: Loss of cooling water
    response: "E-101, E-103 and the condensers E-201 and E-203 lose their duty: the K-101 discharge and the V-101 inlet run hot (TI-107, TI-301 high alarms), methanol stays in the recycle gas and the column pressures rise. The operator cuts the make-up gas and the column steam and shuts the plant down; the vents and PSV-413 and PSV-513 are the layers behind. The refining column's cooling water failure is likely the largest relief case of the plant (D-020)."
    loops: [PIC-404, PIC-504, TIC-402, TIC-502]
  - id: F-BFW
    title: Loss of boiler feed water
    response: "The V-104 level falls (LIC-209 low alarm); the low-low trip I-202 cuts the make-up gas so the converter stops reacting before the shell runs dry."
    loops: [LIC-209]
    interlocks: [I-202]
  - id: F-K102
    title: Recycle circulator trip
    response: "The loop flow stops; the make-up gas raises the loop pressure unless K-101 is stopped (PSV-111 on the K-101 discharge is the relief layer). The V-101 high-high level trip I-302 stops K-102 together with K-101 and XV-110; a K-102 machine trip from its own package should do the same, which is not in the C&E yet and is an open point for the HAZOP (D-021)."
    loops: [PIC-308, PIC-102]
    interlocks: [I-302]
  - id: F-HEAT
    title: Loss of reboiler heat (LP steam failure, TV-402 or TV-502 closed) with the condensers running
    response: "The column overheads condense faster than they are made and the column pressure falls; the pressure loops have no gas make-up (PV-404 and PV-504 vent, and their check valves CV-116 and CV-532 stop any back-flow from the headers), so the columns, condensers, reflux drums and reboilers are pulled towards vacuum. The steam side of E-202 and E-204 goes to vacuum too once TV-402 or TV-502 is closed: the steam left in it condenses to a small amount of condensate (about 0.3 % of the steam-side volume at 450 kPa(a)), so it goes to vacuum without flooding, and the check valves CV-439 and CV-542 on the trap outlets stop condensate being drawn back from the header into it (which would flood it and give water hammer on restart). C-201, E-201, E-202, V-201, C-202, E-203, E-204 and V-202 (process and reboiler steam sides) and their overhead, reflux and reboiler piping are designed for full vacuum (ASSUMED, D-022), so no vacuum breaker or gas make-up is drawn; the operator cuts the cooling water and the feed. A nitrogen or fuel-gas make-up split range with the vents is the basic-engineering alternative (D-022). The steam side floods in a different case, in normal operation: at low load with TV-402 / TV-502 throttled, or with a closed valve passing, steam keeps entering below the condensate header pressure, the traps stall and condensate backs up over the tubes, which degrades TIC-402 / TIC-502; draining it, by a pumping trap or a condensate pot with a pump into the header, with a vacuum breaker on the steam side, is open (I-14). On restart the steam is opened slowly, with any condensate held up in the steam side drained first (start-up sequence, not written yet)."
    loops: [TIC-402, TIC-502, PIC-404, PIC-504]
unresolved:
  - "Start-up, shutdown and abnormal sequences (control/sequences.yaml) are not written in this first issue (D-021), except the K-101 start-up SEQ-K101-START that the interlock I-102 needs (D-022)."
  - "The K-102 trip to K-101 / XV-110 interlock and the depressuring on I-201 are questions for the HAZOP (D-021)."
  - "Trip setpoints, delays, voting and SIL are for the HAZOP / LOPA."
---

# Control philosophy

> PROPOSED. Not approved for implementation; the review status comes from `reviews/`. Loops,
> sequences and trips are defined in `control/loops.yaml`, `control/sequences.yaml` and
> `control/cause-effect.yaml`; this text explains them and does not repeat their values.

## Operating objectives

The plant converts all the make-up gas the front end delivers (OBJ-1) into Grade AA methanol
(OBJ-5). The converter is held inside the catalyst window by its inlet temperature and the
boiling temperature on its shell (OBJ-2). The loop pressure and its inerts are held by the purge
(OBJ-3). The liquid seals between the pressure levels (loop, LP flash, columns) are never lost
(OBJ-4), and the drums and columns run at their design pressures (OBJ-6).

## Control hierarchy

Regulatory control: the loops of `control/loops.yaml` in the DCS. The load is set upstream: the
make-up compressor follows the front end on its suction pressure (PIC-102), the loop follows on
its pressure (PIC-308 setting the purge FIC-303), the let-down and the columns follow on their
levels. Protective functions: the trips of `control/cause-effect.yaml` (I-101 to I-501) on
separate sensors and shutdown valves, and the machine protection inside the compressor
packages. Mechanical relief (`piping/special-items.yaml`) is the last layer. A regulatory loop
is never counted as a safeguard.

## Normal operation and disturbances

A change of the front-end rate moves the K-101 speed (PIC-102) and, after the loop has
responded, the purge (PIC-308). A falling catalyst activity shows as a rising loop pressure and
a falling converter duty; the steam drum pressure (PIC-207) stays at its D-003 value inside the
V-104 design pressure, and raising it over the catalyst life is not part of this issue (D-018,
I-11). The inerts (AI-305) follow the purge. The columns follow their feed on level; the
product rate FIC-507 is set from the feed and corrected on the water analyser AI-509.

## Operator and automatic actions

Automatic: all loops in their normal modes, the anti-surge controllers, the trips. The operator
sets the steam drum pressure, decides between purging on pressure or on inerts (PIC-308 or
AI-305), sets the product rate, starts and stops the spare pumps, depressures the loop by hand
(HS-304) and resets every trip after the cause is cleared.

## Equipment and utility failures

Loss of instrument air (F-AIR), power (F-POWER), cooling water (F-CW) and boiler feed water
(F-BFW), a circulator trip (F-K102) and a loss of reboiler heat with the condensers running
(F-HEAT, the vacuum case of the columns) are described in the front matter with the loops and
trips involved.

## Assumptions and open points

Fail positions, trip delays and the K-102 to K-101 interlock are ASSUMED or open (D-021);
setpoints, voting and SIL are for the HAZOP / LOPA. Of the sequences only the K-101 start-up
SEQ-K101-START is written (D-022); the other start-up, shutdown and abnormal sequences are not
written yet (D-021).
