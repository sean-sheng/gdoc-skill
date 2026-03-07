"""Tests for markdown parser."""
import tempfile
from pathlib import Path

import pytest

from gdoc_fetch.markdown_parser import MarkdownParser
from gdoc_fetch.models import (
    MarkdownDocument, Paragraph, Heading, ListItem, CodeBlock, Image, TextRun
)


@pytest.fixture
def parser():
    """Create parser instance."""
    return MarkdownParser()


@pytest.fixture
def test_md_file(tmp_path):
    """Create a temporary markdown file for testing."""
    md_file = tmp_path / "test.md"
    md_file.write_text("# Test Title\n\nThis is a paragraph.")
    return str(md_file)


def test_parse_file_basic(parser, test_md_file):
    """Test parsing a basic markdown file."""
    doc = parser.parse_file(test_md_file)

    assert isinstance(doc, MarkdownDocument)
    assert doc.title == "Test Title"
    assert len(doc.elements) == 2  # H1 and paragraph


def test_parse_file_not_found(parser):
    """Test parsing non-existent file raises error."""
    with pytest.raises(FileNotFoundError):
        parser.parse_file("nonexistent.md")


def test_parse_empty_file(parser, tmp_path):
    """Test parsing empty file."""
    empty_file = tmp_path / "empty.md"
    empty_file.write_text("")

    doc = parser.parse_file(str(empty_file))

    assert doc.title == "Empty"  # Filename as title
    assert len(doc.elements) == 0


def test_parse_heading(parser, tmp_path):
    """Test parsing headings."""
    md_file = tmp_path / "headings.md"
    md_file.write_text("# H1\n## H2\n### H3")

    doc = parser.parse_file(str(md_file))

    assert len(doc.elements) == 3
    assert isinstance(doc.elements[0], Heading)
    assert doc.elements[0].level == 1
    assert doc.elements[1].level == 2
    assert doc.elements[2].level == 3


def test_parse_paragraph(parser, tmp_path):
    """Test parsing paragraphs."""
    md_file = tmp_path / "para.md"
    md_file.write_text("This is a paragraph.")

    doc = parser.parse_file(str(md_file))

    assert len(doc.elements) == 1
    assert isinstance(doc.elements[0], Paragraph)
    assert len(doc.elements[0].text_runs) == 1
    assert doc.elements[0].text_runs[0].text == "This is a paragraph."


def test_parse_bold_text(parser, tmp_path):
    """Test parsing bold text."""
    md_file = tmp_path / "bold.md"
    md_file.write_text("This is **bold** text.")

    doc = parser.parse_file(str(md_file))

    para = doc.elements[0]
    assert len(para.text_runs) == 3
    assert para.text_runs[0].text == "This is "
    assert para.text_runs[0].bold is False
    assert para.text_runs[1].text == "bold"
    assert para.text_runs[1].bold is True
    assert para.text_runs[2].text == " text."


def test_parse_italic_text(parser, tmp_path):
    """Test parsing italic text."""
    md_file = tmp_path / "italic.md"
    md_file.write_text("This is *italic* text.")

    doc = parser.parse_file(str(md_file))

    para = doc.elements[0]
    assert len(para.text_runs) == 3
    assert para.text_runs[1].text == "italic"
    assert para.text_runs[1].italic is True


def test_parse_link(parser, tmp_path):
    """Test parsing links."""
    md_file = tmp_path / "link.md"
    md_file.write_text("Visit [example](https://example.com) site.")

    doc = parser.parse_file(str(md_file))

    para = doc.elements[0]
    assert len(para.text_runs) == 3
    assert para.text_runs[1].text == "example"
    assert para.text_runs[1].link_url == "https://example.com"


def test_parse_bulleted_list(parser, tmp_path):
    """Test parsing bulleted lists."""
    md_file = tmp_path / "list.md"
    md_file.write_text("- Item 1\n- Item 2\n- Item 3")

    doc = parser.parse_file(str(md_file))

    assert len(doc.elements) == 3
    assert all(isinstance(elem, ListItem) for elem in doc.elements)
    assert all(elem.ordered is False for elem in doc.elements)
    assert doc.elements[0].text_runs[0].text == "Item 1"


def test_parse_numbered_list(parser, tmp_path):
    """Test parsing numbered lists."""
    md_file = tmp_path / "list.md"
    md_file.write_text("1. First\n2. Second\n3. Third")

    doc = parser.parse_file(str(md_file))

    assert len(doc.elements) == 3
    assert all(isinstance(elem, ListItem) for elem in doc.elements)
    assert all(elem.ordered is True for elem in doc.elements)


def test_parse_code_block(parser, tmp_path):
    """Test parsing code blocks."""
    md_file = tmp_path / "code.md"
    md_file.write_text("```python\ndef hello():\n    print('world')\n```")

    doc = parser.parse_file(str(md_file))

    assert len(doc.elements) == 1
    assert isinstance(doc.elements[0], CodeBlock)
    assert doc.elements[0].language == "python"
    assert "def hello()" in doc.elements[0].code


def test_parse_image(parser, tmp_path):
    """Test parsing images."""
    md_file = tmp_path / "image.md"
    md_file.write_text("![Alt text](image.png)")

    doc = parser.parse_file(str(md_file))

    assert len(doc.elements) == 1
    assert isinstance(doc.elements[0], Image)
    assert doc.elements[0].alt_text == "Alt text"
    assert doc.elements[0].local_path == "image.png"


def test_parse_complex_document(parser):
    """Test parsing the test fixture document."""
    fixture_path = Path(__file__).parent.parent / "fixtures" / "test_document.md"

    doc = parser.parse_file(str(fixture_path))

    assert doc.title == "Test Document"
    assert len(doc.elements) > 5

    # Check we have various element types
    has_heading = any(isinstance(e, Heading) for e in doc.elements)
    has_paragraph = any(isinstance(e, Paragraph) for e in doc.elements)
    has_list = any(isinstance(e, ListItem) for e in doc.elements)
    has_code = any(isinstance(e, CodeBlock) for e in doc.elements)
    has_image = any(isinstance(e, Image) for e in doc.elements)

    assert has_heading
    assert has_paragraph
    assert has_list
    assert has_code
    assert has_image


def test_title_from_h1(parser, tmp_path):
    """Test title extraction from first H1."""
    md_file = tmp_path / "test.md"
    md_file.write_text("# My Title\n\nContent here.")

    doc = parser.parse_file(str(md_file))

    assert doc.title == "My Title"


def test_title_from_filename(parser, tmp_path):
    """Test title fallback to filename."""
    md_file = tmp_path / "my-document-name.md"
    md_file.write_text("Some content without H1.")

    doc = parser.parse_file(str(md_file))

    assert doc.title == "My Document Name"
