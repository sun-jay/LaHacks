import cv2
import numpy as np

from ThreadStream import ThreadStream

class VisionSystem:
    def __init__(self):
        self.stream = ThreadStream()

    def show_stream(self):
        while True:
            grabbed, frame = self.stream.read()
            if not grabbed:
                break
            cv2.imshow('Stream', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        cv2.destroyAllWindows()

    def create_mask_for_color(self, image, color):
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        color_lower = np.array([color[0] - 10, color[1] - 10, color[2] - 10], dtype="uint8")
        color_upper = np.array([color[0] + 10, color[1] + 10, color[2] + 10], dtype="uint8")
        mask = cv2.inRange(image_rgb, color_lower, color_upper)
        
        return mask

    def apply_pink_mask(self, image, mask, alpha=0.5):
        # Ensure the mask is in binary format
        mask_binary = cv2.threshold(mask, 1, 255, cv2.THRESH_BINARY)[1]
        
        # Create an all-pink image of the same dimensions as the original image
        pink_overlay = np.zeros_like(image)
        pink_overlay[:] = (180, 105, 255)  # BGR for pink

        # Use the binary mask to create the overlay with the pink color only in the mask area
        pink_mask = cv2.bitwise_and(pink_overlay, pink_overlay, mask=mask_binary)

        # Blend the pink mask and the original image
        image_with_mask = cv2.addWeighted(image, 1 - alpha, pink_mask, alpha, 0)

        return image_with_mask

    


        


if __name__ == '__main__':
    vision_system = VisionSystem()
    # make a custom display loop
    while True:
        ret, frame = vision_system.stream.read()
        if not ret:
            break
        mask = vision_system.create_mask_for_color(frame, (211,225,147))
        frame_with_mask = vision_system.apply_pink_mask(frame, mask)


        



