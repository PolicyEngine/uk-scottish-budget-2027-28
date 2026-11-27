"""Checks on the pinned engine, household situations only (light).

Run with the model extra: ``uv run --extra model pytest -m engine``. They
skip when policyengine_uk is not installed (the CI python job), and need
no microdata.

They test the engine and the measure machinery, not the day's values: each
builds its reform with explicit amounts instead of reading the registry,
which G1 edits (values filled, entries deleted, modifier amounts changed),
so they pass before and after G1. Only the uprating check reads the live
registry, and only the placeholders still in it.
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
from scottish_budget.measure_templates import rate_change  # noqa: E402
from scottish_budget.models import Reform  # noqa: E402
from scottish_budget.reforms import MEASURES, SCOT_RATES  # noqa: E402
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


def _measure_code(module, name):
    """A function from a measure module, or skip: G1 may delete a measure's
    module along with its registry entry, leaving nothing to test."""
    found = pytest.importorskip(f"scottish_budget.measures.{module}")
    return getattr(found, name)


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
    pay = _measure_code("energy_payment_scotland", "energy_payment_scotland")
    reform = _modifier_reform(
        lambda sim: pay(sim, amount=100, year=YEAR, bands=("A", "B", "C", "D"))
    )
    a = _single("A", employment_income=20_000)
    e = _single("E", employment_income=20_000)
    assert calculate(a, YEAR, [reform])["household_net_income"] - calculate(
        a, YEAR
    )["household_net_income"] == pytest.approx(100)
    assert calculate(e, YEAR, [reform])["household_net_income"] == (
        pytest.approx(calculate(e, YEAR)["household_net_income"])
    )


def test_property_add_on_is_two_pence_on_taxable_property_income():
    rates = _measure_code("scottish_property_rates", "scottish_property_rates")
    reform = _modifier_reform(
        lambda sim: rates(sim, add_on=0.02, start_year=YEAR)
    )
    s = _single(employment_income=30_000, property_income=10_000)
    base = calculate(s, YEAR)["income_tax"]
    new = calculate(s, YEAR, [reform])["income_tax"]
    # All £10,000 is taxable property income after allowances here (the
    # personal allowance goes on earnings first).
    assert new - base == pytest.approx(0.02 * 10_000, abs=1)


def test_young_parent_top_up_pays_the_lone_parent_preset():
    top_up = _measure_code("young_parent_top_up", "young_parent_top_up")
    reform = _modifier_reform(
        lambda sim: top_up(
            sim, weekly_amount=10.0, max_age=25, start_year=YEAR
        )
    )
    s = presets()["lone_parent_under_one"]["situation"]
    gain = (
        calculate(s, YEAR, [reform])["household_net_income"]
        - calculate(s, YEAR)["household_net_income"]
    )
    assert gain == pytest.approx(10 * 52)


def test_benefit_cap_mitigation_runs():
    mitigate = _measure_code(
        "benefit_cap_mitigation", "benefit_cap_mitigation"
    )
    reform = _modifier_reform(
        lambda sim: mitigate(sim, take_up=1.0, start_year=YEAR)
    )
    s = presets()["couple_two_children_uc"]["situation"]
    gain = (
        calculate(s, YEAR, [reform])["household_net_income"]
        - calculate(s, YEAR)["household_net_income"]
    )
    assert gain >= 0


def test_council_tax_freeze_reads_weight_growth_from_the_release():
    from policyengine_uk.system import system

    growth = _measure_code("council_tax_freeze", "council_tax_growth_change")
    weight_growth = _measure_code("council_tax_freeze", "WEIGHT_GROWTH")
    freeze = Reform(
        id="t",
        name="t",
        parameter_changes_factory=lambda: growth("scotland", YEAR, 0.0),
    )
    changes = freeze.to_scenario()
    w = system.parameters.get_child(weight_growth)("2027-01-01")
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
        # Values filled at G1 are the statement's: only the placeholders
        # still in the registry are checked.
        if (
            not m.placeholder
            or m.placeholder_sign != -1
            or not m.reform.parameter_changes
        ):
            continue
        for path, values in m.reform.parameter_changes.items():
            if not isinstance(next(iter(values.values())), float):
                continue
            for year in POLICY_YEARS:
                base = _value(params, path, f"{year}-06-01")
                assert values[str(year)] >= base, (m.id, path, year, base)


def test_income_tax_curve_compares_scotland_with_the_rest_of_the_uk():
    from scottish_budget.household import income_tax_curve

    intermediate_plus_1p = Reform(
        id="t",
        name="t",
        parameter_changes=rate_change(
            f"{SCOT_RATES}[2].rate", {"2027": 0.22, "2028": 0.22}
        ),
    )
    rows = income_tax_curve(YEAR, [intermediate_plus_1p])
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
