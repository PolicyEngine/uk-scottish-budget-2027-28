"""Household calculator presets and the rest-of-UK twin.

The calculator runs locally (``uv run --extra model``) or in the page from
presets computed by the pipeline. Nothing here calls a hosted API.

Each preset is a PolicyEngine UK situation for one year. Its rest-of-UK
twin is the same household with ``pays_scottish_income_tax`` set to False
for every person, so only the income tax schedule changes and Scottish
benefits stay. The input variable names are checked against the pinned
release by tests/test_engine_households.py (run with the model extra).

Every calculation runs on the forecast overlay, as the population runs do.

Take-up: in a hand-built situation ``would_claim_uc`` and
``would_claim_scp`` default to true, so a household gets Universal Credit
and the Scottish Child Payment whenever it is eligible, even one the data
say does not claim. A preset or call marked ``claims=False`` sets both
inputs to false for every benefit unit and its members (``not_claiming``),
which gives the right answer for such a household. To turn off one benefit
only, a preset lists it under ``"not_claiming"`` (``["scp"]`` for a
household that claims UC but not SCP) and ``calculate`` takes
``not_claimed=("scp",)``. Population runs use the stored take-up
draws in the Microcosm file instead (María Juaristi, 13 November 2026).
"""

import copy

from scottish_budget.years import BUDGET_YEAR

SCOTTISH_TAX_INPUT = "pays_scottish_income_tax"
# Take-up inputs; both default to true in policyengine-uk. In 2.177.7
# would_claim_uc is a benefit-unit input and would_claim_scp a person input.
UC_CLAIM_INPUT = "would_claim_uc"
SCP_CLAIM_INPUT = "would_claim_scp"
# The benefits a household can be marked as not claiming, in that order.
CLAIMABLE = ("uc", "scp")

# The full new State Pension in 2027-28: £250.70 a week (2.174.1, 2.177.7 and
# 2.175.4; £250.71 on 2.151.0) times 52. G0 re-checks it against the pinned release
# (``state_pension_amount``); 2026-27's £12,548 would sit below the
# personal allowance and hide any tax change for pensioners.
FULL_NEW_STATE_PENSION_2027 = 13_036
STATE_PENSION = "gov.dwp.state_pension.new_state_pension.amount"


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
                {
                    "pensioner": _adult(
                        70, y, state_pension=FULL_NEW_STATE_PENSION_2027
                    )
                },
                ["pensioner"],
                [],
                y,
                band="D",
            ),
        ),
        "carer_part_time": (
            "Carer on Carer Support Payment, earning £8,000",
            _situation(
                {
                    "carer": _adult(
                        45,
                        y,
                        employment_income=8_000,
                        carer_support_payment=4_200,
                    )
                },
                ["carer"],
                [],
                y,
                rent=5_400,
                band="B",
            ),
        ),
    }
    # Every preset claims what it is eligible for. A preset that does not
    # claim sets "claims": False; situation_for() then applies not_claiming.
    return {
        key: {
            "label": label,
            "year": year,
            "situation": situation,
            "claims": True,
        }
        for key, (label, situation) in {**single, **others}.items()
    }


def _benefits(benefits) -> tuple[str, ...]:
    """The named benefits, checked, in ``CLAIMABLE`` order."""
    if isinstance(benefits, str):
        raise TypeError(
            f"Give a list of benefits, not the string {benefits!r}"
        )
    names = set(benefits)
    unknown = names - set(CLAIMABLE)
    if unknown:
        raise ValueError(
            f"Unknown benefit(s) {sorted(unknown)}; use any of {list(CLAIMABLE)}"
        )
    return tuple(b for b in CLAIMABLE if b in names)


def not_claiming(
    situation: dict, year: int = BUDGET_YEAR, benunits=None, benefits=CLAIMABLE
) -> dict:
    """The same household with its benefit units not claiming UC and/or SCP.

    ``benefits`` names what is not claimed: "uc" sets ``would_claim_uc``
    false on each named benefit unit (every one by default); "scp" sets
    ``would_claim_scp`` (a person input in 2.177.7) false on each of its
    members. Both by default. Without this a hand-built household gets both
    whenever it is eligible, because the inputs default to true.
    """
    benefits = _benefits(benefits)
    out = copy.deepcopy(situation)
    units = out.get("benunits") or {}
    names = list(units) if benunits is None else list(benunits)
    unknown = [n for n in names if n not in units]
    if unknown:
        raise KeyError(f"no benefit unit(s) {', '.join(unknown)}")
    for name in names:
        if "uc" in benefits:
            units[name][UC_CLAIM_INPUT] = {str(year): False}
        if "scp" in benefits:
            for member in units[name].get("members", []):
                out["people"][member][SCP_CLAIM_INPUT] = {str(year): False}
    return out


def not_claimed(preset: dict) -> tuple[str, ...]:
    """The benefits a preset does not claim.

    ``"claims": False`` means neither UC nor SCP; otherwise the preset's
    ``"not_claiming"`` list (empty by default). Unknown values are refused,
    so a typo never reads as claiming.
    """
    claims = preset.get("claims", True)
    if not isinstance(claims, bool):
        raise TypeError(f"'claims' must be true or false, not {claims!r}")
    listed = _benefits(preset.get("not_claiming", ()))
    return CLAIMABLE if not claims else listed


def situation_for(preset: dict) -> dict:
    """A preset's situation, with its take-up flags applied."""
    benefits = not_claimed(preset)
    if not benefits:
        return preset["situation"]
    return not_claiming(preset["situation"], preset["year"], benefits=benefits)


def state_pension_amount(year: int = BUDGET_YEAR) -> float:
    """The full new State Pension a year on the installed release."""
    from policyengine_uk.system import system

    weekly = system.parameters.get_child(STATE_PENSION)(f"{year}-04-06")
    return round(float(weekly) * 52, 2)


def rest_of_uk_twin(situation: dict, year: int = BUDGET_YEAR) -> dict:
    """The same household taxed on the rest-of-UK income tax schedule."""
    twin = copy.deepcopy(situation)
    for person in twin["people"].values():
        person[SCOTTISH_TAX_INPUT] = {str(year): False}
    return twin


def combined_scenario(reforms=()):
    """The reforms' scenarios added together, or None for current law."""
    scenario = None
    for reform in reforms or ():
        part = reform.to_scenario()
        scenario = part if scenario is None else scenario + part
    return scenario


def calculate(
    situation: dict, year: int, reforms=(), claims: bool = True, not_claimed=()
) -> dict[str, float]:
    """Net income and income tax for one situation (needs the model extra).

    ``reforms`` is a list of registry Reforms applied together, on the
    forecast overlay. ``claims=False`` marks a household that does not
    claim: UC and SCP take-up are set false on every benefit unit
    (``not_claiming``). ``not_claimed=("scp",)`` turns off one benefit only
    (here, claims UC but not SCP). Check one preset by hand per coded
    measure at G2.
    """
    from policyengine_uk import Simulation

    from scottish_budget.forecast import with_forecast

    if not isinstance(reforms, (list, tuple)):
        reforms = (reforms,)
    benefits = CLAIMABLE if not claims else _benefits(not_claimed)
    if benefits:
        situation = not_claiming(situation, year, benefits=benefits)
    sim = Simulation(
        situation=situation,
        scenario=with_forecast(combined_scenario(reforms)),
    )
    return {
        "household_net_income": float(
            sim.calculate("household_net_income", year).sum()
        ),
        "income_tax": float(sim.calculate("income_tax", year).sum()),
    }


CURVE_MAX = 150_000
CURVE_STEP = 1_000


def _curve_situation(year: int, scottish: bool) -> dict:
    y = str(year)
    person = {"age": {y: 40}}
    if not scottish:
        person[SCOTTISH_TAX_INPUT] = {y: False}
    situation = _situation({"adult": person}, ["adult"], [], y, band="C")
    situation["axes"] = [
        [
            {
                "name": "employment_income",
                "min": 0,
                "max": CURVE_MAX,
                "count": CURVE_MAX // CURVE_STEP + 1,
                "period": y,
            }
        ]
    ]
    return situation


def income_tax_curve(year: int = BUDGET_YEAR, reforms=()) -> list[dict]:
    """Income tax for a single adult by gross earnings, £1,000 steps:
    Scotland under current law and with the measures, and the rest-of-UK
    schedule (needs the model extra)."""
    import numpy as np
    from policyengine_uk import Simulation

    from scottish_budget.forecast import with_forecast

    def tax(scottish, scenario):
        sim = Simulation(
            situation=_curve_situation(year, scottish),
            scenario=with_forecast(scenario),
        )
        return np.asarray(sim.calculate("income_tax", year))

    scenario = combined_scenario(reforms)
    now = tax(True, None)
    after = tax(True, scenario) if scenario is not None else now
    ruk = tax(False, None)
    return [
        {
            "year": year,
            "gross": i * CURVE_STEP,
            "scotland_current_law": round(float(now[i]), 2),
            "scotland_with_measures": round(float(after[i]), 2),
            "rest_of_uk": round(float(ruk[i]), 2),
        }
        for i in range(len(now))
    ]
