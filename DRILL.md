# Drill: Friday 13 November 2026, 14:00–16:30

A timed rehearsal of Scottish Budget day (3 December 2026) on a mock statement. It uses the compressed clock for an afternoon drill. All times are London time.

This file holds the plan only, and is the only copy of the clock and the packet hashes; the drill issue (#11) links here. It says nothing about the mock measures. The statement, documents, correction notice and answer key are held outside this repository by the drill owner and are released at the times below.

The drill runs on a local run branch cut from the head of `bump-policyengine-6.17.2` (PR #15, which is stacked on the template branch `template-dashboard`, PR #10, and moves the engine to policyengine 6.17.2), so it has the pipeline, the page, CI and the new pin. Before G0 the integrator cuts it, merges `drill-plan` into it for this file and the drill CSVs, and records the start SHA and the bump-branch SHA it was cut from. Drills never merge, so the unmerged bump branch is allowed as the base.

## Clock

| Time | T | Release | Gate |
|---|---|---|---|
| by 13:30 | – | none | G0: freeze record |
| 14:00 | T+0 | statement | G1 by 14:10: coverage ledger, every line routed |
| 14:30 | T+30 | none | G2: provisional numbers against the statement, one hand-checked household per coded measure |
| 14:40 | T+40 | documents: costings table, mock forecast, example households, blank scoring sheet | G3 by 15:10: re-base and reconcile; every gap over 10% has a written reason |
| 15:15 | T+75 | correction notice | G5 by 15:35: re-run everything affected, new scoring SHA |
| 15:40 | T+100 | none | G4: full page on a local production build, MOCK banner and noindex checked |
| 15:50 | T+110 | none | stop: log the stop commit |
| 16:00 | T+120 | answer key | scoring (to about 16:20) |
| 16:30 | – | none | retro filed on the drill issue |

### Engine and data pair

The drill runs on the pair locked on the run branch: policyengine 6.17.2, policyengine-uk 2.174.1, policyengine-core 3.33.3, Microcosm `microcosm-uk-2024-25-national-20261107T020434Z-eeb6093e` (SHA-256 `0a9b77db1c0dee2693cb2d47bad68da34cb662916eee4829942bcd45de581f25`, the build 6.17.2 certifies), on the OBR October 2026 forecast overlay (2.174.1 already ships most of that forecast; see PR #15). This holds whatever is released before 13 November. Figures from any pair not recorded at G0 are not scored.

### Gates

Every heavy command below (a `generate`, a production build) runs under the lock with at least 14 GB free, as in `docs/RUNBOOK.md` ("Heavy runs"), one measure per process.

- **G0, freeze record (by 13:30).** `uv run --extra model scottish-budget freeze`, pasted into the clock table as a PR comment: start SHA, clean tree, policyengine, policyengine-uk and core versions, bundle dataset name and SHA-256. Every figure carries the certified pair above, or the label "unvalidated under this engine".
- **G1, coverage ledger (14:00–14:10).** One line per statement item in `data_inputs/drill/coverage-ledger.csv`, each with a route and a cause class (below). Items already in the baseline are flagged here, not coded. Kept measures get their values and `placeholder=False` in `reforms.py`; registry entries the statement does not contain are deleted.
- **G2, provisional numbers (by 14:30).** For each coded measure: `uv run --extra model scottish-budget generate --reforms <id>`; then `generate --package provisional` and `scottish-budget combine --provisional`. Measures are not signed off at G2 (`publish` stays False); the file says "provisional". One hand-checked household per coded measure, starting from `data_inputs/household_fixtures/`.
- **G3, re-base and reconcile (14:40–15:10).** Re-base to the baseline the costings use, fill `data_inputs/drill/reconciliation.csv` and run `uv run scottish-budget reconcile --official data_inputs/drill/reconciliation.csv` until it exits 0: every gap over 10% has a written reason and a cause class. Then set `publish=True` on each reconciled measure. Update ledger causes after G3.
- **G5, correction (15:15–15:35).** Re-run every affected measure and the package, including hand-computed household rows, `combine` again, and record the new scoring SHA (`results_sha256` in `dashboard/public/data/receipt.json`).
- **G4, publication path (by 15:40).** `generate --package final` and `combine`; then from the repository root `uv run python scripts/check_public_data.py dashboard/public/data`, and under the lock `cd dashboard && bun run check-public && NEXT_PUBLIC_MOCK=1 bun run build && bun run start`. In a second shell, `scripts/smoke-built-site.sh http://localhost:3000/uk/scottish-budget-2027-28 MOCK` checks every tab, the banner starting with MOCK, the robots meta (`curl -s <url> | grep -o '<meta name="robots"[^>]*>'` must contain `noindex` and `nofollow`; Next adds `nocache`) and the `X-Robots-Tag` header (`curl -sI <url> | grep -i x-robots-tag`). Then stop the server and release the lock. Nothing is deployed.
- **Stop (15:50).** Log the stop commit in the clock table. Nothing is pushed after it.

## Roles

| Role | Owns | Does not |
|---|---|---|
| Integrator | branch, clock table, every commit, generation, re-basing | score households; open sealed files early |
| Reconciler | ledger, reconciliation CSV, defects posted as PR comments within 5 minutes; the hash check of each file on its release (14:00, 14:40, 15:15) | push code |
| Scorer (the reconciler after the documents) | example households, one commit SHA per scoring run; the hash check of the answer key at 16:00 | edit reform code |
| Drill owner (not the integrator) | the sealed packet, releases at the set times, the answer key | take part in coding |

Who holds each role is recorded on the drill issue, not here. Only the integrator pushes. Reviews are posted as PR comments and read at once.

## Routes and cause classes

Every ledger line gets one route. The route says where the work lands:

| Route | Where the work lands | Meaning |
|---|---|---|
| `dashboard-param` | this repo | a parameter change in `reforms.py`, or a baseline correction in `baseline_parameter_changes` |
| `dashboard-structural` | this repo | a hand-written modifier in `measures/`, one module per modifier |
| `needs-pe-uk-first` | policyengine-uk | the engine has no route; a draft upstream fix is filed the same day and the line links it |
| `not-computable` | data (Microcosm) | the input the measure acts on is not in the data; published with the reason, never as £0 |
| `ledger` | none | not modelled (business taxes, spending, items already in the baseline); the official figure is recorded |

Every line also gets one cause class: `parameter`, `formula`, `data_calibration`, `basis`, `timing_fiscal_calendar`, `coverage`, `interaction`, `baseline_mismatch`.

Declare the basis once, at G1, and repeat it next to every figure: static or behavioural, gross or net, accrued or cash, fiscal year (2026-27, 2027-28, 2028-29), and which baseline.

## Rubric

| Area | Points | How it is scored |
|---|---|---|
| Example households | 20 | each reported value within ±1p of the key, on the values in force after the correction notice |
| National figures | 30 | basis and gap class for each statement line; for not-computable and ledger lines the basis column carries the costing's basis |
| Ledger | 25 | route and cause for each line, as they stand at the stop commit |
| Publication path | 10 | MOCK banner, noindex, not-computable lines shown with reasons, disclosure floor, every coded measure on the page |
| Process | 15 | gates on time, one SHA per scoring run, the correction logged and acted on, defects posted within 5 minutes |

Trap rows (statement items already in the baseline) are scored. The answer key states its own rounding and part-year rules, and the documents state the same rules at 14:40.

## What to time and log

The integrator fills the clock table as the drill runs. For each step, record start and end times, and split machine time (generation, builds, tests) from people time (reading, coding, review).

| Step | Start | End | Machine time | People time | SHA |
|---|---|---|---|---|---|
| G0 | | | | | |
| G1 | | | | | |
| G2 | | | | | |
| Documents received | | | | | |
| G3 | | | | | |
| Correction received | | | | | |
| G5 (due 15:35) | | | | | |
| G4 (due 15:40) | | | | | |
| Stop | | | | | |

Also log:

- every scoring run, with one commit SHA each;
- the time each release arrived and the hash check result;
- every defect, as a PR comment with the time found and the time fixed;
- every upstream draft filed (repository, link, time);
- any heavy run: start, end and peak memory, with the lock taken.

## MOCK and noindex rules

- The drill branch shows a banner on every view that starts with **MOCK** and says the figures are drill figures, not the Scottish Budget. The page does this when built with `NEXT_PUBLIC_MOCK=1`; the template's "Pre-release template" banner is not enough.
- The served HTML carries a robots meta with `noindex` and `nofollow` (Next renders `noindex, nofollow, nocache`), and every response carries `X-Robots-Tag: noindex, nofollow`. Check both in the output of `next start` (G4 above), not only in the source.
- Nothing from the drill is deployed, posted or shared outside the drill PR and the drill issue.
- The drill PR is a draft labelled `not for merge`. It is never merged.
- Public files on the drill branch pass both checks: from the repository root `uv run python scripts/check_public_data.py dashboard/public/data`, and from `dashboard/` `bun run check-public`. No ids or weights, the 10-record floor, no area codes.

## Packet hygiene

- The packet is written and held outside this repository. Only the hashes are committed, below.
- Files are released at the set times, not before. The reconciler (the scorer at 16:00) checks each file's SHA-256 when it arrives (`shasum -a 256 <file>`) against the table below and logs the result.
- The integrator does not open any packet file before its release time.
- Code goes in waves: parameters, then modifiers, then new variables.

## Packet hashes (SHA-256)

| File | Release | SHA-256 |
|---|---|---|
| `00-owner-notes.md` | drill owner only | `5d4002a72ae27abe451a1d959ec464e2d973674f8fb0d82b3d4b5def9ffb9845` |
| `01-statement.md` | 14:00 | `a0ed4bb0890dbc8ec03da4e469971255797465a5377db08e73c4181f6fc08c23` |
| `02-documents.md` | 14:40 | `5f11cdfccf9b0009c75865cd1459b329c326c9591e415cca8443f71a95c281ae` |
| `02-costings.csv` | 14:40 | `949ee0de8221e3664b5875a9539714f5f8321dcb842641b3fca856e007fdcd1d` |
| `02-households.csv` | 14:40 | `cf3681da743f5437885592e2ae4c1b2608a77a5cf8e99a4efae226768d27cf76` |
| `02-scoring-sheet.csv` | 14:40 | `e50340aed1246075088a0622376f2b875bc17f1d920c4ab3f3b855d676f16093` |
| `03-correction-notice.md` | 15:15 | `867bacfbc828f745d702d1cbbedf6d178348859b97eddacc342fca0deebd2b4a` |
| `04-answer-key.md` | 16:00 | `1bc73f97b5a11c70c9bd26e36757416b544615c0aa5f633bd6d41dceff527647` |
| `04-answer-key-households.csv` | 16:00 | `9e96679ddfd2a5f0b2aa6a18e3b3ef6538353d3429c3a61637179b8399e0b224` |
| `04-answer-key-ledger.csv` | 16:00 | `9adb22fa76943300e26a3dea4c9920eb63053251e60989b5656452b7d2869970` |
| `generate_household_key.py` | 16:00 | `01871a969b2e75e38a9e99ab046b196c0db7e3e1877c39888ac9f5c1bea84c80` |
| `generate_national_key.py` | 16:00 | `c684890d3ddc6d6c510e301db6c97f863ec9d61e7e146033dbe07554cada9718` |
