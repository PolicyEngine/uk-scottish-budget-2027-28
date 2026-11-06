"""Population results for Scotland from the engine, one measure per run.

This loads Microcosm and builds simulations, so it follows the heavy-run
rules in docs/RUNBOOK.md: take the lock, check free memory, and run one
measure per process (``scottish-budget generate --reforms ID``). Within a
run the baseline is built, read and released before the reform is built,
so only one simulation is held at a time.

Each run writes a partial file; ``scottish-budget combine`` merges the
partials into results.json. The arithmetic (``summarise``) is pure numpy
and is tested on synthetic arrays; the engine is never imported by tests.

Distributional basis: Scottish deciles of equivalised household net income,
ranked within Scotland and weighted by people (household weight times
household size), as the Scottish Government's distributional analysis
ranks them. Budgetary impact is static: minus the weighted change in
Scottish household net income.
"""

import gc

import numpy as np

from scottish_budget.engine import build_microsimulation, simulation_provenance
from scottish_budget.publication import DISCLOSURE_FLOOR, apply_floor
from scottish_budget.years import POLICY_YEARS, fiscal_year_label

HOUSEHOLD_VARIABLES = (
    "household_net_income",
    "equiv_household_net_income",
    "household_count_people",
)
PERSON_VARIABLES = ("is_child",)
POVERTY_VARIABLES = ("in_poverty_bhc", "in_poverty_ahc")
# A household gains or loses if its net income moves by more than this.
CHANGE_THRESHOLD_GBP = 1.0


def _read(sim, years) -> dict:
    """The arrays a measure's results need, per year, for Scotland."""
    out = {}
    for year in years:
        country = sim.calculate("country", year, map_to="household").values
        person_country = sim.calculate("country", year, map_to="person").values
        frame = {
            "in_scotland": country == "SCOTLAND",
            "person_in_scotland": person_country == "SCOTLAND",
            "household_weight": sim.calculate(
                "household_weight", year, map_to="household"
            ).values,
            "person_weight": sim.calculate(
                "person_weight", year, map_to="person"
            ).values,
        }
        for name in HOUSEHOLD_VARIABLES:
            frame[name] = sim.calculate(name, year, map_to="household").values
        for name in PERSON_VARIABLES:
            frame[name] = sim.calculate(name, year, map_to="person").values
        for name in POVERTY_VARIABLES:
            frame[name] = sim.calculate(name, year, map_to="person").values
        out[year] = frame
    return out


def scottish_deciles(income, weight) -> np.ndarray:
    """Decile (1 to 10) of each record, by weighted rank of ``income``."""
    income = np.asarray(income, dtype=float)
    weight = np.asarray(weight, dtype=float)
    order = np.argsort(income, kind="stable")
    cumulative = np.cumsum(weight[order])
    total = cumulative[-1] if len(cumulative) else 0.0
    if total <= 0:
        return np.ones(len(income), dtype=int)
    ranks = np.empty(len(income), dtype=int)
    # The decile a record falls in is set by the weight below its midpoint.
    midpoint = (cumulative - weight[order] / 2) / total
    ranks[order] = np.minimum(np.floor(midpoint * 10).astype(int) + 1, 10)
    return ranks


def summarise(measure_id: str, base: dict, reform: dict) -> dict:
    """Costs, decile cells, winners and losers, child poverty."""
    figures, cells, winners, poverty = [], [], [], []
    for year in POLICY_YEARS:
        b, r = base[year], reform[year]
        scot = b["in_scotland"]
        w = b["household_weight"][scot]
        change = (r["household_net_income"] - b["household_net_income"])[scot]
        figures.append(
            {
                "year": year,
                "label": fiscal_year_label(year),
                "value_bn": round(-float((change * w).sum()) / 1e9, 3),
            }
        )
        people_w = w * b["household_count_people"][scot]
        decile = scottish_deciles(
            b["equiv_household_net_income"][scot], people_w
        )
        net = b["household_net_income"][scot]
        for d in range(1, 11):
            mask = decile == d
            wd = w[mask]
            total_w = wd.sum()
            avg = (
                float((change[mask] * wd).sum() / total_w) if total_w else 0.0
            )
            base_total = float((net[mask] * wd).sum())
            pct = (
                100 * float((change[mask] * wd).sum()) / base_total
                if base_total
                else None
            )
            cells.append(
                {
                    "measure_id": measure_id,
                    "year": year,
                    "decile": d,
                    "avg_change_gbp": round(avg, 2),
                    "pct_change": None if pct is None else round(pct, 3),
                    "n_records": int(mask.sum()),
                }
            )
        gain = change > CHANGE_THRESHOLD_GBP
        lose = change < -CHANGE_THRESHOLD_GBP
        winners.append(
            {
                "measure_id": measure_id,
                "year": year,
                "gain_share": round(
                    float(people_w[gain].sum() / people_w.sum()), 4
                ),
                "lose_share": round(
                    float(people_w[lose].sum() / people_w.sum()), 4
                ),
                "n_records": int(scot.sum()),
            }
        )
        pscot = b["person_in_scotland"]
        child = pscot & b["is_child"].astype(bool)
        pw = b["person_weight"]
        for basis, name in (
            ("bhc", "in_poverty_bhc"),
            ("ahc", "in_poverty_ahc"),
        ):
            before = float((b[name][child] * pw[child]).sum())
            after = float((r[name][child] * pw[child]).sum())
            children = float(pw[child].sum())
            poverty.append(
                {
                    "measure_id": measure_id,
                    "year": year,
                    "group": "children",
                    "basis": basis,
                    "baseline_rate": round(before / children, 4),
                    "reform_rate": round(after / children, 4),
                    "change_count": round(after - before),
                    "n_records": int(child.sum()),
                }
            )
    return {
        "measure_id": measure_id,
        "budgetary_impact": figures,
        "decile_impact": apply_floor(cells, DISCLOSURE_FLOOR),
        "winners_losers": winners,
        "poverty": poverty,
    }


def run_measure(measure, dataset_path=None) -> dict:
    """One measure against its baseline (custom if the measure has one)."""
    reform = measure.reform
    baseline_scenario = (
        reform.to_baseline_scenario() if reform.has_custom_baseline() else None
    )
    sim = build_microsimulation(dataset_path, baseline_scenario)
    provenance = simulation_provenance(sim)
    base = _read(sim, POLICY_YEARS)
    del sim
    gc.collect()
    reform_scenario = reform.to_scenario()
    if baseline_scenario is not None:
        # The reform is scored against the custom baseline, so it runs on
        # top of it.
        reform_scenario = baseline_scenario + reform_scenario
    sim = build_microsimulation(dataset_path, reform_scenario)
    changed = _read(sim, POLICY_YEARS)
    del sim
    gc.collect()
    out = summarise(measure.id, base, changed)
    out["provenance"] = provenance
    out["custom_baseline"] = baseline_scenario is not None
    return out
