# Design decisions

One entry per decision: what was decided, why, what was rejected, and what it assumes.
Demineralised water from fresh surface water, issue ChemE-as-Code/process-library#470, a site
utility of the library (#45). Concept stage: design basis, balanced BFD/PFD with the RO and
the mixed beds as specified splits, a balance script for what core cannot model, and a
preliminary gate-to-gate LCI linked to the library's acid, caustic and wastewater producers. Out
of scope here: P&IDs, layout, HAZOP, TEA, datasheets.

Starting point (2026-11-19): library `main` with the core pin 0e85885 (v1.12.0 and #254).
Core has no membrane or ion-exchange model (`cheme process` separations coverage: membrane
separation is a specified split, L-1); since core ADR 0070 a component separator with given
recoveries is solved by `cheme process propagate`, and a design specification solves a feed for
a product rate. Templates: `oxalyl-chloride-1` (structure, LCI links to library producers) and
`hydrogen-chloride-1` (a continuous concept entry with a balance script). Requires cheme-as-code
1.12 (plant.yaml).

## Source register

Facts are restated in our own words; nothing is copied. "Read" means the passage named was read
in this work.

| id | source | locator | access / terms | used for |
|---|---|---|---|---|
| SRC-1 | DuPont Water Solutions (2021) FilmTec Reverse Osmosis Membranes Technical Manual, Form No. 45-D01504-en, Rev. 8, September 2021; read in the copy at https://kh.aquaenergyexpo.com/wp-content/uploads/2022/09/FilmTec%E2%84%A2-Reverse-Osmosis-Membrane-technical-manual.pdf | p. 11 (section 1.3): salt rejection of RO typically 95 % to above 99 %; p. 22 Tables 3 and 4: an 8-inch BW30 element gives up to 10,500 gpd (1,660 L/h), tested on 2000 ppm NaCl at 15.5 bar, 25 C, pH 8, 15 % recovery; p. 60 (media filtration): dual-media filters of anthracite over sand, filtration at 10 to 20 m/h, backwash at 40 to 50 m/h for about 10 min, pressure filters with 2 to above 4 bar available, rinse to drain after backwash; p. 100 Table 22: surface water with conventional pretreatment, SDI < 5, design flux 20 to 27 L/(m2 h); p. 104 to 105: ion-exchange mixed beds or EDI polish RO permeate for very low dissolved solids, and a mixed bed is the alternative to a second RO pass; p. 105 Table 25: brackish systems at 70 to 80 % recovery have 12 elements in series, two stages of six-element vessels; p. 107 to 108 (design example): surface water with SDI < 5 at 23.8 L/(m2 h), BW element of 37.2 m2, two stages at 75 % recovery in a 2:1 array; p. 108: two-stage systems run at 55 to 75 % overall recovery; p. 109: a feed osmotic pressure of 1.4 bar corresponds roughly to 2000 mg/L TDS | read (third-party-hosted copy of the vendor's public manual); vendor document, facts only | D-001, D-003, D-004 |
| SRC-2 | de Dardel, F. Regeneration methods (ion exchange), https://dardel.info/IX/processes/regeneration.html, updated 3 September 2021 | mixed-bed regeneration levels: 80 to 120 g HCl per L of cation resin, 80 to 140 g NaOH per L of anion resin, higher than for separate columns because a mixed bed regenerates less efficiently; regenerant strengths HCl 5 %, NaOH 4 %; caustic first, then acid, each displaced with dilution water, resins remixed with air; injection over 20 to 40 min, then displacement and rinse to quality; SAC in reverse flow with HCl at least 110 %, better 120 % of stoichiometric | read; personal website (c) F. de Dardel, facts only | D-005 |
| SRC-3 | de Dardel, F. Basic ion exchange processes in water treatment, https://dardel.info/IX/processes/processes.html, updated 30 November 2020 | mixed-bed polishing: conductivity below 0.1 uS/cm, silica 1 to 10 ug/L; on RO permeate a run of one or a few days, the CO2 limiting the throughput, the anion resin limiting the capacity; two-bed demineralisation: 5 to 25 uS/cm co-flow, below 1 uS/cm reverse flow | read; personal website, facts only | D-001, D-005 |
| SRC-4 | de Dardel, F. Ion exchange capacity, https://dardel.info/IX/capacity.html, updated 3 March 2021 | total capacity SAC 1.7 to 2.2 eq/L, SBA 0.9 to 1.4 eq/L; operating capacity SAC 0.6 to 1.7, SBA 0.4 to 0.9 eq/L, about 40 to 60 % of the total | read; personal website, facts only | D-005 (cross-check) |
| SRC-5 | de Dardel, F. Neutralisation of regenerants, https://dardel.info/IX/processes/neutralisation.html, updated 10 June 2014 | the mixed regeneration waste counts as neutral at pH 6 to 9; when the excess caustic exceeds the excess acid (no degasser), acid is added until the acid equivalents equal or slightly exceed the caustic's | read; personal website, facts only | D-006 |
| SRC-6 | Cox, J. D., Wagman, D. D. and Medvedev, V. A. (1989) CODATA Key Values for Thermodynamics, Hemisphere; table at https://www.codata.info/resources/databases/key1.html | dHf (298.15 K): H2O(l) -285.830 +/- 0.040, OH-(aq) -230.015 +/- 0.040, H+(aq) 0 kJ/mol | read | reactions.yaml (NEUT) |
| SRC-7 | processes/hydrogen-chloride-1, chlor-alkali-1, utility-wwtp (this library) | hydrochloric acid 33 wt-% (product:HCLACID); caustic soda 50 wt-% (product:NAOH); treatment of wastewater per kg | library, internal | D-005, D-008 |
| SRC-8 | core's skill `utility-boiler-feed-water` (cheme-as-code 1.12.0) | grades from clarified to demineralised water; demineralised water is corrosive, so it is stored and pumped in stainless steel or lined material | read; core documentation | D-001, equipment list |

Searched and not found openly (2026-11-19): a plant's specific consumptions of a RO and mixed-bed
demineralisation (regenerant, electricity and wastewater per m3) that could serve as a benchmark;
the EU BREF for common waste water and waste gas treatment (CWW) was not read in this work; rinse
volumes of mixed-bed regeneration in bed volumes (SRC-2 says only "to quality"); a mixed bed's
operating capacity on RO permeate.

## D-001 Route and boundary (2026-11-19)
Decision: media filtration, a two-stage brackish-water RO and mixed-bed ion exchange polishing,
the mixed beds regenerated in place with hydrochloric acid and caustic soda, the regeneration
effluent neutralised and all wastewater sent to the site's biological treatment:
- PRE: raw-water pump P-101, dual-media pressure filters F-101 (with cartridge filters);
- RO: high-pressure pump P-102, RO M-101 in a 2:1 array, permeate tank T-101;
- IX: mixed-bed feed pump P-201, two mixed beds X-201 (one in service), their regeneration;
- NEU: neutralisation pit T-301 with trim acid, wastewater sump T-302.

Why: RO removes about 99 % of the dissolved salts with electricity only, so the ion exchange
that follows sees a fraction of the raw water's load and its acid and caustic fall
accordingly; a mixed bed is the usual polisher of RO permeate to below 0.1 uS/cm (SRC-1 p. 104
to 105, SRC-3).

Rejected:
- a two-bed cation/anion ion exchange train on the filtered water (with a degasser): reaches
  only 5 to 25 uS/cm co-flow, below 1 uS/cm reverse flow (SRC-3), so it still needs a mixed bed
  for boiler-quality water, and it takes the raw water's whole salt load on its resins, so its
  acid, caustic and saline effluent scale with the raw water's salinity; preferred for very low
  salinity raw water or where wastewater salinity is not limited; a candidate for a
  demineralised-water-2;
- RO with electrodeionisation (EDI) polishing (SRC-1 p. 105): no regeneration chemicals, but
  more electricity and a second RO pass usually ahead of it; not chosen because the library has
  the acid and caustic producers and the EDI's performance would rest on vendor data only;
- a second RO pass instead of the mixed bed (SRC-1 p. 104): does not reach mixed-bed quality;
- thermal processes (evaporation): for seawater or zero liquid discharge, not for fresh water.

Boundary: from the raw-water intake (the water as a resource, after clarification) to the
demineralised water header at 5 bar(a); the wastewater leaves to the site's treatment. Not in
the boundary: raw-water clarification (coagulation and settling), the RO antiscalant and
dechlorination, RO cleaning, resin and membrane replacement (D-008).

## D-002 Capacity, raw water and the product (2026-11-19)
Decision: 50 m3/h (50 000 kg/h) of demineralised water for 8000 h/a, 400 000 m3/a (ASSUMED, a
mid-size site plant for boiler make-up and process water). Raw water: fresh surface water,
clarified, 500 mg/kg of dissolved solids lumped as NaCl (ASSUMED), at 25 degC, the membranes'
rating temperature (SRC-1 p. 22). Product: below 0.1 uS/cm (a mixed bed's quality, SRC-3),
modelled with 0.02 mg/kg of residual salt, at 5 bar(a) and 25 degC into the site header.
Why lumped as NaCl: core has no electrolyte or carbonate chemistry for these streams (L-2); one
monovalent salt keeps the equivalents of the ion exchange simple and the mass balance exact.

## D-003 Media filters (2026-11-19)
Decision: dual-media pressure filters at 15 m/h (SRC-1 p. 60: 10 to 20 m/h), backwashed every
24 h (ASSUMED) at 45 m/h for 10 min (SRC-1 p. 60: 40 to 50 m/h, about 10 min) and rinsed to
drain for 10 min at 15 m/h (ASSUMED): (45 x 10/60 + 15 x 10/60) / (15 x 24) = 2.78 % of the
filtered water goes to the sump (F101's `split:`). About 4.6 m2 of filter area in service.
Suspended solids are not carried (they would leave with the backwash); air scour is not counted.

## D-004 Reverse osmosis (2026-11-19)
Decision: two stages of six-element vessels in a 2:1 array at 75 % water recovery (SRC-1 p. 105
Table 25, p. 107 to 108); salt rejection 0.99 on the mean feed-side concentration (ASSUMED,
within SRC-1 p. 11's 95 to above 99 %). The share of the feed's salt in the permeate is the
rejection's complement times the log-mean concentration factor of a plug-flow array,
-ln(1 - r)/r = 1.848 at r = 0.75, times r: 0.01386 (M101's `recovery:`; the permeate has about
9 mg/kg of salt). Flux 23.8 L/(m2 h) on 37.2 m2 elements (SRC-1 p. 107): 57 elements, 10 vessels
of six in a 7:3 array.

Feed pressure from the element's tested permeability (scripts/balance.py): 1,660 L/h over 37.2
m2 at a net driving pressure of 15.5 - 1.4 bar (the test pressure less the osmotic pressure of
2000 ppm, SRC-1 p. 22, p. 109) gives 3.16 L/(m2 h bar), taken at 0.85 for fouling and ageing
(ASSUMED); the design flux then needs 8.85 bar of net driving pressure, plus the mean osmotic
pressure (0.35 bar at 500 mg/kg, scaled from SRC-1 p. 109, times 1.848), half of an ASSUMED 3 bar
pressure drop over the array and 0.5 bar of permeate back-pressure (ASSUMED): 12.5 bar(a). Colder
water needs more pressure (the permeability falls with temperature); a design at the site's
minimum water temperature is an open input. No energy recovery from the concentrate: at
brackish-water pressures and 25 % concentrate it is rarely fitted (ASSUMED).

## D-005 Mixed beds and their regeneration (2026-11-19)
Decision: two mixed beds of 1.25 m3 of resin each (50 m3/h at 40 bed volumes per hour, ASSUMED),
40 % strong acid cation and 60 % strong base anion resin by volume (ASSUMED), one in service, the
other regenerating or on standby. A service run of 72 h (ASSUMED; SRC-3: one or a few days on RO
permeate, limited by the CO2 the permeate carries). Per regeneration (scripts/balance.py):
- 100 g HCl per L of cation resin (SRC-2: 80 to 120 g/L), 50 kg HCl, as 33 wt-% acid diluted to
  5 wt-% (SRC-2);
- 110 g NaOH per L of anion resin (SRC-2: 80 to 140 g/L), 82.5 kg NaOH, as 50 wt-% caustic
  diluted to 4 wt-% (SRC-2);
- 15 bed volumes of backwash, displacement and rinse water (ASSUMED: SRC-2 gives no volume);
- the dilution and rinse water is RO permeate from T-101 (ASSUMED; mixed-bed product would be
  the stricter choice and would make a recycle).

Year averages over 111 regenerations a year: 2.104 kg/h of 33 wt-% acid, 2.292 kg/h of 50 wt-%
caustic, 298.6 kg/h of regeneration water. The beds let 0.2 % of the permeate's salt through
(ASSUMED, X201's `recovery:`); the 0.461 kg/h of salt they hold is released at regeneration
(stream S12, a bookkeeping stream of the year average, not a pipe).

Cross-check: the regenerants are 2.4 (acid) and 3.6 (caustic) times the salt the beds take up in
equivalents. That is higher than the 1.1 to 1.2 of separate reverse-flow columns (SRC-2), as a
mixed bed regenerates less efficiently (SRC-2), and the anion resin also takes up the permeate's
CO2, which the model does not carry (L-2). With SBA's operating capacity of 0.4 to 0.9 eq/L
(SRC-4), 0.75 m3 of anion resin holds 0.30 to 0.68 kmol a run, against 0.033 kmol of NaCl
taken up in 72 h: the run is not capacity-limited by the salt, and the 72 h stands for the CO2
load and a regular regeneration (an open input with a measured CO2 of the permeate).

## D-006 Neutralisation and wastewater (2026-11-19)
Decision: the regeneration effluent is collected in the neutralisation pit T-301; since the
caustic's equivalents (28.6 mol/h) exceed the acid's (19.0 mol/h), trim acid is added until the
acid equivalents are 1.001 times the caustic's (SRC-5): 1.064 kg/h of 33 wt-% acid. R301 lumps
the regenerants' reaction HCl + NaOH -> NaCl + H2O (conversion 1 on NaOH): what the resin does
in regeneration (the salt it held released, the acid and the caustic regenerating it) and what
the pit does (the excesses) give the same year-average mass balance as one neutralisation
(reactions.yaml). Its heat, 0.44 kW (core's conversion model with SRC-6), warms the effluent and
is lost (E5). The neutralised effluent (pH 6 to 9, SRC-5), the filter backwash and the RO
concentrate (about 2.0 g/kg of salt) are mixed in the sump T-302 and sent to the site's
biological wastewater treatment: 19.0 t/h, 0.380 kg per kg of product with 0.72 g of salt (0.69 g from the raw water, 0.03 g formed by the neutralisation)
(stream S18). The biological treatment does not remove the salt: in practice RO concentrate and
backwash often go to a sewer or a surface water under a discharge permit; sending them to
treatment is the conservative choice of the LCI (D-008).

## D-007 Pumps and power (2026-11-19)
Decision: pump and motor efficiency 0.70 (ASSUMED) for the raw-water pump (1.013 to 4 bar(a),
the pressure filters' head, SRC-1 p. 60), the RO high-pressure pump (2 to 12.5 bar(a)) and the
mixed-bed feed and forwarding pump (1.013 to 6 bar(a): 1 bar over the bed to the 5 bar(a)
header), and 3 kW year average for the dosing and regeneration pumps, the resin-mixing blower
and the instruments (ASSUMED). Total 49.05 kW, 0.98 kWh per m3: RO pump 0.56, forwarding pump
0.20, raw-water pump 0.16, auxiliaries 0.06 kWh/m3 (scripts/balance.py). No heat duties: the
plant works at ambient temperature.

## D-008 Preliminary gate-to-gate LCI (2026-11-19)
Decision: the inventory per kg of demineralised water (lca/lca.yaml, `cheme assess lca
--write`): 1.380 kg of raw water withdrawn from a river (a water resource, `resource: true`; its
dissolved salts free, as they leave again with the wastewater), 0.0634 g of 33 wt-% hydrochloric
acid, 0.0458 g of 50 wt-% caustic soda, 0.98 Wh of electricity and 0.380 kg of wastewater to
treatment. In the Atlas build (lca/mappings.yaml): the acid links hydrogen-chloride-1's
product:HCLACID, the caustic chlor-alkali-1's product:NAOH (both kg of solution for kg), the
electricity the shared grid entry, the wastewater utility-wwtp (by its registry slug). The
product is the registry grade water/demineralised, the supplier of the new market
`markets/water.yaml` (an on-site header, 1 km ASSUMED, no losses counted).

Consequence for the library: every input of the registry substance `water` (process water,
boiler feed water, wash water of about 40 processes) was already read by the shared `water`
entry of lci/mappings.yaml as deionised water; with prefer_atlas (the default) these inputs now
link this market instead of the background, as #45 intends. A consumer whose water is not
demineralised (a raw make-up) keeps the background with an `atlas: false` override in its own
mappings; deciding that is each consumer's own review. The loop chlor-alkali-1 -> caustic ->
demineralised water -> chlor-alkali-1's water is a real supply loop and is solved by the
background's matrix.

Not in the inventory (open, each a candidate refinement): the RO antiscalant and
dechlorination (sodium bisulfite) dosing, RO cleaning chemicals, resin replacement (a few years'
life) and membrane replacement (about five years), the raw water's clarification; the salt
discharged with the wastewater as an emission to water (the WWTP's dataset counts the water,
not the salt). The raw-water feed itself (feed:RAW) is reported as a mapping gap by build_lci:
the build skips an output released to the environment but not an input taken from nature,
which it counts by its resource:* exchanges (resource:H2O here, linked); a candidate library
fix (L-4). Construction excluded.

## D-009 Id and family (2026-11-19)
Decision: the id `demineralised-water-1` in the family `utilities`, not `utility-demin`. The
library's `utility-*` folders are manifest-only Tier 1 utilities with one hand-written
parameterised dataset in `lca/datasets/` each, and tests/test_utilities.py,
tests/test_export_formats.py and tests/test_lci_brightway.py treat every `utility-*` folder that
way; this entry is a Tier 2 engineering project with a flowsheet and a generated
`lca/dataset.yaml`, so it follows the `<coverage id>-<n>` convention of the engineering entries
(coverage id `demineralised-water`, rank 59), which leaves room for another route
(demineralised-water-2: an ion-exchange train or EDI, D-001). It is still a utility in what it
does: family `utilities`, its product linked by default (D-008).

## Method and dependency table

| step | status | basis |
|---|---|---|
| mass and component balances | done in cheme | cheme validate / process streams / propagate --check |
| raw water for the product rate, regeneration water share | done in cheme (specs) | core ADR 0070, D-002, D-005 |
| filter backwash split, RO split, mixed-bed split | done in cheme (splitter, component separators), splits from the script and sources | D-003, D-004, D-005, L-1 |
| RO salt passage, feed pressure, element count | script | D-004 |
| resin volume, regenerant doses, rinse water, trim acid | script | D-005, D-006 |
| neutralisation and its heat | done in cheme (conversion step, energy port) | D-006, SRC-6 |
| pump powers | script | D-007 |
| LCI inventory | done; acid, caustic, power and wastewater linked in the Atlas build | D-008 |

## Core features used (core 1.12.0)

- Component separators with `recovery:` (ADR 0070) for the RO M101 and the mixed bed X201; a
  splitter with `split:` for the filters' backwash F101.
- `specs:` (ADR 0070): the raw-water feed S1 varied for 50 000 kg/h of product, and the permeate
  tank's regeneration share varied for the script's regeneration water.
- A conversion step R301 with `energy_port` (ADR 0059): the heat of neutralisation calculated.
- `lca.yaml` with a resource feed (`resource: true`, the water as `water-river`), a waste
  `treatment`, `emission_exclusions`, a library mapping file with Atlas `dataset` links.
- The balance-output contract (library ADR 0027) for scripts/balance.py.

## Core limits hit (each a candidate core issue)

- L-1: no membrane or ion-exchange model: the RO's salt passage and the feed pressure, and the
  mixed bed's leakage, capacity and regenerant demand, are a script's and the specified splits'
  (`cheme process` coverage: membrane separation is a specified split). A solution-diffusion RO
  element model (permeability, osmotic pressure, concentration polarisation, staging) and an
  ion-exchange equilibrium and regeneration model would make D-004 and D-005 calculated.
- L-2: no aqueous electrolyte or carbonate chemistry for these streams: the dissolved solids
  are one lumped NaCl, without hardness, alkalinity, silica or dissolved CO2, which set the RO's
  scaling limit (and its antiscalant or acid dose) and the mixed bed's anion load
  (`cheme process electrolyte` covers aqueous NaCl properties only).
- L-3: a run-and-regenerate cycle of a fixed bed (service for 72 h, then a regeneration) has no
  form in the flowsheet or the recipe for a continuous plant: the regeneration is a year average
  (S12 carries the bed's load to its regeneration as a stream).
- L-4 (library, not core): build_lci reports a feed taken from nature (`resource: true`) as a
  mapping gap, although its components are counted as resource:* exchanges (D-008).

## Open inputs
The raw water's analysis (hardness, alkalinity, silica, CO2, temperature range, SDI) and with it
the RO's recovery limit, antiscalant and the design temperature; the mixed beds' measured run
length and rinse volumes; the boilers' feed water specification; the site's discharge permit for
the RO concentrate (sewer, surface water or treatment); resin and membrane lives; a benchmark of
specific consumptions from an open plant record.
