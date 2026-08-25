from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from aster_row.agent import Session, SupportAgent
from aster_row.eval_assert import evaluate_case
from aster_row.paths import ORIGINAL_CASES, VISIBLE_CASES


def load_cases() -> list[dict[str, Any]]:
    visible = json.loads(VISIBLE_CASES.read_text(encoding="utf-8"))["cases"]
    original = json.loads(ORIGINAL_CASES.read_text(encoding="utf-8"))["cases"]
    return visible + original


def run_case(agent: SupportAgent, case: dict[str, Any]) -> dict[str, Any]:
    session = Session()
    last = None
    for message in case["messages"]:
        last = agent.reply(session, message["content"])
    assert last is not None
    return {
        "answer": last.answer,
        "sources": last.sources,
        "handoff": last.handoff,
        "tool_calls": last.tool_calls,
        "asked_for_order_id": last.asked_for_order_id,
        "tool_called": bool(last.tool_calls),
    }


def run_suite(case_ids: list[str] | None = None, verbose: bool = True) -> dict[str, Any]:
    agent = SupportAgent()
    cases = [c for c in load_cases() if not case_ids or c["id"] in case_ids]
    if verbose:
        print(f"Running Aster & Row Evaluation Suite ({len(cases)} cases)...\n")
    results = []
    for idx, case in enumerate(cases, 1):
        if verbose:
            print(f"[{idx}/{len(cases)}] Running '{case['id']}' ({case['category']})... ", end="", flush=True)
        run = run_case(agent, case)
        graded = evaluate_case(case, run)
        graded["answer"] = run["answer"]
        results.append(graded)
        if verbose:
            mark = "PASS" if graded["passed"] else "FAIL"
            print(f"[{mark}]", flush=True)
    if verbose:
        print()



    by_category: dict[str, dict[str, int]] = {}
    for row in results:
        bucket = by_category.setdefault(row["category"], {"passed": 0, "total": 0})
        bucket["total"] += 1
        if row["passed"]:
            bucket["passed"] += 1

    # Map assignment reporting buckets
    reporting = {
        "retrieval": _sum_cats(by_category, {"retrieval", "multi-source-grounding", "source-conflict"}),
        "groundedness": _sum_cats(by_category, {"groundedness", "abstention", "prompt-security"}),
        "tool_use": _sum_cats(by_category, {"tool-use", "tool-reliability"}),
        "privacy": _sum_cats(by_category, {"privacy"}),
        "multi_turn": _sum_cats(by_category, {"conversation", "multi-turn"}),
    }

    passed = sum(1 for row in results if row["passed"])
    return {
        "passed": passed,
        "total": len(results),
        "by_category": by_category,
        "reporting": reporting,
        "results": results,
    }


def _sum_cats(by_category: dict, names: set[str]) -> dict[str, int]:
    passed = total = 0
    for name in names:
        bucket = by_category.get(name)
        if not bucket:
            continue
        passed += bucket["passed"]
        total += bucket["total"]
    return {"passed": passed, "total": total}


def write_report(payload: dict[str, Any], path: Path) -> None:
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
