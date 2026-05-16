"""
Test script to demonstrate the colored logger functionality.
Run with: python test_logger.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from utils import (
    log_voice_info,
    log_transcribe_info,
    log_agent_info,
    log_browser_info,
    log_tts_info,
    log_system_info,
    log_success,
    log_header,
)

def main():
    """Demonstrate the voice browser agent pipeline with colored logging."""
    
    log_header("VOICE BROWSER AGENT - PIPELINE DEMO")
    
    # Simulate the voice input stage
    log_voice_info("🎤 Listening for voice input...")
    log_voice_info("Recording started")
    log_voice_info("Silence detected, stopping recording")
    
    # Simulate transcription
    log_transcribe_info("🔤 Transcribing audio with Whisper...")
    log_transcribe_info("Transcription complete: 'Open GitHub and search for Python projects'")
    
    # Simulate agent processing
    log_agent_info("🤖 Processing command with LLM...")
    log_agent_info("LLM response received")
    log_agent_info("Tool call: navigate(url='https://github.com')")
    log_agent_info("Tool call: search(query='Python projects')")
    
    # Simulate browser actions
    log_browser_info("🌐 Launching browser...")
    log_browser_info("Navigating to: https://github.com")
    log_browser_info("Page loaded successfully")
    log_browser_info("Finding search box...")
    log_browser_info("Typing: 'Python projects'")
    log_browser_info("Submitting search...")
    log_browser_info("Search results loaded")
    
    # Simulate TTS output
    log_tts_info("🔊 Speaking response...")
    log_tts_info("Output: 'I've opened GitHub and searched for Python projects. Here are the results.'")
    
    # Complete
    log_success("✅ Task completed successfully!", "SYSTEM")
    log_system_info("Ready for next command...")

if __name__ == "__main__":
    main()
