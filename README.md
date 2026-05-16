# Voice Browser Agent

> 🎤 Control your web browser with voice commands using AI

A Python application that listens to your voice, transcribes it locally using Whisper, sends the transcription to an LLM, and lets the LLM autonomously control a real Chromium browser via Playwright — clicking, typing, navigating, and reading pages — until the task is done. Then it speaks the result back to you via TTS.

**The loop runs continuously:** you speak → agent acts → agent speaks back → repeat.

---

## 🚀 Quick Start

```bash
# Clone the repository
git clone https://github.com/yourusername/voice-browser-agent.git
cd voice-browser-agent

# Install dependencies
pip install -r requirements.txt

# Install Playwright browsers
playwright install chromium

# Set up your environment variables
cp .env.example .env
# Edit .env and add your API keys

# Run the agent
python main.py
```

---

## ✨ Features

- 🎙️ **Voice Input**: Speak naturally to control your browser
- 🤖 **LLM-Powered**: Uses Groq for fast, intelligent command interpretation
- 🌐 **Browser Automation**: Full Playwright integration for web interactions
- 🔊 **Text-to-Speech**: Hear responses from the agent
- 🔄 **Continuous Loop**: Seamless conversation flow
- 📝 **Session Memory**: Maintains context during your session

---

## 🏗️ Project Structure

```
voice-browser-agent/
├── main.py                 # Entry point — starts the voice loop
├── config.py               # Configuration and constants
├── voice/                  # Voice input/output modules
│   ├── recorder.py         # Microphone recording + silence detection
│   ├── transcriber.py      # Whisper STT
│   └── speaker.py          # TTS output
├── agent/                  # Agent logic
│   ├── loop.py             # Core agent loop
│   ├── prompts.py          # System prompts
│   ├── tools.py            # Tool definitions
│   └── dispatcher.py       # Tool call routing
├── browser/                # Browser automation
│   ├── manager.py          # Playwright lifecycle
│   ├── actions.py          # Browser actions (click, type, navigate)
│   └── utils.py            # Helper utilities
├── memory/                 # Context management
│   ├── context.py          # Message history
│   └── session.py          # Session persistence
└── utils/                  # Utilities
    ├── logger.py           # Logging
    └── audio_utils.py      # Audio helpers
```

---

## 🛠️ Technologies

- **Speech Recognition**: OpenAI Whisper
- **LLM**: Groq (fast, free tier available)
- **Browser Automation**: Playwright
- **Text-to-Speech**: pyttsx3
- **Audio**: PyAudio

---

## 📋 Requirements

- Python 3.8+
- Working microphone
- Internet connection
- Groq API key (free tier available)

---

## 🔧 Installation

### 1. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 2. Install PyAudio (Platform-Specific)

**Windows:**
```bash
pip install pyaudio
```

**macOS:**
```bash
brew install portaudio
pip install pyaudio
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get install python3-pyaudio
```

### 3. Install Playwright Browsers

```bash
playwright install chromium
```

### 4. Set Up Environment Variables

Create a `.env` file in the project root:

```env
GROQ_API_KEY=your_api_key_here
GROQ_MODEL=llama-3.1-70b-versatile
SILENCE_THRESHOLD=500
SILENCE_DURATION=2.0
```

Get your Groq API key from: https://console.groq.com

---

## 🎯 Usage

### Start the Agent

```bash
python main.py
```

### Example Voice Commands

- "Search Google for weather in San Francisco"
- "Go to GitHub and find trending repositories"
- "Open Wikipedia and search for Python programming"
- "Fill the search box with machine learning"
- "Click the login button"

### Stop the Agent

- Press `Ctrl+C` in the terminal
- Or say: "exit" or "quit"

---

## ⚙️ Configuration

Edit `.env` to customize:

- `GROQ_API_KEY`: Your Groq API key (required)
- `GROQ_MODEL`: LLM model to use (default: llama-3.1-70b-versatile)
- `SILENCE_THRESHOLD`: Audio level for silence detection (default: 500)
- `SILENCE_DURATION`: Seconds of silence before processing (default: 2.0)

---

## 🐛 Troubleshooting

### PyAudio Installation Issues

If `pip install pyaudio` fails, see platform-specific solutions in the installation section above.

### Microphone Not Working

- Check system microphone permissions
- Verify microphone is set as default input device
- Adjust `SILENCE_THRESHOLD` in `.env` if needed

### Browser Doesn't Open

```bash
playwright install chromium
```

---

## 🔒 Security & Privacy

- Voice audio is processed locally by Whisper
- Transcribed text is sent to Groq's LLM
- No audio is stored permanently
- Keep your `.env` file secure and never commit it to version control

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

---

## 📄 License

[Add your license here]

---

## 🙏 Acknowledgments

- OpenAI Whisper for speech recognition
- Groq for fast LLM inference
- Playwright for browser automation

---

## 📚 Documentation

> **Note**: Comprehensive documentation is currently being developed. This README will be updated with detailed setup instructions, troubleshooting guides, and usage examples soon.

For now, refer to the code comments and structure above to get started.

---

**Built with ❤️ for voice-controlled automation**
