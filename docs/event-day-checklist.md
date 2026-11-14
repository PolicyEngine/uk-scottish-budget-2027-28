# Event-day checklist (one page)

The order of 3 December on one page. Detail and reasons are in [`RUNBOOK.md`](RUNBOOK.md); where the two differ, the runbook wins. T+0 is the statement (time to be confirmed). Roles: the integrator generates and commits; the reconciler owns the ledger and the reconciliation; the scorer checks example households. Names go in the PR, not here.

| When | Who | Step |
|---|---|---|
| T−120 | Integrator | `uv sync --locked --extra dev --extra model`; `uv run python -m scottish_budget.certified_data` passes |
| by T−60 | Integrator | **G0**: `uv run --extra model scottish-budget freeze`, pasted into the PR |
| T+0 | Reconciler | **G1** starts: one ledger line per statement item, route and cause |
| T+0 to T+10 | Integrator | Values into `reforms.py`, `placeholder=False`, unannounced entries deleted; commit |
| T+10 to T+30 | Integrator | Under the lock, one process each: `generate --reforms ID`; then `generate --package provisional`; `combine --provisional`; commit |
| by T+30 | Scorer | **G2**: one hand-checked household per coded measure |
| documents | Reconciler | Fill `data_inputs/official/sfc_costings_2027_28.csv` from the costings |
| documents + 30 | Reconciler | **G3**: `scottish-budget reconcile --official ...` exits 0; integrator sets `publish=True` per reconciled measure |
| after G3 | Integrator | `generate --package final`; `combine`; public data checks |
| after G3 | Integrator | **G4**: under the lock, `cd dashboard && bun run build && bun run start`; `scripts/smoke-built-site.sh`; kill the server |
| any time | Integrator | **G5** on a correction: re-run affected measures and the package; new SHA; G4 again |
| on go-ahead | Dashboard owner | Remove banner and noindex in a PR; merge only with the go-ahead |

## Never

1. Never run two heavy jobs at once, or a heavy job without the lock (the file `/tmp/pe-heavy.lock`, removed only by its owner) and 22 GB free+inactive.
2. Never run more than one measure in a `generate --reforms` call.
3. Never publish a figure from an engine and data pair not recorded at G0.
4. Never show a not-computable measure as £0.
5. Never deploy from a drill, and never merge without the go-ahead.
6. Never print `HUGGING_FACE_TOKEN`.
