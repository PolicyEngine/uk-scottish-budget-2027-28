import { formatGbp } from "../utils/format";

/**
 * Example households from presets computed by the pipeline. The live
 * calculator runs locally (src/scottish_budget/household.py); the page
 * calls no hosted API.
 */
export default function HouseholdCalculator({ households, measures, placeholder }) {
  return (
    <section className="panel" aria-label="Example households">
      <h3 className="mb-1 text-lg font-semibold">Example households, net income a year</h3>
      <p className="mb-3 text-sm text-slate-600">
        Measures in the calculator: {measures.map((m) => m.name).join("; ")}.
        {placeholder && " Placeholder figures."}
      </p>
      <div className="overflow-x-auto">
        <table className="data-table compact" data-testid="household-table">
          <thead>
            <tr>
              <th>Household</th>
              <th>Current law</th>
              <th>With the measures</th>
              <th>Same household, rest of UK</th>
            </tr>
          </thead>
          <tbody>
            {households.map((h) => (
              <tr key={h.id}>
                <td>{h.label}</td>
                <td>{formatGbp(h.baseline_net_income)}</td>
                <td>{formatGbp(h.reform_net_income)}</td>
                <td>{formatGbp(h.rest_of_uk_net_income)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}
