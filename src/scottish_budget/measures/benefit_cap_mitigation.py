"""Benefit cap mitigation in Scotland (``benefit_cap_mitigation``).
Hand-written.

The model has no Discretionary Housing Payment variable (issue #6). Full
mitigation pays each capped Scottish family its benefit cap reduction, so
the payment is ``benefit_cap_reduction`` times ``take_up`` for households
in Scotland. It is paid through ``ebr_council_tax_rebate`` (counted in
household benefits and net income on every release), the host the energy
payment modifier also uses; each modifier adds to the value before it, so
both can apply together.

PLACEHOLDER defaults: set the take-up and start year on the day.
"""

from scottish_budget.formula_tools import call_formula, replace_formula


def benefit_cap_mitigation(sim, take_up=1.0, start_year=2027):
    """Pay ``take_up`` times the benefit cap reduction to Scottish homes."""
    if not 0 <= take_up <= 1:
        raise ValueError("take_up is a share between 0 and 1")
    from policyengine_uk.model_api import add

    native = sim.tax_benefit_system.get_variable("ebr_council_tax_rebate")
    country_enum = sim.tax_benefit_system.get_variable(
        "country"
    ).possible_values

    def formula(household, period, parameters):
        current = call_formula(native, household, period, parameters)
        if period.start.year < start_year:
            return current
        in_scotland = household("country", period) == country_enum.SCOTLAND
        reduction = add(household, period, ["benefit_cap_reduction"])
        return current + in_scotland * reduction * take_up

    replace_formula(sim, "ebr_council_tax_rebate", formula)
    return sim
