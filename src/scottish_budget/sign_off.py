"""Whether publishing needs people's sign-off: one switch, on.

On (``REQUIRED = True``): a measure is published only if its registry entry
has ``publish=True`` and ``placeholder=False``, which the integrator sets
after G3 (docs/RUNBOOK.md). Two places read it:
``reforms.publishable()`` and ``publication.validate_results`` (a measure
marked published without ``publish=True`` is refused). Leave it on.
"""

REQUIRED = True
