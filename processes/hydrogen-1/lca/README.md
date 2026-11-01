# LCA of hydrogen-1: preliminary gate-to-gate LCI

Status (2026-10-27): **preliminary gate-to-gate life cycle inventory**, concept stage. The
foreground comes from the balanced flowsheet (`process/flowsheet.yaml`, case `design`); every
background is deliberately **unmapped** (`missing:` in `lca.yaml`), so the only characterised
number in `results.md` is the plant's own fossil CO2 at the stack. That is not a carbon
footprint of hydrogen: the natural gas supply chain, electricity, water treatment, cooling and
waste water treatment are gaps (`gaps.csv`), never zero. DESIGN.md D-013.

**Read the number with its allocation.** The burdens are shared between hydrogen and the export
steam by **exergy** (H2 90.1 %, steam 9.9 %; `lca.yaml` `allocation`, revised after review
2026-10-27-pfd-lci-review#1). The 9.11 kg CO2-eq per kg H2 in `results.md` is the
exergy-allocated direct stack CO2 (plus the small CH4 and N2O of the combustion estimate);
unallocated, with the steam's share left on hydrogen, it is 10.10 kg. Neither is a footprint.
The inventory tables below are the whole plant per kg H2, unallocated.

| file | what | written by |
|---|---|---|
| `lca.yaml` | goal and scope, functional unit, allocation (exergy), the combustion emission estimate, the mapping of every flow with the background activity it should connect to | people (agent-drafted) |
| `factors.yaml` | the project's factors: none; the packaged `desnz-ghg-2026` profile is included but no flow uses it | `cheme init` |
| `inventory.csv`, `dataset.yaml` | the foreground inventory per kg H2 and the unallocated dataset per hour | `cheme assess lca --inventory --write` |
| `results.*`, `gaps.csv`, `manifest.json` | the classification (partial screening), the gaps, what the result rests on | `cheme assess lca --write` |

Rewrite them with `cheme assess lca --inventory --write`; check with `cheme assess lca
--coverage`, `--balance` and `--check`. Never edit the generated files.

## Inventory per functional unit (1 kg hydrogen product, S17, 99.9 mol% H2, 2.85 MPa)

From `inventory.csv` (generated); provenance: all flows `assumed` (scripts/h2_balance.py and
the design basis, D-006) except what cheme calculates from them.
The numbers below are from the concept balance (before the DWSIM run of DESIGN.md D-016, which
lowers the product by 0.35 % and raises the per-kg flows by about as much); `inventory.csv` and
`results.md` are current.

| exchange | stream | per kg H2 | background to connect (now a gap) |
|---|---|---|---|
| in: natural gas feedstock | S1 | 3.217 kg | market for natural gas, high pressure, site country (incl. upstream methane leakage) |
| in: natural gas trim fuel | S20 | 0.617 kg | the same natural gas supply (supply only: its combustion is in the stack gas) |
| in: demineralised water | S27 | 15.66 kg | deionised water at the user (treatment chemicals, energy, raw water withdrawn) |
| in: combustion air | S22 | 30.89 kg | free (ambient air) |
| in: electricity | Q1, Q10-Q12 | 0.164 kWh | market for electricity, medium voltage, site country |
| out: hydrogen (reference flow) | S17 | 1 kg | - |
| out: export steam, 4.3 MPa / 673 K (co-product) | S33 | 10.55 kg | co-product, exergy allocation (1256.6 kJ/kg against 121 243.5 kJ/kg for H2, `scripts/allocation_exergy.py`); system expansion kept for a substitution variant |
| out: boiler blowdown (waste water) | S34 | 0.210 kg | treatment of waste water |
| out: CO2 (and traces of H2, CO), fossil, to air from the deaerator vent (since D-016) | S35 | 0.028 kg (simulated basis, unallocated; inventory.csv has 0.0253 exergy-allocated) | elementary (characterised by CAS) |
| out: heat to cooling water | Q9 | 3.30 kWh | cooling water supply / heat rejection in a cooling tower |
| out: CO2, fossil, to air | S26 | 10.10 kg | elementary (characterised by CAS) |
| out: H2O vapour to air | S26 | 4.06 kg | elementary (no climate factor) |
| out: N2, O2, Ar to air | S26 | 23.42 / 0.650 / 0.396 kg | free (atmospheric, returned) |

**CO2 by origin (process and combustion kept apart).** All carbon leaves as CO2 through the
reformer stack (complete combustion, D-009). Split by the carbon of the two natural gas
terminals (2.635 kg CO2 per kg of this gas, from its composition, D-004):

| origin | from | kg CO2 per kg H2 |
|---|---|---|
| process (feedstock carbon: reforming and shift, released when the PSA tail gas burns) | feed:NG, 3.217 kg | 8.47 |
| combustion (trim fuel carbon) | feed:NGF, 0.617 kg | 1.63 |
| total at the stack | emission:CO2 | 10.10 |

The flowsheet has one stack, so the inventory carries one CO2 exchange; the split above
follows from the two feed exchanges and the closed carbon balance.

## Balance checks against the flowsheet (2026-10-27)

- Mass per kg H2: in 3.217 + 0.617 + 15.661 + 30.888 = 50.383 kg; out 1 + 10.548 + 38.625
  + 0.210 = 50.383 kg. `cheme assess lca --balance`: mass, Ar, C, H, N and O closed (largest
  residual C -0.01 %), carbon fossil in = fossil out.
- The inventory equals the flowsheet's boundary streams (S1, S20, S22, S27, S17, S33, S26,
  S34, Q-streams) divided by the product flow 9 109.9 kg/h.
- Energy closure is not evaluated: the natural gas has no lower heating value declared to the
  LCA (carrier `lhv`), a next-stage item.

## Open items (not in this inventory)

- Combustion emissions of H-301: estimated since review #2 (`emission_estimates`
  H301-firing: CH4 and N2O from IPCC 2006 Tier 1, CO and NOx from EMEP/EEA 2019 Tier 1, all
  for natural gas, applied to the whole fired duty, ASSUMED). Open: burner-specific factors,
  particulates, and the unburnt C2H6, C3H8 and H2, which stay at the complete-combustion zero
  of the balance (D-009) and are not a determined value. The EMEP/EEA CO and NOx values were
  not re-read in this run: check them against the guidebook table.
- Process condensate (S15) and deaerator: the deaerator vent (dissolved CO2, later traces of
  methanol and ammonia once the shift by-products are modelled) and the stripping steam are not
  in the flowsheet or this inventory (D-010); a condensate stripper or the deaerator vent is an
  emission source to add (review #6).
- Consumables: reforming catalyst (Ni), HT shift catalyst (Fe-Cr), hydrogenation catalyst
  (CoMo/NiMo), ZnO sorbent, PSA adsorbents, boiler water chemicals: amounts and lives are
  vendor inputs; each needs a disposal route (spent ZnO and nickel catalyst carry metals).
- Construction, maintenance, transport and end of life: no take-off at concept stage.
- A substitution (system expansion) variant for the export steam, with the receiving site's
  steam supply as the avoided product, as a comparison to the exergy allocation (D-013).
- Dataset documentation for publication: location, ISIC/CPC classification and flow
  identities (`cheme.lca-dataset-undocumented`).
