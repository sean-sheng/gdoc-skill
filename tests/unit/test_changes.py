"""Unit tests for gdoc_fetch.changes and DriveRevisionClient."""
from datetime import datetime, timezone
from unittest.mock import MagicMock, Mock, patch

import pytest

from gdoc_common.google_api import DriveRevisionClient, Revision
from gdoc_fetch.changes import diff_texts, format_revision_list, get_changes


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_revision(rev_id: str, iso_time: str, display_name: str) -> dict:
    """Build a raw Drive API revision dict."""
    return {
        'id': rev_id,
        'modifiedTime': iso_time,
        'lastModifyingUser': {'displayName': display_name},
    }


def _rev(rev_id: str, iso_time: str, name: str) -> Revision:
    dt = datetime.fromisoformat(iso_time.replace('Z', '+00:00'))
    return Revision(revision_id=rev_id, modified_time=dt, modified_by=name)


# ---------------------------------------------------------------------------
# DriveRevisionClient.list_revisions
# ---------------------------------------------------------------------------

class TestDriveRevisionClientListRevisions:

    def _make_client_with_service(self, mock_service) -> DriveRevisionClient:
        client = DriveRevisionClient(token='test-token')
        client.service = mock_service
        return client

    def test_returns_revisions_sorted_newest_first(self):
        mock_service = MagicMock()
        mock_revisions = mock_service.revisions.return_value
        mock_list = mock_revisions.list.return_value
        mock_list.execute.return_value = {
            'revisions': [
                _make_revision('r1', '2026-03-01T10:00:00Z', 'Alice'),
                _make_revision('r2', '2026-03-09T15:00:00Z', 'Bob'),
                _make_revision('r3', '2026-03-05T08:00:00Z', 'Carol'),
            ]
        }

        client = self._make_client_with_service(mock_service)
        revs = client.list_revisions('doc123')

        assert len(revs) == 3
        # Newest first
        assert revs[0].revision_id == 'r2'
        assert revs[1].revision_id == 'r3'
        assert revs[2].revision_id == 'r1'

    def test_parses_display_name(self):
        mock_service = MagicMock()
        mock_service.revisions().list().execute.return_value = {
            'revisions': [_make_revision('r1', '2026-03-09T12:00:00Z', 'Alice Smith')]
        }

        client = self._make_client_with_service(mock_service)
        revs = client.list_revisions('doc123')

        assert revs[0].modified_by == 'Alice Smith'

    def test_falls_back_to_email_when_no_display_name(self):
        mock_service = MagicMock()
        mock_service.revisions().list().execute.return_value = {
            'revisions': [{
                'id': 'r1',
                'modifiedTime': '2026-03-09T12:00:00Z',
                'lastModifyingUser': {'emailAddress': 'alice@example.com'},
            }]
        }

        client = self._make_client_with_service(mock_service)
        revs = client.list_revisions('doc123')

        assert revs[0].modified_by == 'alice@example.com'

    def test_unknown_user_when_no_user_info(self):
        mock_service = MagicMock()
        mock_service.revisions().list().execute.return_value = {
            'revisions': [{
                'id': 'r1',
                'modifiedTime': '2026-03-09T12:00:00Z',
                'lastModifyingUser': {},
            }]
        }

        client = self._make_client_with_service(mock_service)
        revs = client.list_revisions('doc123')

        assert revs[0].modified_by == 'Unknown'

    def test_handles_pagination(self):
        mock_service = MagicMock()
        mock_revisions = mock_service.revisions.return_value
        mock_list = mock_revisions.list.return_value

        # Two pages
        mock_list.execute.side_effect = [
            {
                'revisions': [_make_revision('r1', '2026-03-01T10:00:00Z', 'Alice')],
                'nextPageToken': 'token-page2',
            },
            {
                'revisions': [_make_revision('r2', '2026-03-09T10:00:00Z', 'Bob')],
            },
        ]

        client = self._make_client_with_service(mock_service)
        revs = client.list_revisions('doc123')

        assert len(revs) == 2
        assert mock_list.execute.call_count == 2

    def test_returns_empty_list_when_no_revisions(self):
        mock_service = MagicMock()
        mock_service.revisions().list().execute.return_value = {'revisions': []}

        client = self._make_client_with_service(mock_service)
        revs = client.list_revisions('doc123')

        assert revs == []

    def test_parses_modified_time_correctly(self):
        mock_service = MagicMock()
        mock_service.revisions().list().execute.return_value = {
            'revisions': [_make_revision('r1', '2026-03-09T14:30:00Z', 'Alice')]
        }

        client = self._make_client_with_service(mock_service)
        revs = client.list_revisions('doc123')

        expected = datetime(2026, 3, 9, 14, 30, 0, tzinfo=timezone.utc)
        assert revs[0].modified_time == expected


# ---------------------------------------------------------------------------
# DriveRevisionClient.get_revision_text
# ---------------------------------------------------------------------------

class TestDriveRevisionClientGetRevisionText:

    def _make_client_with_service(self, mock_service) -> DriveRevisionClient:
        client = DriveRevisionClient(token='test-token')
        client.service = mock_service
        return client

    def test_fetches_and_returns_plain_text(self):
        mock_service = MagicMock()
        export_url = 'https://docs.google.com/export?format=txt&id=doc123&rev=r1'
        mock_service.revisions().get().execute.return_value = {
            'exportLinks': {'text/plain': export_url}
        }

        mock_response = Mock()
        mock_response.text = 'Hello, world!'
        mock_response.raise_for_status = Mock()

        with patch('gdoc_common.google_api.requests.get', return_value=mock_response) as mock_get:
            client = self._make_client_with_service(mock_service)
            text = client.get_revision_text('doc123', 'r1')

        assert text == 'Hello, world!'
        mock_get.assert_called_once_with(
            export_url,
            headers={'Authorization': 'Bearer test-token'},
            timeout=30,
        )

    def test_raises_when_no_export_link(self):
        mock_service = MagicMock()
        mock_service.revisions().get().execute.return_value = {
            'exportLinks': {}
        }

        client = self._make_client_with_service(mock_service)

        with pytest.raises(ValueError, match="No plain text export available"):
            client.get_revision_text('doc123', 'r1')

    def test_raises_on_http_error(self):
        mock_service = MagicMock()
        export_url = 'https://docs.google.com/export?format=txt'
        mock_service.revisions().get().execute.return_value = {
            'exportLinks': {'text/plain': export_url}
        }

        mock_response = Mock()
        mock_response.raise_for_status.side_effect = Exception("403 Forbidden")

        with patch('gdoc_common.google_api.requests.get', return_value=mock_response):
            client = self._make_client_with_service(mock_service)

            with pytest.raises(Exception, match="403 Forbidden"):
                client.get_revision_text('doc123', 'r1')


# ---------------------------------------------------------------------------
# diff_texts
# ---------------------------------------------------------------------------

class TestDiffTexts:

    def test_detects_added_lines(self):
        old = "line one\n"
        new = "line one\nnew line\n"
        diff = diff_texts(old, new, "old", "new")

        assert "+new line" in diff

    def test_detects_removed_lines(self):
        old = "line one\nold line\n"
        new = "line one\n"
        diff = diff_texts(old, new, "old", "new")

        assert "-old line" in diff

    def test_detects_modified_lines(self):
        old = "The quick brown fox\n"
        new = "The quick red fox\n"
        diff = diff_texts(old, new, "old", "new")

        assert "-The quick brown fox" in diff
        assert "+The quick red fox" in diff

    def test_no_changes_returns_message(self):
        text = "identical content\n"
        result = diff_texts(text, text, "old", "new")

        assert result == "(no text changes detected)"

    def test_includes_labels_in_output(self):
        diff = diff_texts("a\n", "b\n", "from-label", "to-label")

        assert "from-label" in diff
        assert "to-label" in diff

    def test_empty_to_non_empty(self):
        diff = diff_texts("", "hello\n", "empty", "filled")

        assert "+hello" in diff

    def test_non_empty_to_empty(self):
        diff = diff_texts("hello\n", "", "filled", "empty")

        assert "-hello" in diff


# ---------------------------------------------------------------------------
# format_revision_list
# ---------------------------------------------------------------------------

class TestFormatRevisionList:

    def test_marks_first_as_latest(self):
        revs = [
            _rev('r2', '2026-03-09T12:00:00Z', 'Bob'),
            _rev('r1', '2026-03-01T10:00:00Z', 'Alice'),
        ]
        output = format_revision_list(revs)

        first_line, second_line = output.split('\n')
        assert '(latest)' in first_line
        assert '(latest)' not in second_line

    def test_includes_author_names(self):
        revs = [
            _rev('r1', '2026-03-09T12:00:00Z', 'Alice Smith'),
        ]
        output = format_revision_list(revs)

        assert 'Alice Smith' in output

    def test_includes_revision_ids(self):
        revs = [
            _rev('revision-abc', '2026-03-09T12:00:00Z', 'Alice'),
        ]
        output = format_revision_list(revs)

        assert 'revision-abc' in output

    def test_numbers_revisions_from_one(self):
        revs = [
            _rev('r3', '2026-03-09T12:00:00Z', 'Alice'),
            _rev('r2', '2026-03-05T12:00:00Z', 'Bob'),
            _rev('r1', '2026-03-01T12:00:00Z', 'Carol'),
        ]
        output = format_revision_list(revs)

        lines = output.strip().split('\n')
        assert '[1]' in lines[0]
        assert '[2]' in lines[1]
        assert '[3]' in lines[2]

    def test_single_revision(self):
        revs = [_rev('r1', '2026-03-09T12:00:00Z', 'Alice')]
        output = format_revision_list(revs)

        assert '[1]' in output
        assert '(latest)' in output


# ---------------------------------------------------------------------------
# get_changes
# ---------------------------------------------------------------------------

class TestGetChanges:

    def _make_client(self, revisions, texts: dict):
        """Build a mocked DriveRevisionClient."""
        client = MagicMock(spec=DriveRevisionClient)
        client.list_revisions.return_value = revisions
        client.get_revision_text.side_effect = lambda doc_id, rev_id: texts[rev_id]
        return client

    def test_returns_revisions_and_diff(self):
        revs = [
            _rev('r2', '2026-03-09T12:00:00Z', 'Bob'),
            _rev('r1', '2026-03-01T10:00:00Z', 'Alice'),
        ]
        texts = {'r2': 'new content\n', 'r1': 'old content\n'}

        with patch('gdoc_fetch.changes.DriveRevisionClient', return_value=self._make_client(revs, texts)):
            returned_revs, diff = get_changes('doc123', 'token', last=1)

        assert returned_revs is revs
        assert '-old content' in diff
        assert '+new content' in diff

    def test_spans_multiple_revisions_with_last(self):
        revs = [
            _rev('r3', '2026-03-09T12:00:00Z', 'Carol'),
            _rev('r2', '2026-03-05T10:00:00Z', 'Bob'),
            _rev('r1', '2026-03-01T10:00:00Z', 'Alice'),
        ]
        texts = {
            'r3': 'version 3\n',
            'r1': 'version 1\n',
        }

        client = self._make_client(revs, texts)
        with patch('gdoc_fetch.changes.DriveRevisionClient', return_value=client):
            _, diff = get_changes('doc123', 'token', last=2)

        # Should compare r1 (index 2) → r3 (index 0)
        client.get_revision_text.assert_any_call('doc123', 'r3')
        client.get_revision_text.assert_any_call('doc123', 'r1')
        assert '-version 1' in diff
        assert '+version 3' in diff

    def test_only_one_revision_returns_message(self):
        revs = [_rev('r1', '2026-03-01T10:00:00Z', 'Alice')]

        client = self._make_client(revs, {})
        with patch('gdoc_fetch.changes.DriveRevisionClient', return_value=client):
            _, diff = get_changes('doc123', 'token', last=1)

        assert 'only one revision' in diff

    def test_clamps_last_to_available_revisions(self):
        revs = [
            _rev('r2', '2026-03-09T12:00:00Z', 'Bob'),
            _rev('r1', '2026-03-01T10:00:00Z', 'Alice'),
        ]
        texts = {'r2': 'new\n', 'r1': 'old\n'}

        client = self._make_client(revs, texts)
        # Asking for last=10 but only 2 revisions exist
        with patch('gdoc_fetch.changes.DriveRevisionClient', return_value=client):
            returned_revs, diff = get_changes('doc123', 'token', last=10)

        assert len(returned_revs) == 2
        assert diff != "(no text changes detected)"

    def test_no_change_between_revisions(self):
        revs = [
            _rev('r2', '2026-03-09T12:00:00Z', 'Bob'),
            _rev('r1', '2026-03-01T10:00:00Z', 'Alice'),
        ]
        same = 'identical content\n'
        texts = {'r2': same, 'r1': same}

        client = self._make_client(revs, texts)
        with patch('gdoc_fetch.changes.DriveRevisionClient', return_value=client):
            _, diff = get_changes('doc123', 'token', last=1)

        assert diff == "(no text changes detected)"
