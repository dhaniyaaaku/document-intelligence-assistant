"""Streamlit UI for the Document Intelligence Assistant."""

import os
from typing import Any

import requests
import streamlit as st

BACKEND_URL = os.environ.get("BACKEND_URL", "http://localhost:8000")
REQUEST_TIMEOUT = 120

st.set_page_config(page_title="Document Intelligence Assistant", layout="wide")


# ---------- API helpers ----------
def api_get(path: str, **kwargs) -> Any:
    r = requests.get(f"{BACKEND_URL}{path}", timeout=REQUEST_TIMEOUT, **kwargs)
    r.raise_for_status()
    return r.json()


def api_post(path: str, json: dict | None = None, files: dict | None = None) -> Any:
    r = requests.post(
        f"{BACKEND_URL}{path}", json=json, files=files, timeout=REQUEST_TIMEOUT
    )
    r.raise_for_status()
    return r.json()


def api_delete(path: str) -> None:
    r = requests.delete(f"{BACKEND_URL}{path}", timeout=REQUEST_TIMEOUT)
    r.raise_for_status()


def fetch_documents() -> list[dict]:
    try:
        return api_get("/documents").get("documents", [])
    except requests.RequestException as e:
        st.error(f"Cannot reach backend at {BACKEND_URL}: {e}")
        return []


# ---------- Session state ----------
if "history" not in st.session_state:
    st.session_state.history = []  # list of {role, content, sources, tool_used}
if "use_agent" not in st.session_state:
    st.session_state.use_agent = True

# ---------- Sidebar ----------
with st.sidebar:
    st.title("Documents")
    uploaded = st.file_uploader(
        "Upload PDF / DOCX / TXT",
        type=["pdf", "docx", "txt"],
        accept_multiple_files=True,
    )
    if uploaded and st.button("Index uploads", use_container_width=True):
        for f in uploaded:
            try:
                resp = api_post(
                    "/documents/upload",
                    files={"file": (f.name, f.getvalue(), f.type)},
                )
                st.success(f"Indexed: {resp['document']['filename']}")
            except requests.RequestException as e:
                st.error(f"{f.name}: {e}")

    st.divider()
    st.subheader("Indexed")
    docs = fetch_documents()
    if not docs:
        st.caption("No documents yet.")
    for d in docs:
        with st.container(border=True):
            st.write(f"**{d['filename']}**")
            st.caption(
                f"{d['chunk_count']} chunks · {d['size_bytes'] // 1024} KB · "
                f"id: `{d['id'][:8]}…`"
            )
            if st.button("Delete", key=f"del-{d['id']}", use_container_width=True):
                try:
                    api_delete(f"/documents/{d['id']}")
                    st.rerun()
                except requests.RequestException as e:
                    st.error(str(e))

    st.divider()
    st.toggle("Use agent (LangGraph)", key="use_agent")
    if st.button("Clear chat", use_container_width=True):
        st.session_state.history = []
        st.rerun()


# ---------- Main tabs ----------
st.title("Document Intelligence Assistant")
tab_chat, tab_summary, tab_compare, tab_insights = st.tabs(
    ["Chat", "Summary", "Comparison", "Key Insights"]
)


# ---- Chat tab ----
with tab_chat:
    for msg in st.session_state.history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if msg.get("tool_used"):
                st.caption(f"Tool used: `{msg['tool_used']}`")
            sources = msg.get("sources") or []
            if sources:
                with st.expander(f"Sources ({len(sources)})"):
                    for i, s in enumerate(sources, start=1):
                        st.markdown(
                            f"**[{i}] {s['filename']}** — chunk {s['chunk_index']}"
                            + (f" · score {s['score']:.2f}" if s.get("score") else "")
                        )
                        st.code(s["text"][:600] + ("..." if len(s["text"]) > 600 else ""))
            trace = msg.get("agent_trace") or []
            if trace:
                with st.expander("Agent trace"):
                    for step in trace:
                        st.json(step)

    question = st.chat_input("Ask a question about your documents…")
    if question:
        st.session_state.history.append({"role": "user", "content": question})
        endpoint = "/chat/agent" if st.session_state.use_agent else "/chat"
        history_payload = [
            {"role": m["role"], "content": m["content"]}
            for m in st.session_state.history
            if m["role"] in {"user", "assistant"}
        ][:-1]
        with st.spinner("Thinking…"):
            try:
                resp = api_post(
                    endpoint, json={"question": question, "history": history_payload}
                )
                st.session_state.history.append(
                    {
                        "role": "assistant",
                        "content": resp.get("answer", ""),
                        "sources": resp.get("sources", []),
                        "tool_used": resp.get("tool_used"),
                        "agent_trace": resp.get("agent_trace", []),
                    }
                )
            except requests.RequestException as e:
                st.session_state.history.append(
                    {"role": "assistant", "content": f"Error: {e}"}
                )
        st.rerun()


# ---- Summary tab ----
with tab_summary:
    docs = fetch_documents()
    if not docs:
        st.info("Upload a document first.")
    else:
        choice = st.selectbox(
            "Document",
            options=docs,
            format_func=lambda d: d["filename"],
            key="summary-pick",
        )
        if st.button("Generate summary"):
            with st.spinner("Summarizing…"):
                try:
                    resp = api_post(
                        "/analysis/summarize", json={"document_id": choice["id"]}
                    )
                    st.markdown(resp["summary"])
                except requests.RequestException as e:
                    st.error(str(e))


# ---- Comparison tab ----
with tab_compare:
    docs = fetch_documents()
    if len(docs) < 2:
        st.info("Upload at least two documents to compare.")
    else:
        col1, col2 = st.columns(2)
        a = col1.selectbox("Doc A", docs, format_func=lambda d: d["filename"], key="cmp-a")
        b = col2.selectbox("Doc B", docs, format_func=lambda d: d["filename"], key="cmp-b")
        if st.button("Compare"):
            if a["id"] == b["id"]:
                st.warning("Pick two different documents.")
            else:
                with st.spinner("Comparing…"):
                    try:
                        resp = api_post(
                            "/analysis/compare",
                            json={"document_id_a": a["id"], "document_id_b": b["id"]},
                        )
                        st.markdown(resp["comparison"])
                    except requests.RequestException as e:
                        st.error(str(e))


# ---- Insights tab ----
with tab_insights:
    docs = fetch_documents()
    if not docs:
        st.info("Upload a document first.")
    else:
        choice = st.selectbox(
            "Document",
            options=docs,
            format_func=lambda d: d["filename"],
            key="insights-pick",
        )
        col_t, col_a = st.columns(2)
        if col_t.button("Extract topics"):
            with st.spinner("Extracting topics…"):
                try:
                    resp = api_post(
                        "/analysis/topics",
                        json={"document_id": choice["id"], "n_topics": 5},
                    )
                    for t in resp["topics"]:
                        st.markdown(f"- {t}")
                except requests.RequestException as e:
                    st.error(str(e))
        if col_a.button("Action items"):
            with st.spinner("Extracting action items…"):
                try:
                    resp = api_post(
                        "/analysis/action-items", json={"document_id": choice["id"]}
                    )
                    items = resp["action_items"]
                    if not items:
                        st.info("No action items found.")
                    for t in items:
                        st.markdown(f"- {t}")
                except requests.RequestException as e:
                    st.error(str(e))
