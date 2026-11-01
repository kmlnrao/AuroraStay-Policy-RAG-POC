---
name: Groq policy-answer reliability
description: Model choice and table-reading safeguards for AuroraStay policy Q&A.
---

For AuroraStay policy questions backed by flattened property tables, retain explicit row-and-column instructions in the generation prompt. Use Groq's `openai/gpt-oss-120b` default unless a later evaluation demonstrates an equally reliable alternative. In a direct comparison, `openai/gpt-oss-20b` confused the $22-per-person breakfast amount with the pet fee; `openai/gpt-oss-120b` returned the supported $50/night fee and $150 stay cap.

**Why:** The PDF table text places parking, pet-fee, and breakfast amounts close together, and a fluent answer can still assign a value to the wrong column.

**How to apply:** When changing the Groq model, prompt, or chunk formatting, retest property-specific fee questions against the cited PDF table and verify that the answer preserves the correct field labels.
