"""
Simple test for TTS Speaker (no dependencies on recorder/transcriber).
Run with: python test_speaker_simple.py
"""

import sys
sys.path.insert(0, '.')

# Import only what we need
from voice.speaker import Speaker, speak_text, split_into_sentences
from utils.logger import log_header, log_system_info, log_success

def test_sentence_splitting():
    """Test sentence splitting logic."""
    log_header("TEST: Sentence Splitting")
    
    # Test 1: Simple sentences
    text1 = "Hello there. How are you? I'm doing great!"
    chunks1 = split_into_sentences(text1)
    log_system_info(f"Input: {text1}")
    log_system_info(f"Chunks: {chunks1}")
    log_system_info(f"Count: {len(chunks1)}")
    log_system_info("")
    
    # Test 2: Long sentence with commas
    text2 = "This is a long sentence, with many commas, and lots of words, that should be split."
    chunks2 = split_into_sentences(text2, max_chunk_length=50)
    log_system_info(f"Input: {text2}")
    log_system_info(f"Chunks: {chunks2}")
    log_system_info(f"Count: {len(chunks2)}")
    log_system_info("")
    
    log_success("Sentence splitting test complete", "SYSTEM")

def test_speaker():
    """Test speaker functionality."""
    log_header("TEST: TTS Speaker")
    
    log_system_info("Initializing speaker...")
    speaker = Speaker()
    
    log_system_info("Speaking test message...")
    success = speaker.speak("Hello! This is a test of the text to speech system.")
    
    if success:
        log_success("Speaker test passed!", "SYSTEM")
    else:
        log_system_info("Speaker test completed (check audio output)")

def main():
    """Run tests."""
    test_sentence_splitting()
    print()
    test_speaker()

if __name__ == "__main__":
    main()
