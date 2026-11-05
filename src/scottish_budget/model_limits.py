"""What the model cannot do yet, by policyengine-uk release.

From the model audit of 5 November 2026: 2.151.0 is the release the
certified bundle (policyengine.py 6.11.1) pins; 2.175.4 is the newest on
PyPI. A measure listed here is routed ``needs-pe-uk-first`` until the
pinned release has what it needs.
"""

from dataclasses import dataclass

BUNDLE_RELEASE = "2.151.0"
NEWEST_RELEASE = "2.175.4"


@dataclass(frozen=True)
class ModelLimit:
    id: str
    reason: str
    fixed_in: str | None
    """First release that has it, or None if no release does."""
    issue: int | None = None


MODEL_LIMITS: tuple[ModelLimit, ...] = (
    ModelLimit(
        "no_scottish_property_rates",
        "No parameter for Scottish property income rates; "
        "property_income_tax sends Scottish taxpayers to the main scale.",
        None,
        2,
    ),
    ModelLimit(
        "energy_payment_england_only",
        "The £100 household energy payment exists from 2.175.4, for "
        "England only, and is £0 from 2027-04-06.",
        "2.175.4",
        3,
    ),
    ModelLimit(
        "no_band_j",
        "CouncilTaxBand has no J and the Scottish band ratios cover A to H.",
        None,
        5,
    ),
    ModelLimit(
        "no_scottish_payments",
        "No variable for ADP, Best Start, Child Winter Heating Payment, "
        "Winter Heating Payment, a young parent top-up or DHP mitigation.",
        None,
        6,
    ),
    ModelLimit(
        "pension_tax_allowance",
        "The Pension Tax Allowance exists from 2.175.4 only.",
        "2.175.4",
        1,
    ),
    ModelLimit(
        "carer_supplement_not_uprated",
        "The carer supplement stays at £11.70 in 2027-28 on 2.151.0.",
        "2.175.4",
        1,
    ),
)

_BY_ID = {limit.id: limit for limit in MODEL_LIMITS}


def model_limit(limit_id: str) -> ModelLimit:
    try:
        return _BY_ID[limit_id]
    except KeyError as exc:
        raise KeyError(f"No model limit {limit_id!r}") from exc


def _release_tuple(release: str) -> tuple[int, ...]:
    return tuple(int(part) for part in release.split("."))


def fixed_in_release(limit_id: str, release: str) -> bool:
    """Whether ``release`` of policyengine-uk lifts the limit."""
    fixed = model_limit(limit_id).fixed_in
    return fixed is not None and _release_tuple(release) >= _release_tuple(
        fixed
    )
