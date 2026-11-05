/** Method and data: the basis is stated here once; other tabs link here. */
export default function MethodologyTab({ meta, measures, repoUrl }) {
  const notComputable = measures.filter((m) => m.status === "not-computable");
  return (
    <div className="space-y-6">
      <section className="panel" id="basis">
        <h3 className="mb-2 text-lg font-semibold">Basis</h3>
        <ul className="list-disc space-y-1 pl-5 text-sm">
          {Object.entries(meta.basis).map(([k, v]) => (
            <li key={k}>
              <strong>{k.replaceAll("_", " ")}:</strong> {v}
            </li>
          ))}
        </ul>
      </section>
      <section className="panel" id="engine">
        <h3 className="mb-2 text-lg font-semibold">Model and data</h3>
        <p className="text-sm" data-testid="replication">
          Built with policyengine.py {meta.policyengine} (policyengine-uk {meta.policyengine_uk}) on Microcosm build{" "}
          <code>{meta.dataset}</code>. Replication code: <a href={repoUrl}>PolicyEngine/uk-scottish-budget-2027-28</a>.
        </p>
        <p className="mt-2 text-sm">
          Cells resting on fewer than {meta.disclosure_floor} survey households are withheld.
        </p>
      </section>
      <section className="panel" id="limits">
        <h3 className="mb-2 text-lg font-semibold">Not computable</h3>
        <ul className="list-disc space-y-1 pl-5 text-sm">
          {notComputable.map((m) => (
            <li key={m.id}>
              <strong>{m.name}.</strong> {m.reason}
            </li>
          ))}
        </ul>
      </section>
    </div>
  );
}
