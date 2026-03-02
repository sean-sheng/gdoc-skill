# gdoc-fetch

Fetch Google Docs, download images, and convert to Markdown.

## Installation

```bash
pip install -e .
```

## Usage

```bash
gdoc-fetch <google-doc-url> [--output-dir ./output]
```

## Authentication

Run once:
```bash
gcloud auth login --enable-gdrive-access
```

## Development

Install dev dependencies:
```bash
pip install -e ".[dev]"
```

Run tests:
```bash
pytest
```
