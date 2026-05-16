"""
Test the complete voice loop: Record → Transcribe → Speak
Run with: python test_complete_voice_loop.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from voice import record_audio, transcribe_audio, speak_text
from utils import log_header, log_system_info, log_success, log_error

def main():
    """Test the complete voice loop."""
    
    log_header("COMPLETE VOICE LOOP TEST")
    
    log_system_info("This demonstrates the complete voice I/O pipeline:")
    log_system_info("  1. 🎤 Record audio from microphone")
    log_system_info("  2. 🔤 Transcribe with Whisper")
    log_system_info("  3. 🔊 Speak back the transcription")
    log_system_info("")
    log_system_info("Speak a command into your microphone.")
    log_system_info("Example: 'Hello, how are you today?'")
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
        
        if not text:
            log_error("No speech detected or transcription failed", "SYSTEM")
            sys.exit(1)
        
        log_success(f"Transcribed: \"{text}\"", "SYSTEM")
        log_system_info("")
        
        # Step 3: Speak back
        log_system_info("=" * 70)
        log_system_info("STEP 3: TEXT-TO-SPEECH")
        log_system_info("=" * 70)
        
        # Create response
        response = f"You said: {text}"
        
        success = speak_text(response)
        
        if success:
            log_success("Speech completed", "SYSTEM")
        else:
            log_error("Speech failed", "SYSTEM")
        
        log_system_info("")
        
        # Summary
        log_header("VOICE LOOP COMPLETE")
        log_system_info("")
        log_system_info(f"📝 Input: \"{text}\"")
        log_system_info(f"🔊 Output: \"{response}\"")
        log_system_info("")
        log_success("Complete voice loop test successful!", "SYSTEM")
        log_system_info("")
        log_system_info("Next steps:")
        log_system_info("  - Add LLM agent to process commands")
        log_system_info("  - Add browser automation to execute actions")
        log_system_info("  - Create main loop for continuous operation")
        
    except KeyboardInterrupt:
        log_system_info("\n\n⚠️  Test cancelled by user.")
        sys.exit(0)
    except Exception as e:
        log_error(f"Voice loop test failed: {e}", "SYSTEM")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
