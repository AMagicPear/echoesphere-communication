import asyncio
from echoesphere_lights.client import TcpClient
from datetime import datetime
import logging
import argparse
from echoesphere_lights.led_controller import LedController

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
    colors = {
        "green": (0, 255, 0),
        "lightgreen": (0, 255, 128),
        "red": (255, 0, 0),
        "blue": (0, 0, 255),
        "white": (255, 255, 255),
        "yellow": (255, 255, 0),
        "cyan": (0, 255, 255),
        "magenta": (255, 0, 255),
    }

    if command == "off":
        led.clear()
    elif command == "breathing":
        led.breathing()
    elif command == "rainbow":
        led.rainbow_chase()
    elif command.startswith("chase:"):
        color_name = command.split(":", 1)[1]
        if color_name in colors:
            led.chase(colors[color_name])
    elif command.startswith("solid:"):
        color_name = command.split(":", 1)[1]
        if color_name in colors:
            led.solid(colors[color_name])
    elif command.startswith("gain_note:"):
        note_name = command.split(":", 1)[1]
        led.gain_note(note_name)
    elif command.startswith("drop_note:"):
        note_name = command.split(":", 1)[1]
        led.drop_note(note_name)
    elif command.startswith("play_note:"):
        note_name = command.split(":", 1)[1]
        led.play_note(note_name)


async def main():
    parser = argparse.ArgumentParser(description="Echoesphere Communication Client")
    parser.add_argument("--host", default="PerryTree.local", help="Server host address")
    parser.add_argument("--port", type=int, default=65432, help="Server port")
    parser.add_argument("--pixels", type=int, default=64, help="Number of LED pixels")
    parser.add_argument("--brightness", type=float, default=0.2, help="LED brightness (0.0-1.0)")
    args = parser.parse_args()

    led = LedController(num_pixels=args.pixels, brightness=args.brightness)
    client = TcpClient(args.host, args.port)
    client.on_command += lambda msg: handle_command(msg.get("data", ""), led)
    client.on_text += lambda msg: logger.info(msg)
    await client.connect()
    await client.send_register("raspberry_pi")
    
    try:
        await asyncio.Future()
    except KeyboardInterrupt:
        logger.info("Interrupted")
    finally:
        led.deinit_leds()
        await client.close()


if __name__ == "__main__":
    asyncio.run(main())
