# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Echoesphere Communication - a Raspberry Pi client that reads sensors and sends data to Echoesphere main server, also receives commands to control WS2812B LED strips.

## Running the Application

```bash
# Run main.py (requires Raspberry Pi hardware)
python main.py

# Run LED test directly
python led_control/led_controller.py
```

## Architecture

```
main.py                 # Entry point, connects TCP client and LED controller
client.py               # TcpClient with length-prefixed JSON protocol
led_control/
  led_controller.py    # LedController class with light effects
  ws2812b_test.py       # Original LED test code
  deinit_leds.py        # LED cleanup utility
```

## TCP Protocol

Communication with server uses a length-prefixed JSON protocol:
- 4 bytes (big-endian): payload length
- N bytes: UTF-8 JSON

JSON message types: `text`, `image`, `command`, `register`

## LED Commands

The server sends color names as commands, which are translated to RGB tuples:
- `green`, `red`, `blue`, `white`, `yellow`, `cyan`, `magenta` - Chase loop with that color
- `off` - Turn off all LEDs

## Key Dependencies

- `neopixel` / `rpi_ws281x` - WS2812B LED control
- `board` - Raspberry Pi GPIO
- `asyncio` - Async TCP communication