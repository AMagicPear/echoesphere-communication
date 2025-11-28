import board
import neopixel
import time

pixel_pin = board.D18
num_pixels = 15

pixels = neopixel.NeoPixel(pixel_pin, num_pixels, auto_write=False, brightness=0.05)

if __name__ == "__main__":
    while True:
        # 全红
        pixels.fill((255, 0, 0))
        pixels.show()
        time.sleep(1)

        # 全绿
        pixels.fill((0, 255, 0))
        pixels.show()
        time.sleep(1)

        # 跑马灯
        for i in range(num_pixels):
            pixels.fill((0, 0, 0))
            pixels[i] = (0, 0, 255)
            pixels.show()
            time.sleep(0.05)