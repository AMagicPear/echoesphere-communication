import asyncio
from client import TcpClient
from datetime import datetime
import logging
from led_control.led_controller import LedController

# 配置日志
LOG_FILE = f"logs/echo_pi_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
    ],
)
logger = logging.getLogger("Pi")


def handle_command(command: str, led: LedController):
    logger.info(f"received command: {command}")
    if command == "green":
        led.green_chase()
    elif command == "red":
        led.red_chase()
    elif command == "blue":
        led.blue_chase()
    elif command == "rainbow":
        led.rainbow_chase()
    elif command == "breathing":
        led.breathing()
    elif command == "off":
        led.clear()


async def main():
    led = LedController()
    client = TcpClient(
        "192.168.2.1", 65432, lambda cmd: handle_command(cmd, led), on_text=lambda msg: logger.info(msg)
    )
    await client.connect()
    await client.send_register("raspberry_pi")

    # async def periodic_send() -> None:
    #     for i in range(5):
    #         await asyncio.sleep(1)
    #         await client.send_text(f"Ping from raspberry_pi: {i}")

    # send_task = asyncio.create_task(periodic_send())
    try:
        await asyncio.Future()
    except KeyboardInterrupt:
        logger.info("Interrupted")
    finally:
        led.deinit_leds()
        await client.close()


if __name__ == "__main__":
    asyncio.run(main())
