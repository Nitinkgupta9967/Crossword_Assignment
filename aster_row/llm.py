from __future__ import annotations

import json
import os
import re
from typing import Any

from dotenv import load_dotenv

load_dotenv()

DEFAULT_OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
DEFAULT_ANTHROPIC_MODEL = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-5-20250929")




def _complete_json_anthropic(system: str, user: str, model: str | None = None) -> dict[str, Any]:
    import anthropic

    api_key = os.getenv("ANTHROPIC_API_KEY")
    client = anthropic.Anthropic(api_key=api_key)
    model_name = model or DEFAULT_ANTHROPIC_MODEL

    prompt_user = (
        user
        + "\n\nIMPORTANT: Respond with ONLY a single, valid JSON object matching the requested schema. "
        "Do NOT wrap in markdown triple backticks (```json) or add any extra prose."
    )

    response = client.messages.create(
        model=model_name,
        max_tokens=2048,
        temperature=0,
        system=system,
        messages=[{"role": "user", "content": prompt_user}],
    )

    content = response.content[0].text.strip()
    if content.startswith("```"):
        lines = content.splitlines()
        if lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        content = "\n".join(lines).strip()

    try:
        return json.loads(content)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", content, re.DOTALL)
        if match:
            return json.loads(match.group(0))
        raise


def _complete_json_openai(system: str, user: str, model: str | None = None) -> dict[str, Any]:
    from openai import OpenAI

    api_key = os.getenv("OPENAI_API_KEY")
    kwargs: dict[str, Any] = {"api_key": api_key}
    base = os.getenv("OPENAI_BASE_URL")
    if base:
        kwargs["base_url"] = base
    client = OpenAI(**kwargs)

    response = client.chat.completions.create(
        model=model or DEFAULT_OPENAI_MODEL,
        temperature=0,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
    )
    content = response.choices[0].message.content or "{}"
    return json.loads(content)


def complete_json(system: str, user: str, model: str | None = None) -> dict[str, Any]:
    if os.getenv("ANTHROPIC_API_KEY"):
        return _complete_json_anthropic(system, user, model)
    elif os.getenv("OPENAI_API_KEY"):
        return _complete_json_openai(system, user, model)
    else:
        raise RuntimeError(
            "Neither ANTHROPIC_API_KEY nor OPENAI_API_KEY is set in environment. "
            "Copy .env.example to .env and add your API key."
        )

