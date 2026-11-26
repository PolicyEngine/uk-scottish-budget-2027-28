"""The engine entry point, its provenance and the bundle guard.

Every population simulation is built here, on the forecast overlay
(``scottish_budget.forecast``), through policyengine.py's
``pe.uk.managed_microsimulation``, on the bundle the installed policyengine
release certifies. That bundle must be ``data_build.DATA_BUILD``: the
installed policyengine, policyengine-uk and policyengine-core, the pins and
certified build policyengine.py carries, and the dataset file a simulation
loads must all agree with it. A build is never mixed with another engine
version.

With no dataset path, policyengine.py downloads the certified file into
``./data/`` (needs HUGGING_FACE_TOKEN) and checks its SHA-256. A named path
must be a copy of that file: its SHA-256 is checked here before it loads.

Versions and SHA-256s are read at run time, never typed in by hand.
``policyengine`` and ``policyengine_uk`` are imported only when a simulation
is built or the bundle is read, so the tests run without the engine
installed.
"""

import hashlib
import json
import os
import subprocess
from importlib import metadata
from pathlib import Path

from scottish_budget.data_build import (
    DATA_BUILD,
    HF_FILE,
    HF_REPO,
    HF_REPO_TYPE,
    LABEL,
)

PACKAGES = ("policyengine", "policyengine-uk", "policyengine-core")
ROOT = Path(__file__).resolve().parents[2]

# What DATA_BUILD says each installed package must be.
_PINNED_VERSIONS = {
    "policyengine": DATA_BUILD.policyengine,
    "policyengine-uk": DATA_BUILD.engine,
    "policyengine-core": DATA_BUILD.core,
}


class DatasetMismatch(RuntimeError):
    """The dataset on disk is not the one recorded at G0."""


class EngineMismatch(RuntimeError):
    """The installed engine or bundle is not the one DATA_BUILD names."""


def installed_version(name: str) -> str | None:
    try:
        return metadata.version(name)
    except metadata.PackageNotFoundError:
        return None


def installed_versions() -> dict[str, str | None]:
    return {name: installed_version(name) for name in PACKAGES}


def pinned_dataset() -> dict:
    """The bundle every simulation runs on (``data_build.DATA_BUILD``)."""
    return {
        "build": DATA_BUILD.id,
        "sha256": DATA_BUILD.sha256,
        "repo_id": HF_REPO,
        "repo_type": HF_REPO_TYPE,
        "path": DATA_BUILD.hf_path,
        "revision": DATA_BUILD.revision,
        "policyengine": DATA_BUILD.policyengine,
        "policyengine_uk": DATA_BUILD.engine,
        "policyengine_core": DATA_BUILD.core,
        "label": LABEL,
    }


def installed_bundle() -> dict:
    """What the installed policyengine.py certifies for the UK: its version,
    the engine it pins and the build and file it certifies."""
    from policyengine.bundle import get_current_bundle
    from policyengine.provenance.manifest import get_release_manifest

    release = get_release_manifest("uk")
    packages = get_current_bundle().get("packages", {})
    artifact = release.certified_data_artifact
    certification = release.certification
    return {
        "policyengine": release.policyengine_version,
        "bundle_id": release.bundle_id,
        "policyengine_uk": release.model_package.version,
        "policyengine_core": (packages.get("policyengine-core") or {}).get(
            "version"
        ),
        "build": certification.data_build_id if certification else None,
        "build_made_on_policyengine_uk": (
            certification.built_with_model_version if certification else None
        ),
        "dataset": release.default_dataset,
        "dataset_uri": release.default_dataset_uri,
        "sha256": artifact.sha256 if artifact else None,
    }


def build_manifest() -> dict:
    """The build's own release manifest on Hugging Face, at the revision
    policyengine.py pins: the engine it was built on and its file's
    SHA-256 (needs HUGGING_FACE_TOKEN or a saved login)."""
    from huggingface_hub import hf_hub_download

    path = hf_hub_download(
        repo_id=HF_REPO,
        filename=DATA_BUILD.manifest_path,
        repo_type=HF_REPO_TYPE,
        revision=DATA_BUILD.revision,
        token=os.environ.get("HUGGING_FACE_TOKEN") or None,
    )
    manifest = json.loads(Path(path).read_text())
    artifact = manifest.get("artifacts", {}).get(Path(HF_FILE).stem, {})
    return {
        "path": DATA_BUILD.manifest_path,
        "revision": DATA_BUILD.revision,
        "policyengine_uk": (
            manifest.get("built_with_model_package") or {}
        ).get("version"),
        "policyengine_core": (
            manifest.get("built_with_core_package") or {}
        ).get("version"),
        "sha256": artifact.get("sha256"),
    }


def _differences(found: dict, wanted: dict, where: str) -> list[str]:
    return [
        f"{where} {name} is {found.get(name)}, DATA_BUILD wants {want}"
        for name, want in wanted.items()
        if found.get(name) != want
    ]


def version_differences(versions: dict) -> list[str]:
    """Installed packages that are not DATA_BUILD's."""
    return _differences(versions, _PINNED_VERSIONS, "installed")


def bundle_differences(bundle: dict) -> list[str]:
    """Pins of the installed policyengine.py that are not DATA_BUILD's."""
    return _differences(
        bundle,
        {
            "policyengine": DATA_BUILD.policyengine,
            "policyengine_uk": DATA_BUILD.engine,
            "policyengine_core": DATA_BUILD.core,
            "build": DATA_BUILD.id,
            "build_made_on_policyengine_uk": DATA_BUILD.engine,
            "sha256": DATA_BUILD.sha256,
        },
        "policyengine.py's bundle:",
    )


def manifest_differences(manifest: dict) -> list[str]:
    """Fields of the build's own manifest that are not DATA_BUILD's."""
    return _differences(
        manifest,
        {
            "policyengine_uk": DATA_BUILD.engine,
            "policyengine_core": DATA_BUILD.core,
            "sha256": DATA_BUILD.sha256,
        },
        "the build's manifest:",
    )


def check_engine() -> str:
    """The installed policyengine-uk; refuse an installed engine or
    policyengine.py bundle other than DATA_BUILD's."""
    wrong = version_differences(installed_versions())
    if not wrong:
        wrong = bundle_differences(installed_bundle())
    if wrong:
        raise EngineMismatch(
            f"{'; '.join(wrong)}. Runs use build {DATA_BUILD.id} with "
            f"policyengine-uk {DATA_BUILD.engine}, as certified in "
            f"policyengine {DATA_BUILD.policyengine}: run `uv sync --locked "
            "--extra model`. Never mix a build with another engine version."
        )
    return DATA_BUILD.engine


def pair_record() -> dict:
    """The G0 pair check: the installed packages, policyengine.py's pins
    and the build's own manifest, each against DATA_BUILD. The pair
    matches only if all three agree."""
    versions = installed_versions()
    bundle = installed_bundle()
    try:
        manifest = build_manifest()
    except Exception as error:  # no token, no network: the check fails
        manifest = {"error": f"{type(error).__name__}: {error}"}
    mismatches = (
        version_differences(versions)
        + bundle_differences(bundle)
        + manifest_differences(manifest)
    )
    return {
        "versions": versions,
        "pinned_dataset": pinned_dataset(),
        "bundle": bundle,
        "build_manifest": manifest,
        "mismatches": mismatches,
        "engine_matches_build": not mismatches,
        "label": LABEL,
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


_CHECKED: dict[tuple, str] = {}


def _checked_sha256(path: Path) -> str:
    """``check_dataset`` against the build, once per file version."""
    stat = path.stat()
    key = (str(path.resolve()), stat.st_size, stat.st_mtime_ns)
    if key not in _CHECKED:
        _CHECKED[key] = check_dataset(path, DATA_BUILD.sha256)
    return _CHECKED[key]


def build_microsimulation(dataset_path=None, scenario=None):
    """A managed Microsimulation on the certified bundle, on the forecast.

    Args:
        dataset_path: A local copy of the certified file, or None for the
            bundle's own (downloaded by policyengine.py into ``./data/``;
            needs HUGGING_FACE_TOKEN). Either way the file must have the
            build's SHA-256.
        scenario: A policyengine_uk Scenario, or None for current law.
    """
    import policyengine as pe

    from scottish_budget.forecast import with_forecast

    check_engine()
    certified_uri = (
        f"hf://{HF_REPO}/{DATA_BUILD.hf_path}@{DATA_BUILD.revision}"
    )
    if dataset_path is None:
        sim = pe.uk.managed_microsimulation(scenario=with_forecast(scenario))
        bundle = dict(getattr(sim, "policyengine_bundle", {}) or {})
        sha = bundle.get("runtime_dataset_sha256")
        if sha != DATA_BUILD.sha256:
            raise DatasetMismatch(
                f"policyengine.py loaded a file with SHA-256 {sha}, not "
                f"build {DATA_BUILD.id}'s {DATA_BUILD.sha256}."
            )
        source = bundle.get("runtime_dataset_source")
        uri = bundle.get("runtime_dataset_uri") or certified_uri
    else:
        path = Path(dataset_path)
        sha = _checked_sha256(path)
        sim = pe.uk.managed_microsimulation(
            dataset=str(path),
            allow_unmanaged=True,
            scenario=with_forecast(scenario),
        )
        bundle = dict(getattr(sim, "policyengine_bundle", {}) or {})
        source = str(path)
        uri = certified_uri
    sim.scottish_budget_provenance = {
        "runtime_dataset": DATA_BUILD.id,
        "runtime_dataset_uri": uri,
        "runtime_dataset_revision": DATA_BUILD.revision,
        "runtime_dataset_source": source,
        "runtime_dataset_sha256": sha,
        "bundle_id": bundle.get("bundle_id"),
        "managed_by": (
            f"policyengine.py {bundle.get('policyengine_version')} "
            "(pe.uk.managed_microsimulation)"
        ),
        "label": LABEL,
    }
    return sim


def simulation_provenance(sim) -> dict:
    """The dataset fields recorded on a simulation built here."""
    return dict(getattr(sim, "scottish_budget_provenance", {}) or {})
