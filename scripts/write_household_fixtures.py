#!/usr/bin/env python3
"""Write each example household and its rest-of-UK twin as JSON.

The files are the situations G2's hand checks start from, so a checker can
run one in the PolicyEngine API or a notebook without this package. They
are generated from ``household.presets``; tests/test_household.py fails if
they drift.
"""

import json
from pathlib import Path

from scottish_budget.household import presets, rest_of_uk_twin, situation_for

OUT = (
    Path(__file__).resolve().parents[1] / "data_inputs" / "household_fixtures"
)


def fixtures() -> dict[str, dict]:
    out = {}
    for key, preset in presets().items():
        # situation_for applies the preset's take-up flag, so a preset
        # marked as not claiming exports (with its twin) as not claiming.
        situation = situation_for(preset)
        out[key] = {
            "label": preset["label"],
            "year": preset["year"],
            "claims": preset.get("claims", True),
            "situation": situation,
            "rest_of_uk_twin": rest_of_uk_twin(situation, preset["year"]),
        }
    return out


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for key, body in fixtures().items():
        (OUT / f"{key}.json").write_text(json.dumps(body, indent=2) + "\n")


if __name__ == "__main__":
    main()
