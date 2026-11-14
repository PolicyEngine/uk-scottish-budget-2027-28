"""Scottish property income rates set above the main Scottish rates
(``scottish_property_rates``). Hand-written.

policyengine-uk has no Scottish property income rate parameter on any
release to 2.175.x: ``property_income_tax`` taxes a Scottish taxpayer's
property income on the main Scottish scale (issue #2). This wraps it and
adds ``add_on`` times taxable property income after allowances for each
Scottish taxpayer from fiscal year ``start_year``. A uniform add-on across
every band is exact, because each pound of taxable property income falls in
one band and every band's rate rises by the same amount. Different add-ons
by band need the band split and are refused.

Caveat (stated on the Method tab): Scottish property income rests on 666 to
807 person rows, depending on the build (763 rows from only 99 survey
households on build 6f918b81).

PLACEHOLDER defaults: set from the statement on the day.
"""

from scottish_budget.formula_tools import call_formula, replace_formula


def scottish_property_rates(sim, add_on=0.02, start_year=2027):
    """Raise every Scottish rate on property income by ``add_on``."""
    if isinstance(add_on, (list, tuple, dict)):
        raise ValueError(
            "Different add-ons by band need the band split; this modifier "
            "takes one add-on for every band"
        )
    if not 0 <= add_on <= 0.2:
        raise ValueError("add_on is a decimal rate, 0.02 for 2p")
    import numpy as np

    native = sim.tax_benefit_system.get_variable("property_income_tax")

    def formula(person, period, parameters):
        current = call_formula(native, person, period, parameters)
        if period.start.year < start_year:
            return current
        scottish = person("pays_scottish_income_tax", period)
        taxable = person("taxable_property_income_after_allowances", period)
        return current + np.where(scottish, add_on * taxable, 0)

    replace_formula(sim, "property_income_tax", formula)
    return sim
