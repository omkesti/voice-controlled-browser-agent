"""
Core agent loop for Voice Browser Agent.
Calls the Groq API, executes tool calls, and returns a final response.
"""

import json
from typing import Any, Dict, List, Optional

from groq import Groq

import config
from agent.prompts import build_system_prompt
from agent.tools import get_tool_definitions
from agent.dispatcher import ToolDispatcher
from memory.context import ContextManager
from utils.logger import (
    log_agent_info,
    log_agent_debug,
    log_agent_warning,
    log_agent_error,
)


class AgentLoop:
    """
    Core agent loop that interacts with the LLM and tools.
    """

    def __init__(
        self,
        dispatcher: Optional[ToolDispatcher] = None,
        context: Optional[ContextManager] = None,
        model: Optional[str] = None,
    ) -> None:
        self.dispatcher = dispatcher or ToolDispatcher()
        self.context = context or ContextManager()
        self.model = model or config.GROQ_MODEL
        self.client = Groq(api_key=config.GROQ_API_KEY)
        self.tool_schemas = get_tool_definitions()

    def run(self, user_task: str) -> str:
        """
        Run the agent for a single user task.

        Returns:
            Final response string
        """
        system_prompt = build_system_prompt(user_task)
        self.context.reset(keep_system=False)
        self.context.set_system_prompt(system_prompt)
        self.context.append_user(user_task)

        max_iters = config.MAX_TOOL_CALLS_PER_TURN
        for step in range(max_iters):
            log_agent_info(f"LLM call {step + 1}/{max_iters}")

            response = self._call_llm(self.context.get_messages())
            message = response.get("message")
            if not message:
                log_agent_warning("Empty LLM response message")
                return "error: empty response from LLM"

            tool_calls = message.get("tool_calls") or []
            content = (message.get("content") or "").strip()

            if tool_calls:
                final = self._handle_tool_calls(tool_calls)
                if final is not None:
                    return final
                continue

            if content:
                # Fallback: some models emit tool calls as JSON in content.
                tool_payloads = self._extract_tool_payloads(content)
                if tool_payloads:
                    final = self._handle_tool_payloads(tool_payloads)
                    if final is not None:
                        return final
                    continue
                self.context.append_assistant(content)
                return content

            log_agent_warning("LLM response contained no content or tool calls")
            return "error: no content or tool calls"

        log_agent_error("Max tool iterations reached")
        return "error: max tool iterations reached"

    def _call_llm(self, messages: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Call Groq chat completions with tool schemas.
        """
        log_agent_debug(f"Sending {len(messages)} messages to LLM")
        try:
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=self.tool_schemas,
                temperature=config.LLM_TEMPERATURE,
                max_tokens=config.LLM_MAX_TOKENS,
                top_p=config.LLM_TOP_P,
            )
        except Exception as e:
            log_agent_error(f"LLM call failed: {e}")
            raise

        choice = completion.choices[0]
        message = choice.message

        # Normalize to plain dict for easier handling
        tool_calls = []
        if getattr(message, "tool_calls", None):
            for call in message.tool_calls:
                tool_calls.append(
                    {
                        "id": getattr(call, "id", None),
                        "type": getattr(call, "type", "function"),
                        "function": {
                            "name": getattr(call.function, "name", ""),
                            "arguments": getattr(call.function, "arguments", "{}"),
                        },
                    }
                )

        return {
            "message": {
                "content": getattr(message, "content", None),
                "tool_calls": tool_calls,
            }
        }

    def _handle_tool_calls(self, tool_calls: List[Dict[str, Any]]) -> Optional[str]:
        """
        Dispatch tool calls; return final result if done tool called.
        """
        for call in tool_calls:
            fn = (call.get("function") or {})
            name = (fn.get("name") or "").strip()
            args_str = fn.get("arguments") or "{}"

            args = self._parse_tool_args(args_str)
            log_agent_info(f"Tool call: {name}")
            log_agent_debug(f"Tool args: {args}")

            result = self.dispatcher.dispatch(name, args)
            log_agent_info(f"Tool result: {result}")

            if name == "done":
                return result

            self.context.append_tool_result(name, result)

        return None

    def _handle_tool_payloads(self, payloads: List[Dict[str, Any]]) -> Optional[str]:
        """
        Dispatch tool calls parsed from content JSON.
        """
        for payload in payloads:
            fn_payload = payload.get("function") if isinstance(payload, dict) else None

            name = (payload.get("name") or "").strip()
            if not name and isinstance(fn_payload, dict):
                name = (fn_payload.get("name") or "").strip()

            args = payload.get("arguments") or payload.get("parameters") or {}
            if isinstance(fn_payload, dict) and not args:
                args = fn_payload.get("arguments") or {}

            if isinstance(args, str):
                args = self._parse_tool_args(args)
            if not isinstance(args, dict):
                args = {}

            log_agent_info(f"Tool call (content): {name}")
            log_agent_debug(f"Tool args: {args}")

            result = self.dispatcher.dispatch(name, args)
            log_agent_info(f"Tool result: {result}")

            if name == "done":
                return result

            self.context.append_tool_result(name, result)

        return None

    @staticmethod
    def _parse_tool_args(args_str: str) -> Dict[str, Any]:
        """
        Parse tool call arguments JSON into a dict.
        """
        if not args_str:
            return {}

        if isinstance(args_str, dict):
            return args_str

        try:
            parsed = json.loads(args_str)
            return parsed if isinstance(parsed, dict) else {}
        except json.JSONDecodeError:
            return {}

    @staticmethod
    def _extract_tool_payloads(content: str) -> List[Dict[str, Any]]:
        """
        Extract tool call payloads from assistant content JSON.
        Supports a single JSON object or a JSON array.
        """
        text = (content or "").strip()
        if not text:
            return []

        decoder = json.JSONDecoder()
        idx = 0
        payloads: List[Dict[str, Any]] = []

        while idx < len(text):
            ch = text[idx]
            if ch not in "{[":
                idx += 1
                continue

            try:
                parsed, end = decoder.raw_decode(text, idx)
            except json.JSONDecodeError:
                idx += 1
                continue

            if isinstance(parsed, dict):
                payloads.append(parsed)
            elif isinstance(parsed, list):
                payloads.extend([p for p in parsed if isinstance(p, dict)])

            idx = end

        return payloads
