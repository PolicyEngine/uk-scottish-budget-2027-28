"""The engine pins are stated once in uv.lock; everything else agrees."""

import re
import tomllib
from pathlib import Path

from scottish_budget.engine import bundle_dataset, check_dataset, sha256_file
from scottish_budget.pipeline import LOCKED_ENGINE

ROOT = Path(__file__).resolve().parents[1]


def _locked(name):
    lock = tomllib.loads((ROOT / "uv.lock").read_text())
    return next(p["version"] for p in lock["package"] if p["name"] == name)


def test_placeholder_engine_stamp_matches_uv_lock():
    assert LOCKED_ENGINE["policyengine"] == _locked("policyengine")
    assert LOCKED_ENGINE["policyengine_uk"] == _locked("policyengine-uk")


def test_model_extra_pins_the_locked_policyengine():
    project = tomllib.loads((ROOT / "pyproject.toml").read_text())
    model = project["project"]["optional-dependencies"]["model"]
    pin = next(d for d in model if d.startswith("policyengine["))
    assert pin == f"policyengine[uk]=={_locked('policyengine')}"


def test_docs_state_the_locked_pair():
    method = (ROOT / "docs" / "METHOD.md").read_text()
    assert f"policyengine.py {_locked('policyengine')}" in method
    assert f"policyengine-uk {_locked('policyengine-uk')}" in method
    assert LOCKED_ENGINE["dataset"] in method


def test_bundle_dataset_reads_the_manifest():
    manifest = {
        "data_releases": {
            "uk": {
                "default_dataset": "d",
                "datasets": {
                    "d": {
                        "revision": "build-1",
                        "sha256": "ab",
                        "path": "d.h5",
                    }
                },
            }
        }
    }
    assert bundle_dataset(manifest) == {
        "name": "d",
        "build": "build-1",
        "sha256": "ab",
        "path": "d.h5",
    }


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
