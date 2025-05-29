import asyncio
import websockets

async def wss_handler(websocket):
    async for message in websocket:
        print(f"收到消息: {message}")
        await websocket.send(f"已收到: {message}")

async def main():
    print("Listening on port 80")
    async with websockets.serve(
        wss_handler,
        host="0.0.0.0",
        port=80
    ):
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())