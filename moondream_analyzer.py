import os
import torch
import logging
from PIL import Image
from transformers import AutoModelForCausalLM, AutoTokenizer

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def load_model():
    """Load the Moondream2 model and tokenizer."""
    try:
        logging.info("Loading Moondream2 model and tokenizer...")
        moondream_path = '/python_code_src/moondream2'
        
        if not os.path.isdir(moondream_path):
            logging.error(f"Moondream model directory not found at: {moondream_path}")
            raise FileNotFoundError(f"Moondream model directory not found at: {moondream_path}")

        model = AutoModelForCausalLM.from_pretrained(
            moondream_path,
            trust_remote_code=True,
            local_files_only=True,
            torch_dtype=torch.float32,
            device_map="cpu",
        )
        tokenizer = AutoTokenizer.from_pretrained(
            moondream_path,
            trust_remote_code=True,
            local_files_only=True
        )
        logging.info("Moondream2 model and tokenizer loaded successfully.")
        return model, tokenizer
    except Exception as e:
        logging.error(f"Failed to load Moondream2 model: {e}")
        return None, None

def get_moondream_analysis(model, tokenizer, image_path: str) -> str:
    """
    Analyzes a traffic camera image using the Moondream2 model with a specific prompt.

    Args:
        model: The loaded Moondream2 model.
        tokenizer: The loaded Moondream2 tokenizer.
        image_path: The path to the image file.

    Returns:
        The textual analysis of the image.
    """
    try:
        logging.info(f"Analyzing image at: {image_path}")
        if not os.path.exists(image_path):
            logging.error(f"Image file not found at: {image_path}")
            return "Unable to determine safety from this image."

        image = Image.open(image_path).convert('RGB')
        enc_image = model.encode_image(image)
        
        question = "You are a helpful assistant for a visually impaired person. Analyze this traffic camera image. Describe the pedestrian signal status (e.g., 'Walk' sign, 'Don't Walk' sign, countdown timer). Are there any cars, bicycles, or other vehicles currently moving through or about to enter the crosswalk area? Based ONLY on the visual information, conclude with a direct, one-sentence recommendation: 'It appears safe to cross the street now.' or 'It does not appear safe to cross the street now.' or 'Unable to determine safety from this image.'"

        logging.info("Generating analysis with Moondream2...")
        analysis = model.answer_question(
            enc_image,
            question,
            tokenizer
        )
        logging.info(f"Moondream2 analysis generated: {analysis}")
        return analysis
    except Exception as e:
        logging.error(f"An error occurred during image analysis: {e}")
        return "Unable to determine safety from this image."
