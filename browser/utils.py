"""
Browser utility helpers for Voice Browser Agent.
Includes URL normalization, text truncation, and selector fallback chains.
"""

from typing import List
from urllib.parse import urlparse

import config

# ============================================================================
# URL UTILITIES
# ============================================================================

def normalize_url(url: str) -> str:
    """
    Normalize a URL by trimming whitespace and adding scheme if missing.

    Args:
        url: Raw URL input

    Returns:
        Normalized URL string

    Example:
        >>> normalize_url("example.com")
        'https://example.com'
    """
    if not url:
        return ""

    cleaned = url.strip()
    if not cleaned:
        return ""

    parsed = urlparse(cleaned)
    if not parsed.scheme:
        return f"https://{cleaned}"

    return cleaned

# ============================================================================
# TEXT UTILITIES
# ============================================================================

def truncate_text(text: str, max_length: int = None) -> str:
    """
    Truncate text to a maximum length with safe trimming.

    Args:
        text: Input text
        max_length: Maximum length (defaults to config.MAX_PAGE_CONTENT_LENGTH)

    Returns:
        Truncated text
    """
    if text is None:
        return ""

    limit = max_length or config.MAX_PAGE_CONTENT_LENGTH
    if limit <= 0:
        return ""

    if len(text) <= limit:
        return text

    return text[:limit].rstrip()

# ============================================================================
# SELECTOR UTILITIES
# ============================================================================

def build_selector(selector: str) -> List[str]:
    """
    Build a fallback selector chain (CSS -> text -> XPath).

    Args:
        selector: Raw selector string

    Returns:
        List of selector candidates
    """
    if not selector:
        return []

    raw = selector.strip()
    if not raw:
        return []

    # If selector already has a Playwright engine prefix, use it directly.
    lowered = raw.lower()
    if lowered.startswith("css=") or lowered.startswith("text=") or lowered.startswith("xpath="):
        return [raw]

    # Heuristic: treat leading '//' as XPath
    if raw.startswith("//"):
        return [f"xpath={raw}"]

    return [raw, f"text={raw}", f"xpath={raw}"]
