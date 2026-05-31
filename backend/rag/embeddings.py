"""Wrapper around a sentence-transformers model with lazy loading."""

from functools import lru_cache

from sentence_transformers import SentenceTransformer

from backend.utils.config import get_settings
from backend.utils.logging import get_logger

log = get_logger(__name__)


@lru_cache(maxsize=1)
def get_embedding_model() -> SentenceTransformer:
    name = get_settings().embedding_model
    log.info("Loading embedding model: %s", name)
    return SentenceTransformer(name)


def embed_texts(texts: list[str]) -> list[list[float]]:
    if not texts:
        return []
    model = get_embedding_model()
    vectors = model.encode(texts, show_progress_bar=False, convert_to_numpy=True)
    return [v.tolist() for v in vectors]


def embed_query(text: str) -> list[float]:
    return embed_texts([text])[0]
