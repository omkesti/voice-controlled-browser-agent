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

    # Models sometimes copy the inspect output verbatim, e.g.
    #   '- [input] "Search" -> #sb_form_q'  or  '-> #sb_form_q'
    # Keep only the real selector after the last '->' arrow.
    if "->" in raw:
        raw = raw.rsplit("->", 1)[-1].strip()
    # Strip a stray leading list dash if one survived.
    raw = raw.lstrip("- ").strip()
    if not raw:
        return []

    # If selector already has a Playwright engine prefix, use it directly.
    lowered = raw.lower()
    if lowered.startswith("css=") or lowered.startswith("text=") or lowered.startswith("xpath="):
        return [raw]

    # Heuristic: treat leading '//' or '(' as XPath.
    if raw.startswith("//") or raw.startswith("(//") or raw.startswith(".."):
        return [f"xpath={raw}"]

    # Only add a text= fallback for plain text (no CSS syntax). Wrapping a
    # real CSS selector like "[data-testid='x']" as xpath=/text= produces an
    # invalid XPath expression (DOMException) and a never-matching text query,
    # so we avoid those variants entirely for CSS-looking selectors.
    css_syntax = set("#.[]>+~*=:() ")
    looks_like_css = any(ch in raw for ch in css_syntax)

    if looks_like_css:
        return [raw]

    # Plain text: try it as a CSS type selector first, then as a text match.
    return [raw, f"text={raw}"]
