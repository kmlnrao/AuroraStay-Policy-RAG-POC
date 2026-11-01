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
  DeepEval judge scores. A separate DeepEval 4.3.2 GEval run covers all 20
  supplied cases using Groq `openai/gpt-oss-120b` for both generation and
  judging; its mean score is 0.745/1.00. Because the same model generated and
  judged the answers, the result is not an independent evaluation or a course
  grade. One case (`test.csv:3`) had a score and rationale that disagreed, so
  review per-case results in `evaluation_results_deepeval.csv` before relying on
  the aggregate.
- If `GROQ_API_KEY` is set in the runtime's secret manager, generation uses
  Groq's OpenAI-compatible chat-completions endpoint with
  `openai/gpt-oss-120b` by default. Successful hosted responses are labeled
  `groq`; without a key the API returns a cited extractive answer labeled
  `offline_extract`. If a hosted request fails, the fallback is labeled
  `offline_extract_fallback`.
- Keep `GROQ_API_KEY` in Replit Secrets or Codespaces Secrets as appropriate;
  the two environments do not share secrets. Never put an API key or token in
  this folder, notebook, or presentation.
- In Codespaces, also create a separate high-entropy `API_ACCESS_KEY` secret.
  Docker Compose requires it, the Streamlit server sends it to the backend as a
  Bearer token, and unauthenticated `/v1/*` requests are rejected. The `/health`
  endpoint remains public for service checks. Do not reuse the Groq provider key
  as the API access key.

## Run locally

1. Build the vector index: `python backend/build_index.py`
2. Start the API: `cd backend && python app.py`
3. In another terminal start the UI: `cd frontend && streamlit run app.py`
4. Or use Docker Compose from this directory after setting `API_ACCESS_KEY`:
   `docker compose up --build`
5. Run the supplied offline checks: `python backend/evaluate_offline.py`
6. Run the DeepEval judge: install `requirements-evaluation.txt`, set
   `GROQ_API_KEY`, then run `python evaluate_deepeval.py`

The API listens on port 7860; Streamlit listens on port 8501. The offline
extractor is an engineering fallback, not a substitute for the hosted LLM and
independent rubric evaluation.

To use Groq with Docker Compose, make `GROQ_API_KEY` available to the shell
running Compose. Optionally set `GROQ_MODEL` to another currently supported
Groq chat model. The compose file passes the key only into the backend
container; do not commit it or paste it into screenshots.

For direct API calls, send `Authorization: Bearer <API_ACCESS_KEY>` to
`/v1/relevant_chunks`, `/v1/answer`, and
`/v1/answer_with_relevant_chunks`. Keep the access token in a secret manager,
never in source control or screenshots.
