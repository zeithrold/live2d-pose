import websockets.server as serve
import asyncio
import os
import mediapipe as mp
from loguru import logger

async def protocol(ws: serve.WebSocketServerProtocol):
    pass

async def echo(ws: serve.WebSocketServerProtocol):
    async for msg in ws:
        logger.info(f"Received message: {msg}")
        await ws.send(msg)

async def main():
    try:
        async with serve.serve(echo, "localhost", 8765):
            logger.success("Server running on ws://localhost:8765")
            await asyncio.Future()
    except KeyboardInterrupt:
        logger.info("Shutting down server")

asyncio.run(main())
