import json

import time
import urllib.parse as urlparse
from asyncio import Event as AsyncEvent, Queue as AsyncQueue
from queue import Queue

import cv2

import numpy as np
import websockets
import websockets.server as server

from data import MPImageQueueBody, MPResultQueueBody, MPResultQueueType
from image import MPThread
from loguru import logger


timestamp_ms = lambda: int(time.time() * 1000)

locks: dict[str, tuple[AsyncQueue[bytes], AsyncEvent, AsyncEvent, AsyncQueue[dict]]] = (
    {}
)


async def image_handler(ws: server.WebSocketServerProtocol):
    unique_id = ws.id.hex[:8]
    uuid = ws.id.hex
    logger.info(
        f"[WebSocketImageHandler-{unique_id}] 成功连接，正在创建MediaPipe图像处理线程"
    )
    image_queue = Queue[MPImageQueueBody]()
    result_queue = Queue[MPResultQueueBody]()
    t = MPThread(unique_id, image_queue, result_queue)
    t.start()
    result = result_queue.get()
    if not result.type == MPResultQueueType.READY:
        raise ValueError("MediaPipe初始化失败")
    await ws.send(json.dumps({"type": "initialized"}))
    logger.info(f"[WebSocketImageHandler-{unique_id}] MediaPipe已初始化")
    base_timestamp_ms = timestamp_ms()
    logger.info(f"[WebSocketImageHandler-{unique_id}] 正在等待图像大小数据")
    payload = await ws.recv()
    payload = json.loads(payload)
    image_size = payload["imageSize"]
    await ws.send(json.dumps({"type": "ok"}))
    (callback_queue, browser_connected_event, closed_event, image_size_queue) = locks[
        uuid
    ]
    logger.info(f"[WebSocketImageHandler-{unique_id}] 收到图像大小数据：{image_size}")
    await image_size_queue.put(image_size)
    logger.info(
        f"[WebSocketImageHandler-{unique_id}] 浏览器参数：uuid = {uuid} ，正在等待浏览器连接"
    )
    await browser_connected_event.wait()
    logger.info(f"[WebSocketImageHandler-{unique_id}] 浏览器已连接")
    browser_connected_event.clear()
    await ws.send(json.dumps({"type": "ready"}))
    while True:
        try:
            logger.debug(f"[WebSocketImageHandler-{unique_id}] 等待图像数据")
            payload = await ws.recv()
            current_timestamp_ms = timestamp_ms()
            # 获取图像时间戳
            image_timestamp_ms = current_timestamp_ms - base_timestamp_ms
            logger.debug(
                f"[WebSocketImageHandler-{unique_id}] 收到图像数据：{len(payload)}"
            )
            # 从Payload (bytes) 获取图像数据
            compressed_image = np.frombuffer(payload, dtype=np.uint8)
            decompressed_image = cv2.imdecode(compressed_image, cv2.IMREAD_COLOR)
            logger.debug(f"[WebSocketImageHandler-{unique_id}] 解压成功")
            logger.debug(
                f"[WebSocketImageHandler-{unique_id}] 收到图像尺寸：{decompressed_image.shape}"
            )
            image = MPImageQueueBody.image(image_timestamp_ms, decompressed_image)
            # 将图像数据放入队列
            image_queue.put(image)
            # 从MediaPipe图像处理线程获取结果
            # IMPORTANT: 这里会阻塞，注意和浏览器handler避免产生死锁
            result = result_queue.get()
            logger.debug(f"[WebSocketImageHandler-{unique_id}] 从图像处理线程收到结果")
            result = result.body.to_binary()
            logger.debug(f"[WebSocketImageHandler-{unique_id}] 结果长度：{len(result)}")
            await callback_queue.put(result)
            logger.debug(
                f"[WebSocketImageHandler-{unique_id}] 结果提交至浏览器回调队列"
            )
            if closed_event.is_set():
                logger.info(f"[WebSocketImageHandler-{unique_id}] 浏览器已断开连接")
                del locks[uuid]
                break
        except Exception as e:
            if isinstance(e, websockets.exceptions.ConnectionClosed):
                logger.info(
                    f"[WebSocketImageHandler-{unique_id}] WebSocket连接已关闭，正在关闭MediaPipe图像处理线程"
                )
            elif isinstance(e, KeyboardInterrupt):
                logger.info(
                    f"[WebSocketImageHandler-{unique_id}] 服务器正在关闭，正在关闭MediaPipe图像处理线程"
                )
            else:
                logger.error(
                    f"[WebSocketImageHandler-{unique_id}] 发生错误：{e}，正在关闭MediaPipe图像处理线程"
                )
            result = MPImageQueueBody.closed()
            image_queue.put(result)
            closed_event.set()
            break


async def browser_handler(ws: server.WebSocketServerProtocol):
    unique_id = ws.id.hex[:8]
    path = ws.path
    query = urlparse.parse_qs(urlparse.urlparse(path).query)
    if "uuid" not in query:
        logger.warning(f"[WebSocketBrowserHandler-{unique_id}] 缺少参数 uuid，无效连接")
        await ws.close()
        return
    target_uuid = query["uuid"][0]
    logger.debug(f"[WebSocketBrowserHandler-{unique_id}] 锁列表：{locks.keys()}")
    if target_uuid not in locks.keys():
        logger.warning(f"[WebSocketBrowserHandler-{unique_id}] uuid 无效，无效连接")
        logger.warning(f"[WebSocketBrowserHandler-{unique_id}] uuid = {target_uuid}")
        await ws.close()
        return
    logger.success(f"[WebSocketBrowserHandler-{unique_id}] 成功连接")
    callback_queue, bridge_event, closed_event, image_size_queue = locks[target_uuid]
    bridge_event.set()
    image_size = await image_size_queue.get()
    await ws.send(json.dumps({"type": "ready", "imageSize": image_size}))
    logger.info(f"[WebSocketBrowserHandler-{unique_id}] 已发送准备就绪")
    while True:
        try:
            if closed_event.is_set():
                logger.info(f"[WebSocketBrowserHandler-{unique_id}] 图像处理线程已关闭")
                del locks[target_uuid]
                break
            # IMPORTANT: 这里会阻塞，注意和图像处理handler避免产生死锁
            result = await callback_queue.get()
            logger.debug(
                f"[WebSocketBrowserHandler-{unique_id}] 收到结果：{len(result)}"
            )
            await ws.send(result)
            logger.debug(f"[WebSocketBrowserHandler-{unique_id}] 结果已发送")
        except Exception as e:
            if isinstance(e, websockets.exceptions.ConnectionClosed):
                logger.info(
                    f"[WebSocketBrowserHandler-{unique_id}] WebSocket连接已关闭"
                )
                await closed_event.set()
            elif isinstance(e, KeyboardInterrupt):
                logger.info(f"[WebSocketBrowserHandler-{unique_id}] 服务器正在关闭")
                await closed_event.set()
            else:
                logger.error(f"[WebSocketBrowserHandler-{unique_id}] 发生错误：{e}")
            break


async def handler(ws: server.WebSocketServerProtocol):
    unique_id = ws.id.hex[:8]
    path = ws.path
    parsed_path = urlparse.urlparse(path)
    if parsed_path.path == "/image":
        locks[ws.id.hex] = (
            AsyncQueue[bytes](),
            AsyncEvent(),
            AsyncEvent(),
            AsyncQueue[dict](),
        )
        logger.debug(f"[WebSocketRootHandler-{unique_id}] 已创建锁")
        logger.debug(f"[WebSocketRootHandler-{unique_id}] 锁数量：{len(locks)}")
        await image_handler(ws)
    elif parsed_path.path == "/browser":
        await browser_handler(ws)
    else:
        logger.warning(
            f"[WebSocketRootHandler-{unique_id}] 未知路径：{parsed_path.path}"
        )
        await ws.close()
