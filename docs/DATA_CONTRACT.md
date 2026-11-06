# Data contract

- Microdata never enter this repository. `*.h5` files are ignored; runs read Microcosm from the Hugging Face cache.
- Only generated files go in `dashboard/public/data/`. Hand edits fail `tests/test_pipeline.py`.
- Public files hold aggregates only: no record identifiers, no weights, no cell below 10 survey households, and no area codes (`scripts/check_public_data.py`, `dashboard/scripts/check-public-files.mjs`). Both run in CI.
- Official figures (Scottish Fiscal Commission costings, Scottish Government ready reckoners, HMRC outturn) go in `data_inputs/official/` with their source URL and the date they were read.
- Drill packets are never committed. Their SHA-256 hashes are in the drill branch's `DRILL.md` only.
- Pipeline outputs other than the public files (`data_outputs/`: partials, reconciliation) are never committed.
