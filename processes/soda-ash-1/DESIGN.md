# Design decisions

One entry per decision: what was decided, why, what was rejected, and what it assumes.
The numbers live in `process/*.yaml`; the stream table is generated: `cheme process streams
--md` (provenance letter per value). Issue: ChemE-as-Code/process-library#177.

Run record of this stage (2026-10-27): library branch `case/soda-ash-1` from `79a7cd4`;
cheme-as-code 0.8.0 (pyDEXPI 2.1.0), Python 3.15.0; DWSIM not used; Cantera not available
(no build for Python 3.15: `uv pip install cantera` failed in CMake), so `cheme process
furnace` runs its specific-energy fallback. Core dependencies as stated in #177 (not
re-audited against core main in this run): core #364 adds an electrolyte route for aqueous
NaCl only, so NH3-CO2-NaCl-NH4Cl-CaCl2 liquors stay unsupported (phase and DWSIM routes refuse
them); core #365 supports one-solute crystallizers and solid separations (not used:
the towers precipitate NaHCO3 from a reciprocal four-salt system, which stays at
imposed yield); core #370 (solid-reaction furnace energy) is gated here by Cantera.

## 1. Route and boundary memo

- **Route**: Solvay ammonia-soda process (synthetic soda ash from NaCl brine and limestone).
  Overall CaCO3 + 2 NaCl -> Na2CO3 + CaCl2, run through NH3 and CO2 cycles. The issue asks to
  keep it apart from trona / natural soda refining, which is a mining and crystallisation
  route with a different feed, energy use and waste; not compared numerically here. The
  Hou (combined soda-NH4Cl) variant, which sells NH4Cl instead of making CaCl2 waste, is
  also out of scope.
- **Boundary** (gate-to-gate): from purified brine, limestone, coke, ammonia make-up, process
  water and air at the battery limit to light soda ash at the calciner outlet. Inside: lime
  kiln, kiln gas washing and compression, slaker, tower-gas scrubber, ammonia absorber,
  carbonating towers, rotary vacuum filter, steam calciner with calciner gas recovery,
  ammonia distiller. Outside: salt mining and brine purification (Ca/Mg softening), steam and
  power generation, cooling tower, product cooling, storage, densification to dense ash,
  CaCl2 recovery, settling ponds.
- **What crosses the boundary**: LST, COKE, AIR, BRINE, NH3, PW (raw materials); SODA
  (product); DSW (distiller waste, wastewater); VENT (off-gas); POWER, LPS (live steam,
  material), HPS (heat), CW (utilities).
- **Comparisons**: only with Solvay cases of the same boundary (light ash, brine purified
  upstream, steam bought in).

## 2. Decisions

## D-001 Route and boundary (2026-10-27)
Decision: classical Solvay process, boundary as in section 1.
Reason: the case notes of #177 name it; it is the synthetic route with explicit CaCl2 waste
and kiln CO2, which the LCI must show.
Rejected: trona refining (another route), Hou process, CaCl2 recovery (a by-product plant).
Assumptions: brine arrives purified (D-003); steam and power from outside the boundary.

## D-002 Capacity, product and hours (2026-10-27)
Decision: 1000 t/d light soda ash (41,667 kg/h), 99.5 wt% Na2CO3 and 0.5 wt% NaCl, 8000 h/a,
generic site.
Reason: a normalisation basis for a per-kg inventory, not a plant claim (#177). ASSUMED.
Rejected: dense ash (needs the rehydration and drying plant; outside the boundary).

## D-003 Brine (2026-10-27)
Decision: purified brine 26.0 wt% NaCl at 293 K, 300 kPa(a).
Reason: near saturation (NaCl solubility about 35.9 g per 100 g water at 20 C, i.e. 26.4 wt%;
standard handbook value), a little below to avoid salting out. ASSUMED. Ca/Mg removal is
upstream and part of the brine background (lca.yaml).

## D-004 Lime kiln (2026-10-27)
Decision: mixed-feed shaft kiln, limestone and coke charged together; degree of calcination
0.95; lime out at 363 K, kiln gas at 393 K; air excess 1.10; heat use 4.0 GJ/t lime. Kiln basis
in `process/furnaces.yaml`: `cheme process furnace` with `method: specific-energy` (the
labelled fallback), because the energy-balance method needs Cantera, which cannot be
installed for this Python 3.15 build. Result: 29.5 MW heat input -> 3648 kg/h coke at an
LHV of 29.11 MJ/kg (87.6 kg/t soda ash).
Reason: mixed-feed shaft kilns give the CO2-rich kiln gas (here about 37 mol%) the towers
need; the heat use is mid-range of the lime BREF's typical range for this kiln type (3.4-4.7
GJ/t, JRC 2013 Table 2.23, via cheme's packaged table). Combustion is complete (C + O2), as
the furnace module assumes. All ASSUMED.
Gated: the furnace energy closure (core #370 route) waits for Cantera; then switch to
`method: energy-balance` with the same fuel, air and losses, and compare.

## D-005 Limestone and coke (2026-10-27)
Decision: limestone 96 % CaCO3, 3 % SiO2 (standing for all insolubles), 1 % moisture; coke
89 % C, 9 % ash (as SiO2), 2 % moisture; H, N and S of the coke neglected; LHV 29.11 MJ/kg
from the carbon (32.76 MJ/kg C from the CO2 formation enthalpy) less the moisture.
Reason: no quarry assay or coke analysis exists. ASSUMED. Consequence: SO2 is not estimated
(D-010), and MgCO3 of a real limestone is not carried.

## D-006 Material balance model (2026-10-27)
Decision: an independent sequential balance, `scripts/solvay_balance.py`, sets every stream;
the flowsheet carries its values as ASSUMED and cheme checks them (block, step and reactive
element balances by extents). Component basis: dissolved NH3 and CO2 as molecules; "free"
ammonia of the mother liquor as NH3 + CO2 (CO2/free NH3 = 1, ammonium bicarbonate); fixed
ammonia as NH4Cl. ASSUMED parameters, all to be replaced by sourced or owner data:
- sodium utilisation of the towers 0.73 (NaHCO3 precipitated / NaCl in), the CARB conversion;
  the Solvay literature reports roughly 70-75 %, limited by the reciprocal salt equilibrium
  (to be located in the Ullmann chapter or the LVIC-S BREF; not read in this run);
- NH3/NaCl 1.10 mol/mol in the ammoniated brine; 1 % of its NH3 leaves with the tower gas and
  is scrubbed back except 0.5 kg/t to the vent; 1.5 kg/t NH3 left in the distiller waste;
  make-up = losses (2.0 kg/t);
- washed cake 15 wt% liquid, 0.3 wt% NH3 (as NH4HCO3), NaCl as the product's 0.5 %;
  NH4Cl fully washed out; wash water 0.30 kg/kg dry cake; no NaHCO3 lost in the filtrate;
- lime 5 % over the NH4Cl stoichiometry; milk of lime 20 wt% Ca(OH)2; slaking complete;
- calciner gas condenser at 313 K: the CO2 keeps water at saturation, NH3 with an equimolar
  CO2 goes to the weak liquor; distiller gas H2O/NH3 0.6 mol/mol after its condenser;
- all kiln and calciner CO2 goes to the towers; the CO2 not absorbed leaves in the vent.
Result per t soda ash: brine 5.78 t (NaCl 1.50 t), limestone 1.08 t, coke 87.6 kg, ammonia
2.0 kg, process water 3.48 t, LP steam 1.88 t; distiller waste 11.19 t (CaCl2 1.04 t, NaCl
0.40 t), vent 1.11 t with 306 kg CO2. Plant element balances close to rounding (worst unit
7e-12 kmol/h; mass to the molar-mass rounding, < 1 kg/h).
Rejected: a crystallizer (core #365) for the towers; it treats one solute in one solvent, and
NaHCO3 here precipitates from a four-salt system whose yield is the sodium utilisation.
Sanity checks against independent figures (cross-checks only, not inputs): vented CO2 200-300
kg/t (EMEP/EEA air pollutant emission inventory guidebook, chapter 2.B.7 soda ash): ours, 306
kg/t, is just above, with all kiln gas going through the towers; salt 1.7 t/t and limestone
1.4 t/t (USGS Minerals Yearbook 1992, soda ash): ours are lower (1.50, 1.08) because of the
assumed 73 % utilisation, 96 % CaCO3 and only 5 % excess lime, which are optimistic; energy
9.7-13.6 GJ/t (a literature review found in the search, figure not traced to its primary
source): ours is about 9.7 GJ/t (kiln 2.55 GJ/t, LP steam about 4.3, HP steam heat 2.43,
power 0.4), at the low end.

## D-007 Thermodynamic and reaction model basis (2026-10-27)
Decision: no property package and no simulation. Reactions (`process/reactions.yaml`) are
stoichiometric with specified conversions (a sourced-range conversion model, not kinetics);
heats of reaction from standard formation enthalpies (NBS tables, Wagman et al. 1982),
aqueous species at infinite dilution, recalled for this concept stage and marked ASSUMED
until checked against the table.
Reason: the liquors are concentrated electrolytes (NaCl, NH4Cl, NH4HCO3, CaCl2 with NH3 and
CO2): neither the phase routes nor DWSIM may compute them (core #364 covers aqueous NaCl
only); solids have no package. `cheme process props --coverage` covers no stream.
Evidence to gather next (`process/reaction-evidence.yaml`, skill reaction-evidence-search):
NaCl-NH4Cl-NaHCO3-NH4HCO3 solubility data (sodium utilisation vs temperature and NH3/CO2
ratio), the NH3-CO2-H2O VLE of the absorber and distiller (an electrolyte NRTL or extended
UNIQUAC model with sourced parameters), and plant figures from the LVIC-S BREF soda ash
chapter.

## D-008 Utilities and duties (2026-10-27)
Decision: duties from a lumped enthalpy balance in the same script (formation enthalpies,
constant heat capacities: liquor 3.6 kJ/(kg K), solids 1.1 kJ/(kg K)); compressors adiabatic,
ideal gas, isentropic efficiency 0.75, 101 -> 350 kPa(a), aftercoolers removing the work;
auxiliary power 35 kWh/t; calciner losses 10 %, distiller losses 5 %. Utilities: cooling water
298/308 K; LP steam 450 kPa(a) as live steam into the distiller (a material feed, solved from
the distiller heat balance: 78.5 t/h); HP steam 3000 kPa(a) to the calciner (28.2 MW, condensate
returned); electric drives. Kiln, slaker and distiller exchange no heat with a utility
(`process/simulation.yaml` declares them adiabatic for the boundary check). All ASSUMED.
Gated: `cheme process energy` evaluates no energy balance (no stream enthalpies: no property
package for electrolytes and solids, core #364/#365); the duties stay a script estimate.

## D-009 Lists (2026-10-27)
Decision: one equipment item per PFD step, one line per material stream; no trains, spares,
sizes, design conditions or materials yet; line DN not sized (no densities, D-007).

## D-010 Preliminary gate-to-gate LCI (2026-10-27)
Decision: `lca/lca.yaml` with the functional unit 1 kg light soda ash; every foreground
exchange from the flowsheet terminals (stream ids in each `source`); no background mapped:
each feed, utility and the distiller waste is `missing:` with the activity it should link to.
`boundary: cradle-to-gate` because cheme's `gate-to-gate` maps every feed free, which would hide
the raw materials; the result is therefore a partial screening footprint with every
background a gap. Vent CO2 is an elementary emission to air (fossil: geogenic carbonate and
coke carbon); vent NH3 an elementary emission to air (no GWP); N2, O2 and H2O of the vent are
free. The distiller waste is a waste to settling ponds; its dissolved CaCl2, NaCl and NH3
reach water through that treatment, whose dataset must carry them (composition in stream S24
and lca/dataset.yaml). Kiln CO, NOx, SO2 and dust are declared excluded (not estimated), not
zero. No allocation (one product). No construction, transport or end of life at this stage.
Open: lime BREF emission ranges for the kiln pollutants, an elementary representation of the
CaCl2/NaCl discharge, ISIC/CPC classification, site and grid.

## 3. Stream table

Generated: `cheme process streams --md` (not copied here).

## 4. Registry entries missing in `chemicals/chemicals.yaml` (for the consolidated PR)

sodium-carbonate (with a grade light-soda-ash), sodium-chloride (or a brine grade), limestone
or calcium-carbonate, coke, ammonia, calcium-chloride (distiller waste), and as internal
intermediates calcium-oxide, calcium-hydroxide, sodium-bicarbonate, ammonium-chloride. Until
then `process.yaml` lists only the existing slugs (water, air, wastewater, carbon-dioxide,
electricity, steam, cooling-water).

## 5. Open inputs and gated steps

- Sourced values for every D-006 parameter (sodium utilisation, NH3 ratio, cake moisture,
  losses, excess lime) with exact locators; the Ullmann chapter and the LVIC-S BREF are leads
  not read in this run.
- Kiln energy balance: needs Cantera in cheme's interpreter (D-004).
- Electrolyte thermodynamics (core #364) for the absorber, towers and distiller; the
  reciprocal-salt equilibrium for a predicted sodium utilisation.
- Energy closure in core (stream enthalpies of liquors and solids).
- Site, steam and power supply (decides the backgrounds), coke sulfur and kiln emissions.
