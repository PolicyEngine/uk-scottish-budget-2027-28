"""Command line: ``scottish-budget generate --placeholder``."""

import argparse
import json
from pathlib import Path

from scottish_budget.pipeline import (
    model_results,
    placeholder_results,
    write,
)
from scottish_budget.publication import manifest

DEFAULT_OUT = Path("dashboard/public/data/results.json")


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(prog="scottish-budget")
    sub = parser.add_subparsers(dest="command", required=True)
    gen = sub.add_parser("generate", help="Write results.json")
    gen.add_argument(
        "--placeholder",
        action="store_true",
        help="Write the pre-release placeholder file (no data needed)",
    )
    gen.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args(argv)

    results = placeholder_results() if args.placeholder else model_results()
    path = write(results, args.out)
    print(json.dumps({"written": str(path), **manifest(results)}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
