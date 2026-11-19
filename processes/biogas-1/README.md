# Biogas and biomethane (biogas-1)

An agricultural biogas plant that digests cattle slurry with hygienised catering waste, grease
trap waste and biowaste, and upgrades the biogas to grid-quality biomethane with membranes. A
concept-stage design of the [ChemE-as-Code process library](https://github.com/ChemE-as-Code/process-library),
issue [#462](https://github.com/ChemE-as-Code/process-library/issues/462); not reviewed.

## The plant

| | |
|---|---|
| Substrates | 22 100 t/a: 4000 t cattle slurry, 8000 t catering waste, 4600 t grease trap waste, 5500 t biowaste (the wastes hygienised before delivery); the FNR Guide to Biogas's model plant VII |
| Digestion | two stirred concrete digesters, 2 x 1700 m3, 40 C (mesophilic), 51 d retention, 2.4 kg VS per m3 and day |
| Raw biogas | 216.93 Nm3/h (dry), 60.68 mol% methane; the guide gives 1 735 468 m3/a at 60.7 % for plant VII |
| Digester heat | 135.8 kW (the substrate warmed, the tanks' losses, the water evaporated into the biogas) from a hot-water boiler burning 11.1 % of the biogas |
| Upgrading | a gas chiller to 10 C that removes the water before compression, activated carbon (H2S), compression to 16 bar(a), an after-cooler, three membrane stages with internal recycle: 99.5 % of the methane to the product |
| Biomethane | 87.99 kg/h, 118.8 Nm3/h, 98.0 mol% CH4 (0.947 kg CH4 per kg), 1.16 MW (LHV, 47.4 MJ/kg), 704 t/a, to a grid injection station |
| Electricity | 1.03 kWh per kg of biomethane (the membrane unit 0.25 kWh/Nm3 raw biogas, the gas chiller, the agitators and pumps) |
| Digestate | 28.4 kg per kg of biomethane, stored six months under a gas-tight cover, spread on farmland |
| Screening carbon footprint | 0.32 kg CO2-eq per kg of biomethane, 6.7 g per MJ (the plant's gate-to-gate emissions with its electricity from cradle to gate): 60 % electricity (UK grid factor as a proxy), 40 % the 0.5 % methane slip of the membranes; the wastes enter burden-free (cut-off). A lower bound: methane leaks are excluded, and a leak the size of the slip would add 40 %. AR4/AR5 (electricity) and AR6 (methane) GWPs mixed: a screening figure |

## How it is modelled

The substrates' volatile solids are lumped into a digestible carbohydrate, a digestible fat and
an inert remainder, so that Buswell's stoichiometry of the digestible part gives each
substrate's standard biogas yield and methane content from the FNR guide; the plant then
reproduces the guide's gas output for model plant VII. `cheme process propagate` computes the
digesters (a conversion reactor), the gas space, the boiler and its heat, and the separators;
`scripts/balance.py` gives the feeds, the lumped compositions, the water saturation, the
membranes' split from the SGC review of upgrading technologies, the heat demand, the chiller's
and after-coolers' heat and the power.
Core has no anaerobic digestion model: the QSDsan integration runs a project's own model, and
the library's QSDsan entry covers an activated-sludge waterline, not a digester. Nitrogen,
sulphur, kinetics and methane leaks are not modelled. Every decision, source and limit is in
[DESIGN.md](DESIGN.md).

## Files

| file | what |
|---|---|
| `process.yaml` | the Atlas manifest |
| `process/design-basis.yaml` | what the plant must do |
| `process/materials.yaml`, `process/reactions.yaml` | components (with the lumps) and the Buswell and combustion reactions |
| `process/flowsheet.yaml` | the flowsheet with closed balances; `process/BFD.xml` and `process/PFD.xml` are generated from it |
| `scripts/balance.py` | what core cannot calculate (`cheme run scripts/balance.py`) |
| `equipment/equipment-list.yaml` | the equipment of the PFD with sizes |
| `lca/` | goal and scope, the preliminary LCI dataset and the screening results |

## Checks

```sh
cheme validate
cheme process propagate --check
cheme process build
cheme assess lca --check
cheme check --stage concept
```

Sources: FNR, Guide to Biogas (2010); Bauer et al., SGC Rapport 2013:270; Evonik's US 8 999 038
B2; IAPWS-95 through the `chemicals` package. Data and design under CC BY 4.0.
