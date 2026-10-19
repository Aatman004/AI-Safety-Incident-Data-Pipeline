"""Unit tests for URL normalization and canonical ID deduplication."""

from incident_pipeline.processors.deduplicator import (
    generate_record_id,
    normalize_title,
    normalize_url,
)


def test_normalize_url_strips_tracking():
    url = "https://arxiv.org/abs/2307.15043?utm_source=twitter&utm_medium=social"
    normalized = normalize_url(url)
    assert normalized == "https://arxiv.org/abs/2307.15043"
    assert "utm_source" not in normalized


def test_normalize_url_canonicalizes_arxiv():
    pdf_url = "http://arxiv.org/pdf/2307.15043.pdf"
    abs_url = "https://arxiv.org/abs/2307.15043"
    assert normalize_url(pdf_url) == "https://arxiv.org/abs/2307.15043"
    assert normalize_url(abs_url) == "https://arxiv.org/abs/2307.15043"


def test_normalize_title_removes_punctuation():
    raw = "Universal & Transferable Adversarial Attacks: On Aligned Models!"
    expected = "universal transferable adversarial attacks on aligned models"
    assert normalize_title(raw) == expected


def test_generate_record_id_deterministic():
    url1 = "https://arxiv.org/abs/2307.15043?ref=safety"
    url2 = "http://arxiv.org/pdf/2307.15043.pdf"
    title = "Universal and Transferable Adversarial Attacks"

    id1 = generate_record_id(url1, title)
    id2 = generate_record_id(url2, title)

    assert id1 == id2
    assert len(id1) == 64  # SHA-256 hex string length
