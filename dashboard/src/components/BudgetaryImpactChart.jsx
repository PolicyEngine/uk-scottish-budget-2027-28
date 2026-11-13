"use client";

import { Bar, BarChart, CartesianGrid, Legend, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { axisStyle, chartColours, yearColour } from "../utils/chartTheme";
import { formatBn } from "../utils/format";
import { useNarrow } from "../utils/useNarrow";
import ChartDownloadMenu from "./ChartDownloadMenu";
import ChartLogo from "./ChartLogo";
import ChartTooltip from "./ChartTooltip";

export function budgetRows(measures, years) {
  return measures.map((m) => {
    const row = { measure: m.name };
    for (const y of years) {
      row[y.label] = m.budgetary_impact.find((f) => f.year === y.year)?.value_bn ?? null;
    }
    return row;
  });
}

/** Phones: each measure's name above its bars, drawn without an axis
 * column, so the bars have the full width. */
function BarList({ rows, years, placeholder }) {
  const max = Math.max(0.01, ...rows.flatMap((r) => years.map((y) => Math.abs(r[y.label] ?? 0))));
  return (
    <ul className="space-y-3" data-testid="budget-bar-list">
      {rows.map((r) => (
        <li key={r.measure}>
          <p className="mb-1 text-sm font-medium">{r.measure}</p>
          {years.map((y, i) => {
            const v = r[y.label] ?? 0;
            const width = `${(Math.abs(v) / max) * 50}%`;
            return (
              <div key={y.year} className="mb-1 flex items-center gap-2">
                <span className="w-14 shrink-0 text-xs text-slate-600">{y.label}</span>
                <div className="bar-list-track flex-1" aria-hidden="true">
                  <span className="bar-list-axis" style={{ left: "50%" }} />
                  <span
                    className="bar-list-bar"
                    style={{ background: yearColour(i), width, left: v < 0 ? `calc(50% - ${width})` : "50%" }}
                  />
                </div>
                <span className="w-20 shrink-0 text-right text-xs">
                  {formatBn(r[y.label])}
                  {placeholder ? "*" : ""}
                </span>
              </div>
            );
          })}
        </li>
      ))}
    </ul>
  );
}

/** Net effect on revenue by measure and year (£bn; negative is a cost). */
export default function BudgetaryImpactChart({ measures, years, placeholder, label }) {
  const narrow = useNarrow();
  const rows = budgetRows(measures, years);
  const height = Math.max(240, 44 * rows.length + 60);
  const format = (v) => `${formatBn(v)}${placeholder ? " (placeholder)" : ""}`;
  return (
    <section className="panel" aria-labelledby="budget-heading">
      <div className="mb-3 flex flex-wrap items-center justify-between gap-4">
        <h2 id="budget-heading" className="text-lg font-semibold">
          Net effect on Scottish Government revenue by measure
        </h2>
        <ChartDownloadMenu rows={rows} filename="budgetary-impact" />
      </div>
      <p className="mb-3 text-sm text-slate-600">
        £bn a year. Positive is more revenue, negative is a cost. Static.
        {placeholder && " * Placeholder figures."}
        {label ? ` Figures: ${label}.` : ""}
      </p>
      {narrow ? (
        <BarList rows={rows} years={years} placeholder={placeholder} />
      ) : (
        <div style={{ width: "100%", height }}>
          <ResponsiveContainer width="100%" height="100%" initialDimension={{ width: 900, height }}>
            <BarChart data={rows} layout="vertical" margin={{ left: 8, right: 24, bottom: 24 }}>
              <CartesianGrid stroke={chartColours.grid} horizontal={false} />
              <XAxis
                type="number"
                tick={axisStyle}
                tickFormatter={(v) => formatBn(v)}
                label={{ value: "£bn a year", position: "insideBottom", offset: -16, ...axisStyle }}
              />
              <YAxis type="category" dataKey="measure" width={220} tick={axisStyle} />
              <Tooltip content={<ChartTooltip format={format} />} />
              <Legend verticalAlign="top" height={28} />
              {years.map((y, i) => (
                <Bar key={y.year} dataKey={y.label} name={y.label} fill={yearColour(i)} />
              ))}
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}
      <ChartLogo />
    </section>
  );
}
