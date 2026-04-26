import board
import neopixel
import time

pixel_pin = board.D23
num_pixels = 150

pixels = neopixel.NeoPixel(
    pixel_pin, num_pixels, auto_write=True, brightness=0.5
)

if __name__ == "__main__":
    while True:
        for i in range(num_pixels):
            pixels.fill((0, 0, 0))
            pixels[i] = (0, 255, 0)
            pixels.show()
            time.sleep(0.05)
