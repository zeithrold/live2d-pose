import asyncio

import websockets
from args import args
from loguru import logger
from ws import handler

logger.add("app.log")

ip = args.ip
port = args.port

async def main():
    async with websockets.serve(
        handler, ip, port, ping_interval=None, ping_timeout=None
    ):
        # IMPORTANT: websockets库自带keepalive机制，若频度过高将会导致无空隙await keepalive
        # 务必注意提交视频内容的时候不要帧率过高
        logger.success(f"[MainThread] WebSocket服务器已启动于 ws://{ip}:{port}")
        logger.info(
            f"[MainThread] 若要开始，请将图像通过WebSocket发送至ws://{ip}:{port}/image"
        )
        await asyncio.Future()


asyncio.run(main())
