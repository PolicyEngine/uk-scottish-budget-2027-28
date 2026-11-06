from scottish_budget.forecast import (
    forecast_parameter_changes,
    forecast_record,
)
from scottish_budget.measures.council_tax_freeze import (
    GROWTH,
    calendar_key,
    council_tax_growth_change,
    growth_for_cash_change,
)
from scottish_budget.reforms import MEASURES


def test_forecast_is_the_october_2026_obr_vintage():
    record = forecast_record()
    assert record["vintage"] == "OBR EFO October 2026"
    cpi = forecast_parameter_changes()[
        "gov.economic_assumptions.yoy_growth.obr.consumer_price_index"
    ]
    assert cpi[calendar_key(2027)] == 0.0342


def test_no_registry_measure_changes_a_forecast_path():
    forecast = set(forecast_parameter_changes())
    for m in MEASURES:
        overlap = forecast & set(m.reform.parameter_changes or {})
        assert not overlap, (m.id, overlap)


def test_a_cash_freeze_is_g_equals_weight_growth():
    assert round(growth_for_cash_change(0.0, 0.0013), 10) == 0.0013
    change = council_tax_growth_change("scotland", 2027, 0.0, 0.0037)
    path = GROWTH.format(country="scotland")
    assert change == {path: {"2027-01-01.2027-12-31": 0.0037}}
    assert path in forecast_parameter_changes()
    # A 3% rise with 0.37% weight growth.
    assert round(growth_for_cash_change(0.03, 0.0037), 6) == 0.033811
