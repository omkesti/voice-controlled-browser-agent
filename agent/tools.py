"""
Tool schema definitions for the Voice Browser Agent.
Provides OpenAI-style tool definitions for browser actions.
"""

from typing import List, Dict, Any

# ============================================================================
# TOOL DEFINITIONS
# ============================================================================

def get_tool_definitions() -> List[Dict[str, Any]]:
    """
    Return OpenAI-style tool definitions for the agent.

    Each tool includes a name, description, and JSON schema parameters
    so the LLM can select and call tools correctly.
    """
    return [
        {
            "type": "function",
            "function": {
                "name": "navigate",
                "description": "Open a URL in the browser and wait for the page to load. Returns the page title.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "url": {
                            "type": "string",
                            "description": "The destination URL to open.",
                        }
                    },
                    "required": ["url"],
                    "additionalProperties": False,
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "click",
                "description": "Click an element on the page using a CSS, text, or XPath selector.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "selector": {
                            "type": "string",
                            "description": "CSS, text, or XPath selector for the element to click.",
                        }
                    },
                    "required": ["selector"],
                    "additionalProperties": False,
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "type_text",
                "description": "Clear an input field and type text into it with a human-like delay.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "selector": {
                            "type": "string",
                            "description": "CSS, text, or XPath selector for the input field.",
                        },
                        "text": {
                            "type": "string",
                            "description": "Text to type into the field.",
                        },
                    },
                    "required": ["selector", "text"],
                    "additionalProperties": False,
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "scroll",
                "description": "Scroll the page up or down by a number of pixels.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "direction": {
                            "type": "string",
                            "description": "Scroll direction.",
                            "enum": ["up", "down"],
                        },
                        "amount": {
                            "type": "integer",
                            "description": "Number of pixels to scroll.",
                        },
                    },
                    "required": ["direction", "amount"],
                    "additionalProperties": False,
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "screenshot",
                "description": "Capture a screenshot and save it under the screenshots directory.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "path": {
                            "type": "string",
                            "description": "Filename or relative path for the screenshot.",
                        }
                    },
                    "required": ["path"],
                    "additionalProperties": False,
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "scrape",
                "description": "Extract visible text from the current page and return a truncated result.",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": [],
                    "additionalProperties": False,
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "done",
                "description": "Signal completion with a final result string to speak to the user.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "result": {
                            "type": "string",
                            "description": "Final response to speak to the user.",
                        }
                    },
                    "required": ["result"],
                    "additionalProperties": False,
                },
            },
        },
    ]
