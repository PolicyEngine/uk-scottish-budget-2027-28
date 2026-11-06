"""Council tax freeze in Scotland (``council_tax_freeze``).

Council tax is a stored input, grown each year before data load by
``uprate_council_tax``. A household's bill grows by (1 + g) / (1 + w),
where g is ``gov.economic_assumptions.yoy_growth.obr.council_tax.scotland``
and w is household weight growth
(``gov.economic_assumptions.yoy_growth.ons.population``). A cash freeze is
therefore g = w for the year, not g = 0, and w differs by release (0.0037
for 2027 on 2.151.0, 0.0013 on 2.165.1 and 2.175.4), so g is computed from
the installed release when the scenario is built (issue #4).

The change is a parameter change on the forecast path, so it is applied
before data load with the forecast overlay, and only the year changed is
replaced (Scenario addition merges by period).
"""

GROWTH = "gov.economic_assumptions.yoy_growth.obr.council_tax.{country}"
WEIGHT_GROWTH = "gov.economic_assumptions.yoy_growth.ons.population"


def growth_for_cash_change(cash_growth, weight_growth):
    """The g that gives bills ``cash_growth`` when weights grow by w."""
    return (1 + cash_growth) * (1 + weight_growth) - 1


def calendar_key(year):
    return f"{year}-01-01.{year}-12-31"


def council_tax_growth_change(
    country="scotland", year=2027, cash_growth=0.0, weight_growth=None
):
    """``{path: {calendar year: g}}`` for a cash change in ``year``.

    ``weight_growth`` defaults to the installed release's value.
    """
    if weight_growth is None:
        from policyengine_uk.system import system

        weight_growth = system.parameters.get_child(WEIGHT_GROWTH)(
            f"{year}-01-01"
        )
    g = growth_for_cash_change(cash_growth, float(weight_growth))
    return {GROWTH.format(country=country): {calendar_key(year): round(g, 6)}}
