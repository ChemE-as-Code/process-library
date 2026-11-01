# Design decisions

One entry per decision: what was decided, why, what was rejected, and what it assumes.
The numbers live in `process/*.yaml` and `scripts/bayer_balance.py`; the stream table is
generated: `cheme process streams --md` (provenance letter per value). Issue:
ChemE-as-Code/process-library#178.

Run record of this stage (2026-10-28): library branch `case/alumina-1` from `5ecbd1e`;
cheme-as-code 0.8.0 (pyDEXPI 2.1.0), Python 3.15.0; DWSIM not used. Core dependencies as
reported in the #178 comments (not re-audited against core main in this run): core adds an
electrolyte route for aqueous NaCl only, so NaOH-NaAl(OH)4-H2O liquors stay unsupported; core
supports one-solute crystallisers and solid separations with sourced solubility (gibbsite
from an impure multi-component caustic aluminate liquor is not that case: imposed yield); core
`cheme process furnace` covers limestone calcination only and refuses gibbsite
(`cheme.furnace-unsupported`).

## 1. Route and boundary memo

- **Route**: Bayer process for metallurgical (smelter-grade) alumina from a gibbsitic
  (trihydrate) bauxite: grinding in spent liquor, pre-desilication, low-temperature caustic
  digestion, flash heat recovery, residue settling, counter-current washing and filtration,
  seeded precipitation of gibbsite, classification with seed recycle, hydrate filtration,
  calcination; spent liquor evaporation and caustic make-up close the liquor cycle (the
  defining recycle; the residue is its purge). Net: 2 Al(OH)3 (bauxite) -> Al2O3 + 3 H2O,
  carried through Al(OH)3 + NaOH <-> NaAlO2 + 2 H2O. Operation sequence after the IAI Bayer
  process overview (references in process.yaml) and the tech skill
  `tech-heavy-chem-pigments-and-minerals` (Speight, Part 2).
- **Rejected for this case**: high-temperature (513-543 K class) digestion for boehmitic or
  diasporic bauxite (not needed for a trihydrate ore; it would raise steam use and attack
  quartz); sinter or combined Bayer-sinter processes (for high-silica ores); nepheline and
  other non-bauxite routes (out of scope, IAI estimates <5 % of production). Hall-Heroult
  smelting stays outside (#178 scope note).
- **Boundary** (gate-to-gate): from bauxite (as received, crushed), quicklime, 50 % caustic
  soda, natural gas, fresh water and air at the battery limit to smelter-grade alumina at the
  calciner cooler outlet. Inside: slaker, mills, pre-desilication, heaters, digesters, flash
  train, settler, washers, residue filters, liquor coolers, precipitators, classification,
  hydrate filters, evaporators, make-up and hot water tanks, gas suspension calciner with ESP.
  Outside: bauxite mining and shipping, lime burning, caustic production, steam and power
  generation, cooling tower, residue storage area, alumina storage and shipping, liquor
  impurity removal (oxalate, organics), residue neutralisation or reuse.
- **What crosses the boundary**: BX, LIME, NAOH, PW, NG, AIR (raw materials); ALU (product);
  RES (bauxite residue filter cake, solid waste); STACK (calciner flue gas); POWER, MPS, LPS
  (heat delivered), CW (utilities).
- **Links to other library processes**: caustic soda is a product of `chlor-alkali-1` (link its
  dataset once mapped); steam could come from `utility-steam-ng-boiler`, cooling from
  `utility-cooling-tower`. They are boundary feeds here (#178 case notes).

## 2. Decisions

## D-001 Route and boundary (2026-10-28)
Decision: Bayer process with low-temperature digestion of a gibbsitic bauxite, boundary as in
section 1. Reason: the dominant route for metallurgical alumina; a trihydrate ore is the
common case for Atlantic and Australian refineries and keeps the digestion at 418 K.
Rejected: see section 1. Assumptions: no residue reuse, no impurity (oxalate) removal
circuit, no lime causticisation of carbonate (not carried, D-006).

## D-002 Capacity, product and hours (2026-10-28)
Decision: 3000 t/d smelter-grade alumina (125 t/h), 8400 h/a; product 99.0 wt% Al2O3,
0.40 wt% Na2O, 0.60 wt% LOI. Reason: a normalisation basis in the size range of world-scale
refineries (about 1 Mt/a) for the inventory, not a commercial plant claim (#178). The grade
is a typical smelter specification range; ASSUMED (no customer specification).

## D-003 Bauxite (2026-10-28)
Decision: the Debele / Balaya plateau (Kindia, Guinea) gibbsitic bauxite, chemistry from
Zainudeen et al. (2023) Heliyon 9:e19070 Table 6 (column "Balaya Plateau 2": Al2O3 54.69,
Fe2O3 12.25, SiO2 0.76, TiO2 2.85, LOI 29.69, minor oxides 0.38 wt%), minerals from its Table 5
(gibbsite 83.9, kaolinite 1.1, diaspore 1.3, goethite 4.5 + aluminian goethite 6.15, hematite
4.1 wt%). Normative mineralogy derived in `scripts/bayer_balance.py`: kaolinite carries the
reactive silica, the remaining SiO2 is quartz, diaspore is carried as AlOOH, the remaining
Al2O3 is gibbsite (80.9 wt%), goethite as listed and hematite as the iron remainder; minor
oxides are lumped into TiO2. The derived water (29.60 wt%) agrees with the assay LOI (29.69
wt%) within 0.1 point, a consistency check of the derivation. Moisture 10 wt% ASSUMED (the
IAI 2019 LCI report s. 3.4 says bauxite input typically carries 10-20 % water).
Rejected: the Sangaredi assay of the same table: its chemistry (61.25 % Al2O3, LOI 28.89 %)
and its mineral list do not close (the gibbsite listed would need more water than the LOI),
so its normative mineralogy would need an invented boehmite content. Assumptions: a single
assay stands for the ore; no organic carbon, carbonate, phosphate or sulfur carried.

## D-004 Digestion, desilication and lime (2026-10-28)
Decision: digestion at 418 K (low-temperature digestion of gibbsite is run at about 413-423 K,
ICSOBA 2024 paper AA05, abstract level), 98 % of the gibbsite dissolved, diaspore/boehmite and
quartz not attacked (ASSUMED), blow-off A/C 0.70 (ASSUMED). Kaolinite fully converted to a
desilication product carried as hydroxysodalite Na8Al6Si6O24(OH)2 (Na/Si 1.33), in
pre-desilication at 373 K (ASSUMED). Lime 52 kg CaO/t alumina: the 2019 surveyed lime
consumption of the IAI 2019 LCI report s. 3.11.2.3 (a global average, used as the dose);
slaked to 15 wt% milk of lime (ASSUMED); all lime leaves as tricalcium aluminate (TCA,
hydrogarnet), which also takes alumina out of the liquor (TCA reaction).
Rejected: kinetics or a solubility model (not available in core, no sourced data for this
ore; #178 forbids invented kinetics). Assumptions: the real roles of lime (causticisation of
carbonate, phosphate and titania control) are not carried; the TCA reaction is the simplest
lime fate that closes the balance.

## D-005 Clarification, washing, residue, caustic and water (2026-10-28)
Decision: settler underflow 2.0, last-washer underflow 1.0 and filter cake 0.43 kg liquor/kg
solids (cake 70 wt% solids, filter presses for dry stacking); 6 ideal counter-current stages
at a wash ratio of 1.6 (wash water / last-underflow liquor), the solute carried into the last
underflow from the Kremser-type relation (R - 1)/(R^(N+1) - 1); residue filtrate returns to
the washers; overflow of the settler solids-free after security filtration. All ASSUMED.
Caustic make-up (50 wt% NaOH) equals the sodium leaving with DSP, residue cake liquor and the
product soda (solved, 15.5 kg NaOH/t alumina). The flash and evaporator condensate go to a hot
water tank that supplies slaking, residue washing and hydrate washing; fresh water closes it
(0.134 t/t). Rejected: thickener models from settling data (none available).
Assumptions: no other soda losses (spills, liquor purge with oxalate and carbonate, sodium in
scale): the caustic make-up is a lower bound and likely well below refinery practice; this
is the most consequential open input of the LCI after the energy.

## D-006 Liquor basis, precipitation and evaporation (2026-10-28)
Decision: liquors carried as neutral NaOH + NaAlO2 + H2O (NaAlO2 = NaAl(OH)4 - 2 H2O), with
the industry's A/C convention: spent liquor 250 g/L caustic as Na2CO3, A/C 0.38, density 1.30
kg/L for every liquor (ASSUMED). Precipitation fixed by the spent A/C 0.38 at 335 K after a
fill at 351 K (ASSUMED), seed charge 250 g/L, seed and product slurries 1 kg liquor/kg
hydrate, hydrate cake 8 wt% free water after washing with 0.25 kg/kg; occluded soda sets the
product's 0.40 % Na2O (ASSUMED). The evaporators return the liquor to 250 g/L (water removal
solved, 0.42 t/t). Rejected: a gibbsite solubility or precipitation-kinetics model (core
core does not cover caustic aluminate; no sourced equilibrium for this liquor in this run).
Assumptions: carbonate, oxalate, organics, chloride and sulfate of real liquors are not
carried; the A/C values are typical design choices to be replaced by a sourced or simulated
equilibrium.

## D-007 Utilities and duties (2026-10-28)
Decision: duties from a lumped sensible-heat balance in the script: liquor cp 3.35, solids
1.0 kJ/kg K; 3 flash/regenerative stages with 5 K approach (slurry preheated to 397 K), MP
steam 1000 kPa(a) for the rest of the heating to 418 K plus the dissolution heat (20.6 kJ/mol
from formation enthalpies) and 3 % losses (57.8 MW); the pregnant liquor cooler recovers 70 %
of its duty into the spent liquor, which, with the flash heat the slurry cannot take, heats the
mill feed to 373 K, LP steam covering the rest (15.9 MW); evaporators at an economy of 3.0
(10.3 MW LP steam), their condenser rejecting the same heat; precipitator interstage cooling
to cooling water. Electricity 152 kWh/t: the 2019 global average of the IAI 2019 LCI report
Table 4 (547 MJ/t Al2O3), lumped on the mill step. All ASSUMED.
Result per t alumina: steam heat 0.67 MWh (2.42 GJ: MP 1.66, LP 0.75), calciner 2.80 GJ,
electricity 0.55 GJ, about 5.8 GJ/t delivered. Cross-check: the IAI 2019 global average of
fuel and electricity is about 10.5 GJ/t (Table 4, summed), which includes high-temperature
digestion, coal-fired steam and older plants; the ICSOBA 2024 AA05 abstract puts steam at
about 55 % and calcination at about 35 % of a refinery's energy, i.e. steam about 1.6 times
the calciner; here it is 0.9 times. The steam figure is therefore likely LOW: no tank and
pipe losses, no heat for pre-desilication residence, ideal heat recovery and no steam to
other users. Rejected: DWSIM (refuses the electrolytes and solids).

## D-008 Calcination (2026-10-28)
Decision: gas suspension calciner on natural gas (taken as methane, LHV 50 MJ/kg), specific
energy 2.8 GJ/t alumina LHV, ASSUMED a little above the about 2.72 GJ/t that the ICSOBA 2017
paper AA22 (abstract level) reports as an average for gas suspension calciners; air excess
1.15 (ASSUMED); complete calcination and soda fixation (CALC, SODA, COMB). Flue gas leaves at
423 K after the ESP. Reason: `cheme process furnace` refuses gibbsite calcination (core's furnace energy
covers limestone only), so this is the labelled specific-energy fallback. A self-made
enthalpy estimate (reaction 1.81 GJ/t from formation enthalpies, moisture, flue gas and
product sensible heat) gives about 2.5 GJ/t before losses, consistent with the sourced value.
Rejected: rotary kilns (older, about 4 GJ/t). Assumptions: NOx, CO, SO2 and dust not
estimated (D-010).

## D-009 Lists (2026-10-28)
Decision: equipment list with one item per PFD step (19 items, tags linked from the steps) and
a line list with one line per piped stream (32 lines); solids on conveyors are not lines.
No nominal diameters: no property package gives densities or viscosities for these liquors
and slurries. Trains, spares, sizes and materials come at basic engineering. The instrument
list stays empty (no P&ID in scope).

## D-010 Preliminary gate-to-gate LCI (2026-10-28)
Decision: functional unit 1 kg smelter-grade alumina at the gate (`lca/lca.yaml`), every
foreground exchange of the balanced flowsheet; every background declared `missing:` with the
activity it should connect to (10 gaps, never 0, no licensed values); allocation none (one
product; residue a waste, flue gas an emission); boundary keyword cradle-to-gate so that the
raw materials and utilities are not mapped free (as soda-ash-1 D-010). Calciner pollutants
(NOx, CO, SO2, dust) and the liquor tank vents are declared emission exclusions. Overrides in
`lca/mappings.yaml`: natural gas by mass, MP and LP steam as heat delivered. ISIC 2420; CPC not
set (open).
Result (lca/inventory.csv, per kg alumina): bauxite 2.193 kg (wet), quicklime 0.052 kg,
caustic soda 50 % 0.0310 kg (0.0155 kg NaOH), fresh water 0.134 kg, natural gas 0.056 kg,
air 1.110 kg (free); electricity 0.152 kWh, MP steam heat 0.462 kWh, LP steam heat 0.210 kWh,
heat to cooling water 0.567 kWh; bauxite residue cake 0.758 kg (0.530 kg dry solids); CO2 to
air 0.154 kg (fossil), N2 0.853, O2 0.034, H2O 0.778 kg (free). Mass check: inputs 3.5767 kg =
outputs 3.5767 kg (product 1 + residue 0.7585 + flue gas 1.8183); `cheme assess lca
--balance`: mass, element and carbon-origin balances closed. Coverage: "partial screening
carbon footprint" (all backgrounds are gaps).
Cross-check against the IAI 2019 global averages (s. 3.4): 2.685 t bauxite and 1.22 t residue
per t alumina; this case needs less of both because its bauxite is high grade (54.7 % Al2O3,
0.76 % SiO2) and its residue is counted as filter cake solids of this one ore.

## 3. Stream table

`cheme process streams --md` (or `--csv`); every value carries its provenance (A: assumed,
C: calculated by `cheme process propagate`). Balances: 6 blocks and 19 steps closed within
1 kg/h + 0.5 %; reactive steps by extents (SLAKE 115.9, DESIL 3.49, TCA 38.6, DIG 2507.8,
PREC 2427.4, CALC 1213.7, SODA 8.07, COMB 436.3 kmol/h). The script prints the element balance
of the whole plant (Al, C, Ca, Fe, H, N, Na, O, Si, Ti closed to rounding) and the recycle
closure (evaporated spent liquor = liquor to the mill).

Key recycles: spent liquor 2006 t/h (16.1 t/t alumina), seed slurry 853 t/h, washer overflow
210 t/h, residue filtrate 38 t/h, condensate 187 t/h.

## 4. Registry entries missing (for the consolidated PR)

- `chemicals/chemicals.yaml`: alumina (smelter grade; main product), bauxite (gibbsitic),
  quicklime (calcium oxide), sodium hydroxide 50 % solution (caustic soda; may already be
  planned with chlor-alkali-1), natural gas (if not covered by `methane`), bauxite residue
  (red mud) as a waste.
- `lci/mappings.yaml` technosphere entries: bauxite, quicklime, sodium-hydroxide-50 (or a link
  to chlor-alkali-1's dataset), bauxite-residue treatment (residue storage area / landfill of
  alkaline mineral residue); the steam-heat and natural-gas entries already exist and are used
  through `lca/mappings.yaml`.
- `taxonomy/families.yaml`: an `alumina` family (ISIC 2420, NACE 24.42) if alumina should not
  sit under `aluminium`.

## 5. Open inputs and gated steps

- **Calculation maturity** (`cheme maturity`): none. `sourced.boundary` fails because the feed
  flows are solved from the ASSUMED capacity (provenance assumed, not given); 
  `balanced.model-basis` fails because the conversions and splits are ASSUMED specifications.
  Mass, component and element balances close (`balanced.balances-closed` ok). The design
  maturity claim stays `concept` (the lowest the manifest has); cheme warns that it exceeds
  the evidence.
- **Gated by core**: caustic aluminate speciation and gibbsite solubility (core's electrolyte support covers
  aqueous NaCl only; core's solids support needs a single sourced solute) - the A/C values of digestion
  and precipitation stay specifications; gibbsite calcination energy (core's furnace energy covers limestone
  only: `cheme.furnace-unsupported`); energy closure of the blocks (no property package for
  the liquors and solids, `cheme process props --coverage`).
- **Open process inputs** (would replace ASSUMED values): a refinery or licensor liquor
  specification (caustic, A/C, temperatures), the soda loss breakdown (D-005), the bauxite
  moisture and a full assay with organic carbon and carbonate, settling and filtration data,
  a sourced steam balance of a low-temperature refinery (D-007), the calciner emission factors
  (NOx, CO, SO2, dust) from the non-ferrous metals BREF or the IAI LCI averages, flocculant and
  other reagents (not inventoried).
- **Sources to audit**: the ICSOBA 2017 AA22 and 2024 AA05 papers were used at abstract level
  only (PDF text not extractable in this run); Ullmann "Aluminum Oxide" and the EU BREF for
  the non-ferrous metals industries (2017, alumina chapter) were not read.
- **Recommended next stage**: an independent review of this BFD/PFD and LCI; then source the
  liquor specification and soda losses, add a steam balance check against an open refinery
  energy study, map the backgrounds (bauxite, lime, caustic from chlor-alkali-1, natural gas,
  steam, power, residue treatment) and estimate the calciner emissions.

## 6. Source register

| source | locator | access / read status | reuse | used for |
|---|---|---|---|---|
| Zainudeen et al. (2023) Heliyon 9:e19070, doi:10.1016/j.heliyon.2023.e19070 | Table 6 col. Balaya Plateau 2; Table 5 | full text read (Europe PMC) | CC BY 4.0; facts cited | bauxite assay and minerals (D-003) |
| IAI (2022) LCI Data and Environmental Metrics, 2019 data | s. 3.4 (bauxite 2,685 kg, residue 1,220 kg per t alumina, 10-20 % water); s. 3.11.2.2 Table 4 (energy mix, electricity 547 MJ/t); s. 3.11.2.3 (lime ~52 kg/t) | full text read (docx from international-aluminium.org) | IAI copyright; single facts cited | lime dose, electricity, cross-checks (D-003, D-004, D-007, D-010) |
| ICSOBA 2017 AA22 (gas suspension calciner energy) | abstract | search abstract only | facts cited | calciner energy (D-008) |
| ICSOBA 2024 AA05 (digestion waste heat recovery) | abstract / introduction | search abstract only | facts cited | digestion temperature, energy split (D-004, D-007) |
| IAI Bayer refining process overview (alustory) | web page | read in the #178 preparation | facts cited | operation sequence (section 1) |
| NBS tables (Wagman et al. 1982); Robie and Hemingway (1995) | formation enthalpies | recalled, not checked in this run | facts | heats of reaction (process/reactions.yaml), ASSUMED |
