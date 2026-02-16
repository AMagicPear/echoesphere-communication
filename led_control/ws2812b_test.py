import board
import neopixel
import time

pixel_pin_1 = board.D23
num_pixels_1 = 150

pixel_pin_2 = board.D18
num_pixels_2 = 101

pixels_1 = neopixel.NeoPixel(
    pixel_pin_1, num_pixels_1, auto_write=False, brightness=0.2
)
pixels_2 = neopixel.NeoPixel(
    pixel_pin_2, num_pixels_2, auto_write=False, brightness=0.2
)

pixels = pixels_2

if __name__ == "__main__":
    for i in range(max(num_pixels_1, num_pixels_2)):
        pixels_1.fill((0, 0, 0))
        pixels_2.fill((0, 0, 0))
        pixels_1[i] = (255, 0, 0)
        if i < num_pixels_1 - 1:
            pixels_1[i+1] = (0, 0, 255)
        if i < num_pixels_2:
            pixels_2[i] = (0, 255, 0)
        if 2 * i < num_pixels_1:
            pixels_1[2 * i] = (0, 0, 255)
        if 2 * i + 1 < num_pixels_1:
            pixels_1[2 * i + 1] = (255, 255, 0)
        pixels_1.show()
        pixels_2.show()
        time.sleep(0.05)
    pixels_1.deinit()
    pixels_2.deinit()
