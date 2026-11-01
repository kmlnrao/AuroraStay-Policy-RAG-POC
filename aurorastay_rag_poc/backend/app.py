import os
import hmac
from pathlib import Path

from flask import Flask, jsonify, request

from rag_core import OpenAIFaissStore, TfidfFaissStore, public_result


HERE = Path(__file__).resolve().parent
embedding_provider = os.getenv("EMBEDDING_PROVIDER", "tfidf").strip().lower()
if embedding_provider == "openai":
    store = OpenAIFaissStore.load(
        os.getenv("INDEX_DIR", str(HERE / "index_openai"))
    )
elif embedding_provider == "tfidf":
    store = TfidfFaissStore.load(os.getenv("INDEX_DIR", str(HERE / "index")))
else:
    raise RuntimeError("EMBEDDING_PROVIDER must be 'openai' or 'tfidf'.")
embedding_model = getattr(store, "model", "local normalized TF-IDF")
app = Flask("AuroraStay Policy Assistant")
app.config["MAX_CONTENT_LENGTH"] = 32 * 1024


@app.before_request
def protect_inference_api():
    if not request.path.startswith("/v1/"):
        return None

    expected_key = os.getenv("API_ACCESS_KEY", "").strip()
    if not expected_key:
        return jsonify({"error": "API access is not configured"}), 503

    authorization = request.headers.get("Authorization", "")
    scheme, separator, supplied_key = authorization.partition(" ")
    if (
        not separator
        or scheme.lower() != "bearer"
        or not hmac.compare_digest(supplied_key.strip(), expected_key)
    ):
        return jsonify({"error": "Unauthorized"}), 401
    return None


@app.get("/")
@app.get("/health")
def health():
    return jsonify({"service": "AuroraStay Policy RAG", "status": "ok",
                    "vectors": int(store.index.ntotal),
                    "embedding_provider": embedding_provider,
                    "embedding_model": embedding_model})


@app.post("/v1/relevant_chunks")
def relevant_chunks():
    data = request.get_json(silent=True) or {}
    try:
        result = public_result(data.get("query"), data.get("k", 5), store,
                              include_answer=False)
        result["embedding_provider"] = embedding_provider
        result["embedding_model"] = embedding_model
        return jsonify(result)
    except (TypeError, ValueError) as exc:
        return jsonify({"error": str(exc)}), 400
    except RuntimeError as exc:
        return jsonify({"error": str(exc)}), 502


@app.post("/v1/answer")
@app.post("/v1/answer_with_relevant_chunks")
def answer():
    data = request.get_json(silent=True) or {}
    try:
        provider = str(
            data.get("provider") or os.getenv("LLM_PROVIDER", "groq")
        ).strip().lower()
        model_env = "OPENAI_MODEL" if provider == "openai" else "GROQ_MODEL"
        default_model = "gpt-5-mini" if provider == "openai" else "openai/gpt-oss-120b"
        generation_model = data.get("model_name") or os.getenv(model_env, default_model)
        result = public_result(
            data.get("query"),
            data.get("k", 5),
            store,
            include_answer=True,
            model=generation_model,
            temperature=data.get("temperature", 0.0),
            max_tokens=data.get("max_tokens", 1024),
            provider=provider,
        )
        result["embedding_provider"] = embedding_provider
        result["embedding_model"] = embedding_model
        result["generation_model"] = generation_model
        if request.path.endswith("/answer"):
            result.pop("relevant_chunks", None)
        return jsonify(result)
    except (TypeError, ValueError) as exc:
        return jsonify({"error": str(exc)}), 400
    except RuntimeError as exc:
        return jsonify({"error": str(exc)}), 502


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "7860")), debug=False)
