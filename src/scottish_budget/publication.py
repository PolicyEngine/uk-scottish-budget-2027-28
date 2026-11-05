"""Scaled-down publication layer: disclosure floor, validation, manifest.

The figures come from UKDS-licensed survey microdata, so public files
carry no record identifiers or weights, and any cell resting on fewer than
``DISCLOSURE_FLOOR`` survey households is withheld (published as null with
a reason, never as 0).
"""

import hashlib
import json

DISCLOSURE_FLOOR = 10

FORBIDDEN_KEYS = frozenset(
    {
        "household_id",
        "person_id",
        "benunit_id",
        "household_weight",
        "person_weight",
        "benunit_weight",
        "weight",
    }
)

REQUIRED_META = (
    "status",
    "placeholder",
    "policyengine",
    "policyengine_uk",
    "dataset",
    "basis",
    "years",
    "disclosure_floor",
)
REQUIRED_MEASURE = (
    "id",
    "name",
    "description",
    "route",
    "cause",
    "topic",
    "status",
    "placeholder",
    "publish",
    "budgetary_impact",
)
STATUSES = ("placeholder", "published", "not-computable", "ledger", "pending")


class PublicationError(ValueError):
    pass


def apply_floor(cells: list[dict], floor: int = DISCLOSURE_FLOOR):
    """Withhold cells with fewer than ``floor`` records (value -> None)."""
    out = []
    for cell in cells:
        cell = dict(cell)
        if cell.get("n_records", 0) < floor:
            for key in ("avg_change_gbp", "pct_change", "value"):
                if key in cell:
                    cell[key] = None
            cell["withheld"] = "fewer than %d survey households" % floor
        out.append(cell)
    return out


def _walk_keys(obj, path="$"):
    if isinstance(obj, dict):
        for key, value in obj.items():
            yield f"{path}.{key}", key
            yield from _walk_keys(value, f"{path}.{key}")
    elif isinstance(obj, list):
        for i, value in enumerate(obj):
            yield from _walk_keys(value, f"{path}[{i}]")


def validate_results(results: dict) -> None:
    """Raise PublicationError if results.json breaks the schema or rules."""
    problems = []
    meta = results.get("meta", {})
    for key in REQUIRED_META:
        if key not in meta:
            problems.append(f"meta.{key} missing")
    for where, key in _walk_keys(results):
        if key.lower() in FORBIDDEN_KEYS:
            problems.append(f"{where}: record identifier or weight")
    for m in results.get("measures", []):
        for key in REQUIRED_MEASURE:
            if key not in m:
                problems.append(f"measure {m.get('id')}: {key} missing")
        status = m.get("status")
        if status not in STATUSES:
            problems.append(f"measure {m.get('id')}: bad status {status!r}")
        if status == "not-computable":
            if m.get("budgetary_impact") is not None:
                problems.append(
                    f"measure {m['id']}: not computable but has a figure"
                )
            if not m.get("reason"):
                problems.append(f"measure {m['id']}: no reason given")
        if m.get("publish") and m.get("placeholder"):
            problems.append(f"measure {m['id']}: placeholder marked publish")
        if status == "published" and not m.get("publish"):
            problems.append(f"measure {m['id']}: published without sign-off")
        if not meta.get("placeholder") and m.get("placeholder"):
            problems.append(
                f"measure {m['id']}: placeholder in a non-placeholder file"
            )
    for cell in results.get("decile_impact", []):
        n = cell.get("n_records", 0)
        if n < meta.get("disclosure_floor", DISCLOSURE_FLOOR) and (
            cell.get("avg_change_gbp") is not None
        ):
            problems.append(
                f"decile cell {cell.get('measure_id')}/{cell.get('decile')}: "
                "below the disclosure floor"
            )
    if problems:
        raise PublicationError("; ".join(problems))


def manifest(results: dict) -> dict:
    """SHA-256 of the canonical results, for the G0/G5 clock table."""
    body = json.dumps(results, sort_keys=True, separators=(",", ":"))
    return {
        "sha256": hashlib.sha256(body.encode()).hexdigest(),
        "placeholder": bool(results.get("meta", {}).get("placeholder")),
        "measures": len(results.get("measures", [])),
    }
