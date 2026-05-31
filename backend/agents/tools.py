"""LangChain Tool definitions wired to the service layer.

Each tool returns plain strings so the LLM can read them as observations.
"""

from langchain_core.tools import tool

from backend.services import analysis_service, chat_service, document_service


def _resolve_document(name_or_id: str) -> str | None:
    """Accept either a doc id or a filename (case-insensitive)."""
    name_or_id = name_or_id.strip().strip("'\"")
    meta = document_service.get_document(name_or_id)
    if meta:
        return meta.id
    for doc in document_service.list_documents():
        if doc.filename.lower() == name_or_id.lower():
            return doc.id
    return None


@tool
def search_documents(query: str) -> str:
    """Semantic search across all uploaded documents. Input: a search query string.
    Returns the most relevant passages with their source documents."""
    hits = chat_service.retrieve(query)
    if not hits:
        return "No relevant passages found."
    return "\n\n".join(
        f"[{i + 1}] {h.filename} (chunk {h.chunk_index}, score={h.score:.2f})\n{h.text}"
        for i, h in enumerate(hits)
    )


@tool
def answer_question(question: str) -> str:
    """Answer a question using retrieval-augmented generation across all documents.
    Use this for factual questions about document contents."""
    resp = chat_service.answer_question(question)
    return resp.answer


@tool
def summarize_document(document: str) -> str:
    """Summarize a document. Input: filename or document id."""
    doc_id = _resolve_document(document)
    if not doc_id:
        return f"Document '{document}' not found."
    return analysis_service.summarize(doc_id)


@tool
def extract_key_topics(document: str) -> str:
    """Extract the main topics from a document. Input: filename or document id."""
    doc_id = _resolve_document(document)
    if not doc_id:
        return f"Document '{document}' not found."
    topics = analysis_service.extract_topics(doc_id)
    return "Key topics:\n" + "\n".join(f"- {t}" for t in topics)


@tool
def compare_documents(documents: str) -> str:
    """Compare two documents. Input: two filenames or ids separated by ' vs '
    (e.g., 'report_q1.pdf vs report_q2.pdf')."""
    if " vs " not in documents.lower():
        return "Input must be two documents separated by ' vs '."
    parts = [p.strip() for p in documents.split(" vs ", 1)]
    if len(parts) != 2:
        parts = [p.strip() for p in documents.split(" VS ", 1)]
    id_a, id_b = _resolve_document(parts[0]), _resolve_document(parts[1])
    if not id_a or not id_b:
        return f"Could not resolve one or both documents: {parts}"
    return analysis_service.compare_documents(id_a, id_b)


@tool
def generate_action_items(document: str) -> str:
    """Extract concrete action items / TODOs from a document. Input: filename or id."""
    doc_id = _resolve_document(document)
    if not doc_id:
        return f"Document '{document}' not found."
    items = analysis_service.extract_action_items(doc_id)
    if not items:
        return "No action items found in this document."
    return "Action items:\n" + "\n".join(f"- {item}" for item in items)


ALL_TOOLS = [
    search_documents,
    answer_question,
    summarize_document,
    extract_key_topics,
    compare_documents,
    generate_action_items,
]
