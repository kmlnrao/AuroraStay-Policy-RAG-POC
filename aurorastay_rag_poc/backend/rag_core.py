"""Local, policy-grounded RAG core with optional hosted generation."""

from __future__ import annotations

import json
import math
import os
import re
from collections import Counter
from pathlib import Path

import faiss
import fitz
import numpy as np
import requests

STOP = {
    "a", "an", "and", "are", "as", "at", "be", "by", "can", "do", "does",
    "for", "from", "how", "i", "in", "is", "it", "me", "my", "of", "on",
    "or", "the", "to", "what", "when", "where", "who", "will", "with",
}
ABSTENTION = "The available AuroraStay policy documents do not contain enough information to answer this question. Please verify with the property team."


def tokens(text: str) -> list[str]:
    return [
        t for t in re.findall(r"[a-z0-9]+", text.lower())
        if len(t) > 1 and t not in STOP
    ]


def read_policy_pages(data_dir: str | Path) -> list[dict]:
    """Extract text by page so every retrieved passage can be cited."""
    pages = []
    for path in sorted(Path(data_dir).glob("*.pdf")):
        doc = fitz.open(path)
        for number, page in enumerate(doc, start=1):
            text = re.sub(r"\s+", " ", page.get_text()).strip()
            if text:
                pages.append({
                    "text": text,
                    "source": path.name,
                    "page": number,
                })
    if not pages:
        raise RuntimeError(f"No readable policy PDF pages found in {data_dir}")
    return pages


def chunk_pages(pages: list[dict], chunk_words: int = 120, overlap: int = 20) -> list[dict]:
    chunks = []
    for page in pages:
        words = page["text"].split()
        start = 0
        while start < len(words):
            end = min(start + chunk_words, len(words))
            text = " ".join(words[start:end]).strip()
            if text:
                chunks.append({
                    "text": text,
                    "source": page["source"],
                    "page": page["page"],
                })
            if end == len(words):
                break
            start = max(end - overlap, start + 1)
    return chunks


class TfidfFaissStore:
    """Corpus-fitted local TF-IDF vectors indexed by FAISS cosine similarity."""

    def __init__(self, chunks, vocabulary, idf, index):
        self.chunks = chunks
        self.vocabulary = vocabulary
        self.idf = idf
        self.word_index = {word: i for i, word in enumerate(vocabulary)}
        self.index = index

    @classmethod
    def build(cls, chunks):
        tokenized = [tokens(c["text"]) for c in chunks]
        vocabulary = sorted({word for row in tokenized for word in row})
        if not vocabulary:
            raise ValueError("The policy corpus produced no indexable terms.")
        df = Counter(word for row in tokenized for word in set(row))
        n = max(len(tokenized), 1)
        idf = [math.log((1 + n) / (1 + df[word])) + 1 for word in vocabulary]
        store = cls(chunks, vocabulary, idf, None)
        matrix = np.vstack([store.embed(c["text"]) for c in chunks]).astype("float32")
        index = faiss.IndexFlatIP(len(vocabulary))
        index.add(matrix)
        store.index = index
        return store

    def embed(self, text):
        counts = Counter(t for t in tokens(text) if t in self.word_index)
        vector = np.zeros(len(self.vocabulary), dtype="float32")
        for word, count in counts.items():
            i = self.word_index[word]
            vector[i] = (1 + math.log(count)) * self.idf[i]
        norm = float(np.linalg.norm(vector))
        if norm:
            vector /= norm
        return vector

    def search(self, query, k=3):
        vector = self.embed(query).reshape(1, -1)
        if not np.any(vector):
            return []
        scores, indices = self.index.search(vector, min(max(int(k), 1), len(self.chunks)))
        found = []
        for score, idx in zip(scores[0], indices[0]):
            if idx < 0:
                continue
            item = dict(self.chunks[int(idx)])
            item["score"] = float(score)
            found.append(item)
        return found

    def save(self, path):
        target = Path(path)
        target.mkdir(parents=True, exist_ok=True)
        faiss.write_index(self.index, str(target / "policy.faiss"))
        (target / "store.json").write_text(json.dumps({
            "chunks": self.chunks,
            "vocabulary": self.vocabulary,
            "idf": self.idf,
            "embedding": "local normalized TF-IDF",
            "similarity": "cosine (FAISS inner product on normalized vectors)",
        }, ensure_ascii=False, indent=2), encoding="utf-8")

    @classmethod
    def load(cls, path):
        target = Path(path)
        state = json.loads((target / "store.json").read_text(encoding="utf-8"))
        index = faiss.read_index(str(target / "policy.faiss"))
        return cls(state["chunks"], state["vocabulary"], state["idf"], index)


class OpenAIFaissStore:
    """FAISS cosine index over OpenAI text-embedding-3-small vectors."""

    DEFAULT_MODEL = "text-embedding-3-small"

    def __init__(self, chunks, index, model=DEFAULT_MODEL):
        self.chunks = chunks
        self.index = index
        self.model = model

    @staticmethod
    def _embed_texts(texts, model):
        api_key = os.getenv("OPENAI_API_KEY", "").strip()
        if not api_key:
            raise RuntimeError(
                "OpenAI embeddings are selected but OPENAI_API_KEY is not configured."
            )
        response = requests.post(
            "https://api.openai.com/v1/embeddings",
            headers={"Authorization": f"Bearer {api_key}"},
            json={"model": model, "input": texts},
            timeout=60,
        )
        if not response.ok:
            raise RuntimeError(
                f"OpenAI embedding request failed (HTTP {response.status_code})."
            )
        vectors = sorted(response.json()["data"], key=lambda item: item["index"])
        matrix = np.asarray([item["embedding"] for item in vectors], dtype="float32")
        if matrix.ndim != 2 or len(matrix) != len(texts):
            raise RuntimeError("OpenAI returned an invalid embedding matrix.")
        return matrix

    @classmethod
    def build(cls, chunks, model=None, batch_size=64):
        selected_model = model or os.getenv("OPENAI_EMBEDDING_MODEL", cls.DEFAULT_MODEL)
        matrices = []
        for start in range(0, len(chunks), batch_size):
            batch = chunks[start:start + batch_size]
            matrices.append(cls._embed_texts([item["text"] for item in batch], selected_model))
        if not matrices:
            raise ValueError("No chunks are available to index.")
        matrix = np.vstack(matrices)
        faiss.normalize_L2(matrix)
        index = faiss.IndexFlatIP(matrix.shape[1])
        index.add(matrix)
        return cls(chunks, index, selected_model)

    @classmethod
    def load(cls, path):
        target = Path(path)
        state = json.loads((target / "store.json").read_text(encoding="utf-8"))
        index = faiss.read_index(str(target / "policy.faiss"))
        model = state.get("embedding_model", cls.DEFAULT_MODEL)
        if state.get("embedding") != "OpenAI embeddings":
            raise ValueError(f"{target} does not contain an OpenAI embedding index.")
        return cls(state["chunks"], index, model)

    def save(self, path):
        target = Path(path)
        target.mkdir(parents=True, exist_ok=True)
        faiss.write_index(self.index, str(target / "policy.faiss"))
        (target / "store.json").write_text(
            json.dumps({
                "chunks": self.chunks,
                "embedding": "OpenAI embeddings",
                "embedding_model": self.model,
                "vector_dimensions": self.index.d,
                "similarity": "cosine (FAISS inner product on normalized vectors)",
            }, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def search(self, query, k=3):
        matrix = self._embed_texts([query], self.model)
        faiss.normalize_L2(matrix)
        scores, indices = self.index.search(
            matrix, min(max(int(k), 1), len(self.chunks))
        )
        found = []
        for score, idx in zip(scores[0], indices[0]):
            if idx >= 0:
                item = dict(self.chunks[int(idx)])
                item["score"] = float(score)
                found.append(item)
        return found


def format_citation(item):
    return f'{item["source"]}, p. {item["page"]}'


def offline_answer(query, results):
    """Return the best grounded sentence; abstain when retrieval has no signal."""
    if not results or results[0]["score"] <= 0:
        return ABSTENTION
    query_terms = set(tokens(query))
    candidates = []
    for item in results:
        for sentence in re.split(r"(?<=[.!?])\s+", item["text"]):
            sentence_terms = set(tokens(sentence))
            overlap = len(query_terms & sentence_terms)
            if overlap:
                candidates.append((overlap / max(len(query_terms), 1), len(sentence), sentence, item))
    if not candidates:
        return ABSTENTION
    _, _, sentence, item = max(candidates, key=lambda x: (x[0], -x[1]))
    return f"{sentence} [{format_citation(item)}]"


def answer_query(query, results, model=None, temperature=0.0, max_tokens=1024,
                 provider=None):
    """Use the selected hosted provider or disclose the local fallback mode."""
    if not results or results[0]["score"] <= 0:
        return ABSTENTION, "offline_extract"

    evidence = "\n\n".join(
        f'[{format_citation(item)}]\n{item["text"]}' for item in results
    )
    prompt = (
        "Answer the hotel staff question using only the supplied AuroraStay policy "
        "evidence. State property/rate-plan qualifications. If evidence is missing or "
        "conflicting, say so and direct staff to verify with the property. Never invent "
        "a fee, promise, or legal conclusion. Include short source citations as "
        "[filename, p. N]. Do not expose sensitive guest or payment information. "
        "For multi-part questions, answer each part separately. Before saying a fact "
        "is missing, check every supplied passage for the relevant amount, date, time, "
        "or staff action and use it when present. For noise or service issues, include "
        "the exact policy time window and required response steps when retrieved. "
        "When evidence is a table, match the exact property row and requested column "
        "heading before using an amount. Do not assign an adjacent amount to the wrong "
        "column or infer limits that are not explicitly stated. For pet-fee questions, "
        "distinguish nightly versus per-stay amounts and answer cancellation terms from "
        "the rate-plan evidence. If a table is ambiguous, state only the clearly labeled "
        "facts and advise staff to verify.\n\n"
        f"Question: {query}\n\nEvidence:\n{evidence}"
    )
    provider = (provider or os.getenv("LLM_PROVIDER", "groq")).strip().lower()

    if provider == "openai":
        api_key = os.getenv("OPENAI_API_KEY", "").strip()
        if not api_key:
            raise RuntimeError("OpenAI is selected but OPENAI_API_KEY is not configured.")
        selected_model = model or os.getenv("OPENAI_MODEL", "gpt-5-mini")
        try:
            response = requests.post(
                "https://api.openai.com/v1/responses",
                headers={"Authorization": f"Bearer {api_key}"},
                json={
                    "model": selected_model,
                    "reasoning": {"effort": "low"},
                    "instructions": (
                        "Answer only from the supplied policy evidence. Match the "
                        "exact property and fee column. Keep the answer concise."
                    ),
                    "input": prompt,
                    "max_output_tokens": max(400, min(int(max_tokens), 1600)),
                },
                timeout=60,
            )
            response.raise_for_status()
            payload = response.json()
            text = "\n".join(
                content["text"]
                for item in payload.get("output", [])
                for content in item.get("content", [])
                if content.get("type") == "output_text" and content.get("text")
            ).strip()
            if not text:
                raise RuntimeError("OpenAI returned an empty answer.")
            return text, "openai"
        except requests.RequestException as exc:
            status = getattr(getattr(exc, "response", None), "status_code", None)
            detail = f" (HTTP {status})" if status else ""
            raise RuntimeError(f"OpenAI request failed{detail}.") from None

    if provider != "groq":
        raise ValueError("provider must be 'groq' or 'openai'")

    api_key = os.getenv("GROQ_API_KEY", "").strip()
    if not api_key:
        return offline_answer(query, results), "offline_extract"
    model = model or os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")
    base = os.getenv("GROQ_API_BASE", "https://api.groq.com/openai/v1").rstrip("/")
    try:
        response = requests.post(
            f"{base}/chat/completions",
            headers={"Authorization": f"Bearer {api_key}"},
            json={
                "model": model,
                "temperature": float(temperature),
                "max_tokens": int(max_tokens),
                "messages": [{"role": "user", "content": prompt}],
            },
            timeout=45,
        )
        response.raise_for_status()
        text = response.json()["choices"][0]["message"]["content"].strip()
        if not text:
            raise ValueError("Groq returned an empty answer.")
        return text, "groq"
    except Exception:
        # Fail closed to a transparent extractive answer rather than lose service.
        return offline_answer(query, results), "offline_extract_fallback"


def public_result(query, k=5, store=None, include_answer=True, model=None,
                  temperature=0.0, max_tokens=1024, provider=None):
    if not isinstance(query, str) or not query.strip():
        raise ValueError("query must be a non-empty string")
    results = store.search(query.strip(), k=k)
    output = {
        "query": query.strip(),
        "k": min(max(int(k), 1), 8),
        "relevant_chunks": [
            {
                "content": item["text"],
                "source": item["source"],
                "page": item["page"],
                "score": round(item["score"], 4),
            }
            for item in results
        ],
    }
    if include_answer:
        output["answer"], output["mode"] = answer_query(
            query.strip(), results, model=model, temperature=temperature,
            max_tokens=max_tokens, provider=provider,
        )
    return output
