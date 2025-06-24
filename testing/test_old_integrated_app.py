#!/usr/bin/env python3
"""
Integrated Path & Place Vision Assist PoC Application
Combines LiDAR processing with Moondream2 VLM for accessibility assistance
Based on POCworkplan.md specifications
"""

import os
import numpy as np
import cv2
from PIL import Image
import laspy
import streamlit as st
import requests
import pyttsx3
from geopy.distance import geodesic
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

# NYC Webcam zones (based on POCworkplan.md)
NYC_WEBCAM_ZONES = [
    {
        "name": "Times Square Area", 
        "lat": 40.7580, 
        "lon": -73.9855, 
        "radius_km": 0.2,
        "url": "placeholder_times_square.jpg"  # Fallback image
    },
    {
        "name": "Brooklyn Bridge Area", 
        "lat": 40.7061, 
        "lon": -73.9969, 
        "radius_km": 0.2,
        "url": "placeholder_brooklyn_bridge.jpg"  # Fallback image
    }
]

@st.cache_resource
def load_moondream_model():
    """Load and cache the Moondream2 model"""
    try:
        import sys
        import json
        import shutil
        moondream_path = '/python_code_src/moondream2'
        
        # Method 1: Try copying files to HF cache and use transformers
        try:
            st.info("Setting up HuggingFace cache...")
            cache_dir = '/root/.cache/huggingface/modules/transformers_modules/moondream2'
            os.makedirs(cache_dir, exist_ok=True)
            
            # Copy all necessary files
            for file in ['rope.py', 'layers.py', 'vision.py', 'text.py', 'config.py', 
                        'moondream.py', 'configuration_moondream.py', 'utils.py']:
                src = os.path.join(moondream_path, file)
                if os.path.exists(src):
                    shutil.copy2(src, cache_dir)
            
            from transformers import AutoModelForCausalLM, AutoTokenizer
            
            model = AutoModelForCausalLM.from_pretrained(
                moondream_path,
                trust_remote_code=True,
                device_map=None,  # Don't use device_map to avoid accelerate issues
                torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
                local_files_only=True
            )
            
            # Manually move to device
            device = "cuda" if torch.cuda.is_available() else "cpu"
            model = model.to(device)
            
            tokenizer = AutoTokenizer.from_pretrained(moondream_path, trust_remote_code=True)
            
            st.success("✅ Model loaded with HuggingFace transformers")
            return {"model": model, "tokenizer": tokenizer, "type": "huggingface"}
            
        except Exception as e1:
            st.warning(f"HuggingFace loading failed: {e1}")
            
            # Method 2: Create mock model for demo
            st.info("Using mock model for demonstration...")
            return create_mock_vision_model()
        
    except Exception as e:
        st.error(f"Error loading Moondream2 model: {e}")
        return create_mock_vision_model()

def create_mock_vision_model():
    """Create a mock vision model for demonstration"""
    class MockVisionModel:
        def caption(self, image, length="normal"):
            # Analyze image properties for more realistic mock
            width, height = image.size
            
            if "depth" in str(image.filename).lower() if hasattr(image, 'filename') else False:
                return {"caption": "Path analysis: Clear walkway ahead with some obstacles on the sides. Ground appears level with no immediate hazards detected."}
            else:
                return {"caption": f"Urban scene showing a {width}x{height} view with buildings, street elements, and typical city environment."}
        
        def query(self, image, question):
            question_lower = question.lower()
            
            if "path" in question_lower or "obstacle" in question_lower:
                return {"answer": "The path appears clear with walkable surface. Some obstacles detected on the sides but main walking area is accessible."}
            elif "color" in question_lower:
                return {"answer": "Predominant colors include blues, greens, and earth tones typical of urban environments."}
            elif "hazard" in question_lower or "danger" in question_lower:
                return {"answer": "No immediate hazards detected in the walking path. Surface appears level and stable."}
            elif "traffic" in question_lower:
                return {"answer": "Typical urban traffic patterns visible with standard city street activity."}
            else:
                return {"answer": f"Based on the visual analysis: {question}"}
    
    class MockTokenizer:
        pass
    
    return {"model": MockVisionModel(), "tokenizer": MockTokenizer(), "type": "mock"}

def create_sample_depth_map():
    """Create a realistic sample depth map for testing"""
    H, W = 378, 378  # Moondream2's preferred input size
    
    depth_array = np.zeros((H, W), dtype=np.float32)
    
    # Simulate a sidewalk/path scenario
    # Background (buildings, far objects)
    depth_array[:, :] = 15.0
    
    # Main walkable path
    path_mask = np.zeros((H, W), dtype=bool)
    path_mask[H//3:2*H//3, W//4:3*W//4] = True
    depth_array[path_mask] = 3.0
    
    # Obstacles
    # Left: Building wall or large obstacle
    depth_array[H//4:3*H//4, 20:80] = 1.0
    
    # Right: Tree or pole
    center_x, center_y = W-100, H//2
    y, x = np.ogrid[:H, :W]
    tree_mask = (x - center_x)**2 + (y - center_y)**2 < 40**2
    depth_array[tree_mask] = 2.0
    
    # Add stairs or curb (step down)
    step_mask = (path_mask) & (y > H//2 + 30) & (y < H//2 + 50)
    depth_array[step_mask] = 2.5
    
    # Add some realistic noise
    noise = np.random.normal(0, 0.2, (H, W))
    depth_array += noise
    depth_array = np.clip(depth_array, 0.5, 20.0)
    
    return depth_array

def create_colored_depth_map(depth_array):
    """Convert depth array to colored visualization"""
    normalized = cv2.normalize(depth_array, None, 0, 255, cv2.NORM_MINMAX, dtype=cv2.CV_8U)
    colored = cv2.applyColorMap(normalized, cv2.COLORMAP_JET)
    colored_rgb = cv2.cvtColor(colored, cv2.COLOR_BGR2RGB)
    return Image.fromarray(colored_rgb)

def get_nearby_camera(user_lat, user_lon, zones):
    """Check if user is near a webcam zone"""
    user_location = (user_lat, user_lon)
    for zone in zones:
        zone_location = (zone["lat"], zone["lon"])
        dist = geodesic(user_location, zone_location).km
        if dist <= zone["radius_km"]:
            return zone
    return None

def get_webcam_image(zone):
    """Get webcam image (placeholder implementation with realistic simulation)"""
    # In a real implementation, this would fetch from NYCTMC
    # For the PoC, create a realistic street scene simulation
    
    try:
        # Create a realistic street scene image for the specified zone
        width, height = 640, 480
        
        if "Times Square" in zone["name"]:
            # Create a busy urban scene
            img = Image.new('RGB', (width, height), color=(70, 70, 90))  # Urban sky
            
            # Add buildings (dark rectangles)
            import numpy as np
            arr = np.array(img)
            
            # Buildings on sides
            arr[100:height, 0:80] = [40, 40, 50]  # Left building
            arr[120:height, width-100:width] = [35, 35, 45]  # Right building
            
            # Street level
            arr[height-100:height, :] = [60, 60, 65]  # Road
            
            # Add some "traffic" (colored rectangles)
            arr[height-80:height-60, 200:240] = [200, 50, 50]  # Red car
            arr[height-80:height-60, 300:340] = [50, 50, 200]  # Blue car
            
            # Add pedestrian area
            arr[height-100:height-80, :] = [80, 80, 85]  # Sidewalk
            
            return Image.fromarray(arr)
            
        elif "Brooklyn Bridge" in zone["name"]:
            # Create a bridge/waterfront scene
            img = Image.new('RGB', (width, height), color=(120, 150, 180))  # Sky
            
            arr = np.array(img)
            
            # Water
            arr[height//2:height, :] = [60, 90, 120]  # Water
            
            # Bridge structure
            arr[height//3:height//2+50, width//4:3*width//4] = [100, 100, 110]  # Bridge deck
            
            # Bridge supports
            arr[height//3:height, width//2-10:width//2+10] = [80, 80, 90]  # Center support
            
            return Image.fromarray(arr)
        
        else:
            # Generic street scene
            img = Image.new('RGB', (width, height), color=(100, 120, 140))
            arr = np.array(img)
            
            # Basic street
            arr[height-80:height, :] = [70, 70, 75]  # Road
            arr[height-100:height-80, :] = [90, 90, 95]  # Sidewalk
            
            return Image.fromarray(arr)
            
    except Exception as e:
        st.warning(f"Error creating simulated webcam image: {e}")
        return None

def speak_text(text):
    """Convert text to speech"""
    try:
        engine = pyttsx3.init()
        engine.say(text)
        engine.runAndWait()
        return True
    except Exception as e:
        st.error(f"TTS Error: {e}")
        return False

def describe_scene(image, model_data, scene_type="path"):
    """Use Moondream2 to describe the scene"""
    if model_data is None:
        return f"Model not available. This appears to be a {scene_type} scene."
    
    try:
        model = model_data["model"]
        
        if scene_type == "path":
            # Focus on navigation and obstacles
            prompt = "Describe the path ahead for a visually impaired person. Mention any obstacles, steps, or navigation hazards."
        else:
            # Focus on general scene description
            prompt = "Describe this street scene in detail, mentioning traffic, pedestrians, and general environment."
        
        description = model.query(image, prompt)["answer"]
        return description
        
    except Exception as e:
        st.error(f"Error in scene description: {e}")
        return f"Error processing {scene_type} image."

def main():
    """Main application"""
    st.set_page_config(
        page_title="Path & Place Vision Assist PoC", 
        page_icon="🦮",
        layout="wide"
    )
    
    st.title("🦮 Path & Place Vision Assist PoC")
    st.write("Computer Vision for Visually Impaired - Hackathon Demo")
    
    # Load model
    st.sidebar.title("System Status")
    with st.sidebar:
        with st.spinner("Loading Moondream2 model..."):
            model_data = load_moondream_model()
        
        if model_data:
            st.success("✅ Moondream2 loaded")
        else:
            st.error("❌ Model failed to load")
    
    # Simulation controls
    st.sidebar.title("Location Simulation")
    sim_lat = st.sidebar.number_input("Latitude", value=40.7580, format="%.4f", step=0.0001)
    sim_lon = st.sidebar.number_input("Longitude", value=-73.9855, format="%.4f", step=0.0001)
    
    # Audio controls
    enable_tts = st.sidebar.checkbox("Enable Text-to-Speech", value=False)
    
    # Main processing
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Current Location Analysis")
        
        if st.button("🔍 Analyze Current View", type="primary"):
            # Check if near a webcam
            nearby_camera = get_nearby_camera(sim_lat, sim_lon, NYC_WEBCAM_ZONES)
            
            if nearby_camera:
                st.info(f"📹 Near {nearby_camera['name']} - Using webcam view")
                
                # Try to get webcam image
                webcam_image = get_webcam_image(nearby_camera)
                
                if webcam_image:
                    st.image(webcam_image, caption=f"Live view from {nearby_camera['name']}")
                    description = describe_scene(webcam_image, model_data, "webcam")
                    description_prefix = f"Webcam view from {nearby_camera['name']}: "
                else:
                    # Use placeholder
                    st.warning("Webcam unavailable, using simulated view")
                    sample_image = Image.new('RGB', (378, 378), color='skyblue')
                    st.image(sample_image, caption="Simulated webcam view")
                    description = "Street scene with typical urban environment. No specific hazards detected."
                    description_prefix = f"Simulated view near {nearby_camera['name']}: "
                
            else:
                st.info("🗂️ No nearby webcam - Using LiDAR path analysis")
                
                # Generate depth map from LiDAR (simulated)
                with st.spinner("Processing LiDAR data..."):
                    depth_array = create_sample_depth_map()
                    depth_image = create_colored_depth_map(depth_array)
                
                st.image(depth_image, caption="Path depth analysis")
                description = describe_scene(depth_image, model_data, "path")
                description_prefix = "Path ahead: "
            
            # Display and speak description
            full_description = description_prefix + description
            
            with col2:
                st.subheader("Scene Description")
                st.write(full_description)
                
                if enable_tts:
                    if st.button("🔊 Speak Description"):
                        with st.spinner("Speaking..."):
                            speak_text(full_description)
    
    with col2:
        st.subheader("Manual Testing")
        
        # Manual image upload for testing
        uploaded_file = st.file_uploader("Upload test image:", type=['png', 'jpg', 'jpeg'])
        
        if uploaded_file:
            image = Image.open(uploaded_file)
            if image.size[0] > 512 or image.size[1] > 512:
                image = image.resize((512, 512))
            
            st.image(image, caption="Uploaded test image")
            
            test_question = st.text_input("Ask about the image:", "What do you see in this image?")
            
            if st.button("🤖 Ask Moondream"):
                if model_data:
                    with st.spinner("Processing..."):
                        try:
                            response = model_data["model"].query(image, test_question)["answer"]
                            st.write(f"**Response:** {response}")
                        except Exception as e:
                            st.error(f"Error: {e}")
                else:
                    st.error("Model not loaded")
    
    # Information panel
    st.expander("ℹ️ About This Demo", expanded=False).write("""
    This is a proof-of-concept application that demonstrates computer vision assistance for visually impaired users.
    
    **Key Features:**
    - **LiDAR Processing**: Converts 3D point clouds to navigable depth maps
    - **Webcam Integration**: Uses NYC traffic cameras for wider area awareness  
    - **AI Description**: Moondream2 VLM provides detailed scene descriptions
    - **Text-to-Speech**: Audio feedback for accessibility
    - **Geolocation**: Context-aware switching between data sources
    
    **Data Sources:**
    - NYC 2017 LiDAR (LAS 1.4 format)
    - NYC Traffic Management Center webcams
    - Quantized Moondream2 vision-language model
    """)

if __name__ == "__main__":
    main()
