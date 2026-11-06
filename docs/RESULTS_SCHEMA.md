# results.json schema

Written to `dashboard/public/data/results.json` by `scottish-budget generate --placeholder` (before the day) or `scottish-budget combine` (on the day). `publication.validate_results` enforces the rules. `combine` also writes `receipt.json` beside it: git SHA and clean-tree flag, installed versions, bundle dataset, dataset SHA-256, the time, the measures scored, the placeholders dropped and the SHA-256 of `results.json`.

## meta

| Field | Type | Meaning |
|---|---|---|
| `status` | string | `pre-release template`, `provisional` (G2) or `published` |
| `placeholder` | bool | True only in the pre-release file |
| `notice` | string | Must contain "placeholder" while `placeholder` is true |
| `policyengine`, `policyengine_uk`, `dataset` | string | Engine and data pair: read at run time on a model file |
| `dataset_sha256` | string or null | Required on a model file |
| `forecast` | `{vintage, source_url}` | The forecast overlay |
| `basis` | object | The declared basis (METHOD.md) |
| `years` | list of `{year, label}` | Policy years, e.g. `{2027, "2027-28"}` |
| `disclosure_floor` | int | Survey households below which a cell is withheld (10) |

## measures[]

| Field | Type | Meaning |
|---|---|---|
| `id`, `name`, `description` | string | From the registry; public text |
| `route`, `route_label` | string | Route slug and its plain label |
| `cause`, `topic`, `likelihood` | string | Ledger fields |
| `status` | string | `placeholder`, `provisional`, `published`, `not-computable`, `ledger`, `pending` |
| `reason` | string or null | Required when `status` is `not-computable` |
| `basis_note` | string or null | Public note; null when it would repeat `reason` |
| `first_year` | int or null | First fiscal year, when after 2027-28 |
| `placeholder`, `publish` | bool | A placeholder is never published; `published` needs `publish` |
| `in_baseline`, `calculator` | bool | Trap row; shown with the example households |
| `issues` | list of int | Issues in this repository |
| `budgetary_impact` | list of `{year, label, value_bn}` or null | £bn; negative is a cost. Null, never 0, when not computed |

## Tables

- `decile_impact[]`: `{measure_id, year, decile, avg_change_gbp, pct_change, n_records}`, by Scottish decile, per measure (they add across measures). `pct_change` is in per cent. Values are null with `withheld` set below the floor.
- `winners_losers[]`, `poverty[]`, `council_tax_bands[]`, `scotland_vs_rest_of_uk[]`: from the package run (`measure_id` `package`), because they do not add across measures.
- `official_costings[]`: `{measure_id, year, official_value_bn, source, basis}` once the costings file exists.
- `households[]`: `{id, label, year, baseline_net_income, reform_net_income, change, rest_of_uk_net_income, scotland_minus_rest_of_uk}`, £ a year. All null in the pre-release file.
