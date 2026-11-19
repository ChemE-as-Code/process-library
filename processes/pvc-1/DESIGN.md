# Design decisions

One entry per decision: what was decided, why, what was rejected, and what it assumes.
Polyvinyl chloride by batch suspension polymerisation of vinyl chloride monomer (S-PVC), issue
ChemE-as-Code/process-library#461, a batch entry of the library (coverage rank 26, variant
`suspension`). Concept stage: design basis, batch recipe, balanced BFD/PFD, thermal screening of
the closed batch and a preliminary gate-to-gate LCI linked to vcm-1. Out of scope here: P&IDs,
layout, HAZOP, TEA, datasheets.

Starting point (2026-11-19): library `main` (c241d8d7) with the core pin 0e85885 (v1.12.0 and
the QSDsan integration). Core has the batch reactor with its duty on an energy stream (ADRs
0050, 0059), recycles with tear streams (ADR 0060), component separators (ADR 0070), the solid
separation and the dryer (ADR 0057), the batch recipe with vessel, jacket and heat-up (ADRs
0051, 0052, 0063) and the thermal screening (ADRs 0058, 0069). Library ADR 0035: one dedicated
train (four autoclaves taking the batches in turn), no campaigns. Templates:
`oxalyl-chloride-1` (batch entry, recipe, screening), `n-bromosuccinimide-1` (solids, dryer).
Requires cheme-as-code 1.12 (plant.yaml).

## Source register

Facts are restated in our own words; nothing is copied. "Read" means the passage named was read
in this work.

| id | source | locator | access / terms | used for |
|---|---|---|---|---|
| SRC-1 | European Commission JRC (2007) Reference Document on Best Available Techniques in the Production of Polymers (POL BREF), August 2007, https://eippcb.jrc.ec.europa.eu/sites/default/files/2019-11/pol_bref_0807.pdf | chapter 5: 5.2.1 (raw materials: suspending agents about 1 kg/t, initiators below 1 kg/t VCM, short-stops below 1 kg/t), 5.2.3 (water and additives charged, air removed by vacuum or nitrogen, VCM charged; 0.4 to 1.2 MPa, 35 to 70 C, 85 to 95 % converted; unconverted VCM vented to a gas holder or the recovery; S-PVC always batchwise in a stirred vessel, particles 50 to 200 um, closed-reactor technology opened less than once in 100 batches), 5.2.4 (stripping batchwise or continuously with steam), 5.2.5 (centrifuge, fluid-bed, cyclone or flash dryer), 5.2.7 (VCM recovery by condensation at low temperature and raised pressure, gas holder, vent treatment, polyperoxides), 5.2.8 (water stripper, flocculation), Table 5.4 (VCM in the product 5 g/t general purpose, 1 g/t food and medical), Table 5.5 and 5.3.2.1 (S-PVC emissions; German plants 1 to 4 m3/t of wastewater), Table 5.9 (S-PVC 2 to 3 GJ/t thermal, 0.7 to 1.1 GJ/t electrical), Table 5.10 (an example plant: 3.1 m3/t water, 0.879 t/t steam, 139 kWh/t without off-site and utilities); 13.4 (BAT for PVC: BAT 3 reactor emissions, BAT 6 cyclones for S-PVC, BAT 9 accidental emissions: inhibitor, emergency cooling, emergency power for agitation, controlled emergency vent), Table 13.9 (S-PVC: 18 to 45 g/t total VCM, 10 to 40 g/t dust) | read (PDF, 2026-11-19); EU document, facts only | D-001 to D-011, benchmarks |
| SRC-2 | US 6 825 288 B2 (Shin-Etsu Chemical, 2004): Method of producing of vinyl chloride-based polymer, https://patents.google.com/patent/US6825288B2/en | Example 1: a 130 m3 stainless autoclave with jacket, cooling baffle and reflux condenser; 56.8 t deionised water, 13.7 and 2.9 kg of partially hydrolysed polyvinyl alcohols and 5.6 kg of hydroxypropyl methylcellulose; degassed to 8.0 kPa; 46.3 t VCM; 22.5 kg di-2-ethylhexyl peroxydicarbonate; heated with 80 C water, held at 57.0 C with 10 C cold water from a refrigeration device; the reflux condenser at 7000 MJ/h from 30 to 65 % conversion and 5000 MJ/h from 75 % to the end, the jacket and baffle 8500 MJ/h at 35 % and 14 000 MJ/h at 80 % (Table 1); the end at 0.588 MPa, a conversion of 90 %; 44.7 kg of a 30 % antioxidant dispersion added, unreacted monomer recovered, 17.9 kg of 25 % ammonia water, the slurry dewatered and dried. Detailed description: the conversion counted from the heat removed over the charge times 368 kcal/kg; the reflux condenser's share 30 to 60 % in its first stage, 20 to 30 % in its second | read (Google Patents, 2026-11-19); patent, facts only | D-003 to D-005, D-008 |
| SRC-3 | Barkanyi, A.; Lakatos, B. G.; Nemeth, S. (2012) Modelling of heat exchange between drops in suspension polymerization of vinyl chloride. Periodica Polytechnica Chemical Engineering 56(2) 55-64, doi:10.3311/pp.ch.2012-2.02 | the three stages of VCM polymerisation: below 0.1 % one phase; then a monomer-rich and a polymer-rich phase, the polymer phase saturated with monomer, until a critical conversion where the monomer phase disappears and the pressure drops; then the swollen polymer only; dispersed phase about 0.3 by volume; droplets 10 to 100 um | read (open PDF, 2026-11-19); facts only | D-005 |
| SRC-4 | Barkanyi, A.; Nemeth, S.; Lakatos, B. G. (2014) Temperature control of batch suspension polyvinyl chloride reactors. Chemical Engineering Transactions 39, 1285-1290, doi:10.3303/CET1439215 | Table 1: Arrhenius terms of kd (15 460 K), kp (3320 K) and kt (2190 K) of the two-phase model after Sidiropoulou and Kiparissides (1990); simulations at 323 and 328 K over about 200 min; industrial reactors up to 160 to 200 m3 | read (open PDF, 2026-11-19); facts only | D-005 |
| SRC-5 | Wikipedia, Polyvinyl chloride, https://en.wikipedia.org/wiki/Polyvinyl_chloride | density 1.4 g/cm3, specific heat 0.9 kJ/(kg K), glass transition 82 C (infobox); about 80 % of production by suspension polymerisation, particles 100 to 180 um | read (first 100 000 characters, 2026-11-19); CC BY-SA, facts only | materials, D-009 |
| SRC-6 | The `thermo` 0.6.1 and `chemicals` 1.5.2 packages (core's environment): vinyl chloride's vapour pressure, liquid molar volume and heat of vaporization on the DIPPR_PERRY_8E method (Perry's Chemical Engineers' Handbook, 8th ed., coefficients as packaged), its liquid heat capacity on HEOS_FIT; water's on HEOS_FIT and IAPWS; normal boiling point and identities in `chemicals` | VCM: 921.7 kPa at 330.15 K, 1644 kPa at 357.10 K, 0.07409 m3/kmol at 330.15 K, 22 553 J/mol at 259.44 K, 17 133 J/mol at 338 K, 102.1 kJ/(kmol K); water: 17.3 kPa at 330.15 K, 0.01830 m3/kmol, 75.33 kJ/(kmol K), 42 333 J/mol at 338 K, 2278 kJ/kg at 368 K | open-source packages queried 2026-11-19; single values, facts only, with their source; not open data (library ADR 0037). Perry's itself not read | materials, D-008 to D-010 |
| SRC-7 | NIST Chemistry WebBook, SRD 69: vinyl chloride, https://webbook.nist.gov/cgi/cbook.cgi?ID=C75014 | boiling point 259.45 K (Dreisbach and Martin 1949); heat of vaporization 22.7 to 23.3 kJ/mol near 245 to 265 K; an Antoine fit only from 165 to 259 K (not used above it) | read | materials (cross-check) |
| SRC-8 | EBI OLS (ChEBI) and PubChem PUG REST | CHEBI:53243 poly(vinyl chloride) with CAS 9002-86-2; CHEBI:17246 poly(vinyl alcohol) macromolecule with CAS 9002-89-5; CID 85963 for di(2-ethylhexyl) peroxydicarbonate's InChIKey; no CID for CAS 9002-86-2 | read (2026-11-19) | registry |
| SRC-9 | Stoessel, F. (2008) Thermal Safety of Chemical Processes, Wiley-VCH, doi:10.1002/9783527621606 | MTSR, MTT and the criticality classes (method, implemented in core ADRs 0050, 0058) | method reference, no data taken | D-010 |
| SRC-10 | processes/vcm-1 (this library) | vinyl chloride monomer by the balanced EDC process, its Tier 1 dataset | library, internal | D-004, D-011 |

Searched and not found openly (2026-11-19): a complete kinetic parameter set with gel-effect
constants for an industrial recipe, a measured heat-release curve of a plant batch, a TD24 of
a VCM/PVC suspension or of the peroxydicarbonate in it, the residual VCM after venting, the
stripper's steam ratio, the centrifuge's cake moisture and the dryer's efficiency of a named
plant, the plant's motor powers, prices.

## D-001 Route and boundary (2026-11-19)
Decision: suspension polymerisation of VCM (S-PVC) in batch autoclaves, the process SRC-1
describes in 5.2 for the suspension variant, with:
- M101, E101, R101, DG101 in each autoclave R-101 to R-104: water and suspending agent charged,
  the head space evacuated, VCM and initiator charged, heated to 330.15 K, polymerised to the
  pressure drop at 90 % conversion, short-stopped, the unreacted VCM vented to the gas holder,
  the slurry dropped to the slurry tank with the autoclave's rinse water;
- ST301, CN301: continuous stripping of the slurry with live steam, the overhead condensed;
- M401, REC401: the gas holder and the recovery (compression, condensation, water knock-out),
  the recovered VCM back to the charge, the vent to the incinerator;
- E501, CF501, DR601: the stripped slurry cooled, centrifuged, the wet cake dried in a fluid bed;
- M701: the process wastewater collected for the wastewater stripper and the site's treatment.
Boundary: from VCM (vcm-1), water and the additives to the dried resin before sieving and the
silos; the wastewater stripper, the site's wastewater treatment and the vent incinerator are
outside (wastes to treatment); sieving, bagging and storage are not modelled.
Reason: suspension PVC is SRC-1's main process (its PVC capacity in Europe mostly suspension)
and SRC-5's about 80 % of production; it is batchwise by nature (SRC-1, 5.2.3.2), which fits
the library's batch entries, and its recipe is openly documented (SRC-2).
Rejected:
- emulsion and microsuspension PVC (E-PVC): the other variant in coverage.yaml; latex, spray
  drying, 6 to 9 GJ/t thermal (SRC-1, Table 5.9), a niche of paste grades, left for its own
  entry;
- mass (bulk) polymerisation: no open source read for it here; a small share of production;
- stripping in the autoclave (SRC-1 allows batch stripping in the reactor): it lengthens the
  autoclave's occupancy; the continuous column decouples the batch section from the finishing
  (D-007);
- a blow-down tank for the venting: the venting stays in the autoclave (SRC-1 allows both),
  one vessel less.
Assumptions: the vinyl chloride is pure; no comonomer, homopolymer only.

## D-002 Capacity, product and operating hours (2026-11-19)
Decision: four autoclaves of SRC-2's 130 m3 on one train, 8000 h/a (333 days, ASSUMED), which
gives 4110 batches and 171.8 kt/a of dried resin (the recipe's result, D-003). Product: S-PVC
resin with 0.3 wt% volatiles (ASSUMED, D-009) and below 1 g of VCM per t (D-007), carrying the
initiator's fragments, the short-stop and 0.01 wt% of the suspending agent.
Reason: SRC-2's autoclave is a current industrial size (SRC-4: up to 160 to 200 m3); four of
them give a world-scale single line of 100 to 200 kt/a (ASSUMED, no capacity source used). The
plant size does not change any ratio of the inventory.

## D-003 Batch basis, recipe and vessels (2026-11-19)
Decision: `process/recipe.yaml`, one unit procedure POLYMERISE over M101, E101, R101 and DG101
(core ADR 0057), `parallel: 4`. Its operations: the water and suspending agent charged (0.5 h),
evacuated (0.25 h), the VCM and initiator charged (0.5 h), heated on the jacket from 298.15 to
330.15 K (calculated, 1.07 h, core ADR 0052, 0063), polymerised (from R101's model, 3.71 h),
short-stopped and vented (0.75 h), dropped (0.5 h), rinsed and coated (0.5 h): 7.786 h per
autoclave, a cycle of 1.9465 h, 4109.9 batches a year. The durations other than the heat-up and
the polymerisation are ASSUMED. The batch size is 41 794 kg of dried resin (stream S23), the
charge of SRC-2's Example 1 carried through; the flowsheet's flows are one batch's amounts over
the cycle, so the recipe's year-average rate equals S23 (no `cheme.recipe-basis` finding).
The autoclave is given as 130 m3 (SRC-2) and filled to at most 87 % (112.6 m3 at the charge;
the charge shrinks as the denser PVC forms). The stripper, the recovery, the centrifuge and the
dryer run continuously from the slurry tank T-301 and the gas holder T-401 and are no batch
units (SRC-1, 5.2.4, 5.2.7).
Reason: SRC-1: S-PVC is always batchwise in a stirred vessel, with buffer tanks to continuous
finishing.

## D-004 Feeds and the charge (2026-11-19)
Decision: per batch, SRC-2's Example 1: 46 300 kg of VCM (41 680 kg fresh, 4620 kg recovered),
56 800 kg of demineralised water, 22.2 kg of suspending agents (lumped as polyvinyl alcohol,
PVA), 22.5 kg of di(2-ethylhexyl) peroxydicarbonate (INIT), 44.7 kg of a 30 % dispersion of the
short-stop antioxidant (STOP), and 2000 kg of rinse water (ASSUMED) that goes with the slurry to
the stripper (SRC-1, BAT 3). Fresh VCM = the charge less the recovered VCM: 46 300 x (1 - 0.1 x
0.997843) = 41 680 kg (the recovery's overall yield, D-006). The 17.9 kg of 25 % ammonia water
SRC-2 adds for the pH are left out (0.4 g per kg of resin; not in the balance). The
initiator's and the short-stop's fragments stay in the resin (`phase: solid`, ASSUMED: the
initiator decomposes to radicals that end as end groups), the suspending agent in the water
(ASSUMED); the peroxydicarbonate is stored and charged cold (D-010).
Reason: SRC-2's example is the one complete open charge found; SRC-1's ranges (suspending agents
about 1 kg/t, initiators and short-stops below 1 kg/t VCM) bracket it.

## D-005 Reactor R101: a batch, its rate and its heat (2026-11-19)
Decision: `reactor: batch`, isothermal at 330.15 K (SRC-2's 57.0 C), to 90 % conversion of the
VCM (SRC-2's end at the pressure drop), the duty to chilled water (Q2, written by propagate,
core ADR 0059). Reaction POLY: VCM -> PVC per mole of repeat units, -96.23 kJ/mol (SRC-2's
368 kcal/kg, 1539.7 kJ/kg). Rate: zero order in VCM, constant per m3 of suspension,
k = 4.86e-4 kmol/(m3 s) at 330.15 K, Ea 82 766 J/mol (ASSUMED).
Reason: between about 0.1 % conversion and the pressure drop the monomer phase is pure and the
polymer phase stays saturated with monomer (SRC-3), so the rate does not follow the overall
monomer content; zero order is the simplest law that keeps the heat release about constant,
as SRC-2's heat removal is (15 500 MJ/h at 35 %, 19 000 MJ/h at 80 % conversion). k is set so
that SRC-2's charge reaches 90 % in 3.72 h at the mean of those two rates, 17 250 MJ/h; the model
gives 3.71 h (the suspension shrinks as it converts). Ea is the overall activation energy of the
free-radical scheme, Ep + (Ed - Et)/2, from SRC-4's Arrhenius terms.
Rejected: the full two-phase kinetic model with the gel effect (SRC-3, SRC-4): its gel-effect
constants and initiator efficiency for an industrial recipe were not found openly, and core's
batch takes a power law, not a moment model; a first-order law: it would put the largest heat
release at the start, against SRC-2's rising heat removal.
Assumptions: the polymer's rate pseudo-homogeneous (L-1); the auto-acceleration and the slowing
after the pressure drop not resolved; to be replaced by the licensor's or a calorimetric rate.

## D-006 Venting and VCM recovery (2026-11-19)
Decision: after the short-stop, 85 % of the unreacted VCM is vented from the autoclave to the
gas holder (DG101, ASSUMED); the rest stays dissolved in the resin and the water (1.7 wt% on the
resin) for the stripper. The gas holder takes the vent and the stripper's gas (M401); the
recovery compresses and condenses on cooling and chilled water (REC401): 99.8 % of the VCM back
to the charge as liquid (the tear S17), its water knocked out to the wastewater, 0.2 % (4.76
kg/h, 0.22 g per kg of resin) to the vent incinerator (ASSUMED). The recovery's condensers Q6
(289.6 kW) by hand: the VCM condensed at 321.8 kJ/kg (SRC-6), the gas cooled from an ASSUMED
380 K compressor discharge, the water knocked out.
Reason: SRC-1, 5.2.7 describes this recovery; no open figure for the residual VCM after venting
or for the recovery's yield was found, so both are ASSUMED round values, and the vent goes to an
incinerator (SRC-1, BAT 7). The recovery's overall yield on the unreacted VCM is 0.998 x (0.85
+ 0.15 x 0.99995 x 0.999) = 0.997843.

## D-007 Slurry stripping (2026-11-19)
Decision: a continuous column with live steam (LP 450 kPa(a), 7500 kg per batch, 0.179 kg per
kg of resin, ASSUMED), all but 0.005 % of the slurry's VCM overhead (ASSUMED), so that the resin
keeps 0.84 g/t before the dryer, below SRC-1's 1 g/t (Table 5.4); about 3 % of the water in
leaves overhead as steam; the overhead condensed on cooling water (CN301, Q5 711.8 kW by hand),
its VCM to the gas holder, its condensate (with 0.1 % of the VCM) to the wastewater stripper.
The stripped slurry (368 K) is cooled to 333 K on cooling water (E501, Q4 1526.5 kW by hand).
Reason: SRC-1, 5.2.4 and BAT 4; the steam: the slurry (about 305 MJ/K) heated from 330 to 368 K
by condensing steam (5.5 t) plus about 2 t overhead. No heat is recovered between the hot
stripped slurry and the stripper's feed: a feed/bottoms exchanger would save most of Q4 and
of the live steam, a design improvement for the next stage.

## D-008 Utilities and heat (2026-11-19)
Decision:
- R101's heat (Q2, 9155.9 kW year average, 64 160 MJ per batch) to chilled water at 283/293 K
  (SRC-2's 10 C cold water). The recipe's jacket is the autoclave's jacket and cooled baffles,
  150 m2 at U 500 W/(m2 K) (ASSUMED), at the chilled water's log-mean 41.84 K: 3138 kW against the
  model's peak of 5438 kW (`cheme.recipe-jacket`, a warning kept on purpose). SRC-2's autoclave
  has a reflux condenser that removes 26 to 45 % of the heat (its Table 1), on a separate
  coolant; here it would take 2.3 MW, 42 % of the peak. Core's closed batch has no reflux
  condenser (L-3), so all of Q2 is booked to chilled water: conservative for the chilled water,
  which in the plant carries 55 to 75 % of it.
- The heat-up Q1 (1519.1 kW year average, 10 645 MJ per batch) from the recipe (core ADR 0063):
  the charge and the autoclave's metal (ASSUMED 50 000 kJ/K, about 100 t of clad steel) on hot
  water at 353.15 K (SRC-2's 80 C), from LP steam.
- The dryer Q3 (7658.8 kW), from core's dryer model (D-009).
- Power: 139 kWh per t of resin, SRC-1's example plant (Table 5.10, without off-site and
  utilities), 2984.5 kW, split ASSUMED: agitators 35 % (P1), the recovery compressor 10 % (P2),
  the centrifuge 15 % (P3), the dryer's fans, conveying, sieving and pumps 40 % (P4).
- Cross-check: LP steam (Q1 + Q3, 9178 kW, about 15.6 t/h) and live steam (3.85 t/h) are 0.90 t
  per t of resin against SRC-1's example plant's 0.879 t/t (Table 5.10); thermal energy 2.03
  GJ/t against SRC-1's 2 to 3 GJ/t (Table 5.9). The electricity, 139 kWh/t, is below SRC-1's
  194 to 306 kWh/t because the chiller's electricity is in the chilled-water exchange (about
  90 to 110 kWh/t at a COP of 4 to 5).

## D-009 Centrifuge and dryer (2026-11-19)
Decision: a decanter centrifuge (CF501, core's solid separation): 99.9 % of the resin to the
cake (0.1 % fines to the wastewater), cake 0.30 kg of water per kg of resin (23 wt%), ASSUMED. A
fluid-bed dryer on LP steam (DR601, core's dryer, ADR 0057): the water and VCM dried off to
0.3 wt% in the resin at 338.15 K (below the resin's 355 K glass transition, SRC-5), the wet
cake's heat capacity 1.66 kJ/(kg K), latent heats at 338 K from SRC-6, 55 % of the heat
reaching the cake (ASSUMED, a convective dryer's exhaust losses). The model gives 6355 kg/h
evaporated and 7658.8 kW. The exhaust goes through cyclones (SRC-1, BAT 6) to air; its dust
(10 to 40 g/t associated with BAT, SRC-1, Table 13.9) is not in the balance.
Reason: SRC-1, 5.2.5: centrifuge, then a fluid-bed, cyclone or flash dryer. The moisture and
the efficiency are round values; no open plant figure was found.

## D-010 Thermal screening and the hazards of the batch (2026-11-19)
Decision: `cheme process reactor-hazards` screens R101 as a batch (accumulation 1: all charged,
cooling fails at the start): dT_ad 227.6 K, MTSR 557.7 K. The MTT is given (`hazard.mtt`
357.10 K): the autoclave is closed while it polymerises, so a cooling failure raises its
pressure along the charge's vapour pressure; the MTT is the temperature at which VCM's and
water's vapour pressures together reach the relief set pressure, 1700 kPa(a) (ASSUMED; VCM
1644 kPa and water 56 kPa at 357.10 K, SRC-6). The MTSR lies 200 K above it: Stoessel class 3,
4 or 5 (SRC-9), which needs the TD24 of the suspension (not found). At the start of the batch
the mass heats adiabatically at 0.98 K/min and, with the rate's Arrhenius term, reaches the MTT
in about 11 min (our integration of the zero-order rate over the charge's heat capacity with
the metal).
Findings for the next stage (SRC-1, BAT 9 of 13.4):
- a loss of cooling or of agitation must be stopped by injecting a short-stop (inhibitor) within
  minutes, with emergency cooling capacity, the agitator on emergency power, and a controlled
  emergency vent to the VCM recovery sized for the case;
- the reflux condenser (D-008) is part of the heat removal: its loss is a partial cooling
  failure;
- the peroxydicarbonate initiator decomposes exothermically at ambient temperature: cold
  storage and charging (D-004); its TD24 is an open input;
- recovered VCM held with oxygen can form polyperoxides that decompose explosively (SRC-1,
  5.2.7): the recovery is kept oxygen-free, which the evacuation before the charge serves.
The screening values are screening only; they do not replace calorimetry or a relief study.

## D-011 Preliminary gate-to-gate LCI (2026-11-19)
Decision: `lca/lca.yaml`, per kg of dried resin (S23), single product. Linked (lca/mappings.yaml):
the VCM to vcm-1 (SRC-10), the demineralised water to the shared water entry, the live steam by
mass to the shared steam entry (11 bar(a), about 1 % more enthalpy than 450 kPa(a) steam), the LP
steam as heat delivered; the electricity, the cooling water and the wastewater to the library
defaults. Gaps with the activity each should connect to: the suspending agent, the initiator,
the short-stop, the chilled water (processes/utility-chiller makes chilled water at 6 C; not
linked: its supply temperature differs and the exchange is heat removed), the vent to the
incinerator. Emissions: the dryer's water vapour (free) and its VCM (0.16 mg per kg, no
characterisation factor in the climate method). Declared exclusions: the fugitive VCM (SRC-1:
18 to 45 g/t with BAT, all sources), the tanks' breathing, the autoclave openings, the dryer's
dust.

## D-012 Dedicated train (2026-11-19)
One train of four autoclaves making one product family (library ADR 0035); grade changes are
within the batch recipe, not campaigns of other products.

## Method and dependency table

| step | status | basis |
|---|---|---|
| mass and component balances | done in cheme | cheme validate / process streams / propagate |
| the VCM recycle | done in cheme (tear S17, Wegstein) | D-006, core ADR 0060 |
| batch R101: conversion, time, duty Q2 | done in cheme, rate ASSUMED | D-005, core ADRs 0050, 0059 |
| venting, stripper, condenser, recovery | done in cheme (component separators), splits ASSUMED | D-006, D-007, core ADR 0070 |
| centrifuge and dryer (Q3) | done in cheme, cake and efficiency ASSUMED | D-009, core ADR 0057 |
| batch recipe, cycle, basis check, vessel, jacket check, heat-up (Q1) | done in cheme | D-003, D-008, core ADRs 0051, 0052, 0063 |
| thermal screening | done in cheme, MTT given | D-010, core ADRs 0058, 0069 |
| Q4, Q5, Q6, the motors' power | by hand | D-006 to D-008 |
| time to the MTT at a cooling failure | by hand | D-010 |
| LCI inventory | done, several backgrounds gaps | D-011 |

## Core features used (core 1.12.0)

- `reactor: batch` with `batch.target`, `heat: isothermal` and `energy_port` (ADRs 0050, 0059):
  the model writes Q2 `calculated`; `hazard.mtt` (ADR 0058) for the screening.
- `recovery:` component separators (ADR 0070) for the venting, the stripper, its condenser and
  the recovery; `tears:` with Wegstein `convergence` (ADR 0060).
- `solid_separation:` for the centrifuge and `dryer:` with `energy` (ADR 0057).
- `process/recipe.yaml` (ADRs 0051, 0052, 0057, 0063): `units` over four steps, `parallel: 4`, a
  given `volume`, the jacket check at the chilled water's log-mean temperature, a `heat`
  operation with `temperatures`, `vessel.metal_heat_capacity`, `react from:` R101.
- `lca.yaml` with `emission: true` on the dryer's exhaust and `emission_exclusions`.
- Not used: `reactor: semibatch` (nothing is dosed: the whole charge is in before the heat-up);
  `batch.vent` (the autoclave is closed while it polymerises); `batch.heat_up` (the heat-up is
  E101's, Q1 on LP steam, while R101's duty goes to chilled water); `specs:` (the feeds follow
  the charge directly, D-004).

## Core limits hit (each a candidate core issue)

- L-1: a polymer that precipitates in its monomer. The batch carries the PVC as a solid
  component in one pseudo-homogeneous liquid; the two-phase kinetics (monomer phase, swollen
  polymer phase) and the pressure drop when the monomer phase disappears are not modelled: the
  end is a given conversion, not a pressure.
- L-2: rate laws are power laws or LHHW: no moment model with an initiator and a gel effect, so
  the rate is an effective zero-order law calibrated to one heat-removal pattern (D-005).
- L-3: a closed batch has no reflux condenser: the heat a boiling monomer carries to a condenser
  on its own coolant cannot be split from the jacket's, and the recipe compares the whole peak
  with the jacket (the kept `cheme.recipe-jacket` warning, D-008).
- L-4: the batch's pressure is its inlet's; the autoclave's pressure over the batch (the
  monomer's vapour pressure, then the drop) is not computed, and the MTT of a closed,
  pressurised batch is given by hand from the relief set pressure (D-010).
- L-5: the separators' splits (venting, stripping, recovery) are specified, not predicted: no
  sorption equilibrium of VCM in PVC and no stripping model.

## Open inputs
The licensor's or a calorimetric rate and heat release with the reflux condenser's share; the
TD24 of the suspension and of the initiator; the relief set pressure and the emergency vent
sizing; the residual VCM after venting and the stripper's design; the cake moisture and the
dryer's efficiency; the motors' powers; the autoclave's mass; a feed/bottoms exchanger on the
stripper; prices for a TEA.
