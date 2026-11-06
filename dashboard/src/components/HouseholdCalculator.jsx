import { formatChangeGbp, formatGbp } from "../utils/format";

/**
 * Example households, from presets the pipeline computes
 * (src/scottish_budget/household.py). The page calls no hosted API.
 */
export default function HouseholdCalculator({ households, measures, placeholder, yearLabel }) {
  const cell = (v, change = false) =>
    placeholder ? <span className="text-slate-500">Placeholder</span> : change ? formatChangeGbp(v) : formatGbp(v);
  return (
    <section className="panel" aria-labelledby="households-heading">
      <h2 id="households-heading" className="mb-1 text-lg font-semibold">
        Example households in Scotland, net income in {yearLabel}
      </h2>
      <p className="mb-3 text-sm text-slate-600">
        £ a year. With the measures: {measures.length ? measures.map((m) => m.name).join("; ") : "none yet"}.
      </p>
      <div className="overflow-x-auto">
        <table className="data-table compact" data-testid="household-table">
          <thead>
            <tr>
              <th scope="col">Household</th>
              <th scope="col">Current law</th>
              <th scope="col">With the measures</th>
              <th scope="col">Change</th>
              <th scope="col">Same household, rest of UK</th>
              <th scope="col">Scotland minus rest of UK</th>
            </tr>
          </thead>
          <tbody>
            {households.map((h) => (
              <tr key={h.id}>
                <th scope="row">{h.label}</th>
                <td>{cell(h.baseline_net_income)}</td>
                <td>{cell(h.reform_net_income)}</td>
                <td>{cell(h.change, true)}</td>
                <td>{cell(h.rest_of_uk_net_income)}</td>
                <td>{cell(h.scotland_minus_rest_of_uk, true)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}
