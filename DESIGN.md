# Design decisions

One entry per decision: what was decided, why, what was rejected, and what it assumes.
Numbers marked ASSUMED are concept estimates (about +/-30 %), not vendor or client data.

## 1 Process description (stage concept)

ASU-1 is a low-pressure double-column cryogenic air separation unit without an argon column.

- **P-01 Main air compression and precooling.** Ambient air (76,000 Nm3/h, ASSUMED) passes the
  self-cleaning inlet filter F-1101 and is compressed in the integrally geared, 3-stage
  centrifugal main air compressor K-1101 to 5.8 bara (ASSUMED) with intercoolers E-1101/E-1102
  and aftercooler E-1103 (cooling water). Inlet guide vanes control throughput; an anti-surge
  blow-off valve vents to atmosphere through silencer S-1101. The direct contact aftercooler
  C-1101 cools the air to 12 C (ASSUMED): cooling water in the lower section (pumps P-1101A/B),
  chilled water in the upper section. The chilled water (pumps P-1102A/B) is cooled to about
  10 C (ASSUMED) in the evaporative cooler C-1102 by dry waste nitrogen from the cold box.
- **P-02 Front-end purification.** Two molecular sieve adsorbers V-2101A/B (activated alumina
  under 13X, ASSUMED) work in TSA mode: one adsorbs H2O, CO2, N2O and most hydrocarbons
  (C2H2 completely) while the other is regenerated with waste nitrogen heated to 200 C in the
  electric heater E-2101, then cooled with unheated waste N2. Switching valves are sequenced by
  KS-2101. Dust filter F-2101 retains sieve fines. CO2 (AIA-2102) and H2O (AIA-2103) analyzers on
  the outlet detect breakthrough.
- **P-03 Cold box.** The purified air is split. The main part (64,500 Nm3/h) is cooled close to
  its dew point in the brazed aluminium main heat exchanger E-3101 and fed to the HP column
  C-3101 (5.4 bara). The rest (11,500 Nm3/h) is boosted in K-3101 (braked by expander KT-3101,
  aftercooler E-3104), part-cooled in E-3101, expanded in KT-3101 to 1.35 bara and fed to the
  LP column C-3102 (Lachmann air) as the plant's refrigeration. HP column bottom (rich liquid,
  ~38 % O2) and top liquid nitrogen are subcooled in E-3102 and let down through JT valves into
  the LP column. The main condenser-reboiler E-3103 (bath type, in the LP column sump) condenses
  HP nitrogen against boiling LOX. GOX is drawn from the LP sump vapour space, GAN (pressurized
  N2) from the HP column top, waste N2 from the LP top. A continuous LOX purge from the sump
  (FIC-3111) removes hydrocarbons; the LOX product is drawn from the same sump. Sump liquid is
  analysed for hydrocarbons (AIA-3103).
- **P-04 Products.** GOX (1.15 bara, warm) is compressed to 31 bara in the oil-free, multistage
  centrifugal GOX compressor K-4101 (D-002). GAN (5.2 bara) is compressed to 9 bara in K-4102.
  LOX and LIN go to the flat-bottom tanks T-4101 (250 m3) and T-4102 (400 m3). On loss of the
  ASU the cryogenic pumps P-4101A/B (LOX) and P-4102A/B (LIN) start and send liquid through the
  ambient-air vaporizers E-4105A/B and E-4106A/B into the GOX and GAN headers (D-014).

## 2 Block flow

```mermaid
flowchart LR
  AIR([Ambient air 76,000 Nm3/h]) --> F1101[F-1101 inlet filter]
  F1101 --> K1101[K-1101 MAC + E-1101..E-1103]
  K1101 --> C1101[C-1101 DCAC]
  C1102[C-1102 evaporative cooler] -- chilled water --> C1101
  C1101 --> V2101[V-2101A/B TSA adsorbers + F-2101]
  V2101 --> E3101[E-3101 main heat exchanger]
  V2101 --> K3101[K-3101 booster] --> E3101
  E3101 --> C3101[C-3101 HP column]
  E3101 --> KT3101[KT-3101 expander] --> C3102[C-3102 LP column]
  C3101 -- rich liquid, LN via E-3102 --> C3102
  C3101 <-- E-3103 condenser-reboiler --> C3102
  C3102 -- GOX --> E3101 -- GOX --> K4101[K-4101 GOX compressor] --> GOXP([GOX 30 barg pipeline])
  C3101 -- GAN --> E3101 -- GAN --> K4102[K-4102 GAN compressor] --> GANP([GAN 8 barg pipeline])
  C3102 -- waste N2 --> E3101 -- waste N2 --> E2101[E-2101 regen heater] --> V2101
  E3101 -- waste N2 --> C1102
  E2101 -.-> VENT([vent, safe location])
  C3102 -- LOX --> T4101[T-4101 LOX tank] --> P4101[P-4101A/B] --> E4105[E-4105A/B vaporizer] --> GOXP
  C3101 -- LIN --> T4102[T-4102 LIN tank] --> P4102[P-4102A/B] --> E4106[E-4106A/B vaporizer] --> GANP
```

## 3 Mass and energy balance (main streams, ASSUMED values)

Basis: design case, 30 C ambient, 94 % O2 recovery (ASSUMED). Nm3 at 0 C, 1.013 bar.

| stream | from -> to | Nm3/h | kg/h | p bara | T C | composition |
|---|---|---|---|---|---|---|
| 1 air feed | atm -> K-1101 | 76,000 | 98,270 | 1.01 | 30 | air, wet |
| 2 compressed air | K-1101 -> C-1101 | 76,000 | 98,270 | 5.8 | 40 | air, saturated |
| 3 precooled air | C-1101 -> V-2101 | 76,000 | 98,270 | 5.7 | 12 | air, saturated |
| 4 dry air to cold box | V-2101 -> E-3101 | 76,000 | 98,000 | 5.6 | 15 | dry, CO2 < 0.1 ppm |
| 5 HP column feed | E-3101 -> C-3101 | 64,500 | 83,400 | 5.5 | -173 | air near dew point |
| 6 Lachmann air | KT-3101 -> C-3102 | 11,500 | 14,870 | 1.35 | -178 | air |
| 7 GOX product | E-3101 -> K-4101 | 14,600 | 20,860 | 1.15 | 25 | O2 99.5 % |
| 8 GOX to pipeline | K-4101 -> BL | 14,600 | 20,860 | 31.0 | 40 | O2 99.5 % |
| 9 GAN product | E-3101 -> K-4102 -> BL | 10,000 | 12,510 | 5.2 / 9.0 | 25 / 40 | N2, O2 <= 10 ppm |
| 10 LOX to storage | C-3102 -> T-4101 | 330 | 470 | 1.3 | -180 | O2 99.5 % |
| 11 LIN to storage | C-3101 -> T-4102 | 375 | 470 | 5.2 | -178 | N2 |
| 12 waste N2 | C-3102 -> E-3101 | 50,500 | 63,530 | 1.15 | 25 | N2 96.8, O2 1.9, Ar 1.3 % |
| 12a regeneration | -> E-2101 -> V-2101 | 13,000 | 16,350 | 1.1 | 200 (heating) | waste N2 |
| 12b evaporative cooler | -> C-1102 | 25,000 | 31,450 | 1.05 | 25 | waste N2 |
| 12c vent | -> atm | 12,500 | 15,730 | 1.02 | 25 | waste N2 |

Mass closure: 98,270 kg/h in, 98,100 kg/h products + waste + ~400 kg/h water/CO2 removed
(within 0.2 %). O2 balance: 15,922 Nm3/h O2 in air, 14,945 Nm3/h in GOX + LOX (94 %), 977 Nm3/h
in waste. (Liquid rates revised to 470 kg/h each with the expander recalculation below; the
difference of 260 kg/h goes to waste N2, inside the accuracy of this balance.)

Refrigeration (ASSUMED, revised at S2 after review finding 5): expander KT-3101 on 14,870 kg/h
(4.13 kg/s), 7.8 -> 1.35 bara. For the -178 C exhaust the LP column needs (just above the air dew
point at 1.35 bara), the inlet must be about -115 to -120 C; design point -118 C. Ideal-gas check:
pressure ratio 0.173, T2s/T1 = 0.606, with eta_s 0.85 T2/T1 = 0.665, so T1 = 95 K / 0.665 = 143 K
ideal gas; real-gas cp near saturation moves this to ~155 K (-118 C). Enthalpy drop ~52 kJ/kg ->
**~215 kW** (the earlier -100 C inlet and 250 kW were inconsistent with a -178 C exhaust).
Demand: heat leak ~50 kW + warm-end temperature difference ~55 kW = ~105 kW; the remaining
~110 kW makes 110 kW / ~420 kJ/kg = 0.26 kg/s = **~940 kg/h liquid** (470 kg/h LOX incl. the
hydrocarbon purge + 470 kg/h LIN), down from 1,200 kg/h. More liquid needs more expander flow at
the cost of O2 recovery (D-017).

| consumer | power / duty | basis |
|---|---|---|
| K-1101 MAC | 8.0 MW electric | 0.105 kWh/Nm3 air, 5.8 bara (ASSUMED) |
| K-4101 GOX compressor | 2.3 MW electric | isothermal 1.48 MW / 0.65 (ASSUMED) |
| K-4102 GAN compressor | 0.3 MW electric | 5.2 -> 9 bara, 1 stage (ASSUMED) |
| E-2101 regeneration heater | 1.0 MW electric (peak) | 16,350 kg/h x 1.04 kJ/kgK x 185 K, ~1/3 of cycle |
| pumps, chiller water, misc. | 0.3 MW electric | ASSUMED |
| **total electric** | **~11.9 MW (average ~11.2 MW)** | 6.6 kV |
| cooling water | ~10.5 MW, ~900 m3/h at 10 K | MAC 7.6, DCAC 0.6, GOX comp 2.2, GAN comp 0.3 MW (ASSUMED) |

Specific energy: ~0.71 kWh per Nm3 GOX delivered at 30 barg (MAC + GOX compressor).

## 4 Relief case list (preliminary, ASSUMED cases; sizing in detail engineering)

| device | protects | governing case | discharge |
|---|---|---|---|
| PSV-1109 | C-1101 DCAC, AIR-1002 | MAC at surge / max. IGV with AIR-1004 blocked; MAC max. discharge ~6.5 bara vs 8 barg design: PSV as backup to UIC-1102 (fire case for the packed column) | atmosphere, local (air) |
| PSV-2108A/B | V-2101A, V-2101B (one each: each bed can be blocked in by its XVs) | fire; blocked outlet during repressurization | atmosphere, local at the bed top (dry air / N2) |
| TSV on E-2101 | heater shell | blocked-in heating (TSHH-2107 primary) | atmosphere |
| PSV-3114 | C-3102 LP column | waste N2 outlet blocked (PIC-3110 failure) with expander and JT valves running | outside cold box, elevated (O2-rich: safe location) |
| PSV-3116 | C-3101 HP column | MAC deadhead feed with GAN and liquid outlets blocked | outside cold box |
| TSVs | trapped cryogenic liquid between valves (LOX, LIN, RL, LN lines) | heat-in of blocked liquid | to vent / drain vaporizer V-3101 |
| PSV-3119 | K-3101 discharge, E-3104 | blocked outlet (KT-3101 inlet XV-3117 closed) | atmosphere (air), local |
| PSV-4122 | K-4101 discharge, E-4102 | blocked outlet at max. speed (ESD XV-4118 closed) | VNT-4002 via S-4101 |
| PSVs + vacuum breaker | T-4101 LOX tank | loss of vacuum/insulation, fill overpressure, roll-over; vacuum on fast draw-off | VNT-4001 / own outlet, safe location |
| PSVs + vacuum breaker | T-4102 LIN tank | as T-4101 | elevated (N2) |
| PSVs | P-4101/P-4102 discharge | closed discharge (pump deadhead), thermal | back to the tank |
| PSVs | E-4105A/B, E-4106A/B | blocked outlet, thermal | elevated |
| PSV on CW headers | E-1101..E-1103 tube side | tube rupture (5.8 bara air into CW) | local |

Device tags PSV-1109, PSV-2108A/B, PSV-3114, PSV-3116 and PSV-3119 are fixed now; the rest get numbers when their sheet
is drawn.

## D-001 Process cycle: LP double column, no argon column, Lachmann expander (2026-10-18)
Decision: Classic LP double-column cycle, MAC at 5.8 bara, bath condenser-reboiler, booster
expander feeding Lachmann air to the LP column, argon left in the waste nitrogen.
Reason: Lowest capital and proven at 500 t/d; 99.5 % O2 needs no argon column (specification).
Rejected: Elevated-pressure cycle (higher MAC power for a GAN demand of only 10,000 Nm3/h);
argon column (excluded by the specification).
Assumptions: O2 recovery 94 %; HP top 5.4 bara; LP top 1.3 bara (ASSUMED).

## D-002 GOX compression route: external GOX compressor (2026-10-18)
Decision: GOX leaves the cold box at low pressure and is compressed to 31 bara in K-4101, an
oil-free, multistage integrally geared centrifugal oxygen compressor with dry gas seals, nitrogen
buffer gas, Monel/copper-alloy wetted parts in high-velocity zones, fire barriers between
stages and a separate fire-safe enclosure.
Reason: About 5-8 % lower specific power than internal compression at 30 barg (no booster air
compressor to ~65 bara), simpler and lower-pressure main heat exchanger, and the LOX backup
system (pumps + vaporizers) is needed anyway. The compressor hazard is handled by the O2 rules
(D-009, D-012) and an oxygen-compressor vendor with a proven reference list.
Rejected: Internal compression (pumped LOX vaporized in the MHX against ~65 bara booster air):
safer in principle and no GOX machine, but higher power, high-pressure brazed exchanger and a
second large air compressor. To be re-evaluated if the client's oxygen-safety policy forbids
GOX compressors at 30 bar.
Assumptions: Suction 1.15 bara, 25 C; discharge 31 bara, 40 C after aftercooler; 2.3 MW.

## D-003 Refrigeration: booster-braked air expander (2026-10-18)
Decision: Turbo-expander KT-3101 on 11,500 Nm3/h air, its power absorbed by the air booster
K-3101 on the same shaft (companders), exhaust to the LP column (Lachmann).
Reason: No electric generator needed, booster raises inlet pressure and so refrigeration per kg;
Lachmann air is standard for LP cycles at 99.5 % O2.
Rejected: Generator-braked expander (power recovery small, electrical complexity); waste-N2
expander (less refrigeration at this LP pressure, cannot produce the liquid needed).
Assumptions: inlet -118 C / 7.8 bara, exhaust -178 C / 1.35 bara, eta_s 0.85, ~215 kW
refrigeration; liquid 470 kg/h LOX + 470 kg/h LIN (see balance, D-017).

## D-004 GAN source and compression (2026-10-18)
Decision: 10,000 Nm3/h pressurized nitrogen from the HP column top (<= 10 ppm O2), warmed in
E-3101 and compressed 5.2 -> 9 bara in the oil-free single-stage centrifugal K-4102.
Reason: Taking GAN from the HP column needs a compression ratio of only 1.7 instead of 7 from
the LP column; ~13 % of the air is compatible with HP reflux needs.
Rejected: LP nitrogen + 3-stage compressor (more power); raising MAC pressure (penalizes all air).
Assumptions: Pure N2 section at the HP column top is sufficient (to be verified by simulation).

## D-005 Precooling: DCAC with chilled water from an evaporative cooler (2026-10-18)
Decision: Packed direct contact aftercooler C-1101 (cooling water lower, chilled water upper
section), chilled water from evaporative cooler C-1102 using dry waste N2. Mist eliminator and
level trip LSHH-1106 at the DCAC to prevent water carry-over to the adsorbers.
Reason: Lowers the water load and adsorber size; uses waste N2 that is otherwise vented; no
refrigeration machine.
Rejected: Mechanical chiller (power, refrigerant; kept as future option if 12 C is not reached at
30 C ambient with high humidity).
Assumptions: Chilled water ~10 C at 30 C ambient (ASSUMED, to be confirmed with site humidity).

## D-006 Front-end purification: 2-bed TSA molecular sieve, electric heater (2026-10-18)
Decision: Two horizontal radial/axial-flow adsorbers V-2101A/B, alumina + 13X, ~4 h adsorption
(ASSUMED), regeneration with waste N2 heated to 200 C in electric heater E-2101 (no steam).
Breakthrough monitored by CO2 analyzer AIA-2102 (alarm 1 ppm, ASSUMED) and H2O analyzer AIA-2103.
Reason: Removes H2O, CO2, N2O and C2H2 before the cold box; steam is not available.
Rejected: Reversing heat exchangers (no hydrocarbon removal, obsolete); steam heater.

## D-007 Tag and numbering convention (2026-10-18)
Decision:
- Equipment: `<letters>-<s><nnn>[A/B]`, s = sheet/section digit (1 = P-01 ... 4 = P-04),
  nnn from 101. Letters: K compressor/booster, KT expander turbine, E heat exchanger/heater/
  vaporizer, C column/contact tower, V vessel/adsorber, T storage tank, P pump, F filter,
  S silencer. A/B = installed spares or parallel units.
- Instruments: ISA 5.1 letters + loop `<s><nnn>`, e.g. FIC-1101, AIA-3103. One loop number per
  measured variable; trips carry the same number (e.g. LSHH-1106).
- Lines: `<fluid>-<s><nnn>`, fluid codes AIR, GOX, GAN, WN (waste N2), RL (rich liquid), LN
  (liquid N2 reflux), LOX, LIN, CW/CWR (cooling water supply/return), CHW (chilled water),
  RG (regeneration gas), VNT (vent). DN, pressure class and insulation are list attributes.
Reason: Section digit makes the sheet obvious from the tag; short tags stay legible on sheets.

## D-008 Sheet split (2026-10-18)
Decision: P-01 MAC + precooling, P-02 TSA purification, P-03 cold box, P-04 products, storage
and backup. Off-sheet connectors at the section boundaries: air P-01 -> P-02 -> P-03; waste N2
P-03 -> P-02 (regeneration) and P-01 (evaporative cooler); GOX, GAN, LOX, LIN P-03 -> P-04.
Reason: Follows the process blocks and vendor packages (MAC, TSA, cold box, product machines).

## D-009 Oxygen service: materials and cleaning (2026-10-18)
Decision: All equipment and lines with O2 > 23.5 % (GOX, LOX, LP column, condenser, GOX
compressor, LOX tank, pumps, vaporizers, analyzer sample lines) are designed and cleaned for
oxygen service to EIGA Doc 13 / Doc 33 and ASTM G93: stainless steel or copper alloys in
impingement zones and valves, carbon steel only below the EIGA impingement velocity curve
(GOX at 31 bara: <= ~10 m/s ASSUMED design limit), no fast-opening valves in GOX lines (bypass
for pressure equalisation), oxygen-compatible gaskets and lubricants, cleaning verified and
documented, lines marked "Oxygen - clean". GOX DN chosen for <= 10 m/s.
Reason: Ignition by particle impact and adiabatic compression is the main GOX fire mechanism.

## D-010 Hydrocarbon accumulation protection (2026-10-18)
Decision: (1) Molecular sieve removes C2H2, most C3+, N2O and CO2 (D-006). (2) Continuous LOX
purge from the LP sump of >= 0.2 % of the O2 product (~30 Nm3/h, ASSUMED; FIC-3111) to the LOX
tank / drain vaporizer. (3) The condenser-reboiler E-3103 is kept fully submerged (LP sump level
LICA-3102 with low alarm), bath type, no dry boiling. (4) Analyzers: total hydrocarbons and
C2H2 in sump LOX (AIA-3103, alarm/trip), CO2 at TSA outlet (AIA-2102); action limits per EIGA
Doc 65 (ASSUMED); hydrocarbons in the LOX tank liquid (AIA-4121, periodic), since
boil-off in storage concentrates them. (5) Air intake located away from hydrocarbon sources; intake survey in basic
engineering. (6) Periodic derime/warm-up procedure.
Reason: Hydrocarbon accumulation in boiling LOX is the dominant ASU explosion hazard.

## D-011 Relief, vent and blowdown philosophy (2026-10-18)
Decision: Every enclosed volume that can be blocked in has a relief device; trapped cryogenic
liquid between two valves has a thermal relief valve. Columns relieve to atmosphere through
dedicated vent lines. O2-rich vents (GOX, LOX tank, LOX purge, vaporizers, analyzer vents) are
routed to a safe location: elevated, away from ignition sources, walkways and air intake; GOX
vent with silencer. N2 vents routed high to avoid asphyxiation zones. LOX/LIN tanks: PSVs +
vacuum breakers + rupture discs on the annular space. Cold liquid drains go to an atmospheric
drain vaporizer, never to sewers or open pits. Relief cases (blocked outlet, fire, CW failure,
control valve failure, heater over-temperature) are listed per device in section 4. The LP
column C-3102 has its own PSV-3114 (design 3.5 barg against normal 0.3 barg): it can be blocked in
by PIC-3110 / the waste N2 valves while the expander and the JT valves keep feeding it. Vents of
different pressure levels never share a header (D-019).
Reason: Overpressure, O2 enrichment and N2 asphyxiation risks of an ASU.

## D-012 No oil-lubricated equipment in O2 service (2026-10-18)
Decision: GOX compressor with dry gas seals and N2 buffer gas, oil system separated by an
atmospheric distance piece; LOX pumps with vapour-lifted/leakage-vented seals and grease-free
bearings in O2-wetted parts; MAC oil system with demister and oil-free air path; no
oil-lubricated valve actuators in O2 lines. The compander KT-3101/K-3101 is the one oil-bearing
machine that touches cold-box air: its bearings are oil-lubricated, sealed from the expander and
booster wheels by labyrinths fed with N2 seal gas. PDSLL-3115 (seal gas minus bearing housing
pressure) is a permissive for the lube oil pump (seal gas first, oil second) and trips the
compander (inlet XV closed) on low-low. The oil tank vent has an oil mist eliminator and vents
outside the cold box. So no oil can be carried with the Lachmann air into the LP column, where it
would accumulate in the LOX sump. (Alternative for the vendor enquiry: magnetic or gas bearings.)
Reason: Hydrocarbon oils are ignition sources in oxygen.

## D-013 Isolation and blowdown (2026-10-18)
Decision: Double block and bleed at the GOX and GAN battery limits (ESD valves XV-4119 GOX,
XV-4120 GAN); emergency isolation valves XV-4117 (K-4101 suction) and XV-4118 (discharge);
GOX compressor depressurized on trip by blowdown valve XV-4116 to VNT-4002 / S-4101; cold box liquid drain valves to the drain vaporizer; the
cold box casing is N2-purged (PIC on purge) with a breathing valve.
Reason: Safe isolation for maintenance and fast removal of energy from a GOX fire.

## D-014 Backup supply (2026-10-18)
Decision: On GOX or GAN header low pressure (PIC-4111 / PIC-4112) the standby LOX pump P-4101A/B
or LIN pump P-4102A/B starts and supplies through ambient-air vaporizers E-4105A/B / E-4106A/B.
Low outlet temperature trip TSLL-4113/4114 protects the carbon-steel pipeline from cold gas.
Reason: Supply continuity during ASU trips (25 % GOX, 50 % GAN, 2 days, specification).
Assumptions: Pumps cold-standby (kept cold by recirculation to the tank).

## D-015 Empty sheet frames at stage concept (2026-10-18)
Decision: pid/P-01..P-04.xml are created now as empty DEXPI frames (title block only), drafted in
stage basic.
Reason: plant.yaml must declare the sheets and plantcode requires each declared file to exist.
The lists then cross-check against the sheets; the resulting "not on P&ID" warnings are expected
until basic engineering.

## D-016 Line sizing basis (2026-10-18)
Decision: Concept DN from velocity: gas <= 20 m/s (waste/regen <= 25 m/s at near-atmospheric
pressure), GOX <= 10 m/s at 31 bara (D-009), liquids 1-2 m/s, pump suction <= 1 m/s.
Reason: Pressure-drop and O2 velocity limits. Final sizing in basic engineering.

## D-017 Liquid production and storage refill time: client to confirm (2026-10-18)
Decision (proposed, CLIENT TO CONFIRM): keep the expander at 11,500 Nm3/h and ~940 kg/h liquid.
Refilling the full backup reserve then takes ~22 days for LOX (250 t / 470 kg/h) and ~27 days
for LIN (300 t / 470 kg/h); at the previous 600 kg/h it was 17 / 21 days. After a backup event
the tanks are topped up by road tankers (truck fill connection on T-4101/T-4102, P-04).
Alternative for the client: a ~30 % larger expander flow (~15,000 Nm3/h) restores ~1,200 kg/h
(refill ~17 / 21 days) for about 1-1.5 points of O2 recovery and ~0.2 MW more MAC power.
Reason: the backup reserve (2 days of 25 % GOX and 50 % GAN) is set by the specification, the
refill time is not; it is a commercial choice between truck liquid and power/recovery.
Assumptions: liquid refrigeration ~420 kJ/kg (ASSUMED).

## D-018 O2 recovery 94 % and sensitivity at 90 % (2026-10-18)
Decision: keep 94 % as the design recovery and size the MAC for 80,000 Nm3/h (+5 %, ASSUMED
margin). Check: an LP double column with ~15 % Lachmann air and no argon column typically reaches
93-96 % at 99.5 % O2, so 94 % is plausible but not conservative. At 90 % the O2 in the air must be
14,930 / 0.90 = 16,590 Nm3/h -> 79,200 Nm3/h air (+4.2 %), MAC power ~8.35 MW (+0.35 MW), adsorber
and MHX loads +4 %: covered by the 80,000 Nm3/h MAC rating; specific energy rises to ~0.73 kWh/Nm3.
Reason: recovery is the main uncertainty of the concept balance; the margin keeps the product rate
if the simulation in basic engineering gives less.

## D-019 Vent separation and GOX suction vent (2026-10-18)
Decision: no shared vent headers between pressure levels. VNT-4001 is the LOX tank vent only
(0.5 barg, PV-4109); VNT-4002 is the K-4101 blowdown (31 bara, XV-4116, silencer S-4101);
VNT-4003 is the GOX suction vent on GOX-4001 (PV-4101B, silencer S-4102), split range with
PIC-4101: PV-4101A first (compressor IGV/recycle), PV-4101B opens above it on a K-4101 trip or
during start-up, so the LP column pressure stays controlled while the compressor is not taking
GOX. All three discharge elevated at a safe location (D-011).
Reason: a 31 bara blowdown into a header shared with a 0.5 barg tank would back-pressure and
possibly overpressure the tank, and push O2 back into it (review finding S1-2/3).

## D-020 DEXPI classes used for equipment (2026-10-18)
Decision: CentrifugalCompressor (MAC, booster, GOX/GAN compressors), TubularHeatExchanger
(coolers), PlateHeatExchanger (brazed aluminium exchangers), ProcessColumn (columns, DCAC,
evaporative cooler), GasFilter, Silencer, CentrifugalPump, Tank, PressureVessel, ElectricHeater.
Verified on P-01 by `plantcode validate` (the loader rejects unknown classes). Classes for P-03/
P-04 that are not on a sheet yet (Turbine for KT-3101, Vessel for V-3101, HeatExchanger for the
ambient vaporizers) are checked the same way when those sheets are drawn; if the loader refuses
them: SteamTurbine is wrong for an air expander, so use the generic class the loader offers and
say so here.
Turbine, Vessel and HeatExchanger are valid (generic) pyDEXPI classes (checked in the pyDEXPI
class model at S2): KT-3101 stays Turbine (there is no expander class); V-3101 (atmospheric drain
vaporizer) becomes Tank and the ambient vaporizers stay HeatExchanger when P-03/P-04 are drawn.
Silencers (DEXPI `Silencer` is a PipeFitting) and safety valves (`SpringLoadedGlobeSafetyValve`)
are piping components, not tagged plant items or instrument functions: they carry their tag as
PipingComponentNumber / PositionNumber on the P&ID and are listed here, not in the equipment or
instrument lists:

| tag | class | line | sheet |
|---|---|---|---|
| S-1101 | Silencer | AIR-1003 | P-01 |
| PSV-1109 | SpringLoadedGlobeSafetyValve | AIR-1004 (C-1101 top) | P-01 |
| S-2101 | Silencer | RG-2003 | P-02 |
| PSV-2108A/B | SpringLoadedGlobeSafetyValve | AIR-2001 (V-2101A/B tops) | P-02 |
| S-3101 | Silencer | WN-3003 | P-03 |
| PSV-3114, PSV-3116 | SpringLoadedGlobeSafetyValve | VNT-3002 (C-3102), VNT-3003 (C-3101) | P-03 |
| PSV-3119 | SpringLoadedGlobeSafetyValve | AIR-3002 (K-3101 discharge) | P-03 |
| S-4101, S-4102 | Silencer | VNT-4002, VNT-4003 | P-04 |

Note: the `name` attribute of the XML root (`example`) is rewritten by `plantcode fmt` (pyDEXPI
serializer); the plant identification is in the title-block MetaData (ASU-1).

## D-021 P-01 drawing content (2026-10-18)
Decision: P-01 shows F-1101, K-1101 (one compressor symbol with stage nozzles; intercoolers
E-1101/E-1102 below it on interstage lines AIR-1005/AIR-1006), aftercooler E-1103, blow-off
AIR-1003 with UV-1102 to S-1101, non-return valve on AIR-1002 before the DCAC (no backflow from
the adsorbers into the MAC on trip), PSV-1109 on C-1101, CW pumps P-1101A/B (FV-1108), DCAC sump
water CWR-1001 via LV-1106, chilled water C-1102 -> P-1102A/B -> TV-1105 -> C-1101 upper section,
CW make-up CW-1003 via LV-1107, waste N2 WN-1001 from P-03 into C-1102 and vent WN-1002. Cooling
water to the intercoolers and aftercooler is CW-1002 / CWR-1002 with off-sheet connectors to the
CW utility system (not drawn in this project). One line number per cooler (CW-1002/CWR-1002 E-1101,
CW-1004/CWR-1003 E-1102, CW-1005/CWR-1004 E-1103) so from/to are exact.
Rev after the S2 review: CW-1001 enters C-1101 on the right side (no crossing with AIR-1002), DCAC
level instruments on the left side, CWR-1001 leaves to the left; mist eliminator drawn as a mesh pad
at the C-1101 top (D-005); TIA-1110 (MAC vendor multipoint: stage discharges and intercooler
outlets) and TIA-1111 on AIR-1002 after E-1103. LSHH-1106 trips the MAC only: no XV on AIR-1004,
because the MAC trip stops the flow and the check valve on AIR-1002 prevents back-flow; a 600 mm
XV in the wet air would add a failure point without extra protection.
Signal lines are drawn as dashed lines to the valve actuators; the DEXPI actuating-system objects
(ActuatingSystem / ActuatingFunction) are added in detail engineering. Control valves carry their
tag as the valve number (e.g. TV-1105).

## D-022 P-02 drawing content (2026-10-18)
Decision: adsorbers V-2101A/B in upflow adsorption (air in bottom, dry air out top) and
counter-current downflow regeneration (RG-2002 in at the top, RG-2003 out at the bottom to
S-2101). Eight switching valves XV-2101A/B..XV-2104A/B (actuated ball valves, sequenced by
KS-2101; valve tags, not instrument-list items). AIR-1004 continues from P-01 to the adsorber inlet
header. FV-2105 on RG-2001 (FIC-2105), TIC-2104 trims E-2101, TSHH-2107 on the heater element.
Rev after the S2 review: no line crosses another. With two beds and four external streams (feed in,
product out, regeneration in, regeneration out) two of the four headers must lie inside the loop
formed by the beds; the product header (top) and the regeneration outlet header with S-2101
(bottom, then right) run outside, the feed-air and regeneration-gas inlets (off-page connectors
from P-01 / P-03) sit between the beds. Air out at the outer top nozzles, regeneration in at the
inner top nozzles, air in at the inner bottom, regeneration out at the outer bottom.
Added: PSV-2108A/B on the bed tops; repressurization XV-2111A/B (DN100 globe, slow, bypassing the
inlet XV-2101A/B) and depressurization XV-2112A/B (DN100 globe, bypassing XV-2104A/B to S-2101),
all sequenced by KS-2101; heater bypass XV-2109 (butterfly, DN500) for the cooling step: E-2101 is
de-energised and XV-2109 opens, so cold waste N2 cools the bed; TI-2113A/B on the dry-air outlets
(hot bed on line) and TI-2114A/B on the regeneration outlets (heat pulse ends the heating step).
S-2101 discharges via an arrow "to atmosphere (safe location)" (waste N2, D-011). DN100 of the
bypasses ASSUMED (repressurization in ~15 min).

## D-023 P-03 drawing content (2026-10-18)
Decision: P-03 (scripts/draft_P-03.py) shows E-3101 with the warm end at the top and the cold end
at the bottom; dry air AIR-2002 from P-02 with the booster branch AIR-3005 -> K-3101 -> E-3104 ->
AIR-3002 back to the warm end; booster air leaves E-3101 at mid height (AIR-3003, quick-closing
XV-3117 tripped by SSHH-3108) to KT-3101 and enters the LP column as Lachmann air (AIR-3004,
TIC-3109). The double column is drawn stacked: C-3101 below, C-3102 above, E-3103 in the LP sump
(GAN-3002 vapour up, LN-3002 condensate back). Rich liquid RL-3001 and reflux LN-3001 pass the
subcooler E-3102 (right) and LV-3101 / FV-3106; LIN-3001 is taken from subcooled LN-3001 to P-04.
Waste N2 WN-3001 leaves the LP top, warms in E-3102 and E-3101 and is distributed at the right
edge as WN-3002: RG-2001 to P-02, WN-1001 via PV-3110A to P-01, surplus WN-3003 via PV-3110B and
S-3101 to an elevated vent (split range PIC-3110). Hydrocarbon protection (D-010) on the sheet:
AIA-3103 and LICA-3102 on the LP sump, LOX-3001 with the continuous purge FIC-3111/FV-3111 to the
LOX tank, LOX-3002 drain via HV-3118 to the drain vaporizer V-3101 (vent VNT-3001 to a safe
location). Relief: PSV-3114 (LP column), PSV-3116 (HP column), PSV-3119 (booster discharge).
Casing purge UN-3001 via PV-3113 (PIC-3113). Product analyzers AI-3104 / AIA-3105 and the GAN flow
loop FIC-3107 are on the warm product headers at the compressor suctions, so they are drawn on P-04.
Crossings: with stacked columns the RL and LN loops through the subcooler interleave (RL 232 -> 106,
LN 190 -> 76 on the column side), so they cross once below E-3102; LOX-3001 leaving the LP sump
crosses the GOX-3001 riser once. Both crossings are plain crossings away from any tee.
The compander K-3101 / KT-3101 is one machine (same shaft, D-003); the two casings are drawn apart
because the booster is warm and the expander is in the cold box. Seal-gas and oil systems are in
the vendor package (D-012, PDSLL-3115). DNs of GAN-3002, LN-3002, VNT lines ASSUMED.
