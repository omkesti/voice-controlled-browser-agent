"""
Audio utilities for Voice Browser Agent.
Provides helpers for RMS calculation, WAV file operations, and temp file cleanup.
"""

import os
import wave
import struct
import numpy as np
from pathlib import Path
from typing import Optional, List
from datetime import datetime, timedelta

# ============================================================================
# RMS ENERGY CALCULATION
# ============================================================================

def calculate_rms(audio_data: bytes, sample_width: int = 2) -> float:
    """
    Calculate RMS (Root Mean Square) energy of audio data.
    
    RMS is used to measure the "loudness" or energy level of audio.
    Higher RMS = louder audio, Lower RMS = quieter audio.
    
    Args:
        audio_data: Raw audio bytes (PCM format)
        sample_width: Bytes per sample (2 for int16, 4 for int32)
    
    Returns:
        RMS energy value as a float
    
    Example:
        >>> audio_bytes = b'\\x00\\x01\\x02\\x03...'
        >>> rms = calculate_rms(audio_bytes)
        >>> print(f"Audio energy: {rms}")
    """
    if not audio_data:
        return 0.0
    
    # Convert bytes to numpy array of int16 values
    if sample_width == 2:
        # int16 format (most common)
        audio_array = np.frombuffer(audio_data, dtype=np.int16)
    elif sample_width == 4:
        # int32 format
        audio_array = np.frombuffer(audio_data, dtype=np.int32)
    else:
        raise ValueError(f"Unsupported sample width: {sample_width}")
    
    # Calculate RMS: sqrt(mean(x^2))
    rms = np.sqrt(np.mean(audio_array.astype(np.float64) ** 2))
    
    return float(rms)

def calculate_rms_simple(audio_data: bytes) -> float:
    """
    Calculate RMS energy using simple Python (no numpy).
    Fallback for environments without numpy.
    
    Args:
        audio_data: Raw audio bytes (int16 PCM format)
    
    Returns:
        RMS energy value as a float
    """
    if not audio_data or len(audio_data) < 2:
        return 0.0
    
    # Unpack bytes to int16 values
    count = len(audio_data) // 2
    format_str = f"{count}h"  # 'h' = signed short (int16)
    
    try:
        samples = struct.unpack(format_str, audio_data)
    except struct.error:
        return 0.0
    
    # Calculate sum of squares
    sum_squares = sum(sample ** 2 for sample in samples)
    
    # Calculate mean and square root
    mean_square = sum_squares / count
    rms = mean_square ** 0.5
    
    return rms

# ============================================================================
# WAV FILE OPERATIONS
# ============================================================================

def save_wav(
    filepath: str,
    audio_data: bytes,
    sample_rate: int = 16000,
    channels: int = 1,
    sample_width: int = 2,
) -> str:
    """
    Save raw PCM audio data to a WAV file.
    
    Args:
        filepath: Path where WAV file will be saved
        audio_data: Raw PCM audio bytes
        sample_rate: Sample rate in Hz (e.g., 16000, 44100)
        channels: Number of audio channels (1=mono, 2=stereo)
        sample_width: Bytes per sample (2 for int16)
    
    Returns:
        Absolute path to the saved WAV file
    
    Example:
        >>> audio_bytes = record_audio()
        >>> filepath = save_wav("output.wav", audio_bytes, sample_rate=16000)
        >>> print(f"Saved to: {filepath}")
    """
    # Ensure directory exists
    Path(filepath).parent.mkdir(parents=True, exist_ok=True)
    
    # Write WAV file
    with wave.open(filepath, 'wb') as wav_file:
        wav_file.setnchannels(channels)
        wav_file.setsampwidth(sample_width)
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(audio_data)
    
    return str(Path(filepath).absolute())

def load_wav(filepath: str) -> tuple:
    """
    Load audio data from a WAV file.
    
    Args:
        filepath: Path to WAV file
    
    Returns:
        Tuple of (audio_data, sample_rate, channels, sample_width)
    
    Example:
        >>> audio_data, sr, channels, width = load_wav("input.wav")
        >>> print(f"Loaded {len(audio_data)} bytes at {sr}Hz")
    """
    with wave.open(filepath, 'rb') as wav_file:
        channels = wav_file.getnchannels()
        sample_width = wav_file.getsampwidth()
        sample_rate = wav_file.getframerate()
        audio_data = wav_file.readframes(wav_file.getnframes())
    
    return audio_data, sample_rate, channels, sample_width

def get_wav_duration(filepath: str) -> float:
    """
    Get the duration of a WAV file in seconds.
    
    Args:
        filepath: Path to WAV file
    
    Returns:
        Duration in seconds
    """
    with wave.open(filepath, 'rb') as wav_file:
        frames = wav_file.getnframes()
        rate = wav_file.getframerate()
        duration = frames / float(rate)
    
    return duration

# ============================================================================
# TEMP FILE MANAGEMENT
# ============================================================================

def generate_temp_filename(prefix: str = "recording", extension: str = ".wav") -> str:
    """
    Generate a unique temporary filename with timestamp.
    
    Args:
        prefix: Filename prefix
        extension: File extension (including dot)
    
    Returns:
        Filename string (not full path)
    
    Example:
        >>> filename = generate_temp_filename("voice")
        >>> print(filename)  # voice_20240516_143022_123456.wav
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    return f"{prefix}_{timestamp}{extension}"

def cleanup_temp_files(
    temp_dir: str,
    pattern: str = "*.wav",
    max_age_hours: Optional[float] = None,
    keep_recent: int = 0,
) -> int:
    """
    Clean up old temporary files in a directory.
    
    Args:
        temp_dir: Directory containing temp files
        pattern: File pattern to match (e.g., "*.wav", "recording_*.wav")
        max_age_hours: Delete files older than this many hours (None = delete all)
        keep_recent: Keep this many most recent files
    
    Returns:
        Number of files deleted
    
    Example:
        >>> # Delete WAV files older than 24 hours
        >>> deleted = cleanup_temp_files("temp/", max_age_hours=24)
        >>> print(f"Deleted {deleted} old files")
        
        >>> # Delete all but the 5 most recent files
        >>> deleted = cleanup_temp_files("temp/", keep_recent=5)
    """
    temp_path = Path(temp_dir)
    
    if not temp_path.exists():
        return 0
    
    # Find all matching files
    files = list(temp_path.glob(pattern))
    
    if not files:
        return 0
    
    # Sort by modification time (newest first)
    files.sort(key=lambda f: f.stat().st_mtime, reverse=True)
    
    # Determine which files to delete
    files_to_delete = []
    
    if keep_recent > 0:
        # Keep the N most recent files
        files_to_delete = files[keep_recent:]
    elif max_age_hours is not None:
        # Delete files older than max_age_hours
        cutoff_time = datetime.now() - timedelta(hours=max_age_hours)
        cutoff_timestamp = cutoff_time.timestamp()
        
        files_to_delete = [
            f for f in files
            if f.stat().st_mtime < cutoff_timestamp
        ]
    else:
        # Delete all files
        files_to_delete = files
    
    # Delete files
    deleted_count = 0
    for file_path in files_to_delete:
        try:
            file_path.unlink()
            deleted_count += 1
        except Exception as e:
            # Silently skip files that can't be deleted
            pass
    
    return deleted_count

def cleanup_old_recordings(temp_dir: str, max_age_hours: float = 24) -> int:
    """
    Clean up old recording files (convenience wrapper).
    
    Args:
        temp_dir: Directory containing recordings
        max_age_hours: Delete recordings older than this many hours
    
    Returns:
        Number of files deleted
    """
    return cleanup_temp_files(
        temp_dir,
        pattern="recording_*.wav",
        max_age_hours=max_age_hours
    )

# ============================================================================
# AUDIO FORMAT UTILITIES
# ============================================================================

def bytes_to_samples(audio_data: bytes, sample_width: int = 2) -> List[int]:
    """
    Convert raw audio bytes to a list of sample values.
    
    Args:
        audio_data: Raw PCM audio bytes
        sample_width: Bytes per sample (2 for int16)
    
    Returns:
        List of integer sample values
    """
    if sample_width == 2:
        format_str = f"{len(audio_data) // 2}h"
        return list(struct.unpack(format_str, audio_data))
    elif sample_width == 4:
        format_str = f"{len(audio_data) // 4}i"
        return list(struct.unpack(format_str, audio_data))
    else:
        raise ValueError(f"Unsupported sample width: {sample_width}")

def samples_to_bytes(samples: List[int], sample_width: int = 2) -> bytes:
    """
    Convert a list of sample values to raw audio bytes.
    
    Args:
        samples: List of integer sample values
        sample_width: Bytes per sample (2 for int16)
    
    Returns:
        Raw PCM audio bytes
    """
    if sample_width == 2:
        format_str = f"{len(samples)}h"
        return struct.pack(format_str, *samples)
    elif sample_width == 4:
        format_str = f"{len(samples)}i"
        return struct.pack(format_str, *samples)
    else:
        raise ValueError(f"Unsupported sample width: {sample_width}")

def get_audio_duration(audio_data: bytes, sample_rate: int, sample_width: int = 2) -> float:
    """
    Calculate the duration of raw audio data in seconds.
    
    Args:
        audio_data: Raw PCM audio bytes
        sample_rate: Sample rate in Hz
        sample_width: Bytes per sample
    
    Returns:
        Duration in seconds
    """
    num_samples = len(audio_data) // sample_width
    duration = num_samples / sample_rate
    return duration

# ============================================================================
# AUDIO VALIDATION
# ============================================================================

def is_silent(audio_data: bytes, threshold: float, sample_width: int = 2) -> bool:
    """
    Check if audio data is below the silence threshold.
    
    Args:
        audio_data: Raw PCM audio bytes
        threshold: RMS threshold for silence
        sample_width: Bytes per sample
    
    Returns:
        True if audio is silent (below threshold), False otherwise
    """
    rms = calculate_rms(audio_data, sample_width)
    return rms < threshold

def has_speech(audio_data: bytes, threshold: float, sample_width: int = 2) -> bool:
    """
    Check if audio data contains speech (above threshold).
    
    Args:
        audio_data: Raw PCM audio bytes
        threshold: RMS threshold for speech detection
        sample_width: Bytes per sample
    
    Returns:
        True if audio contains speech (above threshold), False otherwise
    """
    return not is_silent(audio_data, threshold, sample_width)

# ============================================================================
# TESTING / DEMO
# ============================================================================

if __name__ == "__main__":
    """Demo audio utilities."""
    import tempfile
    
    print("=" * 70)
    print("AUDIO UTILITIES DEMO")
    print("=" * 70)
    
    # Test RMS calculation
    print("\n1. RMS Calculation:")
    # Generate some test audio data (sine wave)
    sample_rate = 16000
    duration = 1.0  # seconds
    frequency = 440  # Hz (A4 note)
    
    t = np.linspace(0, duration, int(sample_rate * duration))
    audio_signal = (np.sin(2 * np.pi * frequency * t) * 32767 * 0.5).astype(np.int16)
    audio_bytes = audio_signal.tobytes()
    
    rms = calculate_rms(audio_bytes)
    print(f"   RMS of 440Hz sine wave: {rms:.2f}")
    
    # Test silence detection
    silence_threshold = 500
    is_speech = has_speech(audio_bytes, silence_threshold)
    print(f"   Contains speech (threshold={silence_threshold}): {is_speech}")
    
    # Test WAV file operations
    print("\n2. WAV File Operations:")
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
        temp_path = tmp.name
    
    saved_path = save_wav(temp_path, audio_bytes, sample_rate=sample_rate)
    print(f"   Saved WAV: {saved_path}")
    
    loaded_data, loaded_sr, channels, width = load_wav(saved_path)
    print(f"   Loaded: {len(loaded_data)} bytes, {loaded_sr}Hz, {channels}ch, {width}B/sample")
    
    duration = get_wav_duration(saved_path)
    print(f"   Duration: {duration:.2f} seconds")
    
    # Clean up
    os.unlink(saved_path)
    
    # Test temp filename generation
    print("\n3. Temp Filename Generation:")
    for i in range(3):
        filename = generate_temp_filename("test")
        print(f"   {filename}")
    
    # Test cleanup (with a temp directory)
    print("\n4. Temp File Cleanup:")
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create some test files
        for i in range(5):
            test_file = Path(tmpdir) / f"recording_{i}.wav"
            test_file.write_bytes(b"test")
        
        print(f"   Created 5 test files in {tmpdir}")
        
        # Keep only 2 most recent
        deleted = cleanup_temp_files(tmpdir, pattern="*.wav", keep_recent=2)
        print(f"   Deleted {deleted} files (kept 2 most recent)")
        
        remaining = len(list(Path(tmpdir).glob("*.wav")))
        print(f"   Remaining files: {remaining}")
    
    print("\n" + "=" * 70)
    print("Demo complete!")
    print("=" * 70)
