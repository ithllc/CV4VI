import streamlit as st
import torch
import transformers
import numpy as np
import laspy
import pyttsx3
from PIL import Image
from selenium import webdriver

st.title("Hackathon Environment Check")

st.write("All libraries imported successfully!")

# Display versions
st.subheader("Library Versions:")
st.write(f"- Streamlit: {st.__version__}")
st.write(f"- PyTorch: {torch.__version__}")
st.write(f"- Transformers: {transformers.__version__}")
st.write(f"- NumPy: {np.__version__}")
st.write(f"- laspy: {laspy.__version__}")
st.write(f"- pyttsx3: 2.90")
st.write(f"- Pillow: {Image.__version__}")
st.write(f"- Selenium: {webdriver.__version__}")

st.success("Hackathon environment is ready!")
