from pathlib import Path
from datetime import datetime, timedelta, timezone
import json
import os
import urllib.request


# =================================================
# PATHS
# =================================================

ROOT = Path(__file__).resolve().parent.parent
OUTPUT_PATH = ROOT / "contrib-heatmap.svg"


# =================================================
# SETTINGS
# =================================================

USERNAME = "reiidon"

WEEKS = 53
DAYS = 7

CELL_SIZE = 9
CELL_GAP = 5

PADDING_LEFT = 32
PADDING_RIGHT = 32
PADDING_TOP = 76
PADDING_BOTTOM = 46

TITLE = "CONTRIBUTION ACTIVITY"
SUBTITLE = "GITHUB ACTIVITY MONITOR"


# =================================================
# COLORS
# =================================================

BACKGROUND = "#07090d"
PANEL = "#0d1117"
PANEL_2 = "#10151d"

EMPTY_COLOR = "#161b22"

GREEN_1 = "#0e4429"
GREEN_2 = "#006d32"
GREEN_3 = "#26a641"
GREEN_4 = "#39d353"

BORDER = "#30363d"

TEXT = "#e6edf3"
MUTED = "#8b949e"

ACCENT = "#58a6ff"
ACCENT_DARK = "#1f6feb"

STATUS = "#39d353"


# =================================================
# GET GITHUB TOKEN
# =================================================

TOKEN = os.getenv("GITHUB_TOKEN")

if not TOKEN:
    raise RuntimeError(
        "\nGITHUB_TOKEN was not found.\n\n"
        "Windows PowerShell:\n"
        '$env:GITHUB_TOKEN = "your_github_token"\n\n'
        "Then run:\n"
        "python scripts/make_heatmap.py\n"
    )


# =================================================
# GITHUB GRAPHQL QUERY
# =================================================

today = datetime.now(timezone.utc)
start_date = today - timedelta(weeks=WEEKS)

query = """
query($login: String!, $from: DateTime!, $to: DateTime!) {
  user(login: $login) {
    contributionsCollection(from: $from, to: $to) {
      contributionCalendar {
        totalContributions

        weeks {
          contributionDays {
            date
            contributionCount
            contributionLevel
          }
        }
      }
    }
  }
}
"""


payload = {
    "query": query,
    "variables": {
        "login": USERNAME,
        "from": start_date.isoformat(),
        "to": today.isoformat()
    }
}


# =================================================
# REQUEST REAL GITHUB CONTRIBUTION DATA
# =================================================

request = urllib.request.Request(
    "https://api.github.com/graphql",
    data=json.dumps(payload).encode("utf-8"),
    headers={
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json",
        "User-Agent": "GitHub-Contribution-Heatmap"
    },
    method="POST"
)


try:
    with urllib.request.urlopen(request) as response:
        result = json.loads(
            response.read().decode("utf-8")
        )

except Exception as error:
    raise RuntimeError(
        f"\nCould not fetch GitHub contribution data.\n{error}"
    )


# =================================================
# CHECK FOR GITHUB API ERRORS
# =================================================

if "errors" in result:
    raise RuntimeError(
        "\nGitHub GraphQL Error:\n"
        + json.dumps(
            result["errors"],
            indent=2
        )
    )


user = result.get(
    "data",
    {}
).get(
    "user"
)


if not user:
    raise RuntimeError(
        f"\nGitHub user '{USERNAME}' was not found."
    )


calendar = (
    user["contributionsCollection"]
    ["contributionCalendar"]
)


total_contributions = (
    calendar["totalContributions"]
)


weeks_data = calendar["weeks"]


# =================================================
# CONTRIBUTION LEVEL MAPPING
# =================================================

LEVEL_MAP = {
    "NONE": 0,
    "FIRST_QUARTILE": 1,
    "SECOND_QUARTILE": 2,
    "THIRD_QUARTILE": 3,
    "FOURTH_QUARTILE": 4
}


# =================================================
# CONVERT GITHUB DATA
# =================================================

contributions = []

for week_data in weeks_data:

    column = []

    for day_data in week_data[
        "contributionDays"
    ]:

        level = LEVEL_MAP.get(
            day_data["contributionLevel"],
            0
        )

        column.append(level)

    while len(column) < DAYS:
        column.append(0)

    contributions.append(column)


# Keep exactly 53 weeks

if len(contributions) > WEEKS:

    contributions = contributions[-WEEKS:]


while len(contributions) < WEEKS:

    contributions.insert(
        0,
        [0] * DAYS
    )


# =================================================
# SVG DIMENSIONS
# =================================================

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


# =================================================
# SVG START
# =================================================

svg = []


svg.append(
    f'''<svg
xmlns="http://www.w3.org/2000/svg"
width="100%"
viewBox="0 0 {svg_width} {svg_height}"
role="img"
aria-label="{total_contributions} GitHub contributions in the last year"
>
'''
)


# =================================================
# DEFINITIONS
# =================================================

svg.append(
    f'''
<defs>

    <!-- Blue tactical glow -->

    <filter
        id="blueGlow"
        x="-50%"
        y="-50%"
        width="200%"
        height="200%"
    >
        <feGaussianBlur
            stdDeviation="3"
            result="blur"
        />

        <feMerge>
            <feMergeNode in="blur"/>
            <feMergeNode in="SourceGraphic"/>
        </feMerge>
    </filter>


    <!-- Green contribution glow -->

    <filter
        id="greenGlow"
        x="-50%"
        y="-50%"
        width="200%"
        height="200%"
    >
        <feGaussianBlur
            stdDeviation="2"
            result="blur"
        />

        <feMerge>
            <feMergeNode in="blur"/>
            <feMergeNode in="SourceGraphic"/>
        </feMerge>
    </filter>


    <!-- Scanline pattern -->

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
            opacity="0.012"
        />
    </pattern>


    <!-- Moving scan gradient -->

    <linearGradient
        id="scanner"
        x1="0%"
        y1="0%"
        x2="100%"
        y2="0%"
    >

        <stop
            offset="0%"
            stop-color="#58a6ff"
            stop-opacity="0"
        />

        <stop
            offset="50%"
            stop-color="#58a6ff"
            stop-opacity="0.35"
        />

        <stop
            offset="100%"
            stop-color="#58a6ff"
            stop-opacity="0"
        />

    </linearGradient>

</defs>
'''
)


# =================================================
# STYLES
# =================================================

svg.append(
    f'''
<style>

.title {{
    font-family: "Courier New", monospace;
    font-size: 16px;
    font-weight: 700;
    letter-spacing: 1.5px;
    fill: {TEXT};
}}

.subtitle {{
    font-family: "Courier New", monospace;
    font-size: 9px;
    letter-spacing: 1px;
    fill: {MUTED};
}}

.username {{
    font-family: "Courier New", monospace;
    font-size: 11px;
    fill: {ACCENT};
}}

.footer {{
    font-family: "Courier New", monospace;
    font-size: 10px;
    fill: {MUTED};
}}

.total {{
    font-family: "Courier New", monospace;
    font-size: 11px;
    fill: {TEXT};
}}

.status {{
    font-family: "Courier New", monospace;
    font-size: 9px;
    fill: {STATUS};
    letter-spacing: 1px;
}}

.scan {{
    animation: scan 5s linear infinite;
}}

@keyframes scan {{
    0% {{
        transform: translateX(-200px);
    }}

    100% {{
        transform: translateX(1000px);
    }}
}}

.pulse {{
    animation: pulse 2s ease-in-out infinite;
}}

@keyframes pulse {{
    0%, 100% {{
        opacity: 0.35;
    }}

    50% {{
        opacity: 1;
    }}
}}

</style>
'''
)


# =================================================
# BACKGROUND
# =================================================

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

<!-- Inner panel -->

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

<!-- Scanline texture -->

<rect
    x="8"
    y="8"
    width="{svg_width - 16}"
    height="{svg_height - 16}"
    rx="12"
    fill="url(#scanlines)"
/>
'''
)


# =================================================
# HUD CORNER DETAILS
# =================================================

svg.append(
    f'''
<!-- Top left corner -->

<path
    d="M 14 32 L 14 14 L 32 14"
    fill="none"
    stroke="{ACCENT}"
    stroke-width="2"
    filter="url(#blueGlow)"
/>

<!-- Top right corner -->

<path
    d="M {svg_width - 32} 14 L {svg_width - 14} 14 L {svg_width - 14} 32"
    fill="none"
    stroke="{ACCENT}"
    stroke-width="2"
    filter="url(#blueGlow)"
/>

<!-- Bottom left corner -->

<path
    d="M 14 {svg_height - 32} L 14 {svg_height - 14} L 32 {svg_height - 14}"
    fill="none"
    stroke="{ACCENT}"
    stroke-width="2"
    filter="url(#blueGlow)"
/>

<!-- Bottom right corner -->

<path
    d="M {svg_width - 32} {svg_height - 14} L {svg_width - 14} {svg_height - 14} L {svg_width - 14} {svg_height - 32}"
    fill="none"
    stroke="{ACCENT}"
    stroke-width="2"
    filter="url(#blueGlow)"
/>
'''
)


# =================================================
# HEADER
# =================================================

svg.append(
    f'''
<text
    x="{PADDING_LEFT}"
    y="34"
    class="title"
>
    {TITLE}
</text>

<text
    x="{PADDING_LEFT}"
    y="48"
    class="subtitle"
>
    {SUBTITLE}
</text>


<!-- Username -->

<text
    x="{svg_width - PADDING_RIGHT}"
    y="34"
    text-anchor="end"
    class="username"
>
    @{USERNAME}
</text>


<!-- Live status -->

<circle
    cx="{svg_width - PADDING_RIGHT - 5}"
    cy="47"
    r="4"
    fill="{STATUS}"
    filter="url(#greenGlow)"
    class="pulse"
/>

<text
    x="{svg_width - PADDING_RIGHT - 14}"
    y="50"
    text-anchor="end"
    class="status"
>
    LIVE DATA
</text>


<!-- Divider -->

<line
    x1="{PADDING_LEFT}"
    y1="60"
    x2="{svg_width - PADDING_RIGHT}"
    y2="60"
    stroke="{BORDER}"
    stroke-width="1"
/>
'''
)


# =================================================
# CONTRIBUTION SQUARES
# =================================================

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

        x = (
            PADDING_LEFT
            + week * (
                CELL_SIZE + CELL_GAP
            )
        )

        y = (
            PADDING_TOP
            + day * (
                CELL_SIZE + CELL_GAP
            )
        )

        color = colors[level]

        glow = ""

        if level >= 3:

            glow = (
                'filter="url(#greenGlow)"'
            )

        svg.append(
            f'''
<rect
    x="{x}"
    y="{y}"
    width="{CELL_SIZE}"
    height="{CELL_SIZE}"
    rx="2"
    fill="{color}"
    {glow}
>
'''
        )

        # Animate active contribution cells

        if level > 0:

            delay = (
                (week * 0.025)
                + (day * 0.015)
            )

            svg.append(
                f'''
    <animate
        attributeName="opacity"
        values="0.25;1"
        dur="0.45s"
        begin="{delay:.3f}s"
        fill="freeze"
    />
'''
            )

        svg.append(
            '''
</rect>
'''
        )


# =================================================
# MOVING SCAN EFFECT
# =================================================

scan_width = 120


svg.append(
    f'''
<rect
    x="-{scan_width}"
    y="{PADDING_TOP - 4}"
    width="{scan_width}"
    height="{grid_height + 8}"
    fill="url(#scanner)"
    opacity="0.45"
    class="scan"
/>
'''
)


# =================================================
# FOOTER
# =================================================

footer_y = (
    svg_height - 20
)


svg.append(
    f'''
<text
    x="{PADDING_LEFT}"
    y="{footer_y}"
    class="footer"
>
    SYSTEM WINDOW: LAST 53 WEEKS
</text>
'''
)


svg.append(
    f'''
<text
    x="{svg_width - PADDING_RIGHT}"
    y="{footer_y}"
    text-anchor="end"
    class="total"
>
    {total_contributions} CONTRIBUTIONS
</text>
'''
)


# =================================================
# CLOSE SVG
# =================================================

svg.append(
    "</svg>"
)


# =================================================
# SAVE SVG
# =================================================

OUTPUT_PATH.write_text(
    "".join(svg),
    encoding="utf-8"
)


# =================================================
# DONE
# =================================================

print()
print("Done!")
print(f"User: {USERNAME}")
print(f"Real contributions: {total_contributions}")
print(f"Created: {OUTPUT_PATH}")
print(f"Size: {svg_width} x {svg_height}")