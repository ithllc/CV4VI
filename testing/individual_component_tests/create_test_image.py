from PIL import Image

# Create a new image with a white background
img = Image.new('RGB', (100, 100), color = 'white')

# Save the image
img.save('/python_code_src/AICHackathon/test_data/test_image.png')

print("Test image created successfully.")
