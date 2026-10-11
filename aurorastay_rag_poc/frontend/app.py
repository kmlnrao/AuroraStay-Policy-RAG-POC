import os

import requests
import streamlit as st


st.set_page_config(page_title="AuroraStay Policy Assistant", page_icon="🏨",
                   layout="centered")
st.title("AuroraStay Policy Assistant")
st.caption("Internal POC · grounded answers with page-level policy citations")

backend = os.getenv("BACKEND_URL", "http://localhost:7860").rstrip("/")
with st.sidebar:
    st.header("Response settings")
    k = st.slider("Policy passages", min_value=1, max_value=6, value=3)
    mode = st.radio("Response mode", ["Answer only", "Answer + sources"])
    temperature = st.slider("Temperature (remote mode)", 0.0, 0.7, 0.0, 0.1)

question = st.text_area(
    "Question",
    placeholder="Example: What is the pet fee at ASH-CHI Loop?",
    height=90,
)
st.info(
    "Check the guest's live reservation and property profile before making a "
    "commitment. Do not enter payment card numbers or sensitive medical details."
)

if st.button("Get policy answer", type="primary"):
    if not question.strip():
        st.warning("Enter a question first.")
    else:
        endpoint = "/v1/answer_with_relevant_chunks"
        try:
            with st.spinner("Searching approved policy documents…"):
                response = requests.post(
                    backend + endpoint,
                    json={"query": question, "k": k, "temperature": temperature},
                    timeout=60,
                )
            response.raise_for_status()
            result = response.json()
            st.subheader("Answer")
            st.write(result["answer"])
            st.caption(f"Generation mode: {result['mode']}")
            if mode == "Answer + sources":
                st.subheader("Retrieved policy evidence")
                for i, chunk in enumerate(result.get("relevant_chunks", []), 1):
                    label = f'{i}. {chunk["source"]} · page {chunk["page"]} · similarity {chunk["score"]:.3f}'
                    with st.expander(label):
                        st.write(chunk["content"])
        except requests.RequestException as exc:
            st.error(f"The policy API is unavailable: {exc}")
        except (KeyError, ValueError) as exc:
            st.error(f"The API returned an unexpected response: {exc}")
