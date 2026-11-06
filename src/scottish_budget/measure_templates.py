"""Builders for parameter changes (scaled down from the Autumn Budget repo).

Each builder takes explicit annual values keyed by four-digit years and
returns ``{path: {"2027": value, ...}}``. ISO dates are refused: a lone date
changes one day, not a year. For an uprated amount, supply every scored
year from the first changed year, since a bounded change returns to the
old path afterwards.

A measure built only from these templates needs no hand-written modifier.
Anything else goes in ``measures/`` as one module per modifier, with
literal defaults and no runtime state.
"""

import math
import re
from collections.abc import Mapping
from decimal import ROUND_HALF_UP, Decimal

_YEAR = re.compile(r"[1-9][0-9]{3}")
_PATH = re.compile(r"[a-z][a-z0-9_]*(\[[0-9]+\])?(\.[a-z0-9_]+(\[[0-9]+\])?)+")


def _validate_path(path: str) -> None:
    if not isinstance(path, str) or not _PATH.fullmatch(path):
        raise ValueError(f"Not a parameter path: {path!r}")
    if not path.startswith("gov."):
        raise ValueError(f"Parameter paths start with 'gov.': {path!r}")


def _annual(values: Mapping, *, numeric: bool = True) -> dict[str, object]:
    if not isinstance(values, Mapping) or not values:
        raise ValueError("Supply at least one explicit annual value")
    out: dict[str, object] = {}
    for year, value in values.items():
        if isinstance(year, bool) or not _YEAR.fullmatch(str(year)):
            raise ValueError(
                "Use four-digit annual keys; a lone ISO date changes one day"
            )
        key = str(year)
        if key in out:
            raise ValueError(f"Duplicate annual value for {key}")
        if numeric:
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                raise ValueError(f"Value for {key} must be a number")
            if not math.isfinite(float(value)):
                raise ValueError(f"Value for {key} must be finite")
            out[key] = float(value)
        else:
            if not isinstance(value, bool):
                raise ValueError(f"Value for {key} must be True or False")
            out[key] = value
    return dict(sorted(out.items()))


def rate_change(path: str, values: Mapping) -> dict[str, dict[str, float]]:
    """Explicit annual rates (as decimals, 0.21 for 21%)."""
    _validate_path(path)
    annual = _annual(values)
    if any(not 0 <= v <= 1 for v in annual.values()):
        raise ValueError("A rate is a decimal between 0 and 1")
    return {path: annual}


def threshold_change(
    path: str, values: Mapping
) -> dict[str, dict[str, float]]:
    """Explicit annual thresholds or amounts in the parameter's own units."""
    _validate_path(path)
    annual = _annual(values)
    if any(v < 0 for v in annual.values()):
        raise ValueError("A threshold or amount is not negative")
    return {path: annual}


def switch_change(path: str, values: Mapping) -> dict[str, dict[str, bool]]:
    """Explicit annual True/False for an ``in_effect`` style switch."""
    _validate_path(path)
    return {path: _annual(values, numeric=False)}


def nearest_5p_weekly(amount: float) -> float:
    """Round a weekly amount to the nearest 5p, halves rounded up.

    Scottish benefits are uprated and then rounded; the drill retros lost
    rows to statutory rounding, so apply it explicitly where it applies.
    """
    value = Decimal(str(amount))
    if not value.is_finite() or value < 0:
        raise ValueError("Weekly amount must be a non-negative number")
    step = Decimal("0.05")
    return float((value / step).to_integral_value(ROUND_HALF_UP) * step)


TEMPLATES = (
    "rate_change",
    "threshold_change",
    "switch_change",
    "nearest_5p_weekly",
)
