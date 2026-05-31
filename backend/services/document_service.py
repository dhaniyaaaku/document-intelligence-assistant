"""Upload, extract, chunk, embed, and persist documents."""

import uuid
from datetime import datetime
from pathlib import Path

from backend.database import models as db_models
from backend.database.db import get_session
from backend.models.schemas import DocumentMetadata
from backend.rag import chunker, embeddings, extractor, vector_store
from backend.utils.config import get_settings
from backend.utils.logging import get_logger

log = get_logger(__name__)


def _to_schema(row: db_models.Document) -> DocumentMetadata:
    return DocumentMetadata(
        id=row.id,
        filename=row.filename,
        content_type=row.content_type,
        size_bytes=row.size_bytes,
        chunk_count=row.chunk_count,
        uploaded_at=row.uploaded_at,
    )


def save_and_index(
    filename: str, content_type: str, raw_bytes: bytes
) -> DocumentMetadata:
    settings = get_settings()
    ext = Path(filename).suffix.lower()
    if ext not in extractor.SUPPORTED_EXTENSIONS:
        raise extractor.UnsupportedFileTypeError(
            f"Unsupported file type: {ext}. Allowed: {sorted(extractor.SUPPORTED_EXTENSIONS)}"
        )

    doc_id = uuid.uuid4().hex
    stored_path = settings.upload_dir / f"{doc_id}{ext}"
    stored_path.write_bytes(raw_bytes)
    log.info("Stored upload %s -> %s (%d bytes)", filename, stored_path, len(raw_bytes))

    text = extractor.extract_text(stored_path)
    chunks = chunker.chunk_text(text, settings.chunk_size, settings.chunk_overlap)
    log.info("Extracted %d chars, %d chunks", len(text), len(chunks))

    if chunks:
        vectors = embeddings.embed_texts(chunks)
        vector_store.add_chunks(doc_id, filename, chunks, vectors)

    row = db_models.Document(
        id=doc_id,
        filename=filename,
        content_type=content_type or "application/octet-stream",
        size_bytes=len(raw_bytes),
        chunk_count=len(chunks),
        stored_path=str(stored_path),
        uploaded_at=datetime.utcnow(),
    )
    with get_session() as session:
        session.add(row)
        session.commit()
        session.refresh(row)
        return _to_schema(row)


def list_documents() -> list[DocumentMetadata]:
    with get_session() as session:
        rows = (
            session.query(db_models.Document)
            .order_by(db_models.Document.uploaded_at.desc())
            .all()
        )
        return [_to_schema(r) for r in rows]


def get_document(document_id: str) -> DocumentMetadata | None:
    with get_session() as session:
        row = session.get(db_models.Document, document_id)
        return _to_schema(row) if row else None


def delete_document(document_id: str) -> bool:
    with get_session() as session:
        row = session.get(db_models.Document, document_id)
        if not row:
            return False
        try:
            Path(row.stored_path).unlink(missing_ok=True)
        except OSError as e:
            log.warning("Failed to remove file %s: %s", row.stored_path, e)
        vector_store.delete_document(document_id)
        session.delete(row)
        session.commit()
        return True


def get_full_text(document_id: str) -> str:
    """Reassemble the full document text from stored chunks."""
    return "\n\n".join(vector_store.fetch_document_chunks(document_id))
