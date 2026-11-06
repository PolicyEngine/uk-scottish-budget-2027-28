import csv
from pathlib import Path

import pytest

from scottish_budget.pipeline import placeholder_results
from scottish_budget.reconcile import (
    ReconcileError,
    read_official,
    reconcile,
    unreasoned,
)
from scottish_budget.reforms import MEASURES
from scottish_budget.years import POLICY_YEARS

ROOT = Path(__file__).resolve().parents[1]
EXPECTED = ROOT / "data_inputs" / "expected_effects.csv"


def _write(tmp_path, rows):
    path = tmp_path / "official.csv"
    with open(path, "w", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "measure_id",
                "year",
                "official_value_bn",
                "official_source",
                "basis",
                "reason",
                "cause",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)
    return path


def test_every_expected_effect_names_a_measure_and_a_policy_year():
    ids = {m.id for m in MEASURES}
    with open(EXPECTED, newline="") as handle:
        for row in csv.DictReader(handle):
            assert row["measure_id"] in ids, row
            assert int(row["year"]) in POLICY_YEARS, row
    read_official(EXPECTED)


def test_unknown_ids_and_years_fail(tmp_path):
    path = _write(tmp_path, [{"measure_id": "nope", "year": "2026"}])
    with pytest.raises(ReconcileError, match="unknown measure.*not a policy"):
        read_official(path)


def test_big_gaps_need_a_reason_and_cause(tmp_path):
    results = placeholder_results()
    row = next(
        m for m in results["measures"] if m["id"] == "starter_basic_thresholds"
    )
    ours = row["budgetary_impact"][0]["value_bn"]
    official = [
        {
            "measure_id": "starter_basic_thresholds",
            "year": "2027",
            "official_value_bn": str(ours * 2),
        },
        {
            "measure_id": "starter_basic_thresholds",
            "year": "2028",
            "official_value_bn": str(row["budgetary_impact"][1]["value_bn"]),
        },
    ]
    rows = reconcile(results, read_official(_write(tmp_path, official)))
    assert [r["year"] for r in unreasoned(rows)] == [2027]
    official[0].update(
        reason="behaviour in the official figure", cause="basis"
    )
    rows = reconcile(results, read_official(_write(tmp_path, official)))
    assert unreasoned(rows) == []
