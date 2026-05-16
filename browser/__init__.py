"""
Browser module for Voice Browser Agent.
Handles browser lifecycle management and automation actions via Playwright.
"""

from .manager import BrowserManager
from .actions import BrowserActions
from .utils import truncate_page_content, build_selector, normalize_url

__all__ = [
    "BrowserManager",
    "BrowserActions",
    "truncate_page_content",
    "build_selector",
    "normalize_url",
]
