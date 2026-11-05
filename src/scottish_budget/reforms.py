"""The measure registry: every candidate measure for the Scottish Budget.

PLACEHOLDERS. Until the draft Budget is published on 3 December 2026,
every entry is a placeholder built from the probable reforms in
docs/candidate-reforms.md. Each has ``placeholder=True`` and
``publish=False``, so nothing here reaches a public figure. On the day the
integrator replaces the values with the statement's, sets
``placeholder=False``, and only then sets ``publish=True`` (RUNBOOK G1).

Charts, the household calculator and the ledger read the measure list
from this registry (via results.json), never from a hard-coded list.
"""

from dataclasses import dataclass, field

from scottish_budget.measure_templates import (
    rate_change,
    switch_change,
    threshold_change,
)
from scottish_budget.models import Reform

ROUTES = (
    "dashboard-param",
    "dashboard-structural",
    "ledger",
    "not-computable",
    "needs-pe-uk-first",
)
CAUSES = (
    "parameter",
    "formula",
    "data_calibration",
    "basis",
    "timing_fiscal_calendar",
    "coverage",
    "interaction",
    "baseline_mismatch",
)
LIKELIHOOD = ("high", "medium", "low")

SCOT_RATES = "gov.hmrc.income_tax.rates.scotland.rates"
SCP = "gov.social_security_scotland.scottish_child_payment"
SCP_CONTRIB = "gov.contrib.scotland.scottish_child_payment"
CARER = "gov.social_security_scotland.carer_support_payment"
LBTT = "gov.revenue_scotland.lbtt.residential"


@dataclass(frozen=True)
class Measure:
    reform: Reform
    route: str
    cause: str
    likelihood: str
    topic: str
    basis_note: str
    issues: tuple[int, ...] = ()
    data_limits: tuple[str, ...] = ()
    model_limits: tuple[str, ...] = ()
    in_baseline: bool = False
    """Trap row: the statement repeats something already in the baseline."""
    calculator: bool = True
    """Shown in the household calculator."""
    placeholder: bool = True
    publish: bool = False
    extra: dict = field(default_factory=dict)

    @property
    def id(self) -> str:
        return self.reform.id


def _both_years(value):
    return {"2027": value, "2028": value}


MEASURES: tuple[Measure, ...] = (
    Measure(
        reform=Reform(
            id="starter_basic_thresholds",
            name="Starter and basic rate thresholds raised",
            description=(
                "PLACEHOLDER. Top of the starter band to £17,116 and top of "
                "the basic band to £30,559 (3.5% on the full thresholds). "
                "Thresholds are entered above the personal allowance."
            ),
            parameter_changes={
                **threshold_change(
                    f"{SCOT_RATES}[1].threshold", _both_years(4_546)
                ),
                **threshold_change(
                    f"{SCOT_RATES}[2].threshold", _both_years(17_989)
                ),
            },
        ),
        route="dashboard-param",
        cause="parameter",
        likelihood="high",
        topic="income_tax",
        basis_note=(
            "The baseline thresholds differ by release (4,046 / 17,295 on "
            "2.151.0, 4,103 / 17,536 on 2.175.4), so state the release "
            "beside the cost."
        ),
        issues=(1,),
    ),
    Measure(
        reform=Reform(
            id="upper_thresholds_frozen",
            name="Higher, advanced and top thresholds frozen",
            description=(
                "TRAP ROW. The freeze at £43,662, £75,000 and £125,140 to "
                "2028-29 is already in the baseline on both releases; it "
                "costs nothing against current law."
            ),
        ),
        route="ledger",
        cause="baseline_mismatch",
        likelihood="high",
        topic="income_tax",
        basis_note="Already in the baseline: record, do not cost.",
        in_baseline=True,
        calculator=False,
    ),
    Measure(
        reform=Reform(
            id="new_band_before_higher",
            name="New band before the higher rate",
            description=(
                "PLACEHOLDER. A new band between the intermediate and "
                "higher rates. Needs a bracket inserted into the Scottish "
                "scale, which parameter changes cannot do."
            ),
        ),
        route="dashboard-structural",
        cause="formula",
        likelihood="low",
        topic="income_tax",
        basis_note="Bracket insert: a modifier in measures/.",
    ),
    Measure(
        reform=Reform(
            id="intermediate_rate_plus_1p",
            name="Intermediate rate up 1p",
            description="PLACEHOLDER. Intermediate rate from 21% to 22%.",
            parameter_changes=rate_change(
                f"{SCOT_RATES}[2].rate", _both_years(0.22)
            ),
        ),
        route="dashboard-param",
        cause="parameter",
        likelihood="low",
        topic="income_tax",
        basis_note=(
            "Static; the official ready reckoner includes behaviour, so "
            "expect the PolicyEngine figure to be larger."
        ),
        issues=(7,),
    ),
    Measure(
        reform=Reform(
            id="scottish_property_income_rates",
            name="Scottish property income rates",
            description=(
                "PLACEHOLDER. Scottish rates on property income set 2p "
                "above the main Scottish rates from 2027-28."
            ),
        ),
        route="needs-pe-uk-first",
        cause="formula",
        likelihood="medium",
        topic="income_tax",
        basis_note="No Scottish property rate parameter yet.",
        issues=(2,),
        data_limits=("thin_scottish_property_income",),
        model_limits=("no_scottish_property_rates",),
    ),
    Measure(
        reform=Reform(
            id="scp_increase",
            name="Scottish Child Payment raised",
            description=(
                "PLACEHOLDER. Scottish Child Payment of £30.00 a week in "
                "2027-28. CPI uprating to £29.20 is already in the "
                "baseline on both releases."
            ),
            parameter_changes=threshold_change(
                f"{SCP}.amount", _both_years(30.00)
            ),
        ),
        route="dashboard-param",
        cause="parameter",
        likelihood="medium",
        topic="social_security",
        basis_note="Weekly amount; rounded to 5p.",
    ),
    Measure(
        reform=Reform(
            id="scp_under_one_premium",
            name="Scottish Child Payment premium for children under one",
            description=(
                "PLACEHOLDER. £40 a week for each child under one from "
                "2027-28, through the existing contributed reform, which "
                "is off in the baseline."
            ),
            parameter_changes={
                **switch_change(f"{SCP_CONTRIB}.in_effect", _both_years(True)),
                **threshold_change(
                    f"{SCP_CONTRIB}.under_one", _both_years(40.00)
                ),
            },
        ),
        route="dashboard-param",
        cause="timing_fiscal_calendar",
        likelihood="high",
        topic="social_security",
        basis_note=(
            "The parameter starts on 2027-04-01; check the statement's "
            "start date before costing a full year."
        ),
    ),
    Measure(
        reform=Reform(
            id="energy_payment_bands_a_d",
            name="£100 payment for homes in council tax Bands A to D",
            description=(
                "PLACEHOLDER. A one-off £100 for each household in Bands A "
                "to D. The model has the payment for England only, on "
                "2.175.4 only."
            ),
        ),
        route="needs-pe-uk-first",
        cause="coverage",
        likelihood="high",
        topic="council_tax",
        basis_note="Which tax year the payment falls in is not yet known.",
        issues=(3,),
        data_limits=("main_homes_only",),
        model_limits=("energy_payment_england_only",),
    ),
    Measure(
        reform=Reform(
            id="council_tax_freeze",
            name="Council tax freeze",
            description=(
                "PLACEHOLDER. Bills held flat in cash terms in 2027-28. "
                "Needs council tax growth set to weight growth and the "
                "dataset re-projected."
            ),
        ),
        route="dashboard-structural",
        cause="data_calibration",
        likelihood="medium",
        topic="council_tax",
        basis_note="A freeze is g = weight growth, not g = 0.",
        issues=(4,),
        data_limits=("council_tax_is_an_input",),
    ),
    Measure(
        reform=Reform(
            id="council_tax_bands_i_j",
            name="Council tax Bands I and J",
            description=(
                "PLACEHOLDER. New bands for homes worth £1m to £2m and over "
                "£2m, from April 2028."
            ),
        ),
        route="not-computable",
        cause="coverage",
        likelihood="medium",
        topic="council_tax",
        basis_note="From 2028-29 only.",
        issues=(5,),
        data_limits=("no_band_j_homes",),
        model_limits=("no_band_j",),
    ),
    Measure(
        reform=Reform(
            id="carer_supplement_increase",
            name="Scottish Carer Supplement raised",
            description=(
                "PLACEHOLDER. Carer supplement of £12.50 in 2027-28. "
                "2.151.0 holds it at £11.70; 2.175.4 uprates it to £12.10."
            ),
            parameter_changes=threshold_change(
                f"{CARER}.supplement", _both_years(12.50)
            ),
        ),
        route="dashboard-param",
        cause="baseline_mismatch",
        likelihood="medium",
        topic="social_security",
        basis_note="The baseline differs by release.",
        issues=(1,),
        model_limits=("carer_supplement_not_uprated",),
    ),
    Measure(
        reform=Reform(
            id="adp_changes",
            name="Adult Disability Payment changes",
            description=(
                "PLACEHOLDER. Changes to ADP eligibility rules. ADP is "
                "carried as PIP in the data."
            ),
        ),
        route="not-computable",
        cause="coverage",
        likelihood="low",
        topic="social_security",
        basis_note="Rate changes could pass through PIP; rule changes cannot.",
        issues=(6,),
        data_limits=("adp_carried_as_pip",),
        model_limits=("no_scottish_payments",),
        calculator=False,
    ),
    Measure(
        reform=Reform(
            id="young_parent_top_up",
            name="Top-up for young parents on Universal Credit",
            description=(
                "PLACEHOLDER. A monthly top-up for UC families with a "
                "parent under 25."
            ),
        ),
        route="needs-pe-uk-first",
        cause="formula",
        likelihood="low",
        topic="social_security",
        basis_note="No variable yet.",
        issues=(6,),
        model_limits=("no_scottish_payments",),
    ),
    Measure(
        reform=Reform(
            id="benefit_cap_mitigation",
            name="Benefit cap mitigation",
            description=(
                "PLACEHOLDER. Discretionary Housing Payments to make up "
                "the benefit cap reduction."
            ),
        ),
        route="needs-pe-uk-first",
        cause="formula",
        likelihood="low",
        topic="social_security",
        basis_note="benefit_cap_reduction exists; no DHP variable.",
        issues=(6,),
        model_limits=("no_scottish_payments",),
    ),
    Measure(
        reform=Reform(
            id="lbtt_ads_increase",
            name="Additional Dwelling Supplement raised",
            description="PLACEHOLDER. ADS from 8% to 10%.",
            parameter_changes=rate_change(
                f"{LBTT}.additional_residence_surcharge", _both_years(0.10)
            ),
        ),
        route="dashboard-param",
        cause="data_calibration",
        likelihood="low",
        topic="property_tax",
        basis_note="Purchases are a seeded draw; static.",
        calculator=False,
    ),
    Measure(
        reform=Reform(
            id="air_departure_tax",
            name="Air Departure Tax rates",
            description="PLACEHOLDER. Not a household measure.",
        ),
        route="ledger",
        cause="coverage",
        likelihood="medium",
        topic="other",
        basis_note="Record the official costing; not modelled.",
        calculator=False,
    ),
    Measure(
        reform=Reform(
            id="non_domestic_rates",
            name="Non-domestic rates poundage and reliefs",
            description="PLACEHOLDER. Business tax, outside the model.",
        ),
        route="ledger",
        cause="coverage",
        likelihood="medium",
        topic="other",
        basis_note="Record the official costing; not modelled.",
        calculator=False,
    ),
)

_BY_ID = {m.id: m for m in MEASURES}


def measure(measure_id: str) -> Measure:
    try:
        return _BY_ID[measure_id]
    except KeyError as exc:
        raise KeyError(f"No measure {measure_id!r}") from exc


def publishable() -> list[Measure]:
    """Measures cleared for public figures (none in the template)."""
    return [m for m in MEASURES if m.publish and not m.placeholder]
