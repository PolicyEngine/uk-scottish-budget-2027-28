"""A frozen copy of part of the template registry, for tests.

On the day, G1 edits ``reforms.MEASURES`` in place: kept entries get the
statement's values and ``placeholder=False``, and entries the statement
lacks are deleted. Tests of the machinery (combine, the placeholder file,
reconcile) must not depend on that, or ``uv run pytest`` fails after G1.
They run on this copy instead, installed by the ``template`` fixture in
``conftest.py``. Tests of the live registry (ids unique, routes known,
limits resolve) still read ``reforms.MEASURES``, so they check the
integrator's edits.

The entries are copied from the template as committed on 26 November 2026:
one parameter measure of each sign convention, a trap row, a structural
modifier and a not-computable line.
"""

from scottish_budget.measure_templates import threshold_change
from scottish_budget.measures.energy_payment_scotland import (
    energy_payment_scotland,
)
from scottish_budget.models import Reform
from scottish_budget.reforms import SCOT_RATES, SCP, Measure


def _flat(value):
    return {"2027": value, "2028": value}


def _years(v2027, v2028):
    return {"2027": v2027, "2028": v2028}


# Every id in the template registry before G1, in order.
TEMPLATE_IDS = (
    "starter_basic_thresholds",
    "upper_thresholds_frozen",
    "new_band_before_higher",
    "intermediate_rate_plus_1p",
    "scottish_property_income_rates",
    "scp_increase",
    "scp_under_one_premium",
    "energy_payment_bands_a_d",
    "council_tax_freeze",
    "council_tax_bands_i_j",
    "carer_supplement_increase",
    "adp_changes",
    "young_parent_top_up",
    "benefit_cap_mitigation",
    "lbtt_ads_increase",
    "air_departure_tax",
    "non_domestic_rates",
)

TEMPLATE: tuple[Measure, ...] = (
    Measure(
        reform=Reform(
            id="starter_basic_thresholds",
            name="Starter and basic rate thresholds raised",
            description=(
                "Top of the starter band to £17,116 and top of the basic "
                "band to £30,559, both held in 2028-29."
            ),
            parameter_changes={
                **threshold_change(f"{SCOT_RATES}[1].threshold", _flat(4_546)),
                **threshold_change(
                    f"{SCOT_RATES}[2].threshold", _flat(17_989)
                ),
            },
        ),
        route="dashboard-param",
        cause="parameter",
        likelihood="high",
        topic="income_tax",
        basis_note=(
            "Measured against thresholds uprated by CPI on the October 2026 "
            "forecast."
        ),
        issues=(1,),
        placeholder_sign=-1,
    ),
    Measure(
        reform=Reform(
            id="upper_thresholds_frozen",
            name="Higher, advanced and top thresholds frozen",
            description=(
                "The higher, advanced and top rate thresholds stay at "
                "£43,662, £75,000 and £125,140 to 2028-29."
            ),
        ),
        route="ledger",
        cause="baseline_mismatch",
        likelihood="high",
        topic="income_tax",
        basis_note=(
            "Already current law, so it costs nothing against the baseline."
        ),
        in_baseline=True,
        calculator=False,
    ),
    Measure(
        reform=Reform(
            id="scp_increase",
            name="Scottish Child Payment raised",
            description=(
                "Scottish Child Payment of £30.00 a week in 2027-28, "
                "uprated in 2028-29."
            ),
            parameter_changes=threshold_change(
                f"{SCP}.amount", _years(30.00, 31.05)
            ),
        ),
        route="dashboard-param",
        cause="parameter",
        likelihood="medium",
        topic="social_security",
        basis_note=(
            "Measured against CPI uprating to £29.20 a week, which is "
            "already current law."
        ),
        placeholder_sign=-1,
    ),
    Measure(
        reform=Reform(
            id="energy_payment_bands_a_d",
            name="£100 payment for homes in council tax Bands A to D",
            description=(
                "A one-off £100 for each Scottish household in Bands A to D."
            ),
            simulation_modifier=energy_payment_scotland,
        ),
        route="dashboard-structural",
        cause="coverage",
        likelihood="high",
        topic="council_tax",
        basis_note="Counted in 2027-28; the tax year is to be confirmed.",
        issues=(3,),
        data_limits=("main_homes_only",),
        placeholder_sign=-1,
    ),
    Measure(
        reform=Reform(
            id="council_tax_bands_i_j",
            name="Council tax Bands I and J",
            description=(
                "New bands for homes worth £1m to £2m and over £2m, from "
                "April 2028."
            ),
        ),
        route="not-computable",
        cause="coverage",
        likelihood="medium",
        topic="council_tax",
        basis_note="",
        issues=(5,),
        data_limits=("no_band_j_homes",),
        model_limits=("no_band_j",),
        first_year=2028,
    ),
)
