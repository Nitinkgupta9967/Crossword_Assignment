from __future__ import annotations

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

from aster_row.agent import Session, SupportAgent

app = FastAPI(title="Aster & Row Support Agent")
agent = SupportAgent()
SESSIONS: dict[str, Session] = {}

PAGE = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1"/>
  <title>Aster &amp; Row | Support Assistant</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
  <style>
    :root {
      --bg: #f8fafc;
      --surface: #ffffff;
      --border: #e2e8f0;
      --text: #0f172a;
      --text-muted: #64748b;
      --primary: #1e293b;
      --primary-hover: #0f172a;
      --user-bg: #1e293b;
      --user-text: #ffffff;
      --agent-bg: #ffffff;
      --accent: #2563eb;
      --handoff-bg: #fef2f2;
      --handoff-border: #fecaca;
      --handoff-text: #991b1b;
      --source-bg: #f1f5f9;
      --source-text: #334155;
    }

    * { box-sizing: border-box; margin: 0; padding: 0; }

    body {
      font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      background: var(--bg);
      color: var(--text);
      display: flex;
      flex-direction: column;
      height: 100vh;
      max-width: 820px;
      margin: 0 auto;
      padding: 0 16px;
    }

    header {
      padding: 24px 0 18px;
      border-bottom: 1px solid var(--border);
      background: var(--bg);
      display: flex;
      justify-content: space-between;
      align-items: center;
    }

    .brand {
      display: flex;
      align-items: center;
      gap: 10px;
    }

    .brand-logo {
      width: 36px;
      height: 36px;
      background: var(--primary);
      color: #fff;
      border-radius: 10px;
      display: flex;
      align-items: center;
      justify-content: center;
      font-weight: 700;
      font-size: 16px;
    }

    .brand-title {
      font-size: 18px;
      font-weight: 700;
      letter-spacing: -0.02em;
    }

    .brand-sub {
      font-size: 12px;
      color: var(--text-muted);
    }

    .status-badge {
      display: inline-flex;
      align-items: center;
      gap: 6px;
      font-size: 12px;
      font-weight: 500;
      color: #166534;
      background: #f0fdf4;
      border: 1px solid #bbf7d0;
      padding: 4px 10px;
      border-radius: 20px;
    }

    .status-dot {
      width: 7px;
      height: 7px;
      background: #22c55e;
      border-radius: 50%;
    }

    #chat-log {
      flex: 1;
      overflow-y: auto;
      padding: 20px 0;
      display: flex;
      flex-direction: column;
      gap: 16px;
      scroll-behavior: smooth;
    }

    .message {
      display: flex;
      flex-direction: column;
      max-width: 85%;
      animation: fadeIn 0.25s ease-out;
    }

    @keyframes fadeIn {
      from { opacity: 0; transform: translateY(6px); }
      to { opacity: 1; transform: translateY(0); }
    }

    .message.user {
      align-self: flex-end;
    }

    .message.agent {
      align-self: flex-start;
      width: 100%;
      max-width: 100%;
    }

    .bubble {
      padding: 14px 18px;
      border-radius: 16px;
      font-size: 14px;
      line-height: 1.6;
    }

    .message.user .bubble {
      background: var(--user-bg);
      color: var(--user-text);
      border-bottom-right-radius: 4px;
    }

    .message.agent .bubble {
      background: var(--agent-bg);
      border: 1px solid var(--border);
      color: var(--text);
      border-bottom-left-radius: 4px;
      box-shadow: 0 1px 3px rgba(0,0,0,0.03);
    }

    .bubble p { margin-bottom: 10px; }
    .bubble p:last-child { margin-bottom: 0; }
    .bubble ul, .bubble ol { margin: 8px 0 8px 20px; }
    .bubble li { margin-bottom: 4px; }
    .bubble strong { font-weight: 600; }

    .handoff-banner {
      margin-top: 10px;
      padding: 10px 14px;
      background: var(--handoff-bg);
      border: 1px solid var(--handoff-border);
      color: var(--handoff-text);
      border-radius: 10px;
      font-size: 13px;
      font-weight: 500;
      display: flex;
      align-items: center;
      gap: 8px;
    }

    .sources-container {
      margin-top: 10px;
      display: flex;
      flex-wrap: wrap;
      gap: 6px;
      align-items: center;
    }

    .sources-label {
      font-size: 11px;
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: 0.05em;
      color: var(--text-muted);
      margin-right: 4px;
    }

    .source-chip {
      background: var(--source-bg);
      color: var(--source-text);
      border: 1px solid #e2e8f0;
      border-radius: 6px;
      padding: 3px 8px;
      font-size: 12px;
      font-weight: 500;
      display: inline-flex;
      align-items: center;
      gap: 4px;
    }

    .typing-indicator {
      display: inline-flex;
      align-items: center;
      gap: 4px;
      padding: 12px 16px;
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: 16px;
      width: fit-content;
    }

    .typing-dot {
      width: 6px;
      height: 6px;
      background: var(--text-muted);
      border-radius: 50%;
      animation: bounce 1.4s infinite ease-in-out both;
    }

    .typing-dot:nth-child(1) { animation-delay: -0.32s; }
    .typing-dot:nth-child(2) { animation-delay: -0.16s; }

    @keyframes bounce {
      0%, 80%, 100% { transform: scale(0); }
      40% { transform: scale(1); }
    }

    footer {
      padding: 16px 0 24px;
      background: var(--bg);
    }

    form {
      display: flex;
      gap: 8px;
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: 28px;
      padding: 6px 8px 6px 18px;
      box-shadow: 0 4px 12px rgba(0, 0, 0, 0.03);
      transition: border-color 0.2s ease;
    }

    form:focus-within {
      border-color: var(--accent);
    }

    input {
      flex: 1;
      border: none;
      outline: none;
      background: transparent;
      font-family: inherit;
      font-size: 14px;
      color: var(--text);
    }

    input::placeholder {
      color: #94a3b8;
    }

    button[type="submit"] {
      background: var(--primary);
      color: #fff;
      border: none;
      border-radius: 20px;
      padding: 8px 18px;
      font-family: inherit;
      font-size: 13px;
      font-weight: 600;
      cursor: pointer;
      transition: background 0.2s ease;
      display: flex;
      align-items: center;
      gap: 6px;
    }

    button[type="submit"]:hover {
      background: var(--primary-hover);
    }

    button[type="submit"]:disabled {
      opacity: 0.6;
      cursor: not-allowed;
    }
  </style>
</head>
<body>
  <header>
    <div class="brand">
      <div class="brand-logo">A&amp;R</div>
      <div>
        <div class="brand-title">Aster &amp; Row</div>
        <div class="brand-sub">RAG Customer Support Agent</div>
      </div>
    </div>
    <div class="status-badge">
      <span class="status-dot"></span> Active
    </div>
  </header>

  <div id="chat-log">
    <div class="message agent">
      <div class="bubble">
        Hello! I'm the Aster &amp; Row AI support assistant. How can I help you today with returns, order tracking, products, or shipping policies?
      </div>
    </div>
  </div>

  <footer>
    <form id="chat-form" onsubmit="return false;">
      <input id="user-input" autocomplete="off" placeholder="Ask a question or enter order ID (e.g. ORD-1007)..." />
      <button type="submit" id="send-btn">
        <span>Send</span>
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><line x1="22" y1="2" x2="11" y2="13"></line><polygon points="22 2 15 22 11 13 2 9 22 2"></polygon></svg>
      </button>
    </form>
  </footer>

  <script>
    var sessionId = 'sess_' + Math.random().toString(36).substring(2, 11);
    var chatLog = document.getElementById('chat-log');
    var chatForm = document.getElementById('chat-form');
    var userInput = document.getElementById('user-input');
    var sendBtn = document.getElementById('send-btn');

    function stripTextSources(text) {
      if (!text) return '';
      return String(text).replace(/(?:---|)\s*(?:##\s*Sources|Sources:)\s*[\s\S]*$/i, '').trim();
    }

    function formatMarkdown(text) {
      if (!text) return '';
      var html = String(text)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/\\*\\*(.*?)\\*\\*/g, '<strong>$1</strong>')
        .replace(/\\*(.*?)\\*/g, '<em>$1</em>')
        .replace(/\\n\\n/g, '</p><p>')
        .replace(/\\n/g, '<br>');
      return '<p>' + html + '</p>';
    }

    function appendMessage(role, text, sources, handoff, handoffReason) {
      var msgDiv = document.createElement('div');
      msgDiv.className = 'message ' + role;

      var cleanText = (role === 'agent' && sources && sources.length > 0) ? stripTextSources(text) : text;
      var contentHtml = '<div class="bubble">' + formatMarkdown(cleanText);

      if (handoff) {
        contentHtml += '<div class="handoff-banner"><span>🤝</span><span>Human Specialist Handoff Recommended' + (handoffReason ? ': ' + handoffReason : '') + '</span></div>';
      }

      if (sources && sources.length > 0) {
        contentHtml += '<div class="sources-container"><span class="sources-label">Sources:</span>';
        for (var i = 0; i < sources.length; i++) {
          var s = sources[i];
          contentHtml += '<span class="source-chip">📄 ' + s.filename + ' (' + s.heading + ')</span>';
        }
        contentHtml += '</div>';
      }

      contentHtml += '</div>';
      msgDiv.innerHTML = contentHtml;
      chatLog.appendChild(msgDiv);
      chatLog.scrollTop = chatLog.scrollHeight;
    }

    function showTypingIndicator() {
      var indicator = document.createElement('div');
      indicator.id = 'typing-indicator';
      indicator.className = 'message agent';
      indicator.innerHTML = '<div class="typing-indicator"><div class="typing-dot"></div><div class="typing-dot"></div><div class="typing-dot"></div></div>';
      chatLog.appendChild(indicator);
      chatLog.scrollTop = chatLog.scrollHeight;
    }

    function hideTypingIndicator() {
      var indicator = document.getElementById('typing-indicator');
      if (indicator) indicator.remove();
    }

    async function processMessage(text) {
      if (!text) return;
      appendMessage('user', text);
      userInput.value = '';
      sendBtn.disabled = true;
      showTypingIndicator();

      try {
        var res = await fetch('/api/chat', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ session_id: sessionId, message: text })
        });
        var data = await res.json();
        hideTypingIndicator();
        appendMessage('agent', data.answer, data.sources, data.handoff, data.handoff_reason);
      } catch (err) {
        hideTypingIndicator();
        appendMessage('agent', 'An error occurred while connecting to the assistant. Please try again.');
      } finally {
        sendBtn.disabled = false;
        userInput.focus();
      }
    }

    chatForm.addEventListener('submit', function(e) {
      e.preventDefault();
      var text = userInput.value.trim();
      processMessage(text);
      return false;
    });

    userInput.addEventListener('keydown', function(e) {
      if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        var text = userInput.value.trim();
        processMessage(text);
      }
    });
  </script>
</body>
</html>
"""


class ChatIn(BaseModel):
    session_id: str
    message: str


@app.get("/", response_class=HTMLResponse)
def home() -> str:
    return PAGE


@app.post("/api/chat")
def chat(body: ChatIn):
    session = SESSIONS.setdefault(body.session_id, Session(session_id=body.session_id))
    result = agent.reply(session, body.message)
    return {
        "answer": result.answer,
        "sources": result.sources,
        "handoff": result.handoff,
        "handoff_reason": result.handoff_reason,
        "trace": result.trace if result.trace else None,
    }


def main() -> None:
    import uvicorn

    uvicorn.run("aster_row.web:app", host="127.0.0.1", port=8000, reload=False)


if __name__ == "__main__":
    main()
