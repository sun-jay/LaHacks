import google.generativeai as genai
from PIL import Image
import os
import numpy as np
import io
import pyaudio
import requests
import time
import cv2

from uagents import Agent, Context, Model

import serial_comm as sc
import inverse_kinematics

class GeminiContext(Model):
    user_transcript: str
    image_file_path: str

AGENT_MAILBOX_KEY = "9f0aea76-a1ef-48e4-a999-8778b482d5fe"

geminiCodeGenAgent = Agent(
    name = "GeminiCodeGenAgent",
    seed = "Gemini code gen secret phrase",
    mailbox = f"{AGENT_MAILBOX_KEY}@https://agentverse.ai"
)

gemini = None
manip = sc.Controller()
manip.connect()
manip.send_signal(000,118,127,0)
time.sleep(1)

print(geminiCodeGenAgent.address)

@geminiCodeGenAgent.on_event("startup")
async def configureGemini(ctx: Context):
    global gemini
    genai.configure(api_key = os.environ.get("GOOGLE_API_KEY"))
    gemini = genai.GenerativeModel('gemini-1.5-pro-latest')
    ctx.logger.info(gemini)

@geminiCodeGenAgent.on_message(model = GeminiContext)
async def gemini_codegen_handler(ctx: Context, sender: str, msg: GeminiContext):
    global gemini, manip
    ctx.logger.info(f"Received message from {sender}: {msg.user_transcript}")

    full_prompt = f"""heres how to use a robot arm API. use the pick_and_drop function. all coords are in mm, z=0 is ground level.
  #implementation in class, coords must be lists of 2 ints
  def pick_and_drop(pick_coords, drop_coords):
        go_to_coords(manip, pick_coords[0], pick_coords[1], 10, 0)
        time.sleep(1)
        go_to_coords(manip, pick_coords[0], pick_coords[1], 7, 1)
        time.sleep(1)
        go_to_coords(manip, pick_coords[0], pick_coords[1], 10, 1)
        time.sleep(1)
        go_to_coords(manip, drop_coords[0], drop_coords[1], 10, 1)
        time.sleep(1)
        go_to_coords(manip, drop_coords[0], drop_coords[1], 7, 1)
        time.sleep(1)
        go_to_coords(manip, drop_coords[0], drop_coords[1], 7, 0)
        time.sleep(1)
: You are provided with a birds-eye view image of the workspace, with the centroids of the object marked as points where you interact with the objects. assume all imports and functions are already defined in the context. using this API, write the lines of python that will complete this task: {msg.user_transcript}. use pick_and_drop(params) because this code will be running in a the class. Your response should have ONLY the python code. DO NOT define functions, just write the script out. The entirety of your response will be evaluated directly by an interpreter. use breif comments to show your plan."""

    image = Image.open(msg.image_file_path)

    if image.mode != "RGB":
        annotated_image = image.convert('RGB')
    else:
        annotated_image = image

    img_byte_arr = io.BytesIO()
    annotated_image.save(img_byte_arr, format = "JPEG")
    img_byte_arr.seek(0)

    response = gemini.generate_content([full_prompt, Image.open(img_byte_arr)], safety_settings={
        'HATE': 'BLOCK_NONE',
        'HARASSMENT': 'BLOCK_NONE',
        'SEXUAL' : 'BLOCK_NONE',
        'DANGEROUS' : 'BLOCK_NONE'
    })
    ctx.logger.info(response)
    generated_code = response.text

    # return response.text --> do not have to return here, can create a python script with the robot code

    # wite exec code here



    def create_affine_matrix():
        vision_coords = np.array([[74, 558], [557, 294], [951, 465]], dtype=np.float32)
        kinematics_coords = np.array([[-13, 17], [0, 24], [10, 20]], dtype=np.float32)
        return cv2.getAffineTransform(vision_coords, kinematics_coords)

    affine_matrix = create_affine_matrix()

    def vision_to_kinematics(vision_coords):
        # Check and print the shape of the affine matrix
        print("Shape of affine_matrix:", affine_matrix.shape)

        # Convert the vision coordinates to a numpy array and ensure correct dimensions
        vision_coords_array = np.array([vision_coords], dtype=np.float32).reshape(1, 1, 2)
        print("Shape of vision_coords_array:", vision_coords_array.shape)

        # Apply the affine transformation
        transformed_coords = cv2.transform(vision_coords_array, affine_matrix)
        print("Shape of transformed_coords:", transformed_coords.shape)

        # Return the first element of the transformed coordinates
        return transformed_coords[0][0] 
    
    def kinematics_to_vision(kinematics_coords):
        kinematics_coords_array = np.array([kinematics_coords], dtype=np.float32)
        inverse_matrix = np.linalg.inv(affine_matrix)
        transformed_coords = cv2.transform(kinematics_coords_array, inverse_matrix)
        return transformed_coords[0]

    def go_to_coords(manip, x, y, z, M):
        kinematics_coords = vision_to_kinematics([x, y])
        x_k, y_k = kinematics_coords[0], kinematics_coords[1]

        print("Getting servo angles...")
        print("x_k:", x_k, "y_k:" , y_k, "z:", z)
        s1, s2, s3 = inverse_kinematics.get_srvo_angles_for_coord_linear(x_k, y_k, z)
        print("Angles are: ", s1, s2, s3)
        time.sleep(2)  # Assuming this delay is needed for processing or hardware response

        manip.send_signal(s1, s2, s3, M)

    def pick_and_drop(pick_coords, drop_coords):
        go_to_coords(manip, pick_coords[0], pick_coords[1], 11, 0)
        time.sleep(0.1)
        go_to_coords(manip, pick_coords[0], pick_coords[1], 6, 1)
        time.sleep(0.1)
        go_to_coords(manip, pick_coords[0], pick_coords[1], 11, 1)
        time.sleep(0.1)
        go_to_coords(manip, drop_coords[0], drop_coords[1], 11, 1)
        time.sleep(0.1)
        go_to_coords(manip, drop_coords[0], drop_coords[1], 6, 1)
        time.sleep(1)
        go_to_coords(manip, drop_coords[0], drop_coords[1], 6, 0)
        time.sleep(1)

    

    def clean_string(string):
        return string.replace("```python", "").replace("```", "")
    

    generated_code = clean_string(generated_code)

    try:
    
        exec(generated_code)
    finally:
        manip.send_signal(000,118,127,0)
        time.sleep(0.5)


if __name__ == "__main__":
    geminiCodeGenAgent.run()

# class Gemini:
#     def __init__(self):
#         genai.configure(api_key = os.environ.get("GOOGLE_API_KEY"))
#         self.model = genai.GenerativeModel('gemini-1.5-pro-latest')
    
#     def call_gpt(self, user_prompt, input_image):
#         annotated_image = Image.fromarray(input_image)
#         if annotated_image.mode != "RGB":
#             annotated_image = annotated_image.convert("RGB")
#         img_byte_arr = io.BytesIO()
#         annotated_image.save(img_byte_arr, format='JPEG')

#         img_byte_arr.seek(0)

#         # Reload byte stream as PIL image
#         jpeg_image = Image.open(img_byte_arr)
#         controller_api_prompt = "Utilize the white dot markings in the image, their labelled coordinates and the controller API found here: . Generate Python code for the robot to achieve the task of picking up the previously defined objects and placing them all in the correct position. Each pickup and place should only be one line of code. Limit response and make it extremely concise."
#         full_prompt = user_prompt + ". " + controller_api_prompt

#         response = self.model.generate_content([full_prompt, jpeg_image])
#         return response.text
    
#     def speak(self, prompt):
#         url = "https://api.openai.com/v1/audio/speech"
#         headers = {
#             "Authorization": f'Bearer {os.getenv("OPENAI_API_KEY")}'
#         }

#         model_data = {
#             "model": "tts-1",
#             "input": prompt,
#             "voice": "shimmer",
#             "response_format": "wav"
#         } 

#         response = requests.post(url, headers=headers, json=model_data, stream=True)

#         if response.status_code == 200:
#             p = pyaudio.PyAudio()
#             stream = p.open(format=8, channels=1, rate=24000, output=True)
#             buffer = b''  
    
#             for chunk in response.iter_content(chunk_size=1024):
#                 buffer += chunk
                
#                 # check if the buffer has at least 1024 bytes
#                 while len(buffer) >= 1024:
#                     stream.write(buffer[:1024])
#                     buffer = buffer[1024:]
            
#             if buffer:
#                 stream.write(buffer)  # write the remaining buffer to the PyAudio stream

#             # close the stream
#             stream.stop_stream()
#             stream.close()
#             p.terminate()
    
# image_path = '/Users/aryans0921/Downloads/screenshot_2024-04-05_at_4.44.04___pm_720.png'

# img = Image.open(image_path)

# img_array = np.array(img)

# GEMINI = Gemini()
# ret = GEMINI.call_gpt("place the thing used to fasten things into the big region", img_array)
# print(ret)
# GEMINI.speak(ret)