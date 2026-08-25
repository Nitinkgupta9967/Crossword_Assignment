# Aster & Row AI Support Agent

A RAG-powered customer support assistant built for **Aster & Row** (an ecommerce brand selling bags, drinkware, and travel gear). The agent handles customer queries about returns, shipping, product details, and order tracking while enforcing document precedence rules, privacy guardrails, and human handoff triggers.

---

## 🏆 Evaluation Summary

| Metric | Score | Details |
| :--- | :---: | :--- |
| **Total Test Suite Pass Rate** | **20 / 20 (100%)** | Clean run across all visible and custom regression test cases. |
| **Retrieval & Document Precedence** | **4 / 4 (100%)** | Correctly prefers active official policies over legacy/internal docs. |
| **Groundedness & Safe Abstention** | **6 / 6 (100%)** | Refuses unverified claims (e.g. vegan certification), safe handoffs. |
| **Tool Use & Order Reliability** | **7 / 7 (100%)** | Accurate ID normalization, no stale ETA quoting, PII protection. |
| **Privacy Protection** | **1 / 1 (100%)** | Never exposes email, shipping address, warehouse notes, or risk scores. |
| **Multi-Turn & Conversation State** | **2 / 2 (100%)** | Retains session context across multi-turn user queries. |

Run the automated evaluation suite anytime with:
```bash
python -m aster_row.eval_cli
```

---

## 🚀 Quickstart & Setup

### 1. Prerequisites
- Python 3.10+
- Anthropic Claude API Key (or OpenAI API key)

### 2. Installation
```bash
# Clone the repository
git clone https://github.com/Nitinkgupta9967/Crossword_Assignment.git
cd Crossword_Assignment

# Install dependencies
python -m pip install -r requirements.txt
```

### 3. Environment Setup
Create a `.env` file in the root directory:
```env
ANTHROPIC_API_KEY=your_anthropic_api_key_here
ANTHROPIC_MODEL=claude-sonnet-4-5-20250929
```

### 4. Running the Project

- **Run Automated Evaluation Suite**:
  ```bash
  python -m aster_row.eval_cli
  ```

- **Run Interactive Terminal CLI**:
  ```bash
  python -m aster_row.cli
  ```
  *(Add `--debug` to output structured JSON trace logs)*.

---

## 🏛️ System Architecture

```text
ai-agent-intern-test/
├── aster_row/
│   ├── agent.py          # Core agent coordinator, system prompt rules, & post-processing
│   ├── retrieve.py       # BM25 retriever + document precedence scoring & conflict detection
│   ├── knowledge.py      # Knowledge base markdown chunking & metadata parser
│   ├── orders.py         # OrderStore lookup tool with PII redaction & stale field stripping
│   ├── llm.py            # LLM provider completion wrapper (Anthropic Claude / OpenAI)
│   ├── cli.py           # Interactive terminal CLI interface
│   ├── eval_runner.py    # Evaluation suite execution pipeline
│   ├── eval_assert.py    # Evaluation assertion rules
│   ├── eval_cli.py      # Evaluation CLI entrypoint
│   ├── paths.py          # Centralized repository paths
│   └── traces.py         # Structured JSON logging to traces/agent.jsonl
├── data/
│   ├── orders.json      # Mock order database snapshot
│   └── orders-data-dictionary.md
├── evaluation/
│   ├── visible-cases.json   # Candidate evaluation cases
│   └── original-cases.json  # Regression evaluation cases
├── knowledge-base/      # Official policy & product markdown files
├── README.md
├── requirements.txt
└── .env.example
```

### Key Technical Highlights
1. **Metadata Precedence Retrieval (`retrieve.py`)**: Uses BM25 keyword matching weighted by YAML frontmatter. Active official policies receive a score boost (`1.65x`), while legacy policies (`0.08x`) and internal scratchpads (`0.04x`) are penalized.
2. **Conflict Detection (`detect_conflicts`)**: Automatically detects when official documents contradict each other (e.g. Breeze Tumbler dishwasher safety in Product Care vs Product Card) and triggers a human handoff instead of guessing.
3. **Order Tool & PII Defense (`orders.py`)**: Normalizes order IDs (`ord-1007` -> `ORD-1007`), strips sensitive fields (email, address, internal notes, risk scores), and clears stale tracking dates for cancelled orders.

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

---

## 🤖 AI Coding Tools Disclosure

- **Tools Used**: AI coding tools (Claude / ChatGPT) were used during development for quick boilerplate generation, refactoring, and debugging test assertions.
- **Example of Correcting an AI Error**: An AI tool initially suggested replacing all single-digit integers matching `risk_score` values across the response string, which broke policy answers containing `"7 days"` or `"5–9 days"`. I fixed this by scoping secret scrubbing to explicit key-value contexts.
