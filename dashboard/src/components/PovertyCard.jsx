import { formatShare } from "../utils/format";
import Pending from "./Pending";

const BASIS = { bhc: "Before housing costs", ahc: "After housing costs" };

/** Relative child poverty in Scotland, before and after the measures. */
export default function PovertyCard({ rows, year }) {
  const mine = rows.filter((r) => r.year === year && r.group === "children");
  return (
    <section className="panel" aria-labelledby="poverty-heading">
      <h2 id="poverty-heading" className="mb-2 text-lg font-semibold">
        Child poverty in Scotland, all measures together
      </h2>
      {mine.length ? (
        <table className="data-table compact" data-testid="poverty-table">
          <thead>
            <tr>
              <th scope="col">Measure of poverty</th>
              <th scope="col">Current law</th>
              <th scope="col">With the measures</th>
              <th scope="col">Children (change)</th>
            </tr>
          </thead>
          <tbody>
            {mine.map((r) => (
              <tr key={r.basis}>
                <th scope="row">{BASIS[r.basis]}</th>
                <td>{formatShare(r.baseline_rate)}</td>
                <td>{formatShare(r.reform_rate)}</td>
                <td>{r.change_count.toLocaleString("en-GB")}</td>
              </tr>
            ))}
          </tbody>
        </table>
      ) : (
        <Pending />
      )}
    </section>
  );
}
