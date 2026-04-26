"""TCP client with length-prefixed JSON protocol and subscription-based callbacks.

Protocol
--------
Each message is encoded as:
  - 4 bytes (big-endian unsigned int): byte length of the UTF-8 JSON payload
  - N bytes: UTF-8 encoded JSON

JSON structure:
  {"type": "text"|"image"|"command"|"register", "data": <content>}

For "text": data is the text string
For "image": data is base64 encoded image bytes
For "register": data is {"client_type": "...", "subtype": "..."}

All integers use network byte order (big-endian).

Subscription API
---------------
Use += to subscribe and -= to unsubscribe::

    client.on_text += lambda msg: print(msg)
    client.on_image += lambda img: handle(img)
    client.on_command += lambda msg: process(msg)

    # unsubscribe
    def handler(msg):
        ...
    client.on_command += handler
    client.on_command -= handler

Or use subscribe()::

    client.subscribe("text", lambda msg: ...)
    client.unsubscribe("text", lambda msg: ...)
"""

from __future__ import annotations

import asyncio
import base64
import json
import logging
import struct
from typing import Callable, Optional

logger = logging.getLogger("TcpClient")


class _Event:
    """A simple event that holds a list of callbacks and dispatches to all of them."""

    def __init__(self, name: str) -> None:
        self._name = name
        self._callbacks: list[Callable] = []

    def __iadd__(self, callback: Callable) -> _Event:
        """Subscribe a handler with +=, e.g. client.on_text += handler."""
        self._callbacks.append(callback)
        return self

    def __isub__(self, callback: Callable) -> _Event:
        """Unsubscribe a handler with -=, e.g. client.on_text -= handler."""
        self._callbacks.remove(callback)
        return self

    def subscribe(self, callback: Callable) -> None:
        """Explicit subscribe."""
        self._callbacks.append(callback)

    def unsubscribe(self, callback: Callable) -> None:
        """Explicit unsubscribe."""
        self._callbacks.remove(callback)

    def dispatch(self, *args, **kwargs) -> None:
        for cb in self._callbacks:
            try:
                cb(*args, **kwargs)
            except Exception:
                logger.exception(f"Error in {self._name} handler")


class TcpClient:
    """Async TCP client that connects to a single server.

    Supports text and image messages with a length-prefixed JSON framing protocol.
    Uses subscription-based callbacks::

        client = TcpClient("127.0.0.1", 65432)
        client.on_text += lambda msg: print(f"Received: {msg}")
        client.on_command += lambda msg: handle(msg)
    """

    def __init__(self, host: str, port: int) -> None:
        self.host = host
        self.port = port

        # Subscription-based events
        self.on_text = _Event("on_text")
        self.on_image = _Event("on_image")
        self.on_command = _Event("on_command")

        self._reader: Optional[asyncio.StreamReader] = None
        self._writer: Optional[asyncio.StreamWriter] = None
        self._receive_task: Optional[asyncio.Task[None]] = None

    async def connect(self) -> None:
        self._reader, self._writer = await asyncio.open_connection(self.host, self.port)
        self._receive_task = asyncio.create_task(self._receive_loop())
        logger.info(f"Connected to {self.host}:{self.port}")

    async def _receive_loop(self) -> None:
        try:
            while True and self._reader:
                length_data = await self._reader.readexactly(4)
                total_length = struct.unpack(">I", length_data)[0]
                json_data = await self._reader.readexactly(total_length)
                msg_obj = json.loads(json_data.decode("utf-8"))

                msg_type = msg_obj.get("type")
                data = msg_obj.get("data", "")

                if msg_type == "text":
                    self.on_text.dispatch(data)
                elif msg_type == "image":
                    img_bytes = base64.b64decode(data)
                    self.on_image.dispatch(img_bytes)
                elif msg_type == "command":
                    self.on_command.dispatch(msg_obj)
                else:
                    logger.warning(f"Unknown message type: {msg_type}")
        except asyncio.IncompleteReadError:
            logger.info("Connection closed by peer")
        except ConnectionResetError:
            logger.warning("Connection reset")
        except Exception:
            logger.exception("Error in receive loop")
        finally:
            await self.close()

    def _send_json(self, obj: dict) -> "asyncio.StreamWriter":
        """Send a JSON object with length-prefixed framing. Returns the writer if connected."""
        if not self._writer:
            logger.warning("Not connected")
            raise ConnectionError("Not connected")
        json_str = json.dumps(obj, ensure_ascii=False)
        json_bytes = json_str.encode("utf-8")
        length_prefix = struct.pack(">I", len(json_bytes))
        self._writer.write(length_prefix + json_bytes)
        return self._writer

    async def send_text(self, text: str) -> None:
        """Send a UTF-8 text message."""
        try:
            writer = self._send_json({"type": "text", "data": text})
            await writer.drain()
            logger.debug(f"Text sent: {text[:100]}")
        except ConnectionError:
            pass

    async def send_image(self, image_bytes: bytes) -> None:
        """Send image bytes as base64-encoded JSON."""
        try:
            img_b64 = base64.b64encode(image_bytes).decode("ascii")
            writer = self._send_json({"type": "image", "data": img_b64})
            await writer.drain()
            logger.debug(
                f"Image sent ({len(image_bytes)} bytes, base64 {len(img_b64)} chars)"
            )
        except ConnectionError:
            pass

    async def send_register(self, client_type: str) -> None:
        """Send registration message to server."""
        try:
            writer = self._send_json({"type": "register", "client_type": client_type})
            await writer.drain()
            logger.info("Register sent.")
        except ConnectionError:
            pass

    async def send_command(self, data: str, relay_to: str) -> None:
        """Send a command message directly (not wrapped in text envelope)."""
        try:
            writer = self._send_json({"type": "command", "data": data, "relay_to": relay_to})
            await writer.drain()
        except ConnectionError:
            pass

    async def close(self) -> None:
        if self._writer:
            self._writer.close()
            await self._writer.wait_closed()
            self._writer = None
        if self._receive_task:
            self._receive_task.cancel()
            self._receive_task = None
