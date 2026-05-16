"""
Main entry point for Voice Browser Agent.
Runs the continuous voice -> agent -> browser -> TTS loop.
"""

from typing import Optional

import config
from agent.loop import AgentLoop
from browser.manager import BrowserManager
from utils.audio_utils import cleanup_temp_files
from utils.logger import (
	log_system_info,
	log_system_warning,
	log_system_error,
	log_voice_info,
	log_transcribe_info,
	log_transcribe_warning,
	log_tts_info,
	log_tts_warning,
	log_separator,
	log_header,
)
from voice import AudioRecorder, Transcriber, Speaker


def _is_exit_command(text: Optional[str]) -> bool:
	"""Return True if the transcription matches an exit keyword."""
	if not text:
		return False
	normalized = text.strip().lower()
	return normalized in {kw.lower() for kw in config.EXIT_KEYWORDS}


def main() -> None:
	"""Run the continuous voice interaction loop."""
	log_header("VOICE BROWSER AGENT")
	log_system_info(config.STARTUP_MESSAGE)

	if not config.ENABLE_VOICE_INPUT:
		log_system_error("Voice input disabled by configuration")
		return

	manager = BrowserManager()
	recorder = AudioRecorder()
	transcriber = Transcriber()
	speaker = Speaker()
	agent = AgentLoop()

	try:
		manager.launch()
		log_system_info("Browser ready")

		while True:
			log_separator()
			log_voice_info(config.LISTENING_MESSAGE)

			try:
				wav_path = recorder.record()
			except Exception as e:
				log_system_error(f"Recording failed: {e}")
				continue

			log_transcribe_info(config.PROCESSING_MESSAGE)
			text = transcriber.transcribe(wav_path)

			if not text:
				log_transcribe_warning("No speech detected. Please try again.")
				continue

			if _is_exit_command(text):
				log_system_info("Exit keyword detected. Shutting down...")
				break

			result = agent.run(text)

			if config.ENABLE_VOICE_OUTPUT:
				log_tts_info(config.DONE_MESSAGE)
				success = speaker.speak(result)
				if not success:
					log_tts_warning("TTS playback failed")
			else:
				log_tts_warning("Voice output disabled by configuration")

	except KeyboardInterrupt:
		log_system_info("Interrupted by user. Shutting down...")
	finally:
		try:
			manager.close()
		except Exception:
			pass

		try:
			recorder.close()
		except Exception:
			pass

		Speaker.cleanup()

		deleted = cleanup_temp_files(str(config.TEMP_DIR))
		if deleted:
			log_system_info(f"Cleaned up {deleted} temp file(s)")


if __name__ == "__main__":
	main()
