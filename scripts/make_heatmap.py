from pathlib import Path
import random
from datetime import datetime, timedelta


# -------------------------------------------------
# Paths
# -------------------------------------------------

ROOT = Path(__file__).resolve().parent.parent
OUTPUT_PATH = ROOT / "contrib-heatmap.svg"


# -------------------------------------------------
# Settings
# -------------------------------------------------

USERNAME = "reiidon"

WEEKS = 53
DAYS = 7

CELL_SIZE = 9
CELL_GAP = 5

PADDING_LEFT = 28
PADDING_RIGHT = 28
PADDING_TOP = 50
PADDING_BOTTOM = 34

TITLE = "contribution activity"
SUBTITLE = f"@{USERNAME}"

BACKGROUND = "#0d1117"
EMPTY_COLOR = "#161b22"

GREEN_1 = "#0e4429"
GREEN_2 = "#006d32"
GREEN_3 = "#26a641"
GREEN_4 = "#39d353"

BORDER = "#30363d"
TEXT = "#c9d1d9"
MUTED = "#8b949e"


# -------------------------------------------------
# Generate contribution pattern
# -------------------------------------------------

random.seed(42)

contributions = []

for week in range(WEEKS):
    column = []

    # More natural activity pattern
    active_week = random.random() < 0.42

    for day in range(DAYS):

        if active_week and random.random() < 0.18:

            level = random.choices(
                [1, 2, 3, 4],
                weights=[45, 30, 18, 7]
            )[0]

        else:
            level = 0

        column.append(level)

    contributions.append(column)


# -------------------------------------------------
# Add some natural clusters
# -------------------------------------------------

for start_week in [6, 20, 34, 45, 49]:

    for week_offset in range(random.randint(1, 3)):

        week = start_week + week_offset

        if week >= WEEKS:
            continue

        for _ in range(random.randint(1, 3)):

            day = random.randint(0, DAYS - 1)

            contributions[week][day] = random.choice([2, 3, 4])


# -------------------------------------------------
# SVG dimensions
# -------------------------------------------------

grid_width = (
    WEEKS * CELL_SIZE
    + (WEEKS - 1) * CELL_GAP
)

grid_height = (
    DAYS * CELL_SIZE
    + (DAYS - 1) * CELL_GAP
)

svg_width = (
    PADDING_LEFT
    + grid_width
    + PADDING_RIGHT
)

svg_height = (
    PADDING_TOP
    + grid_height
    + PADDING_BOTTOM
)


# -------------------------------------------------
# SVG
# -------------------------------------------------

svg = []

svg.append(
    f'''<svg
xmlns="http://www.w3.org/2000/svg"
width="100%"
viewBox="0 0 {svg_width} {svg_height}"
role="img"
aria-label="GitHub contribution activity"
>
'''
)

svg.append(
    f'''
<style>

.title {{
    font-family: "Courier New", monospace;
    font-size: 16px;
    font-weight: 700;
    fill: {TEXT};
}}

.username {{
    font-family: "Courier New", monospace;
    font-size: 12px;
    fill: {MUTED};
}}

.footer {{
    font-family: "Courier New", monospace;
    font-size: 11px;
    fill: {MUTED};
}}

</style>
'''
)


# -------------------------------------------------
# Background
# -------------------------------------------------

svg.append(
    f'''
<rect
    x="1"
    y="1"
    width="{svg_width - 2}"
    height="{svg_height - 2}"
    rx="16"
    fill="{BACKGROUND}"
    stroke="{BORDER}"
    stroke-width="1"
/>
'''
)


# -------------------------------------------------
# Header
# -------------------------------------------------

svg.append(
    f'''
<text
    x="{PADDING_LEFT}"
    y="28"
    class="title"
>
    {TITLE}
</text>
'''
)

svg.append(
    f'''
<text
    x="{PADDING_LEFT + 215}"
    y="28"
    class="username"
>
    {SUBTITLE}
</text>
'''
)


# -------------------------------------------------
# Contribution squares
# -------------------------------------------------

colors = [
    EMPTY_COLOR,
    GREEN_1,
    GREEN_2,
    GREEN_3,
    GREEN_4
]

for week in range(WEEKS):

    for day in range(DAYS):

        level = contributions[week][day]

        x = PADDING_LEFT + week * (
            CELL_SIZE + CELL_GAP
        )

        y = PADDING_TOP + day * (
            CELL_SIZE + CELL_GAP
        )

        color = colors[level]

        svg.append(
            f'''
<rect
    x="{x}"
    y="{y}"
    width="{CELL_SIZE}"
    height="{CELL_SIZE}"
    rx="2"
    fill="{color}"
/>
'''
        )


# -------------------------------------------------
# Footer
# -------------------------------------------------

footer_y = svg_height - 14

svg.append(
    f'''
<text
    x="{PADDING_LEFT}"
    y="{footer_y}"
    class="footer"
>
    last 53 weeks • GitHub contribution activity
</text>
'''
)


# -------------------------------------------------
# Close SVG
# -------------------------------------------------

svg.append("</svg>")


# -------------------------------------------------
# Save
# -------------------------------------------------

OUTPUT_PATH.write_text(
    "".join(svg),
    encoding="utf-8"
)

print()
print("Done!")
print(f"Created: {OUTPUT_PATH}")
print(f"Size: {svg_width} x {svg_height}")