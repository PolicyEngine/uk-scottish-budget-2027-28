# Drill: Friday 13 November 2026, 14:00–16:30

A timed rehearsal of Scottish Budget day (3 December 2026) on a mock statement. It uses the compressed clock for an afternoon drill. All times are London time.

This file holds the plan only. It says nothing about the mock measures. The statement, documents, correction notice and answer key are held outside this repository by the drill owner and are released at the times below. For this drill, this file replaces `docs/DRILL.md` on the template branch (PR #10).

## Clock

| Time | T | Release | Gate |
|---|---|---|---|
| by 13:30 | – | none | G0: freeze record |
| 14:00 | T+0 | statement | G1 by 14:10: coverage ledger, every line routed |
| 14:30 | T+30 | none | G2: provisional numbers against the statement, one hand-checked household per coded measure |
| 14:40 | T+40 | documents: costings table, mock forecast, example households, blank scoring sheet | G3 by 15:10: re-base and reconcile; every gap over 10% has a written reason |
| 15:15 | T+75 | correction notice | G5: re-run everything affected, new scoring SHA |
| 15:40 | T+100 | none | G4: full page on a local production build, MOCK banner and noindex checked |
| 15:50 | T+110 | none | stop: log the stop commit |
| 16:00 | T+120 | answer key | scoring (to about 16:20) |
| 16:30 | – | none | retro filed on the drill issue |

### Gates

- **G0, freeze record (by 13:30).** Start SHA, policyengine and policyengine-uk versions, Microcosm dataset name and SHA-256, and either the certified engine and data pair or the label "unvalidated under this engine" on every figure.
- **G1, coverage ledger (14:00–14:10).** One line per statement item, each with a route and a cause class (below). Items already in the baseline are flagged here, not coded.
- **G2, provisional numbers (by 14:30).** National figures for each coded line, and one hand-checked household per coded measure.
- **G3, re-base and reconcile (14:40–15:10).** Re-base to the baseline the costings use, fill the reconciliation CSV, and give every gap over 10% a written reason and a cause class. Update ledger causes after G3.
- **G5, correction (from 15:15).** Re-run every affected figure, including hand-computed household rows, and record a new scoring SHA.
- **G4, publication path (by 15:40).** `next build` then `next start` on the drill branch, locally. Nothing is deployed.
- **Stop (15:50).** Log the stop commit in the clock table. Nothing is pushed after it.

## Roles

| Role | Person | Owns | Does not |
|---|---|---|---|
| Integrator | Vahid | branch, clock table, every commit, generation, re-basing | score households; open sealed files early |
| Reconciler | to be confirmed | ledger, reconciliation CSV, defects posted as PR comments within 5 minutes | push code |
| Scorer (the reconciler after the documents) | to be confirmed | example households, one commit SHA per scoring run, hash checks | edit reform code |
| Drill owner | to be confirmed (not the integrator) | the sealed packet, releases at the set times, the answer key | take part in coding |

Only the integrator pushes. Reviews are posted as PR comments and read at once.

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
| G5 | | | | | |
| G4 | | | | | |
| Stop | | | | | |

Also log:

- every scoring run, with one commit SHA each;
- the time each release arrived and the hash check result;
- every defect, as a PR comment with the time found and the time fixed;
- every upstream draft filed (repository, link, time);
- any heavy run: start, end and peak memory, with the lock taken.

## MOCK and noindex rules

- The drill branch shows a banner on every view that starts with **MOCK** and says the figures are drill figures, not the Scottish Budget. The template's "Pre-release template" banner is not enough.
- The served HTML carries `<meta name="robots" content="noindex, nofollow">`. Check it in the output of `next start`, not only in the source.
- Nothing from the drill is deployed, posted or shared outside the drill PR and the drill issue.
- The drill PR is a draft labelled `not for merge`. It is never merged.
- Public files on the drill branch pass `scripts/check_public_data.py` and `scripts/check-public-files.mjs`: no ids or weights, the 10-record floor, no area codes.

## Packet hygiene

- The packet is written and held outside this repository. Only the hashes are committed, below.
- Files are released at the set times, not before. The scorer checks each file's SHA-256 when it arrives (`shasum -a 256 <file>`).
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
