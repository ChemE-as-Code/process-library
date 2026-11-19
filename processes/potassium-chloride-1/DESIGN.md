# Design decisions: potassium-chloride-1

Potassium chloride (muriate of potash, MOP) from crushed sylvinite ore by hot leaching and vacuum
cooling crystallisation. Concept stage, issue ChemE-as-Code/process-library#514. Every number
below is either taken from a source in the register (with its locator), calculated by core from
the files, or marked ASSUMED. Nothing is copied from the sources: no tables, figures or text,
only single facts in our own words.

## Source register

| id | source | access | used for |
|---|---|---|---|
| SRC-1 | Brazil Potash Corp. (2024), *S-K 1300 Technical Report Summary, Autazes Potash Project*, exhibit 96.1 to its Form F-1, SEC EDGAR, <https://www.sec.gov/Archives/edgar/data/1472326/000119312524203710/d303049dex961.htm> | open, read 2026-11-19: the executive summary and chapters to 7.5 (the 6.8 MB filing is longer than the reader took in; chapter 14 and its tables were not read) | the route (section 1.10): ore crushed below 4 mm in two trains, two cascaded agitated leach stages at about 90 C, cyclone classification, seven-stage vacuum cooling crystallizer to about 45 C, mother liquor reheated to about 115 C and returned, centrifuge, rotary dryer, compaction, glazing in a fluid bed, flocculant and anti-caking agent, tailings filtered to piles and backfill, brine injected at 310-400 m; KCl recovery 90.8 %; 2.44 Mt/a design capacity, 2.16 Mt/a average of 95 % KCl from 8.32 Mt/a of ore at 27.3 % KCl (sections 1.9, 1.10); natural gas for drying and steam (1.10); about 294 MW site demand with the mine and port (1.11); the 2014 averaged grades of Table 10 (KCl 31.5, NaCl 55.4, MgSO4 1.0, K2SO4 1.5, CaSO4 6.8, insolubles 3.5, moisture 0.3 wt%) |
| SRC-2 | Amec Foster Wheeler for Encanto Potash Corp. (2017), *Muskowekwan Project, Preliminary Economic Assessment and Preliminary Feasibility Study, NI 43-101 Technical Report*, <https://minedocs.com/12/Muskowekwan_PFS_05242017.pdf> | open PDF, read (text extracted), 2026-11-19 | the solution-mining variant (D-001): primary brine 148 g/L KCl and 254 g/L NaCl at a 60 C cavern temperature (section 1.9, Table 13-1); NaCl removed first in multi-effect evaporators, then vacuum cooling crystallizers in stages (17.3.2, 17.3.3); centrifuge cake about 96 % solids (17.3.5); fluid-bed dryers with natural-gas burners, crystals out at 140-160 C, cyclones and wet scrubbers (17.3.6); anti-caking and de-dusting oil, flocculant (17.3.7-17.3.10); waste brine to deep-well injection (17.3.11); 8100 h/a, plant recovery 93 % (Table 17-1); natural gas about 1700 GJ/h, mostly for cogeneration (24.18) |
| SRC-3 | Metallgesellschaft AG (1983), *Process for recovering potassium chloride*, US 4 412 838 A, <https://patents.google.com/patent/US4412838A/en> (and its European family member EP 0 003 065 A1, <https://patents.google.com/patent/EP0003065A1/en>) | open, read (description, claims and example), 2026-11-19 | the hot-leach loop: sylvinite leached at 95-100 C, the brine saturated at about 95 C, seven vacuum crystallisation stages to 35 C, the vapour of the first five stages heating the returning mother liquor, which is then heated to 111 C; product 98.13 % KCl; the background statement that the KCl solubility more than doubles between 20 and 110 C while the NaCl solubility hardly changes; feed sylvinite 28-32 % KCl with 3.5-4.5 % insolubles |
| SRC-4 | Shahvarooghi Farahani, S.; Zamanifard, H.; Taki, M. (2024), *Assessing the energy load and environmental footprint of potash fertilizer production in Iran*, PLoS ONE 19(11): e0313129, doi:10.1371/journal.pone.0313129 (CC BY 4.0) | open, read 2026-11-19 | a KCl plant of another route (carnallite from brine pools, flotation and decomposition, Khur, 50 kt/a): electricity 312.5 kWh and fuel oil 36 L (1720.8 MJ) per t K2O, 60 % K2O in KCl (Table 3, Table 5); the only open per-t electricity read, and a cross-check of the heat |
| SRC-5 | National Bureau of Standards: Gevantman, L. H. (ed.) (1981), *Physical properties data for rock salt*, NBS Monograph 167, <https://nvlpubs.nist.gov/nistpubs/Legacy/MONO/nbsmonograph167.pdf> (US government work) | open PDF, read (Table 1.10 and section 2.5.1), 2026-11-19 | the NaCl solubility in KCl solutions of up to 12 wt% KCl, 0-100 C (Table 1.10), and the statement that in the NaCl-KCl-water system the KCl solubility rises strongly with temperature while the NaCl solubility falls slightly below 373 K (2.5.1); it does not reach the two-salt saturation, so it confirms the trend only (L-3) |
| SRC-6 | `thermo` 0.6.1 and `chemicals` 1.5.2 Python packages (C. Bell et al.) | open-source packages queried, 2026-11-19; single values, facts only | single values (library ADR 0037): heat of vaporisation of water 2393.99 kJ/kg at 318.15 K, 2339 kJ/kg at 340.65 K, 2256 kJ/kg at 373.15 K and 2121 kJ/kg at 420.8 K (thermo, method HEOS_FIT, a fit to IAPWS-95); heat capacity of solid KCl 0.688 kJ/(kg K) at 298.15 K and 0.706 at 373.15 K and of solid NaCl 0.864 at 298.15 K (thermo, method WEBBOOK_SHOMATE, the NIST Chemistry WebBook's Shomate fits, not read here), of solid CaSO4 0.716 at 298.15 K (thermo, method PERRY151, a correlation of Perry's handbook as the package bundles it, the handbook not read here). These are facts with their source, not open data |

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

The leach (R-101, L101) is a conversion step: 96.07 % of the sylvite dissolves (DISK) and 4.055
% of the halite (DISN). Both are ASSUMED and set by successive substitution on the propagated
flowsheet: DISK so that the dried product holds 90.8 % of the ore's KCl, SRC-1's recovery (the
rest leaves undissolved, 1.36 wt% of the tailings, and dissolved in the tailings' brine and the
purge); DISN so that the hot brine keeps its 0.2995 kg NaCl per kg water, the halite dissolved
replacing the NaCl lost with the tailings' brine, the purge and the product. The leach
temperature is SRC-1's about 90 C, taken as 363.15 K.

Two loops are torn: the mother liquor to the leach (S2) and the condensate to the crystallizer
(S7). Two design specifications close them: `rate` adjusts the ore (S1, 607.7 t/h, 4.0 t per t of
product) for 150 t/h of crystal, `liquor` adjusts the make-up water (S6, 46.9 t/h) for the hot
brine's 14.19 wt% KCl. The brine circulation follows: 3775 t/h of hot brine, 25 t per t of
product.

### D-006 Tailings and purge

The cyclones, the hot thickener (with flocculant, SRC-1) and the tailings filter are lumped into
one solid separation (S-101, S101): every solid to the tailings, which hold 10 wt% brine
(ASSUMED; no cake wash, L-4). 480 t/h of tailings, 3.16 t per t of product, go to the pile and
the underground backfill (SRC-1). 0.5 % of the mother liquor (18.3 t/h) is purged to deep-well
injection (SRC-1, SRC-2), ASSUMED, against the build-up of the ore's soluble impurities
(magnesium, sulfate), which are not components here (L-1).

### D-007 Crystallizer and centrifuge

Seven vacuum cooling stages from 363.15 to 318.15 K (SRC-1: to about 45 C; SRC-3: seven stages)
are one crystallizer step (X-201, X201) on core's model with an **imposed yield of 0.28**: with
the solubility of D-004, 1 - (1 + 25/90) / (1 + 70/90) = 0.281 of the KCl entering crystallises
when the water is kept (ASSUMED, L-3). The water flashed in the stages is condensed (E-201) and
returned to the crystallizer feed with the make-up water as dilution water, so that the NaCl,
near saturation, stays dissolved while the water evaporates; the NaCl is a spectator whose own
solubility core does not check (L-3). The flash is adiabatic: 7.85 % of the feed's water (216.4
t/h) takes the hot brine's sensible heat from 363.15 to 318.15 K at an ASSUMED 3.0 kJ/(kg K),
less the make-up water's warming, at water's latent heat at the stages' mean 340.65 K (2339
kJ/kg, SRC-6); the heat of crystallisation is left out (L-2). The centrifuges give a cake of 96 %
solids (SRC-2), every crystal to the cake (the hydrocyclones' overflow returned, ASSUMED), no
wash (L-4).

### D-008 Energy

- **Mother-liquor heating.** The mother liquor (3648 t/h) must reach 366.08 K so that, mixed with
  the ore at 298.15 K, the leach is at 363.15 K: 363.15 + S1 x 0.8113 x 65 / (S2 x 3.0), with
  the ore's heat capacity from its minerals (SRC-6; insolubles 0.80 ASSUMED) and the brine's 3.0
  kJ/(kg K) ASSUMED. The vapour of the first five of the seven stages heats it first (SRC-3):
  5/7 of the vapour's 140.57 MW, 100.41 MW (Q1), the stages taken to evaporate equal shares
  (ASSUMED), to 351.18 K. LP steam at 450 kPa(a) does the rest, 45.28 MW (Q3, about 76.9 t/h,
  1.07 GJ per t of product). The last two stages' vapour, 40.16 MW, goes to cooling water (Q2).
- **The difference to SRC-1's 115 C.** SRC-1 reheats the mother liquor to about 115 C, which by
  this sensible balance would put the leach at 384 K. The gap is what the model leaves out: the
  heat of solution of the 2138 kmol/h of KCl dissolved (endothermic; no open value read, L-2),
  the heat lost from tanks, cyclones and thickener, and a smaller circulation if the real per-pass
  yield is higher than the ASSUMED 0.28 (L-3). The steam here is therefore a lower bound.
- **Dryer.** Core's dryer model (DR-301, DR301): the cake heated from 318.15 to 423.15 K (SRC-2:
  140-160 C) at 0.70 kJ/(kg K) (KCl(s), SRC-6) and 4.17 t/h of water evaporated at 2256 kJ/kg
  (SRC-6), at an ASSUMED efficiency of 0.6: 9.67 MW of natural-gas-fired heat (Q4), 0.23 GJ per t.
- **Electricity.** 187.5 kWh per t of product, 28.5 MW, lumped on the mother-liquor pumps (P1):
  SRC-4's 312.5 kWh per t K2O at 0.6 t K2O per t KCl. SRC-4's plant is of another route and is
  the only open per-t figure read (ASSUMED). SRC-1's 294 MW for the whole site with the mine,
  about 1.2 MWh per t, is an upper bound that includes mining and hoisting.
- **Cross-check.** The heat here, 1.07 GJ of steam and 0.23 GJ of fired heat per t, is of the
  order of SRC-4's 1.04 GJ of fuel oil per t of KCl (1720.8 MJ per t K2O / 1.66).

### D-009 What is left out

Flocculant (SRC-1, SRC-2), anti-caking agent and de-dusting oil (SRC-1, SRC-2) and iron oxide
(SRC-2) are named by the sources without amounts read; they are left out of the inventory rather
than invented (L-5). The vacuum system (steam ejectors or vacuum pumps) and its motive steam are
not sized. Compaction and screening are in the lumped power.

### D-010 LCA: boundary, allocation, mappings, gaps

Preliminary gate-to-gate inventory per kg of dried product (S16), one product, no allocation: the
tailings and the purge are wastes (no sale of the halite assumed). Linked in lca/mappings.yaml:
the make-up water to the shared water entry, the steam as heat delivered (steam-heat), the dryer
as heat from natural gas (heat-natural-gas). Gaps, never 0: the ore (no library process mines
sylvinite), the electricity (the Atlas build links the shared grid entry), the cooling water, the
tailings' disposal on a pile and the brine's deep-well injection. The dryer's dust and the fired
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
  electrolyte`), so the duties are sensible-heat hand balances with an ASSUMED 3.0 kJ/(kg K), and
  the leach's endothermic dissolution is left out (D-008).
- **L-3** No solubility of KCl in NaCl-saturated brine: no open two-salt saturation data were read,
  so the crystallizer runs on an imposed yield (D-007), not `basis: solubility`; and core's
  crystallizer has one crystallising solute and does not check a spectator's own solubility, so
  the NaCl's staying dissolved is a design intent (the dilution water), not a result.
- **L-4** No cake wash on the tailings filter or the product centrifuge; the tailings' brine is a
  KCl loss the real plant reduces by washing.
- **L-5** Reagents with no amount read (flocculant, anti-caking agent, de-dusting oil) are left out.

## Open items

- Source the KCl-NaCl-water two-salt saturation at 25-100 C from an open table and switch X201 to
  `basis: solubility` with `measured_in: mother_liquor` (and the leach temperature to the
  saturation it gives).
- Read SRC-1 chapter 14 (brine compositions, steam, power, water and reagent tables) and replace
  the ASSUMED power and heat.
- A flotation variant (the commoner route for sylvinite) once an open source with its reagents
  and energy is read.
- Link the product as the KCl supplier of npk-fertilizers-1 (feed:potassium-chloride) and of
  potassium-tert-butoxide-1's proxy, in their own reviews.
