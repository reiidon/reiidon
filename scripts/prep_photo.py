from pathlib import Path

import cv2
import numpy as np
from PIL import Image
from rembg import remove


# -------------------------------------------------
# Paths
# -------------------------------------------------

ROOT = Path(__file__).resolve().parent.parent
INPUT_PATH = ROOT / "data" / "source-photo.jpeg"
OUTPUT_PATH = ROOT / "data" / "source-prepped.png"


# -------------------------------------------------
# Load and remove background
# -------------------------------------------------

print("Loading image...")

image = Image.open(INPUT_PATH).convert("RGB")

print("Removing background...")
removed = remove(image).convert("RGBA")


# -------------------------------------------------
# Crop around the person
# -------------------------------------------------

alpha = np.array(removed.getchannel("A"))
mask = alpha > 10

if mask.any():
    ys, xs = np.where(mask)

    x1, x2 = xs.min(), xs.max()
    y1, y2 = ys.min(), ys.max()

    width = x2 - x1
    height = y2 - y1

    padding_x = int(width * 0.12)
    padding_y = int(height * 0.08)

    x1 = max(0, x1 - padding_x)
    y1 = max(0, y1 - padding_y)
    x2 = min(removed.width, x2 + padding_x)
    y2 = min(removed.height, y2 + padding_y)

    removed = removed.crop((x1, y1, x2, y2))


# -------------------------------------------------
# Put the person on a pure white background
# -------------------------------------------------

white_bg = Image.new("RGBA", removed.size, (255, 255, 255, 255))
white_bg.alpha_composite(removed)

result = white_bg.convert("RGB")


# -------------------------------------------------
# Convert to grayscale
# -------------------------------------------------

gray = np.array(result.convert("L"))


# -------------------------------------------------
# Improve local contrast using CLAHE
# -------------------------------------------------

clahe = cv2.createCLAHE(
    clipLimit=2.5,
    tileGridSize=(8, 8)
)

enhanced = clahe.apply(gray)


# -------------------------------------------------
# Light smoothing to reduce noise
# -------------------------------------------------

enhanced = cv2.GaussianBlur(
    enhanced,
    (3, 3),
    0
)


# -------------------------------------------------
# Save result
# -------------------------------------------------

Image.fromarray(enhanced).save(OUTPUT_PATH)

print()
print("Done!")
print(f"Saved: {OUTPUT_PATH}")