"""Streamlit UI for the Document Intelligence Assistant."""

import os
from typing import Any

import requests
import streamlit as st

BACKEND_URL = os.environ.get("BACKEND_URL", "http://localhost:8000")
REQUEST_TIMEOUT = 120

st.set_page_config(
    page_title="Document Intelligence",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ----------------------- Pastel theme CSS -----------------------
PASTEL_CSS = """
<style>
  /* Hide Streamlit chrome */
  #MainMenu {visibility: hidden;}
  footer {visibility: hidden;}
  header[data-testid="stHeader"] {background: transparent;}

  /* Pastel palette (works in both light & dark mode) */
  :root {
    --pastel-lavender: #C7B8EA;
    --pastel-pink: #F4C2C2;
    --pastel-mint: #B5EAD7;
    --pastel-peach: #FFD8B1;
    --pastel-sky: #C7E9F1;
  }

  /* App background — soft gradient */
  .stApp {
    background:
      radial-gradient(at 0% 0%, rgba(199, 184, 234, 0.10) 0px, transparent 50%),
      radial-gradient(at 100% 100%, rgba(181, 234, 215, 0.08) 0px, transparent 50%);
  }

  /* Title */
  h1 {
    font-weight: 700 !important;
    letter-spacing: -0.02em;
    background: linear-gradient(120deg, var(--pastel-lavender), var(--pastel-pink));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
  }

  /* Tabs — pill style */
  .stTabs [data-baseweb="tab-list"] {
    gap: 6px;
    background: transparent;
    border-bottom: none;
  }
  .stTabs [data-baseweb="tab"] {
    padding: 8px 18px;
    border-radius: 999px;
    background: rgba(199, 184, 234, 0.08);
    border: 1px solid rgba(199, 184, 234, 0.15);
    transition: all 0.2s ease;
  }
  .stTabs [data-baseweb="tab"]:hover {
    background: rgba(199, 184, 234, 0.15);
  }
  .stTabs [aria-selected="true"] {
    background: rgba(199, 184, 234, 0.25) !important;
    border-color: var(--pastel-lavender) !important;
  }

  /* Buttons */
  .stButton > button {
    border-radius: 10px;
    border: 1px solid rgba(199, 184, 234, 0.3);
    background: rgba(199, 184, 234, 0.08);
    font-weight: 500;
    transition: all 0.15s ease;
  }
  .stButton > button:hover {
    background: rgba(199, 184, 234, 0.2);
    border-color: var(--pastel-lavender);
    transform: translateY(-1px);
  }

  /* Sidebar */
  section[data-testid="stSidebar"] {
    background: rgba(199, 184, 234, 0.04);
    border-right: 1px solid rgba(199, 184, 234, 0.12);
  }
  section[data-testid="stSidebar"] h1,
  section[data-testid="stSidebar"] h2,
  section[data-testid="stSidebar"] h3 {
    -webkit-text-fill-color: initial !important;
    background: none !important;
  }

  /* File uploader */
  [data-testid="stFileUploader"] section {
    background: rgba(199, 184, 234, 0.06);
    border: 1px dashed rgba(199, 184, 234, 0.4);
    border-radius: 12px;
  }

  /* Chat bubbles */
  [data-testid="stChatMessage"] {
    background: rgba(255, 255, 255, 0.03);
    border: 1px solid rgba(199, 184, 234, 0.12);
    border-radius: 14px;
    padding: 12px 16px;
    margin-bottom: 12px;
  }

  /* Chat input */
  [data-testid="stChatInput"] {
    border-radius: 14px;
    border: 1px solid rgba(199, 184, 234, 0.25);
  }

  /* Containers (document cards) */
  [data-testid="stVerticalBlockBorderWrapper"] {
    border-radius: 12px;
    border-color: rgba(199, 184, 234, 0.15) !important;
  }

  /* Expanders (source citations) */
  [data-testid="stExpander"] {
    border-radius: 10px;
    border: 1px solid rgba(181, 234, 215, 0.18);
    background: rgba(181, 234, 215, 0.04);
  }

  /* Code blocks (source snippets) */
  [data-testid="stCodeBlock"] {
    background: rgba(199, 184, 234, 0.05) !important;
    border-radius: 8px;
  }

  /* Tool-used caption */
  .tool-badge {
    display: inline-block;
    padding: 2px 10px;
    border-radius: 999px;
    background: rgba(244, 194, 194, 0.15);
    border: 1px solid rgba(244, 194, 194, 0.3);
    font-size: 0.78rem;
    color: var(--pastel-pink);
    margin-top: 4px;
  }

  /* Info / warning boxes */
  [data-testid="stAlert"] {
    border-radius: 12px;
    border: 1px solid rgba(199, 184, 234, 0.2);
  }
</style>
"""
st.markdown(PASTEL_CSS, unsafe_allow_html=True)


# ----------------------- API helpers -----------------------
class QuotaExceeded(Exception):
    pass


def api_get(path: str, **kwargs) -> Any:
    r = requests.get(f"{BACKEND_URL}{path}", timeout=REQUEST_TIMEOUT, **kwargs)
    r.raise_for_status()
    return r.json()


def api_post(path: str, json: dict | None = None, files: dict | None = None) -> Any:
    r = requests.post(
        f"{BACKEND_URL}{path}", json=json, files=files, timeout=REQUEST_TIMEOUT
    )
    if r.status_code == 429:
        try:
            detail = r.json().get("detail", "Daily quota exceeded.")
        except ValueError:
            detail = "Daily quota exceeded."
        raise QuotaExceeded(detail)
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


# ----------------------- Session state -----------------------
if "history" not in st.session_state:
    st.session_state.history = []
if "use_agent" not in st.session_state:
    st.session_state.use_agent = True


# ----------------------- Sidebar -----------------------
with st.sidebar:
    st.markdown("### 📁 Documents")
    uploaded = st.file_uploader(
        "Drop files here",
        type=["pdf", "docx", "txt"],
        accept_multiple_files=True,
        label_visibility="collapsed",
    )
    if uploaded and st.button("✨ Index uploads", use_container_width=True, type="primary"):
        progress = st.progress(0, text="Starting…")
        for i, f in enumerate(uploaded, start=1):
            progress.progress((i - 1) / len(uploaded), text=f"Indexing {f.name}…")
            try:
                resp = api_post(
                    "/documents/upload",
                    files={"file": (f.name, f.getvalue(), f.type)},
                )
                st.toast(f"Indexed {resp['document']['filename']}", icon="✅")
            except requests.RequestException as e:
                st.toast(f"{f.name}: {e}", icon="❌")
        progress.progress(1.0, text="Done")
        progress.empty()
        st.rerun()

    st.markdown("---")
    st.markdown("### 📚 Library")
    docs = fetch_documents()
    if not docs:
        st.caption("No documents yet.")
    for d in docs:
        with st.container(border=True):
            st.markdown(f"**{d['filename']}**")
            st.caption(
                f"{d['chunk_count']} chunks · {d['size_bytes'] // 1024} KB"
            )
            if st.button("🗑 Delete", key=f"del-{d['id']}", use_container_width=True):
                try:
                    api_delete(f"/documents/{d['id']}")
                    st.toast("Deleted", icon="🗑")
                    st.rerun()
                except requests.RequestException as e:
                    st.error(str(e))

    st.markdown("---")
    st.toggle("🤖 Use agent (LangGraph)", key="use_agent")
    if st.button("🧹 Clear chat", use_container_width=True):
        st.session_state.history = []
        st.rerun()

    st.markdown("---")
    st.caption(
        "Built with FastAPI, LangGraph, ChromaDB & Gemini · "
        "[GitHub](https://github.com/dhaniyaaaku/document-intelligence-assistant)"
    )


# ----------------------- Header -----------------------
st.markdown(
    """
    <div style="margin-bottom: 8px;">
      <h1 style="margin-bottom: 0;">Document Intelligence</h1>
      <p style="color: rgba(232, 232, 240, 0.6); margin-top: 4px; font-size: 1.05rem;">
        Upload documents · ask anything · get grounded answers with sources.
      </p>
    </div>
    """,
    unsafe_allow_html=True,
)

tab_chat, tab_summary, tab_compare, tab_insights = st.tabs(
    ["💬 Chat", "📝 Summary", "⚖️ Comparison", "💡 Key Insights"]
)


# ----------------------- Chat tab -----------------------
with tab_chat:
    if not st.session_state.history:
        st.markdown(
            """
            <div style="
              padding: 32px;
              border-radius: 16px;
              background: rgba(199, 184, 234, 0.05);
              border: 1px dashed rgba(199, 184, 234, 0.2);
              text-align: center;
              margin: 24px 0;
            ">
              <div style="font-size: 2.4rem; margin-bottom: 8px;">💭</div>
              <div style="font-weight: 600; margin-bottom: 4px;">Ask anything about your documents</div>
              <div style="color: rgba(232, 232, 240, 0.55); font-size: 0.92rem;">
                Try: <em>"summarize this"</em> · <em>"what are the action items?"</em> · <em>"compare doc A vs doc B"</em>
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    for msg in st.session_state.history:
        avatar = "🧑" if msg["role"] == "user" else "🤖"
        with st.chat_message(msg["role"], avatar=avatar):
            st.markdown(msg["content"])
            if msg.get("tool_used"):
                st.markdown(
                    f'<span class="tool-badge">🔧 {msg["tool_used"]}</span>',
                    unsafe_allow_html=True,
                )
            sources = msg.get("sources") or []
            if sources:
                with st.expander(f"📎 Sources ({len(sources)})"):
                    for i, s in enumerate(sources, start=1):
                        st.markdown(
                            f"**[{i}] {s['filename']}** · chunk {s['chunk_index']}"
                            + (f" · score {s['score']:.2f}" if s.get("score") else "")
                        )
                        snippet = s["text"][:600] + ("…" if len(s["text"]) > 600 else "")
                        st.code(snippet, language=None)
            trace = msg.get("agent_trace") or []
            if trace:
                with st.expander("🧠 Agent trace"):
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
            except QuotaExceeded as e:
                st.session_state.history.append(
                    {
                        "role": "assistant",
                        "content": f"⚠️ {e}\n\nThe Gemini free tier resets at midnight Pacific Time.",
                    }
                )
            except requests.RequestException as e:
                st.session_state.history.append(
                    {"role": "assistant", "content": f"Error: {e}"}
                )
        st.rerun()


# ----------------------- Summary tab -----------------------
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
        if st.button("✨ Generate summary", type="primary"):
            with st.spinner("Summarizing…"):
                try:
                    resp = api_post(
                        "/analysis/summarize", json={"document_id": choice["id"]}
                    )
                    st.markdown(resp["summary"])
                except QuotaExceeded as e:
                    st.warning(f"⚠️ {e}")
                except requests.RequestException as e:
                    st.error(str(e))


# ----------------------- Comparison tab -----------------------
with tab_compare:
    docs = fetch_documents()
    if len(docs) < 2:
        st.info("Upload at least two documents to compare.")
    else:
        col1, col2 = st.columns(2)
        a = col1.selectbox("Document A", docs, format_func=lambda d: d["filename"], key="cmp-a")
        b = col2.selectbox("Document B", docs, format_func=lambda d: d["filename"], key="cmp-b")
        if st.button("⚖️ Compare", type="primary"):
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
                    except QuotaExceeded as e:
                        st.warning(f"⚠️ {e}")
                    except requests.RequestException as e:
                        st.error(str(e))


# ----------------------- Insights tab -----------------------
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
        if col_t.button("🏷 Extract topics", use_container_width=True):
            with st.spinner("Extracting topics…"):
                try:
                    resp = api_post(
                        "/analysis/topics",
                        json={"document_id": choice["id"], "n_topics": 5},
                    )
                    st.markdown("#### Top topics")
                    for t in resp["topics"]:
                        st.markdown(f"- {t}")
                except QuotaExceeded as e:
                    st.warning(f"⚠️ {e}")
                except requests.RequestException as e:
                    st.error(str(e))
        if col_a.button("✅ Action items", use_container_width=True):
            with st.spinner("Extracting action items…"):
                try:
                    resp = api_post(
                        "/analysis/action-items", json={"document_id": choice["id"]}
                    )
                    items = resp["action_items"]
                    if not items:
                        st.info("No action items found.")
                    else:
                        st.markdown("#### Action items")
                        for t in items:
                            st.markdown(f"- {t}")
                except QuotaExceeded as e:
                    st.warning(f"⚠️ {e}")
                except requests.RequestException as e:
                    st.error(str(e))
