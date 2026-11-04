---
# Process narrative. Schema of this front matter: `cheme schema narrative`. Skill
# control-narrative. Each section gets a heading "## <id> <title>" below. S4 (D-026).
schema: cheme/narrative/v1
sections:
  - id: FEED
    title: Toluene feed drum and feed pumps
    equipment: [V-100, P-101, P-101B]
    blocks: [M100, P101]
    cases: [design]
    modes: [normal, startup, shutdown]
    loops: [LIC-102, FIC-103, PIC-104, FIC-106]
    sequences: [SEQ-START-RXN, SEQ-SD-PLANT]
    interlocks: [I-103]
  - id: RXN
    title: Feed / effluent exchanger, fired heater, reactor and quench
    equipment: [E-101, H-101, R-101]
    blocks: [M101, E101, H101, R101, R101B, Q101]
    cases: [design]
    modes: [normal, startup, shutdown, trip]
    loops: [FIC-108, TIC-111, TIC-115]
    sequences: [SEQ-START-RXN, SEQ-SD-PLANT, SEQ-TRIP-RXN]
    interlocks: [I-101, I-102, I-104, I-105]
  - id: SEPG
    title: Effluent cooler, HP separator, recycle gas compressor and purge
    equipment: [E-102, V-101, K-101, P-102, P-102B]
    blocks: [E102, V101, M102, K101, SPL1, SPL2, P102]
    cases: [design]
    modes: [normal, startup, shutdown, trip, depressuring]
    loops: [LIC-202, PIC-205, UIC-207, AIC-210, FIC-211]
    sequences: [SEQ-START-RXN, SEQ-TRIP-RXN, SEQ-EDP]
    interlocks: [I-201, I-202, I-203]
  - id: PSA
    title: Purge hydrogen recovery (PSA) and tail gas compression
    equipment: [PK-101, K-102, E-103]
    blocks: [X100, X101, PV101, X102, K102]
    cases: [design]
    modes: [normal, startup, trip]
    loops: [PIC-301, PIC-303]
    sequences: [SEQ-START-PSA, SEQ-TRIP-PSA]
  - id: STAB
    title: Stabiliser
    equipment: [C-201, E-201, V-201, P-201A, P-201B, E-202]
    blocks: [C201]
    cases: [design]
    modes: [normal, startup, shutdown]
    loops: [TIC-402, PIC-404, LIC-405, LIC-408]
    sequences: [SEQ-START-DIST, SEQ-SD-PLANT]
    interlocks: [I-401]
  - id: BZ
    title: Benzene column and benzene product
    equipment: [C-202, E-203, V-202, P-202A, P-202B, E-204, E-207]
    blocks: [C202, E207]
    cases: [design]
    modes: [normal, startup, shutdown]
    loops: [TIC-502, PIC-504, LIC-506, FIC-507, LIC-508]
    sequences: [SEQ-START-DIST, SEQ-SD-PLANT]
    interlocks: [I-501]
  - id: TOL
    title: Toluene column, toluene recycle and biphenyl
    equipment: [C-203, E-205, V-203, PK-201, P-203A, P-203B, E-206, P-204A, P-204B]
    blocks: [C203]
    cases: [design]
    modes: [normal, startup, shutdown]
    loops: [TIC-602, PIC-604, LIC-606, FIC-607, LIC-608]
    sequences: [SEQ-START-DIST, SEQ-SD-PLANT]
    interlocks: [I-601]
unresolved: []
---

# Process narrative

> PROPOSED. This narrative describes the intended operation. It is not approved for
> implementation; its review status comes from the records in `reviews/`.

The operating point is the `design` case of `process/flowsheet.yaml` (100 kt/a benzene,
D-002); setpoints are in `control/loops.yaml`, trips in `control/cause-effect.yaml`, the
sequences in `control/sequences.yaml`. The plant is drawn on P-01 to P-08 (D-025). There is no
turndown case yet: the loops are designed for the design case and their part-load behaviour is a
review question (D-026).

## FEED Toluene feed drum and feed pumps

**Purpose.** Collect the fresh toluene and the toluene recycle and pump them to the reaction loop
pressure.

**Boundaries.** From the fresh toluene at the battery limit (S1, TO-101) and the toluene recycle
from C-203 (S23, TO-123) to the pumped toluene (S3, TO-103) that joins the recycle gas at M101
(P-01).

**Normal operation.** V-100 is a nitrogen-blanketed surge drum (PIC-104 vents, PCV-105 pads). Its
level takes the fresh toluene (LIC-102): the plant draws exactly the toluene it converts, since
the recycle comes back on the level of V-203 (LIC-606). P-101 (P-101B spare) lifts the toluene to
the loop pressure; FIC-103 sets the plant load, and FIC-106 keeps the multistage pump above its
minimum flow.

**Modes.** Filled and put on minimum flow in SEQ-START-RXN step S4, before toluene is admitted;
stopped in SEQ-SD-PLANT step S2. I-103 protects the pumps against a dry suction.

**Assumptions and open points.** The level setpoint, the pad and vent pressures and the minimum
flow are ASSUMED (D-026); the minimum flow comes from the pump vendor.

## RXN Feed / effluent exchanger, fired heater, reactor and quench

**Purpose.** Heat the toluene and hydrogen to the reaction temperature, dealkylate the toluene
thermally in R-101 and stop the reaction by quenching the effluent.

**Boundaries.** From the combined feed S5 (toluene S3, make-up hydrogen S4 and recycle gas S28)
to the effluent S10 leaving E-101 for the cooler E-102 (P-01).

**Normal operation.** E-101 preheats the feed against the quenched effluent; H-101 brings it to
the reactor inlet temperature (TIC-111 on the fuel), which with the heat of reaction sets the
outlet temperature (D-021). The make-up hydrogen enters on FIC-108, whose setpoint comes from the
loop pressure PIC-205. Separator liquid quenches the effluent (TIC-115) before E-101. The
H2/aromatics ratio at the reactor inlet follows the toluene rate and the recycle gas; it is
indicated and alarmed (FFI-217) and acted on through the load FIC-103 (D-025, D-026).

**Modes.** Purged, pressured up and heated on circulating hydrogen before toluene enters
(SEQ-START-RXN). On a trip of the coil flow (I-101), the reactor outlet temperature (I-102), the
fuel pressure (I-104) or the burner management (I-105) the firing stops; I-101 and I-102 also cut
the toluene and the make-up hydrogen, and I-102 depressures the loop (SEQ-EDP). The hold after a
trip is SEQ-TRIP-RXN.

**Assumptions and open points.** Sensor voting of I-102 and the SIL of every trip are S6's. The
heater's own controls (fuel/air limits, pilot, flame detection) are the vendor's (I-105).

## SEPG Effluent cooler, HP separator, recycle gas compressor and purge

**Purpose.** Cool the effluent, separate the loop gas from the aromatics, recompress the gas and
purge methane from it.

**Boundaries.** From the effluent S10 to the recycle gas S28 to M101, the purge S13 to the PSA
(P-03), the quench liquid S27 and the separator liquid S18 to C-201 (P-02).

**Normal operation.** E-102 cools the effluent with cooling water; V-101 separates it. LIC-202
lets the liquid down to the stabiliser; XV-204 (I-201) closes if the level is lost, so that loop
gas cannot blow through to C-201. K-101 recompresses the gas with the PSA hydrogen; PIC-205 holds
the loop pressure through the make-up hydrogen, UIC-207 keeps the machine out of surge by
recycling through E-102 and V-101. AIC-210 holds the hydrogen content of the recycle gas through
the purge flow FIC-211 (D-007). P-102 pumps the quench liquid.

**Modes.** K-101 starts on full recycle in SEQ-START-RXN step S2. A liquid carry-over (I-202) or a
machine trip (I-203) stops K-101 and cuts the feed; without recycle gas the coil flow trip I-101
then stops the firing. Emergency depressuring through XV-209 (I-102 or HS-209) is SEQ-EDP.

**Assumptions and open points.** The surge line, the anti-surge algorithm and the machine
protection are the vendor's (D-025); the depressuring rate and orifice are S8's.

## PSA Purge hydrogen recovery (PSA) and tail gas compression

**Purpose.** Recover hydrogen from the purge for the loop and send the rest as fuel gas.

**Boundaries.** From the purge S13 to the hydrogen S31 to the K-101 suction and the tail gas S34
to the site fuel gas header (P-03).

**Normal operation.** PK-101 (vendor package with its own cycle control) adsorbs at the pressure
PIC-301 holds on the hydrogen product; K-102 compresses the tail gas from the desorption pressure
held by its spillback PIC-303 and E-103 cools it.

**Modes.** Started after the loop is at pressure (SEQ-START-PSA, run from SEQ-START-RXN step S7);
a trip of the PSA or K-102 isolates the purge (SEQ-TRIP-PSA) and the loop runs on without it while
methane builds up slowly.

**Assumptions and open points.** The PSA start-up routing of off-specification hydrogen and the
cycle settings are the vendor's (D-024, D-026).

## STAB Stabiliser

**Purpose.** Strip the dissolved hydrogen and methane from the separator liquid.

**Boundaries.** From the separator liquid S18 (AR-116) to the off-gas S19 to the fuel gas header
and the bottoms S20 to C-202 (P-04).

**Normal operation.** The column pressure is held on the off-gas (PIC-404); all condensed liquid
is refluxed on the drum level (LIC-405, no liquid distillate, D-008); the reboiler steam holds a
tray temperature (TIC-402); the sump level sends the bottoms to C-202 by pressure difference
(LIC-408).

**Modes.** Put on reflux as the first let-down arrives (SEQ-START-DIST step S1); I-401 protects
the reflux pumps.

**Assumptions and open points.** The control tray and its setpoint come with the column design
(S7); the first setpoint is the simulated bottoms temperature, ASSUMED (D-026).

## BZ Benzene column and benzene product

**Purpose.** Separate the benzene product from the toluene and heavier aromatics.

**Boundaries.** From the stabiliser bottoms S20 to the benzene product S21 to storage and the
bottoms S22 to C-203 (P-05).

**Normal operation.** The reflux is on flow (FIC-507) at the design ratio; the distillate is on the
drum level through the product cooler E-207 (LIC-506); the boil-up holds a tray temperature
(TIC-502); the sump level sends the bottoms to C-203 (LIC-508); the drum pressure is held by the
nitrogen pad and the vent (PIC-504). The operator trims the reflux from the product purity AI-510.

**Modes.** On total reflux until the product is on specification, then the distillate to storage
(SEQ-START-DIST step S2); I-501 protects P-202A/B.

**Assumptions and open points.** The off-specification routing of the product is in the tank farm
and is not drawn (S9 item).

## TOL Toluene column, toluene recycle and biphenyl

**Purpose.** Recover the unconverted toluene for recycle and draw the biphenyl by-product.

**Boundaries.** From the benzene column bottoms S22 to the toluene recycle S23 to V-100 and the
biphenyl S24 to storage (P-06).

**Normal operation.** The column runs under vacuum held by the PK-201 suction valve (PIC-604); the
reflux is on flow (FIC-607); the drum level sends the toluene back to V-100 (LIC-606); the boil-up
holds a tray temperature (TIC-602); the sump level draws the biphenyl (LIC-608).

**Modes.** Taken under vacuum and on reflux in SEQ-START-DIST step S3; the vacuum is broken with
nitrogen at shutdown (SEQ-SD-PLANT step S5). I-601 protects P-203A/B.

**Assumptions and open points.** PK-201 is a vendor package (load, type and power, D-008); the type
of P-204A/B is open with the pump selection (D-025).
