# Markets and supply chains

> **Status: draft for decision**, like [system-model.md](system-model.md). It was written for
> process-library#49 from the coordinator's decisions of 2026-10-25. Most distances and losses of
> the first markets are ASSUMED screening values, labelled as such.

A plant dataset ends at the plant gate. ASU-1's liquid oxygen, for example, stops at its storage
tank. A consumer, though, takes the product where it is delivered: by road tanker, with some of
it boiled off on the way, or through a pipeline from the plant next door. **Markets** add that
step. A market is an activity of the Atlas database that takes its product from the Atlas
producers, weighted by production volume, and adds the transport and the losses on the way to
the consumer. When an Atlas input is made by another Atlas process, it links to the market by
default, not to a plant.

## Layers

The layering follows common LCI practice (ecoinvent's markets, and the plant / site / national
mix layers that Carbon Minds describes in its published cm.chemicals methodology):

| layer | what it is | in the library |
|---|---|---|
| **technology-specific** | one technology in one region | `layer: technology`, with `technology:`; code `market:<product>:<region>:<technology>`. A consumer chooses it explicitly. It is never the default link |
| **production mix** | the producers in a region, weighted by production volume | `layer: production-mix`; code `market:<product>:<region>`. It states how it stands for consumption (`consumption: {equals_production, reason}`) |
| **consumption mix** | production plus imports minus exports, with transport for the imports | `layer: consumption-mix`; code `market:<product>:<region>`. Its suppliers are domestic plants and the markets of other regions (`market: <region>`), with shares from trade data (`trade_source`) |
| **integrated site** | a plant on an integrated site takes from the site's own plants first, and the rest from the national consumption mix | documented below; built once a second process exists |

A region has one market that consumers link to: a production mix or a consumption mix.
Trade data (UN Comtrade, CEPII BACI) is packaged only if its licence allows redistribution under
CC BY 4.0. Until then a production mix takes consumption as equal to production and says why.

## A market file

`markets/<substance>.yaml`, schema [`schemas/markets.schema.json`](https://github.com/ChemE-as-Code/process-library/blob/main/schemas/markets.schema.json),
one file per substance with any number of markets:

```yaml
schema: cheme-as-code/markets/v1
markets:
  - product: nitrogen/lin          # a registry slug or <slug>/<grade>
    region: RER                    # ISO 3166-1 alpha-2, GLO, RER, RoW
    layer: production-mix
    consumption: {equals_production: true, reason: "..."}
    suppliers:
      - process: asu-1             # its activity of nitrogen/lin
        production_volume: {value: 3948, unit: t/a, status: calculated, source: "..."}
    distribution:                  # producers -> consumer, per kg delivered
      - mode: cryogenic-trailer
        use: lorry                 # a technosphere entry of lci/mappings.yaml, in ton kilometer
        distance: {value: 100, unit: km, status: assumed, source: "ASSUMED ..."}
    losses:
      - {kind: boil-off, fraction: 0.005, released_as: N2, status: assumed, source: "ASSUMED ..."}
    excluded: ["The customer's storage tank ..."]
```

- **Sources.** Every share, production volume, distance and loss has a `status` and a `source`.
  The status is `cited` (a source states the value), `calculated` (derived from cited or design
  values, and the source says how) or `assumed` (an estimate, written "ASSUMED ..." with the
  reason, to be replaced). No number is entered without one of these.
- **Weights.** Either every supplier has a `production_volume`, all in one unit, or every
  supplier has a `share`, and the shares sum to 1. A consumption mix uses shares.
- **Transport.** A leg is the mass carried times the distance, in ton kilometer, linked to the
  background through `use:`. The mass carried includes what is lost later in the chain. A
  pipeline that runs on the producer's delivery pressure names no activity: its distance is
  recorded, and its infrastructure is stated as outside the market.
- **Losses** multiply. The market takes `1 / prod(1 - fraction)` kg from its suppliers per kg
  delivered. The lost product is released as `released_as`: an emission of `lci/mappings.yaml`
  `biosphere` (hydrogen, methane, ...) is exported. An atmospheric constituent of `pass_through`
  (O2, N2, Ar) is not exported, as for the plants, and the activity comment says so.
- **Planned markets** (`planned:` with the reason, no suppliers) are listed in
  `datapackage.json` but not exported. In a public build, a market whose supplier is not public
  is `withheld`.

## In the database

`build_lci.py` writes each market as an activity of the same database (sheet `markets`). Its
name is `market for <reference product>`, its reference product the registry grade's name, its
location the region, and it delivers 1 unit. Its exchanges are the suppliers (Atlas activities),
the transport legs (background) and any exported releases. The comment states the layer, the
suppliers and their shares, the consumption statement, what is not exported and what is outside
the market. `datapackage.json` `markets` lists every market with its status, suppliers and
shares, gross input, and every number with its status and source. `index.json` lists the
exported markets. Market activities are part of the default cut-off database and of the
substitution variant.

## Chaining Atlas processes

When an input's chemical is made by another Atlas process, the build names an Atlas activity
beside the input's background link, and `install(prefer_atlas=True)` links to it:

1. **The candidates** are the other processes' activities of the input's chemical, in the same
   unit. A producer of the grade the input names comes first. **A producer of another grade is
   refused**: LIN never stands in for pipeline GAN. A refusal is recorded in `atlas_links`, and
   the input keeps its background link.
2. **The market** of the input's grade (or of the first candidate's grade when the input names
   only the substance) is the default target: the market of the consumer's region, else `GLO`,
   else `RER`, else the only one (`markets.choose`). A market supplied only by the consumer's own
   process is never chosen.
3. **The plant** stays beside the market (`atlas plant activity`) for pinning:
   `install(prefer_atlas="plant")` links every Atlas input to its plant, and
   `install(pin=["<activity code>"])` (or `"<code>/<atlas key>"`) pins single inputs. A dataset
   pins a plant itself with `link.dataset`.
4. **Without a market** of the grade, the link goes to the plant gate, and the build warns
   (`--strict` fails). A consumer of "nitrogen, liquid" must therefore find a market: the test
   `test_a_consumer_of_liquid_nitrogen_links_to_the_market` checks it for ASU-1's LIN.

### Compatibility check (core#168)

Every Atlas-to-Atlas link is checked: a consumer's input to a market or a plant, a market's
suppliers, a consumption mix's imports, and an explicit `link.dataset`. The result is written into
the workbook (`atlas check`, `atlas plant check`) and into `datapackage.json` (`atlas_links`:
consumer, key, provider, kind, compatible, checks). `install()` lists every link with it, and the
supply chains (`report.chains()`, e.g. *inerting <- market for nitrogen, liquid <- ASU-1 LIN*).

| aspect | ok | note | mismatch |
|---|---|---|---|
| reference product grade and state | the provider's grade is the input's | the input names only the substance, or the provider has no grade | another grade (refused before it is linked) |
| unit | the same unit (candidates are filtered by unit) | | |
| system model | one database, one system model | | |
| allocation | the provider's datasets follow the allocation hierarchy | a dataset with an allocation finding | |
| boundary | a market (delivered), or a plant feeding a market | a plant gate (pinned, or no market) | |

`install()` also compares the Atlas database's system model with the background's recorded
`system_model`. A different one, for example an APOS background under the cut-off Atlas, is a
warning in the report. The report prints the Atlas system model and methodology version too.

## Double counting

- **One market per product and region.** A process is in a chain once: as a supplier of the
  market, or pinned. An input never links to both.
- **Integrated sites** (concept, not built yet): a plant on a site with its own producer of an
  input (for example ammonia next to nitric acid, or an ASU on a steel site) takes the input
  from that plant first, as a pinned link, and only the rest from the national consumption mix.
  The site then needs a site dataset with the shares of each source. Shared utilities belong to
  the site, not to each plant (#45). This is built when the library has a second process that
  shares a site with another; until then every plant is a stand-alone plant feeding its markets.
- **CO2 along chains** (core#181): a CO2 input from an Atlas point source is a technosphere link,
  never a removal, and the source's capture is counted once, at the source.

## Regional and technology variants

A market is per region; the plant datasets stay the same foreground. Core's regional scenarios
(core#172, `lca/scenarios/`) change a plant's background (grid, location), and the markets of
other regions take those plant variants as their suppliers once they are exported as datasets of
their own. A technology market (`layer: technology`) keeps a single technology's supply for
comparisons (for example cryogenic versus PSA oxygen) without changing the regional mix.

## The first markets

| market | supplier | distribution | losses | status |
|---|---|---|---|---|
| `market:oxygen/lox:RER` | ASU-1 LOX (3948 t/a, calculated from the dataset) | cryogenic road tanker, 100 km, ASSUMED | boil-off 0.5 %, transfer 1 %, ASSUMED (O2, not exported) | exported |
| `market:nitrogen/lin:RER` | ASU-1 LIN (3948 t/a, calculated) | cryogenic road tanker, 100 km, ASSUMED | boil-off 0.5 %, transfer 1 %, ASSUMED (N2, not exported) | exported |
| `market:oxygen/gox-30barg-99.5:RER` | ASU-1 GOX (175224 t/a, calculated) | pipeline, 5 km, ASSUMED (no recompression) | leakage 0, ASSUMED | exported |
| `market:nitrogen/gan-8barg-10ppm:RER` | ASU-1 GAN (105084 t/a, calculated) | pipeline, 5 km, ASSUMED | leakage 0, ASSUMED | exported |
| `market:argon/lar:RER`, `market:argon/gar:RER` | none: ASU-1 has no argon column | | | planned |

What is behind the numbers:

- **Distances.** No open source with the delivery distance of merchant liquid oxygen or
  nitrogen in Europe was found. 100 km is the generic road distance for chemicals in ecoinvent
  v2's standard transport assumptions (Frischknecht et al. 2007), used as a placeholder. The
  background's lorry carries its average load factor, which covers the tanker's empty return; it
  has no cryogenic tanker activity.
- **Losses.** No open source with a boil-off or transfer loss per delivery was found. The values
  are ASSUMED and shown in every market comment. A pipeline leakage of 0 is recorded as ASSUMED
  rather than invented.
- **Outside the markets:** the customer's storage tank, its boil-off and the vaporiser (the
  consumer's system), ASU-1's own LOX and LIN tanks (the plant dataset ends at the tank), and
  pipeline infrastructure.
- **Production equals consumption:** UN Comtrade and CEPII BACI report oxygen (HS 2804.40) and
  nitrogen (HS 2804.30) without telling liquid from gas, and their terms are not yet checked for
  redistribution, so none is packaged.
- **Representativeness:** ASU-1 is the only Atlas producer. Each market stands for the Atlas's
  own cryogenic technology, not for the region's actual production, and the build's caveats say so.

A utility market (steam, cooling water) follows when the utility processes exist (#45).

## References

- Frischknecht, R., Jungbluth, N., et al. (2007). *Overview and Methodology*. ecoinvent report
  No. 1, Swiss Centre for Life Cycle Inventories, Dübendorf (standard transport distances).
- Weidema, B. P., et al. (2013). *Overview and methodology. Data quality guideline for the
  ecoinvent database version 3*. ecoinvent report 1 (v3) (market activities and their layers).
- Carbon Minds GmbH, *cm.chemicals database methodology*, version 2.03, 2026 (layered model:
  plant, integrated site, national mixes; cited for its approach only, no content reproduced).
