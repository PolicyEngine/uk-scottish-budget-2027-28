"""The model path: stub partials through combine() to a valid file."""

import dataclasses
import json

import pytest

from scottish_budget import pipeline, reforms
from scottish_budget.publication import validate_results
from scottish_budget.years import POLICY_YEARS

SHA = "b96a8cd625b645a409c063b1de5158532708a2f0d3c3897a794a8fb0bbd5064e"


def _partial(measure_id):
    return {
        "measure_id": measure_id,
        "budgetary_impact": [
            {"year": y, "label": f"{y}-{str(y + 1)[-2:]}", "value_bn": -0.1}
            for y in POLICY_YEARS
        ],
        "decile_impact": [
            {
                "measure_id": measure_id,
                "year": y,
                "decile": d,
                "avg_change_gbp": 10.0,
                "pct_change": 0.1,
                "n_records": 500,
            }
            for y in POLICY_YEARS
            for d in range(1, 11)
        ],
        "winners_losers": [
            {
                "measure_id": measure_id,
                "year": y,
                "gain_share": 0.3,
                "lose_share": 0.0,
                "n_records": 9000,
            }
            for y in POLICY_YEARS
        ],
        "poverty": [],
        "versions": {
            "policyengine": "6.14.0",
            "policyengine-uk": "2.151.0",
            "policyengine-core": "3.33.3",
        },
        "provenance": {
            "runtime_dataset": "microcosm_uk_2024_25",
            "runtime_dataset_revision": "microcosm-a6299504",
            "runtime_dataset_sha256": SHA,
        },
    }


@pytest.fixture
def day(monkeypatch, tmp_path):
    """The registry as on the day: the two threshold-style measures real,
    one signed off; everything else dropped as not in the statement."""
    real = {
        "starter_basic_thresholds": True,
        "scp_increase": False,
        "council_tax_bands_i_j": False,
        "upper_thresholds_frozen": False,
    }
    measures = tuple(
        dataclasses.replace(m, placeholder=False, publish=real[m.id])
        if m.id in real
        else m
        for m in reforms.MEASURES
    )
    monkeypatch.setattr(pipeline, "MEASURES", measures)
    by_id = {m.id: m for m in measures}
    monkeypatch.setattr(pipeline, "measure", lambda i: by_id[i])
    for measure_id in ("starter_basic_thresholds", "scp_increase"):
        (tmp_path / f"{measure_id}.json").write_text(
            json.dumps(_partial(measure_id))
        )
    return tmp_path


def fake_calculate(situation, year, reforms=()):
    scottish = not any(
        p.get("pays_scottish_income_tax") == {str(year): False}
        for p in situation["people"].values()
    )
    return {
        "household_net_income": 20_000.0 + 100 * len(reforms) - 50 * scottish,
        "income_tax": 1_000.0,
    }


def test_provisional_file_passes_validation(day):
    results, receipt = pipeline.combine(
        provisional=True, out_dir=day, calculate=fake_calculate
    )
    validate_results(results)
    assert results["meta"]["status"] == "provisional"
    assert results["meta"]["placeholder"] is False
    assert results["meta"]["dataset_sha256"] == SHA
    statuses = {m["id"]: m["status"] for m in results["measures"]}
    # Provisional mode never marks a measure published, signed off or not.
    assert statuses["starter_basic_thresholds"] == "provisional"
    assert statuses["scp_increase"] == "provisional"
    assert statuses["council_tax_bands_i_j"] == "not-computable"
    assert statuses["upper_thresholds_frozen"] == "ledger"
    assert len(results["measures"]) == 4
    assert "energy_payment_bands_a_d" in receipt["placeholders_dropped"]
    assert receipt["results_sha256"]
    h = results["households"][0]
    assert h["change"] == h["reform_net_income"] - h["baseline_net_income"]


def test_final_file_shows_only_signed_off_figures(day):
    results, _ = pipeline.combine(out_dir=day, calculate=fake_calculate)
    rows = {m["id"]: m for m in results["measures"]}
    assert rows["starter_basic_thresholds"]["status"] == "published"
    assert rows["starter_basic_thresholds"]["budgetary_impact"]
    assert rows["scp_increase"]["status"] == "provisional"
    assert rows["scp_increase"]["budgetary_impact"] is None
    ids = {c["measure_id"] for c in results["decile_impact"]}
    assert ids == {"starter_basic_thresholds"}


def test_mixed_engine_pairs_are_refused(day):
    other = _partial("scp_increase")
    other["provenance"]["runtime_dataset_sha256"] = "0" * 64
    (day / "scp_increase.json").write_text(json.dumps(other))
    with pytest.raises(pipeline.CombineError, match="different engine"):
        pipeline.combine(provisional=True, out_dir=day, with_households=False)


def test_computable_measure_without_a_partial_is_refused(day):
    (day / "scp_increase.json").unlink()
    with pytest.raises(pipeline.CombineError, match="no partial"):
        pipeline.combine(provisional=True, out_dir=day, with_households=False)


def _package(measure_ids):
    p = _partial("package")
    p["measures"] = measure_ids
    p["poverty"] = [
        {
            "measure_id": "package",
            "year": 2027,
            "group": "children",
            "basis": "ahc",
            "baseline_rate": 0.2,
            "reform_rate": 0.19,
            "change_count": -5000,
            "n_records": 3000,
        }
    ]
    p["council_tax_bands"] = [
        {
            "measure_id": "package",
            "year": 2027,
            "band": "H",
            "avg_change_gbp": 3.0,
            "n_records": 4,
        }
    ]
    p["scotland_vs_rest_of_uk"] = [
        {"year": 2027, "scenario": "current_law", "share_paying_less": 0.55}
    ]
    return p


def test_package_tables_come_from_the_package_run(day):
    package = _package(["starter_basic_thresholds", "scp_increase"])
    package["council_tax_bands"][0]["avg_change_gbp"] = None
    (day / "package.json").write_text(json.dumps(package))
    results, receipt = pipeline.combine(
        provisional=True, out_dir=day, with_households=False
    )
    assert receipt["package_run"] is True
    assert results["poverty"][0]["change_count"] == -5000
    assert results["scotland_vs_rest_of_uk"][0]["share_paying_less"] == 0.55
    assert {c["measure_id"] for c in results["winners_losers"]} == {"package"}


def test_a_package_over_other_measures_is_refused(day):
    (day / "package.json").write_text(
        json.dumps(_package(["starter_basic_thresholds"]))
    )
    with pytest.raises(pipeline.CombineError, match="package run covers"):
        pipeline.combine(provisional=True, out_dir=day, with_households=False)


def test_cells_below_the_floor_must_be_withheld(day):
    from scottish_budget.publication import PublicationError

    (day / "package.json").write_text(
        json.dumps(_package(["starter_basic_thresholds", "scp_increase"]))
    )
    with pytest.raises(PublicationError, match="below the disclosure floor"):
        pipeline.combine(provisional=True, out_dir=day, with_households=False)
