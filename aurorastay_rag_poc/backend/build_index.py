from pathlib import Path

import os

from rag_core import OpenAIFaissStore, TfidfFaissStore, chunk_pages, read_policy_pages


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "Data"
PROVIDER = os.getenv("EMBEDDING_PROVIDER", "tfidf").strip().lower()
INDEX_DIR = Path(__file__).resolve().parent / (
    "index_openai" if PROVIDER == "openai" else "index"
)

pages = read_policy_pages(DATA)
chunks = chunk_pages(pages, chunk_words=120, overlap=20)
if PROVIDER == "openai":
    store = OpenAIFaissStore.build(chunks)
elif PROVIDER == "tfidf":
    store = TfidfFaissStore.build(chunks)
else:
    raise ValueError("EMBEDDING_PROVIDER must be 'openai' or 'tfidf'.")
store.save(INDEX_DIR)

print(f"Pages indexed: {len(pages)}")
print(f"Policy chunks: {len(chunks)}")
print(f"Embedding provider: {PROVIDER}")
print(f"Vector dimensions: {store.index.d}")
print(f"FAISS vectors: {store.index.ntotal}")
print(f"Saved index: {INDEX_DIR}")
