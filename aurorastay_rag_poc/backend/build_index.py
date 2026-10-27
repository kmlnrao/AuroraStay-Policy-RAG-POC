from pathlib import Path

from rag_core import TfidfFaissStore, chunk_pages, read_policy_pages


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "Data"
INDEX_DIR = Path(__file__).resolve().parent / "index"

pages = read_policy_pages(DATA)
chunks = chunk_pages(pages, chunk_words=120, overlap=20)
store = TfidfFaissStore.build(chunks)
store.save(INDEX_DIR)

print(f"Pages indexed: {len(pages)}")
print(f"Policy chunks: {len(chunks)}")
print(f"TF-IDF dimensions: {len(store.vocabulary)}")
print(f"FAISS vectors: {store.index.ntotal}")
print(f"Saved index: {INDEX_DIR}")
