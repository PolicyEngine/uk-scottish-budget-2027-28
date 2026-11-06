"""What the data cannot show, and the rule that follows from it.

Pruned from the Autumn Budget repo's data limits to the Scottish Budget.
A measure that acts only through an input the data lack is published as
not computable, with the reason, and never as £0. Figures are from the
model and data audit of 5 November 2026 (Microcosm builds a6299504 and
0639b9c7, 2024-25 values for Scotland).
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class DataLimit:
    id: str
    inputs: tuple[str, ...]
    reason: str
    issue: int | None = None
    blocks: bool = True
    """True: a measure acting only through these inputs is not computable.
    False: computable, but the Method tab states the caveat."""


DATA_LIMITS: tuple[DataLimit, ...] = (
    DataLimit(
        id="no_local_geography",
        inputs=("local_authority", "constituency"),
        reason=(
            "Results are for Scotland as a whole. The national Microcosm "
            "file has no geography below region; the bundle's local-area "
            "file has all 32 Scottish councils, but its fit to income tax "
            "by council is not yet checked, so council results are not "
            "shown."
        ),
        issue=8,
        blocks=False,
    ),
    DataLimit(
        id="no_band_j_homes",
        inputs=("council_tax_band",),
        reason=(
            "No Scottish home in the data is worth over £2m and the model "
            "has no Band J, so Bands I and J cannot be costed."
        ),
        issue=5,
    ),
    DataLimit(
        id="adp_carried_as_pip",
        inputs=("adult_disability_payment",),
        reason=(
            "Adult Disability Payment is carried as PIP; a change to ADP "
            "rules cannot be applied to the data."
        ),
        issue=6,
    ),
    DataLimit(
        id="thin_scottish_property_income",
        inputs=("property_income",),
        reason=(
            "Scottish property income rests on 666 to 807 survey records, "
            "and its total moves from £1.83bn to £2.35bn between builds."
        ),
        issue=2,
        blocks=False,
    ),
    DataLimit(
        id="main_homes_only",
        inputs=("council_tax_band", "council_tax"),
        reason=(
            "The data hold main homes only (1.83m Scottish households in "
            "Bands A to D against about 1.9m dwellings), so payments keyed "
            "on dwellings are slightly understated."
        ),
        issue=3,
        blocks=False,
    ),
    DataLimit(
        id="council_tax_is_an_input",
        inputs=("council_tax",),
        reason=(
            "Council tax is a stored input grown each year; a freeze or "
            "cap needs the dataset re-projected."
        ),
        issue=4,
        blocks=False,
    ),
)

_BY_ID = {limit.id: limit for limit in DATA_LIMITS}


def data_limit(limit_id: str) -> DataLimit:
    try:
        return _BY_ID[limit_id]
    except KeyError as exc:
        raise KeyError(f"No data limit {limit_id!r}") from exc


def blocking_limits(limit_ids) -> list[DataLimit]:
    """The limits among ``limit_ids`` that make a measure not computable."""
    return [data_limit(i) for i in limit_ids if data_limit(i).blocks]
