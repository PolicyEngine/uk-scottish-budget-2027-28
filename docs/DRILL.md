# Drill: Friday 13 November 2026, 14:00–16:30

A timed rehearsal of the day, on a mock statement. It follows the compressed clock used for two drills in one day.

## Packet hygiene

- The drill owner writes the mock statement, the documents, the correction notice and the answer key outside this repository.
- Only the packet hashes are committed, in `data_inputs/packet/HASHES.md`. The scorer checks each file's hash on release.
- Files are released at the set times, not before.
- The drill runs on a draft PR labelled `not for merge`, cut from `main`, not stacked on another unmerged PR.

## Clock

| Time | T | Release | Gate |
|---|---|---|---|
| by 13:30 | – | none | G0: freeze record |
| 14:00 | T+0 | mock statement | G1 by 14:10: coverage ledger, each line routed |
| 14:30 | T+30 | none | G2: provisional numbers, one hand-checked household per coded measure |
| 14:40 | T+40 | documents: costings table, mock forecast, example households, blank scoring sheet | G3 to 15:10: re-base and reconcile |
| 15:15 | T+75 | correction notice | G5: re-run, new scoring SHA |
| 15:40 | T+100 | none | G4: full page on a production build, banner and noindex checked |
| 15:50 | T+110 | none | stop; log the stop commit |
| 16:00 | T+120 | answer key | scoring |
| 16:30 | – | none | retro filed as an issue |

## Roles

| Role | Owns | Does not |
|---|---|---|
| Integrator | branch, clock table, every commit, generation, re-basing | score households |
| Reconciler | ledger, reconciliation CSV, defects posted as PR comments within 5 minutes | push code |
| Scorer (reconciler after the documents) | example households, one commit SHA per scoring run | edit reform code |

## Ledger

Every statement line gets a route (`dashboard-param`, `dashboard-structural`, `ledger`, `not-computable`, `needs-pe-uk-first`) and a cause class (`parameter`, `formula`, `data_calibration`, `basis`, `timing_fiscal_calendar`, `coverage`, `interaction`, `baseline_mismatch`).

What a Scottish Budget packet should exercise:

- Income tax thresholds and rates (parameter routes), with the above-personal-allowance encoding.
- At least one trap row already in the baseline (for example the higher, advanced and top threshold freeze, or CPI uprating of Scottish Child Payment).
- A measure the model cannot run yet (Scottish property income rates, a Scotland-wide £100 payment on 2.151.0) and one the data cannot show (Bands I and J).
- A council tax freeze, which needs the dataset re-projected.
- A basis trap: an official costing that includes behaviour, or a payment whose tax year is unclear.

## Rubric

| Area | Points |
|---|---|
| Example households within ±1p | 20 |
| National figures: basis and gap class | 30 |
| Ledger: class, route and cause | 25 |
| Publication path (banner, noindex, disclosure checks) | 10 |
| Process: gates on time, one SHA per run, correction logged | 15 |

## Clock table (filled in by the integrator)

| Step | Start | End | Machine time | People time | SHA |
|---|---|---|---|---|---|
| G0 | | | | | |
| G1 | | | | | |
| G2 | | | | | |
| G3 | | | | | |
| G5 | | | | | |
| G4 | | | | | |
| Stop | | | | | |
