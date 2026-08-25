from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

import yaml

from aster_row.paths import KNOWLEDGE_DIR


@dataclass
class Chunk:
    chunk_id: str
    filename: str
    heading: str
    text: str
    document_id: str
    title: str
    status: str
    audience: str
    policy_authority: str
    effective_date: str | None = None
    supersedes: str | None = None
    superseded_by: str | None = None
    customer_answering: bool = True
    metadata: dict = field(default_factory=dict)

    @property
    def is_authoritative(self) -> bool:
        if self.customer_answering is False:
            return False
        if self.status in {"superseded", "draft"}:
            return False
        if self.policy_authority not in {"official", "true"}:
            return False
        if self.audience == "internal" and self.policy_authority == "none":
            return False
        return self.status == "active" and self.policy_authority == "official"

    @property
    def retrieval_text(self) -> str:
        return f"{self.title}\n{self.heading}\n{self.text}"


_HEADING_RE = re.compile(r"^(#{1,3})\s+(.+)$", re.MULTILINE)


def _parse_front_matter(raw: str) -> tuple[dict, str]:
    if not raw.startswith("---"):
        return {}, raw
    parts = raw.split("---", 2)
    if len(parts) < 3:
        return {}, raw
    meta = yaml.safe_load(parts[1]) or {}
    return meta, parts[2].strip()


def load_chunks(knowledge_dir: Path | None = None) -> list[Chunk]:
    directory = knowledge_dir or KNOWLEDGE_DIR
    chunks: list[Chunk] = []
    for path in sorted(directory.glob("*.md")):
        raw = path.read_text(encoding="utf-8")
        meta, body = _parse_front_matter(raw)
        matches = list(_HEADING_RE.finditer(body))
        if not matches:
            sections = [("", body)]
        else:
            sections = []
            for i, match in enumerate(matches):
                start = match.end()
                end = matches[i + 1].start() if i + 1 < len(matches) else len(body)
                heading = match.group(2).strip()
                text = body[start:end].strip()
                if text:
                    sections.append((heading, text))
            intro = body[: matches[0].start()].strip()
            if intro:
                sections.insert(0, (matches[0].group(2).strip() + " (overview)", intro))

        for idx, (heading, text) in enumerate(sections):
            answering = meta.get("customer_answering", True)
            if isinstance(answering, str):
                answering = answering.lower() not in {"false", "no", "0"}
            chunks.append(
                Chunk(
                    chunk_id=f"{path.name}#{idx}",
                    filename=path.name,
                    heading=heading or meta.get("title", path.name),
                    text=text,
                    document_id=str(meta.get("document_id", "")),
                    title=str(meta.get("title", path.stem)),
                    status=str(meta.get("status", "unknown")),
                    audience=str(meta.get("audience", "customer")),
                    policy_authority=str(meta.get("policy_authority", "none")),
                    effective_date=str(meta.get("effective_date")) if meta.get("effective_date") else None,
                    supersedes=str(meta.get("supersedes")) if meta.get("supersedes") else None,
                    superseded_by=str(meta.get("superseded_by")) if meta.get("superseded_by") else None,
                    customer_answering=bool(answering),
                    metadata=dict(meta),
                )
            )
    return chunks
