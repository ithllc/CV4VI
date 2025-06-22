import streamlit as st
import os
import asyncio
import openai
from streamlit_mic_recorder import mic_recorder

# Import the modules for each phase
from camera_controller import get_camera_feed_screenshot
from moondream_analyzer import load_model, get_moondream_analysis
from voice_pipeline import transcribe_user_request_realtime, generate_assistant_speech_realtime
from location_parser import extract_and_normalize_location

st.set_page_config(page_title="AI Street Crossing Assistant", layout="wide")

st.title("AI Street Crossing Assistant")
st.markdown("Ask if it's safe to cross the street at a specific location in NYC.")

# --- API Key and Model Loading ---
if 'openai_api_key' not in st.session_state:
    try:
        st.session_state.openai_api_key = st.secrets["OPENAI_API_KEY"]
    except (FileNotFoundError, KeyError):
        st.session_state.openai_api_key = st.text_input("Enter your OpenAI API Key:", type="password")

if not st.session_state.openai_api_key:
    st.warning("Please enter your OpenAI API Key to continue.")
    st.stop()

client = openai.AsyncOpenAI(api_key=st.session_state.openai_api_key)

@st.cache_resource
def cached_load_model():
    return load_model()

with st.spinner("Loading the vision model... This may take a moment."):
    model, tokenizer = cached_load_model()

if not model or not tokenizer:
    st.error("Failed to load the Moondream model. Please check the logs.")
    st.stop()

# --- Main Application Flow ---

st.markdown("### Press the button and ask your question")

audio_bytes = mic_recorder(
    start_prompt="▶️ Ask if it's safe to cross (e.g., 'I'm at 1st Avenue and 110th Street, can I cross?')",
    stop_prompt="⏹️ Processing...",
    key='recorder'
)

if audio_bytes:
    async def main_pipeline():
        # Step 1: Transcribe the user's request
        with st.spinner('Understanding your request...'):
            user_query = await transcribe_user_request_realtime(audio_bytes['bytes'], client)
            if not user_query:
                st.error("Could not understand your request. Please try again.")
                return
            st.write(f"**You asked:** *{user_query}*")

        # Step 2: Extract and normalize the location from the query
        location_query = extract_and_normalize_location(user_query)
        if not location_query:
            error_message = "Sorry, I couldn't identify a location in your request. Please try again and state the location clearly, for example: 'I'm at 1st Avenue and 110th Street.'"
            st.error(error_message)
            with st.spinner('Preparing audio response...'):
                speech_audio_bytes = await generate_assistant_speech_realtime(error_message, client)
                if speech_audio_bytes:
                    st.audio(speech_audio_bytes, format="audio/wav")
            return
        
        st.write(f"**Location identified:** *{location_query}*")

        # Step 3: Get the camera feed screenshot
        with st.spinner(f'Accessing traffic camera for {location_query}...'):
            image_path = get_camera_feed_screenshot(location_query)

        if image_path is None:
            error_message = f"Sorry, I couldn't access the camera feed for '{location_query}'. Please try another location."
            st.error(error_message)
            with st.spinner('Preparing audio response...'):
                speech_audio_bytes = await generate_assistant_speech_realtime(error_message, client)
                if speech_audio_bytes:
                    st.audio(speech_audio_bytes, format="audio/wav")
            return

        # Step 4: Display the screenshot
        st.image(image_path, caption=f"Live Camera View for {location_query}")

        # Step 5: Analyze the image with Moondream
        with st.spinner('Analyzing the view...'):
            analysis_text = get_moondream_analysis(model, tokenizer, image_path)

        # Step 6: Generate and play the audio response
        st.success(f"**Assistant's Assessment:** {analysis_text}")
        with st.spinner('Preparing audio response...'):
            speech_audio_bytes = await generate_assistant_speech_realtime(analysis_text, client)
            if speech_audio_bytes:
                st.audio(speech_audio_bytes, format="audio/wav")
            else:
                st.error("Could not generate audio response.")

    # Run the async pipeline
    asyncio.run(main_pipeline())
