# Tracking process development

The [execution tracker #114](https://github.com/ChemE-as-Code/process-library/issues/114)
coordinates individual process issues. [coverage.md](coverage.md) and coverage.yaml remain
the accepted coverage/ranking plan (#47); issues track execution, sources and review.

## Issue structure

Use the **Process development** form and label `type:process` for one canonical issue per
chemical/process initially. Reuse ammonia #86 and toluene HDA #42. Split route issues when
they have distinct owners, models/boundaries or evidence targets; link the parent.
Electricity mixes and regional sensitivities usually remain scenarios of the same route.
Create issues for selected work rather than inventing a full literature list.

Use the **Process development tracker** form (`scope:library`, `type:tracker`) for a batch.
Literature discovery uses `scope:library`, `type:research`. Keep existing engineering action,
hold, query, change, gate and waiting labels unchanged. Do not put a guessed process folder
in the engineering forms: their existing label workflow verifies folders on main.

Initial batch: ammonia #86; hydrogen #117; methanol #118; nitric acid #119; urea #120;
chlor-alkali #121; steam #122; cooling water #123; wastewater #124; toluene HDA #42.
The utility tickets assess/improve existing datasets. This is a working batch, not a
claim of readiness. Add the remaining coverage candidates as they are selected.

## Reference record

Append references and example plants to the relevant process issue with:

- citation and link, version/date and exact table/section;
- purpose: candidate suggestion, design input, model basis or comparison;
- access/read status and numerical basis/boundary;
- reuse limits, assumptions and outstanding questions.

Keep independently held-out benchmark answers outside design-agent access, including issue
comments when agents can read GitHub. Mentioning a paper is not independent validation.

[Text-to-flowsheet candidates #115](https://github.com/ChemE-as-Code/process-library/issues/115)
use only process names/types as suggestions, not the authors' datasets, expert drawings,
graphs, code, logs or simulation files.
[CRYSTAL prioritization #116](https://github.com/ChemE-as-Code/process-library/issues/116)
uses its 52 hub chemicals (section 5 / Figure 4 / Table S9), distinct from 50 hotspots.
Verify the full supplementary list before creating individual hub tickets; checked v1
omits Table S9. No inventory import is requested.

## GitHub Project setup

Create an organization Project **Process Library Development**, private, and link this repository.
First inspect existing Projects to avoid duplication. The current automation credential lacks
Projects scopes; setup needs an authorized Projects credential or a signed-in owner.

| Field | Values / meaning |
| --- | --- |
| Status | Backlog, Ready, In progress, In review, Done |
| Calculation maturity | Not assessed, None, Sourced, Balanced, Predictive, Engineering |
| Target maturity | Explicit target for this scoped issue; use Not applicable for inventory-only work |
| Entry tier | 0 stoichiometric screening, 1 sourced conceptual inventory, 2 flowsheet design |
| Review status | Not assessed, Unreviewed, Review requested, Reviewed with limitations, Reviewed |
| Priority | P1 next batch, P2 later, P3 candidate; priority is planning, not evidence |
| Process ID / route | Stable IDs once chosen; unknown stays unknown |
| Evidence | Text/link to report and commit, plus pinned core/backend version |
| Assignees | Owner; leave unassigned until agreed |

Create a **Delivery** board grouped by Status (filter `repo:ChemE-as-Code/process-library label:type:process`),
an **Evidence** board grouped by Calculation maturity, and a **Planning** table for trackers/research.
Show labels, owner, tier, target maturity, review and evidence. Start items at Backlog and Not assessed
until audited; do not infer process maturity from existing issue text or a manifest claim.

Ready means the next scoped work has inputs and no blocking dependency. In review means evidence
is ready for a separate reviewer. Done means that issue's declared target is verified, not that
every process is Engineering or public. Use existing `waiting:input`/`waiting:work` labels and
linked dependencies for blocked work; do not turn blocked into a maturity level.
Retain `status:in-progress` and `status:for-verification` on engineering action items where used.

Add the ten canonical issues above. Configure auto-add for this repository's `type:process` issues
if available; backfill existing issues manually. New items default to Backlog. Do not automate
scientific maturity changes from workflow state, labels, merge or closure. Update maturity only
after reviewing a current `cheme maturity` report (where applicable) at a recorded commit.
Inventory-only entries record dataset evidence and leave plant calculation maturity Not assessed.
Record independent review and publication decisions separately.

## Maintaining the tracker

Link new process issues from #114 and their route parents. Add PRs and sources to individual
issues as work progresses. Update coverage.yaml and its generated table only through reviewed
repository changes. Close scoped issues after verification; open a linked follow-up when pursuing
a higher tier/maturity or a materially different route. The Project is a planning view, not a
replacement for committed manifests, balance results, maturity evidence or review records.
