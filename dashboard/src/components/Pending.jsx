/** The one line a panel shows before the model has run. */
export default function Pending({ children }) {
  return (
    <p className="text-sm text-slate-600" data-testid="pending-panel">
      {children ?? "Shown once the measures are run through the model on the day."}
    </p>
  );
}
