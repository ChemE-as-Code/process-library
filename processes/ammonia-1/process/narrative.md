---
# Process narrative. Schema of this front matter: `cheme schema narrative`. Skill
# control-narrative. Each section gets a heading "## <id> <title>" below.
schema: cheme/narrative/v1
sections:
  - id: REF
    title: Desulphurisation, reforming and reformer furnace
    equipment: [V-101, R-100, H-101, R-101, E-101, E-102, E-103, E-104, E-106, E-107, K-101, K-102, K-103, R-102, E-105]
    blocks: [REF]
    cases: [design]
    modes: [normal, startup, shutdown, trip]
    loops: [FIC-1002, FIC-1006, TIC-1103, PIC-1101, PIC-1107, AIC-1109, FIC-1110, FIC-1201, UIC-1202]
    sequences: [SEQ-START-REF, SEQ-SD-PLANT, SEQ-TRIP-FE]
    interlocks: [I-101, I-102, I-103]
  - id: SHF
    title: CO shift and process gas cooling
    equipment: [R-201, E-201, R-202, E-202, E-203, V-201]
    blocks: [SHF]
    cases: [design]
    modes: [normal, startup, shutdown]
    loops: [TIC-1207, TIC-1601, TIC-1306, LIC-1307]
    sequences: [SEQ-START-REF]
    interlocks: [I-104]
  - id: CO2R
    title: CO2 removal (activated MDEA)
    equipment: [C-301, C-302, P-301A, P-301B, E-301, E-302, E-303, V-302, P-302A, P-302B]
    blocks: [CO2R]
    cases: [design]
    modes: [normal, startup, shutdown]
    loops: [LIC-1405, FIC-1407, TIC-1408, PIC-1505, LIC-1506, FIC-1508]
    sequences: [SEQ-START-CO2R]
    interlocks: [I-105]
  - id: MET
    title: Methanation and drying
    equipment: [E-401, R-401, E-402, V-401, X-401]
    blocks: [MET]
    cases: [design]
    modes: [normal, startup, shutdown]
    loops: [TIC-1608, LIC-1609]
    sequences: [SEQ-START-SYN]
    interlocks: [I-106]
  - id: SYN
    title: Compression, synthesis loop, product flash and refrigeration
    equipment: [K-501, K-502, E-501, R-501, E-502, E-503, E-505, E-504, V-501, V-502, V-701, K-701, E-701]
    blocks: [SYN]
    cases: [design]
    modes: [normal, startup, shutdown, trip]
    loops: [UIC-1703, UIC-1802, TIC-1803, AIC-1804, LIC-1903, FIC-1905, PIC-1906, LIC-1907, LIC-1908, LIC-2005, PIC-2007]
    sequences: [SEQ-START-SYN, SEQ-SD-PLANT, SEQ-TRIP-FE]
    interlocks: [I-107]
  - id: PGR
    title: Purge gas recovery
    equipment: [X-601]
    blocks: [PGR]
    cases: [design]
    modes: [normal, startup, shutdown]
    loops: [PIC-2104, FIC-2106]
    sequences: [SEQ-START-SYN]
  - id: STM
    title: Steam system and boiler feed water
    equipment: [U-801, P-801]
    blocks: [STM]
    cases: [design]
    modes: [normal, startup, shutdown]
    loops: [LIC-2201, LIC-2202, PIC-2203, PIC-2206]
    sequences: [SEQ-START-REF]
  - id: UTIL
    title: Cooling water and relief headers
    cases: [design]
    modes: [normal]
unresolved: []
---

# Process narrative

> PROPOSED. This narrative describes the intended operation. It is not approved for
> implementation; its review status comes from the records in `reviews/`.

Values are not repeated here: the operating point is the `design` case of
`process/flowsheet.yaml`, the setpoints are in `control/loops.yaml`, the trips in
`control/cause-effect.yaml` and the operating modes in `control/sequences.yaml`. Decisions are
cited by their number in `DESIGN.md` (control: D-030).

## REF Desulphurisation, reforming and reformer furnace

**Purpose.** Turn natural gas, steam and air into a raw synthesis gas with the nitrogen of the
ammonia and little methane (D-004, D-007).

**Boundaries.** From the natural gas battery limit (S1) and the ambient air intakes (S12, S61) to
the secondary reformer outlet at the waste heat boiler E-105 (S17, S18); the flue gas leaves at
the stack (S67). Fuel is natural gas (S2) and the tail gas of the purge gas recovery (S59).

**Normal operation.** FIC-1002 sets the plant load on the process natural gas. The process steam
(FIC-1006) and the process air (FIC-1201) follow it as ratios, so that the steam to carbon ratio
and the heat balance of the secondary reformer hold through a load change. The H2/N2 analyser of
the synthesis loop (AIC-1804, section SYN) trims the air ratio slowly. The furnace is fired on
burner fuel pressure (PIC-1101), reset by the primary reformer outlet temperature (TIC-1103);
the combustion air (FIC-1110) is reset by the flue gas oxygen (AIC-1109); the induced draft fan
K-103 holds the arch draft (PIC-1107). The process air compressor K-101 is protected by its
blow-off (UIC-1202).

**Modes.** Start-up in SEQ-START-REF (fans, purge, light-off, heat-up with nitrogen, steam, gas,
air, shift on line) with the gas to the front-end vent; normal shutdown in SEQ-SD-PLANT (air
before gas, steam purge); after a trip SEQ-TRIP-FE holds the plant for a restart. The trips are
I-101 (process steam low-low), I-102 (furnace pressure high-high) and I-103 (secondary reformer
outlet high-high).

**Assumptions and open points.** Burner management, the start-up nitrogen connection and the
front-end vent to flare are not drawn (D-030); the fuel/air cross-limit is left to the burner
management package.

## SHF CO shift and process gas cooling

**Purpose.** Convert CO to CO2 and hydrogen in two stages and cool the gas to the absorber
temperature, recovering heat into steam and into the CO2 regenerator (D-008, D-024).

**Boundaries.** From E-105 (S18) to the raw synthesis gas leaving V-201 (S24) and the process
condensate to the stripper in U-801 (S25).

**Normal operation.** The HT shift inlet is held by the E-105 hot bypass (TIC-1207), the LT shift
inlet by the E-401 hot bypass (TIC-1601; this also sets the methanator inlet, section MET). The
gas is cooled in E-201, E-202 (regenerator reboiler) and E-203, whose cooling water TIC-1306
holds the separator inlet. LIC-1307 drains V-201.

**Modes.** Brought on line in SEQ-START-REF, step S6. I-104 alarms a high-high level in V-201.

**Assumptions and open points.** Whether a high-high level in V-201 must also trip the feed is for
the HAZOP (S6).

## CO2R CO2 removal (activated MDEA)

**Purpose.** Remove the CO2 from the raw synthesis gas to the slip of the design case (D-009)
and vent it.

**Boundaries.** From the raw gas S24 and the make-up water S26 to the treated gas S27 and the
CO2 vent S28.

**Normal operation.** The lean solvent flow (FIC-1407) and temperature (TIC-1408) set the
absorption; the absorber sump level (LIC-1405) lets the rich solvent down to the regenerator,
whose pressure is held on the CO2 vent (PIC-1505). The reflux drum level (LIC-1506) returns the
condensed water; the make-up water (FIC-1508) keeps the water balance, trimmed by the operator
from the regenerator inventory.

**Modes.** SEQ-START-CO2R fills and circulates the solvent before the raw gas is admitted. I-105
closes XV-1406 on a low-low absorber level against gas blow-by into the regenerator.

**Assumptions and open points.** The solvent rate is ASSUMED (D-009, D-028); antifoam, filtration
and solvent storage are not drawn.

## MET Methanation and drying

**Purpose.** Convert the remaining CO and CO2 to methane, condense and remove the water so that
the make-up gas is dry and free of oxygenates (D-010).

**Boundaries.** From the treated gas S27 to the dry make-up gas S34.

**Normal operation.** The methanator inlet temperature follows the LT shift bypass (section SHF);
TIC-1608 cools the effluent and LIC-1609 drains V-401; the molecular sieve package X-401 runs on
its own cycle (package).

**Modes.** Taken into line at the start of SEQ-START-SYN. I-106 cuts the methanator feed on a
high-high bed temperature.

**Assumptions and open points.** The dryer regeneration is inside the package (I-05).

## SYN Compression, synthesis loop, product flash and refrigeration

**Purpose.** Compress the make-up gas, convert it to ammonia in the loop, separate and let down
the liquid ammonia and deliver it refrigerated (D-011, D-017, D-026).

**Boundaries.** From the dry make-up gas S34 and the recovered hydrogen S36 to the liquid ammonia
product S60, with the purge S50, the let-down gas S53 and the refrigeration vent S55 to PGR.

**Normal operation.** K-501 and K-502 run on their anti-surge loops (UIC-1703, UIC-1802). The
converter inlet is held by the E-501 bypass (TIC-1803). The H2/N2 ratio of the converter feed
(AIC-1804) trims the process air (section REF). The purge flow (FIC-1905) holds the inerts,
set by the operator from the loop pressure. The separator V-501 level lets down to V-502
(LIC-1903), whose pressure (PIC-1906) and level (LIC-1907) pass gas to PGR and liquid to V-701;
V-701's level (LIC-2005) sends the product to storage. The refrigeration package K-701 holds
the chiller level (LIC-1908) and vents its inerts on PIC-2007.

**Modes.** SEQ-START-SYN (methanation and drying, compression, loop pressurisation, converter
heat-up, chilling, let-down, purge and ratio control); shutdown in SEQ-SD-PLANT; a front-end
trip holds the loop on circulation (SEQ-TRIP-FE). I-107 closes XV-1904 on a low-low separator
level.

**Assumptions and open points.** The converter start-up heater and catalyst reduction are not
drawn; K-501, K-502 and K-701 machine protection (seal, lube oil, vibration) is the vendors'
(D-029, D-030). There is no loop pressure controller: the loop pressure floats with the
conversion and is watched by the operator (D-030).

## PGR Purge gas recovery

**Purpose.** Recover the ammonia and most of the hydrogen of the purge, let-down and vent gases
and burn the rest in the reformer furnace (D-013).

**Boundaries.** From S50, S53 and S55 to the recovered hydrogen S36, the recovered ammonia S58 and
the tail gas S59.

**Normal operation.** PIC-2104 holds the tail gas back-pressure, FIC-2106 the LP steam to the
ammonia distillation; the package controls its own cold box.

**Modes.** Started with the loop in SEQ-START-SYN, step S6.

**Assumptions and open points.** The package internals and their controls are the vendor's.

## STM Steam system and boiler feed water

**Purpose.** Raise MP steam from the waste heat of the reformer, the shift and the loop, supply
the process steam and LP steam, and export the surplus (D-015).

**Boundaries.** From the demineralised water S70 to the MP steam export S68, the blowdown S69 and
the process steam S6.

**Normal operation.** LIC-2201 holds the steam drum level on the BFW valve, LIC-2202 the
deaerator level on the make-up; PIC-2203 holds the MP header on the export and PIC-2206 the LP
steam on the let-down.

**Modes.** The steam system is in service, on start-up steam from the site, before
SEQ-START-REF begins (its permissives).

**Assumptions and open points.** A three-element drum level control, a drum level low-low trip
and the BFW pump spare are open (D-029, D-030).

## UTIL Cooling water and relief headers

**Purpose.** Supply cooling water to the nine users and collect the relief lines into the flare
header (D-012, D-029).

**Normal operation.** The cooling water is supplied by the site; the supply temperature and
pressure and the return temperature are indicated only. The users' temperature loops are in
their own sections.

**Assumptions and open points.** The relief loads and the flare system are S8's.
