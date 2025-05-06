"""URL handling utilities."""

import requests
from typing import Optional


def shorten_url(url: str) -> Optional[str]:
    """Shorten a URL using TinyURL service."""
    try:
        response = requests.get(f'http://tinyurl.com/api-create.php?url={url}')
        if response.status_code == 200:
            return response.text
        return None
    except Exception as e:
        print(f"Error shortening URL: {e}")
        return None


def format_url_button(url: str, language: str = "en") -> str:
    """Format a URL for display in a button."""
    # Shorten the URL
    short_url = shorten_url(url)
    if short_url:
        return short_url
    return url[:30] + "..."  # Fallback to truncated URL if shortening fails
