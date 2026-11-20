# Ibuprofen by the BHC route (HF acylation, hydrogenation, Pd carbonylation)

A concept-stage batch plant for 3500 t/a of ibuprofen, part of the ChemE-as-Code process library
(issue [#508](https://github.com/ChemE-as-Code/process-library/issues/508)). Not reviewed.

## Route

The three catalytic steps of the BHC process (US 4 981 995 A), purified on the sequence of
US 5 151 551 A:

- **Acylation R-101.** Isobutylbenzene in anhydrous HF; acetic anhydride (2 mol per mol, with
  the recycled isobutylbenzene and anhydride) dosed over 1.5 h at 353 K and about 800 kPa(a),
  85 % conversion, 81 % to 4-isobutylacetophenone (IBAP). C-101 strips the HF (99.9 % back to
  the next batch), C-102 cuts the acetic acid co-product, the recycle and the crude IBAP.
- **Hydrogenation R-201.** Neat IBAP over Raney nickel at 343 K to 1-(4-isobutylphenyl)ethanol
  (IBPE), 98 % selective.
- **Carbonylation R-301.** IBPE with CO in aqueous HCl over a palladium triphenylphosphine
  catalyst at 403 K and 16.6 MPa, 99 % conversion, 96.6 % to ibuprofen; the acid phase decanted
  and recycled.
- **Purification.** Water washes of the melt, vacuum distillation in a packed column (the cut at
  403 to 407 K and 40 to 93 Pa, the water taken off first at about 15 kPa), crystallisation from hexane at 278 K, cold filtration, vacuum
  drying at 323 K; the hexane recovered.

| | |
|---|---|
| batch | 3977 kg of dried ibuprofen every 9.0 h, 880 batches a year on a dedicated train |
| product | 99.56 wt% ibuprofen (model; one crystallisation) |
| yield | 67.0 % of the isobutylbenzene becomes product |
| per kg product | 0.967 kg isobutylbenzene, 0.763 kg acetic anhydride, 8.4 g HF make-up, 12 g hydrogen, 0.211 kg CO, 0.059 kg hydrochloric acid 33 %, 6 g hexane |
| co-product and wastes | 0.456 kg acetic acid; 0.51 kg organic residues to incineration; 3.62 kg wastewater |
| vessels | R-101 80 m3 HF autoclave, D-401 16 m3 (sized by the recipe) |
| thermal screening | acylation dT_ad 5.5 K, MTSR 357.7 K against an MTT of 365.8 K (HF and the nitrogen pad); hydrogenation and carbonylation about 190 and 200 K adiabatic, by hand, not screened |

## How it is modelled

The flowsheet (`process/flowsheet.yaml`) is calculated by cheme-as-code 1.13.0: the semi-batch
acylation from assumed rate laws calibrated to the patent's example, the hydrogenation and the
carbonylation from the examples' conversions and selectivities, the separations from assumed
recoveries, the crystallisation from an assumed yield, five recycles and eight design
specifications that set the feeds. The recipe (`process/recipe.yaml`) gives the cycle and sizes
the vessels; `cheme process reactor-hazards` screens the acylation. Every decision, source and
assumption is in [DESIGN.md](DESIGN.md).

## Run

```sh
cheme validate
cheme process propagate --check
cheme process recipe
cheme process reactor-hazards
cheme assess lca --check
```

## Limits

Kinetics, heats of reaction, the separations and the crystallisation yield are assumed; no
property package covers these liquids; the hydrogenation and the carbonylation are not screened
thermally by core (their adiabatic rises are sized by hand, DESIGN.md D-011). Isobutylbenzene, HF, CO, hexane, the refrigeration, the catalysts and the wastes'
treatment are LCI gaps. No P&IDs, layout, HAZOP or cost estimate yet.
