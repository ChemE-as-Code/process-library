# Governance of the Atlas LCI database

> **Status: draft for the owner's review** (process-library#50). Section 6, the data contribution
> policy, is a **DRAFT for TU Delft legal** (website#6) and has no force until legal and the
> owner have approved it.

How the Atlas LCI database is versioned, released, reviewed and fed with contributed data. The
modelling rules are in [system-model.md](system-model.md); this page governs how they and the
datasets change.

## 1. Versions

Three things carry a semantic version, `MAJOR.MINOR.PATCH`:

| what | where it is recorded |
|---|---|
| the **database release** | `--version` of `build_lci.py`: the database name `cheme-as-code-atlas-<version>`, `datapackage.json` `version`, `index.json` |
| each **dataset** | the dataset's own `version` field (core#179); `datapackage.json` `processes[].datasets[].version` and `version_source` |
| the **methodology** | the header of [system-model.md](system-model.md) and `METHODOLOGY_VERSION` in `build_lci.py` (a test keeps them equal); `datapackage.json` `system_model.methodology.version` and each dataset's `methodology_version` |

What raises which part:

- **MAJOR:** a change of functional unit, system boundary or system model; a change of
  allocation method of a dataset; removal or renaming of an activity code (codes are
  `<process>:<dataset>:<product key>`, `market:<product>:<region>` and `proxy:<id>`); a methodology change that changes results
  of existing datasets by design.
- **MINOR:** new datasets or activities; new exchanges; re-estimated amounts (a better
  estimate, a new design revision); new background links; a methodology addition that leaves
  existing results alone.
- **PATCH:** corrections that restore the intended data (a typo, a unit slip, a wrong link),
  metadata and documentation.

A release's version is at least as high as the largest change in it: a release with one MAJOR
dataset change is a MAJOR release. Versions below 1.0.0 are screening releases: the data may
change in any release, and they are not for decision support.

A dataset that records no version is reported as `0.1.0` with `version_source: initial`. Core's
dataset contract v2 (`schema: cheme/lci_dataset/v2`, core#179) has the dataset's `uuid`,
`version`, `methodology_version`, `review`, `valid_until`, `superseded_by` and `system_model`;
the build reads them and records them per dataset in `datapackage.json`. A dataset that states no
`methodology_version` is reported under the build's (`methodology_version_source: build`).
The process manifest has no version of its own (`schemas/process.schema.json`).

## 2. Change reports

`build_lci.py --previous <earlier build>` compares the new build with an earlier one and writes
`lci/changes.json` and `lci/CHANGES.md`:

- per **dataset**: added, removed, changed or unchanged (by a sha256 of its content and by its
  allocation method and shares, which also change with the study's prices or a curated rule),
  the version before and after, an allocation change, and `version_not_raised` when the content
  or the allocation changed but the version did not (a governance error to fix before release).
  The dataset status does not cover changes of the links alone (a new mapping or cut-off
  exclusion): those show in the activity section;
- per **activity**: activities added and removed, and per activity the exchanges added,
  removed and changed (amount before and after with the relative change, or the link: name,
  reference product, unit, location, categories);
- the system model and methodology version of both builds.

The report is at **exchange level**. It gives no impact delta: the stub background of the CI
round trip is built inside the Brightway test from one process's example factors, not a
library-wide reference background, so a GWP delta from it would be a placeholder number. A
reference impact set (e.g. GWP100 per functional unit under a stated background) is a
follow-up.

## 3. Releases and DOIs

The release decision is **the owner's**. No workflow publishes anything.

The workflow `.github/workflows/release.yml` (started by hand, `workflow_dispatch`, read-only
token) drafts a release:

1. runs the tests, including the Brightway round trip;
2. builds the previous release from its own commit with its own builder (input `previous_ref`,
   `previous_version`);
3. builds the database (cut-off, `--public --strict`, `--previous`) and the substitution variant
   (`--public --system-model substitution`). Only processes with `publication.status: public` are
   in it;
4. drafts the archive metadata (`scripts/release_metadata.py`): `.zenodo.json` and
   `CITATION.cff` with the version and date, in `release/archive/`;
5. uploads everything as a workflow artifact (30 days). Its visibility follows the
   repository's: only repository members can download it while the repository is private, but
   any signed-in GitHub user can once it is public. The artifact holds the `--public` build
   only.

It does not tag, create a GitHub release, deposit on Zenodo, mint a DOI or deploy, and it never
reads or sets `DEPLOY_ENABLED`.

When the owner decides to release:

- [ ] check the artifact: the change report, `datapackage.json` (no allocation findings, no
      unintended exclusions), the variant's caveat, the drafted metadata;
- [ ] tag the commit `lci-v<version>`;
- [ ] deposit the artifact on Zenodo by hand (or enable the Zenodo GitHub integration, which
      deposits on a published GitHub release and reads `.zenodo.json`; enabling it is itself a
      release decision). Once the integration is on, the root `.zenodo.json` applies to
      **every** GitHub release of the repository, which would then be deposited as the LCI
      database under CC BY 4.0, although the repository also holds MIT code: tag LCI releases
      only, or deposit by hand;
- [ ] add the DOI to `CITATION.cff` and the database's README in a follow-up commit.

**Citing a dataset:** authors of the process, year, *process title*, dataset `<id>` version
`<dataset version>`, in: ChemE-as-Code Process Atlas LCI database `<release version>`, DOI of the
release.

## 4. Review procedure

The LCI review is separate from the engineering design review (the **review status**,
`process.yaml` `validation.status`, and `processes/<id>/reviews/`): a well-engineered design can
still have a poor inventory, and the reverse. Neither is the design maturity (`process.yaml`
`maturity`) or the calculation maturity (`checks/maturity.json`); the terms follow core's
[glossary](https://github.com/ChemE-as-Code/core/blob/main/docs/concepts/glossary.md).

Levels, recorded in the dataset's `review` field (a list of records, each `type`: `none`,
`internal`, `independent-external` or `panel`, with reviewer, scope, date and report).
`datapackage.json` shows `{"status": "unreviewed"}` when there is none, else the strongest type
and the records:

| status | who | when |
|---|---|---|
| `unreviewed` | nobody | default |
| `internal` | a plausibility review by someone who did not compile the dataset | before a dataset enters a release at 1.0.0 or above |
| `independent-external` | an independent reviewer outside the team that made the dataset | before a dataset is promoted as reviewed or used for public claims |
| `panel` | a panel per ISO 14071 (chair plus at least two independent experts) | comparative assertions disclosed to the public, as ISO 14044 requires |

**Independence:** a reviewer did not contribute to the dataset, its design or its funding, and
has no commercial interest in its results. The record states the reviewer's affiliation.

**Review record** (in the dataset, core#179): type, reviewer (name, affiliation), date, scope
(the checklist items covered) and the report (a file in `processes/<id>/reviews/` or a link). The
dataset version reviewed and open findings go in the report. A new MAJOR or MINOR dataset
version resets the status to `unreviewed` unless the reviewer confirms the change.

**Checklist** (ISO 14044 and the scope of an ILCD-style dataset review):

- [ ] goal, functional unit and reference flow stated; the product and its state are clear;
- [ ] system boundary stated: included and excluded life-cycle stages, infrastructure included or
      excluded (system-model.md section 5);
- [ ] the build's system model is respected: no credits in the cut-off database, exclusions
      recorded with decisions (`system_model.excluded`);
- [ ] multi-functionality follows the hierarchy, or the deviation is justified
      (`follows_hierarchy`, no allocation findings);
- [ ] mass balance (and the elemental balance of C, H, O, N, S where relevant) closes within the
      stated accuracy; gaps explained;
- [ ] cut-off criteria met (system-model.md section 4): cut flows named, below 1 % each and in
      sum, none environmentally relevant, no precious-metal catalyst or high-CF flow cut (the
      build checks the 1 % rules and the never-cut list; relevance is the reviewer's call);
- [ ] energy and utilities complete (power, steam, cooling, fuel, inert gases);
- [ ] emissions complete and correctly characterised (fossil and biogenic, compartments);
- [ ] background links plausible (activity, location, voltage level, unit);
- [ ] screening proxies justified, their amounts sourced or marked ASSUMED;
- [ ] data quality and uncertainty stated; data age within the freshness rule;
- [ ] sources recorded, licences allow CC BY 4.0 publication, no third-party content copied;
- [ ] results plausible against literature or other databases (order of magnitude, main
      contributors), described in our own words;
- [ ] the change report since the last reviewed version read and accepted;
- [ ] EF compliance checked where claimed (nomenclature, compartments, DQR).

## 5. Deprecation

- A dataset is never deleted from a release that has been made: earlier releases stay archived
  under their DOI, and an activity code is never reused for something else.
- A superseded dataset gets `superseded_by` (the successor's code and version) and a deprecation
  note in its activity comment for at least one MINOR release before it is removed. Its removal is
  a MAJOR change of the database.
- The change report lists a removed or superseded dataset with its successor.

The build reads `superseded_by` (`{id, version}`): the deprecated dataset stays in the database
and its activities are named, commented and listed with a pointer to the successor's activities;
`datapackage.json` has `deprecated` and `superseded_by` per dataset, and `install()` reports the
deprecated activities ([lci/README.md](https://github.com/ChemE-as-Code/process-library/blob/main/lci/README.md), "Governance fields and deprecated datasets"). The change
report does not yet list a superseded dataset with its successor (follow-up).

## 6. Data contribution policy (DRAFT for TU Delft legal)

> **DRAFT.** Not approved. Written for review by TU Delft legal (website#6) and the owner. It is
> not legal advice and grants no rights. Numbers marked PROPOSED are open for decision.

**Scope.** Measured or industrial data (operating data, bills of material, emission measurements)
offered by companies, institutes or individuals for an Atlas process or dataset. Designs and
estimates contributed as own work follow CONTRIBUTING.md and stay CC BY 4.0.

**Licence and attribution.** Contributed data enters the public database under CC BY 4.0 only.
The contributor confirms the right to grant that licence and is credited (by name or, on
request, as "an industrial partner"). Data that may not be published under CC BY 4.0 is not
accepted into the public library.

**Restricted data.** Data under restricted terms is recorded with a source whose policy is
`restricted` (core's source policies). It is never written into a public build (`--public`), a
release or a workflow artifact, and is used only in private builds of the people the agreement
names. Restricted and public data are never combined in a dataset that is published.

**Confidentiality.** Plant-specific data is published only aggregated: as an average over
several plants of different operators (PROPOSED: at least three, no single plant above 50 % of
the weight) or as horizontal averaging over a production route, such that no plant's value can be
recovered. Plant names, locations below country level and capacities that identify a plant are
removed. The aggregation method is documented in the dataset.

**Data provider agreement.** A written agreement between the provider and TU Delft before data is
received, stating: the data, its permitted use, the aggregation, the attribution, the licence of
the published result, confidentiality of the raw data, retention and deletion, and the contacts.
TU Delft legal provides the template.

**Raw data.** Raw contributed data is kept outside the public repository, access-limited to the
named people, and deleted at the end of the agreement; only the aggregated, licensed result
enters the library.

**Review and withdrawal.** Contributed data is reviewed like any dataset (section 4). A provider
can ask to withdraw data from future releases; published releases stay archived as published.

**Open questions for legal:** the agreement template; liability and warranty disclaimers; export
control of process data; personal data in contributor records (GDPR); whether aggregated
industrial data under CC BY 4.0 needs the provider's explicit release per version.
