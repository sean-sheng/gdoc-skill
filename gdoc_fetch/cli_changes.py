"""CLI for gdoc-changes: show recent changes to a Google Doc."""
import argparse
import sys

from gdoc_common.auth import get_access_token, AuthenticationError
from gdoc_common.utils import extract_doc_id
from gdoc_common.google_api import DriveRevisionClient
from gdoc_fetch.changes import format_revision_list, get_changes


def parse_args():
    parser = argparse.ArgumentParser(
        description='Show recent changes to a Google Doc',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Diff latest revision against the one before it
  gdoc-changes "https://docs.google.com/document/d/DOC_ID/edit"

  # Diff latest revision against 3 revisions back
  gdoc-changes "DOC_ID" --last 3

  # Only list revision history (no diff)
  gdoc-changes "DOC_ID" --list
        """
    )

    parser.add_argument('url', help='Google Docs URL or document ID')

    parser.add_argument(
        '--last',
        type=int,
        default=1,
        metavar='N',
        help='Span the diff across the last N revisions (default: 1)',
    )

    parser.add_argument(
        '--list',
        action='store_true',
        help='List revision history only, without showing a diff',
    )

    return parser.parse_args()


def main():
    args = parse_args()

    try:
        print("Authenticating with gcloud...")
        try:
            token = get_access_token()
            print("✓ Authentication successful\n")
        except AuthenticationError as e:
            print(f"\nAuthentication Error: {e}", file=sys.stderr)
            print("\nPlease run: gcloud auth login --enable-gdrive-access", file=sys.stderr)
            return 1

        doc_id = extract_doc_id(args.url)
        print(f"Document ID: {doc_id}\n")

        client = DriveRevisionClient(token=token)

        print("Fetching revision history...")
        revisions = client.list_revisions(doc_id)

        if not revisions:
            print("No revisions found for this document.")
            return 1

        print(f"Found {len(revisions)} revision(s):\n")
        print(format_revision_list(revisions))
        print()

        if args.list:
            return 0

        if len(revisions) < 2:
            print("Only one revision exists — no changes to show.")
            return 0

        span = min(args.last, len(revisions) - 1)
        newer = revisions[0]
        older = revisions[span]

        import time
        print(f"Fetching revision content...")
        newer_text = client.get_revision_text(doc_id, newer.revision_id)
        time.sleep(1)  # avoid hitting Google's export rate limit
        older_text = client.get_revision_text(doc_id, older.revision_id)

        print(f"\nChanges from [{span + 1}] → [1]")
        print(f"  From: {older.modified_time.strftime('%Y-%m-%d %H:%M')} by {older.modified_by}")
        print(f"  To:   {newer.modified_time.strftime('%Y-%m-%d %H:%M')} by {newer.modified_by}")
        print("=" * 60)

        from gdoc_fetch.changes import diff_texts
        newer_label = f"[1] {newer.modified_time.strftime('%Y-%m-%d %H:%M')} ({newer.modified_by})"
        older_label = f"[{span + 1}] {older.modified_time.strftime('%Y-%m-%d %H:%M')} ({older.modified_by})"
        diff = diff_texts(older_text, newer_text, older_label, newer_label)
        print(diff)
        print("=" * 60)

        return 0

    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user.", file=sys.stderr)
        return 130

    except Exception as e:
        print(f"\nError: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
