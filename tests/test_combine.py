"""The model path: stub partials through combine() to a valid file."""

import dataclasses
import json

import pytest

from scottish_budget import pipeline
from scottish_budget.publication import validate_results
from scottish_budget.years import POLICY_YEARS

SHA = "ae116bc3cff798fe68df253083f0b26d779e02a0a818ee68df7d29fbc557165a"
BUILD = "uk-frs-calibration-attempt-20261122T100732Z-b891aa69"
REVISION = "a80a4bf70ab4ffeac77357fe0633d3cee4ce7401"
LABEL = (
    "build b891aa69, policyengine-uk 2.179.2, certified in policyengine 6.20.3"
)


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
            "policyengine": "6.20.3",
            "policyengine-uk": "2.179.2",
            "policyengine-core": "3.34.10",
        },
        "provenance": {
            "runtime_dataset": BUILD,
            "runtime_dataset_revision": REVISION,
            "runtime_dataset_sha256": SHA,
            "label": LABEL,
        },
    }


@pytest.fixture
def day(monkeypatch, tmp_path, template):
    """The registry as on the day, built on the frozen template: the two
    threshold-style measures real, one signed off; everything else
    dropped as not in the statement."""
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
        for m in template
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
        provisional=True,
        out_dir=day,
        calculate=fake_calculate,
        curve=lambda year, reforms: [{"year": year, "gross": 0}],
    )
    assert results["income_tax_curve"] == [{"year": 2027, "gross": 0}]
    validate_results(results)
    assert results["meta"]["status"] == "provisional"
    assert results["meta"]["placeholder"] is False
    assert results["meta"]["dataset_sha256"] == SHA
    assert results["meta"]["dataset"] == BUILD
    assert results["meta"]["engine_label"] == LABEL
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
    results, _ = pipeline.combine(
        out_dir=day, calculate=fake_calculate, curve=lambda y, r: []
    )
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


def _old_pair(measure_id, **changes):
    """A partial from a 6.17.2-era run: policyengine-uk 2.174.1 on build
    eeb6093e. The fields can be set one at a time."""
    partial = _partial(measure_id)
    sha = changes.get("sha", "0a9b77db" + "0" * 56)
    partial["versions"]["policyengine"] = changes.get("pe", "6.17.2")
    partial["versions"]["policyengine-uk"] = changes.get("uk", "2.174.1")
    partial["versions"]["policyengine-core"] = changes.get("core", "3.34.10")
    partial["provenance"] = {
        "runtime_dataset": changes.get("build", "microcosm-eeb6093e"),
        "runtime_dataset_revision": changes.get("build", "microcosm-eeb6093e"),
        "runtime_dataset_sha256": sha,
    }
    return partial


def _write_all(day, make):
    for measure_id in ("starter_basic_thresholds", "scp_increase"):
        (day / f"{measure_id}.json").write_text(json.dumps(make(measure_id)))


def test_partials_from_another_engine_and_data_pair_are_refused(day):
    # They agree with each other, so only the DATA_BUILD check stops them.
    _write_all(day, _old_pair)
    with pytest.raises(pipeline.CombineError, match="not on build") as err:
        pipeline.combine(provisional=True, out_dir=day, with_households=False)
    message = str(err.value)
    assert "2.174.1" in message and "0a9b77db" in message


@pytest.mark.parametrize(
    "changes",
    [
        {"sha": SHA, "build": BUILD, "pe": "6.20.3"},  # right file, old engine
        {"pe": "6.20.3", "uk": "2.179.2"},  # right engine, old file
        {
            "sha": SHA,
            "build": BUILD,
            "pe": "6.20.3",
            "uk": "2.179.2",
            "core": "3.34.0",
        },
        # right file and engine, loaded outside policyengine.py (the old
        # route for 2.177.7)
        {"sha": SHA, "build": BUILD, "pe": None, "uk": "2.179.2"},
    ],
)
def test_any_one_field_off_the_build_is_refused(day, changes):
    _write_all(day, lambda i: _old_pair(i, **changes))
    with pytest.raises(pipeline.CombineError, match="not on build"):
        pipeline.combine(provisional=True, out_dir=day, with_households=False)


def test_partials_on_the_pinned_pair_are_accepted(day):
    results, _ = pipeline.combine(
        provisional=True, out_dir=day, with_households=False
    )
    assert results["meta"]["dataset_sha256"] == SHA
    assert results["meta"]["dataset"] == BUILD
    assert results["meta"]["policyengine"] == "6.20.3"
    assert results["meta"]["policyengine_uk"] == "2.179.2"
    assert results["meta"]["policyengine_core"] == "3.34.10"
    assert results["meta"]["engine_label"] == LABEL


def test_household_rows_need_the_build_engine(day, monkeypatch):
    from scottish_budget import engine

    monkeypatch.setattr(engine, "installed_version", lambda name: "2.174.1")
    with pytest.raises(engine.EngineMismatch):
        pipeline.combine(provisional=True, out_dir=day)


def test_injected_household_functions_skip_the_engine_check(day, monkeypatch):
    from scottish_budget import engine

    monkeypatch.setattr(engine, "installed_version", lambda name: "2.174.1")
    pipeline.combine(
        provisional=True,
        out_dir=day,
        calculate=fake_calculate,
        curve=lambda y, r: [],
    )


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


def test_combine_reads_the_costings_file_it_is_given(day, tmp_path):
    """After a correction, combine reads the corrected file and the
    receipt records which one (drill 12 read the uncorrected file)."""
    import hashlib

    header = "measure_id,year,official_value_bn,official_source,basis\n"
    first = tmp_path / "costings.csv"
    first.write_text(header + "starter_basic_thresholds,2027,-0.10,SFC,\n")
    corrected = tmp_path / "costings-corrected.csv"
    corrected.write_text(header + "starter_basic_thresholds,2027,-0.12,SFC,\n")
    for path, value in ((first, -0.10), (corrected, -0.12)):
        results, receipt = pipeline.combine(
            provisional=True,
            out_dir=day,
            with_households=False,
            official=path,
        )
        assert [
            r["official_value_bn"] for r in results["official_costings"]
        ] == [value]
        # Relative to the repository, or just the name outside it: the
        # receipt is served with the page, so never a home directory.
        assert receipt["official_costings"] == {
            "path": path.name,
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        }


def test_a_named_costings_file_must_exist(day, tmp_path):
    """A misspelt --official is an error, never a page with no costings."""
    missing = tmp_path / "costings-corected.csv"
    with pytest.raises(pipeline.CombineError, match="No costings file"):
        pipeline.combine(
            provisional=True,
            out_dir=day,
            with_households=False,
            official=missing,
        )
    with pytest.raises(pipeline.CombineError, match="No costings file"):
        pipeline.choose_costings(missing, tmp_path / "receipt.json")


def test_the_receipt_records_no_local_directory(day):
    from pathlib import Path

    results, receipt = pipeline.combine(
        provisional=True, out_dir=day, with_households=False
    )
    assert receipt["official_costings"]["path"] == (
        "data_inputs/official/sfc_costings_2027_28.csv"
    )
    text = json.dumps(receipt)
    assert str(pipeline.ROOT) not in text
    assert str(Path.home()) not in text


def test_a_plain_combine_never_undoes_a_correction(day, tmp_path):
    """Drill 12 and 13: after combine --official reads corrected costings
    (G5), a plain combine (G4) refuses instead of going back to the
    default file. Naming the corrected file again works."""
    from scottish_budget import cli

    corrected = tmp_path / "costings-corrected.csv"
    corrected.write_text(
        "measure_id,year,official_value_bn,official_source,basis\n"
        "starter_basic_thresholds,2027,-0.12,SFC,\n"
    )
    out = tmp_path / "site" / "results.json"
    plain = [
        "combine",
        "--provisional",
        "--no-households",
        "--partial-dir",
        str(day),
        "--out",
        str(out),
    ]
    assert cli.main(plain) == 0
    assert cli.main([*plain, "--official", str(corrected)]) == 0
    with pytest.raises(pipeline.CombineError, match="--official"):
        cli.main(plain)
    receipt = json.loads((out.parent / "receipt.json").read_text())
    assert receipt["official_costings"]["path"] == corrected.name
    assert cli.main([*plain, "--official", str(corrected)]) == 0


def test_a_receipt_naming_the_default_file_allows_a_plain_combine(tmp_path):
    """Including receipts written before paths were made relative."""
    receipt = tmp_path / "receipt.json"
    for recorded in (
        str(pipeline.OFFICIAL_COSTINGS),
        "data_inputs/official/sfc_costings_2027_28.csv",
    ):
        receipt.write_text(
            json.dumps({"official_costings": {"path": recorded}})
        )
        assert pipeline.choose_costings(None, receipt) is None
    assert pipeline.choose_costings(None, tmp_path / "none.json") is None
