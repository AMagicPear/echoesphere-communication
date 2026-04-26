"""调试文件：点亮全部LED"""
import board
import neopixel

# 配置
PIXEL_PIN = board.D23
NUM_PIXELS = 64

if __name__ == "__main__":
    pixels = neopixel.NeoPixel(PIXEL_PIN, NUM_PIXELS, auto_write=True, brightness=0.05)

    print(f"点亮全部 {NUM_PIXELS} 颗LED...")
    pixels.fill((255, 255, 255))  # 白色
    pixels.show()

    print("完成，按 Ctrl+C 退出")
    try:
        while True:
            pass
    except KeyboardInterrupt:
        pixels.fill((0, 0, 0))
        pixels.show()
        pixels.deinit()
        print("\n已关闭LED")