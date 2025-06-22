import os
import torch
from PIL import Image
from transformers import AutoModelForCausalLM, AutoTokenizer

def load_model():
    """Load the Moondream2 model and tokenizer."""
    moondream_path = '/python_code_src/moondream2'
    model = AutoModelForCausalLM.from_pretrained(
        moondream_path,
        trust_remote_code=True,
        local_files_only=True,
        torch_dtype=torch.float32,
        device_map=None,  # Manually move to CPU
    )
    tokenizer = AutoTokenizer.from_pretrained(
        moondream_path, 
        trust_remote_code=True,
        local_files_only=True
    )
    model = model.to('cpu')
    return model, tokenizer

def describe_image(model, tokenizer, image_path):
    """Describe an image using the Moondream2 model."""
    image = Image.open(image_path)
    enc_image = model.encode_image(image)
    description = model.answer_question(enc_image, "Describe the scene.", tokenizer)
    return description
