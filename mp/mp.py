import json
import os
import queue
import threading

import mediapipe as mp
from loguru import logger

from .data import MPImageQueueBody, MPImageQueueType, MPResultQueueBody

BaseOptions = mp.tasks.BaseOptions
FaceLandmarker = mp.tasks.vision.FaceLandmarker
FaceLandmarkerOptions = mp.tasks.vision.FaceLandmarkerOptions
FaceLandmarkerResult = mp.tasks.vision.FaceLandmarkerResult
VisionRunningMode = mp.tasks.vision.RunningMode

model_path = os.environ.get("MODEL_PATH", "models/face_landmark.tflite")


class MPThread(threading.Thread):
    def __init__(
        self,
        unique_id: str,
        image_queue: queue.Queue[MPImageQueueBody],
        response_queue: queue.Queue[MPImageQueueBody],
    ):
        super().__init__()
        # 当前Websocket连接的唯一ID
        self.unique_id = unique_id
        # 用于接收图像的队列
        self.image_queue = image_queue
        # 用于发送结果的队列
        self.response_queue = response_queue
        # 初始化MediaPipe FaceLandmarker
        self.mp_options = BaseOptions(
            base_options=BaseOptions(model_asset_path=model_path),
            running_mode=VisionRunningMode.LIVE_STREAM,
            result_callback=self.callback,
        )

    def callback(
        self, result: FaceLandmarkerResult, output_image: mp.Image, timestamp_ms: int
    ):
        logger.info(f"[MPThread-{self.unique_id}] 收到来自时间戳{timestamp_ms}的结果")
        self.response_queue.put(MPResultQueueBody.result(timestamp_ms, result))

    def run(self):
        logger.info(f"[MPThread-{self.unique_id}] 正在启动图像处理线程")
        with FaceLandmarker.create_from_options(self.mp_options) as landmarker:
            logger.info(f"[MPThread-{self.unique_id}] FaceLandmarker已创建")
            while True:
                # 队列中直接获取图像，由于停止信号与图像是合并在一个对象中，故直接阻塞即可
                body = self.image_queue.get()
                if body.type == MPImageQueueType.CLOSED:
                    # body.closed是WebSocket端发送的停止信号
                    break
                # 验证数据完整性
                if body.body is None:
                    raise ValueError("图像或时间戳为空")
                logger.debug(
                    f"[MPThread-{self.unique_id}] 收到时间戳{body.timestamp_ms}的图像"
                )
                # 图像预处理
                mp_image = mp.Image(format=mp.ImageFormat.SRGB, data=body.body.image)
                # 提交至MediaPipe处理队列
                landmarker.detect_async(mp_image, body.body.timestamp_ms)
                logger.debug(f"[MPThread-{self.unique_id}] 已提交至MediaPipe处理队列")
