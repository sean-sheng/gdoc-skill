"""Tests for conversion module."""
from gdoc_fetch.converter import HtmlToMarkdownConverter


def test_html_to_markdown_basic():
    """Test basic HTML to Markdown conversion."""
    converter = HtmlToMarkdownConverter()
    html = "<h1>Title</h1><p>Paragraph text.</p>"

    result = converter.convert(html)

    assert "# Title" in result
    assert "Paragraph text." in result


def test_html_to_markdown_formatting():
    """Test text formatting conversion."""
    converter = HtmlToMarkdownConverter()
    html = "<p>Text with <strong>bold</strong> and <em>italic</em>.</p>"

    result = converter.convert(html)

    assert "**bold**" in result
    assert "*italic*" in result


def test_html_to_markdown_links():
    """Test link conversion."""
    converter = HtmlToMarkdownConverter()
    html = '<p>Check <a href="https://example.com">this link</a>.</p>'

    result = converter.convert(html)

    assert "[this link](https://example.com)" in result


def test_html_to_markdown_lists():
    """Test list conversion."""
    converter = HtmlToMarkdownConverter()
    html = "<ul><li>Item 1</li><li>Item 2</li></ul>"

    result = converter.convert(html)

    assert "- Item 1" in result
    assert "- Item 2" in result


def test_html_to_markdown_images():
    """Test that image placeholders are preserved."""
    converter = HtmlToMarkdownConverter()
    html = '<img src="INLINE_OBJECT_kix.abc123" />'

    result = converter.convert(html)

    assert "INLINE_OBJECT_kix.abc123" in result
