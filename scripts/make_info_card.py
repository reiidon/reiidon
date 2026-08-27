from pathlib import Path
from html import escape

ROOT = Path(__file__).resolve().parent.parent
OUTPUT = ROOT / "info-card.svg"


# =================================================
# PROFILE DETAILS
# =================================================

USERNAME = "reiidon"

INFO = [
    ("NOW", "Building AI-powered applications"),
    ("PREV", "Computer Science student"),
    ("STACK", "Python • FastAPI • React • AI"),
    ("FOCUS", "LLMs • Computer Vision • RAG"),
]


# =================================================
# SVG SIZE
# =================================================

WIDTH = 800
HEIGHT = 720


# =================================================
# SVG START
# =================================================

svg = f"""<svg
    xmlns="http://www.w3.org/2000/svg"
    width="{WIDTH}"
    height="{HEIGHT}"
    viewBox="0 0 {WIDTH} {HEIGHT}"
    role="img"
    aria-label="Developer information card"
>

<style>

.title {{
    font-family: monospace;
    font-size: 24px;
    font-weight: bold;
    fill: #58a6ff;
}}

.subtitle {{
    font-family: monospace;
    font-size: 14px;
    fill: #8b949e;
}}

.label {{
    font-family: monospace;
    font-size: 17px;
    font-weight: bold;
    fill: #58a6ff;
}}

.value {{
    font-family: monospace;
    font-size: 17px;
    fill: #c9d1d9;
}}

.section {{
    font-family: monospace;
    font-size: 13px;
    letter-spacing: 2px;
    fill: #8b949e;
}}

.footer {{
    font-family: monospace;
    font-size: 15px;
    fill: #8b949e;
}}

.green {{
    font-family: monospace;
    font-size: 15px;
    fill: #3fb950;
}}

</style>


<!-- ================================================= -->
<!-- BACKGROUND -->
<!-- ================================================= -->

<rect
    x="10"
    y="10"
    width="{WIDTH - 20}"
    height="{HEIGHT - 20}"
    rx="22"
    fill="#0d1117"
    stroke="#30363d"
    stroke-width="2"
/>


<!-- ================================================= -->
<!-- TERMINAL HEADER -->
<!-- ================================================= -->

<rect
    x="10"
    y="10"
    width="{WIDTH - 20}"
    height="72"
    rx="22"
    fill="#161b22"
/>

<rect
    x="10"
    y="50"
    width="{WIDTH - 20}"
    height="32"
    fill="#161b22"
/>


<!-- WINDOW BUTTONS -->

<circle cx="42" cy="45" r="9" fill="#ff5f56"/>
<circle cx="70" cy="45" r="9" fill="#ffbd2e"/>
<circle cx="98" cy="45" r="9" fill="#27c93f"/>


<!-- TERMINAL TITLE -->

<text
    x="135"
    y="52"
    class="title"
>
    {escape(USERNAME)}@github
</text>


<!-- ================================================= -->
<!-- LEFT SIDE VISUAL -->
<!-- ================================================= -->

<text
    x="75"
    y="175"
    font-family="monospace"
    font-size="24"
    fill="#58a6ff"
>
    <tspan x="75" dy="0">   ███████   </tspan>
    <tspan x="75" dy="28"> ██       ██ </tspan>
    <tspan x="75" dy="28">██   ◉ ◉   ██</tspan>
    <tspan x="75" dy="28">██    ▬    ██</tspan>
    <tspan x="75" dy="28"> ██  ───  ██ </tspan>
    <tspan x="75" dy="28">   ███████   </tspan>
</text>


<!-- LEFT SIDE DIVIDER -->

<line
    x1="285"
    y1="130"
    x2="285"
    y2="590"
    stroke="#21262d"
    stroke-width="2"
/>


<!-- ================================================= -->
<!-- LEFT SIDE DETAILS -->
<!-- ================================================= -->

<text
    x="75"
    y="390"
    class="section"
>
    PROFILE
</text>

<text
    x="75"
    y="435"
    class="value"
>
    AI Developer
</text>

<text
    x="75"
    y="470"
    class="value"
>
    Python Developer
</text>

<text
    x="75"
    y="505"
    class="value"
>
    Builder
</text>


<!-- STATUS -->

<circle
    cx="84"
    cy="565"
    r="7"
    fill="#3fb950"
>
    <animate
        attributeName="opacity"
        values="1;0.35;1"
        dur="2s"
        repeatCount="indefinite"
    />
</circle>

<text
    x="105"
    y="570"
    class="subtitle"
>
    online • building
</text>


<!-- ================================================= -->
<!-- RIGHT SIDE HEADER -->
<!-- ================================================= -->

<text
    x="330"
    y="135"
    class="section"
>
    DEVELOPER STATUS
</text>


<!-- ================================================= -->
<!-- INFO ROWS -->
<!-- ================================================= -->
"""

start_y = 200
row_gap = 82

for index, (label, value) in enumerate(INFO):

    y = start_y + index * row_gap
    delay = index * 0.45

    svg += f"""

<g opacity="0">

    <animate
        attributeName="opacity"
        values="0;0;1"
        keyTimes="0;0.4;1"
        dur="0.9s"
        begin="{delay}s"
        fill="freeze"
    />

    <animateTransform
        attributeName="transform"
        type="translate"
        values="25 0;25 0;0 0"
        keyTimes="0;0.4;1"
        dur="0.9s"
        begin="{delay}s"
        fill="freeze"
    />

    <text
        x="330"
        y="{y}"
        class="label"
    >
        {escape(label)}
    </text>

    <text
        x="330"
        y="{y + 34}"
        class="value"
    >
        {escape(value)}
    </text>

    <line
        x1="330"
        y1="{y + 55}"
        x2="710"
        y2="{y + 55}"
        stroke="#21262d"
        stroke-width="1"
    />

</g>
"""


# =================================================
# FOOTER
# =================================================

cursor_delay = len(INFO) * 0.45

svg += f"""

<!-- ================================================= -->
<!-- TERMINAL FOOTER -->
<!-- ================================================= -->

<rect
    x="45"
    y="625"
    width="710"
    height="55"
    rx="12"
    fill="#161b22"
    stroke="#21262d"
    stroke-width="1"
/>

<text
    x="75"
    y="660"
    class="footer"
>
    $ whoami
</text>

<text
    x="210"
    y="660"
    class="green"
>
    developer
</text>

<rect
    x="330"
    y="642"
    width="11"
    height="22"
    rx="2"
    fill="#58a6ff"
>
    <animate
        attributeName="opacity"
        values="1;1;0;0;1"
        keyTimes="0;0.45;0.5;0.95;1"
        dur="1.2s"
        repeatCount="indefinite"
    />
</rect>

</svg>
"""


# =================================================
# SAVE FILE
# =================================================

OUTPUT.write_text(svg, encoding="utf-8")

print("Done!")
print(f"Created: {OUTPUT}")