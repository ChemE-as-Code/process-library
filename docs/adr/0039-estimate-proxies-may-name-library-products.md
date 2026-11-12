# 0039. An LCI proxy may name library products with an amount, and stays visibly an estimate

- **Status:** Proposed, 2026-11-12
- **Deciders:** the owner, as the library's maintainer (drafted by an agent session for issue #419)
- **Scope:** the LCI pipeline: the shared mappings `lci/mappings.yaml` (`proxies:`), its schema
  `schemas/lci-mappings.schema.json`, `scripts/build_lci.py` and `scripts/lci_activities.py`
  (the Atlas LCI database, `datapackage.json`). It extends the screening proxies of
  [ADR 0008](0008-brightway-workbook-linked-by-name.md) and the gap rule of
  [ADR 0022](0022-lci-gaps-for-unpublished-processes-and-per-process-mappings.md) and
  [ADR 0026](0026-public-processes-may-be-preliminary.md); it changes neither.

## Context

A feed that no library entry makes is either linked to a background activity, or a gap
(ADR 0026: a correct gap rather than a doubtful link). Some of these feeds have a sound
stoichiometric estimate from products the library does make: chlorosulfonic acid is made from
SO3 and HCl, potassium tert-butoxide from tert-butanol and potassium, ammonium chloride from
ammonia and HCl. Two limits kept such an estimate out of the database (#418, #419):

- a **per-process override** (`processes/<id>/lca/mappings.yaml`, ADR 0022) links a whole
  exchange, kg for kg, to one Atlas producer or one background entry: no amount, no split;
- a **shared proxy** (`lci/mappings.yaml` `proxies:`) is an activity of the Atlas database
  whose inputs are background entries only; `build_lci.py` refused anything else.

So `p-toluenesulfonyl-chloride-1` recorded its chlorosulfonic-acid proxy (SO3 + HCl) in its
`DESIGN.md` and left the feed a gap, `hda-1` sent its split hydrogen proxy to the background, and
`di-tert-butyl-dicarbonate-1` waited for a dedicated `potassium-tert-butoxide-1` entry (#418,
option 1). A gap counts no burden; leaving a known feed out understates the footprint by more
than an honest estimate would.

The main risk of linking an estimate is that it reads as modelled. An Atlas page, a Brightway
user or a route comparison should never take a chain that rests on a proxy for a chain of
modelled plants. Options considered:

1. **Per-process proxies** (an override with inputs and amounts): each consumer would write its
   own copy of the same estimate, and each copy would become its own activity or a split of the
   consumer's exchange. Rejected: the same substance would be estimated differently in different
   places, and an exchange split into parts no longer matches the dataset core wrote.
2. **Shared proxies extended to name library products** (chosen): one activity per estimated
   substance in the database, reviewed once, used by every consumer through the existing
   lookup (a `chemical` slug or a `use` override), and replaced in one place when a dedicated
   entry arrives.
3. **Keep gaps until a dedicated entry exists** (#418 option 1): right where an entry is worth
   building, but it leaves every other such feed out of the footprint.

## Decision

**An estimate proxy is a shared proxy with a `basis`.** In `lci/mappings.yaml` `proxies:`
(schema `schemas/lci-mappings.schema.json` `$defs/proxy`), a proxy that states `basis` also
states the registry slug of the substance it stands for (`chemical`). Its inputs may name

- a background technosphere entry (`use`, as before), or
- a **library product**, `dataset: {path, product}` (the form of an override's `dataset`), with
  its `amount` per unit of the proxy in the unit of that product,

and an input that is a mixture counts one component on the basis with `content: {component,
fraction}`. A proxy without `basis` is a unit or screening proxy as before: background inputs
only, no estimate marking. Per-process mappings do not get proxies of their own: a consumer's
`lca/mappings.yaml` names the shared proxy through a `chemical` slug or `use`.

**The basis is checked.** `basis: mass` (a mixture or split) and `basis: stoichiometric` (the
reactants of the stated `reaction`, from molar masses) conserve mass: the proxy is in kilogram,
every input is in kilogram, and the inputs' masses on the basis (amount times the content's
fraction) sum to 1 kg per kg within 0.001. `basis: non-mass` declares another basis in
`basis_reason` and is not mass-checked. A content fraction must agree with the composition the
linked product states. The build refuses (an error) a mass that is not conserved and a unit
that does not fit the basis (when it loads the mappings), and, once an exchange uses the proxy
(so that a library holding part of the processes still builds), an unregistered `chemical`, a
content its product contradicts, and:

- **a missing product**: a `dataset` input that is not a product of the library;
- **a circular link**: an estimate proxy whose inputs reach back to it, through the library
  products it names, their datasets' links inside the Atlas (pinned, market, plant, a market's
  suppliers) and the exchanges linked to proxies.

**A dedicated producer takes precedence.** When the build holds a library producer of the
proxy's `chemical` (by the same rules as any Atlas link: the market of the grade, else the
plant, refused for another grade), an exchange mapped to the proxy links that producer directly
inside the Atlas instead, and the build advises (a warning that does not fail `--strict`) that
the proxy can be removed. The proxy is then not exported unless another consumer still uses it.

**A proxy stays visibly an estimate.** Every exchange linked to an estimate proxy is marked in
the exported dataset:

- the workbook columns `atlas proxy` (its id) and `atlas estimate` (the text: which proxy, the
  substance, the basis, the penalty), the activity's `atlas estimates` count and an `ESTIMATE:`
  line at the top of its comment; the openLCA and multifunctional exports carry the same columns;
- a **data-quality penalty consistent with the DQR**: the exchange's further technological
  correlation, the fifth pedigree score and the one core's TfS rating reads as TeR, is raised to
  at least 4 ("data on related processes or materials", ecoinvent data quality guideline), so
  the exported pedigree and the lognormal it implies widen. The dataset's `data_quality` in
  `datapackage.json` is recomputed with the penalised scores (TeR, DQR and DQR_PEF, as core's
  unweighted rating computes them) when the dataset's pedigrees reproduce the manifest's rating,
  and records `proxy_penalty` (the exchanges, the rule, the values before); a weighted rating, or
  one the build cannot reproduce, is kept with `proxy_penalty.recomputed: false`;
- `datapackage.json` `activities[]`: `estimated` and `estimates` on the consumer, an `estimate`
  object (the proxy's code, the text, the pedigree before the penalty) on the exchange, and on
  the proxy's own entry `estimate` (the chemical, the basis), `preliminary` when a library
  product it names is preliminary, and `publication: preview` unless every one of them is
  public. A library product is linked inside the Atlas with its compatibility check
  (`atlas_links`, kind `proxy`).

**The public build stays fail-closed.** A public build that does not hold a library product an
estimate proxy names (its process is not public) cannot use the proxy: an exchange mapped to it
is a gap there (ADR 0026), never linked to a partial proxy.

## Consequences

- A feed with an honest estimate from library products counts a burden instead of none, and the
  footprint rests on the library's own plants where it can. `p-toluenesulfonyl-chloride-1`'s
  chlorosulfonic acid is the first use (SO3 from the background, since `sulfuric-acid-1` makes
  no SO3 or oleum product; HCl from `hydrogen-chloride-1`; its `DESIGN.md` D-016).
- An Atlas page, a Brightway user and a reviewer see the estimate on the exchange, the activity,
  the proxy and the DQR. Results from a proxied chain are still lower bounds: a stoichiometric
  proxy leaves out the conversion step itself (its energy, yield, purification, transport).
- A dedicated entry replaces a proxy with no change to the consumers' mappings, and the advisory
  says when a proxy is obsolete.
- The penalty is a convention: TeR at least 4 for every proxied exchange, whatever the quality of
  the estimate. The recomputed DQR stays core's method only for an unweighted rating; a weighted
  one keeps core's value and says so. The catalog's route comparison (`scripts/routes.py`) still
  reads core's rating from `lca/manifest.json`, which knows nothing of the Atlas links: a
  follow-up if routes come to depend on proxied feeds.
- The circular check follows the Atlas alternatives too (`prefer_atlas`), so it refuses a proxy
  that would only be circular when installed with the Atlas links preferred; that is the default
  install.
- The `use`-only proxies (unit conversions, the screening proxies of ASU-1) are unchanged and not
  marked as estimates: they convert units or carry stated material take-offs, not a substance
  stood in for by others. Marking the screening ones too is a separate decision.
- Not decided here: estimate proxies whose input is a gap (an unlinkable part keeps the whole
  exchange a gap), proxies in `substitution:` with library products (allowed by the schema,
  untested), and a per-process proxy.

## Evidence

- Issue #419 (this decision), #418 (the KOtBu case, option 1 taken there with a dedicated entry).
- `schemas/lci-mappings.schema.json` `$defs/proxy` and `$defs/dataset_ref`;
  `scripts/build_lci.py` (`_proxy_basis_problem`, `check_estimate_proxies`, `_supersede_proxy`,
  `_estimate`, `circular_proxies`, `penalised_rating`, `ESTIMATE_TECHNOLOGY_SCORE`);
  `scripts/lci_activities.py` (`estimate`, `estimated`, `estimates`).
- `tests/test_lci_estimate_proxies.py`: mass on the basis, a declared non-mass basis, a missing
  product, a content its product contradicts, a circular link, a dedicated producer's
  precedence, the estimate marked with its penalty and recomputed DQR, the public build's gap,
  and the library's chlorosulfonic-acid proxy.
- `lci/mappings.yaml` `proxies.chlorosulfonic-acid`, `technosphere.sulfur-trioxide`;
  `processes/p-toluenesulfonyl-chloride-1/lca/mappings.yaml` and its `DESIGN.md` D-016.
