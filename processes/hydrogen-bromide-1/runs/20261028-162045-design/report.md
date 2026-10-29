I've built the hydrogen-bromide-1 concept case: a design basis, a balanced BFD/PFD and a preliminary gate-to-gate LCI, all committed in three commits (`78bf828`, `cd09152`, `f6f18e7`). `cheme validate` reports 0 errors and 0 warnings, and the working tree is clean.

**Process.** Liquid bromine is vaporised with LP steam (E101) and burnt in a 5 mol-% excess of hydrogen in a water-cooled burner (R101). An activated-carbon bed (R102) converts the bromine the flame leaves. A graphite cooler (E102) takes the gas to 60 °C. A cooled falling-film absorber (C201) dissolves it to 48 wt-% acid, and a tail gas scrubber (C202) takes all the absorption water first. P201 pumps the acid to storage. Capacity is 1 000 kg/h HBr = 2 083 kg/h of acid = 8 kt/a.

**Files produced**
- `process.yaml` (internal, concept, unreviewed).
- `process/` files: `design-basis.yaml`, `materials.yaml`, `reactions.yaml`, `catalysts.yaml`, `simulation.yaml`, `flowsheet.yaml`, and the generated `BFD.xml` and `PFD.xml`.
- `scripts/balance.py`, an independent mass and energy balance.
- `equipment/equipment-list.yaml` with the 7 PFD items.
- `lca/lca.yaml` and `lca/mappings.yaml` (no overrides yet, candidates listed), plus the generated inventory, gaps, dataset and manifest.
- `DESIGN.md` (decisions D-001 to D-012) and `PROGRESS.md`.

**Balances and checks**
- **Mass balances:** all three blocks and all seven steps close.
- **Reactor duties:** cheme's burner duty is −166.39 kW, the same as my script; the carbon bed's is −0.053 kW, a 0.5 K rise.
- **Carbon bed:** run as an equilibrium reactor at 448 K (K = 1.1e13). It leaves a Br2 mole fraction of 3.6e-12.
- **Overall energy:** a hand check comes to 410.0 kW against 410.6 kW of cooling (0.14 %). cheme cannot check this itself because it has no property method for these streams.
- **`cheme check`:** every concept gate passes except the plot plan, which is out of scope.
- **`cheme maturity`:** calculation maturity is "none", so the claimed "concept" maturity is flagged as exceeding the evidence. The reasons are that the feed flows are assumed and the absorber and scrubber recoveries are assumed values. The two reactors pass.
- **Library build:** `build_catalog.py --strict` accepts the manifest. I could not run `build_lci.py` because openpyxl is missing in this environment.

**LCI per kg HBr**

| Exchange | Amount |
|---|---|
| Bromine | 0.9875 kg |
| Hydrogen feed | 0.01326 kg (0.01308 kg of it H2) |
| Demineralised water | 1.0835 kg |
| LP steam | 0.058 kWh (0.098 kg) |
| Electricity | 0.0031 kWh |
| Cooling water | 0.411 kWh |
| Product acid | 2.083 kg |
| Vent | 0.94 g: 0.62 g H2, 0.18 g N2, 0.13 g water, 0.036 mg HBr |

- **Balance:** mass, bromine and hydrogen each close to 0.00 %.
- **Coverage:** "partial screening carbon footprint" with 8 gaps. Six are the unlinked backgrounds: bromine, hydrogen, demineralised water, LP steam, electricity, cooling water. Two are H2 and HBr to air, which have no climate factor.
- **Backgrounds:** each is left unmapped, with a description of the activity it should link to later. There is only one product, so no allocation.

**Sources**
- US 6 036 936 A (Elf Atochem): hydrogen-to-bromine ratio, flame, pressures, the carbon finishing stage at 150–200 °C, graphite cooling to about 60 °C, bromine fed at 3 bar / 95 °C.
- US 3 988 427 A (Ethyl Corp.): 99.97 % bromine conversion in the flame, turndown range.
- Wikipedia, "Hydrogen bromide" and "Hydrobromic acid": the 200–400 °C catalytic route, boiling point, the 47.6 % azeotrope, density 1.49 g/cm³.
- Parker (1965, NBS): heat of solution at infinite dilution, −85.14 kJ/mol (from a search summary, not read at source).
- Thermochemical data through `cheme chemistry thermo`, and hydrogen-1's product stream S17 for the hydrogen feed.
- The Ullmann chapters were checked for identity only; no numbers were taken from them.

**Key assumed values**
- Capacity and 8 000 h/a operation.
- 5 % hydrogen excess (inside the patent range).
- Pure bromine at 400 kPa. Real bromine's chlorine and water are left out.
- 99.5 % of the HBr absorbed, and 5 mg/Nm³ HBr in the vent.
- Heat of solution to 48 % acid of −72.0 kJ/mol, scaled from the HCl analogue. A 10 % error moves the absorber duty by about 11 %.
- Acid heat capacity 2.10 kJ/(kg K); LP steam at 450 kPa; cooling water 25/35 °C; 3 kW for instruments and burner management.

**Missing from the shared registries**
- `chemicals/chemicals.yaml`: `bromine`, `hydrogen-bromide`, and a grade such as `hydrobromic-acid/48`.
- `lci/mappings.yaml`: a bromine entry, a demineralised-water entry (#45), and biosphere identities for HBr and H2 to air.
- The library has no bromine-1 process yet.

**Open inputs and blocked steps**
- **Blocked on core#364:** no property method in this cheme (0.8.0) covers HBr–water, Br2 or HBr gas. That blocks the absorber model, stream properties and DWSIM simulation. The issue itself would not open from this account, so its state comes from `cheme process methods` as installed.
- **Open inputs:** supplier data for the burner and absorber, the carbon bed's life and disposal, chlorine in the bromine (it would end up as HCl in the acid), and recovering burner heat to run the vaporiser.
- **Outside my files:** `checks/checks.yaml`, which came with the template, cites a D-023 that does not exist; validate reports it as info.

**Next stage:** an independent review of this concept. Then a bromine-1 case so the main feed gets a dataset, sourcing the burner and absorber data, replacing the heat-of-solution value once core#364 lands, and then the P&IDs and the LCI backgrounds.

No merge is pending: the work is on `case/hydrogen-bromide-1`, not pushed, with no stage sign-off.

STATUS: DONE