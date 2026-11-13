# Method

Status: pre-release template. Every measure is a placeholder.

## Model and data

- Model: PolicyEngine UK, a static microsimulation model of the UK tax and benefit system.
- Engine and data pair (locked in `uv.lock`): Microcosm build `uk-frs-calibration-attempt-20261110T204756Z-9e18f010` (SHA-256 `adb6204d0af5e08a42cccec81250ce116518687f964e31c654a17d658b3416e8`, Hugging Face dataset `policyengine/populace-uk-private`, `releases/microcosm-uk-2024-25-national/uk-frs-calibration-attempt-20261110T204756Z-9e18f010/microcosm_uk_2024_25.h5`) with policyengine-uk 2.177.7 and policyengine-core 3.34.10, the versions the build was made and certified on. The rule is the newest published build with the engine it was built on, even when no policyengine.py release covers the pair, and never a build with another engine version. No policyengine.py release pins 2.177.7, so every figure is labelled "build uk-frs-calibration-attempt-20261110T204756Z-9e18f010, policyengine-uk 2.177.7, not in a policyengine.py release". Build `…-6f918b81` (also 2.177.7) will supersede this one once it is published; the switch is the one constant `DATA_BUILD` in `src/scottish_budget/data_build.py`. A run records the versions it loaded and the dataset's SHA-256 in `results.json` and `receipt.json`; nothing is typed in by hand.
- Every population simulation is built in `src/scottish_budget/engine.py` with `policyengine_uk.Microsimulation`, loaded directly, not through `policyengine.uk.managed_microsimulation` (whose bundle pins another pair). With no `--dataset`, the build is downloaded from Hugging Face. Any file, downloaded or named, must have the build's SHA-256, and the installed policyengine-uk must be 2.177.7; the run refuses anything else.
- 2.177.7, like 2.174.1, has the UK Budget 2026 measures (Pension Tax Allowance, household energy payment; from 2.170.2) and uprates the carer supplement (from 2.165.1), so those limits do not apply on the pinned engine (issue #1). The 6.11.1 to 6.14.0 bundles pinned 2.151.0, which lacked all three.

## Forecast

Every simulation, baseline and reform alike, runs on the OBR's October 2026 forecast (`src/scottish_budget/forecast/obr_october_2026.json`, the file the Autumn Budget 2026 dashboard uses), applied before data load. policyengine-uk 2.151.0 shipped the March 2026 forecast, so without the overlay 2027 CPI was 2.0% rather than 3.42%. policyengine-uk 2.174.1 already ships the October 2026 forecast (2.177.7 adds series but changes none of the overlay's) for CPI, RPI, average earnings and CPIH: 73 of the overlay's 103 year values equal the engine's, and the other 30 differ slightly (CPI AHC by 0.02 points, house prices, per-capita GDP and similar). The overlay sets values rather than adding to them, so it does not apply twice; whether to keep it is open. On the day, the integrator decides whether Scottish earnings and prices should follow the Scottish Fiscal Commission's 3 December forecast instead, and records the choice here.

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
