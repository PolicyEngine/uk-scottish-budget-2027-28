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
        out = calculate(preset["situation"], preset["year"])
        assert out["household_net_income"] > 0, key
        twin = calculate(rest_of_uk_twin(preset["situation"]), preset["year"])
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
