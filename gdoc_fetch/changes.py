"""Google Doc change detection and diffing."""
import difflib
from typing import List, Tuple

from gdoc_common.google_api import DriveRevisionClient, Revision


def format_revision_list(revisions: List[Revision]) -> str:
    """Format a list of revisions for display."""
    lines = []
    for i, rev in enumerate(revisions):
        ts = rev.modified_time.strftime('%Y-%m-%d %H:%M:%S %Z').strip()
        marker = " (latest)" if i == 0 else ""
        lines.append(f"  [{i + 1}] {ts} — {rev.modified_by}{marker}  (id: {rev.revision_id})")
    return "\n".join(lines)


def diff_texts(old_text: str, new_text: str, old_label: str, new_label: str) -> str:
    """Generate a unified diff between two text strings."""
    old_lines = old_text.splitlines(keepends=True)
    new_lines = new_text.splitlines(keepends=True)

    diff = list(difflib.unified_diff(
        old_lines,
        new_lines,
        fromfile=old_label,
        tofile=new_label,
        lineterm='',
    ))

    if not diff:
        return "(no text changes detected)"

    return "\n".join(line.rstrip('\n') for line in diff)


def get_changes(doc_id: str, token: str, last: int = 1) -> Tuple[List[Revision], str]:
    """
    Fetch the latest revisions and return a diff.

    Args:
        doc_id: Google Doc ID
        token: OAuth access token
        last: Number of recent revisions to span the diff across

    Returns:
        Tuple of (revisions list, diff string)
    """
    client = DriveRevisionClient(token=token)
    revisions = client.list_revisions(doc_id)

    if len(revisions) < 2:
        return revisions, "(only one revision exists — no changes to show)"

    # Clamp to available revisions
    span = min(last, len(revisions) - 1)

    newer_rev = revisions[0]
    older_rev = revisions[span]

    newer_text = client.get_revision_text(doc_id, newer_rev.revision_id)
    older_text = client.get_revision_text(doc_id, older_rev.revision_id)

    newer_label = f"revision {newer_rev.revision_id} ({newer_rev.modified_time.strftime('%Y-%m-%d %H:%M')})"
    older_label = f"revision {older_rev.revision_id} ({older_rev.modified_time.strftime('%Y-%m-%d %H:%M')})"

    diff = diff_texts(older_text, newer_text, older_label, newer_label)
    return revisions, diff
