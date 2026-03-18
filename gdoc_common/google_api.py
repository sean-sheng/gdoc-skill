"""Google API clients for Docs and Drive."""
import requests
from datetime import datetime
from dataclasses import dataclass
from typing import Dict, Any, List, Optional
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.oauth2.credentials import Credentials

from gdoc_common.models import Document, InlineObject


@dataclass
class Revision:
    """Represents a Google Doc revision."""
    revision_id: str
    modified_time: datetime
    modified_by: str  # display name or email


class DriveRevisionClient:
    """Client for Google Drive revisions API."""

    def __init__(self, token: str):
        self._token = token
        credentials = Credentials(token=token)
        self.service = build('drive', 'v3', credentials=credentials)

    def list_revisions(self, doc_id: str) -> List[Revision]:
        """List all revisions for a document, newest first."""
        revisions = []
        page_token = None

        while True:
            kwargs = {
                'fileId': doc_id,
                'fields': 'nextPageToken,revisions(id,modifiedTime,lastModifyingUser)',
                'pageSize': 200,
            }
            if page_token:
                kwargs['pageToken'] = page_token

            result = self.service.revisions().list(**kwargs).execute()

            for rev in result.get('revisions', []):
                user = rev.get('lastModifyingUser', {})
                modified_by = user.get('displayName') or user.get('emailAddress', 'Unknown')
                modified_time = datetime.fromisoformat(
                    rev['modifiedTime'].replace('Z', '+00:00')
                )
                revisions.append(Revision(
                    revision_id=rev['id'],
                    modified_time=modified_time,
                    modified_by=modified_by,
                ))

            page_token = result.get('nextPageToken')
            if not page_token:
                break

        # Newest first
        revisions.sort(key=lambda r: r.modified_time, reverse=True)
        return revisions

    def get_revision_text(self, doc_id: str, revision_id: str) -> str:
        """Export a specific revision as plain text."""
        import time

        rev = self.service.revisions().get(
            fileId=doc_id,
            revisionId=revision_id,
            fields='exportLinks',
        ).execute()

        export_url = rev.get('exportLinks', {}).get('text/plain')
        if not export_url:
            raise ValueError(f"No plain text export available for revision {revision_id}")

        for attempt in range(5):
            response = requests.get(
                export_url,
                headers={'Authorization': f'Bearer {self._token}'},
                timeout=30,
            )
            if response.status_code == 429:
                wait = 3 * (2 ** attempt)  # 3s, 6s, 12s, 24s, 48s
                time.sleep(wait)
                continue
            response.raise_for_status()
            return response.text

        response.raise_for_status()
        return response.text


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

    def create_document(self, title: str) -> str:
        """
        Create a new Google Doc.

        Args:
            title: Document title

        Returns:
            Document ID of created document

        Raises:
            ValueError: If API request fails with permission error
            HttpError: For other API errors
        """
        try:
            body = {'title': title}
            doc = self.service.documents().create(body=body).execute()
            return doc['documentId']

        except HttpError as e:
            if e.resp.status == 403:
                raise ValueError("Permission denied. Check authentication and API access.")
            elif e.resp.status == 404:
                raise ValueError("Docs API not found. Ensure API is enabled.")
            else:
                raise

    def update_document_content(self, doc_id: str, requests: List[Dict]) -> None:
        """
        Apply batch updates to document content.

        Args:
            doc_id: Document ID
            requests: List of batchUpdate request dicts

        Raises:
            ValueError: If API request fails
            HttpError: For API errors
        """
        if not requests:
            return

        try:
            self.service.documents().batchUpdate(
                documentId=doc_id,
                body={'requests': requests}
            ).execute()

        except HttpError as e:
            if e.resp.status == 403:
                raise ValueError("Permission denied. Cannot update document.")
            elif e.resp.status == 404:
                raise ValueError(f"Document not found: {doc_id}")
            else:
                raise

    def get_document_url(self, doc_id: str) -> str:
        """
        Get Google Docs edit URL from document ID.

        Args:
            doc_id: Document ID

        Returns:
            Full edit URL for the document
        """
        return f"https://docs.google.com/document/d/{doc_id}/edit"
