import board
import neopixel
import time
import threading
import colorsys
from .music_notes import music_notes_pixels_map, music_notes_colors


class LedController:
    def __init__(self, pixel_pin=board.D23, num_pixels: int = 64, brightness: float = 0.2):
        self.pixel_pin = pixel_pin
        self.pixels = neopixel.NeoPixel(
            pixel_pin, num_pixels, auto_write=True, brightness=brightness
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
        num_steps = 200
        sleep_time = 0.02
        hue = 0.0
        while not self._stop_flag.is_set():
            for i in range(num_steps):
                if self._stop_flag.is_set():
                    break
                progress = i / num_steps
                brightness = (1 - abs(2 * progress - 1)) * 0.8 + 0.1
                r, g, b = colorsys.hls_to_rgb(hue, brightness, 1.0)
                self.pixels.fill((int(r * 255), int(g * 255), int(b * 255)))
                self.pixels.show()
                time.sleep(sleep_time)
            hue = (hue + 0.05) % 1.0

    def _rainbow_chase_loop(self):
        num_heads = 5
        tail_length = 15
        speed = 2
        pixel_count = self.pixels.n
        positions = [0] * num_heads
        hues = [i / num_heads for i in range(num_heads)]
        while not self._stop_flag.is_set():
            self.pixels.fill((0, 0, 0))
            for head in range(num_heads):
                for t in range(tail_length, 0, -1):
                    idx = (positions[head] - t) % pixel_count
                    fade = (1 - t / tail_length) * 0.9 + 0.1
                    r, g, b = colorsys.hls_to_rgb(hues[head], 0.5 * fade, 0.6)
                    self.pixels[idx] = (int(r * 255), int(g * 255), int(b * 255))
                head_brightness = colorsys.hls_to_rgb(hues[head], 0.5, 0.7)
                self.pixels[positions[head]] = (int(head_brightness[0] * 255), int(head_brightness[1] * 255), int(head_brightness[2] * 255))
            self.pixels.show()
            time.sleep(0.03)
            for head in range(num_heads):
                positions[head] = (positions[head] + speed) % pixel_count
            hues = [(h + 0.008) % 1.0 for h in hues]

    def chase(self, color):
        """Run a chase loop with the given color (r, g, b tuple)."""
        self._start_effect(lambda: self._chase_loop(color))

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

    def gain_note(self, note_name: str, color=None):
        """Light up all pixels for the given note name."""
        if note_name not in music_notes_pixels_map:
            return
        if color is None:
            color = music_notes_colors.get(note_name, (255, 255, 255))
        for idx in music_notes_pixels_map[note_name]:
            if 0 <= idx < self.pixels.n:
                self.pixels[idx] = color
        self.pixels.show()

    def drop_note(self, note_name: str):
        """Turn off all pixels for the given note name."""
        if note_name not in music_notes_pixels_map:
            return
        for idx in music_notes_pixels_map[note_name]:
            if 0 <= idx < self.pixels.n:
                self.pixels[idx] = (0, 0, 0)
        self.pixels.show()

    def play_note(self, note_name: str, color=None):
        """Flash effect: off-on-off-on, then leave lit."""
        if note_name not in music_notes_pixels_map:
            return
        if color is None:
            color = music_notes_colors.get(note_name, (255, 255, 255))
        indices = [idx for idx in music_notes_pixels_map[note_name] if 0 <= idx < self.pixels.n]

        # Step 1: off
        for idx in indices:
            self.pixels[idx] = (0, 0, 0)
        self.pixels.show()
        time.sleep(0.1)

        # Step 2: on
        for idx in indices:
            self.pixels[idx] = color
        self.pixels.show()
        time.sleep(0.1)

        # Step 3: off
        for idx in indices:
            self.pixels[idx] = (0, 0, 0)
        self.pixels.show()
        time.sleep(0.1)

        # Step 4: on (stay lit)
        for idx in indices:
            self.pixels[idx] = color
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

    
    
