"""Document conversion from Google Docs to Markdown."""
from typing import Dict, List, Any
from markdownify import markdownify as md


class DocsToHtmlParser:
    """Converts Google Docs JSON structure to HTML."""

    def parse(self, doc_structure: Dict[str, Any]) -> str:
        """
        Parse Google Docs structure to HTML.

        Args:
            doc_structure: Google Docs API response structure

        Returns:
            HTML string
        """
        self.lists_data = doc_structure.get('lists', {})
        html_parts = []

        body = doc_structure.get('body', {})
        content = body.get('content', [])

        # Group consecutive list items
        i = 0
        while i < len(content):
            element = content[i]

            # Check if this is a list item
            if 'paragraph' in element and 'bullet' in element['paragraph']:
                # Collect all consecutive items from the same list
                list_items = []
                current_list_id = element['paragraph']['bullet'].get('listId')

                while i < len(content):
                    curr_elem = content[i]
                    if 'paragraph' in curr_elem and 'bullet' in curr_elem['paragraph']:
                        bullet = curr_elem['paragraph']['bullet']
                        if bullet.get('listId') == current_list_id:
                            list_items.append(curr_elem)
                            i += 1
                        else:
                            break
                    else:
                        break

                # Generate list HTML
                html_parts.append(self._parse_list(list_items, current_list_id))
            else:
                html_parts.append(self._parse_structural_element(element))
                i += 1

        return ''.join(html_parts)

    def _parse_structural_element(self, element: Dict[str, Any]) -> str:
        """Parse a single structural element."""
        if 'paragraph' in element:
            return self._parse_paragraph(element['paragraph'])
        elif 'table' in element:
            return self._parse_table(element['table'])

        return ''

    def _parse_table(self, table: Dict[str, Any]) -> str:
        """Parse a table element into narrative HTML using header row as field titles."""
        rows = table.get('tableRows', [])
        if not rows:
            return ''

        # Extract header labels from the first row
        headers = []
        for cell in rows[0].get('tableCells', []):
            text = self._extract_cell_text(cell.get('content', []))
            headers.append(text)

        # Convert each data row into a narrative block
        html_parts = []
        for row in rows[1:]:
            cells = row.get('tableCells', [])
            row_parts = []
            for col_idx, cell in enumerate(cells):
                cell_html = self._parse_cell_content(cell.get('content', []))
                if not cell_html.strip():
                    continue
                header = headers[col_idx] if col_idx < len(headers) else ''
                if header:
                    row_parts.append(f'<p><strong>{header}:</strong> {cell_html}</p>')
                else:
                    row_parts.append(f'<p>{cell_html}</p>')
            if row_parts:
                html_parts.append(''.join(row_parts))

        if not html_parts:
            return ''

        return '<hr>'.join(html_parts) + '<hr>'

    def _extract_cell_text(self, content: List[Dict[str, Any]]) -> str:
        """Extract plain text from cell content for use as a label."""
        texts = []
        for elem in content:
            if 'paragraph' in elem:
                for pe in elem['paragraph'].get('elements', []):
                    if 'textRun' in pe:
                        texts.append(pe['textRun'].get('content', '').strip())
        return ' '.join(t for t in texts if t)

    def _parse_cell_content(self, content: List[Dict[str, Any]]) -> str:
        """Parse the content elements inside a table cell."""
        parts = []
        i = 0
        while i < len(content):
            element = content[i]
            if 'paragraph' in element and 'bullet' in element['paragraph']:
                list_items = []
                current_list_id = element['paragraph']['bullet'].get('listId')
                while i < len(content):
                    curr = content[i]
                    if 'paragraph' in curr and 'bullet' in curr['paragraph']:
                        if curr['paragraph']['bullet'].get('listId') == current_list_id:
                            list_items.append(curr)
                            i += 1
                        else:
                            break
                    else:
                        break
                parts.append(self._parse_list(list_items, current_list_id))
            else:
                parsed = self._parse_structural_element(element)
                if parsed:
                    parts.append(parsed)
                i += 1
        return ''.join(parts)

    def _parse_list(self, list_items: List[Dict[str, Any]], list_id: str) -> str:
        """Parse a list of items into HTML."""
        if not list_items:
            return ''

        # Determine if it's ordered or unordered
        list_props = self.lists_data.get(list_id, {}).get('listProperties', {})
        nesting_levels = list_props.get('nestingLevels', [{}])
        glyph_type = nesting_levels[0].get('glyphType', 'BULLET')

        is_ordered = glyph_type in ['DECIMAL', 'ROMAN', 'ALPHA']
        tag = 'ol' if is_ordered else 'ul'

        items_html = []
        for item in list_items:
            paragraph = item['paragraph']
            elements = paragraph.get('elements', [])
            text_parts = []

            for elem in elements:
                if 'textRun' in elem:
                    text_parts.append(self._parse_text_run(elem['textRun']))

            text = ''.join(text_parts).strip()
            if text:
                items_html.append(f'<li>{text}</li>')

        return f'<{tag}>{"".join(items_html)}</{tag}>'

    HEADING_MAP = {
        'HEADING_1': 'h1',
        'HEADING_2': 'h2',
        'HEADING_3': 'h3',
        'HEADING_4': 'h4',
        'HEADING_5': 'h5',
        'HEADING_6': 'h6',
    }

    def _parse_paragraph(self, paragraph: Dict[str, Any]) -> str:
        """Parse a paragraph element."""
        elements = paragraph.get('elements', [])
        text_parts = []

        for elem in elements:
            if 'textRun' in elem:
                text_parts.append(self._parse_text_run(elem['textRun']))
            elif 'inlineObjectElement' in elem:
                text_parts.append(self._parse_inline_object(elem['inlineObjectElement']))

        text = ''.join(text_parts).strip()
        if not text:
            return ''

        style_type = paragraph.get('paragraphStyle', {}).get('namedStyleType', '')
        tag = self.HEADING_MAP.get(style_type, 'p')

        return f'<{tag}>{text}</{tag}>'

    def _parse_inline_object(self, inline_object: Dict[str, Any]) -> str:
        """Parse an inline object (typically an image) to a placeholder."""
        object_id = inline_object.get('inlineObjectId', '')
        return f'<img src="INLINE_OBJECT_{object_id}" />'

    def _parse_text_run(self, text_run: Dict[str, Any]) -> str:
        """Parse a text run with optional styling."""
        content = text_run.get('content', '').rstrip('\n')
        if not content:
            return ''

        text_style = text_run.get('textStyle', {})

        # Apply bold
        if text_style.get('bold'):
            content = f'<strong>{content}</strong>'

        # Apply italic
        if text_style.get('italic'):
            content = f'<em>{content}</em>'

        # Apply link
        if 'link' in text_style:
            url = text_style['link'].get('url', '')
            content = f'<a href="{url}">{content}</a>'

        return content


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
