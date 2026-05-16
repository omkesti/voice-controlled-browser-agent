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
    # Future imports
    # elif name == "BrowserActions":
    #     from .actions import BrowserActions
    #     return BrowserActions
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")

__all__ = [
    "BrowserManager",
    "create_browser",
    # "BrowserActions",  # Future
]
