"use client";

/** A tooltip that prints each series' name and a formatted value, never an
 * internal key or a raw number. */
export default function ChartTooltip({ active, payload, label, format, labelFormat }) {
  if (!active || !payload?.length) return null;
  return (
    <div className="panel" style={{ padding: 10 }} role="tooltip">
      <p className="mb-1 text-sm font-semibold">{labelFormat ? labelFormat(label) : label}</p>
      {payload.map((p) => (
        <p key={p.dataKey} className="text-sm">
          {p.name}: {format(p.value, p.payload)}
        </p>
      ))}
    </div>
  );
}
