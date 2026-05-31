"""ChromaDB persistent vector store wrapper."""

from functools import lru_cache

import chromadb
from chromadb.config import Settings as ChromaSettings

from backend.utils.config import get_settings
from backend.utils.logging import get_logger

log = get_logger(__name__)
COLLECTION_NAME = "documents"


@lru_cache(maxsize=1)
def _client() -> chromadb.ClientAPI:
    settings = get_settings()
    log.info("Opening Chroma at %s", settings.chroma_dir)
    return chromadb.PersistentClient(
        path=str(settings.chroma_dir),
        settings=ChromaSettings(anonymized_telemetry=False, allow_reset=True),
    )


def _collection():
    return _client().get_or_create_collection(
        name=COLLECTION_NAME, metadata={"hnsw:space": "cosine"}
    )


def add_chunks(
    document_id: str,
    filename: str,
    chunks: list[str],
    embeddings: list[list[float]],
) -> None:
    if not chunks:
        return
    ids = [f"{document_id}::{i}" for i in range(len(chunks))]
    metadatas = [
        {"document_id": document_id, "filename": filename, "chunk_index": i}
        for i in range(len(chunks))
    ]
    _collection().add(
        ids=ids, documents=chunks, metadatas=metadatas, embeddings=embeddings
    )


def delete_document(document_id: str) -> None:
    _collection().delete(where={"document_id": document_id})


def query(
    embedding: list[float],
    top_k: int,
    document_ids: list[str] | None = None,
) -> list[dict]:
    where = None
    if document_ids:
        where = (
            {"document_id": document_ids[0]}
            if len(document_ids) == 1
            else {"document_id": {"$in": document_ids}}
        )
    result = _collection().query(
        query_embeddings=[embedding],
        n_results=top_k,
        where=where,
        include=["documents", "metadatas", "distances"],
    )
    hits = []
    docs = result.get("documents", [[]])[0]
    metas = result.get("metadatas", [[]])[0]
    dists = result.get("distances", [[]])[0]
    for text, meta, dist in zip(docs, metas, dists):
        hits.append(
            {
                "document_id": meta["document_id"],
                "filename": meta["filename"],
                "chunk_index": meta["chunk_index"],
                "text": text,
                "score": 1.0 - float(dist),  # cosine distance -> similarity
            }
        )
    return hits


def fetch_document_chunks(document_id: str) -> list[str]:
    result = _collection().get(
        where={"document_id": document_id}, include=["documents", "metadatas"]
    )
    pairs = list(zip(result.get("metadatas", []), result.get("documents", [])))
    pairs.sort(key=lambda p: p[0]["chunk_index"])
    return [text for _, text in pairs]
