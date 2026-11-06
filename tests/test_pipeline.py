import json
from pathlib import Path

import pytest

from scottish_budget.pipeline import CombineError, combine, placeholder_results
from scottish_budget.publication import (
    PublicationError,
    apply_floor,
    validate_results,
)
from scottish_budget.reforms import MEASURES

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "dashboard" / "public" / "data" / "results.json"


def test_placeholder_file_is_flagged_everywhere():
    results = placeholder_results()
    assert results["meta"]["placeholder"] is True
    assert "placeholder" in results["meta"]["notice"].lower()
    assert all(m["placeholder"] for m in results["measures"])
    assert not any(m["publish"] for m in results["measures"])


def test_every_registry_measure_is_in_the_file():
    ids = [m["id"] for m in placeholder_results()["measures"]]
    assert ids == [m.id for m in MEASURES]


def test_not_computable_is_never_zero():
    for m in placeholder_results()["measures"]:
        if m["status"] == "not-computable":
            assert m["budgetary_impact"] is None
            assert m["reason"]


def test_committed_file_matches_the_generator():
    """dashboard/public/data/results.json is generated, never hand-edited."""
    committed = json.loads(PUBLIC.read_text())
    assert committed == json.loads(json.dumps(placeholder_results()))


def test_combine_refuses_without_partials(tmp_path):
    with pytest.raises(CombineError, match="No partial"):
        combine(out_dir=tmp_path)


def test_placeholder_signs_follow_the_measure():
    for row in placeholder_results()["measures"]:
        from scottish_budget.reforms import measure

        sign = measure(row["id"]).placeholder_sign
        for f in row["budgetary_impact"] or []:
            assert f["value_bn"] * sign > 0, row["id"]


def test_placeholder_households_carry_no_numbers():
    for h in placeholder_results()["households"]:
        assert h["baseline_net_income"] is None
        assert h["year"] == 2027


def test_no_internal_notes_or_jargon_in_public_text():
    import re

    for row in placeholder_results()["measures"]:
        assert "internal_note" not in row
        for key in ("name", "description", "reason", "basis_note"):
            text = row.get(key) or ""
            assert not re.search(
                r"PLACEHOLDER|TRAP|measures/|\w+_\w+", text
            ), (
                row["id"],
                key,
                text,
            )
        if row["reason"] and row["basis_note"]:
            assert row["reason"] != row["basis_note"]


def test_floor_withholds_small_cells():
    cells = apply_floor([{"avg_change_gbp": 5.0, "n_records": 3}])
    assert cells[0]["avg_change_gbp"] is None
    assert "withheld" in cells[0]


def test_validation_rejects_a_zero_for_a_not_computable_measure():
    results = placeholder_results()
    row = next(
        m for m in results["measures"] if m["status"] == "not-computable"
    )
    row["budgetary_impact"] = [{"year": 2027, "value_bn": 0.0}]
    with pytest.raises(PublicationError, match="not computable"):
        validate_results(results)


def test_validation_rejects_weights():
    results = placeholder_results()
    results["households"][0]["household_weight"] = 1.0
    with pytest.raises(PublicationError, match="weight"):
        validate_results(results)
