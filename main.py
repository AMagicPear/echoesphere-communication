import asyncio

import websockets

HOST = "0.0.0.0"
PORT = 65432

async def echo(websocket: websockets.ServerConnection):
    async for message in websocket:
        print(f"收到消息: {message}")
        await websocket.send(f"服务器响应，收到消息：{message}")


async def main():
    async with websockets.serve(echo, HOST, PORT):
        await asyncio.Future()  # 持续运行

if __name__ == "__main__":
    asyncio.run(main())
