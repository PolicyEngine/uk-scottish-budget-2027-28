import { formatBn, formatShare } from "../utils/format";

/** Headline tiles for the selected year: one home per number. */
export default function StatTiles({ measures, year, versus, poverty, placeholder }) {
  const total = measures.reduce(
    (sum, m) => sum + (m.budgetary_impact?.find((f) => f.year === year.year)?.value_bn ?? 0),
    0,
  );
  const less = versus.find((r) => r.year === year.year && r.scenario === "with_measures");
  const child = poverty.find((r) => r.year === year.year && r.basis === "ahc");
  return (
    <div className="grid gap-4 sm:grid-cols-3" data-testid="stat-tiles">
      <div className="metric-card">
        <p className="eyebrow text-slate-500">Net effect on revenue, {year.label}</p>
        <p className="text-2xl font-bold">{formatBn(Math.round(total * 100) / 100)}</p>
        <p className="text-xs text-slate-500">
          Selected measures; negative is a cost.{placeholder ? " Placeholder." : ""}
        </p>
      </div>
      <div className="metric-card">
        <p className="eyebrow text-slate-500">Taxpayers paying less than in the rest of the UK</p>
        <p className="text-2xl font-bold">{less ? formatShare(less.share_paying_less) : "–"}</p>
        <p className="text-xs text-slate-500">{less ? "With all measures." : "After the model run."}</p>
      </div>
      <div className="metric-card">
        <p className="eyebrow text-slate-500">Children in poverty, change</p>
        <p className="text-2xl font-bold">{child ? child.change_count.toLocaleString("en-GB") : "–"}</p>
        <p className="text-xs text-slate-500">{child ? "After housing costs, all measures." : "After the model run."}</p>
      </div>
    </div>
  );
}
