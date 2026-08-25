# Aster & Row AI Support Agent

A RAG-powered customer support assistant built for **Aster & Row** (an ecommerce brand selling bags, drinkware, and travel gear). The agent handles customer queries about returns, shipping, product details, and order tracking while enforcing policy constraints, privacy rules, and human handoff triggers.

---

## 📊 Evaluation Results

- **Pass Rate**: **20 / 20 (100%)**
- **Test Categories**:
  - `retrieval`: 4/4
  - `groundedness`: 6/6
  - `tool_use`: 7/7
  - `privacy`: 1/1
  - `multi_turn`: 2/2

Run the suite anytime with:
```bash
python -m aster_row.eval_cli
```

---

## 🚀 Quickstart & Setup

### 1. Prerequisites
- Python 3.10+
- Anthropic Claude API key (or OpenAI API key)

### 2. Installation
```bash
# Install dependencies
python -m pip install -r requirements.txt
```

### 3. Environment Configuration
Create a `.env` file in the root directory:
```env
ANTHROPIC_API_KEY=your_anthropic_api_key_here
ANTHROPIC_MODEL=claude-sonnet-4-5-20250929
```

### 4. Running the Agent

- **Web Interface (FastAPI)**:
  ```bash
  python -m aster_row.web
  ```
  Open `http://127.0.0.1:8000` in your browser.

- **Terminal CLI**:
  ```bash
  python -m aster_row.cli
  ```

- **Automated Test Suite**:
  ```bash
  python -m aster_row.eval_cli
  ```

---

## 🏗️ Architecture & Core Components

```text
ai-agent-intern-test/
├── aster_row/
│   ├── agent.py          # Main support agent coordinator & prompt rules
│   ├── retrieve.py       # BM25 retrieval + metadata precedence & conflict detection
│   ├── knowledge.py      # Knowledge base markdown chunking & metadata parser
│   ├── orders.py         # OrderStore lookup tool & PII filtering
│   ├── llm.py            # LLM provider wrapper (Anthropic Claude / OpenAI)
│   ├── web.py           # FastAPI Web Application & UI
│   ├── cli.py           # Interactive terminal CLI
│   ├── eval_runner.py    # Evaluation suite execution pipeline
│   ├── eval_assert.py    # Evaluation assertion rules
│   └── eval_cli.py      # Evaluation CLI entrypoint
├── data/
│   ├── orders.json      # Mock order database snapshot
│   └── orders-data-dictionary.md
├── evaluation/
│   ├── visible-cases.json   # Candidate evaluation cases
│   └── original-cases.json  # Regression evaluation cases
└── knowledge-base/      # Official policy & product markdown files
```

### Technical Highlights
1. **Metadata Precedence Retrieval (`retrieve.py`)**: Uses BM25 keyword matching weighted by YAML frontmatter. Active official policies receive a score boost (`1.65x`), while legacy policies (`0.08x`) and internal scratchpads (`0.04x`) are penalized.
2. **Conflict Detection**: Automatically detects when official documents contradict each other (e.g. Breeze Tumbler dishwasher safety in Product Care vs Product Card) and triggers a human handoff instead of guessing.
3. **PII & Order Privacy (`orders.py`)**: Normalizes order IDs (`ord-1007` -> `ORD-1007`), strips sensitive fields (email, address, internal notes, risk scores), and clears stale tracking dates for cancelled orders.

---

## 📔 Bug Diary

### 1. Risk Score Over-Redaction
- **Issue**: The initial secret scrubber used regex `\b{score}\b` to sanitize `risk_score` values. Because mock orders contained risk scores of `7`, `5`, and `9`, valid numbers in policy answers (like `"within 7 calendar days"` or `"5–9 business days"`) were being redacted as `"[redacted]"`.
- **Fix**: Scoped risk score redaction specifically to `risk score:` key-value patterns rather than standalone digits.

### 2. Order Status Invention on Missing ID
- **Issue**: When asking the user for a missing order ID (*"Where is my order?"*), the model sometimes outputted phrases like *"To check if your package has shipped..."*. The word `"shipped"` violated the assertion rule against inventing order status before a lookup occurred.
- **Fix**: Added a post-processing guard forcing a clean clarification question whenever an order ID is missing.

### 3. Cross-Turn Conflict Leakage
- **Issue**: In multi-turn chat sessions, appending previous search queries caused a Breeze Tumbler dishwasher conflict from an earlier turn to leak into an unrelated question 5 turns later (e.g. order cancellation).
- **Fix**: Scoped `detect_conflicts()` so conflict warnings only trigger when the user's current query actually pertains to that product/cleaning topic.

---

## 🛠️ Known Limitations & Future Improvements

- **Hybrid Dense Retrieval**: BM25 keyword search works well for policy lookups, but adding vector embeddings (e.g. `text-embedding-3-small` + Cohere rerank) would improve semantic matching for long natural queries.
- **Database Integration**: Replace the static `orders.json` snapshot with an active SQL/ORM database connection for live status updates.
- **Streaming UI**: Implement Server-Sent Events (SSE) streaming in `web.py` for real-time token streaming.

---

## 🤖 AI Coding Tools Disclosure

- **Tools Used**: AI coding tools (Claude / ChatGPT) were used during development for quick boilerplate generation, refactoring, and debugging test assertions.
- **Example of Correcting an AI Error**: An AI tool initially suggested replacing all single-digit integers matching `risk_score` values across the response string, which broke policy answers containing `"7 days"` or `"5–9 days"`. I fixed this by scoping secret scrubbing to explicit key-value contexts.
