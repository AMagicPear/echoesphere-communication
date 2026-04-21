import board
import neopixel
import time
import threading


class LedController:
    def __init__(self, pixel_pin=board.D23, num_pixels: int = 150):
        self.pixel_pin = pixel_pin
        self.pixels = neopixel.NeoPixel(
            pixel_pin, num_pixels, auto_write=True, brightness=0.5
        )
        self._running_thread = None
        self._stop_flag = threading.Event()

    def deinit_leds(self):
        self._stop_flag.set()
        self.pixels.deinit()

    def _chase_loop(self, color):
        for i in range(self.pixels.n):
            if self._stop_flag.is_set():
                break
            self.pixels.fill((0, 0, 0))
            self.pixels[i] = color
            self.pixels.show()
            time.sleep(0.05)

    def _breathing_loop(self):
        colors = [
            (255, 0, 0),
            (255, 127, 0),
            (255, 255, 0),
            (0, 255, 0),
            (0, 255, 255),
            (0, 0, 255),
            (127, 0, 255),
            (255, 0, 127),
        ]
        while not self._stop_flag.is_set():
            for color in colors:
                if self._stop_flag.is_set():
                    break
                for brightness in [0.1, 0.3, 0.5, 0.3]:
                    if self._stop_flag.is_set():
                        break
                    self.pixels.fill(color)
                    self.pixels.brightness = brightness
                    self.pixels.show()
                    time.sleep(0.5)

    def _rainbow_chase_loop(self):
        colors = [
            (255, 0, 0),
            (255, 127, 0),
            (255, 255, 0),
            (0, 255, 0),
            (0, 255, 255),
            (0, 0, 255),
            (127, 0, 255),
            (255, 0, 127),
        ]
        color_idx = 0
        while not self._stop_flag.is_set():
            for i in range(self.pixels.n):
                if self._stop_flag.is_set():
                    break
                self.pixels.fill((0, 0, 0))
                self.pixels[i] = colors[color_idx]
                self.pixels.show()
                time.sleep(0.05)
            color_idx = (color_idx + 1) % len(colors)

    def green_chase(self):
        self._start_effect(lambda: self._chase_loop((0, 255, 0)))

    def red_chase(self):
        self._start_effect(lambda: self._chase_loop((255, 0, 0)))

    def blue_chase(self):
        self._start_effect(lambda: self._chase_loop((0, 0, 255)))

    def rainbow_chase(self):
        self._start_effect(self._rainbow_chase_loop)

    def breathing(self):
        self._start_effect(self._breathing_loop)

    def solid(self, color):
        self._stop_effect()
        self.pixels.fill(color)
        self.pixels.show()

    def clear(self):
        self._stop_effect()
        self.pixels.fill((0, 0, 0))
        self.pixels.show()

    def _start_effect(self, effect_func):
        self._stop_effect()
        self._stop_flag.clear()
        self._running_thread = threading.Thread(target=effect_func)
        self._running_thread.daemon = True
        self._running_thread.start()

    def _stop_effect(self):
        self._stop_flag.set()
        if self._running_thread and self._running_thread.is_alive():
            self._running_thread.join(timeout=0.5)
        self._running_thread = None


if __name__ == "__main__":
    led = LedController()
    try:
        led.green_chase()
        time.sleep(5)
    finally:
        led.deinit_leds()
    
    
