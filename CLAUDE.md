# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

A continuous voice → agent → browser → TTS loop. The user speaks; Whisper transcribes locally; a Groq LLM autonomously drives a real Chromium browser via Playwright using tool calls until the task is done; then the result is spoken back via TTS. `main.py` wires the components together and runs the loop forever until an exit keyword (`exit`, `quit`, `stop`, `goodbye`, `bye`) or `Ctrl+C`.

## Commands

```bash
# Setup
pip install -r requirements.txt
playwright install chromium          # required — browser won't launch otherwise
cp .env.example .env                 # then add GROQ_API_KEY (required)

# Run the full voice loop
python main.py

# Print resolved configuration
python config.py

# Run a module's built-in demo (most modules are runnable standalone)
python -m browser.manager            # launches Chromium, hits example.com
python -m browser.actions            # navigate + scrape + screenshot demo
```

### Tests

Tests in `tests/` are **standalone interactive scripts**, not a pytest suite — most require a working microphone, speakers, and/or a live browser, and prompt for real speech. Run them directly:

```bash
python tests/test_browser_manager.py
python tests/test_complete_voice_loop.py    # records from mic, transcribes, speaks back
```

They insert the project root on `sys.path` themselves, so run from the repo root. `pytest`/`black`/`flake8`/`mypy` are listed but commented out in `requirements.txt` — there is no configured lint/format/type-check step.

## Configuration

`config.py` is the single source of truth. It loads `.env` via `python-dotenv`, then exposes ~everything as module-level constants and **runs `validate_config()` at import time** — importing `config` raises immediately if `GROQ_API_KEY` is missing or values are out of range. Nearly every tunable (Whisper model, silence thresholds, browser viewport/timeouts, LLM params, feature flags) is an env var with a default here; prefer adding new settings to `config.py` rather than hardcoding. Note the README/`.env.example` reference `llama-3.1-70b-versatile` but the code default is `llama-3.1-8b-instant`.

## Architecture

The dependency flow is one-directional. `main.py` constructs a single `BrowserManager` and threads it through everything so all layers share one browser page:

```
main.py
  └─ BrowserManager (Playwright lifecycle, ONE shared page)
       └─ BrowserActions (navigate/click/type_text/scroll/screenshot/scrape)
            └─ ToolDispatcher (tool name → BrowserActions method, results→str)
                 └─ AgentLoop (Groq calls + tool execution)
```

Key invariant: **one browser page is shared across the whole app.** `BrowserManager` is effectively a singleton holder (Playwright → Browser → Context → Page); `BrowserActions.__init__` calls `manager.get_page()` and caches it. If you construct any of these without passing the shared instance, you'll spawn a second browser. `main.py` does it correctly — follow that pattern.

### The agent loop (`agent/loop.py`)

`AgentLoop.run(user_task)` is the heart of the system:

1. Builds a fresh system prompt (`agent/prompts.py`) and **resets context each turn** (`reset(keep_system=False)`) — there is no cross-task memory in the loop today despite `MAX_CONTEXT_MESSAGES`/session config existing.
2. Calls Groq with the OpenAI-style tool schemas from `agent/tools.py`, up to `MAX_TOOL_CALLS_PER_TURN` iterations.
3. Executes tool calls via `ToolDispatcher`, appending each result back into context, and loops until the model calls the `done` tool (whose `result` string becomes the spoken response) or returns plain content.
4. **Robustness shim:** some Groq models emit tool calls as raw JSON in the message *content* instead of structured `tool_calls`. `_extract_tool_payloads` / `_handle_tool_payloads` parse and dispatch those as a fallback. Keep this in mind when changing tool-call handling.

### Adding a tool

A tool requires changes in **three** places, kept in sync by name:
1. `agent/tools.py` — add the OpenAI-style schema in `get_tool_definitions()`.
2. `agent/dispatcher.py` — add `name → method` to `ToolDispatcher._tool_map`.
3. `browser/actions.py` — implement the method on `BrowserActions`.

The dispatcher calls `tool(**args)`, so schema property names must exactly match method parameter names. Results are coerced to strings by `_normalize_result` before going back to the LLM. The `done` tool is special-cased (handled by `_done`, terminates the loop).

### Browser actions notes (`browser/actions.py`)

- Selectors run through `build_selector()` (in `browser/utils.py`), which produces multiple fallback candidates tried in order — actions are resilient to imperfect selectors from the LLM.
- `_dismiss_common_dialogs()` best-effort clicks cookie/consent banners before clicks and typing.
- `type_text` has special-casing for search boxes (`name="q"`): it adds extra fallbacks and presses Enter to submit. The system prompt steers searches to DuckDuckGo/Bing over Google to dodge bot detection.

### Voice layer (`voice/`)

`voice/__init__.py` uses lazy `__getattr__` imports so importing the package doesn't pull in PyAudio/Whisper/pyttsx3 all at once. `recorder.py` records with silence-detection (RMS threshold + duration) and a pre-roll buffer; `speaker.py` does TTS (pyttsx3 default, ElevenLabs optional). Audio temp files land in `temp/` and are cleaned up on shutdown.

**STT (`transcriber.py`) is provider-switched by `STT_PROVIDER`:**
- `groq` (**default**): cloud transcription via the Groq Whisper API (`client.audio.transcriptions.create`, default model `whisper-large-v3-turbo`). Fast + accurate, reuses `GROQ_API_KEY`, needs no local model or ffmpeg. Requires `groq>=0.11` (project pins `>=1.4.0`) — the audio API didn't exist in older SDKs.
- `local`: offline `openai-whisper` (`WHISPER_MODEL`, default `base`); `whisper` is imported lazily only on this path, and it needs ffmpeg on PATH. `WHISPER_USE_API=true` forces this local path regardless of `STT_PROVIDER`.

Both paths share the same `Transcriber.transcribe()` interface and confidence extraction (Groq uses `response_format="verbose_json"` to keep per-segment metrics), so `main.py` is provider-agnostic. Note: voice *activity* detection (knowing when you're speaking) is plain RMS energy in `recorder.py`, not a model — only the audio→text step is Whisper.

### Logging (`utils/logger.py`)

All modules log through namespaced helpers — `log_<area>_<level>`, e.g. `log_browser_info`, `log_agent_debug`, `log_voice_info`, `log_tts_warning`. Use the matching area helper rather than `print`; output is colorized via `rich`/`colorama`.

## Platform notes

Primary dev environment is Windows (PowerShell). `playwright.sync_api` cannot run inside a live asyncio loop — `BrowserManager.launch()` detects and works around a running loop by swapping in a fresh event loop (matters in notebooks). PyAudio install is platform-specific (see README).
