import { formatShare } from "../utils/format";
import Pending from "./Pending";

const SCENARIO = { current_law: "Current law", with_measures: "With the measures" };

/** Scottish income taxpayers paying less or more income tax than on the
 * rest-of-UK schedule. Example households: the Household tab. */
export default function ScotlandVsRestOfUk({ rows, year }) {
  const mine = rows.filter((r) => r.year === year);
  return (
    <section className="panel" aria-labelledby="ruk-heading">
      <h2 id="ruk-heading" className="mb-2 text-lg font-semibold">
        Scottish income taxpayers compared with the rest of the UK
      </h2>
      {mine.length ? (
        <table className="data-table compact" data-testid="ruk-table">
          <thead>
            <tr>
              <th scope="col"> </th>
              <th scope="col">Pay less than in the rest of the UK</th>
              <th scope="col">Pay more</th>
            </tr>
          </thead>
          <tbody>
            {mine.map((r) => (
              <tr key={r.scenario}>
                <th scope="row">{SCENARIO[r.scenario]}</th>
                <td>{formatShare(r.share_paying_less)}</td>
                <td>{formatShare(r.share_paying_more)}</td>
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
