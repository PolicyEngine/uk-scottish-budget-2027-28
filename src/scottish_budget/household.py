"""Household calculator presets and the rest-of-UK twin.

The calculator runs locally (``uv run --extra model``) or in the page from
presets computed by the pipeline. Nothing here calls a hosted API.

Each preset is a PolicyEngine UK situation for one year. Its rest-of-UK
twin is the same household with ``pays_scottish_income_tax`` set to False
for every person, so only the income tax schedule changes and Scottish
benefits stay. PLACEHOLDER: the input variable names are to be checked
against the pinned release at G0.
"""

import copy

from scottish_budget.years import BUDGET_YEAR

SCOTTISH_TAX_INPUT = "pays_scottish_income_tax"


def _adult(age, year, **incomes):
    person = {"age": {year: age}}
    for name, amount in incomes.items():
        person[name] = {year: amount}
    return person


def _child(age, year):
    return {"age": {year: age}}


def _situation(people, adults, children, year, *, rent=None, band="B"):
    members = adults + children
    household = {
        "members": members,
        "region": {year: "SCOTLAND"},
        "council_tax_band": {year: band},
    }
    if rent is not None:
        household["rent"] = {year: rent}
    return {
        "people": people,
        "benunits": {"benunit": {"members": members}},
        "households": {"household": household},
    }


def presets(year: int = BUDGET_YEAR) -> dict[str, dict]:
    """The example households, keyed by id: label plus situation."""
    y = str(year)
    single = {
        f"single_{k}k": (
            f"Single adult earning £{k},000",
            _situation(
                {"adult": _adult(35, y, employment_income=k * 1_000)},
                ["adult"],
                [],
                y,
                band="C" if k < 50 else "E",
            ),
        )
        for k in (25, 45, 60, 100)
    }
    others = {
        "couple_two_children_uc": (
            "Couple with two children on Universal Credit, one earner on "
            "£18,000",
            _situation(
                {
                    "adult_1": _adult(34, y, employment_income=18_000),
                    "adult_2": _adult(32, y),
                    "child_1": _child(4, y),
                    "child_2": _child(7, y),
                },
                ["adult_1", "adult_2"],
                ["child_1", "child_2"],
                y,
                rent=7_800,
                band="B",
            ),
        ),
        "lone_parent_under_one": (
            "Lone parent aged 24 with a child under one, earning £10,000",
            _situation(
                {
                    "parent": _adult(24, y, employment_income=10_000),
                    "baby": _child(0, y),
                },
                ["parent"],
                ["baby"],
                y,
                rent=6_600,
                band="A",
            ),
        ),
        "pensioner_full_state_pension": (
            "Single pensioner on the full new State Pension",
            _situation(
                {"pensioner": _adult(70, y, state_pension=12_548)},
                ["pensioner"],
                [],
                y,
                band="D",
            ),
        ),
    }
    return {
        key: {"label": label, "situation": situation}
        for key, (label, situation) in {**single, **others}.items()
    }


def rest_of_uk_twin(situation: dict, year: int = BUDGET_YEAR) -> dict:
    """The same household taxed on the rest-of-UK income tax schedule."""
    twin = copy.deepcopy(situation)
    for person in twin["people"].values():
        person[SCOTTISH_TAX_INPUT] = {str(year): False}
    return twin


def calculate(situation: dict, year: int, reform=None) -> dict[str, float]:
    """Net income and income tax for one situation (needs the model extra).

    Not exercised by the tests: it loads policyengine_uk. Check one preset
    by hand per coded measure at G2 (docs/RUNBOOK.md).
    """
    from policyengine_uk import Simulation

    kwargs = {"situation": situation}
    if reform is not None:
        kwargs["scenario"] = reform.to_scenario()
    sim = Simulation(**kwargs)
    return {
        "household_net_income": float(
            sim.calculate("household_net_income", year).sum()
        ),
        "income_tax": float(sim.calculate("income_tax", year).sum()),
    }
