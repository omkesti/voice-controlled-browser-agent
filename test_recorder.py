"""
Test script for the AudioRecorder.
Run with: python test_recorder.py
"""

import sys
from pathlib import Path
from voice import record_audio
from utils import log_header, log_system_info, get_wav_duration

def main():
    """Test the audio recorder."""
    
    log_header("AUDIO RECORDER TEST")
    
    log_system_info("This will record audio from your microphone.")
    log_system_info("Instructions:")
    log_system_info("  1. Speak clearly into your microphone")
    log_system_info("  2. Stay silent for 2 seconds to stop recording")
    log_system_info("  3. Press Ctrl+C to cancel anytime")
    log_system_info("")
    
    try:
        # Record audio
        wav_path = record_audio()
        
        # Show results
        log_header("RECORDING COMPLETE")
        
        duration = get_wav_duration(wav_path)
        file_size = Path(wav_path).stat().st_size
        
        log_system_info(f"✓ File: {Path(wav_path).name}")
        log_system_info(f"✓ Duration: {duration:.2f} seconds")
        log_system_info(f"✓ Size: {file_size:,} bytes ({file_size/1024:.1f} KB)")
        log_system_info(f"✓ Location: {wav_path}")
        log_system_info("")
        log_system_info("You can play this file with any audio player or:")
        log_system_info(f"  python -m sounddevice play {wav_path}")
        
    except KeyboardInterrupt:
        log_system_info("\n\n⚠️  Recording cancelled by user.")
        sys.exit(0)
    except Exception as e:
        log_system_info(f"\n\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
