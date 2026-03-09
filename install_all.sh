#!/bin/bash
# Install both gdoc-fetch and gdoc-upload packages
# Supports both pip and uv

set -e

# Detect which package manager to use
if command -v uv &> /dev/null; then
    PM="uv pip"
    echo "Using uv..."
else
    PM="pip"
    echo "Using pip..."
fi

echo "Installing gdoc-fetch and gdoc-upload..."
$PM install -e ./gdoc_fetch -e ./gdoc_upload

echo ""
echo "✓ Installation complete!"
echo ""
echo "Installed packages:"
if command -v uv &> /dev/null; then
    uv pip list | grep gdoc
else
    pip list | grep gdoc
fi

echo ""
echo "CLI commands available:"
echo "  - gdoc-fetch"
echo "  - gdoc-upload"
