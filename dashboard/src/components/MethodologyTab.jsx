const BASIS_LABELS = {
  period: "Period",
  gross_or_net: "Gross or net",
  cash_or_accrued: "Cash or accrued",
  behaviour: "Behaviour",
};

/** Method and data: the basis is stated here once; other tabs link here. */
export default function MethodologyTab({ meta, measures, repoUrl, onOpenPolicy }) {
  const notComputable = measures.filter((m) => m.status === "not-computable");
  return (
    <div className="space-y-6">
      <section className="panel" id="basis" aria-labelledby="basis-heading">
        <h2 id="basis-heading" className="mb-2 text-lg font-semibold">
          Basis
        </h2>
        <dl className="grid gap-x-6 gap-y-2 text-sm sm:grid-cols-[max-content_1fr]">
          {Object.entries(meta.basis).map(([k, v]) => (
            <div key={k} className="contents">
              <dt className="font-semibold">{BASIS_LABELS[k] ?? k}</dt>
              <dd>{v}</dd>
            </div>
          ))}
        </dl>
      </section>
      <section className="panel" id="engine" aria-labelledby="engine-heading">
        <h2 id="engine-heading" className="mb-2 text-lg font-semibold">
          Model and data
        </h2>
        <p className="text-sm" data-testid="replication">
          Built with PolicyEngine UK on Microcosm, PolicyEngine&apos;s calibrated survey dataset:{" "}
          {meta.engine_label ?? `build ${meta.dataset}, policyengine-uk ${meta.policyengine_uk}`}. Replication code:{" "}
          <a href={repoUrl}>PolicyEngine/uk-scottish-budget-2027-28</a>.
        </p>
        <p className="mt-2 text-sm">
          Data year: 2024-25 survey data, projected to each year on the {meta.forecast?.vintage ?? "OBR"} forecast, which every
          simulation uses.
        </p>
      </section>
      <section className="panel" id="distribution" aria-labelledby="distribution-heading">
        <h2 id="distribution-heading" className="mb-2 text-lg font-semibold">
          Distribution
        </h2>
        <p className="text-sm">
          Deciles rank households in Scotland against each other by equivalised net income, weighted by people. Winners and
          losers, child poverty and council tax bands come from one run of every measure together.
        </p>
      </section>
      <section className="panel" id="disclosure" aria-labelledby="disclosure-heading">
        <h2 id="disclosure-heading" className="mb-2 text-lg font-semibold">
          Disclosure
        </h2>
        <p className="text-sm">Cells resting on fewer than {meta.disclosure_floor} survey households are withheld.</p>
      </section>
      <section className="panel" id="limits" aria-labelledby="limits-heading">
        <h2 id="limits-heading" className="mb-2 text-lg font-semibold">
          Limits
        </h2>
        <ul className="list-disc space-y-1 pl-5 text-sm">
          <li>
            Not modelled: Air Departure Tax, non-domestic rates, behaviour in property purchases, and spending other than cash
            payments to households.
          </li>
          <li>Geography: Scotland as a whole. Council results are not shown until the local data fit is checked.</li>
          <li>
            Adult Disability Payment and Carer Support Payment: the data are not calibrated to Social Security
            Scotland&apos;s caseloads for these payments, so costs of changes to them may differ from official estimates.
          </li>
          {notComputable.length > 0 && (
            <li>
              Not computable, with the reason on each card:{" "}
              {notComputable.map((m, i) => (
                <span key={m.id}>
                  {i > 0 && ", "}
                  <a
                    href={`?tab=policies#policy-${m.id}`}
                    onClick={(e) => {
                      e.preventDefault();
                      onOpenPolicy?.(m.id);
                    }}
                  >
                    {m.name}
                  </a>
                </span>
              ))}
              .
            </li>
          )}
        </ul>
      </section>
    </div>
  );
}
