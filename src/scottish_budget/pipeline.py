"""Generate results.json: placeholder figures now, model figures on the day.

``placeholder_results()`` builds the file the dashboard reads before the
Budget, from the registry and the presets, with illustrative numbers that
are flagged as placeholders at every level. ``model_results()`` runs the
measures cleared for publication through the engine (``national.py``).
"""

import hashlib
import json
from pathlib import Path

from scottish_budget import __version__
from scottish_budget.data_limits import blocking_limits
from scottish_budget.household import presets
from scottish_budget.publication import (
    DISCLOSURE_FLOOR,
    apply_floor,
    validate_results,
)
from scottish_budget.reforms import MEASURES, Measure, publishable
from scottish_budget.years import BASIS, POLICY_YEARS, fiscal_year_label

ENGINE = {
    "policyengine": "6.11.1",
    "policyengine_uk": "2.151.0",
    "dataset": "microcosm-uk-2024-25-national-20261025T091414Z-a6299504",
}


def _seed(*parts) -> int:
    digest = hashlib.sha256("/".join(map(str, parts)).encode()).hexdigest()
    return int(digest[:8], 16)


def _placeholder_amount(measure_id: str, year: int) -> float:
    """An illustrative £bn figure between -0.30 and +0.30, 2 decimals."""
    return round((_seed(measure_id, year) % 61 - 30) / 100, 2)


def _status(m: Measure) -> tuple[str, str | None]:
    blocking = blocking_limits(m.data_limits)
    if m.route == "not-computable" or blocking:
        reasons = [limit.reason for limit in blocking] or [m.basis_note]
        return "not-computable", " ".join(reasons)
    if m.route == "ledger":
        return "ledger", m.basis_note
    if m.route == "needs-pe-uk-first":
        return "pending", m.basis_note
    return "placeholder", None


def _measure_row(m: Measure) -> dict:
    status, reason = _status(m)
    figures = None
    if status == "placeholder":
        figures = [
            {
                "year": y,
                "label": fiscal_year_label(y),
                "value_bn": _placeholder_amount(m.id, y),
            }
            for y in POLICY_YEARS
        ]
    return {
        "id": m.id,
        "name": m.reform.name,
        "description": m.reform.description,
        "route": m.route,
        "cause": m.cause,
        "topic": m.topic,
        "likelihood": m.likelihood,
        "in_baseline": m.in_baseline,
        "calculator": m.calculator,
        "issues": list(m.issues),
        "status": status,
        "reason": reason,
        "basis_note": m.basis_note,
        "placeholder": m.placeholder,
        "publish": m.publish,
        "budgetary_impact": figures,
    }


def _decile_cells(rows: list[dict]) -> list[dict]:
    cells = []
    for row in rows:
        if row["status"] != "placeholder":
            continue
        for decile in range(1, 11):
            seed = _seed(row["id"], decile)
            cells.append(
                {
                    "measure_id": row["id"],
                    "decile": decile,
                    "avg_change_gbp": round((seed % 401 - 200) / 4, 2),
                    "pct_change": round((seed % 41 - 20) / 100, 2),
                    # Illustrative: decile 10 of the property measure sits
                    # below the floor to show a withheld cell.
                    "n_records": 6
                    if (decile == 10 and seed % 5 == 0)
                    else 700,
                }
            )
    return apply_floor(cells)


def _household_rows() -> list[dict]:
    rows = []
    for key, preset in presets().items():
        seed = _seed(key)
        base = 15_000 + seed % 50_000
        rows.append(
            {
                "id": key,
                "label": preset["label"],
                "baseline_net_income": base,
                "reform_net_income": base + (seed % 300) - 100,
                "rest_of_uk_net_income": base + (seed % 900) - 300,
            }
        )
    return rows


def placeholder_results() -> dict:
    rows = [_measure_row(m) for m in MEASURES]
    results = {
        "meta": {
            "status": "pre-release template",
            "placeholder": True,
            "notice": (
                "Pre-release template: placeholder figures. Not a costing "
                "of the Scottish Budget 2027-28."
            ),
            "generated_by": f"scottish_budget {__version__}",
            **ENGINE,
            "basis": BASIS,
            "years": [
                {"year": y, "label": fiscal_year_label(y)}
                for y in POLICY_YEARS
            ],
            "disclosure_floor": DISCLOSURE_FLOOR,
        },
        "measures": rows,
        "decile_impact": _decile_cells(rows),
        "households": _household_rows(),
    }
    validate_results(results)
    return results


def model_results() -> dict:
    """Run every publishable measure through the engine (the real day)."""
    cleared = publishable()
    if not cleared:
        raise RuntimeError(
            "No measure is cleared for publication: every registry entry "
            "is a placeholder. Use --placeholder for the template file."
        )
    from scottish_budget.national import run_measures

    results = run_measures(cleared)
    validate_results(results)
    return results


def write(results: dict, path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(results, indent=2, ensure_ascii=False) + "\n")
    return path
