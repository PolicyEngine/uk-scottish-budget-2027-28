"""Population results for Scotland from the engine (used on the day only).

NOT YET RUN AGAINST DATA. This loads Microcosm and builds simulations, so
it follows the heavy-run rules in docs/RUNBOOK.md (one heavy job at a
time; take the lock first). The tests never import it.
"""

from scottish_budget.publication import DISCLOSURE_FLOOR, apply_floor
from scottish_budget.years import POLICY_YEARS, fiscal_year_label


def _scotland(sim, year):
    country = sim.calculate("country", year, map_to="household")
    return country.values == "SCOTLAND"


def run_measures(measures, dataset=None) -> dict:
    from policyengine_uk import Microsimulation

    kwargs = {"dataset": dataset} if dataset is not None else {}
    baseline = Microsimulation(**kwargs)
    rows, cells = [], []
    for m in measures:
        reform = Microsimulation(scenario=m.reform.to_scenario(), **kwargs)
        figures, changes = [], {}
        for year in POLICY_YEARS:
            in_scot = _scotland(baseline, year)
            base = baseline.calculate(
                "household_net_income", year, map_to="household"
            )
            new = reform.calculate(
                "household_net_income", year, map_to="household"
            )
            change = (new - base)[in_scot]
            changes[year] = (change, in_scot)
            # Cost to government is the household gain, on a static basis.
            figures.append(
                {
                    "year": year,
                    "label": fiscal_year_label(year),
                    "value_bn": round(-float(change.sum()) / 1e9, 3),
                }
            )
        first = POLICY_YEARS[0]
        change, in_scot = changes[first]
        decile = baseline.calculate(
            "household_income_decile", first, map_to="household"
        )[in_scot]
        for d in range(1, 11):
            mask = decile.values == d
            cells.append(
                {
                    "measure_id": m.id,
                    "decile": d,
                    "avg_change_gbp": round(float(change[mask].mean()), 2),
                    "pct_change": None,
                    "n_records": int(mask.sum()),
                }
            )
        rows.append({"id": m.id, "budgetary_impact": figures})
    return {
        "measures": rows,
        "decile_impact": apply_floor(cells, DISCLOSURE_FLOOR),
    }
