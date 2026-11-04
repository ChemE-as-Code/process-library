# Design extension: PP waste throughput against a fixed LDPE chain

> **HYPOTHETICAL design extension, not validated.** It uses the reconstructed LDPE pyrolysis
> model, the ASSUMED PP pyrolysis yields and the ASSUMED recycling shares of `inputs.yaml`. No
> source reports any of these results.

## Changed input

One input changes: the sorted waste PP treated, `functional_basis.waste_PP_sorted`, from
1000 kg to **4000 kg**, with the LDPE batch fixed at 1000 kg and everything else unchanged.
The configuration is L (linked). `run.py` also sweeps 100 to 6000 kg for the figure
(`results/extension-pp-throughput.svg`); the values are in `results/comparison.json`
(`extension`).

## Result

| Linked configuration | Base (1000 kg waste PP) | Changed (4000 kg waste PP) |
| --- | --- | --- |
| Ethylene received by the LDPE chain | 93.8 kg | 336.4 kg |
| Share of the LDPE chain's monomer demand (625 kg) met by the exchange | 15 % | 54 % |
| Virgin ethylene still bought by the LDPE chain | 242.6 kg | 0 kg |
| Ethylene surplus the PP chain must sell | 0 kg | 38.6 kg |
| Propylene received by the PP chain | 108.6 kg | 108.6 kg |
| Virgin propylene bought by the PP chain | 328.9 kg | 1641.4 kg |
| Virgin olefin saved against D_fuel (other olefin burnt) | 202.4 kg | 445.0 kg |
| Virgin olefin saved against D_market, system expansion | 0 kg | 0 kg |

The exchange saturates at **3588 kg waste PP, 3.6 times the LDPE batch**. There the ethylene
from the PP plant (0.15 kg per kg pyrolysis feed, 0.625 kg feed per kg waste) equals the LDPE
chain's remaining demand after its recyclate and its own ethylene (336.4 kg).

## Engineering consequence

- The benefit of the link is capped by the receiver's monomer deficit, not by the sender's
  output. With equal batches the LDPE chain can absorb up to 3.6 times the ethylene the PP
  plant offers it; the PP chain absorbs all of the LDPE plant's propylene at any PP throughput
  above about 250 kg, because its own propylene covers only 30 % of its monomer demand.
- Beyond saturation the extra ethylene has to leave the pair again, as in D_market. Sizing an
  exchange line or storage for more than the receiver's deficit gives no further saving.
- The saving against a market outlet is zero at every throughput under system expansion. The
  link pays off physically only where the other olefin would otherwise be burnt, or where
  selling it is not possible (no buyer for small, intermittent off-gas olefin streams). Whether
  that holds is a site question, not a property of the chemistry.
- The saturation point scales inversely with the PP plant's ethylene yield. At 0.10 kg/kg it
  moves to 5.4 times the LDPE batch; at 0.20 kg/kg to 2.7 times (comparison.json
  `sensitivities.pp_yields`). This yield is assumed, so the number 3.6 is illustrative.

## Out of range and extrapolation flags

- PP pyrolysis yields: assumed, no source. They set the ethylene supply and the saturation point.
- The LDPE model is a PE model at one severity (1000 degC); no temperature dependence is used.
- The model is linear in throughput: no economies of scale, no minimum plant size, no change of
  pyrolysis conditions with feed rate.
- The 4:1 throughput ratio is outside anything the sources discuss.
- The PP chain's virgin propylene rises with its own throughput because the basis delivers as
  much polymer as it collects; that is a property of the basis, not of the link.
