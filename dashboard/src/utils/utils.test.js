import { readdirSync, readFileSync } from "node:fs";
import { resolve } from "node:path";
import { describe, expect, it } from "vitest";
import { decileRows } from "../components/DistributionalChart";
import { curveRows } from "../components/IncomeTaxCurve";
import { calculatorMeasures, chartedMeasures } from "./calculatorOnlyMeasures";
import { yearColour } from "./chartTheme";
import { formatBn, toCsv } from "./format";
import { policyDetail } from "./policyDetails";

describe("utils", () => {
  it("policy text is ignored once the description changes", () => {
    const details = { a: { writtenFor: "old", summary: "text" } };
    expect(policyDetail({ id: "a", description: "old" }, details)).toBe("text");
    expect(policyDetail({ id: "a", description: "new" }, details)).toBeNull();
  });

  it("charted and calculator measures come from the catalogue", () => {
    const ms = [
      { id: "a", calculator: true, status: "placeholder", budgetary_impact: [] },
      { id: "b", calculator: false, status: "placeholder", budgetary_impact: null },
      { id: "c", calculator: true, status: "pending", budgetary_impact: null },
      { id: "d", calculator: true, status: "not-computable", first_year: 2028, budgetary_impact: null },
    ];
    expect(chartedMeasures(ms).map((m) => m.id)).toEqual(["a"]);
    expect(calculatorMeasures(ms).map((m) => m.id)).toEqual(["a"]);
  });

  it("a withheld cell withholds its decile, and years are kept apart", () => {
    const cells = [
      { measure_id: "a", year: 2027, decile: 1, avg_change_gbp: 5 },
      { measure_id: "a", year: 2028, decile: 1, avg_change_gbp: 7 },
      { measure_id: "b", year: 2027, decile: 1, avg_change_gbp: null },
    ];
    expect(decileRows(cells, ["a"], 2027)[0].value).toBe(5);
    expect(decileRows(cells, ["a"], 2028)[0].value).toBe(7);
    expect(decileRows(cells, ["a", "b"], 2027)[0].value).toBeNull();
  });

  it("income tax curve gives the gap and marginal rates", () => {
    const rows = curveRows([
      { gross: 0, scotland_current_law: 0, scotland_with_measures: 0, rest_of_uk: 0 },
      { gross: 1000, scotland_current_law: 210, scotland_with_measures: 220, rest_of_uk: 200 },
    ]);
    expect(rows[1].gap_now).toBe(10);
    expect(rows[1].gap_after).toBe(20);
    expect(rows[1].rate_scotland).toBe(22);
    expect(rows[1].rate_ruk).toBe(20);
  });

  it("formats and exports", () => {
    expect(formatBn(-0.2)).toBe("−£0.20bn");
    expect(formatBn(null)).toBe("–");
    expect(toCsv([{ a: 1, b: "x,y" }])).toBe('a,b\n1,"x,y"');
    expect(() => yearColour(5)).toThrow();
  });

  it("components take colours from chartTheme, never a hex literal", () => {
    const dir = resolve(__dirname, "../components");
    for (const file of readdirSync(dir).filter((f) => f.endsWith(".jsx") && !f.includes(".test."))) {
      const source = readFileSync(resolve(dir, file), "utf8").replace(/var\([^)]*\)/g, "");
      expect(source, file).not.toMatch(/#[0-9a-fA-F]{6}\b/);
    }
  });
});
