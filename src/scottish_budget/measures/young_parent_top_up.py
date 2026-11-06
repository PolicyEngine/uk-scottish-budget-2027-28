"""Top-up for young parents on Universal Credit in Scotland
(``young_parent_top_up``). Hand-written.

No variable exists for it (issue #6). The top-up is paid to the head of
each Scottish benefit unit that receives Universal Credit, has a child and
has an adult under ``max_age``. It is paid through
``scottish_child_payment``, which is disregarded for Universal Credit and
income tax as a Scottish top-up would be, and counted in household net
income.

PLACEHOLDER defaults: set the weekly amount, age limit and start year on
the day.
"""

from scottish_budget.formula_tools import call_formula, replace_formula


def young_parent_top_up(sim, weekly_amount=10.0, max_age=25, start_year=2027):
    """``weekly_amount`` a week to eligible young parents' benefit units."""
    if weekly_amount < 0:
        raise ValueError("weekly_amount is not negative")
    native = sim.tax_benefit_system.get_variable("scottish_child_payment")
    country_enum = sim.tax_benefit_system.get_variable(
        "country"
    ).possible_values

    def formula(person, period, parameters):
        current = call_formula(native, person, period, parameters)
        if period.start.year < start_year:
            return current
        benunit = person.benunit
        young_adult = person("is_adult", period) & (
            person("age", period) < max_age
        )
        eligible = (
            person("is_benunit_head", period)
            & (benunit("universal_credit", period) > 0)
            & (benunit.sum(person("is_child", period)) > 0)
            & benunit.any(young_adult)
            & (person.household("country", period) == country_enum.SCOTLAND)
        )
        return current + eligible * weekly_amount * 52

    replace_formula(sim, "scottish_child_payment", formula)
    return sim
