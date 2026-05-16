"""
Conversation context manager for Voice Browser Agent.
Maintains a bounded list of chat messages.
"""

from typing import Any, Dict, List, Optional

import config


class ContextManager:
    """
    Manage conversation messages and trim to a sliding window.
    """

    def __init__(self, system_prompt: Optional[str] = None, max_messages: Optional[int] = None):
        self._max_messages = max_messages or config.MAX_CONTEXT_MESSAGES
        self._system_message: Optional[Dict[str, str]] = None
        self._messages: List[Dict[str, Any]] = []

        if system_prompt:
            self.set_system_prompt(system_prompt)

    def set_system_prompt(self, system_prompt: str) -> None:
        """Set or replace the system message and keep it at index 0."""
        content = (system_prompt or "").strip()
        if not content:
            self._system_message = None
            self._messages = [m for m in self._messages if m.get("role") != "system"]
            return

        self._system_message = {"role": "system", "content": content}
        self._messages = [m for m in self._messages if m.get("role") != "system"]
        self._messages.insert(0, self._system_message)
        self._trim_messages()

    def append_user(self, content: str) -> None:
        self._messages.append({"role": "user", "content": (content or "").strip()})
        self._trim_messages()

    def append_assistant(self, content: str) -> None:
        self._messages.append({"role": "assistant", "content": (content or "").strip()})
        self._trim_messages()

    def append_tool_result(self, tool_name: str, content: str) -> None:
        name = (tool_name or "").strip() or "tool"
        self._messages.append({"role": "tool", "name": name, "content": (content or "").strip()})
        self._trim_messages()

    def get_messages(self) -> List[Dict[str, Any]]:
        """Return the current message list."""
        return list(self._messages)

    def reset(self, keep_system: bool = True) -> None:
        """Clear messages for a new task."""
        if keep_system and self._system_message:
            self._messages = [self._system_message]
        else:
            self._messages = []

    def _trim_messages(self) -> None:
        """Trim messages to a sliding window while preserving the system message."""
        if self._max_messages <= 0:
            return

        system_msg = None
        if self._messages and self._messages[0].get("role") == "system":
            system_msg = self._messages[0]
            non_system = self._messages[1:]
        else:
            non_system = self._messages

        if len(non_system) > self._max_messages:
            non_system = non_system[-self._max_messages :]

        if system_msg:
            self._messages = [system_msg] + non_system
        else:
            self._messages = non_system
