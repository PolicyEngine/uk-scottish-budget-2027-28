// Measures shown in the household calculator, read from results.json
// (registry field "calculator"), never from a hard-coded list.

export function calculatorMeasures(measures) {
  return measures.filter((m) => m.calculator);
}

/** Measures that have figures to chart, from the same catalogue. */
export function chartedMeasures(measures) {
  return measures.filter((m) => Array.isArray(m.budgetary_impact));
}
