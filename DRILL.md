# Drill 13: Friday 27 November 2026, 14:00–16:30

A timed rehearsal of Scottish Budget day (Thursday 3 December 2026, with the Scottish Fiscal Commission's forecasts) on a mock statement, using the 2.5-hour compressed clock. It's the first drill on the certified pair and the first with María as integrator. All times are London time.

This file holds the plan only; the drill issue is #26 and the prep plan is #25. It says nothing about the mock measures. The drill owner holds the statement, documents, correction notice, answer key and scoring tool outside this repository and releases them at the times below. The packet hashes are added to this file before 13:30.

## What's new since drill 12

Drill 13 checks the fixes for what drill 12 found, plus three things no drill has covered yet:

1. **The certified pair.** The drill runs on policyengine 6.20.3 (policyengine-uk 2.179.2, Microcosm build b891aa69), through `pe.uk.managed_microsimulation()`. Task 1 of the plan must be pushed by 12:00. If it isn't, the drill runs on the old pair and that is logged as a defect.
2. **The disclosure floor on survey households** (#22). It applies whether or not the fix is merged: count unique `source_household_id`, not rows.
3. **Combine reads the corrected costings.** After G5, `combine` must read the post-correction costings. Drill 12 found it read the uncorrected file.
4. **Registry tests with mock measures.** `uv run pytest` must pass after G1, once mock measures replace the template entries. Drill 12 found the registry tests broke.
5. **The production build is timed.** Drill 12 never recorded how long it took.
6. **New: a report draft (G6).** On the day we publish a post as well as the dashboard. G6 fills the report template's headline and table from the frozen results.
7. **New: one integrator, one reviewer.** María is integrator and reconciler, and Vahid reviews. This is how the day will run. Earlier drills used a separate stand-in for each role.

## Roles

| Role | Who | Owns | Doesn't |
|---|---|---|---|
| Integrator and reconciler | María | the run branch, every commit, generation, the ledger, reconciliation, national CSVs, the report draft, the hash check of each release, posting defects within 5 minutes | open sealed files early |
| Drill owner and reviewer | Vahid | the sealed packet, releases on time, review at G2, G3 and G6, the answer key and scoring | write code or ledger lines |

Only the integrator pushes. The scorer is the drill owner, working only on the frozen files.

## Clock

| Time | T | Release | Gate |
|---|---|---|---|
| by 13:30 | T−30 | none | **G0:** freeze and pair record posted on the drill PR |
| 14:00 | T+0 | statement | **G1 by 14:10:** coverage ledger, every line routed and classed; `uv run pytest` passes with the mock measures |
| 14:10–14:30 | T+10 to T+30 | none | heavy slot 1 (G2 runs) |
| 14:30 | T+30 | none | **G2:** provisional numbers, one hand-checked household per coded measure; reviewer checks one |
| 14:40 | T+40 | documents: costings, mock SFC forecast, example households, scoring sheet, formats | **G3 by 15:10:** re-base and reconcile; every gap over 10% has a written reason; reviewer signs off `publish=True` |
| 15:15 | T+75 | correction notice | **G5 by 15:35:** re-run everything affected; `combine` reads the corrected costings; hand rows go in their own file; new scoring SHA recorded |
| 15:15–15:45 | T+75 to T+105 | none | heavy slot 2 (G5 runs and the G4 build, **timed**) |
| 15:45 | T+105 | none | **G4:** full page on a local production build, MOCK banner and noindex checked, floor counts recorded |
| 15:45–16:05 | T+105 to T+125 | none | **G6:** report draft filled from the results; reviewer reads it |
| 16:05 | T+125 | none | stop: log the stop commit |
| by 16:10 | T+130 | none | `FREEZE.txt` posted on the drill PR |
| 16:10 | T+130 | answer key and scoring tool | scoring (to 16:25) |
| 16:30 | T+150 | none | retro filed on the drill issue (#26) |

No other drill runs on the machine, so the heavy slots are this drill's alone. Heavy runs take `/tmp/pe-heavy.lock` as described in `docs/RUNBOOK.md` ("Heavy runs"): at least 22 GB free, one measure per process, and the lock removed only by the process that wrote it. A run that can't finish inside its slot isn't started.

## Engine and data pair

**Pair:** `policyengine[uk]==6.20.3`, which pins policyengine-uk 2.179.2 and the certified Microcosm build b891aa69, with the OBR October 2026 forecast overlay.

**Label:** every figure carries "build b891aa69, policyengine-uk 2.179.2, certified in policyengine 6.20.3".

**Mixed pairs aren't scored:** that means policyengine-uk 2.177.7, build 6f918b81, or any pair other than the one recorded at G0.

## Gates

- **G0, pair record (by 13:30).** From the run branch, post `uv run --extra model scottish-budget freeze` as a PR comment. It must show:
  - the start SHA and a clean tree;
  - the policyengine, policyengine-uk and core versions;
  - the bundle's dataset id and SHA-256;
  - `engine_matches_build: true`.

  PASS only if the installed versions, policyengine.py's pins and the build's manifest all agree.
- **G1, coverage ledger (14:00–14:10).** One line per statement item in `data_inputs/drill/coverage-ledger.csv` (`line,statement_item,route,cause,trap,basis,upstream_draft,zero_reason,notes`). Items already in the baseline are flagged (`trap` True) and not coded. Then:
  - set values and `placeholder=False` in `reforms.py`, and delete the entries the statement doesn't contain;
  - run `uv run pytest`, which must pass;
  - commit a copy as `data_outputs/drill/coverage-ledger-g1.csv`.
- **G2, provisional numbers (by 14:30, heavy slot 1).** For each coded measure, run `generate --reforms <id>`, then `generate --package provisional` and `combine --provisional`. Hand-check one household per measure, starting from `data_inputs/household_fixtures/`. The fixtures must be regenerated on the new pair; if they aren't, log a defect. The reviewer checks one household.
- **G3, re-base and reconcile (14:40–15:10).**
  - Re-base to the costings' baseline.
  - Fill `data_inputs/drill/reconciliation.csv` and run `reconcile` until it exits 0.
  - Fill `data_outputs/drill/national.csv`.
  - Write a gap class and reason for every gap over 10%.
  - The reviewer signs off each measure in a PR comment before the integrator sets `publish=True`.
- **G5, correction (15:15–15:35, heavy slot 2).**
  - Log the correction's arrival time and hash check.
  - Re-run every affected measure and the package, then run `combine` **against the corrected costings file**, and record the file's SHA-256 in the G5 comment.
  - Re-run every hand-checked household into `data_outputs/drill/g5-household-checks.csv`.
  - Record the new `results_sha256` beside the old one.
- **G4, publication path (by 15:45, heavy slot 2).**
  1. Run `generate --package final` and `combine`, then `uv run python scripts/check_public_data.py dashboard/public/data`.
  2. Under the lock, run `cd dashboard && bun run check-public && NEXT_PUBLIC_MOCK=1 bun run build && bun run start`. **Record the build's wall-clock time.**
  3. Run `scripts/smoke-built-site.sh http://localhost:3000/uk/scottish-budget-2027-28 MOCK`.
  4. Check the robots meta and `X-Robots-Tag` with curl.
  5. Record the floor counts: method and smallest count for each table.

  Nothing is deployed.
- **G6, report draft (15:45–16:05).** In a local copy of the report template (task 7; if it doesn't exist yet, a markdown file `data_outputs/drill/report-draft.md`), fill:
  - the headline bullets: total cost or yield for each year, the household effect, poverty;
  - the measures table;
  - one chart block, from `results.json` at the G4 SHA.

  Every figure must match `results.json`, carry the basis and label, and leave not-computable lines unshown with their reasons, never as £0. The reviewer reads the draft and posts any defect.
- **Stop (16:05).** Log the stop commit. Nothing scored changes after it.

## Freeze at stop

By 16:10, before the answer key, post `FREEZE.txt` on the drill PR. It holds the SHA-256 (`shasum -a 256`) of every scored file at the stop commit:
- the filled scoring sheets;
- both ledger copies;
- `national.csv` and `reconciliation.csv`;
- `results.json` and `receipt.json`;
- every hand-check file;
- `report-draft.md` (or the template copy).

Add the stop commit SHA and the SHA-256 of `FREEZE.txt` itself. A file that changes after the freeze isn't scored.

## Routes, cause and gap classes, the zero rule

These are as in drill 12's `DRILL.md`, unchanged: routes `dashboard-param`, `dashboard-structural`, `needs-pe-uk-first`, `not-computable` and `ledger`, with the same cause and gap classes. A `needs-pe-uk-first` line, or a structural modifier standing in for missing engine logic, earns route credit only if it links a policyengine-uk draft filed before the stop. £0 is never a costing: a coded measure at £0 in every year needs a written `zero_reason` or a not-computable route.

## Disclosure floor

A published cell resting on fewer than 10 survey households is withheld: null, with a reason. Count unique `source_household_id` among the households the cell's figure rests on. A floor applied to rows doesn't meet this rule, even if `check_public_data.py` passes.

## Rubric

| Area | Points | How it's scored |
|---|---|---|
| Example households | 20 | each value within ±1p of the key, on post-correction values |
| National figures | 25 | basis and gap class for each line; not-computable and ledger lines record the costing and the reason |
| Ledger | 20 | route and cause for each line at the stop; trap rows flagged at G1 and left uncoded |
| Publication path | 10 | MOCK banner, noindex meta and header, not-computable lines shown with reasons, floor on survey households, every coded measure on the page |
| Report draft | 10 | every figure matches `results.json`; basis and label present; no £0 for not-computable lines; neutral wording |
| Process | 15 | G0 on time on the certified pair; gates on time; `pytest` green at G1; combine reads the corrected costings; build timed; correction logged and hand rows re-run; `FREEZE.txt` before the key; defects posted within 5 minutes |

## Defects

Post each defect as a comment on the drill PR within 5 minutes of finding it, with the time found, and post the fix in the same thread with the time fixed. A defect kept only in a local file counts as not posted.

## What to log

Fill the clock table as the drill runs, with start, end, machine time, people time and SHA for G0 to G6, the stop and the freeze. Also log:
- each release's arrival time and hash check;
- every heavy run (start, end, peak memory, lock taken and released);
- the production build's time;
- every upstream draft filed;
- every scoring run's commit SHA.

## MOCK and noindex rules

- Every view shows a **MOCK** banner (`NEXT_PUBLIC_MOCK=1`).
- The served HTML carries `noindex, nofollow`, and every response carries `X-Robots-Tag: noindex, nofollow`. Check both on `next start`.
- Nothing is deployed, posted or shared outside the drill PR and issue.
- The drill PR is a draft labelled `not for merge`, and is never merged.

## Packet

The drill owner wrote the packet on 26 November; its hashes are below. The integrator doesn't open any file before its release time, and checks each file's hash on arrival.

| File | Release | SHA-256 |
|---|---|---|
| `00-owner-notes.md` | drill owner only | `fc94f4736a35cebd47ab0f8e5cf03f767c5f20515c87b7554c9171ef4cd218a9` |
| `01-statement.md` | 14:00 | `890f6d846d7f76931257ac6f049dbfba0f3f2ffb2c25a4215e960738a8a8d640` |
| `02-documents.md` | 14:40 | `d121228f896e1b67bcd7b3e2caab74dff689f9c7ef6d347bde82b6ec998af1f0` |
| `02-costings.csv` | 14:40 | `642ff2323dc40143141e4e6851be5fde2928d7ed52aabd8d4220739c7b08f00f` |
| `02-households.csv` | 14:40 | `95d7d23c2a9e711c0f4030feafb01996f366a43bba43efd02c7cc104f3f8856a` |
| `02-scoring-sheet.csv` | 14:40 | `ea4ab2c3e8bda26b94f21e7461c99d81425679899dc92b2004421d2ffdc3771c` |
| `03-correction-notice.md` | 15:15 | `4ced0082606569230d5a5a6df06299e6dc6a67aa73fb3c729f4c42d034ad56e4` |
| `04-answer-key.md` | 16:10 | `681afc82ad6464f1fc1892840b36656071485f3d48e07e82b95e8f8411f20160` |
| `04-answer-key-households.csv` | 16:10 | `42d0f46274d15a739c646a09c98135b49265d1f638997b9a529cb8d139c216d9` |
| `04-answer-key-ledger.csv` | 16:10 | `174f53779b2864a3a49af751a1d4c9f96bd561d12c300dc37fa13775ca38244d` |
| `generate_household_key.py` | 16:10 | `6cf0c171a9767db92f89b21cc1683f15dead66867c7e091791c1ec3e32eb2513` |
| `04-score.py` | 16:10 | `fcdc5cc254dbd6a8d63ccb76aef8e44b49646235f579b79e99224bd3397dd4b6` |
