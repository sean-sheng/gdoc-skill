# Development Installation

This project consists of two separate packages:
- `gdoc-fetch` - Fetch Google Docs to Markdown
- `gdoc-upload` - Upload Markdown to Google Docs

## Quick Install

Install both packages in editable mode with one command:

```bash
./install_all.sh
```

This script auto-detects whether you have `uv` or `pip` and installs both packages.

## Manual Installation

### Using pip (Recommended)
```bash
pip install -e ./gdoc_fetch -e ./gdoc_upload
```

This creates proper console scripts that work from anywhere.

### Using uv
```bash
uv pip install -e ./gdoc_fetch -e ./gdoc_upload
```

**Note:** `uv` doesn't create console scripts for editable installs. Use one of these alternatives:

**Option 1:** Run as Python modules:
```bash
python -m gdoc_fetch.cli --help
python -m gdoc_upload.cli --help
```

**Option 2:** Use the wrapper scripts directly:
```bash
./gdoc_fetch/bin/gdoc-fetch --help
./gdoc_upload/bin/gdoc-upload --help
```

**Option 3:** Add wrapper scripts to your PATH:
```bash
export PATH="$PATH:$(pwd)/gdoc_fetch/bin:$(pwd)/gdoc_upload/bin"
```

## Verification

After installation, you should have:

✅ Two packages installed:
```bash
pip list | grep gdoc
# Output:
# gdoc-fetch               0.1.0
# gdoc-upload              0.1.0
```

✅ Two CLI commands available (with pip):
```bash
which gdoc-fetch
which gdoc-upload
```

✅ All modules importable:
```python
import gdoc_fetch
import gdoc_upload
import gdoc_common
```

## Package Structure

```
gdoc-skill/
├── gdoc_common/           # Shared code for both packages
├── gdoc_fetch/            # Fetch package
│   ├── bin/
│   │   └── gdoc-fetch    # Wrapper script (for uv users)
│   └── pyproject.toml
├── gdoc_upload/           # Upload package
│   ├── bin/
│   │   └── gdoc-upload   # Wrapper script (for uv users)
│   └── pyproject.toml
├── install_all.sh         # Universal install script
└── pyproject.toml         # Root pytest configuration only
```

Each package (`gdoc_fetch` and `gdoc_upload`) includes `gdoc_common` in its distribution, so both packages work independently.
