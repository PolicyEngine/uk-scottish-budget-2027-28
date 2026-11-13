"""The engine pins are stated once in uv.lock; everything else agrees."""

import re
import tomllib
from pathlib import Path

from scottish_budget.data_build import DATA_BUILD, LABEL
from scottish_budget.engine import check_dataset, pinned_dataset, sha256_file
from scottish_budget.pipeline import LOCKED_ENGINE

ROOT = Path(__file__).resolve().parents[1]


def _locked(name):
    lock = tomllib.loads((ROOT / "uv.lock").read_text())
    return next(p["version"] for p in lock["package"] if p["name"] == name)


def test_placeholder_engine_stamp_matches_uv_lock():
    assert LOCKED_ENGINE["policyengine"] is None
    assert LOCKED_ENGINE["policyengine_uk"] == _locked("policyengine-uk")
    assert LOCKED_ENGINE["dataset"] == DATA_BUILD.id
    assert LOCKED_ENGINE["engine_label"] == LABEL


def test_lock_holds_the_engine_the_build_was_made_on():
    assert _locked("policyengine-uk") == DATA_BUILD.engine
    assert _locked("policyengine-core") == DATA_BUILD.core
    lock = tomllib.loads((ROOT / "uv.lock").read_text())
    assert "policyengine" not in {p["name"] for p in lock["package"]}


def test_model_extra_pins_the_builds_engine():
    project = tomllib.loads((ROOT / "pyproject.toml").read_text())
    model = project["project"]["optional-dependencies"]["model"]
    assert f"policyengine-uk=={DATA_BUILD.engine}" in model
    assert f"policyengine-core=={DATA_BUILD.core}" in model
    assert not any(d.startswith("policyengine[") for d in model)


def test_docs_state_the_pinned_pair():
    method = (ROOT / "docs" / "METHOD.md").read_text()
    assert f"policyengine-uk {_locked('policyengine-uk')}" in method
    assert DATA_BUILD.id in method
    assert DATA_BUILD.sha256 in method
    assert LABEL in method
    assert "certified by policyengine" not in method


def test_label_and_pinned_dataset():
    assert LABEL == (
        "build uk-frs-calibration-attempt-20261110T204756Z-9e18f010, "
        "policyengine-uk 2.177.7, not in a policyengine.py release"
    )
    pinned = pinned_dataset()
    assert pinned["repo_id"] == "policyengine/populace-uk-private"
    assert pinned["repo_type"] == "dataset"
    assert pinned["path"] == (
        "releases/microcosm-uk-2024-25-national/"
        f"{DATA_BUILD.id}/microcosm_uk_2024_25.h5"
    )
    assert pinned["sha256"] == DATA_BUILD.sha256


def test_engine_guard_refuses_another_release(monkeypatch):
    import pytest

    from scottish_budget import engine

    monkeypatch.setattr(engine, "installed_version", lambda name: "2.174.1")
    with pytest.raises(engine.EngineMismatch):
        engine.check_engine()


def test_dataset_guard_refuses_a_different_file(tmp_path):
    path = tmp_path / "data.h5"
    path.write_bytes(b"microcosm")
    sha = sha256_file(path)
    assert check_dataset(path, sha) == sha
    import pytest

    from scottish_budget.engine import DatasetMismatch

    with pytest.raises(DatasetMismatch):
        check_dataset(path, "0" * 64)
    assert re.fullmatch(r"[0-9a-f]{64}", sha)
