import board
import neopixel
import time

pixel_pin = board.D18
num_pixels = 10

pixels = neopixel.NeoPixel(pixel_pin, num_pixels, auto_write=False, brightness=0.05)

if __name__ == "__main__":
    for i in range(num_pixels):
        pixels.fill((0, 0, 0))
        for j in range(0, i):
            pixels[j] = (255, j * 20 % 255, 0)
        pixels.show()
        time.sleep(0.5)
    # while True:
    #     # 全红
    #     pixels.fill((255, 0, 0))
    #     pixels.show()
    #     time.sleep(1)

    #     # 全绿
    #     pixels.fill((0, 255, 0))
    #     pixels.show()
    #     time.sleep(1)

    #     # 跑马灯
    #     for i in range(num_pixels):
    #         pixels.fill((0, 0, 0))
    #         pixels[i] = (195, 175, 76)
    #         pixels.show()
    #         time.sleep(0.05)