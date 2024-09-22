# Import the necessary packages
from picamera2 import Picamera2, Preview
import time
import cv2

# Initialize the Picamera2
picam2 = Picamera2()

# Configure the camera to capture images
config = picam2.create_still_configuration()
picam2.configure(config)

# Start the camera
picam2.start()

# Allow the camera to warm up
time.sleep(0.1)

# Capture an image from the camera
image = picam2.capture_array()

# Display the image on screen and wait for a keypress
cv2.imshow("Image", image)
cv2.waitKey(0)

# Stop the camera
picam2.stop()
