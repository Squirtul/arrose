
# makes an image.. oh this file is FUN!

from PIL import Image, ImageDraw, ImageFont
import math
import os
from airports import AIRPORT_NAMES
from config import RING_LENGTH
from config import AIRPORT
from controllers import sfxs

AIRPORT_LABEL = AIRPORT
if AIRPORT in AIRPORT_NAMES:
    AIRPORT_LABEL = f"{AIRPORT} - {AIRPORT_NAMES[AIRPORT]}"

SIZE = 600 # could make this screen size? works fine as it is though
CENTER_X = SIZE // 2
OUTER_MARGIN = 10 # gap at very top/bottom
LABEL_GAP = 20 # gap between circle diagram and name label
BAR_HEIGHT = 102 # height of controller bar
BAR_TOP_PADDING = 32  # gap between squares and top border
SQUARE_SIZE = 44  # gap for squares
BAR_SQUARE_GAP = 10  # horizontal gap between squares
DIAGRAM_TOP_GAP = 15 # more to push the diagram further down.. looks more balanced that way. this one is theoretically futile
DIAGRAM_EXTRA_OFFSET = 10 # extra nudge down
CANVAS_WIDTH = SIZE
TARGET_DISPLAY_WIDTH = 240 # resolution of display used. can be rid of if connecting via hdmi
TARGET_DISPLAY_HEIGHT = 320
CANVAS_HEIGHT = int(SIZE * TARGET_DISPLAY_HEIGHT / TARGET_DISPLAY_WIDTH)
BACKGROUND = (0, 0, 0) # background white
INNER_RING_COLOUR = (220, 220, 220) # grey ring
INNER_RING_STROKE = 4 # would keep this

# controller categories
STYLES = {
    "DEL": ((20, 110, 255), "D"),
    "GND": ((0, 170, 90), "G"),
    "TWR": ((220, 40, 40), "T"),
    "APP": ((255, 140, 0), "A"),
    "ACC": ((150, 150, 150), "A"),
}

# nice fonts on the OS to try and use. falls back to PILs font if none available
tryFonts = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf",
]

def getColour(v):
    if v == 0:
        return BACKGROUND #white if area empty
    if v == 1:
        return (0, 120, 255) # blue for 1 acft in that area
    if v == 2:
        return (0, 200, 120) # green for 2
    if v == 3:
        return (255, 200, 0) # yellow for 3
    if v == 4:
        return (255, 120, 0) # orange for 4
    return (255, 0, 0) # red for 5

def load_font(size):
    for path in tryFonts: # tries local fonts
        if os.path.exists(path):
            return ImageFont.truetype(path, size)
    return ImageFont.load_default() # otherwise falls back to silly PIL font

STRIP_HEIGHT = 4 # strips below controller icons to show if multiple are online (up to 3)
STRIP_GAP = 4 # gap between strips

def drawControllerBar(draw, category_counts):
    category_counts = category_counts or {}
    active = [cat for cat in sfxs if category_counts.get(cat, 0) > 0]

    if not active:
        return

    square_size = SQUARE_SIZE
    font = load_font(int(square_size * 0.6))

    total_width = (len(active) * square_size + (len(active) - 1) * BAR_SQUARE_GAP)
    start_x = (CANVAS_WIDTH - total_width) // 2
    y0 = BAR_TOP_PADDING
    y1 = y0 + square_size

    for i, cat in enumerate(active):
        colour, letter = STYLES[cat]
        x0 = start_x + i * (square_size + BAR_SQUARE_GAP)
        x1 = x0 + square_size

        draw.rectangle([x0, y0, x1, y1], fill=colour) # background

        bbox = draw.textbbox((0, 0), letter, font=font) # drawing boxes
        tw = bbox[2] - bbox[0]
        th = bbox[3] - bbox[1]
        tx = x0 + (square_size - tw) // 2 - bbox[0]
        ty = y0 + (square_size - th) // 2 - bbox[1]

        draw.text((tx, ty), letter, font=font, fill=(255, 255, 255))

        extra = category_counts[cat] - 1 # number of extra stripe
        strip_y = y1 + STRIP_GAP
        for _ in range(extra):
            draw.rectangle(
                [x0, strip_y, x1, strip_y + STRIP_HEIGHT], fill=colour # drawing strips
            )
            strip_y += STRIP_HEIGHT + STRIP_GAP


# main render

def draw_grid(grid, category_counts=None):

    rings = len(grid)
    sectors = len(grid[0])

    denominator = 2 + (1 / rings)
    max_radius = (SIZE - LABEL_GAP - (2 * OUTER_MARGIN)) / denominator

    ring_step = max_radius / rings # find depth of rings based on given max size of diagram
    font_size = max(int(ring_step), 10)
    font = load_font(font_size)

    circle_center_y = OUTER_MARGIN + max_radius
    y_offset = BAR_HEIGHT + DIAGRAM_TOP_GAP

    img = Image.new("RGB", (CANVAS_WIDTH, CANVAS_HEIGHT), BACKGROUND)
    pixels = img.load() # we now have our base image. it's put into pixels so can directly manipulate these for the diagram

    sector_step = (2 * math.pi) / sectors

    # pixel shenanigans
    for y in range(SIZE):
        for x in range(SIZE):

            dx = x - CENTER_X
            dy = y - circle_center_y

            r = math.sqrt(dx * dx + dy * dy)

            if r > max_radius:
                continue # don't colour outside the diagram

            # ring index
            ring = int(r / ring_step)
            if ring >= rings:
                continue
            
            if ring == 0:
                if r >= ring_step - INNER_RING_STROKE:
                    pixels[x, y + y_offset + DIAGRAM_EXTRA_OFFSET] = INNER_RING_COLOUR # inner ring is always white! its actually calculated including the centrepiece, then shifted up lol
                continue

            angle = math.atan2(dy, dx)
            angle = (math.degrees(angle) + 450) % 360
            sector = int(angle // (360 / sectors)) % sectors
            value = grid[ring][sector]
            pixels[x, y + y_offset + DIAGRAM_EXTRA_OFFSET] = getColour(value) # drawing sectors

    draw = ImageDraw.Draw(img)

    # name label
    label_font = font
    label_max_width = CANVAS_WIDTH - (2 * OUTER_MARGIN)
    bbox = draw.textbbox((0, 0), AIRPORT_LABEL, font=label_font)
    text_width = bbox[2] - bbox[0]

    label_font_size = font_size
    while text_width > label_max_width and label_font_size > 8:
        label_font_size -= 1
        label_font = load_font(label_font_size)
        bbox = draw.textbbox((0, 0), AIRPORT_LABEL, font=label_font)
        text_width = bbox[2] - bbox[0]

    text_height = bbox[3] - bbox[1]

    text_x = (SIZE - text_width) // 2
    text_y = int(circle_center_y + max_radius + LABEL_GAP) + y_offset + 64

    draw.text((text_x, text_y), AIRPORT_LABEL, font=label_font, fill=(255, 255, 255)) # drawing label

    # add the bar ontop
    drawControllerBar(draw, category_counts)

    # optional little text in bottom corner
    icon_font_size = int(SQUARE_SIZE * 0.6)
    placeholder_font_size = max(int(icon_font_size * 0.65), 6)
    placeholder_font = load_font(placeholder_font_size)

    placeholder_margin_left = 8
    placeholder_margin_bottom = 18 
    ph_bbox = draw.textbbox((0, 0), "placeholder", font=placeholder_font)
    ph_x = placeholder_margin_left - ph_bbox[0]
    ph_y = CANVAS_HEIGHT - placeholder_margin_bottom - (ph_bbox[3] - ph_bbox[1]) - ph_bbox[1]

    draw.text((ph_x, ph_y), "", font=placeholder_font, fill=(255, 255, 255))
    # put optional text here ^

    output = os.path.join(os.getcwd(), "vatsim.png")
    img.save(output) # save image

    print("Saved to ", output)
