"""Retrieval-augmented question answering with source grounding."""

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

from backend.models.schemas import ChatMessage, ChatResponse, SourceChunk
from backend.rag import embeddings, vector_store
from backend.services.llm_client import get_llm
from backend.utils.config import get_settings
from backend.utils.logging import get_logger

log = get_logger(__name__)

SYSTEM_PROMPT = """You are a precise document analysis assistant.

RULES:
1. Answer the user's question using ONLY the context passages below.
2. If the context does not contain enough information, say: "I cannot find this in the uploaded documents." Do not guess.
3. Cite sources inline as [Source N] where N is the passage number.
4. Be concise. Use bullet points when listing items.
"""


def _format_context(sources: list[SourceChunk]) -> str:
    blocks = []
    for i, s in enumerate(sources, start=1):
        blocks.append(f"[Source {i}] ({s.filename}, chunk {s.chunk_index})\n{s.text}")
    return "\n\n".join(blocks) if blocks else "(no relevant passages found)"


def retrieve(
    question: str, document_ids: list[str] | None = None, top_k: int | None = None
) -> list[SourceChunk]:
    settings = get_settings()
    k = top_k or settings.top_k
    query_vec = embeddings.embed_query(question)
    hits = vector_store.query(query_vec, top_k=k, document_ids=document_ids)
    return [SourceChunk(**h) for h in hits]


def answer_question(
    question: str,
    document_ids: list[str] | None = None,
    history: list[ChatMessage] | None = None,
) -> ChatResponse:
    sources = retrieve(question, document_ids=document_ids)
    llm = get_llm()

    messages: list = [SystemMessage(content=SYSTEM_PROMPT)]
    for msg in history or []:
        if msg.role == "user":
            messages.append(HumanMessage(content=msg.content))
        elif msg.role == "assistant":
            messages.append(AIMessage(content=msg.content))

    user_prompt = (
        f"CONTEXT:\n{_format_context(sources)}\n\n"
        f"QUESTION: {question}\n\n"
        "Answer using only the context above. Cite sources as [Source N]."
    )
    messages.append(HumanMessage(content=user_prompt))

    log.info("Calling LLM with %d sources", len(sources))
    response = llm.invoke(messages)
    return ChatResponse(answer=response.content, sources=sources)
