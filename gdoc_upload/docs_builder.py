"""Build Google Docs API requests from markdown elements."""
from typing import List, Dict, Any

from gdoc_common.models import (
    Paragraph, Heading, ListItem, CodeBlock, Image, TextRun
)


class DocsRequestBuilder:
    """Build Google Docs API batchUpdate requests from DocElements."""

    def __init__(self):
        """Initialize the request builder."""
        self.current_index = 1  # Start after document title
        self.image_urls = {}  # Map local paths to uploaded URLs

    def set_image_urls(self, image_urls: Dict[str, str]):
        """
        Set mapping of local image paths to uploaded URLs.

        Args:
            image_urls: Dict mapping local paths to Drive URLs
        """
        self.image_urls = image_urls

    def build_content_requests(self, elements: List[Any], image_urls: Dict[str, str] = None) -> List[Dict]:
        """
        Convert elements to API requests with proper indexing.

        Args:
            elements: List of DocElement objects
            image_urls: Optional dict mapping image paths to uploaded URLs

        Returns:
            List of Google Docs API request dicts
        """
        if image_urls:
            self.image_urls = image_urls

        requests = []

        for element in elements:
            if isinstance(element, Paragraph):
                requests.extend(self._build_paragraph_requests(element))
            elif isinstance(element, Heading):
                requests.extend(self._build_heading_requests(element))
            elif isinstance(element, ListItem):
                requests.extend(self._build_list_item_requests(element))
            elif isinstance(element, CodeBlock):
                requests.extend(self._build_code_block_requests(element))
            elif isinstance(element, Image):
                requests.extend(self._build_image_requests(element))

        return requests

    def _build_paragraph_requests(self, para: Paragraph) -> List[Dict]:
        """Build requests for paragraph with formatting."""
        requests = []

        # Insert text with inline formatting
        start_index = self.current_index

        for run in para.text_runs:
            # Insert text
            requests.append({
                'insertText': {
                    'location': {'index': self.current_index},
                    'text': run.text
                }
            })

            run_length = len(run.text)

            # Apply formatting if needed
            if run.bold or run.italic or run.link_url:
                text_style = {}
                fields = []

                if run.bold:
                    text_style['bold'] = True
                    fields.append('bold')

                if run.italic:
                    text_style['italic'] = True
                    fields.append('italic')

                if run.link_url:
                    text_style['link'] = {'url': run.link_url}
                    fields.append('link')

                requests.append({
                    'updateTextStyle': {
                        'range': {
                            'startIndex': self.current_index,
                            'endIndex': self.current_index + run_length
                        },
                        'textStyle': text_style,
                        'fields': ','.join(fields)
                    }
                })

            self.current_index += run_length

        # Add newline after paragraph
        requests.append({
            'insertText': {
                'location': {'index': self.current_index},
                'text': '\n'
            }
        })
        self.current_index += 1

        return requests

    def _build_heading_requests(self, heading: Heading) -> List[Dict]:
        """Build requests for heading."""
        requests = []
        start_index = self.current_index

        # Insert text with inline formatting
        for run in heading.text_runs:
            requests.append({
                'insertText': {
                    'location': {'index': self.current_index},
                    'text': run.text
                }
            })

            run_length = len(run.text)

            # Apply inline formatting if needed
            if run.bold or run.italic or run.link_url:
                text_style = {}
                fields = []

                if run.bold:
                    text_style['bold'] = True
                    fields.append('bold')

                if run.italic:
                    text_style['italic'] = True
                    fields.append('italic')

                if run.link_url:
                    text_style['link'] = {'url': run.link_url}
                    fields.append('link')

                requests.append({
                    'updateTextStyle': {
                        'range': {
                            'startIndex': self.current_index,
                            'endIndex': self.current_index + run_length
                        },
                        'textStyle': text_style,
                        'fields': ','.join(fields)
                    }
                })

            self.current_index += run_length

        # Add newline
        requests.append({
            'insertText': {
                'location': {'index': self.current_index},
                'text': '\n'
            }
        })
        self.current_index += 1

        # Apply heading style to the entire paragraph
        heading_style = f'HEADING_{heading.level}'
        requests.append({
            'updateParagraphStyle': {
                'range': {
                    'startIndex': start_index,
                    'endIndex': self.current_index
                },
                'paragraphStyle': {
                    'namedStyleType': heading_style
                },
                'fields': 'namedStyleType'
            }
        })

        return requests

    def _build_list_item_requests(self, item: ListItem) -> List[Dict]:
        """Build requests for list item."""
        requests = []
        start_index = self.current_index

        # Insert text with inline formatting (similar to paragraph)
        for run in item.text_runs:
            requests.append({
                'insertText': {
                    'location': {'index': self.current_index},
                    'text': run.text
                }
            })

            run_length = len(run.text)

            if run.bold or run.italic or run.link_url:
                text_style = {}
                fields = []

                if run.bold:
                    text_style['bold'] = True
                    fields.append('bold')

                if run.italic:
                    text_style['italic'] = True
                    fields.append('italic')

                if run.link_url:
                    text_style['link'] = {'url': run.link_url}
                    fields.append('link')

                requests.append({
                    'updateTextStyle': {
                        'range': {
                            'startIndex': self.current_index,
                            'endIndex': self.current_index + run_length
                        },
                        'textStyle': text_style,
                        'fields': ','.join(fields)
                    }
                })

            self.current_index += run_length

        # Add newline
        requests.append({
            'insertText': {
                'location': {'index': self.current_index},
                'text': '\n'
            }
        })
        self.current_index += 1

        # Apply bullet formatting
        glyph_type = 'NUMBERED_DECIMAL_ALPHA_ROMAN' if item.ordered else 'BULLET_DISC_CIRCLE_SQUARE'

        requests.append({
            'createParagraphBullets': {
                'range': {
                    'startIndex': start_index,
                    'endIndex': self.current_index
                },
                'bulletPreset': glyph_type
            }
        })

        return requests

    def _build_code_block_requests(self, code: CodeBlock) -> List[Dict]:
        """Build requests for code block (monospace style)."""
        requests = []
        start_index = self.current_index

        # Insert code text
        requests.append({
            'insertText': {
                'location': {'index': self.current_index},
                'text': code.code + '\n'
            }
        })

        code_length = len(code.code) + 1
        self.current_index += code_length

        # Apply monospace font family (Courier New or Consolas)
        requests.append({
            'updateTextStyle': {
                'range': {
                    'startIndex': start_index,
                    'endIndex': self.current_index
                },
                'textStyle': {
                    'weightedFontFamily': {
                        'fontFamily': 'Courier New'
                    },
                    'fontSize': {
                        'magnitude': 10,
                        'unit': 'PT'
                    }
                },
                'fields': 'weightedFontFamily,fontSize'
            }
        })

        # Add background color for code block
        requests.append({
            'updateParagraphStyle': {
                'range': {
                    'startIndex': start_index,
                    'endIndex': self.current_index
                },
                'paragraphStyle': {
                    'shading': {
                        'backgroundColor': {
                            'color': {
                                'rgbColor': {
                                    'red': 0.95,
                                    'green': 0.95,
                                    'blue': 0.95
                                }
                            }
                        }
                    }
                },
                'fields': 'shading'
            }
        })

        return requests

    def _build_image_requests(self, image: Image) -> List[Dict]:
        """Build requests for inline image insertion."""
        requests = []

        # Get uploaded URL for this image
        image_url = self.image_urls.get(image.local_path)

        if not image_url:
            # Image not uploaded, insert placeholder text instead
            placeholder = f"[Image: {image.alt_text or image.local_path}]\n"
            requests.append({
                'insertText': {
                    'location': {'index': self.current_index},
                    'text': placeholder
                }
            })
            self.current_index += len(placeholder)
            return requests

        # Insert inline image
        requests.append({
            'insertInlineImage': {
                'location': {'index': self.current_index},
                'uri': image_url,
                'objectSize': {
                    'height': {'magnitude': 300, 'unit': 'PT'},
                    'width': {'magnitude': 400, 'unit': 'PT'}
                }
            }
        })

        # Images take 1 character space
        self.current_index += 1

        # Add newline after image
        requests.append({
            'insertText': {
                'location': {'index': self.current_index},
                'text': '\n'
            }
        })
        self.current_index += 1

        return requests
