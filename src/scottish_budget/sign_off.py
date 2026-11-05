"""Whether publishing needs people's sign-off: one switch, on.

On (``REQUIRED = True``) while this repository is a pre-release template:
no measure is published unless its registry entry has ``publish=True``,
``placeholder=False`` and the integrator has recorded the engine and data
pair at G0 (docs/RUNBOOK.md). Every automated check in
``scripts/check_public_data.py`` blocks whatever this switch says.
"""

REQUIRED = True
