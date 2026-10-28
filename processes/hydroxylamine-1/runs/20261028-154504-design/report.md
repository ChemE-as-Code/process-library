I've built the concept design for hydroxylamine-1: a design basis, a BFD/PFD whose balances close in cheme, and a preliminary gate-to-gate LCI. Everything is committed in four commits on `case/hydroxylamine-1` (`38fa1ee`, `2c9040e`, `3cab4f3`). `cheme validate` shows 0 errors and 0 warnings. Energy closure cannot be checked in cheme yet, the reactor model rests on patent examples plus several assumed values, and nothing has been reviewed.

**Route, product and boundary**
- **Product:** a hydroxylammonium sulfate solution at 25.4 wt% (10.2 wt% NH2OH, 1.86 wt% ammonium sulfate, 1.30 wt% free acid), at 30 kt/a NH2OH contained (ASSUMED).
- **Route:** NO is hydrogenated in about 20 wt% sulfuric acid over suspended platinum on graphite (BASF-type process).
- **NO is made inside the boundary:** ammonia is burnt with oxygen and steam on a Pt/Rh gauze. NO is not traded, and keeping its generation inside means the burner's N2O, the reuse of its condensate as acid water and the steam export all stay visible.
- **Boundary feeds:** ammonia (ammonia-1), oxygen (asu-1), hydrogen (hydrogen-1 or chlor-alkali-1), sulfuric acid 98.5% (sulfuric-acid-1), demineralised water and steam.

**Files produced**
- `process.yaml` (status internal, maturity concept, unreviewed, references listed)
- `DESIGN.md`: route memo, source register with locators, decisions D-001 to D-011, the list of missing registry entries, open inputs O-1 to O-9
- `process/`: design basis, materials, reactions, flowsheet (3 blocks, 19 steps, 40 streams), generated BFD and PFD, and `simulation.yaml`, which only declares which reactors are adiabatic
- `scripts/has_balance.py`: my independent balance script; it closes at 37 025.02 kg/h in and out
- equipment list (18 items) and line list (22 lines)
- `lca/`: `lca.yaml`, `mappings.yaml`, and the generated inventory, gaps, dataset, manifest and results files

**Balance and check results**
- Every block and step balances on mass, components and reaction extents.
- `cheme check`: the concept gates pass except the plot plan, which is out of scope.
- `cheme maturity` reaches level none, as for hydrogen-peroxide-1 and methanol-1, because feed flows and some conversions are assumed. It therefore flags the "concept" claim in `process.yaml` as exceeding the evidence.
- Per kg NH2OH: NH3 0.612 kg, oxygen 1.538 kg, H2 0.131 kg, acid 1.774 kg, demineralised water 2.70 kg, dilution steam 3.12 kg, electricity 0.095 kWh, LP steam heat 0.198 kWh, cooling water 6.49 kWh, MP steam export 1.865 kWh.
- 84.2% of the ammonia nitrogen ends up as NH2OH.

**LCI results**
- The functional unit is 1 kg NH2OH contained (9.782 kg of solution).
- Every background is left unmapped: 13 gaps, each with a description of the activity it should link to later.
- The mass balance closes against the flowsheet: 11.3675 kg in and out per functional unit (42 628 kg/h).
- The only characterised flow is the plant's own N2O, 25.9 g per kg NH2OH, which comes to 7.08 kg CO2-eq. That is the direct emission only, not a product footprint, even though the generated `results.csv` labels it "total".
- As a cross-check, the N2O works out to about 7.5 kg per tonne of caprolactam, inside the IPCC default of 9 kg/t ±40%.
- NO emission is 33.7 g per kg NH2OH. This is conservative: the off-gas burner is credited with no NO or N2O destruction. Choosing an abatement method (O-8) is the first follow-up.

**Sources used** (patents read in full on Google Patents)
- US 3,110,563 (BASF burner): feed ratio 14 : 18.6 : 67.4 and a 98% NO yield.
- EP 0 945 401 (DOMO): 90% O2 hydrogenation, condensate reused as acid water, 19% acid.
- US 4,895,711 and EP 1 343 719 (BASF): cascade conditions, H2:NO of 2:1, N2O selectivity 2%.
- US 4,997,635: the product analysis.
- US 4,457,906: the N2O explosion hazard.
- IPCC 2006, Vol. 3 Ch. 3, Tables 3.3 and 3.5: N2O defaults.
- NBS aqueous formation enthalpies: used but not re-read in this run, because the open scan has no text layer (O-4).
- Ullmann's article: lead only, not read.

**Key ASSUMED values**
- Capacity and 8000 h/a.
- 90% of the NO converted per pass in the cascade, with a 30% off-gas purge. This leaves 6.5 mol% N2O in the loop gas and 96.8% NO utilisation.
- NH2OH selectivity of 89.8%, derived from the US 4,997,635 product analysis.
- Burner N2O taken from the IPCC atmospheric-plant default.
- Agitator power 2 kW/m³.
- Heat of dilution of the acid.
- Catalyst losses: Pt/Rh 9.2 kg/a, Pt 1.2 kg/a, Ag-Mn catalyst 800 kg/a.
- Nitrate from the condensate carried through into the product.

**Missing from the shared registry (for the consolidated PR)**
- `chemicals/chemicals.yaml`: hydroxylammonium sulfate, ammonia, sulfuric acid, nitrous oxide, nitric oxide, ammonium sulfate, platinum and rhodium.
- `lci/mappings.yaml`: entries for the Pt catalyst loss, the Ag-Mn catalyst and its silver recovery, and an elementary-flow identity for NO.

**Gated steps and open inputs**
- Energy closure can't be checked in cheme: no property package covers NO, N2O or steam-rich gas (core #315) or the aqueous salt solution (core #364 covers aqueous NaCl only). The duties therefore come from my script.
- Open inputs:
  - the explosion limits of the burner feed and of the NO/H2/N2O loop gas (O-7)
  - how to abate the purge's NOx and N2O (O-8)
  - continuous-plant selectivity and per-pass conversion (O-2)
  - catalyst losses (O-3)
  - what happens to the nitrate in the cascade (O-6)

**Recommended next stage:** an independent design review, then the purge abatement decision (O-8) and the explosion-limit work (O-7), sourcing the selectivity, conversion and catalyst-loss values, and adding the registry entries.

No run record is written yet (the session hooks normally do that), and the generated PFD layout is very wide but readable. The merge is pending: the branch needs review and a human merge, and no stage has been signed off.

STATUS: DONE