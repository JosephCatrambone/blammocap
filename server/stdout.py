#!/usr/bin/env python

import asyncio
import time

from websockets.asyncio.server import serve

from datamodels import Point, Detection, Frame 

async def echo(websocket):
    async for message in websocket:
        print(message)
        await websocket.send(message)

async def track(websocket):
    async for message in websocket:
        try:
            f = Frame.model_validate_json(message)
            print(f)
        except KeyboardInterrupt:
            return
        except Exception as e:
            print(f"Exception during processing: {e}")

async def main():
    async with serve(track, "0.0.0.0", 8765) as server:
        await server.serve_forever()

asyncio.run(main())

