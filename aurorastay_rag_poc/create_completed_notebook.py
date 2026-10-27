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
        "**Execution note:** this notebook runs the local FAISS/TF-IDF baseline "
        "without secrets. Its quality metrics are offline lexical proxies, not "
        "DeepEval judge scores. Hosted LLM evaluation and Codespaces inference "
        "remain separate deployment steps."
    ),
    nbf.v4.new_code_cell(
        "from pathlib import Path\n"
        "import json, sys\n"
        "import pandas as pd\n"
        "ROOT = Path.cwd()\n"
        "if not (ROOT / 'Data').exists():\n"
        "    ROOT = Path('aurorastay_rag_poc')\n"
        "sys.path.insert(0, str(ROOT / 'backend'))\n"
        "from rag_core import TfidfFaissStore, read_policy_pages, chunk_pages, public_result\n"
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
        "## 2. Chunking, local embeddings, and vector database\n"
        "Each page is split into 120-word chunks with 20-word overlap. The local "
        "corpus-fitted TF-IDF embedder creates normalized vectors; FAISS "
        "IndexFlatIP returns cosine-ranked passages. This avoids model downloads "
        "and retains source filename/page metadata."
    ),
    nbf.v4.new_code_cell(
        "index_dir = ROOT / 'backend' / 'index'\n"
        "if (index_dir / 'store.json').exists():\n"
        "    store = TfidfFaissStore.load(index_dir)\n"
        "else:\n"
        "    store = TfidfFaissStore.build(chunks)\n"
        "    store.save(index_dir)\n"
        "print('FAISS vectors:', store.index.ntotal)\n"
        "print('Vector dimensions:', len(store.vocabulary))"
    ),
    nbf.v4.new_markdown_cell("## 3. Retrieval and grounded answer demonstration"),
    nbf.v4.new_code_cell(
        "sample_question = 'What is the pet fee at ASH-CHI Loop?'\n"
        "sample = public_result(sample_question, k=3, store=store)\n"
        "print('Question:', sample_question)\n"
        "print('Answer:', sample['answer'])\n"
        "print('Mode:', sample['mode'])\n"
        "for item in sample['relevant_chunks']:\n"
        "    print(f\"\\n{item['source']} p.{item['page']} (score={item['score']})\")\n"
        "    print(item['content'][:350])"
    ),
    nbf.v4.new_markdown_cell(
        "## 4. Evaluation and held-out test set\n"
        "Run all ten rows from each provided file. The four local checks below "
        "are labelled proxies: retrieved-context term recall/precision, exact "
        "extractive support, and query-term answer overlap. They are useful for "
        "debugging but are not semantic judge metrics. For official GEval scores, "
        "run DeepEval with an approved judge-model secret and report its actual "
        "per-case results."
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
        "- Local index/inference can be tested. GitHub push and public "
        "Codespaces forwarded-URL inference have not been performed; no "
        "deployment URL or screenshot is fabricated.\n"
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
