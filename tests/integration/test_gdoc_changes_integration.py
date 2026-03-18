"""Integration tests for gdoc-changes: current version vs previous version."""
import subprocess
import time
from pathlib import Path
from typing import List, Tuple

import pytest

from gdoc_common.auth import get_access_token, AuthenticationError
from gdoc_common.google_api import DocsClient, DriveRevisionClient


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def auth_token() -> str:
    try:
        return get_access_token()
    except AuthenticationError:
        pytest.skip("Authentication not available. Run: gcloud auth login --enable-gdrive-access")


@pytest.fixture(scope="module")
def docs_client(auth_token: str) -> DocsClient:
    return DocsClient(token=auth_token)


@pytest.fixture(scope="module")
def revision_client(auth_token: str) -> DriveRevisionClient:
    return DriveRevisionClient(token=auth_token)


@pytest.fixture(scope="module")
def two_revision_doc(auth_token: str, docs_client: DocsClient) -> str:
    """
    Create a Google Doc with two distinct content revisions and return its ID.

    Strategy: insert original text, wait for Drive to register the revision,
    then append an UPDATED line. Tests use list_revisions() at runtime to get
    the current accessible revision IDs (Drive may consolidate revisions).

    Invariant guaranteed:
      - revisions[0] (latest): contains "UPDATED" text
      - revisions[1] (previous accessible): does NOT contain "UPDATED"
    """
    # --- Create document and insert v1 content ---
    doc_id = docs_client.create_document("gdoc-changes Integration Test")

    v1_text = (
        "Introduction\n"
        "This is the original version of the document.\n"
        "It contains baseline content for change detection.\n"
    )
    docs_client.update_document_content(doc_id, [
        {'insertText': {'location': {'index': 1}, 'text': v1_text}}
    ])

    # Wait long enough for Drive to register a distinct revision
    time.sleep(5)

    # --- Append v2 content (UPDATED line) ---
    doc_data = docs_client.service.documents().get(documentId=doc_id).execute()
    end_index = 1
    for element in doc_data.get('body', {}).get('content', []):
        if 'endIndex' in element:
            end_index = element['endIndex']

    insert_index = max(end_index - 1, 1)
    v2_addition = "UPDATED: This line was added in the second revision.\n"
    docs_client.update_document_content(doc_id, [
        {'insertText': {'location': {'index': insert_index}, 'text': v2_addition}}
    ])

    # Allow Drive to register the second revision
    time.sleep(3)

    yield doc_id

    print(f"\n[cleanup] Test doc left in Drive: "
          f"https://docs.google.com/document/d/{doc_id}/edit")


# ---------------------------------------------------------------------------
# Tests: DriveRevisionClient (against real API)
# ---------------------------------------------------------------------------

@pytest.mark.integration
class TestDriveRevisionClientIntegration:

    def test_list_revisions_returns_at_least_two(
        self, revision_client: DriveRevisionClient, two_revision_doc: str
    ):
        """The test doc should have at least 2 revisions."""
        revs = revision_client.list_revisions(two_revision_doc)

        assert len(revs) >= 2, (
            f"Expected ≥2 revisions, got {len(revs)}. "
            "The second revision may not have been saved yet."
        )

    def test_latest_revision_is_first(
        self, revision_client: DriveRevisionClient, two_revision_doc: str
    ):
        """Revisions should be sorted newest-first."""
        revs = revision_client.list_revisions(two_revision_doc)

        for i in range(len(revs) - 1):
            assert revs[i].modified_time >= revs[i + 1].modified_time, (
                "Revisions are not sorted newest-first"
            )

    def test_revision_has_required_fields(
        self, revision_client: DriveRevisionClient, two_revision_doc: str
    ):
        """Each revision should have id, modified_time, and modified_by."""
        revs = revision_client.list_revisions(two_revision_doc)

        for rev in revs:
            assert rev.revision_id, "revision_id should not be empty"
            assert rev.modified_time is not None
            assert rev.modified_by, "modified_by should not be empty"

    def test_get_revision_text_returns_string(
        self, revision_client: DriveRevisionClient, two_revision_doc: str
    ):
        """Exporting the latest revision should return non-empty text."""
        revs = revision_client.list_revisions(two_revision_doc)
        text = revision_client.get_revision_text(two_revision_doc, revs[0].revision_id)

        assert isinstance(text, str)
        assert len(text) > 0

    def test_current_revision_contains_updated_text(
        self, revision_client: DriveRevisionClient, two_revision_doc: str
    ):
        """The latest revision should contain the UPDATED line."""
        revs = revision_client.list_revisions(two_revision_doc)
        current_text = revision_client.get_revision_text(two_revision_doc, revs[0].revision_id)

        assert "UPDATED" in current_text, (
            f"Expected 'UPDATED' in latest revision text. Got:\n{current_text[:500]}"
        )

    def test_previous_revision_does_not_contain_updated_text(
        self, revision_client: DriveRevisionClient, two_revision_doc: str
    ):
        """The previous accessible revision should NOT contain UPDATED."""
        revs = revision_client.list_revisions(two_revision_doc)

        if len(revs) < 2:
            pytest.skip("Only one accessible revision; cannot test previous version")

        previous_text = revision_client.get_revision_text(two_revision_doc, revs[1].revision_id)

        assert "UPDATED" not in previous_text, (
            f"Previous revision should not contain 'UPDATED'. Got:\n{previous_text[:500]}"
        )

    def test_diff_between_current_and_previous(
        self, revision_client: DriveRevisionClient, two_revision_doc: str
    ):
        """Diffing current vs previous should show the UPDATED line as added."""
        from gdoc_fetch.changes import diff_texts

        revs = revision_client.list_revisions(two_revision_doc)

        if len(revs) < 2:
            pytest.skip("Only one accessible revision; cannot diff")

        current_text = revision_client.get_revision_text(two_revision_doc, revs[0].revision_id)
        previous_text = revision_client.get_revision_text(two_revision_doc, revs[1].revision_id)

        diff = diff_texts(previous_text, current_text, "previous", "current")

        assert diff != "(no text changes detected)", (
            "Expected changes between revisions, but diff found nothing"
        )
        added_lines = [l for l in diff.split('\n') if l.startswith('+') and not l.startswith('+++')]
        assert any("UPDATED" in l for l in added_lines), (
            f"Expected '+UPDATED ...' in diff added lines. Diff:\n{diff}"
        )


# ---------------------------------------------------------------------------
# Tests: gdoc-changes CLI end-to-end
# ---------------------------------------------------------------------------

@pytest.mark.integration
class TestGdocChangesCLIIntegration:

    def test_list_flag_shows_revision_history(self, two_revision_doc: str):
        """--list should print revision history and exit 0."""
        result = subprocess.run(
            ["gdoc-changes", two_revision_doc, "--list"],
            capture_output=True,
            text=True,
            timeout=60,
        )

        assert result.returncode == 0, f"CLI failed:\n{result.stderr}"
        assert "[1]" in result.stdout, f"Expected revision list in output:\n{result.stdout}"

    def test_default_shows_diff_between_last_two_revisions(self, two_revision_doc: str):
        """Default (no flags) should show a diff between the latest and previous revision."""
        time.sleep(2)  # avoid 429 after previous test
        result = subprocess.run(
            ["gdoc-changes", two_revision_doc],
            capture_output=True,
            text=True,
            timeout=120,
        )

        assert result.returncode == 0, f"CLI failed:\n{result.stderr}"
        output = result.stdout
        assert "---" in output or "+++" in output or "@@" in output or "no text changes" in output, (
            f"Expected diff markers in output:\n{output}"
        )

    def test_diff_output_shows_updated_content_as_added(self, two_revision_doc: str):
        """The diff should show 'UPDATED' as an added line (+)."""
        time.sleep(2)
        result = subprocess.run(
            ["gdoc-changes", two_revision_doc],
            capture_output=True,
            text=True,
            timeout=120,
        )

        assert result.returncode == 0, f"CLI failed:\n{result.stderr}"

        added_lines = [
            l for l in result.stdout.split('\n')
            if l.startswith('+') and not l.startswith('+++')
        ]
        assert any("UPDATED" in l for l in added_lines), (
            "Expected '+UPDATED ...' in diff output. Added lines:\n" + "\n".join(added_lines) +
            f"\n\nFull output:\n{result.stdout}"
        )

    def test_last_flag_spans_multiple_revisions(self, two_revision_doc: str):
        """--last 2 should attempt to span 2 revisions back and exit 0."""
        time.sleep(2)
        result = subprocess.run(
            ["gdoc-changes", two_revision_doc, "--last", "2"],
            capture_output=True,
            text=True,
            timeout=120,
        )

        assert result.returncode == 0, f"CLI failed:\n{result.stderr}"

    def test_invalid_doc_id_returns_nonzero(self):
        """A nonexistent doc ID should exit with non-zero status."""
        result = subprocess.run(
            ["gdoc-changes", "FAKE_DOC_ID_THAT_DOES_NOT_EXIST_XYZ"],
            capture_output=True,
            text=True,
            timeout=30,
        )

        assert result.returncode != 0

    def test_help_flag(self):
        """--help should print usage and exit 0."""
        result = subprocess.run(
            ["gdoc-changes", "--help"],
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0
        assert "gdoc-changes" in result.stdout
        assert "--last" in result.stdout
        assert "--list" in result.stdout
