import asyncio
import os
import logging
import base64
from typing import Optional
import openai
import re

# This path adjustment assumes the script is run in an environment where the SDK is accessible.
# If running from the AICHackathon directory, this might need adjustment.
# For this implementation, we assume the SDK is in the Python path.

# from agents import Agent, Voice, AudioConfig, AudioFormat
# from runner import Runner

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def normalize_spoken_text(text: str) -> str:
    """
    Normalizes spoken text to a more usable format.
    - Converts common spelled-out ordinals to numbers (e.g., "first" -> "1st").
    """
    ordinal_replacements = {
        "first": "1st", "second": "2nd", "third": "3rd", "fourth": "4th",
        "fifth": "5th", "sixth": "6th", "seventh": "7th", "eighth": "8th",
        "ninth": "9th", "tenth": "10th", "eleventh": "11th", "twelfth": "12th"
    }
    
    # This pattern finds whole words from the keys of the dictionary
    pattern = r'\b(' + '|'.join(ordinal_replacements.keys()) + r')\b'

    def replace_ordinal(match):
        word = match.group(0).lower()
        return ordinal_replacements[word]

    # Replace the found ordinals in the text
    normalized_text = re.sub(pattern, replace_ordinal, text, flags=re.IGNORECASE)
    
    return normalized_text

# This is a placeholder for the real-time transcription.
# The actual implementation would require the OpenAI Realtime SDK
# and an asyncio event loop.
async def transcribe_user_request_realtime(audio_bytes: bytes, client: openai.AsyncOpenAI) -> str:
    """
    Transcribes audio bytes using OpenAI's Whisper API and normalizes the text.
    NOTE: This is a non-real-time implementation for demonstration.
    """
    logger.info("Starting transcription...")
    try:
        # The Whisper API expects a file-like object.
        import io
        audio_file = io.BytesIO(audio_bytes)
        audio_file.name = "audio.wav" # The API needs a file name

        transcript = await client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file,
        )
        logger.info(f"Raw transcription: {transcript.text}")
        
        # Normalize the transcribed text
        normalized_text = normalize_spoken_text(transcript.text)
        logger.info(f"Normalized transcription: {normalized_text}")
        
        return normalized_text
    except Exception as e:
        logger.error(f"An error occurred during transcription: {e}")
        return ""

# This is a placeholder for the real-time TTS.
# The actual implementation would require the OpenAI Realtime SDK.
async def generate_assistant_speech_realtime(text: str, client: openai.AsyncOpenAI) -> Optional[bytes]:
    """
    Generates speech from text using OpenAI's TTS API.
    NOTE: This is a non-real-time implementation for demonstration.
    """
    logger.info(f"Generating speech for text: '{text}'")
    try:
        response = await client.audio.speech.create(
            model="tts-1",
            voice="alloy",
            input=text,
        )
        logger.info("Speech generation successful.")
        return response.content
    except Exception as e:
        logger.error(f"An error occurred during TTS generation: {e}")
        return None
