# Design decisions

One entry per decision: what was decided, why, what was rejected, and what it assumes. Concept
stage for issue ChemE-as-Code/process-library#465 (coverage rank 53, `mdi-tdi`), on
cheme-as-code 1.12.0 (the library's pin, core 0e85885).

## Source register

Only sources read in this session are used for numbers; each fact is restated in our own words
with its locator. Nothing is copied (no tables, figures or text).

| id | source | locator | status | used for |
|---|---|---|---|---|
| SRC-1 | European Commission JRC (2017) Best Available Techniques (BAT) Reference Document for the Production of Large Volume Organic Chemicals (LVOC BREF), EUR 28882 EN, JRC109279. https://eippcb.jrc.ec.europa.eu/sites/default/files/2019-11/JRC109279_LVOC_Bref.pdf (open, accessed 2026-11-19) | Chapter 10: 10.1 (MDI/PMDI, the 4:1 ratio of polymeric to pure MDI in 2013), 10.2.1, 10.2.2.1.3 (liquid- and gas-phase phosgenation, phosgene excess, HCl purity of a pressure process), 10.2.2.2.1-2 (condensation, neutralisation, phosgenation in MCB, 146 kg HCl per 250 kg MDI, fractionation), 10.3.1.3, 10.3.2.5 (brine), 10.3.3 Table 10.11 (0.78 kg phosgene and 0.56 kg chlorine per kg MDI), 10.3.4, 10.3.6 Table 10.12, 10.3.7 (start-up waste gas), 10.4.4.2 (methanol as fuel), 10.5.1 (phosgene-free MDI); Chapter 13 BAT 72-73, Table 13.9 | read (Chapter 10, BAT 70-73) | route (D-001), product split (D-008), benchmarks, hazards (D-011) |
| SRC-2 | Knauf, T.; Wershofen, S.; Gruner, K.-G.; Hartjes, V. (Covestro Deutschland AG) (2020) Method of producing diamines and polyamines of the diphenylmethane series. US 10 640 455 B1. https://patents.google.com/patent/US10640455B1/en (accessed 2026-11-19) | Description of the nameplate (starting) state: 23.20 t/h feed aniline (90 % aniline) and 9.60 t/h of 32 % formaldehyde (2.25 mol per mol), aminal at 90 C and 1.40 bar(a), 30 % HCl at a protonation level of 10 %, seven-reactor cascade 50 to 156 C (first reactor at 104 mbar), 32 % NaOH at 1.10 mol per mol HCl at 115 C and 1.40 bar(a), washing with condensate, MDA with 51.0 % two-ring diamines (45.2 % 4,4'-, 5.5 % 2,4'-, 0.3 % 2,2'-MDA) | read (description and examples) | MDA section (D-003, D-004) |
| SRC-3 | Covestro Deutschland AG (2019) Method for producing isocyanates. US 10 364 214 B1. https://patents.google.com/patent/US10364214B1/en (accessed 2026-11-19) | Examples, general conditions of the MDI production at nameplate: 20.4 t/h MDA at 110 C mixed with 55.0 t/h MCB at 30 C to a 27.1 % solution, fed at 45 C; 120 t/h of 35 % phosgene solution at 0 C (42 t/h phosgene); reaction solution at 81 C; tower top 1.6 bar(a) and 111 C; phosgene removal at 116 C and 1.6 bar(a); phosgene absorption in MCB; HCl absorber; solvent removal in a first column (155 C feed, 600 mbar top, 145 C bottoms), a second column (70 mbar top, 150 C bottoms) and a countercurrent evaporator (20 mbar, 170 C top); 25.45 t/h MDI. Examples 1 and 2, overall assessment, and the conclusion: MCB losses of 430 t/a in the comparative example (330 t/a via the offgas combustion and 100 t/a discharged from the liquid separator) and 30 t/a in the inventive one, 400 t/a saved | read (description and examples) | phosgenation (D-005, D-007, D-008) |
| SRC-4 | Müller, H.-H.; Wershofen, S.; Grabowski, S. (Bayer MaterialScience AG) (2007) Process for the preparation of di- and polyamines of the diphenylmethane series. US 7 186 857 B2. https://patents.google.com/patent/US7186857B2/en (accessed 2026-11-19) | Description (aniline to formaldehyde 1.5:1 to 20:1, formalin 30-50 wt%, reaction 110-160 C preferred, caustic excess 105-120 %), laboratory example | read | cross-check of D-003 |
| SRC-5 | Sphera Solutions for ISOPA / PlasticsEurope (2021) Eco-profile and EPD: Toluene diisocyanate (TDI) and methylene diphenyl diisocyanate (MDI), reference year 2018. https://www.pu-europe.eu/wp-content/uploads/2023/06/ISOPA_Eco-profile_TDI_MDI_2021.pdf (accessed 2026-11-19) | Sections 1.2-1.3 (process description, combined elemental and mass allocation of the HCl co-product), Allocation Rules, Table 2 (MDI GWP 2.76 / 2.32 / 3.37 kg CO2 eq per kg under elemental+mass / mass / price allocation) | read | allocation (D-012) |
| SRC-6 | Franklin Associates for the American Chemistry Council (2022) Cradle-to-gate life cycle analysis of methylene diphenyl diisocyanate (MDI), final report. https://americanchemistry.com/content/download/11831/file/Cradle-to-Gate-Life-Cycle-Analysis-of-Methylene-Diphenyl-Diisocyanate-Resin-Precursor.pdf (accessed 2026-11-19) | Methodology (mass allocation with HCl; 14 % pure, 86 % polymeric MDI of US demand in 2018), Table 3 (gate-to-gate phosgene/MDA/MDI energy 4.65 GJ per 1000 kg, 3.34 GJ of it natural gas, 63 % of that burnt on site) | read | allocation (D-012), energy cross-check (D-009) |
| SRC-7 | chemicals 1.5.2 and thermo 0.6.1 (Python packages, MIT): normal boiling points (`chemicals.Tb`: CRC_ORG and CRC_INORG, the CRC Handbook tables as packaged; HEOS, the CoolProp equations of state; YAWS, the packaged Yaws table), melting points (`chemicals.Tm`: OPEN_NTBKM, the Open Notebook Science melting point data as packaged), heats of vaporization at the boiling point (thermo `Chemical(...).Hvap_Tb`, default methods: VDI_PPDS, coefficients from the VDI Heat Atlas, for aniline and phosgene; HEOS_FIT for MCB and water; MORGAN_KOBAYASHI, a correlation, for MDI), the liquid heat capacity of MCB (HEOS_FIT), the vapour pressure of MCB at 258.15 K (110.9 Pa, HEOS_FIT), MDI's formation enthalpies (`Hfg` WEBBOOK, YAWS, JOBACK; `Hfs` WEBBOOK) and MDA's (JOBACK, an estimate), saturation temperatures of steam (`iapws95_Tsat`), ideal-gas data through `cheme chemistry thermo` | the method named per component in process/materials.yaml and in each duty's source (flowsheet energy streams) | single facts with the package and method named (library ADR 0037), not open data; the underlying works (CRC Handbook, Yaws, VDI Heat Atlas, the Open Notebook Science melting point collection, the NIST WebBook, Poling) not read | properties, duty estimates |
| SRC-8 | PubChem (NIH), compound records CID 7570 (4,4'-MDI) and CID 7964 (chlorobenzene), REST interface | InChIKey, formula, ChEBI cross-reference | read | registry identifiers |

## D-001 Route: MDA by HCl-catalysed condensation, liquid-phase phosgenation in MCB, MDI by distillation (2026-11-19)

Decision: MDI, not TDI, by the route the LVOC BREF describes for every European MDI plant
(SRC-1 10.2.2.2): aniline and formaldehyde condensed over hydrochloric acid to MDA and its
oligomers, neutralised with caustic soda, washed and freed of aniline; the MDA phosgenated in the
liquid phase in monochlorobenzene; HCl, phosgene and solvent recovered; monomeric MDI distilled
off the crude, the bottoms sold as polymeric MDI. One process id, `mdi-1`; TDI (toluene
nitration to DNT, hydrogenation to TDA, phosgenation in o-dichlorobenzene or in the gas phase,
SRC-1 10.2.2.1) is left for another entry under the same coverage item.

Reason: the issue's scope; the library already makes every feed (aniline-1, formaldehyde-1,
phosgene-1, chlor-alkali-1), so the entry closes a chain from benzene and chlorine; MDI is the
larger of the two isocyanates (SRC-1 10.1: over 5 Mt/a of MDI and PMDI in 2011 against 2.1 Mt/a
of TDI capacity in 2013), and two open patents give a consistent nameplate case for both halves
of the plant (SRC-2, SRC-3).

Rejected:
- Gas-phase phosgenation (SRC-1 10.2.2.1.3): built for TDI by one operator; the BREF names no
  MDI plant using it, and the oligomeric PMDA does not evaporate.
- High-temperature, high-pressure liquid phosgenation (SRC-1 10.2.2.1.3, described for TDI):
  smaller phosgene hold-up and HCl recovered under pressure; no open MDI example with numbers
  was found, so the low-pressure tower of SRC-3 is kept.
- Phosgene-free MDI via methyl phenyl carbamate from dimethyl carbonate, condensation with
  formaldehyde and thermal cleavage (SRC-1 10.5.1): an emerging technique, assessed as not yet
  economically feasible; no plant.
- Acid recycle without salt formation (SRC-1 10.3.2.5: patented, not used industrially).
- Solid-acid (zeolite or clay) catalysts for the condensation: no open plant source read.

## D-002 Capacity and basis (2026-11-19)

Decision: the formaldehyde of SRC-2's nameplate, 3072 kg/h (9.60 t/h of 32 % solution there),
fed as 6144 kg/h of formaldehyde-1's 50 wt% formalin (0.28 wt% methanol); 8000 h/a. The rest of
the plant follows from the sourced ratios: 22.2 t/h of crude MDI, about 178 kt/a, within the
160-560 kt/a of the European MDI plants the BREF lists (SRC-1 Table 10.1). The fresh aniline is
aniline-1's product, its diphenylamine traces lumped with the aniline (99.95 wt% aniline, 0.05
wt% water, ASSUMED).

Reason: the 50 wt% formalin is formaldehyde-1's product and inside SRC-4's 30-50 wt%; feeding it
undiluted gives less water to the brine than SRC-2's 32 % solution.

Assumptions: SRC-2 feeds 90 % aniline (its recycle mixed in); here the fresh and recycled aniline
are separate streams, and the 2.25 ratio holds at the cascade's inlet (D-003).

## D-003 Condensation and neutralisation conditions (2026-11-19)

Decision: SRC-2's nameplate, as design specifications on the flowsheet: 2.25 mol aniline per
mol formaldehyde at the cascade inlet (SP-ANILINE sets the fresh aniline), 0.10 mol HCl per mol
of amino groups (SP-PROTONATION sets the HCl split X301) from 30 % hydrochloric acid (SP-ACID sets
the absorber water), the aminal at 363 K and 140 kPa(a), the cascade from 323 to 429 K, caustic
soda at 1.10 mol per mol HCl (SP-CAUSTIC) at 388 K and 140 kPa(a). The caustic is chlor-alkali-1's
50 wt% solution, not SRC-2's 32 %. The neutraliser R-102 is held at 388 K by a cooler
(process/simulation.yaml, energy stream Q15, about 1.2 MW to cooling water): the cascade's
effluent arrives at 429 K and the neutralisation of 23 kmol/h of HCl releases heat (an ASSUMED
56 kJ/mol, not sourced), so it is not adiabatic; without the cooler the let-down from 700 to
140 kPa(a) would flash water and aniline. The first cascade reactor is held at 323 K by
evaporative cooling at 104 mbar (SRC-2; the reflux condenser Q19 to cooling water), the later
reactors are heated to 429 K (Q1, MP steam).

Assumptions: the last cascade reactor at 700 kPa(a) to stay liquid at 429 K (ASSUMED); SRC-4's
caustic excess of 105-120 % brackets the 110 %.

## D-004 MDA composition and the lumping (2026-11-19)

Decision: formaldehyde converted completely; the MDA is two components: MDA (the two-ring
diamines 4,4'-, 2,4'- and 2,2'-MDA as one) and PMDA (the three-ring and higher polyamines, as the
three-ring triamine C20H21N3). Their split, 51.0 wt% two-ring, is SRC-2's nameplate product,
written as a selectivity on formaldehyde (0.44333 kmol MDA and 0.278335 kmol PMDA per kmol).

Reason: the isomers and the oligomer distribution need kinetics no open source gives; the
two-ring share is what sets the split into monomeric and polymeric MDI (D-008).

Consequence: the three-ring lump makes the aniline use per formaldehyde 1.72 mol, while SRC-2's
flows give about 1.66 (heavier oligomers); the aniline per kg of MDA is about 4 % high. The
aminal water separation of SRC-2 is not modelled (its water joins the brine); N-methyl and
N-formyl MDA, acridines and aminobenzylanilines (SRC-2) are not resolved.

## D-005 Phosgenation (2026-11-19)

Decision: SRC-3's MDI example: the MDA as a 27.1 % solution in MCB (SP-MCB-MDA sets the MCB
make-up), phosgene as a 35 % solution in MCB at 273 K (SP-PHOSGENE-SOLUTION sets the MCB split
X201), 2.0588 kg phosgene per kg MDA (42 t/h per 20.4 t/h in SRC-3; SP-PHOSGENE sets the fresh
phosgene), the MDA solution at 318 K (45 C in SRC-3; here the 473 K MDA bottoms and the 303 K
MCB mix at about 369 K and the MDA solution cooler Q18 takes them to 318 K), mixing nozzle and
tower with the top at 384 K and 160 kPa(a). With feeds at SRC-3's 45 and 0 C, the reaction
solution reaches SRC-3's 81 C by the heat of phosgenation (about 3.9 MW here, inferred from that
temperature rise at an ASSUMED 1.3 kJ/(kg K)); steam heats it only from there to the tower top
(Q6). The amines are converted
completely (MDI_FORM, PMDI_FORM). The fresh phosgene is phosgene-1's liquid product (253 K, 340
kPa(a)), without storage; its 35 ppm(wt) of chlorine is left out.

Reason: SRC-3 is one consistent nameplate case; its ratio is 2.08 mol phosgene per amino group,
inside the 50-300 % excess the BREF gives for liquid phosgenation (SRC-1 10.2.2.1.3).

Consequence: 17.41 t/h of fresh phosgene, 0.784 kg per kg of crude MDI against the 0.78 of the
BREF's example plant (SRC-1 Table 10.11). phosgene-1 makes 17.35 t/h, so its whole output fits
this plant within 0.4 %.

Assumptions: no ureas, carbodiimides or chlorinated by-products (SRC-1 10.3.6 names them); no
carbon tetrachloride (from the phosgene's chlorine) is formed.

## D-006 MDA work-up: separators and recycles (2026-11-19)

Decision: the neutralised mixture splits in V-101 (the polyamines organic, 5 % of the aniline
and 97 % of the water to the brine); the organic phase is washed in W-101 with 3.0 t/h of
process water (SRC-2 washes with condensate, amount not given: ASSUMED); C-101 takes water,
methanol and the aniline overhead (0.05 % of the aniline left in the MDA, ASSUMED); the brine and
wash water are stripped in T-102 (99.5 % of the aniline overhead, the methanol drawn off as fuel
as SRC-1 10.4.4.2 describes, ASSUMED); the condensates of C-101 and T-102 separate in the
decanter V-102, whose aniline phase is the recycle (tear S3) and whose water phase returns to
T-102 (tear S17). Every split is an ASSUMED recovery fraction (flowsheet.yaml `recovery:`).
V-101 separates at 368 K: its feed is cooled from the neutraliser's 388 K on the way in (Q16,
the cooler lumped with V-101). The stripped brine leaves T-102 at about 373 K and is cooled to
313 K with cooling water in a brine cooler (Q17): the stripper feeds arrive at 363-368 K and
cannot take that heat, so no feed/effluent exchange is claimed.

Consequence: the aniline lost is about 4 kg/h, 0.03 % of the fresh feed (in the brine, the
methanol draw and the MDA); the brine, 12.7 t/h with 10.6 wt% NaCl, is the plant's largest waste stream (SRC-1
10.3.2.5: such plants sit at an outlet that can take salt water).

## D-007 HCl and phosgene recovery, the HCl recycle (2026-11-19)

Decision: the tower top separates 90 % of the HCl and 40 % of the phosgene as gas (V-201); the
dephosgenation column C-201 takes the rest of both overhead with 5 % of the MCB; both gases go to
the phosgene absorber T-201, where chilled MCB (258 K, split X201) takes up the phosgene, and the
absorbent returns to the phosgene solution (tear S23). The absorbent is chilled from 303 to
258 K in an absorbent chiller lumped with T-201 (its duty is in Q8). The HCl gas leaves T-201
with 10 ppm of the phosgene fed (about 5 ppmv, the phosgene purity the BREF cites for HCl from a
pressure process, SRC-1 10.2.2.1.3) and saturated with MCB over the lean absorbent at its top:
MCB's vapour pressure at 258.15 K is 110.9 Pa (SRC-7), 7.4e-4 mol/mol at 150 kPa(a), about
29 kg/h (740 ppmv) on the 352 kmol/h of HCl. The BREF's under 1 ppmv solvent is for a pressure
process and is not met by this low-pressure absorber: a consumer that needs ppm-level MCB would
need a further step (deeper chilling, adsorption on activated carbon, or HCl distillation under
pressure), which is not designed here (open item). 6.5 % of it is absorbed in water to 30 % hydrochloric acid in A-301 for the
condensation (the HCl recycle, tear S4; the split is set by SP-PROTONATION); the rest, 12.0 t/h,
is exported as gas. Every split ASSUMED.

Reason: SRC-3 separates HCl and phosgene, absorbs the phosgene in MCB and absorbs HCl to
hydrochloric acid "for further use"; SRC-2 needs 30 % acid. Exporting the rest as gas keeps the
co-product anhydrous, as SRC-1 10.2.2.2.2 lists (EDC oxychlorination, hydrochloric acid, chlorine
recovery by electrolysis or Deacon); which consumer takes it is outside the boundary.

Rejected: HCl oxidation back to chlorine inside the boundary (a second process; a later variant).

## D-008 Solvent recovery and the MDI split (2026-11-19)

Decision: C-202 recovers 99.995 % of the MCB (SRC-3's first column at 600 mbar, its second
column at 70 mbar and its countercurrent evaporator at 20 mbar and 170 C, lumped as one step
here; the separation is a recovery fraction, so the number of stages changes no modelled value); the rest goes with the crude to C-203, whose lights cut
takes it to incineration. C-203 takes 39.1 % of the two-ring MDI overhead as monomeric MDI, a
fifth of the crude (4.44 of 22.2 t/h), the BREF's 4:1 ratio of polymeric to pure MDI in 2013
(SRC-1 10.1); the bottoms are polymeric MDI with about 40 wt% two-ring MDI. The monomeric MDI
goes molten (318 K) to storage.

Consequence: MCB make-up 34.6 kg/h, 277 t/a, between SRC-3's 30 t/a (inventive example) and
430 t/a (comparative example: 330 t/a via the offgas combustion plus 100 t/a from the liquid
separator); 29.3 kg/h of it leaves with the HCl gas (D-007), 5.3 kg/h with the lights cut.

Not modelled: the separation of pure 4,4'-MDI from the 2,4'-rich mother liquor (crystallisation
or a further column, SRC-1 10.2.2.2.2); the monomeric MDI here is the isomer mixture (L-3). The
ACC study gives 14 % pure MDI for the US (SRC-6): the split is a market choice.

## D-009 Utilities and duties (2026-11-19)

Decision: three steam levels, each at least 10 K (the declared minimum approach) above the
process it heats:

- LP steam 600 kPa(a) (saturation 432 K) for the brine stripper (bottoms about 373 K) and the
  phosgenation tower (top 384 K);
- MP steam 1600 kPa(a) (saturation 474.5 K, SRC-7) for the cascade (the last reactors at 429 K),
  the dephosgenation column (bottoms 428 K) and the solvent column with its countercurrent
  evaporator (bottoms 443 K, SRC-3's 170 C): LP steam's 432 K is below the evaporator and within
  3-4 K of the other two;
- HP steam 4000 kPa(a) (523.5 K) for the MDA and MDI column reboilers;
- cooling water 298/308 K for the condensers, the cascade's reflux condenser, the neutraliser,
  separator, brine and MDA solution coolers, the product coolers and the HCl absorber;
- refrigerated brine 248/253 K for the phosgene absorber and its absorbent chiller;
- electric allowances of 700 kW.

Every duty is an ASSUMED estimate: latent heats at the normal boiling point (thermo 0.6.1, the
method named in each source, SRC-7) of what each column takes overhead, ASSUMED reflux, sensible
heats at ASSUMED heat capacities; the arithmetic is in each energy stream's source. Every
temperature change of a stream between two units has its energy stream (Q15 to Q19 were added
for the neutraliser, the separator feed, the brine, the MDA solution and the cascade's first
reactor). The reaction heats are sized but not booked as utilities: the condensation about 2.9
MW (MDA's Joback formation enthalpy, an estimate, L-1), stated in Q1, which is therefore an
upper estimate of the cascade's steam; the phosgenation about 3.9 MW, inferred from SRC-3's
temperature rise and used by Q6, which starts from SRC-3's 81 C reaction solution.

Consequence: 19.95 MW of steam heat (0.90 kWh per kg of crude MDI): 3.13 MW LP, 13.31 MW MP,
3.51 MW HP; 21.94 MW to cooling water; 3.79 MW refrigeration. The solvent column's 9.3 MW
dominates (single effect, no heat integration). As a cross-check, SRC-6 reports 4.65 GJ of
primary energy per tonne for phosgene, MDA and MDI together, 2.1 GJ of it natural gas burnt on
site: our steam alone (3.2 GJ per tonne) is higher. Heat integration (the MCB vapour to the
pre-evaporation, SRC-3; the hot MDA bottoms and the cascade effluent, now cooled to cooling
water, against the cold streams) and crediting the condensation heat would lower it; they are
open for the basic design.

## D-010 Pressures (2026-11-19)

Decision: the pressures of SRC-2 and SRC-3 where they give them (aminal and neutralisation 140
kPa(a), tower top 160 kPa(a), solvent column 60 kPa(a) and evaporator 2 kPa(a)); the rest
ASSUMED battery limits and pump discharges. No hydraulics are calculated.

## D-011 Hazards (2026-11-19)

Phosgene is the governing hazard (SRC-1 10.1: among the most harmful emissions to health;
preventing releases outside normal operation is a main safety issue). The design case holds 36.3
t/h of phosgene in the 35 % solution to R-201, 18.9 t/h of it recycled through T-201. What the
concept fixes and what basic engineering must add:

- Containment: the phosgene-containing equipment (M-202, R-201, V-201, C-201, T-201, C-202) in an
  enclosure vented to a phosgene destruction (hydrolysis in water or caustic, about 99.9 %
  removal, or wet activated carbon, SRC-1 10.3.1.3) and the thermal oxidiser; inventories kept
  low (the tower is the largest; the high-pressure phosgenation and the gas phase would cut it,
  D-001).
- No phosgene storage: phosgene-1 delivers to M-202 directly (as phosgene-1's D-011 assumes).
- Start-up and shutdown gases: the BREF reports that an MDI plant's waste gas cannot go to its
  regenerative oxidiser at start-up (high CO) and that these periods dominate its CCl4 emissions
  (SRC-1 10.3.7): not estimated here (lca/lca.yaml exclusion).
- The condensation is acid (hydrochloric acid, enamelled or lined equipment) and the cascade runs
  above the water's boiling point under pressure; the neutralisation is exothermic.
- MDI and PMDI are respiratory sensitisers; aniline is toxic; MCB is flammable. Area
  classification and the relief basis are open for the basic stage.
- No reactor hazard screening: the plant is continuous; the reaction heats are sized only
  roughly (the condensation about 2.9 MW from a Joback estimate, the phosgenation about 3.9 MW
  from SRC-3's temperature rise, D-009, L-1), not from calorimetry.

## D-012 LCI scope and allocation (2026-11-19)

Decision: a preliminary gate-to-gate inventory per kg of monomeric MDI (lca/lca.yaml), with mass
allocation between monomeric MDI (13.0 %), polymeric MDI (51.9 %) and HCl gas (35.1 %), as the
ACC study allocates between MDI and HCl (SRC-6). The aniline, formalin, caustic soda and
phosgene link aniline-1, formaldehyde-1, chlor-alkali-1 and phosgene-1 (lca/mappings.yaml); steam
is counted as heat delivered (the shared `steam-heat` entry, LP, MP and HP alike). In the
Atlas build (scripts/build_lci.py) power, cooling water, process water and the brine are linked
as well, through the shared lci/mappings.yaml by their chemical slugs (electricity,
cooling-water, water, wastewater; the brine goes to the generic activated-sludge treatment,
which does not reflect its 10.6 wt% NaCl); the Atlas gaps are the MCB make-up (no library
process; proxy recorded: benzene chlorination), refrigeration, the methanol condensate, the
lights and the vent. For `cheme assess lca`, which does not read the shared mappings, power,
cooling water, process water and the brine treatment are gaps too (lca/lca.yaml `missing:`).

Rejected: ISOPA's combined elemental and mass allocation (SRC-5: chlorine to the HCl, MDA and
CO to the MDI), which the library's allocation methods do not express directly; its MDI GWP is
19 % above the mass key's (2.76 against 2.32 kg CO2 eq per kg, SRC-5 Table 2), recorded as the
deviation. Substitution of the HCl (no library producer of anhydrous HCl gas; hydrogen-chloride-1
makes 33 % acid by synthesis).

## Core features used

- `cheme process propagate` with five tears (S3, S17, S4, S31, S23) and seven design
  specifications (core ADR 0060, ADR 0070), converged by Broyden in 5 iterations;
- component separators with `recovery:` (ADR 0070), conversion reactors with `selectivity:`;
- `cheme assess lca --write` with mass allocation and library-producer links.

## Core limits

- L-1: chemicals 1.5.2 has only a Joback estimate of MDA's formation enthalpy (206.05 kJ/mol,
  gas), none for the three-ring lumps, and for MDI values that disagree (`Hfg` WEBBOOK 189.0,
  YAWS -55.8, JOBACK 86.4 kJ/mol; `Hfs` WEBBOOK -54.4 kJ/mol); no measured heat of reaction was
  read. Core therefore does not calculate the cascade's or the phosgenation's duty. The duties
  are ASSUMED sensible and latent heats, and each reaction heat is given as an order of
  magnitude in its energy stream: the condensation about 2.9 MW (2 aniline + formaldehyde to
  MDA + water, about -100 kJ/mol in the gas phase with the Joback value, on 102 kmol/h of
  formaldehyde; Q1), the phosgenation about 3.9 MW (SRC-3's temperature rise; Q6).
- L-2: no property package of core covers aniline-water-brine, MDA, MDI or HCl-phosgene-MCB:
  no flashes, column models or energy balances; every separator is a recovery fraction.
- L-3: the isomers are lumped (one two-ring and one three-ring component each for MDA and MDI):
  the 4,4'/2,4' split, the NCO content and the viscosity of PMDI cannot be specified.
- L-4: a separator with three outlets (T-102's methanol draw, C-203's lights cut) lumps a
  stripper and a small column each.

## Open items

- Heat integration and calorimetric heats of condensation, phosgenation and neutralisation
  (D-003, D-009, L-1); the 56 kJ/mol of the neutralisation (Q15) is ASSUMED, not sourced.
- The by-products and residues (ureas, carbodiimides, CCl4, the distillation residue of SRC-1
  Table 10.12) and their incineration.
- HAZOP, relief basis and the phosgene detection and containment design (D-011).
- The HCl consumer and its purity specification, and with it a step that takes the MCB in the
  HCl gas (about 740 ppmv) down if the consumer needs it (D-007).
