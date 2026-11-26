"""The certified bundle a model run uses: policyengine.py, its engine and
its Microcosm build.

The rule (26 November 2026): run on the Microcosm build that the pinned
policyengine.py release certifies, with the policyengine-uk and
policyengine-core versions that release pins, through
``pe.uk.managed_microsimulation``; never mix a build with another engine
version. ``DATA_BUILD`` names that bundle once. The pins in ``uv.lock``
must match it (tests/test_provenance.py), and at run time ``engine.py``
refuses an installed bundle that differs from it.
"""

from dataclasses import dataclass

HF_REPO = "policyengine/populace-uk-private"
HF_REPO_TYPE = "dataset"
HF_RELEASE = "microcosm-uk-2024-25-national"
HF_FILE = "microcosm_uk_2024_25.h5"


@dataclass(frozen=True)
class DataBuild:
    """One certified bundle: the policyengine.py release, the Microcosm
    build it certifies and the engine the build was made on."""

    id: str
    sha256: str
    revision: str
    """The Hugging Face commit policyengine.py pins the build's files at."""
    policyengine: str
    engine: str
    core: str

    @property
    def short_id(self) -> str:
        return self.id.rsplit("-", 1)[-1]

    @property
    def hf_path(self) -> str:
        return f"releases/{HF_RELEASE}/{self.id}/{HF_FILE}"

    @property
    def manifest_path(self) -> str:
        return f"releases/{HF_RELEASE}/{self.id}/release_manifest.json"

    @property
    def label(self) -> str:
        return (
            f"build {self.short_id}, policyengine-uk {self.engine}, "
            f"certified in policyengine {self.policyengine}"
        )


# Switched 26 November 2026 to the bundle in policyengine 6.20.3 (the pair
# the Milburn review dashboard runs on). Before: build 6f918b81 on
# policyengine-uk 2.177.7, loaded outside any policyengine.py release.
DATA_BUILD = DataBuild(
    id="uk-frs-calibration-attempt-20261122T100732Z-b891aa69",
    sha256="ae116bc3cff798fe68df253083f0b26d779e02a0a818ee68df7d29fbc557165a",
    revision="a80a4bf70ab4ffeac77357fe0633d3cee4ce7401",
    policyengine="6.20.3",
    engine="2.179.2",
    core="3.34.10",
)

LABEL = DATA_BUILD.label
