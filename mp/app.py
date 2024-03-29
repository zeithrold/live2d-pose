import asyncio

import websockets.server as serve
from loguru import logger
from ws import handler


async def main():
    try:
        async with serve.serve(handler, "localhost", 8765):
            logger.success("Server running on ws://localhost:8765")
            await asyncio.Future()
    except KeyboardInterrupt:
        logger.info("Shutting down server")


asyncio.run(main())
