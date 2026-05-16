"""
Prompt templates for the Voice Browser Agent.
Keep prompts concise to minimize latency.
"""

from typing import Dict

# Keep system prompt short to reduce token usage.
_BASE_SYSTEM_PROMPT = (
    "You are a voice-driven web assistant that can browse the web using tools. "
    "Follow the user task, think briefly, and act when needed. "
    "Use tools only when browsing or page interaction is required; otherwise answer directly. "
    "Available tools: navigate, click, type_text, scroll, screenshot, scrape, done. "
    "When calling tools, respond ONLY with tool_calls (JSON arguments). "
    "Do NOT use <function> tags. "
    "Prefer DuckDuckGo or Bing for searches; avoid Google to reduce bot-detection blocks. "
    "Rules: do not submit forms, do not make purchases, do not handle passwords or payment info. "
    "Do not click confirm/delete buttons without stating intent first. "
    "If a task is unsafe or not possible, say so and finish with done."
)


def build_system_prompt(user_task: str) -> str:
    """
    Build the system prompt by injecting the user task.
    Keep output concise to minimize latency.
    """
    task = (user_task or "").strip()
    if task:
        return f"{_BASE_SYSTEM_PROMPT} Task: {task}"
    return _BASE_SYSTEM_PROMPT


def build_user_message(user_task: str) -> Dict[str, str]:
    """
    Build a user message wrapper for chat-style APIs.
    """
    return {
        "role": "user",
        "content": (user_task or "").strip(),
    }
