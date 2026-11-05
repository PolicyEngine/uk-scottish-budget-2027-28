// Build-time guard on public/data (the JavaScript twin of
// scripts/check_public_data.py). Fails the build if a public file carries
// record identifiers or weights, a value on a cell below the floor of 10
// survey households, or area codes; or if results.json is a placeholder
// file without its placeholder flag and notice.
import { readdirSync, readFileSync, statSync } from "node:fs";
import { join } from "node:path";

const FLOOR = 10;
const FORBIDDEN = new Set(["household_id", "person_id", "benunit_id", "household_weight", "person_weight", "benunit_weight", "weight"]);
const AREA_CODE = /\b(S12|S14|S16|S01|E14|W07|N06)\d{6}\b/;
const VALUE_KEYS = ["avg_change_gbp", "pct_change", "value"];
const dir = new URL("../public/data/", import.meta.url).pathname;
const problems = [];

function walk(obj, where) {
  if (Array.isArray(obj)) return obj.forEach((v, i) => walk(v, `${where}[${i}]`));
  if (obj && typeof obj === "object") {
    for (const [k, v] of Object.entries(obj)) {
      if (FORBIDDEN.has(k.toLowerCase())) problems.push(`${where}.${k}: identifier or weight`);
      walk(v, `${where}.${k}`);
    }
    if (Number.isInteger(obj.n_records) && obj.n_records < FLOOR) {
      for (const k of VALUE_KEYS) if (obj[k] !== null && obj[k] !== undefined) problems.push(`${where}.${k}: below the floor`);
    }
  }
}

function files(root) {
  return readdirSync(root).flatMap((name) => {
    const p = join(root, name);
    return statSync(p).isDirectory() ? files(p) : [p];
  });
}

for (const file of files(dir)) {
  const text = readFileSync(file, "utf8");
  if (AREA_CODE.test(text)) problems.push(`${file}: area codes present`);
  if (file.endsWith(".json")) {
    const data = JSON.parse(text);
    walk(data, file);
    if (file.endsWith("results.json")) {
      const anyPlaceholder = (data.measures ?? []).some((m) => m.placeholder);
      if (anyPlaceholder && !(data.meta?.placeholder && /placeholder/i.test(data.meta?.notice ?? ""))) {
        problems.push(`${file}: placeholder measures without the placeholder flag and notice`);
      }
    }
  } else if (!file.endsWith(".csv") && !file.endsWith(".gitkeep")) {
    problems.push(`${file}: only .json and .csv are allowed`);
  }
}

for (const p of problems) console.error(p);
console.log(`${problems.length} problem(s) in public/data`);
process.exit(problems.length ? 1 : 0);
