# gdoc-fetch

Fetch Google Docs, download images, and convert to Markdown.

A standalone Python CLI tool that integrates seamlessly with Claude Code, allowing you to fetch Google Docs documents, download embedded images, and convert everything to clean Markdown format.

## ✨ Features

- 📥 **Fetch Google Docs** - Works with both public and private documents
- 🖼️ **Download Images** - Automatically downloads and embeds images with authentication
- 📝 **Clean Markdown** - Preserves formatting (bold, italic, links, lists, tables)
- 🔒 **Secure** - Uses Google Cloud authentication (no API keys needed)
- 🤖 **Claude Code Ready** - Integrates as a skill for seamless use in conversations
- ✅ **Well Tested** - 58 comprehensive unit tests with 100% pass rate

## 🚀 Quick Start

See [QUICKSTART.md](QUICKSTART.md) for a 5-minute setup guide!

```bash
# 1. Install
pip3 install --user -e .

# 2. Authenticate (one-time)
gcloud auth login --enable-gdrive-access

# 3. Use it!
gdoc-fetch "https://docs.google.com/document/d/YOUR_DOC_ID/edit"
```

## 📚 Documentation

- **[QUICKSTART.md](QUICKSTART.md)** - Get started in 5 minutes
- **[INSTALLATION.md](INSTALLATION.md)** - Complete installation guide with troubleshooting
- **[SKILL.md](SKILL.md)** - Claude Code integration documentation

## 💻 Usage

### Basic Command

```bash
gdoc-fetch <google-doc-url> [--output-dir ./output] [--no-images]
```

### Examples

```bash
# Fetch a document
gdoc-fetch "https://docs.google.com/document/d/123abc/edit"

# Custom output location
gdoc-fetch "https://docs.google.com/document/d/123abc/edit" --output-dir ./docs

# Skip images (faster)
gdoc-fetch "https://docs.google.com/document/d/123abc/edit" --no-images

# Use document ID directly
gdoc-fetch "123abc"
```

### Output Structure

```
output/
└── document-name/
    ├── document-name.md    # Markdown with frontmatter
    └── images/
        ├── image-001.png
        └── image-002.jpg
```

## 🔐 Authentication

Requires Google Cloud SDK (gcloud) for authentication.

**One-time setup:**
```bash
gcloud auth login --enable-gdrive-access
```

This uses your Google account credentials - no API keys needed!

## 🤖 Claude Code Integration

Works seamlessly with Claude Code. Just paste a Google Docs URL:

```
You: "Here's a spec: https://docs.google.com/document/d/..."
Claude: [automatically fetches and reads the document]
```

See [SKILL.md](SKILL.md) for integration details.

## 🛠️ Development

### Install Dev Dependencies

```bash
pip3 install -e ".[dev]"
```

### Run Tests

```bash
PYTHONPATH=. pytest tests/ -v

# Expected: 58 tests passed
```

### Project Structure

```
gdoc-skill/
├── gdoc_fetch/         # Source code
│   ├── auth.py         # Authentication
│   ├── cli.py          # CLI entry point
│   ├── converter.py    # Docs→HTML→Markdown
│   ├── google_api.py   # Google Docs API client
│   ├── images.py       # Image downloader
│   ├── models.py       # Data models
│   ├── utils.py        # URL parsing
│   └── writer.py       # File writing
├── tests/              # Test suite (58 tests)
├── SKILL.md            # Claude Code integration
└── README.md           # This file
```

## 🐛 Troubleshooting

See [INSTALLATION.md](INSTALLATION.md) for detailed troubleshooting guides.

**Common issues:**

- **Command not found**: Add `~/.local/bin` to your PATH
- **Auth error**: Run `gcloud auth login --enable-gdrive-access`
- **Module not found**: Install dependencies with pip

## 📝 Requirements

- Python 3.10+
- Google Cloud SDK (gcloud)
- Dependencies: google-api-python-client, google-auth, markdownify

## 🤝 Contributing

Contributions welcome! The codebase is well-tested and documented.

1. Fork the repository
2. Create a feature branch
3. Write tests for your changes
4. Ensure all tests pass
5. Submit a pull request

## 📄 License

MIT License - See LICENSE file for details

## 🙏 Acknowledgments

Built with:
- [google-api-python-client](https://github.com/googleapis/google-api-python-client) - Google Docs API access
- [markdownify](https://github.com/matthewwithanm/python-markdownify) - HTML to Markdown conversion
- [pytest](https://pytest.org/) - Testing framework

---

**Made with ❤️ for seamless Google Docs integration with Claude Code**
