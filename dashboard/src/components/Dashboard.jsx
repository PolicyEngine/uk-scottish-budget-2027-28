"use client";

import { useEffect, useMemo, useState } from "react";
import { calculatorMeasures, chartedMeasures } from "../utils/calculatorOnlyMeasures";
import BudgetaryImpactChart from "./BudgetaryImpactChart";
import DistributionalChart from "./DistributionalChart";
import HouseholdCalculator from "./HouseholdCalculator";
import MethodologyTab from "./MethodologyTab";
import PolicyCards from "./PolicyCards";
import PolicySelector from "./PolicySelector";
import StatTiles from "./StatTiles";

export const REPO_URL = "https://github.com/PolicyEngine/uk-scottish-budget-2027-28";

// The tabs, as on the Autumn Budget 2026 dashboard. State lives in the
// address: ?tab=, ?sub= and ?policies=.
export const VIEWS = [
  { value: "dashboard", label: "Population impact", subs: ["finances", "deciles"] },
  { value: "household", label: "Household calculator" },
  { value: "policies", label: "Policies" },
  { value: "methodology", label: "Methodology" },
];
const SUB_LABELS = { finances: "Public finances", deciles: "Income deciles" };
const DEFAULT_VIEW = "dashboard";

function readAddress(charted) {
  if (typeof window === "undefined") return { tab: DEFAULT_VIEW, sub: "finances", policies: charted };
  const params = new URLSearchParams(window.location.search);
  const tab = VIEWS.some((v) => v.value === params.get("tab")) ? params.get("tab") : DEFAULT_VIEW;
  const sub = SUB_LABELS[params.get("sub")] ? params.get("sub") : "finances";
  const listed = params.get("policies")?.split(",").filter((id) => charted.includes(id));
  return { tab, sub, policies: listed?.length ? listed : charted };
}

export default function Dashboard({ data }) {
  const { meta, measures } = data;
  const charted = useMemo(() => chartedMeasures(measures), [measures]);
  const chartedIds = useMemo(() => charted.map((m) => m.id), [charted]);
  const [state, setState] = useState(() => readAddress(chartedIds));

  useEffect(() => {
    const params = new URLSearchParams();
    params.set("tab", state.tab);
    if (state.tab === "dashboard") params.set("sub", state.sub);
    if (state.policies.length !== chartedIds.length) params.set("policies", state.policies.join(","));
    window.history.replaceState(null, "", `${window.location.pathname}?${params}`);
  }, [state, chartedIds]);

  const selected = charted.filter((m) => state.policies.includes(m.id));
  const set = (patch) => setState((s) => ({ ...s, ...patch }));

  return (
    <div className="app-shell min-h-screen">
      <div className="title-row">
        <div className="mx-auto max-w-[1200px] px-6 py-3">
          <h1>Scottish Budget 2027-28</h1>
        </div>
      </div>
      <main className="relative z-[1] mx-auto max-w-[1200px] space-y-6 px-6 py-8">
        <p className="note-card rounded-xl p-4 text-sm" data-testid="placeholder-note">
          {meta.notice}
        </p>
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
              <StatTiles measures={selected} years={meta.years} placeholder={meta.placeholder} />
              <div role="tablist" aria-label="Population impact" className="flex gap-2">
                {VIEWS[0].subs.map((s) => (
                  <button
                    key={s}
                    type="button"
                    role="tab"
                    aria-selected={state.sub === s}
                    className={`tab-button sub-tab-button${state.sub === s ? " active" : ""}`}
                    onClick={() => set({ sub: s })}
                  >
                    {SUB_LABELS[s]}
                  </button>
                ))}
              </div>
              {state.sub === "finances" && <BudgetaryImpactChart measures={selected} years={meta.years} />}
              {state.sub === "deciles" && (
                <DistributionalChart cells={data.decile_impact} selectedIds={selected.map((m) => m.id)} />
              )}
              <p className="text-sm text-slate-600">
                Basis and data: see the <a href="?tab=methodology">Methodology</a> tab.
              </p>
            </>
          )}
          {state.tab === "household" && (
            <HouseholdCalculator
              households={data.households}
              measures={calculatorMeasures(measures)}
              placeholder={meta.placeholder}
            />
          )}
          {state.tab === "policies" && <PolicyCards measures={measures} repoUrl={REPO_URL} />}
          {state.tab === "methodology" && <MethodologyTab meta={meta} measures={measures} repoUrl={REPO_URL} />}
        </div>
      </main>
    </div>
  );
}
