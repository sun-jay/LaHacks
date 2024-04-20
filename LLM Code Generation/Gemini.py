import google.generativeai as genai
from PIL import Image
import os
import numpy as np
import io

class Gemini:
    def __init__(self):
        genai.configure(api_key = os.environ.get("GOOGLE_API_KEY"))
        self.model = genai.GenerativeModel('gemini-1.5-pro-latest')
    
    def call_gpt(self, user_prompt, input_image):
        annotated_image = Image.fromarray(input_image)
        print(type(annotated_image))
        if annotated_image.mode != "RGB":
            annotated_image = annotated_image.convert("RGB")
        img_byte_arr = io.BytesIO()
        annotated_image.save(img_byte_arr, format='JPEG')

        img_byte_arr.seek(0)

        # Reload byte stream as PIL image
        jpeg_image = Image.open(img_byte_arr)
        controller_api_prompt = "Utilize the white dot markings in the image, their labelled coordinates and the controller API found here: . Generate Python code for the robot to achieve the task of picking up the previously defined objects and placing them all in the correct position. Each pickup and place should only be one line of code."
        full_prompt = user_prompt + ". " + controller_api_prompt
        response = self.model.generate_content([full_prompt, jpeg_image])
        return response.text

GEMINI = Gemini()
ret = GEMINI.call_gpt("place the tweezer in the dish bath", np.random.randint(0, 256, (100, 100, 3), dtype=np.uint8))
print(ret)

