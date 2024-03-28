import asyncio
import json
from queue import Queue

import websockets
import websockets.server as server
from loguru import logger

from .data import MPImageQueueBody, MPResultQueueBody, MPResultQueueType
from .mp import MPThread


async def handler(ws: server.WebSocketServerProtocol):
    unique_id = ws.id[:8]
    logger.info(
        f"[WebSocketHandler-{unique_id}] 成功连接，正在创建MediaPipe图像处理线程"
    )
    image_queue = Queue[MPImageQueueBody]()
    result_queue = Queue[MPResultQueueBody]()
    t = MPThread(unique_id, image_queue, result_queue)
    t.start()
    body = result_queue.get()
    if not body.type == MPResultQueueType.READY:
        raise ValueError("MediaPipe初始化失败")
    await ws.send(json.dumps({"type": "ready"}))
    while True:
        try:
            image = await ws.recv()
            body = MPImageQueueBody.image(image)
            image_queue.put(body)
            body = result_queue.get()
            await ws.send(json.dumps(body.data))
        except websockets.exceptions.ConnectionClosedError:
            logger.info(
                f"[WebSocketHandler-{unique_id}] WebSocket连接已关闭，正在关闭MediaPipe图像处理线程"
            )
            body = MPImageQueueBody.closed()
            image_queue.put(body)
            break
        except Exception as e:
            logger.error(
                f"[WebSocketHandler-{unique_id}] 发生错误：{e}，正在关闭MediaPipe图像处理线程"
            )
            body = MPImageQueueBody.closed()
            image_queue.put(body)
            break


async def main():
    logger.info("Starting server")
    async with websockets.serve(handler, "localhost", 8765):
        await asyncio.Future()
