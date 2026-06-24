from app.text import chunk_text


def test_chunk_text_returns_short_text_as_single_chunk():
    chunks = chunk_text("hello world")

    assert chunks == ["hello world"]


def test_chunk_text_splits_long_text():
    text = "a" * 1000

    chunks = chunk_text(text, chunk_size=400, overlap=100)

    assert len(chunks) > 1
    assert chunks[0] == "a" * 400
    assert chunks[1] == "a" * 400


def test_chunk_text_ignores_empty_chunks():
    chunks = chunk_text("   ")

    assert chunks == []