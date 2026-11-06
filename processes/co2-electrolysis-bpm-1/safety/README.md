# Safety: HAZOP studies

| path | what |
|---|---|
| `safety/hazop/<study-id>/study.yaml` | one HAZOP study (`cheme schema hazop-study`): the one authoritative file, edited by the team and by agents |
| `safety/risk-matrix.yaml` | the risk matrix the studies rate against (`cheme schema risk-matrix`). **Here it is a proposal by an agent (ASSUMED, `status: proposed`)** in the structure of asu-1's 5x5 matrix, scaled to the pilot: the owner's team accepts it, or replaces it with the company's matrix, before anything is assessed; a study rated against a proposed matrix stays a draft |
| `build/hazop/<study-id>.md`, `.html` | the report, derived from the study (`cheme safety hazop report`); never edited |
| `reviews/<date>-hazop-<study-id>.md` | the review record of the study (skill `review`, `cheme safety hazop review`) |
| `safety/hazop/SESSION.md` | the team session pack: roles, agenda, the decisions to take first, every high scenario with its proposed action, and how to record acceptance |

## The studies of this plant

> **These are agent-prepared drafts for a HAZOP team session. They are not a HAZOP: no session
> has been held, nobody has accepted anything in them, and no human has reviewed them.** Every
> node, scenario, safeguard, rating and action is `status: proposed, by: agent` (a deviation
> carries no status of its own in the schema: it is a guide word applied to a parameter, and the
> scenarios under it are proposed), the risk matrix is proposed, and `cheme safety hazop check` reports both studies as `draft`. Do
> not use them for safety decisions, procurement or operation before the team session and a
> human review (`safety/hazop/SESSION.md`).

| study | what | sheet | nodes | scenarios | worst band high / medium / low | actions |
|---|---|---|---:|---:|---|---:|
| `H-01` | Skid A: one-fill anolyte reservoir | P-01 | 8 | 78 | 15 / 40 / 23 | 54 |
| `H-02` | Skid B: KOH dosing, bleed and make-up | P-02 | 9 | 94 | 25 / 40 / 29 | 57 |

The node numbers mean the same part of each skid (N1 anolyte loop, N2 stacks and DC supply, N3
cathode CO2 feed, N4 cathode gas outlet, N5 gas conditioning, N6 tail gas and vents, N7 Skid B's
dosing, bleed and make-up, N8 fill and drain, N9 the open, naturally ventilated skid and its gas
detection: the enclosure and its extract fan of the first drafts are deleted, DESIGN.md D-050).
Both studies were revised by an agent on 2026-11-06 for the owner's decisions D-050 to D-058
(open skid, Ex marking, tempered water, tail-gas arrester and trip valve, drains, the rectifier
and oxidiser off the frames, the pH 12.2 trip), every revised entry proposed for the team, and
re-stamped (safety/hazop/SESSION.md section 3.6), and again for P&ID revision C, the fixes of
the agent design review 2026-11-06-design (relief, the compressor and instrument-air trips, the
H2-in-O2 analyser and the membrane's pressure difference, the total CO2, the condensate, the
stack monitoring, the check valves; DESIGN.md D-060 to D-066, SESSION.md section 3.6.1). The
two studies were drafted
apart and then integrated, so that the hardware both skids share is examined alike and rated by
one convention, and then reviewed against the plant as drawn and their own credit rules
(DESIGN.md D-030). The actions the drafting agent considers most important are
in DESIGN.md D-031; the hazards judged not applicable, and the gaps of the plant as drawn, in
D-032. The studies do not change the plant: what they find is an action for the design team.

The gate `hazop-current` of `checks/checks.yaml` passes on the drafts: both studies are current
against their analysed inputs and neither is example data. The house gates for an assessed and
reviewed HAZOP (below) are added once the team session and a human review are recorded.

There is no study until you start one: `cheme safety hazop init H-01 --title "..." --input
pid/P-01.xml --input control/cause-effect.yaml`. A new study is a draft and has no judgements.

## The study file

```yaml
schema: cheme/hazop-study/v1
kind: hazop-study
id: H-01                         # = the directory name
title: Feed vessel and transfer pump
scope: what the study covers, and what it does not
modes: [{id: normal, title: Normal operation}]
analysed:                        # the files analysed, at the revision analysed (cheme safety hazop stamp)
  - {path: pid/P-01.xml, revision: 'sha256:...', relation: analyses}
risk_matrix: safety/risk-matrix.yaml
assessment_basis: how risk is ranked (initial before safeguards, residual with them)
nodes:
  - id: N1                       # stable ids: never renumbered, never reused
    title: V-101 and pump suction
    design_intent: ...
    members: [V-101, LT-102, {tag: 80-P-101, sheet: P-01}]
    status: accepted             # proposed (default) until the team accepts it
    deviations:
      - id: N1-LL
        guide_word: less         # "no" (quoted or not), more, less, as-well-as, part-of, reverse, other-than, early, late, before, after
        parameter: level
        scenarios:
          - id: S1
            cause: ...
            consequence: ...
            refs: [V-101, P-101]
            safeguards: [SG1]    # ids of safeguards: below
            actions: [A1]        # ids of actions: below
            status: accepted
            risk:
              initial:           # before the safeguards, per category of the matrix
                - {category: people, severity: "3", likelihood: C, basis: ..., status: accepted}
              residual:          # with them, as the team judges it; never derived by a tool
                - {category: people, severity: "3", likelihood: A, basis: ..., status: accepted}
safeguards:
  - {id: SG1, title: Interlock I-01 stops P-101, kind: interlock, interlock: I-01, refs: [LT-102], status: accepted}
actions:
  - {id: A1, text: ..., owner: ..., status: open}   # proposed, open, closed, rejected (+ response)
```

- **Ids** are what the team, the actions and the review records refer to. Insert and reorder
  freely: the order is display order only.
- **Plant references** are tags as printed on the P&IDs (equipment, instrument, piping item,
  line number); add `sheet:` where a tag alone is ambiguous, or name a DEXPI object by
  `{sheet, object}`. Interlocks are declared in `control/cause-effect.yaml` and referred to by
  id, not copied.
- **Who decided**: everything is `status: proposed` until the team accepts it. Agents propose;
  only the team writes `accepted`. The calculated `band:` of a rating is written by `cheme
  safety hazop rate --write` (with the matrix and input fingerprint) and never by hand.
- **Unrated is explicit**: a scenario without ratings, a rating without a code or a basis, a
  band not looked up yet are listed as unresolved, never filled in.
- `extensions:` (on the study, a node or a scenario) holds other tools' data by tool name;
  cheme-as-code keeps it and does not read it.

## Workflow

1. **Scope and source revision.** `cheme safety hazop init`, then the scope, the operating
   modes, the team and the assessment basis. `analysed:` records the revision of every P&ID and
   control file the study analyses.
2. **Nodes and design intent.** Split the plant into nodes; give each its members and design
   intent. Skill `hazop-study`.
3. **Deviations.** For each node, the guide words that make sense with each parameter of its
   intent (flow, pressure, temperature, level, composition, ...).
4. **Causes and consequences.** One scenario per credible cause and consequence; a deviation
   without a credible cause says so in `notes:`.
5. **Safeguards.** The ones the P&IDs and the cause and effect actually have, by tag or
   interlock id.
6. **Assessment and recommendations.** The team rates severity and likelihood per category,
   initial and, where it credits safeguards, residual, each with its basis; `cheme safety hazop
   rate H-01 --write` looks the bands up; a band whose matrix policy requires an action asks for
   one. Skill `hazop-assessment`.
7. **Human review.** `cheme safety hazop check H-01`, `cheme safety hazop report H-01`, then a
   review record (`cheme safety hazop review H-01` prepares it; skill `hazop-review`).
8. **Revisions.** When a P&ID or the C&E changes, `cheme validate` reports
   `hazop-input-changed`: reassess the nodes it touches, rate again (`--target N1`), record
   the new revisions (`cheme safety hazop stamp H-01 --write`) and review again.

## Commands

| | |
|---|---|
| `cheme safety hazop init ID [--title T] [--input F]... [--matrix F]` | a draft study |
| `cheme safety hazop check [ID] [--json]` | the study's findings and state: `invalid`, `draft`, `assessed` (complete, current, accepted), `reviewed` (and a current human review) |
| `cheme safety hazop rate ID [--target NODE\|SCENARIO] [--write] [--json]` | the band of every rating from the matrix; `--write` records them, nothing else changes |
| `cheme safety hazop report ID` | `build/hazop/ID.md` and `.html` |
| `cheme safety hazop stamp ID [--input F]... [--write]` | the analysed inputs' recorded and current revisions (a file by its sha256, a committed directory by the commit); `--write` records the current ones |
| `cheme safety hazop review ID [--write]` | a review record to complete, in the format of `reviews/` |

`cheme validate` checks every study: ids, references inside the study, tags against the lists
and P&IDs, interlocks against the C&E, matrix codes, stale bands, actions, changed inputs.

A study that is `assessed` is complete and consistent, not approved. Stage gates ask for what a
stage needs, e.g. in `checks/checks.yaml`:

```yaml
- {id: hazop-basic, title: HAZOP assessed and reviewed, stage: basic, kind: hazop,
   require: [assessed, inputs-current, no-example]}
- {id: hazop-review, title: HAZOP human review, stage: basic, kind: review, topic: hazop,
   require_kind: [human]}
```

The tools look bands up in the matrix; they do not estimate frequencies, infer severities,
credit safeguards or model consequences. Those judgements are the team's.
