from pathlib import Path
from html import escape

ROOT = Path(__file__).resolve().parent.parent
OUTPUT = ROOT / "info-card.svg"

# -----------------------------
# CHANGE THESE DETAILS ANYTIME
# -----------------------------
USERNAME = "reiidon"

INFO = [
    ("Now", "Building AI-powered applications"),
    ("Prev", "Computer Science student"),
    ("Stack", "Python • FastAPI • React • AI"),
    ("Highlights", "AI • Computer Vision • RAG"),
]

WIDTH = 800
HEIGHT = 330

svg = f"""<svg
    xmlns="http://www.w3.org/2000/svg"
    width="{WIDTH}"
    height="{HEIGHT}"
    viewBox="0 0 {WIDTH} {HEIGHT}"
    role="img"
    aria-label="Neofetch style developer information card"
>
    <style>
        .title {{
            font: bold 22px monospace;
            fill: #58a6ff;
        }}

        .label {{
            font: bold 18px monospace;
            fill: #f0f6fc;
        }}

        .value {{
            font: 18px monospace;
            fill: #c9d1d9;
        }}

        .cursor {{
            fill: #58a6ff;
        }}
    </style>

    <!-- Background -->
    <rect
        x="10"
        y="10"
        width="{WIDTH - 20}"
        height="{HEIGHT - 20}"
        rx="18"
        fill="#0d1117"
        stroke="#30363d"
        stroke-width="2"
    />

    <!-- Top bar -->
    <rect
        x="10"
        y="10"
        width="{WIDTH - 20}"
        height="55"
        rx="18"
        fill="#161b22"
    />

    <!-- Bottom of top bar -->
    <rect
        x="10"
        y="47"
        width="{WIDTH - 20}"
        height="18"
        fill="#161b22"
    />

    <!-- Window buttons -->
    <circle cx="42" cy="37" r="8" fill="#ff5f56"/>
    <circle cx="68" cy="37" r="8" fill="#ffbd2e"/>
    <circle cx="94" cy="37" r="8" fill="#27c93f"/>

    <!-- Title -->
    <text x="125" y="44" class="title">
        {escape(USERNAME)}@github
    </text>

    <!-- Left ASCII decoration -->
    <text
        x="70"
        y="120"
        font-family="monospace"
        font-size="18"
        fill="#58a6ff"
        opacity="0.9"
    >
        <tspan x="70" dy="0">   ███████   </tspan>
        <tspan x="70" dy="22"> ██       ██ </tspan>
        <tspan x="70" dy="22">██   ◉ ◉   ██</tspan>
        <tspan x="70" dy="22">██     &gt;   ██</tspan>
        <tspan x="70" dy="22"> ██  ───  ██ </tspan>
        <tspan x="70" dy="22">   ███████   </tspan>
    </text>
"""

# -----------------------------
# Animated information rows
# -----------------------------
start_y = 110
row_gap = 45

for index, (label, value) in enumerate(INFO):
    y = start_y + index * row_gap

    delay = index * 0.55

    svg += f"""
    <g opacity="0">
        <animate
            attributeName="opacity"
            values="0;0;1"
            keyTimes="0;0.5;1"
            dur="1.1s"
            begin="{delay}s"
            fill="freeze"
        />

        <animateTransform
            attributeName="transform"
            type="translate"
            values="20 0;20 0;0 0"
            keyTimes="0;0.5;1"
            dur="1.1s"
            begin="{delay}s"
            fill="freeze"
        />

        <text x="310" y="{y}" class="label">
            {escape(label)}
        </text>

        <text x="430" y="{y}" class="value">
            {escape(value)}
        </text>
    </g>
"""

# -----------------------------
# Animated cursor
# -----------------------------
cursor_delay = len(INFO) * 0.55

svg += f"""
    <rect
        x="310"
        y="{start_y + len(INFO) * row_gap - 25}"
        width="14"
        height="22"
        rx="2"
        class="cursor"
        opacity="0"
    >
        <animate
            attributeName="opacity"
            values="0;0;1;1;0;0"
            keyTimes="0;0.45;0.5;0.7;0.75;1"
            dur="1.2s"
            begin="{cursor_delay}s"
            repeatCount="indefinite"
        />
    </rect>

    <!-- Footer -->
    <text
        x="310"
        y="285"
        font-family="monospace"
        font-size="14"
        fill="#8b949e"
        opacity="0"
    >
        $ whoami
        <animate
            attributeName="opacity"
            from="0"
            to="1"
            dur="0.6s"
            begin="{cursor_delay + 0.5}s"
            fill="freeze"
        />
    </text>

    <text
        x="400"
        y="285"
        font-family="monospace"
        font-size="14"
        fill="#3fb950"
        opacity="0"
    >
        developer
        <animate
            attributeName="opacity"
            from="0"
            to="1"
            dur="0.6s"
            begin="{cursor_delay + 1.1}s"
            fill="freeze"
        />
    </text>

</svg>
"""

OUTPUT.write_text(svg, encoding="utf-8")

print("Done!")
print(f"Created: {OUTPUT}")