# Voice Browser Agent - Quick Start Guide

## 🚀 What's Working Now

### ✅ Completed Components (50%)

1. **Project Scaffolding** - Complete configuration and structure
2. **Colored Logger** - Stage-specific colored logging
3. **Audio Utilities** - RMS, WAV operations, temp file management
4. **Mic Recorder** - PyAudio recording with silence detection
5. **Whisper Transcriber** - Speech-to-text with confidence scoring

### ⏳ Pending Components (50%)

6. **Agent Core** - LLM prompts, tools, dispatcher, loop
7. **Browser Automation** - Playwright integration
8. **Text-to-Speech** - Voice output
9. **Memory Management** - Context and session persistence
10. **Main Application** - Complete integration

---

## 🧪 Try It Now!

### Test 1: Colored Logger
```bash
python test_logger.py
```
See the pipeline stages with different colors.

### Test 2: Audio Recorder
```bash
python test_recorder.py
```
Record audio from your microphone with silence detection.

### Test 3: Whisper Transcriber
```bash
python test_transcriber.py
```
Record and transcribe speech to text.

### Test 4: Complete Voice Pipeline
```bash
python test_voice_pipeline.py
```
Full voice input: Record → Transcribe

---

## 📋 Installation

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Install Playwright Browsers
```bash
playwright install chromium
```

### 3. Configure Environment
Copy `.env.example` to `.env` and add your API keys:
```bash
copy .env.example .env  # Windows
# or
cp .env.example .env    # Linux/Mac
```

Edit `.env` and set:
```env
GROQ_API_KEY=your_groq_api_key_here
```

Get your Groq API key from: https://console.groq.com

---

## 🎯 Current Capabilities

### Voice Input ✅
```python
from voice import record_audio, transcribe_audio

# Record from microphone
wav_path = record_audio()

# Transcribe to text
text = transcribe_audio(wav_path)

print(f"You said: {text}")
```

### Audio Processing ✅
```python
from utils import calculate_rms, save_wav, cleanup_temp_files

# Calculate audio energy
rms = calculate_rms(audio_bytes)

# Save to WAV
save_wav("output.wav", audio_bytes, sample_rate=16000)

# Clean up old files
cleanup_temp_files("temp/", max_age_hours=24)
```

### Logging ✅
```python
from utils import (
    log_voice_info,
    log_transcribe_info,
    log_agent_info,
    log_browser_info,
    log_tts_info,
)

log_voice_info("Recording started")
log_transcribe_info("Transcribing audio...")
log_agent_info("Processing command...")
log_browser_info("Opening browser...")
log_tts_info("Speaking response...")
```

---

## 🔧 Configuration

### Audio Settings (`.env`)
```env
# Sample rate (16000 Hz recommended for speech)
SAMPLE_RATE=16000

# Frame duration (20-30ms optimal)
FRAME_DURATION_MS=30

# Silence detection
SILENCE_THRESHOLD=500      # Lower = more sensitive
SILENCE_DURATION=2.0       # Seconds of silence to stop

# Recording limits
MIN_RECORDING_DURATION=0.5
MAX_RECORDING_DURATION=30.0

# Pre-roll buffer (captures early speech)
PRE_ROLL_DURATION=0.3
```

### Whisper Settings (`.env`)
```env
# Model size: tiny, base, small, medium, large
WHISPER_MODEL=base

# Language (empty = auto-detect)
# WHISPER_LANGUAGE=en
```

### Logging Settings (`.env`)
```env
# Log level: DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_LEVEL=INFO

# Save logs to file
LOG_TO_FILE=false
```

---

## 📊 What Each Test Does

### `test_logger.py`
- Demonstrates colored logging for each pipeline stage
- Shows VOICE (cyan), TRANSCRIBE (magenta), AGENT (green), BROWSER (blue), TTS (yellow)

### `test_recorder.py`
- Records audio from your microphone
- Uses silence detection to auto-stop
- Saves to temp WAV file
- Shows duration and file info

### `test_transcriber.py`
- Records audio (or uses existing file)
- Transcribes with Whisper
- Shows transcription text
- Displays confidence metrics

### `test_voice_pipeline.py`
- Complete voice input pipeline
- Record → Transcribe
- Shows what would happen next (agent processing)

---

## 🎨 Colored Logging

Each pipeline stage has its own color:

- 🔵 **VOICE** (Cyan) - Microphone recording
- 🟣 **TRANSCRIBE** (Magenta) - Speech-to-text
- 🟢 **AGENT** (Green) - LLM thinking
- 🔵 **BROWSER** (Blue) - Web automation
- 🟡 **TTS** (Yellow) - Text-to-speech
- ⚪ **SYSTEM** (White) - System messages

---

## 📁 Project Structure

```
voice-browser-agent/
├── config.py              # Configuration
├── .env                   # Environment variables
├── requirements.txt       # Dependencies
│
├── voice/                 # Voice I/O
│   ├── recorder.py        # ✅ Audio recording
│   ├── transcriber.py     # ✅ Speech-to-text
│   └── speaker.py         # ⏳ Text-to-speech
│
├── agent/                 # ⏳ Agent logic
│   ├── loop.py
│   ├── prompts.py
│   ├── tools.py
│   └── dispatcher.py
│
├── browser/               # ⏳ Browser automation
│   ├── manager.py
│   ├── actions.py
│   └── utils.py
│
├── memory/                # ⏳ Context management
│   ├── context.py
│   └── session.py
│
└── utils/                 # Utilities
    ├── logger.py          # ✅ Colored logging
    └── audio_utils.py     # ✅ Audio helpers
```

---

## 🐛 Troubleshooting

### PyAudio Installation Issues

**Windows:**
```bash
pip install pipwin
pipwin install pyaudio
```

**macOS:**
```bash
brew install portaudio
pip install pyaudio
```

**Linux:**
```bash
sudo apt-get install python3-pyaudio
```

### Microphone Not Working

1. Check system microphone permissions
2. Verify default input device
3. Adjust `SILENCE_THRESHOLD` in `.env`
4. List devices:
```bash
python -c "import pyaudio; p=pyaudio.PyAudio(); [print(f'{i}: {p.get_device_info_by_index(i)[\"name\"]}') for i in range(p.get_device_count())]"
```

### Whisper Model Loading Slow

First load is slow (downloads model). Subsequent loads are fast (cached).

Model sizes:
- `tiny`: Fastest, lowest accuracy
- `base`: **Recommended** - good balance
- `small`: Better accuracy, slower
- `medium`/`large`: Best accuracy, very slow

---

## 📚 Documentation

- `README.md` - Project overview
- `LOGGER_IMPLEMENTATION.md` - Colored logger details
- `RECORDER_IMPLEMENTATION.md` - Audio recorder details
- `TRANSCRIBER_IMPLEMENTATION.md` - Whisper transcriber details
- `IMPLEMENTATION_STATUS.md` - Current progress
- `QUICK_START.md` - This file

---

## 🎯 Next Steps

To complete the project, we need to implement:

1. **Agent Core** - LLM integration with Groq
2. **Browser Automation** - Playwright actions
3. **Text-to-Speech** - Voice output
4. **Memory Management** - Context tracking
5. **Main Loop** - Tie everything together

---

## 💡 Example Usage (When Complete)

```python
# This will work once all components are implemented:

from main import VoiceBrowserAgent

agent = VoiceBrowserAgent()
agent.run()

# User speaks: "Open GitHub and search for Python projects"
# → Records audio
# → Transcribes: "Open GitHub and search for Python projects"
# → Agent processes command
# → Browser opens GitHub
# → Browser searches for "Python projects"
# → Agent speaks: "I've opened GitHub and searched for Python projects"
```

---

## 🤝 Contributing

The project is 50% complete. Contributions welcome!

Focus areas:
- Agent core implementation
- Browser automation
- TTS integration
- Testing and documentation

---

**Last Updated:** 2026-05-16  
**Status:** 50% Complete (5/10 components)
