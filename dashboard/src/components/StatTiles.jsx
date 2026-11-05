import { formatBn } from "../utils/format";

/** Headline tiles: one home per number (the total of the selected measures). */
export default function StatTiles({ measures, years, placeholder }) {
  return (
    <div className="grid gap-4 sm:grid-cols-3" data-testid="stat-tiles">
      {years.map((y) => {
        const total = measures.reduce(
          (sum, m) => sum + (m.budgetary_impact?.find((f) => f.year === y.year)?.value_bn ?? 0),
          0,
        );
        return (
          <div key={y.year} className="metric-card">
            <p className="eyebrow text-slate-500">Net effect on revenue, {y.label}</p>
            <p className="text-2xl font-bold">{formatBn(Math.round(total * 100) / 100)}</p>
            {placeholder && <p className="text-xs text-slate-500">Placeholder</p>}
          </div>
        );
      })}
      <div className="metric-card">
        <p className="eyebrow text-slate-500">Measures selected</p>
        <p className="text-2xl font-bold">{measures.length}</p>
      </div>
    </div>
  );
}
