"""
Test the complete voice pipeline: Record → Transcribe
Run with: python test_voice_pipeline.py
"""

import sys
from voice import record_audio, transcribe_audio
from utils import log_header, log_system_info, log_success, log_error

def main():
    """Test the complete voice input pipeline."""
    
    log_header("VOICE PIPELINE TEST: RECORD → TRANSCRIBE")
    
    log_system_info("This demonstrates the complete voice input pipeline:")
    log_system_info("  1. 🎤 Record audio from microphone")
    log_system_info("  2. 🔤 Transcribe with Whisper")
    log_system_info("")
    log_system_info("Speak a command into your microphone.")
    log_system_info("Example: 'Open GitHub and search for Python projects'")
    log_system_info("")
    log_system_info("Press Ctrl+C to cancel anytime.")
    log_system_info("")
    
    try:
        # Step 1: Record
        log_system_info("=" * 70)
        log_system_info("STEP 1: RECORDING")
        log_system_info("=" * 70)
        
        wav_path = record_audio()
        log_success(f"Recording saved: {wav_path}", "SYSTEM")
        log_system_info("")
        
        # Step 2: Transcribe
        log_system_info("=" * 70)
        log_system_info("STEP 2: TRANSCRIPTION")
        log_system_info("=" * 70)
        
        text = transcribe_audio(wav_path)
        
        if text:
            log_system_info("")
            log_header("PIPELINE COMPLETE")
            log_system_info("")
            log_system_info(f"🎤 You said: \"{text}\"")
            log_system_info("")
            log_success("Voice pipeline test successful!", "SYSTEM")
            log_system_info("")
            log_system_info("Next steps:")
            log_system_info("  - This text would be sent to the LLM agent")
            log_system_info("  - The agent would interpret the command")
            log_system_info("  - Browser actions would be executed")
            log_system_info("  - Results would be spoken back via TTS")
        else:
            log_error("No speech detected or transcription failed", "SYSTEM")
            log_system_info("")
            log_system_info("Possible reasons:")
            log_system_info("  - Audio was too quiet (adjust SILENCE_THRESHOLD)")
            log_system_info("  - Recording was too short")
            log_system_info("  - Only background noise was captured")
        
    except KeyboardInterrupt:
        log_system_info("\n\n⚠️  Test cancelled by user.")
        sys.exit(0)
    except Exception as e:
        log_error(f"Pipeline test failed: {e}", "SYSTEM")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
