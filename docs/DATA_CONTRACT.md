# Data contract

- Microdata never enter this repository. `*.h5` files are ignored; runs read Microcosm from the Hugging Face cache.
- Only generated files go in `dashboard/public/data/`. Hand edits fail `tests/test_pipeline.py`.
- Public files hold aggregates only: no record identifiers, no weights, no cell below 10 survey households, and no area codes (`scripts/check_public_data.py`, `dashboard/scripts/check-public-files.mjs`). Both run in CI.
- Take-up: population runs use the take-up draws stored in the Microcosm file. Build `…-6f918b81` meets its 2025 calibration targets for Scottish Child Payment spending, Scottish Universal Credit households with a child under one, and babies under one; nothing targets young parents. Hand-built households (presets, the calculator) claim UC and SCP unless marked not claiming (`household.not_claiming`).
- Official figures (Scottish Fiscal Commission costings, Scottish Government ready reckoners, HMRC outturn) go in `data_inputs/official/` with their source URL and the date they were read.
- Drill packets are never committed. Their SHA-256 hashes are in the drill branch's `DRILL.md` only.
- Pipeline outputs other than the public files (`data_outputs/`: partials, reconciliation) are never committed.
