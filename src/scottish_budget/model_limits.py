"""What the model cannot do yet, by policyengine-uk release.

From the model audits of 5 and 6 November 2026. Three tiers of release
matter (issue #1):

- 2.151.0: what policyengine.py 6.11.1 to 6.14.0 pin, with Microcosm
  a6299504 (the certified pair this repo locks);
- 2.165.1: what policyengine.py#731 (unreleased) would pin, with Microcosm
  0639b9c7; it uprates the carer supplement but has none of the Budget 2026
  measures;
- 2.170.2 and later: the Budget 2026 measures (Pension Tax Allowance,
  household energy payment, 24/44/49 property rates), with no certified
  Microcosm build yet.

A limit here is either worked round in this repo (a modifier in
``measures/``) or makes a measure ``needs-pe-uk-first``.
"""

from dataclasses import dataclass

BUNDLE_RELEASE = "2.151.0"
NEXT_BUNDLE_RELEASE = "2.165.1"
BUDGET_2026_RELEASE = "2.170.2"
NEWEST_RELEASE = "2.175.7"


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
        "No parameter for Scottish property income rates on any release; "
        "property_income_tax sends Scottish taxpayers to the main scale. "
        "Worked round by measures/scottish_property_rates.py.",
        None,
        2,
    ),
    ModelLimit(
        "energy_payment_england_only",
        "The £100 household energy payment exists from 2.170.2, for "
        "England only, and is £0 from 2027-04-06; its countries list "
        "cannot take a parameter change. Worked round by "
        "measures/energy_payment_scotland.py on every release.",
        "2.170.2",
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
        "Winter Heating Payment, a young parent top-up or DHP mitigation. "
        "The top-up and the mitigation are worked round by modifiers in "
        "measures/.",
        None,
        6,
    ),
    ModelLimit(
        "pension_tax_allowance",
        "The Pension Tax Allowance exists from 2.170.2 only.",
        "2.170.2",
        1,
    ),
    ModelLimit(
        "carer_supplement_not_uprated",
        "The carer supplement stays at £11.70 in 2027-28 on 2.151.0; "
        "2.165.1 uprates it to £12.10.",
        "2.165.1",
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
