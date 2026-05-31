"""High-level document analysis: summary, topics, comparison, action items."""

from langchain_core.messages import HumanMessage, SystemMessage

from backend.services.document_service import get_document, get_full_text
from backend.services.llm_client import get_llm
from backend.utils.logging import get_logger

log = get_logger(__name__)

# Hard cap to avoid blowing the LLM context on huge files.
_MAX_CHARS = 30_000


class DocumentNotFoundError(LookupError):
    pass


def _load_text(document_id: str) -> tuple[str, str]:
    meta = get_document(document_id)
    if not meta:
        raise DocumentNotFoundError(f"No document with id {document_id}")
    text = get_full_text(document_id)
    if len(text) > _MAX_CHARS:
        text = text[:_MAX_CHARS] + "\n\n[...truncated...]"
    return meta.filename, text


def summarize(document_id: str) -> str:
    filename, text = _load_text(document_id)
    llm = get_llm()
    messages = [
        SystemMessage(
            content="You produce concise, faithful summaries of documents. "
            "Do not invent facts."
        ),
        HumanMessage(
            content=(
                f"Summarize the document '{filename}' in 5-8 bullet points covering "
                f"its purpose, key arguments, and conclusions.\n\nDOCUMENT:\n{text}"
            )
        ),
    ]
    return llm.invoke(messages).content


def extract_topics(document_id: str, n_topics: int = 5) -> list[str]:
    filename, text = _load_text(document_id)
    llm = get_llm()
    messages = [
        SystemMessage(
            content="You extract the main topics covered in a document. "
            "Return exactly one topic per line, no numbering, no extra text."
        ),
        HumanMessage(
            content=(
                f"Extract the top {n_topics} key topics from '{filename}'.\n\n"
                f"DOCUMENT:\n{text}"
            )
        ),
    ]
    raw = llm.invoke(messages).content
    topics = [line.strip("-* \t") for line in raw.splitlines() if line.strip()]
    return topics[:n_topics]


def compare_documents(document_id_a: str, document_id_b: str) -> str:
    name_a, text_a = _load_text(document_id_a)
    name_b, text_b = _load_text(document_id_b)
    llm = get_llm()
    messages = [
        SystemMessage(
            content="You compare two documents objectively. "
            "Highlight similarities, differences, and any contradictions."
        ),
        HumanMessage(
            content=(
                f"Compare these two documents.\n\n"
                f"=== DOCUMENT A: {name_a} ===\n{text_a}\n\n"
                f"=== DOCUMENT B: {name_b} ===\n{text_b}\n\n"
                "Structure your answer as:\n"
                "1. Shared themes\n2. Key differences\n3. Contradictions (if any)\n"
                "4. Overall assessment"
            )
        ),
    ]
    return llm.invoke(messages).content


def extract_action_items(document_id: str) -> list[str]:
    filename, text = _load_text(document_id)
    llm = get_llm()
    messages = [
        SystemMessage(
            content="You extract concrete action items from a document. "
            "Return one action per line, imperative voice, no numbering. "
            "If the document contains no action items, return the single line: NONE."
        ),
        HumanMessage(
            content=f"Extract action items from '{filename}'.\n\nDOCUMENT:\n{text}"
        ),
    ]
    raw = llm.invoke(messages).content
    if raw.strip().upper().startswith("NONE"):
        return []
    return [line.strip("-* \t") for line in raw.splitlines() if line.strip()]
