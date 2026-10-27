import json
import re
import uuid
from pathlib import Path

ROOT = Path("artifacts/aurorastay-presentation")
SLIDES = ROOT / "src/pages/slides"
titles = {
    1: "AuroraStay Policy Assistant",
    2: "Contents / Agenda",
    3: "Executive Summary",
    4: "Business Problem and Solution",
    5: "Policy Data",
    6: "Text Representation",
    7: "Chunk Design",
    8: "Policy Chunk Example",
    9: "FAISS Vector Index",
    10: "Retrieval Example",
    11: "Answer Generation",
    12: "Grounding Rules",
    13: "RAG Demonstration",
    14: "Evaluation Set",
    15: "Judge Model",
    16: "Evaluation Measures",
    17: "Evaluation Results",
    18: "Held-Out Test Set",
    19: "Test Results",
    20: "Persisted Backend Index",
    21: "Flask API",
    22: "Backend Dependencies",
    23: "Backend Container",
    24: "Streamlit Interface",
    25: "Frontend Container",
    26: "GitHub Publication",
    27: "Hosted Inference",
    28: "Retrieved Evidence API",
    29: "Answer API",
    30: "APPENDIX",
    31: "Completion and Submission Checklist",
    32: "AuroraStay Policy Assistant",
}

body = {
    3: "A reproducible local RAG baseline is built from four policy guides. It retrieves cited passages and runs all 20 supplied cases. Offline proxy scores are diagnostic only; hosted judging and inference remain unverified.",
    4: "Problem: 1,200 weekly queries; about 40% require cross-document policy lookup. Manual work takes 8–12 minutes, with a stated 15–20% error rate. Approach: retrieve approved policy evidence, answer only from it, show citations, and escalate uncertainty.",
    5: "Four supplied guides cover booking, room/property facts, refunds/charges, and conduct/accessibility. Extraction produced 19 pages. Key risk: property, rate plan, timing, and exception details must not be generalized.",
    6: "Embedding: corpus-fitted normalized TF-IDF vectors (local, deterministic; no pretrained max length). Similarity: cosine via normalized vectors. This is a lightweight POC baseline, not the domain-specific embedding model contemplated in the starter.",
    7: "Recursive word-window chunking: 120 words per chunk, 20-word overlap; each chunk retains source PDF and page. This measured setting improves precision and answer overlap proxies while reducing context recall.",
    8: "61 chunks from 19 pages. Example: “ASH-CHI Loop lists a $50 per night pet fee, capped at $150 per stay.” Citation metadata is retained as source filename and page.",
    9: "FAISS IndexFlatIP stores 61 normalized vectors. The persisted index and JSON metadata allow restart without re-reading PDFs. Vector dimension: 1,008 corpus terms.",
    10: "Query: “What is the pet fee at ASH-CHI Loop?” Retrieval returns policy passages with source/page and similarity. Staff should verify the live property profile before quoting a fee.",
    11: "Configured hosted option: OpenAI-compatible gpt-4o-mini, temperature 0.0. No model key was available, so tested answers used an extractive local fallback; hosted generation is not verified.",
    12: "Prompt policy: answer only from retrieved passages; preserve property/rate-plan qualifications; cite filename and page; do not invent fees or promises; state uncertainty and verify with the property.",
    13: "The local RAG route accepts a question, retrieves up to 3 passages, and returns a policy sentence plus citation. Fallback mode is explicitly labelled offline_extract.",
    14: "Evaluation.csv contains 10 questions, expected answers, and reference context. Topics include check-in, cancellation, pet fees, smoking, service animals, refunds, and accessibility.",
    15: "Rubric plan: DeepEval GEval with a separate gpt-4o judge. It was not run because an approved judge-model secret is not configured. No judge score is claimed.",
    16: "Faithfulness: claims supported by retrieval. Contextual recall: evidence completeness. Contextual precision: evidence relevance. Answer relevancy: response addresses question. Current reported values are lexical proxies, not GEval.",
    17: "10/10 evaluation questions returned an answer. Offline proxies: support 1.000; context recall 0.574; context precision 0.164; answer overlap 0.449. Precision and overlap improved versus the prior chunk setting; recall fell. Not semantic judge scores.",
    18: "test.xlsx was converted to test.csv and includes 10 held-out cases across booking channel, member offers, occupancy, accessible rooms, parking, breakfast, rate changes, checkout, pets, and card holds.",
    19: "10/10 test questions returned an answer. Offline proxies: support 1.000; context recall 0.704; context precision 0.158; answer overlap 0.455. Precision improved versus the prior chunk setting; recall fell. Not semantic judge scores.",
    20: "Backend persists policy.faiss and store.json under backend/index. The API loads this index at startup and returns the cited retrieval evidence.",
    21: "Flask routes: GET /health; POST /v1/relevant_chunks; POST /v1/answer; POST /v1/answer_with_relevant_chunks. Invalid or empty queries return HTTP 400.",
    22: "Backend: Flask, Gunicorn, FAISS CPU, NumPy, PyMuPDF, Requests. Frontend: Streamlit and Requests. Dockerfiles and Compose are included with the supporting source.",
    23: "Backend Dockerfile serves port 7860 with Gunicorn. The vector index is copied into the image. Docker build/runtime has not been executed in this hosted project.",
    24: "Streamlit supports a staff question, top-k and response mode, answer display, and expandable source passages. It warns staff not to enter card or sensitive medical details.",
    25: "Frontend Dockerfile serves Streamlit on port 8501; Compose connects it to the Flask service. This is a local deployment scaffold, not a Codespaces deployment record.",
    26: "Not published: the GitHub integration card was dismissed. There is no repository URL or verified push. Backend/frontend files are available in the supporting project folder.",
    27: "No public Codespaces URL or live inference screenshot exists. Do not submit a fabricated endpoint. This 6-point deployment-inference criterion remains unverified.",
    28: "Local API: POST /v1/relevant_chunks with {query, k}. Response includes retrieved content, source, page, and similarity. This validates local retrieval only, not forwarded online inference.",
    29: "Local API: POST /v1/answer_with_relevant_chunks. Response includes answer, mode, cited source chunks, and similarity. No hosted call was made.",
    31: "Submit the presentation PDF only for the low-code path. Keep the notebook as working evidence. Before claiming full rubric completion: run DeepEval, publish files to GitHub, deploy both containers in Codespaces, capture live inference, and replace proxy results with judge scores.",
}

agenda = [
    "Executive summary",
    "Business problem and solution",
    "Policy data and RAG design",
    "Evaluation and test results",
    "Backend and frontend deployment",
    "Inference status and next steps",
]

def jsx_texts(src):
    found = []
    for match in re.finditer(r'\{("(?:\\.|[^"\\])*")\}', src):
        raw = match.group(1)
        try:
            value = json.loads(raw)
        except json.JSONDecodeError:
            # Preserve JSX string escapes such as the template copyright glyph.
            continue
        found.append((raw, value))
    return found

def assign(slide_no):
    title = titles[slide_no]
    if slide_no == 1:
        return ["AuroraStay", "Policy RAG POC", "Oct 11"]
    if slide_no == 2:
        return ["Contents / Agenda", *agenda]
    if slide_no == 3:
        return [title, body[3], "", ""]
    if slide_no == 4:
        return [title,
                "Staff reconcile policy details across four guides; 40% of 1,200 weekly queries are complex.",
                "Local retrieval POC returns grounded, page-cited evidence for staff review."]
    if slide_no == 14:
        return [title, "", body[14], "", "", ""]
    if slide_no in (30,):
        return [title]
    if slide_no == 31:
        return [title, body[31]]
    if slide_no == 32:
        return ["Thank You", "32"]
    return [title, body[slide_no], "", "", ""]

for n in range(1, 33):
    path = SLIDES / f"Slide{n}.tsx"
    src = path.read_text()
    literals = jsx_texts(src)
    values = assign(n)
    if len(literals) != len(values):
        raise RuntimeError(f"Slide {n}: expected {len(literals)} text nodes, got {len(values)}")
    for (old_literal, _), new in zip(literals, values):
        src = src.replace("{" + old_literal + "}", "{" + json.dumps(new, ensure_ascii=False) + "}", 1)
    path.write_text(src)

manifest = []
for n in range(1, 33):
    manifest.append({
        "id": str(uuid.uuid4()),
        "position": n,
        "filepath": f"src/pages/slides/Slide{n}.tsx",
        "title": titles[n],
        "description": body.get(n, "AuroraStay RAG project presentation."),
        "speakerNotes": "",
    })
(ROOT / "src/data/slides-manifest.json").write_text(
    json.dumps(manifest, indent=2), encoding="utf-8"
)
print(f"Populated {len(manifest)} template slides.")
