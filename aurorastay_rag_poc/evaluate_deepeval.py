"""Run DeepEval GEval with OpenAI RAG generation and a separate Groq judge."""

from __future__ import annotations

import argparse
import asyncio
import csv
import json
import os
import re
import sys
from pathlib import Path

import requests
os.environ.setdefault("DEEPEVAL_TELEMETRY_OPT_OUT", "1")
from deepeval.metrics import GEval
from deepeval.models import DeepEvalBaseLLM
from deepeval.test_case import LLMTestCase, SingleTurnParams

ROOT = Path(__file__).resolve().parent
BACKEND = ROOT / "backend"
sys.path.insert(0, str(BACKEND))
from rag_core import OpenAIFaissStore, public_result  # noqa: E402

GENERATOR_MODEL = os.getenv("OPENAI_MODEL", "gpt-5-mini")
JUDGE_MODEL = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")
API_BASE = os.getenv("GROQ_API_BASE", "https://api.groq.com/openai/v1").rstrip("/")


class GroqJudge(DeepEvalBaseLLM):
    def __init__(self, api_key: str, model: str = JUDGE_MODEL):
        self.api_key = api_key
        self.model = model

    def load_model(self):
        return self

    def get_model_name(self):
        return f"Groq {self.model}"

    def generate(self, prompt: str, schema=None):
        messages = [{"role": "user", "content": prompt}]
        payload = {
            "model": self.model,
            "temperature": 0,
            "max_tokens": 1200,
            "messages": messages,
        }
        if schema is not None:
            payload["response_format"] = {"type": "json_object"}
            messages[0]["content"] += (
                "\nReturn one JSON object matching this schema: "
                + json.dumps(schema.model_json_schema())
            )

        response = requests.post(
            f"{API_BASE}/chat/completions",
            headers={"Authorization": f"Bearer {self.api_key}"},
            json=payload,
            timeout=90,
        )
        response.raise_for_status()
        text = response.json()["choices"][0]["message"]["content"].strip()
        if schema is None:
            return text
        text = re.sub(r"^```(?:json)?\s*|\s*```$", "", text, flags=re.I)
        return schema.model_validate_json(text)

    async def a_generate(self, prompt: str, schema=None):
        return await asyncio.to_thread(self.generate, prompt, schema)


def load_rows():
    rows = []
    for name in ("evaluation.csv", "test.csv"):
        with (ROOT / "Data" / name).open(newline="", encoding="utf-8-sig") as f:
            for line, row in enumerate(csv.DictReader(f), start=1):
                rows.append({
                    "dataset": name,
                    "case_id": f"{name}:{line}",
                    "question": row["question"],
                    "expected_answer": row["expected_answer"],
                    "relevant_context": row["relevant_context"],
                })
    return rows


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, help="Evaluate only the first N cases.")
    args = parser.parse_args()

    judge_key = os.getenv("GROQ_API_KEY", "").strip()
    if not judge_key:
        raise SystemExit("GROQ_API_KEY is required for the independent DeepEval judge.")
    if not os.getenv("OPENAI_API_KEY", "").strip():
        raise SystemExit("OPENAI_API_KEY is required for the OpenAI RAG generator.")

    rows = load_rows()
    if args.limit:
        rows = rows[:args.limit]
    store = OpenAIFaissStore.load(BACKEND / "index_openai")
    judge = GroqJudge(judge_key)
    metric = GEval(
        name="Policy Answer Correctness and Grounding",
        criteria=(
            "Score whether the actual answer correctly answers the question, agrees "
            "with the expected answer, and is supported by the retrieved policy "
            "context. Penalize wrong property, fee, rate-plan, or date values; "
            "unsupported claims; and missing material qualifications. Reward a clear "
            "abstention when evidence is insufficient."
        ),
        evaluation_steps=[
            "Compare key facts in the actual answer with the expected answer.",
            "Check each factual claim against the retrieved policy context.",
            "Check that property names, amounts, dates, and qualifications are not mixed up.",
            "Assign a score from 0 to 1 and briefly explain the main reason.",
        ],
        evaluation_params=[
            SingleTurnParams.INPUT,
            SingleTurnParams.ACTUAL_OUTPUT,
            SingleTurnParams.EXPECTED_OUTPUT,
            SingleTurnParams.RETRIEVAL_CONTEXT,
        ],
        model=judge,
        threshold=None,
        async_mode=False,
        verbose_mode=False,
    )

    results = []
    total = len(rows)
    for index, row in enumerate(rows, start=1):
        result = public_result(
            row["question"], k=5, store=store, model=GENERATOR_MODEL,
            provider="openai",
        )
        if result["mode"] != "openai":
            raise RuntimeError(
                f"{row['case_id']} used {result['mode']}; refusing to call this a hosted run."
            )
        context = [
            item["content"] for item in result.get("relevant_chunks", [])
        ]
        test_case = LLMTestCase(
            input=row["question"],
            actual_output=result["answer"],
            expected_output=row["expected_answer"],
            retrieval_context=context,
        )
        metric.measure(test_case)
        record = {
            **row,
            "generator_mode": result["mode"],
            "generator_model": f"OpenAI {GENERATOR_MODEL}",
            "judge_model": judge.get_model_name(),
            "deepeval_metric": metric.name,
            "score": metric.score,
            "reason": metric.reason or "",
            "answer": result["answer"],
            "retrieved_context": json.dumps(context, ensure_ascii=False),
        }
        results.append(record)
        print(f"[{index}/{total}] {row['case_id']}: {metric.score:.3f}")

    output = ROOT / "evaluation_results_deepeval.csv"
    with output.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(results[0]))
        writer.writeheader()
        writer.writerows(results)

    scores = [float(row["score"]) for row in results]
    summary = {
        "metric": metric.name,
        "judge_model": judge.get_model_name(),
        "generator_model": f"OpenAI {GENERATOR_MODEL}",
        "cases": len(scores),
        "mean_score": sum(scores) / len(scores),
        "scores_below_0_50_descriptive": sum(score < 0.5 for score in scores),
        "threshold": None,
        "evaluation_library": "DeepEval",
        "independence_warning": (
            "OpenAI generated answers and a separate Groq model judged them. "
            "The judge is still an LLM and scores require human review."
        ),
        "review_note": (
            "At least one score/reason pair may require manual review; inspect "
            "per-case output before relying on the aggregate."
        ),
        "score_interpretation": "GEval score from 0 to 1; not a guaranteed course grade.",
    }
    (ROOT / "evaluation_summary_deepeval.json").write_text(
        json.dumps(summary, indent=2), encoding="utf-8"
    )
    print(json.dumps(summary, indent=2))
    print(f"Saved per-case results to {output}")


if __name__ == "__main__":
    main()
