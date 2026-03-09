"""Parser for converting markdown files to structured document elements."""
import re
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import List, Optional

import markdown

from gdoc_common.models import (
    MarkdownDocument, Paragraph, Heading, ListItem, CodeBlock, Image, TextRun
)


class MarkdownParser:
    """Parse markdown files into structured document elements."""

    def __init__(self):
        """Initialize the markdown parser with extensions."""
        self.md = markdown.Markdown(
            extensions=['extra', 'fenced_code', 'nl2br']
        )

    def parse_file(self, filepath: str) -> MarkdownDocument:
        """
        Parse markdown file into structured document.

        Args:
            filepath: Path to markdown file

        Returns:
            MarkdownDocument with parsed elements

        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If file is empty or invalid
        """
        path = Path(filepath)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {filepath}")

        content = path.read_text(encoding='utf-8')
        if not content.strip():
            # Empty file - create doc with just filename as title
            return MarkdownDocument(
                title=path.stem.replace('-', ' ').replace('_', ' ').title(),
                elements=[]
            )

        # Parse markdown to HTML
        html = self.md.convert(content)
        self.md.reset()

        # Parse HTML to ElementTree
        try:
            # Wrap in div to ensure single root
            root = ET.fromstring(f'<div>{html}</div>')
        except ET.ParseError as e:
            raise ValueError(f"Failed to parse markdown: {e}")

        # Convert to our document elements
        elements = []
        for child in root:
            element = self._parse_element(child)
            if element:
                # Lists return multiple items, others return single item
                if isinstance(element, list):
                    elements.extend(element)
                else:
                    elements.append(element)

        # Extract title from first H1 or use filename
        title = self._get_title(elements, path.stem)

        return MarkdownDocument(title=title, elements=elements)

    def _parse_element(self, elem: ET.Element) -> Optional[object]:
        """
        Convert XML element to DocElement.

        Args:
            elem: ElementTree element

        Returns:
            DocElement instance or None if not supported
        """
        tag = elem.tag

        # Headings
        if tag in ('h1', 'h2', 'h3', 'h4', 'h5', 'h6'):
            level = int(tag[1])
            text_runs = self._extract_text_runs(elem)
            return Heading(level=level, text_runs=text_runs)

        # Paragraphs
        elif tag == 'p':
            # Check if paragraph contains only an image
            img_elem = elem.find('img')
            if img_elem is not None and len(list(elem)) == 1 and not elem.text and not elem.tail:
                # This is just an image wrapped in a paragraph
                alt = img_elem.attrib.get('alt', '')
                src = img_elem.attrib.get('src', '')
                if src:
                    return Image(alt_text=alt, local_path=src)

            # Regular paragraph with text
            text_runs = self._extract_text_runs(elem)
            if text_runs:  # Skip empty paragraphs
                return Paragraph(text_runs=text_runs)

        # Lists - process list items
        elif tag in ('ul', 'ol'):
            ordered = tag == 'ol'
            items = []
            for li in elem.findall('.//li'):
                text_runs = self._extract_text_runs(li)
                if text_runs:
                    items.append(ListItem(text_runs=text_runs, ordered=ordered))
            return items if items else None

        # Code blocks
        elif tag == 'pre':
            code_elem = elem.find('code')
            if code_elem is not None:
                code = ''.join(code_elem.itertext())
                # Try to extract language from class
                lang = None
                if 'class' in code_elem.attrib:
                    classes = code_elem.attrib['class'].split()
                    for cls in classes:
                        if cls.startswith('language-'):
                            lang = cls[9:]
                            break
                return CodeBlock(code=code, language=lang)

        # Images
        elif tag == 'img':
            alt = elem.attrib.get('alt', '')
            src = elem.attrib.get('src', '')
            if src:
                return Image(alt_text=alt, local_path=src)

        return None

    def _extract_text_runs(self, elem: ET.Element) -> List[TextRun]:
        """
        Extract text runs with inline formatting from element.

        Args:
            elem: ElementTree element

        Returns:
            List of TextRun objects
        """
        runs = []

        def process_node(node, bold=False, italic=False, link_url=None):
            """Recursively process node and its children."""
            # Process text before first child
            if node.text:
                runs.append(TextRun(
                    text=node.text,
                    bold=bold,
                    italic=italic,
                    link_url=link_url
                ))

            # Process children
            for child in node:
                child_bold = bold or child.tag in ('strong', 'b')
                child_italic = italic or child.tag in ('em', 'i')
                child_link = link_url

                if child.tag == 'a':
                    child_link = child.attrib.get('href', link_url)

                process_node(child, child_bold, child_italic, child_link)

                # Process tail text after child
                if child.tail:
                    runs.append(TextRun(
                        text=child.tail,
                        bold=bold,
                        italic=italic,
                        link_url=link_url
                    ))

        process_node(elem)
        return runs

    def _get_title(self, elements: List[object], filename: str) -> str:
        """
        Extract title from first H1 or use filename.

        Args:
            elements: List of parsed elements
            filename: Fallback filename without extension

        Returns:
            Document title
        """
        # Look for first H1
        for elem in elements:
            if isinstance(elem, Heading) and elem.level == 1:
                # Concatenate text from all runs
                return ''.join(run.text for run in elem.text_runs)

        # Fallback to filename, cleaned up
        title = filename.replace('-', ' ').replace('_', ' ')
        return title.title()
