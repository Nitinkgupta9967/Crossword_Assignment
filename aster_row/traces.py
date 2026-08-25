from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from aster_row.paths import TRACES_DIR


def debug_enabled() -> bool:
    return os.getenv("AGENT_DEBUG", "").strip() in {"1", "true", "TRUE", "yes"}


def write_trace(event: dict[str, Any], session_id: str | None = None) -> dict[str, Any]:
    payload = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "session_id": session_id,
        **event,
    }
    if debug_enabled():
        TRACES_DIR.mkdir(parents=True, exist_ok=True)
        path = TRACES_DIR / "agent.jsonl"
        with path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(payload, ensure_ascii=False) + "\n")
        print(json.dumps(payload, indent=2, ensure_ascii=False), flush=True)
    return payload
