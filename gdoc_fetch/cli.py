"""Command-line interface for gdoc-fetch."""
import argparse
import sys
from pathlib import Path

from gdoc_common.auth import get_access_token, AuthenticationError
from gdoc_common.utils import extract_doc_id
from gdoc_common.google_api import DocsClient
from gdoc_fetch.converter import DocsToHtmlParser, HtmlToMarkdownConverter
from gdoc_fetch.images import extract_image_urls, download_images
from gdoc_fetch.writer import write_document, replace_image_placeholders


def parse_args():
    """
    Parse command-line arguments.

    Returns:
        argparse.Namespace: Parsed arguments
    """
    parser = argparse.ArgumentParser(
        description='Fetch Google Docs, download images, convert to Markdown'
    )
    parser.add_argument(
        'url',
        help='Google Docs URL or document ID'
    )
    parser.add_argument(
        '--output-dir',
        default='./output',
        help='Output directory (default: ./output)'
    )
    parser.add_argument(
        '--no-images',
        action='store_true',
        help='Skip downloading images'
    )

    return parser.parse_args()


def main():
    """Main entry point for CLI."""
    args = parse_args()

    try:
        # Step 1: Extract document ID
        print(f"Extracting document ID from: {args.url}")
        doc_id = extract_doc_id(args.url)
        print(f"Document ID: {doc_id}")

        # Step 2: Authenticate
        print("\nAuthenticating with gcloud...")
        token = get_access_token()
        print("Authentication successful")

        # Step 3: Fetch document
        print(f"\nFetching document {doc_id}...")
        client = DocsClient(token=token)
        doc = client.fetch_document(doc_id)
        print(f"Fetched: {doc.title}")

        # Step 4: Convert to HTML then Markdown
        print("\nConverting to Markdown...")

        # We need to fetch the full document structure with body content
        # The DocsClient.fetch_document returns a Document model, but we need the raw API response
        # for the converter. Let me refetch with the raw data.
        raw_doc = client.service.documents().get(documentId=doc_id).execute()

        parser = DocsToHtmlParser()
        html = parser.parse(raw_doc)

        converter = HtmlToMarkdownConverter()
        markdown = converter.convert(html)

        print("Conversion complete")

        # Step 5: Download images (if not disabled)
        image_map = {}
        if not args.no_images:
            print("\nDownloading images...")
            image_urls = extract_image_urls(doc)

            if image_urls:
                print(f"Found {len(image_urls)} images")

                # Create output directory for this document
                from gdoc_fetch.writer import sanitize_filename
                safe_name = sanitize_filename(doc.title)
                doc_output_dir = Path(args.output_dir) / safe_name

                image_map = download_images(
                    image_urls=image_urls,
                    output_dir=str(doc_output_dir),
                    token=token
                )
                print(f"Downloaded {len(image_map)} images successfully")
            else:
                print("No images found")

        # Step 6: Replace image placeholders
        if image_map:
            print("\nReplacing image placeholders...")
            markdown = replace_image_placeholders(markdown, image_map)

        # Step 7: Write document
        print("\nWriting document...")

        # Reconstruct URL for frontmatter
        source_url = args.url if args.url.startswith('http') else f'https://docs.google.com/document/d/{doc_id}/edit'

        output_path = write_document(
            title=doc.title,
            source_url=source_url,
            markdown=markdown,
            output_dir=args.output_dir
        )

        print(f"\nSuccess! Document written to: {output_path}")

        return 0

    except AuthenticationError as e:
        print(f"\nAuthentication Error: {e}", file=sys.stderr)
        return 1
    except ValueError as e:
        print(f"\nError: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"\nUnexpected error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
