import { cleanup, fireEvent, render, screen, within } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import results from "../../public/data/results.json";
import Dashboard, { SUBS, VIEWS } from "./Dashboard";

beforeEach(() => window.history.replaceState(null, "", "/"));
afterEach(() => {
  cleanup();
  vi.unstubAllGlobals();
});

describe("Dashboard", () => {
  it("states the pre-release notice once, in the banner, not again on the page", () => {
    render(<Dashboard data={results} />);
    expect(screen.queryByTestId("placeholder-note")).toBeNull();
    expect(document.body.textContent).not.toContain(results.meta.notice);
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
    for (const v of VIEWS) expect(screen.getByRole("tab", { name: v.label })).toBeTruthy();
    fireEvent.click(screen.getByRole("tab", { name: "Policies" }));
    expect(window.location.search).toContain("tab=policies");
    expect(screen.getAllByTestId("policy-card")).toHaveLength(results.measures.length);
  });

  it("wires every sub-tab to its panel", () => {
    render(<Dashboard data={results} />);
    for (const s of SUBS) {
      const tab = screen.getByRole("tab", { name: s.label });
      fireEvent.click(tab);
      expect(document.getElementById(tab.getAttribute("aria-controls"))).toBeTruthy();
    }
  });

  it("opens the tab named in the address", () => {
    window.history.replaceState(null, "", "/?tab=methodology");
    render(<Dashboard data={results} />);
    expect(screen.getByTestId("replication").textContent).toContain(results.meta.engine_label);
    expect(screen.getByTestId("replication").textContent).toContain("not in a policyengine.py release");
  });

  it("keeps the selected policies when the methodology link is followed", () => {
    const first = results.measures.find((m) => Array.isArray(m.budgetary_impact));
    window.history.replaceState(null, "", `/?policies=${first.id}`);
    render(<Dashboard data={results} />);
    fireEvent.click(screen.getByTestId("methodology-link"));
    expect(window.location.search).toContain("tab=methodology");
    expect(window.location.search).toContain(`policies=${first.id}`);
  });

  it("lists every example household with a change column and a placeholder stamp", () => {
    window.history.replaceState(null, "", "/?tab=household");
    render(<Dashboard data={results} />);
    const table = screen.getByTestId("household-table");
    expect(table.querySelectorAll("tbody tr")).toHaveLength(results.households.length);
    expect(within(table).getByText("Change")).toBeTruthy();
    expect(within(table).getAllByText("Placeholder").length).toBe(results.households.length * 5);
  });

  it("uses h2 under the page h1, never skipping a level", () => {
    render(<Dashboard data={results} />);
    expect(document.querySelectorAll("h1")).toHaveLength(1);
    expect(document.querySelectorAll("h3").length).toBe(0);
    expect(document.querySelectorAll("h2").length).toBeGreaterThan(0);
  });

  it("draws the budget chart as a labelled list at phone width", () => {
    vi.stubGlobal("matchMedia", (q) => ({
      matches: q.includes("max-width"),
      addEventListener() {},
      removeEventListener() {},
    }));
    window.matchMedia = globalThis.matchMedia;
    render(<Dashboard data={results} />);
    const list = screen.getByTestId("budget-bar-list");
    const charted = results.measures.filter((m) => Array.isArray(m.budgetary_impact));
    expect(list.querySelectorAll("li")).toHaveLength(charted.length);
    expect(list.querySelectorAll(".bar-list-bar").length).toBe(charted.length * results.meta.years.length);
  });

  it("shows no internal ids, route slugs or code paths on the policy cards", () => {
    window.history.replaceState(null, "", "/?tab=policies");
    render(<Dashboard data={results} />);
    for (const text of screen.getAllByTestId("policy-card-text").map((n) => n.textContent)) {
      expect(text).not.toMatch(/PLACEHOLDER|TRAP|measures\/|\b[a-z]+_[a-z_]+\b|dashboard-param|needs-pe-uk-first|not-computable/);
    }
  });

  it("marks Bands I and J as starting later", () => {
    window.history.replaceState(null, "", "/?tab=policies");
    render(<Dashboard data={results} />);
    expect(screen.getAllByText(/^From 2028-29$/).length).toBeGreaterThan(0);
  });
});
