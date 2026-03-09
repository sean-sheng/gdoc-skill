#!/bin/bash
# Install both gdoc-fetch and gdoc-upload in editable mode

set -e

echo "Installing gdoc-fetch..."
pip install -e ./gdoc_fetch

echo "Installing gdoc-upload..."
pip install -e ./gdoc_upload

echo "✓ Installation complete!"
echo ""
echo "Installed packages:"
pip list | grep gdoc
