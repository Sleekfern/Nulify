import cv2
import numpy as np
from picamera2 import Picamera2
import time
import logging
from aiohttp import web
import asyncio
import json
from av import VideoFrame
from aiortc import RTCPeerConnection, RTCSessionDescription, VideoStreamTrack

logging.basicConfig(level=logging.DEBUG)

class HomogeneousBgDetector:
    def detect_objects(self, frame):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        mask = cv2.adaptiveThreshold(
            gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY_INV, 19, 5
        )
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        return [cnt for cnt in contours if cv2.contourArea(cnt) > 2000]

class VideoTransformTrack(VideoStreamTrack):
    def __init__(self, picam2):
        super().__init__()
        self.picam2 = picam2
        self.detector = HomogeneousBgDetector()
        self.aruco_dict = cv2.aruco.Dictionary_get(cv2.aruco.DICT_5X5_50)
        self.parameters = cv2.aruco.DetectorParameters_create()

    async def recv(self):
        img = self.picam2.capture_array()
        
        if img.dtype != np.uint8 or len(img.shape) != 3 or img.shape[2] != 3:
            img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)

        corners, _, _ = cv2.aruco.detectMarkers(img, self.aruco_dict, parameters=self.parameters)
        
        if len(corners) > 0:
            int_corners = np.int0(corners)
            cv2.polylines(img, int_corners, True, (0, 255, 0), 5)
            
            aruco_perimeter = cv2.arcLength(corners[0], True)
            pixel_cm_ratio = aruco_perimeter / 20
            
            contours = self.detector.detect_objects(img)
            
            for cnt in contours:
                rect = cv2.minAreaRect(cnt)
                (x, y), (w, h), angle = rect
                
                object_width = w / pixel_cm_ratio
                object_height = h / pixel_cm_ratio
                
                box = cv2.boxPoints(rect)
                box = np.int0(box)
                
                cv2.circle(img, (int(x), int(y)), 5, (0, 0, 255), -1)
                cv2.polylines(img, [box], True, (255, 0, 0), 2)
                cv2.putText(img, f"Width {object_width:.1f} cm", (int(x - 100), int(y - 20)),
                            cv2.FONT_HERSHEY_PLAIN, 2, (100, 200, 0), 2)
                cv2.putText(img, f"Height {object_height:.1f} cm", (int(x - 100), int(y + 15)),
                            cv2.FONT_HERSHEY_PLAIN, 2, (100, 200, 0), 2)

        # Convert the image to VideoFrame
        frame = VideoFrame.from_ndarray(img, format="bgr24")
        frame.pts, frame.time_base = await self.next_timestamp()

        return frame

async def index(request):
    content = open("index.html", "r").read()
    return web.Response(content_type="text/html", text=content)

async def javascript(request):
    content = open("client.js", "r").read()
    return web.Response(content_type="application/javascript", text=content)

async def offer(request):
    params = await request.json()
    offer = RTCSessionDescription(sdp=params["sdp"], type=params["type"])

    pc = RTCPeerConnection()
    pcs.add(pc)

    @pc.on("connectionstatechange")
    async def on_connectionstatechange():
        print("Connection state is %s" % pc.connectionState)
        if pc.connectionState == "failed":
            await pc.close()
            pcs.discard(pc)

    # Set up video stream
    picam2 = Picamera2()
    config = picam2.create_preview_configuration(main={"size": (640, 480)})
    picam2.configure(config)
    picam2.start()

    video = VideoTransformTrack(picam2)
    pc.addTrack(video)

    await pc.setRemoteDescription(offer)
    answer = await pc.createAnswer()
    await pc.setLocalDescription(answer)

    return web.Response(
        content_type="application/json",
        text=json.dumps(
            {"sdp": pc.localDescription.sdp, "type": pc.localDescription.type}
        ),
    )

pcs = set()

async def on_shutdown(app):
    # close peer connections
    coros = [pc.close() for pc in pcs]
    await asyncio.gather(*coros)
    pcs.clear()

if __name__ == "__main__":
    app = web.Application()
    app.on_shutdown.append(on_shutdown)
    app.router.add_get("/", index)
    app.router.add_get("/client.js", javascript)
    app.router.add_post("/offer", offer)
    web.run_app(app, host="0.0.0.0", port=8080)