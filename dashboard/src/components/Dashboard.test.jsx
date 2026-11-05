import { cleanup, fireEvent, render, screen } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it } from "vitest";
import results from "../../public/data/results.json";
import Dashboard, { VIEWS } from "./Dashboard";

beforeEach(() => window.history.replaceState(null, "", "/"));
afterEach(cleanup);

describe("Dashboard", () => {
  it("shows the placeholder notice from results.json", () => {
    render(<Dashboard data={results} />);
    expect(screen.getByTestId("placeholder-note").textContent).toMatch(/placeholder/i);
  });

  it("offers one chip per measure with figures, read from the catalogue", () => {
    render(<Dashboard data={results} />);
    const withFigures = results.measures.filter((m) => Array.isArray(m.budgetary_impact));
    expect(screen.getAllByTestId("policy-chip")).toHaveLength(withFigures.length);
    expect(withFigures.length).toBeGreaterThan(0);
  });

  it("never offers a not-computable measure as a chip", () => {
    render(<Dashboard data={results} />);
    const names = screen.getAllByTestId("policy-chip").map((c) => c.textContent);
    for (const m of results.measures.filter((x) => x.status === "not-computable")) {
      expect(names).not.toContain(m.name);
    }
  });

  it("has the four tabs and writes ?tab= to the address", () => {
    render(<Dashboard data={results} />);
    expect(screen.getAllByRole("tab", { name: /./ }).length).toBeGreaterThanOrEqual(VIEWS.length);
    fireEvent.click(screen.getByRole("tab", { name: "Policies" }));
    expect(window.location.search).toContain("tab=policies");
    expect(screen.getAllByTestId("policy-card")).toHaveLength(results.measures.length);
  });

  it("opens the tab named in the address", () => {
    window.history.replaceState(null, "", "/?tab=methodology");
    render(<Dashboard data={results} />);
    expect(screen.getByTestId("replication").textContent).toContain(results.meta.policyengine);
  });

  it("lists every household preset", () => {
    window.history.replaceState(null, "", "/?tab=household");
    render(<Dashboard data={results} />);
    const rows = screen.getByTestId("household-table").querySelectorAll("tbody tr");
    expect(rows).toHaveLength(results.households.length);
  });
});
