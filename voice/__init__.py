"""
Voice module for Voice Browser Agent.
Handles voice input (recording, transcription) and output (text-to-speech).
"""

from .recorder import AudioRecorder, record_audio
from .transcriber import Transcriber, transcribe_audio

# Speaker will be implemented later
# from .speaker import Speaker

__all__ = [
    "AudioRecorder",
    "record_audio",
    "Transcriber",
    "transcribe_audio",
    # "Speaker",
]
