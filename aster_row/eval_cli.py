from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from aster_row.eval_runner import run_suite, write_report
from aster_row.paths import ROOT


def main() -> None:
    parser = argparse.ArgumentParser(description="Run Aster & Row agent evaluations")
    parser.add_argument("--only", nargs="*", help="Optional case ids")
    parser.add_argument(
        "--out",
        default=str(ROOT / "evaluation" / "last-run.json"),
        help="Where to write the JSON report",
    )
    args = parser.parse_args()
    report = run_suite(args.only)
    write_report(report, Path(args.out))
    print(f"Passed {report['passed']} / {report['total']}")
    print("By category:")
    for name, bucket in sorted(report["by_category"].items()):
        print(f"  {name}: {bucket['passed']}/{bucket['total']}")
    print("Reporting buckets:")
    for name, bucket in report["reporting"].items():
        print(f"  {name}: {bucket['passed']}/{bucket['total']}")
    print()
    for row in report["results"]:
        mark = "PASS" if row["passed"] else "FAIL"
        print(f"[{mark}] {row['id']} ({row['category']})")
        for failure in row["failures"]:
            print(f"    - {failure}")
    sys.exit(0 if report["passed"] == report["total"] else 1)


if __name__ == "__main__":
    main()
