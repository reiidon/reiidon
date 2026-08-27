from pathlib import Path
from html import escape

import numpy as np
from PIL import Image, ImageEnhance


# -------------------------------------------------
# Paths
# -------------------------------------------------

ROOT = Path(__file__).resolve().parent.parent

INPUT_PATH = ROOT / "data" / "source-prepped.png"

OUTPUT_PATH = ROOT / "avi-ascii.svg"


# -------------------------------------------------
# Settings
# -------------------------------------------------

WIDTH = 140

RAMP = (
    " "
    "."
    ":"
    "-"
    "="
    "+"
    "*"
    "#"
    "%"
    "@"
)

FONT_SIZE = 7

CHAR_WIDTH = 4.3

LINE_HEIGHT = 8

COLOR = "#c9d1d9"

BACKGROUND = "#0d1117"


# -------------------------------------------------
# Load image
# -------------------------------------------------

print("Loading prepared image...")

image = Image.open(INPUT_PATH).convert("RGBA")


# -------------------------------------------------
# Get person area from transparency
# -------------------------------------------------

alpha = image.getchannel("A")

bbox = alpha.getbbox()


if bbox:

    padding = 8

    left = max(
        0,
        bbox[0] - padding
    )

    top = max(
        0,
        bbox[1] - padding
    )

    right = min(
        image.width,
        bbox[2] + padding
    )

    bottom = min(
        image.height,
        bbox[3] + padding
    )

    image = image.crop(
        (
            left,
            top,
            right,
            bottom
        )
    )


# -------------------------------------------------
# Separate grayscale and transparency
# -------------------------------------------------

gray = image.convert("L")

alpha = image.getchannel("A")


# -------------------------------------------------
# Improve contrast
# -------------------------------------------------

gray = ImageEnhance.Contrast(
    gray
).enhance(1.6)


# -------------------------------------------------
# Calculate size
# -------------------------------------------------

aspect_ratio = (
    image.height
    / image.width
)


HEIGHT = max(
    1,
    int(
        WIDTH
        * aspect_ratio
        * 0.50
    )
)


# -------------------------------------------------
# Resize
# -------------------------------------------------

gray = gray.resize(
    (WIDTH, HEIGHT),
    Image.Resampling.LANCZOS
)


alpha = alpha.resize(
    (WIDTH, HEIGHT),
    Image.Resampling.LANCZOS
)


# -------------------------------------------------
# Convert to NumPy
# -------------------------------------------------

gray_pixels = np.array(gray)

alpha_pixels = np.array(alpha)


# -------------------------------------------------
# Convert pixels to ASCII
# -------------------------------------------------

def pixel_to_char(
    brightness,
    transparency
):

    # Transparent background
    if transparency < 80:

        return " "


    # Convert brightness to darkness
    darkness = 255 - int(brightness)


    # Gamma adjustment
    darkness = (
        darkness / 255
    ) ** 0.8


    index = int(
        darkness
        * (len(RAMP) - 1)
    )


    # Safety
    index = max(
        0,
        min(
            index,
            len(RAMP) - 1
        )
    )


    return RAMP[index]


# -------------------------------------------------
# Create ASCII rows
# -------------------------------------------------

rows = []


for y in range(HEIGHT):

    line = ""

    for x in range(WIDTH):

        character = pixel_to_char(

            gray_pixels[y, x],

            alpha_pixels[y, x]

        )

        line += character


    rows.append(line)


# -------------------------------------------------
# SVG dimensions
# -------------------------------------------------

svg_width = int(
    WIDTH
    * CHAR_WIDTH
    + 40
)


svg_height = int(
    HEIGHT
    * LINE_HEIGHT
    + 50
)


# -------------------------------------------------
# Build SVG
# -------------------------------------------------

parts = []


parts.append(
    f'''<svg
xmlns="http://www.w3.org/2000/svg"
width="{svg_width}"
height="{svg_height}"
viewBox="0 0 {svg_width} {svg_height}"
role="img"
aria-label="ASCII portrait"
>

<style>

.ascii {{
    font-family: monospace;
    font-size: {FONT_SIZE}px;
    font-weight: 400;
    fill: {COLOR};
}}

.row {{
    opacity: 0;
    animation:
        appear
        0.1s
        forwards;
}}

@keyframes appear {{

    from {{
        opacity: 0;
    }}

    to {{
        opacity: 1;
    }}

}}

</style>

<rect
width="100%"
height="100%"
rx="12"
fill="{BACKGROUND}"
/>
'''
)


# -------------------------------------------------
# Add rows
# -------------------------------------------------

for i, line in enumerate(rows):

    y = 28 + (
        i
        * LINE_HEIGHT
    )


    delay = (
        i
        * 0.015
    )


    safe_line = escape(line)


    parts.append(
        f'''
<text
x="20"
y="{y}"
class="ascii row"
xml:space="preserve"
style="animation-delay:{delay:.3f}s"
>{safe_line}</text>
'''
    )


# -------------------------------------------------
# Close SVG
# -------------------------------------------------

parts.append(
    "</svg>"
)


# -------------------------------------------------
# Save
# -------------------------------------------------

OUTPUT_PATH.write_text(

    "".join(parts),

    encoding="utf-8"

)


print()

print("Done!")

print(
    f"Created: {OUTPUT_PATH}"
)

print(
    f"Grid size: {WIDTH} x {HEIGHT}"
)