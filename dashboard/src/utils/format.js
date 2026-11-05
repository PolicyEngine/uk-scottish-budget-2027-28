export function formatBn(value) {
  if (value === null || value === undefined) return "–";
  const sign = value < 0 ? "−" : value > 0 ? "+" : "";
  return `${sign}£${Math.abs(value).toFixed(2)}bn`;
}

export function formatGbp(value) {
  if (value === null || value === undefined) return "withheld";
  const sign = value < 0 ? "−" : "";
  return `${sign}£${Math.abs(Math.round(value)).toLocaleString("en-GB")}`;
}

export function toCsv(rows) {
  if (!rows.length) return "";
  const keys = Object.keys(rows[0]);
  const cell = (v) => (v === null || v === undefined ? "" : String(v).includes(",") ? `"${v}"` : String(v));
  return [keys.join(","), ...rows.map((r) => keys.map((k) => cell(r[k])).join(","))].join("\n");
}
