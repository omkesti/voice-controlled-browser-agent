"""
Browser module for Voice Browser Agent.
Handles browser lifecycle management and automation actions via Playwright.
"""

# Lazy imports to avoid loading all dependencies at once
def __getattr__(name):
    if name == "BrowserManager":
        from .manager import BrowserManager
        return BrowserManager
    elif name == "create_browser":
        from .manager import create_browser
        return create_browser
    elif name == "BrowserActions":
        from .actions import BrowserActions
        return BrowserActions
    elif name == "truncate_text":
        from .utils import truncate_text
        return truncate_text
    elif name == "build_selector":
        from .utils import build_selector
        return build_selector
    elif name == "normalize_url":
        from .utils import normalize_url
        return normalize_url
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")

__all__ = [
    "BrowserManager",
    "create_browser",
    "BrowserActions",
    "truncate_text",
    "build_selector",
    "normalize_url",
]
