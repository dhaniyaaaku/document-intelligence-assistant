"""Streamlit UI for PaperPal — soft editorial dark theme."""

import os
from typing import Any

import requests
import streamlit as st

BACKEND_URL = os.environ.get("BACKEND_URL", "http://localhost:8000")
REQUEST_TIMEOUT = 120

st.set_page_config(
    page_title="PaperPal",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ----------------------- Soft editorial dark theme -----------------------
EDITORIAL_CSS = """
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,500;9..144,600;9..144,700&family=Inter:wght@400;500;600&display=swap" rel="stylesheet">

<style>
  /* Strip Streamlit chrome */
  #MainMenu, footer, header[data-testid="stHeader"] { visibility: hidden; }
  [data-testid="stToolbar"] { display: none; }

  /* Hide the auto-generated anchor link icon next to headers */
  [data-testid="stHeaderActionElements"] { display: none !important; }
  .stMarkdown a[href^="#"] svg,
  h1 > a, h2 > a, h3 > a { display: none !important; }

  :root {
    --bg-base: #1B1A1F;
    --bg-elevated: #232229;
    --bg-card: rgba(255, 250, 245, 0.025);
    --border-soft: rgba(232, 220, 210, 0.08);
    --border-medium: rgba(232, 220, 210, 0.14);
    --text-primary: #EFE9E2;
    --text-secondary: rgba(239, 233, 226, 0.62);
    --text-tertiary: rgba(239, 233, 226, 0.40);
    --accent-warm: #E8B7A8;       /* warm peach */
    --accent-sage: #A8C5B5;       /* dusty sage */
    --accent-lavender: #C0B5D6;   /* muted lavender */
  }

  html, body, [class*="css"] { font-family: 'Inter', -apple-system, system-ui, sans-serif; }

  /* Background: warm charcoal with a single subtle glow behind the hero */
  .stApp {
    background: var(--bg-base);
    background-image:
      radial-gradient(ellipse 800px 400px at 30% 0%, rgba(232, 183, 168, 0.06), transparent 60%),
      radial-gradient(ellipse 600px 300px at 100% 100%, rgba(192, 181, 214, 0.04), transparent 60%);
    color: var(--text-primary);
  }
  .stApp > header { background: transparent; }

  /* Block container: editorial reading width */
  .main .block-container {
    padding-top: 2.2rem;
    padding-bottom: 4rem;
    max-width: 1080px;
  }

  /* Display typography */
  h1, .stMarkdown h1 {
    font-family: 'Fraunces', Georgia, serif !important;
    font-weight: 600 !important;
    font-size: 2.6rem !important;
    line-height: 1.05 !important;
    letter-spacing: -0.025em;
    font-variation-settings: "opsz" 144;
    color: var(--text-primary) !important;
    margin-bottom: 0.5rem !important;
  }
  h2, .stMarkdown h2 {
    font-family: 'Fraunces', Georgia, serif !important;
    font-weight: 500 !important;
    letter-spacing: -0.015em;
  }
  h3, h4, .stMarkdown h3, .stMarkdown h4 {
    font-family: 'Inter', sans-serif !important;
    font-weight: 600 !important;
    letter-spacing: -0.005em;
    color: var(--text-primary) !important;
  }

  /* Hero block */
  .pp-hero {
    margin-bottom: 1.6rem;
    padding-bottom: 1.4rem;
    border-bottom: 1px solid var(--border-soft);
  }
  .pp-hero .pp-tagline {
    font-family: 'Inter', sans-serif;
    font-size: 1rem;
    line-height: 1.55;
    color: var(--text-secondary);
    max-width: 620px;
    font-weight: 400;
    margin-top: 0.3rem;
  }
  .pp-hero .pp-tagline em {
    font-family: 'Fraunces', Georgia, serif;
    font-style: italic;
    color: var(--accent-warm);
    font-weight: 500;
  }

  /* Tabs: text-only with a hand-feeling underline on active */
  .stTabs { margin-top: 0; }
  .stTabs [data-baseweb="tab-list"] {
    gap: 2rem;
    background: transparent !important;
    border-bottom: 1px solid var(--border-soft) !important;
    padding-bottom: 0.55rem;
    margin-bottom: 1.6rem;
  }
  .stTabs [data-baseweb="tab-list"]::after { display: none; }
  .stTabs [data-baseweb="tab-highlight"],
  .stTabs [data-baseweb="tab-border"] { display: none !important; }
  .stTabs [data-baseweb="tab"] {
    padding: 0.4rem 0 !important;
    background: transparent !important;
    border: none !important;
    border-radius: 0 !important;
    color: var(--text-tertiary) !important;
    font-family: 'Inter', sans-serif;
    font-size: 0.95rem;
    font-weight: 500;
    letter-spacing: 0.005em;
    transition: color 0.2s ease;
  }
  .stTabs [data-baseweb="tab"]:hover { color: var(--text-secondary) !important; }
  .stTabs [aria-selected="true"] {
    color: var(--text-primary) !important;
    background: transparent !important;
    position: relative;
  }
  .stTabs [aria-selected="true"]::after {
    content: "";
    position: absolute;
    left: 0; right: 0; bottom: -0.55rem;
    height: 2px;
    border-radius: 2px;
    background: linear-gradient(90deg, var(--accent-warm), var(--accent-lavender));
  }

  /* Buttons */
  .stButton > button {
    border-radius: 8px;
    border: 1px solid var(--border-medium);
    background: var(--bg-card);
    color: var(--text-primary);
    font-family: 'Inter', sans-serif;
    font-weight: 500;
    font-size: 0.9rem;
    padding: 0.5rem 1rem;
    transition: all 0.18s ease;
  }
  .stButton > button:hover {
    background: rgba(232, 183, 168, 0.08);
    border-color: var(--accent-warm);
    color: var(--text-primary);
  }
  .stButton > button[kind="primary"] {
    background: var(--accent-warm);
    color: #1B1A1F;
    border-color: var(--accent-warm);
  }
  .stButton > button[kind="primary"]:hover {
    background: #f0c4b5;
    border-color: #f0c4b5;
  }

  /* Sidebar */
  section[data-testid="stSidebar"] {
    background: var(--bg-elevated);
    border-right: 1px solid var(--border-soft);
  }
  section[data-testid="stSidebar"] .block-container { padding-top: 2.5rem; }
  section[data-testid="stSidebar"] h1,
  section[data-testid="stSidebar"] h2,
  section[data-testid="stSidebar"] h3 {
    font-family: 'Inter', sans-serif !important;
    font-size: 0.72rem !important;
    font-weight: 600 !important;
    text-transform: uppercase;
    letter-spacing: 0.16em;
    color: var(--text-tertiary) !important;
    margin-bottom: 0.8rem !important;
  }

  /* Wordmark in sidebar */
  .pp-wordmark {
    font-family: 'Fraunces', Georgia, serif;
    font-weight: 600;
    font-size: 1.5rem;
    letter-spacing: -0.02em;
    color: var(--text-primary);
    margin-bottom: 0.2rem;
  }
  .pp-wordmark-dot { color: var(--accent-warm); }
  .pp-wordmark-sub {
    font-family: 'Inter', sans-serif;
    font-size: 0.75rem;
    color: var(--text-tertiary);
    letter-spacing: 0.08em;
    margin-bottom: 2rem;
  }

  /* File uploader */
  [data-testid="stFileUploader"] section {
    background: var(--bg-card);
    border: 1px dashed var(--border-medium);
    border-radius: 10px;
    padding: 1.2rem;
  }
  [data-testid="stFileUploader"] section:hover {
    border-color: var(--accent-warm);
  }

  /* Chat bubbles */
  [data-testid="stChatMessage"] {
    background: var(--bg-card);
    border: 1px solid var(--border-soft);
    border-radius: 14px;
    padding: 1rem 1.2rem;
    margin-bottom: 0.8rem;
  }
  [data-testid="stChatMessage"] p { font-size: 0.97rem; line-height: 1.6; }

  /* Chat input */
  [data-testid="stChatInput"] {
    border-radius: 12px;
    border: 1px solid var(--border-medium);
    background: var(--bg-elevated);
  }

  /* Containers (document cards) */
  [data-testid="stVerticalBlockBorderWrapper"] {
    border-radius: 10px;
    border: 1px solid var(--border-soft) !important;
    background: var(--bg-card);
  }

  /* Expanders */
  [data-testid="stExpander"] {
    border-radius: 10px;
    border: 1px solid var(--border-soft);
    background: var(--bg-card);
  }
  [data-testid="stExpander"] summary { font-size: 0.88rem; color: var(--text-secondary); }

  /* Code blocks */
  [data-testid="stCodeBlock"] {
    background: rgba(0, 0, 0, 0.25) !important;
    border-radius: 8px;
    border: 1px solid var(--border-soft);
  }
  [data-testid="stCodeBlock"] code { font-size: 0.82rem !important; }

  /* Alerts */
  [data-testid="stAlert"] {
    border-radius: 10px;
    border: 1px solid var(--border-soft);
    background: var(--bg-card);
  }

  /* Empty state card */
  .pp-empty {
    padding: 3rem 2rem;
    border-radius: 14px;
    background: var(--bg-card);
    border: 1px solid var(--border-soft);
    text-align: center;
    margin: 1rem 0 2rem 0;
  }
  .pp-empty-title {
    font-family: 'Fraunces', Georgia, serif;
    font-size: 1.3rem;
    font-weight: 500;
    color: var(--text-primary);
    margin-bottom: 0.4rem;
  }
  .pp-empty-sub {
    font-family: 'Inter', sans-serif;
    font-size: 0.9rem;
    color: var(--text-tertiary);
  }
  .pp-empty-sub em {
    color: var(--text-secondary);
    font-style: italic;
    background: rgba(232, 183, 168, 0.06);
    padding: 1px 6px;
    border-radius: 4px;
    margin: 0 2px;
  }

  /* Tool badge */
  .pp-tool-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 3px 10px;
    border-radius: 999px;
    background: rgba(168, 197, 181, 0.08);
    border: 1px solid rgba(168, 197, 181, 0.18);
    font-family: 'Inter', sans-serif;
    font-size: 0.72rem;
    color: var(--accent-sage);
    letter-spacing: 0.02em;
    margin-top: 0.4rem;
  }
  .pp-tool-badge::before {
    content: "";
    width: 5px; height: 5px;
    border-radius: 50%;
    background: var(--accent-sage);
  }

  /* Toggle */
  [data-baseweb="checkbox"] label, label { color: var(--text-secondary) !important; }

  /* Selectbox */
  [data-baseweb="select"] > div {
    background: var(--bg-card) !important;
    border: 1px solid var(--border-medium) !important;
    border-radius: 8px !important;
  }

  /* Soft divider replacement */
  hr {
    border: none;
    height: 1px;
    background: var(--border-soft);
    margin: 1.4rem 0;
  }

  /* Caption */
  .stCaption, [data-testid="stCaptionContainer"] {
    color: var(--text-tertiary) !important;
    font-size: 0.78rem;
  }

  /* Scrollbar */
  ::-webkit-scrollbar { width: 10px; height: 10px; }
  ::-webkit-scrollbar-track { background: transparent; }
  ::-webkit-scrollbar-thumb {
    background: var(--border-medium);
    border-radius: 5px;
  }
  ::-webkit-scrollbar-thumb:hover { background: var(--text-tertiary); }
</style>
"""
st.markdown(EDITORIAL_CSS, unsafe_allow_html=True)


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
    st.markdown(
        '<div class="pp-wordmark">paperpal<span class="pp-wordmark-dot">.</span></div>'
        '<div class="pp-wordmark-sub">a quiet reading companion</div>',
        unsafe_allow_html=True,
    )

    st.markdown("### Upload")
    uploaded = st.file_uploader(
        "Drop files here",
        type=["pdf", "docx", "txt"],
        accept_multiple_files=True,
        label_visibility="collapsed",
    )
    if uploaded and st.button("Index", use_container_width=True, type="primary"):
        progress = st.progress(0, text="Starting…")
        for i, f in enumerate(uploaded, start=1):
            progress.progress((i - 1) / len(uploaded), text=f"Indexing {f.name}…")
            try:
                resp = api_post(
                    "/documents/upload",
                    files={"file": (f.name, f.getvalue(), f.type)},
                )
                st.toast(f"Indexed {resp['document']['filename']}")
            except requests.RequestException as e:
                st.toast(f"{f.name}: {e}")
        progress.progress(1.0, text="Done")
        progress.empty()
        st.rerun()

    st.markdown("### Library")
    docs = fetch_documents()
    if not docs:
        st.caption("Nothing here yet.")
    for d in docs:
        with st.container(border=True):
            st.markdown(f"**{d['filename']}**")
            st.caption(f"{d['chunk_count']} chunks · {d['size_bytes'] // 1024} KB")
            if st.button("Remove", key=f"del-{d['id']}", use_container_width=True):
                try:
                    api_delete(f"/documents/{d['id']}")
                    st.toast("Removed")
                    st.rerun()
                except requests.RequestException as e:
                    st.error(str(e))

    st.markdown("### Preferences")
    st.toggle("Agent mode", key="use_agent", help="Let the agent pick the right tool for each query.")
    if st.button("Clear conversation", use_container_width=True):
        st.session_state.history = []
        st.rerun()

    st.markdown("---")
    st.caption(
        "FastAPI · LangGraph · ChromaDB · Gemini  \n"
        "[github](https://github.com/dhaniyaaaku/document-intelligence-assistant)"
    )


# ----------------------- Hero -----------------------
st.markdown(
    """
    <div class="pp-hero">
      <h1>read between the lines.</h1>
      <p class="pp-tagline">
        Upload a paper, report, or contract. Ask anything in plain English and get
        answers drawn straight from the page, <em>with the exact passages shown as proof.</em>
      </p>
    </div>
    """,
    unsafe_allow_html=True,
)

tab_chat, tab_summary, tab_compare, tab_insights = st.tabs(
    ["Chat", "Summary", "Comparison", "Insights"]
)


# ----------------------- Chat tab -----------------------
with tab_chat:
    if not st.session_state.history:
        st.markdown(
            """
            <div class="pp-empty">
              <div class="pp-empty-title">Ask anything about your documents.</div>
              <div class="pp-empty-sub">
                Try <em>summarize this</em> or <em>what are the action items</em> or <em>compare A and B</em>.
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    for msg in st.session_state.history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if msg.get("tool_used"):
                st.markdown(
                    f'<span class="pp-tool-badge">{msg["tool_used"]}</span>',
                    unsafe_allow_html=True,
                )
            sources = msg.get("sources") or []
            if sources:
                with st.expander(f"Sources · {len(sources)}"):
                    for i, s in enumerate(sources, start=1):
                        st.markdown(
                            f"**[{i}] {s['filename']}** · chunk {s['chunk_index']}"
                            + (f" · {s['score']:.2f}" if s.get("score") else "")
                        )
                        snippet = s["text"][:600] + ("…" if len(s["text"]) > 600 else "")
                        st.code(snippet, language=None)
            trace = msg.get("agent_trace") or []
            if trace:
                with st.expander("Agent trace"):
                    for step in trace:
                        st.json(step)

    question = st.chat_input("Ask…")
    if question:
        st.session_state.history.append({"role": "user", "content": question})
        endpoint = "/chat/agent" if st.session_state.use_agent else "/chat"
        history_payload = [
            {"role": m["role"], "content": m["content"]}
            for m in st.session_state.history
            if m["role"] in {"user", "assistant"}
        ][:-1]
        with st.spinner("Reading…"):
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
                        "content": f"{e}\n\nThe Gemini free tier resets at midnight Pacific Time.",
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
        if st.button("Generate summary", type="primary"):
            with st.spinner("Reading…"):
                try:
                    resp = api_post(
                        "/analysis/summarize", json={"document_id": choice["id"]}
                    )
                    st.markdown(resp["summary"])
                except QuotaExceeded as e:
                    st.warning(str(e))
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
        if st.button("Compare", type="primary"):
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
                        st.warning(str(e))
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
        if col_t.button("Extract topics", use_container_width=True):
            with st.spinner("Extracting…"):
                try:
                    resp = api_post(
                        "/analysis/topics",
                        json={"document_id": choice["id"], "n_topics": 5},
                    )
                    st.markdown("#### Topics")
                    for t in resp["topics"]:
                        st.markdown(f"- {t}")
                except QuotaExceeded as e:
                    st.warning(str(e))
                except requests.RequestException as e:
                    st.error(str(e))
        if col_a.button("Action items", use_container_width=True):
            with st.spinner("Extracting…"):
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
                    st.warning(str(e))
                except requests.RequestException as e:
                    st.error(str(e))
