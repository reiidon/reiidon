from pathlib import Path
from datetime import datetime, timedelta, timezone
import json
import os
import urllib.request


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
# Get GitHub Token
# -------------------------------------------------

TOKEN = os.getenv("GITHUB_TOKEN")

if not TOKEN:
    raise RuntimeError(
        "\nGITHUB_TOKEN was not found.\n\n"
        "Windows PowerShell:\n"
        '$env:GITHUB_TOKEN = "your_github_token"\n\n'
        "Then run:\n"
        "python scripts/contrib-heatmap.py\n"
    )


# -------------------------------------------------
# GitHub GraphQL Query
# -------------------------------------------------

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


# -------------------------------------------------
# Request Real GitHub Contribution Data
# -------------------------------------------------

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
        result = json.loads(response.read().decode("utf-8"))

except Exception as error:
    raise RuntimeError(
        f"\nCould not fetch GitHub contribution data.\n{error}"
    )


# -------------------------------------------------
# Check For GitHub API Errors
# -------------------------------------------------

if "errors" in result:
    raise RuntimeError(
        "\nGitHub GraphQL Error:\n"
        + json.dumps(result["errors"], indent=2)
    )


user = result.get("data", {}).get("user")

if not user:
    raise RuntimeError(
        f"\nGitHub user '{USERNAME}' was not found."
    )


calendar = (
    user["contributionsCollection"]
    ["contributionCalendar"]
)

total_contributions = calendar["totalContributions"]
weeks_data = calendar["weeks"]


# -------------------------------------------------
# Contribution Level Mapping
# -------------------------------------------------

LEVEL_MAP = {
    "NONE": 0,
    "FIRST_QUARTILE": 1,
    "SECOND_QUARTILE": 2,
    "THIRD_QUARTILE": 3,
    "FOURTH_QUARTILE": 4
}


# -------------------------------------------------
# Convert GitHub Data
# -------------------------------------------------

contributions = []

for week_data in weeks_data:

    column = []

    for day_data in week_data["contributionDays"]:

        level = LEVEL_MAP.get(
            day_data["contributionLevel"],
            0
        )

        column.append(level)

    # Make sure every week has 7 days
    while len(column) < DAYS:
        column.append(0)

    contributions.append(column)


# Keep exactly the latest 53 weeks

if len(contributions) > WEEKS:
    contributions = contributions[-WEEKS:]


while len(contributions) < WEEKS:
    contributions.insert(
        0,
        [0] * DAYS
    )


# -------------------------------------------------
# SVG Dimensions
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
# SVG Start
# -------------------------------------------------

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


# -------------------------------------------------
# Styles
# -------------------------------------------------

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

.total {{
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
    @{USERNAME}
</text>
'''
)


# -------------------------------------------------
# Contribution Squares
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

        x = (
            PADDING_LEFT
            + week * (CELL_SIZE + CELL_GAP)
        )

        y = (
            PADDING_TOP
            + day * (CELL_SIZE + CELL_GAP)
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
# Contribution Count
# -------------------------------------------------

svg.append(
    f'''
<text
    x="{svg_width - PADDING_RIGHT}"
    y="{footer_y}"
    text-anchor="end"
    class="total"
>
    {total_contributions} contributions
</text>
'''
)


# -------------------------------------------------
# Close SVG
# -------------------------------------------------

svg.append("</svg>")


# -------------------------------------------------
# Save SVG
# -------------------------------------------------

OUTPUT_PATH.write_text(
    "".join(svg),
    encoding="utf-8"
)


# -------------------------------------------------
# Done
# -------------------------------------------------

print()
print("Done!")
print(f"User: {USERNAME}")
print(f"Real contributions: {total_contributions}")
print(f"Created: {OUTPUT_PATH}")
print(f"Size: {svg_width} x {svg_height}")