from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class DocumentMetadata(BaseModel):
    id: str
    filename: str
    content_type: str
    size_bytes: int
    chunk_count: int
    uploaded_at: datetime


class UploadResponse(BaseModel):
    document: DocumentMetadata
    message: str = "Document indexed successfully"


class DocumentListResponse(BaseModel):
    documents: list[DocumentMetadata]


class ChatMessage(BaseModel):
    role: str
    content: str


class SourceChunk(BaseModel):
    document_id: str
    filename: str
    chunk_index: int
    text: str
    score: float | None = None


class ChatRequest(BaseModel):
    question: str
    document_ids: list[str] | None = None
    history: list[ChatMessage] = Field(default_factory=list)


class ChatResponse(BaseModel):
    answer: str
    sources: list[SourceChunk] = Field(default_factory=list)
    tool_used: str | None = None
    agent_trace: list[dict[str, Any]] = Field(default_factory=list)


class SummarizeRequest(BaseModel):
    document_id: str


class SummarizeResponse(BaseModel):
    document_id: str
    summary: str


class TopicsRequest(BaseModel):
    document_id: str
    n_topics: int = 5


class TopicsResponse(BaseModel):
    document_id: str
    topics: list[str]


class CompareRequest(BaseModel):
    document_id_a: str
    document_id_b: str


class CompareResponse(BaseModel):
    document_id_a: str
    document_id_b: str
    comparison: str


class ActionItemsRequest(BaseModel):
    document_id: str


class ActionItemsResponse(BaseModel):
    document_id: str
    action_items: list[str]
