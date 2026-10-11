"""Run all supplied cases and write explicitly-labelled offline proxy metrics."""
from pathlib import Path
import json
import sys

import pandas as pd

from rag_core import ABSTENTION, TfidfFaissStore, public_result, tokens


ROOT = Path(__file__).resolve().parents[1]
STORE = TfidfFaissStore.load(Path(__file__).resolve().parent / "index")
records = []
for split, filename in [("Evaluation", "evaluation.csv"), ("Test", "test.csv")]:
    frame = pd.read_csv(ROOT / "Data" / filename).fillna("")
    for number, row in frame.iterrows():
        result = public_result(row["question"], 3, STORE, include_answer=True)
        retrieved = " ".join(item["content"] for item in result["relevant_chunks"])
        retrieved_terms = set(tokens(retrieved))
        target_terms = set(tokens(str(row["relevant_context"])))
        query_terms = set(tokens(str(row["question"])))
        answer = result["answer"]
        answer_terms = set(tokens(answer))
        evidence_sentence = answer.split(" [")[0]
        support = any(evidence_sentence in item["content"]
                      for item in result["relevant_chunks"])
        records.append({
            "split": split,
            "case": number + 1,
            "question": row["question"],
            "expected_answer": row["expected_answer"],
            "answer": answer,
            "mode": result["mode"],
            "sources": "; ".join(dict.fromkeys(
                f'{item["source"]} p.{item["page"]}'
                for item in result["relevant_chunks"])),
            "context_recall_proxy": len(target_terms & retrieved_terms) /
                                    max(1, len(target_terms)),
            "context_precision_proxy": len(target_terms & retrieved_terms) /
                                       max(1, len(retrieved_terms)),
            "extractive_support_proxy": float(support and answer != ABSTENTION),
            "answer_relevancy_proxy": len(query_terms & answer_terms) /
                                      max(1, len(query_terms)),
        })

results = pd.DataFrame(records)
for metric in ["context_recall_proxy", "context_precision_proxy",
               "extractive_support_proxy", "answer_relevancy_proxy"]:
    results[metric] = results[metric].round(4)
results.to_csv(ROOT / "evaluation_results_offline.csv", index=False)
summary = {
    split: {
        "cases": int(len(group)),
        **{metric: round(float(group[metric].mean()), 3) for metric in [
            "context_recall_proxy", "context_precision_proxy",
            "extractive_support_proxy", "answer_relevancy_proxy",
        ]},
        "answers_returned": int((group["answer"] != ABSTENTION).sum()),
    }
    for split, group in results.groupby("split", sort=False)
}
(ROOT / "evaluation_summary_offline.json").write_text(
    json.dumps(summary, indent=2), encoding="utf-8")
print(results.to_string(index=False))
print("\nOFFLINE PROXY SUMMARY (not DeepEval scores)")
print(json.dumps(summary, indent=2))
