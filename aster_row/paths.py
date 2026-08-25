from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
KNOWLEDGE_DIR = ROOT / "knowledge-base"
ORDERS_PATH = ROOT / "data" / "orders.json"
VISIBLE_CASES = ROOT / "evaluation" / "visible-cases.json"
ORIGINAL_CASES = ROOT / "evaluation" / "original-cases.json"
TRACES_DIR = ROOT / "traces"
