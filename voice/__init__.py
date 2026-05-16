"""
Voice module for Voice Browser Agent.
Handles voice input (recording, transcription) and output (text-to-speech).
"""

from .recorder import AudioRecorder
from .transcriber import Transcriber
from .speaker import Speaker

__all__ = ["AudioRecorder", "Transcriber", "Speaker"]
