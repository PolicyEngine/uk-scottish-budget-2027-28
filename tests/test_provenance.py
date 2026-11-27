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

    with pytest.raises(DatasetMismatch) as caught:
        check_dataset(path, "0" * 64)
    # The message is pasted into PR comments: no local directory in it.
    assert str(tmp_path) not in str(caught.value)
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


def _matching_pair(monkeypatch, engine):
    """Installed packages, policyengine.py's pins and the build's manifest
    all DATA_BUILD's."""
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
    monkeypatch.setattr(
        engine,
        "build_manifest",
        lambda: {
            "policyengine_uk": DATA_BUILD.engine,
            "policyengine_core": DATA_BUILD.core,
            "sha256": DATA_BUILD.sha256,
        },
    )


def test_g0_fails_where_a_run_could_not_load_the_data(monkeypatch):
    """G0 fetches the file as runs do: if that fails (no token in the
    environment, no cached copy), G0 fails rather than G2."""
    import json

    from scottish_budget import engine

    _matching_pair(monkeypatch, engine)
    monkeypatch.setattr(
        engine,
        "fetch_certified_file",
        lambda: {"path": "data/file.h5", "sha256": DATA_BUILD.sha256},
    )
    assert engine.pair_record()["engine_matches_build"]

    def refused():
        raise RuntimeError(
            f"Hugging Face rejected the configured credentials for "
            f"{engine.ROOT}/data/file.h5 in {Path.home()}"
        )

    monkeypatch.setattr(engine, "fetch_certified_file", refused)
    record = engine.pair_record()
    assert not record["engine_matches_build"]
    assert record["mismatches"] == [
        "the dataset file could not be read: RuntimeError: Hugging Face "
        "rejected the configured credentials for <repository>/data/file.h5 "
        "in ~"
    ]
    # The record is pasted into the PR: no local directory in it.
    assert str(Path.home()) not in json.dumps(record)


def test_g0_checks_a_named_dataset_against_the_build(
    monkeypatch, tmp_path, capsys
):
    """A file named with --dataset passes G0 only if it is the build's
    file, whatever --dataset-sha256 says."""
    import json

    from scottish_budget import cli, engine

    _matching_pair(monkeypatch, engine)
    path = tmp_path / "copy.h5"
    path.write_bytes(b"not the build")
    own = sha256_file(path)
    for flags in ([], ["--dataset-sha256", own]):
        assert cli.main(["freeze", "--dataset", str(path), *flags]) == 1
        record = json.loads(capsys.readouterr().out)
        assert record["engine_matches_build"] is False
        assert record["dataset_file"] == {
            "route": "named file (--dataset)",
            "path": "copy.h5",
            "sha256": own,
        }
    assert cli.main(["freeze", "--dataset-sha256", own]) == 2


def test_g0_fetches_the_file_from_the_repository_root(monkeypatch, tmp_path):
    """policyengine.py keeps the file in ./data/ under the working
    directory: G0 and runs both fetch it from the repository root."""
    import sys
    import types

    from scottish_budget import engine

    cached = tmp_path / "file.h5"
    cached.write_bytes(b"cached")
    seen = []

    def materialize_dataset(country_id):
        seen.append((country_id, Path.cwd()))
        return types.SimpleNamespace(path=str(cached))

    monkeypatch.setitem(
        sys.modules,
        "policyengine.provenance.dataset_materialization",
        types.SimpleNamespace(materialize_dataset=materialize_dataset),
    )
    monkeypatch.chdir(tmp_path)
    found = engine.fetch_certified_file()
    assert seen == [("uk", engine.ROOT)]
    assert Path.cwd() == tmp_path.resolve()
    assert found["path"] == "file.h5"
    assert found["sha256"] == sha256_file(cached)


def test_managed_runs_start_from_the_repository_root(monkeypatch, tmp_path):
    import sys
    import types

    from scottish_budget import engine, forecast

    seen = []

    def managed_microsimulation(**kwargs):
        seen.append(Path.cwd())
        sim = types.SimpleNamespace()
        sim.policyengine_bundle = {
            "runtime_dataset_sha256": DATA_BUILD.sha256,
            "runtime_dataset_source": "data/file.h5",
        }
        return sim

    fake = types.SimpleNamespace(
        uk=types.SimpleNamespace(
            managed_microsimulation=managed_microsimulation
        )
    )
    monkeypatch.setitem(sys.modules, "policyengine", fake)
    monkeypatch.setattr(engine, "check_engine", lambda: DATA_BUILD.engine)
    monkeypatch.setattr(forecast, "with_forecast", lambda scenario: scenario)
    monkeypatch.chdir(tmp_path)
    sim = engine.build_microsimulation()
    assert seen == [engine.ROOT]
    assert Path.cwd() == tmp_path.resolve()
    assert sim.scottish_budget_provenance["runtime_dataset_source"] == (
        "data/file.h5"
    )


def test_local_paths_are_recorded_relative_to_the_repository(tmp_path):
    from scottish_budget import engine

    inside = engine.ROOT / "data_inputs" / "official" / "costings.csv"
    assert engine.repo_path(inside) == "data_inputs/official/costings.csv"
    assert engine.repo_path(tmp_path / "corrected.csv") == "corrected.csv"


def test_every_check_reads_the_token_where_runs_read_it(monkeypatch):
    """The data check and G0 read the token from the same variables, in
    the same order, as policyengine.py's managed download."""
    from scottish_budget.data_build import TOKEN_ENVS, hf_token

    for name in TOKEN_ENVS:
        monkeypatch.delenv(name, raising=False)
    assert hf_token() is None
    monkeypatch.setenv("HUGGINGFACE_HUB_TOKEN", "c")
    monkeypatch.setenv("HF_TOKEN", "b")
    assert hf_token() == "b"
    monkeypatch.setenv("HUGGING_FACE_TOKEN", "a")
    assert hf_token() == "a"
    try:
        from policyengine.provenance.manifest import hugging_face_auth_headers
    except ImportError:  # no model extra (the CI python job)
        return
    for name in TOKEN_ENVS:
        assert hugging_face_auth_headers() == {
            "Authorization": f"Bearer {hf_token()}"
        }
        monkeypatch.delenv(name)


def test_the_data_check_names_every_token_variable():
    import pytest

    from scottish_budget.certified_data import (
        CertifiedDataAccessError,
        check_access,
    )

    with pytest.raises(
        CertifiedDataAccessError,
        match="HUGGING_FACE_TOKEN, HF_TOKEN, HUGGINGFACE_HUB_TOKEN",
    ):
        check_access(None, [])
