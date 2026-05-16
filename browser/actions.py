"""
Browser actions module for Voice Browser Agent.
Provides high-level actions for navigation, scraping, clicking, typing, scrolling, and screenshots.
"""

from pathlib import Path
from typing import Optional
import re

from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

try:
    import config
except ModuleNotFoundError:
    import sys
    from pathlib import Path as _Path

    sys.path.insert(0, str(_Path(__file__).resolve().parents[1]))
    import config
from browser.manager import BrowserManager
from browser.utils import normalize_url, truncate_text, build_selector
from utils.logger import (
    log_browser_info,
    log_browser_debug,
    log_browser_warning,
    log_browser_error,
)

# ============================================================================
# BROWSER ACTIONS
# ============================================================================

class BrowserActions:
    """
    High-level browser actions using a shared Playwright page instance.

    Example:
        >>> manager = BrowserManager()
        >>> actions = BrowserActions(manager)
        >>> actions.navigate("https://example.com")
    """

    def __init__(self, manager: Optional[BrowserManager] = None):
        self.manager = manager or BrowserManager()
        self.page = self.manager.get_page()

    def navigate(self, url: str) -> str:
        """
        Navigate to a URL and return the page title.

        Args:
            url: Destination URL

        Returns:
            Page title
        """
        normalized = normalize_url(url)
        if not normalized:
            raise ValueError("URL is empty or invalid")

        log_browser_info(f"Navigating to: {normalized}")
        self.page.goto(normalized)
        self.page.wait_for_load_state("load")
        self._dismiss_common_dialogs()

        title = self.page.title()
        log_browser_debug(f"Page title: {title}")
        return title

    def scrape(self) -> str:
        """
        Extract visible text from the page and truncate to limit.

        Returns:
            Extracted text (possibly truncated)
        """
        log_browser_info("Scraping page text...")

        try:
            raw_text = self.page.evaluate(
                """
                () => {
                    const removeTags = ['script', 'style', 'noscript'];
                    removeTags.forEach(tag => {
                        document.querySelectorAll(tag).forEach(el => el.remove());
                    });
                    const body = document.body;
                    return body ? body.innerText || '' : '';
                }
                """
            )
        except Exception as e:
            log_browser_error(f"Failed to evaluate page text: {e}")
            return ""

        # Collapse whitespace and truncate
        text = re.sub(r"\s+", " ", raw_text).strip()
        text = truncate_text(text)

        log_browser_debug(f"Scrape length: {len(text)} characters")
        return text

    def click(self, selector: str) -> bool:
        """
        Click an element using selector fallbacks and wait for navigation if any.

        Args:
            selector: CSS/text/xpath selector string

        Returns:
            True if click succeeded
        """
        selectors = build_selector(selector)
        if not selectors:
            raise ValueError("Selector is empty")

        last_error = None
        for candidate in selectors:
            try:
                self._dismiss_common_dialogs()
                log_browser_debug(f"Trying selector: {candidate}")
                element = self.page.wait_for_selector(
                    candidate,
                    state="visible",
                    timeout=config.DEFAULT_ACTION_TIMEOUT,
                )
                element.scroll_into_view_if_needed()

                # Attempt click with navigation wait if it happens
                try:
                    with self.page.expect_navigation(wait_until="load", timeout=5000):
                        element.click()
                except PlaywrightTimeoutError:
                    pass

                log_browser_info(f"Clicked: {candidate}")
                return True
            except Exception as e:
                last_error = e
                log_browser_debug(f"Selector failed: {candidate} ({e})")

        log_browser_error(f"Click failed for selector: {selector}")
        if last_error:
            log_browser_error(f"Last error: {last_error}")
        return False

    def type_text(self, selector: str, text: str, delay_ms: int = 20) -> bool:
        """
        Clear a field and type text character-by-character.

        Args:
            selector: CSS/text/xpath selector
            text: Text to type
            delay_ms: Delay per character in milliseconds

        Returns:
            True if typing succeeded
        """
        selectors = build_selector(selector)
        if "name=\"q\"" in selector or "name='q'" in selector or "name=q" in selector:
            selectors = selectors + ["textarea[name=\"q\"]", "[name=\"q\"]"]
        if not selectors:
            raise ValueError("Selector is empty")

        last_error = None
        for candidate in selectors:
            try:
                self._dismiss_common_dialogs()
                log_browser_debug(f"Trying selector: {candidate}")
                element = self.page.wait_for_selector(
                    candidate,
                    state="visible",
                    timeout=config.DEFAULT_ACTION_TIMEOUT,
                )
                element.scroll_into_view_if_needed()
                element.click()

                # Clear existing text
                try:
                    element.fill("")
                except Exception:
                    pass

                element.type(text, delay=delay_ms)

                # Submit common search inputs with Enter when appropriate.
                if "name=\"q\"" in candidate or "name='q'" in candidate or "name=q" in candidate:
                    self.page.keyboard.press("Enter")
                log_browser_info(f"Typed into: {candidate}")
                return True
            except Exception as e:
                last_error = e
                log_browser_debug(f"Selector failed: {candidate} ({e})")

        log_browser_error(f"Type failed for selector: {selector}")
        if last_error:
            log_browser_error(f"Last error: {last_error}")
        return False

    def scroll(self, direction: str = "down", amount: int = 500) -> None:
        """
        Scroll the page using window.scrollBy.

        Args:
            direction: "up" or "down"
            amount: Pixel amount to scroll
        """
        if amount <= 0:
            return

        delta = amount if direction.lower() == "down" else -amount
        log_browser_info(f"Scrolling {direction} by {amount}px")

        self.page.evaluate("(dy) => window.scrollBy(0, dy)", delta)

    def screenshot(self, path: str) -> str:
        """
        Take a screenshot and save it under the screenshots directory.

        Args:
            path: File path or filename

        Returns:
            Saved screenshot path
        """
        if not path:
            raise ValueError("Screenshot path is required")

        target = Path(path)
        if not target.is_absolute():
            target = Path(config.SCREENSHOTS_DIR) / target

        target.parent.mkdir(parents=True, exist_ok=True)

        self.page.screenshot(path=str(target))
        log_browser_info(f"Screenshot saved: {target}")
        return str(target)

    def _dismiss_common_dialogs(self) -> None:
        """Best-effort click for common consent/popups."""
        candidates = [
            "Accept all",
            "Accept all cookies",
            "I agree",
            "I Agree",
            "Accept",
            "Agree",
            "Got it",
        ]

        for text in candidates:
            try:
                element = self.page.wait_for_selector(
                    f"text={text}",
                    state="visible",
                    timeout=800,
                )
                element.click()
                log_browser_info(f"Dismissed dialog: {text}")
                break
            except Exception:
                continue

# ============================================================================
# TESTING / DEMO
# ============================================================================

if __name__ == "__main__":
    """Demo the browser actions."""
    print("\n" + "=" * 70)
    print("BROWSER ACTIONS DEMO")
    print("=" * 70)

    manager = BrowserManager()
    actions = BrowserActions(manager)

    try:
        actions.navigate("https://example.com")
        text = actions.scrape()
        print(f"Scraped text (truncated): {text[:200]}")
        actions.screenshot("example.png")
    finally:
        manager.close()
