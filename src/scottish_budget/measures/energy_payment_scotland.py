"""£100 payment to Scottish households in council tax Bands A to D
(``energy_payment_scotland``). Hand-written.

Ported from the Autumn Budget repo's ``household_energy_payment_2026``,
which pays England's £100 through ``ebr_council_tax_rebate`` (the 2022
Energy Bills Rebate's Bands A to D payment, counted in household benefits
and net income on 2.151.0 and later). A parameter change cannot do it:
``gov.treasury.household_energy_payment.countries`` is a list, which
Scenario parameter changes refuse, and the parameter is absent before
policyengine-uk 2.170.2. The payment is keyed on the fiscal year the
simulation period starts in, so no lookup instant can miss it.

PLACEHOLDER defaults: the amount and the fiscal year are set from the
statement on the day (issue #3).
"""

from scottish_budget.formula_tools import call_formula, replace_formula


def energy_payment_scotland(
    sim,
    amount=100,
    year=2027,
    country="SCOTLAND",
    bands=("A", "B", "C", "D"),
):
    """Pay ``amount`` in fiscal year ``year`` to each household in
    ``country`` whose council tax band is in ``bands``."""
    import numpy as np

    native = sim.tax_benefit_system.get_variable("ebr_council_tax_rebate")
    country_enum = sim.tax_benefit_system.get_variable(
        "country"
    ).possible_values
    band_enum = sim.tax_benefit_system.get_variable(
        "council_tax_band"
    ).possible_values

    def formula(household, period, parameters):
        current = call_formula(native, household, period, parameters)
        if period.start.year != year:
            return current
        band = household("council_tax_band", period)
        eligible = np.zeros(household.count, dtype=bool)
        for name in bands:
            eligible = eligible | (band == band_enum[name])
        eligible = eligible & (
            household("country", period) == country_enum[country]
        )
        return current + eligible * amount

    replace_formula(sim, "ebr_council_tax_rebate", formula)
    return sim
