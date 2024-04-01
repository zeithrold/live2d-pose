import asyncio
import json
import time

import cv2
import matplotlib.pyplot as plt
import numpy as np
import websockets
from loguru import logger

ws_url = "ws://localhost:8765/image"

cap = cv2.VideoCapture(1)
cap.set(3, 640)  # adjust width
cap.set(4, 480)  # adjust height

timestamp_ms = lambda: int(time.time() * 1000)
elapsed_time_ms_list = []


async def main():
    async with websockets.connect(ws_url, ping_timeout=None, ping_interval=None) as ws:
        base_timestamp_ms = timestamp_ms()
        logger.debug("Connected to server")
        data = await ws.recv()
        logger.debug(data)
        await ws.send(json.dumps({"imageSize": {"width": 640, "height": 480}}))
        data = await ws.recv()
        logger.debug(data)
        data = await ws.recv()
        logger.debug(data)
        while True:
            start_timestamp_ms = timestamp_ms()
            relative_timestamp_ms = start_timestamp_ms - base_timestamp_ms
            logger.debug("Capturing frame...")
            success, img = cap.read()
            logger.debug("Frame captured")
            # Convert to Pillow-compatible base64
            params = [cv2.IMWRITE_JPEG_QUALITY, 50]
            compressed_img = cv2.imencode(".jpg", img, params)[1].tobytes()
            logger.debug(f"Sending frame at {relative_timestamp_ms} ms")
            await asyncio.sleep(0.03)
            await ws.send(compressed_img)
            logger.debug("Frame sent")
            cv2.imshow("Webcam", img)  # This will open an independent window
            logger.debug("Frame displayed")
            if cv2.waitKey(1) & 0xFF == ord("q"):  # quit when 'q' is pressed
                means = np.mean(elapsed_time_ms_list)
                std = np.std(elapsed_time_ms_list)
                logger.success(f"Mean: {means} ms, Std: {std} ms")
                plt.hist(elapsed_time_ms_list, bins=10)
                plt.show()
                cap.release()
                break


asyncio.run(main())
