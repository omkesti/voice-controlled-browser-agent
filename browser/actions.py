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
from browser.selector_cache import SelectorCache, domain_of
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
        self.selector_cache = SelectorCache()

    def _build_candidates(self, selector, label, extra=None):
        """
        Build the ordered selector candidate list for an interaction.

        Tier-3 self-healing: a cached working selector for (domain, label) is
        tried FIRST, then the LLM-provided selector's fallback chain, then any
        action-specific extras. Returns (domain, candidates).
        """
        domain = domain_of(getattr(self.page, "url", "") or "")
        candidates = []

        if label:
            cached = self.selector_cache.get(domain, label)
            if cached:
                candidates.append(cached)
                log_browser_debug(f"Cache hit '{label}'@{domain}: {cached}")

        for s in build_selector(selector):
            if s not in candidates:
                candidates.append(s)
        for s in extra or []:
            if s not in candidates:
                candidates.append(s)

        return domain, candidates

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

    def search(self, query: str) -> str:
        """
        Answer a query via web-search APIs (currency, instant answers, Tavily).

        Search engines serve CAPTCHAs to automated browsers, so this routes
        through structured APIs instead of scraping a results page. See
        agent.web_search for the source order. Returns text for the LLM.

        Args:
            query: The search query string.

        Returns:
            Answer text, or a "no_result" marker if nothing was found.
        """
        if not query or not query.strip():
            raise ValueError("Search query is empty")

        # Imported here to keep the browser layer importable without requests.
        from agent.web_search import run as web_search_run

        answer = web_search_run(query)
        # Show the result in the (otherwise idle) browser window so the user
        # sees the answer, not a blank page, when a query is answered via API.
        self._render_answer(query, answer)
        return answer

    def _render_answer(self, query: str, answer: str) -> None:
        """Render a query/answer card into the visible browser page."""
        import html

        q = html.escape(query or "")
        a = html.escape(answer or "")
        try:
            self.page.set_content(
                f"""<!doctype html><html><head><meta charset="utf-8">
                <title>{q}</title></head>
                <body style="margin:0;font-family:Segoe UI,Roboto,Arial,sans-serif;
                background:#0f172a;color:#e2e8f0;display:flex;align-items:center;
                justify-content:center;min-height:100vh;">
                <div style="max-width:760px;padding:48px;">
                <div style="font-size:14px;letter-spacing:.1em;text-transform:uppercase;
                color:#38bdf8;margin-bottom:12px;">Search</div>
                <div style="font-size:24px;font-weight:600;margin-bottom:24px;">{q}</div>
                <div style="font-size:32px;line-height:1.4;white-space:pre-wrap;">{a}</div>
                </div></body></html>"""
            )
        except Exception as e:
            log_browser_warning(f"Could not render answer in browser: {e}")

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

    def click(self, selector: str, label: Optional[str] = None) -> bool:
        """
        Click an element using selector fallbacks and wait for navigation if any.

        Args:
            selector: CSS/text/xpath selector string
            label: Optional short stable name for this element (e.g. "play button")
                   used to cache/reuse the working selector across calls and runs.

        Returns:
            True if click succeeded
        """
        domain, selectors = self._build_candidates(selector, label)
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
                if label:
                    self.selector_cache.put(domain, label, candidate)
                return True
            except Exception as e:
                last_error = e
                log_browser_debug(f"Selector failed: {candidate} ({e})")

        # Cached selector led the list and everything failed: drop the stale entry.
        if label:
            self.selector_cache.invalidate(domain, label)
        log_browser_error(f"Click failed for selector: {selector}")
        if last_error:
            log_browser_error(f"Last error: {last_error}")
        return False

    def type_text(self, selector: str, text: str, delay_ms: int = 20, label: Optional[str] = None) -> bool:
        """
        Clear a field and type text character-by-character.

        Args:
            selector: CSS/text/xpath selector
            text: Text to type
            delay_ms: Delay per character in milliseconds
            label: Optional short stable name for this field (e.g. "search box")
                   used to cache/reuse the working selector across calls and runs.

        Returns:
            True if typing succeeded
        """
        extra = []
        if "name=\"q\"" in selector or "name='q'" in selector or "name=q" in selector:
            extra = ["textarea[name=\"q\"]", "[name=\"q\"]"]
        domain, selectors = self._build_candidates(selector, label, extra)
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
                if label:
                    self.selector_cache.put(domain, label, candidate)
                return True
            except Exception as e:
                last_error = e
                log_browser_debug(f"Selector failed: {candidate} ({e})")

        if label:
            self.selector_cache.invalidate(domain, label)
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

    def inspect(self, max_elements: int = 40) -> str:
        """
        List visible, interactive elements on the page with ready-to-use selectors.

        Lets the agent pick real selectors instead of guessing. Prefers stable
        attributes (data-testid, id, aria-label, placeholder) and falls back to
        text= for buttons/links. Returns a compact newline-separated list.

        Args:
            max_elements: Maximum number of elements to return.

        Returns:
            Formatted list like: '- [button] "Play" -> [data-testid="play-button"]'
        """
        log_browser_info("Inspecting page for interactive elements...")

        self._dismiss_common_dialogs()
        try:
            # Let SPA content settle briefly (search results, etc.).
            self.page.wait_for_load_state("domcontentloaded")
            self.page.wait_for_timeout(800)
        except Exception:
            pass

        try:
            elements = self.page.evaluate(
                """
                (max) => {
                    const sel = 'a, button, input, textarea, select, [role="button"], [role="link"], [role="textbox"], [data-testid], [contenteditable="true"]';
                    const nodes = Array.from(document.querySelectorAll(sel));
                    const out = [];
                    const seen = new Set();
                    const cssEscape = (window.CSS && CSS.escape) ? CSS.escape : (s) => s.replace(/[^a-zA-Z0-9_-]/g, '\\\\$&');
                    for (const el of nodes) {
                        if (out.length >= max) break;
                        const rect = el.getBoundingClientRect();
                        if (rect.width === 0 || rect.height === 0) continue;
                        const style = window.getComputedStyle(el);
                        if (style.visibility === 'hidden' || style.display === 'none' || style.opacity === '0') continue;

                        const tag = el.tagName.toLowerCase();
                        const testid = el.getAttribute('data-testid');
                        const aria = el.getAttribute('aria-label');
                        const ph = el.getAttribute('placeholder');
                        const id = el.id;
                        let selector = null;
                        if (testid) selector = `[data-testid="${testid}"]`;
                        else if (id) selector = `#${cssEscape(id)}`;
                        else if (ph) selector = `[placeholder="${ph}"]`;
                        else if (aria) selector = `[aria-label="${aria}"]`;

                        let text = (el.innerText || el.value || aria || ph || '').trim().replace(/\\s+/g, ' ').slice(0, 60);
                        if (!selector) {
                            if (text && (tag === 'button' || tag === 'a')) selector = `text=${text}`;
                            else continue;
                        }
                        const key = selector + '|' + text;
                        if (seen.has(key)) continue;
                        seen.add(key);
                        out.push({ tag, text, selector });
                    }
                    return out;
                }
                """,
                max_elements,
            )
        except Exception as e:
            log_browser_error(f"Inspect failed: {e}")
            return "error: could not inspect page"

        if not elements:
            return "No interactive elements found."

        lines = []
        for el in elements:
            text = el.get("text") or ""
            lines.append(f'- [{el.get("tag")}] "{text}" -> {el.get("selector")}')

        result = "\n".join(lines)
        log_browser_debug(f"Inspect found {len(elements)} elements")
        return truncate_text(result)

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
