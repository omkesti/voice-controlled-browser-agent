"""
Voice module for Voice Browser Agent.
Handles voice input (recording, transcription) and output (text-to-speech).
"""

from .recorder import AudioRecorder, record_audio

# Transcriber and Speaker will be implemented later
# from .transcriber import Transcriber
# from .speaker import Speaker

__all__ = [
    "AudioRecorder",
    "record_audio",
    # "Transcriber",
    # "Speaker",
]
