# Runbook for 3 December 2026

The draft Scottish Budget 2027-28 goes to the Scottish Parliament on Thursday 3 December 2026. The Scottish Fiscal Commission publishes its economic and fiscal forecasts, with policy costings, the same day. The statement time is to be confirmed; the clock below counts from it (T+0).

One integrator pushes. Everyone else posts defects as PR comments within 5 minutes.

## Heavy runs

Before any Python that loads Microcosm or builds a simulation, take the lock and check memory. Release it when done.

```
until mkdir /tmp/pe-heavy.lock 2>/dev/null; do sleep 30; done
trap 'rmdir /tmp/pe-heavy.lock' EXIT
uv run --extra model scottish-budget generate
```

## Gates

| Gate | When | What |
|---|---|---|
| G0 | by 09:00 | Freeze record in the PR: start SHA, policyengine and policyengine-uk versions, dataset name and SHA-256, and either the certified pair or the label "unvalidated under this engine" |
| G1 | T+0 to T+10 | Coverage ledger: every statement line gets a route and a cause class (`docs/candidate-reforms.md` lists the expected lines). Trap rows (already in the baseline) are recorded, not costed |
| G2 | T+30 | Provisional numbers against the statement's figures, and one hand-checked example household per coded measure |
| G3 | documents + 30 min | Re-base and reconcile against the Scottish Fiscal Commission's costings in `data_inputs/official/`. Each gap over 10% gets a written reason and a cause class |
| G5 | after any correction | Re-run, including hand-computed household rows; new scoring SHA; update ledger causes |
| G4 | before release | Full page on a production build with the banner removed only for published figures; check noindex is removed only on sign-off. No deploy target exists yet (see `.github/workflows/deploy.yml`) |

## On the day, in order

1. Replace each placeholder's values with the statement's; set `placeholder=False`.
2. Code in waves: parameters first, then modifiers in `src/scottish_budget/measures/`, then anything needing a new variable (held as `needs-pe-uk-first`).
3. Set `publish=True` only after G3 for that measure.
4. `uv run --extra model scottish-budget generate`, then `bun run build` in `dashboard/`.
5. Remove the pre-release banner and noindex only when every published measure has passed G3.

## Basis

State gross or net, cash or accrued, fiscal or calendar year, and static or behavioural once, on the Method tab. Most reconciliation gaps against official costings come from basis, not the model.
