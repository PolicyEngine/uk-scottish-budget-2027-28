# Method

Status: pre-release template. Every measure is a placeholder.

## Model and data

- Model: PolicyEngine UK, a static microsimulation model of the UK tax and benefit system.
- Engine and data pair (locked in `uv.lock`): the certified bundle in policyengine.py 6.20.3, which pins policyengine-uk 2.179.2 and policyengine-core 3.34.10 and certifies Microcosm build `uk-frs-calibration-attempt-20261122T100732Z-b891aa69` (SHA-256 `ae116bc3cff798fe68df253083f0b26d779e02a0a818ee68df7d29fbc557165a`, Hugging Face dataset `policyengine/populace-uk-private`, `releases/microcosm-uk-2024-25-national/uk-frs-calibration-attempt-20261122T100732Z-b891aa69/microcosm_uk_2024_25.h5` at revision `a80a4bf70ab4ffeac77357fe0633d3cee4ce7401`), the national build made on that engine. Results are for Scotland as a whole, so the bundle's local-area file is not used. Every figure is labelled "build b891aa69, policyengine-uk 2.179.2, certified in policyengine 6.20.3". The repo moved to this bundle on 26 November 2026 from build 6f918b81 on policyengine-uk 2.177.7, which no policyengine.py release covered. A bundle switch is the `policyengine[uk]` pin in `pyproject.toml` and the one constant `DATA_BUILD` in `src/scottish_budget/data_build.py`. A run records the versions it loaded and the dataset's SHA-256 in `results.json` and `receipt.json`; nothing is typed in by hand.
- Every population simulation is built in `src/scottish_budget/engine.py` through `pe.uk.managed_microsimulation`. With no `--dataset`, policyengine.py downloads the certified file into `./data/` (git-ignored) and checks its SHA-256; a named file must have the same SHA-256. Before any data load the run refuses an installed policyengine, policyengine-uk or policyengine-core, or a policyengine.py bundle, other than `DATA_BUILD`'s. At G0, `scottish-budget freeze` checks the installed packages, policyengine.py's pins and the build's own release manifest against `DATA_BUILD`, and `engine_matches_build` is true only if all three agree.
- 2.179.2, like 2.174.1 and 2.177.7, has the UK Budget 2026 measures (Pension Tax Allowance, household energy payment; from 2.170.2) and uprates the carer supplement (from 2.165.1), so those limits do not apply on the pinned engine (issue #1). The 6.11.1 to 6.14.0 bundles pinned 2.151.0, which lacked all three.

## Forecast

Every simulation, baseline and reform alike, runs on the OBR's October 2026 forecast (`src/scottish_budget/forecast/obr_october_2026.json`, the file the Autumn Budget 2026 dashboard uses), applied before data load. policyengine-uk 2.151.0 shipped the March 2026 forecast, so without the overlay 2027 CPI was 2.0% rather than 3.42%. policyengine-uk 2.174.1 already ships the October 2026 forecast (2.177.7 and 2.179.2 add series but change none of the overlay's) for CPI, RPI, average earnings and CPIH: 73 of the overlay's 103 year values equal the engine's, and the other 30 differ slightly (CPI AHC by 0.02 points, house prices, per-capita GDP and similar). The overlay sets values rather than adding to them, so it does not apply twice; whether to keep it is open. On the day, the integrator decides whether Scottish earnings and prices should follow the Scottish Fiscal Commission's 3 December forecast instead, and records the choice here.

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

Example households claim every benefit they are eligible for: in a hand-built household `would_claim_uc` and `would_claim_scp` default to true. A household marked not claiming has both set to false (UC on its benefit unit, SCP on its members), so it gets neither. Population figures use the take-up draws stored in Microcosm instead. Gaps to official costings that include behaviour are basis gaps, not take-up (`docs/RUNBOOK.md`, Gap reasons at G3).

## Not modelled

Air Departure Tax, non-domestic rates, behaviour in Land and Buildings Transaction Tax purchases, and spending other than cash payments to households. These are recorded with the official costing.

## Disclosure

Public files carry no record identifiers or weights. A cell resting on fewer than 10 survey households is withheld.

## Geography

Scotland as a whole. The national Microcosm file has no geography below region. The bundle's local-area file has all 32 Scottish councils, but its fit to income tax by council is not yet checked, so council results are not shown (issue #8).
