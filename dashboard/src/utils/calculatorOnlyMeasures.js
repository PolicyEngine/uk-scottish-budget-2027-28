// Measures shown with the example households and in the charts, read from
// results.json (registry fields), never from a hard-coded list.

const WITH_FIGURES = new Set(["placeholder", "provisional", "published"]);

/** Measures the example households include: in the calculator, with
 * figures, and in force in the Budget year. */
export function calculatorMeasures(measures) {
  return measures.filter((m) => m.calculator && WITH_FIGURES.has(m.status) && !m.first_year);
}

/** Measures that have figures to chart, from the same catalogue. */
export function chartedMeasures(measures) {
  return measures.filter((m) => Array.isArray(m.budgetary_impact));
}
