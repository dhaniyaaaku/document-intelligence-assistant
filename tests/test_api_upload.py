"""Upload roundtrip test. Skipped if sentence-transformers cannot load offline."""

import pytest
from fastapi.testclient import TestClient

from backend.main import app


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c


def test_upload_txt_roundtrip(client):
    try:
        from backend.rag import embeddings

        embeddings.get_embedding_model()
    except Exception as e:  # noqa: BLE001
        pytest.skip(f"Embedding model unavailable in this environment: {e}")

    r = client.post(
        "/documents/upload",
        files={"file": ("note.txt", b"FastAPI is a Python web framework.", "text/plain")},
    )
    assert r.status_code == 200
    body = r.json()
    assert body["document"]["filename"] == "note.txt"
    assert body["document"]["chunk_count"] >= 1
    doc_id = body["document"]["id"]

    r = client.get("/documents")
    assert any(d["id"] == doc_id for d in r.json()["documents"])

    r = client.delete(f"/documents/{doc_id}")
    assert r.status_code == 204
