"""
Test script for the Whisper Transcriber.
Run with: python test_transcriber.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from voice import record_audio, Transcriber
from utils import log_header, log_system_info, log_success, log_error

def test_with_recording():
    """Test transcriber with a new recording."""
    
    log_header("WHISPER TRANSCRIBER TEST")
    
    log_system_info("This will:")
    log_system_info("  1. Record audio from your microphone")
    log_system_info("  2. Transcribe it using Whisper")
    log_system_info("  3. Display the transcription and confidence")
    log_system_info("")
    log_system_info("Speak clearly into your microphone, then stay silent for 2 seconds.")
    log_system_info("Press Ctrl+C to cancel anytime.")
    log_system_info("")
    
    try:
        # Step 1: Record audio
        log_system_info("Step 1: Recording audio...")
        wav_path = record_audio()
        log_success(f"Recorded: {Path(wav_path).name}", "SYSTEM")
        log_system_info("")
        
        # Step 2: Transcribe
        log_system_info("Step 2: Transcribing with Whisper...")
        transcriber = Transcriber()
        
        # Get full metadata
        result = transcriber.transcribe_with_metadata(wav_path)
        
        if result:
            log_header("TRANSCRIPTION RESULT")
            
            log_system_info(f"📝 Text: {result['text']}")
            log_system_info(f"🌍 Language: {result['language']}")
            
            if result['confidence']:
                conf = result['confidence']
                log_system_info("")
                log_system_info("📊 Confidence Metrics:")
                
                if 'confidence_pct' in conf:
                    confidence_pct = conf['confidence_pct']
                    emoji = "🟢" if confidence_pct > 80 else "🟡" if confidence_pct > 60 else "🔴"
                    log_system_info(f"  {emoji} Confidence: {confidence_pct:.1f}%")
                
                if 'avg_logprob' in conf:
                    log_system_info(f"  📈 Avg log prob: {conf['avg_logprob']:.3f}")
                
                if 'num_segments' in conf:
                    log_system_info(f"  🔢 Segments: {conf['num_segments']}")
                
                if 'avg_no_speech_prob' in conf:
                    no_speech = conf['avg_no_speech_prob']
                    log_system_info(f"  🔇 No-speech prob: {no_speech:.3f}")
            
            log_system_info("")
            log_success("Transcription complete!", "SYSTEM")
            
        else:
            log_error("No speech detected or transcription failed", "SYSTEM")
        
    except KeyboardInterrupt:
        log_system_info("\n\n⚠️  Test cancelled by user.")
        sys.exit(0)
    except Exception as e:
        log_error(f"Test failed: {e}", "SYSTEM")
        import traceback
        traceback.print_exc()
        sys.exit(1)

def test_with_existing_file(audio_path: str):
    """Test transcriber with an existing audio file."""
    
    log_header("WHISPER TRANSCRIBER TEST (Existing File)")
    
    if not Path(audio_path).exists():
        log_error(f"File not found: {audio_path}", "SYSTEM")
        sys.exit(1)
    
    log_system_info(f"Transcribing: {audio_path}")
    log_system_info("")
    
    try:
        transcriber = Transcriber()
        result = transcriber.transcribe_with_metadata(audio_path)
        
        if result:
            log_header("TRANSCRIPTION RESULT")
            
            log_system_info(f"📝 Text: {result['text']}")
            log_system_info(f"🌍 Language: {result['language']}")
            
            if result['confidence']:
                conf = result['confidence']
                log_system_info("")
                log_system_info("📊 Confidence Metrics:")
                
                if 'confidence_pct' in conf:
                    confidence_pct = conf['confidence_pct']
                    emoji = "🟢" if confidence_pct > 80 else "🟡" if confidence_pct > 60 else "🔴"
                    log_system_info(f"  {emoji} Confidence: {confidence_pct:.1f}%")
                
                if 'avg_logprob' in conf:
                    log_system_info(f"  📈 Avg log prob: {conf['avg_logprob']:.3f}")
            
            log_system_info("")
            log_success("Transcription complete!", "SYSTEM")
        else:
            log_error("No speech detected or transcription failed", "SYSTEM")
    
    except Exception as e:
        log_error(f"Test failed: {e}", "SYSTEM")
        import traceback
        traceback.print_exc()
        sys.exit(1)

def main():
    """Main test function."""
    
    if len(sys.argv) > 1:
        # Test with existing file
        audio_path = sys.argv[1]
        test_with_existing_file(audio_path)
    else:
        # Test with new recording
        test_with_recording()

if __name__ == "__main__":
    main()
