"""
Test script for the BrowserManager.
Run with: python test_browser_manager.py
"""

import sys
from browser import BrowserManager
from utils import log_header, log_system_info, log_success, log_error

def test_basic_launch():
    """Test basic browser launch and navigation."""
    
    log_header("BROWSER MANAGER TEST - Basic Launch")
    
    log_system_info("Testing browser launch and navigation...")
    log_system_info("")
    
    manager = None
    try:
        # Create manager
        log_system_info("Creating BrowserManager...")
        manager = BrowserManager()
        
        # Get page
        log_system_info("Getting page...")
        page = manager.get_page()
        log_success("Browser launched successfully", "SYSTEM")
        log_system_info("")
        
        # Navigate to example.com
        log_system_info("Navigating to https://example.com...")
        page.goto("https://example.com")
        log_success("Navigation successful", "SYSTEM")
        log_system_info("")
        
        # Get page info
        title = page.title()
        url = page.url
        
        log_system_info(f"📄 Page title: {title}")
        log_system_info(f"🔗 URL: {url}")
        log_system_info("")
        
        # Get user agent
        user_agent = page.evaluate("navigator.userAgent")
        log_system_info(f"🤖 User agent: {user_agent}")
        log_system_info("")
        
        # Get viewport
        viewport = page.viewport_size
        log_system_info(f"📐 Viewport: {viewport['width']}x{viewport['height']}")
        log_system_info("")
        
        log_success("Basic launch test passed!", "SYSTEM")
        
    except Exception as e:
        log_error(f"Test failed: {e}", "SYSTEM")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        if manager:
            manager.close()

def test_multiple_navigations():
    """Test multiple page navigations."""
    
    log_header("BROWSER MANAGER TEST - Multiple Navigations")
    
    log_system_info("Testing multiple page navigations...")
    log_system_info("")
    
    manager = None
    try:
        manager = BrowserManager()
        page = manager.get_page()
        
        # Navigate to multiple sites
        sites = [
            "https://example.com",
            "https://example.org",
            "https://example.net",
        ]
        
        for i, site in enumerate(sites, 1):
            log_system_info(f"Navigation {i}/{len(sites)}: {site}")
            page.goto(site)
            title = page.title()
            log_system_info(f"  Title: {title}")
            log_system_info("")
        
        log_success("Multiple navigations test passed!", "SYSTEM")
        
    except Exception as e:
        log_error(f"Test failed: {e}", "SYSTEM")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        if manager:
            manager.close()

def test_context_manager():
    """Test context manager usage."""
    
    log_header("BROWSER MANAGER TEST - Context Manager")
    
    log_system_info("Testing context manager (with statement)...")
    log_system_info("")
    
    try:
        with BrowserManager() as manager:
            page = manager.get_page()
            
            log_system_info("Navigating to https://example.com...")
            page.goto("https://example.com")
            
            title = page.title()
            log_system_info(f"Page title: {title}")
            log_system_info("")
        
        log_success("Context manager test passed!", "SYSTEM")
        log_system_info("(Browser automatically closed)")
        
    except Exception as e:
        log_error(f"Test failed: {e}", "SYSTEM")
        import traceback
        traceback.print_exc()
        sys.exit(1)

def test_reset():
    """Test browser context reset."""
    
    log_header("BROWSER MANAGER TEST - Context Reset")
    
    log_system_info("Testing browser context reset...")
    log_system_info("")
    
    manager = None
    try:
        manager = BrowserManager()
        page = manager.get_page()
        
        # Navigate to first site
        log_system_info("First navigation: https://example.com")
        page.goto("https://example.com")
        title1 = page.title()
        log_system_info(f"  Title: {title1}")
        log_system_info("")
        
        # Reset context
        log_system_info("Resetting browser context...")
        page = manager.reset()
        log_success("Context reset successful", "SYSTEM")
        log_system_info("")
        
        # Navigate to second site
        log_system_info("Second navigation: https://example.org")
        page.goto("https://example.org")
        title2 = page.title()
        log_system_info(f"  Title: {title2}")
        log_system_info("")
        
        log_success("Reset test passed!", "SYSTEM")
        
    except Exception as e:
        log_error(f"Test failed: {e}", "SYSTEM")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        if manager:
            manager.close()

def test_user_agent_override():
    """Test custom user agent."""
    
    log_header("BROWSER MANAGER TEST - User Agent Override")
    
    log_system_info("Testing custom user agent...")
    log_system_info("")
    
    custom_ua = "Mozilla/5.0 (CustomBot/1.0)"
    
    manager = None
    try:
        manager = BrowserManager(user_agent=custom_ua)
        page = manager.get_page()
        
        page.goto("https://example.com")
        
        # Get user agent from page
        actual_ua = page.evaluate("navigator.userAgent")
        
        log_system_info(f"Expected UA: {custom_ua}")
        log_system_info(f"Actual UA:   {actual_ua}")
        log_system_info("")
        
        if actual_ua == custom_ua:
            log_success("User agent override test passed!", "SYSTEM")
        else:
            log_error("User agent mismatch!", "SYSTEM")
        
    except Exception as e:
        log_error(f"Test failed: {e}", "SYSTEM")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        if manager:
            manager.close()

def main():
    """Run all tests."""
    
    if len(sys.argv) > 1:
        test_name = sys.argv[1]
        
        if test_name == "basic":
            test_basic_launch()
        elif test_name == "multiple":
            test_multiple_navigations()
        elif test_name == "context":
            test_context_manager()
        elif test_name == "reset":
            test_reset()
        elif test_name == "useragent":
            test_user_agent_override()
        else:
            print(f"Unknown test: {test_name}")
            print("Available tests: basic, multiple, context, reset, useragent")
            sys.exit(1)
    else:
        # Run all tests
        test_basic_launch()
        print()
        test_multiple_navigations()
        print()
        test_context_manager()
        print()
        test_reset()
        print()
        test_user_agent_override()
        print()
        log_header("ALL TESTS COMPLETE")

if __name__ == "__main__":
    main()
