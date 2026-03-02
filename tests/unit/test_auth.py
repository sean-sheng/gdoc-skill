"""Tests for authentication module."""
import subprocess
from unittest.mock import patch, MagicMock
import pytest
from gdoc_fetch.auth import get_access_token, AuthenticationError


def test_get_access_token_from_user_account(mocker):
    """Test successful token retrieval from gcloud user account."""
    mock_run = mocker.patch('subprocess.run')
    mock_run.return_value = MagicMock(
        returncode=0,
        stdout='ya29.test-token-here\n',
        stderr=''
    )

    token = get_access_token()

    assert token == 'ya29.test-token-here'
    mock_run.assert_called_once_with(
        ['gcloud', 'auth', 'print-access-token'],
        capture_output=True,
        text=True,
        timeout=10
    )


def test_get_access_token_fallback_to_app_default(mocker):
    """Test fallback to application-default credentials."""
    mock_run = mocker.patch('subprocess.run')
    # First call fails, second succeeds
    mock_run.side_effect = [
        MagicMock(returncode=1, stdout='', stderr='not logged in'),
        MagicMock(returncode=0, stdout='ya29.app-default-token\n', stderr='')
    ]

    token = get_access_token()

    assert token == 'ya29.app-default-token'
    assert mock_run.call_count == 2


def test_get_access_token_no_credentials(mocker):
    """Test error when no credentials available."""
    mock_run = mocker.patch('subprocess.run')
    mock_run.side_effect = [
        MagicMock(returncode=1, stdout='', stderr='not logged in'),
        MagicMock(returncode=1, stdout='', stderr='not configured')
    ]

    with pytest.raises(AuthenticationError) as exc:
        get_access_token()

    assert 'gcloud auth login --enable-gdrive-access' in str(exc.value)


def test_get_access_token_gcloud_not_found(mocker):
    """Test error when gcloud CLI not installed."""
    mock_run = mocker.patch('subprocess.run')
    mock_run.side_effect = FileNotFoundError()

    with pytest.raises(AuthenticationError) as exc:
        get_access_token()

    assert 'gcloud CLI not found' in str(exc.value)
