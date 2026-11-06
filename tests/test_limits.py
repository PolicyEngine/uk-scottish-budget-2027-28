from scottish_budget.data_limits import DATA_LIMITS, blocking_limits
from scottish_budget.model_limits import (
    BUNDLE_RELEASE,
    MODEL_LIMITS,
    NEWEST_RELEASE,
    fixed_in_release,
)


def test_limit_ids_unique():
    assert len({d.id for d in DATA_LIMITS}) == len(DATA_LIMITS)
    assert len({m.id for m in MODEL_LIMITS}) == len(MODEL_LIMITS)


def test_every_limit_has_a_reason_and_issue():
    for limit in (*DATA_LIMITS, *MODEL_LIMITS):
        assert limit.reason
        assert limit.issue is not None


def test_blocking_filter():
    ids = ("no_band_j_homes", "main_homes_only")
    assert [d.id for d in blocking_limits(ids)] == ["no_band_j_homes"]


def test_release_comparison():
    assert not fixed_in_release("pension_tax_allowance", BUNDLE_RELEASE)
    assert fixed_in_release("pension_tax_allowance", NEWEST_RELEASE)
    assert not fixed_in_release("no_band_j", NEWEST_RELEASE)
    assert fixed_in_release("carer_supplement_not_uprated", "2.165.1")
    assert not fixed_in_release("pension_tax_allowance", "2.165.1")
    assert fixed_in_release("energy_payment_england_only", "2.170.2")
