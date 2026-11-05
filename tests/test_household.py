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
