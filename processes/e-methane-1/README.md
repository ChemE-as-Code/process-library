# e-Methane, synthetic natural gas from hydrogen and CO2 (e-methane-1)

Synthetic natural gas (e-methane) made from electrolytic hydrogen and captured CO2 by two-stage
catalytic methanation (the Sabatier reaction on nickel), after the STORE&GO power-to-gas
demonstration at Falkenhagen, Germany. A concept-stage design of the
[ChemE-as-Code process library](https://github.com/ChemE-as-Code/process-library), issue
[#520](https://github.com/ChemE-as-Code/process-library/issues/520); not reviewed.

## The plant

| | |
|---|---|
| Feeds | dry hydrogen, 9.0045 kmol/h (18.15 kg/h; the source's 200 m3/h STP) from an electrolysis plant; 50 Nm3/h CO2 (99.09 kg/h, H2/CO2 = 4) from a dense-phase CO2 pipeline at 15.3 MPa (the library's carbon-capture-1) |
| Feed conditioning | hydrogen compressed in two stages to 1.53 MPa(a); the CO2 let down to the same pressure with a heater (isenthalpic let-down alone would end at about 245 K, two-phase) |
| Honeycomb reactor | catalyst-coated metallic honeycombs in oil-cooled tubes, feed preheated to 523 K against the effluent, isothermal at about 623 K, 92 % of the CO2 converted (the demonstration's measured value), 93.0 kW to the thermal oil |
| Water removal | air cooler and chilled-water cooler to 283 K, knock-out: 74.6 kg/h of reaction water |
| Polishing reactor | oil-cooled fixed bed of nickel pellets at 513 K, fed by an electric preheater; the remaining CO2 reaches its ideal-gas equilibrium (97.6 % of it converted, 99.81 % of the hydrogen overall), 8.5 kW to the oil |
| Drying and injection | cooling and knock-out at 283 K, two adsorption dryers, a compressor to 5.0 MPa(a) for the transport grid |
| SNG | 36.27 kg/h, 50.84 Nm3/h, 99.06 mol% CH4, 0.75 mol% H2, 0.19 mol% CO2, dry; 556 kW (HHV), 502 kW (LHV, 49.8 MJ/kg); 290 t/a in 8000 h |
| Methanation efficiency | 77.7 % (HHV of the methane over that of the hydrogen); the demonstration measured 77.5 % and its ASPEN model gave 78.0 % at this point |
| Electricity | 46.1 kW: the methanation unit's 41 kW measured at this load (hydrogen compressor 27.7 kW, electric preheater 7.2 kW, the rest the chiller, pumps and fans) and 5.1 kW for injection; 0.91 kWh per Nm3 of SNG, 1.27 kWh per kg |
| Heat | 94.8 kW at about 180-200 C in the thermal oil after the CO2 heater (1.86 kWh per Nm3 SNG; the demonstration used 86 kW, 1.7 kWh/Nm3); rejected to air at this generic site without a heat user |
| Condensate | 81.0 kg/h of reaction water to treatment (2.23 kg per kg SNG) |
| Screening carbon footprint | 0.23 kg CO2-eq per kg of SNG from the plant's electricity alone (UK grid factor as a proxy). The hydrogen is an open gap: about 31 kWh of electrolyser power per kg of SNG at the demonstration's measured efficiency, which dominates any complete footprint. The CO2 links to carbon-capture-1 in the Atlas build; its carbon is fossil (an ammonia plant's stripper vent) |

## How it is modelled

`cheme process propagate` computes the mixers, the honeycomb reactor as a conversion reactor at
the measured 92 %, the polishing reactor as a conversion reactor at the equilibrium conversion
that `scripts/balance.py` solves from the same ideal-gas data (Sabatier and reverse water-gas
shift, 0.7 ppm CO; `cheme process reactors` confirms ln(Q/K) = 0.04 at its outlet, and shows the
honeycomb reactor at ln(Q/K) = -4.6, short of equilibrium), both reactors' heat to the thermal
oil, the knock-outs and the dryer. The script gives the feeds, the knock-outs' water split
(IAPWS-95), the exchanger, cooler and heater duties (ideal gas), the CO2 let-down heat
(Span-Wagner in CoolProp), the compressor power and the rest of the measured electricity, and
compares the result with the demonstration's measured and simulated indicators. Not modelled:
the reactors' kinetics and hot spots, carbon deposition, start-up and part load, the gases
dissolved in the condensate, the dryers' regeneration. Every decision, source and limit is in
[DESIGN.md](DESIGN.md).

## Files

| file | what |
|---|---|
| `process.yaml` | the Atlas manifest |
| `process/design-basis.yaml` | what the plant must do |
| `process/materials.yaml`, `process/reactions.yaml` | components and the Sabatier and reverse water-gas shift reactions |
| `process/flowsheet.yaml` | the flowsheet with closed balances; `process/BFD.xml` and `process/PFD.xml` are generated from it |
| `scripts/balance.py` | what core cannot calculate (`cheme run scripts/balance.py`) |
| `equipment/equipment-list.yaml` | the equipment of the PFD with sizes |
| `lca/` | goal and scope, the preliminary LCI dataset and the screening results |

## Checks

```sh
cheme validate
cheme process propagate --check
cheme process reactors
cheme process build
cheme assess lca --check
cheme check --stage concept
```

Sources: STORE&GO deliverables D5.9 (DVGW, 2020) and D8.3 (University of Groningen, 2018);
IAPWS-95 and ideal-gas data through the `chemicals` and `thermo` packages; CO2 properties from
CoolProp. Data and design under CC BY 4.0.
