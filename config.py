"""
Configuration module for Voice Browser Agent.
Loads environment variables and defines all constants used throughout the application.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# ============================================================================
# PROJECT PATHS
# ============================================================================

# Base directory (project root)
BASE_DIR = Path(__file__).parent.absolute()

# Data directories
DATA_DIR = BASE_DIR / "data"
SESSIONS_DIR = DATA_DIR / "sessions"
TEMP_DIR = BASE_DIR / "temp"
SCREENSHOTS_DIR = BASE_DIR / "screenshots"

# Ensure directories exist
DATA_DIR.mkdir(exist_ok=True)
SESSIONS_DIR.mkdir(exist_ok=True)
TEMP_DIR.mkdir(exist_ok=True)
SCREENSHOTS_DIR.mkdir(exist_ok=True)

# ============================================================================
# API CONFIGURATION
# ============================================================================

# Groq API Configuration
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.1-70b-versatile")
GROQ_API_BASE = os.getenv("GROQ_API_BASE", "https://api.groq.com/openai/v1")

# OpenAI API Configuration (optional, for Whisper API mode)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Validate required API keys
if not GROQ_API_KEY:
    raise ValueError(
        "GROQ_API_KEY not found in environment variables. "
        "Please set it in your .env file."
    )

# ============================================================================
# WHISPER (SPEECH-TO-TEXT) CONFIGURATION
# ============================================================================

# Whisper model size: tiny, base, small, medium, large
WHISPER_MODEL = os.getenv("WHISPER_MODEL", "base")

# Use local Whisper or OpenAI API
WHISPER_USE_API = os.getenv("WHISPER_USE_API", "false").lower() == "true"

# Language for transcription (None = auto-detect)
WHISPER_LANGUAGE = os.getenv("WHISPER_LANGUAGE", None)

# ============================================================================
# AUDIO RECORDING CONFIGURATION
# ============================================================================

# Audio recording parameters
SAMPLE_RATE = int(os.getenv("SAMPLE_RATE", "16000"))  # Hz
CHANNELS = int(os.getenv("CHANNELS", "1"))  # Mono audio
FORMAT = "int16"  # Audio format (int16 PCM)

# Frame duration in milliseconds (20-30ms is optimal for speech)
FRAME_DURATION_MS = int(os.getenv("FRAME_DURATION_MS", "30"))  # milliseconds

# Calculate frames per buffer from frame duration and sample rate
# This ensures consistent timing regardless of sample rate
# Formula: frames = (sample_rate * duration_ms) / 1000
CHUNK_SIZE = int((SAMPLE_RATE * FRAME_DURATION_MS) / 1000)

# Allow manual override via CHUNK_SIZE env var if needed
if os.getenv("CHUNK_SIZE"):
    CHUNK_SIZE = int(os.getenv("CHUNK_SIZE"))

# Silence detection parameters
SILENCE_THRESHOLD = int(os.getenv("SILENCE_THRESHOLD", "500"))  # RMS energy threshold
SILENCE_DURATION = float(os.getenv("SILENCE_DURATION", "2.0"))  # Seconds of silence to stop recording
MIN_RECORDING_DURATION = float(os.getenv("MIN_RECORDING_DURATION", "0.5"))  # Minimum recording length in seconds
MAX_RECORDING_DURATION = float(os.getenv("MAX_RECORDING_DURATION", "30.0"))  # Maximum recording length in seconds

# Pre-roll buffer to capture early speech (in seconds)
PRE_ROLL_DURATION = float(os.getenv("PRE_ROLL_DURATION", "0.3"))  # Capture 300ms before speech detected

# Audio device selection (None = default device)
INPUT_DEVICE_INDEX = os.getenv("INPUT_DEVICE_INDEX")
if INPUT_DEVICE_INDEX:
    INPUT_DEVICE_INDEX = int(INPUT_DEVICE_INDEX)

# ============================================================================
# TEXT-TO-SPEECH CONFIGURATION
# ============================================================================

# TTS Engine: "pyttsx3" or "elevenlabs"
TTS_ENGINE = os.getenv("TTS_ENGINE", "pyttsx3")

# pyttsx3 settings
TTS_RATE = int(os.getenv("TTS_RATE", "150"))  # Words per minute
TTS_VOLUME = float(os.getenv("TTS_VOLUME", "0.9"))  # 0.0 to 1.0

# ElevenLabs settings (if using ElevenLabs)
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
ELEVENLABS_VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID", "21m00Tcm4TlvDq8ikWAM")  # Default voice

# ============================================================================
# BROWSER AUTOMATION CONFIGURATION
# ============================================================================

# Browser settings
BROWSER_TYPE = os.getenv("BROWSER_TYPE", "chromium")  # chromium, firefox, webkit
HEADLESS = os.getenv("HEADLESS", "false").lower() == "true"  # Run browser in headless mode
BROWSER_TIMEOUT = int(os.getenv("BROWSER_TIMEOUT", "30000"))  # Milliseconds

# Browser window size
VIEWPORT_WIDTH = int(os.getenv("VIEWPORT_WIDTH", "1280"))
VIEWPORT_HEIGHT = int(os.getenv("VIEWPORT_HEIGHT", "720"))

# User agent override (None = use Playwright default)
USER_AGENT = os.getenv("USER_AGENT", None)

# Page interaction settings
DEFAULT_NAVIGATION_TIMEOUT = int(os.getenv("DEFAULT_NAVIGATION_TIMEOUT", "30000"))  # ms
DEFAULT_ACTION_TIMEOUT = int(os.getenv("DEFAULT_ACTION_TIMEOUT", "10000"))  # ms

# Page content extraction
MAX_PAGE_CONTENT_LENGTH = int(os.getenv("MAX_PAGE_CONTENT_LENGTH", "5000"))  # Characters

# Browser debugging options (optional)
SLOW_MO = int(os.getenv("SLOW_MO", "0"))  # Milliseconds to slow down operations (0 = disabled)
DEVTOOLS = os.getenv("DEVTOOLS", "false").lower() == "true"  # Open DevTools on launch

# ============================================================================
# LLM AGENT CONFIGURATION
# ============================================================================

# Model parameters
LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0.7"))
LLM_MAX_TOKENS = int(os.getenv("LLM_MAX_TOKENS", "2000"))
LLM_TOP_P = float(os.getenv("LLM_TOP_P", "1.0"))

# Agent behavior
MAX_TOOL_CALLS_PER_TURN = int(os.getenv("MAX_TOOL_CALLS_PER_TURN", "5"))
MAX_CONVERSATION_TURNS = int(os.getenv("MAX_CONVERSATION_TURNS", "50"))

# ============================================================================
# MEMORY & CONTEXT CONFIGURATION
# ============================================================================

# Context window management
MAX_CONTEXT_MESSAGES = int(os.getenv("MAX_CONTEXT_MESSAGES", "20"))  # Keep last N messages
CONTEXT_TRIM_STRATEGY = os.getenv("CONTEXT_TRIM_STRATEGY", "sliding")  # sliding, summarize

# Session persistence
SAVE_SESSIONS = os.getenv("SAVE_SESSIONS", "true").lower() == "true"
SESSION_FILE_PREFIX = os.getenv("SESSION_FILE_PREFIX", "session")

# ============================================================================
# RATE LIMITING & RETRY CONFIGURATION
# ============================================================================

# Rate limit handling
RATE_LIMIT_RETRY = os.getenv("RATE_LIMIT_RETRY", "true").lower() == "true"
RATE_LIMIT_WAIT = int(os.getenv("RATE_LIMIT_WAIT", "60"))  # Seconds to wait on rate limit

# Retry settings
MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3"))
RETRY_DELAY = float(os.getenv("RETRY_DELAY", "1.0"))  # Seconds

# ============================================================================
# LOGGING CONFIGURATION
# ============================================================================

# Logging level: DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# Log to file
LOG_TO_FILE = os.getenv("LOG_TO_FILE", "false").lower() == "true"
LOG_FILE_PATH = BASE_DIR / "logs" / "voice_browser_agent.log"

# Ensure log directory exists if logging to file
if LOG_TO_FILE:
    LOG_FILE_PATH.parent.mkdir(exist_ok=True)

# ============================================================================
# FEATURE FLAGS
# ============================================================================

# Enable/disable features
ENABLE_VOICE_INPUT = os.getenv("ENABLE_VOICE_INPUT", "true").lower() == "true"
ENABLE_VOICE_OUTPUT = os.getenv("ENABLE_VOICE_OUTPUT", "true").lower() == "true"
ENABLE_SCREENSHOTS = os.getenv("ENABLE_SCREENSHOTS", "true").lower() == "true"
ENABLE_SESSION_MEMORY = os.getenv("ENABLE_SESSION_MEMORY", "true").lower() == "true"

# Debug mode
DEBUG_MODE = os.getenv("DEBUG_MODE", "false").lower() == "true"

# ============================================================================
# SYSTEM PROMPTS & MESSAGES
# ============================================================================

# System messages
STARTUP_MESSAGE = "Voice Browser Agent initialized. Speak your command..."
LISTENING_MESSAGE = "Listening..."
PROCESSING_MESSAGE = "Processing..."
THINKING_MESSAGE = "Thinking..."
ACTING_MESSAGE = "Performing action..."
DONE_MESSAGE = "Task completed."
ERROR_MESSAGE = "An error occurred. Please try again."
EXIT_KEYWORDS = ["exit", "quit", "stop", "goodbye", "bye"]

# ============================================================================
# VALIDATION
# ============================================================================

def validate_config():
    """Validate configuration settings."""
    errors = []
    
    # Check required API keys
    if not GROQ_API_KEY:
        errors.append("GROQ_API_KEY is required")
    
    if WHISPER_USE_API and not OPENAI_API_KEY:
        errors.append("OPENAI_API_KEY is required when WHISPER_USE_API is enabled")
    
    if TTS_ENGINE == "elevenlabs" and not ELEVENLABS_API_KEY:
        errors.append("ELEVENLABS_API_KEY is required when using ElevenLabs TTS")
    
    # Check numeric ranges
    if not (0 <= TTS_VOLUME <= 1.0):
        errors.append("TTS_VOLUME must be between 0.0 and 1.0")
    
    if SILENCE_THRESHOLD < 0:
        errors.append("SILENCE_THRESHOLD must be positive")
    
    if SILENCE_DURATION <= 0:
        errors.append("SILENCE_DURATION must be positive")
    
    if errors:
        raise ValueError(f"Configuration errors:\n" + "\n".join(f"  - {e}" for e in errors))

# Run validation on import
validate_config()

# ============================================================================
# CONFIGURATION SUMMARY
# ============================================================================

def print_config_summary():
    """Print a summary of the current configuration."""
    print("=" * 70)
    print("VOICE BROWSER AGENT - CONFIGURATION SUMMARY")
    print("=" * 70)
    print(f"Groq Model: {GROQ_MODEL}")
    print(f"Whisper Model: {WHISPER_MODEL} ({'API' if WHISPER_USE_API else 'Local'})")
    print(f"TTS Engine: {TTS_ENGINE}")
    print(f"Browser: {BROWSER_TYPE} ({'Headless' if HEADLESS else 'Visible'})")
    print(f"Silence Threshold: {SILENCE_THRESHOLD}")
    print(f"Silence Duration: {SILENCE_DURATION}s")
    print(f"Debug Mode: {'Enabled' if DEBUG_MODE else 'Disabled'}")
    print("=" * 70)

if __name__ == "__main__":
    print_config_summary()
