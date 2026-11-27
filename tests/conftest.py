import pytest
from template_registry import TEMPLATE


@pytest.fixture
def template(monkeypatch, tmp_path):
    """The frozen template registry in place of ``reforms.MEASURES``, in
    every module that reads it, so a test passes before and after G1.
    From G3 the real costings file exists and names live measures, so the
    default costings file is an absent one."""
    from scottish_budget import pipeline, reconcile, reforms

    absent = tmp_path / "no-costings" / "sfc_costings_2027_28.csv"
    monkeypatch.setattr(pipeline, "OFFICIAL_COSTINGS", absent)
    by_id = {m.id: m for m in TEMPLATE}
    monkeypatch.setattr(reforms, "MEASURES", TEMPLATE)
    monkeypatch.setattr(reforms, "_BY_ID", by_id)
    monkeypatch.setattr(pipeline, "MEASURES", TEMPLATE)
    monkeypatch.setattr(reconcile, "MEASURES", TEMPLATE)
    return TEMPLATE
