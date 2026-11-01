from pathlib import Path

import nbformat as nbf

ROOT = Path(__file__).resolve().parent
cells = [
    nbf.v4.new_markdown_cell(
        "# AuroraStay Policy RAG — completed low-code notebook\n"
        "Purpose: answer internal staff questions from four supplied policy "
        "documents, show page-level sources, and measure all 20 supplied cases. "
        "The PDF presentation is the required submission; this notebook is a "
        "supporting, reproducible artifact.\n\n"
        "**Execution note:** production retrieval uses OpenAI "
        "`text-embedding-3-small` vectors in a FAISS cosine index. The local "
        "TF-IDF index remains an offline fallback. "
        "Choose Groq (`LLM_PROVIDER=groq`) or OpenAI "
        "(`LLM_PROVIDER=openai`, `OPENAI_API_KEY`, `gpt-5-mini` by default); "
        "without the selected provider's key, it reports "
        "`offline_extract`. Both the Groq demonstration and OpenAI-backed "
        "pet-fee route were verified in Replit, not through Codespaces. The "
        "OpenAI response and citations are recorded "
        "in `openai_demo_result.json`. Official DeepEval GEval results are included for "
        "20 cases; the offline lexical proxies remain separate diagnostics."
    ),
    nbf.v4.new_code_cell(
        "from pathlib import Path\n"
        "import json, sys\n"
        "import pandas as pd\n"
        "ROOT = Path.cwd()\n"
        "if not (ROOT / 'Data').exists():\n"
        "    ROOT = Path('aurorastay_rag_poc')\n"
        "sys.path.insert(0, str(ROOT / 'backend'))\n"
        "from rag_core import OpenAIFaissStore, TfidfFaissStore, read_policy_pages, chunk_pages, public_result\n"
        "print('Project:', ROOT.resolve())"
    ),
    nbf.v4.new_markdown_cell("## 1. Data understanding and document extraction"),
    nbf.v4.new_code_cell(
        "pages = read_policy_pages(ROOT / 'Data')\n"
        "chunks = chunk_pages(pages, chunk_words=120, overlap=20)\n"
        "print(f'Policy PDFs: {len(list((ROOT / \"Data\").glob(\"*.pdf\")))}')\n"
        "print(f'Extracted pages: {len(pages)} | chunks: {len(chunks)}')\n"
        "print('Sample metadata:', {k: chunks[0][k] for k in ('source','page')})\n"
        "print('Sample chunk:', chunks[0]['text'][:400])"
    ),
    nbf.v4.new_markdown_cell(
        "## 2. Chunking, transformer embeddings, and vector database\n"
        "Each page is split into 120-word chunks with 20-word overlap. OpenAI "
        "`text-embedding-3-small` produces 1,536-dimensional vectors; FAISS "
        "IndexFlatIP returns cosine-ranked passages. Source filename and page "
        "metadata stay attached to every chunk. The TF-IDF index remains available "
        "for offline demonstrations."
    ),
    nbf.v4.new_code_cell(
        "provider = __import__('os').getenv('EMBEDDING_PROVIDER', 'openai').lower()\n"
        "index_dir = ROOT / 'backend' / ('index_openai' if provider == 'openai' else 'index')\n"
        "store_class = OpenAIFaissStore if provider == 'openai' else TfidfFaissStore\n"
        "if (index_dir / 'store.json').exists():\n"
        "    store = store_class.load(index_dir)\n"
        "else:\n"
        "    store = store_class.build(chunks)\n"
        "    store.save(index_dir)\n"
        "print('FAISS vectors:', store.index.ntotal)\n"
        "print('Embedding provider:', provider)\n"
        "print('Vector dimensions:', store.index.d)"
    ),
    nbf.v4.new_markdown_cell("## 3. Retrieval and grounded answer demonstration"),
    nbf.v4.new_code_cell(
        "sample_question = 'What is the pet fee at ASH-CHI Loop?'\n"
        "sample = public_result(sample_question, k=5, store=store)\n"
        "print('Question:', sample_question)\n"
        "print('Answer:', sample['answer'])\n"
        "print('Mode:', sample['mode'])\n"
        "for item in sample['relevant_chunks']:\n"
        "    print(f\"\\n{item['source']} p.{item['page']} (score={item['score']})\")\n"
        "    print(item['content'][:350])"
    ),
    nbf.v4.new_code_cell(
        "openai_demo = json.loads((ROOT / 'openai_demo_result.json').read_text())\n"
        "print('Verified backend mode:', openai_demo['mode'])\n"
        "print('Model:', openai_demo['model'])\n"
        "print('Question:', openai_demo['query'])\n"
        "print('Answer:', openai_demo['answer'])\n"
        "print('Citations:', ', '.join(f\"{x['source']} p.{x['page']}\" "
        "for x in openai_demo['sources']))"
    ),
    nbf.v4.new_markdown_cell(
        "## 4. Evaluation and held-out test set\n"
        "The four local checks below are diagnostic proxies only. A separate "
        "official DeepEval 4.3.2 GEval run evaluates the OpenAI embedding + "
        "generation pipeline with Groq `openai/gpt-oss-120b` as a separate judge. "
        "The judge is independent of the generator, but the metric is still an "
        "LLM score, not a course grade or pass threshold. Review each score and "
        "rationale in the per-case CSV; summary metadata is in "
        "`evaluation_summary_deepeval.json`."
    ),
    nbf.v4.new_code_cell(
        "deepeval_results = pd.read_csv(ROOT / 'evaluation_results_deepeval.csv')\n"
        "deepeval_summary = json.loads((ROOT / 'evaluation_summary_deepeval.json').read_text())\n"
        "display(pd.DataFrame(deepeval_summary, index=[0]))\n"
        "display(deepeval_results[['case_id','score','reason']])"
    ),
    nbf.v4.new_code_cell(
        "import subprocess\n"
        "subprocess.run([sys.executable, str(ROOT / 'backend' / 'evaluate_offline.py')], "
        "check=True)\n"
        "results = pd.read_csv(ROOT / 'evaluation_results_offline.csv')\n"
        "summary = json.loads((ROOT / 'evaluation_summary_offline.json').read_text())\n"
        "display(pd.DataFrame(summary).T)\n"
        "display(results[['split','case','question','sources','context_recall_proxy',"
        "'context_precision_proxy','extractive_support_proxy','answer_relevancy_proxy']])"
    ),
    nbf.v4.new_markdown_cell(
        "## 5. Deployment and completion status\n"
        "- Backend files: `backend/app.py`, `backend/rag_core.py`, "
        "`backend/requirements.txt`, `backend/Dockerfile`.\n"
        "- Frontend files: `frontend/app.py`, `frontend/requirements.txt`, "
        "`frontend/Dockerfile`; `docker-compose.yml` wires them together.\n"
        "- Routes: `/health`, `/v1/relevant_chunks`, `/v1/answer`, "
        "`/v1/answer_with_relevant_chunks`.\n"
        "- OpenAI gpt-5-mini generation was verified through the backend route "
        "in Replit. This does not verify Codespaces inference; add "
        "`OPENAI_API_KEY` and `API_ACCESS_KEY` separately there and capture the "
        "forwarded app/API evidence before claiming deployment.\n"
        "- Keep API credentials only in the hosting provider's secret manager."
    ),
]
notebook = nbf.v4.new_notebook(cells=cells)
notebook.metadata = {
    "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
    "language_info": {"name": "python", "version": "3.11"},
}
nbf.write(notebook, ROOT / "AuroraStay_RAG_Completed.ipynb")
print("Wrote", ROOT / "AuroraStay_RAG_Completed.ipynb")
