"""Local, policy-grounded RAG core with optional OpenAI-compatible generation."""

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


def chunk_pages(pages: list[dict], chunk_words: int = 190, overlap: int = 35) -> list[dict]:
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


def answer_query(query, results, model="gpt-4o-mini", temperature=0.0, max_tokens=350):
    """Use remote generation only when a key exists; otherwise disclose local mode."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not results or results[0]["score"] <= 0:
        return ABSTENTION, "offline_extract"
    if not api_key:
        return offline_answer(query, results), "offline_extract"

    base = os.getenv("OPENAI_API_BASE", "https://api.openai.com/v1").rstrip("/")
    evidence = "\n\n".join(
        f'[{format_citation(item)}]\n{item["text"]}' for item in results
    )
    prompt = (
        "Answer the hotel staff question using only the supplied AuroraStay policy "
        "evidence. State property/rate-plan qualifications. If evidence is missing or "
        "conflicting, say so and direct staff to verify with the property. Never invent "
        "a fee, promise, or legal conclusion. Include short source citations as "
        "[filename, p. N]. Do not expose sensitive guest or payment information.\n\n"
        f"Question: {query}\n\nEvidence:\n{evidence}"
    )
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
        return text, "openai"
    except Exception:
        # Fail closed to a transparent extractive answer rather than lose service.
        return offline_answer(query, results), "offline_extract_fallback"


def public_result(query, k=3, store=None, include_answer=True, model="gpt-4o-mini",
                  temperature=0.0, max_tokens=350):
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
            max_tokens=max_tokens,
        )
    return output
