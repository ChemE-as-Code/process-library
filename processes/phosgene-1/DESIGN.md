# Design decisions

One entry per decision: what was decided, why, what was rejected, and what it assumes.
Phosgene from CO and chlorine, issue ChemE-as-Code/process-library#164. Concept stage: design
basis, balanced BFD/PFD and a preliminary gate-to-gate LCI. Out of scope here: P&IDs, layout,
HAZOP, TEA, datasheets.

Starting point (2026-10-28): library `main` at 11d50ef, cheme-as-code 0.8.0 (pyDEXPI 2.1.0).

## Source register

Facts are restated in our own words; nothing is copied. "Read" means the passage given was read
in this session.

| id | source | locator | access / terms | used for |
|---|---|---|---|---|
| SRC-1 | Hughes, R.; Rossi, G. E.; Lennon, D. (2023) Operational parameters relevant to the examination of phosgene synthesis catalysis. *React. Chem. Eng.* 8, 3150-3161, doi:10.1039/D3RE00354J | sect. 1 (route, heat of reaction -107.6 kJ/mol citing Mitchell 2012, world output about 12 Mt/a, 95 % to polyurethanes and polycarbonates); sect. 2.1.1, eqn (1) (phosgene destroyed in aqueous NaOH to Na2CO3 and NaCl; chlorine also absorbed); sect. 2.1.2 (industrial peak bed temperatures above 750 K); sect. 3.2.3 (CCl4 seen in industrial operation, attributed to chlorine attacking the carbon; temperatures above 723 K occur industrially) | read; open access, CC BY 3.0 | route, heat of reaction cross-check, scrubber chemistry, hot spot and CCl4 notes |
| SRC-2 | EP1640341A2, Bayer MaterialScience AG, published 2006-03-29: process and apparatus for the production of phosgene | description and claims (Google Patents text, no paragraph numbers): CO molar excess 2-20 % (preferably 5-12 %); gas and tubes at 1.5-10 bar(a) (preferably 2-5); tubes 1-6 m long, 20-100 mm inside diameter, 100-10 000 tubes; extruded activated carbon about 2-4 mm; shell-side water boiling at 0.1-0.8 bar(a) (preferably 0.2-0.3, i.e. 60-70 C), its vapour condensed and returned; phosgene leaving below 100 C; Cl2 in the phosgene below 50 ppm (stated achievable below 20 ppm); carbon steel without corrosion; optional second stage on the CO-rich gas after condensation | read; patent document (facts only) | D-004, D-005, D-007, equipment notes |
| SRC-3 | Mitchell, C. J. et al. (2012) Selection of carbon catalysts for the industrial manufacture of phosgene. *Catal. Sci. Technol.* 2, 2109-2115, doi:10.1039/C2CY20224G | - | not read (publisher refused access, HTTP 403); known only through SRC-1 and patent citations | heat of reaction (via SRC-1); catalyst deactivation by O2 and CCl4 formation (secondary) |
| SRC-4 | Cotarca, L. et al. (2019) Phosgene. *Ullmann's Encyclopedia of Industrial Chemistry*, doi:10.1002/14356007.a19_411.pub2 | - | not read (licensed); listed by the issue | reference lead only |
| SRC-5 | EU JRC (2017) BAT Reference Document for the Production of Large Volume Organic Chemicals, EUR 28882 EN (JRC109279) | - | identified, not read in this session (open) | to be read for isocyanate/phosgene emission levels (open) |
| SRC-6 | chemicals 1.5.2 and thermo 0.6.1 packages of core's environment (open-source, MIT; the versions core pins), through `cheme chemistry thermo` and `cheme chemistry props --source Thermo`: gas formation enthalpies from chemicals' Active Thermochemical Tables 1.112 data (`ATCT_G`); standard entropies from its packaged CRC Handbook table `heat_capacity.CRC_standard_data` (from the CRC Handbook of Chemistry and Physics, 2014 edition as chemicals cites it; a licensed book, not read here); normal boiling points from chemicals' `Tb` (phosgene's from the packaged CRC organic table `miscdata.CRC_organic_data`); critical constants and the ideal-gas cp/R fits (to thermo's HEOS_FIT, TRCIG and WEBBOOK_SHOMATE correlations) by the methods printed per component in process/materials.yaml; at 253.15 K, phosgene's vapour pressure from thermo's WAGNER_MCGARRY (McGarry 1983, Ind. Eng. Chem. Process Des. Dev. 22, 313; not read here) and its heat of vaporization from thermo's VDI_PPDS correlation, whose coefficients thermo takes from the VDI Heat Atlas, 2nd ed. (Springer 2010; a licensed book, not read here); chlorine's vapour pressures and heat of vaporization from thermo's HEOS_FIT (fits to CoolProp's reference equation of state); phosgene's Antoine equation above 281 K from the NIST Chemistry WebBook, SRD 69 (C75445, fitted by NIST to Stull 1947); water's vapour pressure from IAPWS-95 | printed per component in process/materials.yaml and scripts/balance.py: phosgene 30.565 kPa and 26.019 kJ/mol at 253.15 K; chlorine 180.378 kPa and 19.768 kJ/mol at 253.15 K, 1007.963 kPa at 308.15 K | open-source packages queried; single values, facts only. The VDI_PPDS value (26.019 kJ/mol) is not open data; it is a single fact from coefficients a package bundles, with its source named (library ADR 0037) | ideal-gas data, vapour pressures, heats of vaporization |
| SRC-7 | processes/chlor-alkali-1 (this library) | process/flowsheet.yaml stream S42 (dry chlorine product, 400 kPa(a), 313 K, 99.19 wt% Cl2, 0.81 wt% O2), D-002 (12 500 kg/h Cl2) | library, internal | chlorine feed link (D-002, D-003) |

The open issue's handoff asked not to search for published "answers"; no benchmark plant
figures were looked for or used. The capacity is a library coupling, not a published plant.

## D-001 Route and boundary (2026-10-28)
Decision: Phosgene by the gas-phase reaction CO + Cl2 -> COCl2 over activated carbon in a
cooled multitubular reactor (SRC-1 sect. 1, SRC-2), followed by condensation of the phosgene,
caustic scrubbing of the residual phosgene and chlorine in the vent (SRC-1 sect. 2.1.1) and
thermal oxidation of the CO-rich vent. Continuous captive production: the liquid phosgene goes
to an adjacent isocyanate plant without storage in the boundary. Boundary feeds: CO, chlorine,
caustic soda, process water, air, electricity; utility returns: cooling water, brine.
Reason: the case brief prescribes this route; it is the industrial route named by every source
read. Captive, storage-free supply keeps the phosgene inventory small (D-011).
Rejected: other phosgene routes (from CCl4 and oleum, or triphosgene) are laboratory or
historical routes, not considered. Downstream chloroformate or isocyanate use stays outside the
boundary (issue scope note).
Links to other library processes: chlorine and 50 wt% caustic soda from chlor-alkali-1; no
library process makes CO yet (a syngas cold box would; methanol-1 and hydrogen-1 make synthesis
gas but not pure CO).

## D-002 Capacity and operating hours (2026-10-28)
Decision: The plant takes the 12 500 kg/h Cl2 of chlor-alkali-1's design case and converts it
all: 17 346 kg/h liquid phosgene (about 139 kt/a). 8000 h/a, ASSUMED.
Reason: no traceable published plant basis is used (issue note); coupling to the library's
chlorine producer gives a consistent integrated case. Per-kg normalisation makes the LCI
independent of scale; the capacity is not a claim about a commercial plant.

## D-003 Feed specifications (2026-10-28)
Decision: CO 99.8 mol%, the rest lumped as N2, at 303 K, 400 kPa(a) (ASSUMED; the supplier
specification of H2, CH4, CO2, sulfur and water is an open input). Chlorine "phosgene grade",
99.9 mol% Cl2 and 0.1 mol% O2, gas at 313 K, 400 kPa(a) (ASSUMED).
Reason: chlor-alkali-1's chlorine product (SRC-7) holds 0.81 wt% O2 (about 1.8 mol%). Used
directly, that O2 would pass the reactor and collect in the vent at about 24 mol% beside some
65 mol% CO, a flammable vent; O2 also oxidises the carbon catalyst (SRC-3 via patent citations).
The chlorine therefore needs liquefaction and re-evaporation (or another O2 removal) first. That
step is not modelled in chlor-alkali-1 and not in this boundary: an open item for the link
(LCI gap note on feed:CL2). With 0.1 mol% O2 the vent holds 1.7 mol% O2.
Assumption: O2 is inert in the reactor (in reality part may burn carbon of the catalyst).

## D-004 CO excess (2026-10-28)
Decision: 5 % molar CO excess over Cl2. Source: SRC-2 (2-20 %, preferably 5-12 %), at the low
end to keep the CO burnt in the oxidiser small. Rejected: a second reactor stage on the
CO-rich gas with make-up chlorine (SRC-2 option) to use up the excess; a candidate for basic
engineering that would cut the CO2 emission (0.022 kg/kg) and the oxidiser.

## D-005 Reactor model (2026-10-28)
Decision: R-101 is a conversion reactor, 99.995 % of the chlorine converted (ASSUMED), outlet
353 K and 350 kPa(a) (SRC-2: below 100 C, 2-5 bar(a)). The heat goes to water boiling in the
shell at 0.2-0.3 bar(a) (SRC-2), whose vapour is condensed against cooling water: the duty
5180.8 kW appears as cooling water (Q1). No steam is raised.
Reason: no kinetics for a commercial carbon are open (SRC-3 not accessible; SRC-1 measures an
apparent activation energy of 43 kJ/mol on one carbon at low conversion, not a rate law fit for
design). The conversion is set so that the liquid phosgene holds < 50 ppm(wt) Cl2 (SRC-2's
target): the balance gives 35 ppm. `cheme process reactors` checks it against the ideal-gas
equilibrium: ln K = 20.4 at 353 K and ln(Q/K) = -8.7, so the conversion is far from any
equilibrium limit at the outlet (the equilibrium is strongly on the phosgene side below about
400 K; the dissociation at the hot spot is not modelled).
Not modelled: the hot spot (above 750 K industrially, SRC-1 sect. 2.1.2), tube number and length,
catalyst mass and life, CCl4 formation (SRC-1 sect. 3.2.3; the product's CCl4 content is an open
quality item), CO dissolved in the liquid phosgene.
Heat of reaction: -108.5 kJ/mol from the formation enthalpies (ATcT), within 1 % of the -107.6
kJ/mol of SRC-1 (citing SRC-3). Core's duty -5180.77 kW equals the script's -5180.76 kW.
Steam raising instead of cooling water (prior art cited by SRC-2) is an open option.

## D-006 Balance method and what core can and cannot calculate (2026-10-28)
Decision: The flows, compositions, temperatures of the separator and scrubber outlets, mixer
temperatures and all duties come from scripts/balance.py (run with `cheme run`), entered as
`assumed` with that source. Core then propagates the mixers, the reactor, the exchangers' pass
through and the oxidiser (`calculated`) and checks every balance.
Method of the script: ideal gas with the Cp/R polynomials of materials.yaml (fitted 298-1500 K,
SRC-6; the condensation at 253 K extrapolates them 45 K); condensation by Raoult's law with
phosgene's NIST Antoine equation above 281 K and the Thermo vapour pressures below (phosgene
30.6 kPa, Cl2 180.4 kPa at 253.15 K); CO, N2, O2 insoluble; liquid enthalpy = ideal-gas
enthalpy minus the Watson-scaled heat of vaporization (phosgene 26.0, Cl2 19.8 kJ/mol at 253 K).
Gated: no benchmarked property package of core covers phosgene (`cheme process
props --coverage`), so core can neither flash V-101 nor evaluate the condensers' energy. The caustic liquor (NaOH, NaCl, Na2CO3, NaOCl in water) is an electrolyte outside core;
the scrubber species are molecular pseudo-components without ideal-gas data, so T-201's energy
is not evaluable either. Where core can evaluate: R-101 duty reproduced, X-301 adiabatic (0.0004
kW), element balances of every reactive step closed.

## D-007 Condensation (2026-10-28)
Decision: Two stages at 345 / 340 kPa(a): E-102 to 308 K against cooling water (1078.5 kW,
partial condensation), E-103 to 253 K against brine at 243/248 K (482.0 kW), separator V-101.
The vent carries 0.53 % of the phosgene formed (9 mol% of the vent) to the scrubber: the
phosgene yield on chlorine is 99.47 %.
Reason: phosgene boils at 281 K; at 3.4 bar a brine stage is needed to keep the loss to the
scrubber small. Colder condensation or a second reactor stage (D-004) would cut the loss; a
solvent absorber (as in isocyanate plants) is the other common recovery and is not chosen here.
Brine temperature levels ASSUMED.

## D-008 Residual phosgene destruction: caustic scrubber (2026-10-28)
Decision: T-201 scrubs the vent with 18 wt% NaOH (50 wt% caustic diluted with process water),
1.5 x the stoichiometric NaOH, destroying 99.99 % of the phosgene (COCl2 + 4 NaOH -> Na2CO3 +
2 NaCl + 2 H2O, SRC-1 eqn (1), whose water coefficient as printed does not balance; 2 is used)
and of the chlorine (Cl2 + 2 NaOH -> NaCl + NaOCl + H2O). All three figures ASSUMED. The gas
leaves water-saturated at 303 K, 120 kPa(a); the spent liquor (1319 kg/h, 3 mol% each NaOH and
NaCl, 1.5 mol% Na2CO3, traces of NaOCl) goes to the site wastewater treatment, where the
hypochlorite traces are destroyed (outside the boundary). The CO is not absorbed (SRC-1 notes
CO is slowly converted to carbonate in caustic; neglected). Heat of neutralisation leaves with
the liquor (no cooler; not evaluable in core, D-006).
The same scrubber is the emergency scrubber of the containment (D-011); its sizing for a
release case is open.

## D-009 CO-rich vent: thermal oxidiser (2026-10-28)
Decision: X-301 burns the scrubbed vent (8.8 kmol/h CO) with air, adiabatic, outlet 1123 K
(ASSUMED); the air flow (2526 kg/h) is set by that temperature. 99.9 % of the CO and 99 % of the
residual phosgene (hydrolysed to CO2 and HCl) are destroyed (both ASSUMED). No support fuel in
the design case (the vent is 91 mol% CO); pilot and start-up fuel and thermal NOx are declared
emission exclusions (no sourced factor). No heat recovery (0.69 MW of combustion heat leaves
with the flue gas: an open energy-integration option).
Emissions per kg phosgene (stream S32): CO2 22.4 g (fossil), CO 14.2 mg, HCl 0.39 mg,
phosgene 5.3 ug, Cl2 0.1 ug.
Rejected: release of the scrubbed vent without oxidation (CO emission), and the site flare
(utility-flare) as the destination (keeps the emissions in another dataset).

## D-010 Pressure profile and power (2026-10-28)
Decision: feeds at 400 kPa(a), so no compressor: mixer 390, reactor outlet 350, condensers 345
/ 340, scrubber 120 kPa(a) after a let-down valve, oxidiser at atmospheric pressure. Power, all
ASSUMED: coolant-circuit vacuum pump 10 kW (SRC-2 removes inerts from the sub-atmospheric
coolant space), scrubber circulation 4.4 kW (30 m3/h, 300 kPa, pump 0.60, motor 0.95), air
fan 4.8 kW (5 kPa, fan 0.65, motor 0.95). The refrigeration unit's power is in the brine
exchange's background, not in feed:POWER (D-012).

## D-011 Containment and inventory (2026-10-28)
Decision (noted, not designed): phosgene is acutely toxic at low concentration (SRC-1 sect.
1-2). The reactor, condensers and separator sit in a closed containment enclosure whose
extracted air goes to the scrubber T-201; the liquid hold-up of V-101 is kept small and there
is no phosgene storage in the boundary (captive, on-demand supply). Detection, emergency
neutralisation (e.g. steam/ammonia curtains), the scrubber's release case, and fugitive
emissions belong to basic engineering and the HAZOP, which are out of scope here.

## D-012 Preliminary gate-to-gate LCI (2026-10-28)
Decision: lca/lca.yaml: functional unit 1 kg liquid phosgene at the gate (stream S7); every
foreground exchange taken from the balanced flowsheet; every background deliberately
unmapped (`missing:` with the activity it should connect to), so each is a gap, never zero, and
no value from a licensed database is used. The plant's own emissions are elementary flows to
air (non-urban high stack ASSUMED for a site not chosen). Boundary key cradle-to-gate, as in
sulfuric-acid-1, so that purchased inputs stay open gaps. No co-product: no allocation.
Inventory per kg phosgene (`cheme assess lca --inventory --write`): CO 0.2995 kg, Cl2 (with
0.1 mol% O2) 0.7210 kg, NaOH 50 wt% 0.0256 kg, process water 0.0455 kg, air 0.1456 kg (free),
electricity 0.00111 kWh; outputs: spent liquor 0.0761 kg (to treatment), flue gas 0.1612 kg
(CO2 0.0224 kg, CO 1.42e-5 kg, HCl 3.9e-7 kg, phosgene 5.3e-9 kg, Cl2 1.1e-10 kg, N2, O2, Ar,
H2O returned), heat to cooling water 0.361 kWh, heat to brine 0.0278 kWh.
Check against the flowsheet: inputs 21 461.2 kg/h = outputs 21 461.2 kg/h; `cheme assess lca
--balance` closes mass (0.00 %), every element (largest residual C -0.01 %) and carbon by
origin (fossil in 2223.3 kg C/h = product 2106.3 + spent liquor 11.1 + emissions 106.0).
Coverage: "partial screening carbon footprint", 12 gaps (8 unmapped exchanges and 4 emissions
the climate method does not characterise). Excluded and listed: construction, end of life,
transport, catalyst (activated carbon) replacement (amount unknown), oxidiser NOx, fugitive
emissions.

## D-013 Missing shared entries (for the consolidated library PR) (2026-10-28)
Not changed here (shared files are out of this run's scope):
- chemicals/chemicals.yaml: phosgene (main product), carbon-monoxide, chlorine,
  sodium-hydroxide (50 wt% solution grade), refrigeration/brine utility (243 K); possibly
  hydrogen-chloride, sodium-carbonate, sodium-hypochlorite for the liquor.
- lci/mappings.yaml technosphere: carbon monoxide (cold box), chlorine (chlor-alkali-1, phosgene
  grade incl. liquefaction), sodium hydroxide 50 wt%, refrigeration at 243 K.
- lci/mappings.yaml biosphere: phosgene, chlorine and hydrogen chloride to air (CO has one in
  core's crosswalk; the strict build reports CL2, COCL2, HCL as gaps).
- core's elementary-flow crosswalk: CAS 75-44-5, 7782-50-5, 7647-01-0 to air.
- taxonomy: phosgene is filed under chlorinated-organics; a family for isocyanate precursors
  may be preferred.
- chlor-alkali-1: a phosgene-grade chlorine product (liquefaction and re-evaporation, O2
  removal) for this link.

## Calculation maturity (2026-10-28)
`cheme maturity` reaches no level. "Sourced" fails because the feed flows and compositions are
assumed (no owner-given or sourced feed); "balanced" fails only on the model basis (the
conversions of R101, T201 and X301 are assumed), while its rules, evaluable balances and closed
balances pass. Energy closure is not evaluable (no property package for the streams, D-006).
The process.yaml claim stays `concept`. A sourced CO specification, a sourced conversion or
space velocity for the carbon, and sourced destruction efficiencies (e.g. from SRC-5) would
lift it to "balanced".

## Open inputs and gated steps
- CO supplier specification (H2 forms HCl, CH4 forms CCl4-type by-products, sulfur poisons),
  chlorine O2 and CO2 content; product CCl4 specification.
- Kinetics or a sourced space velocity for the activated carbon (tube count, catalyst mass,
  hot spot); catalyst life and its replacement in the LCI.
- Core: phosgene VLE and condensation energy; caustic liquor energy.
- Emission factors for the oxidiser (NOx) and fugitive emissions (needs P&IDs).
- Steam raising from the reaction heat and heat recovery from the oxidiser.
