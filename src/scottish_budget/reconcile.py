"""G3: join our figures to the official costings and flag the gaps.

The official file is a CSV with one row per measure and fiscal year:
``measure_id, year, official_value_bn, official_source, basis, reason,
cause``. ``year`` is the first calendar year of the fiscal year (2027 for
2027-28). Values are £bn, negative a cost, on the official basis.

Every row must name a registry measure and a policy year, or the command
fails. A gap over ``THRESHOLD`` (10%) needs a written reason and a cause
class; rows that lack one are flagged and the command exits non-zero, so
G3 is not passed until every flagged gap has a reason.

Cause guidance (docs/RUNBOOK.md, "Gap reasons at G3"): a gap against a
costing that includes behaviour, or a grant to councils, is ``basis``;
take-up or caseload (``data_calibration``) applies only where the costing
has no behaviour in it.
"""

import csv
from pathlib import Path

from scottish_budget.reforms import CAUSES, MEASURES
from scottish_budget.years import POLICY_YEARS

THRESHOLD = 0.10
COLUMNS = (
    "measure_id",
    "year",
    "official_value_bn",
    "official_source",
    "basis",
    "reason",
    "cause",
)
OUT_COLUMNS = (
    "measure_id",
    "year",
    "our_value_bn",
    "official_value_bn",
    "gap_bn",
    "gap_pct",
    "basis",
    "reason",
    "cause",
    "flag",
)


class ReconcileError(ValueError):
    pass


def read_official(path) -> list[dict]:
    with open(path, newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    known = {m.id for m in MEASURES}
    problems = []
    for i, row in enumerate(rows, start=2):
        if row.get("measure_id") not in known:
            problems.append(
                f"line {i}: unknown measure {row.get('measure_id')!r}"
            )
        try:
            year = int(row.get("year", ""))
        except ValueError:
            year = None
        if year not in POLICY_YEARS:
            problems.append(
                f"line {i}: year {row.get('year')!r} not a policy year"
            )
        cause = (row.get("cause") or "").strip()
        if cause and cause not in CAUSES:
            problems.append(f"line {i}: unknown cause {cause!r}")
    if problems:
        raise ReconcileError("; ".join(problems))
    return rows


def _ours(results: dict) -> dict[tuple[str, int], float]:
    out = {}
    for m in results.get("measures", []):
        for f in m.get("budgetary_impact") or []:
            out[(m["id"], f["year"])] = f["value_bn"]
    return out


def reconcile(results: dict, official: list[dict]) -> list[dict]:
    ours = _ours(results)
    rows = []
    for row in official:
        key = (row["measure_id"], int(row["year"]))
        our = ours.get(key)
        value = row.get("official_value_bn", "").strip()
        theirs = float(value) if value else None
        gap = gap_pct = None
        flag = ""
        if our is None or theirs is None:
            flag = "no figure to compare"
        else:
            gap = round(our - theirs, 3)
            if theirs:
                gap_pct = round(100 * gap / abs(theirs), 1)
            big = (
                abs(gap) > THRESHOLD * abs(theirs) if theirs else abs(gap) > 0
            )
            if big and not (row.get("reason") and row.get("cause")):
                flag = "gap over 10% without a reason and cause"
        rows.append(
            {
                "measure_id": key[0],
                "year": key[1],
                "our_value_bn": our,
                "official_value_bn": theirs,
                "gap_bn": gap,
                "gap_pct": gap_pct,
                "basis": row.get("basis", ""),
                "reason": row.get("reason", ""),
                "cause": row.get("cause", ""),
                "flag": flag,
            }
        )
    return rows


def write_rows(rows: list[dict], path) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=OUT_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)
    return path


def unreasoned(rows: list[dict]) -> list[dict]:
    return [r for r in rows if r["flag"].startswith("gap over")]
