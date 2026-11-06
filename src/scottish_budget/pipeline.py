"""Generate results.json: placeholder figures now, model figures on the day.

``placeholder_results()`` builds the file the dashboard reads before the
Budget, from the registry, with illustrative numbers that are flagged as
placeholders at every level.

On the day, each measure is run in its own process
(``scottish-budget generate --reforms ID``, which calls ``run_one``) and
writes a partial file; ``combine()`` merges the partials with the registry
rows, the meta block and the example households into results.json, and
writes a receipt beside it.

- ``combine(provisional=True)`` (G2): every computed measure with
  ``placeholder=False`` gets its figures, with status ``provisional``.
- ``combine()`` (G4): only measures signed off (``publish=True``) get
  figures, with status ``published``; computed but unsigned measures are
  listed as ``provisional`` with no figures.
"""

import datetime as dt
import hashlib
import json
from pathlib import Path

from scottish_budget import __version__
from scottish_budget.data_limits import blocking_limits
from scottish_budget.engine import (
    bundle_dataset,
    git_identity,
    installed_versions,
)
from scottish_budget.forecast import forecast_record
from scottish_budget.household import presets
from scottish_budget.publication import (
    DISCLOSURE_FLOOR,
    apply_floor,
    manifest,
    validate_results,
)
from scottish_budget.reforms import MEASURES, Measure, measure
from scottish_budget.years import BASIS, POLICY_YEARS, fiscal_year_label

ROOT = Path(__file__).resolve().parents[2]
PARTIAL_DIR = ROOT / "data_outputs" / "partials"

# The certified pair in the lock file, for the placeholder file only. A
# model run records what is installed (``installed_versions``) and what the
# simulation loaded (the partials' provenance). tests/test_provenance.py
# checks these against uv.lock.
LOCKED_ENGINE = {
    "policyengine": "6.14.0",
    "policyengine_uk": "2.151.0",
    "dataset": "microcosm-uk-2024-25-national-20261025T091414Z-a6299504",
}

ROUTE_LABELS = {
    "dashboard-param": "Modelled",
    "dashboard-structural": "Modelled",
    "ledger": "Recorded, not modelled",
    "not-computable": "Not computable",
    "needs-pe-uk-first": "Needs a model change first",
}


class CombineError(RuntimeError):
    pass


def _seed(*parts) -> int:
    digest = hashlib.sha256("/".join(map(str, parts)).encode()).hexdigest()
    return int(digest[:8], 16)


def _placeholder_amount(m: Measure, year: int) -> float:
    """An illustrative £bn figure of the measure's own sign, 0.01 to 0.30."""
    size = (_seed(m.id, year) % 30 + 1) / 100
    return round(m.placeholder_sign * size, 2)


def _status(m: Measure) -> tuple[str, str | None]:
    blocking = blocking_limits(m.data_limits)
    if m.route == "not-computable" or blocking:
        reasons = [limit.reason for limit in blocking] or [m.basis_note]
        return "not-computable", " ".join(reasons)
    if m.route == "ledger":
        return "ledger", None
    if m.route == "needs-pe-uk-first":
        return "pending", "The model cannot represent this measure yet."
    if m.placeholder:
        return "placeholder", None
    return "provisional", None


def _measure_row(m: Measure) -> dict:
    status, reason = _status(m)
    figures = None
    if status == "placeholder":
        figures = [
            {
                "year": y,
                "label": fiscal_year_label(y),
                "value_bn": _placeholder_amount(m, y),
            }
            for y in POLICY_YEARS
        ]
    note = m.basis_note if m.basis_note and m.basis_note != reason else None
    return {
        "id": m.id,
        "name": m.reform.name,
        "description": m.reform.description,
        "route": m.route,
        "route_label": ROUTE_LABELS[m.route],
        "cause": m.cause,
        "topic": m.topic,
        "likelihood": m.likelihood,
        "in_baseline": m.in_baseline,
        "calculator": m.calculator,
        "issues": list(m.issues),
        "status": status,
        "reason": reason,
        "basis_note": note,
        "first_year": m.first_year,
        "placeholder": m.placeholder,
        "publish": m.publish,
        "budgetary_impact": figures,
    }


def _placeholder_cells(rows: list[dict]) -> list[dict]:
    cells = []
    for row in rows:
        if row["status"] != "placeholder":
            continue
        sign = measure(row["id"]).placeholder_sign or 1
        for year in POLICY_YEARS:
            for decile in range(1, 11):
                seed = _seed(row["id"], year, decile)
                # A household's gain is the government's cost.
                gain = -sign * (seed % 200 + 1) / 4
                cells.append(
                    {
                        "measure_id": row["id"],
                        "year": year,
                        "decile": decile,
                        "avg_change_gbp": round(gain, 2),
                        "pct_change": round(gain / 400, 3),
                        # Illustrative: some top-decile cells sit below the
                        # floor to show a withheld cell.
                        "n_records": 6
                        if (decile == 10 and seed % 5 == 0)
                        else 700,
                    }
                )
    return apply_floor(cells)


def _placeholder_households() -> list[dict]:
    """Preset labels only: every value is null until the model runs."""
    return [
        {
            "id": key,
            "label": preset["label"],
            "year": preset["year"],
            "baseline_net_income": None,
            "reform_net_income": None,
            "change": None,
            "rest_of_uk_net_income": None,
            "scotland_minus_rest_of_uk": None,
        }
        for key, preset in presets().items()
    ]


def _years_meta() -> list[dict]:
    return [{"year": y, "label": fiscal_year_label(y)} for y in POLICY_YEARS]


def _forecast_meta() -> dict:
    record = forecast_record()
    return {"vintage": record["vintage"], "source_url": record["source_url"]}


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
            **LOCKED_ENGINE,
            "dataset_sha256": None,
            "forecast": _forecast_meta(),
            "basis": BASIS,
            "years": _years_meta(),
            "disclosure_floor": DISCLOSURE_FLOOR,
        },
        "measures": rows,
        "decile_impact": _placeholder_cells(rows),
        "winners_losers": [],
        "poverty": [],
        "council_tax_bands": [],
        "scotland_vs_rest_of_uk": [],
        "official_costings": [],
        "households": _placeholder_households(),
        "income_tax_curve": [],
    }
    validate_results(results)
    return results


# --- The day: one measure per process, then combine ------------------------


def run_one(measure_id: str, dataset_path=None, out_dir=PARTIAL_DIR) -> Path:
    """Run one measure through the engine and write its partial file."""
    from scottish_budget.national import run_measure

    m = measure(measure_id)
    if m.placeholder:
        raise CombineError(
            f"{measure_id} is still a placeholder: set its values from the "
            "statement and placeholder=False first (G1)."
        )
    partial = run_measure(m, dataset_path)
    partial["versions"] = installed_versions()
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"{measure_id}.json"
    path.write_text(json.dumps(partial, indent=2) + "\n")
    return path


PACKAGE_ID = "package"
OFFICIAL_COSTINGS = (
    ROOT / "data_inputs" / "official" / "sfc_costings_2027_28.csv"
)


def package_measures(provisional: bool) -> list[Measure]:
    """The measures the package run covers: every computable measure for
    G2, the signed-off ones for the final file."""
    from scottish_budget.reforms import computable

    return [m for m in computable() if provisional or m.publish]


def run_package(
    provisional: bool, dataset_path=None, out_dir=PARTIAL_DIR
) -> Path:
    """All the package's measures together (heavy: one process)."""
    from scottish_budget.national import run_package as engine_package

    measures = package_measures(provisional)
    if not measures:
        raise CombineError("No measure to run as a package.")
    partial = engine_package(measures, dataset_path)
    partial["versions"] = installed_versions()
    partial["provisional"] = provisional
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"{PACKAGE_ID}.json"
    path.write_text(json.dumps(partial, indent=2) + "\n")
    return path


def official_costings(path=OFFICIAL_COSTINGS) -> list[dict]:
    """The official costings, once filled in on the day (G3)."""
    if not Path(path).exists():
        return []
    from scottish_budget.reconcile import read_official

    return [
        {
            "measure_id": row["measure_id"],
            "year": int(row["year"]),
            "official_value_bn": float(row["official_value_bn"])
            if row.get("official_value_bn")
            else None,
            "source": row.get("official_source", ""),
            "basis": row.get("basis", ""),
        }
        for row in read_official(path)
    ]


def read_partials(out_dir=PARTIAL_DIR) -> dict[str, dict]:
    partials = {}
    for path in sorted(Path(out_dir).glob("*.json")):
        partial = json.loads(path.read_text())
        partials[partial["measure_id"]] = partial
    return partials


def _engine_meta(partials: dict[str, dict]) -> dict:
    """One engine and data pair for every partial, or refuse."""
    pairs = {
        (
            json.dumps(p.get("versions"), sort_keys=True),
            (p.get("provenance") or {}).get("runtime_dataset_sha256"),
            (p.get("provenance") or {}).get("runtime_dataset"),
        )
        for p in partials.values()
    }
    if len(pairs) != 1:
        raise CombineError(
            "The partials were built on different engine or data pairs; "
            "re-run them on the pair recorded at G0."
        )
    versions_json, sha, name = pairs.pop()
    versions = json.loads(versions_json) or {}
    provenance = next(iter(partials.values())).get("provenance") or {}
    return {
        "policyengine": versions.get("policyengine"),
        "policyengine_uk": versions.get("policyengine-uk"),
        "policyengine_core": versions.get("policyengine-core"),
        "dataset": provenance.get("runtime_dataset_revision") or name,
        "dataset_sha256": sha,
    }


def household_rows(measures, calculate=None) -> list[dict]:
    """Each preset and its rest-of-UK twin, current law and with the
    measures (``household.calculate``; injectable for tests)."""
    from scottish_budget.household import calculate as engine_calculate
    from scottish_budget.household import rest_of_uk_twin

    calculate = calculate or engine_calculate
    reforms = [m.reform for m in measures if m.calculator]
    rows = []
    for key, preset in presets().items():
        year = preset["year"]
        situation = preset["situation"]
        twin = rest_of_uk_twin(situation, year)
        base = calculate(situation, year)["household_net_income"]
        new = calculate(situation, year, reforms)["household_net_income"]
        twin_new = calculate(twin, year, reforms)["household_net_income"]
        rows.append(
            {
                "id": key,
                "label": preset["label"],
                "year": year,
                "baseline_net_income": round(base, 2),
                "reform_net_income": round(new, 2),
                "change": round(new - base, 2),
                "rest_of_uk_net_income": round(twin_new, 2),
                "scotland_minus_rest_of_uk": round(new - twin_new, 2),
            }
        )
    return rows


def income_tax_curve_rows(measures, curve=None) -> list[dict]:
    """Income tax by gross earnings for the Budget year (injectable)."""
    from scottish_budget.household import income_tax_curve
    from scottish_budget.years import BUDGET_YEAR

    curve = curve or income_tax_curve
    return curve(BUDGET_YEAR, [m.reform for m in measures])


def combine(
    provisional: bool = False,
    out_dir=PARTIAL_DIR,
    calculate=None,
    with_households: bool = True,
    curve=None,
) -> tuple[dict, dict]:
    """results.json and its receipt from the partials and the registry."""
    partials = read_partials(out_dir)
    if not partials:
        raise CombineError(
            f"No partial files in {out_dir}: run "
            "`scottish-budget generate --reforms ID` for each measure first."
        )
    package = partials.pop(PACKAGE_ID, None)
    unknown = sorted(set(partials) - {m.id for m in MEASURES})
    if unknown:
        raise CombineError(
            f"Partials for measures not in the registry: {unknown}"
        )
    dropped = [m.id for m in MEASURES if m.placeholder]
    kept = [m for m in MEASURES if not m.placeholder]
    rows, cells, winners, poverty, scored = [], [], [], [], []
    for m in kept:
        row = _measure_row(m)
        partial = partials.get(m.id)
        if row["status"] == "provisional":
            if partial is None:
                raise CombineError(
                    f"{m.id} is computable but has no partial: run it first."
                )
            signed = m.publish
            if signed and not provisional:
                row["status"] = "published"
            if signed or provisional:
                row["budgetary_impact"] = partial["budgetary_impact"]
                cells += partial["decile_impact"]
                scored.append(m)
            else:
                row["reason"] = "Awaiting sign-off after reconciliation."
        rows.append(row)
    bands, versus = [], []
    if package is not None:
        if sorted(package.get("measures", [])) != sorted(m.id for m in scored):
            raise CombineError(
                "The package run covers other measures than this file: "
                "re-run `scottish-budget generate --package`."
            )
        # Winners and losers, poverty and the rest do not add up across
        # measures, so they come from the package run only.
        winners = package["winners_losers"]
        poverty = package["poverty"]
        bands = package.get("council_tax_bands", [])
        versus = package.get("scotland_vs_rest_of_uk", [])
    engine = _engine_meta(
        {**partials, **({PACKAGE_ID: package} if package else {})}
    )
    status = "provisional" if provisional else "published"
    results = {
        "meta": {
            "status": status,
            "placeholder": False,
            "notice": (
                "Provisional figures, not signed off."
                if provisional
                else "PolicyEngine estimates of the Scottish Budget 2027-28."
            ),
            "generated_by": f"scottish_budget {__version__}",
            **engine,
            "forecast": _forecast_meta(),
            "basis": BASIS,
            "years": _years_meta(),
            "disclosure_floor": DISCLOSURE_FLOOR,
        },
        "measures": rows,
        "decile_impact": cells,
        "winners_losers": winners,
        "poverty": poverty,
        "council_tax_bands": bands,
        "scotland_vs_rest_of_uk": versus,
        "official_costings": official_costings(),
        "households": (
            household_rows(scored, calculate) if with_households else []
        ),
        "income_tax_curve": (
            income_tax_curve_rows(scored, curve) if with_households else []
        ),
    }
    validate_results(results)
    receipt = {
        "package_run": package is not None,
        **git_identity(),
        "generated_at": dt.datetime.now(dt.UTC).isoformat(timespec="seconds"),
        "versions": installed_versions(),
        "bundle_dataset": bundle_dataset(),
        "dataset": engine["dataset"],
        "dataset_sha256": engine["dataset_sha256"],
        "measures_scored": [m.id for m in scored],
        "placeholders_dropped": dropped,
        "results_sha256": manifest(results)["sha256"],
    }
    return results, receipt


def write(results: dict, path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(results, indent=2, ensure_ascii=False) + "\n")
    return path
