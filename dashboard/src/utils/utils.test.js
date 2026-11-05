import { readdirSync, readFileSync } from "node:fs";
import { resolve } from "node:path";
import { describe, expect, it } from "vitest";
import { decileRows } from "../components/DistributionalChart";
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
      { id: "a", calculator: true, budgetary_impact: [] },
      { id: "b", calculator: false, budgetary_impact: null },
    ];
    expect(chartedMeasures(ms).map((m) => m.id)).toEqual(["a"]);
    expect(calculatorMeasures(ms).map((m) => m.id)).toEqual(["a"]);
  });

  it("a withheld cell withholds its decile", () => {
    const cells = [
      { measure_id: "a", decile: 1, avg_change_gbp: 5 },
      { measure_id: "b", decile: 1, avg_change_gbp: null },
    ];
    expect(decileRows(cells, ["a"])[0].avg_change_gbp).toBe(5);
    expect(decileRows(cells, ["a", "b"])[0].avg_change_gbp).toBeNull();
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
