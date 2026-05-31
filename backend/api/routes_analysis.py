from fastapi import APIRouter, HTTPException

from backend.models.schemas import (
    ActionItemsRequest,
    ActionItemsResponse,
    CompareRequest,
    CompareResponse,
    SummarizeRequest,
    SummarizeResponse,
    TopicsRequest,
    TopicsResponse,
)
from backend.services import analysis_service
from backend.services.llm_client import LLMNotConfiguredError, LLMQuotaExceededError

router = APIRouter(prefix="/analysis", tags=["analysis"])


def _wrap(fn, *args, **kwargs):
    try:
        return fn(*args, **kwargs)
    except analysis_service.DocumentNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
    except LLMNotConfiguredError as e:
        raise HTTPException(status_code=503, detail=str(e)) from e
    except LLMQuotaExceededError as e:
        raise HTTPException(status_code=429, detail=str(e)) from e


@router.post("/summarize", response_model=SummarizeResponse)
def summarize(req: SummarizeRequest) -> SummarizeResponse:
    summary = _wrap(analysis_service.summarize, req.document_id)
    return SummarizeResponse(document_id=req.document_id, summary=summary)


@router.post("/topics", response_model=TopicsResponse)
def topics(req: TopicsRequest) -> TopicsResponse:
    topics = _wrap(analysis_service.extract_topics, req.document_id, req.n_topics)
    return TopicsResponse(document_id=req.document_id, topics=topics)


@router.post("/compare", response_model=CompareResponse)
def compare(req: CompareRequest) -> CompareResponse:
    text = _wrap(analysis_service.compare_documents, req.document_id_a, req.document_id_b)
    return CompareResponse(
        document_id_a=req.document_id_a,
        document_id_b=req.document_id_b,
        comparison=text,
    )


@router.post("/action-items", response_model=ActionItemsResponse)
def action_items(req: ActionItemsRequest) -> ActionItemsResponse:
    items = _wrap(analysis_service.extract_action_items, req.document_id)
    return ActionItemsResponse(document_id=req.document_id, action_items=items)
