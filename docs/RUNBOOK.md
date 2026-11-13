# Runbook for 3 December 2026

The draft Scottish Budget 2027-28 goes to the Scottish Parliament on Thursday 3 December 2026. The Scottish Fiscal Commission publishes its economic and fiscal forecasts, with policy costings, the same day. The statement time is to be confirmed; the clock counts from it (T+0). The one-page order of the day is [`event-day-checklist.md`](event-day-checklist.md); where the two differ, this runbook wins.

One integrator pushes. Everyone else posts defects as PR comments within 5 minutes.

## Set-up

- `uv sync --locked --extra dev --extra model`, then `cd dashboard && bun install --frozen-lockfile`.
- `HUGGING_FACE_TOKEN` must be set (copy `.env.example` to `.env` and fill it, or export it). The pinned Microcosm build (`data_build.DATA_BUILD`) is in a private Hugging Face dataset repository; `uv run python -m scottish_budget.certified_data` checks the token can read it and that its SHA-256 matches the pin, without downloading it. Never print the token.

## Heavy runs

Anything that loads Microcosm (`generate --reforms`, `generate --package`) or runs a Next.js production build takes the machine-wide lock and waits for 22 GB of free+inactive memory first. The lock is a file holding "<pid> <label>", created with noclobber (`set -C`) and removed only by the process that wrote it; never delete a lock you do not own. One measure per process; the next waits for the lock.

```
until ( set -C; echo "$$ scottish-budget-manual" > /tmp/pe-heavy.lock ) 2>/dev/null; do sleep 15; done
trap '[ "$(cut -d" " -f1 /tmp/pe-heavy.lock 2>/dev/null)" = "$$" ] && rm -f /tmp/pe-heavy.lock' EXIT
free_gb() { vm_stat | awk '/page size of/ {p=$8} /Pages free/ {f=$3} /Pages inactive/ {i=$3} END {print int((f+i)*p/1e9)}'; }
until [ "$(free_gb)" -ge 22 ]; do sleep 30; done
uv run --extra model scottish-budget generate --reforms <measure id>
```

One measure took 2 min 16 s and peaked at 11.3 GB resident (6 November, 6.14.0 on a6299504, cached data); the package run builds three simulations one after another, so allow about 3 to 4 minutes for it. `make measures IDS="a b c"` runs that block once per measure, each in its own process. Unit tests, lint and the household engine tests (`pytest -m engine`) do not need the lock.

## Gates

| Gate | When | What | Command |
|---|---|---|---|
| G0 | by T−60 | Freeze record in the PR: start SHA, policyengine, policyengine-uk and core versions, dataset name and SHA-256 (must be the pinned build's), `engine_matches_build: true`, and the label "build uk-frs-calibration-attempt-20261110T204756Z-9e18f010, policyengine-uk 2.177.7, not in a policyengine.py release" | `uv run --extra model scottish-budget freeze` |
| G1 | T+0 to T+10 | Coverage ledger: every statement line gets a route and a cause class (`docs/candidate-reforms.md` lists the expected lines). Trap rows (already in the baseline) are recorded, not costed. Set each kept measure's values and `placeholder=False`; delete entries the statement does not have | |
| G2 | T+30 | Provisional numbers, and one hand-checked example household per coded measure (`data_inputs/household_fixtures/`) | `generate --reforms ID` per measure, `generate --package provisional`, `combine --provisional` |
| G3 | documents + 30 min | Re-base and reconcile against the Scottish Fiscal Commission's costings in `data_inputs/official/sfc_costings_2027_28.csv`. Each gap over 10% gets a written reason and a cause class. Then set `publish=True` for each reconciled measure | `scottish-budget reconcile --official data_inputs/official/sfc_costings_2027_28.csv` |
| G4 | before release | Full page on a production build: banner text, noindex meta and `X-Robots-Tag` checked in the served page; every published measure on the page | `generate --package final`, `combine`, then the build and `scripts/smoke-built-site.sh` |
| G5 | whenever a correction arrives, before or after G4 | Re-run every affected measure and the package, including hand-computed household rows; new results SHA-256; update ledger causes; if after G4, run G4 again | as G2 to G4 |

## On the day, in order

1. G0: `scottish-budget freeze` (add `--dataset PATH --dataset-sha256 SHA` if running on a named file). Paste the output into the PR.
2. G1: replace each placeholder's values with the statement's; set `placeholder=False`. Code in waves: parameters first, then modifiers in `src/scottish_budget/measures/`, then anything needing a new variable (held as `needs-pe-uk-first`, with an upstream draft filed the same day).
3. G2: under the lock, `generate --reforms ID` for each computable measure (one process each), then `generate --package provisional`, then `combine --provisional`. Hand-check one household per measure.
4. G3: copy `data_inputs/official/costings_template.csv` to `sfc_costings_2027_28.csv`, fill it from the costings, run `reconcile` until it exits 0, then set `publish=True` on each reconciled measure.
5. G4: `generate --package final`, `combine` (writes `results.json` and `receipt.json`), `uv run python scripts/check_public_data.py dashboard/public/data`, then under the lock `cd dashboard && bun run build && bun run start` and `scripts/smoke-built-site.sh`. Kill the server and release the lock.
6. Remove the pre-release banner and noindex only when every published measure has passed G3, and only with the go-ahead to publish.

## Corrections (G5)

1. Record the correction (time received, what it changes) as a PR comment.
2. Change the affected measures; re-run each one and the package under the lock; `combine`.
3. The new `results.json` SHA-256 (`receipt.json`, `results_sha256`) is the new scoring SHA; record it beside the old one.
4. On a published page, add a dated correction note to the Methodology tab saying what changed, and keep the old figures out of the page.

## Rollback

- Vercel: promote the previous production deployment (Vercel dashboard, Deployments, "Instant rollback", or `vercel promote <deployment url>` with the team scope). This needs no new build.
- Repository: revert the publishing PR with a new PR (`git revert -m 1 <merge sha>` on a branch), never a force-push to `main`.
- Record the rollback, the deployment it went back to and the reason in the PR.

## Production setup (for the dashboard owner, before the event)

Nothing deploys from this repository yet: `deploy.yml` runs on manual dispatch only and does nothing. Before 3 December:

1. Decide the address (issue on the multizone address): `/uk/scottish-budget-2027-28`, as `dashboard/src/lib/basePath.json` has it, or `/uk/budgets/<event>`.
2. Create the Vercel project in the `policy-engine` team from `PolicyEngine/uk-scottish-budget-2027-28`, root directory `dashboard/`, framework Next.js, build `bun run build`, production branch `main`.
3. Add the app-v2 zone route and rewrite once the project's domain exists.
4. Add this repository to the `PE_UK_PRIVATE_HF_READ_TOKEN` secret's selected repositories (an organisation admin), so the certified-data CI job can pass.
5. Drills use a local production build only, never a deployment.

## Basis

State gross or net, cash or accrued, fiscal or calendar year, and static or behavioural once, on the Method tab. Most reconciliation gaps against official costings come from basis, not the model.
