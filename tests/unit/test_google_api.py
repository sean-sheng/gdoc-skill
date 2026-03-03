"""Tests for Google API client."""
from unittest.mock import MagicMock, Mock
import pytest
from gdoc_fetch.google_api import DocsClient
from gdoc_fetch.models import Document


def test_docs_client_fetch_document(mocker):
    """Test fetching a document from Google Docs API."""
    mock_service = MagicMock()
    mock_docs = mock_service.documents.return_value
    mock_get = mock_docs.get.return_value
    mock_get.execute.return_value = {
        'documentId': '123abc',
        'title': 'Test Document',
        'body': {
            'content': [
                {
                    'paragraph': {
                        'elements': [
                            {'textRun': {'content': 'Test content\n'}}
                        ]
                    }
                }
            ]
        },
        'inlineObjects': {}
    }

    client = DocsClient(token="test-token")
    client.service = mock_service

    doc = client.fetch_document("123abc")

    assert doc.doc_id == "123abc"
    assert doc.title == "Test Document"
    mock_docs.get.assert_called_once_with(documentId="123abc")


def test_docs_client_parse_inline_objects(mocker):
    """Test parsing inline objects from API response."""
    mock_service = MagicMock()
    mock_docs = mock_service.documents.return_value
    mock_get = mock_docs.get.return_value
    mock_get.execute.return_value = {
        'documentId': '123',
        'title': 'Test',
        'body': {'content': []},
        'inlineObjects': {
            'kix.abc123': {
                'inlineObjectProperties': {
                    'embeddedObject': {
                        'imageProperties': {
                            'contentUri': 'https://lh3.googleusercontent.com/image.png'
                        }
                    }
                }
            }
        }
    }

    client = DocsClient(token="test-token")
    client.service = mock_service

    doc = client.fetch_document("123")

    assert len(doc.inline_objects) == 1
    assert 'kix.abc123' in doc.inline_objects
    assert 'googleusercontent' in doc.inline_objects['kix.abc123'].image_url
