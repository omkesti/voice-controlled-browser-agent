"""
Tool dispatcher for Voice Browser Agent.
Maps tool names to browser action methods.
"""

from typing import Any, Callable, Dict, Optional

from browser.actions import BrowserActions
from utils.logger import log_browser_warning, log_browser_error, log_browser_debug


class ToolDispatcher:
    """
    Dispatch tool calls to BrowserActions and normalize results to strings.
    """

    def __init__(self, actions: Optional[BrowserActions] = None) -> None:
        self.actions = actions or BrowserActions()
        self._tool_map: Dict[str, Callable[..., Any]] = {
            "navigate": self.actions.navigate,
            "search": self.actions.search,
            "click": self.actions.click,
            "type_text": self.actions.type_text,
            "scroll": self.actions.scroll,
            "screenshot": self.actions.screenshot,
            "scrape": self.actions.scrape,
            "inspect": self.actions.inspect,
            "done": self._done,
        }

    def dispatch(self, tool_name: str, args: Optional[Dict[str, Any]] = None) -> str:
        """
        Dispatch a tool call by name with arguments.

        Args:
            tool_name: Name of the tool to call
            args: Dict of arguments for the tool

        Returns:
            String result for the LLM
        """
        name = (tool_name or "").strip().lower()
        if not name:
            log_browser_warning("Empty tool name received")
            return "error: tool name is empty"

        tool = self._tool_map.get(name)
        if tool is None:
            log_browser_warning(f"Unknown tool: {name}")
            return f"error: unknown tool '{name}'"

        params = args or {}
        try:
            log_browser_debug(f"Dispatching tool: {name} with args: {params}")
            result = tool(**params) if params else tool()
            return self._normalize_result(result)
        except TypeError as e:
            log_browser_error(f"Invalid args for tool '{name}': {e}")
            return f"error: invalid args for '{name}'"
        except Exception as e:
            log_browser_error(f"Tool '{name}' failed: {e}")
            return f"error: tool '{name}' failed"

    def _done(self, result: str = "") -> str:
        """Return the final response string."""
        return result or ""

    @staticmethod
    def _normalize_result(result: Any) -> str:
        """Normalize native results to a string for the LLM."""
        if result is None:
            return ""
        if isinstance(result, bool):
            return "true" if result else "false"
        return str(result)
