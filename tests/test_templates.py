import pytest

from scottish_budget.measure_templates import (
    nearest_5p_weekly,
    rate_change,
    switch_change,
    threshold_change,
)

P = "gov.hmrc.income_tax.rates.scotland.rates[2].rate"


def test_rate_change_builds_annual_values():
    assert rate_change(P, {2027: 0.22}) == {P: {"2027": 0.22}}


@pytest.mark.parametrize("bad", [{"2027-04-06": 0.22}, {}, {"27": 0.2}])
def test_annual_keys_only(bad):
    with pytest.raises(ValueError):
        rate_change(P, bad)


def test_rate_must_be_a_decimal():
    with pytest.raises(ValueError):
        rate_change(P, {2027: 22})


def test_threshold_not_negative():
    with pytest.raises(ValueError):
        threshold_change(P.replace("rate", "threshold"), {2027: -1})


def test_switch_takes_booleans():
    path = "gov.contrib.scotland.scottish_child_payment.in_effect"
    assert switch_change(path, {2027: True}) == {path: {"2027": True}}
    with pytest.raises(ValueError):
        switch_change(path, {2027: 1})


def test_path_must_be_gov():
    with pytest.raises(ValueError):
        threshold_change("hmrc.income_tax", {2027: 1})


@pytest.mark.parametrize(
    "raw,rounded",
    [(28.20 * 1.035, 29.20), (29.175, 29.20), (40.0, 40.0), (12.11, 12.10)],
)
def test_nearest_5p(raw, rounded):
    assert nearest_5p_weekly(raw) == pytest.approx(rounded)
