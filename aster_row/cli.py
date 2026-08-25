from __future__ import annotations

import argparse
import json
import sys

from aster_row.agent import Session, SupportAgent


def main() -> None:
    parser = argparse.ArgumentParser(description="Aster & Row support agent CLI")
    parser.add_argument("--debug", action="store_true", help="Print JSON traces")
    args = parser.parse_args()
    if args.debug:
        import os

        os.environ["AGENT_DEBUG"] = "1"

    agent = SupportAgent()
    session = Session()
    print("Aster & Row support agent. Type a question, or /quit.")
    print("Sources and handoff flags appear after each answer.\n")
    while True:
        try:
            user = input("you> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            return
        if not user or user in {"/quit", "/exit"}:
            return
        result = agent.reply(session, user)
        print()
        print(result.answer)
        print()
        if result.handoff:
            print("[handoff recommended]", result.handoff_reason or "")
        if result.sources:
            print("[sources]", ", ".join(sorted({s['filename'] for s in result.sources})))
        print()


if __name__ == "__main__":
    main()
