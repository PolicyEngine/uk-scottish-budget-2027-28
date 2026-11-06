"""Helpers for hand-written modifiers (from the Autumn Budget repo's
``measure_templates._call_formula`` and ``_replace_formula``).

A modifier wraps an existing variable: the replacement formula computes the
variable as the engine would, then changes it. These run only inside a
simulation, so ``policyengine_uk`` is imported lazily.
"""


def call_formula(variable, entity, period, parameters):
    """A variable's previous value, computed as policyengine-core does.

    A period with no formula takes the variable's default value; a
    two-argument formula takes no parameters. A ``defined_for`` condition
    is applied here, because the replacement variable does not carry it
    (``scottish_child_payment`` is defined for ``is_scp_eligible``).
    """
    import numpy as np

    formula = variable.get_formula(period)
    if formula is None:
        return entity.filled_array(variable.default_value)
    if formula.__code__.co_argcount == 2:
        value = formula(entity, period)
    else:
        value = formula(entity, period, parameters)
    condition = getattr(variable, "defined_for", None)
    if condition is not None:
        name = getattr(condition, "name", condition)
        value = np.where(entity(name, period), value, variable.default_value)
    return value


def replace_formula(sim, name, formula):
    """Replace ``name``'s formula on this simulation only.

    Refused when the engine would compute the variable some other way: a
    stored input (the formula would be bypassed), a neutralised variable,
    or one built from ``adds`` or ``subtracts``.
    """
    from policyengine_core.reforms import Reform as CoreReform
    from policyengine_uk.model_api import Variable
    from policyengine_uk.utils.scenario import _apply_reform_class

    if set(sim.get_holder(name).get_input_periods(sim.branch_name)):
        raise ValueError(
            f"{name} is a stored input; a formula override would be bypassed"
        )
    current = sim.tax_benefit_system.get_variable(name)
    if getattr(current, "is_neutralized", False):
        raise ValueError(f"{name} is neutralised; it cannot be wrapped")
    if current.adds or current.subtracts:
        raise ValueError(
            f"{name} is built from adds or subtracts; it cannot be wrapped"
        )
    replacement = type(
        name, (Variable,), {"formula": formula, "__module__": __name__}
    )

    class FormulaReform(CoreReform):
        def apply(self):
            self.update_variable(replacement)

    _apply_reform_class(FormulaReform, sim)
