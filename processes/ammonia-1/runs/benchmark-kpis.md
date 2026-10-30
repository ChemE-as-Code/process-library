# Key performance indicators of the final ammonia-1 design (blind)

Computed 2026-10-30 on branch `bench/ammonia-1-kpis` from `main` at `7535684` (concept and
basic stages signed off). Design case only (D-003). Every number comes from the design's own
files: the stream table of `process/flowsheet.yaml` (`cheme process streams`), the component
data of `process/materials.yaml` and the LCI dataset `lca/dataset.yaml` (checked current with
`cheme assess lca --check`, not regenerated). The calculation is `scripts/benchmark_kpis.py`
(`cheme run scripts/benchmark_kpis.py` reproduces every figure below).

**Blind.** No reference or benchmark value for ammonia plants was looked up or used: no web
search, no `benchmarks/` file, no `benchmark/ammonia` branch. One disclosure: a `grep` of the
design files for "LHV" showed a line in DESIGN.md D-034 that quotes a published range as a check
of the design; that line was not used, and every value here is computed from the streams.

## Common basis

- **Per t of ammonia product**: S60 / `product:NH3`, 62,471.8 kg/h of refrigerated liquid
  (99.969 wt% NH3, 62,452.6 kg/h contained NH3). Per t of contained NH3 every figure would be
  0.03 % higher.
- **Heating values**: lower heating value at 298.15 K, water as vapour, from the ideal-gas
  formation enthalpies `dHf_298` of `process/materials.yaml` (chemicals, ATcT): CH4 802.58,
  C2H6 1,428.63, C3H8 2,043.32, H2 241.82, NH3 317.18 MJ/kmol. Natural gas S1 (D-040 composition,
  M = 16.856 kg/kmol): **LHV 49.086 MJ/kg**.
- **Electricity**: counted as delivered energy, 3.6 GJ/MWh; no primary-energy or power-plant
  factor (the design does not determine one). 36.771 MW, the sum of the energy streams Q1, Q37,
  Q11, Q12, Q17, Q20, Q22, Q32, Q35, Q27, Q31, Q36 (= `feed:POWER`, 36,770.85 kWh per h). All
  drives are electric (D-016).
- **Steam**: enthalpy content above the boundary water it is raised from: MP steam S68 at
  4600 kPa(a), 673.15 K, h = 3,203.78 kJ/kg, minus demineralised water S70 at 500 kPa(a),
  298.15 K, h = 105.30 kJ/kg (IAPWS-IF97): 3.0985 MJ/kg. No boiler-efficiency equivalent is
  used (the design has no reference boiler).
- **Boundary** (DESIGN.md section 1, D-001): natural gas, air and demineralised water in;
  NH3 product, vented process CO2, flue gas, MP steam export and boiler blowdown out;
  electricity in, heat to cooling water out. The furnace, steam system, refrigeration and purge
  recovery are inside; storage, cooling tower, water treatment and flare are outside.
- **Dataset expressions** use the exchange keys of `lca/dataset.yaml` (amounts per 1 h of
  operation, kg or kWh); with an MJ/kg coefficient over `product:NH3` in kg the result is
  directly GJ/t. The coefficients are the heating value, enthalpy and mass fractions stated
  here; the dataset itself carries no heating value.

## Results

| # | KPI | value | unit | dataset expression | per |
|---|---|---|---|---|---|
| 1 | specific-energy-net | **26.97** | GJ/t (LHV) | `(feed:NG * 49.0858 + feed:POWER * 3.6 - product:STEAM * 3.0985) / product:NH3` | product:NH3 |
| 2 | specific-energy-gross | **30.13** | GJ/t (LHV) | `(feed:NG * 49.0858 + feed:POWER * 3.6) / product:NH3` | product:NH3 |
| 3 | natural-gas-feed-plus-fuel | **28.01** | GJ/t (LHV) | `feed:NG * 49.0858 / product:NH3` | product:NH3 |
| 4 | process-co2 | **1.164** | t CO2/t | `product:CO2V * 0.978874105 / product:NH3` | product:NH3 |
| 5 | direct-co2-total | **1.558** | t CO2/t | `emission:CO2 / product:NH3` | product:NH3 |
| 6 | steam-net-export | **+3.16** | GJ/t (export positive) | `product:STEAM * 3.0985 / product:NH3` | product:NH3 |
| 7 | synthesis-loop-pressure | **154.0 bar(a)** (152.99 bar(g)) | bar | none (no exchange) | - |
| 8 | synthesis-conversion-per-pass | **30.2** (H2+N2 basis); 25.5 (total gas) | % | none (no exchange) | - |
| 9 | nox-concentration-reformer | **not determined by the design** | mg/m3(n) as NO2, dry | none (no NOx exchange) | - |
| 10 | nox-emission-factor | **not determined by the design** | kg NO2/t | none (no NOx exchange) | - |

## 1. specific-energy-net: 26.97 GJ/t (LHV)

Natural gas feed and fuel plus electricity minus the exported MP steam:

| term | stream / exchange | flow | MW | GJ/t |
|---|---|---|---|---|
| natural gas, process feed | S3 | 27,716.6 kg/h | 377.91 | 21.78 |
| natural gas, furnace fuel | S2 | 7,929.0 kg/h | 108.11 | 6.23 |
| natural gas total | S1 = `feed:NG` | 35,645.6 kg/h | 486.03 | 28.01 |
| electricity | Q-streams of `feed:POWER` | 36,770.8 kWh/h | 36.77 | 2.12 |
| MP steam export (minus) | S68 = `product:STEAM` | 63,727.3 kg/h | 54.85 | -3.16 |
| **net** | | | **467.95** | **26.97** |

Boundary choices: no steam is imported, so the only steam term is the export. The steam is
credited at its enthalpy above the make-up water (3.0985 MJ/kg); credited at its exergy instead
(1,262 kJ/kg, the D-021 allocation property) the net would be 28.84 GJ/t. Not counted as
exported energy: heat to cooling water (`product:CW`, 136.5 MW), the boiler blowdown S69
(0.89 MW above make-up water, 0.05 GJ/t) and the flue gas. The HRU tail gas S59 (15.43 MW
LHV, 0.89 GJ/t) is an internal fuel recycled from the loop purge, not an import; it is already
contained in the natural gas figure. The LP steam to the purge recovery (Q29, 0.37 MW) is
internal.

Drivers: D-040 (gas composition and the flows from the 1500 t/d basis), D-007 (steam to carbon
3.0, reformer outlet 1083 K at 3500 kPa(a), air-blown secondary reformer), D-014 (furnace:
10 % excess O2, air preheat to 523 K, fuel from the radiant balance), D-024/D-040 (the E-107
duty spec and the simulated stack, 396-397 K, not the 423 K target), D-015 (single MP steam
level, export of the surplus), D-016 (all drives electric: no steam turbines, so the steam is
exported and the power imported; I-09), D-009 (CO2 regeneration heat from the process gas
reboiler E-202, no steam), D-011 and D-017 (loop pressure, refrigeration power at 0.55 of
Carnot), D-013 (purge recovery, tail gas to fuel), D-021 (steam as co-product).

## 2. specific-energy-gross: 30.13 GJ/t (LHV)

Natural gas (28.01 GJ/t) plus electricity (2.12 GJ/t), no credit for the exported steam:
(486.03 + 36.77) MW x 3.6 / 62.4718 t/h. Same boundary and drivers as KPI 1; the electricity
term is set by D-016 (35-37 MW of electric drives: process air K-101 8.76 MW, synthesis gas
K-501 12.68 MW, circulator K-502 1.61 MW, refrigeration K-701 10.07 MW plus its flash-gas
stages 1.06 MW, solvent pumps 1.53 MW, fans, BFW and make-up pumps 1.02 MW, H2 compressor
0.05 MW).

## 3. natural-gas-feed-plus-fuel: 28.01 GJ/t (LHV)

S1 (35,645.6 kg/h, LHV 49.086 MJ/kg) = S3 process feed 21.78 GJ/t + S2 fuel 6.23 GJ/t. No
electricity or steam. The furnace fires S2 plus the tail gas S59 (123.5 MW LHV in all); S59 is
counted at its origin (natural gas feed carbon and hydrogen that leave the loop with the purge),
not again. Drivers: D-040 (fuel split 0.22244 from the balance), D-007, D-014, D-013.

## 4. process-co2: 1.164 t/t

CO2 removed from the synthesis gas and vented: the aMDEA regenerator vent S28 (72,413.5 kg/h
CO2) plus the process condensate stripper overhead S87 (293.9 kg/h CO2, the CO2 dissolved in the
condensates, vented with it): 72,707.5 kg/h. In the dataset this is the CO2 of `product:CO2V`
(74,276.61 kg x mass fraction 0.978874105). Equivalent expression:
`(emission:CO2 - product:STACK * 0.137982561) / product:NH3`.

Boundary choices: all of it is vented (D-001, no CO2 use or capture). It includes the CO2 that
enters with the natural gas feed S3 (217.1 kg/h) and the process air S12 (43.8 kg/h) and leaves
by the same vent; without them the CO2 formed in reforming and shift and removed is 1.160 t/t.
The CO2 left in the treated gas (S27, 500 ppmv, 166 kg/h) is methanated, not counted. Flue-gas
CO2 is excluded. Drivers: D-007, D-008 (HT and LT shift, CO 0.28 mol% wet after LTS), D-009
(500 ppmv slip, CO2 vented, no co-absorption), D-010 (methanation), D-024 (stripper vent S87),
D-040 (gas composition).

## 5. direct-co2-total: 1.558 t/t

`emission:CO2` 97,343.8 kg/h = process vent 72,707.5 kg/h (KPI 4) + flue gas S67 24,636.4 kg/h
(0.394 t/t). No CO2 is used or stored. Boundary choices: the total includes the atmospheric
CO2 carried through by the process and combustion air (151.0 kg/h, 0.0024 t/t), counted as
emitted (D-020); fossil only it is 1.556 t/t. CO, CH4 and other carbon to air are zero in the
model (complete combustion, no co-absorption: D-014, D-009; not data, open input I-07).
Drivers: as KPI 4 plus D-014 (furnace fuel and complete combustion), D-013 (tail gas fired),
D-020.

## 6. steam-net-export: +3.16 GJ/t

MP steam S68 63,727.3 kg/h (1.020 t steam per t NH3) at 4600 kPa(a), 673.15 K, enthalpy above
the make-up water S70 3.0985 MJ/kg: 54.85 MW = 3.16 GJ/t. No steam is imported (the LP steam
of Q29 is let down internally). At the steam's exergy (D-021, 1,262 kJ/kg) the export is
1.29 GJ/t. Boundary choices: reference state is the boundary make-up water (298.15 K,
500 kPa(a)), not the boiler feed water at 313 K (the deaerator heating is inside the raising
duty, D-015); blowdown not counted. The steam system U801 is evaluated on the simulated duties by
`scripts/packages_on_simulated_duties.py` (ASSUMED, D-026), not simulated. Drivers: D-015,
D-016 (electric drives leave the steam for export), D-014 and D-040 (E-107 duty spec 2.72 MW),
D-024/D-026 (boiler duties Q8, Q10, Q13, Q23 simulated).

## 7. synthesis-loop-pressure: 154.0 bar(a) = 152.99 bar(g)

Converter feed S42 at the R-501 inlet: 15,400 kPa(a), 493.8 K (gauge with 1.01325 bar
atmospheric). Around it: circulator discharge S41 155.0 bar(a), converter outlet S43 151.0
bar(a), separator V-501 147.0 bar(a), make-up compressor discharge S38 146.0 bar(a). The
dataset has no exchange for it. Drivers: D-011 (make-up to 14,600 kPa(a), circulator to
15,500 kPa(a), a mid-range pressure for magnetite catalyst, ASSUMED, not optimised), D-026.

## 8. synthesis-conversion-per-pass: 30.2 % (H2+N2 basis)

Converter R-501, S42 in, S43 out (simulated, D-026). Feed 294,703 kg/h = 28,727.9 kmol/h
(H2 63.46, N2 21.19, CH4 9.72, Ar 2.29, NH3 3.34 mol%; H2/N2 2.994); outlet 25,060.3 kmol/h
with NH3 18.47 mol%. NH3 formed 3,667.3 kmol/h (step extent of NH3_SYN 1,833.7 kmol/h x 2).
H2+N2 consumed = 2 x NH3 formed = 7,334.6 kmol/h.

- **H2+N2 basis** (moles of H2+N2 converted / moles of H2+N2 entering): **30.16 %** (H2 30.18 %,
  N2 30.12 %).
- **Total gas basis** (moles of H2+N2 converted / all moles entering, inerts and NH3 included):
  25.53 %.
- NH3 3.34 -> 18.47 mol%; total moles fall by 12.77 %.

No dataset exchange expresses it. Drivers: D-011 (equilibrium with a 15 K approach and
Peng-Robinson fugacity, 12 % inerts at the inlet from the purge fraction, outlet 703 K, overall
adiabatic), D-026 (E-502 outlet retuned to 532.6 K so the converter runs adiabatic, inlet
493.8 K; process air retuned for H2/N2 ~3.0), D-005 (no kinetics: an equilibrium-approach
converter), D-013 (H2 recovery returns inerts-lean gas), D-025 (property package).

## 9. nox-concentration-reformer: not determined by the design

The furnace H-101 is modelled with complete combustion to CO2, H2O, N2 and O2 (D-014, the
`given` basis of D-040 and reactions CH4_COMB to NH3_COMB); the component list has no NO or
NO2, and the dataset declares the furnace's NOx, N2O, CO and unburnt fuel as not estimated
(cut-off `emission-excluded:furnace-incomplete-combustion`, open input I-07). No sourced
emission factor or burner guarantee was chosen, so no concentration follows from the design.
What the design does fix, for whoever adds one: the flue gas S67 is 6,398.7 kmol/h, dry
5,298.9 kmol/h = 118,770 m3(n)/h dry (273.15 K, 101.325 kPa), with 2.06 vol% O2 dry (10 %
excess O2, D-014); the burners fire 123.5 MW LHV (S2 + S59), and the fuel carries 0.04 mol% NH3
from the tail gas (fuel-bound nitrogen, NH3_COMB, also not converted to NOx in the model).

## 10. nox-emission-factor: not determined by the design

The only combustion source inside the boundary is the reformer furnace H-101 (the steam is raised
from waste heat, U801 is not fired; the secondary reformer's burner zone burns H2 in the process
gas and has no flue gas; the flare is outside the boundary). Its NOx is not modelled (KPI 9, D-014,
I-07), so there is no NOx emission factor from the design and no exchange in the dataset.

## Gaps and limits

- KPIs 9 and 10 need a NOx model or a sourced emission factor (I-07).
- The steam system U801 and refrigeration K701 are evaluated by script on simulated duties
  (ASSUMED, D-026); the furnace H-101 is not simulated (its fuel comes from the concept radiant
  balance, D-014, D-024). KPIs 1, 2, 3, 5 and 6 rest on them.
- Energy closure of the whole plant is not evaluated by core (component separators, core#60);
  stream properties are outside core's benchmarked claim for most streams (core#315). The
  balances themselves close (`cheme process streams`).
- Electricity is counted 1:1 and the steam at its enthalpy; other conventions change KPIs 1
  and 6 as stated in their sections.
