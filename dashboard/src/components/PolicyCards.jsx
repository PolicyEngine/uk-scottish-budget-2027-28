import { policyDetail } from "../utils/policyDetails";

const STATUS_LABEL = {
  placeholder: "Placeholder figures",
  published: "Published",
  "not-computable": "Not computable",
  ledger: "Recorded, not modelled",
  pending: "Needs a model change first",
};

/** Every measure in the registry, with its route and status. */
export default function PolicyCards({ measures, repoUrl }) {
  return (
    <div className="grid gap-4 md:grid-cols-2" data-testid="policy-cards">
      {measures.map((m) => (
        <article key={m.id} className="panel" data-testid="policy-card">
          <div className="mb-2 flex flex-wrap items-center gap-2">
            <h3 className="text-base font-semibold">{m.name}</h3>
            <span className="status-pill">{STATUS_LABEL[m.status] ?? m.status}</span>
            {m.in_baseline && <span className="status-pill">Already in the baseline</span>}
          </div>
          <p className="text-sm text-slate-700">{m.description}</p>
          {policyDetail(m) && <p className="mt-2 text-sm">{policyDetail(m)}</p>}
          {m.reason && <p className="mt-2 text-sm text-slate-600">{m.reason}</p>}
          <p className="mt-2 text-xs text-slate-500">
            Route: {m.route}. {m.basis_note}
            {m.issues.length > 0 && (
              <>
                {" "}
                Issues:{" "}
                {m.issues.map((n, i) => (
                  <span key={n}>
                    {i > 0 && ", "}
                    <a href={`${repoUrl}/issues/${n}`}>#{n}</a>
                  </span>
                ))}
                .
              </>
            )}
          </p>
        </article>
      ))}
    </div>
  );
}
