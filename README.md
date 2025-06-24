# Computer Vision For Vision Impaired

CV4VI is an acronym for "Computer Vision For Vision Impaired".

This is a proof of concept that uses a web app as simulated environment for an application on an edge device that has practical use of AI models.

## Installation
1. Clone the repo  
   `git clone https://github.com/ithllc/CV4VI.git`
2. Navigate to the directory  
   `cd CV4VI`
3. Install dependencies  
   `pip install -r requirements.txt`
   
   Alternatively, use Conda:
   ```
   conda env create -f environment.yml
   conda activate hackathon
   ```

## Usage
To start the app:
```
python app.py
```

This will launch a Streamlit web interface where you can:
1. Press the microphone button to record your voice
2. Ask if it's safe to cross at a specific NYC intersection (e.g., "I'm at 1st Avenue and 110th Street, can I cross?")
3. View the traffic camera feed from that location
4. Receive an AI analysis of the intersection safety
5. Hear the spoken response through your speakers

## Features
- Natural language processing to extract street intersections from spoken queries
- Automated web scraping of NYC Traffic Management Center (NYCTMC) cameras
- Real-time camera feed access for any monitored NYC intersection
- Computer vision analysis using the Moondream2 vision language model
- Spoken responses for visually impaired users using OpenAI's TTS technology
- User-friendly Streamlit interface for demonstration purposes

## Built With
- Python 3.11
- Streamlit for the web interface
- Selenium for web automation and camera feed access
- OpenAI APIs for speech-to-text and text-to-speech
- Hugging Face Transformers with Moondream2 vision language model
- WebDriver Manager for seamless browser automation

## Testing / Demo
For a quick test of the system:
1. Start the application
2. Click the microphone button
3. Say "I'm at 1st Avenue and 110th Street, can I cross?"
4. Wait for the system to process and respond

## License
This project is licensed under the MIT License - see the LICENSE file for details.

## Roadmap
### Refinement and Robustness
- Advanced location matching with geocoding API
- Selenium hardening for better web automation
- Configuration management improvements

### Model and Analysis Improvement
- Evaluation of different Vision Language Models
- Image pre-processing for better analysis in low-light conditions
- Confidence scoring for safety recommendations

### User Experience Enhancements
- Lower latency through optimization
- Interactive map showing camera locations
- Additional accessibility improvements

## Acknowledgments
- AI Tinkerers of NYC for hosting the hackathon on June 21, 2025 to June 22, 2025 (https://nyc.aitinkerers.org/)
- Moondream for sponsoring the hackathon event (https://moondream.ai/)
- New York City Department of Transportation (https://www.nyc.gov/html/dot/html/home/home.shtml)
