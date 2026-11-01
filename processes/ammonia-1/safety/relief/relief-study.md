# Relief study (preliminary): the eight relief valves of ammonia-1

Status: **proposed, by agent** (S8 of `runs/plan.md`, DESIGN.md D-033). No relief engineer or
HAZOP team has reviewed it. It names, per drawn relief device, the cases that can demand it,
the relieving rate of each case where the repository allows a calculation, the case claimed to
govern, and what is missing. It does not size orifices, inlet lines, tail pipes or the flare
header, and it certifies nothing (skill `relief-scenarios`: the governing case, the credited
scenarios, set pressure, size and exemptions are for the relief study proper and the HAZOP team).

Numbers are from `cheme run scripts/relief_loads.py` (design case of `process/flowsheet.yaml`,
the simulated streams of D-026, `equipment/equipment-list.yaml`, `layout/equipment-placement.yaml`;
thermo 0.6.1 for latent heats and ideal-gas heat capacities). The script prints every input it
uses; nothing here is entered by hand except the arithmetic marked "own arithmetic".

## Basis

| item | basis |
|---|---|
| devices | the eight `SpringLoadedGlobeSafetyValve`s on the P&IDs, listed in `piping/special-items.yaml` (PSV-1212 P-103, PSV-1310 P-104, PSV-1513 P-106, PSV-1704 P-108, PSV-1911 and PSV-1912 P-110, PSV-2010 P-111, PSV-2210 P-113) |
| set pressure | the design pressure of the protected item (equipment list, D-032), as the single-valve set pressure. ASSUMED: the MAWP comes with the vessel design and may be higher |
| relieving pressure | set + 10 % accumulation for process cases, set + 21 % for the fire case (single valve; ASME BPVC VIII-1 / API 520 Part I as commonly cited; the code text was not read here) |
| case method | causes and governing-case rules of CCPS, *Guidelines for Engineering Design for Process Safety*, chapter 14 and 15.1.7, as summarised in the skill `relief-scenarios`: one device is sized for its largest single credible case; cases are not added; a trip is not credited in place of a device; a control valve is taken in the position that makes the load worse; favourable control action is not credited |
| fire | pool fire on the wetted wall, Q = C F A^0.82 W (A in m2; C = 43 200 with adequate drainage and fire fighting, 70 900 without; API Std 521, 6th ed. 2014, 4.4.13.2.4, SI form as published in secondary sources: the standard itself was not read). F = 1 (bare, no insulation credit). Wetted area: the whole shell up to 7.6 m above grade and the bottom head (2:1 ellipsoidal, 1.084 D2), base at grade as placed (z = 0 in the placement). ASSUMED: no liquid level is set yet, so the wetted area is the upper bound. Drainage is not designed, so both values are given and the undrained one is the one claimed |
| boiling component | V-201 and C-302: water; V-502, V-701: ammonia (pure component, ASSUMED: the dissolved gases and the aMDEA are ignored) |
| process cases | rated flow = the design-case stream of the source, without a margin for the machine curve (the vendor's curve at the relieving pressure replaces it) |
| tube rupture | double-ended break of one tube: two bores of 14.83 mm (19.05 mm OD, 2.11 mm wall, ASSUMED: no tube layout exists), choked ideal-gas orifice flow, discharge coefficient 1 (conservative) |
| gas blow-by | a level valve fully open after loss of liquid level: IEC 60534-2-1 compressible flow at choked conditions, W = 27.3 Kv (2/3) sqrt(x p1 rho1), x = (k/1.4) xT, xT = 0.7 ASSUMED (globe valve); ideal-gas density. The valves are not sized, so the result is given per unit Kv, and an indicative value is added from the Kv of the normal liquid duty at 70 % opening (ASSUMED, non-flashing liquid sizing) |

## Summary

Relieving rates in kg/h. "governing" is the case claimed for the device; "n.c." = not
calculated (reason in the device section).

| device | protects | set barg (ASSUMED) | discharge | cases and rates | governing case | required capacity |
|---|---|---|---|---|---|---|
| PSV-1212 | K-101 discharge, PA-1022 to XV-1204 (K-101 and E-104 at 38.5 barg) | 38.5 | atmosphere (PA-1054) | blocked discharge 67 184 | blocked discharge: XV-1204 closed by I-101/I-103 with the anti-surge blow-off FV-1202 failed closed (A11) | **67 184** (air, 429 K) |
| PSV-1310 | V-201 and the gas train back to R-102 (V-201 33 barg) | 33.0 | flare (PG-1055) | blocked outlet 139 409; fire 3 876 / 6 361 | blocked outlet: XV-1604 closed by I-106 (or K-501 stopped) with the front end still fed (A16, A17) | **139 409** (raw synthesis gas, M 15.0, 313 K) |
| PSV-1513 | C-302 with E-303, V-302 and the E-202 aMDEA side (2.5 barg) | 2.5 | atmosphere (CO2-1076) | LV-1405 blow-by 355 per Kv (indicative 127 000); blocked vent 74 528; overhead condenser failure up to 34 400 extra; E-202 tube rupture 5 181; fire 5 209 / 8 549 | gas blow-by from C-301 through a fully open LV-1405 (A18) | **not established**: 355 kg/h per Kv of LV-1405 (and its bypass), indicative 127 000; at least 74 528 (blocked vent) |
| PSV-1704 | K-501 discharge to the check valve CV1088, and the loop through it (K-501 159.5 barg) | 159.5 | flare (PG-1090) | blocked loop with full make-up 65 958 | loop pressure rising with the make-up still running: K-502 stopped, dead converter or loss of loop cooling (A26) | **65 958** (make-up gas, M 8.7, 313 K) |
| PSV-1911 | V-501 and the cold end of the loop (V-501 161 barg) | 161.0 | flare (PG-1119) | fire: heat input 1.35 / 2.21 MW, rate n.c. (supercritical); make-up case taken by PSV-1704 | fire | **not established**: needs a transient supercritical fire calculation |
| PSV-1912 | V-502 (26.5 barg) | 26.5 | flare (PG-1120) | LV-1903 blow-by 1 566 per Kv (indicative 16 000); PV-1906 closed 997; fire 5 299 / 8 697 | gas blow-by from V-501 through a fully open LV-1903 (A28) | **not established**: 1 566 kg/h per Kv of LV-1903 (and its bypass), indicative 16 000 |
| PSV-2010 | V-701 (26.5 barg) | 26.5 | flare (AG-1134) | fire 6 101 / 10 014; blow-by and blocked vapour outlet: removed by rating | fire | **10 014** (ammonia vapour, 33.1 bar(a), 343 K) |
| PSV-2210 | MP steam header SM-1140 and U-801 (49.5 barg) | 49.5 | atmosphere through a silencer (SM-1143) | process steam blocked 92 834; export blocked 60 099; E-502 tube rupture 17 725 of loop gas | process steam valve FV-1006 closed (stuck, or isolated) at full steam raising (A36) | **92 834** (MP steam, 673 K) |

## Devices

### PSV-1212, K-101 discharge (P-103)

Where: on PA-1054, branching from PA-1022 upstream of the discharge check valve. Protected:
the K-101 last stage, PA-1022, the E-104 process air coil and PA-1023 up to XV-1204 (all 38.5
barg, D-032).

- **Blocked discharge** (claimed governing): XV-1204 closes on I-101 or I-103 (and A10 proposes
  it also closes on a K-101 trip) while K-101 keeps running; FV-1202 (anti-surge blow-off of UIC-1202,
  fails open) is taken as stuck closed, the position that makes the load worse. Rate: the rated
  process air flow S13, 67 184 kg/h at 36.0 bar(a), 429 K, M 28.97, k 1.39. The flow on the
  compressor curve at 42.4 barg (relieving) is lower; the vendor's curve replaces this value.
- **Exemption to check**: a centrifugal compressor whose maximum discharge pressure (surge at
  maximum speed) stays below 38.5 barg cannot overpressure the section, and the case falls away
  (CCPS 14.2.2.1, system rated above the source). The K-101 maximum discharge pressure is the
  vendor's (A12); until it is known the case stands.
- Fire: a compressor discharge pipe holds no liquid; not a case for this valve.

### PSV-1310, V-201 and the front-end gas train (P-104)

Where: on PG-1055 from V-201 to the flare header. Protected without a block valve in between:
V-201 (33 barg), E-203, E-202 tube side, R-202, E-401 tube side, E-201, R-201, E-105 process
side, R-102 (38 barg), and downstream C-301 (33 barg), the E-401 shell (35) up to XV-1604. The
design pressures fall along the train by about the normal pressure drop, so a valve at the low
end set at 33 barg keeps the upstream items within their design pressure at the relieving flow
(ASSUMED: pressure drops at the relieving flow equal the design-case ones).

- **Blocked outlet** (claimed governing): XV-1604 closes on I-106 (methanator high-high
  temperature), which does not trip the feed (A16), or K-501 stops. The sources keep feeding:
  natural gas at 4500 kPa(a) (44 barg, S1), MP process steam at 4600 kPa(a), K-101 air. All
  exceed 33 barg (A17). Rate: the whole front-end gas flow at the V-201 gas outlet, S24
  139 409 kg/h (M 15.04, k 1.37, 313 K); the condensate keeps leaving on LV-1307.
- Fire on V-201: 96.8 m2 wetted; 1.84 MW drained / 3.01 MW undrained; 3 876 / 6 361 kg/h of
  steam at 40.9 bar(a). Smaller than the blocked outlet.
- **Finding R-1 (high): the K-501-stop case is not covered below V-201.** With XV-1604 open and
  K-501 stopped, R-401 (32 barg), E-402 (31.5), V-401 (31) and X-401 (31) are pressurised up to
  the PSV-1310 relieving pressure, 36.3 barg at V-201 with no flow downstream to drop it. That
  exceeds their design pressure plus 10 % accumulation (34.1 barg for V-401). Either a relief
  valve at the low end (V-401 or the X-401 outlet, set at 31 barg; D-028 already lists V-401
  among the devices not drawn), or a design pressure of these items at or above 33 barg, or a
  front-end vent to flare under pressure control (A16). For the team; nothing was changed.

### PSV-1513, CO2 regenerator C-302 (P-106)

Where: on CO2-1076 from C-302 to atmosphere. Protected: C-302, E-303, V-302 and the E-202 aMDEA
side through AM-1049/1050/1051 (all 2.5 barg; no block valve drawn between them).

- **Gas blow-by through LV-1405** (claimed governing): C-301 loses its sump level and LV-1405
  (fails closed) is stuck open or opened; raw synthesis gas at 3100 kPa(a) flows through E-301 into
  C-302. I-105 (LZ-1406 closing XV-1406) is not credited for the device (CCPS 4.4.2; skill
  `safeguard-crediting`). Rate: 355 kg/h per unit Kv of the fully open valve (S24 gas, 31 bar(a),
  rho 17.9 kg/m3). LV-1405 is not sized; from the normal rich-solvent duty (1 313 m3/h on the
  ASSUMED 18 m3 per t CO2 of D-009, SG 1.04 ASSUMED, 28.5 bar drop) its Kv is about 251 and,
  at 70 % opening, 358 fully open: **indicative 127 000 kg/h**. Degassing of the rich solvent in
  the valve makes the real liquid-duty valve larger, so this is not an upper bound. A manual
  bypass of LV-1405 (block and bypass valves are not drawn yet) would add its own capacity
  (CCPS 14.2.3.3).
- Blocked CO2 vent: PV-1505 (fails open) stuck closed with E-202 at full duty: all the vent gas,
  S28 74 528 kg/h at 150 kPa(a).
- Overhead condenser failure (cooling water lost on E-303) with PV-1505 at its normal opening:
  the water vapour no longer condensed adds at most 34 400 kg/h (own arithmetic: the whole
  20.4 MW reboiler duty Q15 as steam at 4.04 bar(a), 2 132 kJ/kg; an upper bound, the stripping
  steam rate is the licensor's, I-06). What the vent valve then passes at the higher pressure is
  not established.
- E-202 tube rupture (A42): low/high design pressure 2.5/34.5 = 0.07, far from any rating
  exemption; process gas S21 (32 bar(a), 507 K) through two tube bores: 5 181 kg/h.
- Fire on C-302: 182 m2 wetted; 3.09 / 5.06 MW; 5 209 / 8 549 kg/h of steam at 4.0 bar(a).
- **Finding R-2 (high): blow-by and tube rupture discharge hydrogen-rich gas to atmosphere.**
  The governing case puts raw synthesis gas (61 mol% H2, CO 0.4 mol%) out of CO2-1076, a vent to
  atmosphere designed for CO2. The discharge needs a dispersion and ignition assessment (A22) or
  routing to the flare; the relief rate depends on the Kv of LV-1405, which must be sized first.

### PSV-1704, K-501 discharge (P-108)

Where: on PG-1090 to the flare, upstream of the discharge check valve CV1088 on PG-1088.
Protected: the K-501 last stage and aftercooler, PG-1088 (159.5 barg) and, through the check
valve in its forward direction, the synthesis loop (V-501 161 barg is its lowest rated item;
E-504 161.5, E-505 162, E-503 163). Because PSV-1704 is set below every loop item and no block
valve is drawn between K-501 and the loop, a make-up excess relieves here first.

- **Blocked loop with full make-up** (claimed governing, A26): K-502 stops, the converter dies
  (catalyst, low inlet temperature) or the loop loses its cooling (cooling water failure, A37) so
  that the make-up is no longer converted and condensed, while K-501 keeps running. No loop
  pressure control exists (D-030). Rate: the make-up flow S38, 65 958 kg/h (M 8.69, k 1.40,
  313 K at 146 bar(a)). Purge and product would reduce it at their normal openings; they are not
  credited.
- As for K-101, the K-501 maximum discharge pressure (vendor) may remove the case if it stays
  below 159.5 barg.
- If isolation valves are later drawn between K-501 and the loop, they must be locked open or
  the loop needs its own make-up relief (CCPS 14.5.2).

### PSV-1911, ammonia separator V-501 (P-110)

Where: on PG-1119 from V-501 to the flare. Protected: V-501 (161 barg) and the cold end of the
loop connected to it.

- Blocked loop with full make-up: relieved by PSV-1704 (set 159.5 barg, below this valve), see
  above. Not a case for PSV-1911 as long as no block valve is drawn in between.
- **Fire** (claimed governing): 66.5 m2 wetted, 1.35 / 2.21 MW. The relieving pressure,
  195.8 bar(a), is above the critical pressure of ammonia (113.6 bar): the liquid does not boil,
  it expands, and the relieving rate follows from the transient heating of the inventory
  (the supercritical-fluid fire method of API Std 521) with real-fluid properties. **Not
  calculated**: core v1.0.0 has no such method, thermo's pure-component correlations are not
  qualified near the critical point, and the liquid inventory is not set.
- The gas-filled part of the vessel wall can fail by overheating before the valve protects it
  (CCPS 14.2.1): depressuring of the loop is a question for the team.

### PSV-1912, let-down vessel V-502 (P-110)

Where: on PG-1120 from V-502 to the flare. Protected: V-502 (26.5 barg).

- **Gas blow-by through LV-1903** (claimed governing, A28): V-501 loses its level and LV-1903
  is open; loop gas at 14 700 kPa(a) enters V-502 (low/high design pressure 26.5/161 = 0.16).
  I-107 is not credited. Rate: 1 566 kg/h per unit Kv (S49 gas, 147 bar(a), 263 K,
  rho 72.3 kg/m3). From the normal let-down (64 265 kg/h, 97 m3/h of liquid ammonia, 122 bar
  drop) its Kv is about 7.2, 10.2 fully open at 70 %: **indicative 16 000 kg/h**. The let-down
  valve and any bypass must be sized first; the relief may be two-phase while the level is lost.
- PV-1906 (fails closed) closed: the let-down gas S53, 997 kg/h.
- Fire: 68.5 m2 wetted (horizontal drum at grade); 1.38 / 2.27 MW; 5 299 / 8 697 kg/h of ammonia
  at 33.1 bar(a), 343 K.
- The let-down gas path to X-601 (30.5 barg) is closed by PV-1906; X-601 itself is fed from the
  loop through FV-1905 (fails closed) and its own protection is inside the package (a vendor item;
  no HAZOP action names it yet).

### PSV-2010, product flash drum V-701 (P-111)

Where: on AG-1134 from V-701 to the flare. Protected: V-701 (26.5 barg, set by D-032 from the
V-502 pressure upstream of LV-1907).

- **Gas blow-by through LV-1907 and a blocked flash-gas outlet are removed by rating**: their
  source is V-502 at 2500 kPa(a) (23.7 barg), below the 26.5 barg design pressure of V-701
  (CCPS 14.2.2.1). It holds while V-502 stays at its normal pressure; V-502 relieving through
  PSV-1912 (up to 29.2 barg) at the same time as V-701 being blocked in is a second,
  independent failure. For the team to confirm (A30).
- **Fire** (claimed governing): 81.4 m2 wetted; 1.59 / 2.61 MW; 6 101 / 10 014 kg/h of ammonia
  vapour at 33.1 bar(a), 343 K. Required capacity 10 014 kg/h (undrained).
- **Finding R-3 (medium): K-701 suction.** Blow-by through LV-1907 (303 kg/h per Kv, S53 at
  25 bar(a)) goes on to the flash-gas stages of K-701 through AG-1121; PSV-2010 at 26.5 barg does
  not protect the suction side of a package designed for 18 barg. The package's own relief is
  the vendor's (A32).

### PSV-2210, MP steam header (P-113)

Where: on SM-1143 from the MP header SM-1140 to atmosphere through a silencer. Protected: the MP
header and U-801 (49.5 barg).

- **Process steam blocked** (claimed governing): FV-1006 (fails open) stuck closed, or the
  process steam isolated, while the waste heat boilers and the convection coil keep raising
  steam; the export valve PV-2203 stays at its normal opening (not credited to open further).
  Rate: S6, 92 834 kg/h. I-101 (low-low process steam) closes the feed and the air but not the
  firing or the boilers' heat at once; it is not credited.
- Export blocked: PV-2203 (fails closed, so also on instrument air failure) closed: S68,
  60 099 kg/h. HAZOP A36 named this case with "full raising"; the full raising of 153 t/h would
  need both valves closed at once, which no single cause in `control/loops.yaml` does (on air
  failure FV-1006 opens).
- **Finding R-4 (high): E-502 tube rupture into the steam side** (A45): low/high design pressure
  49.5/165 = 0.30, so no rating exemption applies; loop gas S43 (151 bar(a), 703 K, H2, N2, NH3)
  through two tube bores, 17 725 kg/h, reaches the steam drum and the MP header. PSV-2210
  discharges to atmosphere at a steam outlet: hydrogen and ammonia would be released there. A
  separate device on the E-502 steam side to a safe place, or a design pressure that removes the
  case, is needed; not covered by this valve.
- The steam drum and deaerator reliefs are inside U-801 (package, not drawn).

## Relief lines and flare header (not sized)

The relief line and header DN in `piping/line-list.yaml` were ASSUMED without loads (D-029). At
the loads above they are far too small (own arithmetic, ideal gas at 2 bar(a) and 313 K):
PSV-1310's 139 409 kg/h of raw synthesis gas is about 33.5 m3/s, about 1 900 m/s in the DN 150
tail pipe PG-1055 and about 470 m/s in the DN 300 header FLR-1146, against a speed of sound of
about 490 m/s; PSV-1704's 65 958 kg/h is about 27 m3/s in DN 150 PG-1090. PA-1054 (DN 100),
CO2-1076 (DN 150) and SM-1143 (DN 150) are similarly small for their cases. **Finding R-5
(high)**: every relief line and the flare header must be sized with the valve orifices and the
allowed built-up back pressure in a flare network calculation. Core v1.0.0 has neither the
orifice sizing (API 520 Part I) nor a back-pressure or header calculation, so this is left open;
no DN was changed.

Cumulative flare loads (header and flare, CCPS 15.1.7) by common cause, from the cases above;
the trips are not credited:

- Plant power failure: K-101, K-501, K-502 and K-701 stop. The front end, still fed by natural
  gas and steam through pneumatic valves, is blocked at the K-501 suction: PSV-1310 at up to
  139 409 kg/h (and finding R-1 below V-201). The loop gets no make-up (PSV-1704 not demanded);
  V-701 is rated above its source. Load about 139 t/h of raw synthesis gas.
- Cooling water failure: loss of the loop cooling demands PSV-1704 (65 958 kg/h); E-203 and
  E-402 lose duty, the front end runs hot but is not blocked; E-303 loses duty and PSV-1513
  vents to atmosphere (not flare). Load about 66 t/h of make-up gas, plus whatever the K-701 and
  X-601 package reliefs add (vendor).
- Fire around the loop vessels (V-501, V-502 at 20 m spacing): PSV-1911 (not calculated) and
  PSV-1912 (8 697 kg/h). V-701 is 70 m away and is a separate fire zone (ASSUMED from the
  placement).

The governing header load is therefore the power failure, set by PSV-1310, unless the front
end is tripped on K-501 stop or vented under control (A16). Whether the ammonia reliefs
(PSV-1912, PSV-2010) need a separate header and the minimum design temperature of FLR-1146
remain open (A34).

## Cases for which no device is drawn

Carried from the HAZOP H-01 and the design records, for the next P&ID revision; no device was
added in S8:

| case | item | action |
|---|---|---|
| K-501 stop with XV-1604 open: R-401, E-402, V-401, X-401 above design (finding R-1) | V-401 / X-401 | A16, A17 |
| tube rupture of E-203, E-402, E-503, E-701 into cooling water whose pressure is not stated | CW sides | A43, A44, A46, A47 |
| tube rupture of E-504 into the refrigerant side | E-504 shell, K-701 package | A31 |
| tube rupture of E-502 into the steam side (finding R-4) | E-502 shell, U-801 | A45 |
| gas blow-by from V-201 and V-401 into the condensate stripper | U-801 | A14 |
| thermal expansion of blocked-in cooling water | CW sides of the coolers | A41 |
| loop gas through FV-1905 into X-601 (30.5 barg) | X-601 package | vendor |
| steam drum, deaerator, K-701 refrigeration side | U-801, K-701 packages | A32, A36 |

## What core v1.0.0 cannot size, and what is missing

- No relief-load, orifice (API 520), back-pressure or flare-network calculation exists in core;
  the loads above come from `scripts/relief_loads.py`, a provenance script using published
  equations, not from a qualified tool.
- The supercritical fire case of V-501 (PSV-1911) needs a transient real-fluid method; core's property-package qualification
  (property qualification) covers neither the near-critical region nor this method.
- The blow-by cases (PSV-1513, PSV-1912) need the Kv of LV-1405 and LV-1903 and of any bypass;
  no control valve is sized.
- The compressor cases (PSV-1212, PSV-1704) need the vendors' curves and maximum discharge
  pressures.
- Two-phase relief (blow-by after the level is lost, fire on a liquid-full vessel) is not
  assessed; the DIERS methods are not available here.
- MAWPs, normal liquid levels, vessel elevations, insulation and drainage are not set; each
  changes a fire load.
