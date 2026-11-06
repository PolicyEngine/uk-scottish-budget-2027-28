# Method

Status: pre-release template. Every measure is a placeholder.

## Model and data

- Model: PolicyEngine UK, a static microsimulation model of the UK tax and benefit system.
- Engine and data pair (locked in `uv.lock`): policyengine.py 6.14.0, which pins policyengine-uk 2.151.0 and policyengine-core 3.33.3, with Microcosm build `microcosm-uk-2024-25-national-20261025T091414Z-a6299504`. A run records the versions it loaded and the dataset's SHA-256 in `results.json` and `receipt.json`; nothing is typed in by hand.
- Every population simulation goes through `policyengine.uk.managed_microsimulation`, which enforces the bundle's certified dataset (`src/scottish_budget/engine.py`). A named dataset path is allowed only when given explicitly with `--dataset`, and `--dataset-sha256` refuses any other file.
- 2.151.0 lacks the Pension Tax Allowance and the UK household energy payment, and does not uprate the carer supplement (issue #1). policyengine.py#731 would move the pin to 2.165.1, which uprates the carer supplement but still lacks the UK Budget 2026 measures; those first ship in 2.170.2, which has no certified Microcosm build yet. If the pin is not on a certified pair on the day, every figure is labelled "unvalidated under this engine".

## Forecast

Every simulation, baseline and reform alike, runs on the OBR's October 2026 forecast (`src/scottish_budget/forecast/obr_october_2026.json`, the file the Autumn Budget 2026 dashboard uses), applied before data load. policyengine-uk 2.151.0 ships the March 2026 forecast, so without the overlay 2027 CPI is 2.0% rather than 3.42%, and current-law thresholds and benefit rates for 2027-28 and 2028-29 are too low. On the day, the integrator decides whether Scottish earnings and prices should follow the Scottish Fiscal Commission's 3 December forecast instead, and records the choice here.

## Basis (declared once)

All figures use the basis in `src/scottish_budget/years.json`:

| | |
|---|---|
| Period | Fiscal year, April to March; 2027 means 2027-28 |
| Gross or net | Gross cost or yield to the Scottish Government, before any block grant adjustment |
| Cash or accrued | Cash, nominal |
| Behaviour | Static: no behavioural response unless a measure says so |

Official Scottish Government ready reckoners and Scottish Fiscal Commission costings include behavioural responses, so static figures differ from them, most for the top bands.

## Data year

Microcosm is built from 2024-25 survey data and projected to each policy year on the forecast above.

## Measures

Each measure is a parameter change or a hand-written modifier against current law (`src/scottish_budget/reforms.py`, `src/scottish_budget/measures/`). Income tax thresholds are entered above the personal allowance: a starter band top of £17,116 encodes as 4,546. A measure with its own baseline (`baseline_parameter_changes`) is scored against that baseline.

A measure that acts only through an input the data lack is published as not computable, with the reason, and never as £0 (`data_limits.py`). A measure the model cannot represent yet is held as `needs-pe-uk-first` (`model_limits.py`).

## Distribution

Deciles are Scottish deciles of equivalised household net income: households in Scotland ranked against each other, weighted by people. Percentage changes are the change in net income over baseline net income in each decile. Winners and losers, child poverty (before and after housing costs) and council tax bands come from one run of all scored measures together, because they do not add up across measures.

## Rest-of-UK comparison

Each example household has a twin with `pays_scottish_income_tax` set to False, so only the income tax schedule changes. The population comparison taxes every Scottish taxpayer on the rest-of-UK schedule in the same way.

## Not modelled

Air Departure Tax, non-domestic rates, behaviour in Land and Buildings Transaction Tax purchases, and spending other than cash payments to households. These are recorded with the official costing.

## Disclosure

Public files carry no record identifiers or weights. A cell resting on fewer than 10 survey households is withheld.

## Geography

Scotland as a whole. The national Microcosm file has no geography below region. The bundle's local-area file has all 32 Scottish councils, but its fit to income tax by council is not yet checked, so council results are not shown (issue #8).
