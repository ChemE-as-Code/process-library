# Adipic acid from cyclohexane via KA oil and nitric acid oxidation

> **AI-generated research output, not engineering advice.** This design was produced by AI coding
> agents (Claude Code) under human direction and is checked by automated tools; it has had
> no independent human review. It is not approved for construction, operation, procurement or
> safety decisions and comes with no warranty. Check the design maturity and review status in
> `process.yaml` before relying on any number.

Manifest and LCI datasets only, with no flowsheet and no simulation. Per tonne of dried adipic
acid, from cyclohexane: cobalt-catalysed air oxidation to KA oil (cyclohexanol and
cyclohexanone), then oxidation of the KA with 50 to 60 % nitric acid over copper and vanadium.

## Route

This is the dominant industrial route. The US EPA's 1991 control-techniques document (section
3.2.2) reports that 98 % of US adipic acid was made from cyclohexane, in continuous operation,
and that cobalt-catalysed air oxidation was the most widely used way to make the KA. Phenol
hydrogenation to KA is the lesser-used alternative. The LVOC BREF (2.1.2.3.3) and the EU ETS
benchmark study (2009, chapter 6) describe the same two stages. The process is continuous. The
cyclohexane oxidation runs in a multistage column or a series of stirred tanks, with the
unconverted cyclohexane recycled. The mother liquor of the nitric acid stage is recycled to its
reactor (AP-42 6.2.2, BREF 2.1.2.3.3). The BREF cites one plant that cut its effluent by changing
from discontinuous to continuous operation.

## How it is built

There are two hand-written Tier 1 datasets in `lca/datasets/`. They are identical except for
the N2O abatement:

| dataset | N2O per t | basis |
|---|---|---|
| `adipic-acid-ka-nitric-catalytic-n2o-abatement` | 53 kg | IPCC 2006 Table 3.4: 300 kg/t generated, catalytic destruction 92.5 % at 89 % utilisation |
| `adipic-acid-ka-nitric-unabated` | 300 kg | the same generation factor, no abatement (IPCC Tier 1 good practice) |

Every amount is the `formula` of its `parameters`, and `generation.balance` records the closed
C, H, N and O balance.

| Item | Source | Value used |
|---|---|---|
| KA per cyclohexane converted | US EPA (1991), EPA-450/3-91-026, p. 3-19 | 77.5 mol%, the midpoint of 75 to 80 % |
| Adipic acid per KA | same, p. 3-20 | 94 mol%, the midpoint of 92 to 96 % |
| N2O generated, destruction and utilisation factors | IPCC 2006 Vol. 3, Table 3.4 | 300 kg/t; 0.925 and 0.89 |
| CO, CO2, CH4, organics, NOx | US EPA AP-42 section 6.2 (1995), Tables 6.2-1 and 6.2-2 | sums of the listed sources |
| Electricity, steam, fuel | IEA information paper (Saygin et al. 2009), Table 13 | the Western European averages: 1.4, 25.7 and 1.2 GJ/t |

The feeds come out at 0.79 t cyclohexane and 1.45 t of 60 wt% nitric acid (0.87 t HNO3) per t.

- **Nitric acid.** The make-up counts the nitrogen that leaves as N2O, before abatement, and as
  NOx. The NO and NO2 are reabsorbed in the plant. The make-up is linked to `nitric-acid-1`'s 60
  wt% acid by mass of solution. It is modelled as (HNO3)3(H2O)7, 59.98 wt%, so that the element
  balance can read it.
- **Process air.** Oxygen from process air is free and closes the oxygen balance.
- **Effluent and residues.** The effluent water closes the hydrogen balance. The KA-section
  residue and the dibasic acids (glutaric and succinic) close the carbon balance of each stage.
  They are modelled as C6H10O4 and glutaric acid, both ASSUMED.
- **KA-section off-gas.** It is ASSUMED to be burned in process heaters, as AP-42 says it may
  be. Its carbon is emitted as CO2.

## What is weak

- **The energy is old and its scope is assumed.** The IEA's averages go back to Chauvel and
  Lefebvre (1989). They are taken to cover both stages, because the paper lists cyclohexane
  making separately, but the paper does not say so. Steam is the largest item: 7140 kWh/t,
  gross, against a best practice of 5140 kWh/t. The paper's footnote 2 to Table 1 marks the
  adipic acid best practice values as estimated, not measured. The EU ETS study puts the CO2 of the steam at the
  adipic acid installation at only 0.40 t/t in 2007/08. That suggests most of the steam is used
  in the KA section, if the study's boundary is the nitric acid stage. This is not resolved.
- **The abated N2O is above what EU plants reached.** The IPCC defaults for catalytic
  destruction give 82 % removal overall. German production in 2001 to 2007 removed about 86 to
  94 % (`benchmarks/oxygenates.yaml`, explained). Plants that use thermal destruction or
  recycle the N2O to nitric acid are not modelled.
- **The nitric acid is a lower bound.** N2 formed from the acid, and acid lost to the effluent,
  are not quantified in an open source.
- **The yields are US figures from 1978 to 1991.** The by-product compounds are model choices.
  The residue, 255 kg/t, is a carbon residual of the KA yield. No open source states a cyclohexane
  or nitric acid consumption to check it against.
- **The air emission factors** have ratings of D and E and come from two to three US plants.
- **Freshness.** `valid_until` is the reference year + 5, 2014, so it has already lapsed.
- **Uncertainty.** `gsd2 = sqrt(high / low)` where a source gives a range (our convention), and
  ASSUMED values elsewhere.

## Linking

- The product has the registry slug `adipic-acid`. The cyclohexane feed (slug `cyclohexane`) is
  a reported gap: the library has no producer and the shared vocabulary has no entry.
- The nitric acid links explicitly to `nitric-acid-1` (`lca/mappings.yaml`). Steam and fuel use
  the shared heat entries.
- The residue and dibasic acids stay unlinked outputs, so they are gaps. Their carbon is large
  against the direct CO2 of 0.16 t/t. The residue holds 126 kg C/t, which would be 0.46 t CO2/t
  if it were burned, as AP-42 says it may be in process heaters. The dibasic acids hold 14 kg
  C/t, or 0.05 t CO2/t. Neither is in the datasets' footprint until a treatment is linked. The
  heat from burning the residue is not credited against the fuel either.

## Not counted yet (TODO)

- N2 from the nitric acid
- acid, metals and organic acids in the effluent
- catalysts (cobalt, copper-vanadium, the N2O decomposition catalyst)
- wash, recrystallisation and cooling water
- spent caustic
- adipic acid dust (no particle size)
- recovered heat
- thermal destruction and N2O recycle
- the phenol route

The full list is in each dataset's `system_boundary.excluded`.
