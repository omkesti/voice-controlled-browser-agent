"""
Text-to-Speech module for Voice Browser Agent.
Converts text to speech using pyttsx3 (offline) or ElevenLabs (online).
"""

import re
from typing import Optional, List
import pyttsx3

import config
from utils.logger import (
    log_tts_info,
    log_tts_debug,
    log_tts_warning,
    log_tts_error,
)

# ============================================================================
# TEXT PROCESSING
# ============================================================================

def split_into_sentences(text: str, max_chunk_length: int = 300) -> List[str]:
    """
    Split text into sentences with fallback for long sentences.
    
    Uses regex to split on sentence boundaries (. ! ?) followed by whitespace.
    If a sentence exceeds max_chunk_length, splits it further at commas or spaces.
    
    Args:
        text: Text to split
        max_chunk_length: Maximum characters per chunk
    
    Returns:
        List of text chunks
    
    Example:
        >>> text = "Hello there. How are you? I'm doing great!"
        >>> chunks = split_into_sentences(text)
        >>> print(chunks)
        ['Hello there.', 'How are you?', "I'm doing great!"]
    """
    # Normalize whitespace
    text = ' '.join(text.split())
    
    if not text:
        return []
    
    # Split on sentence boundaries: . ! ? followed by space or end of string
    # Keep the punctuation with the sentence
    sentence_pattern = r'(?<=[.!?])\s+(?=[A-Z])|(?<=[.!?])$'
    sentences = re.split(sentence_pattern, text)
    
    # Filter empty strings
    sentences = [s.strip() for s in sentences if s.strip()]
    
    # Further split long sentences
    chunks = []
    for sentence in sentences:
        if len(sentence) <= max_chunk_length:
            chunks.append(sentence)
        else:
            # Split long sentence at commas or spaces
            sub_chunks = _split_long_sentence(sentence, max_chunk_length)
            chunks.extend(sub_chunks)
    
    return chunks

def _split_long_sentence(sentence: str, max_length: int) -> List[str]:
    """
    Split a long sentence into smaller chunks.
    
    Tries to split at commas first, then at spaces if needed.
    
    Args:
        sentence: Long sentence to split
        max_length: Maximum characters per chunk
    
    Returns:
        List of chunks
    """
    chunks = []
    
    # Try splitting at commas first
    if ',' in sentence:
        parts = sentence.split(',')
        current_chunk = ""
        
        for part in parts:
            part = part.strip()
            if not part:
                continue
            
            # Add comma back (except for last part)
            if part != parts[-1].strip():
                part += ','
            
            if len(current_chunk) + len(part) + 1 <= max_length:
                current_chunk += (' ' + part if current_chunk else part)
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = part
        
        if current_chunk:
            chunks.append(current_chunk.strip())
    else:
        # Split at spaces as last resort
        words = sentence.split()
        current_chunk = ""
        
        for word in words:
            if len(current_chunk) + len(word) + 1 <= max_length:
                current_chunk += (' ' + word if current_chunk else word)
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = word
        
        if current_chunk:
            chunks.append(current_chunk.strip())
    
    return chunks

# ============================================================================
# SPEAKER
# ============================================================================

class Speaker:
    """
    Text-to-speech speaker supporting multiple backends.
    
    Backends:
    - pyttsx3: Offline, free, cross-platform (default)
    - ElevenLabs: Online, high quality, requires API key (optional)
    
    Features:
    - Automatic sentence splitting for natural pauses
    - Long text handling with max chunk length
    - Blocking playback (waits until speech completes)
    - Configurable voice, rate, and volume
    - Comprehensive logging
    
    Example:
        >>> speaker = Speaker()
        >>> speaker.speak("Hello! How can I help you today?")
    """
    
    # Class-level pyttsx3 engine cache
    _pyttsx3_engine = None
    
    def __init__(
        self,
        engine: Optional[str] = None,
        rate: Optional[int] = None,
        volume: Optional[float] = None,
        voice_id: Optional[str] = None,
    ):
        """
        Initialize the Speaker.
        
        Args:
            engine: TTS engine ('pyttsx3' or 'elevenlabs')
            rate: Speech rate in words per minute (pyttsx3 only)
            volume: Volume level 0.0-1.0 (pyttsx3 only)
            voice_id: Voice ID for ElevenLabs
        """
        self.engine = engine or config.TTS_ENGINE
        self.rate = rate or config.TTS_RATE
        self.volume = volume or config.TTS_VOLUME
        self.voice_id = voice_id or config.ELEVENLABS_VOICE_ID
        
        # Initialize backend
        if self.engine == "pyttsx3":
            self._init_pyttsx3()
        elif self.engine == "elevenlabs":
            self._init_elevenlabs()
        else:
            log_tts_warning(f"Unknown TTS engine: {self.engine}, falling back to pyttsx3")
            self.engine = "pyttsx3"
            self._init_pyttsx3()
        
        log_tts_debug(f"Speaker initialized with {self.engine} engine")
    
    def _init_pyttsx3(self):
        """Initialize pyttsx3 engine (singleton)."""
        if Speaker._pyttsx3_engine is None:
            try:
                log_tts_debug("Initializing pyttsx3 engine...")
                Speaker._pyttsx3_engine = pyttsx3.init()
                log_tts_debug("✓ pyttsx3 engine initialized")
            except Exception as e:
                log_tts_error(f"Failed to initialize pyttsx3: {e}")
                raise RuntimeError(f"Could not initialize pyttsx3: {e}")
        
        # Configure engine
        try:
            Speaker._pyttsx3_engine.setProperty('rate', self.rate)
            Speaker._pyttsx3_engine.setProperty('volume', self.volume)
            
            log_tts_debug(f"  Rate: {self.rate} WPM")
            log_tts_debug(f"  Volume: {self.volume}")
            
            # Log available voices
            voices = Speaker._pyttsx3_engine.getProperty('voices')
            if voices:
                current_voice = Speaker._pyttsx3_engine.getProperty('voice')
                log_tts_debug(f"  Available voices: {len(voices)}")
                log_tts_debug(f"  Current voice: {current_voice}")
        except Exception as e:
            log_tts_warning(f"Could not configure pyttsx3 properties: {e}")
    
    def _init_elevenlabs(self):
        """Initialize ElevenLabs (optional)."""
        # Check if API key is configured
        if not config.ELEVENLABS_API_KEY:
            log_tts_error("ElevenLabs API key not configured (ELEVENLABS_API_KEY)")
            log_tts_warning("Falling back to pyttsx3")
            self.engine = "pyttsx3"
            self._init_pyttsx3()
            return
        
        # Check if elevenlabs package is installed
        try:
            import elevenlabs
            self.elevenlabs = elevenlabs
            log_tts_debug("✓ ElevenLabs package available")
            log_tts_debug(f"  Voice ID: {self.voice_id}")
        except ImportError:
            log_tts_error("ElevenLabs package not installed")
            log_tts_warning("Install with: pip install elevenlabs")
            log_tts_warning("Falling back to pyttsx3")
            self.engine = "pyttsx3"
            self._init_pyttsx3()
    
    def speak(self, text: str, max_chunk_length: int = 300) -> bool:
        """
        Speak the given text using the configured TTS engine.
        
        Blocks until speech completes.
        
        Args:
            text: Text to speak
            max_chunk_length: Maximum characters per chunk
        
        Returns:
            True if successful, False otherwise
        
        Example:
            >>> speaker = Speaker()
            >>> speaker.speak("Hello! How are you today?")
            True
        """
        # Normalize and strip text
        text = ' '.join(text.split()).strip()
        
        # Return early if empty
        if not text:
            log_tts_debug("Empty text, nothing to speak")
            return False
        
        log_tts_info(f"🔊 Speaking: \"{text[:100]}{'...' if len(text) > 100 else ''}\"")
        log_tts_debug(f"  Engine: {self.engine}")
        log_tts_debug(f"  Length: {len(text)} characters")
        
        # Split into chunks
        chunks = split_into_sentences(text, max_chunk_length)
        log_tts_debug(f"  Chunks: {len(chunks)}")
        
        # Speak each chunk
        try:
            if self.engine == "pyttsx3":
                return self._speak_pyttsx3(chunks)
            elif self.engine == "elevenlabs":
                return self._speak_elevenlabs(chunks)
            else:
                log_tts_error(f"Unknown engine: {self.engine}")
                return False
        except Exception as e:
            log_tts_error(f"Speech failed: {e}")
            return False
    
    def _speak_pyttsx3(self, chunks: List[str]) -> bool:
        """
        Speak using pyttsx3.
        
        Args:
            chunks: List of text chunks to speak
        
        Returns:
            True if successful
        """
        try:
            engine = Speaker._pyttsx3_engine
            
            # Queue all chunks
            for i, chunk in enumerate(chunks, 1):
                log_tts_debug(f"  Speaking chunk {i}/{len(chunks)}: \"{chunk[:50]}...\"")
                engine.say(chunk)
            
            # Block until all speech completes
            log_tts_debug("  Waiting for speech to complete...")
            engine.runAndWait()
            
            log_tts_info("✓ Speech completed")
            return True
            
        except Exception as e:
            log_tts_error(f"pyttsx3 speech failed: {e}")
            return False
    
    def _speak_elevenlabs(self, chunks: List[str]) -> bool:
        """
        Speak using ElevenLabs.
        
        Args:
            chunks: List of text chunks to speak
        
        Returns:
            True if successful
        """
        try:
            # Import here to avoid dependency if not used
            from elevenlabs import generate, play, set_api_key
            
            # Set API key
            set_api_key(config.ELEVENLABS_API_KEY)
            
            # Speak each chunk
            for i, chunk in enumerate(chunks, 1):
                log_tts_debug(f"  Speaking chunk {i}/{len(chunks)}: \"{chunk[:50]}...\"")
                
                # Generate audio
                audio = generate(
                    text=chunk,
                    voice=self.voice_id,
                )
                
                # Play audio (blocks until complete)
                play(audio)
            
            log_tts_info("✓ Speech completed")
            return True
            
        except Exception as e:
            log_tts_error(f"ElevenLabs speech failed: {e}")
            return False
    
    def stop(self):
        """Stop current speech (pyttsx3 only)."""
        if self.engine == "pyttsx3" and Speaker._pyttsx3_engine:
            try:
                Speaker._pyttsx3_engine.stop()
                log_tts_debug("Speech stopped")
            except Exception as e:
                log_tts_warning(f"Could not stop speech: {e}")
    
    @classmethod
    def cleanup(cls):
        """Clean up resources."""
        if cls._pyttsx3_engine:
            try:
                cls._pyttsx3_engine.stop()
                cls._pyttsx3_engine = None
                log_tts_debug("pyttsx3 engine cleaned up")
            except Exception:
                pass

# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================

def speak_text(text: str, engine: Optional[str] = None) -> bool:
    """
    Convenience function to speak text with default settings.
    
    Args:
        text: Text to speak
        engine: TTS engine ('pyttsx3' or 'elevenlabs')
    
    Returns:
        True if successful
    
    Example:
        >>> speak_text("Hello there!")
        True
    """
    speaker = Speaker(engine=engine)
    return speaker.speak(text)

# ============================================================================
# TESTING / DEMO
# ============================================================================

if __name__ == "__main__":
    """Demo the speaker."""
    import sys
    
    print("\n" + "=" * 70)
    print("TTS SPEAKER DEMO")
    print("=" * 70)
    print("\nThis will test text-to-speech with different scenarios.\n")
    
    try:
        speaker = Speaker()
        
        # Test 1: Simple greeting
        print("Test 1: Simple greeting")
        speaker.speak("Hello! Welcome to the Voice Browser Agent.")
        print()
        
        # Test 2: Multiple sentences
        print("Test 2: Multiple sentences")
        speaker.speak("This is a test. I can speak multiple sentences. Each one is processed separately.")
        print()
        
        # Test 3: Long text with sentence splitting
        print("Test 3: Long paragraph")
        long_text = (
            "The Voice Browser Agent is a Python application that listens to your voice, "
            "transcribes it using Whisper, and sends the transcription to an LLM. "
            "The LLM can then control a web browser using Playwright. "
            "Finally, the results are spoken back to you using text-to-speech."
        )
        speaker.speak(long_text)
        print()
        
        # Test 4: Text with punctuation
        print("Test 4: Text with punctuation")
        speaker.speak("Great! This works well. How about questions? Yes, those work too!")
        print()
        
        # Test 5: Very long sentence (tests max chunk length)
        print("Test 5: Very long sentence")
        very_long = (
            "This is an extremely long sentence that goes on and on and on, "
            "with many commas, and lots of words, and it just keeps going, "
            "and going, and going, until it finally reaches the maximum chunk length, "
            "at which point it will be split into smaller pieces for better processing."
        )
        speaker.speak(very_long)
        print()
        
        print("=" * 70)
        print("Demo complete!")
        print("=" * 70 + "\n")
        
    except KeyboardInterrupt:
        print("\n\nDemo cancelled by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\n\nError: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
