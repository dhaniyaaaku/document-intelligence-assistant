from fastapi import APIRouter, HTTPException

from backend.agents.graph import run_agent
from backend.models.schemas import ChatRequest, ChatResponse
from backend.services import chat_service
from backend.services.llm_client import LLMNotConfiguredError

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("", response_model=ChatResponse)
def chat(req: ChatRequest) -> ChatResponse:
    try:
        return chat_service.answer_question(
            req.question, document_ids=req.document_ids, history=req.history
        )
    except LLMNotConfiguredError as e:
        raise HTTPException(status_code=503, detail=str(e)) from e


@router.post("/agent", response_model=ChatResponse)
def chat_agent(req: ChatRequest) -> ChatResponse:
    try:
        return run_agent(req.question, history=req.history)
    except LLMNotConfiguredError as e:
        raise HTTPException(status_code=503, detail=str(e)) from e
