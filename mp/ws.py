import asyncio
import base64
import json

import time
from queue import Queue

import cv2

import numpy as np
import websockets
import websockets.server as server

from data import MPImageQueueBody, MPResultQueueBody, MPResultQueueType
from image import MPThread
from loguru import logger


timestamp_ms = lambda: int(time.time() * 1000)


async def handler(ws: server.WebSocketServerProtocol):
    unique_id = ws.id.hex[:8]
    logger.info(
        f"[WebSocketHandler-{unique_id}] 成功连接，正在创建MediaPipe图像处理线程"
    )
    image_queue = Queue[MPImageQueueBody]()
    result_queue = Queue[MPResultQueueBody]()
    t = MPThread(unique_id, image_queue, result_queue)
    t.start()
    result = result_queue.get()
    if not result.type == MPResultQueueType.READY:
        raise ValueError("MediaPipe初始化失败")
    await ws.send(json.dumps({"type": "ready"}))
    logger.info(f"[WebSocketHandler-{unique_id}] MediaPipe已初始化")
    base_timestamp_ms = timestamp_ms()
    while True:
        try:
            logger.debug(f"[WebSocketHandler-{unique_id}] 等待图像数据")
            payload = await ws.recv()
            current_timestamp_ms = timestamp_ms()
            # 获取图像时间戳
            image_timestamp_ms = current_timestamp_ms - base_timestamp_ms
            logger.debug(f"[WebSocketHandler-{unique_id}] 收到图像数据：{len(payload)}")
            # 从Payload (bytes) 获取图像数据
            compressed_image = np.frombuffer(payload, dtype=np.uint8)
            decompressed_image = cv2.imdecode(compressed_image, cv2.IMREAD_COLOR)
            logger.debug(f"[WebSocketHandler-{unique_id}] 解压成功")
            logger.debug(
                f"[WebSocketHandler-{unique_id}] 收到图像尺寸：{decompressed_image.shape}"
            )
            image = MPImageQueueBody.image(image_timestamp_ms, decompressed_image)
            # 将图像数据放入队列
            image_queue.put(image)
            # 从MediaPipe图像处理线程获取结果
            result = result_queue.get()
            logger.debug(f"[WebSocketHandler-{unique_id}] 从图像处理线程收到结果")
            result = result.body.to_binary()
            logger.debug(f"[WebSocketHandler-{unique_id}] 结果长度：{len(result)}")
            await ws.send(result)
            logger.debug(f"[WebSocketHandler-{unique_id}] 结果发送成功")
        except Exception as e:
            if isinstance(e, websockets.exceptions.ConnectionClosed):
                logger.info(
                    f"[WebSocketHandler-{unique_id}] WebSocket连接已关闭，正在关闭MediaPipe图像处理线程"
                )
                result = MPImageQueueBody.closed()
                image_queue.put(result)
                break
            logger.error(
                f"[WebSocketHandler-{unique_id}] 发生错误：{e}，正在关闭MediaPipe图像处理线程"
            )
            result = MPImageQueueBody.closed()
            image_queue.put(result)
            break
