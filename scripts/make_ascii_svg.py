from pathlib import Path
from html import escape

import numpy as np
from PIL import Image, ImageEnhance, ImageFilter


# =================================================
# PATHS — KEEP EXISTING CONNECTIONS
# =================================================

ROOT = Path(__file__).resolve().parent.parent

INPUT_PATH = ROOT / "data" / "source-prepped.png"

OUTPUT_PATH = ROOT / "avi-ascii.svg"


# =================================================
# SETTINGS
# =================================================

WIDTH = 150

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
CHAR_WIDTH = 4.25
LINE_HEIGHT = 8

BACKGROUND = "#07090d"
PANEL = "#0d1117"

TEXT_COLOR = "#c9d1d9"
ACCENT = "#58a6ff"
ACCENT_DARK = "#1f6feb"
MUTED = "#8b949e"


# =================================================
# LOAD IMAGE
# =================================================

print("Loading prepared image...")

image = Image.open(INPUT_PATH).convert("RGBA")


# =================================================
# CROP USING TRANSPARENCY
# =================================================

alpha = image.getchannel("A")

bbox = alpha.getbbox()

if bbox:

    padding_x = 12
    padding_y = 8

    left = max(0, bbox[0] - padding_x)
    top = max(0, bbox[1] - padding_y)

    right = min(
        image.width,
        bbox[2] + padding_x
    )

    bottom = min(
        image.height,
        bbox[3] + padding_y
    )

    image = image.crop(
        (
            left,
            top,
            right,
            bottom
        )
    )


# =================================================
# GRAYSCALE + ALPHA
# =================================================

gray = image.convert("L")

alpha = image.getchannel("A")


# =================================================
# IMPROVE FACE DETAIL
# =================================================

gray = ImageEnhance.Contrast(
    gray
).enhance(1.8)

gray = ImageEnhance.Sharpness(
    gray
).enhance(1.4)

# Very subtle smoothing prevents noisy ASCII
gray = gray.filter(
    ImageFilter.GaussianBlur(radius=0.15)
)


# =================================================
# CALCULATE ASCII SIZE
# =================================================

aspect_ratio = (
    image.height
    / image.width
)

HEIGHT = max(
    1,
    int(
        WIDTH
        * aspect_ratio
        * 0.48
    )
)


# =================================================
# RESIZE
# =================================================

gray = gray.resize(
    (WIDTH, HEIGHT),
    Image.Resampling.LANCZOS
)

alpha = alpha.resize(
    (WIDTH, HEIGHT),
    Image.Resampling.LANCZOS
)


# =================================================
# NUMPY ARRAYS
# =================================================

gray_pixels = np.array(gray)

alpha_pixels = np.array(alpha)


# =================================================
# PIXEL → ASCII
# =================================================

def pixel_to_char(brightness, transparency):

    # Remove transparent background
    if transparency < 70:
        return " "

    # Convert brightness to darkness
    darkness = 1 - (
        brightness / 255
    )

    # Better midtone detail
    darkness = darkness ** 0.72

    index = int(
        darkness
        * (len(RAMP) - 1)
    )

    index = max(
        0,
        min(
            index,
            len(RAMP) - 1
        )
    )

    return RAMP[index]


# =================================================
# CREATE ASCII ROWS
# =================================================

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


# =================================================
# SVG DIMENSIONS
# =================================================

PADDING = 26

svg_width = int(
    WIDTH * CHAR_WIDTH
    + PADDING * 2
)

svg_height = int(
    HEIGHT * LINE_HEIGHT
    + PADDING * 2
    + 36
)


# =================================================
# BUILD SVG
# =================================================

parts = []


parts.append(
    f'''<svg
xmlns="http://www.w3.org/2000/svg"
width="{svg_width}"
height="{svg_height}"
viewBox="0 0 {svg_width} {svg_height}"
role="img"
aria-label="Animated tactical ASCII portrait"
>

<defs>

    <filter
        id="blueGlow"
        x="-50%"
        y="-50%"
        width="200%"
        height="200%"
    >
        <feGaussianBlur
            stdDeviation="2.5"
            result="blur"
        />

        <feMerge>
            <feMergeNode in="blur"/>
            <feMergeNode in="SourceGraphic"/>
        </feMerge>
    </filter>


    <linearGradient
        id="scanGradient"
        x1="0%"
        y1="0%"
        x2="100%"
        y2="0%"
    >
        <stop
            offset="0%"
            stop-color="{ACCENT}"
            stop-opacity="0"
        />

        <stop
            offset="50%"
            stop-color="{ACCENT}"
            stop-opacity="0.28"
        />

        <stop
            offset="100%"
            stop-color="{ACCENT}"
            stop-opacity="0"
        />

    </linearGradient>


    <pattern
        id="scanlines"
        width="6"
        height="6"
        patternUnits="userSpaceOnUse"
    >
        <rect
            width="6"
            height="3"
            fill="#ffffff"
            opacity="0.015"
        />
    </pattern>

</defs>


<style>

.ascii {{
    font-family: "Courier New", monospace;
    font-size: {FONT_SIZE}px;
    font-weight: 400;
    fill: {TEXT_COLOR};
    letter-spacing: 0;
}}

.row {{
    opacity: 0;
    animation:
        reveal 0.25s ease-out forwards;
}}

@keyframes reveal {{

    from {{
        opacity: 0;
        transform: translateX(-8px);
    }}

    to {{
        opacity: 1;
        transform: translateX(0);
    }}

}}

.scan {{
    animation:
        scanMove 5s linear infinite;
}}

@keyframes scanMove {{

    0% {{
        transform: translateX(-180px);
    }}

    100% {{
        transform: translateX(900px);
    }}

}}

.pulse {{
    animation:
        pulse 1.8s ease-in-out infinite;
}}

@keyframes pulse {{

    0%, 100% {{
        opacity: 0.4;
    }}

    50% {{
        opacity: 1;
    }}

}}

</style>


<!-- MAIN BACKGROUND -->

<rect
    x="1"
    y="1"
    width="{svg_width - 2}"
    height="{svg_height - 2}"
    rx="16"
    fill="{BACKGROUND}"
    stroke="#30363d"
    stroke-width="1"
/>


<!-- INNER PANEL -->

<rect
    x="8"
    y="8"
    width="{svg_width - 16}"
    height="{svg_height - 16}"
    rx="12"
    fill="{PANEL}"
    stroke="{ACCENT_DARK}"
    stroke-opacity="0.22"
    stroke-width="1"
/>


<!-- SUBTLE SCANLINES -->

<rect
    x="8"
    y="8"
    width="{svg_width - 16}"
    height="{svg_height - 16}"
    rx="12"
    fill="url(#scanlines)"
/>


<!-- HUD CORNERS -->

<path
    d="M 14 34 L 14 14 L 34 14"
    fill="none"
    stroke="{ACCENT}"
    stroke-width="2"
    filter="url(#blueGlow)"
/>

<path
    d="M {svg_width - 34} 14 L {svg_width - 14} 14 L {svg_width - 14} 34"
    fill="none"
    stroke="{ACCENT}"
    stroke-width="2"
    filter="url(#blueGlow)"
/>

<path
    d="M 14 {svg_height - 34} L 14 {svg_height - 14} L 34 {svg_height - 14}"
    fill="none"
    stroke="{ACCENT}"
    stroke-width="2"
    filter="url(#blueGlow)"
/>

<path
    d="M {svg_width - 34} {svg_height - 14} L {svg_width - 14} {svg_height - 14} L {svg_width - 14} {svg_height - 34}"
    fill="none"
    stroke="{ACCENT}"
    stroke-width="2"
    filter="url(#blueGlow)"
/>


<!-- HEADER -->

<text
    x="{PADDING}"
    y="27"
    font-family="Courier New, monospace"
    font-size="10"
    letter-spacing="2"
    fill="{MUTED}"
>
    IDENTITY // PORTRAIT
</text>


<!-- STATUS -->

<circle
    cx="{svg_width - PADDING - 4}"
    cy="23"
    r="4"
    fill="#39d353"
    class="pulse"
/>

<text
    x="{svg_width - PADDING - 14}"
    y="27"
    text-anchor="end"
    font-family="Courier New, monospace"
    font-size="9"
    fill="#39d353"
>
    ONLINE
</text>


<!-- HEADER LINE -->

<line
    x1="{PADDING}"
    y1="40"
    x2="{svg_width - PADDING}"
    y2="40"
    stroke="#30363d"
    stroke-width="1"
/>

'''
)


# =================================================
# ADD ASCII ROWS
# =================================================

portrait_start_y = 62

for i, line in enumerate(rows):

    y = (
        portrait_start_y
        + i * LINE_HEIGHT
    )

    delay = (
        i * 0.018
    )

    safe_line = escape(line)

    parts.append(
        f'''
<text
    x="{PADDING}"
    y="{y}"
    class="ascii row"
    xml:space="preserve"
    style="animation-delay:{delay:.3f}s"
>{safe_line}</text>
'''
    )


# =================================================
# MOVING SCAN
# =================================================

parts.append(
    f'''
<rect
    x="-160"
    y="45"
    width="160"
    height="{svg_height - 80}"
    fill="url(#scanGradient)"
    opacity="0.5"
    class="scan"
/>
'''
)


# =================================================
# FOOTER
# =================================================

parts.append(
    f'''
<text
    x="{PADDING}"
    y="{svg_height - 24}"
    font-family="Courier New, monospace"
    font-size="9"
    letter-spacing="1"
    fill="{MUTED}"
>
    SUBJECT: REIIDON
</text>


<text
    x="{svg_width - PADDING}"
    y="{svg_height - 24}"
    text-anchor="end"
    font-family="Courier New, monospace"
    font-size="9"
    fill="{ACCENT}"
>
    SCAN COMPLETE
</text>
'''
)


# =================================================
# CLOSE SVG
# =================================================

parts.append(
    "</svg>"
)


# =================================================
# SAVE
# =================================================

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