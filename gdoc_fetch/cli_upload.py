"""CLI for uploading markdown files to Google Docs."""
import argparse
import sys
from pathlib import Path
from typing import Dict, List

from gdoc_fetch.auth import get_access_token, AuthenticationError
from gdoc_fetch.markdown_parser import MarkdownParser
from gdoc_fetch.docs_builder import DocsRequestBuilder
from gdoc_fetch.google_api import DocsClient
from gdoc_fetch.drive_client import DriveClient
from gdoc_fetch.models import Image


def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description='Upload Markdown file to Google Docs',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  gdoc-upload document.md
  gdoc-upload document.md --title "My Document"
  gdoc-upload document.md --no-images
        """
    )

    parser.add_argument(
        'markdown_file',
        help='Path to markdown file to upload'
    )

    parser.add_argument(
        '--title',
        help='Document title (default: extracted from H1 or filename)'
    )

    parser.add_argument(
        '--no-images',
        action='store_true',
        help='Skip uploading images (faster, but images will be omitted)'
    )

    return parser.parse_args()


def collect_images(elements: List) -> List[Image]:
    """
    Collect all Image elements from document.

    Args:
        elements: List of document elements

    Returns:
        List of Image objects
    """
    images = []
    for element in elements:
        if isinstance(element, Image):
            images.append(element)
    return images


def upload_images(images: List[Image], drive_client: DriveClient, markdown_dir: Path) -> Dict[str, str]:
    """
    Upload images to Google Drive.

    Args:
        images: List of Image objects
        drive_client: DriveClient instance
        markdown_dir: Directory containing the markdown file

    Returns:
        Dict mapping local paths to uploaded URLs
    """
    if not images:
        return {}

    print(f"Uploading {len(images)} image(s) to Google Drive...")

    # Prepare image paths (resolve relative to markdown directory)
    image_paths = {}
    for img in images:
        local_path = img.local_path

        # Resolve relative paths
        if not Path(local_path).is_absolute():
            local_path = str(markdown_dir / local_path)

        image_paths[img.local_path] = local_path

    # Upload images
    uploaded_urls = {}
    success_count = 0

    for original_path, full_path in image_paths.items():
        try:
            # Use original path as key for results
            url = drive_client.upload_image(full_path)
            uploaded_urls[original_path] = url
            success_count += 1
            print(f"  ✓ Uploaded: {Path(full_path).name}")
        except (FileNotFoundError, ValueError, Exception) as e:
            print(f"  ✗ Failed: {Path(full_path).name} - {e}")
            continue

    print(f"Successfully uploaded {success_count}/{len(images)} image(s)")
    return uploaded_urls


def main():
    """Main entry point for gdoc-upload CLI."""
    args = parse_args()

    try:
        # Validate markdown file exists
        md_path = Path(args.markdown_file)
        if not md_path.exists():
            print(f"Error: File not found: {args.markdown_file}", file=sys.stderr)
            return 1

        # Step 1: Authenticate
        print("Authenticating with gcloud...")
        try:
            token = get_access_token()
            print("✓ Authentication successful\n")
        except AuthenticationError as e:
            print(f"\nAuthentication Error: {e}", file=sys.stderr)
            print("\nPlease run: gcloud auth login --enable-gdrive-access", file=sys.stderr)
            return 1

        # Step 2: Parse markdown
        print(f"Parsing markdown file: {args.markdown_file}")
        parser = MarkdownParser()

        try:
            doc = parser.parse_file(args.markdown_file)
        except (FileNotFoundError, ValueError) as e:
            print(f"\nError parsing markdown: {e}", file=sys.stderr)
            return 1

        # Use provided title or extracted title
        title = args.title or doc.title

        print(f"✓ Parsed document: '{title}'")
        print(f"  Found {len(doc.elements)} element(s)\n")

        # Step 3: Upload images (if not skipped)
        image_urls = {}
        if not args.no_images:
            images = collect_images(doc.elements)
            if images:
                drive_client = DriveClient(token=token)
                image_urls = upload_images(images, drive_client, md_path.parent)
                print()

        # Step 4: Create Google Doc
        print(f"Creating Google Doc: '{title}'...")
        docs_client = DocsClient(token=token)

        try:
            doc_id = docs_client.create_document(title)
            print(f"✓ Document created (ID: {doc_id})\n")
        except ValueError as e:
            print(f"\nError creating document: {e}", file=sys.stderr)
            return 1

        # Step 5: Build and upload content
        print("Uploading content...")
        builder = DocsRequestBuilder()
        requests = builder.build_content_requests(doc.elements, image_urls)

        if requests:
            try:
                docs_client.update_document_content(doc_id, requests)
                print(f"✓ Inserted {len(doc.elements)} element(s)")
                print(f"✓ Applied {len(requests)} operation(s)\n")
            except ValueError as e:
                print(f"\nWarning: Content upload failed: {e}", file=sys.stderr)
                print("Document was created but may be empty.\n", file=sys.stderr)
        else:
            print("✓ No content to upload (empty document)\n")

        # Step 6: Output URL
        url = docs_client.get_document_url(doc_id)
        print("=" * 60)
        print("Success! Document created:")
        print(url)
        print("=" * 60)

        return 0

    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user.", file=sys.stderr)
        return 130

    except Exception as e:
        print(f"\nUnexpected error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
