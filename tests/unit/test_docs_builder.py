"""Tests for Google Docs API request builder."""
import pytest

from gdoc_fetch.docs_builder import DocsRequestBuilder
from gdoc_fetch.models import (
    Paragraph, Heading, ListItem, CodeBlock, Image, TextRun
)


@pytest.fixture
def builder():
    """Create request builder instance."""
    return DocsRequestBuilder()


def test_builder_initialization(builder):
    """Test builder initialization."""
    assert builder.current_index == 1
    assert builder.image_urls == {}


def test_build_simple_paragraph(builder):
    """Test building requests for simple paragraph."""
    para = Paragraph(text_runs=[TextRun(text="Hello world")])

    requests = builder.build_content_requests([para])

    assert len(requests) == 2  # Text insertion + newline
    assert requests[0]['insertText']['text'] == "Hello world"
    assert requests[0]['insertText']['location']['index'] == 1
    assert requests[1]['insertText']['text'] == "\n"


def test_build_paragraph_with_bold(builder):
    """Test paragraph with bold text."""
    para = Paragraph(text_runs=[
        TextRun(text="Hello "),
        TextRun(text="world", bold=True)
    ])

    requests = builder.build_content_requests([para])

    # Should have: Hello insertion, world insertion, bold formatting, newline
    assert len(requests) == 4

    # Check bold formatting request
    bold_req = requests[2]
    assert bold_req['updateTextStyle']['textStyle']['bold'] is True
    assert bold_req['updateTextStyle']['range']['startIndex'] == 7
    assert bold_req['updateTextStyle']['range']['endIndex'] == 12


def test_build_paragraph_with_italic(builder):
    """Test paragraph with italic text."""
    para = Paragraph(text_runs=[
        TextRun(text="Hello "),
        TextRun(text="world", italic=True)
    ])

    requests = builder.build_content_requests([para])

    italic_req = requests[2]
    assert italic_req['updateTextStyle']['textStyle']['italic'] is True


def test_build_paragraph_with_link(builder):
    """Test paragraph with link."""
    para = Paragraph(text_runs=[
        TextRun(text="Visit "),
        TextRun(text="example", link_url="https://example.com")
    ])

    requests = builder.build_content_requests([para])

    link_req = requests[2]
    assert link_req['updateTextStyle']['textStyle']['link']['url'] == "https://example.com"


def test_build_paragraph_with_multiple_formats(builder):
    """Test paragraph with bold + italic."""
    para = Paragraph(text_runs=[
        TextRun(text="Bold and italic", bold=True, italic=True)
    ])

    requests = builder.build_content_requests([para])

    format_req = requests[1]
    assert format_req['updateTextStyle']['textStyle']['bold'] is True
    assert format_req['updateTextStyle']['textStyle']['italic'] is True
    assert 'bold' in format_req['updateTextStyle']['fields']
    assert 'italic' in format_req['updateTextStyle']['fields']


def test_build_heading_level_1(builder):
    """Test building H1 heading."""
    heading = Heading(level=1, text_runs=[TextRun(text="Title")])

    requests = builder.build_content_requests([heading])

    # Should have: text insertion, newline, heading style
    assert len(requests) == 3

    style_req = requests[2]
    assert style_req['updateParagraphStyle']['paragraphStyle']['namedStyleType'] == 'HEADING_1'


def test_build_heading_level_3(builder):
    """Test building H3 heading."""
    heading = Heading(level=3, text_runs=[TextRun(text="Subtitle")])

    requests = builder.build_content_requests([heading])

    style_req = requests[2]
    assert style_req['updateParagraphStyle']['paragraphStyle']['namedStyleType'] == 'HEADING_3'


def test_build_heading_with_formatting(builder):
    """Test heading with inline formatting."""
    heading = Heading(level=2, text_runs=[
        TextRun(text="Important", bold=True),
        TextRun(text=" Title")
    ])

    requests = builder.build_content_requests([heading])

    # Should have: text1, bold format, text2, newline, heading style
    assert len(requests) == 5

    # Check bold formatting
    bold_req = requests[1]
    assert bold_req['updateTextStyle']['textStyle']['bold'] is True

    # Check heading style applied
    style_req = requests[4]
    assert style_req['updateParagraphStyle']['paragraphStyle']['namedStyleType'] == 'HEADING_2'


def test_build_bulleted_list_item(builder):
    """Test building bulleted list item."""
    item = ListItem(text_runs=[TextRun(text="Item 1")], ordered=False)

    requests = builder.build_content_requests([item])

    # Should have: text, newline, bullet formatting
    assert len(requests) == 3

    bullet_req = requests[2]
    assert bullet_req['createParagraphBullets']['bulletPreset'] == 'BULLET_DISC_CIRCLE_SQUARE'


def test_build_numbered_list_item(builder):
    """Test building numbered list item."""
    item = ListItem(text_runs=[TextRun(text="First")], ordered=True)

    requests = builder.build_content_requests([item])

    bullet_req = requests[2]
    assert bullet_req['createParagraphBullets']['bulletPreset'] == 'NUMBERED_DECIMAL_ALPHA_ROMAN'


def test_build_list_item_with_formatting(builder):
    """Test list item with bold text."""
    item = ListItem(text_runs=[
        TextRun(text="Bold", bold=True),
        TextRun(text=" item")
    ], ordered=False)

    requests = builder.build_content_requests([item])

    # Should have: text1, bold format, text2, newline, bullet format
    assert len(requests) == 5

    bold_req = requests[1]
    assert bold_req['updateTextStyle']['textStyle']['bold'] is True


def test_build_code_block(builder):
    """Test building code block."""
    code = CodeBlock(code="def hello():\n    print('world')", language="python")

    requests = builder.build_content_requests([code])

    # Should have: text insertion, monospace style, background shading
    assert len(requests) == 3

    # Check monospace font
    font_req = requests[1]
    assert font_req['updateTextStyle']['textStyle']['weightedFontFamily']['fontFamily'] == 'Courier New'
    assert font_req['updateTextStyle']['textStyle']['fontSize']['magnitude'] == 10

    # Check background shading
    shade_req = requests[2]
    assert 'shading' in shade_req['updateParagraphStyle']['paragraphStyle']


def test_build_image_with_url(builder):
    """Test building image with uploaded URL."""
    image = Image(alt_text="Test", local_path="image.png")

    # Provide uploaded URL
    builder.set_image_urls({"image.png": "https://drive.google.com/uc?id=123"})

    requests = builder.build_content_requests([image])

    # Should have: image insertion, newline
    assert len(requests) == 2

    img_req = requests[0]
    assert img_req['insertInlineImage']['uri'] == "https://drive.google.com/uc?id=123"
    assert img_req['insertInlineImage']['location']['index'] == 1


def test_build_image_without_url(builder):
    """Test building image without uploaded URL (fallback to text)."""
    image = Image(alt_text="Test", local_path="missing.png")

    requests = builder.build_content_requests([image])

    # Should insert placeholder text
    assert len(requests) == 1
    assert "[Image:" in requests[0]['insertText']['text']


def test_build_multiple_elements(builder):
    """Test building requests for multiple elements."""
    elements = [
        Heading(level=1, text_runs=[TextRun(text="Title")]),
        Paragraph(text_runs=[TextRun(text="Content")]),
        ListItem(text_runs=[TextRun(text="Item")], ordered=False)
    ]

    requests = builder.build_content_requests(elements)

    # Should have requests for all three elements
    assert len(requests) > 6  # At least 2-3 requests per element


def test_index_tracking(builder):
    """Test that indices are tracked correctly."""
    elements = [
        Paragraph(text_runs=[TextRun(text="First")]),
        Paragraph(text_runs=[TextRun(text="Second")])
    ]

    requests = builder.build_content_requests(elements)

    # First paragraph starts at index 1
    assert requests[0]['insertText']['location']['index'] == 1

    # Second paragraph starts after "First\n" (6 characters)
    second_para_idx = next(
        r['insertText']['location']['index']
        for r in requests[2:]  # Skip first paragraph requests
        if 'insertText' in r and r['insertText']['text'] == "Second"
    )
    assert second_para_idx == 7  # After "First\n"


def test_empty_elements_list(builder):
    """Test building with empty elements list."""
    requests = builder.build_content_requests([])

    assert len(requests) == 0
    assert builder.current_index == 1  # Should not change


def test_set_image_urls(builder):
    """Test setting image URL mapping."""
    urls = {
        "image1.png": "https://drive.google.com/1",
        "image2.png": "https://drive.google.com/2"
    }

    builder.set_image_urls(urls)

    assert builder.image_urls == urls


def test_complex_document(builder):
    """Test building complex document with various elements."""
    elements = [
        Heading(level=1, text_runs=[TextRun(text="Document Title")]),
        Paragraph(text_runs=[
            TextRun(text="This is "),
            TextRun(text="bold", bold=True),
            TextRun(text=" and "),
            TextRun(text="italic", italic=True),
            TextRun(text=".")
        ]),
        Heading(level=2, text_runs=[TextRun(text="Features")]),
        ListItem(text_runs=[TextRun(text="Feature 1")], ordered=False),
        ListItem(text_runs=[TextRun(text="Feature 2")], ordered=False),
        CodeBlock(code="code here", language="python"),
    ]

    requests = builder.build_content_requests(elements)

    # Should have many requests
    assert len(requests) > 15

    # Check we have various request types
    has_insert_text = any('insertText' in r for r in requests)
    has_text_style = any('updateTextStyle' in r for r in requests)
    has_para_style = any('updateParagraphStyle' in r for r in requests)
    has_bullets = any('createParagraphBullets' in r for r in requests)

    assert has_insert_text
    assert has_text_style
    assert has_para_style
    assert has_bullets
