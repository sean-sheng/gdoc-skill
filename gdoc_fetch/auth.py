"""Authentication using gcloud credentials."""
import subprocess
from typing import Optional


class AuthenticationError(Exception):
    """Raised when authentication fails."""
    pass


def get_access_token() -> str:
    """
    Get Google OAuth access token from gcloud.

    Tries in order:
    1. gcloud auth print-access-token (user account)
    2. gcloud auth application-default print-access-token

    Returns:
        OAuth access token string

    Raises:
        AuthenticationError: If no valid token can be obtained
    """
    token_sources = [
        (['gcloud', 'auth', 'print-access-token'], 'user account'),
        (['gcloud', 'auth', 'application-default', 'print-access-token'], 'application-default'),
    ]

    for cmd, label in token_sources:
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode == 0 and result.stdout.strip():
                return result.stdout.strip()

        except FileNotFoundError:
            raise AuthenticationError(
                "gcloud CLI not found. Install from https://cloud.google.com/sdk"
            )
        except subprocess.TimeoutExpired:
            continue

    raise AuthenticationError(
        "Could not obtain gcloud access token.\n\n"
        "To fix this, run:\n"
        "  gcloud auth login --enable-gdrive-access\n\n"
        "Then retry."
    )
