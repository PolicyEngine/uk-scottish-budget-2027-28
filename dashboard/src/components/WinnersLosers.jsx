import { formatShare } from "../utils/format";
import Pending from "./Pending";

/** Share of people in Scottish households that gain or lose, for the whole
 * package (these shares do not add across measures). */
export default function WinnersLosers({ rows, year }) {
  const row = rows.find((r) => r.year === year);
  return (
    <section className="panel" aria-labelledby="winners-heading">
      <h2 id="winners-heading" className="mb-2 text-lg font-semibold">
        People better or worse off, all measures together
      </h2>
      {row ? (
        <dl className="grid gap-4 sm:grid-cols-3">
          <div>
            <dt className="text-sm text-slate-600">Better off by more than £1</dt>
            <dd className="text-2xl font-bold">{formatShare(row.gain_share)}</dd>
          </div>
          <div>
            <dt className="text-sm text-slate-600">Worse off by more than £1</dt>
            <dd className="text-2xl font-bold">{formatShare(row.lose_share)}</dd>
          </div>
          <div>
            <dt className="text-sm text-slate-600">Little or no change</dt>
            <dd className="text-2xl font-bold">{formatShare(1 - row.gain_share - row.lose_share)}</dd>
          </div>
        </dl>
      ) : (
        <Pending />
      )}
    </section>
  );
}
