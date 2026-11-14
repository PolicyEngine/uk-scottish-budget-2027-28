"""The engine entry point, its provenance and the dataset guard.

Every population simulation is built here, on the forecast overlay
(``scottish_budget.forecast``), with ``policyengine_uk.Microsimulation``
loaded directly. The data is the Microcosm build in
``data_build.DATA_BUILD``, run on the policyengine-uk version it was built
on; no policyengine.py release covers that pair, so the
``policyengine.uk.managed_microsimulation`` wrapper (which pins policyengine.py's
own bundle) is not used. The build is downloaded from Hugging Face when no
path is named. Any dataset file, downloaded or named, must have the
build's SHA-256, and the installed policyengine-uk must be the build's:
a build is never mixed with another engine version.

Versions and the dataset's SHA-256 are read at run time, never typed in by
hand. ``policyengine_uk`` is imported only when a simulation is built, so
the tests run without the engine installed.
"""

import hashlib
import os
import subprocess
from importlib import metadata
from pathlib import Path

from scottish_budget.data_build import (
    DATA_BUILD,
    HF_REPO,
    HF_REPO_TYPE,
    LABEL,
)

PACKAGES = ("policyengine", "policyengine-uk", "policyengine-core")
ROOT = Path(__file__).resolve().parents[2]


class DatasetMismatch(RuntimeError):
    """The dataset on disk is not the one recorded at G0."""


class EngineMismatch(RuntimeError):
    """The installed policyengine-uk is not the one the build was made on."""


def installed_version(name: str) -> str | None:
    try:
        return metadata.version(name)
    except metadata.PackageNotFoundError:
        return None


def installed_versions() -> dict[str, str | None]:
    return {name: installed_version(name) for name in PACKAGES}


def pinned_dataset() -> dict:
    """The build every simulation runs on (``data_build.DATA_BUILD``)."""
    return {
        "build": DATA_BUILD.id,
        "sha256": DATA_BUILD.sha256,
        "repo_id": HF_REPO,
        "repo_type": HF_REPO_TYPE,
        "path": DATA_BUILD.hf_path,
        "policyengine_uk": DATA_BUILD.engine,
        "policyengine_core": DATA_BUILD.core,
        "label": LABEL,
    }


def fetch_dataset() -> Path:
    """The pinned build's file, downloaded once into the Hugging Face
    cache (needs HUGGING_FACE_TOKEN or a saved login)."""
    from huggingface_hub import hf_hub_download

    return Path(
        hf_hub_download(
            repo_id=HF_REPO,
            filename=DATA_BUILD.hf_path,
            repo_type=HF_REPO_TYPE,
            token=os.environ.get("HUGGING_FACE_TOKEN") or None,
        )
    )


def check_engine() -> str:
    """The installed policyengine-uk; refuse one other than the build's."""
    installed = installed_version("policyengine-uk")
    if installed != DATA_BUILD.engine:
        raise EngineMismatch(
            f"policyengine-uk {installed} is installed, but build "
            f"{DATA_BUILD.id} was made on {DATA_BUILD.engine}. Never mix a "
            "build with another engine version."
        )
    return installed


def sha256_file(path) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def check_dataset(path, expected_sha256: str | None) -> str:
    """SHA-256 of ``path``; refuse if it differs from ``expected_sha256``."""
    actual = sha256_file(path)
    if expected_sha256 and actual != expected_sha256.lower():
        raise DatasetMismatch(
            f"{path} has SHA-256 {actual}, not the {expected_sha256} "
            "recorded at G0. Refusing to run on a different dataset."
        )
    return actual


def git_identity(root: Path = ROOT) -> dict:
    """Commit SHA and whether the tree is clean (None outside git)."""

    def run(*args):
        return subprocess.run(
            ["git", "-C", str(root), *args],
            capture_output=True,
            text=True,
            check=True,
        ).stdout.strip()

    try:
        sha = run("rev-parse", "HEAD")
        clean = run("status", "--porcelain", "--untracked-files=no") == ""
    except (OSError, subprocess.CalledProcessError):
        return {"git_sha": None, "clean_tree": None}
    return {"git_sha": sha, "clean_tree": clean}


_CHECKED: dict[tuple, str] = {}


def _checked_sha256(path: Path) -> str:
    """``check_dataset`` against the build, once per file version."""
    stat = path.stat()
    key = (str(path.resolve()), stat.st_size, stat.st_mtime_ns)
    if key not in _CHECKED:
        _CHECKED[key] = check_dataset(path, DATA_BUILD.sha256)
    return _CHECKED[key]


def _runtime_dataset(path: Path):
    """The dataset object policyengine_uk reads, as policyengine.py's
    managed helper builds it from a local file."""
    from policyengine_uk.data.dataset_schema import (
        UKMultiYearDataset,
        UKSingleYearDataset,
    )

    if UKMultiYearDataset.validate_file_path(str(path), False):
        return UKMultiYearDataset(str(path))
    if UKSingleYearDataset.validate_file_path(str(path), False):
        return UKSingleYearDataset(str(path))
    return str(path)


def build_microsimulation(dataset_path=None, scenario=None):
    """A Microsimulation on the pinned build and engine, on the forecast.

    Args:
        dataset_path: An explicit dataset path, or None to download the
            pinned build (needs HUGGING_FACE_TOKEN). Either way the file
            must have the build's SHA-256.
        scenario: A policyengine_uk Scenario, or None for current law.
    """
    from policyengine_uk import Microsimulation

    from scottish_budget.forecast import with_forecast

    check_engine()
    path = Path(dataset_path) if dataset_path is not None else fetch_dataset()
    sha = _checked_sha256(path)
    sim = Microsimulation(
        dataset=_runtime_dataset(path), scenario=with_forecast(scenario)
    )
    sim.scottish_budget_provenance = {
        "runtime_dataset": DATA_BUILD.id,
        "runtime_dataset_uri": (
            f"hf://{HF_REPO}/{DATA_BUILD.hf_path} ({HF_REPO_TYPE})"
        ),
        "runtime_dataset_revision": DATA_BUILD.id,
        "runtime_dataset_sha256": sha,
        "managed_by": "scottish_budget.engine (policyengine_uk directly)",
        "label": LABEL,
    }
    return sim


def simulation_provenance(sim) -> dict:
    """The dataset fields recorded on a simulation built here."""
    return dict(getattr(sim, "scottish_budget_provenance", {}) or {})
