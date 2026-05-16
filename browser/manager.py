"""
Browser manager module for Voice Browser Agent.
Manages Playwright browser lifecycle with singleton page instance.
"""

from typing import Optional
import asyncio
from playwright.sync_api import sync_playwright, Browser, BrowserContext, Page, Playwright

import config
from utils.logger import (
    log_browser_info,
    log_browser_debug,
    log_browser_warning,
    log_browser_error,
)

# ============================================================================
# BROWSER MANAGER
# ============================================================================

class BrowserManager:
    """
    Manages Playwright browser lifecycle with singleton pattern.
    
    Features:
    - Singleton page instance shared across all browser actions
    - Configurable browser type (chromium, firefox, webkit)
    - Headless or visible mode
    - Custom viewport size
    - User agent override
    - Automatic timeout configuration
    - Clean shutdown handling
    
    Example:
        >>> manager = BrowserManager()
        >>> page = manager.get_page()
        >>> page.goto("https://example.com")
        >>> manager.close()
    """
    
    def __init__(
        self,
        browser_type: Optional[str] = None,
        headless: Optional[bool] = None,
        viewport_width: Optional[int] = None,
        viewport_height: Optional[int] = None,
        user_agent: Optional[str] = None,
        timeout: Optional[int] = None,
        slow_mo: Optional[int] = None,
        devtools: Optional[bool] = None,
    ):
        """
        Initialize the BrowserManager.
        
        Args:
            browser_type: Browser type ('chromium', 'firefox', 'webkit')
            headless: Run in headless mode
            viewport_width: Browser window width
            viewport_height: Browser window height
            user_agent: Custom user agent string
            timeout: Default timeout in milliseconds
            slow_mo: Slow down operations by N milliseconds (for debugging)
            devtools: Open DevTools on launch
        """
        # Configuration
        self.browser_type = browser_type or config.BROWSER_TYPE
        self.headless = headless if headless is not None else config.HEADLESS
        self.viewport_width = viewport_width or config.VIEWPORT_WIDTH
        self.viewport_height = viewport_height or config.VIEWPORT_HEIGHT
        self.user_agent = user_agent or config.USER_AGENT
        self.timeout = timeout or config.BROWSER_TIMEOUT
        self.slow_mo = slow_mo if slow_mo is not None else config.SLOW_MO
        self.devtools = devtools if devtools is not None else config.DEVTOOLS
        
        # Playwright instances (initialized on first use)
        self._playwright: Optional[Playwright] = None
        self._browser: Optional[Browser] = None
        self._context: Optional[BrowserContext] = None
        self._page: Optional[Page] = None
        
        # State tracking
        self._is_launched = False
        self._is_closed = False
        
        log_browser_debug("BrowserManager initialized")
        log_browser_debug(f"  Browser type: {self.browser_type}")
        log_browser_debug(f"  Headless: {self.headless}")
        log_browser_debug(f"  Viewport: {self.viewport_width}x{self.viewport_height}")
        if self.user_agent:
            log_browser_debug(f"  User agent: {self.user_agent[:50]}...")
        if self.slow_mo > 0:
            log_browser_debug(f"  Slow-mo: {self.slow_mo}ms")
        if self.devtools:
            log_browser_debug(f"  DevTools: enabled")
    
    def launch(self) -> Page:
        """
        Launch the browser and return the page instance.
        
        Creates Playwright instance, browser, context, and page.
        Subsequent calls return the existing page.
        
        Returns:
            Playwright Page instance
        
        Raises:
            RuntimeError: If browser launch fails
        """
        if self._is_closed:
            raise RuntimeError("BrowserManager has been closed. Create a new instance.")
        
        if self._is_launched and self._page:
            log_browser_debug("Reusing existing browser page")
            return self._page
        
        log_browser_info("🌐 Launching browser...")
        
        try:
            # Playwright sync API cannot run inside an active asyncio loop.
            # If a loop is running (e.g., in notebooks), create a fresh one.
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    log_browser_warning(
                        "Detected running asyncio loop; creating a new event loop for Playwright"
                    )
                    asyncio.set_event_loop(asyncio.new_event_loop())
            except RuntimeError:
                asyncio.set_event_loop(asyncio.new_event_loop())

            # Start Playwright
            log_browser_debug("Starting Playwright...")
            self._playwright = sync_playwright().start()
            
            # Get browser launcher
            if self.browser_type == "chromium":
                browser_launcher = self._playwright.chromium
            elif self.browser_type == "firefox":
                browser_launcher = self._playwright.firefox
            elif self.browser_type == "webkit":
                browser_launcher = self._playwright.webkit
            else:
                log_browser_error(f"Unknown browser type: {self.browser_type}")
                raise ValueError(f"Unknown browser type: {self.browser_type}")
            
            # Launch browser
            log_browser_debug(f"Launching {self.browser_type}...")
            launch_options = {
                "headless": self.headless,
                "timeout": self.timeout,
            }
            
            if self.slow_mo > 0:
                launch_options["slow_mo"] = self.slow_mo
            
            if self.devtools:
                launch_options["devtools"] = self.devtools
            
            self._browser = browser_launcher.launch(**launch_options)
            
            # Create context
            log_browser_debug("Creating browser context...")
            context_options = {
                "viewport": {
                    "width": self.viewport_width,
                    "height": self.viewport_height,
                },
            }
            
            if self.user_agent:
                context_options["user_agent"] = self.user_agent
            
            self._context = self._browser.new_context(**context_options)
            
            # Set default timeouts
            self._context.set_default_navigation_timeout(config.DEFAULT_NAVIGATION_TIMEOUT)
            self._context.set_default_timeout(config.DEFAULT_ACTION_TIMEOUT)
            
            # Create page
            log_browser_debug("Creating page...")
            self._page = self._context.new_page()
            
            self._is_launched = True
            
            log_browser_info(f"✓ Browser launched: {self.browser_type}")
            log_browser_debug(f"  Headless: {self.headless}")
            log_browser_debug(f"  Viewport: {self.viewport_width}x{self.viewport_height}")
            log_browser_debug(f"  Navigation timeout: {config.DEFAULT_NAVIGATION_TIMEOUT}ms")
            log_browser_debug(f"  Action timeout: {config.DEFAULT_ACTION_TIMEOUT}ms")
            
            return self._page
            
        except Exception as e:
            log_browser_error(f"Failed to launch browser: {e}")
            self._cleanup()
            raise RuntimeError(f"Could not launch browser: {e}")
    
    def get_page(self) -> Page:
        """
        Get the singleton page instance.
        
        Launches browser if not already launched.
        
        Returns:
            Playwright Page instance
        
        Example:
            >>> manager = BrowserManager()
            >>> page = manager.get_page()
            >>> page.goto("https://example.com")
        """
        if not self._is_launched or not self._page:
            return self.launch()
        return self._page
    
    def is_launched(self) -> bool:
        """
        Check if browser is launched.
        
        Returns:
            True if browser is running
        """
        return self._is_launched and self._page is not None
    
    def reset(self) -> Page:
        """
        Reset the browser context and page.
        
        Useful for recovering from errors or clearing state.
        Closes existing context/page and creates new ones.
        
        Returns:
            New Page instance
        
        Example:
            >>> manager = BrowserManager()
            >>> page = manager.get_page()
            >>> # ... some error occurs ...
            >>> page = manager.reset()  # Fresh start
        """
        if not self._browser:
            log_browser_warning("Cannot reset: browser not launched")
            return self.launch()
        
        log_browser_info("Resetting browser context...")
        
        try:
            # Close existing context and page
            if self._page:
                self._page.close()
                self._page = None
            
            if self._context:
                self._context.close()
                self._context = None
            
            # Create new context and page
            log_browser_debug("Creating new context...")
            context_options = {
                "viewport": {
                    "width": self.viewport_width,
                    "height": self.viewport_height,
                },
            }
            
            if self.user_agent:
                context_options["user_agent"] = self.user_agent
            
            self._context = self._browser.new_context(**context_options)
            self._context.set_default_navigation_timeout(config.DEFAULT_NAVIGATION_TIMEOUT)
            self._context.set_default_timeout(config.DEFAULT_ACTION_TIMEOUT)
            
            self._page = self._context.new_page()
            
            log_browser_info("✓ Browser context reset")
            return self._page
            
        except Exception as e:
            log_browser_error(f"Failed to reset browser: {e}")
            raise RuntimeError(f"Could not reset browser: {e}")
    
    def close(self):
        """
        Close the browser and clean up resources.
        
        Closes page, context, browser, and stops Playwright in correct order.
        Safe to call multiple times.
        
        Example:
            >>> manager = BrowserManager()
            >>> page = manager.get_page()
            >>> # ... use browser ...
            >>> manager.close()
        """
        if self._is_closed:
            log_browser_debug("Browser already closed")
            return
        
        log_browser_info("Closing browser...")
        
        self._cleanup()
        self._is_closed = True
        
        log_browser_info("✓ Browser closed")
    
    def _cleanup(self):
        """Internal cleanup method."""
        try:
            # Close page
            if self._page:
                log_browser_debug("Closing page...")
                self._page.close()
                self._page = None
            
            # Close context
            if self._context:
                log_browser_debug("Closing context...")
                self._context.close()
                self._context = None
            
            # Close browser
            if self._browser:
                log_browser_debug("Closing browser...")
                self._browser.close()
                self._browser = None
            
            # Stop Playwright
            if self._playwright:
                log_browser_debug("Stopping Playwright...")
                self._playwright.stop()
                self._playwright = None
            
            self._is_launched = False
            
        except Exception as e:
            log_browser_warning(f"Error during cleanup: {e}")
    
    def __enter__(self):
        """Context manager entry."""
        self.launch()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
    
    def __del__(self):
        """Destructor to ensure cleanup."""
        if not self._is_closed:
            self.close()

# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================

def create_browser() -> BrowserManager:
    """
    Create a browser manager with default settings.
    
    Returns:
        BrowserManager instance
    
    Example:
        >>> manager = create_browser()
        >>> page = manager.get_page()
    """
    return BrowserManager()

# ============================================================================
# TESTING / DEMO
# ============================================================================

if __name__ == "__main__":
    """Demo the browser manager."""
    import sys
    
    print("\n" + "=" * 70)
    print("BROWSER MANAGER DEMO")
    print("=" * 70)
    print("\nThis will:")
    print("1. Launch a Chromium browser")
    print("2. Navigate to example.com")
    print("3. Get the page title")
    print("4. Close the browser")
    print("\nPress Ctrl+C to cancel.\n")
    
    try:
        # Create manager
        manager = BrowserManager()
        
        # Get page
        page = manager.get_page()
        
        # Navigate
        print("\nNavigating to https://example.com...")
        page.goto("https://example.com")
        
        # Get title
        title = page.title()
        print(f"Page title: {title}")
        
        # Get user agent
        user_agent = page.evaluate("navigator.userAgent")
        print(f"User agent: {user_agent}")
        
        # Wait a bit
        print("\nBrowser will close in 3 seconds...")
        page.wait_for_timeout(3000)
        
        # Close
        manager.close()
        
        print("\n" + "=" * 70)
        print("Demo complete!")
        print("=" * 70 + "\n")
        
    except KeyboardInterrupt:
        print("\n\nDemo cancelled by user.")
        if 'manager' in locals():
            manager.close()
        sys.exit(0)
    except Exception as e:
        print(f"\n\nError: {e}")
        if 'manager' in locals():
            manager.close()
        import traceback
        traceback.print_exc()
        sys.exit(1)
