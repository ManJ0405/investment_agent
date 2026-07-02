"""Embedding client abstraction for RAG chunks/queries."""

from __future__ import annotations

import os
from typing import Sequence

from ollama import Client


class EmbeddingClient:
    def __init__(self, model: str = "nomic-embed-text", host: str | None = None) -> None:
        self.model = model
        self.client = Client(host=host or os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434"))

    def embed_text(self, text: str) -> list[float]:
        # Compatible with newer ollama-python API.
        resp = self.client.embed(model=self.model, input=text)
        vectors = resp.get("embeddings") or []
        if not vectors:
            raise RuntimeError("Embedding API returned empty vector")
        return vectors[0]

    def embed_many(self, texts: Sequence[str]) -> list[list[float]]:
        resp = self.client.embed(model=self.model, input=list(texts))
        vectors = resp.get("embeddings") or []
        if len(vectors) != len(texts):
            raise RuntimeError("Embedding API returned unexpected vector count")
        return vectors

