import numpy as np

from scottish_budget.national import scottish_deciles, summarise
from scottish_budget.years import POLICY_YEARS


def test_deciles_split_weight_evenly():
    income = np.arange(100.0)
    deciles = scottish_deciles(income, np.ones(100))
    assert list(np.bincount(deciles)[1:]) == [10] * 10
    assert deciles[0] == 1 and deciles[-1] == 10


def test_deciles_follow_weights():
    deciles = scottish_deciles([1.0, 2.0], [9.0, 1.0])
    assert deciles[0] < deciles[1]


def _frame(n, change=0.0, poverty=0):
    rng = np.arange(n, dtype=float)
    return {
        "in_scotland": rng % 2 == 0,
        "person_in_scotland": np.repeat(rng % 2 == 0, 2),
        "household_weight": np.full(n, 100.0),
        "person_weight": np.full(2 * n, 100.0),
        "household_net_income": 20_000 + 100 * rng + change,
        "equiv_household_net_income": 20_000 + 100 * rng,
        "household_count_people": np.full(n, 2.0),
        "is_child": np.tile([False, True], n),
        "in_poverty_bhc": np.full(2 * n, poverty),
        "in_poverty_ahc": np.full(2 * n, poverty),
    }


def test_summarise_costs_a_gain_and_counts_scotland_only():
    base = {y: _frame(400) for y in POLICY_YEARS}
    reform = {y: _frame(400, change=10.0) for y in POLICY_YEARS}
    out = summarise("m", base, reform)
    # 200 Scottish households x weight 100 x £10 = £200,000 cost.
    assert out["budgetary_impact"][0]["value_bn"] == round(-200_000 / 1e9, 3)
    cells = [c for c in out["decile_impact"] if c["year"] == POLICY_YEARS[0]]
    assert len(cells) == 10
    assert all(c["avg_change_gbp"] == 10.0 for c in cells)
    assert all(c["pct_change"] > 0 for c in cells)
    assert out["winners_losers"][0]["gain_share"] == 1.0
    child = [p for p in out["poverty"] if p["basis"] == "ahc"][0]
    assert child["change_count"] == 0


def test_summarise_counts_children_lifted_out_of_poverty():
    base = {y: _frame(40, poverty=1) for y in POLICY_YEARS}
    reform = {y: _frame(40, poverty=0) for y in POLICY_YEARS}
    out = summarise("m", base, reform)
    row = [p for p in out["poverty"] if p["basis"] == "bhc"][0]
    assert row["baseline_rate"] == 1.0 and row["reform_rate"] == 0.0
    assert row["change_count"] == -20 * 100
