import { formatChangeGbp } from "../utils/format";
import Pending from "./Pending";

/** Average change in household net income by council tax band. */
export default function CouncilTaxBands({ cells, year }) {
  const mine = cells.filter((c) => c.year === year);
  return (
    <section className="panel" aria-labelledby="bands-heading">
      <h2 id="bands-heading" className="mb-2 text-lg font-semibold">
        Change in household net income by council tax band, all measures together
      </h2>
      {mine.length ? (
        <table className="data-table compact" data-testid="bands-table">
          <thead>
            <tr>
              <th scope="col">Band</th>
              <th scope="col">Average change, £ a year</th>
            </tr>
          </thead>
          <tbody>
            {mine.map((c) => (
              <tr key={c.band}>
                <th scope="row">{c.band}</th>
                <td>{formatChangeGbp(c.avg_change_gbp)}</td>
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
