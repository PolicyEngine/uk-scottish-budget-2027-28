"""Hand-written simulation modifiers, one module per modifier.

Rules (from the Autumn Budget repo): literal defaults, no runtime state,
no reads of the clock or the environment, so a receipt can bind the
module's source. Each module is named after its modifier; shared helpers
live outside the package, in ``scottish_budget.formula_tools``.

The values in each module's defaults are placeholders until the Budget is
published; the integrator sets them from the statement on the day.
"""
