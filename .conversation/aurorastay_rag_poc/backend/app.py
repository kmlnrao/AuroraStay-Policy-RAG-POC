import os
from pathlib import Path

from flask import Flask, jsonify, request

from rag_core import TfidfFaissStore, public_result


HERE = Path(__file__).resolve().parent
store = TfidfFaissStore.load(os.getenv("INDEX_DIR", str(HERE / "index")))
app = Flask("AuroraStay Policy Assistant")
app.config["MAX_CONTENT_LENGTH"] = 32 * 1024


@app.get("/")
@app.get("/health")
def health():
    return jsonify({"service": "AuroraStay Policy RAG", "status": "ok",
                    "vectors": int(store.index.ntotal)})


@app.post("/v1/relevant_chunks")
def relevant_chunks():
    data = request.get_json(silent=True) or {}
    try:
        result = public_result(data.get("query"), data.get("k", 3), store,
                              include_answer=False)
        return jsonify(result)
    except (TypeError, ValueError) as exc:
        return jsonify({"error": str(exc)}), 400


@app.post("/v1/answer")
@app.post("/v1/answer_with_relevant_chunks")
def answer():
    data = request.get_json(silent=True) or {}
    try:
        result = public_result(
            data.get("query"),
            data.get("k", 3),
            store,
            include_answer=True,
            model=data.get("model_name", "gpt-4o-mini"),
            temperature=data.get("temperature", 0.0),
            max_tokens=data.get("max_tokens", 350),
        )
        if request.path.endswith("/answer"):
            result.pop("relevant_chunks", None)
        return jsonify(result)
    except (TypeError, ValueError) as exc:
        return jsonify({"error": str(exc)}), 400


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "7860")), debug=False)
