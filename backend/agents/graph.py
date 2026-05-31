"""LangGraph ReAct-style agent that routes user queries to the right tool."""

from functools import lru_cache
from typing import Any

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage
from langgraph.prebuilt import create_react_agent

from backend.agents.tools import ALL_TOOLS
from backend.models.schemas import ChatMessage, ChatResponse, SourceChunk
from backend.services import chat_service
from backend.services.llm_client import get_llm
from backend.utils.logging import get_logger

log = get_logger(__name__)

AGENT_SYSTEM_PROMPT = """You are a document intelligence agent with tools.

Available tools:
- search_documents(query): semantic search for raw passages.
- answer_question(question): full RAG QA across all documents.
- summarize_document(document): summarize one document.
- extract_key_topics(document): list main topics in one document.
- compare_documents("A vs B"): compare two documents.
- generate_action_items(document): extract action items.

Pick exactly one tool per user request. Choose based on intent:
- "summarize / give me a summary / TL;DR" -> summarize_document
- "what topics / themes" -> extract_key_topics
- "compare / differences between" -> compare_documents
- "action items / tasks / TODOs" -> generate_action_items
- factual question -> answer_question
- raw search request -> search_documents

When passing a document argument, use the filename if the user mentioned one.
After getting the tool result, present it cleanly to the user.
"""


@lru_cache(maxsize=1)
def _agent():
    return create_react_agent(get_llm(), ALL_TOOLS)


def _to_lc_messages(history: list[ChatMessage]) -> list[BaseMessage]:
    out: list[BaseMessage] = [SystemMessage(content=AGENT_SYSTEM_PROMPT)]
    for m in history:
        if m.role == "user":
            out.append(HumanMessage(content=m.content))
        elif m.role == "assistant":
            out.append(AIMessage(content=m.content))
    return out


def _summarize_trace(messages: list[BaseMessage]) -> tuple[list[dict[str, Any]], str | None]:
    trace: list[dict[str, Any]] = []
    tool_used: str | None = None
    for msg in messages:
        msg_type = msg.__class__.__name__
        if msg_type == "AIMessage" and getattr(msg, "tool_calls", None):
            for call in msg.tool_calls:
                tool_used = tool_used or call.get("name")
                trace.append(
                    {
                        "step": "tool_call",
                        "tool": call.get("name"),
                        "args": call.get("args", {}),
                    }
                )
        elif msg_type == "ToolMessage":
            content = getattr(msg, "content", "")
            preview = content if len(content) < 400 else content[:400] + "..."
            trace.append(
                {
                    "step": "tool_result",
                    "tool": getattr(msg, "name", None),
                    "output_preview": preview,
                }
            )
    return trace, tool_used


def run_agent(
    question: str, history: list[ChatMessage] | None = None
) -> ChatResponse:
    msgs = _to_lc_messages(history or [])
    msgs.append(HumanMessage(content=question))

    log.info("Invoking agent for: %s", question[:120])
    result = _agent().invoke({"messages": msgs})
    final_messages: list[BaseMessage] = result["messages"]
    final_answer = ""
    for msg in reversed(final_messages):
        if msg.__class__.__name__ == "AIMessage" and not getattr(msg, "tool_calls", None):
            final_answer = msg.content
            break

    trace, tool_used = _summarize_trace(final_messages)

    sources: list[SourceChunk] = []
    if tool_used in {"answer_question", "search_documents"}:
        try:
            sources = chat_service.retrieve(question)
        except Exception as e:  # noqa: BLE001
            log.warning("Could not attach sources: %s", e)

    return ChatResponse(
        answer=final_answer or "(no answer produced)",
        sources=sources,
        tool_used=tool_used,
        agent_trace=trace,
    )
