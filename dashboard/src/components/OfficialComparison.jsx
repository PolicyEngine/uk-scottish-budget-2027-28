import { formatBn } from "../utils/format";
import Pending from "./Pending";

/** PolicyEngine figures beside the Scottish Fiscal Commission's costings. */
export default function OfficialComparison({ measures, costings, year }) {
  const rows = costings
    .filter((c) => c.year === year)
    .map((c) => {
      const m = measures.find((x) => x.id === c.measure_id);
      const ours = m?.budgetary_impact?.find((f) => f.year === year)?.value_bn ?? null;
      return { ...c, name: m?.name ?? c.measure_id, ours };
    });
  return (
    <section className="panel" aria-labelledby="official-heading">
      <h2 id="official-heading" className="mb-2 text-lg font-semibold">
        PolicyEngine and the Scottish Fiscal Commission
      </h2>
      {rows.length ? (
        <table className="data-table compact" data-testid="official-table">
          <thead>
            <tr>
              <th scope="col">Measure</th>
              <th scope="col">PolicyEngine (static)</th>
              <th scope="col">Scottish Fiscal Commission</th>
              <th scope="col">Official basis</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((r) => (
              <tr key={r.measure_id}>
                <th scope="row">{r.name}</th>
                <td>{formatBn(r.ours)}</td>
                <td>{formatBn(r.official_value_bn)}</td>
                <td>{r.basis}</td>
              </tr>
            ))}
          </tbody>
        </table>
      ) : (
        <Pending>Filled from the Scottish Fiscal Commission&apos;s costings when they are published.</Pending>
      )}
    </section>
  );
}
