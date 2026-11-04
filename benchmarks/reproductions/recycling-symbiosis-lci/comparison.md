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
  Output `results/comparison.json` and three SVG figures. Rerun after review from an empty
  cache; two runs gave byte-identical results. The component source (UPCommons accepted
  manuscript) and the target's abstract book were downloaded into the cache and both matched
  their pinned sha256. The library file `processes/ethylene-1/lca/inventory.csv` is read as
  committed at the pinned commit 7943fe1 (`git show`), which is reachable from main; it matched
  its pinned sha256, as does the working-tree copy. Rerun after the second review from an empty
  cache, with the same result files byte for byte.
- **Revised after review** (same day, after the first comparison run): the frozen
  `tolerances.yaml` and every input of the component checks are unchanged, so the component
  verdict is the one first reported. Changes to the reconciliation are listed under
  [Changes after review](#changes-after-review).

## Verdict under the frozen rule: FAIL (target: not achievable)

| Part | Result |
| --- | --- |
| Target reproduction (El Khoury et al. 2025) | **not achievable**: no inventory inputs published; every reported result is a share of characterised impacts on an unnamed licensed background |
| Component reproduction (Somoza-Tornos et al. 2020, Table 2) | **fail**: 4 of 5 checks pass; benzene is 6.3 % low against a 3 % tolerance |
| Reconciliation checks (mass, carbon, exchange identity, allocation conservation) | all hold to rounding (relative error 0) in all three configurations, the extension and the sensitivities. They are bookkeeping checks inside one model: they catch routing and supply errors, not errors in the model's inputs. The carbon check holds by construction for the pyrolysis units, whose element balance is reported separately below |
| Direction check against the target's claim (S4 lowest) | consistent on inventory indicators (does not count for the verdict) |

The pass rule makes the case verdict "fail" when a component check fails. That is the result.
It does not make the olefin mass reconciliation below wrong: the olefin flows (exchanged, bought,
sold) need only the ethylene and propylene yields of the PE model, and both pass. Every other
reconciliation row uses the benzene and fuel split that fails: the direct CO2 rows, the
per-folder allocation and the exported-product masses inherit its deviation of about 4 to 5 %.

**The direct CO2 check is not independent evidence.** It passes at +4.03 % only because the
frozen allowance is 5 %. The rounding of the Eq. 1 coefficients bounds the CO2 deviation at
about ±2 % (every coefficient varied by ±0.005, all sign combinations: 1.0058 to 1.0458 kg/kg
ethylene, ±1.95 %; with the 0.5 % purity term still about 2.5 %). The +4.03 % is the same
benzene and fuel shift as the benzene failure (item 1 below), not rounding. The frozen reason
cites "up to 7 %" for the small coefficients 0.07 and 0.09; those are relative errors of small
terms, not of the CO2 total, so the 5 % is wider than its own reason supports. The CO2 is
therefore not reproduced within the precision of the inputs. The tolerance is left as frozen;
a revision would be a new file, with tolerances derived from a perturbation envelope like the
one above.

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
and 3.24 kg in ours. The CO2 status "pass" rests on the frozen 5 % allowance only (see above).

### Deviations and explanations

1. **Benzene and fuel are shifted against each other.** Our benzene is 0.018 kg/kg ethylene
   low and our fuel 0.016 kg/kg high; the feed, ethylene, propylene and methane agree within
   0.5 %. So in the source simulation about 0.017 kg/kg ethylene that Eq. 1 with a 99 % benzene
   recovery sends to the T4 top (fuel) ends up in the benzene product. Candidate causes, not
   resolvable from the paper: the simulation's reactor used a benzene coefficient other than
   the printed 0.45 (0.48 would give 0.2867 kg and move the feed by +0.63 %, to 2.1837 kg), or
   the benzene line holds C4 or C3 material from the T4 bottoms, which would contradict the
   stated 99.5 wt% purity (butadiene and butenes boil about 85 K below benzene). A 1.1 %
   rounding allowance cannot cover 6.3 %.
2. **Direct CO2 +4 %.** Follows from the larger fuel stream (item 1); it is the same deviation,
   not a second one, and lies outside the ±2 % rounding envelope. The CO2 per kg of fuel agrees
   within 1.2 %, so the combustion bookkeeping is consistent.
3. **Eq. 1 is not element-balanced.** Its products correspond to C20.04 H39.38 per
   pseudo-mole: a hydrogen deficit of 1.75 % against the CH2 polymer (H = 2 C = 40.08), or
   1.55 % against C20H40 (H = 40). The rationale in `inputs.yaml` (frozen with the tolerances)
   says 1.5 %, which is the second reference rounded; the 1.75 % here is the one that matters
   for the CH2 polymer. In mass, the missing hydrogen is 0.25 % of the product mass, the
   "0.2 % of mass" in `tolerances.yaml`. We normalised the product masses (`inputs.yaml`), so
   the products carry 0.8584 kg C per kg feed against 0.8563 for CH2: the reconstructed model
   creates 0.0022 kg C per kg feed (+0.25 %), 1.35 kg C in the LDPE folder of the base case
   (comparison.json `pyrolysis_element_balance`). The effect on the compared numbers is below
   0.3 %.
4. **Purity not attributed.** Products are taken as the recovered key component only; the
   0.5 wt% impurities would raise each product mass by at most 0.5 %.

## Mass-inventory reconciliation (achievable scope)

Basis: 1000 kg sorted waste LDPE and 1000 kg sorted waste PP; each chain delivers 1000 kg
polymer. Half of each waste goes to mechanical recycling at 75 % yield (375 kg recyclate), the
rejects and the other half (625 kg) to pyrolysis. Every assumption is labelled in `inputs.yaml`.
PP pyrolysis yields are ASSUMED (no open source found; the search is in `sufficiency.md`). A
"folder" here is the sub-inventory of one chain (LDPE or PP) inside this case. No
`processes/<id>/` folder exists for either chain, and these results are not design data for
one (ADR 0030).

| Combined system (both chains) | D_fuel: disconnected, other olefin burnt | D_market: disconnected, other olefin sold | L: linked |
| --- | --- | --- | --- |
| Virgin ethylene bought | 336.4 kg | 336.4 kg | 242.6 kg |
| Virgin propylene bought | 437.5 kg | 437.5 kg | 328.9 kg |
| Olefin exchanged between chains | 0 | 0 | 202.4 kg (108.6 kg propylene to PP, 93.8 kg ethylene to LDPE) |
| Olefin sold to the market | 0 | 202.4 kg | 0 |
| Olefin burnt as fuel (flared or burnt with no use for its heat, assumed) | 202.4 kg | 0 | 0 |
| Net virgin olefin, system expansion view | 773.9 kg | 571.5 kg | 571.5 kg |
| Methane and benzene sold | 133.8 kg and 127.6 kg | same | same |
| Foreground direct fossil CO2 (pyrolysis furnaces) | 1634.8 kg | 999.8 kg | 999.8 kg |
| Net electricity (inventory flow, not characterised) | 262.1 kWh | 262.1 kWh | 262.1 kWh |
| Gate-to-gate direct CO2 of the virgin olefin bought (Atlas ethylene-1, 0.4326 kg/kg, mass-allocated) | 334.8 kg | 334.8 kg | 247.2 kg |

The direct CO2 rows inherit the benzene and fuel split of the LDPE model (about 4 to 5 % high
against the source table, item 1) and the assumed PP yields.

Reconciliation of the exchange: the propylene the LDPE folder sends (108.6 kg) equals what the
PP folder receives, and the PP folder's virgin propylene falls from 437.5 to 328.9 kg, by
exactly that amount. Likewise 93.8 kg ethylene from PP to LDPE, virgin ethylene 336.4 to
242.6 kg. Neither receiver is saturated in the base case.

**What linking changes depends on the counterfactual.** Against D_fuel, linking saves 202.4 kg
virgin olefin and up to 635 kg direct CO2 (the burnt olefin's carbon, 3.14 kg CO2/kg). The
635 kg is an upper bound: D_fuel assumes the burnt olefin is surplus fuel whose heat has no use,
because each furnace is already fired by its own remainder stream. If its heat (9394 MJ, lower
heating value) displaced natural gas one to one (0.0561 kg CO2/MJ), the net CO2 avoided would
be 108 kg (comparison.json `sensitivities.D_fuel_heat_credit`). Against D_market, the combined
system buys 202.4 kg less virgin olefin under cut-off accounting, but with system expansion
(the sold olefin displaces virgin olefin elsewhere) the net virgin olefin and the direct CO2 are
identical. The exchange then only moves the displacement from the market into the partner
folder. Our inventory indicators are therefore consistent with the abstract's ranking (S4
lowest) only when the disconnected chains do not use the other olefin as a material. Whether S3
used that counterfactual, and what S4 exchanged, is not stated; the abstract's finding is about
characterised impacts on an unnamed background, which this case does not compute. A study that
credits every pyrolysis coproduct in both chains (avoided burden, as Somoza-Tornos et al. 2020
did) would find no difference from the exchange as such, apart from logistics.

### Coproduct treatment and per-folder attribution (cut-off, mass allocation)

Allocation rule: the WBCSD step (step 3) of docs/system-model.md. The price ratio of the
pyrolysis coproducts (ethylene 1.075, benzene 0.994, propylene 0.875, methane 0.334 EUR/kg;
source Table 1) is 3.2, below 5, so mass. Each plant's direct CO2 is shared over its products
per kg. Step 2 (energy content for co-produced fuels) is a curated decision and is not applied:
three of the four products are chemical feedstocks and only methane is a fuel
(`inputs.yaml` `coproduct_treatment.allocation_rule.step_2_not_applied`). As a sensitivity,
energy (LHV) allocation changes the foreground CO2 carried by each polymer by at most 2.1 %
(LDPE in D_market, 160.1 to 163.6 kg; comparison.json `sensitivities.energy_allocation`).

| Per folder, cut-off | D_fuel LDPE | D_fuel PP | D_market LDPE | D_market PP | L LDPE | L PP |
| --- | --- | --- | --- | --- | --- | --- |
| Plant direct CO2 per kg product | 1.499 kg/kg | 3.193 kg/kg | 0.555 kg/kg | 1.732 kg/kg | 0.555 kg/kg | 1.732 kg/kg |
| Foreground CO2 carried by the folder's polymer | 432.6 kg | 598.7 kg | 160.1 kg | 324.8 kg | 322.5 kg | 385.1 kg |
| Foreground CO2 leaving with exported products | 204.3 kg | 399.2 kg | 135.9 kg | 378.9 kg | 75.6 kg | 216.5 kg |
| Virgin monomer bought | 336.4 kg | 437.5 kg | 336.4 kg | 437.5 kg | 242.6 kg | 328.9 kg |

The allocated parts sum to the unallocated total in every configuration (allocation
conservation check). In L, received olefin carries its sender's allocated burden: the LDPE
folder takes over 93.8 kg x 1.732 = 162.4 kg CO2 from the PP plant and buys 93.8 kg less
virgin ethylene, whose gate-to-gate direct CO2 in the Atlas ethane cracker is 40.6 kg
(0.4326 kg/kg, mass-allocated). The effect on the LDPE folder's polymer depends on the
counterfactual. Against D_market (other olefin sold), linking makes its foreground direct CO2
look worse (160.1 to 322.5 kg), because the assumed PP plant burns 0.35 kg of each kg of feed.
Against D_fuel (other olefin burnt), linking improves it (432.6 to 322.5 kg), because the LDPE
plant no longer burns its propylene. This is a screening comparison with gaps on both sides
(pyrolysis utilities beyond electricity, ethane and power upstream of the cracker), not an
impact result.

### Pyrolysis element balance (diagnostic, not a frozen check)

| Model, per kg feed | Carbon in feed (CH2) | Carbon in products and fuel | Imbalance |
| --- | --- | --- | --- |
| LDPE (Eq. 1, normalised; reconstructed) | 0.8563 kg | 0.8584 kg | +0.0022 kg (+0.25 %), from Eq. 1 itself |
| PP (assumed yields) | 0.8563 kg | 0.8563 kg | 0 by construction: the remainder takes the carbon the products do not hold (0.878 kg C/kg, H/C 1.66) |

The frozen carbon-closure check (`tolerances.yaml`, rel 1e-9) takes every hydrocarbon input as
CH2 and adds the LDPE model's +1.35 kg C as a declared term, so it tests the routing, burning
and export of carbon in each folder. It cannot detect an element imbalance inside a pyrolysis
model; that is what the table above reports. Without the declared term the LDPE folder closes
to 1.2e-3, not 1e-9 (comparison.json `rel_against_CH2_without_model_term_diagnostic`).

### Sensitivity to the assumed PP pyrolysis yields (not frozen checks)

One yield varied at a time over the assumed range in `inputs.yaml` (`pyrolysis_PP.sensitivity_range`);
the remainder takes up the difference and closes the carbon on CH2.

| PP yield varied | Ethylene to LDPE chain | Virgin olefin saved by L against D_fuel | Direct CO2, D_fuel / L | Extension saturation (waste PP / waste LDPE) |
| --- | --- | --- | --- | --- |
| Base (C2H4 0.15, C3H6 0.30 kg/kg) | 93.8 kg | 202.4 kg | 1634.8 / 999.8 kg | 3.6 |
| C2H4 0.10 kg/kg | 62.5 kg | 171.1 kg | 1634.8 / 1097.8 kg | 5.4 |
| C2H4 0.20 kg/kg | 125.0 kg | 233.6 kg | 1634.8 / 901.7 kg | 2.7 |
| C3H6 0.20 kg/kg | 93.8 kg | 202.4 kg | 1830.9 / 1195.9 kg | 3.6 |
| C3H6 0.40 kg/kg | 93.8 kg | 202.4 kg | 1438.7 / 803.7 kg | 3.6 |

The propylene sent to the PP chain (108.6 kg) does not depend on the PP yields. The ethylene
exchange and the saturation point scale with the PP ethylene yield; the PP propylene yield
moves only the PP chain's virgin propylene and its fuel.

## Changes after review

Made after the first comparison run, with the frozen `tolerances.yaml` and the component inputs
unchanged:

1. **PP remainder carbon.** The first run took the 0.35 kg/kg PP remainder as CH2, which lost
   0.0076 kg C per kg feed (0.9 % of the feed carbon: 4.76 kg C, 17.4 kg CO2 per 1000 kg waste
   PP). The carbon check did not see it, because it took the carbon in from the model's own
   products. The remainder now closes the carbon on CH2: PP direct CO2 rises from 1.098 to
   1.126 kg/kg feed, the combined direct CO2 from 1617.4 to 1634.8 kg (D_fuel) and from 982.4 to
   999.8 kg (D_market, L). The carbon check now takes the inputs as CH2 (above).
2. **Displaced-olefin factor.** `processes/ethylene-1/lca/inventory.csv` already carries the
   mass allocation (ethylene-1 D-016); the first run divided it by the product sum a second
   time (0.396 instead of 0.4326 kg/kg). Virgin-olefin gate CO2 changes from 306.5 / 306.5 /
   226.3 kg to 334.8 / 334.8 / 247.2 kg, and the LDPE folder's avoided virgin ethylene from
   37.1 to 40.6 kg. The qualitative conclusion is unchanged.
3. **Labels.** Our modelling choices (PE model for LDPE, one-to-one olefin substitution,
   complete combustion and routing of all unrecovered material to fuel, the cracker value for
   propylene, the allocation decision) are now labelled assumed in `inputs.yaml`.
4. **New sensitivities:** the burnt-olefin heat credit, energy allocation and the PP yields.
5. **Wording:** the CO2 pass, the reach of the component failure, the D_fuel upper bound and the
   consistency with the abstract's ranking, as above.

Second review (no result changed; every number above is as before):

6. **Reconciliation checks made independent.** As first written, the exchange identity could
   not fail: it compared the received olefin with the sent olefin times the substitution ratio,
   and the virgin monomer with the deficit less the received olefin, which is how `run.py`
   computes both. The mass and carbon closures also cancelled in their monomer terms, because
   they took the polymer made from the monomer supply itself. The checks now rebuild the out
   side from the primary inputs: the exchange identity compares the received olefin with the
   sender's recovered other olefin less what it sold and burnt, and the receiver's own,
   received and virgin monomer with its demand recomputed from waste, delivery basis and
   mechanical split; the mass and carbon closures take the polymer from the delivery basis.
   A changed virgin, received or sold olefin now fails them (tested by perturbing each by 1 kg).
   They remain checks of bookkeeping inside one model, not evidence on its inputs. The frozen
   rule (`tolerances.yaml` reconciliation_checks) is unchanged and is not at fault: it states
   what must hold, and the first implementation did not test it independently. All checks
   still hold to rounding, so the verdict is unchanged.
7. **Pinned library file.** `run.py` read the working-tree
   `processes/ethylene-1/lca/inventory.csv` and only warned if it differed from the pinned
   sha256, so a later change to that file would have changed the displaced-olefin results
   silently. It now reads the file at the pinned commit with `git show` and stops if the
   commit is not reachable from main or the content does not match the pinned sha256.
8. **Download cache.** On a sha256 mismatch the downloaded file replaced the cached copy. The
   download is now checked before it is moved into the cache; on a mismatch it is discarded,
   the cached copy is kept and the status records "hash mismatch".

## Gaps found (reported, not fixed here)

- No published inventory of the target study; the PP pyrolysis yields that size the ethylene
  exchange are assumed.
- No open, documented background for virgin naphtha ethylene or propylene in the library;
  `processes/ethylene-1` is an ethane cracker, gate-to-gate, concept maturity, unreviewed.
- Mechanical recycling energy, sorting, pyrolysis utilities other than net electricity, and
  transport of the exchanged olefin are outside the inventory.
- No characterised impact category is reported: the source studies use ecoinvent, which cannot
  be published here, and the library holds no open factors for the missing backgrounds.
