import streamlit as st
from streamlit_mic_recorder import mic_recorder
import openai
import os
import sys

# Add the project root to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, project_root)

from AICHackathon.testing.individual_component_tests.test_selenium_flow import get_camera_screenshot
from AICHackathon.testing.test_moondream_helper import load_model, describe_image

# --- App Configuration ---
st.set_page_config(page_title="Street Crossing Assistant", page_icon="횡단보도")
st.title("AI Street Crossing Assistant")

# --- OpenAI API Key ---
if "openai_api_key" not in st.session_state:
    st.session_state.openai_api_key = os.environ.get("OPENAI_API_KEY")

if not st.session_state.openai_api_key:
    st.session_state.openai_api_key = st.text_input("Enter your OpenAI API Key:", type="password")

if st.session_state.openai_api_key:
    client = openai.OpenAI(api_key=st.session_state.openai_api_key)
else:
    st.warning("Please enter your OpenAI API Key to proceed.")
    st.stop()

# --- Load Moondream2 Model ---
with st.spinner("Loading vision model..."):
    model, tokenizer = load_model()
st.success("Vision model loaded.")

# --- Main Application Logic ---
st.header("Street Crossing Check")

camera_name = st.text_input("Enter the camera name:", "1 Ave @ 110 St")

if st.button("Check Street"):
    if camera_name:
        with st.spinner("Getting camera feed..."):
            screenshot_path = "camera_feed.png"
            get_camera_screenshot(camera_name, screenshot_path)
        
        if os.path.exists(screenshot_path):
            st.image(screenshot_path, caption="Live Camera Feed")
            with st.spinner("Analyzing image..."):
                description = describe_image(model, tokenizer, screenshot_path)
                st.write(f"**Description:** {description}")

                with st.spinner("Generating audio description..."):
                    try:
                        response = client.audio.speech.create(
                            model="tts-1",
                            voice="alloy",
                            input=description
                        )
                        st.audio(response.content)
                    except Exception as e:
                        st.error(f"Error during TTS generation: {e}")
        else:
            st.error("Could not retrieve camera feed.")
    else:
        st.warning("Please enter a camera name.")

# --- Speech-to-Text ---
st.header("Speech-to-Text")

audio = mic_recorder(start_prompt="Start recording", stop_prompt="Stop recording", key='recorder')

if audio:
    st.audio(audio['bytes'])
    with st.spinner("Transcribing..."):
        try:
            # The API expects a file-like object, so we write the bytes to a temporary file
            with open("audio.wav", "wb") as f:
                f.write(audio['bytes'])
            audio_file = open("audio.wav", "rb")
            transcript = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file
            )
            st.write(f"**Transcription:** {transcript.text}")
        except Exception as e:
            st.error(f"Error during transcription: {e}")

# --- Text-to-Speech ---
st.header("Text-to-Speech")

text_to_speak = st.text_area("Enter text to convert to speech:")

if st.button("Speak"):
    if text_to_speak:
        with st.spinner("Generating audio..."):
            try:
                response = client.audio.speech.create(
                    model="tts-1",
                    voice="alloy",
                    input=text_to_speak
                )
                st.audio(response.content)
            except Exception as e:
                st.error(f"Error during TTS generation: {e}")
    else:
        st.warning("Please enter some text to speak.")
