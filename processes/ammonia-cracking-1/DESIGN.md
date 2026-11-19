# Design decisions

One entry per decision: what was decided, why, what was rejected, and what it assumes.
Hydrogen by catalytic ammonia cracking with PSA purification, issue
ChemE-as-Code/process-library#519, a continuous Tier 2 entry of the library. Concept stage:
design basis, balanced BFD/PFD solved by core, duties, equipment list and a preliminary
gate-to-gate LCI. Out of scope here: P&IDs, layout, HAZOP, TEA, datasheets.

Starting point (2026-11-19): library `main` at c04ed69 with the core pin v1.13.0 (b97a833).
Core 1.13 solves feeds for targets with design specifications and splits component separators
(core ADR 0070), holds a gas-phase reaction at equilibrium at a step's outlet, and writes a
conversion step's duty on its energy stream (ADR 0059). This entry uses all three, so the whole
material balance is calculated by `cheme process propagate`. Templates: `vinyl-acetate-1`
(continuous structure, source register, balance-output script), `oxalyl-chloride-1` (folder
layout, PROGRESS rows), `hydrogen-1` (PSA and fired furnace with tail-gas firing) and
`ammonia-1` (the ammonia this plant consumes). Requires cheme-as-code 1.13 (plant.yaml).

The issue proposed the id `hydrogen-2`; the entry is `ammonia-cracking-1`, named by its route as
the library's other second routes to an existing product are, so that hydrogen-1 (steam
methane reforming) keeps its id.

## Source register

Facts are restated in our own words; nothing is copied. "Read" means the passage named was read
in this work.

| id | source | locator | access / terms | used for |
|---|---|---|---|---|
| SRC-1 | EP 4 337 600 A1, A. Shaw, S. C. Saloway, V. White (Air Products and Chemicals), priority and filing 2021-06-18, published 2024-03-20: Ammonia cracking process, https://patents.google.com/patent/EP4337600A1/en | description: liquid ammonia pumped (preferably 5-50 bar), heated against the cracked gas and the flue gas to above 250 C (typically 400-600 C); in the Fig. 1 scheme (to which reference example 2's Fig. 3 refers for its other features) the cracked gas is cooled in exchanger E101 against the feed ammonia, the tail gas fuel and the combustion air from fan K201, and the warmed air is fed to the furnace: heat integration preheats the air and the ammonia to the cracker; no air preheat or stack temperature stated in the text read and cracked in catalyst-filled tubes heated by a furnace, an SMR-type radiant section preferred; any conventional cracking catalyst (nickel, iron, ruthenium, rhodium, iridium, metal amides/imides); the cracked gas cooled to a PSA inlet of about 20-60 C; PSA product to ISO 14687 (ammonia below 0.1 ppmv, nitrogen below 300 ppmv) at about the reaction pressure; the PSA tail gas fired in the furnace; ammonia slip removable by a water scrubber and stripper, a TSA or membranes. Examples (Aspen Plus): equilibrium cracking at 11 bar and 500 C; reference example 1 (ammonia as supplementary fuel) 77.18 % hydrogen recovery from the ammonia at 83.5 % PSA recovery; reference example 2 (tail gas the only fuel, recovery adjusted so that it provides all the process heat) 77.05 % at 79.4 %; secondary-cracker and membrane variants 93.65-99.00 % | read (Google Patents machine text, the description and examples; the example tables were not in the text read; the air-preheat passages re-read 2026-11-20); patent, facts only | D-001, D-004, D-005, D-006, benchmark |
| SRC-2 | K. Fothergill, S. Greenwood, J. Makepeace, I. Wilkinson (Ecuity, Engie, STFC, Siemens), Ammonia to Green Hydrogen Project, Feasibility Study, report HS420 for BEIS, 2020, https://assets.publishing.service.gov.uk/government/uploads/system/uploads/attachment_data/file/880826/HS420_-_Ecuity_-_Ammonia_to_Green_Hydrogen.pdf | PDF pp. 24-26: a 200 t/d hydrogen fired reformer design; feed ammonia at 15 bar and 20 C, fuel 85 % NH3 and 15 % H2, steam 40 bar and 345 C, flue gas 67 % N2, 31 % H2O, below 2 % O2/Ar at 181 C, product gas 69 % H2, 23 % N2, 8 % NH3 at 2.3 bar and 380 C; a trade-off between conversion and heat efficiency: 93.1 % thermal efficiency at 84.6 % conversion, a more efficient design converting less through heat transfer limits (PDF p. 24); heat recovered from the flue gas in four convection banks, the last a combustion air preheater (PDF p. 24); heater duty about 119 MWth (45 cracking, 27 ammonia preheat, 38 steam; stack 5.8, firebox radiation 2.6 MWth); up to 15 MW from a Rankine cycle; ammonia recovered by water absorption (8 stages, 8 % to 0.06 %) and a stripper (10 stages, up to 183 t/d, 14 % of the feed); cryogenic purification after compression to 240 bar; 99.97 % hydrogen at 250 bar, overall efficiency about 69 %, 12.65 MJ/Nm3 | read (PDF text, PDF pp. 22-26; p. 24 re-read 2026-11-20); UK government report (Open Government Licence), facts only | D-001 (rejected alternative), D-002, D-003, D-006 |
| SRC-3 | European Commission, Joint Research Centre (2022), Assessment of Hydrogen Delivery Options, EUR 31199 EN, JRC130442, https://publications.jrc.ec.europa.eu/repository/bitstream/JRC130442/kjna31199enn.pdf | section 2.3 (PDF p. 19, printed p. 15): cracking is the endothermic reverse of the synthesis, high conversion above 400 C, equilibrium conversion falls with pressure, purification needed; section 2.3.4 (PDF p. 21): commercial crackers below about 100 kg H2/h, few large designs, SRC-2's firebox about 52 GJ/t H2 at 98.5 % conversion, 200 t/d at 25 MPa and 99.97 %; section 5.5.3.4 (PDF pp. 45-46): SRC-2 the only detailed large-scale reference, 0.137 t H2 per t NH3 (feed and fuel, recycle included), electricity about 17.5 GJ/t H2 (to 25 MPa and 99.97 %), fuel 51.9 GJ/t H2, CAPEX EUR2020 369 m for 200 t H2/d | read (PDF text); EU publication (reuse with attribution), facts only | D-001, D-002, benchmark |
| SRC-4 | processes/ammonia-1 (this library) | the feed: anhydrous liquid ammonia, refrigerated at its battery limit | library, internal | D-003, D-010 |
| SRC-5 | The `chemicals` 1.5.2 and `thermo` 0.6.1 packages (core's environment, C. Bell, MIT), printed by `cheme chemistry thermo NAME --fit 298.15,1500` (cheme-as-code 1.13.0) and queried in scripts/balance.py | ideal-gas formation enthalpies (ATcT: NH3 -45.558, H2O -241.822 kJ/mol), CRC entropies, ideal-gas heat capacities fitted by core to thermo's TRCIG (NH3, H2) and HEOS_FIT (N2, O2, H2O, Ar) over 298.15-1500 K (within 0.5 %); HEOS critical constants; thermo's HEOS_FIT vapour pressure, heat of vaporization and liquid heat capacity of ammonia: saturation 308.15 K at 1350 kPa(a), 19.12 kJ/mol to vaporise there, 1.23 kJ/mol to warm the liquid from 293.15 K | open-source packages queried 2026-11-19; single values, facts only, with their source; not open data (library ADR 0037); the underlying works (ATcT, the CRC Handbook, the TRC tables, the HEOS reference equations) were not read here | materials, reactions (equilibrium), scripts/balance.py |
| SRC-6 | ISO 14687 (hydrogen fuel quality) | - | not read (licensed standard); its nitrogen and ammonia limits are taken as SRC-1 states them | D-005 |
| SRC-7 | Kinetics of ammonia decomposition over nickel and ruthenium catalysts; vendor cracker data (Topsoe, thyssenkrupp Uhde, KBR, Air Products) | - | not read here; known leads for sizing the tubes and for a kinetic reactor | L-4 |

## D-001 Route and boundary (2026-11-19)

Decided: catalytic cracking of ammonia in catalyst-filled tubes in a fired furnace, the tube
outlet at chemical equilibrium, the hydrogen purified by PSA and the PSA tail gas burnt as the
furnace's only fuel, as in SRC-1's reference example 2: 2 NH3 <=> N2 + 3 H2. Ammonia vaporised in
a feed-effluent exchanger and superheated in the convection section, and the combustion air
preheated in the convection section (D-006). SRC-1 heats the ammonia against the cracked gas and
the flue gas, and preheats the combustion air and the tail gas against the cracked gas too; this
entry uses the cracked gas's heat for the ammonia only and preheats the air with the flue gas, a
departure stated in D-006. The boundary is the plant gate: pressurised liquid ammonia in
from ammonia-1 (SRC-4), air and power from the site, hydrogen out at 1030 kPa(a), flue gas to
the stack. Compression of the hydrogen to a pipeline or a trailer (SRC-2 and SRC-3 deliver at 25
MPa) is outside the boundary, as hydrogen-1 delivers at its PSA pressure: the two hydrogen
routes are compared at the plant gate.

Rejected:
- **Cracking at low pressure with ammonia recovery by water absorption and stripping, and
  cryogenic nitrogen removal** (SRC-2, the design the issue first named): 84.6 % conversion at
  2.3 bar, 8 % ammonia recovered and recycled, the gas compressed to 240 bar and the nitrogen
  liquefied at 43 K, fuel 85 % ammonia; with a steam Rankine cycle. More units (absorber,
  stripper, six-stage compressor, cold box, steam cycle), and the published balance is given
  only in aggregate (heater, efficiency); core has no NH3-water property package to solve the
  absorber and stripper (the issue's own note). The PSA variant has open examples with
  recoveries and a fuel balance at a stated equilibrium basis (SRC-1), which core can solve.
- **PSA with ammonia trim fuel** (SRC-1 reference example 1, 77.18 % at 83.5 % PSA recovery):
  the same plant with 4.8 % of the ammonia burnt (from its two recoveries over the equilibrium
  conversion); kept as a variant: a higher PSA recovery needs a second fuel.
- **A secondary cracker or a membrane on the tail gas** (SRC-1, 93.65-99.00 %): recovers more
  hydrogen but then needs a fuel (natural gas or ammonia) for the furnace; more equipment and
  compression. A next-stage variant once the fuel's origin is chosen.
- **Electrically heated cracking, membrane reactors and lithium imide catalysts**: small-scale or
  early-stage (SRC-3: commercial crackers below about 100 kg H2/h); no open large-scale balance
  read.

## D-002 Capacity, product and operating hours (2026-11-19)

200 t/d of hydrogen (8333.33 kg/h), the size of the only detailed open large-scale design
(SRC-2) and of JRC's unpacking plant (SRC-3); 8000 h/a, ASSUMED. A normalisation basis for the
inventory, not an owner figure. The design specification `rate` sets the ammonia feed for this
rate of hydrogen in S7.

## D-003 Feed (2026-11-19)

Anhydrous liquid ammonia from ammonia-1, taken pressurised at 1500 kPa(a) and 293.15 K, the
HS420 feed (SRC-2); dissolved gases and water are not modelled. ammonia-1 delivers it
refrigerated at its battery limit (110 kPa(a), 240.15 K); the terminal's storage, pumping and
warming between the two are outside the boundary of both entries (no burden counted for them).
Their size on thermo 0.6.1's HEOS_FIT liquid heat capacity and density of ammonia (SRC-5), for
the 60.7 t/h of S1:
- **warming** from 240.15 to 293.15 K: 4.14 kJ/mol, 4.10 MW (0.49 kWh per kg of product, a fifth
  of E-101's Q4), heat at or below ambient temperature (ambient air, sea water, or the cracked
  gas in E-103, whose 6.32 MW it would partly replace);
- **pumping** 89.1 m3/h (681 kg/m3 at 240 K) from 110 to 1500 kPa(a): 34.4 kW hydraulic, about
  49 kW electric at an overall efficiency of 0.7 (ASSUMED), 0.0059 kWh per kg of product, a
  third of the 0.0181 kWh/kg the LCI counts (D-008). SRC-1 pumps the liquid inside the cracking
  plant; counting the pump here (and taking S1 at ammonia-1's battery limit) is a next-stage
  change of the boundary. Pressure on the way to the tubes: 1350
kPa(a) after the vaporiser, 1250 kPa(a) at the tube inlet (ASSUMED drops).

## D-004 Cracking reactor: equilibrium basis (2026-11-19)

R101 is `reactor: equilibrium`: the outlet S4 at the equilibrium of NH3_CRACK at 773.15 K and
1100 kPa(a), the basis of all of SRC-1's examples. On the ideal-gas data of materials.yaml
(SRC-5) the equilibrium constant of NH3 -> 0.5 N2 + 1.5 H2 is 266.7 at 773.15 K (standard
pressure 100 kPa), so 97.42 % of the ammonia is cracked and 1.30 mol% stays. SRC-1's reference
example 2 implies 97.04 % (77.05 % over 79.4 %), reference example 1 with its ammonia fuel
about the same: the ideal-gas model is within 0.4 points of the source's simulation, a
difference of the order of the real-gas correction at 11 bar and of any pressure drop the
source assumes. No approach to equilibrium is set (the source states none). A nickel catalyst is
ASSUMED (SRC-1 names nickel first among the conventional catalysts). The feed is superheated to
723.15 K in the convection coil E-102 (ASSUMED, inside SRC-1's 400-600 C); the tubes take it to
773.15 K and crack it. The tube count, catalyst volume and heat flux are not sized: no kinetics
was read (L-4, SRC-7). Equilibrium falls with pressure (SRC-3): the 11 bar keep the PSA at a
useful pressure without compression, at the cost of 1.3 % slip compared with about 0.3 % at
2.3 bar (SRC-5 data).

## D-005 Cooling and PSA (2026-11-19)

The cracked gas gives its heat to the vaporising ammonia in E-101 (from 773 to 424 K) and is
cooled to 313.15 K on cooling water in E-103 (inside SRC-1's 20-60 C PSA inlet). The PSA U201 is
a component separator (`recovery:`, core ADR 0070): 79.4 % of the hydrogen to the product
(SRC-1 reference example 2), 0.02 % of the nitrogen (ASSUMED: 84 ppm(mol) in the product,
inside SRC-1's 300 ppmv), no ammonia (below SRC-1's 0.1 ppmv: the ammonia is adsorbed and
leaves with the tail gas; whether an ammonia layer in the PSA or a TSA ahead of it does this is a
vendor choice, SRC-1). Product 99.99 mol% at 1030 kPa(a) and 318 K; tail gas at 130 kPa(a) and
303 K (ASSUMED) to the burners. The PSA's power (valve actuators and instrument air) is not
counted; it is ASSUMED below 20 kW (0.0024 kWh per kg of product, no source read), against the
151 kW of the air fan.

## D-006 Furnace: tail gas firing, air preheat, bridgewall check and NOx (2026-11-19, revised 2026-11-20)

H101 burns the tail gas S8 (36.99 mol% H2, 59.84 % N2, 3.17 % NH3; 80.1 MW LHV) completely with
air to N2 and water (ASSUMED), as the only fuel (SRC-1 reference example 2). The air (S9) is set
by the design specification `air` for 2.0 mol% oxygen in the wet flue gas (ASSUMED; SRC-2's flue
gas holds below 2 % O2 and Ar); it is dry air with its argon, CO2 and other minor gases counted
as argon (ASSUMED). The fan K-101 sends it through the air preheater E-104, the cold
end of the convection section, which heats it to 623.15 K (350 C, ASSUMED; Q5, 9.09 MW, from
scripts/balance.py). The flue gas passes the radiant section with the tubes (Q1, 53.6 MW), the
superheater coil E-102 (Q2, 17.3 MW, written by propagate as H101's rest, `energy_port: conv`)
and E-104, and leaves at the temperature that closes this balance, 492 K (scripts/balance.py,
D-008): 70.9 MW reaches the process, 88.5 % of the fired LHV. The air preheat returns flue gas
heat to the firebox; it does not change the stack temperature, which is fixed by the fuel (the
PSA recovery) and the process duties. No steam is raised (no steam user; the plant exports
none). The furnace's radiation loss is not modelled (SRC-2: 2.6 MWth in its larger heater).

Bridgewall check (scripts/balance.py prints it; ideal-gas data of materials.yaml, the flue gas
S11's composition):

| point (flue gas order) | flue gas | process side | approach |
|---|---|---|---|
| adiabatic flame, tail gas S8 with air S12 | 1885.8 K | - | - |
| leaving the radiant section, after Q1 (bridgewall) | 993.1 K | tube outlet S4 773.15 K | 219.9 K |
| E-102 hot end | 993.1 K | ammonia out S3 723.15 K | 269.9 K |
| E-102 cold end | 671.5 K | ammonia in S2 313.15 K | 358.4 K |
| E-104 hot end | 671.5 K | air out S12 623.15 K | 48.4 K |
| E-104 cold end, stack | 492.04 K | air in S10 303.31 K | 188.7 K |

Without the preheater (this entry's first version, air at 303 K) the flame was at 1742.9 K and
the gas left the radiant section at 826.9 K, 54 K above the tube outlet: the tube wall must be
hotter than the gas inside it and radiant flux grows with the difference of the fourth powers of
gas and wall temperature, so the tubes could not have taken Q1 there. With air at 623 K the
bridgewall is 166 K hotter; the radiant section takes 60 % of the heat entering the firebox (the
fired LHV plus the air preheat), 66.9 % of the fired LHV. The firebox still runs cool for a fired
heater: Q1 is 76 % of the duty absorbed and all of it is needed above 723 K, while the fuel is
fixed by the PSA recovery. Whether the tubes take 53.6 MW at a bridgewall of 993 K depends on
their area and wall temperature, which are not sized (L-4); SRC-2 likewise names heat transfer
limits on the conversion of its fired design. If the tube design needs a hotter firebox, the
air can be preheated further only with the preheater ahead of E-102 (the flue gas then reaches
E-102 at 826.9 K, a 104 K approach at its hot end), or a trim fuel at a lower PSA recovery
(SRC-1 reference example 1, D-001).

Departure from SRC-1: its scheme preheats the combustion air, the ammonia and the tail gas
against the cracked gas in its exchanger E101, and its reference example 2 sets the PSA
recovery so that the tail gas covers all the process heat; the text read states no air or stack
temperature. This entry keeps SRC-1's recovery, 79.4 %, but integrates differently: the cracked
gas vaporises the liquid feed (E-101, D-005) and the flue gas preheats the air, as SRC-2's fired
design does in its convection banks (a combustion air preheater among them). The recovery is
therefore SRC-1's figure for a scheme whose heat integration differs, and the stack temperature
is a result here, not a choice: 492 K, against 454 K in SRC-2. Cooling the flue gas to 454 K
would free 1.88 MW, which a higher recovery could use (L-5: no spec on a temperature yet).

NOx: the tail gas holds 3.2 mol% ammonia, which burns partly to NO (fuel NOx); unburnt slip and
N2O are possible. No open factor was read for this fuel at this scale, so the flowsheet burns it
to N2 and the LCI declares the open emission (`emission_exclusions`, D-010, L-3). Low-NOx burners
or an SCR on the flue gas (which would use a little of the ammonia) are a basic-stage decision.

## D-007 Hydrogen recovery and ammonia use (2026-11-19)

The plant recovers 77.35 % of the hydrogen in the ammonia (0.9742 x 0.794; SRC-1 reference
example 2: 77.05 %) and needs 7.281 kg of ammonia per kg of H2, 7.272 kg per kg of the product with its 84 ppm(mol) of
nitrogen (JRC: 0.137 t/t, 7.30 kg/kg
for SRC-2's design with ammonia fuel and recycle, SRC-3). The hydrogen product carries 88.5 % of
the ammonia's LHV: the cracking heat, supplied by burning the rest, is stored in the hydrogen.

## D-008 Heat and power: every energy flow (2026-11-19)

Every enthalpy is on the elements basis of the ideal-gas data of materials.yaml, the liquid
ammonia's warming and vaporization from thermo's HEOS_FIT correlations (SRC-5).
`scripts/balance.py` (balance-output contract, library ADR 0027) gives the values core does not
calculate; propagate writes Q2.

| stream | value | basis |
|---|---|---|
| Q1 | 53596.4 kW | R-101: H(S4) - H(S3); core's equilibrium model writes no duty (L-1) |
| Q2 | 17280.0 kW | propagate: H101's heat release less Q1 and Q5; the script's E-102 duty (S2 to S3) is 17279.9 kW |
| Q4 | 20310.3 kW | E-101: liquid S1 at 293.15 K warmed to saturation (308.15 K at 1350 kPa(a)), vaporised (19.12 kJ/mol) and superheated to 313.15 K |
| S5 | 423.82 K | the cracked gas after giving up Q4 |
| Q3 | 6321.3 kW | E-103: S5 to 313.15 K, to cooling water |
| S10, W1 | 303.31 K, 151.2 kW | K-101: 101.325 to 106 kPa(a), isentropic efficiency 0.75, drive 0.95 (ASSUMED) |
| Q5 | 9091.6 kW | E-104: the air S10 heated to S12's 623.15 K (ASSUMED, D-006) |
| S11 | 492.04 K | the stack temperature at which S8 and S12 burnt give Q1 + E-102's duty + Q5 |

The lower heating values behind the 80.1 MW fired and the 88.5 % figures (D-006, D-007) follow
from the same formation enthalpies, with the water as vapour: H2 241.822 MJ/kmol (that of
H2O(g)), NH3 1.5 x 241.822 - 45.558 = 317.175 MJ/kmol; scripts/balance.py computes them from
materials.yaml.

The vapour is taken as an ideal gas from its saturation point (its departure at 1.35 MPa, of
the order of 1 kJ/mol, is left out, L-2). Per kg of hydrogen product: 0.0181 kWh of electricity, 0.758
kWh to cooling water; no steam is imported or exported.

## D-009 Hazards (2026-11-19)

- **Ammonia.** Toxic and corrosive to eyes and lungs, flammable in air over a narrow range;
  the plant holds it as pressurised liquid (1500 kPa(a)) and hot vapour. Toxic-gas detection,
  isolation of the liquid inventory and relief to a safe location are basic-stage items; the
  exposure and flammability limits are to be taken from a safety data sheet (none read here).
- **Hydrogen.** The cracked gas (74 mol% H2) and the product are highly flammable over a wide
  range and leak readily; the PSA's beds cycle between 1060 and 130 kPa(a). Area
  classification and fire and gas detection are basic-stage items.
- **Materials at temperature.** Hot ammonia nitrides steels and hot hydrogen attacks carbon
  steel; the tubes, the hot end of E-101 and the outlet header see both at 773 K and 11 bar.
  Material selection is open (D-004).
- **Furnace.** A fired heater on a hydrogen-rich, low-calorific tail gas whose rate swings with
  the PSA cycle: burner management, flame detection, purge before light-off and a fuel buffer
  are needed; loss of feed with the burners firing overheats the tubes (no cracking heat
  sink). The reaction is endothermic, so there is no thermal runaway of the reactor;
  core's semi-batch thermal screening does not apply to it.

## D-010 Preliminary gate-to-gate LCI (2026-11-19)

`lca/lca.yaml` takes every exchange of the design case per kg of hydrogen (`cheme assess lca
--write`). In the Atlas LCI (`scripts/build_lci.py`), lca/mappings.yaml links the ammonia
directly to ammonia-1 (as acrylonitrile-1 and caprolactam-1 do); the library has no ammonia
market yet (a parallel change adds `markets/ammonia.yaml`; once it is merged this feed may link
through it). The shared lci/mappings.yaml links electricity (medium voltage) and cooling water
(its screening proxy per kWh rejected). Air is free. The flue gas's N2, O2, Ar and water are
free; its hydrogen and ammonia are elementary flows at zero (not estimated, see the exclusion);
no CO2 is emitted on site. One product, no allocation.

Not in the inventory:
- **Burner NOx, N2O and ammonia slip** (D-006): an open emission exclusion declared in
  lca/lca.yaml (`emission_exclusions`), not a measured zero.
- **Fugitive ammonia and hydrogen**: not estimated without a P&ID; declared likewise.
- **The cracking catalyst's and the PSA adsorbents' replacement**: no open rate read; neither
  inventoried nor cut off, an open input. It is noted only in a comment of lca/lca.yaml, so it
  does not reach the dataset or gaps.csv (a `cutoff:` entry needs a mass to check, and none is
  known).
- **Energy outside the boundary**, stated with its size: the pumping (about 49 kW) and warming
  (4.10 MW) of the ammonia between ammonia-1 and S1 (D-003), and the PSA's valves and instrument
  air (ASSUMED below 20 kW, D-005).

## Method and dependency table

| value | from | changes when |
|---|---|---|
| feeds S1, S9 and every other flow and composition | propagate: specs, R101 (equilibrium), U201 (recovery), H101 (conversion) | reactions.yaml, the split, the targets, R101's outlet temperature or pressure |
| Q2 | propagate: H101's conversion duty | H101's streams or Q1 |
| Q1, Q3, Q4, Q5, W1, the temperatures of S5, S10 and S11 | scripts/balance.py | any stream (rerun the script after propagate, then propagate again) |
| LCA outputs | cheme assess lca --write | the flowsheet or lca.yaml |

## Core features used (core 1.13.0)

- `specs:` with two design specifications, the product rate and a flue gas fraction (ADR 0070)
- `recovery:` component separator for the PSA (ADR 0070)
- `reactor: equilibrium` on ideal-gas data for a gas-phase reversible reaction
- `reactor: conversion` with two combustion reactions and its duty through `energy_port` with
  the step's two other energy streams (Q1, Q5) given (ADR 0059)
- `ideal_gas` data for every component, fitted to 1500 K by `cheme chemistry thermo --fit`

## Core limits hit (each a candidate core issue)

- **L-1** The equilibrium reactor writes no duty: R-101's heat Q1 comes from the script as the
  enthalpy difference of its streams. A conversion step's duty (ADR 0059) extended to an
  equilibrium step would make it `calculated` and keep it current.
- **L-2** No property package for liquid ammonia or for ammonia vapour near saturation (the
  `syngas-pr-vapor` package covers ammonia only pure or dilute in a vapour): the vaporiser's
  duty is computed outside core from thermo's correlations, and the vapour is ideal.
- **L-3** No emission model for a combustion step: fuel NOx from ammonia, N2O and slip cannot be
  given as a sourced factor on the conversion reactor, so the burners are complete combustion
  and the NOx an exclusion.
- **L-4** No kinetic model sized against an open rate: the tubes, catalyst volume and heat flux
  are not sized (a fixed-bed model needs a rate law, SRC-7).
- **L-5** No spec on a duty or a temperature (ADR 0070 follow-up): the furnace closes by a
  stack temperature solved in the script; a spec could instead set the PSA recovery so that the
  tail gas just covers the process heat at a fixed stack temperature (SRC-1 set its recovery so
  that the tail gas covers the process heat; the text read states no stack temperature).

## Open inputs

- Kinetics of the cracking catalyst and vendor tube data, for sizing R-101 (L-4) and checking
  that the tubes take Q1 at the 993 K bridgewall (D-006).
- A NOx (and N2O, slip) factor for ammonia-bearing tail gas, and the abatement it needs (D-006).
- Catalyst and adsorbent lives for the LCI (D-010).
- Ammonia's and hydrogen's exposure and flammability limits from a safety data sheet (D-009).
