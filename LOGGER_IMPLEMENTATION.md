# Colored Logger Implementation

## Overview

Implemented a comprehensive colored logging system for the Voice Browser Agent that provides visual tracking of different pipeline stages.

## Features

### Stage-Specific Colors

Each pipeline stage has its own color for easy visual identification:

- **VOICE** (Cyan): Voice input and recording
- **TRANSCRIBE** (Magenta): Speech-to-text transcription
- **AGENT** (Green): LLM thinking and decision making
- **BROWSER** (Blue): Browser automation actions
- **TTS** (Yellow): Text-to-speech output
- **SYSTEM** (White): System messages
- **ERROR** (Red): Error messages

### Logging Functions

#### Basic Stage Logging

Each stage has a set of logging functions:

```python
# Voice stage
log_voice_info("Message")
log_voice_debug("Debug message")
log_voice_warning("Warning message")
log_voice_error("Error message")

# Transcribe stage
log_transcribe_info("Message")
log_transcribe_debug("Debug message")
log_transcribe_warning("Warning message")
log_transcribe_error("Error message")

# Agent stage
log_agent_info("Message")
log_agent_debug("Debug message")
log_agent_warning("Warning message")
log_agent_error("Error message")

# Browser stage
log_browser_info("Message")
log_browser_debug("Debug message")
log_browser_warning("Warning message")
log_browser_error("Error message")

# TTS stage
log_tts_info("Message")
log_tts_debug("Debug message")
log_tts_warning("Warning message")
log_tts_error("Error message")

# System stage
log_system_info("Message")
log_system_debug("Debug message")
log_system_warning("Warning message")
log_system_error("Error message")
```

#### Convenience Functions

```python
# Success/error shortcuts
log_success("Operation completed!", "SYSTEM")
log_error("Something went wrong!", "SYSTEM")

# Visual separators
log_separator()  # Prints a line of = characters
log_header("TITLE")  # Prints a centered header with separators
```

### Logger Setup

```python
from utils import setup_logger, get_logger

# Setup with custom configuration
logger = setup_logger(
    name="voice_browser_agent",
    level="INFO",  # DEBUG, INFO, WARNING, ERROR, CRITICAL
    log_to_file=True,
    log_file_path="logs/app.log"
)

# Or get the global logger instance
logger = get_logger()
```

## Usage Example

```python
from utils import (
    log_voice_info,
    log_transcribe_info,
    log_agent_info,
    log_browser_info,
    log_tts_info,
    log_success,
)

# Voice input
log_voice_info("Listening for voice input...")
log_voice_info("Recording started")

# Transcription
log_transcribe_info("Transcribing audio...")
log_transcribe_info("Transcription: 'Search for Python tutorials'")

# Agent processing
log_agent_info("Processing command with LLM...")
log_agent_info("Tool call: search_google(query='Python tutorials')")

# Browser actions
log_browser_info("Opening browser...")
log_browser_info("Navigating to: https://google.com")
log_browser_info("Typing in search box")

# TTS output
log_tts_info("Speaking response...")

# Success
log_success("Task completed!", "SYSTEM")
```

## Configuration

The logger respects the following environment variables from `.env`:

- `LOG_LEVEL`: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- `LOG_TO_FILE`: Whether to save logs to a file (true/false)

## Testing

Run the demo script to see all colors in action:

```bash
python utils/logger.py
```

Run the pipeline demo:

```bash
python test_logger.py
```

## Implementation Details

### Files Created

1. **`utils/logger.py`**: Main logger implementation with colored formatting
2. **`test_logger.py`**: Demo script showing the logger in action
3. **`utils/__init__.py`**: Updated to export all logging functions

### Dependencies

- `colorama`: Cross-platform colored terminal output (already in requirements.txt)
- `logging`: Python standard library

### Key Components

1. **ColoredFormatter**: Custom log formatter that adds colors based on stage and level
2. **Stage-specific functions**: Convenience functions for each pipeline stage
3. **Global logger instance**: Singleton pattern for consistent logging across modules
4. **File logging support**: Optional file output without colors for log files

## Benefits

1. **Visual Clarity**: Easy to track which part of the pipeline is executing
2. **Debugging**: Quickly identify issues by stage
3. **Professional Output**: Clean, colored console output
4. **Flexible**: Easy to add new stages or customize colors
5. **Cross-platform**: Works on Windows, macOS, and Linux thanks to colorama

## Next Steps

The logger is ready to be integrated into:
- Voice recording module (`voice/recorder.py`)
- Transcription module (`voice/transcriber.py`)
- Agent loop (`agent/loop.py`)
- Browser actions (`browser/actions.py`)
- TTS module (`voice/speaker.py`)
