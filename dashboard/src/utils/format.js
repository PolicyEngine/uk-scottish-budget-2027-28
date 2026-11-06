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

/** A change in £, with its sign. */
export function formatChangeGbp(value) {
  if (value === null || value === undefined) return "withheld";
  const sign = value < 0 ? "−" : value > 0 ? "+" : "";
  return `${sign}£${Math.abs(Math.round(value)).toLocaleString("en-GB")}`;
}

/** A percentage given in per cent (0.25 means 0.25%). */
export function formatPct(value, digits = 2) {
  if (value === null || value === undefined) return "withheld";
  const sign = value < 0 ? "−" : value > 0 ? "+" : "";
  return `${sign}${Math.abs(value).toFixed(digits)}%`;
}

/** A share between 0 and 1 as a percentage. */
export function formatShare(value) {
  if (value === null || value === undefined) return "–";
  return `${(value * 100).toFixed(1)}%`;
}

export function toCsv(rows) {
  if (!rows.length) return "";
  const keys = Object.keys(rows[0]);
  const cell = (v) => (v === null || v === undefined ? "" : String(v).includes(",") ? `"${v}"` : String(v));
  return [keys.join(","), ...rows.map((r) => keys.map((k) => cell(r[k])).join(","))].join("\n");
}
