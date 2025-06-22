import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'openai_realtime_voice_agent_sdk'))

import asyncio
import os
import toml
import wave
import logging
from agents import Agent, Voice, AudioConfig, AudioFormat
from runner import Runner
import queue
import threading
import time

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

# PyAudio configuration
CHUNK = 1024
CHANNELS = 1
RATE = 24000 # OpenAI's recommended sample rate
TEST_WAV_PATH = os.path.join(os.path.dirname(__file__), 'test_data', 'silent_5s.wav')

def main():
    """Main function to run the realtime transcription test."""
    
    # --- Agent and Runner Setup ---
    stt_agent = Agent(
        name="Realtime Transcriber",
        model="gpt-4o-realtime-preview-2025-06-03",
        instructions="You are a live transcriber. Your sole purpose is to accurately transcribe the audio you receive.",
        input_audio=AudioConfig(
            format=AudioFormat.PCM16,
            sample_rate=RATE,
            channels=CHANNELS
        ),
        enable_text=True # Enable text output for transcription
    )

    transcription_queue = queue.Queue()

    def on_transcription_update(text: str):
        """Callback function to handle transcription updates."""
        transcription_queue.put(text)

    runner = Runner(stt_agent, is_streaming=True, on_transcript_user=on_transcription_update)

    # --- Audio Input Setup (from file) ---
    try:
        wf = wave.open(TEST_WAV_PATH, 'rb')
        assert wf.getnchannels() == CHANNELS
        assert wf.getframerate() == RATE
        assert wf.getsampwidth() == 2 # 16-bit PCM
    except FileNotFoundError:
        logger.error(f"Test audio file not found at: {TEST_WAV_PATH}")
        return
    except Exception as e:
        logger.error(f"Error opening test audio file: {e}")
        return


    # --- Main Loop ---
    try:
        logger.info("Connecting to OpenAI Realtime API...")
        runner.init()
        logger.info("Starting live transcription... Press Ctrl+C to stop.")
        
        # Start a thread to print transcriptions from the queue
        def print_transcriptions():
            while True:
                try:
                    text = transcription_queue.get(block=False)
                    print(f"Live Transcription: {text}")
                except queue.Empty:
                    time.sleep(0.1) # Avoid busy-waiting

        print_thread = threading.Thread(target=print_transcriptions, daemon=True)
        print_thread.start()

        logger.info(f"Streaming audio from '{TEST_WAV_PATH}'...")
        while True:
            data = wf.readframes(CHUNK)
            if not data:
                logger.info("End of audio file reached.")
                break
            runner._send_audio_input(data)
            time.sleep(float(CHUNK) / RATE) # Simulate real-time streaming

    except KeyboardInterrupt:
        logger.info("User interrupted. Stopping transcription...")
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
    finally:
        # --- Cleanup ---
        logger.info("Cleaning up resources.")
        wf.close()
        runner._disconnect()
        logger.info("Transcription stopped.")

if __name__ == "__main__":
    main()
