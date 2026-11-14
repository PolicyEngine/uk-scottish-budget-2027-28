"""Check that the configured Hugging Face token can read the certified data.

Copied from the Autumn Budget 2026 dashboard (``uk_budget_data.certified_data``).

The dashboard runs on the Microcosm build pinned in
``data_build.DATA_BUILD`` (with the policyengine-uk version it was built on;
no policyengine.py release covers the pair), downloaded from a private
Hugging Face dataset repository. CI runs this check so a missing or rejected
credential fails at once with an actionable message instead of surfacing as
a download error during a run, or as a silent skip.

It confirms that the token can see the pinned build's file and that its
SHA-256 equals the hash in ``DATA_BUILD``. A file stored in LFS is checked from its metadata, which carries the
SHA-256, so no dataset is downloaded. A small file stored in plain git (a
release's certification or diagnostics JSON) has no SHA-256 in its metadata,
so it is downloaded to a temporary directory and hashed, up to
``MAX_GIT_FILE_BYTES``.

Usage::

    HUGGING_FACE_TOKEN=... uv run --extra model python -m scottish_budget.certified_data
"""

import argparse
import hashlib
import os
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from scottish_budget.data_build import DATA_BUILD, HF_REPO, HF_REPO_TYPE

TOKEN_ENV = "HUGGING_FACE_TOKEN"

ACCESS_HINT = (
    "CI reads the token from the organisation secret "
    "PE_UK_PRIVATE_HF_READ_TOKEN. It must be able to read every Hugging Face "
    "repository this check lists: the Hugging Face dataset repository "
    "policyengine/populace-uk-private that holds the pinned Microcosm build. "
    "This repository must be "
    "among that secret's selected repositories. Changing either is an "
    "organisation admin's call."
)


# The largest file stored in plain git, not LFS, that the check downloads
# to hash. policyengine 6.10.0's largest is 9.9 MB (Microcosm's calibration
# diagnostics); anything bigger belongs in LFS.
MAX_GIT_FILE_BYTES = 32 * 1024 * 1024


class CertifiedDataAccessError(RuntimeError):
    """Raised when the certified data cannot be read with the token."""


@dataclass(frozen=True)
class Artifact:
    """One pinned data file."""

    name: str
    repo_id: str
    repo_type: str
    path: str
    revision: str
    sha256: str


def pinned_artifacts() -> list[Artifact]:
    """The pinned build's dataset file (``data_build.DATA_BUILD``)."""
    return [
        Artifact(
            name=DATA_BUILD.id,
            repo_id=HF_REPO,
            repo_type=HF_REPO_TYPE,
            path=DATA_BUILD.hf_path,
            revision="main",
            sha256=DATA_BUILD.sha256,
        )
    ]


def _reason(error: Exception) -> str:
    """First line of an HTTP error, without its trailing full stop."""
    return str(error).strip().splitlines()[0].rstrip(".")


def token_fingerprint(token: str) -> str:
    """Return a short, non-reversible fingerprint safe to print in logs."""
    return hashlib.sha256(token.encode()).hexdigest()[:12]


def check_access(
    token: Optional[str],
    artifacts: list[Artifact],
    api=None,
) -> list[str]:
    """Confirm the token can read every artifact at its pinned hash.

    Args:
        token: The Hugging Face token, or None/empty if unset.
        artifacts: Artifacts pinned in data_build.DATA_BUILD.
        api: A ``huggingface_hub.HfApi``-compatible client (for tests).

    Returns:
        Log lines describing what was checked. They never contain the token.

    Raises:
        CertifiedDataAccessError: If the token is missing, rejected, cannot
            see an artifact, or an artifact's hash differs from the pin.
    """
    if not token:
        raise CertifiedDataAccessError(
            f"{TOKEN_ENV} is not set, so the certified dataset cannot be "
            f"downloaded. {ACCESS_HINT}"
        )
    if api is None:
        from huggingface_hub import HfApi

        api = HfApi()

    from huggingface_hub.errors import HfHubHTTPError

    try:
        identity = api.whoami(token=token)
    except HfHubHTTPError as error:
        raise CertifiedDataAccessError(
            f"Hugging Face rejected the token (fingerprint "
            f"{token_fingerprint(token)}): {_reason(error)}. {ACCESS_HINT}"
        ) from error

    lines = [
        f"Hugging Face account {identity.get('name', '?')}, token "
        f"fingerprint {token_fingerprint(token)}"
    ]

    groups: dict[tuple[str, str, str], list[Artifact]] = {}
    for artifact in artifacts:
        key = (artifact.repo_id, artifact.repo_type, artifact.revision)
        groups.setdefault(key, []).append(artifact)

    for (repo_id, repo_type, revision), group in sorted(groups.items()):
        try:
            infos = api.get_paths_info(
                repo_id,
                [a.path for a in group],
                revision=revision,
                repo_type=repo_type,
                token=token,
            )
        except HfHubHTTPError as error:
            raise CertifiedDataAccessError(
                f"The token cannot read {repo_type} repository {repo_id} at "
                f"revision {revision}: {_reason(error)}. {ACCESS_HINT}"
            ) from error
        by_path = {info.path: info for info in infos}
        for artifact in group:
            info = by_path.get(artifact.path)
            if info is None:
                raise CertifiedDataAccessError(
                    f"{repo_id}@{revision} has no file {artifact.path} "
                    f"(pinned dataset {artifact.name})."
                )
            lfs = getattr(info, "lfs", None)
            if lfs is not None:
                remote_sha, how = getattr(lfs, "sha256", None), ""
            else:
                remote_sha = _git_file_sha256(api, artifact, info, token)
                how = " (git file, downloaded and hashed)"
            if remote_sha != artifact.sha256:
                raise CertifiedDataAccessError(
                    f"{repo_id}@{revision}/{artifact.path} has SHA-256 "
                    f"{remote_sha}, but DATA_BUILD pins {artifact.sha256} "
                    f"(dataset {artifact.name})."
                )
            lines.append(
                f"OK {artifact.name}: {repo_id}@{revision}/{artifact.path} "
                f"sha256={artifact.sha256[:12]}{how}"
            )
    return lines


def _git_file_sha256(api, artifact: Artifact, info, token: str) -> str:
    """The SHA-256 of a file stored in plain git, whose metadata carry none:
    downloaded to a temporary directory and hashed. A refused or failed
    download is an access error, never a hash."""
    from huggingface_hub.errors import HfHubHTTPError, LocalEntryNotFoundError

    where = f"{artifact.repo_id}@{artifact.revision}/{artifact.path}"
    size = getattr(info, "size", None)
    if (
        not isinstance(size, int)
        or isinstance(size, bool)
        or size > MAX_GIT_FILE_BYTES
    ):
        raise CertifiedDataAccessError(
            f"{where} is stored in plain git, not LFS, so its metadata carry "
            f"no SHA-256, and at {size} bytes it is not downloaded to check "
            f"it (the limit is {MAX_GIT_FILE_BYTES}; dataset "
            f"{artifact.name})."
        )
    with tempfile.TemporaryDirectory() as directory:
        try:
            path = api.hf_hub_download(
                repo_id=artifact.repo_id,
                filename=artifact.path,
                revision=artifact.revision,
                repo_type=artifact.repo_type,
                token=token,
                local_dir=directory,
            )
        except (HfHubHTTPError, LocalEntryNotFoundError) as error:
            # huggingface_hub reports a plain 403, a server error or a
            # network failure as LocalEntryNotFoundError, with the HTTP or
            # connection error as its cause, which says what happened.
            # (force_download is not passed: with it, the library turns
            # these into a bare ValueError. Whatever bytes are hashed must
            # equal the pin, so a cached copy that matches is the file.)
            cause = error
            if isinstance(error, LocalEntryNotFoundError) and error.__cause__:
                cause = error.__cause__
            raise CertifiedDataAccessError(
                f"Could not download {where}: {_reason(cause)}. {ACCESS_HINT}"
            ) from error
        digest = hashlib.sha256()
        with open(Path(path), "rb") as handle:
            for block in iter(lambda: handle.read(1 << 20), b""):
                digest.update(block)
        return digest.hexdigest()


def main(argv: Optional[list[str]] = None) -> int:
    """Run the check against the pinned build and the environment."""
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.parse_args(argv)
    try:
        artifacts = pinned_artifacts()
        for line in check_access(os.environ.get(TOKEN_ENV), artifacts):
            print(line)
    except CertifiedDataAccessError as error:
        print(f"::error::{error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
