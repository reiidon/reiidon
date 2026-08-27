from pathlib import Path
import requests
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parent.parent
OUTPUT = ROOT / "contrib-heatmap.svg"

USERNAME = "reiidon"

print("Fetching GitHub contribution data...")

url = f"https://github.com/users/{USERNAME}/contributions"

headers = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "text/html"
}

response = requests.get(url, headers=headers, timeout=30)
response.raise_for_status()

soup = BeautifulSoup(response.text, "html.parser")

# GitHub contribution cells
days = soup.select("td[data-date]")

if not days:
    # Backup selector for different GitHub markup
    days = soup.select("[data-date]")

if not days:
    print()
    print("Could not read the contribution graph.")
    print("GitHub may have changed its HTML format.")
    print(f"URL checked: {url}")
    raise SystemExit(1)

print(f"Found {len(days)} contribution days.")

COLORS = {
    0: "#161b22",
    1: "#0e4429",
    2: "#006d32",
    3: "#26a641",
    4: "#39d353",
}

# SVG settings
CELL_SIZE = 12
GAP = 4
STEP = CELL_SIZE + GAP

ROWS = 7
COLS = 53

LEFT = 30
TOP = 55

WIDTH = LEFT * 2 + COLS * STEP
HEIGHT = TOP + ROWS * STEP + 45


def get_level(day):
    """Extract GitHub contribution level safely."""

    level = day.get("data-level")

    if level is not None:
        try:
            return max(0, min(4, int(level)))
        except ValueError:
            pass

    # Some GitHub versions use classes like ContributionCalendar-day--level-3
    for class_name in day.get("class", []):
        if "level-" in class_name:
            try:
                return max(0, min(4, int(class_name.split("level-")[-1])))
            except ValueError:
                pass

    return 0


svg = f"""<svg
    xmlns="http://www.w3.org/2000/svg"
    width="{WIDTH}"
    height="{HEIGHT}"
    viewBox="0 0 {WIDTH} {HEIGHT}"
    role="img"
    aria-label="GitHub contribution heatmap for {USERNAME}"
>
    <style>
        .title {{
            font-family: monospace;
            font-size: 18px;
            font-weight: bold;
            fill: #c9d1d9;
        }}

        .subtitle {{
            font-family: monospace;
            font-size: 13px;
            fill: #8b949e;
        }}
    </style>

    <rect
        width="100%"
        height="100%"
        rx="16"
        fill="#0d1117"
        stroke="#30363d"
        stroke-width="2"
    />

    <text x="{LEFT}" y="30" class="title">
        contribution activity
    </text>

    <text x="{LEFT + 245}" y="30" class="subtitle">
        @{USERNAME}
    </text>
"""


# Keep approximately 53 weeks
days = days[-371:]

for index, day in enumerate(days):

    level = get_level(day)
    color = COLORS[level]

    date = day.get("data-date", "")

    column = index // ROWS
    row = index % ROWS

    x = LEFT + column * STEP
    y = TOP + row * STEP

    # Diagonal animation
    delay = (column * 0.035) + (row * 0.06)

    svg += f"""
    <g opacity="0">
        <animate
            attributeName="opacity"
            values="0;0;1"
            keyTimes="0;0.45;1"
            dur="0.5s"
            begin="{delay:.3f}s"
            fill="freeze"
        />

        <animateTransform
            attributeName="transform"
            type="translate"
            values="-10 -10;-10 -10;0 0"
            keyTimes="0;0.45;1"
            dur="0.5s"
            begin="{delay:.3f}s"
            fill="freeze"
        />

        <rect
            x="{x}"
            y="{y}"
            width="{CELL_SIZE}"
            height="{CELL_SIZE}"
            rx="3"
            fill="{color}"
        >
            <title>{date} — contribution level {level}</title>
        </rect>
    </g>
"""

last_delay = ((COLS - 1) * 0.035) + ((ROWS - 1) * 0.06) + 0.5

svg += f"""
    <text
        x="{LEFT}"
        y="{HEIGHT - 18}"
        class="subtitle"
        opacity="0"
    >
        last 53 weeks • GitHub contribution activity

        <animate
            attributeName="opacity"
            from="0"
            to="1"
            dur="0.6s"
            begin="{last_delay:.2f}s"
            fill="freeze"
        />
    </text>

</svg>
"""

OUTPUT.write_text(svg, encoding="utf-8")

print()
print("Done!")
print(f"Created: {OUTPUT}")
print(f"Contribution days: {len(days)}")