"""Checks on the pinned engine, household situations only (light).

Run with the model extra: ``uv run --extra model pytest -m engine``. They
skip when policyengine_uk is not installed (the CI python job), and need
no microdata.
"""

import pytest

pytest.importorskip("policyengine_uk")

pytestmark = pytest.mark.engine

from scottish_budget.household import (  # noqa: E402
    FULL_NEW_STATE_PENSION_2027,
    calculate,
    presets,
    rest_of_uk_twin,
    situation_for,
    state_pension_amount,
)
from scottish_budget.models import Reform  # noqa: E402
from scottish_budget.reforms import MEASURES, measure  # noqa: E402
from scottish_budget.years import POLICY_YEARS  # noqa: E402

YEAR = 2027


def _single(band="A", **incomes):
    person = {"age": {str(YEAR): 40}}
    person.update({k: {str(YEAR): v} for k, v in incomes.items()})
    return {
        "people": {"p": person},
        "benunits": {"b": {"members": ["p"]}},
        "households": {
            "h": {
                "members": ["p"],
                "region": {str(YEAR): "SCOTLAND"},
                "council_tax_band": {str(YEAR): band},
            }
        },
    }


def _modifier_reform(modifier):
    return Reform(id="t", name="t", simulation_modifier=modifier)


def test_every_preset_runs_on_the_pinned_release():
    for key, preset in presets().items():
        situation = situation_for(preset)
        out = calculate(situation, preset["year"])
        assert out["household_net_income"] > 0, key
        twin = calculate(rest_of_uk_twin(situation), preset["year"])
        assert twin["household_net_income"] > 0, key


def test_pensioner_preset_is_the_full_new_state_pension():
    assert abs(state_pension_amount(YEAR) - FULL_NEW_STATE_PENSION_2027) < 1


def test_energy_payment_reaches_scottish_band_a_to_d_only():
    reform = measure("energy_payment_bands_a_d").reform
    a = _single("A", employment_income=20_000)
    e = _single("E", employment_income=20_000)
    assert calculate(a, YEAR, [reform])["household_net_income"] - calculate(
        a, YEAR
    )["household_net_income"] == pytest.approx(100)
    assert calculate(e, YEAR, [reform])["household_net_income"] == (
        pytest.approx(calculate(e, YEAR)["household_net_income"])
    )


def test_property_add_on_is_two_pence_on_taxable_property_income():
    reform = measure("scottish_property_income_rates").reform
    s = _single(employment_income=30_000, property_income=10_000)
    base = calculate(s, YEAR)["income_tax"]
    new = calculate(s, YEAR, [reform])["income_tax"]
    # All £10,000 is taxable property income after allowances here (the
    # personal allowance goes on earnings first).
    assert new - base == pytest.approx(0.02 * 10_000, abs=1)


def test_young_parent_top_up_pays_the_lone_parent_preset():
    reform = measure("young_parent_top_up").reform
    s = presets()["lone_parent_under_one"]["situation"]
    gain = (
        calculate(s, YEAR, [reform])["household_net_income"]
        - calculate(s, YEAR)["household_net_income"]
    )
    assert gain == pytest.approx(10 * 52)


def test_benefit_cap_mitigation_runs():
    reform = measure("benefit_cap_mitigation").reform
    s = presets()["couple_two_children_uc"]["situation"]
    gain = (
        calculate(s, YEAR, [reform])["household_net_income"]
        - calculate(s, YEAR)["household_net_income"]
    )
    assert gain >= 0


def test_council_tax_freeze_reads_weight_growth_from_the_release():
    from policyengine_uk.system import system

    from scottish_budget.measures.council_tax_freeze import WEIGHT_GROWTH

    changes = measure("council_tax_freeze").reform.to_scenario()
    w = system.parameters.get_child(WEIGHT_GROWTH)("2027-01-01")
    ((path, values),) = changes.parameter_changes.items()
    assert values == {"2027-01-01.2027-12-31": round(float(w), 6)}


def _value(parameters, path, instant):
    node = parameters
    for part in path.replace("]", "").replace("[", ".").split("."):
        node = (
            node.brackets[int(part)] if part.isdigit() else getattr(node, part)
        )
    return node(instant)


def test_no_placeholder_sits_below_its_baseline_in_any_policy_year():
    """Uprated amounts: a raise never turns into a cut in 2028-29."""
    from scottish_budget.forecast import forecast_parameters

    params = forecast_parameters()
    for m in MEASURES:
        if m.placeholder_sign != -1 or not m.reform.parameter_changes:
            continue
        for path, values in m.reform.parameter_changes.items():
            if not isinstance(next(iter(values.values())), float):
                continue
            for year in POLICY_YEARS:
                base = _value(params, path, f"{year}-06-01")
                assert values[str(year)] >= base, (m.id, path, year, base)


def test_income_tax_curve_compares_scotland_with_the_rest_of_the_uk():
    from scottish_budget.household import income_tax_curve

    rows = income_tax_curve(
        YEAR, [measure("intermediate_rate_plus_1p").reform]
    )
    assert rows[0]["gross"] == 0 and rows[-1]["gross"] == 150_000
    at_60k = next(r for r in rows if r["gross"] == 60_000)
    assert at_60k["scotland_current_law"] > at_60k["rest_of_uk"]
    assert at_60k["scotland_with_measures"] > at_60k["scotland_current_law"]


def _uc_and_scp(situation):
    from policyengine_uk import Simulation

    from scottish_budget.forecast import with_forecast

    sim = Simulation(situation=situation, scenario=with_forecast(None))
    return (
        float(sim.calculate("universal_credit", YEAR).sum()),
        float(sim.calculate("scottish_child_payment", YEAR).sum()),
    )


def test_a_household_that_does_not_claim_gets_no_uc_or_scp():
    # Hand-built households default to claiming (would_claim_uc and
    # would_claim_scp are true); a does-not-claim household gets neither.
    from scottish_budget.household import not_claiming

    s = presets()["lone_parent_under_one"]["situation"]
    uc, scp = _uc_and_scp(s)
    assert uc > 0 and scp > 0
    assert _uc_and_scp(not_claiming(s, YEAR)) == (0.0, 0.0)
    claiming = calculate(s, YEAR)["household_net_income"]
    not_claim = calculate(s, YEAR, claims=False)["household_net_income"]
    assert claiming - not_claim == pytest.approx(uc + scp, abs=1)


def test_a_household_that_claims_uc_but_not_scp():
    # Only SCP is turned off: SCP goes to 0 and UC is exactly unchanged.
    from scottish_budget.household import not_claiming

    s = presets()["lone_parent_under_one"]["situation"]
    uc, scp = _uc_and_scp(s)
    assert uc > 0 and scp > 0
    assert _uc_and_scp(not_claiming(s, YEAR, benefits=["scp"])) == (uc, 0.0)
    claiming = calculate(s, YEAR)["household_net_income"]
    no_scp = calculate(s, YEAR, not_claimed=("scp",))["household_net_income"]
    assert claiming - no_scp == pytest.approx(scp, abs=1)
