import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'openai_realtime_voice_agent_sdk'))

import toml
import logging
from agents import Agent, Voice, AudioConfig, AudioFormat
from runner import Runner
import time
import base64
import wave
import threading
import queue

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# --- Configuration ---
try:
    secrets_path = os.path.join(os.path.dirname(__file__), '.streamlit', 'secrets.toml')
    secrets = toml.load(secrets_path)
    os.environ["OPENAI_API_KEY"] = secrets.get("OPENAI_API_KEY")
    if not os.environ["OPENAI_API_KEY"]:
        raise ValueError("OPENAI_API_KEY not found in secrets.toml")
except (FileNotFoundError, ValueError) as e:
    logger.error(f"Error loading OPENAI_API_KEY: {e}")
    sys.exit(1)

class AudioFileWriter:
    """A class to handle writing audio chunks to a WAV file."""
    def __init__(self, filepath, format, channels, rate):
        self.filepath = filepath
        self.format = format
        self.channels = channels
        self.rate = rate
        self.wave_file = None
        self.audio_queue = queue.Queue()
        self.write_thread = threading.Thread(target=self._write_audio, daemon=True)
        self._stop_event = threading.Event()

    def start(self):
        """Start the writing thread."""
        self.wave_file = wave.open(self.filepath, 'wb')
        self.wave_file.setnchannels(self.channels)
        # PyAudio format paInt16 is 2 bytes
        self.wave_file.setsampwidth(2) 
        self.wave_file.setframerate(self.rate)
        self.write_thread.start()
        logger.info(f"Audio file writer started. Saving to {self.filepath}")

    def _write_audio(self):
        """Internal method to write audio from the queue to the file."""
        while not self._stop_event.is_set():
            try:
                chunk = self.audio_queue.get(timeout=1)
                if chunk is None:
                    break
                self.wave_file.writeframes(chunk)
            except queue.Empty:
                continue

    def add_chunk(self, chunk):
        """Add an audio chunk to the queue."""
        self.audio_queue.put(chunk)

    def stop(self):
        """Stop the writing and clean up resources."""
        logger.info("Stopping audio file writer...")
        self._stop_event.set()
        self.audio_queue.put(None)
        self.write_thread.join()
        self.wave_file.close()
        logger.info("Audio file writer stopped.")

def main():
    """Main function to run the realtime TTS test."""
    output_filepath = os.path.join(os.path.dirname(__file__), 'test_data', 'tts_output.wav')
    audio_writer = AudioFileWriter(
        filepath=output_filepath,
        # Based on OpenAI's recommendation and common usage
        format=None, # Not needed for wave file directly, sampwidth is used
        channels=1, 
        rate=24000
    )

    def on_audio_delta_callback(delta: str):
        """Callback to handle audio output from the agent."""
        if delta:
            try:
                audio_chunk = base64.b64decode(delta)
                audio_writer.add_chunk(audio_chunk)
            except Exception as e:
                logger.error(f"Error processing audio chunk: {e}")

    tts_agent = Agent(
        name="Realtime TTS",
        model="gpt-4o-realtime-preview-2025-06-03",
        instructions="You are a helpful assistant. Please say 'Hello, this is a test.'",
        output_audio=AudioConfig(
            format=AudioFormat.PCM16,
            sample_rate=24000,
            channels=1
        ),
        voice=Voice.ALLOY
    )

    runner = Runner(tts_agent, is_streaming=True, on_audio_delta=on_audio_delta_callback)

    try:
        audio_writer.start()
        
        # The agent is instructed to speak, so we don't need to send any text input.
        # We just need to keep the script running to receive the audio.
        logger.info("Agent is running. Waiting for TTS output...")
        time.sleep(10) # Wait for the TTS to complete

    except KeyboardInterrupt:
        logger.info("Interrupted by user.")
    except Exception as e:
        logger.error(f"An error occurred: {e}")
    finally:
        logger.info("Stopping runner and audio writer...")
        runner.stop()
        audio_writer.stop()
        logger.info("Script finished.")

if __name__ == "__main__":
    main()
