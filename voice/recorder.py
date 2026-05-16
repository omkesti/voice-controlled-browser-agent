"""
Audio recording module for Voice Browser Agent.
Implements PyAudio-based recording with silence detection and automatic stopping.
"""

import pyaudio
import time
from pathlib import Path
from typing import Optional, List
from collections import deque

import config
from utils.audio_utils import (
    calculate_rms,
    save_wav,
    generate_temp_filename,
    cleanup_old_recordings,
    get_audio_duration,
)
from utils.logger import (
    log_voice_info,
    log_voice_debug,
    log_voice_warning,
    log_voice_error,
)

# ============================================================================
# AUDIO RECORDER
# ============================================================================

class AudioRecorder:
    """
    Records audio from the microphone with automatic silence detection.
    
    Features:
    - Records from default microphone (or specified device)
    - Detects speech start using RMS energy threshold
    - Includes pre-roll buffer to capture early speech
    - Stops after configured silence duration
    - Respects min/max recording duration limits
    - Saves to temporary WAV file
    - Cleans up old recordings automatically
    
    Example:
        >>> recorder = AudioRecorder()
        >>> wav_path = recorder.record()
        >>> print(f"Recorded: {wav_path}")
    """
    
    def __init__(
        self,
        sample_rate: Optional[int] = None,
        chunk_size: Optional[int] = None,
        channels: Optional[int] = None,
        silence_threshold: Optional[int] = None,
        silence_duration: Optional[float] = None,
        min_duration: Optional[float] = None,
        max_duration: Optional[float] = None,
        pre_roll_duration: Optional[float] = None,
        device_index: Optional[int] = None,
    ):
        """
        Initialize the AudioRecorder.
        
        Args:
            sample_rate: Sample rate in Hz (default from config)
            chunk_size: Frames per buffer (default from config)
            channels: Number of channels (default from config)
            silence_threshold: RMS threshold for silence (default from config)
            silence_duration: Seconds of silence to stop (default from config)
            min_duration: Minimum recording duration (default from config)
            max_duration: Maximum recording duration (default from config)
            pre_roll_duration: Pre-roll buffer duration (default from config)
            device_index: Input device index (None = default device)
        """
        # Load configuration
        self.sample_rate = sample_rate or config.SAMPLE_RATE
        self.chunk_size = chunk_size or config.CHUNK_SIZE
        self.channels = channels or config.CHANNELS
        self.silence_threshold = silence_threshold or config.SILENCE_THRESHOLD
        self.silence_duration = silence_duration or config.SILENCE_DURATION
        self.min_duration = min_duration or config.MIN_RECORDING_DURATION
        self.max_duration = max_duration or config.MAX_RECORDING_DURATION
        self.pre_roll_duration = pre_roll_duration or config.PRE_ROLL_DURATION
        self.device_index = device_index or config.INPUT_DEVICE_INDEX
        
        # Calculate derived values
        self.sample_width = 2  # int16 = 2 bytes
        self.format = pyaudio.paInt16
        
        # Calculate silence duration in frames
        self.silence_frames = int(
            (self.silence_duration * self.sample_rate) / self.chunk_size
        )
        
        # Calculate pre-roll buffer size in frames
        self.pre_roll_frames = int(
            (self.pre_roll_duration * self.sample_rate) / self.chunk_size
        )
        
        # PyAudio instance
        self.audio = pyaudio.PyAudio()
        
        # Log initialization
        log_voice_debug(f"AudioRecorder initialized:")
        log_voice_debug(f"  Sample rate: {self.sample_rate}Hz")
        log_voice_debug(f"  Chunk size: {self.chunk_size} frames")
        log_voice_debug(f"  Channels: {self.channels}")
        log_voice_debug(f"  Silence threshold: {self.silence_threshold}")
        log_voice_debug(f"  Silence duration: {self.silence_duration}s ({self.silence_frames} frames)")
        log_voice_debug(f"  Pre-roll: {self.pre_roll_duration}s ({self.pre_roll_frames} frames)")
        log_voice_debug(f"  Min duration: {self.min_duration}s")
        log_voice_debug(f"  Max duration: {self.max_duration}s")
        
        # List available devices
        self._log_audio_devices()
    
    def _log_audio_devices(self):
        """Log information about available audio input devices."""
        try:
            device_count = self.audio.get_device_count()
            log_voice_debug(f"Available audio devices: {device_count}")
            
            default_input = self.audio.get_default_input_device_info()
            log_voice_debug(f"Default input device: {default_input['name']} (index {default_input['index']})")
            
            if self.device_index is not None:
                device_info = self.audio.get_device_info_by_index(self.device_index)
                log_voice_debug(f"Using device: {device_info['name']} (index {self.device_index})")
        except Exception as e:
            log_voice_warning(f"Could not enumerate audio devices: {e}")
    
    def record(self, output_dir: Optional[str] = None) -> str:
        """
        Record audio from the microphone until silence is detected.
        
        Process:
        1. Clean up old recordings
        2. Open audio stream
        3. Wait for speech to start (RMS above threshold)
        4. Record audio with pre-roll buffer
        5. Stop when silence detected for configured duration
        6. Save to WAV file
        7. Return path to WAV file
        
        Args:
            output_dir: Directory to save recording (default: config.TEMP_DIR)
        
        Returns:
            Path to the saved WAV file
        
        Raises:
            RuntimeError: If recording fails
        """
        output_dir = output_dir or str(config.TEMP_DIR)
        
        # Clean up old recordings on startup
        deleted = cleanup_old_recordings(output_dir, max_age_hours=24)
        if deleted > 0:
            log_voice_debug(f"Cleaned up {deleted} old recording(s)")
        
        log_voice_info("🎤 Listening for voice input...")
        
        # Open audio stream
        try:
            stream = self.audio.open(
                format=self.format,
                channels=self.channels,
                rate=self.sample_rate,
                input=True,
                input_device_index=self.device_index,
                frames_per_buffer=self.chunk_size,
            )
        except Exception as e:
            log_voice_error(f"Failed to open audio stream: {e}")
            raise RuntimeError(f"Could not open microphone: {e}")
        
        try:
            # Record audio
            audio_data = self._record_with_silence_detection(stream)
            
            # Close stream
            stream.stop_stream()
            stream.close()
            
            # Save to WAV file
            filename = generate_temp_filename("recording")
            filepath = str(Path(output_dir) / filename)
            
            saved_path = save_wav(
                filepath,
                audio_data,
                sample_rate=self.sample_rate,
                channels=self.channels,
                sample_width=self.sample_width,
            )
            
            # Log success
            duration = get_audio_duration(audio_data, self.sample_rate, self.sample_width)
            log_voice_info(f"✓ Recording saved: {Path(saved_path).name} ({duration:.2f}s)")
            
            return saved_path
            
        except Exception as e:
            stream.stop_stream()
            stream.close()
            log_voice_error(f"Recording failed: {e}")
            raise RuntimeError(f"Recording failed: {e}")
    
    def _record_with_silence_detection(self, stream) -> bytes:
        """
        Record audio with silence detection logic.
        
        Args:
            stream: PyAudio stream object
        
        Returns:
            Raw PCM audio data as bytes
        """
        frames: List[bytes] = []
        pre_roll_buffer: deque = deque(maxlen=self.pre_roll_frames)
        
        silent_frames = 0
        speech_started = False
        recording_start_time = None
        
        log_voice_debug("Waiting for speech to start...")
        
        while True:
            # Read audio chunk
            try:
                data = stream.read(self.chunk_size, exception_on_overflow=False)
            except Exception as e:
                log_voice_warning(f"Error reading audio stream: {e}")
                continue
            
            # Calculate RMS energy
            rms = calculate_rms(data, self.sample_width)
            
            # Check if speech has started
            if not speech_started:
                # Add to pre-roll buffer
                pre_roll_buffer.append(data)
                
                # Check if RMS exceeds threshold (speech detected)
                if rms >= self.silence_threshold:
                    speech_started = True
                    recording_start_time = time.time()
                    
                    # Add pre-roll buffer to frames
                    frames.extend(pre_roll_buffer)
                    
                    log_voice_info("🔴 Recording started (speech detected)")
                    log_voice_debug(f"  RMS: {rms:.2f} (threshold: {self.silence_threshold})")
                
                continue
            
            # Speech has started, now recording
            frames.append(data)
            
            # Calculate current recording duration
            current_duration = time.time() - recording_start_time
            
            # Check for silence
            if rms < self.silence_threshold:
                silent_frames += 1
                
                # Log silence detection (only once)
                if silent_frames == 1:
                    log_voice_debug(f"Silence detected (RMS: {rms:.2f})")
                
                # Check if silence duration exceeded
                if silent_frames >= self.silence_frames:
                    # Only stop if minimum duration met
                    if current_duration >= self.min_duration:
                        log_voice_info(f"⏹️  Recording stopped (silence: {self.silence_duration}s)")
                        break
                    else:
                        # Reset silence counter if min duration not met
                        silent_frames = 0
                        log_voice_debug(f"Silence detected but min duration not met ({current_duration:.2f}s < {self.min_duration}s)")
            else:
                # Reset silence counter when speech detected
                if silent_frames > 0:
                    log_voice_debug(f"Speech resumed (RMS: {rms:.2f})")
                silent_frames = 0
            
            # Check maximum duration
            if current_duration >= self.max_duration:
                log_voice_warning(f"⏹️  Recording stopped (max duration: {self.max_duration}s)")
                break
            
            # Log progress every 2 seconds
            if int(current_duration) % 2 == 0 and int(current_duration) > 0:
                if int(current_duration * 10) % 20 == 0:  # Only log once per 2-second interval
                    log_voice_debug(f"Recording... {current_duration:.1f}s (RMS: {rms:.0f})")
        
        # Combine all frames into single bytes object
        audio_data = b''.join(frames)
        
        return audio_data
    
    def close(self):
        """Close the PyAudio instance and release resources."""
        if self.audio:
            self.audio.terminate()
            log_voice_debug("AudioRecorder closed")
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
    
    def __del__(self):
        """Destructor to ensure cleanup."""
        self.close()

# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================

def record_audio(output_dir: Optional[str] = None) -> str:
    """
    Convenience function to record audio with default settings.
    
    Args:
        output_dir: Directory to save recording (default: config.TEMP_DIR)
    
    Returns:
        Path to the saved WAV file
    
    Example:
        >>> wav_path = record_audio()
        >>> print(f"Recorded: {wav_path}")
    """
    with AudioRecorder() as recorder:
        return recorder.record(output_dir)

# ============================================================================
# TESTING / DEMO
# ============================================================================

if __name__ == "__main__":
    """Demo the audio recorder."""
    import sys
    
    print("\n" + "=" * 70)
    print("AUDIO RECORDER DEMO")
    print("=" * 70)
    print("\nThis will record audio from your microphone.")
    print("Speak into your microphone, then stay silent for 2 seconds.")
    print("\nPress Ctrl+C to cancel.\n")
    
    try:
        # Record audio
        wav_path = record_audio()
        
        print("\n" + "=" * 70)
        print(f"✓ Recording saved: {wav_path}")
        print("=" * 70)
        
        # Show file info
        from utils.audio_utils import get_wav_duration
        duration = get_wav_duration(wav_path)
        print(f"\nDuration: {duration:.2f} seconds")
        print(f"Location: {wav_path}")
        
        print("\nYou can play this file with:")
        print(f"  python -c \"import sounddevice as sd; import soundfile as sf; data, sr = sf.read('{wav_path}'); sd.play(data, sr); sd.wait()\"")
        print("\n" + "=" * 70 + "\n")
        
    except KeyboardInterrupt:
        print("\n\nRecording cancelled by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\n\nError: {e}")
        sys.exit(1)
