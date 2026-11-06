"""The engine entry point, its provenance and the dataset guard.

Every population simulation is built here, as on the Autumn Budget 2026
dashboard (``uk_budget_data.pipeline.build_microsimulation``): through
``policyengine.uk.managed_microsimulation``, which pins the certified
Microcosm build in the installed policyengine.py release bundle, on the
forecast overlay (``scottish_budget.forecast``). A named dataset path is
allowed only when given explicitly, and is then checked against an
expected SHA-256 if one is given (G0).

Versions, the dataset name and its SHA-256 are read at run time, never
typed in by hand. ``policyengine`` is imported only when a simulation is
built, so the tests run without the engine installed.
"""

import hashlib
import json
import subprocess
from importlib import metadata, resources
from pathlib import Path

PACKAGES = ("policyengine", "policyengine-uk", "policyengine-core")
ROOT = Path(__file__).resolve().parents[2]


class DatasetMismatch(RuntimeError):
    """The dataset on disk is not the one recorded at G0."""


def installed_version(name: str) -> str | None:
    try:
        return metadata.version(name)
    except metadata.PackageNotFoundError:
        return None


def installed_versions() -> dict[str, str | None]:
    return {name: installed_version(name) for name in PACKAGES}


def bundle_manifest() -> dict | None:
    """The release manifest inside the installed policyengine, if any."""
    try:
        path = (
            resources.files("policyengine")
            / "data"
            / "bundle"
            / "manifest.json"
        )
        return json.loads(path.read_text())
    except (ModuleNotFoundError, FileNotFoundError):
        return None


def bundle_dataset(manifest: dict | None = None) -> dict | None:
    """Name, build and SHA-256 of the bundle's default UK dataset."""
    manifest = manifest if manifest is not None else bundle_manifest()
    if manifest is None:
        return None
    release = manifest["data_releases"]["uk"]
    name = release["default_dataset"]
    entry = release["datasets"][name]
    return {
        "name": name,
        "build": entry.get("revision"),
        "sha256": entry.get("sha256"),
        "path": entry.get("path"),
    }


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


def build_microsimulation(dataset_path=None, scenario=None):
    """A Microsimulation pinned to the installed bundle, on the forecast.

    Args:
        dataset_path: An explicit dataset path, or None for the bundle's
            certified dataset (needs HUGGING_FACE_TOKEN).
        scenario: A policyengine_uk Scenario, or None for current law.
    """
    import policyengine as pe

    from scottish_budget.forecast import with_forecast

    return pe.uk.managed_microsimulation(
        dataset=str(dataset_path) if dataset_path is not None else None,
        allow_unmanaged=dataset_path is not None,
        scenario=with_forecast(scenario),
    )


def simulation_provenance(sim) -> dict:
    """The dataset fields policyengine.py records on a managed simulation."""
    bundle = getattr(sim, "policyengine_bundle", {}) or {}
    keys = (
        "runtime_dataset",
        "runtime_dataset_uri",
        "runtime_dataset_revision",
        "runtime_dataset_sha256",
        "managed_by",
    )
    return {key: bundle.get(key) for key in keys if key in bundle}
