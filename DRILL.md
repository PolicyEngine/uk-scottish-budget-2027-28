# Drill: Sunday 15 November 2026, 23:40–02:10

A timed rehearsal of Scottish Budget day (Thursday 3 December 2026, with the Scottish Fiscal Commission's forecasts) on a mock statement. It uses the 2.5-hour compressed clock. All times are London time; times after midnight are Monday 16 November.

This file holds the plan only, and is the only copy of the clock and the packet hashes; the drill issue links here. It says nothing about the mock measures. The statement, documents, correction notice, answer key and scoring tool are held outside this repository by the drill owner and are released at the times below.

The drill runs on a local run branch cut from the head of `engine-2.177.7-microcosm-9e18f010` (it is on Microcosm build 6f918b81 despite its name; the cut head must include b08bb96). Before G0 the integrator cuts it, merges the drill branch into it for this file, and records the start SHA and the engine-branch SHA it was cut from. Drills never merge.

## Clock

Three other drills share the machine tonight. Heavy runs never overlap: each drill takes the lock only inside its own slots.

| Time | T | Release | Gate |
|---|---|---|---|
| by 23:10 | T−30 | none | G0: freeze and pair record posted on the drill PR |
| 23:40 | T+0 | statement | G1 by 23:50: coverage ledger, every line routed and classed |
| 23:50–00:10 | T+10 to T+30 | none | heavy slot 1 (G2 runs) |
| 00:10 | T+30 | none | G2: provisional numbers, one hand-checked household per coded measure |
| 00:20 | T+40 | documents: costings, mock forecast, example households, scoring sheet, file formats | G3 by 00:50: re-base and reconcile; every gap over 10% has a written reason |
| 00:55 | T+75 | correction notice | G5 by 01:15: re-run everything affected, hand rows into their own file, new scoring SHA |
| 00:55–01:20 | T+75 to T+100 | none | heavy slot 2 (G5 runs and the G4 build) |
| 01:20 | T+100 | none | G4: full page on a local production build, MOCK banner and noindex checked |
| 01:30 | T+110 | none | stop: log the stop commit; nothing scored changes after it |
| by 01:35 | T+115 | none | FREEZE.txt posted on the drill PR |
| 01:40 | T+120 | answer key and scoring tool | scoring (to 02:00) |
| 02:10 | T+150 | none | retro filed on the drill issue |

Heavy lock slots on this machine tonight (Sunday 15 November into Monday 16 November). This drill's slots are the only times it may hold `/tmp/pe-heavy.lock`; the others are busy:

| Drill | Slot 1 | Slot 2 |
|---|---|---|
| Drill 9 | 21:40–22:05 (busy) | 22:45–23:10 (busy) |
| Drill 10 | 22:15–22:35 (busy) | 23:20–23:45 (busy) |
| Drill 11 | 23:10–23:20 (busy) | 00:15–00:40 (busy) |
| **Drill 12 (this drill)** | **23:50–00:10** | **00:55–01:20** |

A heavy run (any `generate --reforms`, `generate --package`, or production build) takes the lock as in `docs/RUNBOOK.md` ("Heavy runs"): contents "<pid> <label>", created with noclobber, at least 22 GB free, one measure per process, removed only by the process that wrote it. A run that cannot finish inside the slot is not started. An overrun is logged; the next slot's owner logs the wait as lock wait. Never delete a lock you do not own.

### Engine and data pair

policyengine-uk 2.177.7, policyengine-core 3.34.10 (no policyengine.py), Microcosm build `uk-frs-calibration-attempt-20261112T133744Z-6f918b81` (SHA-256 `e268e3af7932784ad4471f008097a5acc6c3c5bc15c4c54fbb5a489b2a0ac9ae`, made on 2.177.7), with the OBR October 2026 forecast overlay. Every figure carries the label "build uk-frs-calibration-attempt-20261112T133744Z-6f918b81, policyengine-uk 2.177.7, not in a policyengine.py release". policyengine.py 6.19.0 pins a different, certified pair (policyengine-uk 2.174.1 with build eeb6093e). Running eeb6093e under 2.177.7, or 6f918b81 under 2.174.1, is a mixed pair: invalid, and not scored. Figures from any pair not recorded at G0 are not scored.

## Gates

- **G0, freeze and pair record (by 23:10).** From the run branch, `uv run --extra model scottish-budget freeze --dataset <path to the build's .h5>`, pasted into the clock table as a PR comment: start SHA, clean tree, policyengine-uk and core versions, `pinned_dataset` (build id), `dataset_sha256` (must equal the build's), and `engine_matches_build: true`. Add the engine the build itself records in its release manifest (the files published with the build in its release folder), with the manifest's path: it must be policyengine-uk 2.177.7. The pair-check result is PASS only if the installed engine, the pinned engine and the manifest's engine all agree and the dataset hash matches.
- **G1, coverage ledger (23:40–23:50).** One line per statement item in `data_inputs/drill/coverage-ledger.csv`, columns `line,statement_item,route,cause,trap,basis,upstream_draft,zero_reason,notes`, each with a route and a cause class (below). Items already in the baseline are flagged here (`trap` True), not coded. Commit a copy as `data_outputs/drill/coverage-ledger-g1.csv`; it is frozen at the stop. Kept measures get their values and `placeholder=False` in `reforms.py`; registry entries the statement does not contain are deleted.
- **G2, provisional numbers (by 00:10, in heavy slot 1).** For each coded measure: `uv run --extra model scottish-budget generate --reforms <id>`; then `generate --package provisional` and `uv run scottish-budget combine --provisional`. One hand-checked household per coded measure, starting from `data_inputs/household_fixtures/`.
- **G3, re-base and reconcile (00:20–00:50).** Re-base to the baseline the costings use, fill `data_inputs/drill/reconciliation.csv` and run `uv run scottish-budget reconcile --official data_inputs/drill/reconciliation.csv` until it exits 0. Fill `data_outputs/drill/national.csv` in the format the documents give. Set `publish=True` on each reconciled measure. Update ledger causes after G3.
- **G5, correction (00:55–01:15, in heavy slot 2).** Record the correction (arrival time, hash check) as a PR comment. Re-run every affected measure and the package under the lock, `combine` again, re-run every hand-computed household row into its own file (`data_outputs/drill/g5-household-checks.csv`), and record the new scoring SHA (`results_sha256` in `dashboard/public/data/receipt.json`) beside the old one.
- **G4, publication path (by 01:20, in heavy slot 2).** `generate --package final` and `combine`; from the repository root `uv run python scripts/check_public_data.py dashboard/public/data`; then under the lock `cd dashboard && bun run check-public && NEXT_PUBLIC_MOCK=1 bun run build && bun run start`. In a second shell, `scripts/smoke-built-site.sh http://localhost:3000/uk/scottish-budget-2027-28 MOCK`, plus `curl -s <url> | grep -o '<meta name="robots"[^>]*>'` (must contain `noindex` and `nofollow`) and `curl -sI <url> | grep -i x-robots-tag`. Record the disclosure-floor counts (below) in the G4 comment. Stop the server and release the lock. Nothing is deployed.
- **Stop (01:30).** Log the stop commit in the clock table. Nothing is pushed after it, and no scored file changes after it.

## Freeze at stop

By 01:35 (T+115), and in any case before the answer key at 01:40, the integrator posts `FREEZE.txt` on the drill PR. It lists the SHA-256 of every scored file at the stop commit, one per line in `shasum -a 256` format (`<64 hex>  <path from the repository root>`):

- each filled scoring sheet (one per scoring run, named with its commit SHA);
- `data_inputs/drill/coverage-ledger.csv` and `data_outputs/drill/coverage-ledger-g1.csv`;
- `data_outputs/drill/national.csv` and `data_inputs/drill/reconciliation.csv`;
- `dashboard/public/data/results.json` and `receipt.json`;
- every hand-check file (`data_outputs/drill/g2-household-checks.csv`, `g5-household-checks.csv`).

The post also gives the stop commit SHA and the SHA-256 of `FREEZE.txt` itself. The scorer copies the frozen files from the stop commit, reads only those copies, and runs the released scoring tool on them; the tool refuses any file whose hash differs from `FREEZE.txt`. A file that changes after the freeze is not scored. Anything that arrives after the stop (a late correction, a relabel) is logged as a defect; frozen files are not changed.

## Roles

| Role | Owns | Does not |
|---|---|---|
| Integrator | run branch, clock table, every commit, generation, re-basing, FREEZE.txt | score households; open sealed files early |
| Reconciler | ledger, reconciliation and national CSVs, defects posted as PR comments within 5 minutes; the hash check of each release (23:40, 00:20, 00:55) | push code |
| Scorer (the reconciler after the documents) | example households, one commit SHA per scoring run; the hash check of the key and tool at 01:40 | edit reform code |
| Drill owner (not the integrator) | the sealed packet, releases at the set times, the answer key and scoring tool | take part in coding |

Who holds each role is recorded on the drill issue, not here. Only the integrator pushes.

## Routes

Every ledger line gets one route. The route says where the work lands:

| Route | Where the work lands | Meaning |
|---|---|---|
| `dashboard-param` | this repo | a parameter change in `reforms.py`, or a baseline correction |
| `dashboard-structural` | this repo | a hand-written modifier in `measures/`, one module per modifier |
| `needs-pe-uk-first` | policyengine-uk | the engine has no route; a draft upstream fix is filed the same day |
| `not-computable` | data (Microcosm) | the input the measure acts on is not in the data or the model; published with the reason, never as £0 |
| `ledger` | none | not modelled (business taxes, spending, items already in the baseline); the official figure is recorded |

**Upstream drafts.** A `needs-pe-uk-first` line, and a `dashboard-structural` line whose modifier stands in for missing engine logic, earns route credit only if its `upstream_draft` column links a policyengine-uk issue or draft pull request filed on the drill night, before the stop. Log every draft (repository, link, time).

## Cause and gap classes

Cause class (ledger: what the measure needs before PolicyEngine can show it):

- `parameter`: an existing parameter carries it.
- `formula`: engine or modifier logic must change.
- `coverage`: the input the measure acts on is not in the data or the model (every not-computable line).
- `baseline_mismatch`: the baseline already holds the measure, or holds a different value from the official baseline (every trap row).
- `timing_fiscal_calendar`: start date, part year or fiscal year placement is the substance.
- `interaction`: the measure works through another benefit or measure.
- `data_calibration`: the data hold the input but its level is off.
- `basis`: a presentation choice only.

Gap class (national: why our figure differs from the official one by more than 10%):

- `basis`: static vs behavioural, accrued vs cash, geography, price base, gross vs net.
- `data_calibration`: the data's count or level of the affected group differs from the official one for the same year.
- `baseline_mismatch`: the official baseline holds different policy or forecast assumptions.
- `timing_fiscal_calendar`.
- `coverage`.
- `interaction`.

The cause class and the gap class are separate columns. Equal values need a written reason. Choose each class from why the item matters, not from the kind of code change made, and re-check every cause and gap class after re-basing and after the correction.

Declare the basis once, at G1, and repeat it next to every figure: static or behavioural, gross or net, accrued or cash, fiscal year (2026-27, 2027-28, 2028-29), and which baseline.

## The zero rule

£0 is not a costing. A coded measure whose figure is £0 in every year needs either a written `zero_reason` on its ledger line, saying why the model truly shows no effect, or a not-computable route with the reason. A not-computable or ledger line is never published, charted or tabled as £0: its figure is left empty and its reason is shown.

## Disclosure floor

Any published cell resting on fewer than 10 survey households is withheld (null with a reason, never 0). The count is of survey households, not Microcosm rows: count unique `source_household_id`, not `household_id` (build 6f918b81 has about 4.8 rows per survey household; issue #22). Count the households the cell's figure rests on: for a measure's decile or band cell, the households that measure changes. The G4 comment records, for each published table, the counting method and the smallest count. A floor applied to rows does not meet this rule even if `check_public_data.py` passes.

## Rubric

| Area | Points | How it is scored |
|---|---|---|
| Example households | 20 | each reported value within ±1p of the key, on the values in force after the correction notice |
| National figures | 30 | basis and gap class for each statement line; for not-computable and ledger lines the basis column carries the costing's basis, and the gap point is for recording the costing and the reason no figure is shown |
| Ledger | 25 | route and cause for each line, as they stand at the stop; trap rows score only if flagged as in the baseline at G1 and left uncoded |
| Publication path | 10 | MOCK banner, noindex meta and `X-Robots-Tag`, not-computable lines shown with reasons and never as £0, disclosure floor on survey households, every coded measure on the page |
| Process | 15 | G0 pair record on time, gates on time, one commit SHA per scoring run, the correction logged and every hand row re-run into its own file, FREEZE.txt posted before T+120, defects posted within 5 minutes |

The answer key states per-line weights inside these parts, and its own rounding and part-year rules; the documents state the same rules at 00:20. The scoring tool is released with the key and run by the scorer on the frozen files only.

## Defects

Anyone who finds a defect posts it as a comment on the drill PR within 5 minutes of finding it, with the time found; the fix is posted in the same thread with the time fixed. If posting is blocked (a permission prompt, an outage), retry; if it is still blocked, attach the defect to the next gate comment within the window and log the block. A defect kept only in a local file counts as not posted.

## What to time and log

The integrator fills the clock table as the drill runs. For each step, record start and end times, and split machine time (generation, builds, tests) from people time (reading, coding, review).

| Step | Start | End | Machine time | People time | SHA |
|---|---|---|---|---|---|
| G0 (due 23:10) | | | | | |
| G1 (due 23:50) | | | | | |
| G2 (due 00:10) | | | | | |
| Documents received | | | | | |
| G3 (due 00:50) | | | | | |
| Correction received | | | | | |
| G5 (due 01:15) | | | | | |
| G4 (due 01:20) | | | | | |
| Stop (01:30) | | | | | |
| FREEZE.txt posted (by 01:35) | | | | | |

Also log:

- every scoring run, with one commit SHA each;
- the time each release arrived and the hash check result;
- every defect, as a PR comment with the time found and the time fixed;
- every upstream draft filed (repository, link, time);
- every heavy run: start, end, peak memory, the lock taken and released, and any lock wait.

## MOCK and noindex rules

- The drill branch shows a banner on every view that starts with **MOCK** and says the figures are drill figures, not the Scottish Budget. The page does this when built with `NEXT_PUBLIC_MOCK=1`; the template's "Pre-release template" banner is not enough.
- The served HTML carries a robots meta with `noindex` and `nofollow` (Next renders `noindex, nofollow, nocache`), and every response carries `X-Robots-Tag: noindex, nofollow`. Check both in the output of `next start` (G4), not only in the source.
- Nothing from the drill is deployed, posted or shared outside the drill PR and the drill issue.
- The drill PR is a draft labelled `not for merge`. It is never merged.
- Public files on the drill branch pass both checks: from the repository root `uv run python scripts/check_public_data.py dashboard/public/data`, and from `dashboard/` `bun run check-public`. No ids or weights, no area codes, and the survey-household floor above.

## Packet hygiene

- The packet is written and held outside this repository by the drill owner. Only the hashes are committed, below.
- Files are released at the set times, not before. The reconciler (the scorer at 01:40) checks each file's SHA-256 when it arrives (`shasum -a 256 <file>`) against the table below and logs the result.
- The integrator does not open any packet file before its release time.
- Code goes in waves: parameters, then modifiers, then new variables.

## Packet hashes (SHA-256)

| File | Release | SHA-256 |
|---|---|---|
| `00-owner-notes.md` | drill owner only | `1aabdb3fdda660d980175ba845df0cb5c23059fcd6b3661673e4bdf2fa6c99a6` |
| `01-statement.md` | 23:40 (T+0) | `fd5a4ec1eae51ed98c94beed8feac4fde40e9d8f8b1314addcd9398ebede49e1` |
| `02-documents.md` | 00:20 (T+40) | `1a44021418e3917870b830b4e06bfe0f5c9ff6227a1af63543e5a3dab1338b06` |
| `02-costings.csv` | 00:20 (T+40) | `cda48998e1012c2d1de926d776f2b3c64214d7d7d3c3baf65fa636217f2634bc` |
| `02-households.csv` | 00:20 (T+40) | `4b3a14d04ddc8770ca4421e87608185e00df8ea16a047cec57619b37b440d18b` |
| `02-scoring-sheet.csv` | 00:20 (T+40) | `27b301839f2a97ee0cf34cad04fe79d57e12dfae81b3cbf927746a2e2c4dca02` |
| `03-correction-notice.md` | 00:55 (T+75) | `ec1db2b5b23471c044069ea817b08c0f7a2eeca6d98df767cc895df49cbf5d3c` |
| `04-answer-key.md` | 01:40 (T+120) | `ffea50821d2dd57fdce648999a6ad110e84fea6dbddf8050927530bc1df2bad6` |
| `04-answer-key-households.csv` | 01:40 (T+120) | `750ad18ce52286cab4aea5ab0e5d3c663b0f5122e5f91064897017c965d0a5be` |
| `04-answer-key-ledger.csv` | 01:40 (T+120) | `3be16f9aa603dbe3c4361d54a422385e72c019d8b2fe9e9bf5467c96e824d33d` |
| `generate_household_key.py` | 01:40 (T+120) | `bad85b0c1084289bbded6f80f55241dc258481b0883d3823841ae0e868b9d42b` |
| `04-score.py` | 01:40 (T+120) | `85943afaa3a50c8ae529b10bc91fd67e707b7aa2e63d9cb572e45436b3acb441` |
