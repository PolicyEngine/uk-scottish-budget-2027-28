"use client";

import { useEffect, useMemo, useState } from "react";
import { calculatorMeasures, chartedMeasures } from "../utils/calculatorOnlyMeasures";
import BudgetaryImpactChart from "./BudgetaryImpactChart";
import CouncilTaxBands from "./CouncilTaxBands";
import DistributionalChart from "./DistributionalChart";
import HouseholdCalculator from "./HouseholdCalculator";
import IncomeTaxCurve from "./IncomeTaxCurve";
import MethodologyTab from "./MethodologyTab";
import OfficialComparison from "./OfficialComparison";
import PolicyCards from "./PolicyCards";
import PolicySelector from "./PolicySelector";
import PovertyCard from "./PovertyCard";
import ScotlandVsRestOfUk from "./ScotlandVsRestOfUk";
import StatTiles from "./StatTiles";
import WinnersLosers from "./WinnersLosers";

export const REPO_URL = "https://github.com/PolicyEngine/uk-scottish-budget-2027-28";

// The tabs, as on the Autumn Budget 2026 dashboard. State lives in the
// address: ?tab=, ?sub=, ?year= and ?policies=.
export const SUBS = [
  { value: "finances", label: "Public finances" },
  { value: "households", label: "All households" },
  { value: "ruk", label: "Scotland and rest of UK" },
  { value: "poverty", label: "Poverty" },
  { value: "council_tax", label: "Council tax" },
];
export const VIEWS = [
  { value: "dashboard", label: "Population impact" },
  { value: "household", label: "Example households" },
  { value: "policies", label: "Policies" },
  { value: "methodology", label: "Methodology" },
];
const DEFAULT_VIEW = "dashboard";

function readAddress(charted, years) {
  const fallback = { tab: DEFAULT_VIEW, sub: "finances", year: years[0].year, policies: charted };
  if (typeof window === "undefined") return fallback;
  const params = new URLSearchParams(window.location.search);
  const tab = VIEWS.some((v) => v.value === params.get("tab")) ? params.get("tab") : DEFAULT_VIEW;
  const sub = SUBS.some((s) => s.value === params.get("sub")) ? params.get("sub") : "finances";
  const year = years.some((y) => String(y.year) === params.get("year")) ? Number(params.get("year")) : years[0].year;
  const listed = params.get("policies")?.split(",").filter((id) => charted.includes(id));
  return { tab, sub, year, policies: listed?.length ? listed : charted };
}

function YearPill({ years, year, onChange }) {
  return (
    <div className="year-pill" role="group" aria-label="Fiscal year">
      {years.map((y) => (
        <button key={y.year} type="button" aria-pressed={year === y.year} onClick={() => onChange(y.year)}>
          {y.label}
        </button>
      ))}
    </div>
  );
}

export default function Dashboard({ data }) {
  const { meta, measures } = data;
  const charted = useMemo(() => chartedMeasures(measures), [measures]);
  const chartedIds = useMemo(() => charted.map((m) => m.id), [charted]);
  const [state, setState] = useState(() => readAddress(chartedIds, meta.years));

  useEffect(() => {
    const params = new URLSearchParams();
    params.set("tab", state.tab);
    if (state.tab === "dashboard") params.set("sub", state.sub);
    if (state.year !== meta.years[0].year) params.set("year", String(state.year));
    if (state.policies.length !== chartedIds.length) params.set("policies", state.policies.join(","));
    window.history.replaceState(null, "", `${window.location.pathname}?${params}${window.location.hash}`);
  }, [state, chartedIds, meta.years]);

  const selected = charted.filter((m) => state.policies.includes(m.id));
  const set = (patch) => setState((s) => ({ ...s, ...patch }));
  const year = meta.years.find((y) => y.year === state.year) ?? meta.years[0];
  const openPolicy = (id) => {
    set({ tab: "policies" });
    window.setTimeout(() => document.getElementById(`policy-${id}`)?.scrollIntoView(), 0);
  };
  const openMethodology = (e) => {
    e.preventDefault();
    set({ tab: "methodology" });
  };

  return (
    <div className="app-shell min-h-screen">
      <div className="title-row">
        <div className="mx-auto flex max-w-[1200px] flex-wrap items-center justify-between gap-3 px-4 py-3 sm:px-6">
          <h1>Scottish Budget 2027-28</h1>
          <YearPill years={meta.years} year={state.year} onChange={(y) => set({ year: y })} />
        </div>
      </div>
      <main className="relative z-[1] mx-auto max-w-[1200px] space-y-6 px-4 py-8 sm:px-6">
        <nav role="tablist" aria-label="Views" className="flex flex-wrap border-b border-slate-200">
          {VIEWS.map((v) => (
            <button
              key={v.value}
              type="button"
              role="tab"
              id={`tab-${v.value}`}
              aria-selected={state.tab === v.value}
              aria-controls={`panel-${v.value}`}
              className={`tab-button${state.tab === v.value ? " active" : ""}`}
              onClick={() => set({ tab: v.value })}
            >
              {v.label}
            </button>
          ))}
        </nav>

        <div role="tabpanel" id={`panel-${state.tab}`} aria-labelledby={`tab-${state.tab}`} className="tab-body space-y-6">
          {state.tab === "dashboard" && (
            <>
              <PolicySelector measures={charted} selected={state.policies} onChange={(policies) => set({ policies })} />
              <StatTiles
                measures={selected}
                year={year}
                versus={data.scotland_vs_rest_of_uk ?? []}
                poverty={data.poverty ?? []}
                placeholder={meta.placeholder}
              />
              <div role="tablist" aria-label="Population impact" className="flex flex-wrap gap-2">
                {SUBS.map((s) => (
                  <button
                    key={s.value}
                    type="button"
                    role="tab"
                    id={`sub-${s.value}`}
                    aria-selected={state.sub === s.value}
                    aria-controls={`subpanel-${s.value}`}
                    className={`tab-button sub-tab-button${state.sub === s.value ? " active" : ""}`}
                    onClick={() => set({ sub: s.value })}
                  >
                    {s.label}
                  </button>
                ))}
              </div>
              <div role="tabpanel" id={`subpanel-${state.sub}`} aria-labelledby={`sub-${state.sub}`} className="space-y-6">
                {state.sub === "finances" && (
                  <>
                    <BudgetaryImpactChart measures={selected} years={meta.years} placeholder={meta.placeholder} />
                    <OfficialComparison measures={measures} costings={data.official_costings ?? []} year={year.year} />
                  </>
                )}
                {state.sub === "households" && (
                  <>
                    <DistributionalChart
                      cells={data.decile_impact}
                      selectedIds={selected.map((m) => m.id)}
                      year={year.year}
                      yearLabel={year.label}
                      placeholder={meta.placeholder}
                    />
                    <WinnersLosers rows={data.winners_losers ?? []} year={year.year} />
                  </>
                )}
                {state.sub === "ruk" && (
                  <>
                    <ScotlandVsRestOfUk rows={data.scotland_vs_rest_of_uk ?? []} year={year.year} />
                    <IncomeTaxCurve rows={data.income_tax_curve ?? []} yearLabel={meta.years[0].label} />
                  </>
                )}
                {state.sub === "poverty" && <PovertyCard rows={data.poverty ?? []} year={year.year} />}
                {state.sub === "council_tax" && <CouncilTaxBands cells={data.council_tax_bands ?? []} year={year.year} />}
              </div>
              <p className="text-sm text-slate-600">
                Basis and data: see the{" "}
                <a href="?tab=methodology" onClick={openMethodology} data-testid="methodology-link">
                  Methodology
                </a>{" "}
                tab.
              </p>
            </>
          )}
          {state.tab === "household" && (
            <HouseholdCalculator
              households={data.households}
              measures={calculatorMeasures(measures)}
              placeholder={meta.placeholder}
              yearLabel={meta.years[0].label}
            />
          )}
          {state.tab === "policies" && <PolicyCards measures={measures} repoUrl={REPO_URL} years={meta.years} />}
          {state.tab === "methodology" && (
            <MethodologyTab meta={meta} measures={measures} repoUrl={REPO_URL} onOpenPolicy={openPolicy} />
          )}
        </div>
      </main>
    </div>
  );
}
