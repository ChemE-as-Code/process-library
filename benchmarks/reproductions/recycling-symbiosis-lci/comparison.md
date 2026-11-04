# Comparison: linked LDPE and PP recycling inventories

- **Target:** El Khoury et al. 2025, SETAC Europe abstract 5.10.P-We469 (`source.yaml` target).
  A conference abstract: no inventory inputs, no absolute results.
- **Component reproduced:** Somoza-Tornos et al. 2020, ACS Sust. Chem. Eng. 8, 3561, Table 2
  (net flows per kg ethylene of waste-PE pyrolysis), recomputed from the same paper's Eq. 1
  and column recoveries (`source.yaml` component).
- **Tolerances:** `tolerances.yaml`, frozen in commit 7319d4b (2026-11-04 14:52 +01:00),
  committed with `source.yaml`, `inputs.yaml` and `sufficiency.md` before `run.py` existed.
  Before the freeze we checked Table 2's mass closure by hand and saw, in a rough estimate,
  that benzene and CO2 might differ by a few per cent; the tolerances rest on the stated
  precision of the inputs (their `reason:` fields), not on that estimate.
- **Run:** `uv run benchmarks/reproductions/recycling-symbiosis-lci/run.py` from the repository
  root, 2026-11-04, uv 0.13.0, Python 3.13.16, numpy 2.3.4, matplotlib 3.10.7, pyyaml 6.0.3.
  Output `results/comparison.json` and three SVG figures. Two runs gave byte-identical results.
  The component source (UPCommons accepted manuscript) was downloaded into the cache and its
  sha256 matched the pinned value. The library file `processes/ethylene-1/lca/inventory.csv`
  matched its pinned sha256.

## Verdict under the frozen rule: FAIL (target: not achievable)

| Part | Result |
| --- | --- |
| Target reproduction (El Khoury et al. 2025) | **not achievable**: no inventory inputs published; every reported result is a share of characterised impacts on an unnamed licensed background |
| Component reproduction (Somoza-Tornos et al. 2020, Table 2) | **fail**: 4 of 5 checks pass; benzene is 6.3 % low against a 3 % tolerance |
| Reconciliation checks (mass, carbon, exchange identity, allocation conservation) | all hold to rounding (relative error 0) in all three configurations and in the extension |
| Direction check against the target's claim (S4 lowest) | consistent on inventory indicators (does not count for the verdict) |

The pass rule makes the case verdict "fail" when a component check fails. That is the result.
It does not make the mass reconciliation below wrong: the reconciliation needs only the ethylene
and propylene yields of the PE model, and both pass.

### Component checks (per kg ethylene)

| Quantity | Reference (Table 2) | Ours (Eq. 1 + recoveries) | Deviation | Tolerance | Status |
| --- | --- | --- | --- | --- | --- |
| Waste PE feed | 2.17 kg | 2.1656 kg | -0.20 % | rel 2 % | pass |
| Methane | 0.204 kg | 0.2036 kg | -0.18 % | rel 2 % | pass |
| Propylene | 0.378 kg | 0.3764 kg | -0.41 % | rel 2 % | pass |
| Benzene | 0.287 kg | 0.2688 kg | -6.35 % | rel 3 % | **fail** |
| Direct CO2, fuel combustion | 0.986 kg | 1.0258 kg | +4.03 % | rel 5 % | pass |

Context (not frozen checks): the table's own mass closure gives 0.301 kg fuel per kg ethylene
(feed less products); our split gives 0.317 kg. The CO2 per kg of fuel is 3.28 kg in the table
and 3.24 kg in ours.

### Deviations and explanations

1. **Benzene and fuel are shifted against each other.** Our benzene is 0.018 kg/kg ethylene
   low and our fuel 0.016 kg/kg high; the feed, ethylene, propylene and methane agree within
   0.5 %. So in the source simulation about 0.017 kg/kg ethylene that Eq. 1 with a 99 % benzene
   recovery sends to the T4 top (fuel) ends up in the benzene product. Candidate causes, not
   resolvable from the paper: the simulation's reactor used a benzene coefficient other than
   the printed 0.45 (0.48 would reproduce 0.287 kg and still keep the feed within 0.6 %), or
   the benzene line holds C4 or C3 material from the T4 bottoms, which would contradict the
   stated 99.5 wt% purity (butadiene and butenes boil about 85 K below benzene). A 1.1 %
   rounding allowance cannot cover 6.3 %.
2. **Direct CO2 +4 %.** Follows from the larger fuel stream (item 1). The CO2 per kg of fuel
   agrees within 1.2 %, so combustion bookkeeping is consistent.
3. **Eq. 1 is not element-balanced.** Its products correspond to C20.04 H39.38 per
   pseudo-mole, a hydrogen deficit of 1.7 % against the CH2 polymer. We normalised the product
   masses (inputs.yaml); the carbon closure of the LDPE folder uses the carbon content Eq. 1
   implies for the feed (0.8584 kg/kg against 0.8563 for CH2). The effect on the compared
   numbers is below 0.3 %.
4. **Purity not attributed.** Products are taken as the recovered key component only; the
   0.5 wt% impurities would raise each product mass by at most 0.5 %.

## Mass-inventory reconciliation (achievable scope)

Basis: 1000 kg sorted waste LDPE and 1000 kg sorted waste PP; each chain delivers 1000 kg
polymer. Half of each waste goes to mechanical recycling at 75 % yield (375 kg recyclate), the
rejects and the other half (625 kg) to pyrolysis. Every assumption is labelled in `inputs.yaml`.
PP pyrolysis yields are ASSUMED (no open source found).

| Combined system (both chains) | D_fuel: disconnected, other olefin burnt | D_market: disconnected, other olefin sold | L: linked |
| --- | --- | --- | --- |
| Virgin ethylene bought | 336.4 kg | 336.4 kg | 242.6 kg |
| Virgin propylene bought | 437.5 kg | 437.5 kg | 328.9 kg |
| Olefin exchanged between chains | 0 | 0 | 202.4 kg (108.6 kg propylene to PP, 93.8 kg ethylene to LDPE) |
| Olefin sold to the market | 0 | 202.4 kg | 0 |
| Olefin burnt as fuel | 202.4 kg | 0 | 0 |
| Net virgin olefin, system expansion view | 773.9 kg | 571.5 kg | 571.5 kg |
| Methane and benzene sold | 133.8 kg and 127.6 kg | same | same |
| Foreground direct fossil CO2 (pyrolysis furnaces) | 1617.4 kg | 982.4 kg | 982.4 kg |
| Net electricity (inventory flow, not characterised) | 262.1 kWh | 262.1 kWh | 262.1 kWh |
| Gate-to-gate direct CO2 of the virgin olefin bought (Atlas ethylene-1, 0.396 kg/kg) | 306.5 kg | 306.5 kg | 226.3 kg |

Reconciliation of the exchange: the propylene the LDPE folder sends (108.6 kg) equals what the
PP folder receives, and the PP folder's virgin propylene falls from 437.5 to 328.9 kg, by
exactly that amount. Likewise 93.8 kg ethylene from PP to LDPE, virgin ethylene 336.4 to
242.6 kg. Neither receiver is saturated in the base case.

**What linking changes depends on the counterfactual.** Against D_fuel, linking saves 202.4 kg
virgin olefin and 635 kg direct CO2 (the burnt olefin's carbon, 3.14 kg CO2/kg). Against
D_market, the combined system buys 202.4 kg less virgin olefin under cut-off accounting, but
with system expansion (the sold olefin displaces virgin olefin elsewhere) the net virgin olefin
and the direct CO2 are identical. The exchange then only moves the displacement from the
market into the partner folder. The abstract's finding that S4 is lowest therefore holds when
the disconnected chains do not use the other olefin as a material. A study that credits every
pyrolysis coproduct in both chains (avoided burden, as Somoza-Tornos et al. 2020 did) would
find no difference from the exchange as such, apart from logistics. The abstract does not say
which counterfactual S3 used.

### Coproduct treatment and per-folder attribution (cut-off, mass allocation)

Allocation rule: the WBCSD step of docs/system-model.md. The price ratio of the pyrolysis
coproducts (ethylene 1.075, benzene 0.994, propylene 0.875, methane 0.334 EUR/kg; source Table 1)
is 3.2, below 5, so mass. Each plant's direct CO2 is shared over its products per kg.

| Per folder, cut-off | D_fuel LDPE | D_fuel PP | D_market LDPE | D_market PP | L LDPE | L PP |
| --- | --- | --- | --- | --- | --- | --- |
| Plant direct CO2 per kg product | 1.499 kg/kg | 3.137 kg/kg | 0.555 kg/kg | 1.689 kg/kg | 0.555 kg/kg | 1.689 kg/kg |
| Foreground CO2 carried by the folder's polymer | 432.6 kg | 588.3 kg | 160.1 kg | 316.8 kg | 318.5 kg | 377.0 kg |
| Foreground CO2 leaving with exported products | 204.3 kg | 392.2 kg | 135.9 kg | 369.6 kg | 75.6 kg | 211.2 kg |
| Virgin monomer bought | 336.4 kg | 437.5 kg | 336.4 kg | 437.5 kg | 242.6 kg | 328.9 kg |

The allocated parts sum to the unallocated total in every configuration (allocation
conservation check). In L, received olefin carries its sender's allocated burden: the LDPE
folder takes over 93.8 kg x 1.689 = 158.4 kg CO2 from the PP plant and buys 93.8 kg less
virgin ethylene, whose gate-to-gate direct CO2 in the Atlas ethane cracker is 37.1 kg. On
foreground direct CO2 alone, linking makes the LDPE folder's polymer look worse, because the
assumed PP plant burns 0.35 kg of each kg of feed. This is a screening comparison with gaps on
both sides (pyrolysis utilities beyond electricity, ethane and power upstream of the cracker),
not an impact result.

## Gaps found (reported, not fixed here)

- No published inventory of the target study; the PP pyrolysis yields that size the ethylene
  exchange are assumed.
- No open, documented background for virgin naphtha ethylene or propylene in the library;
  `processes/ethylene-1` is an ethane cracker, gate-to-gate, concept maturity, unreviewed.
- Mechanical recycling energy, sorting, pyrolysis utilities other than net electricity, and
  transport of the exchanged olefin are outside the inventory.
- No characterised impact category is reported: the source studies use ecoinvent, which cannot
  be published here, and the library holds no open factors for the missing backgrounds.
