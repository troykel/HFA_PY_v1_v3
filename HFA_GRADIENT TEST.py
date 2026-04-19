"""
HFA Gradient Lab - Standalone Test File
=======================================
Tests two experimental gradient types:
  LEFT  : Lava Lamp  (Metaball blending)
  RIGHT : Watercolor (Voronoi blending)

Safe to run - zero connection to HFA main file.
Author: Troyski / HFA 2026
"""

import sys
import numpy as np
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QHBoxLayout, QLabel, QVBoxLayout
from PySide6.QtGui import QImage, QPixmap, QPainter, QFont, QColor
from PySide6.QtCore import Qt, QTimer

# ─────────────────────────────────────────────
#  VIVID COLOR PALETTE  (feel free to swap these)
# ─────────────────────────────────────────────
VIVID_COLORS = [
    (255,  20, 147),   # Deep Pink
    (  0, 255, 200),   # Cyan Mint
    (255, 140,   0),   # Dark Orange
    ( 80,   0, 255),   # Electric Violet
    (255, 255,   0),   # Yellow
    (  0, 180, 255),   # Sky Blue
    (255,  60,  60),   # Red
    (  0, 255,  80),   # Lime Green
]

CANVAS_W = 325
CANVAS_H = 325


# ─────────────────────────────────────────────
#  LAVA LAMP  (Metaball blending)
# ─────────────────────────────────────────────
def render_lava_lamp(width, height, colors, seed=42):
    """
    HOW IT WORKS:
    - Place N colored blobs at random positions
    - Every pixel asks: how close am I to each blob?
    - Closer = more influence from that blob's color
    - Influence = 1 / distance^2  (inverse square law)
    - Final color = weighted average of all blob colors
    Result: soft, melting, organic color pools
    """
    rng = np.random.default_rng(seed)
    num_blobs = len(colors)

    # Random blob positions (normalized 0.0 to 1.0)
    bx = rng.uniform(0.1, 0.9, num_blobs)
    by = rng.uniform(0.1, 0.9, num_blobs)

    # Build pixel coordinate grids
    px = np.linspace(0, 1, width)
    py = np.linspace(0, 1, height)
    gx, gy = np.meshgrid(px, py)   # shape: (height, width)

    # Accumulate weighted colors across all blobs
    r_acc = np.zeros((height, width))
    g_acc = np.zeros((height, width))
    b_acc = np.zeros((height, width))
    w_acc = np.zeros((height, width))

    for i, (cr, cg, cb) in enumerate(colors):
        # Distance squared from every pixel to this blob
        dx = gx - bx[i]
        dy = gy - by[i]
        dist_sq = dx*dx + dy*dy

        # Avoid division by zero at exact blob center
        dist_sq = np.maximum(dist_sq, 1e-6)

        # Influence falls off with distance (inverse square)
        influence = 1.0 / dist_sq

        r_acc += influence * cr
        g_acc += influence * cg
        b_acc += influence * cb
        w_acc += influence

    # Normalize: divide by total influence weight
    r = np.clip(r_acc / w_acc, 0, 255).astype(np.uint8)
    g = np.clip(g_acc / w_acc, 0, 255).astype(np.uint8)
    b = np.clip(b_acc / w_acc, 0, 255).astype(np.uint8)

    # Pack into RGBA array for QImage
    rgba = np.stack([r, g, b, np.full_like(r, 255)], axis=2)
    return rgba.tobytes(), width, height


# ─────────────────────────────────────────────
#  WATERCOLOR  (Voronoi blending)
# ─────────────────────────────────────────────
def render_watercolor(width, height, colors, seed=77):
    """
    HOW IT WORKS:
    - Scatter N seed points, each with a color
    - Every pixel finds its 2 nearest seed points
    - Blend between those 2 colors by distance ratio
    - Add a little noise at the borders = painted edge feel
    Result: watercolor washes bleeding into each other
    """
    rng = np.random.default_rng(seed)
    num_seeds = len(colors)

    # Random seed positions
    sx = rng.uniform(0.05, 0.95, num_seeds) * width
    sy = rng.uniform(0.05, 0.95, num_seeds) * height

    # Build pixel coordinate grids
    px = np.arange(width)
    py = np.arange(height)
    gx, gy = np.meshgrid(px, py)   # shape: (height, width)

    # For each pixel, find distances to ALL seeds
    # seeds shape: (num_seeds,)  grids shape: (height, width)
    # We expand dims to broadcast: (height, width, num_seeds)
    dx = gx[:, :, np.newaxis] - sx[np.newaxis, np.newaxis, :]
    dy = gy[:, :, np.newaxis] - sy[np.newaxis, np.newaxis, :]
    dists = np.sqrt(dx*dx + dy*dy)   # (height, width, num_seeds)

    # Find indices of 2 nearest seeds per pixel
    sorted_idx = np.argsort(dists, axis=2)
    idx1 = sorted_idx[:, :, 0]   # nearest seed
    idx2 = sorted_idx[:, :, 1]   # second nearest seed

    d1 = np.take_along_axis(dists, idx1[:, :, np.newaxis], axis=2).squeeze(2)
    d2 = np.take_along_axis(dists, idx2[:, :, np.newaxis], axis=2).squeeze(2)

    # Blend ratio: how far between seed1 and seed2
    total = d1 + d2
    total = np.maximum(total, 1e-6)

    # Add noise to soften the Voronoi edges (watercolor bleed)
    noise = rng.uniform(0, 0.25, (height, width))
    t = np.clip((d1 / total) + noise, 0, 1)   # 0=all seed1, 1=all seed2

    # Gather colors for nearest and second-nearest seeds
    colors_arr = np.array(colors, dtype=np.float32)  # (num_seeds, 3)

    c1 = colors_arr[idx1]   # (height, width, 3)
    c2 = colors_arr[idx2]   # (height, width, 3)

    # Lerp between the two colors
    t3 = t[:, :, np.newaxis]
    blended = c1 * (1 - t3) + c2 * t3
    blended = np.clip(blended, 0, 255).astype(np.uint8)

    r, g, b = blended[:, :, 0], blended[:, :, 1], blended[:, :, 2]
    rgba = np.stack([r, g, b, np.full_like(r, 255)], axis=2)
    return rgba.tobytes(), width, height

def render_watercolor_soft(width, height, colors, seed=99):
    """
    TRUE WATERCOLOR: Same Voronoi structure as Stained Glass
    but with a much wider blend zone — colors bleed softly
    into each other like wet paint on paper.
    """
    rng = np.random.default_rng(seed)
    num_seeds = len(colors)

    sx = rng.uniform(0.05, 0.95, num_seeds) * width
    sy = rng.uniform(0.05, 0.95, num_seeds) * height

    px = np.arange(width)
    py = np.arange(height)
    gx, gy = np.meshgrid(px, py)

    dx = gx[:, :, np.newaxis] - sx[np.newaxis, np.newaxis, :]
    dy = gy[:, :, np.newaxis] - sy[np.newaxis, np.newaxis, :]
    dists = np.sqrt(dx*dx + dy*dy)

    sorted_idx = np.argsort(dists, axis=2)
    idx1 = sorted_idx[:, :, 0]
    idx2 = sorted_idx[:, :, 1]

    d1 = np.take_along_axis(dists, idx1[:, :, np.newaxis], axis=2).squeeze(2)
    d2 = np.take_along_axis(dists, idx2[:, :, np.newaxis], axis=2).squeeze(2)

    gap = d2 - d1
    blend_zone = 200.0          # ← wide zone = soft watercolor bleeds
    t = np.clip(1.0 - (gap / blend_zone), 0.0, 1.0)
    t = t * t * (3.0 - 2.0 * t)   # smoothstep

    colors_arr = np.array(colors, dtype=np.float32)
    c1 = colors_arr[idx1]
    c2 = colors_arr[idx2]

    t3 = t[:, :, np.newaxis]
    blended = c1 * (1 - t3) + c2 * t3
    blended = np.clip(blended, 0, 255).astype(np.uint8)

    r, g, b = blended[:, :, 0], blended[:, :, 1], blended[:, :, 2]
    rgba = np.stack([r, g, b, np.full_like(r, 255)], axis=2)
    return rgba.tobytes(), width, height

# ─────────────────────────────────────────────
#  GRADIENT WIDGET  (renders one gradient)
# ─────────────────────────────────────────────
class GradientWidget(QWidget):
    def __init__(self, title, render_fn, colors, seed, parent=None):
        super().__init__(parent)
        self.setFixedSize(CANVAS_W, CANVAS_H + 50)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Title label
        lbl_title = QLabel(title)
        lbl_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_title.setFixedHeight(50)
        font = QFont("Arial", 18, QFont.Weight.Bold)
        lbl_title.setFont(font)
        lbl_title.setStyleSheet("color: #FFFFFF; background: #1A1A1A;")
        layout.addWidget(lbl_title)

        # Render the gradient to bytes
        raw, w, h = render_fn(CANVAS_W, CANVAS_H, colors, seed)

        # Build QImage from raw RGBA bytes
        img = QImage(raw, w, h, w * 4, QImage.Format.Format_RGBA8888)
        pixmap = QPixmap.fromImage(img)

        # Display in a label
        lbl_img = QLabel()
        lbl_img.setPixmap(pixmap)
        lbl_img.setFixedSize(CANVAS_W, CANVAS_H)
        layout.addWidget(lbl_img)


class GradientTestWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("HFA Gradient Lab — Lava Lamp | Stained Glass | Watercolor")
        self.setStyleSheet("background-color: #1A1A1A;")

        central = QWidget()
        self.setCentralWidget(central)
        layout = QHBoxLayout(central)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)

        # LEFT: Lava Lamp
        lava = GradientWidget(
            "🫧  Lava Lamp  (Metaball)",
            render_lava_lamp,
            VIVID_COLORS,
            seed=42
        )
        layout.addWidget(lava)

        # MIDDLE: Stained Glass
        water = GradientWidget(
            "🪟  Stained Glass  (Voronoi)",
            render_watercolor,
            VIVID_COLORS,
            seed=99
        )
        layout.addWidget(water)

        # RIGHT: Watercolor
        soft = GradientWidget(
            "🎨  Watercolor  (Soft Voronoi)",
            render_watercolor_soft,
            VIVID_COLORS,
            seed=99
        )
        layout.addWidget(soft)

        self.adjustSize()


# ─────────────────────────────────────────────
#  ENTRY POINT
# ─────────────────────────────────────────────
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = GradientTestWindow()
    window.show()
    sys.exit(app.exec())