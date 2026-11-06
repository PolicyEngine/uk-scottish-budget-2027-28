"""The measure registry: every candidate measure for the Scottish Budget.

PLACEHOLDERS. Until the draft Budget is published on 3 December 2026,
every entry is a placeholder built from the probable reforms in
docs/candidate-reforms.md. Each has ``placeholder=True`` and
``publish=False``, so nothing here reaches a public figure. On the day the
integrator replaces the values with the statement's, sets
``placeholder=False`` (G1), runs provisional figures (G2), and sets
``publish=True`` only after G3 for that measure. Entries the statement does
not contain are deleted.

``description``, ``name`` and ``basis_note`` are public text (plain
English, no code paths); ``internal_note`` is for the integrator and is
never written to results.json.

Charts, the household calculator and the ledger read the measure list
from this registry (via results.json), never from a hard-coded list.
"""

from dataclasses import dataclass, field

from scottish_budget.measure_templates import (
    rate_change,
    switch_change,
    threshold_change,
)
from scottish_budget.measures.benefit_cap_mitigation import (
    benefit_cap_mitigation,
)
from scottish_budget.measures.council_tax_freeze import (
    council_tax_growth_change,
)
from scottish_budget.measures.energy_payment_scotland import (
    energy_payment_scotland,
)
from scottish_budget.measures.scottish_property_rates import (
    scottish_property_rates,
)
from scottish_budget.measures.young_parent_top_up import young_parent_top_up
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


def freeze_2027() -> dict:
    """Scottish council tax bills flat in cash terms in 2027-28."""
    return council_tax_growth_change("scotland", 2027, 0.0)


@dataclass(frozen=True)
class Measure:
    reform: Reform
    route: str
    cause: str
    likelihood: str
    topic: str
    basis_note: str
    """Public: shown on the measure's card when it adds to the reason."""
    issues: tuple[int, ...] = ()
    data_limits: tuple[str, ...] = ()
    model_limits: tuple[str, ...] = ()
    in_baseline: bool = False
    """Trap row: the statement repeats something already in the baseline."""
    calculator: bool = True
    """Shown in the household calculator."""
    placeholder: bool = True
    publish: bool = False
    internal_note: str = ""
    """For the integrator only: never written to results.json."""
    placeholder_sign: int = 0
    """Sign of the placeholder figure: -1 a cost, +1 a yield, 0 none."""
    first_year: int | None = None
    """First fiscal year the measure applies in, if after the Budget year."""
    extra: dict = field(default_factory=dict)

    @property
    def id(self) -> str:
        return self.reform.id


def _years(v2027, v2028):
    """Explicit values for both policy years.

    An uprated amount is given for 2028-29 as well, uprated by about the
    October 2026 forecast's CPI (3.42%) and rounded to 5p, so a placeholder
    never sits below its own baseline in 2028-29 (a bounded change returns
    to the old path afterwards).
    """
    return {"2027": v2027, "2028": v2028}


def _flat(value):
    """The same value in both policy years (frozen or cash amounts)."""
    return {"2027": value, "2028": value}


MEASURES: tuple[Measure, ...] = (
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
        internal_note=(
            "Thresholds are entered above the personal allowance. Baseline "
            "4,046 / 17,295 on 2.151.0 with the March forecast; 4,103 / "
            "17,536 with the October forecast overlay or on 2.165.1+ "
            "(forecast vintage, not a model change)."
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
        internal_note="Trap row: record in the ledger, do not cost.",
        in_baseline=True,
        calculator=False,
    ),
    Measure(
        reform=Reform(
            id="new_band_before_higher",
            name="New band before the higher rate",
            description=(
                "A new band between the intermediate and higher rates."
            ),
        ),
        route="dashboard-structural",
        cause="formula",
        likelihood="low",
        topic="income_tax",
        basis_note="",
        internal_note=(
            "Bracket insert into the Scottish scale: parameter changes "
            "cannot add a bracket, so it needs a modifier in measures/."
        ),
        placeholder_sign=1,
    ),
    Measure(
        reform=Reform(
            id="intermediate_rate_plus_1p",
            name="Intermediate rate up 1p",
            description="Intermediate rate from 21% to 22%.",
            parameter_changes=rate_change(
                f"{SCOT_RATES}[2].rate", _flat(0.22)
            ),
        ),
        route="dashboard-param",
        cause="parameter",
        likelihood="low",
        topic="income_tax",
        basis_note=(
            "Static. Official costings include behaviour, so expect this "
            "figure to be larger."
        ),
        issues=(7,),
        placeholder_sign=1,
    ),
    Measure(
        reform=Reform(
            id="scottish_property_income_rates",
            name="Scottish property income rates",
            description=(
                "Rates on property income set 2p above the main Scottish "
                "rates from 2027-28."
            ),
            simulation_modifier=scottish_property_rates,
        ),
        route="dashboard-structural",
        cause="formula",
        likelihood="medium",
        topic="income_tax",
        basis_note="",
        internal_note=(
            "No Scottish property rate parameter on any release (issue #2): "
            "measures/scottish_property_rates.py adds a uniform add-on to "
            "property_income_tax for Scottish taxpayers."
        ),
        issues=(2,),
        data_limits=("thin_scottish_property_income",),
        placeholder_sign=1,
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
        internal_note="Weekly amount; rounded to 5p.",
        placeholder_sign=-1,
    ),
    Measure(
        reform=Reform(
            id="scp_under_one_premium",
            name="Scottish Child Payment premium for children under one",
            description=(
                "£40 a week for each child under one from 2027-28, uprated "
                "in 2028-29."
            ),
            parameter_changes={
                **switch_change(f"{SCP_CONTRIB}.in_effect", _flat(True)),
                **threshold_change(
                    f"{SCP_CONTRIB}.under_one", _years(40.00, 41.35)
                ),
            },
        ),
        route="dashboard-param",
        cause="timing_fiscal_calendar",
        likelihood="high",
        topic="social_security",
        basis_note="Costed for a full year from April 2027.",
        internal_note=(
            "Existing contributed reform, off in the baseline; its "
            "parameter starts on 2027-04-01. Check the statement's start "
            "date before costing a full year."
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
        internal_note=(
            "measures/energy_payment_scotland.py pays it through "
            "ebr_council_tax_rebate, which works on 2.151.0 and later. The "
            "countries list parameter (2.170.2+) cannot take a Scenario "
            "parameter change."
        ),
        issues=(3,),
        data_limits=("main_homes_only",),
        placeholder_sign=-1,
    ),
    Measure(
        reform=Reform(
            id="council_tax_freeze",
            name="Council tax freeze",
            description="Council tax bills held flat in cash terms in 2027-28.",
            parameter_changes_factory=freeze_2027,
        ),
        route="dashboard-structural",
        cause="data_calibration",
        likelihood="medium",
        topic="council_tax",
        basis_note=(
            "Council tax is a cost to councils; any Scottish Government "
            "funding to councils for the freeze is not modelled."
        ),
        internal_note=(
            "A freeze is g = weight growth, not g = 0: "
            "measures/council_tax_freeze.py, applied before data load."
        ),
        issues=(4,),
        data_limits=("council_tax_is_an_input",),
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
        internal_note="Needs a Bill; applies from 2028-29 only.",
        issues=(5,),
        data_limits=("no_band_j_homes",),
        model_limits=("no_band_j",),
        first_year=2028,
    ),
    Measure(
        reform=Reform(
            id="carer_supplement_increase",
            name="Scottish Carer Supplement raised",
            description=(
                "Carer Supplement of £12.50 in 2027-28, uprated in 2028-29."
            ),
            parameter_changes=threshold_change(
                f"{CARER}.supplement", _years(12.50, 12.95)
            ),
        ),
        route="dashboard-param",
        cause="baseline_mismatch",
        likelihood="medium",
        topic="social_security",
        basis_note=(
            "The current-law supplement depends on the model release; the "
            "Methodology tab names it."
        ),
        internal_note=(
            "2.151.0 holds it at £11.70; 2.165.1 and later uprate it to "
            "£12.10 (2027) and £12.50 (2028)."
        ),
        issues=(1,),
        model_limits=("carer_supplement_not_uprated",),
        placeholder_sign=-1,
    ),
    Measure(
        reform=Reform(
            id="adp_changes",
            name="Adult Disability Payment changes",
            description="Changes to Adult Disability Payment eligibility.",
        ),
        route="not-computable",
        cause="coverage",
        likelihood="low",
        topic="social_security",
        basis_note="",
        internal_note=(
            "ADP is carried as PIP; rate changes could pass through PIP, "
            "rule changes cannot."
        ),
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
                "A weekly top-up for Universal Credit families with a "
                "parent under 25."
            ),
            simulation_modifier=young_parent_top_up,
        ),
        route="dashboard-structural",
        cause="formula",
        likelihood="low",
        topic="social_security",
        basis_note="",
        internal_note=(
            "No variable exists: measures/young_parent_top_up.py pays it "
            "through scottish_child_payment."
        ),
        issues=(6,),
        placeholder_sign=-1,
    ),
    Measure(
        reform=Reform(
            id="benefit_cap_mitigation",
            name="Benefit cap mitigation",
            description=(
                "Payments that make up the benefit cap reduction for "
                "capped families."
            ),
            simulation_modifier=benefit_cap_mitigation,
        ),
        route="dashboard-structural",
        cause="formula",
        likelihood="low",
        topic="social_security",
        basis_note="Full take-up assumed.",
        internal_note=(
            "No DHP variable: measures/benefit_cap_mitigation.py pays "
            "benefit_cap_reduction through ebr_council_tax_rebate."
        ),
        issues=(6,),
        placeholder_sign=-1,
    ),
    Measure(
        reform=Reform(
            id="lbtt_ads_increase",
            name="Additional Dwelling Supplement raised",
            description=(
                "Additional Dwelling Supplement on second homes and buy-to-"
                "let purchases from 8% to 10%."
            ),
            parameter_changes=rate_change(
                f"{LBTT}.additional_residence_surcharge", _flat(0.10)
            ),
        ),
        route="dashboard-param",
        cause="data_calibration",
        likelihood="low",
        topic="property_tax",
        basis_note=(
            "Static: the number of purchases does not change. Purchases "
            "are modelled, not observed."
        ),
        calculator=False,
        placeholder_sign=1,
    ),
    Measure(
        reform=Reform(
            id="air_departure_tax",
            name="Air Departure Tax rates",
            description="Rates of Air Departure Tax on flights from Scotland.",
        ),
        route="ledger",
        cause="coverage",
        likelihood="medium",
        topic="other",
        basis_note="Not a household tax in the model; the official costing is recorded.",
        calculator=False,
    ),
    Measure(
        reform=Reform(
            id="non_domestic_rates",
            name="Non-domestic rates poundage and reliefs",
            description="Business rates poundage and reliefs.",
        ),
        route="ledger",
        cause="coverage",
        likelihood="medium",
        topic="other",
        basis_note="A business tax, outside the model; the official costing is recorded.",
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
    """Measures cleared for public figures (none in the template).

    With the sign-off switch on (``sign_off.REQUIRED``), a measure needs
    ``publish=True``; with it off, any measure that is not a placeholder.
    """
    from scottish_budget.sign_off import REQUIRED

    return [
        m
        for m in MEASURES
        if not m.placeholder and (m.publish or not REQUIRED)
    ]


def computable() -> list[Measure]:
    """Measures with real values that the engine can run (G2 onward)."""
    return [
        m
        for m in MEASURES
        if not m.placeholder
        and m.route in ("dashboard-param", "dashboard-structural")
        and (m.reform.parameter_changes or m.reform.is_structural())
    ]
