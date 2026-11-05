"""The Reform model, copied from the Autumn Budget 2026 dashboard.

A reform is parameter changes (simple measures), a simulation modifier
(structural measures) or both, optionally against its own baseline.
``policyengine_uk`` is imported only when a scenario is built, so the
registry and its tests run without the engine installed.
"""

from typing import Any, Callable, Optional

from pydantic import BaseModel, Field


def _scenario(**kwargs):
    from policyengine_uk.utils.scenario import Scenario

    return Scenario(**kwargs)


class Reform(BaseModel):
    """Definition of a policy reform."""

    id: str = Field(..., description="Unique identifier for the reform")
    name: str = Field(..., description="Human-readable name")
    description: str = Field(default="")
    parameter_changes: Optional[dict[str, dict[str, Any]]] = Field(
        default=None,
        description="Parameter path -> {year: value} for the reform",
    )
    baseline_parameter_changes: Optional[dict[str, dict[str, Any]]] = Field(
        default=None,
        description="Parameter changes for a custom baseline",
    )
    baseline_simulation_modifier: Optional[Callable] = None
    simulation_modifier: Optional[Callable] = None

    model_config = {"arbitrary_types_allowed": True}

    def to_scenario(self):
        """The reform as a policyengine_uk Scenario."""
        kwargs = {}
        if self.simulation_modifier is not None:
            kwargs["simulation_modifier"] = self.simulation_modifier
        if self.parameter_changes is not None:
            kwargs["parameter_changes"] = self.parameter_changes
        return _scenario(**kwargs)

    def to_baseline_scenario(self):
        """The custom baseline as a Scenario, or None for current law."""
        kwargs = {}
        if self.baseline_simulation_modifier is not None:
            kwargs["simulation_modifier"] = self.baseline_simulation_modifier
        if self.baseline_parameter_changes is not None:
            kwargs["parameter_changes"] = self.baseline_parameter_changes
        return _scenario(**kwargs) if kwargs else None

    def has_custom_baseline(self) -> bool:
        return (
            self.baseline_parameter_changes is not None
            or self.baseline_simulation_modifier is not None
        )

    def is_structural(self) -> bool:
        return (
            self.simulation_modifier is not None
            or self.baseline_simulation_modifier is not None
        )
