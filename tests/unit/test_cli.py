"""Tests for CLI module."""
import sys
from unittest.mock import patch
import pytest
from gdoc_fetch.cli import parse_args


def test_parse_args_with_url():
    """Test parsing URL argument."""
    with patch.object(sys, 'argv', ['gdoc-fetch', 'https://docs.google.com/document/d/123/edit']):
        args = parse_args()
        assert args.url == 'https://docs.google.com/document/d/123/edit'
        assert args.output_dir == './output'


def test_parse_args_with_output_dir():
    """Test parsing custom output directory."""
    with patch.object(sys, 'argv', ['gdoc-fetch', 'doc123', '--output-dir', '/tmp/docs']):
        args = parse_args()
        assert args.url == 'doc123'
        assert args.output_dir == '/tmp/docs'


def test_parse_args_with_no_images():
    """Test --no-images flag."""
    with patch.object(sys, 'argv', ['gdoc-fetch', 'doc123', '--no-images']):
        args = parse_args()
        assert args.no_images is True


def test_parse_args_missing_url():
    """Test error when URL is missing."""
    with patch.object(sys, 'argv', ['gdoc-fetch']):
        with pytest.raises(SystemExit):
            parse_args()
