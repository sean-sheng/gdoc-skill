"""Google API clients for Docs and Drive."""
from typing import Dict, Any
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials

from gdoc_fetch.models import Document, InlineObject


class DocsClient:
    """Client for Google Docs API."""

    def __init__(self, token: str):
        """
        Initialize Docs API client.

        Args:
            token: OAuth access token
        """
        credentials = Credentials(token=token)
        self.service = build('docs', 'v1', credentials=credentials)

    def fetch_document(self, doc_id: str) -> Document:
        """
        Fetch document from Google Docs API.

        Args:
            doc_id: Document ID

        Returns:
            Document model
        """
        # Fetch document with full content
        doc_data = self.service.documents().get(documentId=doc_id).execute()

        # Parse inline objects (images)
        inline_objects = self._parse_inline_objects(doc_data.get('inlineObjects', {}))

        return Document(
            doc_id=doc_data['documentId'],
            title=doc_data['title'],
            tabs=[],  # Will implement tab parsing later if needed
            inline_objects=inline_objects
        )

    def _parse_inline_objects(self, inline_objects_data: Dict[str, Any]) -> Dict[str, InlineObject]:
        """Parse inline objects from API response."""
        result = {}

        for object_id, obj_data in inline_objects_data.items():
            props = obj_data.get('inlineObjectProperties', {})
            embedded = props.get('embeddedObject', {})
            image_props = embedded.get('imageProperties', {})

            image_url = image_props.get('contentUri', '')

            if image_url:
                result[object_id] = InlineObject(
                    object_id=object_id,
                    image_url=image_url,
                    content_type='image/png'  # Default, could parse from URL
                )

        return result
