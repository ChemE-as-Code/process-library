# Design decisions: potassium-chloride-1

Potassium chloride (muriate of potash, MOP) from crushed sylvinite ore by hot leaching and vacuum
cooling crystallisation. Concept stage, issue ChemE-as-Code/process-library#514. Every number
below is either taken from a source in the register (with its locator), calculated by core from
the files, or marked ASSUMED. Nothing is copied from the sources: no tables, figures or text,
only single facts in our own words.

## Source register

| id | source | access | used for |
|---|---|---|---|
| SRC-1 | Brazil Potash Corp. (2024), *S-K 1300 Technical Report Summary, Autazes Potash Project*, exhibit 96.1 to its Form F-1, SEC EDGAR, <https://www.sec.gov/Archives/edgar/data/1472326/000119312524203710/d303049dex961.htm> | open, read 2026-11-19: the executive summary and chapters to 7.5; read 2026-11-20: section 13 (the design base parameters), section 15.2.7 with Table 85 (steam plant), section 18.6.4.3 with Tables 128 and 129 (process electricity and natural gas); chapter 14 and its tables were not read | the route (section 1.10): ore crushed below 4 mm in two trains, two cascaded agitated leach stages at about 90 C, cyclone classification, seven-stage vacuum cooling crystallizer to about 45 C, mother liquor reheated to about 115 C and returned, centrifuge, rotary dryer, compaction, glazing in a fluid bed, flocculant and anti-caking agent, tailings filtered to piles and backfill, brine injected at 310-400 m; KCl recovery 90.8 %; 2.44 Mt/a design capacity, 2.16 Mt/a average of 95 % KCl from 8.32 Mt/a of ore at 27.3 % KCl (sections 1.9, 1.10); heating steam and natural gas for drying among the consumables (1.10), the natural gas used by the product dryers only (18.6.4.3.2; Table 129: 1 064 176 MMBtu/a for the dryer and dryer cooler), the steam raised in four high-voltage electrode boilers (15.2.7, 15.2.7.1); 7620 operating h/a for the nominal 2.16 Mt/a (section 13); steam per use (Table 85, nominal: 208.0 t/h for the hot leach, 9.0 t/h for the crystallizer's steam ejectors, at 150 psig saturated, two trains); process electrical demand by area (Table 128); about 294 MW site demand with the mine and port (1.11); the 2014 averaged grades of Table 10 (KCl 31.5, NaCl 55.4, MgSO4 1.0, K2SO4 1.5, CaSO4 6.8, insolubles 3.5, moisture 0.3 wt%) |
| SRC-2 | Amec Foster Wheeler for Encanto Potash Corp. (2017), *Muskowekwan Project, Preliminary Economic Assessment and Preliminary Feasibility Study, NI 43-101 Technical Report*, <https://minedocs.com/12/Muskowekwan_PFS_05242017.pdf> | open PDF, read (text extracted), 2026-11-19 | the solution-mining variant (D-001): primary brine 148 g/L KCl and 254 g/L NaCl at a 60 C cavern temperature (section 1.9, Table 13-1); NaCl removed first in multi-effect evaporators, then vacuum cooling crystallizers in stages (17.3.2, 17.3.3); centrifuge cake about 96 % solids (17.3.5); fluid-bed dryers with natural-gas burners, crystals out at 140-160 C, cyclones and wet scrubbers (17.3.6); anti-caking and de-dusting oil, flocculant (17.3.7-17.3.10); waste brine to deep-well injection (17.3.11); 8100 h/a, plant recovery 93 % (Table 17-1); natural gas about 1700 GJ/h, mostly for cogeneration (24.18) |
| SRC-3 | Metallgesellschaft AG (1983), *Process for recovering potassium chloride*, US 4 412 838 A, <https://patents.google.com/patent/US4412838A/en> (and its European family member EP 0 003 065 A1, <https://patents.google.com/patent/EP0003065A1/en>) | open, read (description, claims and example), 2026-11-19 | the hot-leach loop: sylvinite leached at 95-100 C, the brine saturated at about 95 C, seven vacuum crystallisation stages to 35 C, the vapour of the first five stages heating the returning mother liquor, which is then heated to 111 C; product 98.13 % KCl; the example's crystallizer (rates per hour): 1846 kg of solution with 26 kg of KCl saturated at 95 C, 118 kg of water added in the first stages, 164 kg of KCl crystallised and 141 kg of water vapour formed, 138 kg discharged as product and 26 kg recycled (D-007); the background statement that the KCl solubility more than doubles between 20 and 110 C while the NaCl solubility hardly changes; feed sylvinite 28-32 % KCl with 3.5-4.5 % insolubles |
| SRC-4 | Shahvarooghi Farahani, S.; Zamanifard, H.; Taki, M. (2024), *Assessing the energy load and environmental footprint of potash fertilizer production in Iran*, PLoS ONE 19(11): e0313129, doi:10.1371/journal.pone.0313129 (CC BY 4.0) | open, read 2026-11-19 | a KCl plant of another route (carnallite from brine pools, flotation and decomposition, Khur, 50 kt/a): electricity 312.5 kWh and fuel oil 36 L (1720.8 MJ) per t K2O, 60 % K2O in KCl (Table 3, Table 5); the independent electricity benchmark (another route, D-008) and a cross-check of the heat |
| SRC-5 | National Bureau of Standards: Gevantman, L. H. (ed.) (1981), *Physical properties data for rock salt*, NBS Monograph 167, <https://nvlpubs.nist.gov/nistpubs/Legacy/MONO/nbsmonograph167.pdf> (US government work) | open PDF, read (Table 1.10 and section 2.5.1), 2026-11-19 | the NaCl solubility in KCl solutions of up to 12 wt% KCl, 0-100 C (Table 1.10), and the statement that in the NaCl-KCl-water system the KCl solubility rises strongly with temperature while the NaCl solubility falls slightly below 373 K (2.5.1); it does not reach the two-salt saturation, so it confirms the trend only (L-3) |
| SRC-6 | `thermo` 0.6.1 and `chemicals` 1.5.2 Python packages (C. Bell et al.) | open-source packages queried, 2026-11-19; single values, facts only | single values (library ADR 0037): heat of vaporisation of water 2393.99 kJ/kg at 318.15 K, 2339 kJ/kg at 340.65 K, 2256 kJ/kg at 373.15 K and 2121 kJ/kg at 420.8 K (thermo, method HEOS_FIT, a fit to IAPWS-95); heat capacity of solid KCl 0.688 kJ/(kg K) at 298.15 K and 0.706 at 373.15 K and of solid NaCl 0.864 at 298.15 K (thermo, method WEBBOOK_SHOMATE, the NIST Chemistry WebBook's Shomate fits, not read here), of solid CaSO4 0.716 at 298.15 K (thermo, method PERRY151: the package's correlation of Table 2-151 of Perry's Chemical Engineers' Handbook, 8th ed., D. W. Green and R. H. Perry, McGraw-Hill, 2007, as chemicals 1.5.2 names it; the handbook not read here); the saturation temperature and pressure of water (chemicals 1.5.2, IAPWS-95). These are facts with their source, not open data |

Sources looked for and not found or not read: an open table of the KCl-NaCl-water system at two-salt
saturation between 25 and 100 C (searched 2026-11-19: the J. Chem. Eng. Data and Russian-journal
papers are not open; a Chimia 1952 paper with the 25 and 100 C diagrams is a scanned PDF that
could not be read here; phasediagram.dk has no such numbers); chapter 14 of SRC-1 with its brine
compositions, energy and water figures; an open heat of solution of KCl in NaCl brine; an open
heat capacity and density of the brines. Each is an assumption below (L-2, L-3).

## Decisions

### D-001 Route

**Chosen: hot leaching of crushed sylvinite in a brine near saturation in NaCl, vacuum cooling
crystallisation of KCl, centrifuging, gas-fired drying, the mother liquor reheated and returned
(SRC-1, SRC-3).** The crystallisation route is the one issue #514 asks the library to show: the
KCl-NaCl-water crystallisation, driven by KCl's solubility rising with temperature while NaCl's
hardly changes, with a closed mother-liquor loop. SRC-1 describes a plant designed on it today,
and SRC-3 the same loop with its heat recovery.

Recorded and rejected:

- *Froth flotation of sylvite from halite* (with amine collectors after desliming). It is the
  most common route for sylvinite ores, but no open source with its reagent, power and water use
  per t was read for this entry, and it has no crystallisation; it is the natural second variant
  (Open items).
- *Solution mining with evaporative and cooling crystallisation (SRC-2).* The cavern brine (148
  g/L KCl, 254 g/L NaCl at 60 C) first loses NaCl in multi-effect evaporators, then KCl in vacuum
  coolers. It needs a multi-effect evaporator train with NaCl crystallising, which core's
  crystallizer (one crystallising solute) cannot model in the same step as the KCl, and the
  energy data are site totals with cogeneration (SRC-2, 24.18). SRC-2 is used for the brine
  composition, the centrifuge cake and the dryer.
- *Carnallite decomposition (SRC-4).* A different ore; SRC-4's plant is used only as a cross-check
  of the utilities.

### D-002 Capacity and basis

150 t/h of KCl crystal in the dried product (152.08 t/h of product), 1.2 Mt/a at 8000 h/a: one
of the two trains of SRC-1's 2.44 Mt/a design capacity, the hours ASSUMED (SRC-2 plans 8100 h).
The boundary starts at the crushed ore at the plant (mining, hoisting and crushing outside) and
ends at the dryer outlet; compaction, screening, glazing, cooling and the anti-caking treatment
are lumped into the auxiliary power (D-008) and not modelled as steps.

### D-003 Ore

27.3 wt% KCl, SRC-1's life-of-mine plant feed (section 1.9). The rest is split in the ratios of
SRC-1's 2014 averaged grades (Table 10), scaled to the 72.4 wt% left: NaCl 58.81, CaSO4 7.22,
insolubles 6.37 wt% (the insolubles with the MgSO4 and K2SO4 lumped as INSOL), water 0.3 wt%.
The minor sulfates are soluble in the real plant; here they pass to the tailings with the
insolubles, and the purge (D-006) stands for their removal (L-1). ASSUMED as a whole: the two
sources describe different years and parts of the deposit.

### D-004 Components and the brine's basis

The brine is written as neutral salts in water (KCl, NaCl, H2O), the solids as separate solid
components (KCl_s for both the ore's sylvite and the product crystal, NaCl_s, CaSO4_s, INSOL).
INSOL has no single formula; it is written as SiO2 (ASSUMED) only so that core evaluates the
element balances, through which it passes unchanged (L-1).

**The hot brine's KCl content (the design specification `liquor`).** The brine leaving the leach
at 363.15 K is taken as saturated in KCl and NaCl. With no open two-salt saturation data read
(L-3), it is built from two open facts: SRC-2's 60 C cavern brine (148 g/L KCl and 254 g/L NaCl;
at an ASSUMED density of 1.25 kg/L, 0.1745 kg KCl and 0.2995 kg NaCl per kg water), taken as
saturated in both (ASSUMED: SRC-2 does not say so), and SRC-3's statement that the KCl solubility
more than doubles between 20 and 110 C, taken as a doubling linear in temperature
(s(T) = s20 (1 + (T - 20 C) / 90 K), ASSUMED). At 90 C this gives 0.2148 kg KCl per kg water,
14.18 wt% of the brine, taken as 14.19 wt%; the NaCl per kg water is kept at 0.2995 (SRC-3 and
SRC-5: it changes little with temperature).

### D-005 The leach and the loop

The leach (R-101, L101) is a conversion step: 96.13 % of the sylvite dissolves (DISK) and 4.097
% of the halite (DISN). Both are ASSUMED and set by successive substitution on the propagated
flowsheet: DISK so that the dried product holds 90.8 % of the ore's KCl, SRC-1's recovery (the
rest leaves undissolved, 1.34 wt% of the tailings, and dissolved in the tailings' brine and the
purge); DISN so that the hot brine keeps its 0.2995 kg NaCl per kg water, the halite dissolved
replacing the NaCl lost with the tailings' brine, the purge and the product. The leach
temperature is SRC-1's about 90 C, taken as 363.15 K.

Two loops are torn: the mother liquor to the leach (S2) and the condensate to the crystallizer
(S7). Two design specifications close them: `rate` adjusts the ore (S1, 607.8 t/h, 4.0 t per t of
product) for 150 t/h of crystal, `liquor` adjusts the make-up water (S6, 47.4 t/h) for the hot
brine's 14.19 wt% KCl. The brine circulation follows: 3937 t/h of hot brine, 25.9 t per t of
product.

### D-006 Tailings and purge

The cyclones, the hot thickener (with flocculant, SRC-1) and the tailings filter are lumped into
one solid separation (S-101, S101): every solid to the tailings, which hold 10 wt% brine
(ASSUMED; no cake wash, L-4). 480 t/h of tailings, 3.15 t per t of product, go to the pile and
the underground backfill (SRC-1). 0.5 % of the mother liquor (19.1 t/h) is purged to deep-well
injection (SRC-1, SRC-2), ASSUMED, against the build-up of the ore's soluble impurities
(magnesium, sulfate), which are not components here (L-1).

### D-007 Crystallizer and centrifuge

Seven vacuum cooling stages from 363.15 to 318.15 K (SRC-1: to about 45 C; SRC-3: seven stages)
are one crystallizer step (X-201, X201) on core's model with an **imposed yield of 0.2685**: the
equilibrium on the solubility line of D-004 (ASSUMED, L-3). The mother liquor leaves saturated at
318.15 K, s45 = 0.1208 x (1 + 25/90) = 0.1544 kg KCl per kg water, and holds the hot brine's water
plus the make-up water S6, because the water flashed in the stages comes back as condensate:
1 - 0.1544 x (S5 water + S6) / S5 KCl = 0.2685, found by successive substitution on the
propagated flowsheet (the mother liquor S10 then holds 0.1544 kg/kg). The water flashed in the
stages is condensed (E-201) and returned to the crystallizer feed with the make-up water as
dilution water, so that the NaCl, near saturation, stays dissolved while the water evaporates; the
NaCl is a spectator whose own solubility core does not check (L-3). The flash is adiabatic: an
enthalpy balance from 298.15 K, with the brines at an ASSUMED 3.0 kJ/(kg K) and the cake at 0.70,
gives the vapour the hot brine S5's heat at 363.15 K less that of the mother liquor S10 and the
cake S9 at 318.15 K (the make-up water enters at 298.15 K, the condensate enters and leaves at
318.15 K): 148.8 MW, or 229.1 t/h at water's latent heat at the stages' mean 340.65 K (2339
kJ/kg, SRC-6), 7.97 % of the feed's water. The heat of crystallisation is left out (L-2, D-009).
The centrifuges give a cake of 96 % solids (SRC-2), every crystal to the cake (the hydrocyclones'
overflow returned, ASSUMED), no wash (L-4).

**SRC-3's example as a check of the yield.** The patent's crystallizer forms 164 kg of KCl per
hour from 1846 kg of solution with 26 kg of KCl, saturated at 95 C, and 118 kg of dilution water,
cooled to 35 C: 0.082 kg of crystal per kg of feed over 60 K, 0.00137 per K (0.00116 per K net of
the 26 kg it recycles to the saturator), with 13.6 kg of hot solution per kg of product. The model
forms 150 t/h from 4213 t/h of feed over 45 K, 0.00079 per K, with 25.9 t of hot brine per t of
product: the example gives 1.5-1.7 times more crystal per kg of feed and K. The example states no
brine composition, so it cannot set the solubility line of D-004 without an assumed water content;
the line is kept, and the circulation and every duty that scales with it (the steam above all) are
probably high by a similar factor. The ranges differ (95 to 35 C there, 90 to 45 C here) and the
patent's ore and brine are not SRC-1's, so the gap is recorded, not corrected (L-3, Open items).
SRC-1's steam per t (D-008) points the same way.

### D-008 Energy

The duties are enthalpy balances from 298.15 K on the propagated streams, with the brines at an
ASSUMED 3.0 kJ/(kg K) throughout, so that the leach, the crystallizer and the heaters close around
the loop: the steam Q3 equals what leaves with the cooling water Q2, the tailings (9.15 MW), the
cake (0.61 MW) and the purge (0.32 MW) (checked by the tests).

- **Mother-liquor temperature.** The ore enters the leach at 298.15 K; the mother liquor S2 must
  bring what the hot brine S5 (213.25 MW) and the tailings S4 (9.15 MW: their brine at 3.0, their
  solids at 0.8408 kJ/(kg K) from KCl(s) 0.688, NaCl(s) 0.8642 and CaSO4(s) 0.7163, SRC-6, and the
  insolubles at 0.80, ASSUMED) carry out at 363.15 K: S2 at 368.22 K.
- **Vapour heat recovery, limited by the boiling-point elevation.** The vapour of a stage condenses
  at the saturation temperature of the stage's pressure, which lies below the brine's temperature
  by the boiling-point elevation (BPE). Per stage (equal temperature steps of 6.43 K, equal shares
  of the evaporation and of the crystal), core's Pitzer model of NaCl-H2O (`cheme process
  electrolyte`) gives the water activity at the stage's NaCl molality (4.69-5.03 mol/kg), a BPE of
  4.2-4.9 K for the NaCl alone; the dissolved KCl (2.07-2.53 mol/kg) lowers the water activity
  further, counted here at the NaCl's osmotic coefficient (ln a_w scaled by the total molality,
  ASSUMED: core has no model of the mixed brine and no open water activity of it was read, L-2),
  which gives a BPE of 5.8-7.4 K and condensing temperatures of 349.31 K (stage 1) down to
  312.31 K (stage 7) (IAPWS-95 saturation, chemicals 1.5.2). The vapour of stages 1-5 heats the
  mother liquor counter-currently (SRC-3), each preheater's outlet 5 K (ASSUMED) below its stage's
  condensing temperature: S14 from 318.15 to 344.31 K, 83.04 MW (Q1). Stage 5's vapour condenses
  at 324.65 K and takes the liquor only 1.5 K; the rest of it, stages 6 and 7 and the small
  surplus of stages 1-4 go to cooling water, 65.81 MW (Q2). The last stage's vapour, at about
  312.3 K, keeps a 7 K approach to cooling water returned at 305.15 K (ASSUMED). Without the BPE
  the preheat would reach about 351.7 K; with the NaCl's BPE alone about 346.9 K.
- **Steam.** LP steam at 450 kPa(a) heats the mother liquor from 344.31 to 368.22 K: 75.89 MW
  (Q3, about 128.8 t/h, 1.80 GJ per t of product).
- **Against SRC-1.** SRC-1's nominal hot-leach steam, 208.0 t/h at 150 psig (latent heat 1994
  kJ/kg at 458.6 K, SRC-6) for 2.16 Mt/a in 7620 h (Table 85, section 13), is 1.46 GJ per t of
  product: the model's 1.80 GJ is 1.2 times that, the direction of the yield gap of D-007. SRC-1
  also reheats the mother liquor to about 115 C, which by this balance would put the leach at
  about 384 K; the difference is what the model leaves out (the heats of solution and
  crystallisation and the heat lost from tanks, cyclones and thickener, D-009) and its smaller
  per-pass yield. SRC-1 raises this steam in high-voltage electrode boilers on grid power (15.2.7).
- **Dryer.** Core's dryer model (DR-301, DR301): the cake heated from 318.15 to 423.15 K (SRC-2:
  140-160 C) at 0.70 kJ/(kg K) (KCl(s), SRC-6) and 4.16 t/h of water evaporated at 2256 kJ/kg
  (SRC-6), 5.80 MW taken up by the cake; at an ASSUMED dryer efficiency of 0.6 (the share of the
  drying air's heat that leaves with the exhaust), 9.66 MW of heat taken up by the drying air from
  the direct-fired natural-gas heater (Q4), 0.23 GJ per t. Q4 is that heat, not the fuel: the
  burner's own losses belong to the fired heat's background (D-010). SRC-1's dryer and dryer cooler
  burn 1 064 176 MMBtu/a of natural gas (Table 129), about 0.52 GJ per t of its product; the model's
  0.23 GJ per t is lower, with the dryer cooler, the fuel's heating value and the 0.6 not resolved
  here (Open items).
- **Electricity.** 141.3 kWh per t of product, 21.5 MW, lumped on the mother-liquor pumps (P1):
  SRC-1's process electrical demand of the areas inside this boundary (Table 128: wet process
  11 552, dry process 18 551, product handling and storage 387, tailings processing 1182, reagents
  210, utilities 6171 and ancillary facilities 2001 kW, 40 054 kW for two trains) over its nominal
  283.46 t/h (2.16 Mt/a in 7620 h), taken per t of product (ASSUMED: a demand of a load list, not a
  metered consumption). Left out: raw ore handling and primary crushing (4805 kW, outside the
  boundary), brine injection (3547 kW, with the purge's gap), steam generation (161 000 kW, the
  electrode boilers, the steam being its own feed) and the barge port. The utilities area may
  include cooling-water pumps that the linked cooling-tower utility also counts (ASSUMED small).
  SRC-4's 312.5 kWh per t K2O, 187.5 kWh per t KCl for a carnallite plant of another route, is the
  independent benchmark (benchmarks/fertilizers.yaml).
- **Cross-check.** The heat here, 1.80 GJ of steam and 0.23 GJ of fired heat per t, is of the
  order of SRC-4's 1.04 GJ of fuel oil per t of KCl (1720.8 MJ per t K2O / 1.66), for another
  route.

### D-009 What is left out

Flocculant (SRC-1, SRC-2), anti-caking agent and de-dusting oil (SRC-1, SRC-2) and iron oxide
(SRC-2) are named by the sources without amounts read; they are left out of the inventory rather
than invented (L-5). Compaction and screening are in the lumped power. Energy flows left out, with
their size:

- **The crystallizer's vacuum system.** SRC-1 drives it with steam ejectors, 9.0 t/h of steam
  (nominal, two trains, Table 85); scaled per t of product that is about 4.8 t/h here, about 2.7 MW
  as condensing heat at 150 psig, 3.5 % of the heater's steam Q3. Not modelled (the crystallizer
  step has no energy port); the steam is therefore low by about that share.
- **The heats of solution and crystallisation.** The leach dissolves 2140 kmol/h of KCl and 251
  kmol/h of NaCl; the crystallizer brings 2012 kmol/h of KCl back out. No open heat of solution of
  KCl or NaCl in these brines was read (L-2), so the size is stated per unit of it: per 10 kJ/mol of
  KCl's heat of solution the leach takes up 5.9 MW (endothermic) and the crystallizer releases 5.6
  MW. The leach's share is made up by the steam (Q3 up by 5.9 MW per 10 kJ/mol, 8 % of Q3); the
  crystallizer's share flashes more vapour, which the preheaters, limited by the BPE, take only in
  part, the rest going to cooling water. Their net, 0.35 MW per 10 kJ/mol, is the floor; the steam is
  low by between that and the leach's full share. The NaCl's share is smaller (251 kmol/h).
- **Heat losses** from tanks, cyclones, thickener and pipes: not estimated; they raise the steam.

So the steam Q3 is a lower bound on all three counts.

### D-010 LCA: boundary, allocation, mappings, gaps

Preliminary gate-to-gate inventory per kg of dried product (S16), one product, no allocation: the
tailings and the purge are wastes (no sale of the halite assumed). Linked in lca/mappings.yaml:
the make-up water to the shared water entry, the steam as heat delivered (steam-heat, a
natural-gas-fired background; SRC-1 raises its steam in electrode boilers on grid power, 15.2.7,
which a site-specific study would map instead), the dryer as the heat its air takes up from
natural gas (heat-natural-gas, the burner's losses in the background, D-008). Gaps, never 0: the
ore (no library process mines sylvinite), the tailings' disposal on a pile and the brine's
deep-well injection: both carry their own registry slugs (potash-tailings, potash-brine-purge)
that have no entry, so that the Atlas build leaves them gaps too, instead of reading the
tailings as purchased sodium chloride or the injected brine as wastewater for activated-sludge
treatment. The electricity and the cooling water are gaps in `cheme assess lca` (lca/gaps.csv);
the Atlas build links them by their slugs to the shared grid entry and to the shared
cooling-tower utility (processes/utility-cooling-tower, cooling water from 298.15 K, which this
plant's 25 C supply matches). The dryer's dust and the fired
heater's combustion products are an emission exclusion (the latter belong to the fired heat's
background). The leach has no energy stream (its heat comes with the mother liquor), so `cheme
assess lca` reports one boundary warning (L101), as sodium-chlorate-1 does for its reaction
tanks.

### D-011 Hazards (reasoned; no HAZOP at this stage)

No reaction and no flammable process fluid: the leach is a dissolution, the brine non-flammable.
The hazards are those of a hot-brine and minerals plant: scalding by brine at 90-95 C and LP
steam; the vacuum vessels of the crystallizer (implosion, the barometric legs); the natural-gas
burners of the dryer (fuel-gas train, purge and flame safeguards); dust of the dryer, compaction
and conveyors; heavy rotating machinery (crushers outside, centrifuges, compactors, agitators);
corrosion by hot chloride brine; the tailings pile and its brine (groundwater, the deep-well
injection). `cheme process reactor-hazards` does not apply (no exothermic reaction; the
dissolution is endothermic).

## Core features used

- `cheme process propagate` with two tears (S2, S7) and two design specifications (ore for the
  product rate, make-up water for the brine's KCl);
- a conversion reactor for the dissolutions (process/reactions.yaml);
- `solid_separation:` for the tailings; core's crystallizer (imposed yield, evaporation,
  spectator NaCl, centrifuge) and dryer (`cheme process crystallizers`);
- `cheme process build` (BFD, PFD), `cheme assess lca`.

## Core limits (L-n)

- **L-1** No lumped mineral component: core's component and element balances need a formula, so
  INSOL (clay, dolomite, minor sulfates) is written as SiO2 (ASSUMED), which it is not; the ore's
  soluble impurities (MgSO4, K2SO4, CaSO4 traces) are not components, and the purge stands for
  their removal.
- **L-2** No heats of solution or crystallisation of KCl and NaCl in brine and no brine heat
  capacity: core has no electrolyte enthalpy beyond aqueous NaCl alone (`cheme process
  electrolyte`, NaCl-H2O up to 6 mol/kg), so the duties are sensible-heat hand balances with an
  ASSUMED 3.0 kJ/(kg K), the leach's endothermic dissolution and the heat of crystallisation are
  left out (sized per unit in D-009), and the mixed brine's boiling-point elevation is core's
  NaCl value with the KCl's share ASSUMED (D-008).
- **L-3** No solubility of KCl in NaCl-saturated brine: no open two-salt saturation data were read,
  so the crystallizer runs on an imposed yield, the equilibrium on an ASSUMED solubility line
  (D-007), not `basis: solubility`; SRC-3's example suggests 1.5-1.7 times the yield per kg of
  feed and K (D-007); and core's
  crystallizer has one crystallising solute and does not check a spectator's own solubility, so
  the NaCl's staying dissolved is a design intent (the dilution water), not a result.
- **L-4** No cake wash on the tailings filter or the product centrifuge; the tailings' brine is a
  KCl loss the real plant reduces by washing.
- **L-5** Reagents with no amount read (flocculant, anti-caking agent, de-dusting oil) are left out.

## Open items

- Source the KCl-NaCl-water two-salt saturation at 25-100 C from an open table and switch X201 to
  `basis: solubility` with `measured_in: mother_liquor` (and the leach temperature to the
  saturation it gives).
- Read SRC-1 chapter 14 (brine compositions, water and reagent tables) and its chapter 17 dryer
  data, and resolve the gap to SRC-1's hot-leach steam (1.46 against 1.80 GJ per t, D-008) and
  dryer gas (0.52 against 0.23 GJ per t) with the yield of D-007.
- An open water activity or boiling-point elevation of the KCl-NaCl brine, to replace the ASSUMED
  KCl share of the BPE (D-008), and an open heat of solution of KCl in NaCl brine (D-009).
- A flotation variant (the commoner route for sylvinite) once an open source with its reagents
  and energy is read.
- Link the product as the KCl supplier of npk-fertilizers-1 (feed:potassium-chloride) and of
  potassium-tert-butoxide-1's proxy, in their own reviews.
