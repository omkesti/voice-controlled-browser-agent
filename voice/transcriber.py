"""
Whisper-based transcription module for Voice Browser Agent.
Converts audio files to text using OpenAI's Whisper model.
"""

import os
import shutil
from pathlib import Path
from typing import Optional, Dict, Any
import whisper

import config
from utils.logger import (
    log_transcribe_info,
    log_transcribe_debug,
    log_transcribe_warning,
    log_transcribe_error,
)

# ============================================================================
# TRANSCRIBER
# ============================================================================

class Transcriber:
    """
    Transcribes audio files to text using Whisper.
    
    Features:
    - Singleton model loading (loads once, reuses across calls)
    - Local Whisper model (tiny, base, small, medium, large)
    - Automatic language detection or forced language
    - Confidence scoring from Whisper segments
    - Empty/noise detection (returns None for silent audio)
    - Comprehensive error handling and logging
    
    Example:
        >>> transcriber = Transcriber()
        >>> text = transcriber.transcribe("recording.wav")
        >>> print(f"Transcription: {text}")
    """
    
    # Class-level model cache (singleton pattern)
    _model = None
    _model_name = None
    
    def __init__(
        self,
        model_name: Optional[str] = None,
        language: Optional[str] = None,
        device: Optional[str] = None,
    ):
        """
        Initialize the Transcriber.
        
        Args:
            model_name: Whisper model size (tiny, base, small, medium, large)
                       Default from config.WHISPER_MODEL
            language: Language code (e.g., 'en', 'es', 'fr') or None for auto-detect
                     Default from config.WHISPER_LANGUAGE
            device: Device to run on ('cpu', 'cuda') or None for auto-detect
        
        Note:
            The model is loaded only once and cached at the class level.
            Subsequent instances reuse the same model.
        """
        self.model_name = model_name or config.WHISPER_MODEL
        self.language = language or config.WHISPER_LANGUAGE
        self.device = device
        
        # Load model if not already loaded or if model name changed
        if Transcriber._model is None or Transcriber._model_name != self.model_name:
            self._load_model()
        else:
            log_transcribe_debug(f"Reusing cached Whisper model: {self.model_name}")
    
    def _load_model(self):
        """Load the Whisper model (class-level singleton)."""
        log_transcribe_info(f"Loading Whisper model: {self.model_name}...")
        
        try:
            # Load model
            Transcriber._model = whisper.load_model(
                self.model_name,
                device=self.device,
            )
            Transcriber._model_name = self.model_name
            
            log_transcribe_info(f"✓ Whisper model loaded: {self.model_name}")
            log_transcribe_debug(f"  Device: {Transcriber._model.device}")
            
        except Exception as e:
            log_transcribe_error(f"Failed to load Whisper model: {e}")
            raise RuntimeError(f"Could not load Whisper model '{self.model_name}': {e}")
    
    def transcribe(
        self,
        audio_path: str,
        **kwargs
    ) -> Optional[str]:
        """
        Transcribe an audio file to text.
        
        Args:
            audio_path: Path to audio file (WAV, MP3, etc.)
            **kwargs: Additional arguments passed to whisper.transcribe()
                     (e.g., temperature, beam_size, best_of)
        
        Returns:
            Transcribed text (stripped) or None if empty/silent
        
        Example:
            >>> text = transcriber.transcribe("recording.wav")
            >>> if text:
            ...     print(f"You said: {text}")
            ... else:
            ...     print("No speech detected")
        """
        # Validate file path
        if not os.path.exists(audio_path):
            log_transcribe_error(f"Audio file not found: {audio_path}")
            return None

        # Whisper relies on ffmpeg for audio decoding
        if shutil.which("ffmpeg") is None:
            log_transcribe_error("ffmpeg not found on PATH. Install ffmpeg to enable transcription.")
            log_transcribe_warning("Windows: choco install ffmpeg or winget install Gyan.FFmpeg")
            return None
        
        log_transcribe_info(f"🔤 Transcribing: {Path(audio_path).name}")
        log_transcribe_debug(f"  Model: {self.model_name}")
        log_transcribe_debug(f"  Language: {self.language or 'auto-detect'}")
        
        try:
            # Prepare transcription options
            transcribe_options = {
                "language": self.language,
                "verbose": False,
                **kwargs
            }
            
            # Remove None values
            transcribe_options = {
                k: v for k, v in transcribe_options.items()
                if v is not None
            }
            
            # Transcribe audio
            result = Transcriber._model.transcribe(
                audio_path,
                **transcribe_options
            )
            
            # Extract text and strip whitespace
            text = result.get("text", "").strip()
            
            # Check if empty
            if not text:
                log_transcribe_warning("No speech detected (empty transcription)")
                return None
            
            # Extract confidence information
            confidence_info = self._extract_confidence(result)
            
            # Log transcription result
            self._log_transcription_result(text, confidence_info)
            
            return text
            
        except Exception as e:
            log_transcribe_error(f"Transcription failed: {e}")
            return None
    
    def _extract_confidence(self, result: Dict[str, Any]) -> Dict[str, float]:
        """
        Extract confidence metrics from Whisper result.
        
        Args:
            result: Whisper transcription result dictionary
        
        Returns:
            Dictionary with confidence metrics
        """
        confidence_info = {}
        
        try:
            segments = result.get("segments", [])
            
            if segments:
                # Calculate average log probability (confidence indicator)
                avg_logprobs = [seg.get("avg_logprob", 0.0) for seg in segments]
                
                if avg_logprobs:
                    avg_confidence = sum(avg_logprobs) / len(avg_logprobs)
                    confidence_info["avg_logprob"] = avg_confidence
                    
                    # Convert log probability to approximate confidence percentage
                    # Log probs are typically in range [-1, 0], where 0 is perfect
                    # We map this to [0, 100] percentage
                    confidence_pct = max(0, min(100, (1 + avg_confidence) * 100))
                    confidence_info["confidence_pct"] = confidence_pct
                
                # Count segments
                confidence_info["num_segments"] = len(segments)
                
                # Get no-speech probability (if available)
                no_speech_probs = [
                    seg.get("no_speech_prob", 0.0)
                    for seg in segments
                ]
                if no_speech_probs:
                    avg_no_speech = sum(no_speech_probs) / len(no_speech_probs)
                    confidence_info["avg_no_speech_prob"] = avg_no_speech
        
        except Exception as e:
            log_transcribe_debug(f"Could not extract confidence: {e}")
        
        return confidence_info
    
    def _log_transcription_result(self, text: str, confidence_info: Dict[str, float]):
        """
        Log transcription result with confidence information.
        
        Args:
            text: Transcribed text
            confidence_info: Confidence metrics dictionary
        """
        # Log text preview (first 100 chars)
        text_preview = text[:100] + "..." if len(text) > 100 else text
        log_transcribe_info(f"✓ Transcription: \"{text_preview}\"")
        
        # Log length
        log_transcribe_debug(f"  Length: {len(text)} characters")
        
        # Log confidence metrics
        if "confidence_pct" in confidence_info:
            confidence_pct = confidence_info["confidence_pct"]
            log_transcribe_debug(f"  Confidence: {confidence_pct:.1f}%")
        
        if "avg_logprob" in confidence_info:
            avg_logprob = confidence_info["avg_logprob"]
            log_transcribe_debug(f"  Avg log prob: {avg_logprob:.3f}")
        
        if "num_segments" in confidence_info:
            num_segments = confidence_info["num_segments"]
            log_transcribe_debug(f"  Segments: {num_segments}")
        
        if "avg_no_speech_prob" in confidence_info:
            no_speech = confidence_info["avg_no_speech_prob"]
            log_transcribe_debug(f"  No-speech prob: {no_speech:.3f}")
    
    def transcribe_with_metadata(
        self,
        audio_path: str,
        **kwargs
    ) -> Optional[Dict[str, Any]]:
        """
        Transcribe audio and return full metadata including confidence.
        
        Args:
            audio_path: Path to audio file
            **kwargs: Additional arguments for whisper.transcribe()
        
        Returns:
            Dictionary with 'text', 'confidence', and other metadata
            or None if transcription failed
        
        Example:
            >>> result = transcriber.transcribe_with_metadata("audio.wav")
            >>> if result:
            ...     print(f"Text: {result['text']}")
            ...     print(f"Confidence: {result['confidence']['confidence_pct']:.1f}%")
        """
        # Validate file path
        if not os.path.exists(audio_path):
            log_transcribe_error(f"Audio file not found: {audio_path}")
            return None
        
        try:
            # Prepare transcription options
            transcribe_options = {
                "language": self.language,
                "verbose": False,
                **kwargs
            }
            
            # Remove None values
            transcribe_options = {
                k: v for k, v in transcribe_options.items()
                if v is not None
            }
            
            # Transcribe audio
            result = Transcriber._model.transcribe(
                audio_path,
                **transcribe_options
            )
            
            # Extract text
            text = result.get("text", "").strip()
            
            if not text:
                return None
            
            # Extract confidence
            confidence_info = self._extract_confidence(result)
            
            # Build metadata dictionary
            metadata = {
                "text": text,
                "confidence": confidence_info,
                "language": result.get("language"),
                "segments": result.get("segments", []),
            }
            
            return metadata
            
        except Exception as e:
            log_transcribe_error(f"Transcription failed: {e}")
            return None
    
    @classmethod
    def unload_model(cls):
        """
        Unload the cached model to free memory.
        
        Example:
            >>> Transcriber.unload_model()
        """
        if cls._model is not None:
            log_transcribe_info("Unloading Whisper model...")
            cls._model = None
            cls._model_name = None
            log_transcribe_debug("Model unloaded")

# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================

def transcribe_audio(audio_path: str, model_name: Optional[str] = None) -> Optional[str]:
    """
    Convenience function to transcribe audio with default settings.
    
    Args:
        audio_path: Path to audio file
        model_name: Whisper model size (default from config)
    
    Returns:
        Transcribed text or None
    
    Example:
        >>> text = transcribe_audio("recording.wav")
        >>> print(text)
    """
    transcriber = Transcriber(model_name=model_name)
    return transcriber.transcribe(audio_path)

# ============================================================================
# TESTING / DEMO
# ============================================================================

if __name__ == "__main__":
    """Demo the transcriber."""
    import sys
    from voice.recorder import record_audio
    
    print("\n" + "=" * 70)
    print("WHISPER TRANSCRIBER DEMO")
    print("=" * 70)
    print("\nThis will:")
    print("1. Record audio from your microphone")
    print("2. Transcribe it using Whisper")
    print("3. Display the transcription and confidence")
    print("\nPress Ctrl+C to cancel.\n")
    
    try:
        # Record audio
        print("Step 1: Recording audio...")
        wav_path = record_audio()
        print(f"✓ Recorded: {wav_path}\n")
        
        # Transcribe
        print("Step 2: Transcribing...")
        transcriber = Transcriber()
        
        # Get full metadata
        result = transcriber.transcribe_with_metadata(wav_path)
        
        if result:
            print("\n" + "=" * 70)
            print("TRANSCRIPTION RESULT")
            print("=" * 70)
            print(f"\nText: {result['text']}")
            print(f"\nLanguage: {result['language']}")
            
            if result['confidence']:
                conf = result['confidence']
                print(f"\nConfidence Metrics:")
                if 'confidence_pct' in conf:
                    print(f"  Confidence: {conf['confidence_pct']:.1f}%")
                if 'avg_logprob' in conf:
                    print(f"  Avg log prob: {conf['avg_logprob']:.3f}")
                if 'num_segments' in conf:
                    print(f"  Segments: {conf['num_segments']}")
            
            print("\n" + "=" * 70 + "\n")
        else:
            print("\n❌ No speech detected or transcription failed.\n")
        
    except KeyboardInterrupt:
        print("\n\nDemo cancelled by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\n\nError: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
