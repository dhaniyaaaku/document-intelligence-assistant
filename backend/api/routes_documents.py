from fastapi import APIRouter, File, HTTPException, UploadFile, status

from backend.models.schemas import (
    DocumentListResponse,
    UploadResponse,
)
from backend.rag.extractor import UnsupportedFileTypeError
from backend.services import document_service
from backend.utils.logging import get_logger

router = APIRouter(prefix="/documents", tags=["documents"])
log = get_logger(__name__)


@router.post("/upload", response_model=UploadResponse)
async def upload_document(file: UploadFile = File(...)) -> UploadResponse:
    contents = await file.read()
    if not contents:
        raise HTTPException(status_code=400, detail="Empty upload")
    try:
        meta = document_service.save_and_index(
            filename=file.filename or "unnamed",
            content_type=file.content_type or "application/octet-stream",
            raw_bytes=contents,
        )
    except UnsupportedFileTypeError as e:
        raise HTTPException(status_code=415, detail=str(e)) from e
    return UploadResponse(document=meta)


@router.get("", response_model=DocumentListResponse)
def list_documents() -> DocumentListResponse:
    return DocumentListResponse(documents=document_service.list_documents())


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_document(document_id: str) -> None:
    if not document_service.delete_document(document_id):
        raise HTTPException(status_code=404, detail="Document not found")
