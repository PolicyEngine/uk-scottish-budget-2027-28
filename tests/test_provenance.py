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
    assert LOCKED_ENGINE["policyengine"] == _locked("policyengine")
    assert LOCKED_ENGINE["policyengine_uk"] == _locked("policyengine-uk")
    assert LOCKED_ENGINE["dataset"] == DATA_BUILD.id
    assert LOCKED_ENGINE["engine_label"] == LABEL


def test_lock_holds_the_bundle_and_the_engine_the_build_was_made_on():
    assert _locked("policyengine") == DATA_BUILD.policyengine
    assert _locked("policyengine-uk") == DATA_BUILD.engine
    assert _locked("policyengine-core") == DATA_BUILD.core


def test_model_extra_pins_the_bundle_not_the_engine():
    project = tomllib.loads((ROOT / "pyproject.toml").read_text())
    model = project["project"]["optional-dependencies"]["model"]
    assert f"policyengine[uk]=={DATA_BUILD.policyengine}" in model
    # policyengine.py pins the engine; a second pin here could drift.
    assert not any(d.startswith("policyengine-uk") for d in model)
    assert not any(d.startswith("policyengine-core") for d in model)


def test_docs_state_the_pinned_pair():
    method = (ROOT / "docs" / "METHOD.md").read_text()
    assert f"policyengine-uk {_locked('policyengine-uk')}" in method
    assert DATA_BUILD.id in method
    assert DATA_BUILD.sha256 in method
    assert LABEL in method
    assert f"policyengine {DATA_BUILD.policyengine}" in method
    assert "not in a policyengine.py release" not in method


def test_label_and_pinned_dataset():
    assert LABEL == (
        "build b891aa69, policyengine-uk 2.179.2, "
        "certified in policyengine 6.20.3"
    )
    assert DATA_BUILD.short_id == "b891aa69"
    pinned = pinned_dataset()
    assert pinned["repo_id"] == "policyengine/populace-uk-private"
    assert pinned["repo_type"] == "dataset"
    assert pinned["path"] == (
        "releases/microcosm-uk-2024-25-national/"
        f"{DATA_BUILD.id}/microcosm_uk_2024_25.h5"
    )
    assert pinned["sha256"] == DATA_BUILD.sha256
    assert pinned["revision"] == DATA_BUILD.revision
    assert pinned["policyengine"] == DATA_BUILD.policyengine


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


def _bundle(**changes):
    bundle = {
        "policyengine": DATA_BUILD.policyengine,
        "policyengine_uk": DATA_BUILD.engine,
        "policyengine_core": DATA_BUILD.core,
        "build": DATA_BUILD.id,
        "build_made_on_policyengine_uk": DATA_BUILD.engine,
        "sha256": DATA_BUILD.sha256,
    }
    bundle.update(changes)
    return bundle


def test_engine_guard_refuses_another_bundle(monkeypatch):
    """Right packages installed, but policyengine.py certifies another
    build: refused before any data load."""
    import pytest

    from scottish_budget import engine

    monkeypatch.setattr(
        engine,
        "installed_version",
        lambda name: {
            "policyengine": DATA_BUILD.policyengine,
            "policyengine-uk": DATA_BUILD.engine,
            "policyengine-core": DATA_BUILD.core,
        }[name],
    )
    monkeypatch.setattr(engine, "installed_bundle", _bundle)
    assert engine.check_engine() == DATA_BUILD.engine
    monkeypatch.setattr(
        engine, "installed_bundle", lambda: _bundle(build="other-build")
    )
    with pytest.raises(engine.EngineMismatch, match="other-build"):
        engine.check_engine()


def test_pair_differences_name_each_source():
    from scottish_budget import engine

    assert engine.bundle_differences(_bundle()) == []
    assert (
        engine.manifest_differences(
            {
                "policyengine_uk": DATA_BUILD.engine,
                "policyengine_core": DATA_BUILD.core,
                "sha256": DATA_BUILD.sha256,
            }
        )
        == []
    )
    wrong = engine.bundle_differences(_bundle(sha256="0" * 64))
    assert len(wrong) == 1 and "bundle" in wrong[0]
    # An unreadable manifest is a mismatch, never a pass.
    assert len(engine.manifest_differences({"error": "no token"})) == 3
