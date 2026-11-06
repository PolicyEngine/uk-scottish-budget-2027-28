"use client";

import { CartesianGrid, Legend, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { axisStyle, chartColours, yearColour } from "../utils/chartTheme";
import { formatChangeGbp, formatGbp } from "../utils/format";
import ChartLogo from "./ChartLogo";
import ChartTooltip from "./ChartTooltip";
import Pending from "./Pending";

/** Per £1,000 step: Scotland minus rest of UK, and marginal rates. */
export function curveRows(rows) {
  return rows.map((r, i) => {
    const prev = rows[i - 1];
    const step = prev ? r.gross - prev.gross : 1;
    const rate = (key) => (prev ? Math.round((1000 * (r[key] - prev[key])) / step) / 10 : null);
    return {
      gross: r.gross,
      gap_now: r.scotland_current_law - r.rest_of_uk,
      gap_after: r.scotland_with_measures - r.rest_of_uk,
      rate_scotland: rate("scotland_with_measures"),
      rate_ruk: rate("rest_of_uk"),
    };
  });
}

function Chart({ data, lines, yFormat, yLabel, id }) {
  return (
    <div style={{ width: "100%", height: 300 }} data-testid={id}>
      <ResponsiveContainer width="100%" height="100%" initialDimension={{ width: 900, height: 300 }}>
        <LineChart data={data} margin={{ left: 8, right: 16, bottom: 24 }}>
          <CartesianGrid stroke={chartColours.grid} vertical={false} />
          <XAxis
            dataKey="gross"
            type="number"
            tick={axisStyle}
            tickFormatter={(v) => formatGbp(v)}
            label={{ value: "Gross earnings, £ a year", position: "insideBottom", offset: -16, ...axisStyle }}
          />
          <YAxis tick={axisStyle} tickFormatter={yFormat} width={72} label={{ value: yLabel, angle: -90, position: "insideLeft", ...axisStyle }} />
          <Tooltip content={<ChartTooltip format={(v) => yFormat(v)} labelFormat={(g) => `Earnings ${formatGbp(g)}`} />} />
          <Legend verticalAlign="top" height={28} />
          {lines.map((l, i) => (
            <Line key={l.key} dataKey={l.key} name={l.name} stroke={yearColour(i)} dot={false} type={l.step ? "stepAfter" : "linear"} strokeWidth={2} />
          ))}
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}

/** A single adult's income tax in Scotland against the rest of the UK. */
export default function IncomeTaxCurve({ rows, yearLabel }) {
  const data = curveRows(rows);
  return (
    <section className="panel" aria-labelledby="curve-heading">
      <h2 id="curve-heading" className="mb-2 text-lg font-semibold">
        Income tax in Scotland minus the rest of the UK, single adult, {yearLabel}
      </h2>
      {data.length ? (
        <>
          <p className="mb-2 text-sm text-slate-600">Positive: a Scottish taxpayer pays more than in the rest of the UK.</p>
          <Chart
            id="curve-gap"
            data={data}
            yFormat={(v) => formatChangeGbp(v)}
            yLabel="£ a year"
            lines={[
              { key: "gap_now", name: "Current law" },
              { key: "gap_after", name: "With the measures" },
            ]}
          />
          <h2 className="mb-2 mt-6 text-lg font-semibold">Income tax marginal rate by earnings, {yearLabel}</h2>
          <Chart
            id="curve-rates"
            data={data.slice(1)}
            yFormat={(v) => `${v}%`}
            yLabel="Marginal rate"
            lines={[
              { key: "rate_scotland", name: "Scotland, with the measures", step: true },
              { key: "rate_ruk", name: "Rest of UK", step: true },
            ]}
          />
          <ChartLogo />
        </>
      ) : (
        <Pending />
      )}
    </section>
  );
}
