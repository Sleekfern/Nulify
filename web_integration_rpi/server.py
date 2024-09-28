import cv2
import numpy as np
from picamera2 import Picamera2
import time
import logging
from flask import Flask, render_template, Response, request, jsonify
import threading
import base64
import netifaces

app = Flask(__name__)

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

class VideoCamera:
    def __init__(self):
        self.picam2 = Picamera2()
        config = self.picam2.create_preview_configuration(main={"size": (640, 480)})
        self.picam2.configure(config)
        self.picam2.start()
        time.sleep(2)  # Allow camera to warm up
        self.detector = HomogeneousBgDetector()
        self.aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_5X5_50)
        self.parameters = cv2.aruco.DetectorParameters()
        self.aruco_detector = cv2.aruco.ArucoDetector(self.aruco_dict, self.parameters)

    def __del__(self):
        self.picam2.stop()

    def get_frame(self):
        img = self.picam2.capture_array()

        # Ensure the image is in the correct color format
        img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)

        # Aruco marker detection
        corners, _, _ = self.aruco_detector.detectMarkers(img)
        
        if len(corners) > 0:
            int_corners = np.int0(corners)
            cv2.polylines(img, int_corners, True, (0, 255, 0), 5)
            aruco_perimeter = cv2.arcLength(corners[0], True)
            pixel_cm_ratio = aruco_perimeter / 20

            contours = self.detector.detect_objects(img)
            for cnt in contours:
                is_aruco = any(cv2.pointPolygonTest(corners[0], tuple(map(int, cnt[0][0])), False) >= 0 for corner in corners)
                
                if is_aruco:
                    continue  # Skip processing for ArUco marker
                
                rect = cv2.minAreaRect(cnt)
                (x, y), (w, h), angle = rect
                object_width = w / pixel_cm_ratio
                object_height = h / pixel_cm_ratio
                box = cv2.boxPoints(rect)
                box = np.int0(box)
                
                if self.detector.is_object_in_range(object_width, object_height):
                    color = (0, 255, 0)  # Green for objects in range
                else:
                    color = (0, 0, 255)  # Red for objects out of range
                    # Draw cross sign
                    cv2.line(img, (int(x-w/2), int(y-h/2)), (int(x+w/2), int(y+h/2)), color, 2)
                    cv2.line(img, (int(x-w/2), int(y+h/2)), (int(x+w/2), int(y-h/2)), color, 2)
                
                cv2.circle(img, (int(x), int(y)), 5, color, -1)
                cv2.polylines(img, [box], True, color, 2)
                cv2.putText(img, f"Width {object_width:.1f} cm", (int(x - 100), int(y - 20)),
                            cv2.FONT_HERSHEY_PLAIN, 2, color, 2)
                cv2.putText(img, f"Height {object_height:.1f} cm", (int(x - 100), int(y + 15)),
                            cv2.FONT_HERSHEY_PLAIN, 2, color, 2)

        ret, jpeg = cv2.imencode('.jpg', img)
        return jpeg.tobytes()

    def set_size_range(self, min_width, max_width, min_height, max_height):
        self.detector.set_size_range(min_width, max_width, min_height, max_height)

video_camera = VideoCamera()

@app.route('/')
def index():
    return render_template('index.html')

def gen(camera):
    while True:
        frame = camera.get_frame()
        if frame is not None:
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(gen(video_camera),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/get_frame', methods=['GET'])
def get_frame():
    frame = video_camera.get_frame()
    if frame is not None:
        return base64.b64encode(frame).decode('utf-8')
    return ''

@app.route('/get_ip', methods=['GET'])
def get_ip():
    interfaces = netifaces.interfaces()
    ip_address = None
    for interface in interfaces:
        if interface != 'lo':
            addrs = netifaces.ifaddresses(interface)
            if netifaces.AF_INET in addrs:
                ip_address = addrs[netifaces.AF_INET][0]['addr']
                break  
    return jsonify({'ip': ip_address, 'port': 5000})

@app.route('/set_size_range', methods=['POST'])
def set_size_range():
    data = request.json
    min_width = float(data['min_width'])
    max_width = float(data['max_width'])
    min_height = float(data['min_height'])
    max_height = float(data['max_height'])
    video_camera.set_size_range(min_width, max_width, min_height, max_height)
    return jsonify({'status': 'success'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, threaded=True)