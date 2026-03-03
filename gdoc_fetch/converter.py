"""Document conversion from Google Docs to Markdown."""
from markdownify import markdownify as md


class HtmlToMarkdownConverter:
    """Converts HTML to Markdown using markdownify."""

    def __init__(self):
        """Initialize converter with default options."""
        self.options = {
            'heading_style': 'ATX',  # Use # for headings
            'bullets': '-',  # Use - for bullets
            'strip': ['script', 'style'],
        }

    def convert(self, html: str) -> str:
        """
        Convert HTML to Markdown.

        Args:
            html: HTML string

        Returns:
            Markdown string
        """
        return md(html, **self.options)
