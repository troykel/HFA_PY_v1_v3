# HFA_2025.py - Refactored
# -*- coding: utf-8 -*-
"""
Huemanity for ALL (PySide6) - 2026 Edition

Copyright (c) 2025 Troy (Troyski). All Rights Reserved.
Licensed under Proprietary Software License Agreement - See LICENSE - Non and Commercial.txt

This software is proprietary and confidential. Unauthorized copying,
modification, distribution, or use is strictly prohibited.

Modern, refactored version with:
- Modern Python patterns (walrus operator, type hints, contextlib)
- Cleaner code organization
- Better error handling
- More maintainable structure
"""

from __future__ import annotations

import ast
import json
import math
import os
import random
import re
import sys
from contextlib import suppress
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw

# Optional: NumPy for fast gradients
try:
    import numpy as np

    NUMPY_AVAILABLE = True
    print(" NumPy enabled")
except ImportError:
    NUMPY_AVAILABLE = False
    print("Warning:  NumPy not available (app still works, just slower)")

from PySide6.QtCore import Qt, QTimer, Signal, QPointF, QSize
from PySide6.QtGui import QColor, QFont, QImage, QLinearGradient, QPainter, QPixmap, QPen, QPolygonF
from PySide6.QtWidgets import (
    QApplication, QComboBox, QDialog,
    QFileDialog, QFrame, QGridLayout, QHBoxLayout, QLabel, QLineEdit, QListWidget,
    QListWidgetItem, QInputDialog, QMainWindow, QMessageBox, QPushButton,
    QScrollArea, QSizePolicy, QSlider, QSplitter, QVBoxLayout, QWidget,
)

# --------------------------------------------------------------------------------------
# Font Configuration
# --------------------------------------------------------------------------------------
# Primary font: "Century Gothic UI"
# Fallbacks: Qt will automatically fall back to Roboto, Arial, or system defaults
# if Century Gothic UI is not available on the system.
# --------------------------------------------------------------------------------------

# --------------------------------------------------------------------------------------
# Master palettes import
# --------------------------------------------------------------------------------------
try:
    from HFA_ALL_palettes import Palette, DEFAULT_PALETTE_NAME, palette_names_and_map
except Exception:
    @dataclass(frozen=True)
    class Palette:
        name: str
        colors: list[str]
        category: str = "Primary Colors"
        positions: list[float] | None = None

        def get_positions(self) -> list[float]:
            """Get color positions, calculating even spacing if not specified."""
            if self.positions and len(self.positions) == len(self.colors):
                return self.positions
            # Fallback: even spacing for compatibility
            n = len(self.colors)
            return [i / (n - 1) if n > 1 else 0.0 for i in range(n)]


    DEFAULT_PALETTE_NAME = "RAINBOW - LGBTQ+"


    def palette_names_and_map() -> tuple[list[str], dict[str, Palette]]:
        """Fallback minimal palettes if HFA_ALL_palettes.py cannot be imported."""
        fallback = [
            Palette("RAINBOW - LGBTQ+", ["#FF0000", "#FFA500", "#FFFF00", "#008000", "#0000FF", "#4B0082", "#EE82EE"], "LGBTQ+"),
            Palette("TRANSGENDER_PRIDE", ["#55CDFC", "#FFFFFF", "#F7A8B8"], "LGBTQ+"),
            Palette("Disability Pride Flag", ["#000000", "#E50000", "#FFDD00", "#FFFFFF", "#0000A4", "#008121"], "Disability"),
        ]
        return [p.name for p in fallback], {p.name: p for p in fallback}

# --------------------------------------------------------------------------------------
# Constants
# --------------------------------------------------------------------------------------

DARK_CHARCOAL = "#1A1A1A"
BUTTON_BG = "#61003F"
BUTTON_TEXT = "#c1188b"
BUTTON_HOVER = "#B565F5"
BUTTON_PRESSED = "#8338DD"

MAX_GRADIENT_WIDTH = 3840
MAX_GRADIENT_HEIGHT = 2160

# Support for PyInstaller bundled .exe
if getattr(sys, 'frozen', False):
    # Running as compiled .exe
    SCRIPT_DIR = Path(sys._MEIPASS)
else:
    # Running as .py script
    SCRIPT_DIR = Path(__file__).parent.resolve()

PREVIEW_IDLE_IMAGE = SCRIPT_DIR / "IMAGES" / "HFA - Colors MOST beautiful when MIXED.png"

FONT_FAMILY = "Century Gothic UI", "Roboto", "Arial"
BUTTON_FONT_PT = 18
LABEL_FONT_PT = 18
VALUE_FONT_PT = 18
FONT_WEIGHT = 57  # Medium weight (between Normal 50 and DemiBold 63)

PALETTE_TILE_SIZE = 32
PALETTE_TILE_BORDER = "rgba(255,255,255,0.85)"
PALETTE_TILE_SPACING = 6
PALETTE_STRIP_MARGINS = (8, 6, 8, 6)
PALETTE_STRIP_HEIGHT = 40


# --------------------------------------------------------------------------------------
# File/Settings utilities
# --------------------------------------------------------------------------------------

def get_app_data_dir() -> Path:
    """Get application data directory for storing settings."""
    if sys.platform == "win32":
        base = Path(os.environ.get("APPDATA", Path.home() / "AppData" / "Roaming"))
    elif sys.platform == "darwin":
        base = Path.home() / "Library" / "Application Support"
    else:
        base = Path.home() / ".config"

    app_dir = base / "HuemanityForAll"
    app_dir.mkdir(parents=True, exist_ok=True)
    return app_dir


def safe_read_json(path: Path) -> dict:
    """Safely read JSON file, returning empty dict on error."""
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return {}


def safe_write_json(path: Path, data: dict) -> None:
    """Safely write JSON file."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


# --------------------------------------------------------------------------------------
# Color utilities
# --------------------------------------------------------------------------------------

def get_palette_positions(palette: Palette) -> list[float]:
    """Safely get positions from a Palette, whether it has the method or not."""
    if hasattr(palette, 'get_positions'):
        return palette.get_positions()
    # Fallback: calculate even spacing
    if hasattr(palette, 'positions') and palette.positions and len(palette.positions) == len(palette.colors):
        return palette.positions
    n = len(palette.colors)
    return [i / (n - 1) if n > 1 else 0.0 for i in range(n)]


def hex_to_rgb(s: str) -> tuple[int, int, int]:
    """Convert hex color string to RGB tuple."""
    s = s.strip().lstrip("#")
    return int(s[0:2], 16), int(s[2:4], 16), int(s[4:6], 16)


def lerp_color(c1: tuple[int, int, int], c2: tuple[int, int, int], t: float) -> tuple[int, int, int]:
    """Linear interpolation between two RGB colors."""
    if t <= 0.0:
        return c1
    if t >= 1.0:
        return c2
    r = int(c1[0] + (c2[0] - c1[0]) * t)
    g = int(c1[1] + (c2[1] - c1[1]) * t)
    b = int(c1[2] + (c2[2] - c1[2]) * t)
    return (r, g, b)


def normalize_hex_color(s: str) -> str | None:
    """Normalize and validate hex color string."""
    if not isinstance(s, str) or not (t := s.strip()):
        return None

    t = t.lstrip("#")

    # Convert 3-char to 6-char hex
    if len(t) == 3 and all(c in "0123456789abcdefABCDEF" for c in t):
        t = "".join(c * 2 for c in t)

    return f"#{t.upper()}" if len(t) == 6 and all(c in "0123456789abcdefABCDEF" for c in t) else None


# --------------------------------------------------------------------------------------
# Gradient rendering
# --------------------------------------------------------------------------------------

def radial_gradient(width: int, height: int, colors: list[str], positions: list[float] | None = None) -> Image.Image:
    """Generate radial gradient."""
    img = Image.new("RGB", (width, height))
    pixels = img.load()
    center_x, center_y = width // 2, height // 2
    max_radius = math.hypot(width / 2, height / 2) or 1.0

    stops = [hex_to_rgb(c) for c in colors]
    if len(stops) < 2:
        stops = [stops[0], stops[0]]

    # Use provided positions or calculate even spacing
    if positions and len(positions) == len(stops):
        steps = [(positions[i], stops[i]) for i in range(len(stops))]
    else:
        steps = [(i / (len(stops) - 1), stops[i]) for i in range(len(stops))]

    for y in range(height):
        for x in range(width):
            distance = math.hypot(x - center_x, y - center_y)
            t = min(1.0, distance / max_radius)

            for i in range(len(steps) - 1):
                s_pos, s_color = steps[i]
                e_pos, e_color = steps[i + 1]
                if s_pos <= t <= e_pos:
                    tt = (t - s_pos) / (e_pos - s_pos) if e_pos > s_pos else 0.0
                    pixels[x, y] = lerp_color(s_color, e_color, tt)
                    break
            else:
                pixels[x, y] = steps[-1][1]

    return img


def conical_gradient(width: int, height: int, colors: list[str], positions: list[float] | None = None) -> Image.Image:
    """Generate conical (sweep) gradient."""
    img = Image.new("RGB", (width, height))
    pixels = img.load()
    center_x, center_y = width // 2, height // 2

    stops = [hex_to_rgb(c) for c in colors]
    if len(stops) < 2:
        stops = [stops[0], stops[0]]
    # Use provided positions or calculate even spacing
    if positions and len(positions) == len(stops):
        steps = [(positions[i], stops[i]) for i in range(len(stops))]
    else:
        steps = [(i / (len(stops) - 1), stops[i]) for i in range(len(stops))]

    for y in range(height):
        for x in range(width):
            angle = math.atan2(y - center_y, x - center_x)
            t = (angle + math.pi) / (2 * math.pi)

            for i in range(len(steps) - 1):
                s_pos, s_color = steps[i]
                e_pos, e_color = steps[i + 1]
                if s_pos <= t <= e_pos:
                    tt = (t - s_pos) / (e_pos - s_pos) if e_pos > s_pos else 0.0
                    pixels[x, y] = lerp_color(s_color, e_color, tt)
                    break
            else:
                pixels[x, y] = steps[-1][1]

    return img


def linear_gradient(width: int, height: int, colors: list[str], direction: str, positions: list[float] | None = None) -> Image.Image:
    """Generate linear gradient in specified direction."""
    stops = [hex_to_rgb(c) for c in colors]
    if len(stops) < 2:
        stops = [stops[0], stops[0]]

    n = max(1, len(stops) - 1)

    # Calculate color positions
    if positions and len(positions) == len(stops):
        color_positions = positions
    else:
        color_positions = [i / n for i in range(len(stops))]
    img = Image.new("RGB", (width, height), (0, 0, 0))
    draw = ImageDraw.Draw(img)

    match direction:
        case "Horizontal":
            for x in range(width):
                t = x / (width - 1) if width > 1 else 0.0
                seg = min(int(t * n), n - 1)
                local_t = (t * n) - seg
                draw.line([(x, 0), (x, height)], fill=lerp_color(stops[seg], stops[seg + 1], local_t))

        case "Vertical":
            for y in range(height):
                t = y / (height - 1) if height > 1 else 0.0
                seg = min(int(t * n), n - 1)
                local_t = (t * n) - seg
                draw.line([(0, y), (width, y)], fill=lerp_color(stops[seg], stops[seg + 1], local_t))

        case _:  # Diagonal
            for y in range(height):
                ty = y / (height - 1) if height > 1 else 0.0
                segy = min(int(ty * n), n - 1)
                local_ty = (ty * n) - segy
                cy = lerp_color(stops[segy], stops[segy + 1], local_ty)
                for x in range(width):
                    tx = x / (width - 1) if width > 1 else 0.0
                    segx = min(int(tx * n), n - 1)
                    local_tx = (tx * n) - segx
                    cx = lerp_color(stops[segx], stops[segx + 1], local_tx)
                    img.putpixel((x, y), tuple((cx[i] + cy[i]) // 2 for i in range(3)))

    return img


def liquid_blur_gradient(width: int, height: int, colors: list[str], positions: list[float] | None = None) -> Image.Image:
    """Generate liquid/fluid gradient with soft Gaussian blur for dreamy aesthetic."""
    img = Image.new("RGB", (width, height))

    stops = [hex_to_rgb(c) for c in colors]
    if len(stops) < 2:
        stops = [stops[0], stops[0]]

    # Create well-distributed blob centers for each color
    random.seed(42)  # Consistent seed for reproducible results

    blob_data = []
    for i, color in enumerate(stops):
        # Create 2-3 blobs per color with better distribution
        num_color_blobs = random.randint(2, 5)
        for _ in range(num_color_blobs):
            blob_data.append({
                'color': color,
                'x': random.uniform(-0.2, 1.2),  # Allow blobs to extend beyond edges
                'y': random.uniform(-0.2, 1.2),
                'size': random.uniform(0.15, 0.35),  # Smaller blobs = more distinct colors
                'intensity': random.uniform(0.8, 1.75)  # Higher intensity for bolder colors
            })

    # Create the gradient by blending colored blobs
    pixels = img.load()

    for y in range(height):
        for x in range(width):
            nx = x / max(width, 1)
            ny = y / max(height, 1)

            # Accumulate color influence from all blobs
            r_total, g_total, b_total = 0.0, 0.0, 0.0, 0.0, 0.0
            weight_total = 0.0

            for blob in blob_data:
                # Distance from blob center
                dx = nx - blob['x']
                dy = ny - blob['y']
                dist = math.sqrt(dx * dx + dy * dy)

                # Stronger falloff for more distinct blobs
                influence = math.exp(-dist * dist / (blob['size'] * blob['size']))
                influence *= blob['intensity']

                # Add this blob's color contribution
                r_total += blob['color'][0] * influence
                g_total += blob['color'][1] * influence
                b_total += blob['color'][2] * influence
                weight_total += influence

            # Normalize and clamp
            if weight_total > 0:
                r = int(min(255, max(0, r_total / weight_total)))
                g = int(min(255, max(0, g_total / weight_total)))
                b = int(min(255, max(0, b_total / weight_total)))
            else:
                r, g, b = stops[0]  # Fallback to first color

            pixels[x, y] = (r, g, b)

    # Apply lighter Gaussian blur - enough for dreamy look but preserves color variation
    from PIL import ImageFilter
    blur_radius = min(width, height) // 40  # Lighter blur (was //20)
    img = img.filter(ImageFilter.GaussianBlur(radius=max(8, blur_radius)))

    return img


def spiral_gradient(width: int, height: int, colors: list[str], positions: list[float] | None = None) -> Image.Image:
    """Generate spiral gradient emanating from center."""
    img = Image.new("RGB", (width, height))
    pixels = img.load()
    center_x, center_y = width // 2, height // 2

    stops = [hex_to_rgb(c) for c in colors]
    if len(stops) < 2:
        stops = [stops[0], stops[0]]

    if positions and len(positions) == len(stops):
        steps = [(positions[i], stops[i]) for i in range(len(stops))]
    else:
        steps = [(i / (len(stops) - 1), stops[i]) for i in range(len(stops))]

    max_radius = math.hypot(width / 2, height / 2) or 1.0

    for y in range(height):
        for x in range(width):
            angle = math.atan2(y - center_y, x - center_x)
            distance = math.hypot(x - center_x, y - center_y)
            rotations = 3.0
            t = ((angle + math.pi) / (2 * math.pi) + (distance / max_radius) * rotations) % 1.0

            for i in range(len(steps) - 1):
                s_pos, s_color = steps[i]
                e_pos, e_color = steps[i + 1]
                if s_pos <= t <= e_pos:
                    tt = (t - s_pos) / (e_pos - s_pos) if e_pos > s_pos else 0.0
                    pixels[x, y] = lerp_color(s_color, e_color, tt)
                    break
            else:
                pixels[x, y] = steps[-1][1]

    return img


def diamond_gradient(width: int, height: int, colors: list[str], positions: list[float] | None = None) -> Image.Image:
    """Generate diamond/square gradient from center."""
    img = Image.new("RGB", (width, height))
    pixels = img.load()
    center_x, center_y = width // 2, height // 2

    stops = [hex_to_rgb(c) for c in colors]
    if len(stops) < 2:
        stops = [stops[0], stops[0]]

    if positions and len(positions) == len(stops):
        steps = [(positions[i], stops[i]) for i in range(len(stops))]
    else:
        steps = [(i / (len(stops) - 1), stops[i]) for i in range(len(stops))]

    max_dist = max(width / 2, height / 2)

    for y in range(height):
        for x in range(width):
            dx = abs(x - center_x)
            dy = abs(y - center_y)
            distance = max(dx, dy)
            t = min(1.0, distance / max_dist)

            for i in range(len(steps) - 1):
                s_pos, s_color = steps[i]
                e_pos, e_color = steps[i + 1]
                if s_pos <= t <= e_pos:
                    tt = (t - s_pos) / (e_pos - s_pos) if e_pos > s_pos else 0.0
                    pixels[x, y] = lerp_color(s_color, e_color, tt)
                    break
            else:
                pixels[x, y] = steps[-1][1]

    return img


# --------------------------------------------------------------------------------------
# FAST NumPy gradient functions (10-100x faster!)
# --------------------------------------------------------------------------------------

if NUMPY_AVAILABLE:
    def radial_gradient_fast(width: int, height: int, colors: list[str], positions: list[float] | None = None) -> Image.Image:
        """Fast radial gradient using NumPy."""
        stops = np.array([hex_to_rgb(c) for c in colors], dtype=np.float32)
        if len(stops) < 2:
            stops = np.array([stops[0], stops[0]], dtype=np.float32)
        y_coords, x_coords = np.ogrid[:height, :width]
        center_x, center_y = width / 2, height / 2
        distances = np.sqrt((x_coords - center_x) ** 2 + (y_coords - center_y) ** 2)
        max_radius = math.hypot(width / 2, height / 2) or 1.0
        t_values = np.clip(distances / max_radius, 0, 1)
        num_stops = len(stops)
        segment_indices = np.floor(t_values * (num_stops - 1)).astype(np.int32)
        segment_indices = np.clip(segment_indices, 0, num_stops - 2)
        segment_t = t_values * (num_stops - 1) - segment_indices
        segment_t = np.clip(segment_t, 0, 1)
        img_array = np.zeros((height, width, 3), dtype=np.uint8)
        for i in range(num_stops - 1):
            mask = (segment_indices == i)
            if np.any(mask):
                t_local = segment_t[mask]
                color1, color2 = stops[i], stops[i + 1]
                for channel in range(3):
                    img_array[:, :, channel][mask] = (color1[channel] * (1 - t_local) + color2[channel] * t_local).astype(np.uint8)
        return Image.fromarray(img_array, mode='RGB')


    def conical_gradient_fast(width: int, height: int, colors: list[str], positions: list[float] | None = None) -> Image.Image:
        """Fast conical gradient using NumPy."""
        stops = np.array([hex_to_rgb(c) for c in colors], dtype=np.float32)
        if len(stops) < 2:
            stops = np.array([stops[0], stops[0]], dtype=np.float32)
        y_coords, x_coords = np.ogrid[:height, :width]
        center_x, center_y = width / 2, height / 2
        angles = np.arctan2(y_coords - center_y, x_coords - center_x)
        t_values = (angles + np.pi) / (2 * np.pi)
        num_stops = len(stops)
        segment_indices = np.floor(t_values * (num_stops - 1)).astype(np.int32)
        segment_indices = np.clip(segment_indices, 0, num_stops - 2)
        segment_t = t_values * (num_stops - 1) - segment_indices
        segment_t = np.clip(segment_t, 0, 1)
        img_array = np.zeros((height, width, 3), dtype=np.uint8)
        for i in range(num_stops - 1):
            mask = (segment_indices == i)
            if np.any(mask):
                t_local = segment_t[mask]
                color1, color2 = stops[i], stops[i + 1]
                for channel in range(3):
                    img_array[:, :, channel][mask] = (color1[channel] * (1 - t_local) + color2[channel] * t_local).astype(np.uint8)
        return Image.fromarray(img_array, mode='RGB')


    def linear_gradient_fast(width: int, height: int, colors: list[str], direction: str, positions: list[float] | None = None) -> Image.Image:
        """Fast linear gradient using NumPy."""
        stops = np.array([hex_to_rgb(c) for c in colors], dtype=np.float32)
        if len(stops) < 2:
            stops = np.array([stops[0], stops[0]], dtype=np.float32)
        num_stops = len(stops)
        if direction == "Horizontal":
            t_values = np.linspace(0, 1, width)
            segment_indices = np.floor(t_values * (num_stops - 1)).astype(np.int32)
            segment_indices = np.clip(segment_indices, 0, num_stops - 2)
            segment_t = t_values * (num_stops - 1) - segment_indices
            segment_t = np.clip(segment_t, 0, 1)
            gradient_1d = np.zeros((width, 3), dtype=np.uint8)
            for i in range(num_stops - 1):
                mask = (segment_indices == i)
                if np.any(mask):
                    t_local = segment_t[mask]
                    color1, color2 = stops[i], stops[i + 1]
                    for channel in range(3):
                        gradient_1d[mask, channel] = (color1[channel] * (1 - t_local) + color2[channel] * t_local).astype(np.uint8)
            img_array = np.repeat(gradient_1d[np.newaxis, :, :], height, axis=0)
        elif direction == "Vertical":
            t_values = np.linspace(0, 1, height)
            segment_indices = np.floor(t_values * (num_stops - 1)).astype(np.int32)
            segment_indices = np.clip(segment_indices, 0, num_stops - 2)
            segment_t = t_values * (num_stops - 1) - segment_indices
            segment_t = np.clip(segment_t, 0, 1)
            gradient_1d = np.zeros((height, 3), dtype=np.uint8)
            for i in range(num_stops - 1):
                mask = (segment_indices == i)
                if np.any(mask):
                    t_local = segment_t[mask]
                    color1, color2 = stops[i], stops[i + 1]
                    for channel in range(3):
                        gradient_1d[mask, channel] = (color1[channel] * (1 - t_local) + color2[channel] * t_local).astype(np.uint8)
            img_array = np.repeat(gradient_1d[:, np.newaxis, :], width, axis=1)
        else:
            y_coords, x_coords = np.ogrid[:height, :width]
            t_x = x_coords / (width - 1) if width > 1 else 0
            t_y = y_coords / (height - 1) if height > 1 else 0
            t_values = (t_x + t_y) / 2
            t_values = np.clip(t_values, 0, 1)
            segment_indices = np.floor(t_values * (num_stops - 1)).astype(np.int32)
            segment_indices = np.clip(segment_indices, 0, num_stops - 2)
            segment_t = t_values * (num_stops - 1) - segment_indices
            segment_t = np.clip(segment_t, 0, 1)
            img_array = np.zeros((height, width, 3), dtype=np.uint8)
            for i in range(num_stops - 1):
                mask = (segment_indices == i)
                if np.any(mask):
                    t_local = segment_t[mask]
                    color1, color2 = stops[i], stops[i + 1]
                    for channel in range(3):
                        img_array[:, :, channel][mask] = (color1[channel] * (1 - t_local) + color2[channel] * t_local).astype(np.uint8)
        return Image.fromarray(img_array, mode='RGB')


    def spiral_gradient_fast(width: int, height: int, colors: list[str], positions: list[float] | None = None) -> Image.Image:
        """Fast spiral gradient using NumPy."""
        stops = np.array([hex_to_rgb(c) for c in colors], dtype=np.float32)
        if len(stops) < 2:
            stops = np.array([stops[0], stops[0]], dtype=np.float32)

        y_coords, x_coords = np.ogrid[:height, :width]
        center_x, center_y = width / 2, height / 2
        angles = np.arctan2(y_coords - center_y, x_coords - center_x)
        distances = np.sqrt((x_coords - center_x) ** 2 + (y_coords - center_y) ** 2)
        max_radius = math.hypot(width / 2, height / 2) or 1.0

        rotations = 3.0
        t_values = ((angles + np.pi) / (2 * np.pi) + (distances / max_radius) * rotations) % 1.0

        num_stops = len(stops)
        segment_indices = np.floor(t_values * (num_stops - 1)).astype(np.int32)
        segment_indices = np.clip(segment_indices, 0, num_stops - 2)
        segment_t = t_values * (num_stops - 1) - segment_indices
        segment_t = np.clip(segment_t, 0, 1)

        img_array = np.zeros((height, width, 3), dtype=np.uint8)
        for i in range(num_stops - 1):
            mask = (segment_indices == i)
            if np.any(mask):
                t_local = segment_t[mask]
                color1, color2 = stops[i], stops[i + 1]
                for channel in range(3):
                    img_array[:, :, channel][mask] = (color1[channel] * (1 - t_local) + color2[channel] * t_local).astype(np.uint8)

        return Image.fromarray(img_array, mode='RGB')


    def diamond_gradient_fast(width: int, height: int, colors: list[str], positions: list[float] | None = None) -> Image.Image:
        """Fast diamond gradient using NumPy."""
        stops = np.array([hex_to_rgb(c) for c in colors], dtype=np.float32)
        if len(stops) < 2:
            stops = np.array([stops[0], stops[0]], dtype=np.float32)

        y_coords, x_coords = np.ogrid[:height, :width]
        center_x, center_y = width / 2, height / 2
        dx = np.abs(x_coords - center_x)
        dy = np.abs(y_coords - center_y)
        distances = np.maximum(dx, dy)
        max_dist = max(width / 2, height / 2)
        t_values = np.clip(distances / max_dist, 0, 1)

        num_stops = len(stops)
        segment_indices = np.floor(t_values * (num_stops - 1)).astype(np.int32)
        segment_indices = np.clip(segment_indices, 0, num_stops - 2)
        segment_t = t_values * (num_stops - 1) - segment_indices
        segment_t = np.clip(segment_t, 0, 1)

        img_array = np.zeros((height, width, 3), dtype=np.uint8)
        for i in range(num_stops - 1):
            mask = (segment_indices == i)
            if np.any(mask):
                t_local = segment_t[mask]
                color1, color2 = stops[i], stops[i + 1]
                for channel in range(3):
                    img_array[:, :, channel][mask] = (color1[channel] * (1 - t_local) + color2[channel] * t_local).astype(np.uint8)

        return Image.fromarray(img_array, mode='RGB')


    def liquid_blur_gradient_fast(width: int, height: int, colors: list[str], positions: list[float] | None = None) -> Image.Image:
        """Fast liquid/fluid blur gradient using NumPy."""
        stops = np.array([hex_to_rgb(c) for c in colors], dtype=np.float32)
        if len(stops) < 2:
            stops = np.array([stops[0], stops[0]], dtype=np.float32)

        # Create better-distributed random blob centers
        np.random.seed(42)

        # Variable number of blobs per color (2-3)
        blob_list = []
        for color in stops:
            num_color_blobs = np.random.randint(2, 4)  # 2-3 blobs per color
            for _ in range(num_color_blobs):
                blob_list.append(color)

        num_blobs = len(blob_list)
        blob_colors = np.array(blob_list, dtype=np.float32)

        blob_x = np.random.uniform(-0.2, 1.2, num_blobs)  # Extend beyond edges
        blob_y = np.random.uniform(-0.2, 1.2, num_blobs)
        blob_size = np.random.uniform(0.15, 0.35, num_blobs)  # Smaller blobs
        blob_intensity = np.random.uniform(0.8, 1.2, num_blobs)  # Higher intensity

        # Create coordinate grids
        y_coords, x_coords = np.ogrid[:height, :width]
        nx = x_coords / max(width, 1)
        ny = y_coords / max(height, 1)

        # Initialize color accumulation arrays
        r_total = np.zeros((height, width), dtype=np.float32)
        g_total = np.zeros((height, width), dtype=np.float32)
        b_total = np.zeros((height, width), dtype=np.float32)
        weight_total = np.zeros((height, width), dtype=np.float32)

        # Calculate influence from each blob
        for i in range(num_blobs):
            dx = nx - blob_x[i]
            dy = ny - blob_y[i]
            dist_sq = dx * dx + dy * dy

            # Stronger falloff for more distinct blobs
            influence = np.exp(-dist_sq / (blob_size[i] * blob_size[i]))
            influence *= blob_intensity[i]

            # Accumulate color
            r_total += blob_colors[i][0] * influence
            g_total += blob_colors[i][1] * influence
            b_total += blob_colors[i][2] * influence
            weight_total += influence

        # Normalize
        weight_total = np.maximum(weight_total, 1e-10)  # Avoid division by zero
        img_array = np.stack([
            np.clip(r_total / weight_total, 0, 255).astype(np.uint8),
            np.clip(g_total / weight_total, 0, 255).astype(np.uint8),
            np.clip(b_total / weight_total, 0, 255).astype(np.uint8)
        ], axis=2)

        # Convert to PIL and apply lighter Gaussian blur
        img = Image.fromarray(img_array, mode='RGB')
        from PIL import ImageFilter
        blur_radius = min(width, height) // 40  # Lighter blur
        img = img.filter(ImageFilter.GaussianBlur(radius=max(8, blur_radius)))

        return img


def pil_to_qpixmap(img: Image.Image) -> QPixmap:
    """Convert PIL Image to QPixmap."""
    if img.mode != "RGBA":
        img = img.convert("RGBA")
    data = img.tobytes("raw", "RGBA")
    qimg = QImage(data, img.width, img.height, QImage.Format_RGBA8888)
    return QPixmap.fromImage(qimg)


# --------------------------------------------------------------------------------------
# Gradient settings dataclass
# --------------------------------------------------------------------------------------

@dataclass
class GradientSettings:
    """All settings needed to render a gradient image."""
    width: int = 1200
    height: int = 675
    direction: str = "Horizontal"
    palette: Palette = field(default_factory=lambda: Palette(
        name=DEFAULT_PALETTE_NAME,
        colors=["#FF0000", "#FFA500", "#FFFF00", "#008000", "#0000FF", "#4B0082", "#EE82EE"],
        category="LGBTQ+",
    ))

    def clamp(self) -> bool:
        """Clamp dimensions to safe bounds. Returns True if changed."""
        changed = False

        if self.width < 1:
            self.width, changed = 1, True
        elif self.width > MAX_GRADIENT_WIDTH:
            self.width, changed = MAX_GRADIENT_WIDTH, True

        if self.height < 1:
            self.height, changed = 1, True
        elif self.height > MAX_GRADIENT_HEIGHT:
            self.height, changed = MAX_GRADIENT_HEIGHT, True

        return changed

    def to_image(self) -> Image.Image:
        """Render gradient to PIL Image (uses fast NumPy if available)."""
        if NUMPY_AVAILABLE:
            match self.direction:
                case "Radial (Center)":
                    return radial_gradient_fast(self.width, self.height, self.palette.colors, get_palette_positions(self.palette))
                case "Conical (Sweep)":
                    return conical_gradient_fast(self.width, self.height, self.palette.colors, get_palette_positions(self.palette))

                case "Spiral":
                    return spiral_gradient_fast(self.width, self.height, self.palette.colors, get_palette_positions(self.palette))
                case "Diamond":
                    return diamond_gradient_fast(self.width, self.height, self.palette.colors, get_palette_positions(self.palette))
                case "Liquid / Fluid Blur":
                    return liquid_blur_gradient_fast(self.width, self.height, self.palette.colors, get_palette_positions(self.palette))
                case _:
                    return linear_gradient_fast(self.width, self.height, self.palette.colors, self.direction, get_palette_positions(self.palette))
        else:
            match self.direction:
                case "Radial (Center)":
                    return radial_gradient(self.width, self.height, self.palette.colors, get_palette_positions(self.palette))
                case "Conical (Sweep)":
                    return conical_gradient(self.width, self.height, self.palette.colors, get_palette_positions(self.palette))

                case "Spiral":
                    return spiral_gradient(self.width, self.height, self.palette.colors, get_palette_positions(self.palette))
                case "Diamond":
                    return diamond_gradient(self.width, self.height, self.palette.colors, get_palette_positions(self.palette))
                case "Liquid / Fluid Blur":
                    return liquid_blur_gradient(self.width, self.height, self.palette.colors, get_palette_positions(self.palette))
                case _:
                    return linear_gradient(self.width, self.height, self.palette.colors, self.direction, get_palette_positions(self.palette))


def build_static_banner(width: int = 1450, height: int = 50) -> Image.Image:
    """Build banner gradient using default palette."""
    names, name_to = palette_names_and_map()
    default = name_to.get(DEFAULT_PALETTE_NAME) or (
        name_to[names[0]] if names else
        Palette(DEFAULT_PALETTE_NAME, ["#000000", "#FFFFFF"], "Primary Colors")
    )
    return GradientSettings(width=width, height=height, direction="Horizontal", palette=default).to_image()


# --------------------------------------------------------------------------------------
# Palette loading utilities
# --------------------------------------------------------------------------------------

def _palettes_from_parsed_data(data: Any) -> list[Palette]:
    """Extract Palette objects from parsed JSON/Python data."""
    palettes: list[Palette] = []

    def add_palette(name: str, colors: Any, category: str | None = None) -> None:
        if not name or not isinstance(colors, list):
            return

        norm = [nc for c in colors if (nc := normalize_hex_color(c))]

        if len(norm) >= 2:
            palettes.append(Palette(name=name.strip(), colors=norm, category=category or "Imported"))

    if isinstance(data, dict):
        if "palettes" in data and isinstance(data["palettes"], list):
            for item in data["palettes"]:
                if isinstance(item, dict):
                    add_palette(
                        str(item.get("name", "")).strip(),
                        item.get("colors", []),
                        str(item.get("category", "")).strip() or "Imported",
                    )
        else:
            for k, v in data.items():
                if isinstance(v, list):
                    # Direct list format: {"Name": ["#FF0000", ...]}
                    add_palette(str(k).strip(), v, "Imported")
                elif isinstance(v, dict) and "colors" in v:
                    # Object format: {"Name": {"colors": [...], "category": "..."}}
                    add_palette(
                        str(k).strip(),
                        v.get("colors", []),
                        str(v.get("category", "")).strip() or "Imported"
                    )
    elif isinstance(data, list):
        for item in data:
            if isinstance(item, dict):
                add_palette(
                    str(item.get("name", "")).strip(),
                    item.get("colors", []),
                    str(item.get("category", "")).strip() or "Imported",
                )

    return palettes


def load_palettes_from_file(path: str) -> list[Palette]:
    """Load palettes from JSON or Python data file."""
    ext = Path(path).suffix.lower()

    try:
        with open(path, "r", encoding="utf-8") as f:
            raw = f.read().strip()

        # Try JSON first
        if ext == ".json" or raw.startswith(("{", "[")):
            # Handle triple-quoted JSON
            if (raw.startswith('"""') and raw.endswith('"""')) or \
                    (raw.startswith("'''") and raw.endswith("'''")):
                raw = raw[3:-3].strip()
            data = json.loads(raw)
            return _palettes_from_parsed_data(data)

        # Try Python literal eval
        with suppress(Exception):
            data = ast.literal_eval(raw)
            return _palettes_from_parsed_data(data)

        # Try parsing Python module
        module = ast.parse(raw, filename="<palette_file>", mode="exec")
        allowed_names = {"APPS_ONLY", "palettes", "PALLETES", "palette_data", "PALETTE_DATA"}

        for node in module.body:
            if isinstance(node, ast.Assign) and len(node.targets) == 1 and \
                    isinstance(node.targets[0], ast.Name) and node.targets[0].id in allowed_names:
                data = ast.literal_eval(node.value)
                return _palettes_from_parsed_data(data)

        # Try regex match for dict/list at end
        if match := re.search(r"(\{.*\}|\[.*\])\s*$", raw, flags=re.DOTALL):
            data = ast.literal_eval(match.group(1))
            return _palettes_from_parsed_data(data)

    except Exception as e:
        raise ValueError(f"Could not parse palette file: {e}")

    return []


# --------------------------------------------------------------------------------------
# Accessible HSV Color Wheel + pick_color() helper
# Round disc design: Hue = angle, Saturation = distance from center
# Separate sliders for Hue, Saturation, Brightness, Alpha
# Real-time preview, Hex input with Copy, RGB readout, large fonts
# --------------------------------------------------------------------------------------

class ColorWheelWidget(QWidget):
    """Round HSV disc: angle = hue, distance from center = saturation.
    Brightness is handled by a separate slider, not baked into the disc.
    """
    colorChanged = Signal(QColor)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._hue = 0.0        # 0–360
        self._sat = 1.0        # 0–1
        self._val = 1.0        # 0–1  (brightness, controlled by slider)
        self._alpha = 255      # 0–255
        self._dragging = False
        self.setFixedSize(280, 280)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def color(self) -> QColor:
        c = QColor()
        c.setHsvF(self._hue / 360.0, self._sat, self._val)
        c.setAlpha(self._alpha)
        return c

    def setColor(self, color: QColor) -> None:
        h, s, v, a = color.getHsvF()
        self._hue   = max(0.0, h * 360.0) if h >= 0 else self._hue
        self._sat   = max(0.0, min(1.0, s))
        self._val   = max(0.0, min(1.0, v))
        self._alpha = color.alpha()
        self.update()

    def setVal(self, val: float) -> None:
        """Called by the Brightness slider (0.0–1.0)."""
        self._val = max(0.0, min(1.0, val))
        self.update()
        self.colorChanged.emit(self.color())

    def setAlpha(self, alpha: int) -> None:
        """Called by the Alpha slider (0–255)."""
        self._alpha = max(0, min(255, alpha))
        self.update()
        self.colorChanged.emit(self.color())

    # ------------------------------------------------------------------
    # Geometry helpers
    # ------------------------------------------------------------------

    def _cx(self): return self.width() / 2
    def _cy(self): return self.height() / 2
    def _radius(self): return min(self.width(), self.height()) / 2 - 6

    def _point_to_hs(self, px, py):
        """Convert pixel click to hue (degrees) and saturation (0–1).

        IMPORTANT:
        The wheel rendering uses a +90° hue rotation so that red sits at the top.
        Mouse interpretation must use the exact same mapping.
        """
        cx, cy = self._cx(), self._cy()
        dx, dy = px - cx, py - cy
        hue = (math.degrees(math.atan2(dy, dx)) + 360 + 90) % 360
        sat = min(1.0, math.sqrt(dx * dx + dy * dy) / self._radius())
        return hue, sat

    # ------------------------------------------------------------------
    # Painting
    # ------------------------------------------------------------------

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        cx, cy = self._cx(), self._cy()
        R = self._radius()
        diameter = int(R * 2)

        img = QImage(diameter, diameter, QImage.Format_ARGB32)
        img.fill(Qt.transparent)

        # Build the disc pixel by pixel.
        # Hue = angle (+90° rotation so red is at the top)
        # Saturation = distance from center
        # Brightness = current brightness slider value
        for py in range(diameter):
            for px in range(diameter):
                dx = px - R
                dy = py - R
                dist = math.sqrt(dx * dx + dy * dy)

                if dist <= R:
                    hue = (math.degrees(math.atan2(dy, dx)) + 360 + 90) % 360
                    sat = dist / R

                    color = QColor()
                    color.setHsvF(hue / 360.0, sat, self._val)
                    img.setPixelColor(px, py, color)

        painter.drawImage(int(cx - R), int(cy - R), img)

        # Draw the selector dot.
        # Reverse the +90° paint rotation so the dot lands on the visible color.
        display_angle = math.radians(self._hue - 90)
        dot_x = cx + self._sat * R * math.cos(display_angle)
        dot_y = cy + self._sat * R * math.sin(display_angle)

        painter.setPen(QPen(Qt.white, 2))
        painter.setBrush(Qt.transparent)
        painter.drawEllipse(QPointF(dot_x, dot_y), 8, 8)

        painter.setPen(QPen(Qt.black, 1))
        painter.drawEllipse(QPointF(dot_x, dot_y), 10, 10)

        painter.end()

    # ------------------------------------------------------------------
    # Mouse interaction
    # ------------------------------------------------------------------

    def mousePressEvent(self, event):
        cx, cy = self._cx(), self._cy()
        dx = event.position().x() - cx
        dy = event.position().y() - cy
        if math.sqrt(dx * dx + dy * dy) <= self._radius():
            self._dragging = True
            self._update_from_mouse(event.position().x(), event.position().y())

    def mouseMoveEvent(self, event):
        if self._dragging:
            self._update_from_mouse(event.position().x(), event.position().y())

    def mouseReleaseEvent(self, event):
        self._dragging = False

    def _update_from_mouse(self, mx, my):
        self._hue, self._sat = self._point_to_hs(mx, my)
        self.update()
        self.colorChanged.emit(self.color())


# --------------------------------------------------------------------------------------

class ColorWheelDialog(QDialog):
    """Accessible color picker: round HSV disc + sliders for H, S, B, Alpha."""

    _FONT_PT   = 20
    _LABEL_PT  = 18
    _SLIDER_H  = 36

    def __init__(self, initial_color: QColor = None, parent=None, title: str = "Choose Color"):
        super().__init__(parent)
        self.setWindowTitle(title)
        self._color    = initial_color if initial_color and initial_color.isValid() else QColor("#FF0000")
        self._accepted = False
        self._building = False   # guard against feedback loops during _refresh
        self._build_ui()

    def _build_ui(self):
        self._building = True
        layout = QVBoxLayout(self)
        layout.setSpacing(14)
        layout.setContentsMargins(18, 18, 18, 18)

        # ── Row 1: wheel on left, preview + RGB on right ──
        top_row = QHBoxLayout()
        top_row.setSpacing(18)

        self.wheel = ColorWheelWidget()
        self.wheel.setColor(self._color)
        self.wheel.colorChanged.connect(self._on_wheel_changed)
        top_row.addWidget(self.wheel)

        right_col = QVBoxLayout()
        right_col.setSpacing(10)

        self.preview = QLabel()
        self.preview.setFixedSize(130, 130)
        self.preview.setStyleSheet(
            f"background-color: {self._color.name()}; "
            f"border: 3px solid white; border-radius: 8px;"
        )
        right_col.addWidget(self.preview)

        font_bold = QFont("Arial", self._LABEL_PT, QFont.Bold)
        self.r_label = QLabel()
        self.g_label = QLabel()
        self.b_label = QLabel()
        self.a_label = QLabel()
        for lbl in (self.r_label, self.g_label, self.b_label, self.a_label):
            lbl.setFont(font_bold)
            right_col.addWidget(lbl)

        right_col.addStretch()
        top_row.addLayout(right_col)
        layout.addLayout(top_row)

        # ── Sliders: Hue, Saturation, Brightness, Alpha ──
        slider_grid = QGridLayout()
        slider_grid.setSpacing(8)

        labels = ["Hue", "Saturation", "Brightness", "Alpha"]
        ranges = [(0, 360), (0, 100), (0, 100), (0, 255)]
        self._sliders = {}

        for row, (name, (lo, hi)) in enumerate(zip(labels, ranges)):
            lbl = QLabel(f"{name}:")
            lbl.setFont(QFont("Arial", self._LABEL_PT, QFont.Bold))
            lbl.setMinimumWidth(110)

            sl = QSlider(Qt.Horizontal)
            sl.setRange(lo, hi)
            sl.setMinimumHeight(self._SLIDER_H)
            sl.valueChanged.connect(self._on_slider_changed)

            val_lbl = QLabel()
            val_lbl.setFont(QFont("Arial", self._LABEL_PT))
            val_lbl.setMinimumWidth(46)
            val_lbl.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

            self._sliders[name] = (sl, val_lbl)
            slider_grid.addWidget(lbl,     row, 0)
            slider_grid.addWidget(sl,      row, 1)
            slider_grid.addWidget(val_lbl, row, 2)

        layout.addLayout(slider_grid)

        # ── Hex input + Copy button ──
        hex_row = QHBoxLayout()
        hex_lbl = QLabel("Hex:")
        hex_lbl.setFont(QFont("Arial", self._FONT_PT, QFont.Bold))

        self.hex_input = QLineEdit()
        self.hex_input.setFont(QFont("Arial", self._FONT_PT, QFont.Bold))
        self.hex_input.setMaxLength(9)   # #RRGGBBAA
        self.hex_input.setPlaceholderText("#RRGGBB")
        self.hex_input.setMinimumHeight(44)
        self.hex_input.editingFinished.connect(self._on_hex_entered)

        btn_copy = QPushButton("Copy")
        btn_copy.setFont(QFont("Arial", self._FONT_PT, QFont.Bold))
        btn_copy.setMinimumHeight(44)
        btn_copy.clicked.connect(self._on_copy_hex)

        hex_row.addWidget(hex_lbl)
        hex_row.addWidget(self.hex_input)
        hex_row.addWidget(btn_copy)
        layout.addLayout(hex_row)

        # ── OK / Cancel ──
        btn_row = QHBoxLayout()
        btn_ok = QPushButton("OK")
        btn_ok.setFont(QFont("Arial", self._FONT_PT, QFont.Bold))
        btn_ok.setMinimumHeight(48)
        btn_ok.clicked.connect(self._on_ok)

        btn_cancel = QPushButton("Cancel")
        btn_cancel.setFont(QFont("Arial", self._FONT_PT, QFont.Bold))
        btn_cancel.setMinimumHeight(48)
        btn_cancel.clicked.connect(self.reject)

        btn_row.addWidget(btn_ok)
        btn_row.addWidget(btn_cancel)
        layout.addLayout(btn_row)

        self.resize(540, 620)
        self._building = False
        self._refresh_all()

    # ------------------------------------------------------------------
    # Sync helpers
    # ------------------------------------------------------------------

    def _refresh_all(self):
        """Push current self._color out to every widget."""
        if self._building:
            return
        self._building = True

        c = self._color
        h, s, v, a = c.getHsvF()
        if h < 0:
            h = 0.0

        # Sliders
        self._sliders["Hue"][0].setValue(int(h * 360))
        self._sliders["Saturation"][0].setValue(int(s * 100))
        self._sliders["Brightness"][0].setValue(int(v * 100))
        self._sliders["Alpha"][0].setValue(a if isinstance(a, int) else int(a * 255))

        # Slider value labels
        self._sliders["Hue"][1].setText(str(int(h * 360)))
        self._sliders["Saturation"][1].setText(f"{int(s * 100)}%")
        self._sliders["Brightness"][1].setText(f"{int(v * 100)}%")
        alpha_int = c.alpha()
        self._sliders["Alpha"][1].setText(str(alpha_int))

        # RGB + Alpha readout labels
        self.r_label.setText(f"R:  {c.red()}")
        self.g_label.setText(f"G:  {c.green()}")
        self.b_label.setText(f"B:  {c.blue()}")
        self.a_label.setText(f"A:  {alpha_int}")

        # Preview swatch — show alpha via rgba()
        self.preview.setStyleSheet(
            f"background-color: rgba({c.red()},{c.green()},{c.blue()},{alpha_int}); "
            f"border: 3px solid white; border-radius: 8px;"
        )

        # Hex field (include alpha if not fully opaque)
        if alpha_int < 255:
            self.hex_input.setText(
                f"#{c.red():02X}{c.green():02X}{c.blue():02X}{alpha_int:02X}"
            )
        else:
            self.hex_input.setText(c.name().upper())

        # Wheel
        self.wheel.setColor(c)

        self._building = False

    # ------------------------------------------------------------------
    # Signal handlers
    # ------------------------------------------------------------------

    def _on_wheel_changed(self, color: QColor):
        if self._building:
            return
        # Preserve alpha when wheel changes hue/sat
        color.setAlpha(self._color.alpha())
        self._color = color
        self._refresh_all()

    def _on_slider_changed(self):
        if self._building:
            return
        h = self._sliders["Hue"][0].value() / 360.0
        s = self._sliders["Saturation"][0].value() / 100.0
        v = self._sliders["Brightness"][0].value() / 100.0
        a = self._sliders["Alpha"][0].value()
        c = QColor()
        c.setHsvF(h, s, v)
        c.setAlpha(a)
        self._color = c
        self._refresh_all()

    def _on_hex_entered(self):
        text = self.hex_input.text().strip()

        # First try as a named color (e.g. "cornflowerblue", "tomato")
        c = QColor(text)

        # If that didn't work, try adding # and treating as hex
        if not c.isValid():
            c = QColor("#" + text)

        if c.isValid():
            self._color = c
            hex_value = c.name().upper()

            # If user typed a name (not a hex), show: "cornflowerblue → #6495ED"
            if not text.startswith("#"):
                self.hex_input.setText(f"{text} → {hex_value}")
            else:
                self.hex_input.setText(hex_value)

            self._refresh_all()

    def _on_copy_hex(self):
        QApplication.clipboard().setText(self.hex_input.text())

    def _on_ok(self):
        self._accepted = True
        self.accept()

    # ------------------------------------------------------------------
    # Result accessors
    # ------------------------------------------------------------------

    def selectedColor(self) -> QColor:
        return self._color

    def result_ok(self) -> bool:
        return self._accepted


# --------------------------------------------------------------------------------------

def pick_color(initial: QColor = None, parent=None, title: str = "Choose Color") -> QColor:
    """Drop-in replacement for QColorDialog.getColor().
    Returns the chosen QColor (with alpha), or an invalid QColor if cancelled.
    """
    dlg = ColorWheelDialog(initial, parent, title)
    if dlg.exec() == QDialog.Accepted and dlg.result_ok():
        return dlg.selectedColor()
    return QColor()  # invalid = cancelled


# --------------------------------------------------------------------------------------
# Palette Builder / Editor Dialog
# --------------------------------------------------------------------------------------

class PaletteEditorDialog(QDialog):
    """Dialog for creating and editing palette colors.
    Features: live gradient preview, sliders for color positions, and undo history.
    Designed with larger fonts for accessibility.
    """

    _TITLE_PT = 22
    _LABEL_PT = 18
    _BUTTON_PT = 16

    def __init__(self, palette: Palette | None = None, parent: QWidget | None = None, mode: str = "edit"):
        super().__init__(parent)
        self._palette = palette
        self._mode = mode
        self._save_mode = "update"
        self._history: list[list[tuple[str, float]]] = []

        if mode == "edit" and palette:
            self.setWindowTitle(f"Palette Builder / Editor - {palette.name}")
            colors = palette.colors
            positions = get_palette_positions(palette)
        else:
            self.setWindowTitle("Palette Builder / Editor - Create New")
            colors = ["#FF0000", "#FFFF00", "#00FF00"]
            positions = [0.0, 0.5, 1.0]

        self._build_ui(colors, positions)
        self._push_history()

    def _build_ui(self, colors: list[str], positions: list[float]) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(10)

        if self._mode == "create":
            mode_label = QLabel("CREATE NEW PALETTE")
            mode_label.setFont(QFont(FONT_FAMILY[0], self._TITLE_PT, QFont.Bold))
            mode_label.setStyleSheet("color: #9D4EDD;")
            layout.addWidget(mode_label)

            preset_row = QHBoxLayout()
            preset_lbl = QLabel("Start with:")
            preset_lbl.setFont(QFont(FONT_FAMILY[0], self._LABEL_PT, FONT_WEIGHT))
            self.preset_combo = QComboBox()
            self.preset_combo.setFont(QFont(FONT_FAMILY[0], self._LABEL_PT, FONT_WEIGHT))
            self.preset_combo.addItems(["3 colors", "5 colors", "7 colors"])
            self.preset_combo.currentTextChanged.connect(self._on_preset_changed)
            preset_row.addWidget(preset_lbl)
            preset_row.addWidget(self.preset_combo)
            preset_row.addStretch()
            layout.addLayout(preset_row)
        else:
            title = QLabel(f"Editing: {self._palette.name}")
            title.setFont(QFont(FONT_FAMILY[0], self._TITLE_PT, QFont.Bold))
            layout.addWidget(title)

        # Live gradient preview bar
        self.preview_bar = QLabel()
        self.preview_bar.setFixedHeight(48)
        self.preview_bar.setToolTip("Live preview - updates as you adjust sliders or colors")
        layout.addWidget(self.preview_bar)

        # Color rows list
        self.list_widget = QListWidget()
        self.list_widget.setSpacing(2)
        layout.addWidget(self.list_widget, 1)

        for i, c in enumerate(colors):
            pos = positions[i] if i < len(positions) else (i / (len(colors) - 1) if len(colors) > 1 else 0.0)
            self._add_row(c, pos * 100.0)

        # Add Color + Undo row
        action_row = QHBoxLayout()

        btn_add = QPushButton("Add Color...")
        btn_add.setFont(QFont(FONT_FAMILY[0], self._BUTTON_PT, FONT_WEIGHT))
        btn_add.setMinimumHeight(38)
        btn_add.setToolTip("Add a new color to the palette")
        btn_add.clicked.connect(self._on_add_color)

        self.undo_btn = QPushButton("<- Undo")
        self.undo_btn.setFont(QFont(FONT_FAMILY[0], self._BUTTON_PT, FONT_WEIGHT))
        self.undo_btn.setMinimumHeight(38)
        self.undo_btn.setToolTip("Undo last change")
        self.undo_btn.setEnabled(False)
        self.undo_btn.clicked.connect(self._on_undo)

        action_row.addWidget(btn_add)
        action_row.addWidget(self.undo_btn)
        action_row.addStretch(1)
        layout.addLayout(action_row)

        # Save / Cancel buttons
        button_row = QHBoxLayout()

        if self._mode == "edit":
            self.update_btn = QPushButton("Update Existing")
            self.update_btn.setFont(QFont(FONT_FAMILY[0], self._BUTTON_PT, FONT_WEIGHT))
            self.update_btn.setMinimumHeight(38)
            self.update_btn.clicked.connect(self._on_update)

            self.save_new_btn = QPushButton("Save as New...")
            self.save_new_btn.setFont(QFont(FONT_FAMILY[0], self._BUTTON_PT, FONT_WEIGHT))
            self.save_new_btn.setMinimumHeight(38)
            self.save_new_btn.clicked.connect(self._on_save_new)

            cancel_btn = QPushButton("Cancel")
            cancel_btn.setFont(QFont(FONT_FAMILY[0], self._BUTTON_PT, FONT_WEIGHT))
            cancel_btn.setMinimumHeight(38)
            cancel_btn.clicked.connect(self.reject)

            button_row.addWidget(self.update_btn)
            button_row.addWidget(self.save_new_btn)
            button_row.addStretch()
            button_row.addWidget(cancel_btn)
        else:
            self.save_new_btn = QPushButton("Save as New...")
            self.save_new_btn.setFont(QFont(FONT_FAMILY[0], self._BUTTON_PT, FONT_WEIGHT))
            self.save_new_btn.setMinimumHeight(38)
            self.save_new_btn.clicked.connect(self._on_save_new)

            cancel_btn = QPushButton("Cancel")
            cancel_btn.setFont(QFont(FONT_FAMILY[0], self._BUTTON_PT, FONT_WEIGHT))
            cancel_btn.setMinimumHeight(38)
            cancel_btn.clicked.connect(self.reject)

            button_row.addWidget(self.save_new_btn)
            button_row.addStretch()
            button_row.addWidget(cancel_btn)

        layout.addLayout(button_row)
        self.resize(700, 580)
        self._refresh_preview()

    def _refresh_preview(self) -> None:
        colors = self.get_colors()
        positions = self.get_positions()
        w = self.preview_bar.width() if self.preview_bar.width() > 10 else 660
        h = self.preview_bar.height() if self.preview_bar.height() > 10 else 48
        if len(colors) < 2:
            colors = colors * 2
            positions = [0.0, 1.0]
        stops = list(zip(
            positions if positions else [i / (len(colors) - 1) for i in range(len(colors))],
            [QColor(c) for c in colors]
        ))
        stops.sort(key=lambda s: s[0])
        pixmap = QPixmap(w, h)
        painter = QPainter(pixmap)
        gradient = QLinearGradient(0, 0, w, 0)
        for pos, color in stops:
            gradient.setColorAt(pos, color)
        painter.fillRect(0, 0, w, h, gradient)
        painter.end()
        self.preview_bar.setPixmap(pixmap)

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        self._refresh_preview()

    def _push_history(self) -> None:
        snapshot = list(zip(self.get_colors(), self.get_positions()))
        self._history.append(snapshot)
        if hasattr(self, "undo_btn"):
            self.undo_btn.setEnabled(len(self._history) > 1)

    def _on_undo(self) -> None:
        if len(self._history) <= 1:
            return
        self._history.pop()
        snapshot = self._history[-1]
        colors = [s[0] for s in snapshot]
        positions = [s[1] for s in snapshot]
        self.list_widget.clear()
        for c, p in zip(colors, positions):
            self._add_row(c, p * 100.0)
        self._refresh_preview()
        self.undo_btn.setEnabled(len(self._history) > 1)

    def _add_row(self, hex_color: str, position_percent: float = 0.0) -> None:
        item = QListWidgetItem(self.list_widget)
        row_widget = QWidget()
        row_layout = QHBoxLayout(row_widget)
        row_layout.setContentsMargins(6, 4, 6, 4)
        row_layout.setSpacing(8)

        swatch = QLabel()
        swatch.setFixedSize(36, 36)
        swatch.setStyleSheet(
            f"background-color: {hex_color}; border: 2px solid rgba(255,255,255,0.9); border-radius: 4px;"
        )
        swatch.setToolTip(hex_color)

        hex_label = QLabel(hex_color)
        hex_label.setFixedWidth(105)
        hex_label.setAlignment(Qt.AlignCenter)
        hex_label.setFont(QFont(FONT_FAMILY[0], self._LABEL_PT, FONT_WEIGHT))

        slider = QSlider(Qt.Horizontal)
        slider.setRange(0, 100)
        slider.setValue(int(position_percent))
        slider.setMaximumWidth(300)
        slider.setToolTip("Drag to move this color's position along the gradient")

        pos_label = QLabel(f"{int(position_percent)}%")
        pos_label.setFixedWidth(70)
        pos_label.setAlignment(Qt.AlignCenter)
        pos_label.setFont(QFont(FONT_FAMILY[0], self._LABEL_PT, FONT_WEIGHT))

        btn_edit = QPushButton("Edit")
        btn_edit.setFont(QFont(FONT_FAMILY[0], self._BUTTON_PT, FONT_WEIGHT))
        btn_edit.setFixedWidth(70)
        btn_edit.setMinimumHeight(34)
        btn_edit.setToolTip("Choose a new color")

        btn_delete = QPushButton("Del")
        btn_delete.setFont(QFont(FONT_FAMILY[0], self._BUTTON_PT, FONT_WEIGHT))
        btn_delete.setFixedWidth(60)
        btn_delete.setMinimumHeight(34)
        btn_delete.setToolTip("Remove this color from the palette")

        row_layout.addWidget(swatch)
        row_layout.addWidget(hex_label)
        row_layout.addWidget(slider)
        row_layout.addWidget(pos_label)
        row_layout.addWidget(btn_edit)
        row_layout.addWidget(btn_delete)

        item.setSizeHint(row_widget.sizeHint())
        self.list_widget.setItemWidget(item, row_widget)

        def on_slider_moved(value: int) -> None:
            pos_label.setText(f"{value}%")
            self._refresh_preview()

        def on_slider_released() -> None:
            self._push_history()

        slider.valueChanged.connect(on_slider_moved)
        slider.sliderReleased.connect(on_slider_released)

        def on_edit() -> None:
            if (color := pick_color(QColor(hex_label.text()), self, "Choose Color")).isValid():
                new_hex = color.name().upper()
                hex_label.setText(new_hex)
                swatch.setStyleSheet(
                    f"background-color: {new_hex}; border: 2px solid rgba(255,255,255,0.9); border-radius: 4px;"
                )
                swatch.setToolTip(new_hex)
                self._refresh_preview()
                self._push_history()

        def on_delete() -> None:
            self._push_history()
            self.list_widget.takeItem(self.list_widget.row(item))
            self._refresh_preview()

        btn_edit.clicked.connect(on_edit)
        btn_delete.clicked.connect(on_delete)

    def _on_add_color(self) -> None:
        if (color := pick_color(QColor("#FFFFFF"), self, "Choose Color")).isValid():
            self._add_row(color.name().upper(), 100.0)
            self._refresh_preview()
            self._push_history()

    def _on_preset_changed(self, text: str) -> None:
        num_colors = int(text.split()[0])
        preset_colors = [
            "#FF0000", "#FF7F00", "#FFFF00", "#00FF00",
            "#0000FF", "#4B0082", "#8B00FF"
        ]
        self.list_widget.clear()
        for i in range(num_colors):
            color = preset_colors[i % len(preset_colors)]
            position = (i / (num_colors - 1) * 100.0) if num_colors > 1 else 0.0
            self._add_row(color, position)
        self._refresh_preview()
        self._push_history()

    def _on_update(self) -> None:
        self._save_mode = "update"
        self.accept()

    def _on_save_new(self) -> None:
        default_name = self._palette.name if self._palette else "New Palette"
        name, ok = QInputDialog.getText(
            self, "Save as New Palette", "Palette name:", text=default_name
        )
        if not ok or not name.strip():
            return
        self.new_palette_name = name.strip()

        categories = [
            "LGBTQ+", "Disability", "Abstract / Cool", "Abstract / Vibrant",
            "Animals / Cool", "Art / Bold", "Autumn", "Floral / Desert",
            "Floral / Spring", "Garden / Pastel", "Holiday", "Hippie",
            "Landscape / Desert", "Monochrome / Bold", "Nature", "Primary Colors",
            "Sports / Club Team", "Sports / National Team", "Typography / Minimal",
            "Custom"
        ]
        category, ok = QInputDialog.getItem(
            self, "Select Category", "Category:", categories, 0, False
        )
        if not ok:
            return

        if category == "Custom":
            category, ok = QInputDialog.getText(self, "Custom Category", "Enter category name:")
            if not ok or not category.strip():
                return
            category = category.strip()

        self.new_palette_category = category
        self._save_mode = "new"
        self.accept()

    def get_colors(self) -> list[str]:
        colors: list[str] = []
        for i in range(self.list_widget.count()):
            if (item := self.list_widget.item(i)) and (row_widget := self.list_widget.itemWidget(item)):
                for lbl in row_widget.findChildren(QLabel):
                    t = lbl.text().strip()
                    if t.startswith("#") and len(t) in (7, 4):
                        colors.append(t.upper())
                        break
        if not colors:
            return ["#000000", "#FFFFFF"]
        if len(colors) == 1:
            return [colors[0], colors[0]]
        return colors

    def get_positions(self) -> list[float]:
        positions: list[float] = []
        for i in range(self.list_widget.count()):
            if (item := self.list_widget.item(i)) and (row_widget := self.list_widget.itemWidget(item)):
                sliders = row_widget.findChildren(QSlider)
                if sliders:
                    positions.append(sliders[0].value() / 100.0)
        if len(positions) == len(self.get_colors()):
            return positions
        total = self.list_widget.count()
        return [i / (total - 1) if total > 1 else 0.0 for i in range(total)]

    def get_save_mode(self) -> str:
        return self._save_mode


# --------------------------------------------------------------------------------------
# Theme Dialog
# --------------------------------------------------------------------------------------

class ThemeDialog(QDialog):
    """Dialog for customizing theme colors."""

    def __init__(self, parent) -> None:
        super().__init__(parent)
        self.main_window = parent
        self.setWindowTitle("Customize Theme")
        self.setMinimumWidth(450)

        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        button_font = QFont(FONT_FAMILY[0], BUTTON_FONT_PT, FONT_WEIGHT)

        # User loads his own palettes into HFA
        self.load_diy_palettes_button = QPushButton("Load DIY Palette")
        self.load_diy_palettes_button.setFont(button_font)
        self.load_diy_palettes_button.setMinimumHeight(45)
        self.load_diy_palettes_button.clicked.connect(self.main_window.on_load_diy_palettes)
        layout.addWidget(self.load_diy_palettes_button)

        # Background color button
        self.bg_btn = QPushButton("Change Background Color")
        self.bg_btn.setFont(button_font)
        self.bg_btn.setMinimumHeight(45)
        self.bg_btn.clicked.connect(self.main_window.on_change_bg_color)
        layout.addWidget(self.bg_btn)

        # Font color button
        self.font_btn = QPushButton("Change Font Color")
        self.font_btn.setFont(button_font)
        self.font_btn.setMinimumHeight(45)
        self.font_btn.clicked.connect(self.main_window.on_change_font_color)
        layout.addWidget(self.font_btn)

        # Button background color
        self.btn_bg_btn = QPushButton("Change Button Background Color")
        self.btn_bg_btn.setFont(button_font)
        self.btn_bg_btn.setMinimumHeight(45)
        self.btn_bg_btn.clicked.connect(self.main_window.on_change_button_bg)
        layout.addWidget(self.btn_bg_btn)

        # Button text color
        self.btn_text_btn = QPushButton("Change Button Text Color")
        self.btn_text_btn.setFont(button_font)
        self.btn_text_btn.setMinimumHeight(45)
        self.btn_text_btn.clicked.connect(self.main_window.on_change_button_text)
        layout.addWidget(self.btn_text_btn)

        # Separator
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setStyleSheet("color: #555;")
        layout.addWidget(separator)

        # Reset to defaults
        self.reset_btn = QPushButton("- Reset to Defaults")
        self.reset_btn.setFont(button_font)
        self.reset_btn.setMinimumHeight(45)
        self.reset_btn.clicked.connect(self.main_window.on_reset_theme)
        layout.addWidget(self.reset_btn)

        # Close button
        self.close_btn = QPushButton("Close")
        self.close_btn.setFont(button_font)
        self.close_btn.setMinimumHeight(45)
        self.close_btn.clicked.connect(self.accept)
        layout.addWidget(self.close_btn)


# --------------------------------------------------------------------------------------
# Main Window
# --------------------------------------------------------------------------------------

class MainWindow(QMainWindow):
    """Main application window."""

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("HUEMANITY for ALL by 'Troyski' - Dedicated to the beautiful people of our LGBTQ+ Community")

        # Load palettes
        names, name_to_palette = palette_names_and_map()
        self.all_palette_names: list[str] = list(names)
        self.name_to_palette: dict[str, Palette] = dict(name_to_palette)
        self.name_to_pack: dict[str, str] = {n: "Master Palettes" for n in self.all_palette_names}

        # State
        self.favorite_palettes: set[str] = set()
        self.favorites_only: bool = False
        self.category_filter: str = "All"
        self.search_text: str = ""
        self.current_img: Image.Image | None = None
        self.current_settings: GradientSettings | None = None

        # Auto-preview timers (hover delay for accessibility - prevents seizures)
        self.hover_timer = QTimer(self)
        self.hover_timer.setSingleShot(True)
        self.hover_timer.timeout.connect(self._on_hover_timer_fired)
        self.pending_hover_palette: str = ""
        
        # Size change timer (delay after typing stops)
        self.size_timer = QTimer(self)
        self.size_timer.setSingleShot(True)
        self.size_timer.timeout.connect(self._on_size_timer_fired)

        # Theme colors (with defaults)
        self.bg_color: str = DARK_CHARCOAL
        self.font_color: str = BUTTON_TEXT
        self.button_bg_color: str = BUTTON_BG
        self.button_text_color: str = BUTTON_TEXT

        # Settings file path
        self.settings_path = get_app_data_dir() / "hfa_settings.json"

        # Load saved favorites and theme
        self._load_favorites()
        self._load_theme_settings()

        # Build UI
        self._build_ui()
        self._apply_styles()
        self._apply_window_sizing()

        # Initialize
        select_name = DEFAULT_PALETTE_NAME if DEFAULT_PALETTE_NAME in self.all_palette_names else \
            (self.all_palette_names[0] if self.all_palette_names else "")
        self._rebuild_filters_and_apply(select_name=select_name)
        self._show_idle_image()

    def _apply_window_sizing(self) -> None:
        """Size and center window appropriately."""
        if not (app := QApplication.instance()) or not (screen := app.primaryScreen()):
            self.resize(900, 650)
            return

        geo = screen.availableGeometry()
        start_w, start_h = int(geo.width() * 0.65), int(geo.height() * 0.70)

        # FIXED: Larger minimum size to ensure left panel is usable
        self.setMinimumSize(900, 600)
        # FIXED: Removed setMaximumSize to allow window maximizing
        self.resize(max(900, start_w), max(600, start_h))

        frame = self.frameGeometry()
        frame.moveCenter(geo.center())
        self.move(frame.topLeft())

    def resizeEvent(self, event) -> None:
        """Handle window resize to dynamically scale preview image."""
        super().resizeEvent(event)

        # If we have a current image, re-scale it to FILL the preview_label area
        if self.current_img and self.current_settings:
            # Get new available size
            max_w = max(1, self.preview_label.width())
            max_h = max(1, self.preview_label.height())

            # Calculate scale to FILL (may crop, but no black bars!)
            scale_w = max_w / self.current_settings.width
            scale_h = max_h / self.current_settings.height
            scale = max(scale_w, scale_h)  # Use MAX to fill entire space

            # Resize the stored full-size image
            new_w = int(self.current_settings.width * scale)
            new_h = int(self.current_settings.height * scale)
            disp = self.current_img.resize((new_w, new_h), Image.Resampling.LANCZOS)

            # Update the preview label
            self.preview_label.setPixmap(pil_to_qpixmap(disp))

    def _build_ui(self) -> None:
        """Build the user interface."""
        central = QWidget(self)
        self.setCentralWidget(central)

        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(8, 6, 8, 8)
        main_layout.setSpacing(6)

        # Banner
        banner_label = QLabel()
        banner_label.setScaledContents(True)
        banner_label.setPixmap(pil_to_qpixmap(build_static_banner(710, 50)))
        main_layout.addWidget(banner_label)

        splitter = QSplitter(Qt.Horizontal)

        # THICK VIBRANT PURPLE SPLITTER BAR (turns yellow when grabbed!)
        splitter.setStyleSheet("""
            QSplitter::handle {
                background-color: #C951D8;  /* Vibrant fuchsia/magenta */
                width: 12px;  /* THICK splitter bar */
            }
            QSplitter::handle:hover {
                background-color: #E06BF0;  /* Lighter purple on hover */
            }
            QSplitter::handle:pressed {
                background-color: #FFD700;  /* BRIGHT YELLOW when clicking/dragging! */
            }
        """)
        splitter.setHandleWidth(12)  # Set handle width explicitly

        main_layout.addWidget(splitter, 1)

        # Left panel (controls)
        self._build_left_panel(splitter)

        # Right panel (preview)
        self._build_right_panel(splitter)

        # FIXED: Allow splitter to be dragged, sizes are proportional
        splitter.setStretchFactor(0, 1)  # Left panel
        splitter.setStretchFactor(1, 2)  # Right panel gets more space
        # Use proportional sizes that work at any window size
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 2)

    def _build_left_panel(self, splitter: QSplitter) -> None:
        """Build left control panel."""
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 8, 0)
        left_layout.setSpacing(10)

        label_font = QFont(FONT_FAMILY[0], LABEL_FONT_PT, FONT_WEIGHT)
        value_font = QFont(FONT_FAMILY[0], VALUE_FONT_PT, FONT_WEIGHT)

        # Filters row
        filters_row = QHBoxLayout()
        filters_row.setSpacing(8)

        category_label = QLabel("Category:")
        category_label.setFont(label_font)
        self.category_combo = QComboBox()
        self.category_combo.setFont(value_font)
        self.category_combo.setMinimumWidth(280)  # Wider to show full palette category names
        self.category_combo.currentTextChanged.connect(self.on_category_changed)

        self.favorites_only_button = QPushButton("-")
        self.favorites_only_button.setCheckable(True)
        self.favorites_only_button.setToolTip("Show favorites only")
        self.favorites_only_button.setFixedSize(36, 32)
        self.favorites_only_button.toggled.connect(self.on_favorites_only_toggled)

        filters_row.addWidget(category_label)
        filters_row.addWidget(self.category_combo, 1)
        filters_row.addWidget(self.favorites_only_button)
        left_layout.addLayout(filters_row)

        # Search
        self.search_edit = QLineEdit()
        self.search_edit.setFont(value_font)
        self.search_edit.setPlaceholderText("Search palettes (name or category)")
        self.search_edit.textChanged.connect(self.on_search_changed)
        left_layout.addWidget(self.search_edit)

        left_layout.addSpacing(6)

        # Palette selection
        palette_label = QLabel("Palette:")
        palette_label.setFont(label_font)
        left_layout.addWidget(palette_label)

        palette_row = QHBoxLayout()
        palette_row.setSpacing(8)

        self.palette_combo = QComboBox()
        self.palette_combo.setFont(value_font)
        self.palette_combo.currentTextChanged.connect(self._on_palette_selected)
        self.palette_combo.highlighted.connect(self._on_palette_hover)

        palette_row.addWidget(self.palette_combo, 1)
        left_layout.addLayout(palette_row)

        # Direction
        dir_label = QLabel("Direction:")
        dir_label.setFont(label_font)
        left_layout.addWidget(dir_label)

        self.direction_combo = QComboBox()
        self.direction_combo.setFont(value_font)
        self.direction_combo.addItems([
            "Conical (Sweep)",
            "Diagonal (TL to BR)",
            "Diamond",
            "Horizontal",
            "Liquid / Fluid Blur",
            "Radial (Center)",
            "Spiral",
            "Vertical"
        ])
        self.direction_combo.setCurrentText("Radial (Center)")
        self.direction_combo.currentTextChanged.connect(self._on_direction_changed)
        left_layout.addWidget(self.direction_combo)

        # Size controls
        size_row = QHBoxLayout()
        size_row.setSpacing(8)

        w_label = QLabel("W:")
        w_label.setFont(QFont(FONT_FAMILY[0], BUTTON_FONT_PT, FONT_WEIGHT))  # LARGER for visibility
        self.width_spin = QLineEdit()
        self.width_spin.setText("1200")
        self.width_spin.setMaximumWidth(120)
        self.width_spin.setFont(QFont(FONT_FAMILY[0], BUTTON_FONT_PT, FONT_WEIGHT))  # LARGER for visibility
        self.width_spin.setAlignment(Qt.AlignCenter)
        self.width_spin.textChanged.connect(self._on_size_changed)

        h_label = QLabel("H:")
        h_label.setFont(QFont(FONT_FAMILY[0], BUTTON_FONT_PT, FONT_WEIGHT))  # LARGER for visibility
        self.height_spin = QLineEdit()
        self.height_spin.setText("675")
        self.height_spin.setMaximumWidth(120)
        self.height_spin.setFont(QFont(FONT_FAMILY[0], BUTTON_FONT_PT, FONT_WEIGHT))  # LARGER for visibility
        self.height_spin.setAlignment(Qt.AlignCenter)
        self.height_spin.textChanged.connect(self._on_size_changed)

        size_row.addWidget(w_label)
        size_row.addWidget(self.width_spin)
        size_row.addSpacing(10)
        size_row.addWidget(h_label)
        size_row.addWidget(self.height_spin)
        size_row.addStretch(1)
        left_layout.addLayout(size_row)

        # Buttons
        button_font = QFont(FONT_FAMILY[0], BUTTON_FONT_PT, FONT_WEIGHT)

        self.generate_button = QPushButton("Generate Preview")
        self.random_button = QPushButton("Random Gradient")
        self.save_button = QPushButton("Save PNG")
        self.theme_button = QPushButton("Customize Theme")

        for btn in (self.generate_button, self.random_button, self.save_button,
                    self.theme_button):
            btn.setMinimumHeight(40)
            btn.setMaximumWidth(320)  # FIXED: Limit button width for better appearance
            btn.setFont(button_font)

        # FIXED: Connect ALL buttons to their handlers
        self.generate_button.clicked.connect(self.on_generate_clicked)
        self.random_button.clicked.connect(self.on_random_clicked)
        self.save_button.clicked.connect(self.on_save_clicked)
        self.theme_button.clicked.connect(self.on_open_theme_dialog)

        left_layout.addWidget(self.generate_button)
        left_layout.addWidget(self.random_button)
        left_layout.addWidget(self.save_button)
        left_layout.addWidget(self.theme_button)
        left_layout.addStretch(1)

        # Wrap left panel in scroll area
        left_scroll = QScrollArea()
        left_scroll.setWidgetResizable(True)
        left_scroll.setFrameShape(QFrame.NoFrame)
        left_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        left_scroll.setStyleSheet("QScrollArea { border: none; }")
        left_scroll.setMinimumWidth(340)  # FIXED: Minimum width for left panel
        left_scroll.setMaximumWidth(600)  # FIXED: Maximum width so it doesn't dominate
        left_scroll.setWidget(left_widget)

        splitter.addWidget(left_scroll)

    def _build_right_panel(self, splitter: QSplitter) -> None:
        """Build right preview panel."""
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(8, 0, 0, 0)
        right_layout.setSpacing(6)

        self.preview_label = QLabel()
        self.preview_label.setAlignment(Qt.AlignCenter)  # Center instead of top
        self.preview_label.setMinimumSize(320, 220)
        self.preview_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.preview_label.setScaledContents(False)  # Don't auto-scale, we handle it manually
        self.preview_label.setObjectName("previewLabel")
        right_layout.addWidget(self.preview_label, 1)  # Stretch factor of 1

        self.random_button = QPushButton("🎲  Random Gradient")

        self.random_button.setObjectName("randomButton")
        self.random_button.setMinimumHeight(44)
        self.random_button.clicked.connect(self.on_random_clicked)
        random_layout = QHBoxLayout()
        random_layout.addStretch()
        random_layout.addWidget(self.random_button)
        random_layout.addStretch()
        right_layout.addLayout(random_layout)

        # Button row: Palette Builder + Favorites
        button_row_container = QWidget()
        button_row_layout = QHBoxLayout(button_row_container)
        button_row_layout.setContentsMargins(8, 4, 8, 10)
        button_row_layout.setSpacing(10)

        self.edit_palette_button = QPushButton("Palette Builder / Editor")
        self.edit_palette_button.setToolTip("Create new palettes or edit existing ones")
        self.edit_palette_button.setFont(QFont(FONT_FAMILY[0], 14, FONT_WEIGHT))
        self.edit_palette_button.setFixedHeight(40)
        self.edit_palette_button.clicked.connect(self.on_palette_builder_clicked)

        self.favorite_button = QPushButton("- Mark as Favorite")
        self.favorite_button.setToolTip("Toggle favorite for this palette")
        self.favorite_button.setFont(QFont(FONT_FAMILY[0], 14, FONT_WEIGHT))
        self.favorite_button.setFixedHeight(40)
        self.favorite_button.clicked.connect(self.on_toggle_favorite)

        button_row_layout.addWidget(self.edit_palette_button)
        button_row_layout.addWidget(self.favorite_button)
        button_row_layout.addStretch()

        right_layout.addWidget(button_row_container)

        # Palette strip
        strip_container = QWidget()
        strip_layout = QHBoxLayout(strip_container)
        l, t, r, b = PALETTE_STRIP_MARGINS
        strip_layout.setContentsMargins(l, t, r, b)
        strip_layout.setSpacing(10)

        swatch_host = QWidget()
        self.palette_strip_layout = QHBoxLayout(swatch_host)
        self.palette_strip_layout.setContentsMargins(0, 0, 0, 0)
        self.palette_strip_layout.setSpacing(PALETTE_TILE_SPACING)
        self.palette_strip_layout.setAlignment(Qt.AlignLeft | Qt.AlignTop)

        swatch_scroll = QScrollArea()
        swatch_scroll.setWidgetResizable(True)
        swatch_scroll.setFrameShape(QFrame.NoFrame)
        swatch_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        swatch_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        swatch_scroll.setWidget(swatch_host)
        swatch_scroll.setFixedHeight(PALETTE_STRIP_HEIGHT)

        strip_layout.addWidget(swatch_scroll, 1)

        right_layout.addWidget(strip_container)

        self.status_label = QLabel()
        self.status_label.setFont(QFont(FONT_FAMILY[0], LABEL_FONT_PT, FONT_WEIGHT))  # LARGER for visibility
        self.status_label.setObjectName("statusLabel")

        self.hex_codes_label = QLabel()
        self.hex_codes_label.setFont(QFont(FONT_FAMILY[0], LABEL_FONT_PT, FONT_WEIGHT))  # LARGER for visibility
        self.hex_codes_label.setObjectName("hexCodesLabel")

        tip_label = QLabel(f"Tip: Maximum supported gradient size is {MAX_GRADIENT_WIDTH}x{MAX_GRADIENT_HEIGHT}. Larger sizes auto-clamp.")
        tip_label.setFont(QFont(FONT_FAMILY[0], LABEL_FONT_PT, FONT_WEIGHT))  # LARGER for visibility
        tip_label.setStyleSheet("color: #CCCCCC;")
        tip_label.setWordWrap(True)

        right_layout.addWidget(self.status_label)
        right_layout.addWidget(self.hex_codes_label)
        right_layout.addWidget(tip_label)

        splitter.addWidget(right_widget)

    def _apply_styles(self) -> None:
        """Apply theme-based styles to the UI."""
        # Calculate hover and pressed colors from button bg
        button_hover = self._lighten_color(self.button_bg_color, 20)
        button_pressed = self._darken_color(self.button_bg_color, 20)

        self.setStyleSheet(
            f"""
            QMainWindow {{
                background-color: {self.bg_color};
            }}
            QWidget {{
                background-color: {self.bg_color};
                color: {self.font_color};
                font-weight: bold;
            }}
            #previewLabel {{
                background-color: #000000;
            }}

            QComboBox, QSpinBox, QLineEdit {{
                background-color: {self.button_bg_color};
                color: {self.button_text_color};
                border-radius: 4px;
                border: 1px solid #444444;
                padding: 2px 6px;
            }}

            /* Thicker selection indicator for dropdown items */
            QComboBox QAbstractItemView::item:selected {{
                background-color: {self.button_bg_color};
                border-left: 6px solid #C951D8;  /* Thick magenta/fuchsia stripe */
                padding-left: 4px;
            }}
            QComboBox QAbstractItemView::item:hover {{
                background-color: {button_hover};
                border-left: 6px solid #E06BF0;  /* Lighter magenta on hover */
                padding-left: 4px;
            }}

            QPushButton {{
                background-color: {self.button_bg_color};
                color: {self.button_text_color};
                width: 275px;
                border-radius: 6px;
                padding: 6px 10px;
            }}
            QPushButton:hover {{
                background-color: {button_hover};
            }}
            QPushButton:pressed {{
                background-color: {button_pressed};
            }}
            
            QPushButton#randomButton {{
                background-color: #3D0070;
                color: #FFFFFF;
                font-size: 28px;
                font-weight: 600;
                padding: 8px 32px;
                border-radius: 6px;
                border: 2px solid #7B2FBE;
            }}
            QPushButton#randomButton:hover {{
                background-color: #5A0099;
            }}
            
            #statusLabel {{
                color: {self.font_color};
            }}
            #hexCodesLabel {{
                color: {self.font_color};
            }}
            
            /* - Indigo Scrollbars - */
            QScrollBar:vertical {{
                background: #1a1a2e;
                width: 14px;
                margin: 0px;
                border-radius: 7px;
            }}
            QScrollBar::handle:vertical {{
                background: #3b1f6b;
                min-height: 30px;
                border-radius: 7px;
            }}
            QScrollBar::handle:vertical:hover {{
                background: #4e2a8e;
            }}
            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {{
                height: 0px;
            }}
            QScrollBar:horizontal {{
                background: #1a1a2e;
                height: 14px;
                margin: 0px;
                border-radius: 7px;
            }}
            QScrollBar::handle:horizontal {{
                background: #3b1f6b;
                min-width: 30px;
                border-radius: 7px;
            }}
            QScrollBar::handle:horizontal:hover {{
                background: #4e2a8e;
            }}
            QScrollBar::add-line:horizontal,
            QScrollBar::sub-line:horizontal {{
                width: 0px;
            }}
            """
        )

    def _lighten_color(self, hex_color: str, amount: int) -> str:
        """Lighten a hex color by amount (0-100)."""
        color = QColor(hex_color)
        h, s, v, a = color.getHsv()
        v = min(255, v + int(255 * amount / 100))
        color.setHsv(h, s, v, a)
        return color.name().upper()

    def _darken_color(self, hex_color: str, amount: int) -> str:
        """Darken a hex color by amount (0-100)."""
        color = QColor(hex_color)
        h, s, v, a = color.getHsv()
        v = max(0, v - int(255 * amount / 100))
        color.setHsv(h, s, v, a)
        return color.name().upper()

    def _rebuild_filters_and_apply(self, select_name: str | None = None) -> None:
        """Rebuild filter dropdowns and apply current filters."""
        categories = sorted({(self.name_to_palette[n].category or "Uncategorized").strip() or "Uncategorized" for n in self.all_palette_names}, key=lambda s: s.lower())

        # Put people-focused categories first: LGBTQ+, then Disability, then alphabetize the rest
        priority_categories = []
        if "LGBTQ+" in categories:
            priority_categories.append("LGBTQ+")
            categories.remove("LGBTQ+")
        if "Disability" in categories:
            priority_categories.append("Disability")
            categories.remove("Disability")

        categories = priority_categories + categories

        self.category_combo.blockSignals(True)
        self.category_combo.clear()
        self.category_combo.addItem("All")
        for c in categories:
            self.category_combo.addItem(c)
        if self.category_filter in [self.category_combo.itemText(i) for i in range(self.category_combo.count())]:
            self.category_combo.setCurrentText(self.category_filter)
        else:
            self.category_filter = "All"
            self.category_combo.setCurrentText("All")
        self.category_combo.blockSignals(False)

        self._apply_filters(select_name=select_name)

    def _apply_filters(self, select_name: str | None = None) -> None:
        """Apply current filter settings to palette list."""
        names = list(self.all_palette_names)

        if self.favorites_only:
            names = [n for n in names if n in self.favorite_palettes]

        if self.category_filter != "All":
            names = [n for n in names if (self.name_to_palette[n].category or "").strip() == self.category_filter]

        q = (self.search_text or "").strip().lower()
        if q:
            def match(n: str) -> bool:
                pal = self.name_to_palette.get(n)
                cat = (pal.category or "") if pal else ""
                return (q in n.lower()) or (q in cat.lower())

            names = [n for n in names if match(n)]

        # Sort by category first (LGBTQ+ first, Disability second), then alphabetically within each category
        def sort_key(n: str) -> tuple:
            pal = self.name_to_palette.get(n)
            category = (pal.category or "Uncategorized").strip() if pal else "Uncategorized"
            # LGBTQ+ comes first, Disability second, then everything else alphabetically
            if category.upper() == "LGBTQ+":
                category_priority = "0"
            elif category.upper() == "DISABILITY":
                category_priority = "1"
            else:
                category_priority = "2"
            return (category_priority, category.lower(), n.lower())

        if DEFAULT_PALETTE_NAME in names:
            # Keep default first, then sort the rest by category and name
            others = [n for n in names if n != DEFAULT_PALETTE_NAME]
            names = [DEFAULT_PALETTE_NAME] + sorted(others, key=sort_key)
        else:
            names = sorted(names, key=sort_key)

        current = self.palette_combo.currentText()
        target = select_name or (current if current in names else (names[0] if names else ""))

        self.palette_combo.blockSignals(True)
        self.palette_combo.clear()
        self.palette_combo.addItems(names)
        if target:
            self.palette_combo.setCurrentText(target)
        self.palette_combo.blockSignals(False)

        self.on_palette_changed(self.palette_combo.currentText())

    def _update_palette_strip(self, palette: Palette) -> None:
        """Update the color swatch strip."""
        while self.palette_strip_layout.count():
            item = self.palette_strip_layout.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()

        for hex_color in palette.colors:
            tile = QLabel()
            tile.setFixedSize(PALETTE_TILE_SIZE, PALETTE_TILE_SIZE)
            tile.setToolTip(hex_color)
            tile.setStyleSheet(
                f"background-color: {hex_color}; border: 1px solid {PALETTE_TILE_BORDER}; border-radius: 3px;"
            )
            self.palette_strip_layout.addWidget(tile)

    def _update_hex_codes_line(self, palette: Palette) -> None:
        """Update the hex codes display."""
        self.hex_codes_label.setText("Hex: " + ", ".join(palette.colors))

    def _update_status_line(self, settings: GradientSettings | None) -> None:
        """Update the status line display."""
        if settings is None:
            name = self.palette_combo.currentText()
            pal = self.name_to_palette.get(name)
            if not pal:
                self.status_label.setText("(no palette selected)")
                return
            w = self._get_width_value()
            h = self._get_height_value()
            direction = self.direction_combo.currentText()
            self.status_label.setText(f"{pal.name} - {w}x{h} - {direction} - Category: {pal.category} (ready)")
        else:
            self.status_label.setText(f"{settings.palette.name} - {settings.width}x{settings.height} - {settings.direction} - Category: {settings.palette.category}")

    def _update_favorite_button(self) -> None:
        """Update favorite button display."""
        name = self.palette_combo.currentText()
        if name in self.favorite_palettes:
            self.favorite_button.setText("- Favorite")
        else:
            self.favorite_button.setText("- Mark as Favorite")

    def _show_idle_image(self) -> None:
        """Show a generated banner preview."""
        try:
            # Use reasonable default dimensions (preview label might not be sized yet)
            width = 1200
            height = 600

            # Generate a beautiful rainbow banner
            # Use the RAINBOW - LGBTQ+ palette colors
            rainbow_colors = ["#FF0000", "#FFA500", "#FFFF00", "#008000", "#0000FF", "#4B0082", "#EE82EE"]

            # Create horizontal gradient banner
            banner = linear_gradient(width, height, rainbow_colors, "Horizontal")

            # Convert to QPixmap and display
            pixmap = pil_to_qpixmap(banner)

            # Scale to fit preview label if needed
            if pixmap and not pixmap.isNull():
                # Scale to reasonable size for display
                scaled = pixmap.scaled(800, 400, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                self.preview_label.setPixmap(scaled)
            else:
                # If pixmap creation failed, show text
                self.preview_label.setText("Ready!\n\nPick a palette and click 'Generate Preview'.")

        except Exception as e:
            # Fallback to text if generation fails
            print(f"Error generating idle banner: {e}")
            self.preview_label.setText("Ready!\n\nPick a palette and click 'Generate Preview'.")

    # Filter change handlers
    def on_category_changed(self, category: str) -> None:
        self.category_filter = category or "All"
        self._apply_filters()

    def on_search_changed(self, text: str) -> None:
        self.search_text = text or ""

        # TRULY GLOBAL SEARCH: Reset filters when searching
        if self.search_text.strip():
            # Reset category to "All" for global search
            self.category_combo.blockSignals(True)
            self.category_combo.setCurrentText("All")
            self.category_filter = "All"
            self.category_combo.blockSignals(False)

            # Reset favorites filter for global search
            if self.favorites_only:
                self.favorites_only = False
                # Update favorites button if it exists
                if hasattr(self, 'favorites_button'):
                    self.favorites_button.setChecked(False)

        self._apply_filters()

    def on_favorites_only_toggled(self, checked: bool) -> None:
        self.favorites_only = bool(checked)
        self._apply_filters()

    def on_palette_changed(self, _text: str) -> None:
        name = self.palette_combo.currentText()
        pal = self.name_to_palette.get(name)
        if pal:
            self._update_palette_strip(pal)
            self._update_hex_codes_line(pal)
        self._update_status_line(None)
        self._update_favorite_button()

    # -------------------------------------------------------------------------
    # AUTO-PREVIEW METHODS (hover delay for accessibility)
    # -------------------------------------------------------------------------

    def _on_palette_selected(self, name: str) -> None:
        """Handle palette selection (click) - generates immediately."""
        if not name:
            return
        
        # Cancel any pending hover timer
        self.hover_timer.stop()
        
        # Update UI elements (strip, hex codes, status, favorite button)
        self.on_palette_changed(name)
        
        # Auto-generate the gradient immediately
        if settings := self._build_settings_from_ui():
            self._render_and_show(settings)

    def _on_palette_hover(self, index: int) -> None:
        """Handle palette hover in dropdown - starts delay timer."""
        if index < 0 or index >= self.palette_combo.count():
            return
        
        palette_name = self.palette_combo.itemText(index)
        if not palette_name:
            return
        
        # Store the hovered palette and restart the timer
        self.pending_hover_palette = palette_name
        self.hover_timer.stop()
        self.hover_timer.start(500)  # 500ms delay for accessibility

    def _on_hover_timer_fired(self) -> None:
        """Timer fired after hovering for 500ms - generate preview."""
        if not self.pending_hover_palette:
            return
        
        # Set the combo to the hovered palette (without triggering signals)
        self.palette_combo.blockSignals(True)
        self.palette_combo.setCurrentText(self.pending_hover_palette)
        self.palette_combo.blockSignals(False)
        
        # Update UI and generate
        self.on_palette_changed(self.pending_hover_palette)
        if settings := self._build_settings_from_ui():
            self._render_and_show(settings)

    def _on_direction_changed(self, direction: str) -> None:
        """Handle direction change - auto-generate gradient."""
        self._update_status_line(None)
        if settings := self._build_settings_from_ui():
            self._render_and_show(settings)

    def _on_size_changed(self, text: str) -> None:
        """Handle width/height text change - starts delay timer."""
        self._update_status_line(None)
        self.size_timer.stop()
        self.size_timer.start(500)  # 500ms delay after typing stops

    def _on_size_timer_fired(self) -> None:
        """Timer fired after size input stops - regenerate."""
        if settings := self._build_settings_from_ui():
            self._render_and_show(settings)

    # -------------------------------------------------------------------------

    def on_toggle_favorite(self) -> None:
        name = self.palette_combo.currentText()
        if not name:
            return
        if name in self.favorite_palettes:
            self.favorite_palettes.remove(name)
        else:
            self.favorite_palettes.add(name)
        self._update_favorite_button()
        self._save_favorites()  # Save immediately
        if self.favorites_only:
            self._apply_filters(select_name=name if name in self.favorite_palettes else None)

    def _build_settings_from_ui(self) -> GradientSettings | None:
        name = self.palette_combo.currentText()
        pal = self.name_to_palette.get(name)
        if not pal:
            return None

        settings = GradientSettings(
            width=self._get_width_value(),
            height=self._get_height_value(),
            direction=self.direction_combo.currentText(),
            palette=pal,
        )
        if settings.clamp():
            self.width_spin.blockSignals(True)
            self.height_spin.blockSignals(True)
            self.width_spin.setText(str(settings.width))
            self.height_spin.setText(str(settings.height))
            self.width_spin.blockSignals(False)
            self.height_spin.blockSignals(False)
        return settings

    def _render_and_show(self, settings: GradientSettings) -> None:
        img = settings.to_image()
        self.current_img = img
        self.current_settings = settings

        max_w = max(1, self.preview_label.width())
        max_h = max(1, self.preview_label.height())

        # Calculate scale to FILL (no black bars!)
        scale_w = max_w / settings.width
        scale_h = max_h / settings.height
        scale = max(scale_w, scale_h)  # Use MAX to fill entire space

        # Resize to fill the preview area
        new_w = int(settings.width * scale)
        new_h = int(settings.height * scale)
        disp = img.resize((new_w, new_h), Image.Resampling.LANCZOS)

        self.preview_label.setPixmap(pil_to_qpixmap(disp))
        self._update_palette_strip(settings.palette)
        self._update_hex_codes_line(settings.palette)
        self._update_status_line(settings)

    def on_generate_clicked(self) -> None:
        if settings := self._build_settings_from_ui():
            self._render_and_show(settings)

    def on_random_clicked(self) -> None:
        """Handle Random Gradient button click."""
        # Pick a random palette from ALL available palettes (ignoring filters)
        if not self.all_palette_names:
            return

        random_palette_name = random.choice(self.all_palette_names)

        # Temporarily clear filters to show the random palette
        self.category_combo.setCurrentText("All")

        # Select the random palette
        self._rebuild_filters_and_apply(select_name=random_palette_name)

        # Also randomize direction and dimensions
        directions = ["Horizontal", "Vertical", "Diagonal", "Radial (Center)", "Conical (Sweep)"]
        self.direction_combo.setCurrentText(random.choice(directions))
        self.width_spin.setText(str(random.randint(640, 1640)))
        self.height_spin.setText(str(random.randint(360, 1080)))

        # Generate the preview automatically
        if settings := self._build_settings_from_ui():
            self._render_and_show(settings)

    def on_save_clicked(self) -> None:
        if self.current_img is None or self.current_settings is None:
            QMessageBox.warning(self, "No Image", "Generate a preview first before saving.")
            return

        # Create HFA Gradients folder in Downloads if it doesn't exist
        hfa_gradients_folder = Path.home() / "Downloads" / "HFA Gradients"
        hfa_gradients_folder.mkdir(parents=True, exist_ok=True)

        w, h = self.current_settings.width, self.current_settings.height
        default_filename = f"{self.current_settings.palette.name}_{w}x{h}_{self.current_settings.direction.replace(' ', '_')}.png"

        # Set default path to HFA Gradients folder
        default_path = str(hfa_gradients_folder / default_filename)

        filename, _ = QFileDialog.getSaveFileName(self, "Save Gradient as PNG", default_path, "PNG Files (*.png)")
        if filename:
            self.current_img.save(filename, "PNG")

            # LESSON 1: Separate folder and filename for clarity
            save_path = Path(filename)
            folder = save_path.parent
            file = save_path.name

            QMessageBox.information(
                self,
                " Save Successful",
                f"File: {file}\n\n- Saved to:\n{folder}"
            )

    def on_palette_builder_clicked(self) -> None:
        """Show menu to choose Edit Existing or Create New."""
        from PySide6.QtWidgets import QMenu

        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu {
                background-color: #2A2A2A;
                color: #FFFFFF;
                border: 1px solid #9D4EDD;
                font-size: 18pt;
                width: 300px;
            }
            QMenu::item:selected {
                background-color: #9D4EDD;
            }
        """)

        edit_action = menu.addAction("- Edit Existing Palette")
        create_action = menu.addAction(" Create New Palette")

        action = menu.exec(self.edit_palette_button.mapToGlobal(self.edit_palette_button.rect().bottomLeft()))

        if action == edit_action:
            self.on_edit_existing()
        elif action == create_action:
            self.on_create_new()

    def _load_palette_file(self, filename: str) -> None:
        """Load palettes from a JSON or Python data file."""
        try:
            loaded = load_palettes_from_file(filename)
        except Exception as e:
            QMessageBox.critical(self, "Load Error", f"Could not load palettes.\n\nDetails:\n{e}")
            return

        if not loaded:
            QMessageBox.information(
                self,
                "No Palettes Loaded",
                "No valid palettes were found.\n\n"
                "Supported formats:\n"
                "- JSON: {\"Name\": [\"#FF0000\", \"#00FF00\"]}\n"
                "- JSON with category: {\"Name\": {\"colors\": [...], \"category\": \"Sports\"}}\n"
                "- Python-data: APPS_ONLY = {\"Name\": [\"#FF0000\", \"#00FF00\"]}\n"
                "- Palettes must have at least TWO valid colors.",
            )
            return

        pack_name = os.path.splitext(os.path.basename(filename))[0].strip() or "Imported"

        added: list[str] = []
        for p in loaded:
            base = (p.name or "").strip() or "Imported Palette"
            unique = base
            suffix = 2
            while unique in self.name_to_palette:
                unique = f"{base} ({suffix})"
                suffix += 1

            pal = Palette(name=unique, colors=list(p.colors), category=(p.category or "Imported"))
            self.name_to_palette[unique] = pal
            if unique not in self.all_palette_names:
                self.all_palette_names.append(unique)
            self.name_to_pack[unique] = pack_name
            added.append(unique)

        self._rebuild_filters_and_apply(select_name=(added[0] if added else None))
        QMessageBox.information(self, "Palettes Loaded", f"Loaded {len(loaded)} palettes from:\n{os.path.basename(filename)}")

    def on_edit_existing(self) -> None:
        """Edit the currently selected palette."""
        name = self.palette_combo.currentText()
        pal = self.name_to_palette.get(name)
        if not pal:
            QMessageBox.warning(self, "No Palette Selected", "Please select a palette to edit.")
            return

        dlg = PaletteEditorDialog(pal, self, mode="edit")
        if dlg.exec() != QDialog.Accepted:
            return

        # Get edited colors and positions from dialog
        edited_colors = dlg.get_colors()
        edited_positions = dlg.get_positions()
        save_mode = dlg.get_save_mode()

        if save_mode == "update":
            # Update existing palette
            updated = Palette(
                name=pal.name,
                colors=edited_colors,
                category=pal.category,
                positions=edited_positions if edited_positions else None
            )
            self.name_to_palette[name] = updated
            self._apply_filters(select_name=name)
        else:
            # Save as new palette
            new_name = dlg.new_palette_name
            new_category = dlg.new_palette_category

            # Check for duplicate names
            base_name = new_name
            counter = 1
            while new_name in self.name_to_palette:
                new_name = f"{base_name} ({counter})"
                counter += 1

            new_palette = Palette(
                name=new_name,
                colors=edited_colors,
                category=new_category,
                positions=edited_positions if edited_positions else None
            )

            self.name_to_palette[new_name] = new_palette
            self.all_palette_names.append(new_name)
            self._rebuild_filters_and_apply(select_name=new_name)

        if settings := self._build_settings_from_ui():
            self._render_and_show(settings)
        else:
            self.on_palette_changed(self.palette_combo.currentText())

    def on_create_new(self) -> None:
        """Create a brand new palette from scratch."""
        dlg = PaletteEditorDialog(None, self, mode="create")
        if dlg.exec() != QDialog.Accepted:
            return

        # Get colors and positions from dialog
        colors = dlg.get_colors()
        positions = dlg.get_positions()
        new_name = dlg.new_palette_name
        new_category = dlg.new_palette_category

        # Check for duplicate names
        base_name = new_name
        counter = 1
        while new_name in self.name_to_palette:
            new_name = f"{base_name} ({counter})"
            counter += 1

        new_palette = Palette(
            name=new_name,
            colors=colors,
            category=new_category,
            positions=positions if positions else None
        )

        self.name_to_palette[new_name] = new_palette
        self.all_palette_names.append(new_name)
        self._rebuild_filters_and_apply(select_name=new_name)

        if settings := self._build_settings_from_ui():
            self._render_and_show(settings)
        else:
            self.on_palette_changed(new_name)

    def on_edit_palette_clicked(self) -> None:
        """Legacy method - redirects to on_edit_existing."""
        self.on_edit_existing()

    def _load_favorites(self) -> None:
        """Load favorites from settings file."""
        if not self.settings_path.exists():
            return

        try:
            data = safe_read_json(self.settings_path)
            favorites_list = data.get("favorites", [])
            if isinstance(favorites_list, list):
                self.favorite_palettes = set(favorites_list)
        except Exception:
            pass  # If loading fails, just start with empty favorites

    def _save_favorites(self) -> None:
        """Save favorites to settings file."""
        try:
            data = safe_read_json(self.settings_path) if self.settings_path.exists() else {}
            data["favorites"] = list(self.favorite_palettes)
            safe_write_json(self.settings_path, data)
        except Exception:
            pass  # Silently fail if we can't save

    def _load_theme_settings(self) -> None:
        """Load theme colors from settings file."""
        if not self.settings_path.exists():
            return

        try:
            data = safe_read_json(self.settings_path)
            self.bg_color = data.get("bg_color", DARK_CHARCOAL)
            self.font_color = data.get("font_color", BUTTON_TEXT)
            self.button_bg_color = data.get("button_bg_color", BUTTON_BG)
            self.button_text_color = data.get("button_text_color", BUTTON_TEXT)
        except Exception:
            pass

    def _save_theme_setting(self, key: str, value: str) -> None:
        """Save a single theme setting."""
        try:
            data = safe_read_json(self.settings_path) if self.settings_path.exists() else {}
            data[key] = value
            safe_write_json(self.settings_path, data)
        except Exception:
            pass

    def on_open_theme_dialog(self) -> None:
        """Open the theme customization dialog."""
        dlg = ThemeDialog(self)
        dlg.exec()

    def on_load_diy_palettes(self) -> None:
        """Load DIY (user-created) palettes from a file."""
        filename, _ = QFileDialog.getOpenFileName(
            self,
            "Load DIY Palettes (JSON or Python-data)",
            "",
            "Palette Files (*.json *.py *.txt);;JSON Files (*.json);;Python-data Files (*.py *.txt);;All Files (*)",
        )
        if not filename:
            return

        try:
            loaded = load_palettes_from_file(filename)
        except Exception as e:
            QMessageBox.critical(self, "Load Error", f"Could not load DIY palettes.\n\nDetails:\n{e}")
            return

        if not loaded:
            QMessageBox.information(
                self,
                "No Palettes Loaded",
                "No valid palettes were found.\n\n"
                "Supported formats:\n"
                "- JSON: {\"Name\": [\"#FF0000\", \"#00FF00\"]}\n"
                "- JSON with category: {\"Name\": {\"colors\": [\"#FF0000\", \"#00FF00\"], \"category\": \"DIY\"}}\n"
                "- Python-data: MY_PALETTES = {\"Name\": [\"#FF0000\", \"#00FF00\"]}\n"
                "- Palettes must have at least TWO valid colors.",
            )
            return

        pack_name = os.path.splitext(os.path.basename(filename))[0].strip() or "DIY"

        added: list[str] = []
        for p in loaded:
            base = (p.name or "").strip() or "DIY Palette"
            unique = base
            suffix = 2
            while unique in self.name_to_palette:
                unique = f"{base} ({suffix})"
                suffix += 1

            # Mark as DIY category unless explicitly specified
            category = (p.category or "").strip() or "DIY"
            pal = Palette(name=unique, colors=list(p.colors), category=category)
            self.name_to_palette[unique] = pal
            if unique not in self.all_palette_names:
                self.all_palette_names.append(unique)
            self.name_to_pack[unique] = pack_name
            added.append(unique)

        self._rebuild_filters_and_apply(select_name=(added[0] if added else None))
        QMessageBox.information(
            self,
            "DIY Palettes Loaded",
            f" Loaded {len(loaded)} DIY palette{'s' if len(loaded) != 1 else ''} from:\n{os.path.basename(filename)}"
        )

    def on_change_bg_color(self) -> None:
        """Let user pick a new background color."""
        current = QColor(self.bg_color)
        chosen = pick_color(current, self, "Choose Background Color")

        if chosen.isValid():
            self.bg_color = chosen.name().upper()
            self._save_theme_setting("bg_color", self.bg_color)
            self._apply_styles()

    def on_change_font_color(self) -> None:
        """Let user pick a new font color."""
        current = QColor(self.font_color)
        chosen = pick_color(current, self, "Choose Font Color")

        if chosen.isValid():
            self.font_color = chosen.name().upper()
            self._save_theme_setting("font_color", self.font_color)
            self._apply_styles()

    def on_change_button_bg(self) -> None:
        """Let user pick a new button background color."""
        current = QColor(self.button_bg_color)
        chosen = pick_color(current, self, "Choose Button Color")

        if chosen.isValid():
            self.button_bg_color = chosen.name().upper()
            self._save_theme_setting("button_bg_color", self.button_bg_color)
            self._apply_styles()

    def on_change_button_text(self) -> None:
        """Let user pick a new button text color."""
        current = QColor(self.button_text_color)
        chosen = pick_color(current, self, "Choose Button Text Color")

        if chosen.isValid():
            self.button_text_color = chosen.name().upper()
            self._save_theme_setting("button_text_color", self.button_text_color)
            self._apply_styles()

    def on_load_palettes_clicked(self) -> None:
        filename, _ = QFileDialog.getOpenFileName(
            self,
            "Load Palettes (JSON or Python-data)",
            "",
            "Palette Files (*.json *.py *.txt);;JSON Files (*.json);;Python-data Files (*.py *.txt);;All Files (*)",
        )
        if not filename:
            return

        try:
            loaded = load_palettes_from_file(filename)
        except Exception as e:
            QMessageBox.critical(self, "Load Error", f"Could not load palettes.\n\nDetails:\n{e}")
            return

        if not loaded:
            QMessageBox.information(
                self,
                "No Palettes Loaded",
                "No valid palettes were found.\n\n"
                "Supported formats:\n"
                "- JSON: {\"Name\": [\"#FF0000\", \"#00FF00\"]}\n"
                "- JSON with category: {\"Name\": {\"colors\": [\"#FF0000\", \"#00FF00\"], \"category\": \"Sports\"}}\n"
                "- Python-data: APPS_ONLY = {\"Name\": [\"#FF0000\", \"#00FF00\"]}\n"
                "- Palettes must have at least TWO valid colors.",
            )
            return

        pack_name = os.path.splitext(os.path.basename(filename))[0].strip() or "Imported"

        added: list[str] = []
        for p in loaded:
            base = (p.name or "").strip() or "Imported Palette"
            unique = base
            suffix = 2
            while unique in self.name_to_palette:
                unique = f"{base} ({suffix})"
                suffix += 1

            pal = Palette(name=unique, colors=list(p.colors), category=(p.category or "Imported"))
            self.name_to_palette[unique] = pal
            if unique not in self.all_palette_names:
                self.all_palette_names.append(unique)
            self.name_to_pack[unique] = pack_name
            added.append(unique)

        self._rebuild_filters_and_apply(select_name=(added[0] if added else None))
        QMessageBox.information(self, "Palettes Loaded", f"Loaded {len(loaded)} palettes from:\n{os.path.basename(filename)}")

    def on_reset_theme(self) -> None:
        """Reset to the built-in default theme."""
        reply = QMessageBox.question(
            self,
            "Reset Theme",
            "Reset to default theme?\n\nThis will restore default colors.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply != QMessageBox.Yes:
            return

        # Reset colors to defaults
        self.bg_color = DARK_CHARCOAL
        self.font_color = BUTTON_TEXT
        self.button_bg_color = BUTTON_BG
        self.button_text_color = BUTTON_TEXT

        # Save defaults
        self._save_theme_setting("bg_color", self.bg_color)
        self._save_theme_setting("font_color", self.font_color)
        self._save_theme_setting("button_bg_color", self.button_bg_color)
        self._save_theme_setting("button_text_color", self.button_text_color)

        # Refresh UI
        self._apply_styles()

        QMessageBox.information(self, "Theme Reset", "Theme has been reset to defaults!")

    def closeEvent(self, event) -> None:
        """Save state when closing the application."""
        self._save_favorites()
        super().closeEvent(event)

    def _get_width_value(self) -> int:
        """Get width value from text input, with validation."""
        try:
            value = int(self.width_spin.text())
            return max(1, min(value, MAX_GRADIENT_WIDTH))
        except ValueError:
            return 1200  # Default if invalid

    def _get_height_value(self) -> int:
        """Get height value from text input, with validation."""
        try:
            value = int(self.height_spin.text())
            return max(1, min(value, MAX_GRADIENT_HEIGHT))
        except ValueError:
            return 675  # Default if invalid

        # =============================================================================
        # SECTION 8.5: THEME CUSTOMIZATION DIALOG
        # =============================================================================

    class ThemeDialog(QDialog):
        """Dialog for customizing theme colors."""

        def __init__(self, parent) -> None:
            super().__init__(parent)
            self.main_window = parent
            self.setWindowTitle("Customize Theme")
            self.setMinimumWidth(350)

            layout = QVBoxLayout(self)
            layout.setSpacing(12)

            # Background color button
            self.bg_btn = QPushButton("Change Background")
            self.bg_btn.setFont(QFont(FONT_FAMILY, BUTTON_FONT_PT))
            self.bg_btn.clicked.connect(self.main_window._on_change_bg_color)
            layout.addWidget(self.bg_btn)

            # Font color button
            self.font_btn = QPushButton("Change Font Color")
            self.font_btn.setFont(QFont(FONT_FAMILY, BUTTON_FONT_PT))
            self.font_btn.clicked.connect(self.main_window._on_change_font_color)
            layout.addWidget(self.font_btn)

            # Button background color
            self.btn_bg_btn = QPushButton("Change Button Color")
            self.btn_bg_btn.setFont(QFont(FONT_FAMILY, BUTTON_FONT_PT))
            self.btn_bg_btn.clicked.connect(self.main_window._on_change_button_bg)
            layout.addWidget(self.btn_bg_btn)

            # Button text color
            self.btn_text_btn = QPushButton("  Change Button Text")
            self.btn_text_btn.setFont(QFont(FONT_FAMILY, BUTTON_FONT_PT))
            self.btn_text_btn.clicked.connect(self.main_window._on_change_button_text)
            layout.addWidget(self.btn_text_btn)

            # Separator
            separator = QFrame()
            separator.setFrameShape(QFrame.HLine)
            separator.setStyleSheet("color: #555;")
            layout.addWidget(separator)

            # Load palette file
            self.load_palette_btn = QPushButton("Load Palette File")
            self.load_palette_btn.setFont(QFont(FONT_FAMILY, BUTTON_FONT_PT))
            self.load_palette_btn.clicked.connect(self.main_window._on_load_palette)
            layout.addWidget(self.load_palette_btn)

            # Load theme file
            self.load_btn = QPushButton("Load Theme File")
            self.load_btn.setFont(QFont(FONT_FAMILY, BUTTON_FONT_PT))
            self.load_btn.clicked.connect(self.main_window._on_load_theme)
            layout.addWidget(self.load_btn)

            # Reset to defaults
            self.reset_btn = QPushButton("- Reset to Defaults")
            self.reset_btn.setFont(QFont(FONT_FAMILY, BUTTON_FONT_PT))
            self.reset_btn.clicked.connect(self.main_window._on_reset_theme)
            layout.addWidget(self.reset_btn)

            # Close button
            self.close_btn = QPushButton("Close")
            self.close_btn.setFont(QFont(FONT_FAMILY, BUTTON_FONT_PT))
            self.close_btn.clicked.connect(self.accept)
            layout.addWidget(self.close_btn)


# --------------------------------------------------------------------------------------
# Entry point
# --------------------------------------------------------------------------------------

if __name__ == "__main__":
    app = QApplication(sys.argv)

    app.setStyleSheet("""
        /* - Global Scrollbar Styling for HFA - */
        QScrollBar:vertical {
            background: #1a1a2e;
            width: 14px;
            margin: 0px;
            border-radius: 7px;
        }
        QScrollBar::handle:vertical {
            background: #3b1f6b;
            min-height: 30px;
            border-radius: 7px;
        }
        QScrollBar::handle:vertical:hover {
            background: #4e2a8e;
        }
        QScrollBar::add-line:vertical,
        QScrollBar::sub-line:vertical {
            height: 0px;
        }
        QScrollBar:horizontal {
            background: #1a1a2e;
            height: 14px;
            margin: 0px;
            border-radius: 7px;
        }
        QScrollBar::handle:horizontal {
            background: #3b1f6b;
            min-width: 30px;
            border-radius: 7px;
        }
        QScrollBar::handle:horizontal:hover {
            background: #4e2a8e;
        }
        QScrollBar::add-line:horizontal,
        QScrollBar::sub-line:horizontal {
            width: 0px;
        }
    """)

    # Create splash screen with your beautiful gradient!
    from PySide6.QtWidgets import QSplashScreen
    from PySide6.QtCore import Qt as QtCore

    # Try to load the custom gradient splash image
    splash_image_path = Path(__file__).parent / "HFA_splash.png"

    if splash_image_path.exists():
        # Use your beautiful Pansexual gradient!
        splash_pix = QPixmap(str(splash_image_path))
        # Scale to nice splash size if needed
        if splash_pix.width() > 600:
            splash_pix = splash_pix.scaled(600, 400, QtCore.KeepAspectRatio, QtCore.SmoothTransformation)
    else:
        # Fallback to simple colored splash
        splash_pix = QPixmap(600, 400)
        splash_pix.fill(QColor("#FF1B8D"))  # Pansexual pink as fallback

    splash = QSplashScreen(splash_pix, QtCore.WindowStaysOnTopHint)

    # Add text with shadow for better visibility
    from PySide6.QtGui import QPainter, QFont as QFontGui, QColor as QColorGui
    from PySide6.QtCore import QRect

    painter = QPainter(splash_pix)
    painter.setRenderHint(QPainter.Antialiasing)
    painter.setRenderHint(QPainter.TextAntialiasing)

    # Define text blocks - SHORTER MESSAGE
    title_text = "HUEMANITY for ALL\nby Troyski"
    body_text = "A Colorful Celebration of Equality,\nDiversity and Inclusion \n"
    "This app is dedicated to the beautiful people of our LGBTQ+ Community \n"


    # Fonts - SMALLER SIZES
    title_font = QFontGui("Century Gothic UI", 28, QFontGui.Weight.Bold)
    body_font = QFontGui("Century Gothic UI", 18, QFontGui.Weight.Bold)  # Bold for better readability

    rect = splash_pix.rect()

    # Calculate positions for centered text
    title_rect = QRect(rect.left(), rect.top() + 60, rect.width(), 120)
    body_rect = QRect(rect.left() + 20, rect.top() + 220, rect.width() - 40, 100)

    # Draw TITLE with strong outline (white text with black outline)
    painter.setFont(title_font)
    # Black outline (thicker)
    painter.setPen(QColorGui(0, 0, 0, 255))
    for dx in [-2, -1, 0, 1, 2]:
        for dy in [-2, -1, 0, 1, 2]:
            if dx != 0 or dy != 0:
                painter.drawText(title_rect.adjusted(dx, dy, dx, dy), QtCore.AlignCenter, title_text)
    # Main text in WHITE
    painter.setPen(QColorGui(255, 255, 255, 255))
    painter.drawText(title_rect, QtCore.AlignCenter, title_text)

    # Draw BODY with strong outline (dark navy text with white outline for contrast)
    painter.setFont(body_font)
    # White outline (thicker)
    painter.setPen(QColorGui(255, 255, 255, 255))
    for dx in [-2, -1, 0, 1, 2]:
        for dy in [-2, -1, 0, 1, 2]:
            if dx != 0 or dy != 0:
                painter.drawText(body_rect.adjusted(dx, dy, dx, dy), QtCore.AlignCenter, body_text)
    # Main text in DARK NAVY (much more visible than indigo)
    painter.setPen(QColorGui(25, 25, 112))  # Midnight Blue (#191970)
    painter.drawText(body_rect, QtCore.AlignCenter, body_text)

        # -- e --
    hint_font = QFontGui("Segoe UI", 12, QFontGui.Weight.Bold)
    painter.setFont(hint_font)
    pill_w, pill_h = 240, 28
    pill_x = rect.center().x() - pill_w // 2
    pill_y = rect.bottom() - pill_h - 10
    pill_rect = QRect(pill_x, pill_y, pill_w, pill_h)
    painter.setPen(QtCore.NoPen)
    painter.setBrush(QColorGui(75, 0, 130))          # Solid indigo #4B0082
    painter.drawRoundedRect(pill_rect, 14, 14)
    painter.setPen(QColorGui(0, 255, 180))            # Vibrant mint #00FFB4
    painter.drawText(pill_rect, QtCore.AlignCenter, "Click anywhere to dismiss")

    painter.end()

    splash.setPixmap(splash_pix)
    splash.show()
    app.processEvents()  # Force splash to display immediately

    win = MainWindow()

    # If ALL_palettes import failed, show warning
    if len(win.all_palette_names) <= 3:
        QMessageBox.warning(
            win,
            "Master Palettes Not Found",
            "I couldn't import 'HFA_ALL_palettes.py'.\n\n"
            "Fix:\n"
            "1) Put HFA_ALL_palettes.py in the SAME folder as this app file.\n"
            "2) Make sure it contains Palette, DEFAULT_PALETTE_NAME, and palette_names_and_map().\n\n"
            "The app is running with a tiny fallback palette set for now.",
        )

    win.show()  # No splash - was causing monitor sleep
    win.activateWindow()  # Force activate to prevent sleep
    win.raise_()  # Bring to front
    win.show()
    sys.exit(app.exec())

