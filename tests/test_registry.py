import pytest

from scottish_budget.data_limits import data_limit
from scottish_budget.model_limits import model_limit
from scottish_budget.reforms import (
    CAUSES,
    LIKELIHOOD,
    MEASURES,
    ROUTES,
    publishable,
)


def test_ids_unique():
    ids = [m.id for m in MEASURES]
    assert len(ids) == len(set(ids))


def test_every_measure_is_a_held_back_placeholder():
    for m in MEASURES:
        assert m.placeholder, m.id
        assert not m.publish, m.id
        assert m.reform.description, m.id
    assert publishable() == []


@pytest.mark.parametrize("m", MEASURES, ids=lambda m: m.id)
def test_route_cause_likelihood_are_known(m):
    assert m.route in ROUTES
    assert m.cause in CAUSES
    assert m.likelihood in LIKELIHOOD


@pytest.mark.parametrize("m", MEASURES, ids=lambda m: m.id)
def test_param_routes_carry_parameter_changes(m):
    if m.route == "dashboard-param":
        assert m.reform.parameter_changes
        for path, values in m.reform.parameter_changes.items():
            assert path.startswith("gov.")
            assert set(values) == {"2027", "2028"}
    else:
        assert not m.reform.parameter_changes


@pytest.mark.parametrize("m", MEASURES, ids=lambda m: m.id)
def test_limits_and_issues_resolve(m):
    for limit_id in m.data_limits:
        data_limit(limit_id)
    for limit_id in m.model_limits:
        model_limit(limit_id)
    assert all(1 <= i <= 8 for i in m.issues)


def test_not_computable_measures_name_a_blocking_data_limit():
    for m in MEASURES:
        if m.route == "not-computable":
            assert any(data_limit(i).blocks for i in m.data_limits), m.id


def test_needs_pe_uk_first_names_a_model_limit():
    for m in MEASURES:
        if m.route == "needs-pe-uk-first":
            assert m.model_limits, m.id


def test_there_is_a_trap_row_already_in_the_baseline():
    traps = [m for m in MEASURES if m.in_baseline]
    assert traps
    assert all(m.route == "ledger" for m in traps)


def test_starter_basic_central_case_encoding():
    from scottish_budget.reforms import measure

    changes = measure("starter_basic_thresholds").reform.parameter_changes
    scale = "gov.hmrc.income_tax.rates.scotland.rates"
    # £17,116 and £30,559 less the £12,570 personal allowance
    assert changes[f"{scale}[1].threshold"]["2027"] == 17_116 - 12_570
    assert changes[f"{scale}[2].threshold"]["2027"] == 30_559 - 12_570
