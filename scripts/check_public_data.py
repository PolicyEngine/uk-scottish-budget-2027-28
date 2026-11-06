#!/usr/bin/env python3
"""Guard the public data folder (scaled down from the Autumn Budget repo).

The repository is public and the figures come from UKDS-licensed survey
microdata. This fails if any file under dashboard/public/data:

1. carries a record identifier or a weight (by key name);
2. carries a cell below the survey-household floor with a value in it;
3. carries area codes (Scottish council S12, Scottish Parliament S16,
   UK constituency S14/E14/W07/N06, data zone S01), which would need a
   reviewed reference-geography file first;
4. is not JSON or CSV.

Usage: python scripts/check_public_data.py [folder]
"""

import csv
import json
import re
import sys
from pathlib import Path

FLOOR = 10
FORBIDDEN = {
    "household_id",
    "person_id",
    "benunit_id",
    "household_weight",
    "person_weight",
    "benunit_weight",
    "weight",
}
AREA_CODE = re.compile(r"\b(S12|S14|S16|S01|E14|W07|N06)\d{6}\b")
VALUE_KEYS = ("avg_change_gbp", "pct_change", "value")


def _walk(obj, where, problems):
    if isinstance(obj, dict):
        for key, value in obj.items():
            if str(key).lower() in FORBIDDEN:
                problems.append(f"{where}.{key}: identifier or weight")
            _walk(value, f"{where}.{key}", problems)
        n = obj.get("n_records")
        if isinstance(n, int) and n < FLOOR:
            for key in VALUE_KEYS:
                if obj.get(key) is not None:
                    problems.append(
                        f"{where}.{key}: value on a cell of {n} records"
                    )
    elif isinstance(obj, list):
        for i, value in enumerate(obj):
            _walk(value, f"{where}[{i}]", problems)


def check_file(path: Path) -> list[str]:
    problems = []
    text = path.read_text(encoding="utf-8")
    if AREA_CODE.search(text):
        problems.append(f"{path}: area codes present")
    if path.suffix == ".json":
        _walk(json.loads(text), str(path), problems)
    elif path.suffix == ".csv":
        reader = csv.DictReader(text.splitlines())
        for field in reader.fieldnames or []:
            if field.lower() in FORBIDDEN:
                problems.append(f"{path}: column {field}")
        for i, row in enumerate(reader):
            n = row.get("n_records")
            if n and n.isdigit() and int(n) < FLOOR:
                if any(row.get(k) not in (None, "") for k in VALUE_KEYS):
                    problems.append(f"{path} row {i}: below the floor")
    else:
        problems.append(f"{path}: only .json and .csv are allowed")
    return problems


def check_folder(folder: Path) -> list[str]:
    problems = []
    for path in sorted(folder.rglob("*")):
        if path.is_file() and path.name != ".gitkeep":
            problems.extend(check_file(path))
    return problems


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    folder = Path(argv[0] if argv else "dashboard/public/data")
    problems = check_folder(folder)
    for problem in problems:
        print(problem, file=sys.stderr)
    print(f"{len(problems)} problem(s) in {folder}")
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
