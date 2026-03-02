"""Utility functions."""
import re


def extract_doc_id(url_or_id: str) -> str:
    """
    Extract document ID from a Google Docs URL or return ID as-is.

    Args:
        url_or_id: Google Docs URL or document ID

    Returns:
        Document ID

    Raises:
        ValueError: If ID cannot be extracted
    """
    if not url_or_id or not url_or_id.strip():
        raise ValueError("Empty URL or ID provided")

    # Try to extract from URL
    match = re.search(r"/document/d/([a-zA-Z0-9_-]+)", url_or_id)
    if match:
        return match.group(1)

    # Check if it's already a valid ID format
    if re.match(r"^[a-zA-Z0-9_-]+$", url_or_id.strip()):
        return url_or_id.strip()

    raise ValueError(
        f"Could not extract a Google Doc ID from: {url_or_id}\n"
        f"Expected format: https://docs.google.com/document/d/DOC_ID/..."
    )
