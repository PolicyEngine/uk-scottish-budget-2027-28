# Shortcuts. Heavy targets (measures, package, build) take the machine-wide
# lock, a FILE holding "<pid> <label>" created with noclobber and removed only
# by its owner, then wait for 22 GB free+inactive memory (docs/RUNBOOK.md).
# HEAVY_LOCK and MIN_FREE_GB are variables only so the macro can be tested
# against a scratch path; never change them for a real run.

HEAVY_LOCK ?= /tmp/pe-heavy.lock
MIN_FREE_GB ?= 22
LOCK = until ( set -C; echo "$$$$ scottish-budget-$@" > $(HEAVY_LOCK) ) 2>/dev/null; do sleep 15; done; \
	trap '[ "$$(cut -d" " -f1 $(HEAVY_LOCK) 2>/dev/null)" = "$$$$" ] && rm -f $(HEAVY_LOCK)' EXIT; \
	until [ "$$(vm_stat | awk '/page size of/ {p=$$8} /Pages free/ {f=$$3} /Pages inactive/ {i=$$3} END {print int((f+i)*p/1e9)}')" -ge $(MIN_FREE_GB) ]; do sleep 30; done;

.PHONY: help install test engine-test lint format placeholder fixtures measures package combine build smoke

help:
	@echo "install      uv and bun dependencies (with the model extra)"
	@echo "test         pytest and vitest (no engine, no data)"
	@echo "engine-test  household checks on the pinned engine (light)"
	@echo "lint         ruff and eslint"
	@echo "format       ruff format"
	@echo "placeholder  regenerate the pre-release results.json"
	@echo "fixtures     regenerate data_inputs/household_fixtures/"
	@echo "measures     IDS=\"a b\": one heavy run per measure, under the lock"
	@echo "package      MODE=provisional|final: the package run, under the lock"
	@echo "combine      partials into results.json (PROVISIONAL=1 for G2)"
	@echo "build        production build of the page, under the lock"
	@echo "smoke        check a served build (start it first)"

install:
	uv sync --locked --extra dev --extra model
	cd dashboard && bun install --frozen-lockfile

test:
	uv run pytest
	cd dashboard && bun run test

engine-test:
	uv run --extra model pytest -m engine

lint:
	uv run ruff check . && uv run ruff format --check .
	cd dashboard && bun run lint

format:
	uv run ruff format .

placeholder:
	uv run scottish-budget generate --placeholder

fixtures:
	uv run python scripts/write_household_fixtures.py

measures:
	@for id in $(IDS); do \
	  ( $(LOCK) uv run --extra model scottish-budget generate --reforms $$id ) || exit 1; \
	done

package:
	$(LOCK) uv run --extra model scottish-budget generate --package $(or $(MODE),provisional)

combine:
	uv run --extra model scottish-budget combine $(if $(PROVISIONAL),--provisional,)

build:
	$(LOCK) cd dashboard && bun run build

smoke:
	scripts/smoke-built-site.sh http://127.0.0.1:3000/uk/scottish-budget-2027-28 $(BANNER)
