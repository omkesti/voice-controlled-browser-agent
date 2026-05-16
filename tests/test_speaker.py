"""
Test script for the TTS Speaker.
Run with: python test_speaker.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from voice import Speaker, speak_text
from utils import log_header, log_system_info, log_success, log_error

def test_basic_speech():
    """Test basic speech functionality."""
    
    log_header("TTS SPEAKER TEST - Basic Speech")
    
    log_system_info("Testing basic text-to-speech...")
    log_system_info("")
    
    try:
        speaker = Speaker()
        
        # Test 1: Simple greeting
        log_system_info("Test 1: Simple greeting")
        success = speaker.speak("Hello! Welcome to the Voice Browser Agent.")
        
        if success:
            log_success("Test 1 passed", "SYSTEM")
        else:
            log_error("Test 1 failed", "SYSTEM")
        
        log_system_info("")
        
        # Test 2: Multiple sentences
        log_system_info("Test 2: Multiple sentences")
        success = speaker.speak(
            "This is a test. I can speak multiple sentences. "
            "Each one is processed separately for natural pauses."
        )
        
        if success:
            log_success("Test 2 passed", "SYSTEM")
        else:
            log_error("Test 2 failed", "SYSTEM")
        
        log_system_info("")
        
        # Test 3: Questions and exclamations
        log_system_info("Test 3: Questions and exclamations")
        success = speaker.speak(
            "Great! This works well. How about questions? Yes, those work too!"
        )
        
        if success:
            log_success("Test 3 passed", "SYSTEM")
        else:
            log_error("Test 3 failed", "SYSTEM")
        
        log_system_info("")
        log_success("All basic tests completed!", "SYSTEM")
        
    except Exception as e:
        log_error(f"Test failed: {e}", "SYSTEM")
        import traceback
        traceback.print_exc()
        sys.exit(1)

def test_long_text():
    """Test long text with sentence splitting."""
    
    log_header("TTS SPEAKER TEST - Long Text")
    
    log_system_info("Testing long text with automatic sentence splitting...")
    log_system_info("")
    
    try:
        speaker = Speaker()
        
        long_text = (
            "The Voice Browser Agent is a Python application that listens to your voice, "
            "transcribes it using Whisper, and sends the transcription to an LLM. "
            "The LLM can then control a web browser using Playwright, performing actions "
            "like clicking, typing, and navigating. Finally, the results are spoken back "
            "to you using text-to-speech. This creates a complete voice-controlled "
            "browser automation system."
        )
        
        log_system_info(f"Text length: {len(long_text)} characters")
        log_system_info("")
        
        success = speaker.speak(long_text)
        
        if success:
            log_success("Long text test passed", "SYSTEM")
        else:
            log_error("Long text test failed", "SYSTEM")
        
    except Exception as e:
        log_error(f"Test failed: {e}", "SYSTEM")
        import traceback
        traceback.print_exc()
        sys.exit(1)

def test_convenience_function():
    """Test the convenience function."""
    
    log_header("TTS SPEAKER TEST - Convenience Function")
    
    log_system_info("Testing speak_text() convenience function...")
    log_system_info("")
    
    try:
        success = speak_text("This is a test of the convenience function.")
        
        if success:
            log_success("Convenience function test passed", "SYSTEM")
        else:
            log_error("Convenience function test failed", "SYSTEM")
        
    except Exception as e:
        log_error(f"Test failed: {e}", "SYSTEM")
        import traceback
        traceback.print_exc()
        sys.exit(1)

def test_interactive():
    """Interactive test - speak user input."""
    
    log_header("TTS SPEAKER TEST - Interactive")
    
    log_system_info("Enter text to speak (or 'quit' to exit):")
    log_system_info("")
    
    speaker = Speaker()
    
    while True:
        try:
            text = input("Text to speak: ").strip()
            
            if not text:
                continue
            
            if text.lower() in ['quit', 'exit', 'q']:
                log_system_info("Exiting...")
                break
            
            success = speaker.speak(text)
            
            if not success:
                log_error("Speech failed", "SYSTEM")
            
            print()
            
        except KeyboardInterrupt:
            log_system_info("\n\nExiting...")
            break
        except Exception as e:
            log_error(f"Error: {e}", "SYSTEM")

def main():
    """Main test function."""
    
    if len(sys.argv) > 1:
        # Interactive mode
        if sys.argv[1] == "interactive":
            test_interactive()
        else:
            # Speak command line argument
            text = ' '.join(sys.argv[1:])
            log_header("TTS SPEAKER TEST - Command Line")
            log_system_info(f"Speaking: {text}")
            log_system_info("")
            speak_text(text)
    else:
        # Run all tests
        test_basic_speech()
        print()
        test_long_text()
        print()
        test_convenience_function()
        print()
        log_header("ALL TESTS COMPLETE")

if __name__ == "__main__":
    main()
