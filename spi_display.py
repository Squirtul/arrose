
import os
import sys
import time

from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from waveshare_lib import LCD_2inch4

IMAGE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "vatsim.png")
POLL_SECONDS = 5


def build_display():
    disp = LCD_2inch4.LCD_2inch4(spi_freq=4000000)
    disp.Init()
    disp.clear()
    disp.bl_DutyCycle(80)  # 80% backlight brightness
    return disp


def fit_to_screen(img, target_w, target_h):
    scale = min(target_w / img.width, target_h / img.height)
    new_size = (int(img.width * scale), int(img.height * scale))
    resized = img.resize(new_size, Image.LANCZOS)

    canvas = Image.new("RGB", (target_w, target_h), (0, 0, 0))
    offset = ((target_w - new_size[0]) // 2, 0)
    canvas.paste(resized, offset)
    return canvas


def main():
    disp = build_display()
    last_mtime = None

    print("arrose SPI display running, watching", IMAGE_PATH)

    while True:
        try:
            mtime = os.path.getmtime(IMAGE_PATH)
            if mtime != last_mtime:
                img = Image.open(IMAGE_PATH).convert("RGB")
                img = fit_to_screen(img, disp.width, disp.height)
                disp.ShowImage(img)
                last_mtime = mtime
        except FileNotFoundError:
            pass
        except Exception as exc:
            print("arrose SPI display error:", exc)

        time.sleep(POLL_SECONDS)

if __name__ == "__main__":
    main()
