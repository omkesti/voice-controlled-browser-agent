"""
Colored logging module for Voice Browser Agent.
Provides stage-specific colored logging for better visual tracking of the pipeline.
"""

import logging
import sys
from typing import Optional
from colorama import Fore, Back, Style, init

# Initialize colorama for cross-platform colored output
init(autoreset=True)

# ============================================================================
# STAGE COLORS
# ============================================================================

STAGE_COLORS = {
    "VOICE": Fore.CYAN,           # Cyan for voice input/recording
    "TRANSCRIBE": Fore.MAGENTA,   # Magenta for transcription
    "AGENT": Fore.GREEN,          # Green for agent thinking/decisions
    "BROWSER": Fore.BLUE,         # Blue for browser actions
    "TTS": Fore.YELLOW,           # Yellow for text-to-speech output
    "SYSTEM": Fore.WHITE,         # White for system messages
    "ERROR": Fore.RED,            # Red for errors
    "SUCCESS": Fore.GREEN,        # Green for success messages
    "WARNING": Fore.YELLOW,       # Yellow for warnings
}

# Log level colors
LEVEL_COLORS = {
    "DEBUG": Fore.LIGHTBLACK_EX,
    "INFO": Fore.WHITE,
    "WARNING": Fore.YELLOW,
    "ERROR": Fore.RED,
    "CRITICAL": Fore.RED + Back.WHITE,
}

# ============================================================================
# CUSTOM FORMATTER
# ============================================================================

class ColoredFormatter(logging.Formatter):
    """Custom formatter that adds colors to log messages based on stage and level."""
    
    def __init__(self, fmt: Optional[str] = None, datefmt: Optional[str] = None):
        super().__init__(fmt, datefmt)
    
    def format(self, record: logging.LogRecord) -> str:
        # Get stage from record (if set)
        stage = getattr(record, "stage", "SYSTEM")
        stage_color = STAGE_COLORS.get(stage, Fore.WHITE)
        
        # Get level color
        level_color = LEVEL_COLORS.get(record.levelname, Fore.WHITE)
        
        # Format the stage prefix with color
        stage_prefix = f"{stage_color}[{stage}]{Style.RESET_ALL}"
        
        # Format the level with color
        level_prefix = f"{level_color}{record.levelname}{Style.RESET_ALL}"
        
        # Format the message
        message = record.getMessage()
        
        # Build the final log line
        log_line = f"{stage_prefix} {level_prefix}: {message}"
        
        # Add exception info if present
        if record.exc_info:
            log_line += "\n" + self.formatException(record.exc_info)
        
        return log_line

# ============================================================================
# LOGGER SETUP
# ============================================================================

def setup_logger(
    name: str = "voice_browser_agent",
    level: str = "INFO",
    log_to_file: bool = False,
    log_file_path: Optional[str] = None,
) -> logging.Logger:
    """
    Set up and configure the logger with colored output.
    
    Args:
        name: Logger name
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_to_file: Whether to also log to a file
        log_file_path: Path to log file (if log_to_file is True)
    
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper()))
    
    # Remove existing handlers to avoid duplicates
    logger.handlers.clear()
    
    # Console handler with colors
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, level.upper()))
    console_handler.setFormatter(ColoredFormatter())
    logger.addHandler(console_handler)
    
    # File handler (no colors)
    if log_to_file and log_file_path:
        file_handler = logging.FileHandler(log_file_path)
        file_handler.setLevel(getattr(logging, level.upper()))
        file_formatter = logging.Formatter(
            "%(asctime)s - [%(stage)s] %(levelname)s: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
    
    return logger

# ============================================================================
# GLOBAL LOGGER INSTANCE
# ============================================================================

# This will be initialized by the application
_logger: Optional[logging.Logger] = None

def get_logger() -> logging.Logger:
    """Get the global logger instance."""
    global _logger
    if _logger is None:
        # Import here to avoid circular dependency
        try:
            import config
            _logger = setup_logger(
                level=config.LOG_LEVEL,
                log_to_file=config.LOG_TO_FILE,
                log_file_path=str(config.LOG_FILE_PATH) if config.LOG_TO_FILE else None,
            )
        except ImportError:
            # Fallback if config not available
            _logger = setup_logger()
    return _logger

# ============================================================================
# STAGE-SPECIFIC LOGGING FUNCTIONS
# ============================================================================

def _log_with_stage(stage: str, level: str, message: str, *args, **kwargs):
    """Internal helper to log with a specific stage."""
    logger = get_logger()
    log_func = getattr(logger, level.lower())
    
    # Create a log record with the stage attribute
    extra = kwargs.get("extra", {})
    extra["stage"] = stage
    kwargs["extra"] = extra
    
    log_func(message, *args, **kwargs)

# ============================================================================
# VOICE STAGE LOGGING
# ============================================================================

def log_voice(message: str, level: str = "INFO", *args, **kwargs):
    """
    Log a message for the VOICE stage (recording, audio input).
    
    Args:
        message: Log message
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    _log_with_stage("VOICE", level, message, *args, **kwargs)

def log_voice_debug(message: str, *args, **kwargs):
    """Log a DEBUG message for the VOICE stage."""
    log_voice(message, "DEBUG", *args, **kwargs)

def log_voice_info(message: str, *args, **kwargs):
    """Log an INFO message for the VOICE stage."""
    log_voice(message, "INFO", *args, **kwargs)

def log_voice_warning(message: str, *args, **kwargs):
    """Log a WARNING message for the VOICE stage."""
    log_voice(message, "WARNING", *args, **kwargs)

def log_voice_error(message: str, *args, **kwargs):
    """Log an ERROR message for the VOICE stage."""
    log_voice(message, "ERROR", *args, **kwargs)

# ============================================================================
# TRANSCRIBE STAGE LOGGING
# ============================================================================

def log_transcribe(message: str, level: str = "INFO", *args, **kwargs):
    """
    Log a message for the TRANSCRIBE stage (speech-to-text).
    
    Args:
        message: Log message
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    _log_with_stage("TRANSCRIBE", level, message, *args, **kwargs)

def log_transcribe_debug(message: str, *args, **kwargs):
    """Log a DEBUG message for the TRANSCRIBE stage."""
    log_transcribe(message, "DEBUG", *args, **kwargs)

def log_transcribe_info(message: str, *args, **kwargs):
    """Log an INFO message for the TRANSCRIBE stage."""
    log_transcribe(message, "INFO", *args, **kwargs)

def log_transcribe_warning(message: str, *args, **kwargs):
    """Log a WARNING message for the TRANSCRIBE stage."""
    log_transcribe(message, "WARNING", *args, **kwargs)

def log_transcribe_error(message: str, *args, **kwargs):
    """Log an ERROR message for the TRANSCRIBE stage."""
    log_transcribe(message, "ERROR", *args, **kwargs)

# ============================================================================
# AGENT STAGE LOGGING
# ============================================================================

def log_agent(message: str, level: str = "INFO", *args, **kwargs):
    """
    Log a message for the AGENT stage (LLM thinking, decision making).
    
    Args:
        message: Log message
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    _log_with_stage("AGENT", level, message, *args, **kwargs)

def log_agent_debug(message: str, *args, **kwargs):
    """Log a DEBUG message for the AGENT stage."""
    log_agent(message, "DEBUG", *args, **kwargs)

def log_agent_info(message: str, *args, **kwargs):
    """Log an INFO message for the AGENT stage."""
    log_agent(message, "INFO", *args, **kwargs)

def log_agent_warning(message: str, *args, **kwargs):
    """Log a WARNING message for the AGENT stage."""
    log_agent(message, "WARNING", *args, **kwargs)

def log_agent_error(message: str, *args, **kwargs):
    """Log an ERROR message for the AGENT stage."""
    log_agent(message, "ERROR", *args, **kwargs)

# ============================================================================
# BROWSER STAGE LOGGING
# ============================================================================

def log_browser(message: str, level: str = "INFO", *args, **kwargs):
    """
    Log a message for the BROWSER stage (web automation, actions).
    
    Args:
        message: Log message
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    _log_with_stage("BROWSER", level, message, *args, **kwargs)

def log_browser_debug(message: str, *args, **kwargs):
    """Log a DEBUG message for the BROWSER stage."""
    log_browser(message, "DEBUG", *args, **kwargs)

def log_browser_info(message: str, *args, **kwargs):
    """Log an INFO message for the BROWSER stage."""
    log_browser(message, "INFO", *args, **kwargs)

def log_browser_warning(message: str, *args, **kwargs):
    """Log a WARNING message for the BROWSER stage."""
    log_browser(message, "WARNING", *args, **kwargs)

def log_browser_error(message: str, *args, **kwargs):
    """Log an ERROR message for the BROWSER stage."""
    log_browser(message, "ERROR", *args, **kwargs)

# ============================================================================
# TTS STAGE LOGGING
# ============================================================================

def log_tts(message: str, level: str = "INFO", *args, **kwargs):
    """
    Log a message for the TTS stage (text-to-speech output).
    
    Args:
        message: Log message
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    _log_with_stage("TTS", level, message, *args, **kwargs)

def log_tts_debug(message: str, *args, **kwargs):
    """Log a DEBUG message for the TTS stage."""
    log_tts(message, "DEBUG", *args, **kwargs)

def log_tts_info(message: str, *args, **kwargs):
    """Log an INFO message for the TTS stage."""
    log_tts(message, "INFO", *args, **kwargs)

def log_tts_warning(message: str, *args, **kwargs):
    """Log a WARNING message for the TTS stage."""
    log_tts(message, "WARNING", *args, **kwargs)

def log_tts_error(message: str, *args, **kwargs):
    """Log an ERROR message for the TTS stage."""
    log_tts(message, "ERROR", *args, **kwargs)

# ============================================================================
# SYSTEM LOGGING
# ============================================================================

def log_system(message: str, level: str = "INFO", *args, **kwargs):
    """
    Log a system message (startup, shutdown, configuration).
    
    Args:
        message: Log message
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    _log_with_stage("SYSTEM", level, message, *args, **kwargs)

def log_system_debug(message: str, *args, **kwargs):
    """Log a DEBUG system message."""
    log_system(message, "DEBUG", *args, **kwargs)

def log_system_info(message: str, *args, **kwargs):
    """Log an INFO system message."""
    log_system(message, "INFO", *args, **kwargs)

def log_system_warning(message: str, *args, **kwargs):
    """Log a WARNING system message."""
    log_system(message, "WARNING", *args, **kwargs)

def log_system_error(message: str, *args, **kwargs):
    """Log an ERROR system message."""
    log_system(message, "ERROR", *args, **kwargs)

# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================

def log_success(message: str, stage: str = "SYSTEM"):
    """Log a success message with green color."""
    _log_with_stage(stage, "INFO", f"✓ {message}")

def log_error(message: str, stage: str = "SYSTEM"):
    """Log an error message with red color."""
    _log_with_stage(stage, "ERROR", f"✗ {message}")

def log_separator(char: str = "=", length: int = 70):
    """Log a visual separator line."""
    logger = get_logger()
    logger.info(char * length, extra={"stage": "SYSTEM"})

def log_header(title: str, char: str = "=", length: int = 70):
    """Log a header with title centered in separator lines."""
    log_separator(char, length)
    padding = (length - len(title) - 2) // 2
    header = f"{char * padding} {title} {char * padding}"
    if len(header) < length:
        header += char * (length - len(header))
    log_system_info(header)
    log_separator(char, length)

# ============================================================================
# DEMO / TESTING
# ============================================================================

if __name__ == "__main__":
    """Demo the colored logger."""
    
    # Initialize logger
    logger = setup_logger(level="DEBUG")
    
    print("\n" + "=" * 70)
    print("COLORED LOGGER DEMO - Voice Browser Agent")
    print("=" * 70 + "\n")
    
    # Demo each stage
    log_voice_info("Microphone initialized, starting recording...")
    log_voice_debug("Audio buffer size: 1024 frames")
    log_voice_warning("Background noise detected, adjusting threshold")
    
    log_transcribe_info("Transcribing audio with Whisper...")
    log_transcribe_debug("Using model: base")
    log_transcribe_info("Transcription: 'Search for Python tutorials'")
    
    log_agent_info("Processing command with LLM...")
    log_agent_debug("Sending request to Groq API")
    log_agent_info("Agent decided to use tool: search_google")
    
    log_browser_info("Opening browser...")
    log_browser_debug("Browser type: chromium, headless: False")
    log_browser_info("Navigating to: https://google.com")
    log_browser_info("Typing in search box: 'Python tutorials'")
    log_browser_info("Clicking search button")
    
    log_tts_info("Speaking response...")
    log_tts_debug("TTS engine: pyttsx3, rate: 150")
    log_tts_info("Output: 'I found several Python tutorials for you'")
    
    log_system_info("Task completed successfully")
    
    # Demo convenience functions
    print()
    log_success("Operation completed!", "SYSTEM")
    log_error("Something went wrong!", "SYSTEM")
    
    print()
    log_header("PIPELINE COMPLETE")
    
    # Demo error with exception
    print()
    try:
        raise ValueError("This is a test error")
    except Exception as e:
        log_agent_error(f"Error occurred: {e}", exc_info=True)
    
    print("\n" + "=" * 70)
    print("Demo complete!")
    print("=" * 70 + "\n")
