# AuroraStay Policy RAG — Low-Code POC

This folder contains the completed supporting notebook, a local policy-search
service, the Streamlit interface, evaluation files, and the presentation PDF.
The required course submission is the PDF presentation; the notebook and code
are supporting artifacts, not separate submission uploads unless the instructor
requests them.

## Current evidence and limits

- The four supplied policy PDFs extract to 19 pages and 61 overlapping chunks
  using 120-word chunks with 20-word overlap.
- The index is a persisted FAISS inner-product index over normalized local
  TF-IDF vectors. It is deterministic and runs without model downloads.
- `Data/evaluation.csv` and `Data/test.csv` contain 10 cases each. Run
  `python backend/evaluate_offline.py` to regenerate the 20-case result CSV.
- The offline metrics are transparent lexical/support proxies. They are **not**
  DeepEval judge scores and must not be reported as such. The assignment's
  DeepEval GEval results require an approved evaluation API key.
- If `OPENAI_API_KEY` is set in the runtime's secret manager, generation uses
  the configured OpenAI-compatible chat endpoint. Otherwise it returns an
  extractive, page-cited answer and labels the mode `offline_extract`.
- GitHub push and Codespaces inference were not completed or claimed: the
  GitHub connection was declined, and no hosted endpoint was supplied. Never
  put an API key or token in this folder, notebook, or presentation.

## Run locally

1. Build the vector index: `python backend/build_index.py`
2. Start the API: `cd backend && python app.py`
3. In another terminal start the UI: `cd frontend && streamlit run app.py`
4. Or use Docker Compose from this directory: `docker compose up --build`
5. Run the supplied offline checks: `python backend/evaluate_offline.py`

The API listens on port 7860; Streamlit listens on port 8501. The offline
extractor is an engineering fallback, not a substitute for the hosted LLM and
independent rubric evaluation.
