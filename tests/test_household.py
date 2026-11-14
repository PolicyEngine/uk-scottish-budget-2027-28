from scottish_budget.household import (
    SCOTTISH_TAX_INPUT,
    presets,
    rest_of_uk_twin,
)


def test_presets_are_scottish_and_well_formed():
    all_presets = presets(2027)
    assert len(all_presets) >= 6
    for key, preset in all_presets.items():
        situation = preset["situation"]
        household = situation["households"]["household"]
        assert household["region"] == {"2027": "SCOTLAND"}, key
        members = set(household["members"])
        assert members == set(situation["people"]), key
        assert set(situation["benunits"]["benunit"]["members"]) == members


def test_twin_changes_only_the_tax_schedule():
    situation = presets(2027)["single_45k"]["situation"]
    twin = rest_of_uk_twin(situation, 2027)
    assert SCOTTISH_TAX_INPUT not in situation["people"]["adult"]
    assert twin["people"]["adult"][SCOTTISH_TAX_INPUT] == {"2027": False}
    twin["people"]["adult"].pop(SCOTTISH_TAX_INPUT)
    assert twin == situation


def test_lone_parent_preset_has_a_child_under_one():
    situation = presets(2027)["lone_parent_under_one"]["situation"]
    assert situation["people"]["baby"]["age"] == {"2027": 0}


def test_household_fixtures_match_the_presets():
    import importlib.util
    import json
    from pathlib import Path

    root = Path(__file__).resolve().parents[1]
    spec = importlib.util.spec_from_file_location(
        "fixtures", root / "scripts" / "write_household_fixtures.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    folder = root / "data_inputs" / "household_fixtures"
    expected = module.fixtures()
    assert {p.stem for p in folder.glob("*.json")} == set(expected)
    for key, body in expected.items():
        assert json.loads((folder / f"{key}.json").read_text()) == body, key


def test_not_claiming_sets_take_up_false_on_the_benefit_unit_and_members():
    from scottish_budget.household import (
        SCP_CLAIM_INPUT,
        UC_CLAIM_INPUT,
        not_claiming,
    )

    situation = presets(2027)["lone_parent_under_one"]["situation"]
    out = not_claiming(situation, 2027)
    assert out["benunits"]["benunit"][UC_CLAIM_INPUT] == {"2027": False}
    for person in ("parent", "baby"):
        assert out["people"][person][SCP_CLAIM_INPUT] == {"2027": False}
    # The preset itself still claims (the defaults stay true).
    assert UC_CLAIM_INPUT not in situation["benunits"]["benunit"]
    assert SCP_CLAIM_INPUT not in situation["people"]["parent"]


def test_not_claiming_refuses_an_unknown_benefit_unit():
    import pytest

    from scottish_budget.household import not_claiming

    with pytest.raises(KeyError):
        not_claiming(presets(2027)["single_25k"]["situation"], 2027, ["x"])


def test_household_rows_honour_a_does_not_claim_preset(monkeypatch):
    from scottish_budget import pipeline
    from scottish_budget.household import UC_CLAIM_INPUT

    preset = presets(2027)["lone_parent_under_one"]
    monkeypatch.setattr(
        pipeline,
        "presets",
        lambda: {
            "claims": preset,
            "does_not_claim": {**preset, "claims": False},
        },
    )
    seen = {}

    def fake(situation, year, reforms=()):
        unit = situation["benunits"]["benunit"]
        claims = unit.get(UC_CLAIM_INPUT, {}).get(str(year), True)
        seen.setdefault(claims, 0)
        seen[claims] += 1
        return {"household_net_income": 20_000.0 if claims else 15_000.0}

    rows = {r["id"]: r for r in pipeline.household_rows([], calculate=fake)}
    assert rows["claims"]["baseline_net_income"] == 20_000.0
    assert rows["does_not_claim"]["baseline_net_income"] == 15_000.0
    # Baseline, reform and the rest-of-UK twin all keep the flag.
    assert seen == {True: 3, False: 3}


def test_fixtures_export_a_does_not_claim_preset_as_not_claiming(monkeypatch):
    # REVIEW2 S1: the fixture writer goes through situation_for, so a preset
    # marked "claims": False exports (with its twin) as not claiming.
    import importlib.util
    from pathlib import Path

    from scottish_budget.household import SCP_CLAIM_INPUT, UC_CLAIM_INPUT

    root = Path(__file__).resolve().parents[1]
    spec = importlib.util.spec_from_file_location(
        "fixtures", root / "scripts" / "write_household_fixtures.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    preset = presets(2027)["lone_parent_under_one"]
    monkeypatch.setattr(
        module,
        "presets",
        lambda: {"claims": preset, "no": {**preset, "claims": False}},
    )
    out = module.fixtures()
    assert out["claims"]["claims"] is True
    assert (
        UC_CLAIM_INPUT not in out["claims"]["situation"]["benunits"]["benunit"]
    )
    assert out["no"]["claims"] is False
    for body in (out["no"]["situation"], out["no"]["rest_of_uk_twin"]):
        assert body["benunits"]["benunit"][UC_CLAIM_INPUT] == {"2027": False}
        assert body["people"]["baby"][SCP_CLAIM_INPUT] == {"2027": False}
