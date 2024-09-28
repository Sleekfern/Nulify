import cv2
import numpy as np
from picamera2 import Picamera2
import time
import logging
import sys

logging.basicConfig(level=logging.DEBUG)

class HomogeneousBgDetector:
    def __init__(self):
        self.min_width = 0
        self.max_width = float('inf')
        self.min_height = 0
        self.max_height = float('inf')

    def set_size_range(self, min_width, max_width, min_height, max_height):
        self.min_width = min_width
        self.max_width = max_width
        self.min_height = min_height
        self.max_height = max_height

    def detect_objects(self, frame):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        mask = cv2.adaptiveThreshold(
            gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY_INV, 19, 5
        )
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        return [cnt for cnt in contours if cv2.contourArea(cnt) > 2000]

    def is_object_in_range(self, width, height):
        return (self.min_width <= width <= self.max_width) and (self.min_height <= height <= self.max_height)

def main():
    # Use the arguments passed from the GUI
    min_width = float(sys.argv[1])
    max_width = float(sys.argv[2])
    min_height = float(sys.argv[3])
    max_height = float(sys.argv[4])
    aruco_size = float(sys.argv[5])

    # Initialize Raspberry Pi camera
    picam2 = Picamera2()
    config = picam2.create_preview_configuration(main={"size": (640, 480)})
    picam2.configure(config)
    picam2.start()
    time.sleep(2)  # Allow camera to warm up

    # Load Aruco detector
    parameters = cv2.aruco.DetectorParameters()
    aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_5X5_50)
    aruco_detector = cv2.aruco.ArucoDetector(aruco_dict, parameters)

    # Load Object Detector
    detector = HomogeneousBgDetector()
    detector.set_size_range(min_width, max_width, min_height, max_height)

    while True:
        img = picam2.capture_array()

        # Ensure the image is in the correct color format
        img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)

        # Get Aruco marker
        corners, _, _ = aruco_detector.detectMarkers(img)

        if len(corners) > 0:
            # Draw polygon around the marker
            int_corners = np.int0(corners)
            cv2.polylines(img, int_corners, True, (0, 255, 0), 5)

            # Aruco Perimeter
            aruco_perimeter = cv2.arcLength(corners[0], True)

            # Pixel to cm ratio
            pixel_cm_ratio = aruco_perimeter / aruco_size

            contours = detector.detect_objects(img)

            # Draw objects boundaries
            for cnt in contours:
                is_aruco = any(cv2.pointPolygonTest(corners[0], tuple(map(int, cnt[0][0])), False) >= 0 for corner in corners)
                
                if is_aruco:
                    continue  # Skip processing for ArUco marker

                # Get rect
                rect = cv2.minAreaRect(cnt)
                (x, y), (w, h), angle = rect

                # Get Width and Height of the Objects by applying the Ratio pixel to cm
                object_width = w / pixel_cm_ratio
                object_height = h / pixel_cm_ratio

                # Display rectangle
                box = cv2.boxPoints(rect)
                box = np.int0(box)

                # Check if object size is within the given range
                if detector.is_object_in_range(object_width, object_height):
                    color = (0, 255, 0)  # Green for objects in range
                else:
                    color = (0, 0, 255)  # Red for objects out of range
                    # Draw cross sign for objects out of range
                    cv2.line(img, (int(x - w / 2), int(y - h / 2)), (int(x + w / 2), int(y + h / 2)), color, 2)
                    cv2.line(img, (int(x - w / 2), int(y + h / 2)), (int(x + w / 2), int(y - h / 2)), color, 2)

                cv2.circle(img, (int(x), int(y)), 5, color, -1)
                cv2.polylines(img, [box], True, color, 2)
                cv2.putText(img, f"Width {object_width:.1f} cm", (int(x - 100), int(y - 20)),
                            cv2.FONT_HERSHEY_PLAIN, 2, color, 2)
                cv2.putText(img, f"Height {object_height:.1f} cm", (int(x - 100), int(y + 15)),
                            cv2.FONT_HERSHEY_PLAIN, 2, color, 2)

        # Display the resulting frame
        cv2.imshow("Frame", img)

        # Press 'q' to quit
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cv2.destroyAllWindows()
    picam2.stop()

if __name__ == "__main__":
    main()
