"""Tests for utility functions."""
import pytest
from gdoc_fetch.utils import extract_doc_id


def test_extract_doc_id_from_url():
    """Test extracting document ID from full URL."""
    url = "https://docs.google.com/document/d/1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgVE2upms/edit"
    assert extract_doc_id(url) == "1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgVE2upms"


def test_extract_doc_id_from_url_with_query():
    """Test extracting ID from URL with query parameters."""
    url = "https://docs.google.com/document/d/1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgVE2upms/edit?usp=sharing"
    assert extract_doc_id(url) == "1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgVE2upms"


def test_extract_doc_id_from_plain_id():
    """Test that plain ID passes through."""
    doc_id = "1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgVE2upms"
    assert extract_doc_id(doc_id) == doc_id


def test_extract_doc_id_invalid_url():
    """Test error on invalid URL."""
    with pytest.raises(ValueError) as exc:
        extract_doc_id("https://example.com/notadoc")

    assert "Could not extract" in str(exc.value)


def test_extract_doc_id_empty():
    """Test error on empty input."""
    with pytest.raises(ValueError):
        extract_doc_id("")
