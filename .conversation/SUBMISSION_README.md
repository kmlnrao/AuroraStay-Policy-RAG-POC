# Project 3 — Low-Code Delivery Exception Resolution

## What to upload

- Upload **`Project_3_Delivery_Exception_Resolution_Submission.pdf` only**.
- The assignment says the notebook is not to be submitted. Keep the executed notebook and CSV/JSON reports as supporting files unless the instructor requests them.

## Verified scope

- 13 raw delivery-log rows
- 10 unique shipment scenarios
- 12 customer records
- 6 locker records
- 10-page exception-resolution playbook
- 24 retrieved playbook chunks
- Persistent ChromaDB vector store using deterministic local TF-IDF embeddings and cosine retrieval

## Verified results

| Metric | Result |
|---|---:|
| Task completion rate | 100.0% |
| Escalation accuracy | 100.0% (8/8 exception cases) |
| Tool-call accuracy | 100.0% |
| Reasoning coherence | 5.00/5.0 (offline trace checklist) |
| Mean latency | 0.01s (offline fallback only; not production latency) |

Noise cases are intentionally excluded from escalation accuracy because their ground-truth escalation field is `N/A`.

## Runtime note

No API credentials were attached to this workspace, so the executed notebook used its explicitly labeled deterministic offline fallback. Coherence was scored with a local trace-completeness checklist, not an independent LLM judge. The notebook also supports remote `gpt-4o-mini` generation and validation when `config.json` or environment variables provide valid credentials. No credentials are included in the submission.

## Reproducibility

Run the notebook from the workspace root so the `attached_assets/` paths resolve. It builds the local ChromaDB index and includes assertions for duplicate handling, prompt-injection detection, discretionary escalation, and locker eligibility.