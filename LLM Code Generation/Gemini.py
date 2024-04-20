import google.generativeai as genai
from PIL import Image
import os
import numpy as np

class Gemini:
    def __init__(self):
        genai.configure(api_key = os.environ.get("GOOGLE_API_KEY"))
        self.model = genai.GenerativeModel('gemini-1.5-pro-latest')
    
    def call_gpt(self, prompt, input_image):
        annotated_image = Image.fromarray(input_image)
        annotated_image.show()

GEMINI = Gemini()
GEMINI.call_gpt("lol", np.random.randint(0, 256, (100, 100, 3), dtype=np.uint8))