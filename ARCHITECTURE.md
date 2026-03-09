# Project Architecture

## Overview

The project is structured into three main packages with clear separation of concerns:

```
gdoc-skill/
├── gdoc_common/      # Shared utilities
├── gdoc_fetch/       # Fetch Google Docs → Markdown
├── gdoc_upload/      # Upload Markdown → Google Docs
└── tests/
    ├── unit/
    └── integration/
```

## Package Structure

### gdoc_common/ - Shared Components

Common utilities used by both gdoc-fetch and gdoc-upload:

```
gdoc_common/
├── __init__.py       # Public API exports
├── auth.py           # Google Cloud authentication
├── google_api.py     # Google Docs API client
├── models.py         # Data models (Document, Paragraph, etc.)
└── utils.py          # URL parsing utilities
```

**Responsibilities:**
- Authentication with Google Cloud (gcloud)
- Google Docs API client operations
- Data models for document structure
- URL/ID extraction utilities

**Key Classes:**
- `DocsClient` - Google Docs API operations
- `Document`, `InlineObject` - Document data models
- `Heading`, `Paragraph`, `ListItem`, `CodeBlock`, `Image` - Content elements
- `TextRun` - Inline formatting

### gdoc_fetch/ - Fetch Functionality

Fetch Google Docs and convert to Markdown:

```
gdoc_fetch/
├── __init__.py       # Public API exports
├── cli.py            # Command-line interface (entry point)
├── converter.py      # Docs→HTML→Markdown conversion
├── images.py         # Image download from Google Docs
└── writer.py         # File writing with frontmatter
```

**Responsibilities:**
- CLI for `gdoc-fetch` command
- Convert Google Docs to HTML
- Convert HTML to Markdown
- Download embedded images
- Write files with proper structure

**Key Classes:**
- `DocsToHtmlParser` - Parse Google Docs JSON to HTML
- `HtmlToMarkdownConverter` - Convert HTML to Markdown

**Main Function:**
```python
def main():
    """Entry point for gdoc-fetch command."""
    # 1. Parse arguments
    # 2. Authenticate
    # 3. Fetch document
    # 4. Convert to HTML
    # 5. Convert to Markdown
    # 6. Download images
    # 7. Write files
```

### gdoc_upload/ - Upload Functionality

Upload Markdown files to create Google Docs:

```
gdoc_upload/
├── __init__.py       # Public API exports
├── cli.py            # Command-line interface (entry point)
├── markdown_parser.py # Parse Markdown files
├── docs_builder.py   # Build Google Docs API requests
└── drive_client.py   # Upload images to Google Drive
```

**Responsibilities:**
- CLI for `gdoc-upload` command
- Parse Markdown files
- Build Google Docs API requests
- Upload images to Google Drive
- Create formatted Google Docs

**Key Classes:**
- `MarkdownParser` - Parse Markdown to structured elements
- `DocsRequestBuilder` - Build Google Docs API batch requests
- `DriveClient` - Upload images to Google Drive

**Main Function:**
```python
def main():
    """Entry point for gdoc-upload command."""
    # 1. Parse arguments
    # 2. Authenticate
    # 3. Parse Markdown
    # 4. Upload images (if any)
    # 5. Create Google Doc
    # 6. Build API requests
    # 7. Upload content
```

## Data Flow

### gdoc-fetch (Fetch Flow)

```
Google Docs API
       ↓
  DocsClient.fetch_document()
       ↓
  DocsToHtmlParser.parse()
       ↓
     HTML
       ↓
  HtmlToMarkdownConverter.convert()
       ↓
   Markdown
       ↓
  download_images()
       ↓
  write_document()
       ↓
  Local Files
```

### gdoc-upload (Upload Flow)

```
Markdown File
       ↓
  MarkdownParser.parse_file()
       ↓
  Structured Elements
       ↓
  DriveClient.upload_image() (for images)
       ↓
  DocsRequestBuilder.build_content_requests()
       ↓
  API Requests
       ↓
  DocsClient.create_document()
  DocsClient.update_document_content()
       ↓
  Google Docs
```

## Module Dependencies

### gdoc_common (No Dependencies)
- Self-contained
- Only external dependencies: google-api-python-client, google-auth

### gdoc_fetch Dependencies
- `gdoc_common.auth` - Authentication
- `gdoc_common.google_api` - DocsClient
- `gdoc_common.models` - Document models
- `gdoc_common.utils` - URL parsing
- External: markdownify

### gdoc_upload Dependencies
- `gdoc_common.auth` - Authentication
- `gdoc_common.google_api` - DocsClient
- `gdoc_common.models` - Document models
- External: markdown

## Testing Structure

```
tests/
├── unit/
│   ├── test_auth.py           # gdoc_common tests
│   ├── test_google_api.py     # gdoc_common tests
│   ├── test_models.py         # gdoc_common tests
│   ├── test_utils.py          # gdoc_common tests
│   ├── test_cli.py            # gdoc_fetch tests
│   ├── test_converter.py      # gdoc_fetch tests
│   ├── test_images.py         # gdoc_fetch tests
│   ├── test_writer.py         # gdoc_fetch tests
│   ├── test_markdown_parser.py # gdoc_upload tests
│   ├── test_docs_builder.py   # gdoc_upload tests
│   └── test_drive_client.py   # gdoc_upload tests
└── integration/
    ├── test_gdoc_fetch_integration.py
    └── test_gdoc_upload_integration.py
```

## Key Design Principles

1. **Separation of Concerns**
   - Common utilities in `gdoc_common`
   - Fetch-specific code in `gdoc_fetch`
   - Upload-specific code in `gdoc_upload`

2. **Clear Interfaces**
   - Each module exports clear public APIs via `__init__.py`
   - Internal implementation details are not exposed

3. **Independent Development**
   - Fetch and upload can be developed independently
   - Shared code changes affect both equally

4. **Testability**
   - Unit tests for each module
   - Integration tests for end-to-end workflows
   - Mock patches use correct module paths

5. **CLI Entry Points**
   - `gdoc-fetch` → `gdoc_fetch.cli:main`
   - `gdoc-upload` → `gdoc_upload.cli:main`

## Adding New Features

### Adding to gdoc-fetch

1. Add implementation to appropriate module in `gdoc_fetch/`
2. Export in `gdoc_fetch/__init__.py` if public API
3. Add unit tests in `tests/unit/`
4. Add integration tests if needed

### Adding to gdoc-upload

1. Add implementation to appropriate module in `gdoc_upload/`
2. Export in `gdoc_upload/__init__.py` if public API
3. Add unit tests in `tests/unit/`
4. Add integration tests if needed

### Adding to gdoc_common

1. Add implementation to `gdoc_common/`
2. Export in `gdoc_common/__init__.py`
3. Update both `gdoc_fetch` and `gdoc_upload` if needed
4. Add tests covering both use cases

## Benefits of This Structure

1. **Clarity** - Clear what belongs to fetch vs upload
2. **Maintainability** - Easier to find and modify code
3. **Scalability** - Can add new commands easily
4. **Reusability** - Shared code in one place
5. **Testing** - Easy to test each component
6. **Documentation** - Self-documenting structure

## Migration from Old Structure

Old structure (single package):
```
gdoc_fetch/
├── cli.py (fetch)
├── cli_upload.py (upload)
└── (all modules mixed together)
```

New structure (three packages):
```
├── gdoc_common/ (shared)
├── gdoc_fetch/ (fetch only)
└── gdoc_upload/ (upload only)
```

**Import Changes:**
- `from gdoc_fetch.auth` → `from gdoc_common.auth`
- `from gdoc_fetch.models` → `from gdoc_common.models`
- `from gdoc_fetch.cli_upload` → `from gdoc_upload.cli`
- `from gdoc_fetch.markdown_parser` → `from gdoc_upload.markdown_parser`

All tests have been updated to reflect the new structure.
