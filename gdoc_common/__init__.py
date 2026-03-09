"""Common utilities shared by gdoc-fetch and gdoc-upload."""
from gdoc_common.auth import get_access_token, AuthenticationError
from gdoc_common.google_api import DocsClient
from gdoc_common.models import (
    Document,
    InlineObject,
    Heading,
    Paragraph,
    ListItem,
    CodeBlock,
    Image,
    TextRun,
    MarkdownDocument,
)
from gdoc_common.utils import extract_doc_id

__all__ = [
    # Authentication
    'get_access_token',
    'AuthenticationError',
    # Google API
    'DocsClient',
    # Models
    'Document',
    'InlineObject',
    'Heading',
    'Paragraph',
    'ListItem',
    'CodeBlock',
    'Image',
    'TextRun',
    'MarkdownDocument',
    # Utils
    'extract_doc_id',
]
