# results.json schema

Written by `scottish-budget generate` to `dashboard/public/data/results.json`. Every field below is required; there are no defaults. `publication.validate_results` enforces the rules.

## meta

| Field | Type | Meaning |
|---|---|---|
| `status` | string | `pre-release template` until the day |
| `placeholder` | bool | True while any figure is a placeholder |
| `notice` | string | Text shown on the page; must contain "placeholder" while `placeholder` is true |
| `policyengine`, `policyengine_uk`, `dataset` | string | Engine and data pair |
| `basis` | object | The declared basis (see METHOD.md) |
| `years` | list of `{year, label}` | Policy years, e.g. `{2027, "2027-28"}` |
| `disclosure_floor` | int | Survey households below which a cell is withheld (10) |

## measures[]

| Field | Type | Meaning |
|---|---|---|
| `id`, `name`, `description` | string | From the registry |
| `route` | string | `dashboard-param`, `dashboard-structural`, `ledger`, `not-computable`, `needs-pe-uk-first` |
| `cause` | string | Cause class for the ledger |
| `topic` | string | `income_tax`, `social_security`, `council_tax`, `property_tax`, `other` |
| `status` | string | `placeholder`, `published`, `not-computable`, `ledger`, `pending` |
| `reason` | string or null | Required when `status` is `not-computable` |
| `placeholder`, `publish` | bool | A placeholder is never published |
| `in_baseline` | bool | Trap row: already in the baseline |
| `calculator` | bool | Shown in the household calculator |
| `issues` | list of int | Issues in this repository |
| `budgetary_impact` | list of `{year, label, value_bn}` or null | Change in government revenue net of spending, £bn; negative is a cost. Null, never 0, when not computed |

## decile_impact[]

`{measure_id, decile, avg_change_gbp, pct_change, n_records}`. Average change in household net income, £ a year, by household income decile in Scotland. Values are null with `withheld` set when `n_records` is below the floor. `n_records` is the count of survey households, not a weight.

## households[]

`{id, label, baseline_net_income, reform_net_income, rest_of_uk_net_income}`, £ a year, for the presets in `household.py`.
