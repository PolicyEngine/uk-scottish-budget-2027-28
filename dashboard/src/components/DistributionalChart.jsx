"use client";

import { useState } from "react";
import { Bar, BarChart, CartesianGrid, Cell, LabelList, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { axisStyle, chartColours } from "../utils/chartTheme";
import { formatChangeGbp, formatPct } from "../utils/format";
import ChartDownloadMenu from "./ChartDownloadMenu";
import ChartLogo from "./ChartLogo";
import ChartTooltip from "./ChartTooltip";

const METRICS = {
  avg_change_gbp: { label: "£ a year", format: (v) => formatChangeGbp(v) },
  pct_change: { label: "% of net income", format: (v) => formatPct(v) },
};

/**
 * Change in household net income by Scottish income decile for one year,
 * summed over the selected measures (decile averages add across measures).
 * A decile with any withheld cell is withheld.
 */
export function decileRows(cells, selectedIds, year, metric = "avg_change_gbp") {
  const rows = [];
  for (let d = 1; d <= 10; d += 1) {
    const mine = cells.filter(
      (c) => c.decile === d && selectedIds.includes(c.measure_id) && (year === undefined || c.year === year),
    );
    const withheld = mine.some((c) => c[metric] === null);
    rows.push({
      decile: d,
      value: withheld ? null : mine.reduce((s, c) => s + c[metric], 0),
      withheld,
    });
  }
  return rows;
}

export default function DistributionalChart({ cells, selectedIds, year, yearLabel, placeholder }) {
  const [metric, setMetric] = useState("avg_change_gbp");
  const rows = decileRows(cells, selectedIds, year, metric);
  const { label, format } = METRICS[metric];
  const shown = rows.map((r) => ({ ...r, bar: r.value ?? 0, text: r.withheld ? "withheld" : format(r.value) }));
  return (
    <section className="panel" aria-labelledby="decile-heading">
      <div className="mb-3 flex flex-wrap items-center justify-between gap-4">
        <h2 id="decile-heading" className="text-lg font-semibold">
          Change in household net income by income decile, {yearLabel}
        </h2>
        <ChartDownloadMenu rows={rows} filename="decile-impact" />
      </div>
      <div className="mb-3 flex gap-2" role="group" aria-label="Measure">
        {Object.entries(METRICS).map(([key, m]) => (
          <button
            key={key}
            type="button"
            aria-pressed={metric === key}
            className={`toggle-button${metric === key ? " active" : ""}`}
            onClick={() => setMetric(key)}
          >
            {m.label}
          </button>
        ))}
      </div>
      <div style={{ width: "100%", height: 340 }}>
        <ResponsiveContainer width="100%" height="100%" initialDimension={{ width: 900, height: 340 }}>
          <BarChart data={shown} margin={{ top: 24, bottom: 28, left: 8, right: 8 }}>
            <CartesianGrid stroke={chartColours.grid} vertical={false} />
            <XAxis
              dataKey="decile"
              tick={axisStyle}
              label={{ value: "Income decile (1 = bottom, 10 = top)", position: "insideBottom", offset: -16, ...axisStyle }}
            />
            <YAxis tick={axisStyle} tickFormatter={(v) => format(v)} width={80} />
            <Tooltip
              content={
                <ChartTooltip
                  format={(_, row) => (row.withheld ? "withheld" : format(row.value)) + (placeholder ? " (placeholder)" : "")}
                  labelFormat={(d) => `Decile ${d}`}
                />
              }
            />
            <Bar dataKey="bar" name={label}>
              {shown.map((r) => (
                <Cell key={r.decile} fill={r.bar >= 0 ? chartColours.gain : chartColours.loss} />
              ))}
              <LabelList dataKey="text" position="top" style={{ ...axisStyle, fontSize: 11 }} />
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>
      {rows.some((r) => r.withheld) && (
        <p className="mt-2 text-sm text-slate-600" data-testid="withheld-note">
          A decile marked withheld rests on too few survey households for at least one selected measure (see{" "}
          <a href="#disclosure">disclosure</a> on the Methodology tab).
        </p>
      )}
      <ChartLogo />
    </section>
  );
}
