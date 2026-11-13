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
from scottish_budget.measures.council_tax_freeze import (
    council_tax_growth_change,
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
                "band to £30,559 from April 2027."
            ),
            parameter_changes={
                **threshold_change(f"{SCOT_RATES}[1].threshold", _flat(4_546)),
                **threshold_change(
                    f"{SCOT_RATES}[2].threshold", _flat(17_989)
                ),
            },
            baseline_parameter_changes={
                **threshold_change(f"{SCOT_RATES}[1].threshold", _flat(3_967)),
                **threshold_change(
                    f"{SCOT_RATES}[2].threshold", _flat(16_956)
                ),
            },
        ),
        route="dashboard-param",
        cause="parameter",
        likelihood="high",
        topic="income_tax",
        basis_note=(
            "Measured against the costings' baseline: the 2026-27 starter "
            "and basic thresholds held in cash terms. 2028-29 assumes the thresholds stay at the 2027-28 "
            "level, as the statement gives no 2028-29 value."
        ),
        internal_note=(
            "Entered above the personal allowance: 17,116 - 12,570 = 4,546; "
            "30,559 - 12,570 = 17,989. G3 re-base: custom baseline holds "
            "2026-27's 3,967 / 16,956; current law is 4,103 / 17,536."
        ),
        issues=(1,),
        placeholder=False,
        publish=True,
    ),
    Measure(
        reform=Reform(
            id="upper_thresholds_frozen",
            name="Higher, advanced and top thresholds held",
            description=(
                "The higher, advanced and top rate thresholds stay at "
                "£43,662, £75,000 and £125,140 (rates start at £43,663, "
                "£75,001 and £125,141) in 2027-28 and 2028-29."
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
        placeholder=False,
        publish=True,
    ),
    Measure(
        reform=Reform(
            id="advanced_rate_plus_1p",
            name="Advanced rate up 1p",
            description="Advanced rate from 45% to 46% from April 2027.",
            parameter_changes=rate_change(
                f"{SCOT_RATES}[4].rate", _flat(0.46)
            ),
        ),
        route="dashboard-param",
        cause="parameter",
        likelihood="low",
        topic="income_tax",
        basis_note=(
            "Static: no behavioural response. Costings that include "
            "behaviour will be smaller."
        ),
        issues=(7,),
        placeholder=False,
        publish=True,
    ),
    Measure(
        reform=Reform(
            id="scottish_property_income_rates",
            name="Scottish property income rates",
            description=(
                "Property income of Scottish taxpayers taxed at each "
                "Scottish rate plus 2p from April 2027."
            ),
            simulation_modifier=scottish_property_rates,
        ),
        route="dashboard-structural",
        cause="formula",
        likelihood="medium",
        topic="income_tax",
        basis_note="",
        internal_note=(
            "No Scottish property rate parameter (issue #2): "
            "measures/scottish_property_rates.py adds 2p on taxable "
            "property income after allowances for Scottish taxpayers."
        ),
        issues=(2,),
        data_limits=("thin_scottish_property_income",),
        placeholder=False,
        publish=True,
    ),
    Measure(
        reform=Reform(
            id="lbtt_ads_increase",
            name="Additional Dwelling Supplement raised",
            description=(
                "Additional Dwelling Supplement on second homes and buy-to-"
                "let purchases from 8% to 10%, from 4 December 2026."
            ),
            parameter_changes=rate_change(
                f"{LBTT}.additional_residence_surcharge", _flat(0.10)
            ),
        ),
        route="dashboard-param",
        cause="parameter",
        likelihood="low",
        topic="property_tax",
        basis_note=(
            "Static: the number of purchases does not change. Purchases "
            "are modelled, not observed. The part of 2026-27 from "
            "4 December 2026 is not costed here."
        ),
        calculator=False,
        placeholder=False,
        publish=True,
    ),
    Measure(
        reform=Reform(
            id="non_domestic_rates",
            name="Non-domestic rates held",
            description=(
                "Basic, intermediate and higher property rates held at "
                "48.1p, 53.5p and 54.8p."
            ),
        ),
        route="ledger",
        cause="coverage",
        likelihood="medium",
        topic="other",
        basis_note="A business tax, outside the model; the official costing is recorded.",
        calculator=False,
        placeholder=False,
        publish=True,
    ),
    Measure(
        reform=Reform(
            id="air_departure_tax",
            name="Air Departure Tax rates",
            description="Air Departure Tax rates for 2027-28 match the UK's Air Passenger Duty.",
        ),
        route="ledger",
        cause="baseline_mismatch",
        likelihood="medium",
        topic="other",
        basis_note="Not a household tax in the model; the official costing is recorded.",
        in_baseline=True,
        calculator=False,
        placeholder=False,
        publish=True,
    ),
    Measure(
        reform=Reform(
            id="council_tax_freeze",
            name="Council tax freeze",
            description="Council tax bills held at 2026-27 levels in 2027-28.",
            parameter_changes_factory=freeze_2027,
        ),
        route="dashboard-structural",
        cause="data_calibration",
        likelihood="medium",
        topic="council_tax",
        basis_note=(
            "Council tax is a cost to councils; the Scottish Government's "
            "funding to councils for the freeze is not modelled. Bills grow "
            "as forecast from the frozen level in 2028-29."
        ),
        internal_note=(
            "A freeze is g = weight growth, not g = 0: "
            "measures/council_tax_freeze.py, applied before data load."
        ),
        issues=(4,),
        data_limits=("council_tax_is_an_input",),
        placeholder=False,
        publish=True,
    ),
    Measure(
        reform=Reform(
            id="council_tax_bands_i_j",
            name="Council tax Bands I and J",
            description=(
                "New bands from April 2028: Band I for homes over £1m at "
                "3.00 times Band D, Band J over £2m at 3.50 times."
            ),
        ),
        route="not-computable",
        cause="coverage",
        likelihood="medium",
        topic="council_tax",
        basis_note="",
        internal_note="Applies from 2028-29 only.",
        issues=(5,),
        data_limits=("no_band_j_homes",),
        model_limits=("no_band_j",),
        first_year=2028,
        placeholder=False,
        publish=True,
    ),
    Measure(
        reform=Reform(
            id="scottish_benefits_uprating",
            name="Scottish benefits uprated by 3.5%",
            description=(
                "Scottish benefits up 3.5% from April 2027: Scottish Child "
                "Payment £29.20, Carer Support Payment £89.50 and Scottish "
                "Carer Supplement £12.10 a week."
            ),
        ),
        route="ledger",
        cause="baseline_mismatch",
        likelihood="high",
        topic="social_security",
        basis_note=(
            "Already current law, so it costs nothing against the baseline."
        ),
        internal_note=(
            "Trap row: baseline 2027 is SCP 29.20, CSP 89.50, supplement "
            "12.10 on 2.177.7."
        ),
        in_baseline=True,
        calculator=False,
        placeholder=False,
        publish=True,
    ),
    Measure(
        reform=Reform(
            id="scp_under_one_premium",
            name="Scottish Child Payment premium for children under one",
            description=(
                "Scottish Child Payment of £40.00 a week in total for each "
                "child under one from April 2027."
            ),
            parameter_changes={
                **switch_change(f"{SCP_CONTRIB}.in_effect", _flat(True)),
                **threshold_change(
                    f"{SCP_CONTRIB}.under_one", _years(40.00, 40.80)
                ),
            },
        ),
        route="dashboard-param",
        cause="parameter",
        likelihood="high",
        topic="social_security",
        basis_note=(
            "Costed for a full year from April 2027; 2028-29 uses the "
            "model's uprated amount."
        ),
        internal_note=(
            "Existing contributed reform, off in the baseline; under_one is "
            "the total weekly amount (40.80 in 2028 in the parameter)."
        ),
        placeholder=False,
        publish=True,
    ),
    Measure(
        reform=Reform(
            id="young_parent_top_up",
            name="Young parent payment",
            description=(
                "£10.00 a week per family from 1 October 2027 for families "
                "receiving Scottish Child Payment with a parent under 25."
            ),
            simulation_modifier=young_parent_top_up,
        ),
        route="dashboard-structural",
        cause="formula",
        likelihood="low",
        topic="social_security",
        basis_note=(
            "2027-28 counts 188 of 366 days, from 1 October 2027; 2028-29 "
            "a full year."
        ),
        internal_note=(
            "No variable exists: measures/young_parent_top_up.py pays it "
            "through scottish_child_payment to benefit units already "
            "receiving it."
        ),
        issues=(6,),
        placeholder=False,
        publish=True,
    ),
    Measure(
        reform=Reform(
            id="adp_changes",
            name="Adult Disability Payment mobility descriptors",
            description=(
                "Changes to the mobility component descriptors from April "
                "2028."
            ),
        ),
        route="not-computable",
        cause="coverage",
        likelihood="low",
        topic="social_security",
        basis_note="",
        internal_note=(
            "ADP is carried as PIP; descriptor (rule) changes cannot pass "
            "through it."
        ),
        issues=(6,),
        data_limits=(
            "adp_carried_as_pip",
            "scottish_disability_carer_caseloads",
        ),
        model_limits=("no_scottish_payments",),
        calculator=False,
        first_year=2028,
        placeholder=False,
        publish=True,
    ),
    Measure(
        reform=Reform(
            id="energy_payment_bands_a_d",
            name="£100 payment for homes in council tax Bands A to D",
            description=(
                "A one-off £100 towards energy bills for each household in "
                "Bands A to D, paid by 31 March 2027."
            ),
        ),
        route="ledger",
        cause="timing_fiscal_calendar",
        likelihood="high",
        topic="council_tax",
        basis_note=(
            "Paid by 31 March 2027, so it falls in 2026-27, before the "
            "years shown here (2027-28 and 2028-29). PolicyEngine static "
            "estimate for 2026-27: £185m to about 1.85 million households."
        ),
        internal_note=(
            "measures/energy_payment_scotland.py could pay it in fiscal "
            "2026, but 2026 is not a policy year in years.json."
        ),
        issues=(3,),
        calculator=False,
        placeholder=False,
        publish=True,
    ),
    Measure(
        reform=Reform(
            id="bus_fare_cap",
            name="£2 bus fare cap across Scotland",
            description="The £2 single bus fare cap extended across Scotland from 1 June 2027.",
        ),
        route="ledger",
        cause="coverage",
        likelihood="medium",
        topic="other",
        basis_note="Spending, outside the model; the official costing is recorded.",
        calculator=False,
        placeholder=False,
        publish=True,
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
