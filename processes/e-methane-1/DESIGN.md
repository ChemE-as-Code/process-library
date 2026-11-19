# Design decisions

e-Methane (synthetic natural gas), concept stage (issue ChemE-as-Code/process-library#520,
coverage item `e-methane`, provisional rank 127). One entry per decision: what was decided, why,
what was rejected, and what it assumes. The numbers live in the YAML files and in
`scripts/balance.py`; this file keeps the reasons.

## Source register

The sources read for this entry (SRC-1, SRC-2) and the packages queried for property values
(SRC-3 to SRC-6); facts and numbers are restated in our own words with their locator. No table,
figure or text is copied.

| id | source | access | what it gives here |
|---|---|---|---|
| SRC-1 | Moers, F.; Schlautmann, R.; Gorre, J.; Leonhard, R. (2020) *D5.9 Final report on evaluation of technologies and processes*, STORE&GO (EU Horizon 2020, grant 691797), DVGW; storeandgo.info, deliverables 2020 (PDF, 92 pages, read 2026-11-19) | public deliverable (dissemination level PU; facts only) | Section 2.1 (pp. 10-11): the Falkenhagen plant: hydrogen from existing alkaline electrolysers, up to 210 m3/h (STP) to the methanation, about 1 MW; CO2 delivered liquid from a bioethanol plant, fed stoichiometrically (up to 52.5 m3/h); two stages, the feed compressed up to 14 bar; a multi-tube honeycomb reactor cooled by thermal oil on the shell side, the outlet temperature set by the oil flow; effluent cooled against the feed, then an air cooler to 60 C and a water cooler to 10 C, a liquid separator; a polishing reactor (oil-cooled tube bundle with catalyst pellets, isothermal); two coolers to 10 C and a separator; two parallel drying vessels; the existing compression unit to the grid. Table 2-1: 1186 h of operation. Section 3.1 (p. 22): injection into a transport grid above 45 bar with below 2 vol-% H2 and 2 vol-% CO2; the methanation evaluated between its feed and the product before the last step. Section 4.1 and Table 4-1 (pp. 33-35): the 200 m3/h H2 point (9.0045 kmol/h, 95 % load): H2 in 708/715 kW, SNG 549/557 kW (CH4 only, HHV), 41 kW electricity, GHSV 732 1/h honeycomb and 500 1/h overall as built, honeycomb conversion 92 %, overall H2 conversion 99/100 %, 99 vol-% CH4, heat used 86/103 kW at 184 C, methanation efficiency 77.5/78.0 % (measured/ASPEN); the measured stoichiometry 4.4 judged a measurement error; 99.8 % conversion in the ASPEN model (p. 33). Section 4.1.1 (pp. 36-38): start-up from hot standby with hydrogen circulated, off-spec gas flared (about 33 m3), flared until at least 96 vol-% CH4 and at most 2 vol-% H2; load changes 40-100 %. Section 4.1.2 and Table 4-2 (pp. 38-39): per m3 of SNG 22.4 kWh electrolyser, 0.8 kWh methanation, 0.1 kWh injection, 1.0 kWh CO2 conditioning (biogas, not built), 1.7 kWh usable heat; CO2 compression is needed only if the hydrogen comes at reaction pressure. Executive summary (pp. 7-8): the 5 MW scale-up at 8000 h/a; one reactor stage would do if the grid allowed more hydrogen. Appendix 8.1 (p. 81): efficiency definitions (HHV, methane only). Appendix 8.4 (p. 85): the ASPEN model: stoichiometric ratio 4 with the measured 200 m3/h H2, isothermal reactors at about 350 C (honeycomb) and 240 C (fixed bed), heat losses neglected, electric heating only for the fixed bed's feed |
| SRC-2 | van Leeuwen, C.; Zauner, A. (2018) *D8.3 Report on the costs involved with PtG technologies and their potentials across the EU*, STORE&GO (grant 691797), University of Groningen; storeandgo.info (PDF, 51 pages, read 2026-11-19) | public deliverable (dissemination level PU; facts only) | Section on methanation (pp. 19-21): the three reactions (CO methanation, reverse water-gas shift, Sabatier) after Xu and Froment and Zoss et al.; nickel the usual catalyst, which needs a feed free of hydrogen sulphide; 200-550 C, strongly exothermic, temperature control the key issue; biological methanation at 20-70 C. Falkenhagen (p. 21): two stages, a honeycomb and a wall-coated reactor in parallel (one used at a time), a fixed bed for polishing, nickel in all. Compressors (p. 27): Falkenhagen's grid at 48 bar, the existing hydrogen compressors reused. CO2 storage (p. 25): a 30 m3 liquid CO2 tank at 16-20 bar and -24 C, 11 days at full load, delivered by truck |
| SRC-3 | The `chemicals` 1.5.2 and `thermo` 0.6.1 packages (Caleb Bell, MIT) through `cheme chemistry thermo`: ideal-gas formation enthalpies from the Active Thermochemical Tables (`ATCT_G`), standard entropies from the CRC Handbook table packaged as `heat_capacity.CRC_standard_data` (`CRC`), heat capacities fitted to thermo's `TRCIG` and `HEOS_FIT` methods over 280-1500 K (CH4, H2) and 250-1600 K (CO, CO2, H2O), critical constants packaged as `miscdata.heos_data` (`HEOS`); taken as printed in hydrogen-1's process/materials.yaml for CH4, H2, CO, CO2 and H2O | open-source packages; single values, facts only, with their source; not open data (library ADR 0037). The CRC Handbook, the TRC tables, the ATcT and REFPROP were not read here | dHf_298, S_298, the cp_R coefficients, Tc, Pc and omega in process/materials.yaml; every enthalpy, heat of reaction and equilibrium constant of the flowsheet, `cheme process reactors` and scripts/balance.py (D-004 to D-009) |
| SRC-4 | Wagner, W.; Pruss, A. (2002) The IAPWS formulation 1995 for water, J. Phys. Chem. Ref. Data 31, 387, as implemented in the `chemicals` package 1.5.2 (`iapws95_Psat`, `iapws95_dPsat_dT`, `iapws95_rhol_sat`, `iapws95_rhog_sat`) | open formulation; package values, single facts with their source (ADR 0037) | the vapour pressure of water at 283.15 K (1.228 kPa) for the knock-outs' saturated gas, and its heat of vaporisation by Clausius-Clapeyron for the coolers' duty (D-007) |
| SRC-5 | Span, R.; Wagner, W. (1996) An equation of state for carbon dioxide, J. Phys. Chem. Ref. Data 25, 1509, as implemented in CoolProp 8.0.0 (Bell et al., MIT) | open-source package; single values (ADR 0037); the paper not read here | the CO2 enthalpies at 15.3 MPa and 303.15 K and at 1.53 MPa and 313.15 K, and the isenthalpic let-down temperature (about 245 K) (D-003) |
| SRC-6 | The ChemSep Henry's law parameters (ChemSep, Kooijman and Taylor) as packaged in `thermo` 0.6.1 (`IPDB`, table "ChemSep Henry": ln H/Pa = A + B/T + C ln T + D T, the gas in water) | open-source package; single values with their source (ADR 0037); the ChemSep database itself not read here | Henry's law constants at 283.15 K, about 1.04e8 Pa for CO2, 2.89e9 Pa for CH4 and 3.5e10 Pa for H2 (scripts/balance.py prints them): the gases dissolved in the knock-outs' condensate (D-007, L-4) |

Read but not used for numbers: the issue's other leads were not opened. Not read, so not used:
the STORE&GO deliverables D2.4, D2.5 and D5.5 that SRC-1 cites for the plant's details (D5.5 is
confidential); Xu and Froment (1989), Zoss et al. (2016) and Goetz et al. (2016), cited by
SRC-2 for the reactions and the catalyst.

## Core and library models checked

- **Core's reactor models** (`cheme schema process-flowsheet`, core 1.13.0): `reactor:
  equilibrium` and `gibbs` are checked by `cheme process propagate`, not solved ("only checked,
  never solved" for R-102 without its outlet), and `pfr` needs rate laws. Both reactors are
  conversion steps: R-101 at the measured conversion, R-102 at the equilibrium conversion that
  scripts/balance.py solves from the same materials data on the same feed (the script is the
  source of that conversion, not a cross-check of core); `cheme process reactors` reports ln K
  and ln(Q/K) at both outlets (D-004, D-005, L-1, L-2).
- **Core's adsorption model** (`cheme process adsorption`): an equilibrium TSA cycle from sourced
  isotherms; no isotherm of water on a drying adsorbent was read, so the dryer is a component
  separator (D-008, L-5).
- **Library producers**: hydrogen-1 (steam methane reforming with PSA) and chlor-alkali-1
  (hydrogen as a co-product of chlorine) make hydrogen; no entry makes it by water electrolysis.
  carbon-capture-1 makes dense-phase CO2 (15.3 MPa, 99.95 mol%); bioethanol-1 and biogas-1 vent
  their CO2 as emissions, not products. e-fuels-1 takes hydrogen and CO2 at the gate with both
  as gaps (D-003, D-011).

## D-001 Route: two-stage catalytic methanation on nickel, the Falkenhagen design (2026-11-19)

Decision: the catalytic two-stage methanation of the STORE&GO demonstration at Falkenhagen
(SRC-1 section 2.1): an oil-cooled honeycomb reactor, cooling with water knock-out, an oil-cooled
fixed-bed polishing reactor, cooling and knock-out, adsorption drying and compression into a
transport grid. Hydrogen and CO2 come to the gate (D-003); the electrolysis and the CO2 capture
are outside the boundary.

Reason: the one design read with measured performance at a stated operating point beside a
simulation of the same point (SRC-1 Table 4-1), so the model can be checked against both; a
complete sequence of units with temperatures, pressures and the place of every cooler and
separator; grid-quality product (99 vol-% CH4) without a gas separation step. The reactions and
the catalyst are confirmed by an independent STORE&GO deliverable (SRC-2).

Rejected:
- **Biological methanation** (Solothurn, SRC-1 executive summary, section 3.1 and appendix 8.4):
  archaea in a stirred bubble column at 62 C, product at 10 bar, with a PEM electrolyser; its heat comes at a temperature that
  SRC-1 does not count as usable, the ASPEN model assumes its CO2 conversion (98 %) instead of a
  measured one, and its product needs a gas separation; the variant is listed in coverage.yaml for
  a later entry.
- **Milli-structured reactor with membrane recycle and liquefaction** (Troia, SRC-1): the product
  is LNG, the CO2 comes from direct air capture inside the heat integration, and its ASPEN model
  rests on engineering data, not measurements (appendix 8.4).
- **One reactor stage**: SRC-1 (executive summary, p. 8) says it would suffice only if the grid
  accepted more hydrogen; with the 2 vol-% limit the polishing stage is needed (D-005).
- **Adiabatic fixed-bed cascades with gas recycle** (the large-scale coal-to-SNG layout): no open
  design source was read for this entry.
- **RWGS and Fischer-Tropsch, methanol**: other products (e-fuels-1, methanol-1).

Assumptions: the Falkenhagen design scaled 1:1 (D-002); no CO2 conditioning in the boundary
(the CO2 arrives clean and dry, D-003).

## D-002 Capacity and operating hours (2026-11-19)

Decision: SRC-1's measured point, 200 Nm3/h hydrogen (9.0045 kmol/h, 95 % of the unit's load)
with stoichiometric CO2 (H2/CO2 = 4, 2.2511 kmol/h), over 8000 h/a: 36.13 kg/h of SNG, 289 t/a.

SRC-1 states the hydrogen as 9.0045 kmol/h and 200 m3/h (STP) together; the molar flow is
taken, which is 201.8 Nm3/h as ideal gas at the flowsheet's normal conditions (all Nm3 of this
entry are ideal-gas volumes, 22.414 m3/kmol).

Reason: at this point SRC-1 gives every indicator, measured and simulated (Table 4-1), so the
model is checked at the design point itself. The stoichiometric ratio is SRC-1's ASPEN basis
(appendix 8.4): the measured 4.4 is judged a measurement error there, since 99 vol-% CH4 needs a
ratio near 4 (p. 33). 8000 h/a is SRC-1's operating basis for its scale-up and costs (executive
summary); the demonstration itself ran 1186 h (Table 2-1).

Rejected: the 5 MW scale-up of SRC-1's cost study (no flowsheet or indicators given for it; a
linear scale-up of this design would change no specific number of the LCI); the 210 Nm3/h
maximum (no indicators given there); part load (SRC-1 shows the product quality held at
40-100 % load, but the indicators are for this point only).

Assumptions: 8000 h/a full-load equivalent, ASSUMED for a plant with a steady hydrogen supply
(an electrolyser on variable power would run fewer hours or need hydrogen storage, outside the
boundary).

## D-003 Feeds: dry electrolytic hydrogen at the gate, CO2 from carbon-capture-1's pipeline (2026-11-19)

Decision: hydrogen dry at 303.15 K and 120 kPa(a) from an electrolysis plant (ASSUMED, an
atmospheric alkaline electrolyser like Falkenhagen's, with its own dryer); CO2 from a dense-phase
pipeline at 15.3 MPa and 303.15 K, the product of the library's carbon-capture-1 (99.95 mol% CO2,
500 ppm water), let down to 1.53 MPa(a) through a heater E-100 and a pressure control valve. The
heater takes 6.78 kW from the thermal oil (scripts/balance.py, SRC-5), so the gas leaves at
313.15 K; an isenthalpic let-down alone would end at about 245 K, in the two-phase region.

Reason: the task links library producers where they exist. carbon-capture-1 is the library's
CO2 product, and a plant at a CO2 pipeline needs no CO2 compressor; its CO2 comes from an
ammonia plant's stripper vent (natural gas reformed upstream, so free of hydrogen sulphide, which
the nickel catalyst cannot take, SRC-2). No library entry makes electrolytic hydrogen.

Rejected:
- **Liquid CO2 by truck from a bioethanol plant** (Falkenhagen as built, SRC-1 section 2.1, SRC-2's
  30 m3 tank): bioethanol-1 vents its CO2 (no liquefied product in the library), so the link
  would be a gap; the tank and vaporiser would add nothing to the methanation.
- **CO2 separated from biogas** (SRC-1's chain evaluation, Table 4-2: 1.0 kWh/m3 SNG): biogas-1
  vents its membrane off-gas; a capture unit on it is not in the library.
- **hydrogen-1** (steam methane reforming): fossil hydrogen would make the product fossil methane
  with extra steps; the shared `hydrogen` market is merchant hydrogen of the same kind.
- **chlor-alkali-1's hydrogen**: electrolytic, but a co-product of chlorine whose burden follows
  that plant's allocation and whose amount follows chlorine demand, not a supply for power-to-gas.

Assumptions: the hydrogen is dry and pure (ASSUMED; trace oxygen from the electrolyser is not
counted, L-4); the CO2's 500 ppm water is carried, its other traces are not.

## D-004 Honeycomb reactor R-101: 92 % conversion at 623 K (2026-11-19)

Decision: R-101 as a conversion reactor of the Sabatier reaction, 92 % of the CO2 converted,
isothermal at 623.15 K (about 350 C, SRC-1 appendix 8.4) and 1460-1490 kPa(a); the feed
preheated to 523.15 K (ASSUMED light-off of the nickel catalyst) against the effluent (E-101,
20.8 kW). Core writes its heat to the thermal oil: 93.03 kW (Q3). Reaction pressure 1500 kPa(a)
at the mixer: SRC-1's "up to 14 bar" read as gauge (ASSUMED).

Reason: 92 % is the honeycomb conversion measured and simulated at this point (SRC-1 Table
4-1). `cheme process reactors` gives ln(Q/K) = -4.61 at the outlet: the reactor is far from its
equilibrium at 623 K, as expected of a short, cooled reactor run at a high space velocity (732
1/h as built, about 0.34 m3 of honeycomb for the 250 Nm3/h of feed); an equilibrium model would
overstate its conversion.

Rejected: `reactor: equilibrium` for R-101 (contradicts the measured 92 %); `reactor: pfr` (no
kinetics of the coated honeycomb read; core's fixed-bed model needs rate laws, L-1); an
adiabatic reactor (Falkenhagen's is cooled; the adiabatic rise would be several hundred kelvin,
D-010).

Assumptions: isothermal at the outlet temperature (SRC-1's ASPEN assumption); the 523.15 K inlet
and the pressure drops (10-30 kPa per item) ASSUMED; the wall-coated reactor that SRC-2 mentions in
parallel is a spare, not modelled.

## D-005 Polishing reactor R-102: ideal-gas equilibrium at 513 K (2026-11-19)

Decision: after the first knock-out the gas is heated electrically (E-104, 7.21 kW, as at
Falkenhagen, SRC-1 appendix 8.4) to 513.15 K (about 240 C) and reacts in an isothermal
oil-cooled fixed bed to its ideal-gas equilibrium at 1400 kPa(a). scripts/balance.py solves the
equilibrium of the Sabatier and reverse water-gas shift reactions from the materials' data
(SRC-3): 98.94 % of the remaining CO2 converted and 0.4 ppm CO; the flowsheet carries this as a
conversion step of the Sabatier reaction at that conversion (core's propagate solves
conversion steps, not equilibria; L-2), whose heat core writes to the oil (8.50 kW, Q5). The
script solves the equilibrium on the same feed core propagates (the feeds given to six
decimals, the knock-outs' recoveries to ten), and `cheme process reactors` confirms
ln(Q/K) = 0.0001 at the outlet: at equilibrium. Leaving the CO out of the step moves the
quotient by about 0.001 only.

Result: 99.77 % of the hydrogen converted overall, SNG with 98.99 mol% CH4, 0.93 mol% H2 and
0.08 mol% CO2 (SRC-1: 99 vol-% measured, 99.8 % conversion in the ASPEN model, p. 33), inside the
grid's 2 vol-% limits for H2 and CO2 (SRC-1 section 3.1). The CO2 that dissolves in the first
knock-out's condensate (D-007) leaves the second stage's feed with a little excess hydrogen
(H2/CO2 = 4.08), which is why the product holds more H2 and less CO2 than a stoichiometric feed
would give.

Reason: the water removed before the second stage shifts the equilibrium, and at 240 C it lies
far on the methane side; the measured product purity (99 vol-% CH4) agrees with reaching it.

Rejected: an approach temperature (none read); Peng-Robinson fugacities (at 1.4 MPa and 513 K the
gas is near ideal; core's PR option applies to its equilibrium reactor, not to a conversion
step, L-3); the RWGS reaction in the step (its CO, 0.4 ppm, is below what the balance carries).

Assumptions: equilibrium reached (ASSUMED, consistent with the measured purity); no carbon
deposition or higher hydrocarbons (L-2).

## D-006 Compression and electricity (2026-11-19, revised 2026-11-20)

Decision: the hydrogen alone is compressed, from 120 to 1530 kPa(a) in two stages with an
intercooler and an aftercooler to 313.15 K (K-101, isentropic efficiency 0.70 ASSUMED, the second
stage's suction at 313.15 K: 28.14 kW, W1; the coolers reject 27.41 kW, the work less the
hydrogen's warming from 303.15 to 313.15 K, Q0); the CO2 arrives above the reaction pressure
(D-003). The electricity is computed part by part in scripts/balance.py: K-101, the electric
preheater E-104 (7.21 kW, W3), and the balance of plant W2, 6.42 kW: the chiller of the 10 C
coolers (8.16 kW of cold, E-103 and E-105's chilled-water part, at a COP of 3.0 ASSUMED: 2.72
kW) and the fans of the air coolers and the pumps of the oil and cooling circuits (0.02 kW per
kW of the 184.9 kW rejected to air, ASSUMED: 3.70 kW). The methanation unit takes 41.77 kW
(0.822 kWh/Nm3 SNG). Injection: 0.1 kWh per Nm3 of SNG (SRC-1 Table 4-2), 5.08 kW (W4). In all
46.85 kW, 0.922 kWh/Nm3 SNG, 1.297 kWh/kg.

Check against the source: SRC-1 measured 41 kW for the methanation unit as built (Table 4-1,
0.8 kWh/m3 SNG), where the mixed educt gas was compressed to 14 bar (section 2.1), and gives
0.7 kWh/m3 (35.6 kW here) for the unit with a changed compressor configuration (section 4.1.2,
Table 4-2, p. 39). The 41 kW is not carried over: it belongs to the other configuration, and
under this entry's assumptions (120 kPa(a) suction, efficiency 0.70) the as-built mixed-feed
compressor alone would take 34.79 kW, which with E-104 already exceeds the measured total. So the
entry's compressor assumptions are conservative against the plant, and its 41.77 kW lies 17 %
above the source's figure for a changed configuration.

Reason: compressing only the hydrogen avoids letting the CO2 down and recompressing it; SRC-1
(section 4.1.2) names a different compressor configuration as an optimisation. Computing each
consumer keeps the electricity tied to this design's own duties instead of to a measurement of
a different configuration.

Rejected: subtracting the computed compressor and preheater from the measured 41 kW to get the
balance of plant (the first version of this entry: the measurement is of the mixed-feed
compressor, so the residual had no physical basis); compressing the mixed feed (as built, SRC-1
section 2.1: the educt gas compressed; with the CO2 from a pipeline it would waste the
pipeline's pressure); a pressurised electrolyser (would remove K-101, 28.1 kW, 0.55 kWh/Nm3; a
sensitivity, not this case, since the hydrogen supply is not chosen).

Assumptions: ideal gas with constant heat capacity per stage; stage outlet up to about 510 K;
the efficiency, the suction pressure, the chiller's COP and the fans' and pumps' specific power
ASSUMED (no source read for them).

## D-007 Cooling and water knock-out (2026-11-19, revised 2026-11-20)

Decision: the honeycomb reactor's effluent holds 58 mol% water (4.14 kmol/h) at 1440 kPa(a), so
its dew point is 445.5 K (IAPWS-95, SRC-4). Giving the feed its 20.8 kW (Q2), E-101's hot side
cools it from 623.15 K to 442.3 K, below the dew point: S8 leaves two-phase, 0.67 kmol/h of the
water condensed (molar vapour fraction 0.906). An air cooler E-102 then takes the effluent to
333.15 K (49.19 kW, condensing 3.43 kmol/h, so 99 % of the water is liquid at its outlet) and a
chilled-water cooler E-103 to 283.15 K (6.29 kW) (SRC-1 section 2.1: 60 C and 10 C); the water is
knocked out in V-101 at 1420 kPa(a). After R-102 the gas is cooled to 283.15 K again (E-105:
9.14 kW by air to 333.15 K, 1.87 kW by chilled water) and knocked out in V-102 at 1380 kPa(a).
The gas leaves each drum saturated with water (IAPWS-95): 0.0865 mol% water, or 0.0620 % and
0.573 % of the water entering. The heat removed: 55.48 kW (Q4) and 11.02 kW (Q6), sensible heat
and the heat of condensation. The condensate holds the gases dissolved at the drums' pressure
by Henry's law (SRC-6; with the outlet gas's partial pressures): 0.149 kg/h CO2 (1.9 % of the
CO2 entering V-101), 0.025 kg/h CH4 and a trace of H2. It is let down to an atmospheric
condensate tank T-101, where these gases are released to air (S20, 0.174 kg/h, counted as an
emission in the LCI, D-011); the degassed condensate, 80.9 kg/h with the dryers' water, goes to
treatment.

Reason: SRC-1's sequence; removing the water between the stages is what lets the second stage
reach grid quality. Most of the condensation happens in the air cooler at about 60 C, which
SRC-1 (p. 39) names as a heat source a user could take (0.9 kWh/m3 in its Table 4-2); there is
no such user at this generic site (D-009).

Rejected: reusing the condensate as electrolyser feed water (attractive, about 2.2 kg per kg SNG
against the electrolyser's 9 kg of water per kg H2 by stoichiometry, but the electrolyser is
outside the boundary; an option for a later case); the effluent as a single vapour phase after
E-101 (the first version of this entry: an ideal-gas enthalpy with all the water as vapour gave
344.9 K, about 100 K below the dew point, which cannot exist and put most of the cooling in the
wrong exchanger); stripping the condensate with air before the tank (a further emission point,
not a smaller emission).

Assumptions: the coolers' outlet temperatures are SRC-1's; the gas-liquid split at each point is
the water's saturation (Raoult/Dalton) with the gases' heat of solution neglected; Henry's law at
the drums' temperature with the gas's partial pressures, no salting or carbonic acid
dissociation, equilibrium reached; all dissolved gas released (ASSUMED: at the tank or later at
the wastewater treatment, to air either way); the chiller's power in W2.

## D-008 Drying and grid injection (2026-11-19)

Decision: two adsorption dryers (one adsorbing, one regenerating, SRC-1 section 2.1) remove the
water left after V-102 (0.036 kg/h) to the grid's dew point; the regeneration is a closed loop
(ASSUMED) whose condensed water joins the condensate. The dry gas is compressed to 5000 kPa(a)
(above SRC-1's 45 bar and SRC-2's 48 bar grid) at 0.1 kWh/Nm3 (SRC-1 Table 4-2); its coolers
take the work less the gas's warming from 283.15 to 313.15 K, 4.41 kW to air (Q9).

Reason: SRC-1's sequence and figure; at Falkenhagen the existing hydrogen injection compressors
were reused (SRC-2).

Rejected: delivering at the reactor pressure to a distribution grid (Solothurn's case, 5 bar,
SRC-1 section 3.1): Falkenhagen's grid is a transport grid.

Assumptions: the dryer's regeneration heat and losses not counted (L-5); odorisation and metering
outside the boundary.

## D-009 Heat: thermal oil, no heat user at the generic site (2026-11-19)

Decision: both reactors are cooled by one thermal oil circuit (H-301) at about 180-200 C. It takes
101.53 kW (Q3 + Q5), gives 6.78 kW to the CO2 heater and rejects the rest, 94.75 kW (1.86 kWh per
Nm3 SNG), in an oil air cooler (Q8). No heat is exported in this case.

Reason: the site is generic, and SRC-1 (section 4.1.2) notes that using the heat needs a heat
user at the location. The rejected heat is what a user could take: SRC-1 measured 86 kW used at
184 C (1.7 kWh/m3) and simulated 103 kW without the oil circuit's losses; 94.7 kW lies between.

Rejected: a heat co-product in the LCI (no user chosen; it would need an allocation or a
substitution the case does not support); heating the polishing reactor's feed with oil instead
of electricity (SRC-1's design is electric; an option that would save 7.2 kW).

Assumptions: the oil circuit's losses included in Q8; the start-up oil heater not counted.

## D-010 Hazards (concept)

Screening only, for a later HAZOP; no safeguard is credited here.

- **Hydrogen**: flammable over a wide range and prone to leak; K-101 and the feed lines handle
  9 kmol/h at up to 1.53 MPa. Area classification, leak detection and a nitrogen purge before
  start-up and after shutdown belong to the basic design.
- **Runaway of the methanation**: `cheme process reactor-hazards` (core 1.13.0, screening) gives an
  adiabatic temperature rise of 1014 K for R-101's fresh feed and 229 K for R-102's on the
  conversion model's heat (equilibrium would stop the rise lower, at a few hundred degrees above
  the inlet, which the screening does not model). A loss of oil flow or a feed upset therefore
  overheats the honeycomb tubes and sinters the catalyst within the reactor's residence time.
  Candidate safeguards: high-temperature trips of R-101 and R-102 that stop both feeds, low
  oil-flow trip, the H2/CO2 ratio controller with a high-ratio alarm; no MTT or TD24 applies to a
  gas-phase catalytic reactor (the gate's `hazard:` stays empty).
- **Off-spec product**: SNG with more than 2 vol-% H2 must not reach the grid; at Falkenhagen it
  was flared during start-up until at least 96 vol-% CH4 and at most 2 vol-% H2 (SRC-1 section
  4.1.1, footnote). An analyser on S18 with a switch to a flare is needed; the flare is not
  drawn at concept.
- **CO2**: the 15.3 MPa pipeline let-down; a failed-open control valve overpressures E-100 and the
  mixer (relief on the low-pressure side); cold CO2 if E-100's heat fails (the valve body and
  downstream piping must take about 245 K); CO2 is an asphyxiant in enclosed spaces.
- **Catalyst handling**: reduced nickel catalyst is pyrophoric and nickel compounds are toxic
  (general knowledge, not from a source read here; for the HAZOP and the catalyst vendor's
  data); nickel carbonyl can form from CO on nickel at low temperature, so the cool-down is done
  under hydrogen or nitrogen (general knowledge, same caveat; the normal gas holds 0.4 ppm CO).
- **Sulphur**: hydrogen sulphide poisons the nickel catalyst (SRC-2); carbon-capture-1's CO2 is
  from an ammonia plant (sulphur removed upstream), and a guard bed is a basic-design question.

## D-011 LCI: per kg of SNG, the hydrogen a gap, the CO2 from carbon-capture-1 (2026-11-19)

Decision: a gate-to-gate foreground inventory per kg of SNG (98.99 mol% CH4, 5000 kPa(a), stream
S18) from the design case, cut-off system model, one product (no allocation). The hydrogen
(0.5024 kg/kg) stays an open gap with `atlas: false` (lca/mappings.yaml), as in e-fuels-1. The CO2
(2.743 kg/kg) links in the Atlas build to carbon-capture-1's dense-phase product; core's own study
names no background for it. It is declared captured CO2 (`co2_source: fossil-point-source`), so
the footprint reports the product's carbon as carbon from captured CO2 (CCU). Electricity (1.297
kWh/kg) is screened with the packaged UK grid factor as a proxy and linked to the library's
shared `electricity` in the Atlas build. The gases released from the condensate (D-007) are
counted as emissions: 0.00412 kg CO2 and 0.00070 kg CH4 per kg of SNG, both fossil. The degassed
condensate (2.240 kg/kg) links to the shared wastewater entry by mass. The rejected heat is free.
The SNG's carbon is fossil (carbon-capture-1's CO2 comes from natural gas), declared in
carbon_accounting.

Result: 0.26 kg CO2-eq per kg of SNG (lca/results.md): 0.239 from the electricity and 0.025 from
the CH4 and CO2 released from the condensate. It is not a
footprint of e-methane: the hydrogen, at SRC-1's measured 22.4 kWh electrolyser power per Nm3 of
SNG, would need about 31 kWh per kg of SNG, so its electricity source decides the result.

Rejected: linking the hydrogen to hydrogen-1 or the shared merchant hydrogen (the wrong
technology; a correct gap is better than a doubtful link, CONTRIBUTING "Gaps"); an estimate
proxy for electrolytic hydrogen from water and electricity (no electrolyser's measured
efficiency and balance of plant read for a library-wide proxy; SRC-1's 22.4 kWh/m3 is an old
alkaline plant that it calls inefficient, 63.7 % HHV).

Assumptions: start-up flaring, fugitive methane and the dryers' regeneration are excluded and
listed in lca.yaml; no construction phase.

## Core limits

- **L-1** No kinetic model of the honeycomb reactor: R-101 is a conversion step at the measured
  conversion; core's `pfr` needs rate laws, and none for this catalyst and geometry was read.
  Conversion does not respond to load, temperature or catalyst ageing.
- **L-2** Core's propagate does not solve an equilibrium reactor; R-102's equilibrium is solved by
  scripts/balance.py and given as a conversion, checked by `cheme process reactors`. Only CH4,
  H2, CO, CO2 and H2O are components: no carbon deposition, no higher hydrocarbons, CO left out
  of the step (0.4 ppm).
- **L-3** Ideal gas throughout (1.4-1.5 MPa, 283-623 K) for enthalpies and equilibrium; core's
  Peng-Robinson option applies to equilibrium reactors only. The CO2 let-down uses CoolProp
  in the script, not core.
- **L-4** The knock-outs are component separators with the script's split, not a flash in
  core: the water's saturation (IAPWS-95) and the gases dissolved by Henry's law (SRC-6) are
  computed in scripts/balance.py, without the heat of solution or carbonic acid's dissociation;
  the condensate tank releases all the dissolved gas (ASSUMED); trace oxygen of the electrolytic
  hydrogen not counted.
- **L-5** The dryer is a component separator: no adsorption cycle (core's TSA model needs sourced
  isotherms), its regeneration heat and gas are not counted.
- **L-6** Steady state at one load point: no start-up (hydrogen circulation, flaring), no part
  load or load changes, which SRC-1 tested at 40-100 %; fugitive emissions not estimated.
- **L-7** The electrolyser and the CO2 capture are outside the boundary; core's cell model
  (`process/cells.yaml`) could model an electrolyser in a later entry or case.
