"""
Voice module for Voice Browser Agent.
Handles voice input (recording, transcription) and output (text-to-speech).
"""

# Lazy imports to avoid loading all dependencies at once
def __getattr__(name):
    if name == "AudioRecorder":
        from .recorder import AudioRecorder
        return AudioRecorder
    elif name == "record_audio":
        from .recorder import record_audio
        return record_audio
    elif name == "Transcriber":
        from .transcriber import Transcriber
        return Transcriber
    elif name == "transcribe_audio":
        from .transcriber import transcribe_audio
        return transcribe_audio
    elif name == "Speaker":
        from .speaker import Speaker
        return Speaker
    elif name == "speak_text":
        from .speaker import speak_text
        return speak_text
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")

__all__ = [
    "AudioRecorder",
    "record_audio",
    "Transcriber",
    "transcribe_audio",
    "Speaker",
    "speak_text",
]
