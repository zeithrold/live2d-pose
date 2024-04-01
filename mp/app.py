import asyncio
from argparse import ArgumentParser

import websockets.server as serve
from loguru import logger
from ws import handler

logger.add("app.log")

argparser = ArgumentParser()
argparser.description = "启动WebSocket服务器"
argparser.add_argument(
    "--ip", "-i", default="localhost", type=str, help="server ip to bind"
)
argparser.add_argument(
    "--port", "-p", default=8765, type=int, help="server port to bind"
)
args = argparser.parse_args()

ip = args.ip
port = args.port


async def main():
    async with serve.serve(handler, ip, port):
        logger.success(f"[MainThread] WebSocket服务器已启动于 ws://{ip}:{port}")
        logger.info(
            f"[MainThread] 若要开始，请将图像通过WebSocket发送至ws://{ip}:{port}/image"
        )
        await asyncio.Future()


asyncio.run(main())
