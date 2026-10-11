# Project 3 — Low-Code Delivery Exception Resolution

## Submission contents

- `Project_3_Low_Code_final.ipynb` — completed and executed notebook with outputs.
- `Project_3_Delivery_Exception_Resolution_Presentation.pptx` — completed business presentation based on the supplied template.
- `delivery_exception_evaluation_summary.csv` — aggregate metrics.
- `delivery_exception_evaluation_detail.csv` — per-shipment predictions, pass/fail checks, citations, and trace-event counts.
- `delivery_exception_evaluation_results.json` — machine-readable evaluation export.

## Verified scope

- 13 raw delivery-log rows
- 10 unique shipment scenarios
- 12 customer records
- 6 locker records
- 10-page exception-resolution playbook
- 24 retrieved playbook chunks

## Verified results

| Metric | Result |
|---|---:|
| Task completion rate | 100.0% |
| Escalation accuracy | 100.0% (8/8 exception cases) |
| Tool-call accuracy | 100.0% |
| Reasoning coherence | 5.00/5.0 |

Noise cases are intentionally excluded from escalation accuracy because their ground-truth escalation field is `N/A`.

## Runtime note

No API credentials were attached to this workspace, so the executed notebook used its explicitly labeled deterministic offline fallback. The notebook also supports remote `gpt-4o-mini` generation and validation when `config.json` or environment variables provide valid credentials. No credentials are included in this submission.

## Reproducibility

Run the notebook from the workspace root so the `attached_assets/` paths resolve. The notebook includes additional assertions for duplicate handling, prompt-injection detection, discretionary escalation, and locker eligibility.