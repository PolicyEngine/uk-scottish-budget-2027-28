"use client";

import { Bar, BarChart, CartesianGrid, Cell, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { axisStyle, chartColours } from "../utils/chartTheme";
import ChartDownloadMenu from "./ChartDownloadMenu";
import ChartLogo from "./ChartLogo";

/**
 * Average change in household net income by income decile, summed over the
 * selected measures. A decile with any withheld cell is shown as withheld.
 */
export function decileRows(cells, selectedIds) {
  const rows = [];
  for (let d = 1; d <= 10; d += 1) {
    const mine = cells.filter((c) => c.decile === d && selectedIds.includes(c.measure_id));
    const withheld = mine.some((c) => c.avg_change_gbp === null);
    rows.push({
      decile: d,
      avg_change_gbp: withheld ? null : mine.reduce((s, c) => s + c.avg_change_gbp, 0),
      withheld,
    });
  }
  return rows;
}

export default function DistributionalChart({ cells, selectedIds }) {
  const rows = decileRows(cells, selectedIds);
  return (
    <section className="panel" aria-label="Change by income decile">
      <div className="mb-3 flex items-center justify-between gap-4">
        <h3 className="text-lg font-semibold">Average change in household net income by income decile (£ a year)</h3>
        <ChartDownloadMenu rows={rows} filename="decile-impact" />
      </div>
      <div style={{ width: "100%", height: 320 }}>
        <ResponsiveContainer>
          <BarChart data={rows}>
            <CartesianGrid stroke={chartColours.grid} vertical={false} />
            <XAxis dataKey="decile" tick={axisStyle} />
            <YAxis tick={axisStyle} />
            <Tooltip />
            <Bar dataKey="avg_change_gbp">
              {rows.map((r) => (
                <Cell key={r.decile} fill={(r.avg_change_gbp ?? 0) >= 0 ? chartColours.gain : chartColours.loss} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>
      {rows.some((r) => r.withheld) && (
        <p className="mt-2 text-sm text-slate-600" data-testid="withheld-note">
          Deciles marked withheld rest on fewer than 10 survey households for at least one selected measure.
        </p>
      )}
      <ChartLogo />
    </section>
  );
}
