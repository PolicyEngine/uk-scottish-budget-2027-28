"use client";

import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { axisStyle, chartColours, yearColour } from "../utils/chartTheme";
import ChartDownloadMenu from "./ChartDownloadMenu";
import ChartLogo from "./ChartLogo";

/** Net effect on revenue by measure and year (£bn; negative is a cost). */
export default function BudgetaryImpactChart({ measures, years }) {
  const rows = measures.map((m) => {
    const row = { measure: m.name };
    for (const y of years) {
      row[y.label] = m.budgetary_impact.find((f) => f.year === y.year)?.value_bn ?? null;
    }
    return row;
  });
  return (
    <section className="panel" aria-label="Net effect on revenue by measure">
      <div className="mb-3 flex items-center justify-between gap-4">
        <h3 className="text-lg font-semibold">Net effect on revenue by measure (£bn)</h3>
        <ChartDownloadMenu rows={rows} filename="budgetary-impact" />
      </div>
      <div style={{ width: "100%", height: Math.max(240, 40 * rows.length) }}>
        <ResponsiveContainer>
          <BarChart data={rows} layout="vertical" margin={{ left: 24, right: 24 }}>
            <CartesianGrid stroke={chartColours.grid} horizontal={false} />
            <XAxis type="number" tick={axisStyle} />
            <YAxis type="category" dataKey="measure" width={260} tick={axisStyle} />
            <Tooltip />
            {years.map((y, i) => (
              <Bar key={y.year} dataKey={y.label} fill={yearColour(i)} />
            ))}
          </BarChart>
        </ResponsiveContainer>
      </div>
      <ChartLogo />
    </section>
  );
}
