# Scottish Budget 2027-28 dashboard

PolicyEngine dashboard for the Scottish Budget 2027-28, planned for 3 December 2026 alongside the Scottish Fiscal Commission's economic and fiscal forecasts. It will show the tax and benefit changes in the draft Budget and their effect on households in Scotland.

**Status: pre-release template.** Nothing in this repository is a costing of the Budget. Until the Budget is published, every measure is a placeholder and every figure is a placeholder.

## What the dashboard will show

- **Cost or yield** of each personal tax and benefit measure in 2027-28 and 2028-29, beside the Scottish Fiscal Commission's costing where one exists.
- **Scottish income tax**: the 2026-27 and 2027-28 band schedules, marginal rates by gross income, and how much more or less an identical taxpayer pays in Scotland than in the rest of the UK.
- **Who gains and who loses**: average change in net income by income decile and by family type, and the share of households better or worse off.
- **Poverty**: the change in relative child poverty before and after housing costs.
- **Social security**: Scottish Child Payment (including the under-one premium), carer payments and other Scottish payments the model covers.
- **Council tax**: any payment keyed on council tax band, a freeze or cap on bills, and Bands I and J (from April 2028).
- **Household examples**: net income for a set of example households in 2026-27 and 2027-28, with the rest-of-UK equivalent.
- **Method and data**: what is modelled, what is not, and why.

## Method in brief

The figures will come from PolicyEngine UK, a static microsimulation model of the UK tax and benefit system, run on Microcosm, PolicyEngine's calibrated survey-based dataset. Each measure is a change to model parameters (or, where needed, a change to a formula) compared against current law. Results are static: they do not include changes in behaviour unless a section says so. Costs are on a fiscal-year basis (April to March). A measure that acts only through something the data do not hold is reported as not computable, with the reason, and never as £0.

## Data and model versions

| Component | Version |
|---|---|
| policyengine (Python) | 6.17.2 (certified bundle; `uv.lock`) |
| policyengine-uk | 2.174.1 (pinned by the bundle) |
| Microcosm | `microcosm-uk-2024-25-national-20261107T020434Z-eeb6093e` |
| Forecast | OBR October 2026, applied to every simulation |

`docs/METHOD.md` explains the pin and what it lacks; a run records what it actually loaded in `receipt.json`.

## How to run

Pipeline (Python 3.13, [uv](https://docs.astral.sh/uv/)):

```
uv sync --extra dev
uv run pytest
uv run scottish-budget generate --placeholder   # writes dashboard/public/data/results.json
```

Real runs need the model extra (`uv sync --extra model --extra dev`) and load Microcosm; see `docs/RUNBOOK.md` first. Each measure runs in its own process (`scottish-budget generate --reforms ID`), then `scottish-budget combine` writes `results.json`. A placeholder measure refuses to run. `make help` lists the shortcuts.

Dashboard (Next.js 16, React 19, Recharts, [bun](https://bun.sh)):

```
cd dashboard
bun install
bun run test
bun run dev
```

Every page shows a pre-release banner and is marked noindex. Nothing deploys from this repository.

## Layout

| Path | What |
|---|---|
| `src/scottish_budget/reforms.py` | Measure registry: every candidate measure, its route and limits (all placeholders) |
| `src/scottish_budget/data_limits.py`, `model_limits.py` | What the data and the model cannot show yet |
| `src/scottish_budget/household.py` | Example households and their rest-of-UK twins |
| `src/scottish_budget/engine.py`, `forecast/` | The engine entry point, provenance and the forecast overlay |
| `src/scottish_budget/national.py`, `pipeline.py`, `cli.py` | One measure per run, combined into `results.json` |
| `src/scottish_budget/measures/` | Hand-written modifiers, one per module |
| `src/scottish_budget/reconcile.py` | G3 reconciliation against official costings |
| `src/scottish_budget/publication.py`, `scripts/check_public_data.py` | Disclosure floor and public-data checks |
| `docs/` | Method, schema, runbook, drill, candidate reforms, risk register |
| `data_inputs/` | Expected effects, official figures, drill packet hashes |
| `dashboard/` | The page |

## Licence

[GNU Affero General Public License v3.0](LICENSE), like other PolicyEngine repositories.
