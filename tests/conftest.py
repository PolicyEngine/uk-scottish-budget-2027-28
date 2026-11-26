import pytest
from template_registry import TEMPLATE


@pytest.fixture
def template(monkeypatch):
    """The frozen template registry in place of ``reforms.MEASURES``, in
    every module that reads it, so a test passes before and after G1."""
    from scottish_budget import pipeline, reconcile, reforms

    by_id = {m.id: m for m in TEMPLATE}
    monkeypatch.setattr(reforms, "MEASURES", TEMPLATE)
    monkeypatch.setattr(reforms, "_BY_ID", by_id)
    monkeypatch.setattr(pipeline, "MEASURES", TEMPLATE)
    monkeypatch.setattr(reconcile, "MEASURES", TEMPLATE)
    return TEMPLATE
