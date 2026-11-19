# Design decisions

One entry per decision: what was decided, why, what was rejected, and what it assumes.
Demineralised water from fresh surface water, issue ChemE-as-Code/process-library#470, a site
utility of the library (#45). Concept stage: design basis, balanced BFD/PFD with the RO and
the mixed beds as specified splits, a balance script for what core cannot model, and a
preliminary gate-to-gate LCI linked to the library's acid and caustic producers. Out
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
| SRC-2 | de Dardel, F. Regeneration methods (ion exchange), https://dardel.info/IX/processes/regeneration.html, updated 3 September 2021 | mixed-bed regeneration levels: 80 to 120 g HCl per L of cation resin, 80 to 140 g NaOH per L of anion resin, higher than for separate columns because a mixed bed regenerates less efficiently; regenerant strengths HCl 5 %, NaOH 4 %; caustic first, then acid, each injected diluted in demineralised water and displaced with dilution water, resins remixed with air, the final rinse with feed water at the service flow rate; injection over 20 to 40 min, then displacement and rinse to quality; SAC in reverse flow with HCl at least 110 %, better 120 % of stoichiometric | read; personal website (c) F. de Dardel, facts only | D-005 |
| SRC-3 | de Dardel, F. Basic ion exchange processes in water treatment, https://dardel.info/IX/processes/processes.html, updated 30 November 2020 | mixed-bed polishing ('Capacity and throughput'): conductivity below 0.1 uS/cm and silica 1 to 10 ug/L for a polisher after an ion-exchange primary demineralisation; a polisher on RO permeate is different: the permeate's CO2 limits it, the treated water may be above 0.1 uS/cm but not above 1 uS/cm, and the run is one or a few days; the anion resin limits the capacity; two-bed demineralisation: 5 to 25 uS/cm co-flow, below 1 uS/cm reverse flow | read; personal website, facts only | D-001, D-002, D-005 |
| SRC-4 | de Dardel, F. Ion exchange capacity, https://dardel.info/IX/capacity.html, updated 3 March 2021 | total capacity SAC 1.7 to 2.2 eq/L, SBA 0.9 to 1.4 eq/L; operating capacity SAC 0.6 to 1.7, SBA 0.4 to 0.9 eq/L, about 40 to 60 % of the total | read; personal website, facts only | D-005 (cross-check) |
| SRC-5 | de Dardel, F. Neutralisation of regenerants, https://dardel.info/IX/processes/neutralisation.html, updated 10 June 2014 | the mixed regeneration waste counts as neutral at pH 6 to 9; when the excess caustic exceeds the excess acid (no degasser), acid is added until the acid equivalents equal or slightly exceed the caustic's | read; personal website, facts only | D-006 |
| SRC-6 | Cox, J. D., Wagman, D. D. and Medvedev, V. A. (1989) CODATA Key Values for Thermodynamics, Hemisphere; table at https://www.codata.info/resources/databases/key1.html | dHf (298.15 K): H2O(l) -285.830 +/- 0.040, OH-(aq) -230.015 +/- 0.040, H+(aq) 0 kJ/mol | read | reactions.yaml (NEUT) |
| SRC-7 | processes/hydrogen-chloride-1, chlor-alkali-1, utility-wwtp (this library) | hydrochloric acid 33 wt-% (product:HCLACID); caustic soda 50 wt-% (product:NAOH); utility-wwtp's dataset per m3 (lca/datasets/wwtp-activated-sludge-per-m3.yaml) at its ASSUMED 1 kg COD per m3: 0.7126 kg of fossil CO2 and 0.391 kWh | library, internal | D-005, D-008 |
| SRC-8 | core's skill `utility-boiler-feed-water` (cheme-as-code 1.12.0) | grades from clarified to demineralised water; demineralised water is corrosive, so it is stored and pumped in stainless steel or lined material | read; core documentation | D-001, D-010, equipment list |
| SRC-9 | thermo 0.6.1 with chemicals 1.5.2 (open-source property library, in core's environment): `HeatCapacityLiquid` of water (CAS 7732-18-5) at 298.15 K, method HEOS_FIT | 4.181 kJ/(kg K), used as 4.18 | computed in this work; MIT-licensed library, a single property value with its source (library ADR 0037) | D-007, D-010 |

Searched and not found openly (2026-11-19): a plant's specific consumptions of a RO and mixed-bed
demineralisation (regenerant, electricity and wastewater per m3) that could serve as a benchmark;
the EU BREF for common waste water and waste gas treatment (CWW) was not read in this work; rinse
volumes of mixed-bed regeneration in bed volumes (SRC-2 says only "to quality"); a mixed bed's
operating capacity on RO permeate; the CO2 content of RO permeate from a fresh surface water.

## D-001 Route and boundary (2026-11-19)
Decision: media filtration, a two-stage brackish-water RO and mixed-bed ion exchange polishing,
the mixed beds regenerated in place with hydrochloric acid and caustic soda, the regeneration
effluent neutralised and all wastewater discharged to surface water under the site's permit
(D-006):
- PRE: raw-water pump P-101, dual-media pressure filters F-101 (with cartridge filters) and
  their backwash pump P-103;
- RO: high-pressure pump P-102, RO M-101 in a 2:1 array (10 vessels, 7:3, D-004), permeate tank
  T-101;
- IX: mixed-bed feed pump P-201, two mixed beds X-201 (one in service), their regeneration;
- NEU: neutralisation pit T-301 with trim acid, wastewater sump T-302.

Why: RO removes about 99 % of the dissolved salts with electricity only, so the ion exchange
that follows sees a fraction of the raw water's load and its acid and caustic fall
accordingly; a mixed bed is the usual polisher of RO permeate (SRC-1 p. 104 to 105), to below
1 uS/cm when it is fed with RO permeate (SRC-3, D-002).

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

Not included, an option: CO2 removal (a degasser or a membrane contactor) between the RO and
the mixed beds. It would take the CO2 load off the anion resin, lengthen the runs and is what a
product below 0.1 uS/cm would need (SRC-3, D-002); it waits for the raw water's analysis and the
boilers' feed water specification (open inputs).

Boundary: from the raw-water intake (the water as a resource, after clarification) to the
demineralised water header at 5 bar(a); the wastewater leaves to the site's permitted discharge.
Not in the boundary: raw-water clarification (coagulation and settling), the RO antiscalant and
dechlorination, RO cleaning, resin and membrane replacement (D-008).

## D-002 Capacity, raw water and the product (2026-11-19)
Decision: 50 m3/h (50 000 kg/h) of demineralised water for 8000 h/a, 400 000 m3/a (ASSUMED, a
mid-size site plant for boiler make-up and process water). Raw water: fresh surface water,
clarified, 500 mg/kg of dissolved solids lumped as NaCl (ASSUMED), at 25 degC, the membranes'
rating temperature (SRC-1 p. 22). Product: conductivity below 1 uS/cm, at 5 bar(a) and 25 degC
into the site header. SRC-3 gives this for a mixed bed fed with RO permeate: the permeate's CO2
limits it, so the treated water may be above 0.1 uS/cm but not above 1 uS/cm; its "below 0.1
uS/cm" holds for a polisher after an ion-exchange primary demineralisation. A specification
below 0.1 uS/cm would need CO2 removal ahead of the beds (D-001, not included). The model
carries the residual salt only, 0.02 mg/kg (ASSUMED, D-005); the conductivity itself rests on
the CO2 the model does not carry (L-2).
Why lumped as NaCl: core has no electrolyte or carbonate chemistry for these streams (L-2); one
monovalent salt keeps the equivalents of the ion exchange simple and the mass balance exact.

## D-003 Media filters (2026-11-19)
Decision: dual-media pressure filters at 15 m/h (SRC-1 p. 60: 10 to 20 m/h), backwashed every
24 h (ASSUMED) at 45 m/h for 10 min (SRC-1 p. 60: 40 to 50 m/h, about 10 min) and rinsed to
drain for 10 min at 15 m/h (ASSUMED): (45 x 10/60 + 15 x 10/60) / (15 x 24) = 2.78 % of the
filtered water goes to the sump (F101's `split:`). About 4.7 m2 of filter area in service:
three filters of 2.5 m2, two in service while one backwashes (equipment list F-101).
Backwashing one filter at 45 m/h takes 112.5 m3/h, more than the 70 m3/h the plant filters, so
a backwash pump P-103 draws filtered water from a backwash water tank of the filter package
(ASSUMED): 8.9 kW for 10 min per filter a day at an ASSUMED 2 bar, 0.19 kW as a year average
(scripts/balance.py), counted in the 3 kW auxiliaries allowance E4 (D-007), as is the air-scour
blower, which runs a few minutes per wash (not sized). Suspended solids are not carried (they
leave with the backwash, D-008).

## D-004 Reverse osmosis (2026-11-19)
Decision: two stages of six-element vessels in a 2:1 array at 75 % water recovery (SRC-1 p. 105
Table 25, p. 107 to 108); salt rejection 0.99 on the mean feed-side concentration (ASSUMED,
within SRC-1 p. 11's 95 to above 99 %). The share of the feed's salt in the permeate is the
rejection's complement times the log-mean concentration factor of a plug-flow array,
-ln(1 - r)/r = 1.848 at r = 0.75, times r: 0.01386 (M101's `recovery:`; the permeate has about
9 mg/kg of salt). At the design flux of 23.8 L/(m2 h) on 37.2 m2 elements (SRC-1 p. 107) the
51.2 m3/h of permeate needs 58 elements, rounded up to 10 vessels of six (60 elements, 22.9
L/(m2 h) installed), split 7:3 between the stages: the whole-vessel split nearest the 2:1 of
SRC-1's example.

Feed pressure from the element's tested permeability (scripts/balance.py): 1,660 L/h over 37.2
m2 at a net driving pressure of 15.5 - 1.4 bar (the test pressure less the osmotic pressure of
2000 ppm, SRC-1 p. 22, p. 109) gives 3.16 L/(m2 h bar), taken at 0.85 for fouling and ageing
(ASSUMED); the design flux then needs 8.85 bar of net driving pressure, plus the mean osmotic
pressure (0.35 bar at 500 mg/kg, scaled from SRC-1 p. 109, times 1.848), half of an ASSUMED 3 bar
pressure drop over the array and 0.5 bar of permeate back-pressure (ASSUMED): 12.5 bar(a). The
pressure is taken at the design flux, not at the installed 22.9 L/(m2 h), on purpose: the
difference, 0.32 bar of net driving pressure (8.53 against 8.85 bar), about 0.9 kW of the RO
pump's 28.5 kW, is kept as a margin. Colder water needs more pressure (the permeability falls
with temperature); a design at the site's minimum water temperature is an open input. No energy
recovery from the concentrate: at brackish-water pressures and 25 % concentrate it is rarely
fitted (ASSUMED).

## D-005 Mixed beds and their regeneration (2026-11-19)
Decision: two mixed beds of 2.5 m3 of resin each (50 m3/h at 20 bed volumes per hour, ASSUMED),
40 % strong acid cation and 60 % strong base anion resin by volume (ASSUMED): 1.0 m3 of cation
and 1.5 m3 of anion resin; one in service, the other regenerating or on standby. A service run
of 36 h (ASSUMED; SRC-3: one or a few days on RO permeate, limited by the CO2 the permeate
carries). Per regeneration (scripts/balance.py):
- 100 g HCl per L of cation resin (SRC-2: 80 to 120 g/L), 100 kg HCl, as 33 wt-% acid diluted to
  5 wt-% (SRC-2);
- 110 g NaOH per L of anion resin (SRC-2: 80 to 140 g/L), 165 kg NaOH, as 50 wt-% caustic
  diluted to 4 wt-% (SRC-2);
- 15 bed volumes of backwash, displacement and rinse water (ASSUMED: SRC-2 gives no volume);
- the dilution, displacement and rinse water is RO permeate from T-101. For the rinse that is
  what SRC-2 says (the final rinse with feed water, here the permeate). For the dilution SRC-2
  uses demineralised water; taking permeate (about 9 mg/kg of salt) instead is a departure from
  the source (ASSUMED): it puts about 51 g of salt per regeneration into 6.1 t of dilute acid and
  caustic, 0.3 % of the 16.6 kg the bed took up in its run; the mixed-bed product, the stricter
  choice, would make a recycle.

Capacity check (scripts/balance.py, in kmol; for NaCl one kmol is one keq): the beds take up
0.0079 kmol/h of salt, 0.284 kmol in a 36 h run. SRC-4's operating capacities give 0.60 to
1.35 kmol for the 1.5 m3 of anion resin (0.4 to 0.9 eq/L) and 0.60 to 1.70 kmol for the 1.0 m3
of cation resin (0.6 to 1.7 eq/L). The salt alone therefore uses 47 % of either resin's
capacity at the low end of SRC-4's ranges (21 % and 17 % at the high end). The design rule
(ASSUMED): the salt may use at most half of the low-end operating capacity, the rest being kept
for the CO2 and silica the model does not carry (L-2; SRC-3 names the CO2 as the limit on RO
permeate), which allows at most 38 h; the run is set at 36 h. The first design (1.25 m3 at 40
bed volumes per hour, 72 h) failed this check: its 0.568 kmol a run was 84 to 189 % of its
anion resin's operating capacity before any CO2.

Year averages over 222 regenerations a year: 8.418 kg/h of 33 wt-% acid, 9.167 kg/h of 50 wt-%
caustic, 1194.2 kg/h of regeneration water (2.3 % of the permeate). The beds let 0.2 % of the
permeate's salt through (ASSUMED, X201's `recovery:`); the 0.461 kg/h of salt they hold is
released at regeneration (stream S12, a bookkeeping stream of the year average, not a pipe).

The regenerants are 9.6 (acid) and 14.5 (caustic) times the salt the beds take up in
equivalents: the applied 2.74 eq/L of acid and 2.75 eq/L of caustic are 1.6 to 4.6 and 3.1 to
6.9 times SRC-4's operating capacities (a mixed bed regenerates less efficiently, SRC-2), and
half of the capacity is held for the CO2 and silica. The acid and caustic per m3 are inversely
proportional to the run: at the middle of SRC-4's ranges the same rule would allow 62 h, at the
high end 85 h, with 0.58 and 0.42 times the acid and caustic of the 36 h run. A measured CO2 of
the permeate and the run length found in operation are open inputs; CO2 removal ahead of the
beds (D-001) would lengthen the run.

## D-006 Neutralisation and the discharge (2026-11-19)
Decision: the regeneration effluent is collected in the neutralisation pit T-301; since the
caustic's equivalents (114.6 mol/h) exceed the acid's (76.2 mol/h), trim acid is added until the
acid equivalents are 1.001 times the caustic's (SRC-5): 4.256 kg/h of 33 wt-% acid. R301 lumps
the regenerants' reaction HCl + NaOH -> NaCl + H2O (conversion 1 on NaOH): what the resin does
in regeneration (the salt it held released, the acid and the caustic regenerating it) and what
the pit does (the excesses) give the same year-average mass balance as one neutralisation
(reactions.yaml). Its heat, 1.78 kW as a year average (core's conversion model with SRC-6),
warms the effluent and is lost (E5; a regeneration's batch, D-010). The neutralised effluent
(pH 6 to 9, SRC-5), the filter backwash and the RO concentrate (about 2.0 g/kg of salt) are
mixed in the sump T-302: 20.3 t/h, 0.405 kg per kg of product with 0.84 g of salt (0.70 g from
the raw water, 0.13 g formed by the neutralisation) (stream S18).

The wastewater is discharged to surface water under the site's permit, as RO concentrate and
filter backwash usually are, and not sent to biological treatment: it carries no organics (no
COD), only the raw water's salts, more concentrated, and the neutralisation's salt, which a
biological treatment would not remove. In the LCI its water and salt are emissions to fresh
surface water (D-008). Rejected for the LCI: the library's utility-wwtp. Its dataset assumes 1
kg of COD per m3 (SRC-7) and would charge 0.405 x 0.7126 = 0.29 kg of fossil CO2 and 0.16 kWh
per m3 of product for organics S18 does not have, comparable with the plant's own 0.99 kWh/m3
of electricity, and pass it on to every consumer of the market (D-008). Whether the site's
permit allows the discharge (salinity, suspended solids of the backwash) is an open input.

## D-007 Pumps and power (2026-11-19)
Decision: pump and motor efficiency 0.70 (ASSUMED) for the raw-water pump (1.013 to 4 bar(a),
the pressure filters' head, SRC-1 p. 60), the RO high-pressure pump (2 to 12.5 bar(a)) and the
mixed-bed feed and forwarding pump (1.013 to 6 bar(a): 1 bar over the bed to the 5 bar(a)
header), and 3 kW year average for the dosing and regeneration pumps, the resin-mixing blower,
the filters' backwash pump (0.19 kW, D-003) and air scour, and the instruments (ASSUMED). Total
49.70 kW, 0.99 kWh per m3: RO pump 0.57, forwarding pump 0.20, raw-water pump 0.17, auxiliaries
0.06 kWh/m3 (scripts/balance.py).

No heat duties: the plant works at ambient temperature and needs no heating or cooling utility.
The energy flows that the model leaves out of the streams' temperatures (every stream is at
298.15 K; `cheme process energy` has no enthalpies to close a balance), each sized
(scripts/balance.py, water's heat capacity 4.18 kJ/(kg K), SRC-9):
- the pump work ends as heat in the water: the RO concentrate let down from about 9.5 to 1.013
  bar(a) warms by 0.20 K, the permeate after the membrane by 0.26 K; the electricity is counted
  at the wire, which is all the LCI uses;
- the heat of neutralisation, 1.78 kW as a year average (E5, D-006), and its batch during a
  regeneration (D-010);
- the heat of dilution of the 33 wt-% acid to 5 wt-% and of the 50 wt-% caustic to 4 wt-%:
  excluded, not quantified (no open dilution enthalpy read in this work); it is released into
  about 6.1 t of dilute regenerant a regeneration, inline in the dilution water (ASSUMED), and
  leaves with the effluent; no utility serves it.

## D-008 Preliminary gate-to-gate LCI (2026-11-19)
Decision: the inventory per kg of demineralised water (lca/lca.yaml, `cheme assess lca
--write`): 1.405 kg of raw water withdrawn from a river (a water resource, `resource: true`; its
dissolved salts free, as they leave again with the discharge), 0.253 g of 33 wt-% hydrochloric
acid, 0.183 g of 50 wt-% caustic soda, 0.99 Wh of electricity and 0.405 kg of wastewater
discharged to fresh surface water: 0.404 kg of water returned (elementary flow water-to-water)
and 0.84 g of salt (dissolved solids, the library's biosphere mapping of NaCl); its 4 g/h of
HCl, the trim's 0.1 % excess, is below cut-off (free). In the Atlas build (lca/mappings.yaml):
the acid links hydrogen-chloride-1's product:HCLACID, the caustic chlor-alkali-1's product:NAOH
(both kg of solution for kg), the electricity the shared grid entry. The wastewater is not
linked to utility-wwtp (D-006: 0.29 kg of fossil CO2 and 0.16 kWh per m3 for COD it does not
carry). The product is the registry grade water/demineralised, the supplier of the new market
`markets/water.yaml` (an on-site header, 1 km ASSUMED, no losses counted).

Consequence for the library: every input of the registry substance `water` was already read by
the shared `water` entry of lci/mappings.yaml as deionised water; with prefer_atlas (the default)
these inputs now link this market instead of the background, as #45 intends. In the build of
this branch (build_lci --strict --public, core 0e85885) that is 96 exchanges of 55 processes,
under the keys PW (33), water (30), DMW (11), WATER (6), BFW (4), DEMIN (3), WASHW (3) and DW,
PW1, PW2, TBAW, boiler-feed-water and feedwater (one each); among them utility-steam-ng-boiler's
feedwater, chlor-alkali-1's WATER and DMW, ammonia-1's and hydrogen-1's DMW and ethylene-1's BFW.
The list is the build's datapackage.json `atlas_links` with provider market:water/demineralised:GLO.
A consumer whose water is not demineralised (a raw make-up) keeps the background with an
`atlas: false` override in its own mappings; deciding that is each consumer's own review. The
loop chlor-alkali-1 -> caustic -> demineralised water -> chlor-alkali-1's water is a real supply
loop and is solved by the background's matrix.

Not in the inventory (open, each a candidate refinement): the RO antiscalant and
dechlorination (sodium bisulfite) dosing, RO cleaning chemicals, resin replacement (a few years'
life) and membrane replacement (about five years), the raw water's clarification; the
discharge's suspended solids, hardness, alkalinity, silica and CO2 (emission exclusion
discharge-traces). The raw-water feed itself (feed:RAW) is reported as a mapping gap by
build_lci: the build skips an output released to the environment but not an input taken from
nature, which it counts by its resource:* exchanges (resource:H2O here, linked); a candidate
library fix (L-4). Construction excluded.

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

## D-010 Hazard screening (2026-11-19)
Concept-stage screening of what the PFD handles; HAZOP, relief and interlocks follow with the
P&IDs (out of scope here, see the head of this file):
- 33 wt-% hydrochloric acid: corrosive, and gives off hydrogen chloride vapour; stored in a
  vented tank with a scrubber (outside this flowsheet's tanks, lca emission exclusion
  water-tanks), dosed and diluted inline to 5 wt-% (ASSUMED) in rubber-lined or plastic lines;
- 50 wt-% caustic soda: corrosive; dosed and diluted inline to 4 wt-%; acid and caustic are
  injected one after the other (caustic first, SRC-2), never mixed concentrated;
- heats: the dilution heat of both is not modelled (D-007); the neutralisation is 1.78 kW as a
  year average but comes in a batch: per regeneration 2.74 kmol of HCl meet the caustic, 153 MJ
  at 55.8 kJ/mol (SRC-6), which warms the regeneration's 43.8 t of effluent in the pit by 0.8 K,
  or the 6.1 t of the two dilute regenerants by 6 K if they met alone (scripts/balance.py, SRC-9):
  no boiling or release; the pit's pH control and agitation (T-301) handle it;
- demineralised water is corrosive to carbon steel (SRC-8): stainless steel or lined equipment
  from the permeate on (equipment list);
- pressure: the RO high-pressure pump (12.5 bar(a) in normal operation) against a closed
  concentrate or permeate outlet over-pressurises the vessels and the permeate side; the
  vessels' rating, a relief or a high-pressure trip are decided with the P&IDs (open);
- the RO permeate tank vents dissolved CO2 only (L-2); no flammable or toxic gas is handled.

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
| LCI inventory | done; acid, caustic and power linked in the Atlas build, the discharge as emissions to water | D-008 |

## Core features used (core 1.12.0)

- Component separators with `recovery:` (ADR 0070) for the RO M101 and the mixed bed X201; a
  splitter with `split:` for the filters' backwash F101.
- `specs:` (ADR 0070): the raw-water feed S1 varied for 50 000 kg/h of product, and the permeate
  tank's regeneration share varied for the script's regeneration water.
- A conversion step R301 with `energy_port` (ADR 0059): the heat of neutralisation calculated.
- `lca.yaml` with a resource feed (`resource: true`, the water as `water-river`), a discharge
  as emissions to fresh surface water (`water-to-water` and dissolved solids),
  `emission_exclusions`, a library mapping file with Atlas `dataset` links.
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
- L-3: a run-and-regenerate cycle of a fixed bed (service for 36 h, then a regeneration) has no
  form in the flowsheet or the recipe for a continuous plant: the regeneration is a year average
  (S12 carries the bed's load to its regeneration as a stream).
- L-4 (library, not core): build_lci reports a feed taken from nature (`resource: true`) as a
  mapping gap, although its components are counted as resource:* exchanges (D-008).

## Open inputs
The raw water's analysis (hardness, alkalinity, silica, CO2, temperature range, SDI) and with it
the RO's recovery limit, antiscalant and the design temperature; the mixed beds' measured run
length and rinse volumes, and the permeate's CO2 (D-005); the boilers' feed water specification
(below 1 uS/cm, or below 0.1 uS/cm with CO2 removal, D-002); the site's discharge permit for the
RO concentrate, backwash and neutralised effluent (D-006); resin and membrane lives; a benchmark of
specific consumptions from an open plant record.
