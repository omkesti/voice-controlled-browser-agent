"""
Utilities module for Voice Browser Agent.
Contains logging, audio utilities, and helper functions.
"""

from .logger import (
    setup_logger,
    get_logger,
    log_voice,
    log_voice_info,
    log_voice_debug,
    log_voice_warning,
    log_voice_error,
    log_transcribe,
    log_transcribe_info,
    log_transcribe_debug,
    log_transcribe_warning,
    log_transcribe_error,
    log_agent,
    log_agent_info,
    log_agent_debug,
    log_agent_warning,
    log_agent_error,
    log_browser,
    log_browser_info,
    log_browser_debug,
    log_browser_warning,
    log_browser_error,
    log_tts,
    log_tts_info,
    log_tts_debug,
    log_tts_warning,
    log_tts_error,
    log_system,
    log_system_info,
    log_system_debug,
    log_system_warning,
    log_system_error,
    log_success,
    log_error,
    log_separator,
    log_header,
)

# Audio utils will be implemented later
# from .audio_utils import calculate_rms, save_audio, load_audio, cleanup_temp_files

__all__ = [
    # Logger setup
    "setup_logger",
    "get_logger",
    # Voice stage logging
    "log_voice",
    "log_voice_info",
    "log_voice_debug",
    "log_voice_warning",
    "log_voice_error",
    # Transcribe stage logging
    "log_transcribe",
    "log_transcribe_info",
    "log_transcribe_debug",
    "log_transcribe_warning",
    "log_transcribe_error",
    # Agent stage logging
    "log_agent",
    "log_agent_info",
    "log_agent_debug",
    "log_agent_warning",
    "log_agent_error",
    # Browser stage logging
    "log_browser",
    "log_browser_info",
    "log_browser_debug",
    "log_browser_warning",
    "log_browser_error",
    # TTS stage logging
    "log_tts",
    "log_tts_info",
    "log_tts_debug",
    "log_tts_warning",
    "log_tts_error",
    # System logging
    "log_system",
    "log_system_info",
    "log_system_debug",
    "log_system_warning",
    "log_system_error",
    # Convenience functions
    "log_success",
    "log_error",
    "log_separator",
    "log_header",
    # Audio utils (to be implemented)
    # "calculate_rms",
    # "save_audio",
    # "load_audio",
    # "cleanup_temp_files",
]
