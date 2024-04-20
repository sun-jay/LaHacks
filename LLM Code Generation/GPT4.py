import os
from openai import OpenAI
from PIL import Image
import numpy as np
import io
import base64
import requests
import pyaudio

import sys
print("Python executable:", sys.executable)
print("Python version:", sys.version)
import site
print("Site packages:", site.getsitepackages())

class GPT4:
    def __init__(self):
        self.client = OpenAI(api_key = os.environ.get("OPENAI_API_KEY"))

    def call_gpt(self, user_prompt, input_image):
        annotated_image = Image.fromarray(input_image)
        if annotated_image.mode != "RGB":
            annotated_image = annotated_image.convert("RGB")
        img_byte_arr = io.BytesIO()
        annotated_image.save(img_byte_arr, format='JPEG')

        img_byte_arr.seek(0)

        base64_image = base64.b64encode(img_byte_arr.getvalue()).decode('utf-8')

        controller_api_prompt = "Utilize the white dot markings in the image, their labelled coordinates and the controller API found here: . Generate Python code for the robot to achieve the task of picking up the previously defined objects and placing them all in the correct position. Each pickup and place should only be one line of code. Limit response and make it extremely concise."
        full_prompt = user_prompt + ". " + controller_api_prompt

        res = self.client.chat.completions.create(
            model = "gpt-4-turbo",
            messages = [
                {
                    "role": "user",
                    "content": [
                        {
                            "type":"text",
                            "text": "place the thing used to fasten things into the big region"
                        },
                        {
                            "type":"image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            }
                        }
                    ]
                },
                {
                    "role": "system",
                    "content": [
                        {
                            "type":"text",
                            "text": full_prompt
                        }
                    ]
                }
            ],
            max_tokens = 300
        )

        return res.choices[0].message.content
    
    def speak(self, prompt):
        url = "https://api.openai.com/v1/audio/speech"
        headers = {
            "Authorization": f'Bearer {os.getenv("OPENAI_API_KEY")}'
        }

        model_data = {
            "model": "tts-1",
            "input": prompt,
            "voice": "shimmer",
            "response_format": "wav"
        } 

        response = requests.post(url, headers=headers, json=model_data, stream=True)

        if response.status_code == 200:
            p = pyaudio.PyAudio()
            stream = p.open(format=8, channels=1, rate=24000, output=True)
            buffer = b''  
    
            for chunk in response.iter_content(chunk_size=1024):
                buffer += chunk
                
                # check if the buffer has at least 1024 bytes
                while len(buffer) >= 1024:
                    stream.write(buffer[:1024])
                    buffer = buffer[1024:]
            
            if buffer:
                stream.write(buffer)  # write the remaining buffer to the PyAudio stream

            # close the stream
            stream.stop_stream()
            stream.close()
            p.terminate()

image_path = '/Users/aryans0921/Downloads/screenshot_2024-04-05_at_4.44.04___pm_720.png'

img = Image.open(image_path)

img_array = np.array(img)

gpt4 = GPT4()
ret = gpt4.call_gpt("place the thing used to fasten things into the big region", img_array)
print(ret)
gpt4.speak(ret)