"""Command line.

``scottish-budget generate --placeholder``: the pre-release file.
``scottish-budget generate --reforms ID``: one measure through the engine
  (heavy: take the lock, one measure per process), written as a partial.
``scottish-budget generate --package provisional|final``: the scored
  measures together, for the figures that do not add across measures.
``scottish-budget combine [--provisional]``: partials into results.json and
  receipt.json.
``scottish-budget freeze``: the G0 record.
``scottish-budget reconcile --official CSV``: G3 gaps.
"""

import argparse
import json
import sys
from pathlib import Path

from scottish_budget.publication import manifest

DEFAULT_OUT = Path("dashboard/public/data/results.json")
DEFAULT_RECONCILIATION = Path("data_outputs/reconciliation.csv")


def _generate(args) -> int:
    from scottish_budget.pipeline import (
        PARTIAL_DIR,
        placeholder_results,
        run_one,
        write,
    )

    if args.dataset_sha256 and not args.dataset:
        print("--dataset-sha256 needs --dataset", file=sys.stderr)
        return 2
    if args.dataset:
        from scottish_budget.data_build import DATA_BUILD
        from scottish_budget.engine import check_dataset

        check_dataset(args.dataset, args.dataset_sha256 or DATA_BUILD.sha256)
    if args.placeholder:
        results = placeholder_results()
        path = write(results, args.out)
        print(json.dumps({"written": str(path), **manifest(results)}))
        return 0
    if args.package:
        from scottish_budget.pipeline import run_package

        path = run_package(
            args.package == "provisional",
            args.dataset,
            args.partial_dir or PARTIAL_DIR,
        )
        print(json.dumps({"partial": str(path)}))
        return 0
    if not args.reforms:
        print(
            "Give --placeholder, or --reforms ID for one measure per "
            "process (docs/RUNBOOK.md).",
            file=sys.stderr,
        )
        return 2
    path = run_one(args.reforms, args.dataset, args.partial_dir or PARTIAL_DIR)
    print(json.dumps({"partial": str(path)}))
    return 0


def _combine(args) -> int:
    from scottish_budget.pipeline import PARTIAL_DIR, combine, write

    results, receipt = combine(
        provisional=args.provisional,
        out_dir=args.partial_dir or PARTIAL_DIR,
        with_households=not args.no_households,
    )
    path = write(results, args.out)
    write(receipt, path.with_name("receipt.json"))
    print(json.dumps({"written": str(path), **manifest(results)}))
    return 0


def _freeze(args) -> int:
    from scottish_budget.engine import (
        check_dataset,
        git_identity,
        installed_versions,
        pinned_dataset,
    )

    pinned = pinned_dataset()
    versions = installed_versions()
    record = {
        **git_identity(),
        "versions": versions,
        "pinned_dataset": pinned,
        "engine_matches_build": versions.get("policyengine-uk")
        == pinned["policyengine_uk"],
    }
    if args.dataset:
        record["dataset_path"] = str(args.dataset)
        record["dataset_sha256"] = check_dataset(
            args.dataset, args.dataset_sha256 or pinned["sha256"]
        )
    print(json.dumps(record, indent=2))
    return 0


def _reconcile(args) -> int:
    from scottish_budget.reconcile import (
        read_official,
        reconcile,
        unreasoned,
        write_rows,
    )

    results = json.loads(Path(args.results).read_text())
    rows = reconcile(results, read_official(args.official))
    write_rows(rows, args.out)
    flagged = unreasoned(rows)
    print(
        json.dumps(
            {
                "written": str(args.out),
                "rows": len(rows),
                "flagged": len(flagged),
            }
        )
    )
    for row in flagged:
        print(
            f"  {row['measure_id']} {row['year']}: {row['flag']}",
            file=sys.stderr,
        )
    return 1 if flagged else 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(prog="scottish-budget")
    sub = parser.add_subparsers(dest="command", required=True)

    gen = sub.add_parser("generate", help="Placeholder file, or one measure")
    gen.add_argument("--placeholder", action="store_true")
    gen.add_argument("--reforms", metavar="ID", help="One measure id")
    gen.add_argument(
        "--package",
        choices=("provisional", "final"),
        help="All scored measures together (winners, poverty, bands)",
    )
    gen.add_argument("--dataset", type=Path, help="Explicit dataset path")
    gen.add_argument("--dataset-sha256", help="Refuse a different file")
    gen.add_argument("--partial-dir", type=Path)
    gen.add_argument("--out", type=Path, default=DEFAULT_OUT)
    gen.set_defaults(func=_generate)

    com = sub.add_parser("combine", help="Partials into results.json")
    com.add_argument("--provisional", action="store_true", help="G2 figures")
    com.add_argument("--no-households", action="store_true")
    com.add_argument("--partial-dir", type=Path)
    com.add_argument("--out", type=Path, default=DEFAULT_OUT)
    com.set_defaults(func=_combine)

    frz = sub.add_parser("freeze", help="Print the G0 record")
    frz.add_argument("--dataset", type=Path)
    frz.add_argument("--dataset-sha256")
    frz.set_defaults(func=_freeze)

    rec = sub.add_parser("reconcile", help="G3 gaps against official costings")
    rec.add_argument("--official", type=Path, required=True)
    rec.add_argument("--results", type=Path, default=DEFAULT_OUT)
    rec.add_argument("--out", type=Path, default=DEFAULT_RECONCILIATION)
    rec.set_defaults(func=_reconcile)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
