import { policyDetail } from "../utils/policyDetails";

const STATUS_LABEL = {
  placeholder: "Placeholder figures",
  provisional: "Provisional",
  published: "Costed",
  "not-computable": "Not computable",
  ledger: "Recorded, not modelled",
  pending: "Needs a model change first",
};

/** Every measure in the registry, with its status in plain words. */
export default function PolicyCards({ measures, repoUrl, years }) {
  const label = (y) => years.find((x) => x.year === y)?.label ?? `${y}-${String(y + 1).slice(-2)}`;
  return (
    <div className="grid gap-4 md:grid-cols-2" data-testid="policy-cards">
      {measures.map((m) => (
        <article key={m.id} id={`policy-${m.id}`} className="panel" data-testid="policy-card">
          <div className="mb-2 flex flex-wrap items-center gap-2">
            <h2 className="text-base font-semibold">{m.name}</h2>
            <span className="status-pill">{STATUS_LABEL[m.status] ?? m.status}</span>
            {m.in_baseline && <span className="status-pill">Already in current law</span>}
            {m.first_year && <span className="status-pill">From {label(m.first_year)}</span>}
          </div>
          <div data-testid="policy-card-text">
            <p className="text-sm text-slate-700">{m.description}</p>
            {policyDetail(m) && <p className="mt-2 text-sm">{policyDetail(m)}</p>}
            {m.reason && <p className="mt-2 text-sm text-slate-600">{m.reason}</p>}
            {m.basis_note && <p className="mt-2 text-sm text-slate-600">{m.basis_note}</p>}
          </div>
          {m.issues.length > 0 && (
            <p className="mt-2 text-xs text-slate-500">
              Model notes:{" "}
              {m.issues.map((n, i) => (
                <span key={n}>
                  {i > 0 && ", "}
                  <a href={`${repoUrl}/issues/${n}`}>issue {n}</a>
                </span>
              ))}
            </p>
          )}
        </article>
      ))}
    </div>
  );
}
