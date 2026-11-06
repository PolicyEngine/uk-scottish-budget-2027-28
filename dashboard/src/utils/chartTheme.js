// Chart colours in one place (docs/COLOURS.md). Components never write a
// hex value: they take it from here. Teal and grey only, as on other
// PolicyEngine dashboards; gains in teal, losses in grey.
export const chartColours = {
  gain: "#2C7A7B", // primary-600
  loss: "#9CA3AF", // gray-400
  neutral: "#6B7280", // gray-500
  grid: "#E2E8F0", // border-light
  axis: "#4B5563", // gray-600
  years: ["#285E61", "#4FD1C5"], // primary-700, primary-300
};

export const axisStyle = { fontSize: 12, fill: chartColours.axis };

/** Colour for a year's series, by its position in meta.years. */
export function yearColour(index) {
  const { years } = chartColours;
  if (index < 0 || index >= years.length) {
    throw new Error(`No colour assigned for year index ${index}`);
  }
  return years[index];
}
