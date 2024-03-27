import asyncio
import json
import uuid
from queue import Queue

import websockets
import websockets.server as server
from loguru import logger

from .data import MPImageBody, MPResultBody, MPResultType
from .mp import MPThread


def random_id():
    # 生成随机ID的偏方
    return str(uuid.uuid4())[:8]


async def handler(ws: server.WebSocketServerProtocol):
    unique_id = random_id()
    logger.info(
        f"[WebSocketHandler-{unique_id}] 成功连接，正在创建MediaPipe图像处理线程"
    )
    image_queue = Queue[MPImageBody]()
    result_queue = Queue[MPResultBody]()
    t = MPThread(unique_id, image_queue, result_queue)
    t.start()
    body = result_queue.get()
    if not body.type == MPResultType.READY:
        raise ValueError("MediaPipe初始化失败")
    await ws.send(json.dumps({"type": "ready"}))
    while True:
        try:
            data = await ws.recv()
            data = json.loads(data)
            body = MPImageBody.from_json(data)
            image_queue.put(body)
            body = result_queue.get()
            logger.info(
                f"[WebSocketHandler-{unique_id}] 发送来自时间戳{body.timestamp_ms}的结果"
            )
            await ws.send(json.dumps(body))
        except Exception as e:
            logger.error(f"[WebSocketHandler-{unique_id}] {e}")
            body = MPImageBody.closed_body()
            image_queue.put(body)
            break


async def main():
    logger.info("Starting server")
    async with websockets.serve(handler, "localhost", 8765):
        await asyncio.Future()

