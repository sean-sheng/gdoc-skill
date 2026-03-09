#!/bin/bash
# Install both gdoc-fetch and gdoc-upload in editable mode using uv

set -e

echo "Installing gdoc-fetch..."
uv pip install -e ./gdoc_fetch

echo "Installing gdoc-upload..."
uv pip install -e ./gdoc_upload

echo "✓ Installation complete!"
echo ""
echo "Installed packages:"
uv pip list | grep gdoc
