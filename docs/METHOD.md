# Method

Status: pre-release template. Every measure is a placeholder.

## Model and data

- Model: PolicyEngine UK, a static microsimulation model of the UK tax and benefit system.
- Engine and data pair (provisional): policyengine.py 6.11.1, which pins policyengine-uk 2.151.0, with Microcosm build `microcosm-uk-2024-25-national-20261025T091414Z-a6299504`.
- 2.151.0 lacks the Pension Tax Allowance and the £100 household energy payment, does not uprate the carer supplement, and has different starter and basic thresholds from 2.175.4 (issue #1). If no recertified bundle lands before the day, the run is unmanaged on a named pair and every figure is labelled "unvalidated under this engine".

## Basis (declared once)

All figures use the basis in `src/scottish_budget/years.json`:

| | |
|---|---|
| Period | Fiscal year, April to March; 2027 means 2027-28 |
| Gross or net | Gross cost or yield to the Scottish Government, before any block grant adjustment |
| Cash or accrued | Cash, nominal |
| Behaviour | Static: no behavioural response unless a measure says so |

Official Scottish Government ready reckoners and Scottish Fiscal Commission costings include behavioural responses, so static figures differ from them, most for the top bands.

## Measures

Each measure is a parameter change or a hand-written modifier against current law (`src/scottish_budget/reforms.py`). Income tax thresholds are entered above the personal allowance: a starter band top of £17,116 encodes as 4,546.

A measure that acts only through an input the data lack is published as not computable, with the reason, and never as £0 (`data_limits.py`). A measure the model cannot represent yet is held as `needs-pe-uk-first` (`model_limits.py`).

## Rest-of-UK comparison

Each example household has a twin with `pays_scottish_income_tax` set to False, so only the income tax schedule changes.

## Disclosure

Public files carry no record identifiers or weights. A cell resting on fewer than 10 survey households is withheld.

## Geography

Scotland as a whole. The national Microcosm file has no geography below region (issue #8).
