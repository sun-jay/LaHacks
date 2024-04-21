# vision system address is ejua6mt0v68huhk

from uagents import Agent, Context, Model
import cv2
import numpy as np
from ThreadStream import ThreadStream
from PIL import Image
import tempfile

class Transcript(Model):
    transcript: str

AGENT_MAILBOX_KEY = "2b217244-1f0f-48a5-9c1c-cf0a68a06888"

visionSystemAgent = Agent(
    name = "VisionSystemAgent",
    seed = "Vision system complex secret phrase",
    mailbox = f"{AGENT_MAILBOX_KEY}@https://agentverse.ai"
)

class GeminiContext(Model):
    user_transcript: str
    image_file_path: str

@visionSystemAgent.on_message(model = Transcript)
async def transcript_handler(ctx: Context, sender: str, msg: Transcript):
    visionSystem = VisionSystem()
    ctx.logger.info("handler hit")
    ctx.logger.info(f"Received message from {sender}: {msg.transcript}")

    frame_np = visionSystem.ret_annnotated_frame()
    image = Image.fromarray(frame_np)
    
    path = None
    with tempfile.NamedTemporaryFile(delete = False, suffix = ".jpeg") as temp:
        image.save(temp.name, 'JPEG')
        path = temp.name
        print(temp.name)

    await ctx.send("agent1qfxrqyu4q06lk4kech230ty4yhes06lku0554rpcg5g3hgeuzj8e2uydl0q", GeminiContext(user_transcript = msg.transcript, image_file_path = path))
    # await ctx.send(sender, Transcript(transcript=""))

class VisionSystem:
    def __init__(self):
        self.stream = ThreadStream()
        self.affine_matrix = None

    def create_affine_matrix(self):
        vision_coords = np.array([[0, 0], [0, 1], [1, 0]])
        kinematics_coords = np.array([[0, 0], [0, 480], [640, 0]])

        self.affine_matrix = cv2.getAffineTransform(vision_coords, kinematics_coords)

    def vision_to_kinematics(self, vision_coords):
        if self.affine_matrix is None:
            self.create_affine_matrix()

        return cv2.transform(np.array([vision_coords]), self.affine_matrix)[0]
    
    def kinematics_to_vision(self, kinematics_coords):
        if self.affine_matrix is None:
            self.create_affine_matrix()

        return cv2.transform(np.array([kinematics_coords]), np.linalg.inv(self.affine_matrix))[0]


    def show_stream(self):
        while True:
            grabbed, frame = self.stream.read()
            if not grabbed:
                break

            masks = self.create_individual_masks(frame)
            frame = self.apply_masks_on_image(frame, masks)
            centroids = self.ret_centroids(masks)
            frame = self.plot_centroids(frame, centroids)

            cv2.imshow('Stream', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        cv2.destroyAllWindows()

    
    def apply_masks_on_image(self,image, masks, color=(255, 0, 255)):
        # Check if image is a string (file path) and load it
        if isinstance(image, str):
            image = cv2.imread(image)

        # Convert image to RGB for color overlay if it's not already
        if len(image.shape) == 2 or image.shape[2] == 1:
            image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)

        # Overlay each mask on the image
        for mask in masks:
            # Create a color overlay where the mask is applied
            overlay = np.zeros_like(image, dtype=np.uint8)
            overlay[mask == 255] = color

            # Blend the overlay with the original image
            image = cv2.addWeighted(image, 1, overlay, 0.85, 0)

        return image

    def create_individual_masks(self,image):

        # Convert image to RGB color space from BGR
        rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        # Define range of green color in RGB
        lower_green = np.array([184,198,121]) - 60
        upper_green = np.array([216,225,156]) + 60

        # Threshold the RGB image to get only green colors
        mask = cv2.inRange(rgb, lower_green, upper_green)
        # Invert the mask to get non-green objects
        mask_inv = cv2.bitwise_not(mask)

        # Find contours on the inverted mask
        contours, _ = cv2.findContours(mask_inv, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # Create an array to hold masks for each contour
        masks = []

        # Generate a mask for each contour that meets the area threshold
        for contour in contours:
            if cv2.contourArea(contour) > 220:  # Filtering condition based on the area
                # Create a blank mask with the same dimensions as the original image
                temp_mask = np.zeros_like(mask_inv)
                # Draw the contour on the mask
                cv2.drawContours(temp_mask, [contour], -1, 255, thickness=cv2.FILLED)
                # Add the mask to the list
                masks.append(temp_mask)

        # Return the array of masks
        return masks

    def ret_centroids(self, masks):
        centroids = []
        for mask in masks:
            # Find contours in the mask
            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            # Calculate the centroid for each contour
            for contour in contours:
                M = cv2.moments(contour)
                if M["m00"] != 0:
                    cx = int(M["m10"] / M["m00"])
                    cy = int(M["m01"] / M["m00"])
                    centroids.append((cx, cy))
                else:
                    # In case of zero division error
                    centroids.append((0, 0))
        return centroids


    def plot_centroids(self, image, centroids):
        # Ensure the image is in color to plot colored dots (centroids)
        if len(image.shape) == 2 or image.shape[2] == 1:
            image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)

        # Draw a circle and annotate for each centroid
        for index, (cx, cy) in enumerate(centroids):
            # Draw a white circle at each centroid
            cv2.circle(image, (cx, cy), 5, (255, 255, 255), -1)
            # Prepare text for annotation
            label = f"({cx}, {cy})"
            # Position the text near the centroid
            text_position = (cx + 10, cy)
            # Draw the text on the image
            cv2.putText(image, label, text_position, cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2, cv2.LINE_AA)

        return image
    
    def ret_annnotated_frame(self):
        ret, frame = self.stream.read()
        if ret:
        # mask = vision_system.create_mask_for_color(frame, (211,225,147))
            masks = self.create_individual_masks(frame)
            # frame = self.apply_masks_on_image(frame, masks)
            centroids = self.ret_centroids(masks)
            frame = self.plot_centroids(frame, centroids)
            return frame
    
import asyncio

# Use asyncio to run the above async function
if __name__ == "__main__":
    visionSystemAgent.run()