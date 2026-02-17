import asyncio
import struct

class TcpClient:
    def __init__(self, host, port, on_message=None):
        self.host = host
        self.port = port
        self.on_message = on_message or (lambda msg: print(f"收到消息: {msg}"))
        self.reader = None
        self.writer = None
        self._receive_task = None

    async def connect(self):
        """连接到服务器"""
        self.reader, self.writer = await asyncio.open_connection(self.host, self.port)
        self._receive_task = asyncio.create_task(self._receive_loop())
        print("已连接到服务器")

    async def _receive_loop(self):
        """持续接收消息"""
        try:
            while True:
                # 读取4字节长度（网络字节序）
                length_data = await self.reader.readexactly(4)
                msg_length = struct.unpack('!i', length_data)[0]  # '!i' 表示网络字节序的 int

                # 读取消息内容
                msg_data = await self.reader.readexactly(msg_length)
                message = msg_data.decode('utf-8')
                self.on_message(message)
        except (asyncio.IncompleteReadError, ConnectionResetError):
            print("连接关闭")
        finally:
            self.writer.close()
            await self.writer.wait_closed()
            self.writer = None

    async def send(self, message):
        """发送消息"""
        if self.writer is None:
            print("未连接")
            return

        data = message.encode('utf-8')
        # 发送4字节长度（网络字节序）
        self.writer.write(struct.pack('!i', len(data)))
        self.writer.write(data)
        await self.writer.drain()
        print(f"发送: {message}")

    async def close(self):
        """关闭连接"""
        if self.writer:
            self.writer.close()
            await self.writer.wait_closed()
        if self._receive_task:
            self._receive_task.cancel()

async def main():
    client = TcpClient("192.168.1.103", 65432)
    await client.connect()

    # 示例：定时发送消息
    async def send_periodic():
        counter = 0
        while True:
            await asyncio.sleep(2)
            await client.send(f"来自Python的消息 {counter}")
            counter += 1

    send_task = asyncio.create_task(send_periodic())

    try:
        await asyncio.Future()
    except KeyboardInterrupt:
        pass
    finally:
        send_task.cancel()
        await client.close()

if __name__ == "__main__":
    asyncio.run(main())
