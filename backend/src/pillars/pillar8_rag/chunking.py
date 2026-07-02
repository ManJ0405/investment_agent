"""Chunking utilities for SEC filing text."""

from __future__ import annotations

import re


SECTION_PATTERN = re.compile(r"\b(item\s+(?:1a|1b|2|3|7|7a|8))\b", flags=re.IGNORECASE)


def split_sections(text: str) -> list[tuple[str, str]]:
    """Split filing text into coarse Item sections."""
    matches = list(SECTION_PATTERN.finditer(text))
    if not matches:
        return [("full_document", text)]

    sections: list[tuple[str, str]] = []
    for idx, match in enumerate(matches):
        start = match.start()
        end = matches[idx + 1].start() if idx + 1 < len(matches) else len(text)
        title = match.group(1).lower().replace(" ", "_")
        chunk = text[start:end].strip()
        if chunk:
            sections.append((title, chunk))
    return sections


def sliding_chunks(text: str, chunk_size: int = 1200, overlap: int = 150) -> list[str]:
    """Simple sliding-window chunker by characters."""
    if len(text) <= chunk_size:
        return [text]
    chunks: list[str] = []
    step = max(1, chunk_size - overlap)
    for start in range(0, len(text), step):
        part = text[start : start + chunk_size].strip()
        if part:
            chunks.append(part)
        if start + chunk_size >= len(text):
            break
    return chunks

