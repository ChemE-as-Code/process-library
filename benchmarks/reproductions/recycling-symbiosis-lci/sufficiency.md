# Data sufficiency: linked LDPE and PP recycling inventories

Written 2026-11-04, before any comparison run, to decide the scope of #339 (tracker #333).
The sources are pinned in `source.yaml`.

## What the issue asks for

Recover traceable inventory inputs and a common functional basis for one published scenario of
the TU Delft / URV study. Compare a disconnected and a linked configuration. Reconcile the
exchanged quantity, the displaced production and the coproduct treatment. Report impacts only
with documented background data and methods.

## What exists

| Item | Where | Licence | Usable for |
| --- | --- | --- | --- |
| Target study: conference abstract (El Khoury, Somoza-Tornos, Pozo, Jimenez 2025) | TU Delft portal record; SETAC Europe 2025 abstract book, p. 1081 | none stated | scenario definitions and qualitative findings (facts, restated) |
| Fuller version of the target (paper, thesis, SI, dataset) | not found (OpenAlex, Crossref, Zenodo, 4TU, web search, 2026-11-04) | - | - |
| Related chapter by the same group (El Khoury, Jimenez, Pozo 2024, ESCAPE-34) | Elsevier, doi:10.1016/B978-0-443-28824-1.50183-6 | closed, no repository copy | not read |
| PE pyrolysis-to-monomer process model (Somoza-Tornos et al. 2020) | ACS Sust. Chem. Eng. 8, 3561; accepted manuscript on UPCommons (the version read) | CC BY 4.0 (published, not read), CC BY-NC-ND 3.0 ES (manuscript) | global reaction, recoveries, inventory per kg ethylene, prices |
| PP pyrolysis-to-monomer inventory | no open, citable product distribution found (search below) | - | - |
| Mechanical recycling inventories (yields, energy) | not searched in depth; the abstract cites "the literature" without naming it | - | - |
| Background data for virgin ethylene and propylene | the library's `processes/ethylene-1/lca/inventory.csv` (gate-to-gate, ethane cracker) | CC BY 4.0 | screening direct CO2 of displaced olefin |
| Characterised background (ReCiPe etc.) | ecoinvent in the source studies | licensed | not used (CLAUDE.md) |

## Search for PP pyrolysis yields (recorded after review, 2026-11-04)

The first build recorded only "no open source found in the time given". After review the
search was repeated and recorded:

- OpenAlex works search, open-access filter, sorted by citations: "polypropylene pyrolysis
  ethylene propylene yield fluidized bed". The top 15 hits were reviews and unrelated work; none
  gives a PP product distribution. Title-filtered OpenAlex queries ("polypropylene pyrolysis
  light olefins", "thermal cracking polypropylene olefins", "polypropylene steam cracking
  olefins", "pyrolysis polypropylene gas composition temperature") returned API errors on that
  day and gave no result.
- Web search: "polypropylene pyrolysis ethylene propylene methane yield wt% open access
  fluidized bed 700 °C" and "polypropylene pyrolysis product distribution ethylene propylene
  wt% 750 °C open access". Leads found, none read or used: a microwave-assisted fluidised-bed PP
  pyrolysis study (Applied Energy 342, 2023; not open access), a high-temperature HDPE and PP
  pyrolysis study in Reaction Chemistry & Engineering (2026, doi:10.1039/D5RE00442J, listed as
  CC BY; its focus appears to be hydrogen and carbon), an MDPI Polymers paper on PP and HDPE
  pyrolysis (doi:10.3390/polym17222968; gas composition, conditions not checked), and patents
  on PE.
- Not searched: the Hamburg fluidised-bed pyrolysis work on polyolefins (closed journals) and
  theses.

Result: no PP yields at a severity comparable to the PE model were taken from a source. The
yields stay ASSUMED; `inputs.yaml` gives a low/high range and `comparison.md` a sensitivity.
Reading the two open leads is the next step (follow-up, not done here).

## What is missing for a numerical reproduction of the target

- the functional unit and the scale of each supply chain;
- the split between mechanical and chemical recycling, the mechanical yield and where rejects go;
- the pyrolysis yields used for LDPE and for PP;
- what is exchanged in scenario S4, in what quantity, and what it replaces;
- the allocation or substitution rule for coproducts;
- the background database, its version and system model, and the impact method;
- any numerical result other than impact shares (the abstract has no absolute value).

Without these, none of the reported numbers (contribution shares of 26 to 51 %, avoided shares
of 9 and 14 %) can be recomputed. **The target reproduction is not achievable.**

## Achievable scope (decided here)

1. **Component reproduction.** The step that creates an exchangeable stream is pyrolysis: it
   yields both olefins whatever the polymer. For PE this step is published openly, by two of the
   target's authors, with a global reaction and column recoveries. We recompute its inventory per
   kg ethylene (feed, methane, propylene, benzene, direct CO2) and compare with the published
   table under frozen tolerances. This is a reproduction of a model result, not validation.
2. **Mass-inventory reconciliation of the two chains** on a stated common basis (1 t sorted
   waste per chain, the same mass of polymer delivered), with every missing parameter labelled
   ASSUMED in `inputs.yaml`. Three configurations: disconnected with the other olefin burnt,
   disconnected with it sold, and linked. The reconciliation shows the exchanged quantity, the
   virgin monomer it displaces, and the coproduct treatment under the library's cut-off model
   (ADR 0007) with mass allocation (docs/system-model.md, step 3).
3. **Environmental inventory only where the data are publishable:** foreground direct fossil CO2
   from carbon balances, net electricity as an inventory flow (not characterised), and the
   gate-to-gate direct CO2 of the displaced olefin from the library's own ethylene-1 dataset as a
   screening value, with its gaps named. No characterised impact categories.
4. **One changed input** (`extension.md`): the PP waste throughput relative to LDPE, which shows
   when the exchange saturates.

## Main evidence gaps

- PP pyrolysis yields are assumed, not sourced; they set the size of the ethylene exchange.
- The PE model is applied to LDPE unchanged (an assumption).
- Recovered 99.5 wt% ethylene is counted as polymer grade (an assumption).
- Utilities other than net electricity, mechanical recycling energy, and transport of the
  exchanged olefin are not in the inventory.
- The displaced-olefin value is gate-to-gate and from an ethane route, while European olefins
  come mainly from naphtha.
