import streamlit as st
from streamlit_mic_recorder import mic_recorder
import openai
import os

# --- App Configuration ---
st.set_page_config(page_title="Voice Agent", page_icon="🎙️")
st.title("OpenAI Voice Agent")

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
