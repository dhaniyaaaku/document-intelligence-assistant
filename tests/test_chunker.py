from backend.rag.chunker import chunk_text


def test_chunk_text_basic():
    text = "Sentence one. " * 200
    chunks = chunk_text(text, chunk_size=200, chunk_overlap=20)
    assert len(chunks) > 1
    assert all(len(c) <= 220 for c in chunks)


def test_chunk_empty_returns_empty():
    assert chunk_text("   ", chunk_size=100, chunk_overlap=10) == []
