# Phosphoric acid by the wet dihydrate process

> **AI-generated research output, not engineering advice.** This design was produced by AI coding
> agents (Claude Code) under human direction and is checked by automated tools; it has had
> no independent human review. It is not approved for construction, operation, procurement or
> safety decisions and comes with no warranty. Check the design maturity and review status in
> `process.yaml` before relying on any number.

Manifest and LCI dataset only, with no flowsheet and no simulation. Per tonne of merchant-grade acid (53.97 wt% P2O5, 539.7 kg P2O5), from phosphate rock and sulfuric acid by the dihydrate (DH) process, with concentration of the filter acid and fluosilicic acid recovery. The process is continuous: rock and acid are fed continuously and the vacuum filter runs through its stages in sequence (AP-42 8.9.2.1; LVIC-AAF BREF 5.2.2).

## How it is built

`lca/datasets/phosphoric-acid-dihydrate.yaml` is a hand-written Tier 1 dataset: every amount is the `formula` of its `parameters`, and `generation.balance` records the closed element balance (C, Ca, F, H, O, P, S, Si).

| Item | Source | Value per t P2O5 |
|---|---|---|
| Rock composition | LVIC-AAF BREF Table 5.2, Khouribga (Morocco, 47.5 % of EU supply in 2004) | modelled as 3 Ca10(PO4)6F2 + 4 CaCO3 + CaF2 + 5 SiO2: 33.6 % P2O5, 51.6 % CaO, 4.0 % F, 4.6 % CO2 |
| P2O5 efficiency | BREF 5.4.1, DH 94 to 96 % | 95 %, so 3.13 t rock |
| Sulfuric acid | stoichiometry, one H2SO4 per Ca to gypsum | 2.53 t as 100 % (2.57 t of 98.5 % acid) |
| Phosphogypsum | stoichiometry | 4.98 t dry (gypsum 4.44, P2O5 loss 0.13, fluoride 0.18, gangue 0.23) |
| Electricity | EFMA booklet 4, 4.1: 120 to 180 kWh/t | 180 (upper end: grinding) |
| Steam | EFMA 4.1: 0.5 to 2.2 t/t | 2.2 t (upper end: weak DH acid is concentrated) |
| Process water | EFMA 4.1: 4 to 7 m3/t | 5.5 m3 |
| Fluosilicic acid | EFMA 4.2: 20 to 30 kg/t as 100 % | 25 kg |
| Fluoride to air | EFMA 8.1.1: 40 g/t, new plants | 40 g F, as HF |
| Carbonate CO2 | IPCC 2006 Vol. 3, 2.1 (acid-induced release, named for phosphoric acid) and Table 2.1 | 145 kg, all rock carbonate |

The product is counted by mass of the acid as sold. For the element balance it is written as (H3PO4)86(H2O)152(H2SiF6): 53.97 % P2O5 and 1.0 % F, which keeps 14.9 % of the rock's fluorine in the acid, as the BREF's DH distribution (Table 5.9, 15 %) gives. The sulfuric acid is written as (H2SO4)12(H2O), 98.5 wt%, the grade `sulfuric-acid-1` makes.

Three closing terms, all ASSUMED and labelled: the fluoride left after the acid, the by-product and the stack goes to the gypsum as CaF2 (69 %: the BREF's 43 % in gypsum plus the unrecovered vapour fluoride, which a closed-loop plant returns to the stack); the silicon not bound as H2SiF6 goes to the gypsum as SiO2, standing for all gangue; and the water balance closes on `output:wastewater` (4.2 m3/t P2O5).

## What is weak

- **One rock.** Rock, acid, gypsum and CO2 follow the model Moroccan rock. Igneous rock (Kola: 38.9 % P2O5, 0.2 % CO2) would need about 14 % less rock and give almost no CO2. The rock's minor constituents (about 6 %: Al, Fe, Mg, Na, organics, SO3) are counted as silica. The model rock also carries 51.6 % CaO against the analysis's 50.6 %, and the rock's 1.6 % SO3 is not credited against the acid demand. Both raise the sulfuric acid, together by about 4 % (2.53 t per t P2O5 as 100 %, inside the plant's 2.4 to 2.9 t), and the gypsum by about 2 % (4.98 t, at the top of the 4 to 5 t range).
- **Utilities are range ends.** Electricity and steam are the upper ends of EFMA's ranges, chosen for a DH plant that grinds and concentrates. Their KPIs are bound to one EU DH plant's reported values (Nilefos, 170 to 180 kWh and 1.9 to 2.4 t, BREF Table 5.5), which the dataset also cites as support, so the check is only partly independent. A plant integrated with a sulfuric acid plant uses its exhaust steam (EFMA 4.1); under cut-off that steam carries no burden from `sulfuric-acid-1`, which is not modelled here.
- **Water.** The 4.2 m3/t closing term is counted as effluent to treatment, conservatively: a closed-loop plant recycles its process and stack water and loses it by evaporation from the stack and cooling ponds. Releases to water of open-loop plants (BREF Table 5.7) are not included.
- **P2O5 loss.** The whole 5 % loss is put in the gypsum as CaHPO4.2H2O, 1.06 % P2O5 in the dry gypsum against the BREF's about 0.75 % (5.4.1); the share that leaves in the stack water is not separated.
- **Fluoride to air** is EFMA's achievable new-plant level, an upper bound. It is 17 times the US source-test factors (AP-42 Table 8.9-1) and well below the 90 to 135 g/t the BREF reports for one EU DH plant (`benchmarks/phosphoric-acid.yaml`, explained).
- **Allocation.** Fluosilicic acid is 1.3 % of the product mass. The default is mass allocation, as a recorded deviation, because no prices are sourced.
- The data are of the late 1990s to 2006. `valid_until` is the reference year + 5, 2011, so it has already lapsed.
- Uncertainty: `gsd2 = sqrt(high / low)` where the source gives a range (our convention), ASSUMED values elsewhere.

## Linking

The product has the registry slug `phosphoric-acid`, counted as merchant-grade acid (not 100 % H3PO4). `feed:sulfuric-acid` is pinned to `sulfuric-acid-1` in `lca/mappings.yaml`. Steam is the shared background entry by mass (`atlas: false`), as in `cumene-1`. Phosphate rock and the four phosphogypsum outputs are reported mapping gaps: the shared vocabulary has no entry for them, and none is guessed.

## Not counted yet (TODO)

Cooling water, rock dust, releases to water of open-loop plants, cadmium and other trace elements and radionuclides, the treatment and long-term leachate of the phosphogypsum stack, free sulfate in the product, the hemihydrate and recrystallisation variants. The full list is in the dataset's `system_boundary.excluded`.
